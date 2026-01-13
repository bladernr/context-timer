# Context Timer - AI Development Guide

## Project Overview
A Python desktop application for tracking multiple concurrent task timers, measuring time spent, and counting context switches during work sessions.

## Project Specifications

### Technology Stack
- **Language**: Python 3.10+
- **GUI Framework**: PyQt6 or Tkinter (PyQt6 recommended for modern UI)
- **Data Storage**: SQLite for persistence
- **Target OS**: Linux (primary), cross-platform compatible

### Core Features
1. **Task Management**: Users define common tasks (e.g., "Meeting", "Check Email", "Code Review")
2. **Multiple Concurrent Timers**: Run several task timers simultaneously
3. **Context Switch Tracking**: Count how many times user switches between tasks
4. **Time Tracking**: Record duration for each task session
5. **Persistent State**: Timers survive application restarts

### User Workflow
- Add/edit/delete task definitions
- Start/stop individual task timers (multiple can run concurrently)
- View active timers with elapsed time
- See context switch count and total time per task
- Export reports (daily/weekly summaries)

## Architecture

### Data Model
```python
# Task definition
Task:
  - id: int (primary key)
  - name: str
  - color: str (optional, for UI)
  - created_at: datetime

# Timer session
TimerSession:
  - id: int
  - task_id: int (foreign key)
  - start_time: datetime
  - end_time: datetime (null if running)
  - duration_seconds: int
  
# Context switches
ContextSwitch:
  - id: int
  - from_task_id: int
  - to_task_id: int
  - timestamp: datetime
```

### File Structure
```
context-timer/
├── src/
│   ├── main.py              # Application entry point
│   ├── gui/
│   │   ├── main_window.py   # Main application window
│   │   ├── task_dialog.py   # Add/edit task dialog
│   │   └── timer_widget.py  # Individual timer display widget
│   ├── models/
│   │   ├── database.py      # SQLite setup and queries
│   │   ├── task.py          # Task model
│   │   └── timer.py         # Timer session logic
│   └── utils/
│       ├── time_utils.py    # Time formatting helpers
│       └── export.py        # CSV/JSON export functions
├── tests/
│   ├── test_models.py
│   └── test_timer_logic.py
├── data/                    # SQLite database location (gitignored)
├── requirements.txt         # PyQt6, pytest, etc.
└── README.md
```

## Development Guidelines

### Timer Logic
- Use `datetime.now(timezone.utc)` for all timestamps (timezone-aware)
- Calculate duration on-the-fly for running timers: `now() - start_time`
- Persist timer state every 30 seconds (auto-save)
- On startup, load any timers that were running and resume them

### Context Switch Detection
- When user starts a timer: if other timers already running, log a context switch
- Store: previous task → new task, timestamp
- Display: total switches per task in UI

### GUI Best Practices
- Use QTimer (PyQt) or after() (Tkinter) for updating running timer displays every second
- Keep UI responsive: run long operations (DB writes, exports) in background threads
- Show visual feedback for active timers (color coding, animated indicators)
- Implement keyboard shortcuts (Ctrl+N for new task, Space to start/stop selected timer)

### Data Persistence
- SQLite database at `~/.local/share/context-timer/timers.db` (Linux XDG standard)
- Create database schema on first run if it doesn't exist
- Use context managers for database connections
- Implement migrations if schema changes in future versions

### Error Handling
- Graceful handling of database corruption (backup and recreate)
- Validate task names (non-empty, reasonable length)
- Handle system sleep/hibernate: mark timers as stopped with note

## Common Patterns

### Starting a Timer
```python
# Pseudocode
def start_timer(task_id):
    # Check if task already has running timer
    if is_timer_running(task_id):
        return  # Already running
    
    # Log context switch if other timers active
    active_timers = get_active_timers()
    if active_timers:
        log_context_switch(active_timers[0].task_id, task_id)
    
    # Create new timer session
    create_session(task_id, start_time=now())
```

### Displaying Running Timers
```python
# Update UI every second
def update_timer_display():
    for timer_widget in active_timer_widgets:
        elapsed = now() - timer_widget.start_time
        timer_widget.set_text(format_duration(elapsed))
```

## Dependencies
```
# requirements.txt
PyQt6>=6.4.0
pytest>=7.0.0
```

## Quick Start for AI Agents
1. Create project structure with `src/`, `tests/`, `data/` directories
2. Set up `requirements.txt` and virtual environment
3. Implement database schema in `src/models/database.py`
4. Create basic `Task` and `TimerSession` models
5. Build minimal GUI with task list and start/stop buttons
6. Add timer update loop and duration display
7. Implement context switch logging
8. Add export/reporting features

## Testing Approach
- Unit tests for timer duration calculations
- Test context switch detection logic
- Test database operations (CRUD for tasks and sessions)
- Manual GUI testing for responsiveness and timer accuracy
