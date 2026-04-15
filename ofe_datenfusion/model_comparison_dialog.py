"""
Model Comparison Dialog for Variogram Analysis Results

This module provides a dialog to compare different variogram models
based on their metrics (RMSE, R²) and parameters.
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox, QHeaderView, QFileDialog
)
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QFont
import csv
from datetime import datetime


class ModelComparisonDialog(QDialog):
    """Dialog to compare variogram analysis results from different models."""
    
    # Signal emitted when user selects a model to apply
    model_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None, results=None, is_point_tab=False):
        """
        Initialize the model comparison dialog.
        
        Args:
            parent: Parent widget
            results (list): List of variogram analysis results
            is_point_tab (bool): Whether this is for point or raster interpolation
        """
        super().__init__(parent)
        self.results = results or []
        self.is_point_tab = is_point_tab
        self.setup_ui()
        self.populate_table()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Variogramm-Modellvergleich")
        self.setMinimumSize(800, 400)
        
        layout = QVBoxLayout()
        
        # Title label
        title_label = QLabel("Vergleich der analysierten Variogramm-Modelle")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Info label
        tab_type = "Punkt-Interpolation" if self.is_point_tab else "Raster-Interpolation"
        info_label = QLabel(f"Typ: {tab_type} | Anzahl analysierter Modelle: {len(self.results)}")
        layout.addWidget(info_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Modell", "RMSE ↓", "R² ↑", "Sill", "Range", "Nugget", "Lags", "Zeitstempel"
        ])
        
        # Set alternating row colors for better readability
        self.table.setAlternatingRowColors(True)
        
        # Make table sortable
        self.table.setSortingEnabled(True)
        
        # Resize columns to content
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        
        # Enable row selection
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Double-click to select
        self.table.doubleClicked.connect(self.apply_selected_model)
        
        layout.addWidget(self.table)
        
        # Legend
        legend_label = QLabel("⭐ = Bestes Modell (höchstes R²) | Doppelklick auf Zeile = Parameter übernehmen")
        layout.addWidget(legend_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Parameter übernehmen")
        self.apply_button.clicked.connect(self.apply_selected_model)
        self.apply_button.setEnabled(False)
        button_layout.addWidget(self.apply_button)
        
        self.export_button = QPushButton("Export CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(self.export_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("Schließen")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Enable apply button when row is selected
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
    def populate_table(self):
        """Populate the table with variogram analysis results."""
        if not self.results:
            return
            
        self.table.setRowCount(len(self.results))
        
        # Find best model (highest R²)
        best_r2 = max(r['metrics']['r2'] for r in self.results)
        
        for row, result in enumerate(self.results):
            params = result['parameters']
            metrics = result['metrics']
            
            # Check if this is the best model
            is_best = metrics['r2'] == best_r2
            
            # Model name with star for best model
            model_name = result['model']
            if is_best:
                model_name = f"⭐ {model_name}"
            model_item = QTableWidgetItem(model_name)
            
            # Make best model bold
            if is_best:
                font = model_item.font()
                font.setBold(True)
                model_item.setFont(font)
            
            self.table.setItem(row, 0, model_item)
            
            # RMSE
            rmse_item = QTableWidgetItem(f"{metrics['rmse']:.4f}")
            rmse_item.setData(Qt.UserRole, metrics['rmse'])  # For sorting
            if is_best:
                font = rmse_item.font()
                font.setBold(True)
                rmse_item.setFont(font)
            self.table.setItem(row, 1, rmse_item)
            
            # R²
            r2_item = QTableWidgetItem(f"{metrics['r2']:.4f}")
            r2_item.setData(Qt.UserRole, metrics['r2'])  # For sorting
            if is_best:
                font = r2_item.font()
                font.setBold(True)
                r2_item.setFont(font)
            self.table.setItem(row, 2, r2_item)
            
            # Sill (if applicable)
            sill_value = params.get('sill', '-')
            sill_item = QTableWidgetItem(str(sill_value) if sill_value != '-' else '-')
            if sill_value != '-':
                sill_item.setData(Qt.UserRole, sill_value)
            self.table.setItem(row, 3, sill_item)
            
            # Range (if applicable)
            range_value = params.get('range', '-')
            range_item = QTableWidgetItem(str(range_value) if range_value != '-' else '-')
            if range_value != '-':
                range_item.setData(Qt.UserRole, range_value)
            self.table.setItem(row, 4, range_item)
            
            # Nugget
            nugget_item = QTableWidgetItem(f"{params['nugget']:.4f}")
            nugget_item.setData(Qt.UserRole, params['nugget'])
            self.table.setItem(row, 5, nugget_item)
            
            # Lags
            nlags_item = QTableWidgetItem(str(result.get('nlags', '-')))
            if 'nlags' in result:
                nlags_item.setData(Qt.UserRole, result['nlags'])
            self.table.setItem(row, 6, nlags_item)
            
            # Timestamp
            timestamp_item = QTableWidgetItem(result.get('timestamp', '-'))
            self.table.setItem(row, 7, timestamp_item)
            
            # Store full result in first column for later retrieval
            model_item.setData(Qt.UserRole, result)
            
    def on_selection_changed(self):
        """Enable/disable apply button based on selection."""
        self.apply_button.setEnabled(len(self.table.selectedItems()) > 0)
        
    def apply_selected_model(self):
        """Apply the selected model's parameters."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(
                self,
                "Keine Auswahl",
                "Bitte wählen Sie ein Modell aus der Tabelle aus."
            )
            return
            
        row = selected_rows[0].row()
        model_item = self.table.item(row, 0)
        result = model_item.data(Qt.UserRole)
        
        # Emit signal with selected model
        self.model_selected.emit(result)
        
        QMessageBox.information(
            self,
            "Parameter übernommen",
            f"Die Parameter des Modells '{result['model']}' wurden übernommen."
        )
        
        self.close()
        
    def export_to_csv(self):
        """Export the comparison table to CSV."""
        if not self.results:
            QMessageBox.warning(
                self,
                "Keine Daten",
                "Keine Daten zum Exportieren vorhanden."
            )
            return
            
        # Ask for file location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"variogram_comparison_{timestamp}.csv"
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "CSV exportieren",
            default_filename,
            "CSV Files (*.csv)"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    "Modell", "RMSE", "R²", "Sill", "Range", "Nugget", "Lags", "Zeitstempel"
                ])
                
                # Write data
                for result in self.results:
                    params = result['parameters']
                    metrics = result['metrics']
                    writer.writerow([
                        result['model'],
                        f"{metrics['rmse']:.4f}",
                        f"{metrics['r2']:.4f}",
                        params.get('sill', '-'),
                        params.get('range', '-'),
                        f"{params['nugget']:.4f}",
                        result.get('nlags', '-'),
                        result.get('timestamp', '-')
                    ])
                    
            QMessageBox.information(
                self,
                "Export erfolgreich",
                f"Daten wurden erfolgreich exportiert:\n\n{filename}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export fehlgeschlagen",
                f"Fehler beim Exportieren:\n\n{str(e)}"
            )
