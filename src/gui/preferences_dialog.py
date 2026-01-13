"""Preferences dialog for application settings."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QTimeEdit, QPushButton, QLabel, QGroupBox
)
from PyQt6.QtCore import QTime


class PreferencesDialog(QDialog):
    """Dialog for editing application preferences."""
    
    def __init__(self, parent=None, db=None):
        """Initialize preferences dialog.
        
        Args:
            parent: Parent widget
            db: Database instance
        """
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.setup_ui()
        self.load_preferences()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Work Hours group
        work_hours_group = QGroupBox("Work Hours")
        work_hours_layout = QFormLayout()
        
        # Expected start time
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        self.start_time_edit.setTime(QTime(9, 0))  # Default 9:00 AM
        
        help_label = QLabel("If set, 'Start My Day' will automatically begin\nif you launch the app after this time.")
        help_label.setStyleSheet("color: #666; font-size: 9pt;")
        
        work_hours_layout.addRow("Expected Start Time:", self.start_time_edit)
        work_hours_layout.addRow("", help_label)
        
        work_hours_group.setLayout(work_hours_layout)
        layout.addWidget(work_hours_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_preferences)
        save_button.setDefault(True)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_preferences(self):
        """Load preferences from database."""
        if not self.db:
            return
        
        # Load expected start time
        start_time_str = self.db.get_setting('expected_start_time')
        if start_time_str:
            time = QTime.fromString(start_time_str, "HH:mm")
            if time.isValid():
                self.start_time_edit.setTime(time)
    
    def save_preferences(self):
        """Save preferences to database."""
        if not self.db:
            self.accept()
            return
        
        # Save expected start time
        start_time_str = self.start_time_edit.time().toString("HH:mm")
        self.db.set_setting('expected_start_time', start_time_str)
        
        self.accept()
