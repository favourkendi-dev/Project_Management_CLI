# Project Management CLI Tool



A Python-based command-line application for managing users, projects, tasks, and contributors.

## Features

- Manage users with `add-user`, `list-users`, and `remove-user`.
- Create projects for specific users with `add-project`, `list-projects`, `remove-project`, and `search-projects`.
- Add and manage tasks inside projects with `add-task`, `list-tasks`, `complete-task`, and `remove-task`.
- Track contributors on tasks with `add-contributor` and `remove-contributor`.
- Persist data locally in JSON format under `data/projects.json`.
- Pretty console output using `rich`.

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

## Setup

1. Change to the project root:
   ```bash
   cd /home/user/Documents/Project_Management_CLI
   ```

2. Install dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## Run the application

The entrypoint is `main.py`.

Print the help menu:
```bash
python3 main.py --help
```

### Examples

Add a user:
```bash
python3 main.py add-user --name "Alex" --email "alex@example.com"
```

Create a project for a user:
```bash
python3 main.py add-project --user "Alex" --title "CLI Tool" --due-date "2026-06-30"
```

Add a task to a project:
```bash
python3 main.py add-task --user "Alex" --project "CLI Tool" --title "Implement add-task"
```

List a user's projects:
```bash
python3 main.py list-projects --user "Alex"
```

Search a user's projects by keyword:
```bash
python3 main.py search-projects --user "Alex" --query "cli"
```

List tasks in a project:
```bash
python3 main.py list-tasks --user "Alex" --project "CLI Tool"
```

Mark a task complete:
```bash
python3 main.py complete-task --user "Alex" --project "CLI Tool" --task "Implement add-task"
```

Add a contributor to a task:
```bash
python3 main.py add-contributor --user "Alex" --project "CLI Tool" --task "Implement add-task" --contributor "Jordan"
```

## Testing

Run tests with pytest:
```bash
pytest
```

## Project structure

- `main.py` - application entry point
- `project_manager/cli.py` - command-line interface logic
- `project_manager/models/` - `User`, `Project`, and `Task` classes
- `project_manager/services/` - `Manager` business logic and `Storage` persistence
- `data/` - JSON storage files
- `tests/` - unit tests for models, services, and CLI

## Notes

- The application stores data in `data/projects.json`.
- If `data/projects.json` does not exist, it is created automatically.
- The CLI uses `rich` for colored and tabular output.
