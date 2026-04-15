from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import shutil
import os
from datetime import datetime

# Import config and exceptions for constants
try:
    from .config import InterpolationConfig
    from .exceptions import InterpolationError, InterpolationCalculationError
except ImportError:
    # Fallback if import fails
    class InterpolationConfig:
        VARIOGRAM_DIALOG_MIN_WIDTH = 600
        VARIOGRAM_DIALOG_MIN_HEIGHT = 500
        VARIOGRAM_METRICS_TEXT_HEIGHT = 100
        VARIOGRAM_IMAGE_WIDTH = 550
        VARIOGRAM_IMAGE_HEIGHT = 400
    
    # Fallback exceptions
    class InterpolationError(Exception):
        pass
    class InterpolationCalculationError(InterpolationError):
        pass

class VariogramDialog(QDialog):
    def __init__(self, parent=None, layer_name=None, field_name=None, method="ordinary_kriging", is_point_tab=False):
        super(VariogramDialog, self).__init__(parent)
        self.plot_path = None  # Store plot path for export
        self.layer_name = layer_name
        self.field_name = field_name
        self.method = method
        self.is_point_tab = is_point_tab
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog's UI components."""
        self.setWindowTitle("Variogram Analyse")
        self.setMinimumSize(
            InterpolationConfig.VARIOGRAM_DIALOG_MIN_WIDTH,
            InterpolationConfig.VARIOGRAM_DIALOG_MIN_HEIGHT
        )
        
        # Create layout
        layout = QVBoxLayout()
        
        # Plot label
        self.plot_label = QLabel()
        self.plot_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.plot_label)
        
        # Metrics text area
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setMaximumHeight(InterpolationConfig.VARIOGRAM_METRICS_TEXT_HEIGHT)
        layout.addWidget(self.metrics_text)
        
        # Button layout (horizontal)
        button_layout = QHBoxLayout()
        
        # Export button
        self.export_button = QPushButton("Plot exportieren")
        self.export_button.setEnabled(False)  # Disabled until plot is loaded
        self.export_button.clicked.connect(self.export_plot)
        button_layout.addWidget(self.export_button)
        
        # Close button
        close_button = QPushButton("Dialog schließen")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def display_results(self, plot_path, metrics):
        """Display variogram analysis results.
        
        Args:
            plot_path: Path to the variogram plot image
            metrics: Dictionary containing RMSE and R² values
            
        Raises:
            InterpolationCalculationError: If plot image cannot be loaded
        """
        try:
            # Store plot path for export
            self.plot_path = plot_path
            
            # Display plot
            pixmap = QPixmap(plot_path)
            if pixmap.isNull():
                raise InterpolationCalculationError(
                    f"Variogramm-Plot konnte nicht geladen werden: {plot_path}"
                )
            
            scaled_pixmap = pixmap.scaled(
                InterpolationConfig.VARIOGRAM_IMAGE_WIDTH,
                InterpolationConfig.VARIOGRAM_IMAGE_HEIGHT,
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.plot_label.setPixmap(scaled_pixmap)
            
            # Display metrics
            metrics_text = f"Variogram Analyse:\n"
            metrics_text += f"RMSE: {metrics['rmse']:.3f}\n"
            metrics_text += f"R²: {metrics['r2']:.3f}\n"
            metrics_text += "\nNiedrigere RMSE-Werte und R²-Werte näher an 1 zeigen eine bessere Modellanpassung."
            
            self.metrics_text.setText(metrics_text)
            
            # Enable export button now that we have a plot
            self.export_button.setEnabled(True)
            
        except (KeyError, TypeError) as e:
            raise InterpolationCalculationError(
                f"Ungültige Metriken für Variogramm-Anzeige: {str(e)}"
            )
    
    def export_plot(self):
        """Export the variogram plot to the appropriate interpolation output directory."""
        if not self.plot_path or not os.path.exists(self.plot_path):
            QMessageBox.warning(
                self,
                "Export fehlgeschlagen",
                "Kein Variogramm-Plot zum Exportieren verfügbar."
            )
            return
        
        try:
            # Get QGIS project directory
            from qgis.core import QgsProject
            from pathlib import Path
            project = QgsProject.instance()
            project_path = project.homePath()
            
            if not project_path:
                QMessageBox.warning(
                    self,
                    "Export fehlgeschlagen",
                    "Kein QGIS-Projekt geöffnet. Bitte speichern Sie zuerst Ihr Projekt."
                )
                return
            
            # Determine output directory based on interpolation type
            project_dir = Path(project_path)
            if self.is_point_tab:
                output_dir = project_dir / InterpolationConfig.OUTPUT_DIR_NAME / "point_interpolation"
            else:
                output_dir = project_dir / InterpolationConfig.OUTPUT_DIR_NAME / "raster_interpolation"
            
            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create filename with same convention as interpolation outputs
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            
            # Use provided layer/field names or fallback to generic name
            if self.layer_name and self.field_name:
                filename = f"variogram_{self.method}_{self.layer_name}_{self.field_name}_{timestamp}.png"
            else:
                filename = f"variogram_plot_{timestamp}.png"
            
            export_path = output_dir / filename
            
            # Copy plot to output directory
            shutil.copy2(self.plot_path, str(export_path))
            
            # Show success message
            QMessageBox.information(
                self,
                "Export erfolgreich",
                f"Variogramm-Plot wurde erfolgreich exportiert:\n\n{export_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export fehlgeschlagen",
                f"Fehler beim Exportieren des Plots:\n\n{str(e)}"
            )
