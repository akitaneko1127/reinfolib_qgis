# -*- coding: utf-8 -*-
"""
ReinfoLib for QGIS - Main Plugin Class

Copyright (C) 2024 Link Field
"""

import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.core import QgsApplication


class ReinfoLibPlugin:
    """QGIS Plugin Implementation for Real Estate Information Library API."""

    def __init__(self, iface):
        """Constructor.

        Args:
            iface: An interface instance that will be passed to this class
                which provides the hook by which you can manipulate the QGIS
                application at run time.
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # Initialize locale
        locale = QSettings().value('locale/userLocale', 'en_US')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            f'reinfolib_{locale}.qm'
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Plugin attributes
        self.actions = []
        self.menu = None
        self.toolbar = None

        # Dialog instances
        self.main_dialog = None
        self.settings_dialog = None

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        Args:
            message: String for translation.

        Returns:
            Translated version of message.
        """
        return QCoreApplication.translate('ReinfoLibPlugin', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None
    ):
        """Add a toolbar icon to the toolbar.

        Args:
            icon_path: Path to the icon for this action.
            text: Text that should be shown in menu items for this action.
            callback: Function to be called when the action is triggered.
            enabled_flag: A flag indicating if the action should be enabled
                by default. Defaults to True.
            add_to_menu: Flag indicating whether the action should also
                be added to the menu. Defaults to True.
            add_to_toolbar: Flag indicating whether the action should also
                be added to the toolbar. Defaults to True.
            status_tip: Optional text to show in a popup when mouse pointer
                hovers over the action.
            whats_this: Optional text to show in the status bar when the
                mouse pointer hovers over the action.
            parent: Parent widget for the new action. Defaults None.

        Returns:
            The action that was created.
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.menu.addAction(action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Create toolbar
        self.toolbar = self.iface.addToolBar(self.tr('ReinfoLib'))
        self.toolbar.setObjectName('ReinfoLibToolbar')

        # Create menu under Web menu
        self.menu = QMenu(self.tr('ReinfoLib - Real Estate Info'))
        self.iface.webMenu().addMenu(self.menu)

        # Get icon path
        icon_path = os.path.join(self.plugin_dir, 'icon.png')

        # Add main action - Data Fetch
        self.add_action(
            icon_path,
            self.tr('Fetch Data...'),
            callback=self.run_main_dialog,
            parent=self.iface.mainWindow(),
            status_tip=self.tr('Open Real Estate Information Library data fetch dialog')
        )

        # Add separator
        self.menu.addSeparator()

        # Add settings action
        settings_icon = QgsApplication.getThemeIcon('/mActionOptions.svg')
        settings_action = QAction(
            settings_icon,
            self.tr('Settings...'),
            self.iface.mainWindow()
        )
        settings_action.triggered.connect(self.run_settings_dialog)
        settings_action.setStatusTip(self.tr('Configure API key and plugin settings'))
        self.menu.addAction(settings_action)
        self.actions.append(settings_action)

        # Add separator
        self.menu.addSeparator()

        # Add help action
        help_icon = QgsApplication.getThemeIcon('/mActionHelpContents.svg')
        help_action = QAction(
            help_icon,
            self.tr('Help'),
            self.iface.mainWindow()
        )
        help_action.triggered.connect(self.show_help)
        self.menu.addAction(help_action)
        self.actions.append(help_action)

        # Add API registration link
        api_action = QAction(
            self.tr('Apply for API Key'),
            self.iface.mainWindow()
        )
        api_action.triggered.connect(self.open_api_registration)
        self.menu.addAction(api_action)
        self.actions.append(api_action)

        # Add about action
        self.menu.addSeparator()
        about_action = QAction(
            self.tr('About...'),
            self.iface.mainWindow()
        )
        about_action.triggered.connect(self.show_about)
        self.menu.addAction(about_action)
        self.actions.append(about_action)

    def unload(self):
        """Remove the plugin menu item and icon from QGIS GUI."""
        # Remove toolbar
        if self.toolbar:
            del self.toolbar

        # Remove menu
        if self.menu:
            self.iface.webMenu().removeAction(self.menu.menuAction())

        # Clean up dialogs
        if self.main_dialog:
            self.main_dialog.close()
            self.main_dialog = None

        if self.settings_dialog:
            self.settings_dialog.close()
            self.settings_dialog = None

    def run_main_dialog(self):
        """Run the main data fetch dialog."""
        from .gui.main_dialog import MainDialog

        if self.main_dialog is None:
            self.main_dialog = MainDialog(self.iface, parent=self.iface.mainWindow())

        self.main_dialog.show()
        self.main_dialog.raise_()
        self.main_dialog.activateWindow()

    def run_settings_dialog(self):
        """Run the settings dialog."""
        from .gui.settings_dialog import SettingsDialog

        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(parent=self.iface.mainWindow())

        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def show_help(self):
        """Open online help in browser."""
        import webbrowser
        webbrowser.open('https://github.com/akitaneko1127/reinfolib_qgis#readme')

    def open_api_registration(self):
        """Open API registration page in browser."""
        import webbrowser
        webbrowser.open('https://www.reinfolib.mlit.go.jp/help/apiManual/')

    def show_about(self):
        """Show about dialog."""
        from qgis.PyQt.QtWidgets import QMessageBox

        about_text = self.tr(
            '<h3>ReinfoLib for QGIS</h3>'
            '<p>Version 1.0.1</p>'
            '<p>Access Japan\'s Real Estate Information Library API directly from QGIS.</p>'
            '<p><b>Developer:</b> Link Field</p>'
            '<p><b>Email:</b> info@linkfield.co.jp</p>'
            '<p><b>License:</b> GPL-3.0</p>'
            '<p><a href="https://github.com/akitaneko1127/reinfolib_qgis">GitHub Repository</a></p>'
        )

        QMessageBox.about(
            self.iface.mainWindow(),
            self.tr('About ReinfoLib for QGIS'),
            about_text
        )
