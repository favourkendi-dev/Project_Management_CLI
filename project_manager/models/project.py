from __future__ import annotations

from typing import Any

from .task import Task


class DuplicateTaskError(ValueError):
    """Raised when attempting to add a task with a title that already exists in the project."""


class TaskNotFoundError(ValueError):
    """Raised when a requested task is not found in the project."""


class EmptyProjectTitleError(ValueError):
    """Raised when a project title is empty or contains only whitespace."""


class Project:
    """Represents a project that owns a collection of tasks."""

    def __init__(self, title: str, tasks: list[Task] | None = None) -> None:
        if not isinstance(title, str):
            raise TypeError(f"title must be a string, got {type(title).__name__}")
        stripped_title = title.strip()
        if not stripped_title:
            raise EmptyProjectTitleError("Project title cannot be empty or contain only whitespace.")

        self._title: str = stripped_title
        self._tasks: list[Task] = []

        if tasks is not None:
            if not isinstance(tasks, list):
                raise TypeError(f"tasks must be a list of Task instances, got {type(tasks).__name__}")
            for task in tasks:
                self.add_task(task)

    @property
    def title(self) -> str:
        return self._title

    @property
    def tasks(self) -> list[Task]:
        return self._tasks.copy()

    def add_task(self, task: Task) -> None:
        """Add a task to the project.

        Args:
            task: The Task instance to add.

        Raises:
            TypeError: If task is not a Task instance.
            DuplicateTaskError: If a task with the same title already exists.
        """
        if not isinstance(task, Task):
            raise TypeError(f"task must be a Task instance, got {type(task).__name__}")

        if self._find_task_index(task.title) is not None:
            raise DuplicateTaskError(
                f"Task with title '{task.title}' already exists in project '{self._title}'."
            )

        self._tasks.append(task)

    def get_task(self, title: str) -> Task:
        """Retrieve a task by title.

        Args:
            title: The title of the task to retrieve.

        Returns:
            The matching Task instance.

        Raises:
            TypeError: If title is not a string.
            TaskNotFoundError: If no task with the given title exists.
        """
        if not isinstance(title, str):
            raise TypeError(f"title must be a string, got {type(title).__name__}")

        index = self._find_task_index(title)
        if index is None:
            raise TaskNotFoundError(
                f"Task with title '{title.strip()}' not found in project '{self._title}'."
            )

        return self._tasks[index]

    def remove_task(self, title: str) -> None:
        """Remove a task by title.

        Args:
            title: The title of the task to remove.

        Raises:
            TypeError: If title is not a string.
            TaskNotFoundError: If no task with the given title exists.
        """
        if not isinstance(title, str):
            raise TypeError(f"title must be a string, got {type(title).__name__}")

        index = self._find_task_index(title)
        if index is None:
            raise TaskNotFoundError(
                f"Task with title '{title.strip()}' not found in project '{self._title}'."
            )

        del self._tasks[index]

    def list_tasks(self) -> list[Task]:
        """Return a list of all tasks in the project."""
        return self._tasks.copy()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the project to a JSON-serializable dictionary."""
        return {
            "title": self._title,
            "tasks": [task.to_dict() for task in self._tasks],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Project:
        """Reconstruct a Project instance from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")

        title = data.get("title")
        if title is None:
            raise KeyError("Missing required key: 'title'")

        tasks_data = data.get("tasks", [])
        if not isinstance(tasks_data, list):
            raise TypeError(f"'tasks' must be a list, got {type(tasks_data).__name__}")

        tasks: list[Task] = []
        for task_data in tasks_data:
            if not isinstance(task_data, dict):
                raise TypeError(f"Each task must be a dict, got {type(task_data).__name__}")
            tasks.append(Task.from_dict(task_data))

        return cls(title=title, tasks=tasks)

    def _find_task_index(self, title: str) -> int | None:
        """Find the index of a task by title, case-insensitive."""
        normalized = title.strip().lower()
        for index, task in enumerate(self._tasks):
            if task.title.lower() == normalized:
                return index
        return None
