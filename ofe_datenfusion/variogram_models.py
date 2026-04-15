import numpy as np
from scipy.optimize import curve_fit
from typing import Tuple, Dict, List, Optional

# Import config for constants
try:
    from .config import InterpolationConfig
except ImportError:
    # Fallback if import fails (e.g., during testing)
    class InterpolationConfig:
        VARIOGRAM_EXPONENTIAL_FACTOR = 3.0
        VARIOGRAM_BOUNDS_MULTIPLIER = 2
        VARIOGRAM_DEFAULT_NUGGET_FALLBACK = 0
        VARIOGRAM_DEFAULT_SILL_FALLBACK = 1
        VARIOGRAM_DEFAULT_RANGE_FALLBACK = 1

def linear_variogram_model(d: np.ndarray, nugget: float, slope: float, sill: float = None) -> np.ndarray:
    """Linear variogram model.
    
    Args:
        d: Distance array
        nugget: Nugget effect (intercept)
        slope: Slope of the linear model
        sill: Not used for linear model (kept for API compatibility)
        
    Returns:
        Semivariance values: γ(h) = nugget + slope * h
    """
    return nugget + slope * d

def spherical_variogram_model(d: np.ndarray, nugget: float, range_: float, sill: float) -> np.ndarray:
    """Spherical variogram model."""
    return np.where(d < range_, 
                   nugget + (sill - nugget) * (1.5 * d/range_ - 0.5 * (d/range_)**3),
                   sill)

def exponential_variogram_model(d: np.ndarray, nugget: float, range_: float, sill: float) -> np.ndarray:
    """Exponential variogram model."""
    return nugget + (sill - nugget) * (1 - np.exp(-InterpolationConfig.VARIOGRAM_EXPONENTIAL_FACTOR * d/range_))

def gaussian_variogram_model(d: np.ndarray, nugget: float, range_: float, sill: float) -> np.ndarray:
    """Gaussian variogram model."""
    return nugget + (sill - nugget) * (1 - np.exp(-InterpolationConfig.VARIOGRAM_EXPONENTIAL_FACTOR * (d/range_)**2))

# Dictionary of available variogram models
VARIOGRAM_MODELS = {
    'linear': linear_variogram_model,
    'spherical': spherical_variogram_model,
    'exponential': exponential_variogram_model,
    'gaussian': gaussian_variogram_model
}

def calculate_variogram_metrics(experimental: np.ndarray, theoretical: np.ndarray) -> Dict[str, float]:
    """Calculate goodness of fit metrics for variogram models.
    
    Args:
        experimental: Experimental variogram values
        theoretical: Theoretical variogram values from model
        
    Returns:
        Dictionary with RMSE and R² metrics
    """
    residuals = experimental - theoretical
    rmse = np.sqrt(np.mean(residuals**2))
    r2 = 1 - np.sum(residuals**2) / np.sum((experimental - np.mean(experimental))**2)
    return {'rmse': rmse, 'r2': r2}

def optimize_variogram_parameters(
    lags: np.ndarray,
    gamma: np.ndarray,
    model_type: str,
    initial_guess: Optional[List[float]] = None
) -> Tuple[List[float], Dict[str, float]]:
    """Optimize variogram model parameters using curve fitting.
    
    Args:
        lags: Distance values
        gamma: Experimental variogram values
        model_type: Type of variogram model ('linear', 'spherical', etc.)
        initial_guess: Initial parameters. 
                      - Linear: [nugget, slope]
                      - Others: [nugget, range, sill]
        
    Returns:
        Tuple of:
        - List of optimized parameters (2 for linear, 3 for others)
        - Dictionary of fit metrics {'rmse': float, 'r2': float}
    """
    if model_type not in VARIOGRAM_MODELS:
        raise ValueError(f"Unknown variogram model type: {model_type}")
    
    # Linear model has different parameters (nugget, slope) instead of (nugget, range, sill)
    is_linear = model_type.lower() == 'linear'
    
    # Estimate initial parameters if not provided
    if initial_guess is None:
        nugget = gamma[0] if len(gamma) > 0 else InterpolationConfig.VARIOGRAM_DEFAULT_NUGGET_FALLBACK
        
        if is_linear:
            # For linear: estimate slope from data using linear regression
            # slope ≈ Δγ / Δh (change in semivariance per unit distance)
            if len(lags) > 1 and len(gamma) > 1:
                # Use linear regression for more robust slope estimation
                # Remove nugget effect first for better slope estimate
                gamma_adjusted = gamma - nugget
                # Calculate slope as mean rate of change
                slope = np.mean(gamma_adjusted / lags) if np.all(lags > 0) else InterpolationConfig.DEFAULT_SLOPE
                # Ensure slope is positive and reasonable
                slope = max(slope, InterpolationConfig.DEFAULT_SLOPE)
            else:
                slope = InterpolationConfig.DEFAULT_SLOPE
            initial_guess = [nugget, slope]
        else:
            # For other models: use range and sill
            sill = np.max(gamma) if len(gamma) > 0 else InterpolationConfig.VARIOGRAM_DEFAULT_SILL_FALLBACK
            range_ = np.median(lags) if len(lags) > 0 else InterpolationConfig.VARIOGRAM_DEFAULT_RANGE_FALLBACK
            initial_guess = [nugget, range_, sill]
    
    # Set bounds for parameters
    if is_linear:
        # Linear: [nugget, slope] - both must be non-negative
        bounds = ([0, 0],  # Lower bounds
                 [np.inf, np.inf])  # Upper bounds (no limit on slope)
    else:
        # Other models: [nugget, range, sill]
        bounds = ([0, 0, 0],  # Lower bounds: all parameters must be positive
                 [np.inf, 
                  np.max(lags) * InterpolationConfig.VARIOGRAM_BOUNDS_MULTIPLIER, 
                  np.max(gamma) * InterpolationConfig.VARIOGRAM_BOUNDS_MULTIPLIER])  # Upper bounds
    
    try:
        # Try curve_fit optimization
        model_func = VARIOGRAM_MODELS[model_type]
        popt, _ = curve_fit(model_func, lags, gamma, 
                          p0=initial_guess,
                          bounds=bounds,
                          method='trf')
        
        # Calculate theoretical values with optimized parameters
        theoretical = model_func(lags, *popt)
        
        # Calculate fit metrics
        metrics = calculate_variogram_metrics(gamma, theoretical)
        
        return popt.tolist(), metrics
        
    except Exception as e:
        # Fallback to simple parameter estimation if optimization fails
        print(f"Optimization failed: {str(e)}")
        return initial_guess, calculate_variogram_metrics(gamma, 
            VARIOGRAM_MODELS[model_type](lags, *initial_guess))
