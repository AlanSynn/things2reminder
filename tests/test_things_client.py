"""
Tests for the ThingsClient module.
"""
import unittest
from unittest.mock import patch
from src.things2reminder.things_client import ThingsClient


class TestThingsClient(unittest.TestCase):
    """Test cases for ThingsClient class."""

    @patch('things.areas')
    def test_get_areas(self, mock_areas):
        """Test the get_areas method."""
        # Set up mock return value
        mock_areas.return_value = [
            {'uuid': 'area1', 'title': 'Area 1'},
            {'uuid': 'area2', 'title': 'Area 2'}
        ]

        # Create client and call method
        client = ThingsClient()
        areas = client.get_areas()

        # Verify the result
        self.assertEqual(2, len(areas))
        self.assertEqual('Area 1', areas[0]['title'])
        self.assertEqual('Area 2', areas[1]['title'])

        # Verify the method was called
        mock_areas.assert_called_once_with(include_items=False)

    @patch('things.areas')
    def test_get_area(self, mock_areas):
        """Test the get_area method."""
        # Set up mock return value
        mock_areas.return_value = {'uuid': 'area1', 'title': 'Area 1'}

        # Create client and call method
        client = ThingsClient()
        area = client.get_area('area1')

        # Verify the result
        self.assertEqual('Area 1', area['title'])

        # Verify the method was called
        mock_areas.assert_called_once_with(uuid='area1', include_items=False)

    @patch('things.projects')
    def test_get_projects(self, mock_projects):
        """Test the get_projects method."""
        # Set up mock return value
        mock_projects.return_value = [
            {'uuid': 'proj1', 'title': 'Project 1', 'area': 'area1'},
            {'uuid': 'proj2', 'title': 'Project 2', 'area': 'area2'},
            {'uuid': 'proj3', 'title': 'Project 3', 'area': 'area1'}
        ]

        # Create client and call method
        client = ThingsClient()
        projects = client.get_projects()

        # Verify the result - should get all projects
        self.assertEqual(3, len(projects))
        mock_projects.assert_called_with(include_items=False, status='incomplete')

        # Test filtering by area
        mock_projects.return_value = [
            {'uuid': 'proj1', 'title': 'Project 1', 'area': 'area1'},
            {'uuid': 'proj3', 'title': 'Project 3', 'area': 'area1'}
        ]
        area1_projects = client.get_projects(area_uuid='area1')
        self.assertEqual(2, len(area1_projects))
        mock_projects.assert_called_with(area='area1', include_items=False, status='incomplete')

    @patch('things.projects')
    def test_get_project(self, mock_projects):
        """Test the get_project method."""
        # Set up mock return value
        mock_projects.return_value = {'uuid': 'proj1', 'title': 'Project 1', 'area': 'area1'}

        # Create client and call method
        client = ThingsClient()
        project = client.get_project('proj1')

        # Verify the result
        self.assertEqual('Project 1', project['title'])

        # Verify the method was called
        mock_projects.assert_called_once_with(uuid='proj1', include_items=False)

    @patch('things.todos')
    def test_get_todos(self, mock_todos):
        """Test the get_todos method."""
        # Set up mock return value
        mock_todos.return_value = [
            {'uuid': 'todo1', 'title': 'Todo 1', 'project': 'proj1'},
            {'uuid': 'todo2', 'title': 'Todo 2', 'project': 'proj2'},
            {'uuid': 'todo3', 'title': 'Todo 3', 'project': 'proj1'}
        ]

        # Create client and call method
        client = ThingsClient()
        todos = client.get_todos()

        # Verify the result - should get all todos
        self.assertEqual(3, len(todos))
        mock_todos.assert_called_with(status='incomplete', include_items=True)

        # Test filtering by project
        mock_todos.return_value = [
            {'uuid': 'todo1', 'title': 'Todo 1', 'project': 'proj1'},
            {'uuid': 'todo3', 'title': 'Todo 3', 'project': 'proj1'}
        ]
        proj1_todos = client.get_todos(project_uuid='proj1')
        self.assertEqual(2, len(proj1_todos))
        mock_todos.assert_called_with(project='proj1', status='incomplete', include_items=True)

    @patch('things.todos')
    def test_get_todo(self, mock_todos):
        """Test the get_todo method."""
        # Set up mock return value
        mock_todos.return_value = {'uuid': 'todo1', 'title': 'Todo 1', 'project': 'proj1'}

        # Create client and call method
        client = ThingsClient()
        todo = client.get_todo('todo1')

        # Verify the result
        self.assertEqual('Todo 1', todo['title'])

        # Verify the method was called
        mock_todos.assert_called_once_with(uuid='todo1', include_items=True)

    @patch('things.tags')
    def test_get_tags(self, mock_tags):
        """Test the get_tags method."""
        # Set up mock return value
        mock_tags.return_value = [
            {'uuid': 'tag1', 'title': 'Tag 1'},
            {'uuid': 'tag2', 'title': 'Tag 2'}
        ]

        # Create client and call method
        client = ThingsClient()
        tags = client.get_tags()

        # Verify the result
        self.assertEqual(2, len(tags))
        self.assertEqual('Tag 1', tags[0]['title'])
        self.assertEqual('Tag 2', tags[1]['title'])

        # Verify the method was called
        mock_tags.assert_called_once_with(include_items=False)

    @patch('things.tags')
    def test_get_tag(self, mock_tags):
        """Test the get_tag method."""
        # Set up mock return value
        mock_tags.return_value = {'uuid': 'tag1', 'title': 'Tag 1'}

        # Create client and call method
        client = ThingsClient()
        tag = client.get_tag('Tag 1')

        # Verify the result
        self.assertEqual('Tag 1', tag['title'])

        # Verify the method was called
        mock_tags.assert_called_once_with(title='Tag 1', include_items=False)

    @patch('things.tags')
    def test_get_tag_names_by_ids(self, mock_tags):
        """Test the get_tag_names_by_ids method."""
        # Set up mock return value
        mock_tags.return_value = [
            {'uuid': 'tag1', 'title': 'Tag 1'},
            {'uuid': 'tag2', 'title': 'Tag 2'},
            {'uuid': 'tag3', 'title': 'Tag 3'}
        ]

        # Create client and call method
        client = ThingsClient()
        tag_names = client.get_tag_names_by_ids(['tag1', 'tag3'])

        # Verify the result
        self.assertEqual(2, len(tag_names))
        self.assertEqual('Tag 1', tag_names[0])
        self.assertEqual('Tag 3', tag_names[1])

        # Verify the method was called
        mock_tags.assert_called_once_with(include_items=False)

    @patch('things.deadlines')
    def test_get_deadlines(self, mock_deadlines):
        """Test the get_deadlines method."""
        # Set up mock return value
        mock_deadlines.return_value = [
            {'uuid': 'todo1', 'title': 'Todo 1', 'deadline': '2025-01-01'},
            {'uuid': 'todo2', 'title': 'Todo 2', 'deadline': '2025-02-01'}
        ]

        # Create client and call method
        client = ThingsClient()
        deadlines = client.get_deadlines()

        # Verify the result
        self.assertEqual(2, len(deadlines))
        self.assertEqual('Todo 1', deadlines[0]['title'])

        # Verify the method was called
        mock_deadlines.assert_called_once_with(status='incomplete')


if __name__ == '__main__':
    unittest.main()