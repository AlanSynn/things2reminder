"""
Client module for interacting with Apple Reminders.
"""
from typing import Dict, List, Optional, Any
import logging
import sys
from datetime import datetime
from reminders import RemindKit, Priority



class RemindersClient:
    """Client for accessing and modifying Apple Reminders."""

    def __init__(self):
        """Initialize the RemindKit client."""
        self.remind = RemindKit()
        self.logger = logging.getLogger(__name__)

    def list_calendars(self) -> List[Any]:
        """
        List all calendars.
        """
        return list(self.remind.calendars.list())

    def get_calendars(self) -> List[Any]:
        """
        Get available reminder calendars.

        Note: Due to limitations in pyremindkit, this only returns the default calendar.
        The API doesn't provide a way to get all calendars.

        Returns:
            List containing at least the default calendar
        """
        # pyremindkit doesn't provide a direct get_all method,
        # so we return only the default calendar
        default_calendar = self.get_default_calendar()
        return [default_calendar]

    def get_default_calendar(self) -> Any:
        """
        Get the default calendar.

        If no default calendar is found, attempt to use the first available calendar
        or create a new one.

        Returns:
            Default calendar object
        """
        try:
            return self.remind.calendars.get_default()
        except ValueError as e:
            self.logger.warning("No default calendar found. Attempting to find any available calendar.")

            # Try to get all calendars and use the first one
            try:
                all_calendars = self.remind.get_calendars()
                if all_calendars and len(all_calendars) > 0:
                    self.logger.info(f"Using first available calendar: {all_calendars[0].name}")
                    return all_calendars[0]
            except Exception as cal_err:
                self.logger.warning(f"Could not retrieve calendars: {str(cal_err)}")

            # Try to create a new calendar as a last resort
            try:
                self.logger.info("Attempting to create a new calendar 'Things Export'")
                new_calendar = self.remind.create_calendar("Things Export")
                return new_calendar
            except Exception as create_err:
                self.logger.error(f"Could not create a new calendar: {str(create_err)}")

            # If all else fails, raise a more helpful error
            raise ValueError(
                "Could not find or create a Reminders calendar. Please make sure you have at least one "
                "calendar set up in the Reminders app and that the app has been launched at least once."
            ) from e

    def find_or_create_calendar(self, name: str) -> Any:
        """
        Find a calendar with the given name or use the default calendar.

        Note: Due to API limitations, pyremindkit doesn't support creating new
        calendars. This method will just return the default calendar.

        Args:
            name: Name of the calendar (ignored, included for API compatibility)

        Returns:
            Default calendar object
        """
        # pyremindkit doesn't support creating calendars,
        # so we just return the default calendar
        default_calendar = self.get_default_calendar()
        self.logger.warning(
            f"Calendar '{name}' requested but pyremindkit cannot create calendars. "
            f"Using default calendar '{default_calendar.name}' instead."
        )
        return default_calendar

    def create_reminder(
        self,
        title: str,
        notes: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: Optional[int] = None,
        calendar_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        completed: bool = False,
        completion_date: Optional[str] = None,
        early_reminder_date: Optional[datetime] = None,
        flagged: bool = False
    ) -> Any:
        """
        Create a new reminder.

        Args:
            title: Title of the reminder
            notes: Notes for the reminder
            due_date: Due date for the reminder
            priority: Priority level
            calendar_id: ID of the calendar to create the reminder in
            tags: List of tags to apply to the reminder
            completed: Whether the reminder is completed
            completion_date: The date when the task was completed
            early_reminder_date: Date for an early reminder alert
            flagged: Whether the reminder should be flagged as important

        Returns:
            Created reminder object
        """
        if calendar_id is None:
            calendar_id = self.get_default_calendar().id

        # Add reminder structure info to notes
        structured_notes = notes or ""

        # Add tags if provided (using notes field as a workaround since
        # pyremindkit doesn't directly support tags)
        if tags and len(tags) > 0:
            tag_str = " ".join([f"#{tag}" for tag in tags])
            if structured_notes:
                structured_notes += f"\n\nTags: {tag_str}"
            else:
                structured_notes = f"Tags: {tag_str}"

        # Add completion date info if relevant
        if completed and completion_date:
            if structured_notes:
                structured_notes += f"\n\nCompleted on: {completion_date}"
            else:
                structured_notes = f"Completed on: {completion_date}"

        # Create the reminder with the enhanced notes
        reminder = self.remind.create_reminder(
            title=title,
            notes=structured_notes,
            due_date=due_date,
            priority=priority if priority is not None else Priority.NONE,
            calendar_id=calendar_id,
            is_completed=completed,
        )

        # Handle post-creation updates that require the reminder ID
        try:
            # Set completed status if needed
            if completed:
                self.remind.update_reminder(
                    reminder.id,
                    is_completed=True
                )
                self.logger.debug(f"Marked reminder '{title}' as completed")

            # Set early reminder alert if provided
            if early_reminder_date:
                self.remind.update_reminder(
                    reminder.id,
                    remind_me_date=early_reminder_date
                )
                self.logger.debug(f"Set early reminder for '{title}' at {early_reminder_date}")

            # Set flagged status if needed
            if flagged:
                self.remind.update_reminder(
                    reminder.id,
                    flagged=True
                )
                self.logger.debug(f"Flagged reminder '{title}' as important")

        except Exception as e:
            self.logger.warning(f"Error updating reminder attributes: {str(e)}")

        return reminder

    def get_reminders(self, calendar_id: Optional[str] = None) -> List[Any]:
        """
        Get all reminders, optionally filtered by calendar.

        Args:
            calendar_id: ID of calendar to filter by

        Returns:
            List of reminder objects
        """
        reminders = self.remind.get_reminders()
        if calendar_id:
            return [r for r in reminders if r.calendar_id == calendar_id]
        return reminders