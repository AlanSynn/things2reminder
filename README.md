# Things2Reminder

> **⚠️ WORK IN PROGRESS ⚠️**
> This project is currently under active development. Features may be incomplete or subject to change.

A Python utility to export your Things app todos to Apple Reminders.

## Features

- Exports Things todos to Apple Reminders
- Preserves task details including notes, tags, and due dates
- Preserves checklist items (as part of the reminder notes)
- Maintains details and metadata from Things
- **Preserves completion status**: Tasks marked as completed in Things will also be marked as completed in Reminders
- **Smart flagging**: Tasks from the Anytime list with deadlines are flagged and given an early reminder (1 day before the deadline)
- **Intelligent calendar selection**: Uses LLM to automatically assign todos to the most appropriate calendar
- **Efficient batch processing**: Processes todos in batches of 100 for faster exports

## Important Notes

- **LLM Requirement**: This tool requires the `llm` command-line tool for intelligent calendar selection
- **Permission Required**: macOS requires explicit permission to access Reminders.

## Requirements

- macOS (since both Things and Apple Reminders are macOS/iOS applications)
- Python 3.9 or later
- Things 3 app
- Apple Reminders app
- `llm` command-line tool (for calendar selection)

> See [llm.datasette.io](https://llm.datasette.io) for LLM integration

## Installation

1. Clone this repository:

```bash
git clone https://github.com/AlanSynn/things2reminder.git
cd things2reminder
```

2. Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate

# Install with uv (recommended)
uv pip install -e .

# Or using standard pip
pip install -e .
```

3. Install the `llm` command-line tool for calendar selection:

```bash
# If you use pip
pip install llm

# If you use brew
brew install llm
```

## Usage

First, check your Reminders setup and permissions:

```bash
python -m scripts.check_reminders_setup
```

This will verify that Reminders permissions are granted and at least one calendar exists in Reminders.

If you need to specifically check and grant permissions, you can run:

```bash
python -m scripts.permission_check
```

Then run the export tool with:

```bash
# If installed with pip
things2reminder

# If running from source
python -m things2reminder.cli
```

For more detailed output, use the verbose flag:

```bash
things2reminder --verbose
```

To skip the preliminary Reminders setup checks:

```bash
things2reminder --skip-checks
```

### Export Options

Things2Reminder provides various options to customize which tasks to export:

```bash
# Export everything from Things without any filtering
# (all statuses, trashed items, etc.)
things2reminder --all

# Export only tasks from the Today view
things2reminder --today

# Export only tasks in Inbox
things2reminder --inbox

# Export only tasks with deadlines
things2reminder --with-deadlines

# Include completed tasks in export
things2reminder --completed

# Include canceled tasks in export
things2reminder --canceled

# Export only tasks with a specific tag
things2reminder --tag "Work"

# Export completed tasks from the last week
things2reminder --completed --completed-last 7d

# Export only upcoming tasks
things2reminder --upcoming

# Export only someday tasks
things2reminder --someday

# Combine multiple options
things2reminder --today --completed --tag "Important"
```

You can combine these options to create highly customized exports. If no options are specified, the tool will export all active incomplete tasks by default.

The `--all` option is particularly useful for complete backups, as it exports absolutely everything from Things including trashed items, completed tasks, and all statuses.

### Permissions

The first time you run the script, macOS will prompt you to grant permission to access your Reminders. You must allow this access for the script to work properly.

If you see the error "No access to reminders", you need to grant permission to Terminal or Python to access your Reminders:

1. Go to System Preferences > Privacy & Security > Privacy > Reminders
2. Click the "+" button and add Terminal (or Python) to the list of approved applications
3. Ensure the checkbox next to Terminal/Python is checked
4. Restart Terminal and try running the script again

If you don't see a permission prompt:

1. Run the permission check script:
```bash
python -m scripts.permission_check
```

2. If you still don't see a prompt, you may need to reset permissions:
```bash
tccutil reset Reminders  # This requires admin privileges
```

## How It Works

The tool reads data from your Things app's SQLite database and creates corresponding items in Apple Reminders:

1. **Task Mapping**: Each Things todo is mapped to a Reminder item
2. **Tags Preservation**: Things tags are added as hashtags in the Reminder notes
3. **Structure Preservation**: Information about Things areas and projects is included in the reminder notes
4. **Metadata Preservation**: Due dates, priorities, and notes are transferred
5. **Completion Status**: Completed tasks in Things remain marked as completed in Reminders
6. **Smart Reminders**: Tasks from the Anytime list with deadlines get early reminders (1 day before) and are flagged as important
7. **Intelligent Calendar Selection**: Uses LLM to analyze todo content and assign to the most appropriate calendar
8. **Batch Processing**: Processes todos in batches of 100 for improved performance

## Project Structure

- `things2reminder/`: The main package
  - `cli.py`: Command-line interface for the tool
  - `exporter.py`: Main export functionality
  - `mapper.py`: Logic for mapping between Things and Reminders objects
  - `things_client.py`: Client for interacting with Things app
  - `reminders_client.py`: Client for interacting with Apple Reminders
- `scripts/`: Utility scripts
  - `check_reminders_setup.py`: Utility to verify Reminders app setup
  - `permission_check.py`: Utility to check and grant Reminders permissions
- `tests/`: Test suite

## Development

Run the tests with:

```bash
python -m pytest
```

## Troubleshooting

### Permission Issues

If you see an error like "Permission error: No access to reminders":

1. Run the permission check script: `python -m scripts.permission_check`
2. Follow the instructions to grant permission:
   - Go to System Preferences > Privacy & Security > Privacy > Reminders
   - Click the '+' button to add Terminal (or Python)
   - Ensure the checkbox next to Terminal/Python is checked
   - Restart Terminal and try again

### Calendar Selection

- The tool uses LLM to intelligently select the most appropriate calendar for each todo
- If the LLM command fails or returns invalid results, todos will be assigned to the default calendar
- Make sure the `llm` command-line tool is installed and working properly

### API-Related Errors

If you encounter errors related to missing methods or attributes:

1. Make sure you've installed the latest version of the required packages
2. Run with verbose mode for more details: `things2reminder --verbose`
3. Check for updates to this tool as the underlying APIs may have changed

#### "No default calendar found" Error

If you see this error:
1. Open the Apple Reminders app to ensure it's properly set up
2. Create at least one list/calendar in Reminders if you don't have any
3. Close and reopen the Reminders app
4. Try running the export tool again

### Installation Issues

- Make sure you're using Python 3.9 or newer
- Try reinstalling the package: `pip install -e .`
- If you encounter issues with dependencies, try using uv: `uv pip install -e .`

### Other Issues

For any other issues, please:
1. Run the tool with verbose logging: `things2reminder --verbose`
2. Check the error message and consult this troubleshooting section
3. If the issue persists, please open an issue on GitHub with the error details

## License

MIT

## Credits

This project uses:
- [things.py](https://github.com/thingsapi/things.py/) - A Python library for reading Things app data
- [pyremindkit](https://github.com/namuan/pyremindkit) - A Python wrapper for Apple Reminders API
- [llm](https://github.com/simonw/llm) - A command-line tool for working with large language models
