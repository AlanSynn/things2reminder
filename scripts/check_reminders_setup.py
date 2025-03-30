#!/usr/bin/env python3
"""
Check if Reminders is properly set up.

This script verifies that:
1. Reminders app permissions are granted
2. At least one calendar exists in Reminders
"""
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_reminders_setup():
    """
    Check if Reminders app is properly set up with at least one calendar.

    Returns:
        bool: True if setup is valid, False otherwise
    """
    try:
        from pyremindkit import RemindKit
        logger.info("Checking Reminders setup...")

        # 1. Create RemindKit instance (will test permissions)
        remind = RemindKit()
        logger.info("✅ Reminders permission granted")

        # 2. Check for at least one calendar
        try:
            # Try to get default calendar
            default_calendar = remind.calendars.get_default()
            logger.info(f"✅ Default calendar found: {default_calendar.name}")
            return True
        except ValueError as ve:
            logger.warning(f"No default calendar found: {str(ve)}")

            # If no default, try to get all calendars
            try:
                calendars = remind.get_calendars()
                if calendars and len(calendars) > 0:
                    logger.info(f"✅ Found {len(calendars)} calendar(s). First one: {calendars[0].name}")
                    return True
                else:
                    logger.error("❌ No calendars found in Reminders")
                    logger.error("Please open the Reminders app and create at least one list")

                    # Instructions on how to create a list in Reminders
                    print("\n===== INSTRUCTIONS TO CREATE A REMINDERS LIST =====")
                    print("1. Open the Reminders app on your Mac")
                    print("2. In the sidebar, click the + button near the bottom of the lists")
                    print("3. Enter a name for your new list (e.g., 'Things Import')")
                    print("4. Press Enter/Return to create the list")
                    print("5. Close and reopen Reminders to ensure changes are saved")
                    print("6. Run this check script again")
                    print("===============================================\n")

                    return False
            except Exception as e:
                logger.error(f"❌ Could not retrieve calendars: {str(e)}")
                logger.error("Please ensure Reminders app is properly set up")
                return False

    except ImportError:
        logger.error("❌ PyRemindKit not installed. Run: pip install git+https://github.com/namuan/pyremindkit.git")
        return False
    except PermissionError:
        logger.error("❌ Permission denied. You need to grant access to Reminders")
        logger.error("""
To grant permission:
1. Go to System Preferences > Privacy & Security > Privacy > Reminders
2. Click the '+' button and add Terminal (or Python)
3. Ensure the checkbox next to Terminal/Python is checked
4. Restart Terminal and run this script again
""")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")

        # Check if the error message contains specific known issues
        err_msg = str(e).lower()
        if "no default calendar" in err_msg or "calendar" in err_msg:
            logger.error("❌ No calendars found in Reminders")
            logger.error("Please open the Reminders app and create at least one list")

            # Instructions on how to create a list in Reminders
            print("\n===== INSTRUCTIONS TO CREATE A REMINDERS LIST =====")
            print("1. Open the Reminders app on your Mac")
            print("2. In the sidebar, click the + button near the bottom of the lists")
            print("3. Enter a name for your new list (e.g., 'Things Import')")
            print("4. Press Enter/Return to create the list")
            print("5. Close and reopen Reminders to ensure changes are saved")
            print("6. Run this check script again")
            print("===============================================\n")

        return False

def main():
    """Main function to run the script."""
    print("\n=== Reminders Setup Check ===\n")

    try:
        if check_reminders_setup():
            print("\n✅ Reminders is properly set up! You can now run the Things2Reminder export tool.\n")
            return 0
        else:
            print("\n❌ Reminders setup issues detected. Please fix the problems above.\n")
            return 1
    except Exception as e:
        logger.error(f"Error during check: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())