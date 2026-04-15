"""
Duplicate Coordinates Dialog

This module provides a dialog to handle duplicate coordinates in point layers.
Offers options to average values or keep first occurrence.
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QTextEdit, QGroupBox
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont


class DuplicateCoordinatesDialog(QDialog):
    """Dialog to handle duplicate coordinates in point layers."""
    
    # Return values
    ACTION_AVERAGE = "average"
    ACTION_KEEP_FIRST = "keep_first"
    ACTION_CANCEL = "cancel"
    
    def __init__(self, parent=None, duplicate_count=0, duplicate_details=None):
        """
        Initialize the duplicate coordinates dialog.
        
        Args:
            parent: Parent widget
            duplicate_count (int): Number of duplicate coordinate pairs
            duplicate_details (dict): Details about duplicates {(x,y): [values]}
        """
        super().__init__(parent)
        self.duplicate_count = duplicate_count
        self.duplicate_details = duplicate_details or {}
        self.selected_action = self.ACTION_CANCEL
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Doppelte Koordinaten gefunden")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Warning icon and title
        title_label = QLabel("⚠️ Doppelte Koordinaten gefunden")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Description
        desc_text = (
            f"Es wurden <b>{self.duplicate_count} Punkte</b> mit identischen Koordinaten gefunden.\n"
            "Dies kann zu Fehlern bei der Interpolation führen (z.B. 'singular matrix').\n\n"
            "Wie möchten Sie fortfahren?"
        )
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Options group
        options_group = QGroupBox("Behandlungsoptionen")
        options_layout = QVBoxLayout()
        
        self.button_group = QButtonGroup()
        
        # Option 1: Average (recommended)
        self.radio_average = QRadioButton("Mittelwert bilden (empfohlen)")
        self.radio_average.setChecked(True)
        self.button_group.addButton(self.radio_average, 0)
        options_layout.addWidget(self.radio_average)
        
        avg_desc = QLabel("   → Berechnet den Durchschnitt der Werte für identische Koordinaten")
        avg_desc.setStyleSheet("color: gray; font-size: 10pt;")
        options_layout.addWidget(avg_desc)
        
        # Option 2: Keep first
        self.radio_keep_first = QRadioButton("Erste behalten")
        self.button_group.addButton(self.radio_keep_first, 1)
        options_layout.addWidget(self.radio_keep_first)
        
        first_desc = QLabel("   → Behält nur das erste Feature (Achtung: Datenverlust!)")
        first_desc.setStyleSheet("color: gray; font-size: 10pt;")
        options_layout.addWidget(first_desc)
        
        # Option 3: Cancel
        self.radio_cancel = QRadioButton("Abbrechen")
        self.button_group.addButton(self.radio_cancel, 2)
        options_layout.addWidget(self.radio_cancel)
        
        cancel_desc = QLabel("   → Manuelle Bereinigung erforderlich")
        cancel_desc.setStyleSheet("color: gray; font-size: 10pt;")
        options_layout.addWidget(cancel_desc)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Details section (collapsible)
        self.details_button = QPushButton("Details anzeigen ▼")
        self.details_button.setFlat(True)
        self.details_button.clicked.connect(self.toggle_details)
        layout.addWidget(self.details_button)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        self.details_text.setVisible(False)
        self.populate_details()
        layout.addWidget(self.details_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("Fortfahren")
        self.ok_button.clicked.connect(self.accept_action)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def populate_details(self):
        """Populate the details text with duplicate information."""
        if not self.duplicate_details:
            self.details_text.setText("Keine Details verfügbar.")
            return
            
        details = "Doppelte Koordinaten:\n\n"
        
        # Show first 10 duplicates
        count = 0
        for coord, values in list(self.duplicate_details.items())[:10]:
            x, y = coord
            details += f"Koordinate ({x:.2f}, {y:.2f}):\n"
            details += f"  Anzahl: {len(values)}\n"
            details += f"  Werte: {', '.join(f'{v:.3f}' for v in values[:5])}"
            if len(values) > 5:
                details += f" ... (+{len(values)-5} weitere)"
            details += f"\n  Mittelwert: {sum(values)/len(values):.3f}\n\n"
            count += 1
            
        if len(self.duplicate_details) > 10:
            details += f"... und {len(self.duplicate_details) - 10} weitere Duplikate\n"
            
        self.details_text.setText(details)
        
    def toggle_details(self):
        """Toggle visibility of details section."""
        is_visible = self.details_text.isVisible()
        self.details_text.setVisible(not is_visible)
        
        if is_visible:
            self.details_button.setText("Details anzeigen ▼")
        else:
            self.details_button.setText("Details verbergen ▲")
            
    def accept_action(self):
        """Accept the selected action."""
        checked_id = self.button_group.checkedId()
        
        if checked_id == 0:
            self.selected_action = self.ACTION_AVERAGE
        elif checked_id == 1:
            self.selected_action = self.ACTION_KEEP_FIRST
        else:
            self.selected_action = self.ACTION_CANCEL
            
        if self.selected_action == self.ACTION_CANCEL:
            self.reject()
        else:
            self.accept()
            
    def get_selected_action(self):
        """Get the selected action."""
        return self.selected_action
