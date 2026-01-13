"""Main window for Context Timer application."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QMessageBox, QFileDialog,
    QTabWidget, QTextEdit, QGroupBox, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction
from datetime import datetime, timezone, timedelta
from typing import Dict, List

from ..models import Database, Task, TimerSession
from ..utils import (
    format_duration, get_date_range_for_today, get_date_range_for_week,
    get_date_range_for_month, get_week_dates, format_date, format_datetime,
    export_daily_report_to_csv, export_weekly_report_to_csv,
    export_sessions_to_csv, get_default_export_path, generate_export_filename
)
from .task_dialog import TaskDialog
from .timer_widget import TimerWidget
from .preferences_dialog import PreferencesDialog
from .preferences_dialog import PreferencesDialog
from .preferences_dialog import PreferencesDialog


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.db = Database()
        self.active_timer_widgets: Dict[int, TimerWidget] = {}
        self.setup_ui()
        self.load_tasks()
        self.load_active_timers()
        
        # Check if we should auto-start Work Day
        self.check_auto_start_work_day()
        
        # Auto-save timer state every 30 seconds
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30000)
        
        # Update reports every minute
        self.report_timer = QTimer()
        self.report_timer.timeout.connect(self.update_reports)
        self.report_timer.start(60000)
        self.update_reports()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Context Timer")
        self.setMinimumSize(900, 700)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Work Day Controls (above tabs)
        self.setup_work_day_controls(main_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Timers tab
        timers_tab = QWidget()
        self.setup_timers_tab(timers_tab)
        self.tabs.addTab(timers_tab, "Timers")
        
        # Daily report tab
        daily_tab = QWidget()
        self.setup_daily_report_tab(daily_tab)
        self.tabs.addTab(daily_tab, "Daily Report")
        
        # Weekly report tab
        weekly_tab = QWidget()
        self.setup_weekly_report_tab(weekly_tab)
        self.tabs.addTab(weekly_tab, "Weekly Report")
        
        # Track special timer IDs
        self.work_day_session_id = None
        self.lunch_session_id = None
        self.break_session_id = None
    
    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        export_action = QAction("Export Data...", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Tasks menu
        tasks_menu = menubar.addMenu("Tasks")
        
        add_task_action = QAction("Add Task...", self)
        add_task_action.setShortcut("Ctrl+N")
        add_task_action.triggered.connect(self.add_task)
        tasks_menu.addAction(add_task_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        preferences_action = QAction("Preferences...", self)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(preferences_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_work_day_controls(self, parent_layout: QVBoxLayout):
        """Set up work day control buttons above the tabs.
        
        Args:
            parent_layout: Parent layout to add controls to
        """
        # Container for work day controls
        controls_group = QGroupBox("Work Day Controls")
        controls_layout = QHBoxLayout()
        
        # Start My Day / Stop Working button
        self.work_day_button = QPushButton("Start My Day")
        self.work_day_button.setMinimumHeight(50)
        self.work_day_button.setMinimumWidth(200)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.work_day_button.setFont(font)
        self.work_day_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 3px solid #229954;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
                border: 3px solid #27ae60;
            }
        """)
        self.work_day_button.clicked.connect(self.toggle_work_day)
        controls_layout.addWidget(self.work_day_button)
        
        controls_layout.addSpacing(20)
        
        # Lunch button
        self.lunch_button = QPushButton("Lunch")
        self.lunch_button.setMinimumHeight(50)
        self.lunch_button.setMinimumWidth(150)
        self.lunch_button.setFont(font)
        self.lunch_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: 3px solid #e67e22;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f1c40f;
                border: 3px solid #f39c12;
            }
        """)
        self.lunch_button.clicked.connect(self.toggle_lunch)
        self.lunch_button.setEnabled(False)  # Disabled until work day starts
        controls_layout.addWidget(self.lunch_button)
        
        # Break button
        self.break_button = QPushButton("Break")
        self.break_button.setMinimumHeight(50)
        self.break_button.setMinimumWidth(150)
        self.break_button.setFont(font)
        self.break_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: 3px solid #e67e22;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f1c40f;
                border: 3px solid #f39c12;
            }
        """)
        self.break_button.clicked.connect(self.toggle_break)
        self.break_button.setEnabled(False)  # Disabled until work day starts
        controls_layout.addWidget(self.break_button)
        
        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)
        parent_layout.addWidget(controls_group)
    
    def setup_timers_tab(self, parent: QWidget):
        """Set up the timers tab.
        
        Args:
            parent: Parent widget
        """
        layout = QVBoxLayout(parent)
        
        # Active timers section
        active_group = QGroupBox("Active Timers")
        active_layout = QVBoxLayout()
        
        # Scroll area for active timers
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)
        self.active_timers_widget = QWidget()
        self.active_timers_layout = QVBoxLayout(self.active_timers_widget)
        self.active_timers_layout.addStretch()
        scroll.setWidget(self.active_timers_widget)
        active_layout.addWidget(scroll)
        
        # Stop all button
        stop_all_button = QPushButton("Stop All Timers")
        stop_all_button.clicked.connect(self.stop_all_timers)
        stop_all_button.setMaximumWidth(150)
        active_layout.addWidget(stop_all_button)
        
        active_group.setLayout(active_layout)
        layout.addWidget(active_group)
        
        # Tasks section
        tasks_group = QGroupBox("Tasks")
        tasks_layout = QVBoxLayout()
        
        # Grid layout for task buttons (no scroll area)
        self.tasks_widget = QWidget()
        self.tasks_grid_layout = QGridLayout(self.tasks_widget)
        self.tasks_grid_layout.setSpacing(8)
        tasks_layout.addWidget(self.tasks_widget)
        
        # Task management buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Task")
        add_button.clicked.connect(self.add_task)
        
        edit_button = QPushButton("Edit Task")
        edit_button.clicked.connect(self.edit_task)
        
        delete_button = QPushButton("Delete Task")
        delete_button.clicked.connect(self.delete_task)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        
        tasks_layout.addLayout(button_layout)
        tasks_group.setLayout(tasks_layout)
        layout.addWidget(tasks_group)
        
        # Store task buttons for selection tracking
        self.task_buttons = {}
        self.selected_task_id = None
    
    def setup_daily_report_tab(self, parent: QWidget):
        """Set up the daily report tab.
        
        Args:
            parent: Parent widget
        """
        layout = QVBoxLayout(parent)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Daily Report - Today's Activity")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        header_label.setFont(font)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_daily_report)
        header_layout.addWidget(export_button)
        
        layout.addLayout(header_layout)
        
        # Report content
        self.daily_report_text = QTextEdit()
        self.daily_report_text.setReadOnly(True)
        self.daily_report_text.setFont(QFont("Monospace", 10))
        layout.addWidget(self.daily_report_text)
    
    def setup_weekly_report_tab(self, parent: QWidget):
        """Set up the weekly report tab.
        
        Args:
            parent: Parent widget
        """
        layout = QVBoxLayout(parent)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Weekly Report - This Week's Activity")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        header_label.setFont(font)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_weekly_report)
        header_layout.addWidget(export_button)
        
        layout.addLayout(header_layout)
        
        # Report content
        self.weekly_report_text = QTextEdit()
        self.weekly_report_text.setReadOnly(True)
        self.weekly_report_text.setFont(QFont("Monospace", 10))
        layout.addWidget(self.weekly_report_text)
    
    def load_tasks(self):
        """Load tasks from database and create task buttons in a grid."""
        # Clear existing task buttons
        for button in self.task_buttons.values():
            self.tasks_grid_layout.removeWidget(button)
            button.deleteLater()
        self.task_buttons.clear()
        
        tasks = self.db.get_all_tasks()
        
        # Filter out special timers
        special_timer_names = {"Work Day", "Lunch", "Break"}
        
        # Calculate grid dimensions (3 columns)
        columns = 3
        row = 0
        col = 0
        
        for task_row in tasks:
            task = Task.from_db_row(task_row)
            
            # Skip special timer tasks
            if task.name in special_timer_names:
                continue
            
            # Create button for task
            button = QPushButton(task.name)
            button.setMinimumHeight(60)
            button.setMinimumWidth(150)
            button.setCheckable(True)
            
            # Style button with task color
            if task.color:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {task.color};
                        color: {'white' if self.is_dark_color(task.color) else 'black'};
                        border: 2px solid {task.color};
                        border-radius: 5px;
                        font-size: 11pt;
                        font-weight: bold;
                        text-align: center;
                        padding: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {task.color};
                        border: 3px solid #2c3e50;
                    }}
                    QPushButton:checked {{
                        border: 3px solid #2980b9;
                        background-color: {task.color};
                    }}
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: 2px solid #3498db;
                        border-radius: 5px;
                        font-size: 11pt;
                        font-weight: bold;
                        text-align: center;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background-color: #3498db;
                        border: 3px solid #2c3e50;
                    }
                    QPushButton:checked {
                        border: 3px solid #2980b9;
                        background-color: #3498db;
                    }
                """)
            
            # Connect button click to start timer
            button.clicked.connect(lambda checked, tid=task.id: self.on_task_button_clicked(tid))
            
            # Add to grid layout
            self.tasks_grid_layout.addWidget(button, row, col)
            self.task_buttons[task.id] = button
            
            # Move to next position in grid
            col += 1
            if col >= columns:
                col = 0
                row += 1
    
    @staticmethod
    def is_dark_color(hex_color: str) -> bool:
        """Check if color is dark (for text contrast).
        
        Args:
            hex_color: Hex color string
            
        Returns:
            True if color is dark
        """
        from PyQt6.QtGui import QColor
        color = QColor(hex_color)
        luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
        return luminance < 0.5
    
    def on_task_button_clicked(self, task_id: int):
        """Handle task button click to start timer.
        
        Args:
            task_id: Task ID
        """
        # Uncheck all other buttons
        for tid, button in self.task_buttons.items():
            if tid != task_id:
                button.setChecked(False)
        
        # Update selected task
        self.selected_task_id = task_id
        
        # Start timer for this task
        self.start_timer_for_task(task_id)
    
    def load_active_timers(self):
        """Load active timers from database."""
        sessions = self.db.get_active_sessions()
        
        for session_row in sessions:
            session = TimerSession.from_db_row(session_row)
            self.add_timer_widget(session)
            
            # Check if this is a special timer and set the session ID
            if session.task_name == "Work Day":
                self.work_day_session_id = session.id
                # Update Work Day button state
                self.work_day_button.setText("Stop Working")
                self.work_day_button.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        font-size: 12pt;
                        font-weight: bold;
                        border-radius: 8px;
                        min-width: 200px;
                        min-height: 50px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                self.lunch_button.setEnabled(True)
                self.break_button.setEnabled(True)
            elif session.task_name == "Lunch":
                self.lunch_session_id = session.id
                # Update Lunch button state
                self.lunch_button.setText("End Lunch")
                self.lunch_button.setStyleSheet("""
                    QPushButton {
                        background-color: #e67e22;
                        color: white;
                        font-size: 11pt;
                        font-weight: bold;
                        border-radius: 8px;
                        min-width: 150px;
                        min-height: 50px;
                    }
                    QPushButton:hover {
                        background-color: #d35400;
                    }
                """)
                self.break_button.setEnabled(False)
            elif session.task_name == "Break":
                self.break_session_id = session.id
                # Update Break button state
                self.break_button.setText("End Break")
                self.break_button.setStyleSheet("""
                    QPushButton {
                        background-color: #e67e22;
                        color: white;
                        font-size: 11pt;
                        font-weight: bold;
                        border-radius: 8px;
                        min-width: 150px;
                        min-height: 50px;
                    }
                    QPushButton:hover {
                        background-color: #d35400;
                    }
                """)
                self.lunch_button.setEnabled(False)
    
    def add_task(self):
        """Show dialog to add new task."""
        dialog = TaskDialog(self)
        if dialog.exec():
            name, color = dialog.get_task_data()
            try:
                self.db.create_task(name, color)
                self.load_tasks()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create task: {str(e)}")
    
    def edit_task(self):
        """Show dialog to edit selected task."""
        if not self.selected_task_id:
            QMessageBox.warning(self, "No Selection", "Please click a task button to select a task to edit.")
            return
        
        task_row = self.db.get_task_by_id(self.selected_task_id)
        task = Task.from_db_row(task_row)
        
        dialog = TaskDialog(self, task.name, task.color)
        if dialog.exec():
            name, color = dialog.get_task_data()
            try:
                self.db.update_task(self.selected_task_id, name, color)
                self.load_tasks()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update task: {str(e)}")
    
    def delete_task(self):
        """Delete selected task."""
        if not self.selected_task_id:
            QMessageBox.warning(self, "No Selection", "Please click a task button to select a task to delete.")
            return
        
        task_row = self.db.get_task_by_id(self.selected_task_id)
        task = Task.from_db_row(task_row)
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the task '{task.name}'?\n\n"
            "This will not delete historical data, but you won't be able to start new timers for this task.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_task(self.selected_task_id)
            self.selected_task_id = None
            self.load_tasks()
    
    def start_timer_for_task(self, task_id: int):
        """Start timer for specified task.
        
        Args:
            task_id: Task ID
        """
        task_row = self.db.get_task_by_id(task_id)
        task = Task.from_db_row(task_row)
        
        # Check if timer already running for this task
        for widget in self.active_timer_widgets.values():
            if widget.task_id == task_id:
                QMessageBox.information(
                    self, "Timer Running",
                    f"A timer is already running for '{task.name}'."
                )
                # Uncheck the button
                if task_id in self.task_buttons:
                    self.task_buttons[task_id].setChecked(False)
                return
        
        # Log context switch if other timers are active
        if self.active_timer_widgets:
            # Get any active task for context switch logging
            first_widget = next(iter(self.active_timer_widgets.values()))
            self.db.log_context_switch(first_widget.task_id, task_id)
        
        # Start new session
        session_id = self.db.start_session(task_id)
        start_time = datetime.now(timezone.utc)
        
        session = TimerSession(
            id=session_id,
            task_id=task_id,
            start_time=start_time,
            task_name=task.name,
            task_color=task.color
        )
        
        self.add_timer_widget(session)
    
    def add_timer_widget(self, session: TimerSession):        # Start new session
        session_id = self.db.start_session(task_id)
        start_time = datetime.now(timezone.utc)
        
        session = TimerSession(
            id=session_id,
            task_id=task_id,
            start_time=start_time,
            task_name=task.name,
            task_color=task.color
        )
        
        self.add_timer_widget(session)
    
    def add_timer_widget(self, session: TimerSession):
        """Add timer widget to active timers display.
        
        Args:
            session: Timer session
        """
        widget = TimerWidget(
            session.id,
            session.task_id,
            session.task_name,
            session.task_color,
            session.start_time,
            self
        )
        widget.stop_button.clicked.connect(lambda: self.stop_timer(session.id))
        
        # Insert before the stretch
        self.active_timers_layout.insertWidget(
            self.active_timers_layout.count() - 1,
            widget
        )
        self.active_timer_widgets[session.id] = widget
    
    def stop_timer(self, session_id: int):
        """Stop a timer.
        
        Args:
            session_id: Session ID
        """
        if session_id in self.active_timer_widgets:
            widget = self.active_timer_widgets[session_id]
            widget.stop()
            self.db.stop_session(session_id)
            
            # Remove widget
            self.active_timers_layout.removeWidget(widget)
            widget.deleteLater()
            del self.active_timer_widgets[session_id]
            
            # Update reports
            self.update_reports()
    
    def stop_all_timers(self):
        """Stop all running timers."""
        if not self.active_timer_widgets:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Stop All",
            "Are you sure you want to stop all running timers?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Copy keys to avoid modification during iteration
            session_ids = list(self.active_timer_widgets.keys())
            for session_id in session_ids:
                # Skip Work Day timer - only stop regular task timers
                if session_id != self.work_day_session_id:
                    self.stop_timer(session_id)
    
    def update_reports(self):
        """Update daily and weekly reports."""
        self.update_daily_report()
        self.update_weekly_report()
    
    def update_daily_report(self):
        """Update daily report display."""
        start_date, end_date = get_date_range_for_today()
        sessions = self.db.get_sessions_for_date_range(start_date, end_date)
        switches = self.db.get_context_switches_for_date_range(start_date, end_date)
        
        # Calculate statistics
        total_seconds = 0
        task_times: Dict[int, Dict] = {}
        
        for session_row in sessions:
            session = TimerSession.from_db_row(session_row)
            duration = session.get_elapsed_seconds()
            total_seconds += duration
            
            if session.task_id not in task_times:
                task_times[session.task_id] = {
                    'name': session.task_name,
                    'duration': 0,
                    'sessions': 0
                }
            
            task_times[session.task_id]['duration'] += duration
            task_times[session.task_id]['sessions'] += 1
        
        # Generate report text
        report = []
        report.append("=" * 60)
        report.append(f"DAILY REPORT - {format_date(datetime.now(timezone.utc))}")
        report.append("=" * 60)
        report.append("")
        report.append("SUMMARY")
        report.append("-" * 60)
        report.append(f"Total Tasks Worked On:     {len(task_times)}")
        report.append(f"Total Context Switches:    {len(switches)}")
        report.append(f"Total Time Worked:         {format_duration(total_seconds)}")
        report.append("")
        
        if task_times:
            report.append("TASK BREAKDOWN")
            report.append("-" * 60)
            report.append(f"{'Task':<30} {'Time':<12} {'Sessions':<10}")
            report.append("-" * 60)
            
            for task_data in sorted(task_times.values(), key=lambda x: x['duration'], reverse=True):
                report.append(
                    f"{task_data['name']:<30} "
                    f"{format_duration(task_data['duration']):<12} "
                    f"{task_data['sessions']:<10}"
                )
        
        self.daily_report_text.setText("\n".join(report))
    
    def update_weekly_report(self):
        """Update weekly report display."""
        week_dates = get_week_dates()
        
        report = []
        report.append("=" * 80)
        report.append(f"WEEKLY REPORT - Week of {format_date(week_dates[0])}")
        report.append("=" * 80)
        report.append("")
        
        total_week_seconds = 0
        total_week_switches = 0
        
        report.append(f"{'Date':<15} {'Total Time':<15} {'Context Switches':<20} {'Tasks':<10}")
        report.append("-" * 80)
        
        for date in week_dates:
            start = date.isoformat()
            end = (date + timedelta(days=1)).isoformat()
            
            sessions = self.db.get_sessions_for_date_range(start, end)
            switches = self.db.get_context_switches_for_date_range(start, end)
            
            day_seconds = 0
            task_ids = set()
            
            for session_row in sessions:
                session = TimerSession.from_db_row(session_row)
                day_seconds += session.get_elapsed_seconds()
                task_ids.add(session.task_id)
            
            total_week_seconds += day_seconds
            total_week_switches += len(switches)
            
            report.append(
                f"{format_date(date):<15} "
                f"{format_duration(day_seconds):<15} "
                f"{len(switches):<20} "
                f"{len(task_ids):<10}"
            )
        
        report.append("-" * 80)
        report.append("")
        report.append("WEEKLY SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Time Worked:         {format_duration(total_week_seconds)}")
        report.append(f"Total Context Switches:    {total_week_switches}")
        report.append(f"Average Daily Time:        {format_duration(total_week_seconds // 7)}")
        
        self.weekly_report_text.setText("\n".join(report))
    
    def export_daily_report(self):
        """Export daily report to CSV."""
        export_dir = get_default_export_path()
        filename = generate_export_filename("daily", datetime.now(timezone.utc).strftime("%Y%m%d"))
        filepath = export_dir / filename
        
        # Prepare report data
        start_date, end_date = get_date_range_for_today()
        sessions = self.db.get_sessions_for_date_range(start_date, end_date)
        switches = self.db.get_context_switches_for_date_range(start_date, end_date)
        
        task_times: Dict[int, Dict] = {}
        total_seconds = 0
        
        for session_row in sessions:
            session = TimerSession.from_db_row(session_row)
            duration = session.get_elapsed_seconds()
            total_seconds += duration
            
            if session.task_id not in task_times:
                task_times[session.task_id] = {
                    'name': session.task_name,
                    'duration': 0,
                    'sessions': 0
                }
            
            task_times[session.task_id]['duration'] += duration
            task_times[session.task_id]['sessions'] += 1
        
        report_data = {
            'date': format_date(datetime.now(timezone.utc)),
            'total_tasks': len(task_times),
            'total_switches': len(switches),
            'total_time_formatted': format_duration(total_seconds),
            'tasks': [
                {
                    'name': data['name'],
                    'duration_formatted': format_duration(data['duration']),
                    'session_count': data['sessions']
                }
                for data in task_times.values()
            ]
        }
        
        export_daily_report_to_csv(report_data, str(filepath))
        QMessageBox.information(
            self, "Export Complete",
            f"Daily report exported to:\n{filepath}"
        )
    
    def export_weekly_report(self):
        """Export weekly report to CSV."""
        export_dir = get_default_export_path()
        week_start = get_week_dates()[0]
        filename = generate_export_filename("weekly", week_start.strftime("%Y%m%d"))
        filepath = export_dir / filename
        
        week_dates = get_week_dates()
        days_data = []
        total_week_seconds = 0
        total_week_switches = 0
        
        for date in week_dates:
            start = date.isoformat()
            end = (date + timedelta(days=1)).isoformat()
            
            sessions = self.db.get_sessions_for_date_range(start, end)
            switches = self.db.get_context_switches_for_date_range(start, end)
            
            day_seconds = 0
            task_ids = set()
            
            for session_row in sessions:
                session = TimerSession.from_db_row(session_row)
                day_seconds += session.get_elapsed_seconds()
                task_ids.add(session.task_id)
            
            total_week_seconds += day_seconds
            total_week_switches += len(switches)
            
            days_data.append({
                'date': format_date(date),
                'total_time_formatted': format_duration(day_seconds),
                'context_switches': len(switches),
                'task_count': len(task_ids)
            })
        
        report_data = {
            'week_start': format_date(week_dates[0]),
            'week_end': format_date(week_dates[-1]),
            'days': days_data,
            'total_time_formatted': format_duration(total_week_seconds),
            'total_switches': total_week_switches,
            'average_daily_time': format_duration(total_week_seconds // 7)
        }
        
        export_weekly_report_to_csv(report_data, str(filepath))
        QMessageBox.information(
            self, "Export Complete",
            f"Weekly report exported to:\n{filepath}"
        )
    
    def export_data(self):
        """Export all timer session data to CSV."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QDialogButtonBox
        
        # Create dialog to choose date range
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Timer Data")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Select time period to export:"))
        
        period_combo = QComboBox()
        period_combo.addItems(["Today", "This Week", "This Month", "All Time"])
        layout.addWidget(period_combo)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec():
            period = period_combo.currentText()
            
            # Determine date range
            if period == "Today":
                start_date, end_date = get_date_range_for_today()
                date_suffix = datetime.now(timezone.utc).strftime("%Y%m%d")
            elif period == "This Week":
                start_date, end_date = get_date_range_for_week()
                date_suffix = get_week_dates()[0].strftime("%Y%m%d") + "-week"
            elif period == "This Month":
                start_date, end_date = get_date_range_for_month()
                date_suffix = datetime.now(timezone.utc).strftime("%Y%m")
            else:  # All Time
                # Get earliest session
                start_date = "2000-01-01T00:00:00+00:00"
                end_date = datetime.now(timezone.utc).isoformat()
                date_suffix = "all-time"
            
            self.export_sessions_csv(start_date, end_date, date_suffix)
    
    def export_sessions_csv(self, start_date: str, end_date: str, date_suffix: str):
        """Export timer sessions to CSV.
        
        Args:
            start_date: Start date ISO format
            end_date: End date ISO format
            date_suffix: Suffix for filename
        """
        export_dir = get_default_export_path()
        filename = generate_export_filename("sessions", date_suffix)
        filepath = export_dir / filename
        
        # Get all sessions in date range
        sessions = self.db.get_sessions_for_date_range(start_date, end_date)
        
        # Prepare session data for export
        session_data = []
        for session_row in sessions:
            session = TimerSession.from_db_row(session_row)
            
            # Format timestamps as YYYY-MM-DD HH:MM:SS (standard datetime format with seconds)
            start_time_str = session.start_time.strftime("%Y-%m-%d %H:%M:%S") if session.start_time else ''
            end_time_str = session.end_time.strftime("%Y-%m-%d %H:%M:%S") if session.end_time else 'Running'
            
            session_data.append({
                'task_name': session.task_name or 'Unknown',
                'start_time': start_time_str,
                'end_time': end_time_str,
                'duration_seconds': session.duration_seconds or session.get_elapsed_seconds(),
                'duration_formatted': session.get_elapsed_display()
            })
        
        # Export to CSV
        export_sessions_to_csv(session_data, str(filepath))
        
        QMessageBox.information(
            self, "Export Complete",
            f"Exported {len(session_data)} timer sessions to:\n{filepath}"
        )
    
    def autosave(self):
        """Auto-save timer state."""
        # Database saves on each operation, so this is a placeholder
        # for future functionality like backup or state verification
        pass
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About Context Timer",
            "Context Timer v0.1.0\n\n"
            "A desktop application for tracking multiple concurrent task timers "
            "and context switches.\n\n"
            "Licensed under GPL-3.0"
        )
    
    def show_preferences(self):
        """Show preferences dialog."""
        dialog = PreferencesDialog(self, self.db)
        dialog.exec()
    
    def check_auto_start_work_day(self):
        """Check if Work Day should auto-start based on preferences."""
        # Don't auto-start if Work Day is already running
        if self.work_day_session_id is not None:
            return
        
        # Get expected start time from preferences
        start_time_str = self.db.get_setting('expected_start_time')
        if not start_time_str:
            return  # No preference set
        
        # Parse the expected start time
        try:
            hour, minute = map(int, start_time_str.split(':'))
        except (ValueError, AttributeError):
            return  # Invalid format
        
        # Get current time
        now = datetime.now()
        expected_start = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If current time is after expected start time, auto-start Work Day
        if now >= expected_start:
            self.toggle_work_day()
    
    def toggle_work_day(self):
        """Toggle Work Day timer."""
        if self.work_day_session_id is None:
            # Start Work Day timer
            # Create or get Work Day task
            tasks = self.db.get_all_tasks()
            work_day_task = next((t for t in tasks if t['name'] == "Work Day"), None)
            
            if work_day_task is None:
                # Create Work Day task
                work_day_task_id = self.db.create_task("Work Day", "#2ecc71")  # Green
            else:
                work_day_task_id = work_day_task['id']
            
            # Get or create Work Day session for today (reuses existing if stopped earlier today)
            self.work_day_session_id = self.db.get_or_create_work_day_session_for_today(work_day_task_id)
            
            # Update button
            self.work_day_button.setText("Stop Working")
            self.work_day_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    font-size: 12pt;
                    font-weight: bold;
                    border-radius: 8px;
                    min-width: 200px;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            
            # Enable Lunch and Break buttons
            self.lunch_button.setEnabled(True)
            self.break_button.setEnabled(True)
            
            # Add timer widget
            session_row = self.db.get_session_by_id(self.work_day_session_id)
            if session_row:
                session = TimerSession.from_db_row(session_row)
                self.add_timer_widget(session)
        else:
            # Stop Work Day timer
            self.db.stop_session(self.work_day_session_id)
            
            # Remove timer widget
            if self.work_day_session_id in self.active_timer_widgets:
                widget = self.active_timer_widgets[self.work_day_session_id]
                self.active_timers_layout.removeWidget(widget)
                widget.deleteLater()
                del self.active_timer_widgets[self.work_day_session_id]
            
            # Reset session ID
            self.work_day_session_id = None
            
            # Update button
            self.work_day_button.setText("Start My Day")
            self.work_day_button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    font-size: 12pt;
                    font-weight: bold;
                    border-radius: 8px;
                    min-width: 200px;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            
            # Stop all timers including Lunch/Break
            session_ids = list(self.active_timer_widgets.keys())
            for session_id in session_ids:
                # Stop all timers except the Work Day timer we just stopped
                if session_id != self.work_day_session_id:
                    self.stop_timer(session_id)
            
            # Reset Lunch/Break session IDs and buttons
            self.lunch_session_id = None
            self.break_session_id = None
            
            self.lunch_button.setText("Lunch")
            self.lunch_button.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    font-size: 11pt;
                    font-weight: bold;
                    border-radius: 8px;
                    min-width: 150px;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)
            
            self.break_button.setText("Break")
            self.break_button.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    font-size: 11pt;
                    font-weight: bold;
                    border-radius: 8px;
                    min-width: 150px;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)
            
            self.lunch_button.setEnabled(False)
            self.break_button.setEnabled(False)
    
    def toggle_lunch(self):
        """Toggle Lunch timer."""
        if self.lunch_session_id is None:
            # Stop all regular task timers (but NOT Work Day)
            session_ids = list(self.active_timer_widgets.keys())
            for session_id in session_ids:
                if session_id != self.work_day_session_id:
                    self.stop_timer(session_id)
            
            # Create or get Lunch task
            tasks = self.db.get_all_tasks()
            lunch_task = next((t for t in tasks if t['name'] == "Lunch"), None)
            
            if lunch_task is None:
                # Create Lunch task
                lunch_task_id = self.db.create_task("Lunch", "#f39c12")  # Yellow
            else:
                lunch_task_id = lunch_task['id']
            
            # Start timer
            self.lunch_session_id = self.db.start_session(lunch_task_id)
            
            # Update button
            self.lunch_button.setText("End Lunch")
            self.lunch_button.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    font-size: 11pt;
                    font-weight: bold;
                    border-radius: 8px;
                    min-width: 150px;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: #d35400;
                }
            """)
            
            # Disable Break button
            self.break_button.setEnabled(False)
            
            # Add timer widget
            session_row = self.db.get_session_by_id(self.lunch_session_id)
            if session_row:
                session = TimerSession.from_db_row(session_row)
                self.add_timer_widget(session)
        else:
            # Stop Lunch timer
            self.db.stop_session(self.lunch_session_id)
            
            # Remove timer widget
            if self.lunch_session_id in self.active_timer_widgets:
                widget = self.active_timer_widgets[self.lunch_session_id]
                self.active_timers_layout.removeWidget(widget)
                widget.deleteLater()
                del self.active_timer_widgets[self.lunch_session_id]
            
            # Reset session ID
            self.lunch_session_id = None
            
            # Update button
            self.lunch_button.setText("Lunch")
            self.lunch_button.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    font-size: 11pt;
                    font-weight: bold;
                    border-radius: 8px;
                    min-width: 150px;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)
            
            # Re-enable Break button
            self.break_button.setEnabled(True)
    
    def toggle_break(self):
        """Toggle Break timer."""
        if self.break_session_id is None:
            # Stop all regular task timers (but NOT Work Day)
            session_ids = list(self.active_timer_widgets.keys())
            for session_id in session_ids:
                if session_id != self.work_day_session_id:
                    self.stop_timer(session_id)
            
            # Create or get Break task
            tasks = self.db.get_all_tasks()
            break_task = next((t for t in tasks if t['name'] == "Break"), None)
            
            if break_task is None:
                # Create Break task
                break_task_id = self.db.create_task("Break", "#f39c12")  # Yellow
            else:
                break_task_id = break_task['id']
            
            # Start timer
            self.break_session_id = self.db.start_session(break_task_id)
            
            # Update button
            self.break_button.setText("End Break")
            self.break_button.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    font-size: 11pt;
                    font-weight: bold;
                    border-radius: 8px;
                    min-width: 150px;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: #d35400;
                }
            """)
            
            # Disable Lunch button
            self.lunch_button.setEnabled(False)
            
            # Add timer widget
            session_row = self.db.get_session_by_id(self.break_session_id)
            if session_row:
                session = TimerSession.from_db_row(session_row)
                self.add_timer_widget(session)
        else:
            # Stop Break timer
            self.db.stop_session(self.break_session_id)
            
            # Remove timer widget
            if self.break_session_id in self.active_timer_widgets:
                widget = self.active_timer_widgets[self.break_session_id]
                self.active_timers_layout.removeWidget(widget)
                widget.deleteLater()
                del self.active_timer_widgets[self.break_session_id]
            
            # Reset session ID
            self.break_session_id = None
            
            # Update button
            self.break_button.setText("Break")
            self.break_button.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    font-size: 11pt;
                    font-weight: bold;
                    border-radius: 8px;
                    min-width: 150px;
                    min-height: 50px;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)
            
            # Re-enable Lunch button
            self.lunch_button.setEnabled(True)
    
    def closeEvent(self, event):
        """Handle window close event.
        
        Args:
            event: Close event
        """
        if self.active_timer_widgets:
            reply = QMessageBox.question(
                self, "Active Timers",
                "You have active timers running. Do you want to stop them before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.Yes:
                # Copy keys to avoid modification during iteration
                session_ids = list(self.active_timer_widgets.keys())
                for session_id in session_ids:
                    self.stop_timer(session_id)
        
        self.db.close()
        event.accept()
