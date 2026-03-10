# -*- coding: utf-8 -*-
"""
Cache Manager for ReinfoLib QGIS Plugin

Manages local caching of API responses to reduce network requests.
"""

import json
import hashlib
import time
from typing import Optional, Dict, Any
from pathlib import Path

from qgis.core import QgsApplication, QgsMessageLog, Qgis

from .settings_manager import SettingsManager


class CacheManager:
    """Manages caching of API responses."""

    CACHE_DIR_NAME = 'reinfolib_cache'

    def __init__(self, settings: Optional[SettingsManager] = None):
        """Initialize the cache manager.

        Args:
            settings: Settings manager instance.
        """
        self.settings = settings or SettingsManager()
        self._cache_dir: Optional[Path] = None

    @staticmethod
    def _log(message: str, level: Qgis.MessageLevel = Qgis.Info) -> None:
        """Log a message to QGIS log panel."""
        QgsMessageLog.logMessage(message, 'ReinfoLib', level)

    @property
    def cache_dir(self) -> Path:
        """Get the cache directory path."""
        if self._cache_dir is None:
            # Use QGIS profile directory for cache
            profile_dir = QgsApplication.qgisSettingsDirPath()
            self._cache_dir = Path(profile_dir) / self.CACHE_DIR_NAME

            # Create directory if it doesn't exist
            self._cache_dir.mkdir(parents=True, exist_ok=True)

        return self._cache_dir

    def _generate_cache_key(self, url: str) -> str:
        """Generate a cache key from URL."""
        return hashlib.sha256(url.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache entry."""
        return self.cache_dir / f'{cache_key}.json'

    def is_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self.settings.is_cache_enabled()

    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached data for a URL.

        Args:
            url: The URL to look up.

        Returns:
            Cached data or None if not found/expired.
        """
        if not self.is_enabled():
            return None

        cache_key = self._generate_cache_key(url)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)

            # Check expiration
            cached_time = cache_entry.get('timestamp', 0)
            cache_hours = self.settings.get_cache_hours()
            max_age = cache_hours * 3600  # Convert to seconds

            if time.time() - cached_time > max_age:
                # Cache expired
                self._delete_cache_file(cache_path)
                return None

            self._log(f'Cache hit: {url}')
            return cache_entry.get('data')

        except (json.JSONDecodeError, IOError, KeyError) as e:
            self._log(f'Cache read error: {e}', Qgis.Warning)
            self._delete_cache_file(cache_path)
            return None

    def set(self, url: str, data: Dict[str, Any]) -> bool:
        """Store data in cache.

        Args:
            url: The URL as cache key.
            data: Data to cache.

        Returns:
            True if successfully cached.
        """
        if not self.is_enabled():
            return False

        cache_key = self._generate_cache_key(url)
        cache_path = self._get_cache_path(cache_key)

        cache_entry = {
            'url': url,
            'timestamp': time.time(),
            'data': data
        }

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, ensure_ascii=False)
            return True
        except IOError as e:
            self._log(f'Cache write error: {e}', Qgis.Warning)
            return False

    def _delete_cache_file(self, cache_path: Path) -> None:
        """Safely delete a cache file."""
        try:
            if cache_path.exists():
                cache_path.unlink()
        except IOError:
            pass

    def clear(self) -> int:
        """Clear all cached data.

        Returns:
            Number of files deleted.
        """
        count = 0
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                cache_file.unlink()
                count += 1
            except IOError:
                pass

        self._log(f'Cleared {count} cache files')
        return count

    def clear_expired(self) -> int:
        """Clear only expired cache entries.

        Returns:
            Number of files deleted.
        """
        count = 0
        cache_hours = self.settings.get_cache_hours()
        max_age = cache_hours * 3600
        current_time = time.time()

        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_entry = json.load(f)

                cached_time = cache_entry.get('timestamp', 0)
                if current_time - cached_time > max_age:
                    cache_file.unlink()
                    count += 1

            except (json.JSONDecodeError, IOError, KeyError):
                # Delete corrupted cache files
                try:
                    cache_file.unlink()
                    count += 1
                except IOError:
                    pass

        if count > 0:
            self._log(f'Cleared {count} expired cache files')

        return count

    def get_cache_size(self) -> int:
        """Get total cache size in bytes.

        Returns:
            Total size of cache files in bytes.
        """
        total = 0
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                total += cache_file.stat().st_size
            except IOError:
                pass
        return total

    def get_cache_count(self) -> int:
        """Get number of cached entries.

        Returns:
            Number of cache files.
        """
        return len(list(self.cache_dir.glob('*.json')))

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache statistics.
        """
        return {
            'enabled': self.is_enabled(),
            'directory': str(self.cache_dir),
            'count': self.get_cache_count(),
            'size_bytes': self.get_cache_size(),
            'max_age_hours': self.settings.get_cache_hours(),
        }
