# -*- coding: utf-8 -*-
"""
Generate parallel lines for trial plots in QGIS
"""

import logging
import math
from typing import List, Tuple

from qgis.core import (
    QgsGeometry,
    QgsPoint,
    QgsPointXY,
    QgsLineString,
    QgsMultiLineString,
    QgsWkbTypes,
)

from .constants import BBOX_DIAGONAL_FACTOR, PLOT_ALIGN_JUSTIFY

logger = logging.getLogger(__name__)

def bearing(point_a: QgsPointXY, point_b: QgsPointXY) -> float:
    """Calculate bearing between two points in degrees."""
    dx = point_b.x() - point_a.x()
    dy = point_b.y() - point_a.y()
    angle = math.atan2(dx, dy)
    bearing_deg = math.degrees(angle)
    return bearing_deg


def destination(point: QgsPointXY, distance: float, bearing_deg: float) -> QgsPointXY:
    """Calculate destination point given distance and bearing."""
    bearing_rad = math.radians(bearing_deg)
    x = point.x() + distance * math.sin(bearing_rad)
    y = point.y() + distance * math.cos(bearing_rad)
    return QgsPointXY(x, y)


def midpoint(point_a: QgsPointXY, point_b: QgsPointXY) -> QgsPointXY:
    """Calculate midpoint between two points."""
    return QgsPointXY(
        (point_a.x() + point_b.x()) / 2,
        (point_a.y() + point_b.y()) / 2
    )


def intersect_line_and_polygon(
    poly_geom: QgsGeometry,
    line_geom: QgsGeometry
) -> QgsGeometry:
    """
    Intersect a line with a polygon and return only the parts inside.
    Returns a MultiLineString geometry.
    """
    if not poly_geom or not line_geom:
        return QgsGeometry()
    
    # Get intersection
    intersection = line_geom.intersection(poly_geom)
    
    if intersection.isEmpty():
        return QgsGeometry()
    
    # Convert to MultiLineString if needed
    geom_type = intersection.wkbType()
    
    if geom_type == QgsWkbTypes.LineString:
        # Single line - convert to MultiLineString
        line_coords = intersection.asPolyline()
        multi_line = QgsMultiLineString()
        line_string = QgsLineString([QgsPoint(pt) for pt in line_coords])
        multi_line.addGeometry(line_string)
        return QgsGeometry(multi_line)
    
    elif geom_type == QgsWkbTypes.MultiLineString:
        return intersection
    
    elif geom_type == QgsWkbTypes.GeometryCollection:
        # Extract only LineString geometries
        multi_line = QgsMultiLineString()
        geom_collection = intersection.asGeometryCollection()
        
        for geom in geom_collection:
            if geom.wkbType() == QgsWkbTypes.LineString:
                line_coords = geom.asPolyline()
                line_string = QgsLineString([QgsPoint(pt) for pt in line_coords])
                multi_line.addGeometry(line_string)
        
        if multi_line.numGeometries() > 0:
            return QgsGeometry(multi_line)
    
    return QgsGeometry()


def generate_parallel_lines(
    field_geom: QgsGeometry,
    bbox_diagonal: float,
    ab_line_geom: QgsGeometry,
    width: float,
    amount: int,
    start_offset: float = 0.0,
    plot_alignment: str = PLOT_ALIGN_JUSTIFY
) -> List[QgsGeometry]:
    """
    Generate parallel lines for sowing/planting.
    
    Args:
        field_geom: Field polygon geometry (Polygon or MultiPolygon)
        bbox_diagonal: Diagonal length of field bounding box in meters
        ab_line_geom: AB orientation line geometry (LineString)
        width: Width/spacing between lines in meters
        amount: Number of lines to generate
        start_offset: Offset from start point in meters
        plot_alignment: PLOT_ALIGN_JUSTIFY or other alignment type
        
    Returns:
        List of MultiLineString geometries
    """
    if amount <= 0 or width <= 0:
        return []
    
    # Get AB line coordinates
    ab_coords = ab_line_geom.asPolyline()
    if len(ab_coords) < 2:
        return []
    
    point_a = ab_coords[0]
    point_b = ab_coords[-1]
    
    # Calculate bearing
    bear = bearing(point_a, point_b)
    
    # Determine line length
    if plot_alignment == PLOT_ALIGN_JUSTIFY:
        line_length = bbox_diagonal * BBOX_DIAGONAL_FACTOR
    else:
        line_length = ab_line_geom.length()
    
    sowing_lines = []
    current_offset = start_offset
    max_offset = amount * width + start_offset
    
    while current_offset < max_offset:
        # Calculate perpendicular offset point
        line_start = destination(point_a, current_offset, bear + 90)
        
        # Extend line in both directions
        if plot_alignment == PLOT_ALIGN_JUSTIFY:
            start_far = destination(line_start, line_length / 2, bear + 180)
        else:
            start_far = line_start
        
        end_far = destination(line_start, line_length, bear)
        
        # Create long line
        initial_line = QgsGeometry.fromPolylineXY([start_far, end_far])
        
        # Intersect with field
        line = intersect_line_and_polygon(field_geom, initial_line)
        
        if not line.isEmpty():
            sowing_lines.append(line)
        
        current_offset += width
    
    return sowing_lines
