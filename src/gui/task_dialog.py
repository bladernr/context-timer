"""Task dialog for adding/editing tasks."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QColorDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class TaskDialog(QDialog):
    """Dialog for creating or editing tasks."""
    
    def __init__(self, parent=None, task_name: str = "", task_color: str = None):
        """Initialize task dialog.
        
        Args:
            parent: Parent widget
            task_name: Existing task name (for editing)
            task_color: Existing task color (for editing)
        """
        super().__init__(parent)
        self.task_name = task_name
        self.task_color = task_color or "#3498db"  # Default blue
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Add Task" if not self.task_name else "Edit Task")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Task name input
        name_label = QLabel("Task Name:")
        self.name_input = QLineEdit()
        self.name_input.setText(self.task_name)
        self.name_input.setPlaceholderText("e.g., Check Email, Meeting, Code Review")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        
        # Color picker
        color_layout = QHBoxLayout()
        color_label = QLabel("Color:")
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.choose_color)
        self.update_color_button()
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        layout.addLayout(color_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        save_button.setDefault(True)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.name_input.setFocus()
    
    def choose_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(QColor(self.task_color), self)
        if color.isValid():
            self.task_color = color.name()
            self.update_color_button()
    
    def update_color_button(self):
        """Update color button appearance."""
        self.color_button.setStyleSheet(
            f"background-color: {self.task_color}; "
            f"color: {'white' if self.is_dark_color(self.task_color) else 'black'};"
        )
    
    @staticmethod
    def is_dark_color(hex_color: str) -> bool:
        """Check if color is dark (for text contrast).
        
        Args:
            hex_color: Hex color string
            
        Returns:
            True if color is dark
        """
        color = QColor(hex_color)
        # Calculate luminance
        luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
        return luminance < 0.5
    
    def accept(self):
        """Validate and accept dialog."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Task name cannot be empty.")
            return
        
        self.task_name = name
        super().accept()
    
    def get_task_data(self):
        """Get task data from dialog.
        
        Returns:
            Tuple of (name, color)
        """
        return self.task_name, self.task_color
