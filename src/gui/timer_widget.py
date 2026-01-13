"""Timer widget for displaying individual running timers."""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class TimerWidget(QWidget):
    """Widget for displaying a single running timer."""
    
    def __init__(self, session_id: int, task_id: int, task_name: str, 
                 task_color: str, start_time, parent=None):
        """Initialize timer widget.
        
        Args:
            session_id: Timer session ID
            task_id: Task ID
            task_name: Task name
            task_color: Task color (hex)
            start_time: Start datetime
            parent: Parent widget
        """
        super().__init__(parent)
        self.session_id = session_id
        self.task_id = task_id
        self.task_name = task_name
        self.task_color = task_color
        self.start_time = start_time
        self.setup_ui()
        
        # Update timer display every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)
        self.update_display()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Task name label with color indicator
        self.name_label = QLabel(self.task_name)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.name_label.setFont(font)
        
        # Time display
        self.time_label = QLabel("00:00:00")
        time_font = QFont("Monospace")
        time_font.setPointSize(12)
        time_font.setBold(True)
        self.time_label.setFont(time_font)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setMaximumWidth(80)
        
        layout.addWidget(self.name_label)
        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addWidget(self.stop_button)
        
        self.setLayout(layout)
        
        # Apply color styling
        self.update_styling()
    
    def update_styling(self):
        """Update widget styling based on task color."""
        # Lighter version of task color for background
        from PyQt6.QtGui import QColor
        color = QColor(self.task_color)
        color.setAlpha(30)
        
        self.setStyleSheet(f"""
            TimerWidget {{
                background-color: {color.name()};
                border: 2px solid {self.task_color};
                border-radius: 5px;
            }}
        """)
    
    def update_display(self):
        """Update the elapsed time display."""
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        elapsed = now - self.start_time
        total_seconds = int(elapsed.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def stop(self):
        """Stop the timer update."""
        self.timer.stop()


# Make TimerWidget inherit from QFrame for styling
class TimerWidget(QFrame):
    """Widget for displaying a single running timer."""
    
    def __init__(self, session_id: int, task_id: int, task_name: str, 
                 task_color: str, start_time, parent=None):
        """Initialize timer widget.
        
        Args:
            session_id: Timer session ID
            task_id: Task ID
            task_name: Task name
            task_color: Task color (hex)
            start_time: Start datetime
            parent: Parent widget
        """
        super().__init__(parent)
        self.session_id = session_id
        self.task_id = task_id
        self.task_name = task_name
        self.task_color = task_color
        self.start_time = start_time
        self.setup_ui()
        
        # Update timer display every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)
        self.update_display()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Task name label with color indicator
        self.name_label = QLabel(self.task_name)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.name_label.setFont(font)
        
        # Time display
        self.time_label = QLabel("00:00:00")
        time_font = QFont("Monospace")
        time_font.setPointSize(12)
        time_font.setBold(True)
        self.time_label.setFont(time_font)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setMaximumWidth(80)
        
        layout.addWidget(self.name_label)
        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addWidget(self.stop_button)
        
        self.setLayout(layout)
        
        # Apply color styling
        self.update_styling()
    
    def update_styling(self):
        """Update widget styling based on task color."""
        # Lighter version of task color for background
        from PyQt6.QtGui import QColor
        color = QColor(self.task_color)
        color.setAlpha(30)
        
        self.setStyleSheet(f"""
            TimerWidget {{
                background-color: {color.name()};
                border: 2px solid {self.task_color};
                border-radius: 5px;
            }}
        """)
    
    def update_display(self):
        """Update the elapsed time display."""
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        elapsed = now - self.start_time
        total_seconds = int(elapsed.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def stop(self):
        """Stop the timer update."""
        self.timer.stop()
