# -*- coding: utf-8 -*-
"""
Generate blocks with plots and sowing lines for trial planning
"""

import logging
import math
from dataclasses import dataclass, field

from qgis.core import (
    QgsGeometry,
    QgsRectangle,
)
from typing import List, Dict, Any, Optional
from .generate_parallel_lines import generate_parallel_lines
from .constants import (
    PLOT_TYPE_BORDER,
    PLOT_TYPE_STANDARD,
    PLOT_ALIGN_JUSTIFY,
)


@dataclass
class BlockConfig:
    """Configuration for block/plot generation."""
    width: float
    planting_width: float
    variants: List[Dict[str, Any]]
    groups: List[List[int]]
    distance_between_groups: float = 0.0
    plot_spacing: float = 0.0
    variant_spacing: float = 0.0
    plot_length: float = 0.0
    plot_alignment: str = PLOT_ALIGN_JUSTIFY
    use_guidance_line_as_first_lane: bool = False
    allow_small_start_plots: bool = False
    allow_small_end_plots: bool = False
    enable_border_plots: bool = False

logger = logging.getLogger(__name__)

def calculate_bbox_diagonal(geom: QgsGeometry) -> float:
    """Calculate diagonal of bounding box in map units (meters if CRS is metric)."""
    bbox = geom.boundingBox()
    width = bbox.width()
    height = bbox.height()
    return math.sqrt(width * width + height * height)


def split_polygon_parallel(
    field_geom: QgsGeometry,
    ab_line_geom: QgsGeometry,
    width: float,
    groups: List[List[int]],
    offset: float = 0.0,
    distance_between_groups: float = 0.0,
    plot_spacing: float = 0.0,
    variant_spacing: float = 0.0,
    plot_length: float = 0.0,
    plot_alignment: str = PLOT_ALIGN_JUSTIFY,
    allow_small_start: bool = False,
    allow_small_end: bool = False
) -> List[Dict[str, Any]]:
    """
    Split polygon into parallel plots.
    
    This is a simplified placeholder — full implementation would require
    complex geometric operations similar to the TypeScript version.
    
    Returns:
        List of plot dictionaries with geometry and properties
    """
    plots = []
    
    # Get AB line points
    ab_coords = ab_line_geom.asPolyline()
    if len(ab_coords) < 2:
        return plots
    
    from .generate_parallel_lines import bearing, destination
    
    point_a = ab_coords[0]
    point_b = ab_coords[-1]
    bear = bearing(point_a, point_b)
    
    current_offset = offset
    plot_index = 0
    
    for rep_idx, group in enumerate(groups):
        for var_idx_in_group, variant_idx in enumerate(group):
            # Calculate offset for this plot
            plot_offset = (
                current_offset +
                plot_index * width +
                rep_idx * distance_between_groups +
                plot_index * plot_spacing +
                var_idx_in_group * variant_spacing
            )
            
            # Create parallel line for plot edge
            edge_start = destination(point_a, plot_offset, bear + 90)
            edge_end = destination(point_b, plot_offset, bear + 90)
            
            # Create next edge
            next_offset = plot_offset + width
            next_start = destination(point_a, next_offset, bear + 90)
            next_end = destination(point_b, next_offset, bear + 90)
            
            # Create plot polygon (simplified - rectangle between two parallel lines)
            plot_coords = [edge_start, edge_end, next_end, next_start, edge_start]
            plot_geom = QgsGeometry.fromPolygonXY([plot_coords])
            
            # Intersect with field
            plot_geom = plot_geom.intersection(field_geom)
            
            if not plot_geom.isEmpty():
                plots.append({
                    'geometry': plot_geom,
                    'properties': {
                        'repetitionIndex': rep_idx,
                        'variantIndex': variant_idx,
                        'plotIndex': plot_index,
                        'area': plot_geom.area()
                    }
                })
            
            plot_index += 1
    
    return plots


def generate_blocks(
    field_geom: QgsGeometry,
    ab_line_geom: QgsGeometry,
    obstacles: Optional[List[QgsGeometry]],
    config: BlockConfig,
) -> List[Dict[str, Any]]:
    """
    Generate trial blocks with plots and sowing lines.
    
    Args:
        field_geom: Field boundary geometry (Polygon or MultiPolygon)
        ab_line_geom: AB orientation line (LineString)
        obstacles: List of obstacle geometries to subtract from field
        config: Block generation configuration
        
    Returns:
        List of block dictionaries with nested plots and sowing lines
    """
    width = config.width
    planting_width = config.planting_width
    variants = config.variants
    groups = config.groups
    distance_between_groups = config.distance_between_groups
    plot_spacing = config.plot_spacing
    variant_spacing = config.variant_spacing
    plot_length = config.plot_length
    plot_alignment = config.plot_alignment
    use_guidance_line_as_first_lane = config.use_guidance_line_as_first_lane
    allow_small_start_plots = config.allow_small_start_plots
    allow_small_end_plots = config.allow_small_end_plots
    enable_border_plots = config.enable_border_plots
    # Process field with obstacles
    field_with_obstacles = field_geom
    if obstacles:
        for obstacle in obstacles:
            field_with_obstacles = field_with_obstacles.difference(obstacle)
    
    # Calculate offset
    initial_offset = -(planting_width / 2) if use_guidance_line_as_first_lane else 0.0
    
    # Generate plots
    plots = split_polygon_parallel(
        field_with_obstacles,
        ab_line_geom,
        width,
        groups,
        initial_offset,
        distance_between_groups,
        plot_spacing,
        variant_spacing,
        plot_length,
        plot_alignment,
        allow_small_start_plots,
        allow_small_end_plots
    )
    
    if not plots:
        return []
    
    # Calculate bbox diagonal for line generation
    bbox_diagonal = calculate_bbox_diagonal(field_with_obstacles)
    
    # Find minimum plot index (for offset calculation)
    min_index = min(
        p['properties']['repetitionIndex'] * len(variants) +
        groups[p['properties']['repetitionIndex']].index(p['properties']['variantIndex'])
        for p in plots
    )
    
    # Generate sowing lines for each plot
    for idx, plot in enumerate(plots):
        rep_idx = plot['properties']['repetitionIndex']
        
        lines_offset = (
            planting_width / 2 +
            (min_index + idx - rep_idx) * variant_spacing +
            (min_index + idx) * width +
            initial_offset +
            distance_between_groups * rep_idx +
            distance_between_groups / 2
        )
        
        num_lines = math.ceil((width - planting_width / 2) / planting_width)
        
        sowing_lines = generate_parallel_lines(
            field_with_obstacles,
            bbox_diagonal,
            ab_line_geom,
            planting_width,
            num_lines,
            lines_offset,
            plot_alignment
        )
        
        plot['sowing_lines'] = sowing_lines
    
    # Generate blocks (repetitions)
    block_width = width * len(variants)
    block_offset = initial_offset + (width if enable_border_plots else 0.0)
    
    blocks = split_polygon_parallel(
        field_with_obstacles,
        ab_line_geom,
        block_width,
        [[0] for _ in range(len(groups))],
        block_offset,
        distance_between_groups,
        plot_spacing,
        variant_spacing,
        plot_length,
        plot_alignment,
        True,
        True
    )
    
    # Organize plots into blocks
    result_blocks = []
    plots_amount = len(plots)
    plot_index = 0
    
    for block_idx, block in enumerate(blocks):
        rep_idx = block['properties']['repetitionIndex']
        
        block_plots = [p for p in plots if p['properties']['repetitionIndex'] == rep_idx]
        
        block_dict = {
            'geometry': block['geometry'],
            'label': f"Block {rep_idx + 1}",
            'index': block_idx,
            'gross_area': block['geometry'].area(),
            'plots': []
        }
        
        for plot_sub_idx, plot in enumerate(block_plots):
            var_idx = plot['properties']['variantIndex']
            
            # Determine plot type
            if enable_border_plots and (plot_index == 0 or plot_index == plots_amount - 1):
                plot_type = PLOT_TYPE_BORDER
                variant = None
                label = "Border"
            else:
                plot_type = PLOT_TYPE_STANDARD
                variant = variants[var_idx] if var_idx < len(variants) else None
                label = f"{variant.get('label', '')}_{rep_idx + 1}" if variant else f"Plot_{plot_index}"
            
            plot_dict = {
                'geometry': plot['geometry'],
                'label': label,
                'index': plot_sub_idx,
                'gross_area': plot['geometry'].area(),
                'type': plot_type,
                'variant': variant,
                'sowing_lines': plot.get('sowing_lines', [])
            }
            
            block_dict['plots'].append(plot_dict)
            plot_index += 1
        
        result_blocks.append(block_dict)
    
    return result_blocks
