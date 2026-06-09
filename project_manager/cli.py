from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from rich.console import Console
from rich.table import Table

from project_manager.services.manager import (
    ContributorNotFoundError,
    DuplicateProjectError,
    DuplicateTaskError,
    DuplicateUserError,
    Manager,
    ProjectNotFoundError,
    TaskAlreadyCompletedError,
    TaskNotFoundError,
    UserNotFoundError,
)
from project_manager.services.storage import Storage


class CLI:
    """Command-line interface for the project management system."""

    def __init__(self, manager: Manager, console: Console | None = None) -> None:
        self._manager = manager
        self._console = console or Console()

    def run(self, args: Sequence[str] | None = None) -> int:
        """Parse arguments and execute the requested command.

        Args:
            args: Command-line arguments. Uses sys.argv by default.

        Returns:
            Exit code (0 for success, 1 for error).
        """
        parser = self._build_parser()
        parsed_args = parser.parse_args(args)

        if not hasattr(parsed_args, "func"):
            parser.print_help()
            return 1

        try:
            parsed_args.func(parsed_args)
            return 0
        except (
            DuplicateUserError,
            UserNotFoundError,
            DuplicateProjectError,
            ProjectNotFoundError,
            DuplicateTaskError,
            TaskNotFoundError,
            TaskAlreadyCompletedError,
            ContributorNotFoundError,
            ValueError,
            TypeError,
        ) as exc:
            self._console.print(f"[red]Error:[/red] {exc}")
            return 1

    def _build_parser(self) -> argparse.ArgumentParser:
        """Build the argument parser with all subcommands."""
        parser = argparse.ArgumentParser(
            prog="project_manager",
            description="Command Line Project Management System",
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        self._build_user_commands(subparsers)
        self._build_project_commands(subparsers)
        self._build_task_commands(subparsers)
        self._build_contributor_commands(subparsers)

        return parser

    def _build_user_commands(self, subparsers: argparse._SubParsersAction) -> None:
        """Add user-related subcommands."""
        user_parser = subparsers.add_parser("add-user", help="Add a new user")
        user_parser.add_argument(
            "--name",
            required=True,
            help="Name of the user to create",
        )
        user_parser.set_defaults(func=self._handle_add_user)

        list_users_parser = subparsers.add_parser("list-users", help="List all users")
        list_users_parser.set_defaults(func=self._handle_list_users)

        remove_user_parser = subparsers.add_parser("remove-user", help="Remove a user")
        remove_user_parser.add_argument(
            "--name",
            required=True,
            help="Name of the user to remove",
        )
        remove_user_parser.set_defaults(func=self._handle_remove_user)

    def _build_project_commands(self, subparsers: argparse._SubParsersAction) -> None:
        """Add project-related subcommands."""
        add_project_parser = subparsers.add_parser("add-project", help="Add a new project")
        add_project_parser.add_argument(
            "--user",
            required=True,
            help="Name of the user who owns the project",
        )
        add_project_parser.add_argument(
            "--title",
            required=True,
            help="Title of the project",
        )
        add_project_parser.set_defaults(func=self._handle_add_project)

        list_projects_parser = subparsers.add_parser(
            "list-projects", help="List all projects for a user"
        )
        list_projects_parser.add_argument(
            "--user",
            required=True,
            help="Name of the user",
        )
        list_projects_parser.set_defaults(func=self._handle_list_projects)

        remove_project_parser = subparsers.add_parser("remove-project", help="Remove a project")
        remove_project_parser.add_argument(
            "--user",
            required=True,
            help="Name of the user who owns the project",
        )
        remove_project_parser.add_argument(
            "--title",
            required=True,
            help="Title of the project to remove",
        )
        remove_project_parser.set_defaults(func=self._handle_remove_project)

    def _build_task_commands(self, subparsers: argparse._SubParsersAction) -> None:
        """Add task-related subcommands."""
        add_task_parser = subparsers.add_parser("add-task", help="Add a new task")
        add_task_parser.add_argument(
            "--user",
            required=True,
            help="Name of the user who owns the project",
        )
        add_task_parser.add_argument(
            "--project",
            required=True,
            help="Title of the project",
        )
        add_task_parser.add_argument(
            "--title",
            required=True,
            help="Title of the task",
        )
        add_task_parser.set_defaults(func=self._handle_add_task)

        list_tasks_parser = subparsers.add_parser("list-tasks", help="List all tasks in a project")
        list_tasks_parser.add_argument(
            "--user",
            required=True,
            help="Name of the user who owns the project",
        )
        list_tasks_parser.add_argument(
            "--project",
            required=True,
            help="Title of the project",
        )
        list_tasks_parser.set_defaults(func=self._handle_list_tasks)

        complete_task_parser = subparsers.add_parser("complete-task", help="Mark a task as completed")
        complete_task_parser.add_argument(
            "--user",
            required=True,
            help="Name of the user who owns the project",
        )
        complete_task_parser.add_argument(
            "--project",
            required=True,
            help="Title of the project",
        )
        complete_task_parser.add_argument(
            "--task",
            required=True,
            help="Title of the task to complete",
        )
        complete_task_parser.set_defaults(func=self._handle_complete_task)

        remove_task_parser = subparsers.add_parser("remove-task", help="Remove a task")
        remove_task_parser.add_argument(
            "--user",
            required=True,
            help="Name of the user who owns the project",
        )
        remove_task_parser.add_argument(
            "--project",
            required=True,
            help="Title of the project",
        )
        remove_task_parser.add_argument(
            "--task",
            required=True,
            help="Title of the task to remove",
        )
        remove_task_parser.set_defaults(func=self._handle_remove_task)

    def _build_contributor_commands(self, subparsers: argparse._SubParsersAction) -> None:
        """Add contributor-related subcommands."""
        add_contributor_parser = subparsers.add_parser("add-contributor", help="Add a contributor to a task")
        add_contributor_parser.add_argument(
            "--user",
            required=True,
            help="Name of the user who owns the project",
        )
        add_contributor_parser.add_argument(
            "--project",
            required=True,
            help="Title of the project",
        )
        add_contributor_parser.add_argument(
            "--task",
            required=True,
            help="Title of the task",
        )
        add_contributor_parser.add_argument(
            "--contributor",
            required=True,
            help="Name of the contributor to add",
        )
        add_contributor_parser.set_defaults(func=self._handle_add_contributor)

        remove_contributor_parser = subparsers.add_parser(
            "remove-contributor", help="Remove a contributor from a task"
        )
        remove_contributor_parser.add_argument(
            "--user",
            required=True,
            help="Name of the user who owns the project",
        )
        remove_contributor_parser.add_argument(
            "--project",
            required=True,
            help="Title of the project",
        )
        remove_contributor_parser.add_argument(
            "--task",
            required=True,
            help="Title of the task",
        )
        remove_contributor_parser.add_argument(
            "--contributor",
            required=True,
            help="Name of the contributor to remove",
        )
        remove_contributor_parser.set_defaults(func=self._handle_remove_contributor)

    def _handle_add_user(self, args: argparse.Namespace) -> None:
        user = self._manager.add_user(args.name)
        self._console.print(f"User '{user.name}' added successfully.")

    def _handle_list_users(self, args: argparse.Namespace) -> None:
        users = self._manager.list_users()
        if not users:
            self._console.print("[yellow]No users found in the system.[/yellow]")
            return
        table = Table(title="System Users")
        table.add_column("User Name", style="cyan", no_wrap=True)
        for user in users:
            table.add_row(user.name)
        self._console.print(table)

    def _handle_remove_user(self, args: argparse.Namespace) -> None:
        self._manager.remove_user(args.name)
        self._console.print(f"User '{args.name}' removed successfully.")

    def _handle_add_project(self, args: argparse.Namespace) -> None:
        project = self._manager.add_project(args.user, args.title)
        self._console.print(f"Project '{project.title}' created for user '{args.user}'.")

    def _handle_list_projects(self, args: argparse.Namespace) -> None:
        projects = self._manager.list_projects(args.user)
        if not projects:
            self._console.print(f"[yellow]No projects found for user '{args.user}'.[/yellow]")
            return
        table = Table(title=f"Projects for {args.user}")
        table.add_column("Project Title", style="magenta")
        table.add_column("Total Tasks", style="green")
        for project in projects:
            table.add_row(project.title, str(len(project.tasks)))
        self._console.print(table)

    def _handle_remove_project(self, args: argparse.Namespace) -> None:
        self._manager.remove_project(args.user, args.title)
        self._console.print(f"Project '{args.title}' removed from user '{args.user}'.")

    def _handle_add_task(self, args: argparse.Namespace) -> None:
        task = self._manager.add_task(args.user, args.project, args.title)
        self._console.print(f"Task '{task.title}' added to project '{args.project}'.")

    def _handle_list_tasks(self, args: argparse.Namespace) -> None:
        tasks = self._manager.list_tasks(args.user, args.project)
        if not tasks:
            self._console.print(f"[yellow]No tasks found inside project '{args.project}'.[/yellow]")
            return
        table = Table(title=f"Tasks in {args.project} ({args.user})")
        table.add_column("Task Title", style="blue")
        table.add_column("Status", style="bold")
        table.add_column("Contributors", style="yellow")
        for task in tasks:
            status = "[green]Done[/green]" if task.completed else "[yellow]Pending[/yellow]"
            contributors = ", ".join(task.contributors) if task.contributors else "None"
            table.add_row(task.title, status, contributors)
        self._console.print(table)

    def _handle_complete_task(self, args: argparse.Namespace) -> None:
        self._manager.complete_task(args.user, args.project, args.task)
        self._console.print(f"Task '{args.task}' marked as completed.")

    def _handle_remove_task(self, args: argparse.Namespace) -> None:
        project = self._manager.get_project(args.user, args.project)
        project.remove_task(args.task)
        self._manager._save_data()
        self._console.print(f"Task '{args.task}' removed from project '{args.project}'.")

    def _handle_add_contributor(self, args: argparse.Namespace) -> None:
        self._manager.add_contributor(args.user, args.project, args.task, args.contributor)
        self._console.print(f"Added contributor '{args.contributor}' to task '{args.task}'.")

    def _handle_remove_contributor(self, args: argparse.Namespace) -> None:
        project = self._manager.get_project(args.user, args.project)
        task = project.get_task(args.task)
        task.remove_contributor(args.contributor)
        self._manager._save_data()
        self._console.print(f"Removed contributor '{args.contributor}' from task '{args.task}'.")


def main() -> int:
    """Global execution driver for the CLI application."""
    db_path = Path("data/projects.json")
    storage = Storage(db_path)
    manager = Manager(storage)
    cli = CLI(manager)
    return cli.run(sys.argv[1:])