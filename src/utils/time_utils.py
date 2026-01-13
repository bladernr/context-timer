"""Time formatting utilities for Context Timer application."""
from datetime import datetime, timedelta, timezone
from typing import Tuple


def format_duration(seconds: int) -> str:
    """Format duration in seconds to HH:MM:SS string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (HH:MM:SS)
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_duration_verbose(seconds: int) -> str:
    """Format duration in seconds to verbose string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string like "2h 15m 30s"
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def get_date_range_for_today() -> Tuple[str, str]:
    """Get ISO format date range for today.
    
    Returns:
        Tuple of (start_of_day, end_of_day) in ISO format
    """
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    return start_of_day.isoformat(), end_of_day.isoformat()


def get_date_range_for_week() -> Tuple[str, str]:
    """Get ISO format date range for current week (Monday to Sunday).
    
    Returns:
        Tuple of (start_of_week, end_of_week) in ISO format
    """
    now = datetime.now(timezone.utc)
    # Get Monday of current week
    days_since_monday = now.weekday()
    start_of_week = (now - timedelta(days=days_since_monday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_of_week = start_of_week + timedelta(days=7)
    return start_of_week.isoformat(), end_of_week.isoformat()


def get_date_range_for_month() -> Tuple[str, str]:
    """Get ISO format date range for current month.
    
    Returns:
        Tuple of (start_of_month, end_of_month) in ISO format
    """
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get first day of next month
    if now.month == 12:
        end_of_month = start_of_month.replace(year=now.year + 1, month=1)
    else:
        end_of_month = start_of_month.replace(month=now.month + 1)
    
    return start_of_month.isoformat(), end_of_month.isoformat()


def get_week_dates() -> list:
    """Get list of dates for current week (Monday to Sunday).
    
    Returns:
        List of datetime objects for each day of the week
    """
    now = datetime.now(timezone.utc)
    days_since_monday = now.weekday()
    monday = (now - timedelta(days=days_since_monday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    
    return [monday + timedelta(days=i) for i in range(7)]


def format_date(dt: datetime) -> str:
    """Format datetime as readable date string.
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted string like "Jan 11, 2026"
    """
    return dt.strftime("%b %d, %Y")


def format_datetime(dt: datetime) -> str:
    """Format datetime as readable datetime string.
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted string like "Jan 11, 2026 3:45 PM"
    """
    return dt.strftime("%b %d, %Y %I:%M %p")
