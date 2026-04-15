import matplotlib.pyplot as plt
import numpy as np
from .variogram_models import VARIOGRAM_MODELS

# Import config for constants
try:
    from .config import InterpolationConfig
except ImportError:
    # Fallback if import fails
    class InterpolationConfig:
        VARIOGRAM_PLOT_FIGSIZE = (10, 6)
        VARIOGRAM_PLOT_RESOLUTION = 100
        VARIOGRAM_PLOT_EXPERIMENTAL_COLOR = 'blue'
        VARIOGRAM_PLOT_EXPERIMENTAL_MARKER = 'o'
        VARIOGRAM_PLOT_EXPERIMENTAL_ALPHA = 0.6
        VARIOGRAM_PLOT_MODEL_COLOR = 'red'
        VARIOGRAM_PLOT_MODEL_LINESTYLE = '-'
        VARIOGRAM_PLOT_GRID_ALPHA = 0.3

class VariogramPlotter:
    def __init__(self):
        """Initialize the variogram plotter"""
        self.fig = None
        self.ax = None
        
    def plot_variogram(self, lags, experimental, model_type, nugget, range_, sill,
                      title='Variogram Analyse', save_path=None, show=True):
        """Plot experimental and theoretical variograms.
        
        Args:
            lags: Array of lag distances
            experimental: Array of experimental variogram values
            model_type: Type of variogram model
            nugget: Nugget parameter
            range_: Range parameter
            sill: Sill parameter
            title: Plot title
            save_path: Path to save plot to
            show: Whether to display the plot
        """
        # Create plot
        self.fig, self.ax = plt.subplots(figsize=InterpolationConfig.VARIOGRAM_PLOT_FIGSIZE)
        
        # Plot experimental variogram points
        self.ax.scatter(
            lags, experimental, 
            c=InterpolationConfig.VARIOGRAM_PLOT_EXPERIMENTAL_COLOR, 
            marker=InterpolationConfig.VARIOGRAM_PLOT_EXPERIMENTAL_MARKER, 
            label='Experimentell', 
            alpha=InterpolationConfig.VARIOGRAM_PLOT_EXPERIMENTAL_ALPHA
        )
        
        # Plot theoretical variogram line
        if model_type in VARIOGRAM_MODELS:
            x = np.linspace(0, max(lags), InterpolationConfig.VARIOGRAM_PLOT_RESOLUTION)
            y = VARIOGRAM_MODELS[model_type](x, nugget, range_, sill)
            self.ax.plot(
                x, y, 
                color=InterpolationConfig.VARIOGRAM_PLOT_MODEL_COLOR,
                linestyle=InterpolationConfig.VARIOGRAM_PLOT_MODEL_LINESTYLE,
                label=f'{model_type.capitalize()} Modell'
            )
        
        # Customize plot
        self.ax.set_xlabel('Lag-Distanz')
        self.ax.set_ylabel('Semivarianz')
        self.ax.set_title(title)
        self.ax.legend()
        self.ax.grid(True, alpha=InterpolationConfig.VARIOGRAM_PLOT_GRID_ALPHA)
        
        if save_path:
            self.fig.savefig(save_path)
        
        if show:
            self.fig.show()
        
    def close(self):
        """Close the current plot"""
        if self.fig:
            plt.close(self.fig)
            self.fig = None
            self.ax = None
