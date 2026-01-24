# -*- coding: utf-8 -*-
"""
Settings Dialog for ReinfoLib QGIS Plugin

Dialog for managing API key and plugin settings.
"""

import webbrowser

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QMessageBox,
    QProgressDialog,
)
from qgis.core import QgsMessageLog, Qgis

from ..core.settings_manager import SettingsManager
from ..core.api_client import ApiClient
from ..core.cache_manager import CacheManager


class SettingsDialog(QDialog):
    """Dialog for plugin settings."""

    API_REGISTRATION_URL = 'https://www.reinfolib.mlit.go.jp/help/apiManual/'

    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.settings = SettingsManager()
        self.cache = CacheManager(self.settings)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(self.tr('ReinfoLib Settings'))
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # API Key tab
        self.tabs.addTab(self._create_api_key_tab(), self.tr('API Key'))

        # General tab
        self.tabs.addTab(self._create_general_tab(), self.tr('General'))

        # Cache tab
        self.tabs.addTab(self._create_cache_tab(), self.tr('Cache'))

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_ok = QPushButton(self.tr('OK'))
        self.btn_ok.clicked.connect(self._on_ok)
        button_layout.addWidget(self.btn_ok)

        self.btn_cancel = QPushButton(self.tr('Cancel'))
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)

        self.btn_apply = QPushButton(self.tr('Apply'))
        self.btn_apply.clicked.connect(self._save_settings)
        button_layout.addWidget(self.btn_apply)

        layout.addLayout(button_layout)

    def _create_api_key_tab(self) -> QWidget:
        """Create the API key settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # API Key group
        group = QGroupBox(self.tr('API Key'))
        group_layout = QVBoxLayout(group)

        # API key input
        key_layout = QHBoxLayout()
        self.edit_api_key = QLineEdit()
        self.edit_api_key.setEchoMode(QLineEdit.Password)
        self.edit_api_key.setPlaceholderText(self.tr('Enter your API key'))
        key_layout.addWidget(self.edit_api_key)

        self.btn_show_key = QPushButton(self.tr('Show'))
        self.btn_show_key.setCheckable(True)
        self.btn_show_key.toggled.connect(self._toggle_key_visibility)
        key_layout.addWidget(self.btn_show_key)

        group_layout.addLayout(key_layout)

        # Status label
        self.label_key_status = QLabel()
        group_layout.addWidget(self.label_key_status)

        # Buttons
        btn_layout = QHBoxLayout()

        self.btn_test_key = QPushButton(self.tr('Test Key'))
        self.btn_test_key.clicked.connect(self._test_api_key)
        btn_layout.addWidget(self.btn_test_key)

        self.btn_delete_key = QPushButton(self.tr('Delete Key'))
        self.btn_delete_key.clicked.connect(self._delete_api_key)
        btn_layout.addWidget(self.btn_delete_key)

        btn_layout.addStretch()
        group_layout.addLayout(btn_layout)

        layout.addWidget(group)

        # Registration link
        link_layout = QHBoxLayout()
        link_label = QLabel(self.tr("Don't have an API key?"))
        link_layout.addWidget(link_label)

        self.btn_register = QPushButton(self.tr('Apply for API Key'))
        self.btn_register.clicked.connect(self._open_registration)
        link_layout.addWidget(self.btn_register)

        link_layout.addStretch()
        layout.addLayout(link_layout)

        layout.addStretch()
        return widget

    def _create_general_tab(self) -> QWidget:
        """Create the general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Output settings group
        output_group = QGroupBox(self.tr('Default Output'))
        output_layout = QFormLayout(output_group)

        self.combo_format = QComboBox()
        self.combo_format.addItem(self.tr('Memory Layer'), 'memory')
        self.combo_format.addItem('GeoPackage', 'gpkg')
        self.combo_format.addItem('GeoJSON', 'geojson')
        self.combo_format.addItem('Shapefile', 'shp')
        self.combo_format.addItem('CSV', 'csv')
        output_layout.addRow(self.tr('Default format:'), self.combo_format)

        self.combo_language = QComboBox()
        self.combo_language.addItem(self.tr('Japanese'), 'ja')
        self.combo_language.addItem(self.tr('English'), 'en')
        output_layout.addRow(self.tr('API language:'), self.combo_language)

        layout.addWidget(output_group)

        # Network settings group
        network_group = QGroupBox(self.tr('Network'))
        network_layout = QFormLayout(network_group)

        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(5, 120)
        self.spin_timeout.setSuffix(self.tr(' seconds'))
        network_layout.addRow(self.tr('Timeout:'), self.spin_timeout)

        self.spin_retry = QSpinBox()
        self.spin_retry.setRange(0, 10)
        network_layout.addRow(self.tr('Retry count:'), self.spin_retry)

        self.spin_max_tiles = QSpinBox()
        self.spin_max_tiles.setRange(1, 500)
        network_layout.addRow(self.tr('Max tiles:'), self.spin_max_tiles)

        layout.addWidget(network_group)

        # Display settings group
        display_group = QGroupBox(self.tr('Display'))
        display_layout = QVBoxLayout(display_group)

        self.check_auto_style = QCheckBox(self.tr('Apply automatic styling'))
        display_layout.addWidget(self.check_auto_style)

        self.check_auto_zoom = QCheckBox(self.tr('Zoom to layer after fetch'))
        display_layout.addWidget(self.check_auto_zoom)

        layout.addWidget(display_group)

        layout.addStretch()
        return widget

    def _create_cache_tab(self) -> QWidget:
        """Create the cache settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Cache settings group
        cache_group = QGroupBox(self.tr('Cache Settings'))
        cache_layout = QVBoxLayout(cache_group)

        self.check_cache_enabled = QCheckBox(self.tr('Enable caching'))
        cache_layout.addWidget(self.check_cache_enabled)

        hours_layout = QHBoxLayout()
        hours_layout.addWidget(QLabel(self.tr('Cache duration:')))
        self.spin_cache_hours = QSpinBox()
        self.spin_cache_hours.setRange(1, 168)  # 1 hour to 1 week
        self.spin_cache_hours.setSuffix(self.tr(' hours'))
        hours_layout.addWidget(self.spin_cache_hours)
        hours_layout.addStretch()
        cache_layout.addLayout(hours_layout)

        layout.addWidget(cache_group)

        # Cache status group
        status_group = QGroupBox(self.tr('Cache Status'))
        status_layout = QVBoxLayout(status_group)

        self.label_cache_status = QLabel()
        status_layout.addWidget(self.label_cache_status)

        btn_layout = QHBoxLayout()
        self.btn_clear_cache = QPushButton(self.tr('Clear Cache'))
        self.btn_clear_cache.clicked.connect(self._clear_cache)
        btn_layout.addWidget(self.btn_clear_cache)

        self.btn_clear_expired = QPushButton(self.tr('Clear Expired'))
        self.btn_clear_expired.clicked.connect(self._clear_expired_cache)
        btn_layout.addWidget(self.btn_clear_expired)

        btn_layout.addStretch()
        status_layout.addLayout(btn_layout)

        layout.addWidget(status_group)

        layout.addStretch()
        return widget

    def _load_settings(self):
        """Load current settings into the dialog."""
        # API Key
        api_key = self.settings.get_api_key()
        self.edit_api_key.setText(api_key)
        self._update_key_status()

        # General settings
        format_idx = self.combo_format.findData(self.settings.get_default_format())
        if format_idx >= 0:
            self.combo_format.setCurrentIndex(format_idx)

        lang_idx = self.combo_language.findData(self.settings.get_language())
        if lang_idx >= 0:
            self.combo_language.setCurrentIndex(lang_idx)

        self.spin_timeout.setValue(self.settings.get_timeout())
        self.spin_retry.setValue(self.settings.get_retry_count())
        self.spin_max_tiles.setValue(self.settings.get_max_tiles())

        self.check_auto_style.setChecked(self.settings.is_auto_style_enabled())
        self.check_auto_zoom.setChecked(self.settings.is_auto_zoom_enabled())

        # Cache settings
        self.check_cache_enabled.setChecked(self.settings.is_cache_enabled())
        self.spin_cache_hours.setValue(self.settings.get_cache_hours())
        self._update_cache_status()

    def _save_settings(self):
        """Save settings from dialog."""
        # API Key
        api_key = self.edit_api_key.text().strip()
        self.settings.set_api_key(api_key)

        # General settings
        self.settings.set_value('default_format', self.combo_format.currentData())
        self.settings.set_value('language', self.combo_language.currentData())
        self.settings.set_value('timeout', self.spin_timeout.value())
        self.settings.set_value('retry_count', self.spin_retry.value())
        self.settings.set_value('max_tiles', self.spin_max_tiles.value())
        self.settings.set_value('auto_style', self.check_auto_style.isChecked())
        self.settings.set_value('auto_zoom', self.check_auto_zoom.isChecked())

        # Cache settings
        self.settings.set_value('cache_enabled', self.check_cache_enabled.isChecked())
        self.settings.set_value('cache_hours', self.spin_cache_hours.value())

        self._update_key_status()

    def _on_ok(self):
        """Handle OK button click."""
        self._save_settings()
        self.accept()

    def _toggle_key_visibility(self, show: bool):
        """Toggle API key visibility."""
        if show:
            self.edit_api_key.setEchoMode(QLineEdit.Normal)
            self.btn_show_key.setText(self.tr('Hide'))
        else:
            self.edit_api_key.setEchoMode(QLineEdit.Password)
            self.btn_show_key.setText(self.tr('Show'))

    def _update_key_status(self):
        """Update the API key status label."""
        if self.settings.has_api_key():
            self.label_key_status.setText(
                self.tr('API key is configured')
            )
            self.label_key_status.setStyleSheet('color: green;')
        else:
            self.label_key_status.setText(
                self.tr('API key is not configured')
            )
            self.label_key_status.setStyleSheet('color: red;')

    def _test_api_key(self):
        """Test the current API key."""
        # Save current key first
        api_key = self.edit_api_key.text().strip()
        if not api_key:
            QMessageBox.warning(
                self,
                self.tr('No API Key'),
                self.tr('Please enter an API key to test.')
            )
            return

        self.settings.set_api_key(api_key)

        # Show progress
        progress = QProgressDialog(
            self.tr('Testing API key...'),
            self.tr('Cancel'),
            0, 0,
            self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        # Test the key
        client = ApiClient(self.settings)
        response = client.test_api_key()

        progress.close()

        if response.success:
            QMessageBox.information(
                self,
                self.tr('Success'),
                self.tr('API key is valid.')
            )
            self._update_key_status()
        else:
            QMessageBox.warning(
                self,
                self.tr('Failed'),
                self.tr('API key test failed: {}').format(response.error_message)
            )

    def _delete_api_key(self):
        """Delete the stored API key."""
        reply = QMessageBox.question(
            self,
            self.tr('Confirm Delete'),
            self.tr('Are you sure you want to delete the API key?'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.settings.delete_api_key()
            self.edit_api_key.clear()
            self._update_key_status()

    def _open_registration(self):
        """Open API registration page in browser."""
        webbrowser.open(self.API_REGISTRATION_URL)

    def _update_cache_status(self):
        """Update cache status label."""
        info = self.cache.get_cache_info()
        size_kb = info['size_bytes'] / 1024

        self.label_cache_status.setText(
            self.tr('Cached entries: {count}\nCache size: {size:.1f} KB').format(
                count=info['count'],
                size=size_kb
            )
        )

    def _clear_cache(self):
        """Clear all cache."""
        reply = QMessageBox.question(
            self,
            self.tr('Confirm Clear'),
            self.tr('Are you sure you want to clear all cached data?'),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            count = self.cache.clear()
            self._update_cache_status()
            QMessageBox.information(
                self,
                self.tr('Cache Cleared'),
                self.tr('Cleared {} cache entries.').format(count)
            )

    def _clear_expired_cache(self):
        """Clear only expired cache entries."""
        count = self.cache.clear_expired()
        self._update_cache_status()
        QMessageBox.information(
            self,
            self.tr('Expired Cache Cleared'),
            self.tr('Cleared {} expired cache entries.').format(count)
        )
