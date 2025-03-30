#!/usr/bin/env python3
"""
Permission Check Script for Things2Reminder

This script attempts to access the Apple Reminders API to trigger
the macOS permission prompt if needed. Run this before using the
main Things2Reminder tool to ensure proper permissions are set up.
"""
import sys


def main():
    """
    Main function that checks if Reminders can be accessed.
    This should trigger the macOS permission prompt if needed.
    """
    print("Checking for access to Apple Reminders...")

    try:
        from pyremindkit import RemindKit

        # This will trigger the permission prompt if permissions aren't granted
        remind = RemindKit()

        # Try to access the default calendar
        default_calendar = remind.calendars.get_default()
        print(f"✅ Success! Access granted to Reminders.")
        print(f"Default calendar: {default_calendar.name}")

        # Try to list reminders
        reminders = remind.get_reminders()
        print(f"Found {len(reminders)} reminders in total.")

        print("\nYou can now run the main Things2Reminder tool with:")
        print("python main.py")

        return 0
    except PermissionError as e:
        print(f"❌ Permission error: {e}")
        print("\nPlease grant permission to access Reminders:")
        print("1. Go to System Preferences > Privacy & Security > Privacy > Reminders")
        print("2. Click the '+' button and add Terminal (or Python) to the list")
        print("3. Ensure the checkbox next to Terminal/Python is checked")
        print("4. Restart Terminal and run this script again")
        return 1
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nPlease make sure all dependencies are installed:")
        print("pip install pyobjc")
        print("pip install git+https://github.com/namuan/pyremindkit.git")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\nPlease check the error message above and resolve the issue.")
        return 1


if __name__ == "__main__":
    sys.exit(main())