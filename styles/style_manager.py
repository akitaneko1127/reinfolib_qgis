# -*- coding: utf-8 -*-
"""
Style Manager for ReinfoLib QGIS Plugin

Applies automatic styling to fetched layers.
"""

from typing import Optional, Dict, List, Tuple
from qgis.core import (
    QgsVectorLayer,
    QgsSymbol,
    QgsFillSymbol,
    QgsMarkerSymbol,
    QgsLineSymbol,
    QgsRendererCategory,
    QgsCategorizedSymbolRenderer,
    QgsGraduatedSymbolRenderer,
    QgsRendererRange,
    QgsSingleSymbolRenderer,
    QgsSimpleFillSymbolLayer,
    QgsSimpleMarkerSymbolLayer,
)
from qgis.PyQt.QtGui import QColor


class StyleManager:
    """Manages layer styling for ReinfoLib data."""

    # Zoning colors (用途地域)
    ZONING_COLORS: Dict[str, Tuple[int, int, int, int]] = {
        '第一種低層住居専用地域': (0, 128, 0, 180),
        '第二種低層住居専用地域': (144, 238, 144, 180),
        '第一種中高層住居専用地域': (173, 255, 47, 180),
        '第二種中高層住居専用地域': (255, 255, 0, 180),
        '第一種住居地域': (255, 215, 0, 180),
        '第二種住居地域': (255, 165, 0, 180),
        '準住居地域': (255, 192, 203, 180),
        '田園住居地域': (152, 251, 152, 180),
        '近隣商業地域': (255, 105, 180, 180),
        '商業地域': (255, 0, 0, 180),
        '準工業地域': (138, 43, 226, 180),
        '工業地域': (0, 0, 255, 180),
        '工業専用地域': (0, 0, 139, 180),
    }

    # Flood depth colors (浸水深)
    FLOOD_COLORS: List[Tuple[float, float, Tuple[int, int, int, int]]] = [
        (0, 0.5, (255, 255, 200, 150)),      # 0-0.5m: light yellow
        (0.5, 1.0, (255, 255, 0, 150)),      # 0.5-1m: yellow
        (1.0, 2.0, (255, 165, 0, 150)),      # 1-2m: orange
        (2.0, 5.0, (255, 0, 0, 150)),        # 2-5m: red
        (5.0, 10.0, (139, 0, 0, 150)),       # 5-10m: dark red
        (10.0, 100.0, (128, 0, 128, 150)),   # 10m+: purple
    ]

    # Price range colors (価格帯)
    PRICE_COLORS: List[Tuple[float, float, Tuple[int, int, int], int]] = [
        (0, 10000000, (0, 128, 255), 6),           # ~1000万: blue, size 6
        (10000000, 30000000, (0, 255, 0), 8),      # 1000-3000万: green, size 8
        (30000000, 50000000, (255, 255, 0), 10),   # 3000-5000万: yellow, size 10
        (50000000, 100000000, (255, 165, 0), 12),  # 5000万-1億: orange, size 12
        (100000000, float('inf'), (255, 0, 0), 14), # 1億~: red, size 14
    ]

    # Fire prevention area colors (防火地域)
    FIRE_COLORS: Dict[str, Tuple[int, int, int, int]] = {
        '防火地域': (255, 0, 0, 150),
        '準防火地域': (255, 165, 0, 150),
    }

    # Landslide hazard colors (土砂災害)
    LANDSLIDE_COLORS: Dict[str, Tuple[int, int, int, int]] = {
        '土砂災害警戒区域': (255, 255, 0, 150),
        '土砂災害特別警戒区域': (255, 0, 0, 150),
    }

    # Urban planning area colors (都市計画区域/区域区分)
    URBAN_PLANNING_COLORS: Dict[str, Tuple[int, int, int, int]] = {
        '市街化区域': (255, 200, 200, 150),        # Light red - urbanization promotion
        '市街化調整区域': (200, 255, 200, 150),    # Light green - urbanization control
        '非線引き区域': (255, 255, 200, 150),      # Light yellow - non-delineated
        '都市計画区域外': (200, 200, 200, 150),    # Gray - outside urban planning
        '準都市計画区域': (200, 200, 255, 150),    # Light blue - quasi-urban
    }

    # Location optimization plan colors (立地適正化計画)
    LOCATION_OPTIMIZATION_COLORS: Dict[str, Tuple[int, int, int, int]] = {
        '居住誘導区域': (255, 182, 193, 150),      # Pink - residential guidance
        '都市機能誘導区域': (135, 206, 250, 150),  # Light blue - urban function guidance
        '居住調整区域': (255, 228, 181, 150),      # Peach - residential adjustment
    }

    # Nursery/Kindergarten colors (保育園・幼稚園等)
    NURSERY_COLORS: Dict[str, Tuple[int, int, int, int]] = {
        '保育所': (255, 182, 193, 200),            # Pink
        '幼稚園': (135, 206, 250, 200),            # Light blue
        '認定こども園': (152, 251, 152, 200),      # Pale green
        '小規模保育事業': (255, 218, 185, 200),    # Peach
        '家庭的保育事業': (255, 255, 200, 200),    # Light yellow
        '事業所内保育事業': (216, 191, 216, 200),  # Thistle
    }

    # Welfare facility colors (福祉施設)
    WELFARE_COLORS: Dict[str, Tuple[int, int, int, int]] = {
        '高齢者福祉施設': (255, 165, 0, 200),      # Orange
        '障害者福祉施設': (138, 43, 226, 200),     # Purple
        '児童福祉施設': (255, 105, 180, 200),      # Hot pink
        '介護施設': (255, 200, 100, 200),          # Light orange
        '老人ホーム': (255, 180, 100, 200),        # Darker orange
    }

    # Medical facility colors (医療機関)
    MEDICAL_COLORS: Dict[str, Tuple[int, int, int, int]] = {
        '病院': (255, 0, 0, 200),                  # Red
        '診療所': (255, 100, 100, 200),            # Light red
        '歯科診療所': (255, 150, 150, 200),        # Lighter red
        '薬局': (0, 200, 0, 200),                  # Green
    }

    # Municipal office colors (市区町村役場等)
    MUNICIPAL_COLORS: Dict[str, Tuple[int, int, int, int]] = {
        '市役所': (0, 100, 200, 200),              # Blue
        '区役所': (0, 150, 200, 200),              # Light blue
        '町村役場': (100, 150, 200, 200),          # Grayish blue
        '支所': (150, 180, 200, 200),              # Pale blue
        '出張所': (180, 200, 220, 200),            # Very pale blue
        '公民館': (200, 150, 100, 200),            # Brown
        'コミュニティセンター': (180, 140, 100, 200),  # Darker brown
    }

    @classmethod
    def apply_style(cls, layer: QgsVectorLayer, api_id: str) -> bool:
        """Apply appropriate style based on API ID.

        Args:
            layer: The layer to style.
            api_id: The API identifier.

        Returns:
            True if style was applied.
        """
        style_methods = {
            # Urban planning
            'XKT001': cls._apply_urban_planning_style,
            'XKT002': cls._apply_zoning_style,
            'XKT003': cls._apply_location_optimization_style,
            'XKT014': cls._apply_fire_prevention_style,
            'XKT031': cls._apply_did_style,
            # Disaster
            'XKT026': cls._apply_flood_style,
            'XKT027': cls._apply_storm_surge_style,
            'XKT029': cls._apply_landslide_style,
            'XKT018': cls._apply_disaster_risk_style,
            'XKT025': cls._apply_large_fill_style,
            'XGT001': cls._apply_shelter_style,
            # Price
            'XPT001': cls._apply_price_point_style,
            'XPT002': cls._apply_land_price_style,
            # Facilities
            'XKT004': cls._apply_elementary_school_district_style,
            'XKT005': cls._apply_junior_high_school_district_style,
            'XKT006': cls._apply_school_style,
            'XKT007': cls._apply_nursery_style,
            'XKT010': cls._apply_medical_style,
            'XKT011': cls._apply_welfare_style,
            'XKT015': cls._apply_station_style,
            'XKT022': cls._apply_library_style,
            'XKT023': cls._apply_municipal_style,
            # Other
            'XKT013': cls._apply_population_mesh_style,
            'XKT019': cls._apply_natural_park_style,
        }

        method = style_methods.get(api_id)
        if method:
            return method(layer)

        # Default style
        return cls._apply_default_style(layer)

    @classmethod
    def _apply_default_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply a default style."""
        geom_type = layer.geometryType()

        if geom_type == 0:  # Point
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'circle',
                'color': '0,128,255,200',
                'size': '3',
                'outline_color': '0,0,0,255',
                'outline_width': '0.5',
            })
        elif geom_type == 1:  # Line
            symbol = QgsLineSymbol.createSimple({
                'color': '0,0,255,255',
                'width': '0.5',
            })
        elif geom_type == 2:  # Polygon
            symbol = QgsFillSymbol.createSimple({
                'color': '0,128,255,100',
                'outline_color': '0,0,128,255',
                'outline_width': '0.3',
            })
        else:
            return False

        layer.renderer().setSymbol(symbol)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_urban_planning_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply urban planning area (都市計画区域/区域区分) categorical style."""
        from qgis.core import QgsMessageLog, Qgis

        # Find the area classification field
        field_name = cls._find_field(layer, [
            'area_class', 'kuiki', 'kubun', 'class', 'type',
            'area_divis', 'division', 'category'
        ])

        if not field_name:
            QgsMessageLog.logMessage(
                f'XKT001: Could not find area classification field, using unique values',
                'ReinfoLib', Qgis.Info
            )
            # Try to find any suitable field and create categories from unique values
            return cls._apply_unique_values_style(layer)

        QgsMessageLog.logMessage(
            f'XKT001: Using field "{field_name}" for styling',
            'ReinfoLib', Qgis.Info
        )

        categories = []
        for area_name, color in cls.URBAN_PLANNING_COLORS.items():
            symbol = QgsFillSymbol.createSimple({
                'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                'outline_color': '0,0,0,255',
                'outline_width': '0.3',
            })
            category = QgsRendererCategory(area_name, symbol, area_name)
            categories.append(category)

        # Add default for unknown values
        default_symbol = QgsFillSymbol.createSimple({
            'color': '180,180,180,100',
            'outline_color': '0,0,0,255',
            'outline_width': '0.3',
        })
        categories.append(QgsRendererCategory('', default_symbol, 'その他'))

        renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_unique_values_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply style based on unique values in the first string field."""
        from qgis.core import QgsMessageLog, Qgis
        import random

        # Find a suitable field for categorization
        string_fields = [f for f in layer.fields() if f.type() == 10]  # QVariant.String = 10
        if not string_fields:
            return cls._apply_default_style(layer)

        field_name = string_fields[0].name()

        # Get unique values
        unique_values = set()
        for feature in layer.getFeatures():
            val = feature[field_name]
            if val:
                unique_values.add(str(val))
            if len(unique_values) > 20:  # Limit to 20 categories
                break

        QgsMessageLog.logMessage(
            f'Creating {len(unique_values)} categories for field "{field_name}"',
            'ReinfoLib', Qgis.Info
        )

        # Generate colors for each unique value
        categories = []
        colors = [
            (255, 200, 200, 150), (200, 255, 200, 150), (200, 200, 255, 150),
            (255, 255, 200, 150), (255, 200, 255, 150), (200, 255, 255, 150),
            (255, 180, 180, 150), (180, 255, 180, 150), (180, 180, 255, 150),
            (255, 220, 180, 150), (180, 255, 220, 150), (220, 180, 255, 150),
        ]

        for i, value in enumerate(sorted(unique_values)):
            color = colors[i % len(colors)]
            symbol = QgsFillSymbol.createSimple({
                'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                'outline_color': '0,0,0,255',
                'outline_width': '0.3',
            })
            category = QgsRendererCategory(value, symbol, value)
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_location_optimization_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply location optimization plan (立地適正化計画) categorical style."""
        from qgis.core import QgsMessageLog, Qgis

        # Find the area type field
        field_name = cls._find_field(layer, [
            'area_type', 'kuiki', 'type', 'class', 'category',
            'yudo', 'guidance', 'name'
        ])

        if not field_name:
            QgsMessageLog.logMessage(
                'XKT003: Could not find area type field, using unique values',
                'ReinfoLib', Qgis.Info
            )
            return cls._apply_unique_values_style(layer)

        QgsMessageLog.logMessage(
            f'XKT003: Using field "{field_name}" for styling',
            'ReinfoLib', Qgis.Info
        )

        categories = []
        for area_name, color in cls.LOCATION_OPTIMIZATION_COLORS.items():
            symbol = QgsFillSymbol.createSimple({
                'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                'outline_color': '0,0,0,255',
                'outline_width': '0.3',
            })
            category = QgsRendererCategory(area_name, symbol, area_name)
            categories.append(category)

        # Add default for unknown values
        default_symbol = QgsFillSymbol.createSimple({
            'color': '180,180,180,100',
            'outline_color': '0,0,0,255',
            'outline_width': '0.3',
        })
        categories.append(QgsRendererCategory('', default_symbol, 'その他'))

        renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_zoning_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply zoning (用途地域) categorical style."""
        from qgis.core import QgsMessageLog, Qgis

        # Log all field names for debugging
        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(
            f'XKT002 fields: {field_names}',
            'ReinfoLib', Qgis.Info
        )

        # Find the zoning type field - try multiple candidates
        field_name = cls._find_field(layer, [
            'youto', 'use_type', 'zoning', 'type', 'class',
            'use_catego', 'land_use', 'category', 'name', 'youto_chii'
        ])

        if not field_name:
            QgsMessageLog.logMessage(
                'XKT002: Could not find zoning field, using unique values',
                'ReinfoLib', Qgis.Info
            )
            return cls._apply_unique_values_style(layer)

        QgsMessageLog.logMessage(
            f'XKT002: Using field "{field_name}" for styling',
            'ReinfoLib', Qgis.Info
        )

        # Get unique values from the data
        unique_values = set()
        for feature in layer.getFeatures():
            val = feature[field_name]
            if val:
                unique_values.add(str(val))

        QgsMessageLog.logMessage(
            f'XKT002: Found {len(unique_values)} unique values: {list(unique_values)[:10]}',
            'ReinfoLib', Qgis.Info
        )

        # Create categories based on actual data values
        categories = []
        used_colors = []

        for value in sorted(unique_values):
            # Try to match with predefined zoning colors
            matched_color = None
            for zone_name, color in cls.ZONING_COLORS.items():
                # Exact match or partial match
                if zone_name == value or zone_name in value or value in zone_name:
                    matched_color = color
                    break

            if matched_color:
                color = matched_color
            else:
                # Generate a color for unmatched values
                color = cls._generate_zoning_color(value, used_colors)
                used_colors.append(color)

            symbol = QgsFillSymbol.createSimple({
                'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                'outline_color': '0,0,0,255',
                'outline_width': '0.3',
            })
            category = QgsRendererCategory(value, symbol, value)
            categories.append(category)

        # Add default for null/empty values
        default_symbol = QgsFillSymbol.createSimple({
            'color': '200,200,200,100',
            'outline_color': '0,0,0,255',
            'outline_width': '0.3',
        })
        categories.append(QgsRendererCategory('', default_symbol, 'その他'))

        renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _generate_zoning_color(cls, value: str, used_colors: list) -> Tuple[int, int, int, int]:
        """Generate a color for a zoning value based on keywords."""
        # Color based on keywords in value
        if '住居' in value or '住専' in value:
            if '低層' in value or '１低' in value or '２低' in value:
                return (0, 128, 0, 180)  # Dark green
            elif '中高層' in value or '１中' in value or '２中' in value:
                return (173, 255, 47, 180)  # Yellow-green
            else:
                return (255, 215, 0, 180)  # Gold
        elif '商業' in value or '近商' in value:
            if '近隣' in value or '近商' in value:
                return (255, 105, 180, 180)  # Hot pink
            else:
                return (255, 0, 0, 180)  # Red
        elif '工業' in value or '工専' in value or '準工' in value:
            if '専用' in value or '工専' in value:
                return (0, 0, 139, 180)  # Dark blue
            elif '準' in value:
                return (138, 43, 226, 180)  # Purple
            else:
                return (0, 0, 255, 180)  # Blue
        elif '田園' in value:
            return (152, 251, 152, 180)  # Pale green

        # Fallback: generate distinct colors
        base_colors = [
            (255, 200, 200, 150), (200, 255, 200, 150), (200, 200, 255, 150),
            (255, 255, 200, 150), (255, 200, 255, 150), (200, 255, 255, 150),
            (255, 180, 180, 150), (180, 255, 180, 150), (180, 180, 255, 150),
        ]
        for color in base_colors:
            if color not in used_colors:
                return color

        # If all used, return a default
        return (200, 200, 200, 150)

    @classmethod
    def _apply_fire_prevention_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply fire prevention area (防火・準防火地域) style."""
        from qgis.core import QgsMessageLog, Qgis

        # Find the fire prevention type field
        field_name = cls._find_field(layer, [
            'bouka', 'fire', 'type', 'class', 'category',
            'fire_preve', 'name', 'area_type'
        ])

        if not field_name:
            QgsMessageLog.logMessage(
                'XKT014: Could not find fire prevention field, using unique values',
                'ReinfoLib', Qgis.Info
            )
            return cls._apply_unique_values_style(layer)

        QgsMessageLog.logMessage(
            f'XKT014: Using field "{field_name}" for styling',
            'ReinfoLib', Qgis.Info
        )

        categories = []
        for area_name, color in cls.FIRE_COLORS.items():
            symbol = QgsFillSymbol.createSimple({
                'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                'outline_color': '0,0,0,255',
                'outline_width': '0.3',
            })
            category = QgsRendererCategory(area_name, symbol, area_name)
            categories.append(category)

        # Add default for unknown values
        default_symbol = QgsFillSymbol.createSimple({
            'color': '180,180,180,100',
            'outline_color': '0,0,0,255',
            'outline_width': '0.3',
        })
        categories.append(QgsRendererCategory('', default_symbol, 'その他'))

        renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_flood_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply flood depth graduated style."""
        field_name = cls._find_field(layer, ['depth', 'shinsui', 'rank', 'class'])
        if not field_name:
            return cls._apply_default_style(layer)

        ranges = []
        for min_val, max_val, color in cls.FLOOD_COLORS:
            symbol = QgsFillSymbol.createSimple({
                'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                'outline_color': '0,0,0,255',
                'outline_width': '0.2',
            })
            label = f'{min_val}-{max_val}m'
            range_item = QgsRendererRange(min_val, max_val, symbol, label)
            ranges.append(range_item)

        renderer = QgsGraduatedSymbolRenderer(field_name, ranges)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_landslide_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply landslide hazard area style."""
        field_name = cls._find_field(layer, ['type', 'class', 'keikai', 'hazard'])
        if not field_name:
            return cls._apply_default_style(layer)

        categories = []
        for area_name, color in cls.LANDSLIDE_COLORS.items():
            symbol = QgsFillSymbol.createSimple({
                'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                'outline_color': '0,0,0,255',
                'outline_width': '0.3',
            })
            category = QgsRendererCategory(area_name, symbol, area_name)
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_price_point_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply real estate price point style."""
        import re
        import warnings
        from qgis.core import QgsMessageLog, Qgis, QgsField
        from qgis.PyQt.QtCore import QVariant

        # Log all field names for debugging
        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(
            f'XPT001 fields: {field_names}',
            'ReinfoLib', Qgis.Info
        )

        # Find the transaction price field
        source_field = cls._find_field(layer, ['u_transact'])

        if not source_field:
            QgsMessageLog.logMessage(
                f'Could not find u_transact field',
                'ReinfoLib', Qgis.Warning
            )
            return cls._apply_default_style(layer)

        # Create a numeric price field by parsing the text value
        # "1,500万円" -> 15000000 (yen)
        numeric_field_name = 'price_yen'

        # Add numeric field if not exists
        if numeric_field_name not in field_names:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                layer.dataProvider().addAttributes([
                    QgsField(numeric_field_name, QVariant.Double, 'Real')
                ])
            layer.updateFields()

        # Parse and update values
        layer.startEditing()
        field_idx = layer.fields().indexOf(numeric_field_name)

        for feature in layer.getFeatures():
            price_str = feature[source_field]
            price_yen = cls._parse_price_string(price_str)

            if price_yen is not None:
                layer.changeAttributeValue(feature.id(), field_idx, price_yen)

        layer.commitChanges()

        # Refresh the layer to ensure data is accessible for identification
        layer.updateExtents()
        layer.triggerRepaint()

        # Verify feature count and data integrity
        feature_count = layer.featureCount()
        QgsMessageLog.logMessage(
            f'Layer has {feature_count} features after price parsing',
            'ReinfoLib', Qgis.Info
        )

        # Log sample parsed values and verify all fields
        features = list(layer.getFeatures())[:3]
        for i, f in enumerate(features):
            attrs = {field.name(): f[field.name()] for field in layer.fields()}
            QgsMessageLog.logMessage(
                f'Feature {i} price: {f[source_field]} -> {f[numeric_field_name]}円',
                'ReinfoLib', Qgis.Info
            )
            if i == 0:
                # Log all attributes for first feature with values
                sample_attrs = {k: v for k, v in list(attrs.items())[:5]}
                QgsMessageLog.logMessage(
                    f'First feature sample attrs: {sample_attrs}',
                    'ReinfoLib', Qgis.Info
                )
                QgsMessageLog.logMessage(
                    f'Total fields: {len(attrs)}, Feature ID: {f.id()}',
                    'ReinfoLib', Qgis.Info
                )

        # Use the numeric field for styling
        field_name = numeric_field_name

        ranges = []
        for min_val, max_val, color, size in cls.PRICE_COLORS:
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'circle',
                'color': f'{color[0]},{color[1]},{color[2]},200',
                'size': str(size),
                'outline_color': '0,0,0,255',
                'outline_width': '0.5',
            })
            if max_val == float('inf'):
                label = f'{int(min_val/10000)}万円以上'
            else:
                label = f'{int(min_val/10000)}-{int(max_val/10000)}万円'
            range_item = QgsRendererRange(min_val, max_val if max_val != float('inf') else 10000000000, symbol, label)
            ranges.append(range_item)

        renderer = QgsGraduatedSymbolRenderer(field_name, ranges)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_land_price_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply land price point style for XPT002 (地価公示・地価調査)."""
        from qgis.core import QgsMessageLog, Qgis

        # XPT002 uses 'land_price' field which is numeric (円/㎡)
        field_name = cls._find_field(layer, ['land_price', 'price', 'kakaku'])

        if not field_name:
            QgsMessageLog.logMessage(
                'XPT002: Could not find land_price field, using default style',
                'ReinfoLib', Qgis.Warning
            )
            return cls._apply_default_style(layer)

        # Log sample values
        features = list(layer.getFeatures())[:3]
        for i, f in enumerate(features):
            QgsMessageLog.logMessage(
                f'XPT002 land_price sample {i}: {f[field_name]} (type: {type(f[field_name]).__name__})',
                'ReinfoLib', Qgis.Info
            )

        # Land price ranges (円/㎡) - different from transaction prices
        LAND_PRICE_RANGES = [
            (0, 100000, (0, 128, 255), 6),            # ~10万円/㎡: blue
            (100000, 300000, (0, 255, 0), 8),         # 10-30万円/㎡: green
            (300000, 500000, (255, 255, 0), 10),      # 30-50万円/㎡: yellow
            (500000, 1000000, (255, 165, 0), 12),     # 50-100万円/㎡: orange
            (1000000, float('inf'), (255, 0, 0), 14), # 100万円/㎡~: red
        ]

        ranges = []
        for min_val, max_val, color, size in LAND_PRICE_RANGES:
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'circle',
                'color': f'{color[0]},{color[1]},{color[2]},200',
                'size': str(size),
                'outline_color': '0,0,0,255',
                'outline_width': '0.5',
            })
            if max_val == float('inf'):
                label = f'{int(min_val/10000)}万円/㎡以上'
            else:
                label = f'{int(min_val/10000)}-{int(max_val/10000)}万円/㎡'
            range_item = QgsRendererRange(min_val, max_val if max_val != float('inf') else 100000000, symbol, label)
            ranges.append(range_item)

        renderer = QgsGraduatedSymbolRenderer(field_name, ranges)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_school_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply school (学校) categorical style by school type."""
        from qgis.core import QgsMessageLog, Qgis

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT006 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # School type colors
        SCHOOL_COLORS = {
            '小学校': (255, 215, 0, 200),       # Gold
            '中学校': (0, 191, 255, 200),       # Deep sky blue
            '高等学校': (138, 43, 226, 200),    # Blue violet
            '高校': (138, 43, 226, 200),        # Blue violet
            '大学': (255, 0, 0, 200),           # Red
            '短期大学': (255, 100, 100, 200),   # Light red
            '専門学校': (255, 165, 0, 200),     # Orange
            '特別支援学校': (0, 128, 0, 200),   # Green
            '中等教育学校': (100, 149, 237, 200),  # Cornflower blue
        }

        # Find type field
        field_name = cls._find_field(layer, [
            'school_typ', 'type', 'category', 'class', 'school_cat'
        ])

        if not field_name:
            # Default gold square
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'square',
                'color': '255,215,0,200',
                'size': '4',
                'outline_color': '0,0,0,255',
                'outline_width': '0.5',
            })
            renderer = QgsSingleSymbolRenderer(symbol)
            layer.setRenderer(renderer)
            layer.triggerRepaint()
            return True

        QgsMessageLog.logMessage(f'XKT006: Using field "{field_name}" for styling', 'ReinfoLib', Qgis.Info)
        return cls._apply_categorical_point_style_by_field(layer, field_name, SCHOOL_COLORS, 'square', 4)

    @classmethod
    def _apply_medical_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply medical facility (医療機関) categorical style."""
        from qgis.core import QgsMessageLog, Qgis

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT010 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Find type field
        field_name = cls._find_field(layer, [
            'type', 'facility_t', 'category', 'class', 'med_type', 'name'
        ])

        if not field_name:
            # Default to single cross symbol
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'cross2',
                'color': '255,0,0,200',
                'size': '5',
                'outline_color': '255,255,255,255',
                'outline_width': '1',
            })
            renderer = QgsSingleSymbolRenderer(symbol)
            layer.setRenderer(renderer)
            layer.triggerRepaint()
            return True

        QgsMessageLog.logMessage(f'XKT010: Using field "{field_name}" for styling', 'ReinfoLib', Qgis.Info)
        return cls._apply_categorical_point_style_by_field(layer, field_name, cls.MEDICAL_COLORS, 'cross2', 5)

    @classmethod
    def _apply_shelter_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply emergency shelter point style."""
        symbol = QgsMarkerSymbol.createSimple({
            'name': 'triangle',
            'color': '0,128,0,200',
            'size': '5',
            'outline_color': '255,255,255,255',
            'outline_width': '1',
        })
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_elementary_school_district_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply elementary school district (小学校区) polygon style with A27_004_ja field."""
        from qgis.core import QgsMessageLog, Qgis

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT004 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Log sample values for debugging
        for feature in layer.getFeatures():
            for fn in field_names:
                val = feature[fn]
                if val is not None and str(val).strip():
                    QgsMessageLog.logMessage(f'XKT004 field "{fn}" sample: {val}', 'ReinfoLib', Qgis.Info)
            break

        # Use A27_004_ja field for elementary school district name
        field_name = cls._find_field(layer, [
            'A27_004_ja', 'A27_004', 'school_nam', 'name', 'school', 'gakkou', 'gakko'
        ])

        if not field_name:
            QgsMessageLog.logMessage(
                'XKT004: Could not find A27_004_ja field, using unique values',
                'ReinfoLib', Qgis.Info
            )
            return cls._apply_unique_values_style(layer)

        QgsMessageLog.logMessage(
            f'XKT004: Using field "{field_name}" for styling',
            'ReinfoLib', Qgis.Info
        )

        # Get unique values and assign colors
        unique_values = set()
        for feature in layer.getFeatures():
            val = feature[field_name]
            if val:
                unique_values.add(str(val))

        QgsMessageLog.logMessage(f'XKT004: Found {len(unique_values)} unique school names', 'ReinfoLib', Qgis.Info)

        # Generate distinct colors - using warm colors for elementary schools
        categories = []
        base_colors = [
            (255, 220, 180, 150), (255, 200, 160, 150), (255, 240, 200, 150),
            (255, 230, 170, 150), (255, 210, 190, 150), (255, 250, 210, 150),
            (255, 195, 150, 150), (255, 235, 180, 150), (255, 215, 170, 150),
            (255, 225, 195, 150), (255, 245, 185, 150), (255, 205, 175, 150),
        ]

        for i, value in enumerate(sorted(unique_values)):
            color = base_colors[i % len(base_colors)]
            symbol = QgsFillSymbol.createSimple({
                'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                'outline_color': '200,100,0,255',
                'outline_width': '0.5',
            })
            category = QgsRendererCategory(value, symbol, value)
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_junior_high_school_district_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply junior high school district (中学校区) polygon style with A32_004_ja field."""
        from qgis.core import QgsMessageLog, Qgis

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT005 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Log sample values for debugging
        for feature in layer.getFeatures():
            for fn in field_names:
                val = feature[fn]
                if val is not None and str(val).strip():
                    QgsMessageLog.logMessage(f'XKT005 field "{fn}" sample: {val}', 'ReinfoLib', Qgis.Info)
            break

        # Use A32_004_ja field for junior high school district name
        field_name = cls._find_field(layer, [
            'A32_004_ja', 'A32_004', 'school_nam', 'name', 'school', 'gakkou', 'gakko'
        ])

        if not field_name:
            QgsMessageLog.logMessage(
                'XKT005: Could not find A32_004_ja field, using unique values',
                'ReinfoLib', Qgis.Info
            )
            return cls._apply_unique_values_style(layer)

        QgsMessageLog.logMessage(
            f'XKT005: Using field "{field_name}" for styling',
            'ReinfoLib', Qgis.Info
        )

        # Get unique values and assign colors
        unique_values = set()
        for feature in layer.getFeatures():
            val = feature[field_name]
            if val:
                unique_values.add(str(val))

        QgsMessageLog.logMessage(f'XKT005: Found {len(unique_values)} unique school names', 'ReinfoLib', Qgis.Info)

        # Generate distinct colors - using cool colors for junior high schools
        categories = []
        base_colors = [
            (180, 220, 255, 150), (160, 200, 255, 150), (200, 240, 255, 150),
            (170, 230, 255, 150), (190, 210, 255, 150), (210, 250, 255, 150),
            (150, 195, 255, 150), (180, 235, 255, 150), (170, 215, 255, 150),
            (195, 225, 255, 150), (185, 245, 255, 150), (175, 205, 255, 150),
        ]

        for i, value in enumerate(sorted(unique_values)):
            color = base_colors[i % len(base_colors)]
            symbol = QgsFillSymbol.createSimple({
                'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                'outline_color': '0,100,200,255',
                'outline_width': '0.5',
            })
            category = QgsRendererCategory(value, symbol, value)
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_nursery_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply nursery/kindergarten (保育園・幼稚園等) categorical style."""
        from qgis.core import QgsMessageLog, Qgis

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT007 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Find type field
        field_name = cls._find_field(layer, [
            'type', 'facility_t', 'category', 'class', 'shisetsu', 'name'
        ])

        if not field_name:
            return cls._apply_categorical_point_style(layer, cls.NURSERY_COLORS, 'circle', 5)

        QgsMessageLog.logMessage(f'XKT007: Using field "{field_name}" for styling', 'ReinfoLib', Qgis.Info)
        return cls._apply_categorical_point_style_by_field(layer, field_name, cls.NURSERY_COLORS, 'circle', 5)

    @classmethod
    def _apply_welfare_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply welfare facility (福祉施設) categorical style."""
        from qgis.core import QgsMessageLog, Qgis

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT011 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        field_name = cls._find_field(layer, [
            'type', 'facility_t', 'category', 'class', 'shisetsu', 'name'
        ])

        if not field_name:
            return cls._apply_categorical_point_style(layer, cls.WELFARE_COLORS, 'circle', 5)

        QgsMessageLog.logMessage(f'XKT011: Using field "{field_name}" for styling', 'ReinfoLib', Qgis.Info)
        return cls._apply_categorical_point_style_by_field(layer, field_name, cls.WELFARE_COLORS, 'circle', 5)

    @classmethod
    def _apply_station_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply station ridership (駅別乗降客数) graduated style.

        Supports both LineString (railway lines) and Point (stations) geometry.
        """
        from qgis.core import QgsMessageLog, Qgis, QgsWkbTypes, QgsLineSymbol

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT015 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Detect geometry type
        geom_type = layer.geometryType()
        geom_type_name = QgsWkbTypes.geometryDisplayString(geom_type)
        QgsMessageLog.logMessage(f'XKT015 geometry type: {geom_type_name}', 'ReinfoLib', Qgis.Info)

        # Find ridership field - S12_009 is commonly used for ridership data
        field_name = cls._find_field(layer, [
            'S12_009', 'passenger', 'ridership', 'jokou', 'joko', 'users', 'count'
        ])

        if not field_name:
            # Try to use a numeric field
            for f in layer.fields():
                if f.type() in [2, 4, 6]:  # Int, LongLong, Double
                    field_name = f.name()
                    break

        if not field_name:
            QgsMessageLog.logMessage('XKT015: No numeric field found, using default', 'ReinfoLib', Qgis.Warning)
            return cls._apply_default_style(layer)

        QgsMessageLog.logMessage(f'XKT015: Using field "{field_name}" for styling', 'ReinfoLib', Qgis.Info)

        # Station ridership ranges (color, line_width for lines / marker_size for points)
        RIDERSHIP_RANGES = [
            (0, 10000, (100, 200, 255), 1.0, 4),           # ~1万人: light blue
            (10000, 50000, (0, 150, 255), 1.5, 6),         # 1-5万人: blue
            (50000, 100000, (0, 255, 100), 2.0, 8),        # 5-10万人: green
            (100000, 300000, (255, 255, 0), 2.5, 10),      # 10-30万人: yellow
            (300000, 500000, (255, 165, 0), 3.0, 12),      # 30-50万人: orange
            (500000, float('inf'), (255, 0, 0), 4.0, 14),  # 50万人~: red
        ]

        ranges = []

        # Check if geometry is Line type
        is_line = geom_type == QgsWkbTypes.LineGeometry

        for min_val, max_val, color, line_width, marker_size in RIDERSHIP_RANGES:
            if is_line:
                # Use line symbol for LineString geometry
                symbol = QgsLineSymbol.createSimple({
                    'color': f'{color[0]},{color[1]},{color[2]},255',
                    'width': str(line_width),
                    'capstyle': 'round',
                    'joinstyle': 'round',
                })
            else:
                # Use marker symbol for Point geometry
                symbol = QgsMarkerSymbol.createSimple({
                    'name': 'circle',
                    'color': f'{color[0]},{color[1]},{color[2]},200',
                    'size': str(marker_size),
                    'outline_color': '0,0,0,255',
                    'outline_width': '0.5',
                })

            if max_val == float('inf'):
                label = f'{int(min_val/10000)}万人以上'
            else:
                label = f'{int(min_val/10000)}-{int(max_val/10000)}万人'
            range_item = QgsRendererRange(min_val, max_val if max_val != float('inf') else 10000000, symbol, label)
            ranges.append(range_item)

        renderer = QgsGraduatedSymbolRenderer(field_name, ranges)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        QgsMessageLog.logMessage(f'XKT015: Applied {"line" if is_line else "point"} graduated style', 'ReinfoLib', Qgis.Info)
        return True

    @classmethod
    def _apply_library_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply library (図書館) categorical style."""
        from qgis.core import QgsMessageLog, Qgis, QgsWkbTypes

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT022 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Check geometry type
        geom_type = layer.geometryType()
        geom_type_name = QgsWkbTypes.geometryDisplayString(geom_type)
        QgsMessageLog.logMessage(f'XKT022 geometry type: {geom_type_name}', 'ReinfoLib', Qgis.Info)

        # Log sample values for debugging
        for feature in layer.getFeatures():
            for fn in field_names:
                val = feature[fn]
                if val is not None and str(val).strip():
                    QgsMessageLog.logMessage(f'XKT022 field "{fn}" sample: {val}', 'ReinfoLib', Qgis.Info)
            break

        # Find suitable field for categorization
        field_name = cls._find_field(layer, [
            'P27_003', 'P27_004', 'name', 'library_na', 'type', 'category', 'class', 'shurui'
        ])

        # Library colors based on type
        LIBRARY_COLORS = {
            '都道府県立図書館': (139, 0, 139, 200),      # Dark magenta
            '市立図書館': (139, 69, 19, 200),           # Brown
            '市区町村立図書館': (139, 69, 19, 200),     # Brown
            '町立図書館': (160, 82, 45, 200),           # Sienna
            '村立図書館': (160, 82, 45, 200),           # Sienna
            '私立図書館': (205, 133, 63, 200),          # Peru
            '大学図書館': (70, 130, 180, 200),          # Steel blue
            '専門図書館': (100, 149, 237, 200),         # Cornflower blue
        }

        if geom_type == QgsWkbTypes.PointGeometry:
            if field_name:
                # Get unique values
                unique_values = set()
                for feature in layer.getFeatures():
                    val = feature[field_name]
                    if val is not None:
                        unique_values.add(str(val))

                QgsMessageLog.logMessage(f'XKT022: Using field "{field_name}" with values: {list(unique_values)[:10]}', 'ReinfoLib', Qgis.Info)

                if unique_values:
                    categories = []
                    base_colors = [
                        (139, 69, 19, 200), (160, 82, 45, 200), (205, 133, 63, 200),
                        (210, 105, 30, 200), (178, 34, 34, 200), (165, 42, 42, 200),
                    ]
                    used_idx = 0

                    for value in sorted(unique_values):
                        matched_color = None
                        for key, color in LIBRARY_COLORS.items():
                            if key in value or value in key:
                                matched_color = color
                                break

                        if matched_color:
                            color = matched_color
                        else:
                            color = base_colors[used_idx % len(base_colors)]
                            used_idx += 1

                        symbol = QgsMarkerSymbol.createSimple({
                            'name': 'square',
                            'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                            'size': '5',
                            'outline_color': '255,255,255,255',
                            'outline_width': '0.5',
                        })
                        category = QgsRendererCategory(value, symbol, value)
                        categories.append(category)

                    renderer = QgsCategorizedSymbolRenderer(field_name, categories)
                    layer.setRenderer(renderer)
                    layer.triggerRepaint()
                    return True

            # Default single symbol for points
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'square',
                'color': '139,69,19,200',  # Brown
                'size': '5',
                'outline_color': '255,255,255,255',
                'outline_width': '0.5',
            })
            renderer = QgsSingleSymbolRenderer(symbol)
        else:
            # For non-point geometries, use default
            QgsMessageLog.logMessage(f'XKT022: Unexpected geometry type, using default', 'ReinfoLib', Qgis.Warning)
            return cls._apply_default_style(layer)

        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_municipal_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply municipal office (市区町村役場等) categorical style."""
        from qgis.core import QgsMessageLog, Qgis, QgsWkbTypes
        from ..core.settings_manager import SettingsManager
        import hashlib

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT023 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Check geometry type
        geom_type = layer.geometryType()
        geom_type_name = QgsWkbTypes.geometryDisplayString(geom_type)
        QgsMessageLog.logMessage(f'XKT023 geometry type: {geom_type_name}', 'ReinfoLib', Qgis.Info)

        # Log sample values for debugging
        for feature in layer.getFeatures():
            for fn in field_names:
                val = feature[fn]
                if val is not None and str(val).strip():
                    QgsMessageLog.logMessage(f'XKT023 field "{fn}" sample: {val}', 'ReinfoLib', Qgis.Info)
            break

        # Get user's preferred field from settings
        settings = SettingsManager()
        preferred_field = settings.get_xkt023_style_field()
        QgsMessageLog.logMessage(f'XKT023: User preferred field setting: {preferred_field}', 'ReinfoLib', Qgis.Info)

        # Find city_name and plan_name fields
        city_name_field = cls._find_field(layer, ['city_name', 'P05_003', 'shikuchoson', 'city'])
        plan_name_field = cls._find_field(layer, ['plan_name', 'P05_004', 'shisetsu', 'facility', 'name'])

        QgsMessageLog.logMessage(f'XKT023: city_name_field found: {city_name_field}', 'ReinfoLib', Qgis.Info)
        QgsMessageLog.logMessage(f'XKT023: plan_name_field found: {plan_name_field}', 'ReinfoLib', Qgis.Info)

        # Select field based on user preference
        if preferred_field == 'city_name' and city_name_field:
            field_name = city_name_field
        elif preferred_field == 'plan_name' and plan_name_field:
            field_name = plan_name_field
        elif city_name_field:
            field_name = city_name_field
        elif plan_name_field:
            field_name = plan_name_field
        else:
            # Fallback: try other fields
            field_name = cls._find_field(layer, [
                'P05_003', 'P05_004', 'P05_002', 'type', 'facility_t', 'category', 'class'
            ])

        QgsMessageLog.logMessage(f'XKT023: Using field for styling: {field_name}', 'ReinfoLib', Qgis.Info)

        # Get unique values if field found
        unique_values = set()
        if field_name:
            for feature in layer.getFeatures():
                val = feature[field_name]
                if val is not None:
                    unique_values.add(str(val))
            QgsMessageLog.logMessage(f'XKT023: Found {len(unique_values)} unique values', 'ReinfoLib', Qgis.Info)

        # Facility type colors (for plan_name)
        FACILITY_COLORS = {
            '市役所': (0, 80, 200, 220),
            '区役所': (0, 120, 200, 220),
            '町役場': (0, 160, 180, 220),
            '村役場': (0, 180, 160, 220),
            '町村役場': (0, 170, 170, 220),
            '支所': (100, 150, 200, 200),
            '出張所': (120, 170, 200, 200),
            '公民館': (200, 120, 60, 220),
            'コミュニティセンター': (180, 100, 50, 220),
            '集会所': (160, 130, 80, 200),
            '地域センター': (170, 110, 70, 200),
        }

        # Function to generate distinct color from string (for city names)
        def generate_color_from_string(s: str) -> Tuple[int, int, int, int]:
            """Generate a distinct color based on string hash."""
            hash_val = int(hashlib.md5(s.encode()).hexdigest()[:8], 16)
            # Use HSV-like approach for better color distribution
            hue = (hash_val % 360)
            # Convert hue to RGB (simplified)
            if hue < 60:
                r, g, b = 255, int(255 * hue / 60), 50
            elif hue < 120:
                r, g, b = int(255 * (120 - hue) / 60), 255, 50
            elif hue < 180:
                r, g, b = 50, 255, int(255 * (hue - 120) / 60)
            elif hue < 240:
                r, g, b = 50, int(255 * (240 - hue) / 60), 255
            elif hue < 300:
                r, g, b = int(255 * (hue - 240) / 60), 50, 255
            else:
                r, g, b = 255, 50, int(255 * (360 - hue) / 60)
            return (r, g, b, 200)

        # Create symbols based on geometry type
        if geom_type == QgsWkbTypes.PointGeometry:
            if field_name and unique_values:
                # Categorical point style
                categories = []

                for value in sorted(unique_values):
                    # Check if using facility type (plan_name) or city name
                    if preferred_field == 'plan_name':
                        # Try to match with facility type colors
                        matched_color = None
                        for key, color in FACILITY_COLORS.items():
                            if key in value or value in key:
                                matched_color = color
                                break
                        if matched_color:
                            color = matched_color
                        else:
                            color = generate_color_from_string(value)
                    else:
                        # City name - generate unique color per city
                        color = generate_color_from_string(value)

                    symbol = QgsMarkerSymbol.createSimple({
                        'name': 'square',
                        'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                        'size': '5',
                        'outline_color': '0,0,0,255',
                        'outline_width': '0.5',
                    })
                    category = QgsRendererCategory(value, symbol, value)
                    categories.append(category)

                renderer = QgsCategorizedSymbolRenderer(field_name, categories)
            else:
                # Default single symbol
                symbol = QgsMarkerSymbol.createSimple({
                    'name': 'square',
                    'color': '0,100,200,200',
                    'size': '5',
                    'outline_color': '0,0,0,255',
                    'outline_width': '0.5',
                })
                renderer = QgsSingleSymbolRenderer(symbol)
        else:
            # For non-point geometries, use fill/line symbols
            QgsMessageLog.logMessage(f'XKT023: Unexpected geometry type, using default', 'ReinfoLib', Qgis.Warning)
            return cls._apply_default_style(layer)

        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_did_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply DID (人口集中地区) style with population-based coloring."""
        from qgis.core import QgsMessageLog, Qgis

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT031 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Try to find population field for graduated style
        pop_field = cls._find_field(layer, [
            'population', 'jinko', 'pop', 'total_pop', 'did_pop'
        ])

        if pop_field:
            QgsMessageLog.logMessage(f'XKT031: Using field "{pop_field}" for graduated style', 'ReinfoLib', Qgis.Info)

            # Population density ranges
            POP_RANGES = [
                (0, 5000, (255, 255, 200, 150)),        # ~5000人: light yellow
                (5000, 10000, (255, 255, 100, 150)),    # 5000-1万人: yellow
                (10000, 30000, (255, 200, 100, 150)),   # 1-3万人: orange-yellow
                (30000, 50000, (255, 150, 100, 150)),   # 3-5万人: light orange
                (50000, 100000, (255, 100, 100, 150)),  # 5-10万人: light red
                (100000, float('inf'), (200, 50, 50, 150)),  # 10万人~: dark red
            ]

            ranges = []
            for min_val, max_val, color in POP_RANGES:
                symbol = QgsFillSymbol.createSimple({
                    'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                    'outline_color': '0,0,0,255',
                    'outline_width': '0.3',
                })
                if max_val == float('inf'):
                    label = f'{int(min_val/10000)}万人以上'
                else:
                    label = f'{int(min_val)}-{int(max_val)}人'
                range_item = QgsRendererRange(min_val, max_val if max_val != float('inf') else 10000000, symbol, label)
                ranges.append(range_item)

            renderer = QgsGraduatedSymbolRenderer(pop_field, ranges)
            layer.setRenderer(renderer)
            layer.triggerRepaint()
            return True

        # Fallback to categorical by name/area
        name_field = cls._find_field(layer, ['name', 'did_name', 'area_name', 'city_name'])
        if name_field:
            QgsMessageLog.logMessage(f'XKT031: Using field "{name_field}" for categorical style', 'ReinfoLib', Qgis.Info)
            return cls._apply_unique_values_style(layer)

        # Default single color
        symbol = QgsFillSymbol.createSimple({
            'color': '255,200,150,150',
            'outline_color': '200,100,50,255',
            'outline_width': '0.5',
        })
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_storm_surge_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply storm surge (高潮浸水想定区域) categorical/graduated style."""
        from qgis.core import QgsMessageLog, Qgis

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT027 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Log sample values for debugging
        for feature in layer.getFeatures():
            for fn in field_names:
                val = feature[fn]
                if val is not None and str(val).strip():
                    QgsMessageLog.logMessage(f'XKT027 field "{fn}" sample: {val}', 'ReinfoLib', Qgis.Info)
            break

        # Use A49_003 field for storm surge depth
        field_name = cls._find_field(layer, ['A49_003', 'depth', 'shinsui', 'rank', 'class', 'takashio', 'note'])

        if not field_name:
            # Try any field with values
            for f in layer.fields():
                field_name = f.name()
                break

        if not field_name:
            QgsMessageLog.logMessage('XKT027: No suitable field found', 'ReinfoLib', Qgis.Warning)
            return cls._apply_default_style(layer)

        QgsMessageLog.logMessage(f'XKT027: Using field "{field_name}" for styling', 'ReinfoLib', Qgis.Info)

        # Get unique values to determine if categorical or graduated styling
        unique_values = set()
        for feature in layer.getFeatures():
            val = feature[field_name]
            if val is not None:
                unique_values.add(str(val))

        QgsMessageLog.logMessage(f'XKT027: Found values: {list(unique_values)[:10]}', 'ReinfoLib', Qgis.Info)

        # Storm surge categorical colors by depth description (A49_003 format)
        # Colors from light blue (shallow) to dark purple (deep)
        SURGE_COLORS = {
            # Exact matches for A49_003 field values
            '0.3m未満': (220, 240, 255, 180),               # Very light blue - very shallow
            '0.3m以上0.5m未満': (200, 220, 255, 180),       # Light blue
            '0.5m未満': (200, 220, 255, 180),               # Light blue
            '0.5m以上1.0m未満': (150, 200, 255, 180),       # Blue
            '1.0m未満': (150, 200, 255, 180),               # Blue
            '1.0m以上2.0m未満': (100, 150, 255, 180),       # Medium blue
            '2.0m未満': (100, 150, 255, 180),               # Medium blue
            '2.0m以上3.0m未満': (50, 100, 220, 180),        # Dark blue
            '3.0m未満': (50, 100, 220, 180),                # Dark blue
            '3.0m以上5.0m未満': (30, 60, 180, 200),         # Darker blue
            '5.0m未満': (30, 60, 180, 200),                 # Darker blue
            '5.0m以上10.0m未満': (20, 30, 140, 220),        # Very dark blue
            '10.0m未満': (20, 30, 140, 220),                # Very dark blue
            '10.0m以上20.0m未満': (60, 0, 120, 220),        # Purple
            '20.0m以上': (100, 0, 100, 220),                # Dark purple - very deep
        }

        # Use categorical styling
        categories = []
        base_blues = [
            (200, 220, 255, 180), (150, 200, 255, 180), (100, 150, 255, 180),
            (50, 100, 200, 180), (0, 50, 150, 180), (50, 0, 100, 180),
        ]
        used_idx = 0

        for value in sorted(unique_values):
            matched_color = None
            for key, color in SURGE_COLORS.items():
                if key in value or value in key:
                    matched_color = color
                    break

            if matched_color:
                color = matched_color
            else:
                color = base_blues[used_idx % len(base_blues)]
                used_idx += 1

            symbol = QgsFillSymbol.createSimple({
                'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                'outline_color': '0,0,100,255',
                'outline_width': '0.2',
            })
            category = QgsRendererCategory(value, symbol, value)
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_disaster_risk_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply disaster risk area (災害危険区域) style."""
        from qgis.core import QgsMessageLog, Qgis, QgsWkbTypes

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT018 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Detect geometry type
        geom_type = layer.geometryType()
        geom_type_name = QgsWkbTypes.geometryDisplayString(geom_type)
        QgsMessageLog.logMessage(f'XKT018 geometry type: {geom_type_name}', 'ReinfoLib', Qgis.Info)

        if geom_type == QgsWkbTypes.PointGeometry:
            # Point style - red circle
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'circle',
                'color': '255,0,0,200',
                'size': '6',
                'outline_color': '139,0,0,255',
                'outline_width': '1',
            })
        else:
            # Polygon style - red fill
            symbol = QgsFillSymbol.createSimple({
                'color': '255,100,100,150',
                'outline_color': '200,0,0,255',
                'outline_width': '0.5',
            })

        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_large_fill_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply large fill area (大規模盛土造成地) categorical style based on note/topography field."""
        from qgis.core import QgsMessageLog, Qgis
        from ..core.settings_manager import SettingsManager

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT025 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Log sample values for each field to help identify correct field
        for feature in layer.getFeatures():
            for field_name in field_names:
                val = feature[field_name]
                if val is not None and str(val).strip():
                    QgsMessageLog.logMessage(f'XKT025 field "{field_name}" sample: {val}', 'ReinfoLib', Qgis.Info)
            break  # Only log first feature

        # Get user's preferred field from settings
        settings = SettingsManager()
        preferred_field = settings.get_xkt025_style_field()
        QgsMessageLog.logMessage(f'XKT025: User preferred field setting: {preferred_field}', 'ReinfoLib', Qgis.Info)

        # Try to find both fields first
        topography_field = cls._find_field(layer, ['topography', 'topo', 'chikei', 'classification', 'bunrui', 'type'])
        note_field = cls._find_field(layer, ['note', 'remarks', 'A46_007', 'A46_008'])

        QgsMessageLog.logMessage(f'XKT025: topography_field found: {topography_field}', 'ReinfoLib', Qgis.Info)
        QgsMessageLog.logMessage(f'XKT025: note_field found: {note_field}', 'ReinfoLib', Qgis.Info)

        # Select field based on user preference
        if preferred_field == 'topography' and topography_field:
            field_name = topography_field
        elif preferred_field == 'note' and note_field:
            field_name = note_field
        elif topography_field:
            field_name = topography_field
        elif note_field:
            field_name = note_field
        else:
            # Fallback: find any suitable field
            field_name = cls._find_field(layer, field_names)

        # Large fill area colors - distinct colors for liquefaction risk levels
        # More saturated and distinct colors for better visibility
        FILL_COLORS = {
            # Liquefaction risk levels - clearly distinct colors
            '非常に液状化しやすい': (139, 0, 0, 220),      # Dark red - very high risk
            '液状化しやすい': (255, 0, 0, 200),            # Red - high risk
            'やや液状化しやすい': (255, 140, 0, 200),      # Orange - moderate-high risk
            '評価対象外': (128, 128, 128, 180),            # Gray - not evaluated
            'やや液状化しにくい': (144, 238, 144, 200),    # Light green - moderate-low risk
            '液状化しにくい': (0, 200, 0, 200),            # Green - low risk
            # Topography types
            '谷埋め型': (180, 0, 180, 200),                # Purple - valley fill
            '谷埋め': (180, 0, 180, 200),                  # Purple - valley fill
            '腹付け型': (0, 100, 200, 200),                # Blue - slope fill
            '腹付け': (0, 100, 200, 200),                  # Blue - slope fill
            '大規模盛土': (255, 165, 0, 180),              # Orange - large fill
            '盛土': (255, 200, 100, 180),                  # Light orange - general fill
        }

        if field_name:
            QgsMessageLog.logMessage(f'XKT025: Using field "{field_name}" for styling', 'ReinfoLib', Qgis.Info)

            # Get unique values
            unique_values = set()
            for feature in layer.getFeatures():
                val = feature[field_name]
                if val:
                    unique_values.add(str(val))

            QgsMessageLog.logMessage(f'XKT025: Found values: {list(unique_values)[:20]}', 'ReinfoLib', Qgis.Info)

            categories = []
            base_colors = [
                (255, 180, 100, 180), (255, 150, 80, 180), (255, 120, 60, 180),
                (255, 200, 120, 180), (255, 100, 50, 180),
            ]
            used_idx = 0

            for value in sorted(unique_values):
                matched_color = None
                # Check if the value contains any of the known keywords
                for key, color in FILL_COLORS.items():
                    if key in value:
                        matched_color = color
                        break

                if matched_color:
                    color = matched_color
                else:
                    color = base_colors[used_idx % len(base_colors)]
                    used_idx += 1

                symbol = QgsFillSymbol.createSimple({
                    'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                    'outline_color': '150,75,0,255',
                    'outline_width': '0.3',
                })
                category = QgsRendererCategory(value, symbol, value)
                categories.append(category)

            # Default for empty/null values
            default_symbol = QgsFillSymbol.createSimple({
                'color': '255,200,150,150',
                'outline_color': '150,75,0,255',
                'outline_width': '0.3',
            })
            categories.append(QgsRendererCategory('', default_symbol, 'その他'))

            renderer = QgsCategorizedSymbolRenderer(field_name, categories)
            layer.setRenderer(renderer)
            layer.triggerRepaint()
            return True

        # Default single color if no suitable field found
        symbol = QgsFillSymbol.createSimple({
            'color': '255,180,100,150',
            'outline_color': '150,75,0,255',
            'outline_width': '0.5',
        })
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_population_mesh_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply population projection mesh (将来推計人口メッシュ) graduated style."""
        from qgis.core import QgsMessageLog, Qgis, QgsWkbTypes
        from ..core.settings_manager import SettingsManager

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT013 all fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Check geometry type
        geom_type = layer.geometryType()
        geom_type_name = QgsWkbTypes.geometryDisplayString(geom_type)
        QgsMessageLog.logMessage(f'XKT013 geometry type: {geom_type_name}', 'ReinfoLib', Qgis.Info)

        # Log ALL field values for first feature
        for feature in layer.getFeatures():
            QgsMessageLog.logMessage(f'XKT013 sample feature fields:', 'ReinfoLib', Qgis.Info)
            for fn in field_names:
                val = feature[fn]
                QgsMessageLog.logMessage(f'  {fn} = {val} (type: {type(val).__name__})', 'ReinfoLib', Qgis.Info)
            break

        # Get user's preferences from settings
        settings = SettingsManager()
        selected_year = settings.get_xkt013_year()
        selected_field_prefix = settings.get_xkt013_field()
        data_type = settings.get_xkt013_data_type()

        QgsMessageLog.logMessage(f'XKT013: User selected year: {selected_year}, field: {selected_field_prefix}, type: {data_type}', 'ReinfoLib', Qgis.Info)

        # Build the full field name: PREFIX_YEAR (e.g., PTN_2020, PT01_2020, RTA_2020)
        target_field = f'{selected_field_prefix}_{selected_year}'
        QgsMessageLog.logMessage(f'XKT013: Looking for field: {target_field}', 'ReinfoLib', Qgis.Info)

        # Select population field based on user's selection
        pop_field = None

        # First try exact field name
        for fn in field_names:
            if fn == target_field:
                pop_field = fn
                break

        # If not found, try without underscore
        if not pop_field:
            target_field_no_underscore = f'{selected_field_prefix}{selected_year}'
            for fn in field_names:
                if fn == target_field_no_underscore:
                    pop_field = fn
                    break

        # If not found, try other years as fallback
        if not pop_field:
            fallback_years = ['2020', '2025', '2030', '2035', '2040', '2045', '2050']
            for year in fallback_years:
                for fn in field_names:
                    if fn == f'{selected_field_prefix}_{year}' or fn == f'{selected_field_prefix}{year}':
                        pop_field = fn
                        QgsMessageLog.logMessage(f'XKT013: Selected field not found, using {pop_field}', 'ReinfoLib', Qgis.Warning)
                        break
                if pop_field:
                    break

        # If still not found, try PTN as default
        if not pop_field:
            for fn in field_names:
                if fn.startswith('PTN'):
                    pop_field = fn
                    break

        # Last resort: find any numeric field
        if not pop_field:
            for f in layer.fields():
                if f.type() in [2, 4, 6]:  # Int, LongLong, Double
                    pop_field = f.name()
                    QgsMessageLog.logMessage(f'XKT013: Using numeric field as fallback: {pop_field}', 'ReinfoLib', Qgis.Info)
                    break

        # Determine if this is a ratio field (different range)
        is_ratio = selected_field_prefix.startswith('RT')

        if not pop_field:
            QgsMessageLog.logMessage('XKT013: No suitable field found, using default style', 'ReinfoLib', Qgis.Warning)
            return cls._apply_default_style(layer)

        QgsMessageLog.logMessage(f'XKT013: Using field "{pop_field}" for graduated style', 'ReinfoLib', Qgis.Info)

        # Get actual min/max values from data
        min_data_val = float('inf')
        max_data_val = float('-inf')
        for feature in layer.getFeatures():
            val = feature[pop_field]
            if val is not None:
                try:
                    num_val = float(val)
                    if num_val < min_data_val:
                        min_data_val = num_val
                    if num_val > max_data_val:
                        max_data_val = num_val
                except (ValueError, TypeError):
                    pass

        QgsMessageLog.logMessage(f'XKT013: Data range for {pop_field}: {min_data_val} - {max_data_val}', 'ReinfoLib', Qgis.Info)

        # Define ranges based on data type
        if is_ratio:
            # Check if values are 0-1 (decimal) or 0-100 (percentage)
            if max_data_val <= 1.0:
                # Values are decimals (0.0 - 1.0)
                QgsMessageLog.logMessage(f'XKT013: Ratio values appear to be decimals (0-1)', 'ReinfoLib', Qgis.Info)
                DATA_RANGES = [
                    (0, 0.05, (255, 255, 230, 150), '0-5%'),
                    (0.05, 0.10, (255, 255, 180, 150), '5-10%'),
                    (0.10, 0.15, (255, 240, 130, 150), '10-15%'),
                    (0.15, 0.20, (255, 220, 100, 150), '15-20%'),
                    (0.20, 0.25, (255, 200, 80, 150), '20-25%'),
                    (0.25, 0.30, (255, 170, 60, 150), '25-30%'),
                    (0.30, 0.40, (255, 130, 50, 150), '30-40%'),
                    (0.40, 0.50, (240, 90, 40, 150), '40-50%'),
                    (0.50, 1.0, (200, 50, 30, 180), '50%以上'),
                ]
            else:
                # Values are percentages (0 - 100)
                QgsMessageLog.logMessage(f'XKT013: Ratio values appear to be percentages (0-100)', 'ReinfoLib', Qgis.Info)
                DATA_RANGES = [
                    (0, 5, (255, 255, 230, 150), '0-5%'),
                    (5, 10, (255, 255, 180, 150), '5-10%'),
                    (10, 15, (255, 240, 130, 150), '10-15%'),
                    (15, 20, (255, 220, 100, 150), '15-20%'),
                    (20, 25, (255, 200, 80, 150), '20-25%'),
                    (25, 30, (255, 170, 60, 150), '25-30%'),
                    (30, 40, (255, 130, 50, 150), '30-40%'),
                    (40, 50, (240, 90, 40, 150), '40-50%'),
                    (50, 100, (200, 50, 30, 180), '50%以上'),
                ]
        else:
            # Population ranges for 250m mesh
            DATA_RANGES = [
                (0, 50, (255, 255, 230, 150), '0-50人'),
                (50, 100, (255, 255, 180, 150), '50-100人'),
                (100, 200, (255, 240, 130, 150), '100-200人'),
                (200, 500, (255, 200, 80, 150), '200-500人'),
                (500, 1000, (255, 150, 60, 150), '500-1000人'),
                (1000, 2000, (255, 100, 50, 150), '1000-2000人'),
                (2000, 5000, (220, 60, 40, 150), '2000-5000人'),
                (5000, float('inf'), (180, 30, 30, 180), '5000人以上'),
            ]

        ranges = []
        for min_val, max_val, color, label in DATA_RANGES:
            if geom_type == QgsWkbTypes.PolygonGeometry:
                symbol = QgsFillSymbol.createSimple({
                    'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                    'outline_color': '100,100,100,255',
                    'outline_width': '0.2',
                })
            elif geom_type == QgsWkbTypes.PointGeometry:
                symbol = QgsMarkerSymbol.createSimple({
                    'name': 'square',
                    'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                    'size': '4',
                    'outline_color': '100,100,100,255',
                    'outline_width': '0.3',
                })
            else:
                symbol = QgsLineSymbol.createSimple({
                    'color': f'{color[0]},{color[1]},{color[2]},255',
                    'width': '1',
                })

            range_item = QgsRendererRange(min_val, max_val if max_val != float('inf') else 100000, symbol, label)
            ranges.append(range_item)

        renderer = QgsGraduatedSymbolRenderer(pop_field, ranges)
        layer.setRenderer(renderer)

        # Add labels to show the values on the mesh
        from qgis.core import QgsPalLayerSettings, QgsVectorLayerSimpleLabeling, QgsTextFormat
        from qgis.PyQt.QtGui import QFont, QColor

        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = pop_field
        label_settings.enabled = True

        # Format the label based on data type
        if is_ratio:
            # Show as percentage
            label_settings.isExpression = True
            label_settings.fieldName = f'round("{pop_field}" * 100, 1) || \'%\''
        else:
            # Show as integer
            label_settings.isExpression = True
            label_settings.fieldName = f'round("{pop_field}", 0)'

        # Text format
        text_format = QgsTextFormat()
        font = QFont('Yu Gothic UI', 8)
        text_format.setFont(font)
        text_format.setColor(QColor(0, 0, 0))
        text_format.setSize(8)

        # Add buffer/halo for readability
        buffer = text_format.buffer()
        buffer.setEnabled(True)
        buffer.setSize(1)
        buffer.setColor(QColor(255, 255, 255))
        text_format.setBuffer(buffer)

        label_settings.setFormat(text_format)

        labeling = QgsVectorLayerSimpleLabeling(label_settings)
        layer.setLabeling(labeling)
        layer.setLabelsEnabled(True)

        QgsMessageLog.logMessage(f'XKT013: Added labels for field {pop_field}', 'ReinfoLib', Qgis.Info)

        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_natural_park_style(cls, layer: QgsVectorLayer) -> bool:
        """Apply natural park (自然公園地域) simple style with labels."""
        from qgis.core import (
            QgsMessageLog, Qgis, QgsWkbTypes,
            QgsPalLayerSettings, QgsVectorLayerSimpleLabeling, QgsTextFormat
        )
        from qgis.PyQt.QtGui import QFont, QColor

        field_names = [f.name() for f in layer.fields()]
        QgsMessageLog.logMessage(f'XKT019 fields: {field_names}', 'ReinfoLib', Qgis.Info)

        # Check geometry type
        geom_type = layer.geometryType()
        geom_type_name = QgsWkbTypes.geometryDisplayString(geom_type)
        QgsMessageLog.logMessage(f'XKT019 geometry type: {geom_type_name}', 'ReinfoLib', Qgis.Info)

        # Log sample values for debugging
        for feature in layer.getFeatures():
            for fn in field_names:
                val = feature[fn]
                if val is not None and str(val).strip():
                    QgsMessageLog.logMessage(f'XKT019 field "{fn}" sample: {val}', 'ReinfoLib', Qgis.Info)
            break

        # Single green color for all natural parks
        if geom_type == QgsWkbTypes.PolygonGeometry:
            symbol = QgsFillSymbol.createSimple({
                'color': '100,180,100,150',
                'outline_color': '0,100,0,255',
                'outline_width': '0.5',
            })
        elif geom_type == QgsWkbTypes.PointGeometry:
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'triangle',
                'color': '100,180,100,200',
                'size': '5',
                'outline_color': '0,100,0,255',
                'outline_width': '0.5',
            })
        else:
            symbol = QgsLineSymbol.createSimple({
                'color': '0,150,0,255',
                'width': '1',
            })

        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)

        # Add labels using OBJ_NAME_j field
        label_field = cls._find_field(layer, ['OBJ_NAME_j', 'OBJ_NAME', 'name', 'park_name'])
        if label_field:
            QgsMessageLog.logMessage(f'XKT019: Adding labels using field "{label_field}"', 'ReinfoLib', Qgis.Info)

            label_settings = QgsPalLayerSettings()
            label_settings.fieldName = label_field
            label_settings.enabled = True

            # Filter: don't show label when value is "0"
            label_settings.drawLabels = True
            label_settings.isExpression = True
            label_settings.fieldName = f'CASE WHEN "{label_field}" = \'0\' OR "{label_field}" IS NULL THEN \'\' ELSE "{label_field}" END'

            # Text format
            text_format = QgsTextFormat()
            font = QFont('Yu Gothic UI', 9)
            text_format.setFont(font)
            text_format.setColor(QColor(0, 80, 0))
            text_format.setSize(9)

            # Add buffer/halo for readability
            buffer = text_format.buffer()
            buffer.setEnabled(True)
            buffer.setSize(1)
            buffer.setColor(QColor(255, 255, 255))
            text_format.setBuffer(buffer)

            label_settings.setFormat(text_format)

            labeling = QgsVectorLayerSimpleLabeling(label_settings)
            layer.setLabeling(labeling)
            layer.setLabelsEnabled(True)

        layer.triggerRepaint()
        return True

    @classmethod
    def _apply_categorical_point_style(cls, layer: QgsVectorLayer,
                                        color_dict: Dict, marker: str, size: int) -> bool:
        """Apply categorical point style using unique values."""
        from qgis.core import QgsMessageLog, Qgis

        # Find first string field for categorization
        string_fields = [f for f in layer.fields() if f.type() == 10]
        if not string_fields:
            return cls._apply_default_style(layer)

        field_name = string_fields[0].name()
        return cls._apply_categorical_point_style_by_field(layer, field_name, color_dict, marker, size)

    @classmethod
    def _apply_categorical_point_style_by_field(cls, layer: QgsVectorLayer,
                                                 field_name: str, color_dict: Dict,
                                                 marker: str, size: int) -> bool:
        """Apply categorical point style by field with color matching."""
        from qgis.core import QgsMessageLog, Qgis

        # Get unique values
        unique_values = set()
        for feature in layer.getFeatures():
            val = feature[field_name]
            if val:
                unique_values.add(str(val))

        QgsMessageLog.logMessage(
            f'Found {len(unique_values)} unique values: {list(unique_values)[:5]}',
            'ReinfoLib', Qgis.Info
        )

        categories = []
        base_colors = [
            (255, 100, 100, 200), (100, 255, 100, 200), (100, 100, 255, 200),
            (255, 255, 100, 200), (255, 100, 255, 200), (100, 255, 255, 200),
            (255, 180, 100, 200), (100, 255, 180, 200), (180, 100, 255, 200),
        ]
        used_idx = 0

        for value in sorted(unique_values):
            # Try to match with predefined colors
            matched_color = None
            for key, color in color_dict.items():
                if key in value or value in key:
                    matched_color = color
                    break

            if matched_color:
                color = matched_color
            else:
                color = base_colors[used_idx % len(base_colors)]
                used_idx += 1

            symbol = QgsMarkerSymbol.createSimple({
                'name': marker,
                'color': f'{color[0]},{color[1]},{color[2]},{color[3]}',
                'size': str(size),
                'outline_color': '0,0,0,255',
                'outline_width': '0.5',
            })
            category = QgsRendererCategory(value, symbol, value)
            categories.append(category)

        # Default for empty values
        default_symbol = QgsMarkerSymbol.createSimple({
            'name': marker,
            'color': '180,180,180,200',
            'size': str(size),
            'outline_color': '0,0,0,255',
            'outline_width': '0.5',
        })
        categories.append(QgsRendererCategory('', default_symbol, 'その他'))

        renderer = QgsCategorizedSymbolRenderer(field_name, categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        return True

    @staticmethod
    def _parse_price_string(price_str: str) -> Optional[float]:
        """Parse Japanese price string to numeric value in yen.

        Examples:
            "1,500万円" -> 15000000
            "63,000万円" -> 630000000
            "5,000円" -> 5000
            "1億2,000万円" -> 120000000
        """
        import re
        from qgis.core import QgsMessageLog, Qgis

        if not price_str or not isinstance(price_str, str):
            return None

        try:
            # Remove commas and spaces
            clean = price_str.replace(',', '').replace(' ', '').replace('　', '')

            total = 0.0

            # Check for 億 (100 million)
            oku_match = re.search(r'(\d+(?:\.\d+)?)億', clean)
            if oku_match:
                total += float(oku_match.group(1)) * 100000000

            # Check for 万 (10 thousand)
            man_match = re.search(r'(\d+(?:\.\d+)?)万', clean)
            if man_match:
                total += float(man_match.group(1)) * 10000

            # Check for plain yen (円 without 万 or 億 prefix)
            if '万' not in clean and '億' not in clean:
                yen_match = re.search(r'(\d+(?:\.\d+)?)円?', clean)
                if yen_match:
                    total = float(yen_match.group(1))

            if total > 0:
                return total

            # Try to extract any number as fallback
            numbers = re.findall(r'\d+(?:\.\d+)?', clean)
            if numbers:
                return float(numbers[0])

            return None

        except (ValueError, TypeError) as e:
            QgsMessageLog.logMessage(
                f'Failed to parse price: {price_str}: {e}',
                'ReinfoLib', Qgis.Warning
            )
            return None

    @staticmethod
    def _find_field(layer: QgsVectorLayer, candidates: List[str]) -> Optional[str]:
        """Find a field from a list of candidates."""
        field_names = [f.name().lower() for f in layer.fields()]

        for candidate in candidates:
            if candidate.lower() in field_names:
                idx = field_names.index(candidate.lower())
                return layer.fields()[idx].name()

        # Try partial match
        for candidate in candidates:
            for i, name in enumerate(field_names):
                if candidate.lower() in name:
                    return layer.fields()[i].name()

        return None
