# Context Timer - TODO List

## Future Enhancements

### High Priority

- [ ] **Add comments/notes to timer sessions**: Allow users to add a short comment when starting a timer to provide context
  - Example: When starting "Meeting" timer, add note like "Weekly team standup" or "1:1 with manager"
  - Store in database as optional `note` field in `timer_sessions` table
  - Display notes in reports and timer widgets
  - Edit notes on running timers
  - Export notes in CSV reports

- [ ] **"Start My Day" button**: Quick action to begin work day tracking
  - Single button to start timer for most common/recent morning task
  - Could prompt user to select first task of the day
  - Maybe record "day start" timestamp for tracking total work hours
  - Could pair with "End My Day" button to stop all timers and generate daily summary

### Medium Priority

- [ ] **Graphical charts in reports**: Add visual representations to Daily and Weekly report tabs
  - Pie chart showing time distribution across tasks
  - Bar chart comparing time spent on different tasks
  - Timeline view showing when tasks were worked on throughout the day
  - Stacked bar chart for weekly view showing daily breakdown by task
  - Use matplotlib or similar library for chart generation
  - Make charts interactive (clickable to drill down into details)

- [ ] **Task categories/tags**: Organize tasks into categories (e.g., "Meetings", "Development", "Admin")
- [ ] **Time estimates**: Add estimated duration for tasks and compare to actual time spent
- [ ] **Monthly reports**: Add monthly summary view similar to weekly report
- [ ] **Yearly reports**: Annual overview of time tracking
- [ ] **Dark mode theme**: Add theme toggle for light/dark UI modes
- [ ] **Configurable work hours**: Set expected daily work hours and track against goals
- [ ] **Break detection**: Automatically pause timers after periods of inactivity
- [ ] **Notifications**: Alert when timer reaches certain duration or work day targets
- [ ] **System tray icon with quick actions**: Add tray icon for quick timer control
  - Right-click menu on tray icon to start/stop timers
  - Show active timers in tray menu
  - Quick access to all tasks without opening main window
  - Click tray icon to show/hide main window
  - Display running timer count in tray icon tooltip

### Low Priority

- [ ] **Backup/restore functionality**: Export and import complete database
- [ ] **Data synchronization**: Sync data across multiple devices (optional cloud integration)
- [ ] **Custom report periods**: Allow arbitrary date range selection for reports
- [ ] **Task templates**: Save frequently-used task combinations
- [ ] **Keyboard shortcuts**: More comprehensive keyboard navigation
- [ ] **Timer alarms**: Set duration limits with audio/visual alerts
- [ ] **Pomodoro mode**: Integration with Pomodoro technique (25/5 intervals)
- [ ] **Export to JSON**: Additional export format option
- [ ] **Import data**: Import time tracking data from other tools

### Technical Improvements

- [ ] **Database migrations**: Implement proper schema versioning and migrations
- [ ] **Configuration file**: User preferences stored in config file
- [ ] **Logging**: Add comprehensive logging for debugging
- [ ] **Error reporting**: Better error messages and recovery options
- [ ] **Performance optimization**: Optimize report generation for large datasets
- [ ] **Internationalization**: Support for multiple languages
- [ ] **Accessibility**: Improve screen reader support and keyboard navigation

## Completed Features

- [x] Multiple concurrent timers
- [x] Context switch tracking
- [x] Task management with colors
- [x] Daily reports
- [x] Weekly reports
- [x] CSV export
- [x] Persistent timer state
- [x] SQLite database storage
- [x] Stop all timers button
- [x] Real-time timer updates

## Notes

To contribute or suggest new features, please open an issue on GitHub.

Last updated: 2026-01-12
