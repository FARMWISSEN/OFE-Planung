# -*- coding: utf-8 -*-
"""
Layer management utilities for the OFE Planning plugin.

Centralizes QGIS layer operations: loading, adding, removing, grouping, and exporting.
"""

import logging
import os
import shutil
import tempfile
import zipfile

import sip

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsLayerTreeGroup,
    QgsMapLayer,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsWkbTypes,
)

from .constants import SHAPEFILE_DRIVER, SHAPEFILE_ENCODING

logger = logging.getLogger(__name__)


def is_layer_valid(layer) -> bool:
    """Return True if the layer reference points to a live C++ QGIS object."""
    return layer is not None and not sip.isdeleted(layer)


def is_valid_polygon_layer(layer: QgsMapLayer) -> bool:
    """Check whether the layer is a valid polygon vector layer."""
    return (
        layer is not None
        and layer.type() == QgsMapLayer.VectorLayer
        and QgsWkbTypes.geometryType(layer.wkbType()) == QgsWkbTypes.PolygonGeometry
    )


def is_valid_line_layer(layer: QgsMapLayer) -> bool:
    """Check whether the layer is a valid line vector layer."""
    return (
        layer is not None
        and layer.type() == QgsMapLayer.VectorLayer
        and QgsWkbTypes.geometryType(layer.wkbType()) == QgsWkbTypes.LineGeometry
    )


def get_layer_group(group_name: str):
    """Get or create a layer tree group by name.

    Returns:
        QgsLayerTreeGroup for the given name.
    """
    root = QgsProject.instance().layerTreeRoot()
    layer_group = root.findGroup(group_name)
    if layer_group is None:
        layer_group = QgsLayerTreeGroup(group_name)
        root.insertChildNode(0, layer_group)
    return layer_group


def remove_layer(layer: QgsMapLayer) -> None:
    """Remove a layer from the QGIS project and release the reference.

    Safe to call with None or already-deleted layers.
    """
    if is_layer_valid(layer):
        QgsProject.instance().removeMapLayers([layer.id()])


def clean_layer_add(layer: QgsVectorLayer) -> None:
    """Remove existing layers with the same name, then add the new layer (without tree node).

    This prevents duplicate layers when re-loading.
    """
    existing = QgsProject.instance().mapLayersByName(layer.name())
    for existing_layer in existing:
        QgsProject.instance().removeMapLayers([existing_layer.id()])
    QgsProject.instance().addMapLayer(layer, False)


def move_layer_to_top(layer: QgsMapLayer) -> None:
    """Move a layer to the top of the layer tree root."""
    root = QgsProject.instance().layerTreeRoot()
    layer_node = root.findLayer(layer.id())
    if layer_node is None:
        return

    parent = layer_node.parent()
    if parent is None:
        return

    cloned_node = layer_node.clone()
    parent.removeChildNode(layer_node)
    root.insertChildNode(0, cloned_node)


def export_shapefile(layer: QgsVectorLayer, output_file: str):
    """Export a vector layer to ESRI Shapefile format.

    Returns:
        Tuple of (success: bool, message_or_error).
    """
    logger.info("Saving %s to %s", layer.name(), output_file)
    context = QgsProject.instance().transformContext()
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = SHAPEFILE_DRIVER
    options.fileEncoding = SHAPEFILE_ENCODING
    options.onlySelectedFeatures = False
    options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
    options.layerName = layer.name()

    writer_result = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer, output_file, context, options
    )
    if writer_result[0] != QgsVectorFileWriter.NoError:
        logger.error("Failed to save shapefile: %s", writer_result)
        return False, writer_result
    return True, "Success"


def get_canvas_layers(**kwargs) -> list:
    """Build an ordered list of layers for the map canvas.

    Accepts keyword arguments for each optional layer. Order determines
    draw priority (first = top).

    Args:
        plot_layer: Plot/trial members layer.
        ab_line_layer: AB orientation line layer.
        lenkspur_layer: Guidance line layer.
        inner_layer: Inner surface layer.
        buffer_layer: Headland buffer layer.
        feld_layer: Field boundary layer.
        osm_layer: OpenStreetMap background layer.

    Returns:
        List of valid, non-None layers in draw order.
    """
    layer_keys = [
        'plot_layer', 'ab_line_layer', 'lenkspur_layer',
        'inner_layer', 'buffer_layer', 'feld_layer', 'osm_layer',
    ]
    layers = []
    for key in layer_keys:
        layer = kwargs.get(key)
        if layer is not None:
            layers.append(layer)
    return layers


def export_layers_to_zip(layers: list, zip_path: str):
    """Export a list of vector layers as ESRI Shapefiles in EPSG:4326 into a ZIP file.

    Each layer is reprojected to WGS84 (EPSG:4326) on the fly during export.
    All shapefile sidecar files (.shp, .dbf, .shx, .prj, .cpg) are included.

    Args:
        layers: List of QgsVectorLayer objects to export (None/invalid entries are skipped).
        zip_path: Absolute path of the output ZIP file to create.

    Returns:
        Tuple of (success: bool, failed_layer_names: list[str]).
        success is True when at least one layer was exported successfully.
    """
    wgs84_crs = QgsCoordinateReferenceSystem("EPSG:4326")
    transform_context = QgsProject.instance().transformContext()
    temp_dir = tempfile.mkdtemp(prefix="ofe_export_")

    try:
        exported_files = []
        failed_layers = []

        for layer in layers:
            if layer is None or not layer.isValid():
                continue

            layer_name = layer.name()
            safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in layer_name)
            output_file = os.path.join(temp_dir, safe_name + ".shp")

            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = SHAPEFILE_DRIVER
            options.fileEncoding = SHAPEFILE_ENCODING
            options.onlySelectedFeatures = False
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile

            if layer.crs() != wgs84_crs:
                options.ct = QgsCoordinateTransform(layer.crs(), wgs84_crs, transform_context)

            result = QgsVectorFileWriter.writeAsVectorFormatV3(
                layer, output_file, transform_context, options
            )

            if result[0] == QgsVectorFileWriter.NoError:
                base = os.path.splitext(output_file)[0]
                for ext in (".shp", ".dbf", ".shx", ".prj", ".cpg"):
                    sidecar = base + ext
                    if os.path.exists(sidecar):
                        exported_files.append(sidecar)
            else:
                logger.error("Failed to export layer '%s': %s", layer_name, result)
                failed_layers.append(layer_name)

        if not exported_files:
            return False, failed_layers

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for filepath in exported_files:
                zf.write(filepath, os.path.basename(filepath))

        return True, failed_layers

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
