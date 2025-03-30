#!/usr/bin/env python3
"""
Things2Reminder - A program to export Things todos to Apple Reminders.

This script exports data from Things app to Apple Reminders, preserving
task details, tags, due dates and other metadata.
"""
import argparse
import logging
import sys
from src.things2reminder.exporter import ThingsToRemindersExporter
from check_reminders_setup import check_reminders_setup


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.

    Args:
        verbose: Whether to show debug logs
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Export Things todos to Apple Reminders'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip preliminary checks for Reminders setup'
    )

    # Add export options
    group = parser.add_argument_group('Export Options')
    group.add_argument(
        '--all',
        action='store_true',
        help='Export absolutely everything (all statuses, trashed items, etc.)'
    )
    group.add_argument(
        '--completed',
        action='store_true',
        help='Include completed tasks in export'
    )
    group.add_argument(
        '--canceled',
        action='store_true',
        help='Include canceled tasks in export'
    )
    group.add_argument(
        '--with-deadlines',
        action='store_true',
        help='Export only tasks with deadlines'
    )
    group.add_argument(
        '--today',
        action='store_true',
        help='Export only tasks in Today view'
    )
    group.add_argument(
        '--inbox',
        action='store_true',
        help='Export only tasks in Inbox'
    )
    group.add_argument(
        '--upcoming',
        action='store_true',
        help='Export only tasks in Upcoming view'
    )
    group.add_argument(
        '--someday',
        action='store_true',
        help='Export only tasks in Someday view'
    )
    group.add_argument(
        '--completed-last',
        metavar='PERIOD',
        help='Export completed tasks from last period (e.g., "7d", "2w", "1m")'
    )
    group.add_argument(
        '--tag',
        metavar='TAG',
        help='Export only tasks with specified tag'
    )

    return parser.parse_args()


def main():
    """Main entry point for the program."""
    args = parse_args()
    setup_logging(args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("Starting Things2Reminder export")

    # Check Reminders setup first unless skipped
    if not args.skip_checks:
        logger.info("Checking Reminders setup...")
        if not check_reminders_setup():
            logger.error("Reminders setup check failed. Run check_reminders_setup.py for details.")
            logger.error("To skip this check, run with --skip-checks")
            return 1
        logger.info("Reminders setup verified")

    try:
        exporter = ThingsToRemindersExporter()

        # Check if we should export everything
        if args.all:
            logger.info("Exporting ALL tasks from Things (including all statuses and trashed items)")
            areas, projects, tags, todos = exporter.export_all_tasks()
        else:
            # Configure export options based on arguments
            export_options = {
                'include_completed': args.completed,
                'include_canceled': args.canceled,
                'only_with_deadlines': args.with_deadlines,
                'only_today': args.today,
                'only_inbox': args.inbox,
                'only_upcoming': args.upcoming,
                'only_someday': args.someday,
                'completed_last': args.completed_last,
                'filter_tag': args.tag
            }

            # Filter export options to only include ones that were specified
            export_options = {k: v for k, v in export_options.items() if v}

            if export_options:
                logger.info(f"Using custom export options: {export_options}")
                areas, projects, tags, todos = exporter.export_with_options(**export_options)
            else:
                # If no options specified, do the default export
                logger.info("Using default export options (active incomplete tasks)")
                areas, projects, tags, todos = exporter.export_all()

        logger.info("Export completed successfully!")
        logger.info(f"Exported {todos} todos from Things to Reminders")
        logger.info(f"(Processed {areas} areas, {projects} projects, and {tags} tags)")
        logger.info("All tasks have been exported to your default Reminders calendar.")

        return 0
    except PermissionError as e:
        logger.error(f"Permission error: {str(e)}")
        logger.error("Please run 'python permission_check.py' to grant access to Reminders")
        return 1
    except ValueError as e:
        if "No default calendar found" in str(e) or "Could not find or create a Reminders calendar" in str(e):
            logger.error(f"Calendar error: {str(e)}")
            logger.error("Please make sure Reminders app is open and has at least one list created.")
            logger.error("Run python check_reminders_setup.py for a detailed check.")
            return 1
        else:
            logger.error(f"Export failed: {str(e)}")
            if args.verbose:
                logger.debug("Error details:", exc_info=True)
            return 1
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        if args.verbose:
            logger.debug("Error details:", exc_info=True)
        else:
            logger.error("Run with --verbose for more details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
