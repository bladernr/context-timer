# Context Timer

A Python desktop application for tracking multiple concurrent task timers, measuring time spent on tasks, and counting context switches during work sessions.

## Features

- **Multiple Concurrent Timers**: Run several task timers simultaneously to track multitasking
- **Context Switch Tracking**: Automatically log when you switch between tasks
- **Task Management**: Define and manage your common tasks with custom colors
- **Daily Reports**: View real-time reports of your day's activity
- **Weekly Reports**: See weekly summaries with day-by-day breakdowns
- **Data Export**: Export reports to CSV for further analysis in spreadsheets
- **Persistent State**: Timers continue running even if you close and reopen the app

## Installation

### Option 1: Snap Package (Recommended)

The easiest way to install Context Timer on Linux:

```bash
sudo snap install context-timer
```

Then run:
```bash
context-timer
```

**Note**: The snap is strictly confined for security. Your timer data will be stored in `~/snap/context-timer/current/.local/share/context-timer/`.

### Option 2: From Source

#### Requirements

- Python 3.10 or higher
- PyQt6

#### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/context-timer.git
   cd context-timer
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Or install the package in editable mode (recommended for development):
   ```bash
   pip install -e .
   ```

   To install with development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Usage

### Running the Application

**Option 1**: Run directly from the repository:
```bash
python context_timer.py
```

**Option 2**: Run as a module:
```bash
python -m context_timer
```

**Option 3**: If installed via pip (after `pip install -e .`):
```bash
context-timer
```

### Basic Workflow

1. **Add Tasks**: Click "Add Task" to define tasks you commonly work on (e.g., "Meeting", "Email", "Code Review")
2. **Start Timers**: Select a task and click "Start Timer" to begin tracking time
3. **Multiple Timers**: Start additional timers for other tasks you're working on simultaneously
4. **Stop Timers**: Click "Stop" on individual timers or "Stop All Timers" to end all active timers
5. **View Reports**: Switch to the "Daily Report" or "Weekly Report" tabs to see your statistics
6. **Export Data**: Use the "Export to CSV" button to save reports for analysis

### Keyboard Shortcuts

- **Ctrl+N**: Add new task

## Data Storage

All data is stored locally in a SQLite database at:
- Linux: `~/.local/share/context-timer/timers.db`
- The database includes:
  - Task definitions
  - Timer sessions with start/end times
  - Context switch logs

## Reports

### Daily Report
Shows real-time statistics for the current day:
- Total tasks worked on
- Number of context switches
- Total time worked
- Time breakdown per task

### Weekly Report
Shows summary for the current week (Monday-Sunday):
- Daily time totals
- Context switches per day
- Tasks worked on each day
- Weekly averages

## Development

### Running Tests

```bash
pytest tests/
```

### Building a Snap Package

See [snap/local/README.md](snap/local/README.md) for detailed instructions on building and publishing the snap.

Quick build:
```bash
snapcraft
```

Install locally:
```bash
sudo snap install context-timer_0.1.0_amd64.snap --dangerous
```

### Project Structure

```
context-timer/
├── src/
│   ├── main.py              # Application entry point
│   ├── gui/                 # GUI components
│   │   ├── main_window.py   # Main application window
│   │   ├── task_dialog.py   # Task add/edit dialog
│   │   └── timer_widget.py  # Timer display widget
│   ├── models/              # Data models
│   │   ├── database.py      # SQLite database operations
│   │   ├── task.py          # Task model
│   │   └── timer.py         # Timer session model
│   └── utils/               # Utility functions
│       ├── time_utils.py    # Time formatting helpers
│       └── export.py        # CSV export functions
├── tests/                   # Unit tests
├── data/                    # Database location (gitignored)
└── docs/                    # Documentation

```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Built with Python and PyQt6 for a distraction-free task tracking experience 
