"""Timer session model for Context Timer application."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class TimerSession:
    """Represents a timer session for a task."""
    
    id: Optional[int]
    task_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    task_name: Optional[str] = None
    task_color: Optional[str] = None
    
    @property
    def is_running(self) -> bool:
        """Check if timer is currently running."""
        return self.end_time is None
    
    def get_elapsed_seconds(self) -> int:
        """Get elapsed time in seconds.
        
        Returns:
            Elapsed seconds (for running timers, calculated to now)
        """
        if self.duration_seconds is not None:
            return self.duration_seconds
        
        # Calculate elapsed time for running timer
        now = datetime.now(timezone.utc)
        return int((now - self.start_time).total_seconds())
    
    def get_elapsed_display(self) -> str:
        """Get elapsed time as formatted string.
        
        Returns:
            Formatted time string (HH:MM:SS)
        """
        seconds = self.get_elapsed_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    @classmethod
    def from_db_row(cls, row) -> 'TimerSession':
        """Create TimerSession instance from database row.
        
        Args:
            row: sqlite3.Row object
            
        Returns:
            TimerSession instance
        """
        # sqlite3.Row doesn't have .get() method, need to check keys
        row_keys = row.keys()
        return cls(
            id=row['id'],
            task_id=row['task_id'],
            start_time=datetime.fromisoformat(row['start_time']),
            end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
            duration_seconds=row['duration_seconds'],
            task_name=row['task_name'] if 'task_name' in row_keys else None,
            task_color=row['task_color'] if 'task_color' in row_keys else None
        )
