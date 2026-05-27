# -*- coding: utf-8 -*-
"""
Map styling utilities for the OFE Planning plugin.

Provides functions to create and apply renderers and symbols for plot,
headland, field, and AB line layers.
"""

import logging

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    Qgis,
    QgsCategorizedSymbolRenderer,
    QgsFillSymbol,
    QgsLinePatternFillSymbolLayer,
    QgsLineSymbol,
    QgsPalLayerSettings,
    QgsRendererCategory,
    QgsSymbol,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtGui import QColor

from .constants import (
    FIELD_SYMBOL_PROPS,
    HEADLAND_INNER_SYMBOL_PROPS,
    HEADLAND_PATTERN_ANGLE,
    HEADLAND_PATTERN_DISTANCE,
    HEADLAND_PATTERN_LINE_WIDTH,
    HEADLAND_PATTERN_COLOR,
    AB_LINE_SYMBOL_PROPS,
    BLOCK_SYMBOL_PROPS,
    OBSTACLE_SYMBOL_PROPS,
    PLOT_SYMBOL_OPACITY,
    VARIANT_COLORS,
)

logger = logging.getLogger(__name__)


def create_field_symbol() -> QgsFillSymbol:
    """Create the default field boundary fill symbol."""
    return QgsFillSymbol.createSimple(FIELD_SYMBOL_PROPS)


def create_headland_inner_symbol() -> QgsFillSymbol:
    """Create the transparent inner surface symbol."""
    return QgsFillSymbol.createSimple(HEADLAND_INNER_SYMBOL_PROPS)


def create_headland_pattern_symbol() -> QgsFillSymbol:
    """Create the hatched line-pattern fill symbol for the headland buffer."""
    symbol_lyr = QgsLinePatternFillSymbolLayer()
    symbol_lyr.setLineAngle(HEADLAND_PATTERN_ANGLE)
    symbol_lyr.setDistance(HEADLAND_PATTERN_DISTANCE)
    symbol_lyr.setLineWidth(HEADLAND_PATTERN_LINE_WIDTH)
    symbol_lyr.setColor(HEADLAND_PATTERN_COLOR)

    symbol = QgsFillSymbol()
    symbol.deleteSymbolLayer(0)
    symbol.appendSymbolLayer(symbol_lyr)
    return symbol


def create_ab_line_symbol() -> QgsLineSymbol:
    """Create the default AB line symbol."""
    return QgsLineSymbol.createSimple(AB_LINE_SYMBOL_PROPS)


def create_block_symbol() -> QgsFillSymbol:
    """Create the default block outline symbol."""
    return QgsFillSymbol.createSimple(BLOCK_SYMBOL_PROPS)


def create_obstacle_symbol() -> QgsFillSymbol:
    """Create the symbol for exclusion/obstacle areas."""
    return QgsFillSymbol.createSimple(OBSTACLE_SYMBOL_PROPS)


def apply_categorized_variant_renderer(
    layer: QgsVectorLayer,
    variants: list,
    expression: str = 'VARIANTE',
) -> None:
    """Apply a categorized renderer with random colors per variant.

    Also enables labeling using the 'LABEL' field.
    """
    # Labels — centroid placement, show all even if they overlap
    label_settings = QgsPalLayerSettings()
    label_settings.fieldName = "LABEL"
    label_settings.enabled = True
    # Place at centroid; allow the label to sit outside a narrow polygon
    label_settings.placement = Qgis.LabelPlacement.Horizontal
    label_settings.centroidInside = False
    label_settings.fitInPolygonOnly = False
    # Always render every label — don't skip when space is tight
    label_settings.displayAll = True
    label_settings.obstacle = False
    labeling = QgsVectorLayerSimpleLabeling(label_settings)
    layer.setLabelsEnabled(True)
    layer.setLabeling(labeling)

    # Categories
    categories = []
    for i, variant in enumerate(variants):
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol.setColor(QColor(VARIANT_COLORS[i % len(VARIANT_COLORS)]))
        symbol.setOpacity(PLOT_SYMBOL_OPACITY)
        category = QgsRendererCategory(variant, symbol, QCoreApplication.translate('OFEPlanning', 'Variant {variant}').format(variant=variant))
        categories.append(category)

    renderer = QgsCategorizedSymbolRenderer(expression, categories)
    layer.setRenderer(renderer)
    layer.triggerRepaint()
    logger.debug("Applied categorized renderer with %d categories to '%s'", len(categories), layer.name())
