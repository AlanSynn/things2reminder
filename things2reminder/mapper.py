"""
Mapper module for converting Things objects to Apple Reminders objects.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pyremindkit import Priority


class ThingsToRemindersMapper:
    """Mapper for converting Things objects to Apple Reminders objects."""

    @staticmethod
    def map_priority(things_priority: int) -> int:
        """
        Map Things priority to Apple Reminders priority.

        Args:
            things_priority: Priority value from Things (0-3)

        Returns:
            Apple Reminders priority value
        """
        # Things priority: 0 = no priority, 1 = low, 2 = medium, 3 = high
        # RemindKit Priority: NONE, LOW, MEDIUM, HIGH
        priority_map = {
            0: Priority.NONE,
            1: Priority.LOW,
            2: Priority.MEDIUM,
            3: Priority.HIGH,
        }
        return priority_map.get(things_priority, Priority.NONE)

    @staticmethod
    def parse_things_date(date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse a Things date string into a datetime object.

        Args:
            date_str: Date string from Things app

        Returns:
            Datetime object or None if no date
        """
        if not date_str:
            return None

        # Things dates are in various formats depending on the field
        # Here we're mainly concerned with deadline or when fields
        try:
            # Try common ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # Return None if parsing fails
            return None

    @staticmethod
    def get_reminder_notes_from_todo(todo: Dict[str, Any]) -> str:
        """
        Format notes from a Things todo for Reminders.

        Args:
            todo: Things todo dictionary

        Returns:
            Formatted notes string
        """
        notes_sections = []

        # Add original notes
        if todo.get('notes'):
            notes_sections.append(todo['notes'])

        # Add status information
        status = todo.get('status', 'incomplete')
        if status == 'completed':
            notes_sections.append("Status: ✓ Completed")
        elif status == 'canceled':
            notes_sections.append("Status: ✗ Canceled")

        # Add start category information
        start = todo.get('start')
        if start:
            notes_sections.append(f"Start: {start}")

        # Add deadline information
        deadline = todo.get('deadline')
        if deadline:
            date_obj = ThingsToRemindersMapper.parse_things_date(deadline)
            if date_obj:
                date_str = date_obj.strftime("%Y-%m-%d")
                notes_sections.append(f"Deadline: {date_str}")

        # Add checklist items if any
        if todo.get('checklist') and len(todo['checklist']) > 0:
            checklist_text = ["Checklist:"]
            for item in todo['checklist']:
                status = "✓" if item.get('status') == 'completed' else "☐"
                checklist_text.append(f"{status} {item.get('title', '')}")

            notes_sections.append("\n".join(checklist_text))

        # Add source reference
        notes_sections.append(f"Imported from Things - UUID: {todo.get('uuid', '')}")

        return "\n\n".join(notes_sections)

    @staticmethod
    def get_reminder_params_from_todo(todo: Dict[str, Any], calendar_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert a Things todo to parameters for creating a Reminder.

        Args:
            todo: Things todo dictionary
            calendar_id: Optional calendar ID to use

        Returns:
            Dictionary of parameters for creating a Reminder
        """
        # Extract data from todo
        title = todo.get('title', 'Untitled Task')
        notes = ThingsToRemindersMapper.get_reminder_notes_from_todo(todo)

        # Map dates
        due_date = None
        if todo.get('deadline'):
            due_date = ThingsToRemindersMapper.parse_things_date(todo.get('deadline'))
        elif todo.get('when'):
            due_date = ThingsToRemindersMapper.parse_things_date(todo.get('when'))

        # Map priority
        priority = ThingsToRemindersMapper.map_priority(todo.get('priority', 0))

        # Extract tags if present
        tags = []
        if todo.get('tags'):
            tags = [tag_id for tag_id in todo.get('tags', [])]

        params = {
            'title': title,
            'notes': notes,
            'due_date': due_date,
            'priority': priority,
            'calendar_id': calendar_id,
            'tags': tags,
        }

        # 1. Mark completed tasks as completed in Reminders
        if todo.get('status') == 'completed':
            params['completed'] = True
            params['completion_date'] = todo.get('stop_date')  # Use original completion date if available

        # 2. Set early reminder and flag for Anytime tasks with deadlines
        if todo.get('deadline') and todo.get('start') == 'Anytime':
            # Add early reminder (1 day before deadline)
            if due_date:
                early_reminder_date = due_date - timedelta(days=1)
                params['early_reminder_date'] = early_reminder_date
                # Mark as flagged
                params['flagged'] = True

        return params