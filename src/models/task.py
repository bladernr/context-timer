"""Task model for Context Timer application."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Represents a task that can be timed."""
    
    id: int
    name: str
    color: Optional[str] = None
    created_at: Optional[datetime] = None
    is_active: bool = True
    
    def __str__(self) -> str:
        """String representation of task."""
        return self.name
    
    @classmethod
    def from_db_row(cls, row) -> 'Task':
        """Create Task instance from database row.
        
        Args:
            row: sqlite3.Row object
            
        Returns:
            Task instance
        """
        return cls(
            id=row['id'],
            name=row['name'],
            color=row['color'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            is_active=bool(row['is_active'])
        )
