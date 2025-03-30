"""
Tests for the RemindersClient module.
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from pyremindkit import Priority
from src.things2reminder.reminders_client import RemindersClient


class TestRemindersClient(unittest.TestCase):
    """Test cases for RemindersClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_remind_kit = MagicMock()
        self.mock_calendars = MagicMock()
        self.mock_remind_kit.calendars = self.mock_calendars

        # Mock default calendar
        self.mock_default_calendar = MagicMock()
        self.mock_default_calendar.id = "default-cal-id"
        self.mock_default_calendar.name = "Default"
        self.mock_calendars.get_default.return_value = self.mock_default_calendar

        with patch('src.things2reminder.reminders_client.RemindKit', return_value=self.mock_remind_kit):
            self.client = RemindersClient()

    def test_get_calendars(self):
        """Test getting calendars returns the default calendar."""
        calendars = self.client.get_calendars()
        self.assertEqual(len(calendars), 1)
        self.assertEqual(calendars[0].id, "default-cal-id")
        self.mock_calendars.get_default.assert_called_once()

    def test_find_or_create_calendar_finds_default(self):
        """Test finding a calendar returns the default calendar."""
        with self.assertLogs(level='WARNING') as cm:
            calendar = self.client.find_or_create_calendar("Test Calendar")

        self.assertEqual(calendar.id, "default-cal-id")
        self.assertEqual(calendar.name, "Default")
        self.assertIn("Calendar 'Test Calendar' requested but pyremindkit cannot create calendars", cm.output[0])
        self.mock_calendars.get_default.assert_called()

    def test_create_reminder(self):
        """Test creating a reminder."""
        test_datetime = datetime.now()
        title = "Test Reminder"
        notes = "Test Notes"
        due_date = test_datetime
        priority = 1
        calendar_id = "default-cal-id"

        self.client.create_reminder(
            title=title,
            notes=notes,
            due_date=due_date,
            priority=priority,
            calendar_id=calendar_id
        )

        self.mock_remind_kit.create_reminder.assert_called_once_with(
            title=title,
            notes=notes,
            due_date=due_date,
            priority=priority,
            calendar_id=calendar_id
        )

    def test_create_reminder_with_tags(self):
        """Test creating a reminder with tags."""
        test_datetime = datetime.now()
        title = "Test Reminder"
        notes = "Test Notes"
        due_date = test_datetime
        priority = 1
        calendar_id = "default-cal-id"
        tags = ["tag1", "tag2"]

        self.client.create_reminder(
            title=title,
            notes=notes,
            due_date=due_date,
            priority=priority,
            calendar_id=calendar_id,
            tags=tags
        )

        # Tags should be added to notes
        expected_notes = "Test Notes\n\nTags: #tag1 #tag2"
        self.mock_remind_kit.create_reminder.assert_called_once_with(
            title=title,
            notes=expected_notes,
            due_date=due_date,
            priority=priority,
            calendar_id=calendar_id
        )


if __name__ == '__main__':
    unittest.main()