# Context Timer User Guide

## Getting Started

Context Timer helps you track how much time you spend on different tasks and understand your context-switching patterns.

## Installation

See the main [README.md](../README.md) for installation instructions.

## Using Context Timer

### First Launch

When you first launch Context Timer, you'll see an empty task list. You need to add some tasks before you can start timing.

### Managing Tasks

#### Adding a Task

1. Click the "Add Task" button or press Ctrl+N
2. Enter a descriptive name for your task (e.g., "Email", "Meeting", "Code Review")
3. Optionally choose a color to help identify the task visually
4. Click "Save"

Tasks appear in alphabetical order in the task list.

#### Editing a Task

1. Select a task from the list
2. Click "Edit Task"
3. Modify the name or color
4. Click "Save"

#### Deleting a Task

1. Select a task from the list
2. Click "Delete Task"
3. Confirm the deletion

Note: Deleting a task doesn't delete historical data - you can still see past timer sessions for that task in reports.

### Tracking Time

#### Starting a Timer

1. Select a task from the task list
2. Click "Start Timer"

The timer appears in the "Active Timers" section at the top, showing:
- Task name (color-coded)
- Elapsed time (updated every second)
- Stop button

#### Running Multiple Timers

You can run multiple timers simultaneously:
1. Start a timer for one task
2. Start another timer for a different task
3. Both timers run concurrently

**Context Switches**: When you start a new timer while others are running, Context Timer automatically logs this as a context switch.

#### Stopping a Timer

Click the "Stop" button next to the timer you want to stop. The time is saved to the database.

#### Stopping All Timers

Click the "Stop All Timers" button to stop all running timers at once.

### Viewing Reports

#### Daily Report

The Daily Report tab shows your activity for the current day:

- **Summary Section**:
  - Total tasks worked on
  - Total context switches
  - Total time worked (HH:MM:SS format)

- **Task Breakdown**:
  - Time spent on each task
  - Number of sessions per task

The report updates automatically every minute (or immediately when you stop a timer).

#### Weekly Report

The Weekly Report tab shows activity for the current week (Monday through Sunday):

- **Daily Breakdown**:
  - Each day's total time
  - Context switches per day
  - Number of tasks worked on

- **Weekly Summary**:
  - Total time for the week
  - Total context switches
  - Average daily time

### Exporting Data

#### Export Daily Report

1. Go to the "Daily Report" tab
2. Click "Export to CSV"
3. The file is saved to `~/Documents/context-timer-exports/`

#### Export Weekly Report

1. Go to the "Weekly Report" tab
2. Click "Export to CSV"
3. The file is saved to `~/Documents/context-timer-exports/`

CSV files can be opened in spreadsheet applications like Excel, LibreOffice Calc, or Google Sheets for further analysis.

### Tips and Best Practices

1. **Define Clear Tasks**: Use specific, action-oriented task names
2. **Use Colors**: Assign different colors to help distinguish tasks at a glance
3. **Stop Timers**: Remember to stop timers when switching to non-work activities
4. **Review Reports**: Check your daily report at the end of each day to see patterns
5. **Minimize Context Switches**: The app helps you see how often you switch - try to reduce these for better focus

### Closing the Application

When you close Context Timer with active timers running, you'll be prompted to:
- Stop all timers and close
- Close without stopping (timers resume when you reopen)
- Cancel and stay in the app

## Troubleshooting

### Database Issues

If you encounter database errors:
1. Close the application
2. Back up your database file (usually at `~/.local/share/context-timer/timers.db`)
3. Try reopening the application

### Timers Not Updating

If timer displays freeze:
1. Stop and restart the affected timer
2. If the problem persists, restart the application

### Export Location

Exported files are saved to:
- Linux: `~/Documents/context-timer-exports/`
- Filenames include the date and time to prevent overwriting

## Data Privacy

All data is stored locally on your computer. Context Timer does not send any data to external servers or share your information with anyone.
