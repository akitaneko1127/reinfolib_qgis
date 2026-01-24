# -*- coding: utf-8 -*-
"""
API Client for ReinfoLib QGIS Plugin

Handles HTTP communication with the Real Estate Information Library API.
Uses QgsNetworkAccessManager for QGIS compatibility.
"""

import json
import gzip
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass

from qgis.PyQt.QtCore import QUrl, QByteArray, QEventLoop, QTimer
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import QgsNetworkAccessManager, QgsNetworkReplyContent, QgsMessageLog, Qgis

from .settings_manager import SettingsManager
from .api_definitions import ApiDefinitions, ApiInfo
from .tile_calculator import TileCalculator


@dataclass
class ApiResponse:
    """Response from an API call."""

    success: bool
    data: Optional[Any]
    error_code: Optional[int]
    error_message: Optional[str]


class ApiClient:
    """Client for Real Estate Information Library API."""

    HEADER_API_KEY = 'Ocp-Apim-Subscription-Key'

    def __init__(self, settings: Optional[SettingsManager] = None):
        """Initialize the API client.

        Args:
            settings: Settings manager instance. Creates new one if None.
        """
        self.settings = settings or SettingsManager()
        self.network_manager = QgsNetworkAccessManager.instance()

    def _log(self, message: str, level: Qgis.MessageLevel = Qgis.Info) -> None:
        """Log a message to QGIS log panel."""
        QgsMessageLog.logMessage(message, 'ReinfoLib', level)

    def _create_request(self, url: str) -> QNetworkRequest:
        """Create a network request with API key header."""
        request = QNetworkRequest(QUrl(url))
        api_key = self.settings.get_api_key()
        if api_key:
            request.setRawHeader(
                self.HEADER_API_KEY.encode(),
                api_key.encode()
            )
        request.setRawHeader(b'Accept', b'application/json')
        request.setRawHeader(b'Accept-Encoding', b'gzip')
        return request

    def _parse_response(self, reply: QgsNetworkReplyContent) -> ApiResponse:
        """Parse a network reply into ApiResponse."""
        error = reply.error()

        if error != QNetworkReply.NoError:
            status_code = reply.attribute(
                QNetworkRequest.HttpStatusCodeAttribute
            )
            error_msg = self._get_error_message(status_code, reply.errorString())

            # Log detailed error for debugging
            self._log(
                f'API Error: status={status_code}, error={reply.errorString()}',
                Qgis.Warning
            )

            return ApiResponse(
                success=False,
                data=None,
                error_code=status_code,
                error_message=error_msg
            )

        # Read response data (QgsNetworkReplyContent uses content() not readAll())
        raw_data = reply.content()
        content_encoding = reply.rawHeader(b'Content-Encoding')

        try:
            # Decompress if gzipped
            if content_encoding == b'gzip':
                data_bytes = gzip.decompress(bytes(raw_data))
            else:
                data_bytes = bytes(raw_data)

            # Check if it's JSON or binary (PBF)
            try:
                # Try to parse as JSON first
                data = json.loads(data_bytes.decode('utf-8'))
                return ApiResponse(
                    success=True,
                    data=data,
                    error_code=None,
                    error_message=None
                )
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Might be PBF (binary) format - return raw bytes for later processing
                return ApiResponse(
                    success=True,
                    data={'_raw_bytes': data_bytes, '_format': 'pbf'},
                    error_code=None,
                    error_message=None
                )

        except Exception as e:
            return ApiResponse(
                success=False,
                data=None,
                error_code=None,
                error_message=f'レスポンスエラー: {str(e)}'
            )

    def _get_error_message(
        self,
        status_code: Optional[int],
        default_msg: str
    ) -> str:
        """Get user-friendly error message for HTTP status code."""
        messages = {
            400: 'パラメータが不正です。設定を確認してください。',
            401: 'APIキーが無効です。設定でAPIキーを確認してください。',
            403: 'このAPIへのアクセスが拒否されました。',
            404: 'APIエンドポイントが見つかりません。選択した条件にデータがない可能性があります。',
            429: 'リクエストが多すぎます。しばらく待ってから再試行してください。',
            500: 'サーバーエラーが発生しました。後でもう一度お試しください。',
            502: 'サーバーが一時的に利用できません。',
            503: 'サービスが利用できません。後でもう一度お試しください。',
        }
        if status_code:
            return messages.get(status_code, f'HTTPエラー {status_code}: {default_msg}')
        return default_msg

    def fetch_sync(
        self,
        url: str,
        timeout_ms: Optional[int] = None
    ) -> ApiResponse:
        """Fetch URL synchronously.

        Args:
            url: URL to fetch.
            timeout_ms: Timeout in milliseconds (currently not used, reserved for future).

        Returns:
            ApiResponse with result or error.
        """
        request = self._create_request(url)
        # blockingGet returns QgsNetworkReplyContent (not QNetworkReply)
        reply = self.network_manager.blockingGet(request)

        response = self._parse_response(reply)
        # QgsNetworkReplyContent is not a QObject, no deleteLater() needed

        return response

    def fetch_api(
        self,
        api_id: str,
        params: Optional[Dict[str, str]] = None
    ) -> ApiResponse:
        """Fetch data from an API endpoint.

        Args:
            api_id: API identifier (e.g., 'XIT001').
            params: Query parameters.

        Returns:
            ApiResponse with result or error.
        """
        api_info = ApiDefinitions.get_api(api_id)
        if not api_info:
            return ApiResponse(
                success=False,
                data=None,
                error_code=None,
                error_message=f'Unknown API: {api_id}'
            )

        # Build URL with parameters
        url = api_info.endpoint
        if params:
            query_parts = [f'{k}={v}' for k, v in params.items() if v]
            if query_parts:
                url = f'{url}?{"&".join(query_parts)}'

        self._log(f'Fetching: {url}')
        return self.fetch_sync(url)

    def fetch_tile_api(
        self,
        api_id: str,
        zoom: int,
        x: int,
        y: int,
        extra_params: Optional[Dict[str, str]] = None
    ) -> ApiResponse:
        """Fetch data from a tile-based API.

        Args:
            api_id: API identifier.
            zoom: Zoom level.
            x: Tile X coordinate.
            y: Tile Y coordinate.
            extra_params: Additional parameters for specific APIs.

        Returns:
            ApiResponse with GeoJSON data.
        """
        api_info = ApiDefinitions.get_api(api_id)
        if not api_info:
            return ApiResponse(
                success=False,
                data=None,
                error_code=None,
                error_message=f'Unknown API: {api_id}'
            )

        if not api_info.uses_tile:
            return ApiResponse(
                success=False,
                data=None,
                error_code=None,
                error_message=f'API {api_id} does not support tile coordinates'
            )

        # ReinfoLib uses query parameters for tile coordinates
        # Format: ?response_format=geojson&z={zoom}&x={x}&y={y}&other_params
        url = f'{api_info.endpoint}?response_format=geojson&z={zoom}&x={x}&y={y}'

        # Add extra parameters if provided
        if extra_params:
            for key, value in extra_params.items():
                url += f'&{key}={value}'

        self._log(f'Fetching tile: {url}')
        response = self.fetch_sync(url)

        return response

    def fetch_tiles_for_extent(
        self,
        api_id: str,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        zoom: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        extra_params: Optional[Dict[str, str]] = None
    ) -> ApiResponse:
        """Fetch all tiles covering an extent.

        Args:
            api_id: API identifier.
            min_lat: Minimum latitude.
            min_lon: Minimum longitude.
            max_lat: Maximum latitude.
            max_lon: Maximum longitude.
            zoom: Zoom level (auto-calculated if None).
            progress_callback: Called with (current, total) for progress.

        Returns:
            ApiResponse with merged GeoJSON data.
        """
        max_tiles = self.settings.get_max_tiles()

        # Auto-calculate zoom if not specified
        if zoom is None:
            zoom = TileCalculator.estimate_zoom_for_extent(
                min_lat, min_lon, max_lat, max_lon, max_tiles
            )

        # For mesh data (XKT013), use lower zoom level to get more coverage
        # 250m mesh needs zoom 12 or lower to get complete coverage for large areas
        if api_id == 'XKT013' and zoom > 12:
            zoom = 12
            self._log(f'XKT013: Adjusted zoom to {zoom} for better mesh coverage')

        self._log(f'Fetching tiles: extent=({min_lat:.4f},{min_lon:.4f})-({max_lat:.4f},{max_lon:.4f}), zoom={zoom}, max_tiles={max_tiles}')

        # Get tiles for extent
        tiles = TileCalculator.get_tiles_for_extent(
            min_lat, min_lon, max_lat, max_lon, zoom, max_tiles
        )

        self._log(f'Tiles to fetch: {len(tiles)} tiles at zoom {zoom}')

        if not tiles:
            return ApiResponse(
                success=False,
                data=None,
                error_code=None,
                error_message='No tiles in specified extent'
            )

        # Fetch each tile
        all_features = []
        errors = []
        total = len(tiles)

        for i, (x, y) in enumerate(tiles):
            if progress_callback:
                progress_callback(i + 1, total)

            response = self.fetch_tile_api(api_id, zoom, x, y, extra_params)

            if response.success and response.data:
                features = response.data.get('features', [])
                if features:
                    self._log(f'Tile z={zoom},x={x},y={y}: {len(features)} features')
                all_features.extend(features)
            elif response.error_code == 404:
                # 404 is normal for tiles with no data, skip silently
                pass
            elif response.error_message:
                errors.append(f'Tile {x},{y}: {response.error_message}')

        if not all_features:
            if errors:
                return ApiResponse(
                    success=False,
                    data=None,
                    error_code=None,
                    error_message='選択した範囲にデータがありません。別の場所を選択するか、地図をズームアウトしてより広い範囲を選択してください。'
                )
            else:
                return ApiResponse(
                    success=False,
                    data=None,
                    error_code=None,
                    error_message='選択した範囲にデータがありません。'
                )

        # Build merged GeoJSON
        merged_geojson = {
            'type': 'FeatureCollection',
            'features': all_features
        }

        self._log(f'Total features retrieved: {len(all_features)}')

        return ApiResponse(
            success=True,
            data=merged_geojson,
            error_code=None,
            error_message=None
        )

    def test_api_key(self) -> ApiResponse:
        """Test if the configured API key is valid.

        Returns:
            ApiResponse indicating success or failure.
        """
        # Use XIT002 with Tokyo prefecture as a simple test
        return self.fetch_api('XIT002', {'area': '13'})

    def get_municipalities(self, prefecture_code: str) -> ApiResponse:
        """Get list of municipalities in a prefecture.

        Args:
            prefecture_code: 2-digit prefecture code.

        Returns:
            ApiResponse with municipality list.
        """
        return self.fetch_api('XIT002', {'area': prefecture_code})
