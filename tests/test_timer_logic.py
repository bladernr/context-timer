"""Unit tests for timer logic."""
import pytest
from datetime import datetime, timezone, timedelta
from src.models.timer import TimerSession


def test_timer_session_is_running():
    """Test checking if timer is running."""
    # Running timer (no end time)
    running_session = TimerSession(
        id=1,
        task_id=1,
        start_time=datetime.now(timezone.utc)
    )
    assert running_session.is_running is True
    
    # Stopped timer (has end time)
    stopped_session = TimerSession(
        id=2,
        task_id=1,
        start_time=datetime.now(timezone.utc) - timedelta(hours=1),
        end_time=datetime.now(timezone.utc),
        duration_seconds=3600
    )
    assert stopped_session.is_running is False


def test_get_elapsed_seconds_running():
    """Test getting elapsed time for running timer."""
    start_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    session = TimerSession(
        id=1,
        task_id=1,
        start_time=start_time
    )
    
    elapsed = session.get_elapsed_seconds()
    assert elapsed >= 10
    assert elapsed < 12  # Allow small margin


def test_get_elapsed_seconds_stopped():
    """Test getting elapsed time for stopped timer."""
    session = TimerSession(
        id=1,
        task_id=1,
        start_time=datetime.now(timezone.utc) - timedelta(hours=1),
        end_time=datetime.now(timezone.utc),
        duration_seconds=3600
    )
    
    elapsed = session.get_elapsed_seconds()
    assert elapsed == 3600


def test_get_elapsed_display():
    """Test formatted elapsed time display."""
    session = TimerSession(
        id=1,
        task_id=1,
        start_time=datetime.now(timezone.utc),
        duration_seconds=3661  # 1 hour, 1 minute, 1 second
    )
    
    display = session.get_elapsed_display()
    assert display == "01:01:01"


def test_get_elapsed_display_hours():
    """Test formatted display with multiple hours."""
    session = TimerSession(
        id=1,
        task_id=1,
        start_time=datetime.now(timezone.utc),
        duration_seconds=36125  # 10 hours, 2 minutes, 5 seconds
    )
    
    display = session.get_elapsed_display()
    assert display == "10:02:05"


def test_timer_session_from_db_row():
    """Test creating TimerSession from database row."""
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE test (
            id INTEGER,
            task_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            duration_seconds INTEGER,
            task_name TEXT,
            task_color TEXT
        )
    """)
    
    start = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO test VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, 10, start, None, None, "Test Task", "#ff0000"))
    
    cursor.execute("SELECT * FROM test WHERE id = 1")
    row = cursor.fetchone()
    
    session = TimerSession.from_db_row(row)
    assert session.id == 1
    assert session.task_id == 10
    assert session.task_name == "Test Task"
    assert session.task_color == "#ff0000"
    assert session.is_running is True
    conn.close()


def test_timer_session_from_db_row_without_task_info():
    """Test creating TimerSession from row without task_name/color."""
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE test (
            id INTEGER,
            task_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            duration_seconds INTEGER
        )
    """)
    
    start = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO test VALUES (?, ?, ?, ?, ?)
    """, (1, 10, start, None, None))
    
    cursor.execute("SELECT * FROM test WHERE id = 1")
    row = cursor.fetchone()
    
    session = TimerSession.from_db_row(row)
    assert session.id == 1
    assert session.task_id == 10
    assert session.task_name is None
    assert session.task_color is None
    conn.close()


def test_timer_session_zero_duration():
    """Test timer with zero duration."""
    now = datetime.now(timezone.utc)
    session = TimerSession(
        id=1,
        task_id=1,
        start_time=now,
        end_time=now,
        duration_seconds=0
    )
    
    assert session.get_elapsed_seconds() == 0
    assert session.get_elapsed_display() == "00:00:00"
