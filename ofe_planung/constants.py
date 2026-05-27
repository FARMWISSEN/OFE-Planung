# -*- coding: utf-8 -*-
"""
Constants for the OFE Planning plugin.

Centralizes magic numbers, strings, EPSG codes, and configuration values
used throughout the plugin.
"""

from qgis.PyQt.QtGui import QColor


# --- CRS / Coordinate Reference Systems ---
EPSG_WGS84 = 4326
EPSG_UTM32N = 32632
EPSG_NORTHERN_HEMISPHERE_BASE = 32600
EPSG_SOUTHERN_HEMISPHERE_BASE = 32700

# Default map center (WGS84) — used when no project extent is available
DEFAULT_LAT = 54.287872
DEFAULT_LON = 9.674358
DEFAULT_MAP_EXTENT_PADDING = 250  # meters around default center

# --- Directories & Layer Groups ---
WORKING_DIR_NAME = "ofe_planung"
LAYER_GROUP_NAME = "Versuchsplanung"

# --- Plot Configuration ---
PLOT_TYPE_BORDER = "BORDER"
PLOT_TYPE_STANDARD = "STANDARD"
PLOT_ALIGN_JUSTIFY = "JUSTIFY"

# --- Map Styling ---
FIELD_SYMBOL_PROPS = {
    'outline_color': '0,0,200,255',
    'outline_width': '0.66',
    'color': '20,190,33,20',
    'opacity': '0.1',
}

HEADLAND_INNER_SYMBOL_PROPS = {
    'outline_color': '20,20,240,255',
    'outline_width': '0.66',
    'color': '255,255,255,0',
    'opacity': '0',
}

HEADLAND_PATTERN_ANGLE = 30
HEADLAND_PATTERN_DISTANCE = 2
HEADLAND_PATTERN_LINE_WIDTH = 0.5
HEADLAND_PATTERN_COLOR = QColor("orange")
HEADLAND_BUFFER_SEGMENTS = 5

AB_LINE_SYMBOL_PROPS = {
    'color': '0,255,255,255',
    'width': '0.5',
}

BLOCK_SYMBOL_PROPS = {
    'outline_color': '255,0,0,255',
    'outline_width': '0.5',
    'color': '255,200,100,80',
}

OBSTACLE_SYMBOL_PROPS = {
    'outline_color': '200,0,0,255',
    'outline_width': '0.8',
    'color': '220,50,50,120',
}

PLOT_SYMBOL_OPACITY = 0.5

# Field extent padding for zoom (fraction of extent dimensions)
FIELD_EXTENT_PADDING_FRACTION = 0.1

# Variant colors for plot styling
VARIANT_COLORS = [
    '#FF0000', '#00FF00', '#0000FF', '#FFFF00',
    '#FF00FF', '#00FFFF', '#FFA500', '#800080',
]

# --- Snapping ---
SNAPPING_TOLERANCE_PIXELS = 10

# --- Geometry Generation ---
BBOX_DIAGONAL_FACTOR = 1.5

# --- Rubber Band Colors (Map Tool) ---
RB_RECTANGLE_COLOR = QColor(0, 0, 255, 255)
RB_RECTANGLE_WIDTH = 3

RB_POINT_A_COLOR = QColor(255, 255, 0, 255)
RB_POINT_B_COLOR = QColor(100, 100, 0, 255)
RB_POINT_C_COLOR = QColor(255, 0, 0, 255)
RB_POINT_D_COLOR = QColor(255, 50, 150, 255)
RB_POINT_WIDTH = 8

RB_CUTTING_LINES_COLOR = QColor(40, 180, 30, 255)
RB_CUTTING_LINES_WIDTH = 2

RB_PLOTS_COLOR = QColor(200, 120, 70, 150)
RB_PLOTS_WIDTH = 1

RB_AB_POINT_A_COLOR = QColor(100, 0, 0, 255)
RB_AB_POINT_B_COLOR = QColor(0, 0, 100, 255)
RB_AB_POINT_WIDTH = 4

RB_AB_LINE_COLOR = QColor(0, 255, 255, 255)
RB_AB_LINE_WIDTH = 1

# --- Export ---
SHAPEFILE_DRIVER = "ESRI Shapefile"
SHAPEFILE_ENCODING = "utf-8"

# --- OSM Background ---
OSM_URL_PARAMS = (
    'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png'
    '&zmax=19&zmin=0'
)
OSM_LAYER_NAME = 'OpenStreetMap'
OSM_PROVIDER = 'wms'
