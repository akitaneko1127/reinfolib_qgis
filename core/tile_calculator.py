# -*- coding: utf-8 -*-
"""
Tile Calculator for ReinfoLib QGIS Plugin

Converts geographic coordinates to tile coordinates for tile-based APIs.
"""

import math
from typing import List, Tuple


class TileCalculator:
    """Calculates tile coordinates from geographic coordinates."""

    # Zoom level to approximate tile width in km at equator
    ZOOM_TILE_KM = {
        11: 19.5,
        12: 9.8,
        13: 4.9,
        14: 2.4,
        15: 1.2,
    }

    @staticmethod
    def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """Convert latitude/longitude to tile coordinates.

        Args:
            lat: Latitude in degrees.
            lon: Longitude in degrees.
            zoom: Zoom level.

        Returns:
            Tuple of (x, y) tile coordinates.
        """
        n = 2 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        lat_rad = math.radians(lat)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (x, y)

    @staticmethod
    def tile_to_lat_lon(x: int, y: int, zoom: int) -> Tuple[float, float]:
        """Convert tile coordinates to latitude/longitude (northwest corner).

        Args:
            x: Tile x coordinate.
            y: Tile y coordinate.
            zoom: Zoom level.

        Returns:
            Tuple of (latitude, longitude) in degrees.
        """
        n = 2 ** zoom
        lon = x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat = math.degrees(lat_rad)
        return (lat, lon)

    @classmethod
    def get_tiles_for_extent(
        cls,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        zoom: int,
        max_tiles: int = 100
    ) -> List[Tuple[int, int]]:
        """Get all tiles that cover a given extent.

        Args:
            min_lat: Minimum latitude.
            min_lon: Minimum longitude.
            max_lat: Maximum latitude.
            max_lon: Maximum longitude.
            zoom: Zoom level.
            max_tiles: Maximum number of tiles to return.

        Returns:
            List of (x, y) tile coordinate tuples.
        """
        # Get corner tiles
        min_x, max_y = cls.lat_lon_to_tile(min_lat, min_lon, zoom)
        max_x, min_y = cls.lat_lon_to_tile(max_lat, max_lon, zoom)

        tiles = []
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                tiles.append((x, y))
                if len(tiles) >= max_tiles:
                    return tiles

        return tiles

    @classmethod
    def estimate_zoom_for_extent(
        cls,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        max_tiles: int = 100
    ) -> int:
        """Estimate appropriate zoom level for an extent.

        Args:
            min_lat: Minimum latitude.
            min_lon: Minimum longitude.
            max_lat: Maximum latitude.
            max_lon: Maximum longitude.
            max_tiles: Maximum number of tiles allowed.

        Returns:
            Appropriate zoom level (11-15).
        """
        # ReinfoLib APIs support zoom 11-15
        # Start from highest zoom and decrease until within tile limit
        for zoom in range(15, 10, -1):
            tiles = cls.get_tiles_for_extent(
                min_lat, min_lon, max_lat, max_lon, zoom, max_tiles + 1
            )
            if len(tiles) <= max_tiles:
                return zoom

        return 11

    @staticmethod
    def tile_count_for_extent(
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        zoom: int
    ) -> int:
        """Calculate number of tiles needed to cover an extent.

        Args:
            min_lat: Minimum latitude.
            min_lon: Minimum longitude.
            max_lat: Maximum latitude.
            max_lon: Maximum longitude.
            zoom: Zoom level.

        Returns:
            Number of tiles.
        """
        min_x, max_y = TileCalculator.lat_lon_to_tile(min_lat, min_lon, zoom)
        max_x, min_y = TileCalculator.lat_lon_to_tile(max_lat, max_lon, zoom)

        width = max_x - min_x + 1
        height = max_y - min_y + 1

        return width * height
