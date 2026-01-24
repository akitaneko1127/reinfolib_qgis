# -*- coding: utf-8 -*-
"""
Main Dialog for ReinfoLib QGIS Plugin

Main dialog for fetching data from the Real Estate Information Library API.
"""

import datetime

from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal, QSize
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QPushButton,
    QToolButton,
    QComboBox,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QMessageBox,
    QCheckBox,
    QFileDialog,
    QLineEdit,
    QSpinBox,
)
from qgis.core import QgsProject, QgsRectangle, QgsCoordinateTransform, QgsApplication
from qgis.gui import QgsMapCanvas

from ..core.settings_manager import SettingsManager
from ..core.api_client import ApiClient
from ..core.api_definitions import ApiDefinitions
from ..core.data_converter import DataConverter
from ..core.cache_manager import CacheManager
from ..styles.style_manager import StyleManager


class FetchWorker(QThread):
    """Worker thread for fetching API data."""

    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(object)  # ApiResponse
    error = pyqtSignal(str)

    def __init__(
        self,
        client: ApiClient,
        api_id: str,
        extent: QgsRectangle,
        zoom: int = None,
        extra_params: dict = None
    ):
        super().__init__()
        self.client = client
        self.api_id = api_id
        self.extent = extent
        self.zoom = zoom
        self.extra_params = extra_params

    def run(self):
        """Execute the fetch operation."""
        try:
            response = self.client.fetch_tiles_for_extent(
                self.api_id,
                self.extent.yMinimum(),
                self.extent.xMinimum(),
                self.extent.yMaximum(),
                self.extent.xMaximum(),
                self.zoom,
                progress_callback=lambda c, t: self.progress.emit(c, t),
                extra_params=self.extra_params
            )
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class MainDialog(QDialog):
    """Main dialog for data fetching."""

    # Prefecture codes and names
    PREFECTURES = [
        ('01', '北海道'), ('02', '青森県'), ('03', '岩手県'), ('04', '宮城県'),
        ('05', '秋田県'), ('06', '山形県'), ('07', '福島県'), ('08', '茨城県'),
        ('09', '栃木県'), ('10', '群馬県'), ('11', '埼玉県'), ('12', '千葉県'),
        ('13', '東京都'), ('14', '神奈川県'), ('15', '新潟県'), ('16', '富山県'),
        ('17', '石川県'), ('18', '福井県'), ('19', '山梨県'), ('20', '長野県'),
        ('21', '岐阜県'), ('22', '静岡県'), ('23', '愛知県'), ('24', '三重県'),
        ('25', '滋賀県'), ('26', '京都府'), ('27', '大阪府'), ('28', '兵庫県'),
        ('29', '奈良県'), ('30', '和歌山県'), ('31', '鳥取県'), ('32', '島根県'),
        ('33', '岡山県'), ('34', '広島県'), ('35', '山口県'), ('36', '徳島県'),
        ('37', '香川県'), ('38', '愛媛県'), ('39', '高知県'), ('40', '福岡県'),
        ('41', '佐賀県'), ('42', '長崎県'), ('43', '熊本県'), ('44', '大分県'),
        ('45', '宮崎県'), ('46', '鹿児島県'), ('47', '沖縄県'),
    ]

    # Prefecture approximate center coordinates (lat, lon)
    PREFECTURE_CENTERS = {
        '01': (43.06, 141.35),  # 北海道
        '02': (40.82, 140.74),  # 青森県
        '03': (39.70, 141.15),  # 岩手県
        '04': (38.27, 140.87),  # 宮城県
        '05': (39.72, 140.10),  # 秋田県
        '06': (38.24, 140.33),  # 山形県
        '07': (37.75, 140.47),  # 福島県
        '08': (36.34, 140.45),  # 茨城県
        '09': (36.57, 139.88),  # 栃木県
        '10': (36.39, 139.06),  # 群馬県
        '11': (35.86, 139.65),  # 埼玉県
        '12': (35.61, 140.12),  # 千葉県
        '13': (35.69, 139.69),  # 東京都
        '14': (35.45, 139.64),  # 神奈川県
        '15': (37.90, 139.02),  # 新潟県
        '16': (36.70, 137.21),  # 富山県
        '17': (36.59, 136.63),  # 石川県
        '18': (36.07, 136.22),  # 福井県
        '19': (35.66, 138.57),  # 山梨県
        '20': (36.65, 138.18),  # 長野県
        '21': (35.39, 136.72),  # 岐阜県
        '22': (34.98, 138.38),  # 静岡県
        '23': (35.18, 136.91),  # 愛知県
        '24': (34.73, 136.51),  # 三重県
        '25': (35.00, 135.87),  # 滋賀県
        '26': (35.02, 135.76),  # 京都府
        '27': (34.69, 135.50),  # 大阪府
        '28': (34.69, 135.18),  # 兵庫県
        '29': (34.69, 135.83),  # 奈良県
        '30': (34.23, 135.17),  # 和歌山県
        '31': (35.50, 134.24),  # 鳥取県
        '32': (35.47, 133.05),  # 島根県
        '33': (34.66, 133.93),  # 岡山県
        '34': (34.40, 132.46),  # 広島県
        '35': (34.19, 131.47),  # 山口県
        '36': (34.07, 134.56),  # 徳島県
        '37': (34.34, 134.04),  # 香川県
        '38': (33.84, 132.77),  # 愛媛県
        '39': (33.56, 133.53),  # 高知県
        '40': (33.59, 130.40),  # 福岡県
        '41': (33.25, 130.30),  # 佐賀県
        '42': (32.74, 129.87),  # 長崎県
        '43': (32.79, 130.74),  # 熊本県
        '44': (33.24, 131.61),  # 大分県
        '45': (31.91, 131.42),  # 宮崎県
        '46': (31.56, 130.56),  # 鹿児島県
        '47': (26.21, 127.68),  # 沖縄県
    }

    def __init__(self, iface, parent=None):
        """Initialize the main dialog."""
        super().__init__(parent)
        self.iface = iface
        self.canvas: QgsMapCanvas = iface.mapCanvas()
        self.settings = SettingsManager()
        self.client = ApiClient(self.settings)
        self.cache = CacheManager(self.settings)
        self.worker = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle('不動産情報ライブラリ - データ取得')
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        layout = QVBoxLayout(self)

        # API key warning label (will be updated dynamically)
        self.warning_label = QLabel(
            '警告: APIキーが設定されていません。設定タブでAPIキーを設定してください。'
        )
        self.warning_label.setStyleSheet('color: red; font-weight: bold;')
        self.warning_label.setWordWrap(True)
        self.warning_label.setVisible(not self.settings.has_api_key())
        layout.addWidget(self.warning_label)

        # API category tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs for each category
        for cat_key in ApiDefinitions.get_all_categories():
            cat_name = ApiDefinitions.get_category_name(cat_key, 'ja')
            tab = self._create_category_tab(cat_key)
            self.tabs.addTab(tab, cat_name)

        # Add Settings tab after all category tabs
        settings_tab = self._create_settings_tab()
        self.tabs.addTab(settings_tab, '設定')

        # Connect tab change to update UI
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # Extent selection group
        extent_group = QGroupBox('範囲選択')
        extent_layout = QVBoxLayout(extent_group)

        self.combo_extent = QComboBox()
        self.combo_extent.addItem('現在の地図範囲', 'canvas')
        self.combo_extent.addItem('都道府県で選択', 'prefecture')
        self.combo_extent.currentIndexChanged.connect(self._on_extent_changed)
        extent_layout.addWidget(self.combo_extent)

        # Prefecture selector (hidden by default)
        self.prefecture_widget = QWidget()
        pref_layout = QHBoxLayout(self.prefecture_widget)
        pref_layout.setContentsMargins(0, 0, 0, 0)

        self.combo_prefecture = QComboBox()
        for code, name in self.PREFECTURES:
            self.combo_prefecture.addItem(name, code)
        pref_layout.addWidget(self.combo_prefecture)

        self.prefecture_widget.hide()
        extent_layout.addWidget(self.prefecture_widget)

        layout.addWidget(extent_group)

        # Price API parameters group (for non-tile APIs)
        self.price_params_group = QGroupBox('価格情報パラメータ')
        price_layout = QFormLayout(self.price_params_group)

        # Year selection (data usually available up to previous year)
        self.combo_year = QComboBox()
        current_year = datetime.datetime.now().year
        # Start from previous year as current year data may not be available
        for year in range(current_year - 1, 2005, -1):
            self.combo_year.addItem(f'{year}年', str(year))
        price_layout.addRow('取引時期:', self.combo_year)

        # Quarter selection
        self.combo_quarter = QComboBox()
        self.combo_quarter.addItem('全期間', '')
        self.combo_quarter.addItem('第1四半期（1-3月）', '1')
        self.combo_quarter.addItem('第2四半期（4-6月）', '2')
        self.combo_quarter.addItem('第3四半期（7-9月）', '3')
        self.combo_quarter.addItem('第4四半期（10-12月）', '4')
        price_layout.addRow('四半期:', self.combo_quarter)

        # Area selection for price API with refresh button
        price_area_widget = QWidget()
        price_area_layout = QHBoxLayout(price_area_widget)
        price_area_layout.setContentsMargins(0, 0, 0, 0)

        self.combo_price_area = QComboBox()
        for code, name in self.PREFECTURES:
            self.combo_price_area.addItem(name, code)
        price_area_layout.addWidget(self.combo_price_area)

        # Refresh button to re-detect prefecture from map
        self.btn_refresh_prefecture = QToolButton()
        self.btn_refresh_prefecture.setIcon(QgsApplication.getThemeIcon('/mActionRefresh.svg'))
        self.btn_refresh_prefecture.setToolTip('現在の地図範囲から都道府県を再取得')
        self.btn_refresh_prefecture.clicked.connect(self._update_prefecture_from_map)
        price_area_layout.addWidget(self.btn_refresh_prefecture)

        price_layout.addRow('都道府県:', price_area_widget)

        # Debug info label for prefecture detection
        self.label_pref_debug = QLabel('')
        self.label_pref_debug.setStyleSheet('color: gray; font-size: 10px;')
        price_layout.addRow('', self.label_pref_debug)

        self.price_params_group.hide()
        layout.addWidget(self.price_params_group)

        # XKT025 (大規模盛土造成地) specific options
        self.xkt025_params_group = QGroupBox('大規模盛土造成地オプション')
        xkt025_layout = QFormLayout(self.xkt025_params_group)

        self.combo_xkt025_field = QComboBox()
        self.combo_xkt025_field.addItem('地形区分 (topography)', 'topography')
        self.combo_xkt025_field.addItem('液状化リスク (note)', 'note')
        # Set current selection from settings
        current_field = self.settings.get_xkt025_style_field()
        for i in range(self.combo_xkt025_field.count()):
            if self.combo_xkt025_field.itemData(i) == current_field:
                self.combo_xkt025_field.setCurrentIndex(i)
                break
        self.combo_xkt025_field.currentIndexChanged.connect(self._on_xkt025_field_changed)
        xkt025_layout.addRow('色分け基準:', self.combo_xkt025_field)

        self.xkt025_params_group.hide()
        layout.addWidget(self.xkt025_params_group)

        # XKT023 (市区町村役場等) specific options
        self.xkt023_params_group = QGroupBox('市区町村役場等オプション')
        xkt023_layout = QFormLayout(self.xkt023_params_group)

        self.combo_xkt023_field = QComboBox()
        self.combo_xkt023_field.addItem('市区町村名 (city_name)', 'city_name')
        self.combo_xkt023_field.addItem('施設名 (plan_name)', 'plan_name')
        # Set current selection from settings
        current_xkt023_field = self.settings.get_xkt023_style_field()
        for i in range(self.combo_xkt023_field.count()):
            if self.combo_xkt023_field.itemData(i) == current_xkt023_field:
                self.combo_xkt023_field.setCurrentIndex(i)
                break
        self.combo_xkt023_field.currentIndexChanged.connect(self._on_xkt023_field_changed)
        xkt023_layout.addRow('色分け基準:', self.combo_xkt023_field)

        self.xkt023_params_group.hide()
        layout.addWidget(self.xkt023_params_group)

        # XKT013 (将来推計人口メッシュ) specific options
        self.xkt013_params_group = QGroupBox('将来推計人口メッシュオプション')
        xkt013_layout = QFormLayout(self.xkt013_params_group)

        # Year selection
        self.combo_xkt013_year = QComboBox()
        self.combo_xkt013_year.addItem('令和2年 (2020年)', '2020')
        self.combo_xkt013_year.addItem('令和7年 (2025年)', '2025')
        self.combo_xkt013_year.addItem('令和12年 (2030年)', '2030')
        self.combo_xkt013_year.addItem('令和17年 (2035年)', '2035')
        self.combo_xkt013_year.addItem('令和22年 (2040年)', '2040')
        self.combo_xkt013_year.addItem('令和27年 (2045年)', '2045')
        self.combo_xkt013_year.addItem('令和32年 (2050年)', '2050')
        current_xkt013_year = self.settings.get_xkt013_year()
        for i in range(self.combo_xkt013_year.count()):
            if self.combo_xkt013_year.itemData(i) == current_xkt013_year:
                self.combo_xkt013_year.setCurrentIndex(i)
                break
        self.combo_xkt013_year.currentIndexChanged.connect(self._on_xkt013_option_changed)
        xkt013_layout.addRow('表示年:', self.combo_xkt013_year)

        # Data type selection
        self.combo_xkt013_data_type = QComboBox()
        self.combo_xkt013_data_type.addItem('総人口', 'total')
        self.combo_xkt013_data_type.addItem('年齢階層別人口', 'age_group')
        self.combo_xkt013_data_type.addItem('年齢区分別人口', 'age_category')
        self.combo_xkt013_data_type.addItem('人口比率', 'ratio')
        current_data_type = self.settings.get_xkt013_data_type()
        for i in range(self.combo_xkt013_data_type.count()):
            if self.combo_xkt013_data_type.itemData(i) == current_data_type:
                self.combo_xkt013_data_type.setCurrentIndex(i)
                break
        self.combo_xkt013_data_type.currentIndexChanged.connect(self._on_xkt013_data_type_changed)
        xkt013_layout.addRow('データ種別:', self.combo_xkt013_data_type)

        # Field selection (depends on data type)
        self.combo_xkt013_field = QComboBox()
        self._update_xkt013_field_options()
        self.combo_xkt013_field.currentIndexChanged.connect(self._on_xkt013_option_changed)
        xkt013_layout.addRow('項目:', self.combo_xkt013_field)

        self.xkt013_params_group.hide()
        layout.addWidget(self.xkt013_params_group)

        # Output settings group
        output_group = QGroupBox('出力設定')
        output_layout = QFormLayout(output_group)

        self.combo_output = QComboBox()
        self.combo_output.addItem('メモリレイヤー', 'memory')
        self.combo_output.addItem('GeoPackage (.gpkg)', 'gpkg')
        self.combo_output.addItem('GeoJSON (.geojson)', 'geojson')
        self.combo_output.addItem('Shapefile (.shp)', 'shp')
        self.combo_output.currentIndexChanged.connect(self._on_output_changed)
        output_layout.addRow('出力形式:', self.combo_output)

        # File path (hidden for memory)
        file_layout = QHBoxLayout()
        self.edit_file_path = QLineEdit()
        self.edit_file_path.setPlaceholderText('出力ファイルを選択...')
        file_layout.addWidget(self.edit_file_path)

        self.btn_browse = QPushButton('参照...')
        self.btn_browse.clicked.connect(self._browse_output)
        file_layout.addWidget(self.btn_browse)

        self.file_widget = QWidget()
        self.file_widget.setLayout(file_layout)
        self.file_widget.hide()
        output_layout.addRow(self.file_widget)

        self.check_add_to_map = QCheckBox('地図に追加')
        self.check_add_to_map.setChecked(True)
        output_layout.addRow(self.check_add_to_map)

        self.check_zoom_to_layer = QCheckBox('レイヤーにズーム')
        self.check_zoom_to_layer.setChecked(self.settings.is_auto_zoom_enabled())
        output_layout.addRow(self.check_zoom_to_layer)

        layout.addWidget(output_group)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)

        # Status label
        self.label_status = QLabel()
        layout.addWidget(self.label_status)

        # Buttons
        button_layout = QHBoxLayout()

        self.btn_fetch = QPushButton('データ取得')
        self.btn_fetch.clicked.connect(self._on_fetch)
        button_layout.addWidget(self.btn_fetch)

        self.btn_cancel = QPushButton('キャンセル')
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_cancel.setEnabled(False)
        button_layout.addWidget(self.btn_cancel)

        button_layout.addStretch()

        self.btn_close = QPushButton('閉じる')
        self.btn_close.clicked.connect(self.close)
        button_layout.addWidget(self.btn_close)

        layout.addLayout(button_layout)

    def _create_category_tab(self, category: str) -> QWidget:
        """Create a tab for an API category."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.SingleSelection)
        list_widget.itemSelectionChanged.connect(self._on_api_selection_changed)

        # Populate APIs directly during tab creation
        apis = ApiDefinitions.get_apis_by_category(category)
        for api in apis:
            item = QListWidgetItem(f'{api.name_ja} ({api.api_id})')
            item.setData(Qt.UserRole, api.api_id)
            item.setToolTip(api.description_ja)
            list_widget.addItem(item)

        # Store reference
        setattr(self, f'list_{category}', list_widget)

        layout.addWidget(list_widget)
        return widget

    def _on_api_selection_changed(self):
        """Handle API selection change to show/hide parameter groups."""
        # Check if price_params_group exists (might be called during init)
        if not hasattr(self, 'price_params_group'):
            return

        api_id = self._get_selected_api()
        if api_id:
            api_info = ApiDefinitions.get_api(api_id)
            # Show price params for all price category APIs (including tile-based XPT001, XPT002)
            if api_info and api_info.category == 'price':
                self.price_params_group.show()
                # Auto-detect prefecture when showing price params
                extent_type = self.combo_extent.currentData()
                if extent_type == 'canvas':
                    self._update_prefecture_from_map()
            else:
                self.price_params_group.hide()

            # Show XKT025 options for large fill area
            if hasattr(self, 'xkt025_params_group'):
                if api_id == 'XKT025':
                    self.xkt025_params_group.show()
                else:
                    self.xkt025_params_group.hide()

            # Show XKT023 options for municipal offices
            if hasattr(self, 'xkt023_params_group'):
                if api_id == 'XKT023':
                    self.xkt023_params_group.show()
                else:
                    self.xkt023_params_group.hide()

            # Show XKT013 options for population mesh
            if hasattr(self, 'xkt013_params_group'):
                if api_id == 'XKT013':
                    self.xkt013_params_group.show()
                else:
                    self.xkt013_params_group.hide()
        else:
            self.price_params_group.hide()
            if hasattr(self, 'xkt025_params_group'):
                self.xkt025_params_group.hide()
            if hasattr(self, 'xkt023_params_group'):
                self.xkt023_params_group.hide()
            if hasattr(self, 'xkt013_params_group'):
                self.xkt013_params_group.hide()

    def _on_xkt025_field_changed(self, index: int):
        """Handle XKT025 style field selection change."""
        field = self.combo_xkt025_field.currentData()
        self.settings.set_xkt025_style_field(field)
        # Re-apply style to existing XKT025 layer if present
        self._reapply_style_to_layer('XKT025', '大規模盛土造成地')

    def _on_xkt023_field_changed(self, index: int):
        """Handle XKT023 style field selection change."""
        field = self.combo_xkt023_field.currentData()
        self.settings.set_xkt023_style_field(field)
        # Re-apply style to existing XKT023 layer if present
        self._reapply_style_to_layer('XKT023', '市区町村役場等')

    def _update_xkt013_field_options(self):
        """Update XKT013 field combo box based on selected data type."""
        self.combo_xkt013_field.blockSignals(True)
        self.combo_xkt013_field.clear()

        data_type = self.combo_xkt013_data_type.currentData()

        if data_type == 'total':
            self.combo_xkt013_field.addItem('総人口 (PTN)', 'PTN')
        elif data_type == 'age_group':
            # Organize by age category for clarity
            self.combo_xkt013_field.addItem('── 年少人口 (0-14歳) ──', '')
            age_groups_young = [
                ('PT01', '0～4歳'), ('PT02', '5～9歳'), ('PT03', '10～14歳'),
            ]
            for code, label in age_groups_young:
                self.combo_xkt013_field.addItem(f'  {label} ({code})', code)

            self.combo_xkt013_field.addItem('── 生産年齢人口 (15-64歳) ──', '')
            age_groups_working = [
                ('PT04', '15～19歳'), ('PT05', '20～24歳'), ('PT06', '25～29歳'),
                ('PT07', '30～34歳'), ('PT08', '35～39歳'), ('PT09', '40～44歳'),
                ('PT10', '45～49歳'), ('PT11', '50～54歳'), ('PT12', '55～59歳'),
                ('PT13', '60～64歳'),
            ]
            for code, label in age_groups_working:
                self.combo_xkt013_field.addItem(f'  {label} ({code})', code)

            self.combo_xkt013_field.addItem('── 高齢者人口 (65歳以上) ──', '')
            age_groups_elderly = [
                ('PT14', '65～69歳'), ('PT15', '70～74歳'),
                ('PT16', '75～79歳'), ('PT17', '80～84歳'), ('PT18', '85～89歳'),
                ('PT19', '90～94歳'), ('PT20', '95歳以上'),
            ]
            for code, label in age_groups_elderly:
                self.combo_xkt013_field.addItem(f'  {label} ({code})', code)
        elif data_type == 'age_category':
            categories = [
                ('PTA', '0～14歳 (年少人口)'),
                ('PTB', '15～64歳 (生産年齢人口)'),
                ('PTC', '65歳以上 (高齢者人口)'),
                ('PTD', '75歳以上'),
                ('PTE', '80歳以上'),
            ]
            for code, label in categories:
                self.combo_xkt013_field.addItem(f'{label} ({code})', code)
            # Add note about detailed breakdown
            self.combo_xkt013_field.addItem('─────────────────', '')
            self.combo_xkt013_field.addItem('※ 5歳刻みは「年齢階層別人口」で選択', '')
        elif data_type == 'ratio':
            self.combo_xkt013_field.addItem('── 年少人口比率 ──', '')
            self.combo_xkt013_field.addItem('  0～14歳比率 (RTA)', 'RTA')

            self.combo_xkt013_field.addItem('── 生産年齢人口比率 ──', '')
            self.combo_xkt013_field.addItem('  15～64歳比率 (RTB)', 'RTB')

            self.combo_xkt013_field.addItem('── 高齢者人口比率 ──', '')
            self.combo_xkt013_field.addItem('  65歳以上比率 (RTC)', 'RTC')
            self.combo_xkt013_field.addItem('  75歳以上比率 (RTD)', 'RTD')
            self.combo_xkt013_field.addItem('  80歳以上比率 (RTE)', 'RTE')

        # Restore previous selection if possible
        current_field = self.settings.get_xkt013_field()
        for i in range(self.combo_xkt013_field.count()):
            if self.combo_xkt013_field.itemData(i) == current_field:
                self.combo_xkt013_field.setCurrentIndex(i)
                break

        self.combo_xkt013_field.blockSignals(False)

    def _on_xkt013_data_type_changed(self, index: int):
        """Handle XKT013 data type selection change."""
        data_type = self.combo_xkt013_data_type.currentData()
        self.settings.set_xkt013_data_type(data_type)
        self._update_xkt013_field_options()
        self._on_xkt013_option_changed(0)

    def _on_xkt013_option_changed(self, index: int):
        """Handle XKT013 option change (year or field)."""
        year = self.combo_xkt013_year.currentData()
        field = self.combo_xkt013_field.currentData()
        self.settings.set_xkt013_year(year)
        if field:
            self.settings.set_xkt013_field(field)
        # Re-apply style to existing XKT013 layer if present
        self._reapply_style_to_layer('XKT013', '将来推計人口メッシュ')

    def _reapply_style_to_layer(self, api_id: str, layer_name_pattern: str):
        """Re-apply style to an existing layer in the project."""
        from qgis.core import QgsProject, QgsMessageLog, Qgis

        # Find layer by name pattern
        for layer in QgsProject.instance().mapLayers().values():
            if layer_name_pattern in layer.name():
                QgsMessageLog.logMessage(
                    f'Re-applying style to layer: {layer.name()}',
                    'ReinfoLib', Qgis.Info
                )
                StyleManager.apply_style(layer, api_id)
                return True
        return False

    def _create_settings_tab(self) -> QWidget:
        """Create the settings tab with API key input."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # API Key group
        api_group = QGroupBox('APIキー')
        api_layout = QVBoxLayout(api_group)

        # API key input row
        key_layout = QHBoxLayout()

        self.edit_api_key = QLineEdit()
        self.edit_api_key.setEchoMode(QLineEdit.Password)
        self.edit_api_key.setPlaceholderText('APIキーを入力してください')
        # Load existing key
        existing_key = self.settings.get_api_key()
        if existing_key:
            self.edit_api_key.setText(existing_key)
        key_layout.addWidget(self.edit_api_key)

        # Eye icon button for show/hide
        self.btn_toggle_key = QToolButton()
        self.btn_toggle_key.setCheckable(True)
        self.btn_toggle_key.setToolTip('APIキーの表示/非表示')
        # Use QGIS theme icon
        self.btn_toggle_key.setIcon(QgsApplication.getThemeIcon('/mActionShowAllLayers.svg'))
        self.btn_toggle_key.setIconSize(QSize(20, 20))
        self.btn_toggle_key.toggled.connect(self._toggle_api_key_visibility)
        key_layout.addWidget(self.btn_toggle_key)

        api_layout.addLayout(key_layout)

        # Status label
        self.label_api_status = QLabel()
        self._update_api_key_status()
        api_layout.addWidget(self.label_api_status)

        # Buttons row
        btn_layout = QHBoxLayout()

        self.btn_save_key = QPushButton('保存')
        self.btn_save_key.clicked.connect(self._save_api_key)
        btn_layout.addWidget(self.btn_save_key)

        self.btn_test_key = QPushButton('テスト')
        self.btn_test_key.clicked.connect(self._test_api_key)
        btn_layout.addWidget(self.btn_test_key)

        self.btn_delete_key = QPushButton('削除')
        self.btn_delete_key.clicked.connect(self._delete_api_key)
        btn_layout.addWidget(self.btn_delete_key)

        btn_layout.addStretch()
        api_layout.addLayout(btn_layout)

        # Help text
        help_label = QLabel(
            '<a href="https://www.reinfolib.mlit.go.jp/help/apiManual/">APIキーを申請する（無料）</a>'
        )
        help_label.setOpenExternalLinks(True)
        api_layout.addWidget(help_label)

        layout.addWidget(api_group)

        # General settings group
        general_group = QGroupBox('一般設定')
        general_layout = QFormLayout(general_group)

        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(5, 120)
        self.spin_timeout.setValue(self.settings.get_timeout())
        self.spin_timeout.setSuffix(' 秒')
        self.spin_timeout.valueChanged.connect(
            lambda v: self.settings.set_value('timeout', v)
        )
        general_layout.addRow('タイムアウト:', self.spin_timeout)

        self.spin_max_tiles = QSpinBox()
        self.spin_max_tiles.setRange(1, 500)
        self.spin_max_tiles.setValue(self.settings.get_max_tiles())
        self.spin_max_tiles.valueChanged.connect(
            lambda v: self.settings.set_value('max_tiles', v)
        )
        general_layout.addRow('最大タイル数:', self.spin_max_tiles)

        self.check_auto_style = QCheckBox('自動スタイルを適用')
        self.check_auto_style.setChecked(self.settings.is_auto_style_enabled())
        self.check_auto_style.toggled.connect(
            lambda v: self.settings.set_value('auto_style', v)
        )
        general_layout.addRow(self.check_auto_style)

        layout.addWidget(general_group)

        layout.addStretch()
        return widget

    def _toggle_api_key_visibility(self, show: bool):
        """Toggle API key visibility."""
        if show:
            self.edit_api_key.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_key.setIcon(QgsApplication.getThemeIcon('/mActionHideAllLayers.svg'))
            self.btn_toggle_key.setToolTip('APIキーを非表示')
        else:
            self.edit_api_key.setEchoMode(QLineEdit.Password)
            self.btn_toggle_key.setIcon(QgsApplication.getThemeIcon('/mActionShowAllLayers.svg'))
            self.btn_toggle_key.setToolTip('APIキーを表示')

    def _update_api_key_status(self):
        """Update API key status label."""
        if self.settings.has_api_key():
            self.label_api_status.setText('APIキーが設定されています')
            self.label_api_status.setStyleSheet('color: green;')
        else:
            self.label_api_status.setText('APIキーが設定されていません')
            self.label_api_status.setStyleSheet('color: red;')

    def _save_api_key(self):
        """Save the API key."""
        api_key = self.edit_api_key.text().strip()
        if api_key:
            self.settings.set_api_key(api_key)
            self._update_api_key_status()
            self.warning_label.setVisible(False)
            # Recreate client with new key
            self.client = ApiClient(self.settings)
            QMessageBox.information(
                self,
                '保存完了',
                'APIキーを保存しました。'
            )
        else:
            QMessageBox.warning(
                self,
                '入力エラー',
                'APIキーを入力してください。'
            )

    def _test_api_key(self):
        """Test the API key."""
        api_key = self.edit_api_key.text().strip()
        if not api_key:
            QMessageBox.warning(
                self,
                '入力エラー',
                'テストするAPIキーを入力してください。'
            )
            return

        # Temporarily save the key for testing
        self.settings.set_api_key(api_key)
        self.client = ApiClient(self.settings)

        self.label_api_status.setText('テスト中...')
        self.label_api_status.setStyleSheet('color: blue;')

        # Test the key
        response = self.client.test_api_key()

        if response.success:
            self._update_api_key_status()
            self.warning_label.setVisible(False)
            QMessageBox.information(
                self,
                '成功',
                'APIキーは有効です！'
            )
        else:
            self.label_api_status.setText('APIキーテスト失敗')
            self.label_api_status.setStyleSheet('color: red;')
            QMessageBox.warning(
                self,
                '失敗',
                'APIキーテストに失敗しました: {}'.format(response.error_message)
            )

    def _delete_api_key(self):
        """Delete the API key."""
        reply = QMessageBox.question(
            self,
            '削除確認',
            'APIキーを削除してもよろしいですか？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.settings.delete_api_key()
            self.edit_api_key.clear()
            self._update_api_key_status()
            self.warning_label.setVisible(True)
            QMessageBox.information(
                self,
                '削除完了',
                'APIキーを削除しました。'
            )

    def _populate_apis(self):
        """Populate API lists in each category tab."""
        for cat_key in ApiDefinitions.get_all_categories():
            list_widget = getattr(self, f'list_{cat_key}', None)
            if not list_widget:
                continue

            apis = ApiDefinitions.get_apis_by_category(cat_key)
            for api in apis:
                item = QListWidgetItem(f'{api.name_ja} ({api.api_id})')
                item.setData(Qt.UserRole, api.api_id)
                item.setToolTip(api.description_ja)
                list_widget.addItem(item)

    def _get_selected_api(self) -> str:
        """Get the currently selected API ID."""
        current_tab = self.tabs.currentIndex()
        categories = ApiDefinitions.get_all_categories()

        # Settings tab is the last tab, skip it
        if current_tab >= len(categories):
            return None

        cat_key = categories[current_tab]
        list_widget = getattr(self, f'list_{cat_key}', None)
        if list_widget and list_widget.currentItem():
            return list_widget.currentItem().data(Qt.UserRole)

        return None

    def _on_tab_changed(self, index: int):
        """Handle tab change to show/hide parameter groups."""
        categories = ApiDefinitions.get_all_categories()
        # Disable fetch button on Settings tab
        is_settings_tab = index >= len(categories)
        self.btn_fetch.setEnabled(not is_settings_tab)

        if is_settings_tab:
            # Hide parameter groups on settings tab
            if hasattr(self, 'price_params_group'):
                self.price_params_group.hide()
        else:
            self._on_api_selection_changed()

    def _on_extent_changed(self, index: int):
        """Handle extent selection change."""
        extent_type = self.combo_extent.currentData()
        self.prefecture_widget.setVisible(extent_type == 'prefecture')

        # Auto-detect prefecture from map extent
        if extent_type == 'canvas' and hasattr(self, 'combo_price_area'):
            self._update_prefecture_from_map()

    def _update_prefecture_from_map(self):
        """Update prefecture dropdown based on current map center."""
        from qgis.core import QgsCoordinateReferenceSystem, QgsMessageLog, Qgis

        try:
            # Get map center
            center = self.canvas.center()
            canvas_crs = self.canvas.mapSettings().destinationCrs()

            # Transform to WGS84 if needed
            if canvas_crs.authid() != 'EPSG:4326':
                wgs84 = QgsCoordinateReferenceSystem('EPSG:4326')
                transform = QgsCoordinateTransform(
                    canvas_crs,
                    wgs84,
                    QgsProject.instance()
                )
                center = transform.transform(center)

            lat, lon = center.y(), center.x()

            # Log for debugging
            QgsMessageLog.logMessage(
                f'Map center: lat={lat:.4f}, lon={lon:.4f}',
                'ReinfoLib', Qgis.Info
            )

            # Check if coordinates are within Japan (roughly)
            # Japan: lat 24-46, lon 122-154
            if not (24.0 <= lat <= 46.0 and 122.0 <= lon <= 154.0):
                QgsMessageLog.logMessage(
                    f'Coordinates outside Japan, skipping prefecture detection',
                    'ReinfoLib', Qgis.Info
                )
                # Update debug label
                if hasattr(self, 'label_pref_debug'):
                    self.label_pref_debug.setText(f'座標: ({lat:.4f}, {lon:.4f}) - 日本国外')
                    self.label_pref_debug.setStyleSheet('color: red; font-size: 10px;')
                return

            # Find nearest prefecture
            pref_code = self._find_nearest_prefecture(lat, lon)

            if pref_code:
                # Find prefecture name for logging
                pref_name = ''
                for code, name in self.PREFECTURES:
                    if code == pref_code:
                        pref_name = name
                        break

                QgsMessageLog.logMessage(
                    f'Detected prefecture: {pref_name} ({pref_code})',
                    'ReinfoLib', Qgis.Info
                )

                # Update debug label
                if hasattr(self, 'label_pref_debug'):
                    self.label_pref_debug.setText(f'座標: ({lat:.4f}, {lon:.4f}) → {pref_name}')
                    self.label_pref_debug.setStyleSheet('color: green; font-size: 10px;')

                # Update combo box
                for i in range(self.combo_price_area.count()):
                    if self.combo_price_area.itemData(i) == pref_code:
                        self.combo_price_area.setCurrentIndex(i)
                        break

        except Exception as e:
            QgsMessageLog.logMessage(
                f'Prefecture detection error: {str(e)}',
                'ReinfoLib', Qgis.Warning
            )
            if hasattr(self, 'label_pref_debug'):
                self.label_pref_debug.setText(f'エラー: {str(e)}')
                self.label_pref_debug.setStyleSheet('color: red; font-size: 10px;')

    def _find_nearest_prefecture(self, lat: float, lon: float) -> str:
        """Find the nearest prefecture to given coordinates."""
        import math

        min_dist = float('inf')
        nearest_code = '13'  # Default to Tokyo

        for code, (plat, plon) in self.PREFECTURE_CENTERS.items():
            # Simple Euclidean distance (good enough for Japan)
            dist = math.sqrt((lat - plat) ** 2 + (lon - plon) ** 2)
            if dist < min_dist:
                min_dist = dist
                nearest_code = code

        return nearest_code

    def _on_output_changed(self, index: int):
        """Handle output format change."""
        output_type = self.combo_output.currentData()
        self.file_widget.setVisible(output_type != 'memory')

    def _browse_output(self):
        """Browse for output file."""
        output_type = self.combo_output.currentData()

        filters = {
            'gpkg': 'GeoPackage (*.gpkg)',
            'geojson': 'GeoJSON (*.geojson)',
            'shp': 'Shapefile (*.shp)',
        }

        file_filter = filters.get(output_type, 'All Files (*)')
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '出力ファイルを保存',
            '',
            file_filter
        )

        if file_path:
            self.edit_file_path.setText(file_path)

    def _get_extent(self) -> QgsRectangle:
        """Get the selected extent in WGS84."""
        extent_type = self.combo_extent.currentData()

        if extent_type == 'canvas':
            # Get canvas extent and transform to WGS84
            extent = self.canvas.extent()
            canvas_crs = self.canvas.mapSettings().destinationCrs()
            wgs84 = QgsProject.instance().crs()

            if canvas_crs.authid() != 'EPSG:4326':
                from qgis.core import QgsCoordinateReferenceSystem
                wgs84 = QgsCoordinateReferenceSystem('EPSG:4326')
                transform = QgsCoordinateTransform(
                    canvas_crs,
                    wgs84,
                    QgsProject.instance()
                )
                extent = transform.transformBoundingBox(extent)

            return extent

        elif extent_type == 'prefecture':
            # Return a rough bounding box for prefecture
            # In a full implementation, this would query actual boundaries
            return self.canvas.extent()

        return self.canvas.extent()

    def _on_fetch(self):
        """Handle fetch button click."""
        api_id = self._get_selected_api()
        if not api_id:
            QMessageBox.warning(
                self,
                'API未選択',
                '価格情報・都市計画などのタブに移動し、\nリストからAPIを選択してください。'
            )
            return

        if not self.settings.has_api_key():
            QMessageBox.warning(
                self,
                'APIキー未設定',
                '設定タブでAPIキーを設定してください。'
            )
            return

        api_info = ApiDefinitions.get_api(api_id)
        if not api_info:
            return

        # Get extent
        extent = self._get_extent()

        # Check output path if needed
        output_type = self.combo_output.currentData()
        if output_type != 'memory' and not self.edit_file_path.text():
            QMessageBox.warning(
                self,
                '出力パス未指定',
                '出力ファイルのパスを指定してください。'
            )
            return

        # Start fetch
        self._set_fetching(True)
        self.label_status.setText('データを取得中...')

        if api_info.uses_tile:
            # Check tile count before fetching
            from ..core.tile_calculator import TileCalculator
            max_tiles = self.settings.get_max_tiles()

            # Estimate zoom level and tile count
            estimated_zoom = TileCalculator.estimate_zoom_for_extent(
                extent.yMinimum(), extent.xMinimum(),
                extent.yMaximum(), extent.xMaximum(),
                max_tiles
            )
            tiles = TileCalculator.get_tiles_for_extent(
                extent.yMinimum(), extent.xMinimum(),
                extent.yMaximum(), extent.xMaximum(),
                estimated_zoom, max_tiles
            )
            tile_count = len(tiles)

            # Warn if too many tiles
            if tile_count >= max_tiles:
                reply = QMessageBox.warning(
                    self,
                    '範囲が広すぎます',
                    f'選択された範囲が広すぎるため、最大タイル数（{max_tiles}）に制限されます。\n'
                    f'全てのデータを取得するには、地図をズームインしてから再度お試しください。\n\n'
                    f'このまま取得を続けますか？',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    self.label_status.setText('キャンセルしました。地図をズームインしてください。')
                    return

            # Build extra params for specific APIs
            extra_params = {}

            # Get year from combo (default to previous year if not available)
            default_year = str(datetime.datetime.now().year - 1)
            year = self.combo_year.currentData() if hasattr(self, 'combo_year') and self.combo_year.currentData() else default_year

            if api_id == 'XPT001':
                # XPT001 (不動産価格ポイント) needs 'from' and 'to' parameters (YYYYQ format)
                # Format: from=20201, to=20244 means Q1 2020 to Q4 2024
                extra_params['from'] = f'{year}1'  # Q1
                extra_params['to'] = f'{year}4'    # Q4
            elif api_id == 'XPT002':
                # XPT002 (地価公示・地価調査ポイント) needs 'year' parameter
                extra_params['year'] = year

            # Use worker thread for tile-based APIs
            self.worker = FetchWorker(self.client, api_id, extent, extra_params=extra_params)
            self.worker.progress.connect(self._on_progress)
            self.worker.finished.connect(self._on_fetch_finished)
            self.worker.error.connect(self._on_fetch_error)
            self.worker.start()
        else:
            # Direct fetch for non-tile APIs
            params = {}

            # Build parameters for price APIs
            if api_info.category == 'price':
                # Area parameter (prefecture code)
                params['area'] = self.combo_price_area.currentData()

                # Year parameter for XIT001 and XCT001
                if api_id in ['XIT001', 'XCT001']:
                    year = self.combo_year.currentData()
                    quarter = self.combo_quarter.currentData()
                    if quarter:
                        params['year'] = f'{year}{quarter}'
                    else:
                        params['year'] = year
            else:
                # Fallback for other non-tile APIs
                extent_type = self.combo_extent.currentData()
                if extent_type == 'prefecture':
                    params['area'] = self.combo_prefecture.currentData()

            response = self.client.fetch_api(api_id, params)
            self._on_fetch_finished(response)

    def _on_cancel(self):
        """Handle cancel button click."""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        self._set_fetching(False)
        self.label_status.setText('キャンセルしました')

    def _on_progress(self, current: int, total: int):
        """Handle progress updates."""
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        self.label_status.setText(
            'タイル取得中 {} / {}...'.format(current, total)
        )

    def _on_fetch_finished(self, response):
        """Handle fetch completion."""
        from qgis.core import QgsMessageLog, Qgis

        self._set_fetching(False)
        QgsMessageLog.logMessage('=== Fetch completed ===', 'ReinfoLib', Qgis.Info)

        if not response.success:
            QgsMessageLog.logMessage(
                f'Fetch failed: {response.error_message}',
                'ReinfoLib', Qgis.Warning
            )
            self.label_status.setText(
                'エラー: {}'.format(response.error_message)
            )
            QMessageBox.warning(
                self,
                '取得失敗',
                response.error_message
            )
            return

        # Debug: Log response data structure
        if response.data:
            if isinstance(response.data, dict):
                QgsMessageLog.logMessage(
                    f'Response keys: {list(response.data.keys())}',
                    'ReinfoLib', Qgis.Info
                )
                if 'features' in response.data:
                    feature_count = len(response.data.get('features', []))
                    QgsMessageLog.logMessage(
                        f'GeoJSON features count: {feature_count}',
                        'ReinfoLib', Qgis.Info
                    )
                    # Log first feature geometry for debugging
                    if feature_count > 0:
                        first_feature = response.data['features'][0]
                        if 'geometry' in first_feature:
                            geom = first_feature['geometry']
                            QgsMessageLog.logMessage(
                                f'First feature geometry type: {geom.get("type")}',
                                'ReinfoLib', Qgis.Info
                            )
                            if 'coordinates' in geom:
                                coords = geom['coordinates']
                                if geom.get('type') == 'Point':
                                    QgsMessageLog.logMessage(
                                        f'First point coordinates: lon={coords[0]}, lat={coords[1]}',
                                        'ReinfoLib', Qgis.Info
                                    )
            elif isinstance(response.data, list):
                QgsMessageLog.logMessage(
                    f'Response is list with {len(response.data)} items',
                    'ReinfoLib', Qgis.Info
                )
        else:
            QgsMessageLog.logMessage('Response data is None or empty', 'ReinfoLib', Qgis.Warning)

        # Convert to layer
        api_id = self._get_selected_api()
        api_info = ApiDefinitions.get_api(api_id)
        layer_name = api_info.name_ja if api_info else api_id

        QgsMessageLog.logMessage(
            f'Converting to layer: {layer_name} (API: {api_id})',
            'ReinfoLib', Qgis.Info
        )

        if api_info and api_info.output_format in ('geojson', 'pbf'):
            layer = DataConverter.geojson_to_layer(
                response.data,
                layer_name,
                api_info
            )
        else:
            # Handle JSON data (may or may not have coordinates)
            data = response.data
            if isinstance(data, dict) and 'data' in data:
                data = data['data']

            if isinstance(data, list) and len(data) > 0:
                # Check if data has geometry
                if api_info and api_info.geometry_type:
                    layer = DataConverter.json_to_layer_with_coords(
                        data,
                        layer_name
                    )
                else:
                    # Non-spatial data - show as table/CSV
                    self._show_tabular_data(data, layer_name, api_info)
                    return
            else:
                layer = None

        if not layer:
            self.label_status.setText('選択した範囲にデータが見つかりませんでした。')
            return

        # Apply automatic styling if enabled
        if self.settings.is_auto_style_enabled() and api_id:
            StyleManager.apply_style(layer, api_id)

        # Save or add to map
        output_type = self.combo_output.currentData()
        if output_type != 'memory':
            file_path = self.edit_file_path.text()
            DataConverter.save_layer(layer, file_path, output_type)

            if self.check_add_to_map.isChecked():
                from qgis.core import QgsVectorLayer
                saved_layer = QgsVectorLayer(file_path, layer_name, 'ogr')
                if saved_layer.isValid():
                    # Re-apply style to saved layer
                    if self.settings.is_auto_style_enabled() and api_id:
                        StyleManager.apply_style(saved_layer, api_id)
                    DataConverter.add_layer_to_project(saved_layer, 'ReinfoLib')
                    layer = saved_layer
        else:
            if self.check_add_to_map.isChecked():
                DataConverter.add_layer_to_project(layer, 'ReinfoLib')

        # Zoom to layer with safeguards
        if self.check_zoom_to_layer.isChecked() and layer:
            from qgis.core import QgsMessageLog, Qgis, QgsCoordinateReferenceSystem

            QgsMessageLog.logMessage('=== ZOOM TO LAYER START ===', 'ReinfoLib', Qgis.Info)

            # Get CRS information
            layer_crs = layer.crs()
            canvas_crs = self.canvas.mapSettings().destinationCrs()
            QgsMessageLog.logMessage(
                f'Layer CRS: {layer_crs.authid()}, Canvas CRS: {canvas_crs.authid()}',
                'ReinfoLib', Qgis.Info
            )

            # Get current canvas state before zoom
            canvas_extent_before = self.canvas.extent()
            scale_before = self.canvas.scale()
            QgsMessageLog.logMessage(
                f'Canvas BEFORE zoom: scale={scale_before:.0f}',
                'ReinfoLib', Qgis.Info
            )

            original_extent = layer.extent()
            QgsMessageLog.logMessage(
                f'Layer extent (in layer CRS): xmin={original_extent.xMinimum():.6f}, '
                f'ymin={original_extent.yMinimum():.6f}, '
                f'xmax={original_extent.xMaximum():.6f}, '
                f'ymax={original_extent.yMaximum():.6f}',
                'ReinfoLib', Qgis.Info
            )

            extent = original_extent
            # Always add buffer for point layers to prevent over-zooming
            # 0.02 degrees is approximately 2km - increased buffer
            min_extent_size = 0.02
            if extent.width() < min_extent_size or extent.height() < min_extent_size:
                buffer_x = max(0, (min_extent_size - extent.width()) / 2)
                buffer_y = max(0, (min_extent_size - extent.height()) / 2)
                buffer = max(buffer_x, buffer_y, 0.01)
                extent = extent.buffered(buffer)
                QgsMessageLog.logMessage(
                    f'Applied buffer: {buffer:.6f} degrees',
                    'ReinfoLib', Qgis.Info
                )

            # Transform extent to canvas CRS if different
            if layer_crs.authid() != canvas_crs.authid():
                QgsMessageLog.logMessage(
                    f'Transforming extent from {layer_crs.authid()} to {canvas_crs.authid()}',
                    'ReinfoLib', Qgis.Info
                )
                transform = QgsCoordinateTransform(
                    layer_crs,
                    canvas_crs,
                    QgsProject.instance()
                )
                extent = transform.transformBoundingBox(extent)
                QgsMessageLog.logMessage(
                    f'Transformed extent: xmin={extent.xMinimum():.2f}, '
                    f'ymin={extent.yMinimum():.2f}, '
                    f'xmax={extent.xMaximum():.2f}, '
                    f'ymax={extent.yMaximum():.2f}',
                    'ReinfoLib', Qgis.Info
                )

            # Set extent and refresh
            QgsMessageLog.logMessage('Setting canvas extent...', 'ReinfoLib', Qgis.Info)
            self.canvas.setExtent(extent)

            QgsMessageLog.logMessage('Refreshing canvas...', 'ReinfoLib', Qgis.Info)
            self.canvas.refresh()

            # Get canvas state after zoom
            scale_after = self.canvas.scale()
            QgsMessageLog.logMessage(
                f'Canvas AFTER zoom: scale={scale_after:.0f}',
                'ReinfoLib', Qgis.Info
            )

            QgsMessageLog.logMessage('=== ZOOM TO LAYER END ===', 'ReinfoLib', Qgis.Info)

        feature_count = layer.featureCount() if layer else 0
        self.label_status.setText(
            '{}件のデータを取得しました。'.format(feature_count)
        )

    def _on_fetch_error(self, error_msg: str):
        """Handle fetch error."""
        self._set_fetching(False)
        self.label_status.setText('エラー: {}'.format(error_msg))
        QMessageBox.warning(
            self,
            '取得エラー',
            error_msg
        )

    def _show_tabular_data(self, data: list, layer_name: str, api_info):
        """Show non-spatial tabular data as a table layer."""
        if not data:
            self.label_status.setText('データが見つかりませんでした。')
            return

        record_count = len(data)
        output_type = self.combo_output.currentData()

        if output_type == 'memory':
            # Create a non-geometry table layer
            layer = self._create_table_layer(data, layer_name)
            if layer and layer.isValid():
                if self.check_add_to_map.isChecked():
                    DataConverter.add_layer_to_project(layer, 'ReinfoLib')

                QMessageBox.information(
                    self,
                    'データ取得完了',
                    f'{record_count}件のデータを取得しました。\n\n'
                    f'このAPIは座標情報を含まないため、地図上にポイントは表示されません。\n'
                    f'レイヤパネルのレイヤを右クリック→「属性テーブルを開く」で\n'
                    f'データを確認できます。'
                )
                self.label_status.setText(f'{record_count}件のデータを取得しました。')
            else:
                QMessageBox.warning(self, 'エラー', 'テーブルレイヤの作成に失敗しました。')
        else:
            # Save as CSV
            import csv
            import os

            file_path = self.edit_file_path.text()
            if not file_path:
                QMessageBox.warning(self, 'エラー', '出力ファイルパスを指定してください。')
                return

            # Change extension to CSV for tabular data
            base_path = os.path.splitext(file_path)[0]
            csv_path = base_path + '.csv'

            try:
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    if data:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)

                QMessageBox.information(
                    self,
                    '保存完了',
                    f'{record_count}件のデータをCSVファイルに保存しました。\n\n{csv_path}'
                )
                self.label_status.setText(f'{record_count}件をCSVに保存しました。')
            except Exception as e:
                QMessageBox.warning(self, '保存エラー', f'ファイル保存に失敗しました: {str(e)}')

    def _create_table_layer(self, data: list, layer_name: str):
        """Create a non-geometry table layer from data."""
        import warnings
        from qgis.core import QgsVectorLayer, QgsField, QgsFeature
        from qgis.PyQt.QtCore import QVariant

        if not data:
            return None

        # Create a NoGeometry layer
        uri = 'NoGeometry?crs=EPSG:4326'
        layer = QgsVectorLayer(uri, layer_name, 'memory')

        if not layer.isValid():
            return None

        # Detect fields from first record
        first_record = data[0]
        fields = []
        for key, value in first_record.items():
            field_name = key[:10]
            # Suppress deprecation warning for QgsField constructor
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                if isinstance(value, bool):
                    fields.append(QgsField(field_name, QVariant.Bool, 'Boolean'))
                elif isinstance(value, int):
                    fields.append(QgsField(field_name, QVariant.Int, 'Integer'))
                elif isinstance(value, float):
                    fields.append(QgsField(field_name, QVariant.Double, 'Real'))
                else:
                    fields.append(QgsField(field_name, QVariant.String, 'String'))

        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        # Add features (rows)
        features = []
        field_names = [f.name() for f in layer.fields()]

        for record in data:
            feature = QgsFeature(layer.fields())
            for i, field_name in enumerate(field_names):
                # Find matching key in record
                for key, value in record.items():
                    if key[:10] == field_name:
                        if isinstance(value, (list, dict)):
                            import json
                            value = json.dumps(value, ensure_ascii=False)
                        feature.setAttribute(i, value)
                        break
            features.append(feature)

        layer.dataProvider().addFeatures(features)
        layer.updateExtents()

        return layer

    def _set_fetching(self, fetching: bool):
        """Set UI state for fetching."""
        self.btn_fetch.setEnabled(not fetching)
        self.btn_cancel.setEnabled(fetching)
        self.tabs.setEnabled(not fetching)
        self.progress.setVisible(fetching)

        if not fetching:
            self.progress.setValue(0)
