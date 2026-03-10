# -*- coding: utf-8 -*-
"""
Data Converter for ReinfoLib QGIS Plugin

Converts API responses to QGIS layers.
"""

import json
import warnings
from typing import Optional, Dict, Any, List

from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsFields,
    QgsVectorFileWriter,
    QgsMessageLog,
    QgsPointXY,
    Qgis,
)
from qgis.PyQt.QtCore import QVariant

from .api_definitions import ApiInfo


class DataConverter:
    """Converts API data to QGIS layers."""

    # Geometry type mapping
    GEOMETRY_TYPES = {
        'point': 'Point',
        'polygon': 'Polygon',
        'line': 'LineString',
        'multipoint': 'MultiPoint',
        'multipolygon': 'MultiPolygon',
        'multiline': 'MultiLineString',
    }

    # Output format mapping
    OUTPUT_DRIVERS = {
        'gpkg': 'GPKG',
        'geojson': 'GeoJSON',
        'shp': 'ESRI Shapefile',
        'csv': 'CSV',
    }

    @staticmethod
    def _log(message: str, level: Qgis.MessageLevel = Qgis.Info) -> None:
        """Log a message to QGIS log panel."""
        QgsMessageLog.logMessage(message, 'ReinfoLib', level)

    @classmethod
    def geojson_to_layer(
        cls,
        geojson_data: Dict[str, Any],
        layer_name: str,
        api_info: Optional[ApiInfo] = None
    ) -> Optional[QgsVectorLayer]:
        """Convert GeoJSON data to a memory layer.

        Args:
            geojson_data: GeoJSON FeatureCollection dict.
            layer_name: Name for the layer.
            api_info: Optional API info for metadata.

        Returns:
            QgsVectorLayer or None if conversion fails.
        """
        cls._log(f'=== Starting GeoJSON to Layer conversion: {layer_name} ===')

        features = geojson_data.get('features', [])
        if not features:
            cls._log(f'No features in GeoJSON for {layer_name}', Qgis.Warning)
            return None

        cls._log(f'Input features count: {len(features)}')

        # Detect geometry type from first feature
        geometry_type = cls._detect_geometry_type(features)
        if not geometry_type:
            cls._log(f'Could not detect geometry type for {layer_name}', Qgis.Warning)
            return None

        cls._log(f'Detected geometry type: {geometry_type}')

        # Create memory layer
        uri = f'{geometry_type}?crs=EPSG:4326'
        layer = QgsVectorLayer(uri, layer_name, 'memory')

        if not layer.isValid():
            cls._log(f'Failed to create layer: {layer_name}', Qgis.Warning)
            return None

        # Detect and add fields
        fields = cls._detect_fields(features)
        cls._log(f'Detected {len(fields)} fields')
        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        # Add features
        qgs_features = []
        failed_count = 0
        for i, feature in enumerate(features):
            qgs_feature = cls._convert_feature(feature, layer.fields())
            if qgs_feature:
                qgs_features.append(qgs_feature)
                # Log first few features for debugging
                if i < 3:
                    geom = qgs_feature.geometry()
                    if geom and not geom.isNull():
                        centroid = geom.centroid().asPoint()
                        cls._log(f'Feature {i}: centroid=({centroid.x():.6f}, {centroid.y():.6f})')
            else:
                failed_count += 1

        if failed_count > 0:
            cls._log(f'Failed to convert {failed_count} features', Qgis.Warning)

        layer.dataProvider().addFeatures(qgs_features)
        layer.updateExtents()

        # Log layer extent
        extent = layer.extent()
        cls._log(f'Layer extent: xmin={extent.xMinimum():.6f}, ymin={extent.yMinimum():.6f}, '
                 f'xmax={extent.xMaximum():.6f}, ymax={extent.yMaximum():.6f}')
        cls._log(f'Created layer {layer_name} with {len(qgs_features)} features')

        return layer

    @classmethod
    def _detect_geometry_type(cls, features: List[Dict]) -> Optional[str]:
        """Detect QGIS geometry type from GeoJSON features."""
        for feature in features:
            geom = feature.get('geometry')
            if geom and 'type' in geom:
                geom_type = geom['type'].lower()
                if geom_type == 'point':
                    return 'Point'
                elif geom_type == 'multipoint':
                    return 'MultiPoint'
                elif geom_type == 'linestring':
                    return 'LineString'
                elif geom_type == 'multilinestring':
                    return 'MultiLineString'
                elif geom_type == 'polygon':
                    return 'Polygon'
                elif geom_type == 'multipolygon':
                    return 'MultiPolygon'
        return None

    @classmethod
    def _detect_fields(cls, features: List[Dict]) -> List[QgsField]:
        """Detect fields from GeoJSON features."""
        field_types: Dict[str, QVariant.Type] = {}

        for feature in features[:100]:  # Sample first 100 features
            props = feature.get('properties', {})
            if not props:
                continue

            for key, value in props.items():
                if key not in field_types:
                    field_types[key] = cls._python_to_qvariant_type(value)

        fields = []
        for name, qtype in field_types.items():
            # Truncate field names for Shapefile compatibility
            field_name = name[:10] if len(name) > 10 else name
            type_name = cls._qvariant_to_type_name(qtype)
            # Suppress deprecation warning for QgsField constructor
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                field = QgsField(field_name, qtype, type_name)
            fields.append(field)

        return fields

    @staticmethod
    def _qvariant_to_type_name(qtype: QVariant.Type) -> str:
        """Convert QVariant type to type name string."""
        type_names = {
            QVariant.Bool: 'Boolean',
            QVariant.Int: 'Integer',
            QVariant.LongLong: 'Integer64',
            QVariant.Double: 'Real',
            QVariant.String: 'String',
        }
        return type_names.get(qtype, 'String')

    @staticmethod
    def _python_to_qvariant_type(value: Any) -> QVariant.Type:
        """Convert Python type to QVariant type."""
        if isinstance(value, bool):
            return QVariant.Bool
        elif isinstance(value, int):
            return QVariant.Int
        elif isinstance(value, float):
            return QVariant.Double
        elif isinstance(value, (list, dict)):
            return QVariant.String  # Store as JSON string
        else:
            return QVariant.String

    @classmethod
    def _convert_feature(
        cls,
        geojson_feature: Dict,
        fields: QgsFields
    ) -> Optional[QgsFeature]:
        """Convert a GeoJSON feature to QgsFeature."""
        geom_dict = geojson_feature.get('geometry')
        props = geojson_feature.get('properties', {})

        if not geom_dict:
            return None

        # Create geometry from GeoJSON coordinates
        geometry = cls._geojson_to_geometry(geom_dict)

        if geometry is None or geometry.isNull():
            return None

        # Create feature
        feature = QgsFeature(fields)
        feature.setGeometry(geometry)

        # Set attributes
        for i, field in enumerate(fields):
            field_name = field.name()
            # Try original name and truncated name
            value = props.get(field_name)
            if value is None:
                # Try to find matching key
                for key, val in props.items():
                    if key[:10] == field_name:
                        value = val
                        break

            if isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=False)

            feature.setAttribute(i, value)

        return feature

    @classmethod
    def _geojson_to_geometry(cls, geom_dict: Dict) -> Optional[QgsGeometry]:
        """Convert GeoJSON geometry dict to QgsGeometry."""
        geom_type = geom_dict.get('type', '').lower()
        coords = geom_dict.get('coordinates')

        if not coords:
            return None

        try:
            if geom_type == 'point':
                return QgsGeometry.fromPointXY(QgsPointXY(coords[0], coords[1]))

            elif geom_type == 'multipoint':
                points = [QgsPointXY(c[0], c[1]) for c in coords]
                return QgsGeometry.fromMultiPointXY(points)

            elif geom_type == 'linestring':
                points = [QgsPointXY(c[0], c[1]) for c in coords]
                return QgsGeometry.fromPolylineXY(points)

            elif geom_type == 'multilinestring':
                lines = [[QgsPointXY(c[0], c[1]) for c in line] for line in coords]
                return QgsGeometry.fromMultiPolylineXY(lines)

            elif geom_type == 'polygon':
                rings = [[QgsPointXY(c[0], c[1]) for c in ring] for ring in coords]
                return QgsGeometry.fromPolygonXY(rings)

            elif geom_type == 'multipolygon':
                polygons = [
                    [[QgsPointXY(c[0], c[1]) for c in ring] for ring in polygon]
                    for polygon in coords
                ]
                return QgsGeometry.fromMultiPolygonXY(polygons)

            else:
                cls._log(f'Unsupported geometry type: {geom_type}', Qgis.Warning)
                return None

        except (IndexError, TypeError) as e:
            cls._log(f'Error parsing geometry: {e}', Qgis.Warning)
            return None

    @classmethod
    def save_layer(
        cls,
        layer: QgsVectorLayer,
        file_path: str,
        output_format: str = 'gpkg'
    ) -> bool:
        """Save a layer to file.

        Args:
            layer: Layer to save.
            file_path: Output file path.
            output_format: Output format (gpkg, geojson, shp, csv).

        Returns:
            True if successful.
        """
        driver = cls.OUTPUT_DRIVERS.get(output_format.lower(), 'GPKG')

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = driver
        options.fileEncoding = 'UTF-8'

        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            file_path,
            QgsProject.instance().transformContext(),
            options
        )

        if error[0] == QgsVectorFileWriter.NoError:
            cls._log(f'Saved layer to {file_path}')
            return True
        else:
            cls._log(f'Failed to save layer: {error[1]}', Qgis.Warning)
            return False

    @classmethod
    def add_layer_to_project(
        cls,
        layer: QgsVectorLayer,
        group_name: Optional[str] = None
    ) -> None:
        """Add a layer to the current QGIS project.

        Args:
            layer: Layer to add.
            group_name: Optional group name to add layer to.
        """
        project = QgsProject.instance()
        root = project.layerTreeRoot()

        if group_name:
            group = root.findGroup(group_name)
            if not group:
                group = root.insertGroup(0, group_name)
            project.addMapLayer(layer, False)
            group.insertLayer(0, layer)
        else:
            project.addMapLayer(layer)

    @classmethod
    def json_to_layer_with_coords(
        cls,
        json_data: List[Dict],
        layer_name: str,
        lat_field: str = 'lat',
        lon_field: str = 'lon'
    ) -> Optional[QgsVectorLayer]:
        """Convert JSON with lat/lon fields to point layer.

        Args:
            json_data: List of dicts with coordinate fields.
            layer_name: Name for the layer.
            lat_field: Name of latitude field.
            lon_field: Name of longitude field.

        Returns:
            QgsVectorLayer or None if conversion fails.
        """
        if not json_data:
            return None

        # Convert to GeoJSON
        features = []
        for item in json_data:
            lat = item.get(lat_field)
            lon = item.get(lon_field)

            if lat is not None and lon is not None:
                try:
                    feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [float(lon), float(lat)]
                        },
                        'properties': {
                            k: v for k, v in item.items()
                            if k not in [lat_field, lon_field]
                        }
                    }
                    features.append(feature)
                except (ValueError, TypeError):
                    continue

        if not features:
            return None

        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }

        return cls.geojson_to_layer(geojson, layer_name)
