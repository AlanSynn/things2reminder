"""
Tests for the ThingsToRemindersMapper module.
"""
import unittest
from datetime import datetime
from pyremindkit import Priority
from src.things2reminder.mapper import ThingsToRemindersMapper


class TestThingsToRemindersMapper(unittest.TestCase):
    """Test cases for ThingsToRemindersMapper class."""

    def test_map_priority(self):
        """Test the map_priority method."""
        mapper = ThingsToRemindersMapper()

        # Test mapping of different priority levels
        self.assertEqual(Priority.NONE, mapper.map_priority(0))
        self.assertEqual(Priority.LOW, mapper.map_priority(1))
        self.assertEqual(Priority.MEDIUM, mapper.map_priority(2))
        self.assertEqual(Priority.HIGH, mapper.map_priority(3))

        # Test with invalid priority
        self.assertEqual(Priority.NONE, mapper.map_priority(999))
        self.assertEqual(Priority.NONE, mapper.map_priority(None))

    def test_parse_things_date(self):
        """Test the parse_things_date method."""
        mapper = ThingsToRemindersMapper()

        # Test with valid ISO date string
        iso_date = "2023-10-15T14:30:00Z"
        parsed_date = mapper.parse_things_date(iso_date)
        self.assertIsInstance(parsed_date, datetime)
        self.assertEqual(2023, parsed_date.year)
        self.assertEqual(10, parsed_date.month)
        self.assertEqual(15, parsed_date.day)
        self.assertEqual(14, parsed_date.hour)
        self.assertEqual(30, parsed_date.minute)

        # Test with None or invalid date
        self.assertIsNone(mapper.parse_things_date(None))
        self.assertIsNone(mapper.parse_things_date("not a date"))

    def test_get_reminder_notes_from_todo(self):
        """Test the get_reminder_notes_from_todo method."""
        mapper = ThingsToRemindersMapper()

        # Test with only notes
        todo_with_notes = {
            'uuid': 'todo1',
            'notes': 'This is a note'
        }
        notes = mapper.get_reminder_notes_from_todo(todo_with_notes)
        self.assertIn('This is a note', notes)
        self.assertIn('Imported from Things', notes)
        self.assertIn('todo1', notes)

        # Test with notes and checklist
        todo_with_checklist = {
            'uuid': 'todo2',
            'notes': 'Todo with checklist',
            'checklist': [
                {'title': 'Item 1', 'status': 'completed'},
                {'title': 'Item 2', 'status': 'incomplete'}
            ]
        }

        notes_with_checklist = mapper.get_reminder_notes_from_todo(todo_with_checklist)
        self.assertIn('Todo with checklist', notes_with_checklist)
        self.assertIn('Checklist:', notes_with_checklist)
        self.assertIn('✓ Item 1', notes_with_checklist)
        self.assertIn('☐ Item 2', notes_with_checklist)

        # Test with no notes or checklist
        todo_empty = {
            'uuid': 'todo3'
        }
        notes_empty = mapper.get_reminder_notes_from_todo(todo_empty)
        self.assertIn('Imported from Things', notes_empty)
        self.assertIn('todo3', notes_empty)

    def test_get_reminder_params_from_todo(self):
        """Test the get_reminder_params_from_todo method."""
        mapper = ThingsToRemindersMapper()

        # Create a test todo with all fields
        todo = {
            'uuid': 'todo1',
            'title': 'Test Todo',
            'notes': 'Sample notes',
            'deadline': '2023-10-15T14:30:00Z',
            'priority': 3,  # High priority
            'tags': ['tag1', 'tag2']
        }

        # Test with calendar ID
        params = mapper.get_reminder_params_from_todo(todo, 'cal123')

        self.assertEqual('Test Todo', params['title'])
        self.assertIn('Sample notes', params['notes'])
        self.assertEqual(Priority.HIGH, params['priority'])
        self.assertEqual('cal123', params['calendar_id'])
        self.assertEqual(['tag1', 'tag2'], params['tags'])

        # Verify date was parsed correctly
        self.assertIsInstance(params['due_date'], datetime)
        self.assertEqual(2023, params['due_date'].year)
        self.assertEqual(10, params['due_date'].month)
        self.assertEqual(15, params['due_date'].day)

        # Test with minimal todo
        minimal_todo = {
            'uuid': 'todo2',
            'title': 'Minimal Todo'
        }

        minimal_params = mapper.get_reminder_params_from_todo(minimal_todo)

        self.assertEqual('Minimal Todo', minimal_params['title'])
        self.assertIsNone(minimal_params['due_date'])
        self.assertEqual(Priority.NONE, minimal_params['priority'])
        self.assertEqual([], minimal_params['tags'])


if __name__ == '__main__':
    unittest.main()