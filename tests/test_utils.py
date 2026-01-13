"""Unit tests for time utilities."""
import pytest
from datetime import datetime, timezone
from src.utils.time_utils import (
    format_duration,
    format_duration_verbose,
    get_date_range_for_today,
    get_date_range_for_week,
    get_week_dates,
    format_date,
    format_datetime
)


def test_format_duration():
    """Test duration formatting."""
    assert format_duration(0) == "00:00:00"
    assert format_duration(61) == "00:01:01"
    assert format_duration(3661) == "01:01:01"
    assert format_duration(36125) == "10:02:05"


def test_format_duration_verbose():
    """Test verbose duration formatting."""
    assert format_duration_verbose(0) == "0s"
    assert format_duration_verbose(61) == "1m 1s"
    assert format_duration_verbose(3661) == "1h 1m 1s"
    assert format_duration_verbose(3600) == "1h"
    assert format_duration_verbose(60) == "1m"


def test_get_date_range_for_today():
    """Test getting date range for today."""
    start, end = get_date_range_for_today()
    
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    
    # Should be start and end of same day
    assert start_dt.hour == 0
    assert start_dt.minute == 0
    assert start_dt.second == 0
    
    # End should be 24 hours after start
    assert (end_dt - start_dt).days == 1


def test_get_date_range_for_week():
    """Test getting date range for current week."""
    start, end = get_date_range_for_week()
    
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    
    # Start should be Monday (weekday 0)
    assert start_dt.weekday() == 0
    
    # Should span 7 days
    assert (end_dt - start_dt).days == 7


def test_get_week_dates():
    """Test getting all dates in current week."""
    dates = get_week_dates()
    
    assert len(dates) == 7
    
    # Should start with Monday
    assert dates[0].weekday() == 0
    
    # Should be consecutive days
    for i in range(6):
        assert (dates[i + 1] - dates[i]).days == 1


def test_format_date():
    """Test date formatting."""
    dt = datetime(2026, 1, 11, 15, 30, 0, tzinfo=timezone.utc)
    formatted = format_date(dt)
    assert "Jan" in formatted
    assert "11" in formatted
    assert "2026" in formatted


def test_format_datetime():
    """Test datetime formatting."""
    dt = datetime(2026, 1, 11, 15, 30, 0, tzinfo=timezone.utc)
    formatted = format_datetime(dt)
    assert "Jan" in formatted
    assert "11" in formatted
    assert "2026" in formatted
    assert "PM" in formatted or "AM" in formatted


def test_get_default_export_path():
    """Test getting default export path."""
    from src.utils.export import get_default_export_path
    import os
    
    export_path = get_default_export_path()
    assert export_path.exists()
    assert export_path.is_dir()
    assert "context-timer-exports" in str(export_path)


def test_generate_export_filename():
    """Test generating export filenames."""
    from src.utils.export import generate_export_filename
    
    filename = generate_export_filename("sessions", "20260112")
    assert "context-timer-sessions" in filename
    assert "20260112" in filename
    assert filename.endswith(".csv")
    assert len(filename) > 20  # Should have timestamp


def test_export_sessions_to_csv():
    """Test exporting sessions to CSV."""
    from src.utils.export import export_sessions_to_csv
    import tempfile
    import csv
    import os
    
    # Create test data
    session_data = [
        {
            'task_name': 'Test Task',
            'start_time': '2026-01-12 09:00:00',
            'end_time': '2026-01-12 10:00:00',
            'duration_seconds': 3600,
            'duration_formatted': '01:00:00'
        }
    ]
    
    # Export to temp file
    fd, path = tempfile.mkstemp(suffix='.csv')
    os.close(fd)
    
    try:
        export_sessions_to_csv(session_data, path)
        
        # Verify file contents
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['Task Name'] == 'Test Task'
            assert rows[0]['Start Time'] == '2026-01-12 09:00:00'
            assert rows[0]['Duration (seconds)'] == '3600'
    finally:
        os.unlink(path)


def test_get_date_range_for_month():
    """Test getting date range for current month."""
    from src.utils.time_utils import get_date_range_for_month
    
    start, end = get_date_range_for_month()
    
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    
    # Should start at day 1
    assert start_dt.day == 1
    assert start_dt.hour == 0
    assert start_dt.minute == 0
    
    # End should be first day of next month
    assert end_dt.day == 1
