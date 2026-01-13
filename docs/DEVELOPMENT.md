# Context Timer Development Guide

## Architecture Overview

Context Timer is a PyQt6 desktop application with a simple layered architecture:

```
┌─────────────────────────────────────┐
│         GUI Layer (PyQt6)           │
│  - MainWindow                       │
│  - TaskDialog                       │
│  - TimerWidget                      │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│      Business Logic Layer           │
│  - Task model                       │
│  - TimerSession model               │
│  - Time utilities                   │
│  - Export utilities                 │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│       Data Layer (SQLite)           │
│  - Database class                   │
│  - Schema management                │
└─────────────────────────────────────┘
```

## Key Components

### Database Layer

**File**: `src/models/database.py`

The `Database` class handles all SQLite operations:
- Table creation and schema management
- CRUD operations for tasks and timer sessions
- Context switch logging
- Query methods for reports

**Schema**:
- `tasks`: Task definitions with names and colors
- `timer_sessions`: Start/end times for each work session
- `context_switches`: Log of task switches with timestamps

All timestamps use ISO 8601 format with UTC timezone.

### Models

**Files**: `src/models/task.py`, `src/models/timer.py`

Simple dataclasses that represent:
- `Task`: Task definition
- `TimerSession`: A single timed work session

These provide convenience methods like `get_elapsed_seconds()` and `from_db_row()`.

### GUI Components

**Main Window** (`src/gui/main_window.py`):
- Tabbed interface (Timers, Daily Report, Weekly Report)
- Task list management
- Timer control
- Report generation and display
- Menu bar with export functionality

**Timer Widget** (`src/gui/timer_widget.py`):
- Displays individual running timer
- Updates display every second using QTimer
- Color-coded by task

**Task Dialog** (`src/gui/task_dialog.py`):
- Modal dialog for adding/editing tasks
- Color picker integration
- Input validation

### Utilities

**Time Utils** (`src/utils/time_utils.py`):
- Duration formatting functions
- Date range calculation for reports
- Timezone-aware datetime handling

**Export Utils** (`src/utils/export.py`):
- CSV export functions for reports
- File path management
- Default export locations

## Development Setup

### Prerequisites

- Python 3.10+
- PyQt6
- pytest (for testing)

### Install Development Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### Running Tests

```bash
pytest tests/
```

For verbose output:
```bash
pytest -v tests/
```

For coverage:
```bash
pytest --cov=src tests/
```

## Code Style Guidelines

### Python Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use docstrings for all public methods

### Naming Conventions

- Classes: PascalCase (`TimerSession`, `MainWindow`)
- Functions/methods: snake_case (`start_timer`, `get_elapsed_seconds`)
- Constants: UPPER_SNAKE_CASE (`DEFAULT_COLOR`)
- Private methods: _leading_underscore (`_initialize_database`)

### Documentation

- All public functions/methods should have docstrings
- Use Google-style docstring format
- Include Args, Returns, and Raises sections where applicable

Example:
```python
def format_duration(seconds: int) -> str:
    """Format duration in seconds to HH:MM:SS string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (HH:MM:SS)
    """
```

## Testing Guidelines

### Unit Tests

- Test files mirror source structure (`test_models.py` for `models/`)
- Use pytest fixtures for database setup
- Test both success and error cases
- Mock external dependencies (file I/O, network)

### Test Organization

```python
def test_feature_name():
    """Test description."""
    # Arrange - set up test data
    # Act - perform the action
    # Assert - verify the result
```

## Database Schema Evolution

When modifying the database schema:

1. Update the schema in `Database._initialize_database()`
2. Consider backward compatibility
3. Test with existing databases
4. Document schema changes in commit messages

## GUI Development Tips

### QTimer Usage

Use QTimer for periodic updates:
```python
self.timer = QTimer()
self.timer.timeout.connect(self.update_display)
self.timer.start(1000)  # Update every second
```

### Thread Safety

- All database operations happen in the main thread
- Long-running operations should show progress indicators
- Consider using QThread for heavy operations

### Styling

- Use PyQt stylesheets for consistent appearance
- Color codes should be readable (consider contrast)
- Test UI with different screen sizes

## Common Development Tasks

### Adding a New Task Field

1. Update database schema in `database.py`
2. Update `Task` model in `task.py`
3. Modify `TaskDialog` to include new field
4. Update relevant display components
5. Write migration logic if needed
6. Add tests

### Adding a New Report

1. Create query methods in `Database`
2. Add report generation logic in `MainWindow`
3. Create UI tab or section for display
4. Add export function in `export.py`
5. Write tests for calculations

### Modifying Timer Behavior

1. Update timer logic in `TimerSession` model
2. Modify `TimerWidget` display logic
3. Update database queries if needed
4. Test with multiple concurrent timers
5. Verify reports reflect changes

## Debugging Tips

### Database Inspection

Use sqlite3 CLI to inspect the database:
```bash
sqlite3 ~/.local/share/context-timer/timers.db
.tables
SELECT * FROM tasks;
```

### PyQt Debugging

Enable Qt debug output:
```python
import sys
from PyQt6.QtCore import qDebug, qWarning
qDebug("Debug message")
```

### Common Issues

- **Timers not updating**: Check QTimer is started and connected
- **Database locked**: Ensure connections are properly closed
- **Timezone issues**: Always use timezone-aware datetime objects

## Performance Considerations

- Database queries are fast due to indexes
- Timer updates (1 per second) are lightweight
- Report generation reads from database each time
- For very large datasets (1000+ sessions), consider caching

## Future Enhancement Ideas

- Add monthly/yearly reports
- Export to JSON format
- Task categories or tags
- Statistics and charts (using matplotlib)
- System tray integration
- Backup/restore functionality
- Dark mode theme
- Configurable report periods
- Task time estimates and tracking

## Contributing

When contributing:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## License

GPL-3.0 - See LICENSE file for details.
