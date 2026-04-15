# -*- coding: utf-8 -*-
"""
Custom exceptions for the Interpolation Plugin.

This module defines specific exception types for different error categories,
allowing for better error handling and more informative error messages.
"""


class InterpolationError(Exception):
    """Base exception for all interpolation plugin errors.
    
    All custom exceptions in this plugin inherit from this base class,
    making it easy to catch all plugin-specific errors.
    """
    pass


class DataValidationError(InterpolationError):
    """Raised when input data validation fails.
    
    Examples:
    - No features in layer
    - No valid values in field
    - Invalid data types
    - Missing required data
    """
    pass


class GeometryError(InterpolationError):
    """Raised when geometry operations fail.
    
    Examples:
    - Invalid geometries
    - Failed geometry repairs
    - Geometry combination errors
    - Points outside boundary
    """
    pass


class CoordinateSystemError(InterpolationError):
    """Raised when coordinate system operations fail.
    
    Examples:
    - UTM conversion failed
    - Invalid CRS
    - CRS mismatch
    """
    pass


class InterpolationCalculationError(InterpolationError):
    """Raised when interpolation calculations fail.
    
    Examples:
    - Kriging calculation errors
    - Variogram analysis failures
    - Insufficient data for interpolation
    """
    pass


class OutputError(InterpolationError):
    """Raised when output operations fail.
    
    Examples:
    - Failed to create raster
    - Failed to save output
    - Failed to update layer
    """
    pass
