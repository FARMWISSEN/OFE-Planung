# -*- coding: utf-8 -*-
"""
CRS utilities for the OFE Planning plugin.

Provides UTM zone detection, CRS creation, and layer reprojection.
"""

import logging
import os

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsPointXY,
    QgsProcessingFeedback,
    QgsProject,
    QgsRectangle,
    QgsVectorLayer,
)
import processing

from .constants import (
    EPSG_WGS84,
    EPSG_NORTHERN_HEMISPHERE_BASE,
    EPSG_SOUTHERN_HEMISPHERE_BASE,
)

logger = logging.getLogger(__name__)


def detect_utm_crs(extent: QgsRectangle, source_crs: QgsCoordinateReferenceSystem) -> QgsCoordinateReferenceSystem:
    """Detect the appropriate UTM CRS for a given extent.

    Transforms the extent center to WGS84, calculates the UTM zone,
    and returns the corresponding CRS (EPSG:326xx or 327xx).
    """
    center_x = (extent.xMinimum() + extent.xMaximum()) / 2
    center_y = (extent.yMinimum() + extent.yMaximum()) / 2

    wgs84_crs = QgsCoordinateReferenceSystem(f"EPSG:{EPSG_WGS84}")
    transformer = QgsCoordinateTransform(source_crs, wgs84_crs, QgsProject.instance())
    center_wgs84 = transformer.transform(QgsPointXY(center_x, center_y))
    lon = center_wgs84.x()
    lat = center_wgs84.y()

    utm_zone = int((lon + 180) / 6) + 1

    if lat >= 0:
        target_epsg = EPSG_NORTHERN_HEMISPHERE_BASE + utm_zone
    else:
        target_epsg = EPSG_SOUTHERN_HEMISPHERE_BASE + utm_zone

    logger.debug("Detected UTM zone %d (EPSG:%d) for lon=%.4f, lat=%.4f", utm_zone, target_epsg, lon, lat)
    return QgsCoordinateReferenceSystem(f"EPSG:{target_epsg}")


def reproject_layer(
    input_layer: QgsVectorLayer,
    target_crs: QgsCoordinateReferenceSystem,
    new_name: str,
    output_dir: str,
) -> QgsVectorLayer:
    """Reproject a vector layer to the target CRS and save as shapefile.

    The output filename is based on the source layer's unique ID so that
    layers with identical names never share or overwrite each other's files.

    Args:
        input_layer: Source vector layer to reproject.
        target_crs: Target coordinate reference system.
        new_name: Display name for the output layer.
        output_dir: Directory to write the reprojected shapefile.

    Returns:
        The reprojected QgsVectorLayer loaded from the output file.
    """
    layer_id_short = input_layer.id()
    file_stem = new_name + "_" + layer_id_short
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, file_stem + ".shp")

    if os.path.exists(output_path):
        reprojected = QgsVectorLayer(output_path, new_name, "ogr")
        logger.info("Loaded cached reprojection of '%s' from %s", new_name, output_path)
        return reprojected

    params = {
        'INPUT': input_layer,
        'TARGET_CRS': target_crs,
        'OUTPUT': output_path,
    }
    feedback = QgsProcessingFeedback()
    result = processing.run("native:reprojectlayer", params, feedback=feedback)

    reprojected = QgsVectorLayer(result['OUTPUT'], new_name, "ogr")
    logger.info("Reprojected layer '%s' to %s", new_name, target_crs.authid())
    return reprojected
