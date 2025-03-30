"""
Client module for interacting with the Things app.
"""
from typing import Dict, List, Optional, Any, Union
import logging
import things


class ThingsClient:
    """Client for accessing Things app data."""

    def __init__(self):
        """Initialize the ThingsClient."""
        self.logger = logging.getLogger(__name__)

    def get_areas(self, include_items: bool = False) -> List[Dict[str, Any]]:
        """
        Get all areas from Things.

        Args:
            include_items: Whether to include tasks and projects in each area

        Returns:
            List of area dictionaries
        """
        return things.areas(include_items=include_items)

    def get_area(self, uuid: str, include_items: bool = False) -> Dict[str, Any]:
        """
        Get a specific area by UUID.

        Args:
            uuid: UUID of the area to retrieve
            include_items: Whether to include tasks and projects in the area

        Returns:
            Dictionary containing area information
        """
        return things.areas(uuid=uuid, include_items=include_items)

    def get_projects(self, area_uuid: Optional[str] = None,
                    include_items: bool = False,
                    status: Optional[str] = 'incomplete') -> List[Dict[str, Any]]:
        """
        Get projects from Things, optionally filtered by area.

        Args:
            area_uuid: UUID of area to filter by
            include_items: Whether to include items contained within projects
            status: Filter by status ('incomplete', 'completed', 'canceled', or None for all)

        Returns:
            List of project dictionaries
        """
        if area_uuid:
            return things.projects(area=area_uuid, include_items=include_items, status=status)
        return things.projects(include_items=include_items, status=status)

    def get_project(self, uuid: str, include_items: bool = False) -> Dict[str, Any]:
        """
        Get a specific project by UUID.

        Args:
            uuid: UUID of the project to retrieve
            include_items: Whether to include items contained within the project

        Returns:
            Dictionary containing project information
        """
        return things.projects(uuid=uuid, include_items=include_items)

    def get_todos(self, project_uuid: Optional[str] = None,
                 area_uuid: Optional[str] = None,
                 status: str = 'incomplete',
                 include_items: bool = True,
                 tag: Optional[Union[str, bool]] = None) -> List[Dict[str, Any]]:
        """
        Get todos from Things, with various filtering options.

        Args:
            project_uuid: UUID of project to filter by
            area_uuid: UUID of area to filter by
            status: Filter by status ('incomplete', 'completed', 'canceled', or None for all)
            include_items: Whether to include checklist items
            tag: Filter by tag name or presence of tags

        Returns:
            List of todo dictionaries
        """
        kwargs = {
            'status': status,
            'include_items': include_items
        }

        if project_uuid:
            kwargs['project'] = project_uuid
        if area_uuid:
            kwargs['area'] = area_uuid
        if tag is not None:
            kwargs['tag'] = tag

        return things.todos(**kwargs)

    def get_todo(self, uuid: str, include_items: bool = True) -> Dict[str, Any]:
        """
        Get a specific todo by UUID.

        Args:
            uuid: UUID of the todo to retrieve
            include_items: Whether to include checklist items

        Returns:
            Dictionary containing todo information
        """
        return things.todos(uuid=uuid, include_items=include_items)

    def get_tags(self, include_items: bool = False) -> List[Dict[str, Any]]:
        """
        Get all tags from Things.

        Args:
            include_items: Whether to include items tagged with each tag

        Returns:
            List of tag dictionaries
        """
        return things.tags(include_items=include_items)

    def get_tag(self, title: str, include_items: bool = False) -> Dict[str, Any]:
        """
        Get a specific tag by title.

        Args:
            title: Title of the tag to retrieve
            include_items: Whether to include items tagged with the tag

        Returns:
            Dictionary containing tag information
        """
        return things.tags(title=title, include_items=include_items)

    def get_tag_names_by_ids(self, tag_uuids: List[str]) -> List[str]:
        """
        Get tag names from their UUIDs.

        Args:
            tag_uuids: List of tag UUIDs

        Returns:
            List of tag names
        """
        all_tags = {tag['uuid']: tag['title'] for tag in self.get_tags()}
        return [all_tags.get(uuid, '') for uuid in tag_uuids if uuid in all_tags]

    def get_deadlines(self, status: str = 'incomplete') -> List[Dict[str, Any]]:
        """
        Get all tasks with deadlines.

        Args:
            status: Filter by status ('incomplete', 'completed', 'canceled', or None for all)

        Returns:
            List of tasks with deadlines
        """
        return things.deadlines(status=status)

    def get_inbox_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks in the Inbox.

        Returns:
            List of inbox tasks
        """
        return things.inbox()

    def get_today_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks in Today.

        Returns:
            List of today's tasks
        """
        return things.today()

    def get_upcoming_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks in Upcoming.

        Returns:
            List of upcoming tasks
        """
        return things.upcoming()

    def get_anytime_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks in Anytime.

        Returns:
            List of anytime tasks
        """
        return things.anytime()

    def get_someday_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks in Someday.

        Returns:
            List of someday tasks
        """
        return things.someday()

    def get_completed_tasks(self, last: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all completed tasks.

        Args:
            last: Limit to tasks completed within a time period (e.g., '7d', '1w', '3m')

        Returns:
            List of completed tasks
        """
        kwargs = {'status': 'completed'}
        if last:
            kwargs['last'] = last
        return things.tasks(**kwargs)

    def get_canceled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all canceled tasks.

        Returns:
            List of canceled tasks
        """
        return things.canceled()

    def get_logbook_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks in the Logbook.

        Returns:
            List of logbook tasks
        """
        return things.logbook()

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for tasks matching a query.

        Args:
            query: Search query string

        Returns:
            List of matching tasks
        """
        return things.search(query)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks from Things without any filtering.

        This method retrieves all tasks regardless of their start, area, status,
        project, heading, tag, or trashed status.

        Returns:
            List of all task dictionaries
        """
        return things.tasks(
            start=None,
            area=None,
            status=None,
            project=None,
            heading=None,
            tag=None,
            trashed=None,
            context_trashed=None,
            include_items=True
        )