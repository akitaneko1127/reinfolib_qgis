# -*- coding: utf-8 -*-
"""
Settings Manager for ReinfoLib QGIS Plugin

Handles API key storage and plugin settings using QSettings.
"""

import base64
from qgis.PyQt.QtCore import QSettings


class SettingsManager:
    """Manages plugin settings and API key storage."""

    PREFIX = 'reinfolib'

    # Default values
    DEFAULTS = {
        'api_key': '',
        'default_format': 'memory',
        'language': 'ja',
        'timeout': 30,
        'retry_count': 3,
        'max_tiles': 100,
        'cache_enabled': True,
        'cache_hours': 24,
        'auto_style': True,
        'auto_zoom': True,
        'xkt025_style_field': 'topography',  # 'topography' or 'note'
        'xkt023_style_field': 'city_name',   # 'city_name' or 'plan_name'
        'xkt013_year': '2020',               # '2020', '2025', '2030', '2035', '2040', '2045', '2050'
        'xkt013_data_type': 'total',         # 'total', 'age_group', 'age_category', 'ratio'
        'xkt013_field': 'PTN',               # Field prefix (PTN, PT01-PT20, PTA-PTE, RTA-RTE)
    }

    def __init__(self):
        """Initialize the settings manager."""
        self.settings = QSettings()

    def _key(self, name: str) -> str:
        """Generate full settings key with prefix."""
        return f'{self.PREFIX}/{name}'

    def get_api_key(self) -> str:
        """Get the stored API key (decoded)."""
        encoded = self.settings.value(self._key('api_key'), '')
        if not encoded:
            return ''
        try:
            return base64.b64decode(encoded.encode()).decode()
        except Exception:
            return ''

    def set_api_key(self, api_key: str) -> None:
        """Store the API key (encoded)."""
        if api_key:
            encoded = base64.b64encode(api_key.encode()).decode()
            self.settings.setValue(self._key('api_key'), encoded)
        else:
            self.settings.remove(self._key('api_key'))

    def delete_api_key(self) -> None:
        """Delete the stored API key."""
        self.settings.remove(self._key('api_key'))

    def has_api_key(self) -> bool:
        """Check if an API key is stored."""
        return bool(self.get_api_key())

    def get_value(self, name: str, default=None):
        """Get a setting value."""
        if default is None:
            default = self.DEFAULTS.get(name)
        return self.settings.value(self._key(name), default)

    def set_value(self, name: str, value) -> None:
        """Set a setting value."""
        self.settings.setValue(self._key(name), value)

    def get_timeout(self) -> int:
        """Get API timeout in seconds."""
        return int(self.get_value('timeout', 30))

    def get_retry_count(self) -> int:
        """Get retry count for failed requests."""
        return int(self.get_value('retry_count', 3))

    def get_max_tiles(self) -> int:
        """Get maximum number of tiles per request."""
        return int(self.get_value('max_tiles', 100))

    def is_cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        val = self.get_value('cache_enabled', True)
        return val in (True, 'true', '1', 1)

    def get_cache_hours(self) -> int:
        """Get cache duration in hours."""
        return int(self.get_value('cache_hours', 24))

    def get_language(self) -> str:
        """Get API response language (ja/en)."""
        return self.get_value('language', 'ja')

    def get_default_format(self) -> str:
        """Get default output format."""
        return self.get_value('default_format', 'memory')

    def is_auto_style_enabled(self) -> bool:
        """Check if auto style is enabled."""
        val = self.get_value('auto_style', True)
        return val in (True, 'true', '1', 1)

    def is_auto_zoom_enabled(self) -> bool:
        """Check if auto zoom is enabled."""
        val = self.get_value('auto_zoom', True)
        return val in (True, 'true', '1', 1)

    def get_xkt025_style_field(self) -> str:
        """Get XKT025 (大規模盛土造成地) style field preference."""
        return self.get_value('xkt025_style_field', 'topography')

    def set_xkt025_style_field(self, field: str) -> None:
        """Set XKT025 style field preference ('topography' or 'note')."""
        self.set_value('xkt025_style_field', field)

    def get_xkt023_style_field(self) -> str:
        """Get XKT023 (市区町村役場等) style field preference."""
        return self.get_value('xkt023_style_field', 'city_name')

    def set_xkt023_style_field(self, field: str) -> None:
        """Set XKT023 style field preference ('city_name' or 'plan_name')."""
        self.set_value('xkt023_style_field', field)

    def get_xkt013_year(self) -> str:
        """Get XKT013 (将来推計人口メッシュ) year preference."""
        return self.get_value('xkt013_year', '2020')

    def set_xkt013_year(self, year: str) -> None:
        """Set XKT013 year preference ('2020', '2025', '2030', '2035', '2040', '2045', '2050')."""
        self.set_value('xkt013_year', year)

    def get_xkt013_data_type(self) -> str:
        """Get XKT013 data type preference."""
        return self.get_value('xkt013_data_type', 'total')

    def set_xkt013_data_type(self, data_type: str) -> None:
        """Set XKT013 data type preference ('total', 'age_group', 'age_category', 'ratio')."""
        self.set_value('xkt013_data_type', data_type)

    def get_xkt013_field(self) -> str:
        """Get XKT013 field preference."""
        return self.get_value('xkt013_field', 'PTN')

    def set_xkt013_field(self, field: str) -> None:
        """Set XKT013 field preference."""
        self.set_value('xkt013_field', field)

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults (except API key)."""
        for name, value in self.DEFAULTS.items():
            if name != 'api_key':
                self.set_value(name, value)
