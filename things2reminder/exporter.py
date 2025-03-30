"""
Exporter module for transferring data from Things to Apple Reminders.
"""
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Set
import logging
from .things_client import ThingsClient
from .reminders_client import RemindersClient
from .mapper import ThingsToRemindersMapper


class ThingsToRemindersExporter:
    """
    Exporter class for transferring Things todos to Apple Reminders.

    This class handles the export process, transferring Things todos to Apple Reminders
    while preserving as much information as possible.

    Note:
        Due to limitations in the pyremindkit API, all reminders will be created
        in the default Reminders calendar. Information about Things areas and
        projects will be included in the reminder notes.
    """

    def __init__(self, things_client: Optional[ThingsClient] = None,
                 reminders_client: Optional[RemindersClient] = None):
        """
        Initialize the exporter with clients.

        Args:
            things_client: Client for interacting with Things app
            reminders_client: Client for interacting with Apple Reminders
        """
        self.things = things_client or ThingsClient()
        self.reminders = reminders_client or RemindersClient()
        self.logger = logging.getLogger(__name__)
        self.mapper = ThingsToRemindersMapper()

        # Cache for mapping between Things UUIDs and metadata
        self._area_map: Dict[str, Dict[str, Any]] = {}
        self._project_map: Dict[str, Dict[str, Any]] = {}
        self._tag_map: Dict[str, str] = {}

        # Default calendar to use
        self._default_calendar = None

    def process_areas(self) -> Dict[str, Dict[str, Any]]:
        """
        Process and cache all Things areas.

        This doesn't create separate calendars but stores the area information
        to be included in reminder notes.

        Returns:
            Dictionary mapping Things area UUIDs to area data
        """
        areas = self.things.get_areas()
        self.logger.info(f"Processing {len(areas)} areas from Things")

        for area in areas:
            area_uuid = area.get('uuid')
            # Store area information for reference
            self._area_map[area_uuid] = area

        return self._area_map

    def process_projects(self) -> Dict[str, Dict[str, Any]]:
        """
        Process and cache all Things projects.

        This doesn't create separate calendars but stores the project information
        to be included in reminder notes.

        Returns:
            Dictionary mapping Things project UUIDs to project data
        """
        projects = self.things.get_projects()
        self.logger.info(f"Processing {len(projects)} projects from Things")

        for project in projects:
            project_uuid = project.get('uuid')
            # Store project information for reference
            self._project_map[project_uuid] = project

        return self._project_map

    def process_tags(self) -> Dict[str, str]:
        """
        Process all Things tags for reference.

        Returns:
            Dictionary mapping Things tag UUIDs to tag titles
        """
        tags = self.things.get_tags()
        self.logger.info(f"Processing {len(tags)} tags from Things")

        for tag in tags:
            tag_uuid = tag.get('uuid')
            tag_title = tag.get('title', 'Unnamed Tag')
            self._tag_map[tag_uuid] = tag_title

        return self._tag_map

    def _get_default_calendar(self):
        """Get and cache the default calendar."""
        if not self._default_calendar:
            self._default_calendar = self.reminders.get_default_calendar()
        return self._default_calendar

    def export_todos(self, todos_list: Optional[List[Dict[str, Any]]] = None) -> List[Any]:
        """
        Export a list of Things todos to Apple Reminders.

        Args:
            todos_list: Optional list of todos to export. If None, all active todos will be exported.

        Returns:
            List of created reminders
        """
        if todos_list is None:
            todos = self.things.get_todos()
        else:
            todos = todos_list

        self.logger.info(f"Exporting {len(todos)} todos to Reminders")

        created_reminders = []
        default_calendar = self._get_default_calendar()

        # Get all calendars once
        calendars = self.reminders.list_calendars()
        calendar_dict = {}
        for calendar in calendars:
            calendar_dict[calendar.name.lower()] = calendar.id

        # Process todos in batches of 100
        batch_size = 300
        for i in range(0, len(todos), batch_size):
            batch_todos = todos[i:i+batch_size]
            self.logger.info(f"Processing batch of {len(batch_todos)} todos (batch {i // batch_size + 1})")

            # Prepare batch LLM request
            batch_prompts = []
            for j, todo in enumerate(batch_todos):
                todo_title = todo.get('title', 'Unnamed Todo')
                batch_prompts.append(f"{j}: pick the best calendar for this todo: {todo_title}")

            batch_prompt = "\n".join(batch_prompts)
            llm_system_prompt = f"You are a helpful assistant to make a todo list. For each numbered todo, reply with ONLY the calendar name (like 'personal' or 'work') that best fits. Format your response as 'number: calendar_name' for each todo, one per line.\n\nAvailable calendars: {list(calendar_dict.keys())}"
            llm_prompt = f"{batch_prompt}"

            # Execute batch LLM command
            calendar_names_result = subprocess.run(
                ["llm", "-s", llm_system_prompt, llm_prompt],
                capture_output=True, text=True
            )

            # Execute auto tagging with llm
            # llm_tagging_system_prompt = f"You are a helpful assistant to make a todo list. For each numbered todo, reply with ONLY the tags that best fits, USE ENGLISH, USE 2 or more tags, limit to 5 tags for each todo. Format your response as 'number: tag_name' for each todo, one per line. The tag should be in English. And something like 'publication', 'project', 'shopping', 'work', 'personal', 'family', are good tags. DO NOT include any other text. AVOID using 'tag' 'other' 'unassigned' as a tag."
            # llm_tagging_prompt = f"{batch_prompt}"

            # llm_tagging_result = subprocess.run(
            #     ["llm", "-s", llm_tagging_system_prompt, llm_tagging_prompt],
            #     capture_output=True, text=True
            # )

            # Parse batch results
            calendar_assignments = {}
            for line in calendar_names_result.stdout.strip().split('\n'):
                if ':' in line:
                    try:
                        index_str, calendar_name = line.split(':', 1)
                        index = int(index_str.strip())
                        calendar_name = calendar_name.strip().lower()
                        if calendar_name in calendar_dict:
                            calendar_assignments[index] = calendar_name
                    except (ValueError, IndexError):
                        self.logger.warning(f"Could not parse LLM response line: {line}")

            # Parse auto tagging results
            tag_assignments = {}
            for line in llm_tagging_result.stdout.strip().split('\n'):
                if ':' in line:
                    try:
                        index_str, tag_name = line.split(':', 1)
                        index = int(index_str.strip())
                        tag_name = tag_name.strip().lower().split(',')
                        tag_assignments[index] = tag_name
                    except (ValueError, IndexError):
                        self.logger.warning(f"Could not parse LLM response line: {line}")

            # Process each todo in the batch with its assigned calendar
            for j, todo in enumerate(batch_todos):
                todo_uuid = todo.get('uuid')
                todo_title = todo.get('title', 'Unnamed Todo')
                project_uuid = todo.get('project')
                area_uuid = todo.get('area')

                # Collect context information to include in reminder
                context_info = []

                # Get assigned calendar or use default
                calendar_name_lower = calendar_assignments.get(j, list(calendar_dict.keys())[0])
                calendar_id = calendar_dict.get(calendar_name_lower, default_calendar.id)

                # Get assigned tags
                # tag_names_list = tag_assignments.get(j, [])


                # Add project information if available
                if project_uuid and project_uuid in self._project_map:
                    project = self._project_map[project_uuid]
                    project_name = project.get('title', 'Unnamed Project')
                    context_info.append(f"Project: {project_name}")

                # Add area information if available
                if area_uuid and area_uuid in self._area_map:
                    area = self._area_map[area_uuid]
                    area_name = area.get('title', 'Unnamed Area')
                    context_info.append(f"Area: {area_name}")

                # Get tag names if present
                tag_names = []
                if todo.get('tags'):
                    tag_names = tag_assignments.get(j, [])

                # Map the todo to reminder parameters and add context
                params = self.mapper.get_reminder_params_from_todo(todo, default_calendar.id)

                # Add context information to notes
                if context_info:
                    context_str = "\n".join(context_info)
                    if params.get('notes'):
                        params['notes'] = f"{params['notes']}\n\n{context_str}"
                    else:
                        params['notes'] = context_str

                params['tags'] = tag_names
                params['calendar_id'] = calendar_id

                # Create the reminder
                try:
                    self.logger.info(f"Creating reminder for todo: {todo_title}")
                    reminder = self.reminders.create_reminder(**params)
                    created_reminders.append(reminder)
                except Exception as e:
                    self.logger.error(f"Error creating reminder for todo {todo_uuid}: {str(e)}")

        return created_reminders

    def export_all(self) -> Tuple[int, int, int, int]:
        """
        Export all Things data to Apple Reminders.

        Returns:
            Tuple containing counts of (areas, projects, tags, todos) exported
        """
        # First process metadata
        areas = self.process_areas()
        projects = self.process_projects()
        tags = self.process_tags()

        # Then export todos
        todos = self.export_todos()

        return len(areas), len(projects), len(tags), len(todos)

    def export_with_options(self,
                           include_completed: bool = False,
                           include_canceled: bool = False,
                           only_with_deadlines: bool = False,
                           only_today: bool = False,
                           only_inbox: bool = False,
                           only_upcoming: bool = False,
                           only_someday: bool = False,
                           completed_last: Optional[str] = None,
                           filter_tag: Optional[str] = None) -> Tuple[int, int, int, int]:
        """
        Export Things data to Apple Reminders with various filtering options.

        Args:
            include_completed: Whether to include completed tasks
            include_canceled: Whether to include canceled tasks
            only_with_deadlines: Whether to only export tasks with deadlines
            only_today: Whether to only export tasks in Today view
            only_inbox: Whether to only export tasks in Inbox
            only_upcoming: Whether to only export tasks in Upcoming view
            only_someday: Whether to only export tasks in Someday view
            completed_last: Period for completed tasks (e.g. "7d", "2w", "1m")
            filter_tag: Tag to filter by

        Returns:
            Tuple containing counts of (areas, projects, tags, todos) exported
        """
        # First process metadata
        areas = self.process_areas()
        projects = self.process_projects()
        tags = self.process_tags()

        # Collect all todos to export based on options
        todos_to_export = []
        todo_uuids: Set[str] = set()  # To track which todos we've already added

        # Helper to add todos if they aren't already in the list
        def add_todos(todo_list: List[Dict[str, Any]]) -> None:
            for todo in todo_list:
                uuid = todo.get('uuid')
                if uuid and uuid not in todo_uuids:
                    todos_to_export.append(todo)
                    todo_uuids.add(uuid)

        # Add todos based on the specified options
        if only_today:
            self.logger.info("Adding todos from Today view")
            add_todos(self.things.get_today_tasks())

        if only_inbox:
            self.logger.info("Adding todos from Inbox")
            add_todos(self.things.get_inbox_tasks())

        if only_upcoming:
            self.logger.info("Adding todos from Upcoming view")
            add_todos(self.things.get_upcoming_tasks())

        if only_someday:
            self.logger.info("Adding todos from Someday view")
            add_todos(self.things.get_someday_tasks())

        if only_with_deadlines:
            self.logger.info("Adding todos with deadlines")
            add_todos(self.things.get_deadlines())

        # If no specific view is selected, get all active todos
        if not (only_today or only_inbox or only_upcoming or
                only_someday or only_with_deadlines):
            self.logger.info("Adding all active incomplete todos")
            add_todos(self.things.get_todos())

        # Apply tag filter if specified
        if filter_tag:
            self.logger.info(f"Filtering todos by tag: {filter_tag}")
            filtered_todos = []
            for todo in todos_to_export:
                tag_uuids = todo.get('tags', [])
                tag_names = [self._tag_map.get(tag_uuid, '')
                             for tag_uuid in tag_uuids
                             if tag_uuid in self._tag_map]
                if filter_tag in tag_names:
                    filtered_todos.append(todo)
            todos_to_export = filtered_todos

        # Add completed tasks if requested
        if include_completed:
            if completed_last:
                self.logger.info(f"Adding completed todos from last {completed_last}")
                add_todos(self.things.get_completed_tasks(last=completed_last))
            else:
                self.logger.info("Adding all completed todos")
                add_todos(self.things.get_completed_tasks())

        # Add canceled tasks if requested
        if include_canceled:
            self.logger.info("Adding canceled todos")
            add_todos(self.things.get_canceled_tasks())

        # Export the collected todos
        self.logger.info(f"Exporting {len(todos_to_export)} todos with custom filters")
        todos = self.export_todos(todos_to_export)

        return len(areas), len(projects), len(tags), len(todos)

    def export_all_tasks(self) -> Tuple[int, int, int, int]:
        """
        Export absolutely all tasks from Things without any filtering.

        This method exports all tasks regardless of their status,
        including trashed items, completed items, and items from all areas.

        Returns:
            Tuple containing counts of (areas, projects, tags, todos) exported
        """
        # First process metadata
        areas = self.process_areas()
        projects = self.process_projects()
        tags = self.process_tags()

        # Get all tasks without any filtering
        self.logger.info("Retrieving all tasks from Things without any filtering")
        all_tasks = self.things.get_all_tasks()

        # Export all tasks
        self.logger.info(f"Exporting {len(all_tasks)} tasks (including all statuses and trashed items)")
        todos = self.export_todos(all_tasks)

        return len(areas), len(projects), len(tags), len(todos)