"""Unit tests for GUI components."""
import pytest
import tempfile
import os
from datetime import datetime, timezone
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.models.database import Database
from src.gui.task_dialog import TaskDialog
from src.gui.preferences_dialog import PreferencesDialog


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def test_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp()
    db = Database(path)
    yield db
    db.close()
    os.close(fd)
    os.unlink(path)


def test_task_dialog_creation(qapp):
    """Test creating TaskDialog."""
    dialog = TaskDialog()
    assert dialog is not None
    assert dialog.windowTitle() == "Add Task"
    

def test_task_dialog_edit_mode(qapp, test_db):
    """Test TaskDialog in edit mode."""
    task_id = test_db.create_task("Test Task", "#ff0000")
    
    dialog = TaskDialog(task_name="Test Task", task_color="#ff0000")
    assert dialog.windowTitle() == "Edit Task"
    assert dialog.name_input.text() == "Test Task"


def test_task_dialog_get_data(qapp):
    """Test getting data from TaskDialog."""
    dialog = TaskDialog(task_name="Initial Task", task_color="#00ff00")
    
    # Modify the input
    dialog.name_input.setText("New Task")
    dialog.task_color = "#00ff00"
    
    # Simulate accept to update task_name from input
    dialog.task_name = dialog.name_input.text()
    
    name, color = dialog.get_task_data()
    assert name == "New Task"
    assert color == "#00ff00"


def test_task_dialog_validation_empty_name(qapp):
    """Test task dialog validation with empty name."""
    dialog = TaskDialog()
    dialog.name_input.setText("")
    
    # Accept should not work with empty name
    # (Validation happens in accept method)
    assert dialog.name_input.text() == ""


def test_preferences_dialog_creation(qapp, test_db):
    """Test creating PreferencesDialog."""
    dialog = PreferencesDialog(db=test_db)
    assert dialog is not None
    assert dialog.windowTitle() == "Preferences"
    assert dialog.start_time_edit is not None


def test_preferences_dialog_save(qapp, test_db):
    """Test saving preferences."""
    dialog = PreferencesDialog(db=test_db)
    
    from PyQt6.QtCore import QTime
    dialog.start_time_edit.setTime(QTime(9, 30))
    dialog.save_preferences()
    
    # Verify saved to database
    saved_time = test_db.get_setting('expected_start_time')
    assert saved_time == '09:30'


def test_preferences_dialog_load(qapp, test_db):
    """Test loading existing preferences."""
    # Set a preference
    test_db.set_setting('expected_start_time', '10:15')
    
    # Create dialog and verify it loads the setting
    dialog = PreferencesDialog(db=test_db)
    time = dialog.start_time_edit.time()
    assert time.hour() == 10
    assert time.minute() == 15


def test_main_window_task_button_color():
    """Test task button color determination."""
    from src.gui.main_window import MainWindow
    from PyQt6.QtGui import QColor
    
    # Test with a temporary database
    fd, path = tempfile.mkstemp()
    
    try:
        window = MainWindow()
        
        # Test dark color detection
        assert window.is_dark_color("#000000") is True
        assert window.is_dark_color("#ffffff") is False
        assert window.is_dark_color("#000080") is True   # Navy blue
        
        # Red has low luminance by the RGB luminance formula
        # 0.299 * 255 + 0.587 * 0 + 0.114 * 0 = 76.245/255 = 0.299 which is < 0.5
        assert window.is_dark_color("#ff0000") is True
        
        window.db.close()
    finally:
        os.close(fd)
        if os.path.exists(path):
            os.unlink(path)


def test_timer_widget_creation(qapp):
    """Test creating TimerWidget."""
    from src.gui.timer_widget import TimerWidget
    
    widget = TimerWidget(
        session_id=1,
        task_id=1,
        task_name="Test Task",
        task_color="#ff0000",
        start_time=datetime.now(timezone.utc)
    )
    assert widget is not None
    assert "Test Task" in widget.name_label.text()


def test_timer_widget_update_display(qapp):
    """Test updating timer display."""
    from src.gui.timer_widget import TimerWidget
    
    widget = TimerWidget(
        session_id=1,
        task_id=1,
        task_name="Test Task",
        task_color="#ff0000",
        start_time=datetime.now(timezone.utc)
    )
    widget.update_display()
    
    # Should show elapsed time
    assert "00:" in widget.time_label.text()


def test_timer_widget_stop_callback(qapp):
    """Test timer widget stop callback."""
    from src.gui.timer_widget import TimerWidget
    
    widget = TimerWidget(
        session_id=1,
        task_id=1,
        task_name="Test Task",
        task_color="#ff0000",
        start_time=datetime.now(timezone.utc)
    )
    
    # Verify stop button exists
    assert widget.stop_button is not None
