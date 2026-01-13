"""Database management for Context Timer application."""
import sqlite3
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Tuple


class Database:
    """Manages SQLite database connections and operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use XDG standard location on Linux
            data_dir = Path.home() / ".local" / "share" / "context-timer"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "timers.db")
        
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def _initialize_database(self):
        """Create database schema if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT,
                created_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Timer sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timer_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds INTEGER,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        """)
        
        # Context switches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_switches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_task_id INTEGER,
                to_task_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (from_task_id) REFERENCES tasks (id),
                FOREIGN KEY (to_task_id) REFERENCES tasks (id)
            )
        """)
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_task_start 
            ON timer_sessions(task_id, start_time)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_start_time 
            ON timer_sessions(start_time)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_switches_timestamp 
            ON context_switches(timestamp)
        """)
        
        conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    # Task operations
    def create_task(self, name: str, color: Optional[str] = None) -> int:
        """Create a new task.
        
        Args:
            name: Task name
            color: Optional color code for UI
            
        Returns:
            ID of created task
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        created_at = datetime.now(timezone.utc).isoformat()
        
        cursor.execute(
            "INSERT INTO tasks (name, color, created_at) VALUES (?, ?, ?)",
            (name, color, created_at)
        )
        conn.commit()
        return cursor.lastrowid
    
    def get_all_tasks(self, active_only: bool = True) -> List[sqlite3.Row]:
        """Get all tasks.
        
        Args:
            active_only: If True, only return active tasks
            
        Returns:
            List of task rows
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute("SELECT * FROM tasks WHERE is_active = 1 ORDER BY name")
        else:
            cursor.execute("SELECT * FROM tasks ORDER BY name")
        
        return cursor.fetchall()
    
    def get_task_by_id(self, task_id: int) -> Optional[sqlite3.Row]:
        """Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task row or None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return cursor.fetchone()
    
    def update_task(self, task_id: int, name: Optional[str] = None, 
                   color: Optional[str] = None):
        """Update task properties.
        
        Args:
            task_id: Task ID
            name: New name (if provided)
            color: New color (if provided)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if name is not None:
            cursor.execute("UPDATE tasks SET name = ? WHERE id = ?", (name, task_id))
        if color is not None:
            cursor.execute("UPDATE tasks SET color = ? WHERE id = ?", (color, task_id))
        
        conn.commit()
    
    def delete_task(self, task_id: int):
        """Soft delete a task (mark as inactive).
        
        Args:
            task_id: Task ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET is_active = 0 WHERE id = ?", (task_id,))
        conn.commit()
    
    # Timer session operations
    def start_session(self, task_id: int) -> int:
        """Start a new timer session.
        
        Args:
            task_id: Task ID
            
        Returns:
            ID of created session
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        start_time = datetime.now(timezone.utc).isoformat()
        
        cursor.execute(
            "INSERT INTO timer_sessions (task_id, start_time) VALUES (?, ?)",
            (task_id, start_time)
        )
        conn.commit()
        return cursor.lastrowid
    
    def stop_session(self, session_id: int):
        """Stop a timer session.
        
        Args:
            session_id: Session ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        end_time = datetime.now(timezone.utc).isoformat()
        
        # Get start time to calculate duration
        cursor.execute("SELECT start_time FROM timer_sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            start_time = datetime.fromisoformat(row['start_time'])
            end_time_dt = datetime.fromisoformat(end_time)
            duration_seconds = int((end_time_dt - start_time).total_seconds())
            
            cursor.execute(
                "UPDATE timer_sessions SET end_time = ?, duration_seconds = ? WHERE id = ?",
                (end_time, duration_seconds, session_id)
            )
            conn.commit()
    
    def get_active_sessions(self) -> List[sqlite3.Row]:
        """Get all currently active (running) sessions.
        
        Returns:
            List of active session rows
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, t.name as task_name, t.color as task_color 
            FROM timer_sessions s
            JOIN tasks t ON s.task_id = t.id
            WHERE s.end_time IS NULL
            ORDER BY s.start_time
        """)
        return cursor.fetchall()
    
    def get_session_by_id(self, session_id: int) -> Optional[sqlite3.Row]:
        """Get a session by its ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            Session row or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, t.name as task_name, t.color as task_color 
            FROM timer_sessions s
            JOIN tasks t ON s.task_id = t.id
            WHERE s.id = ?
        """, (session_id,))
        return cursor.fetchone()
    
    def get_or_create_work_day_session_for_today(self, task_id: int) -> int:
        """Get existing Work Day session for today or create a new one.
        
        Args:
            task_id: The Work Day task ID
            
        Returns:
            Session ID
        """
        # Get today's date range
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if a Work Day session exists for today
        cursor.execute("""
            SELECT id FROM timer_sessions
            WHERE task_id = ? AND start_time >= ? AND start_time <= ?
            ORDER BY start_time DESC
            LIMIT 1
        """, (task_id, start_of_day, end_of_day))
        
        row = cursor.fetchone()
        if row:
            # Reopen the existing session by setting end_time to NULL
            session_id = row['id']
            cursor.execute("""
                UPDATE timer_sessions 
                SET end_time = NULL, duration_seconds = NULL
                WHERE id = ?
            """, (session_id,))
            conn.commit()
            return session_id
        else:
            # Create new session
            return self.start_session(task_id)
    
    def get_sessions_for_date_range(self, start_date: str, end_date: str) -> List[sqlite3.Row]:
        """Get sessions within a date range.
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            
        Returns:
            List of session rows
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, t.name as task_name, t.color as task_color
            FROM timer_sessions s
            JOIN tasks t ON s.task_id = t.id
            WHERE s.start_time >= ? AND s.start_time < ?
            ORDER BY s.start_time
        """, (start_date, end_date))
        return cursor.fetchall()
    
    # Context switch operations
    def log_context_switch(self, from_task_id: Optional[int], to_task_id: int):
        """Log a context switch.
        
        Args:
            from_task_id: Previous task ID (None if first task)
            to_task_id: New task ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        cursor.execute(
            "INSERT INTO context_switches (from_task_id, to_task_id, timestamp) VALUES (?, ?, ?)",
            (from_task_id, to_task_id, timestamp)
        )
        conn.commit()
    
    def get_context_switches_for_date_range(self, start_date: str, end_date: str) -> List[sqlite3.Row]:
        """Get context switches within a date range.
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            
        Returns:
            List of context switch rows
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM context_switches
            WHERE timestamp >= ? AND timestamp < ?
            ORDER BY timestamp
        """, (start_date, end_date))
        return cursor.fetchall()
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value.
        
        Args:
            key: Setting key
            
        Returns:
            Setting value or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else None
    
    def set_setting(self, key: str, value: str):
        """Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        """, (key, value))
        conn.commit()
    
    # Clear history operations
    def clear_history_for_date_range(self, start_date: str, end_date: str) -> int:
        """Clear all sessions and context switches within a date range.
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            
        Returns:
            Number of sessions deleted
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Count sessions before deleting
        cursor.execute("""
            SELECT COUNT(*) as count FROM timer_sessions
            WHERE start_time >= ? AND start_time < ?
        """, (start_date, end_date))
        count = cursor.fetchone()['count']
        
        # Delete context switches first (foreign key references)
        cursor.execute("""
            DELETE FROM context_switches
            WHERE timestamp >= ? AND timestamp < ?
        """, (start_date, end_date))
        
        # Delete sessions
        cursor.execute("""
            DELETE FROM timer_sessions
            WHERE start_time >= ? AND start_time < ?
        """, (start_date, end_date))
        
        conn.commit()
        return count
    
    def clear_all_history(self) -> int:
        """Clear all sessions and context switches.
        
        Returns:
            Number of sessions deleted
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Count sessions before deleting
        cursor.execute("SELECT COUNT(*) as count FROM timer_sessions")
        count = cursor.fetchone()['count']
        
        # Delete all context switches
        cursor.execute("DELETE FROM context_switches")
        
        # Delete all sessions
        cursor.execute("DELETE FROM timer_sessions")
        
        conn.commit()
        return count
