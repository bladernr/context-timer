"""Export utilities for Context Timer application."""
import csv
from datetime import datetime, timezone
from typing import List, Dict, Any
from pathlib import Path


def export_sessions_to_csv(sessions: List[Dict[str, Any]], output_path: str):
    """Export timer sessions to CSV file.
    
    Args:
        sessions: List of session dictionaries with keys:
                  task_name, start_time, end_time, duration_seconds, duration_formatted
        output_path: Path to output CSV file
    """
    if not sessions:
        # Create empty file with headers
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Task Name', 'Start Time', 'End Time', 'Duration (seconds)', 'Duration (HH:MM:SS)'])
        return
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['task_name', 'start_time', 'end_time', 'duration_seconds', 'duration_formatted']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header with friendly names
        writer.writerow({
            'task_name': 'Task Name',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'duration_seconds': 'Duration (seconds)',
            'duration_formatted': 'Duration (HH:MM:SS)'
        })
        
        writer.writerows(sessions)


def export_daily_report_to_csv(report_data: Dict[str, Any], output_path: str):
    """Export daily report to CSV file.
    
    Args:
        report_data: Dictionary containing report data
        output_path: Path to output CSV file
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['Context Timer - Daily Report'])
        writer.writerow([f"Date: {report_data.get('date', '')}"])
        writer.writerow([])
        
        # Summary
        writer.writerow(['Summary'])
        writer.writerow(['Total Tasks Worked On', report_data.get('total_tasks', 0)])
        writer.writerow(['Total Context Switches', report_data.get('total_switches', 0)])
        writer.writerow(['Total Time Worked', report_data.get('total_time_formatted', '00:00:00')])
        writer.writerow([])
        
        # Task breakdown
        writer.writerow(['Task', 'Time Spent', 'Sessions'])
        for task in report_data.get('tasks', []):
            writer.writerow([
                task['name'],
                task['duration_formatted'],
                task['session_count']
            ])


def export_weekly_report_to_csv(report_data: Dict[str, Any], output_path: str):
    """Export weekly report to CSV file.
    
    Args:
        report_data: Dictionary containing report data
        output_path: Path to output CSV file
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['Context Timer - Weekly Report'])
        writer.writerow([f"Week: {report_data.get('week_start', '')} - {report_data.get('week_end', '')}"])
        writer.writerow([])
        
        # Daily breakdown
        writer.writerow(['Date', 'Total Time', 'Context Switches', 'Tasks Worked'])
        for day in report_data.get('days', []):
            writer.writerow([
                day['date'],
                day['total_time_formatted'],
                day['context_switches'],
                day['task_count']
            ])
        
        writer.writerow([])
        
        # Weekly summary
        writer.writerow(['Weekly Summary'])
        writer.writerow(['Total Time Worked', report_data.get('total_time_formatted', '00:00:00')])
        writer.writerow(['Total Context Switches', report_data.get('total_switches', 0)])
        writer.writerow(['Average Daily Time', report_data.get('average_daily_time', '00:00:00')])


def get_default_export_path() -> Path:
    """Get default export directory path.
    
    Returns:
        Path to exports directory
    """
    export_dir = Path.home() / "Documents" / "context-timer-exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def generate_export_filename(report_type: str, date_str: str = None) -> str:
    """Generate filename for export.
    
    Args:
        report_type: Type of report ('sessions', 'daily', 'weekly')
        date_str: Optional date string to include in filename
        
    Returns:
        Generated filename
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    
    timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
    return f"context-timer-{report_type}-{date_str}-{timestamp}.csv"
