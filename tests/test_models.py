"""Unit tests for database models."""
import pytest
import tempfile
import os
from datetime import datetime, timezone, timedelta
from src.models.database import Database
from src.models.task import Task
from src.models.timer import TimerSession


@pytest.fixture
def test_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp()
    db = Database(path)
    yield db
    db.close()
    os.close(fd)
    os.unlink(path)


def test_create_task(test_db):
    """Test creating a task."""
    task_id = test_db.create_task("Test Task", "#ff0000")
    assert task_id > 0
    
    task_row = test_db.get_task_by_id(task_id)
    assert task_row is not None
    
    task = Task.from_db_row(task_row)
    assert task.name == "Test Task"
    assert task.color == "#ff0000"
    assert task.is_active is True


def test_get_all_tasks(test_db):
    """Test getting all tasks."""
    test_db.create_task("Task 1", "#ff0000")
    test_db.create_task("Task 2", "#00ff00")
    
    tasks = test_db.get_all_tasks()
    assert len(tasks) == 2


def test_update_task(test_db):
    """Test updating a task."""
    task_id = test_db.create_task("Original Name", "#ff0000")
    test_db.update_task(task_id, name="Updated Name", color="#00ff00")
    
    task_row = test_db.get_task_by_id(task_id)
    task = Task.from_db_row(task_row)
    assert task.name == "Updated Name"
    assert task.color == "#00ff00"


def test_delete_task(test_db):
    """Test soft deleting a task."""
    task_id = test_db.create_task("Task to Delete")
    test_db.delete_task(task_id)
    
    # Should not appear in active tasks
    active_tasks = test_db.get_all_tasks(active_only=True)
    assert len(active_tasks) == 0
    
    # Should still exist when including inactive
    all_tasks = test_db.get_all_tasks(active_only=False)
    assert len(all_tasks) == 1


def test_start_session(test_db):
    """Test starting a timer session."""
    task_id = test_db.create_task("Test Task")
    session_id = test_db.start_session(task_id)
    
    assert session_id > 0
    
    active_sessions = test_db.get_active_sessions()
    assert len(active_sessions) == 1
    
    session = TimerSession.from_db_row(active_sessions[0])
    assert session.task_id == task_id
    assert session.is_running is True


def test_stop_session(test_db):
    """Test stopping a timer session."""
    task_id = test_db.create_task("Test Task")
    session_id = test_db.start_session(task_id)
    
    # Wait a moment to ensure duration > 0
    import time
    time.sleep(0.1)
    
    test_db.stop_session(session_id)
    
    active_sessions = test_db.get_active_sessions()
    assert len(active_sessions) == 0


def test_multiple_active_sessions(test_db):
    """Test multiple concurrent sessions."""
    task1_id = test_db.create_task("Task 1")
    task2_id = test_db.create_task("Task 2")
    
    session1_id = test_db.start_session(task1_id)
    session2_id = test_db.start_session(task2_id)
    
    active_sessions = test_db.get_active_sessions()
    assert len(active_sessions) == 2


def test_log_context_switch(test_db):
    """Test logging context switches."""
    task1_id = test_db.create_task("Task 1")
    task2_id = test_db.create_task("Task 2")
    
    test_db.log_context_switch(None, task1_id)
    test_db.log_context_switch(task1_id, task2_id)
    
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end_of_day = (now + timedelta(days=1)).isoformat()
    
    switches = test_db.get_context_switches_for_date_range(start_of_day, end_of_day)
    assert len(switches) == 2


def test_get_sessions_for_date_range(test_db):
    """Test getting sessions within a date range."""
    task_id = test_db.create_task("Test Task")
    session_id = test_db.start_session(task_id)
    test_db.stop_session(session_id)
    
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end_of_day = (now + timedelta(days=1)).isoformat()
    
    sessions = test_db.get_sessions_for_date_range(start_of_day, end_of_day)
    assert len(sessions) == 1


def test_get_setting(test_db):
    """Test getting a setting value."""
    # Non-existent setting should return None
    value = test_db.get_setting('non_existent')
    assert value is None
    
    # Set and retrieve setting
    test_db.set_setting('test_key', 'test_value')
    value = test_db.get_setting('test_key')
    assert value == 'test_value'


def test_set_setting(test_db):
    """Test setting a value."""
    test_db.set_setting('key1', 'value1')
    assert test_db.get_setting('key1') == 'value1'
    
    # Update existing setting
    test_db.set_setting('key1', 'value2')
    assert test_db.get_setting('key1') == 'value2'


def test_get_session_by_id(test_db):
    """Test getting a specific session by ID."""
    task_id = test_db.create_task("Test Task", "#ff0000")
    session_id = test_db.start_session(task_id)
    
    session_row = test_db.get_session_by_id(session_id)
    assert session_row is not None
    
    session = TimerSession.from_db_row(session_row)
    assert session.id == session_id
    assert session.task_id == task_id
    assert session.task_name == "Test Task"
    assert session.task_color == "#ff0000"
    
    # Non-existent session should return None
    assert test_db.get_session_by_id(9999) is None


def test_get_or_create_work_day_session_for_today_new(test_db):
    """Test creating new Work Day session when none exists."""
    task_id = test_db.create_task("Work Day", "#2ecc71")
    
    # First call should create new session
    session_id = test_db.get_or_create_work_day_session_for_today(task_id)
    assert session_id > 0
    
    # Verify session is active
    session_row = test_db.get_session_by_id(session_id)
    session = TimerSession.from_db_row(session_row)
    assert session.is_running is True


def test_get_or_create_work_day_session_for_today_reopen(test_db):
    """Test reopening existing Work Day session from same day."""
    task_id = test_db.create_task("Work Day", "#2ecc71")
    
    # Create and stop a session
    session_id_1 = test_db.start_session(task_id)
    import time
    time.sleep(0.1)
    test_db.stop_session(session_id_1)
    
    # Verify session is stopped
    session_row = test_db.get_session_by_id(session_id_1)
    session = TimerSession.from_db_row(session_row)
    assert session.is_running is False
    
    # Call get_or_create should reopen the same session
    session_id_2 = test_db.get_or_create_work_day_session_for_today(task_id)
    assert session_id_2 == session_id_1
    
    # Verify session is now running again
    session_row = test_db.get_session_by_id(session_id_2)
    session = TimerSession.from_db_row(session_row)
    assert session.is_running is True


def test_database_context_manager(test_db):
    """Test database context manager."""
    with test_db as db:
        task_id = db.create_task("Context Test")
        assert task_id > 0


def test_task_from_db_row():
    """Test creating Task from database row."""
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            name TEXT,
            color TEXT,
            created_at TEXT,
            is_active INTEGER
        )
    """)
    
    cursor.execute("""
        INSERT INTO tasks (name, color, created_at, is_active)
        VALUES (?, ?, ?, ?)
    """, ("Test", "#ff0000", datetime.now(timezone.utc).isoformat(), 1))
    
    cursor.execute("SELECT * FROM tasks WHERE id = 1")
    row = cursor.fetchone()
    
    task = Task.from_db_row(row)
    assert task.name == "Test"
    assert task.color == "#ff0000"
    assert task.is_active is True
    conn.close()


def test_clear_history_for_date_range(test_db):
    """Test clearing history for a specific date range."""
    task_id = test_db.create_task("Test Task", "#ff0000")
    
    # Create sessions for different days
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    
    # Start and end sessions at different times
    session_today = test_db.start_session(task_id)
    test_db.stop_session(session_today)
    
    # Create yesterday's session by directly inserting (to simulate past data)
    conn = test_db._get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO timer_sessions (task_id, start_time, end_time, duration_seconds)
        VALUES (?, ?, ?, ?)
    """, (task_id, yesterday.isoformat(), (yesterday + timedelta(hours=1)).isoformat(), 3600))
    
    cursor.execute("""
        INSERT INTO timer_sessions (task_id, start_time, end_time, duration_seconds)
        VALUES (?, ?, ?, ?)
    """, (task_id, last_week.isoformat(), (last_week + timedelta(hours=2)).isoformat(), 7200))
    conn.commit()
    
    # Clear yesterday's sessions
    start_of_yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_yesterday = start_of_yesterday + timedelta(days=1)
    count = test_db.clear_history_for_date_range(
        start_of_yesterday.isoformat(),
        end_of_yesterday.isoformat()
    )
    
    assert count == 1
    
    # Verify today's and last week's sessions still exist
    all_sessions = test_db.get_sessions_for_date_range(
        last_week.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),
        (today + timedelta(days=1)).isoformat()
    )
    assert len(all_sessions) == 2  # Today and last week


def test_clear_all_history(test_db):
    """Test clearing all history."""
    task_id = test_db.create_task("Test Task", "#ff0000")
    
    # Create multiple sessions
    for _ in range(5):
        session_id = test_db.start_session(task_id)
        test_db.stop_session(session_id)
    
    # Log some context switches
    test_db.log_context_switch(None, task_id)
    test_db.log_context_switch(task_id, task_id)
    
    # Clear all history
    count = test_db.clear_all_history()
    assert count == 5
    
    # Verify no sessions remain
    today = datetime.now(timezone.utc)
    sessions = test_db.get_sessions_for_date_range(
        "2000-01-01T00:00:00+00:00",
        (today + timedelta(days=1)).isoformat()
    )
    assert len(sessions) == 0
    
    # Verify task still exists (not deleted)
    task = test_db.get_task_by_id(task_id)
    assert task is not None

