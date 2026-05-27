# -*- coding: utf-8 -*-
"""
Core (net) plot generation for the OFE Planning plugin.

Given a plot layer and AB line orientation, generates smaller core plots
inside each gross plot based on core width, core length, and placement settings.
"""

import logging
import math

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
)
from PyQt5.QtCore import QMetaType

logger = logging.getLogger(__name__)


def generate_core_plots(plot_layer, ab_line, core_width, core_length, placement):
    """Generate core plot geometries from a gross plot layer.

    Parameters
    ----------
    plot_layer : QgsVectorLayer
        Source plot layer with polygon features. Must have fields
        ID, LABEL, WDH, FAKTOR1, FAKTOR2, VARIANTE.
    ab_line : QgsGeometry
        The AB line used for orientation (LineString).
    core_width : float
        Width of the core plot (perpendicular to AB). 0 means use full plot width.
    core_length : float
        Length of the core plot (along AB direction). 0 means use full plot length.
    placement : str
        One of 'center', 'bottom', 'top'.
        - 'center': core is centred in AB direction
        - 'bottom': core is aligned to A end of the plot
        - 'top': core is aligned to B end of the plot

    Returns
    -------
    list[QgsFeature]
        Core plot features with the same attribute schema as the input.
    """
    if not plot_layer or not plot_layer.isValid():
        return []

    if ab_line.isMultipart():
        parts = ab_line.asMultiPolyline()
        polyline = parts[0] if parts else []
    else:
        polyline = ab_line.asPolyline()
    if len(polyline) < 2:
        return []

    pt_a = polyline[0]
    pt_b = polyline[-1]

    # AB direction unit vector (along AB) and perpendicular
    ab_azimuth = pt_a.azimuth(pt_b)  # degrees clockwise from north
    ab_rad = math.radians(ab_azimuth)

    # Unit vectors: along AB (dy_ab, dx_ab) and perpendicular (right of AB)
    along_x = math.sin(ab_rad)
    along_y = math.cos(ab_rad)
    perp_x = math.cos(ab_rad)   # perpendicular right
    perp_y = -math.sin(ab_rad)

    features = []

    for feat in plot_layer.getFeatures():
        geom = feat.geometry()
        if geom.isEmpty():
            continue

        bbox = geom.boundingBox()

        # Project the plot polygon onto the AB direction to find its extent
        # along and perpendicular to AB
        vertices = _extract_vertices(geom)
        if len(vertices) < 3:
            continue

        # Project vertices onto AB direction and perpendicular direction
        # using pt_a as origin would shift everything — use centroid as reference
        centroid = geom.centroid().asPoint()

        along_min = float('inf')
        along_max = float('-inf')
        perp_min = float('inf')
        perp_max = float('-inf')

        for v in vertices:
            dx = v.x() - centroid.x()
            dy = v.y() - centroid.y()
            along_proj = dx * along_x + dy * along_y
            perp_proj = dx * perp_x + dy * perp_y
            along_min = min(along_min, along_proj)
            along_max = max(along_max, along_proj)
            perp_min = min(perp_min, perp_proj)
            perp_max = max(perp_max, perp_proj)

        plot_along_size = along_max - along_min  # length in AB direction
        plot_perp_size = perp_max - perp_min     # width perpendicular to AB

        # Determine core dimensions
        eff_core_width = core_width if (core_width > 0 and core_width < plot_perp_size) else plot_perp_size
        eff_core_length = core_length if (core_length > 0 and core_length < plot_along_size) else plot_along_size

        # Perpendicular offset: always centred
        perp_center = (perp_min + perp_max) / 2.0
        perp_half = eff_core_width / 2.0

        # Along offset: depends on placement
        if placement == 'bottom':
            along_start = along_min
            along_end = along_min + eff_core_length
        elif placement == 'top':
            along_end = along_max
            along_start = along_max - eff_core_length
        else:  # center
            along_center = (along_min + along_max) / 2.0
            along_half = eff_core_length / 2.0
            along_start = along_center - along_half
            along_end = along_center + along_half

        # Build the 4 corners of the core plot in projected coordinates,
        # then convert back to map coordinates
        corners_proj = [
            (perp_center - perp_half, along_start),
            (perp_center - perp_half, along_end),
            (perp_center + perp_half, along_end),
            (perp_center + perp_half, along_start),
            (perp_center - perp_half, along_start),  # close ring
        ]

        corners_map = []
        for (pp, ap) in corners_proj:
            mx = centroid.x() + pp * perp_x + ap * along_x
            my = centroid.y() + pp * perp_y + ap * along_y
            corners_map.append(QgsPointXY(mx, my))

        core_geom = QgsGeometry.fromPolygonXY([corners_map])

        # Intersect with original plot to handle irregular shapes
        core_geom = core_geom.intersection(geom)
        if core_geom.isEmpty():
            continue

        core_feat = QgsFeature(feat.fields())
        core_feat.setGeometry(core_geom)
        core_feat.setAttributes(feat.attributes())
        features.append(core_feat)

    return features


def _extract_vertices(geom):
    """Extract all vertices from a geometry as QgsPointXY list."""
    vertices = []
    if geom.isMultipart():
        for part in geom.asMultiPolygon():
            for ring in part:
                vertices.extend(ring)
    else:
        for ring in geom.asPolygon():
            vertices.extend(ring)
    return vertices
