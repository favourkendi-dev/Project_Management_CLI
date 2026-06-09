from __future__ import annotations

from typing import Any


class EmptyTitleError(ValueError):
    """Raised when a task title is empty or contains only whitespace."""


class EmptyContributorError(ValueError):
    """Raised when a contributor name is empty or contains only whitespace."""


class ContributorNotFoundError(ValueError):
    """Raised when a contributor is not found on the task."""


class Task:
    """Represents a project task with title, completion status, and contributors."""

    def __init__(self, title: str, completed: bool = False, contributors: list[str] | None = None) -> None:
        if not isinstance(title, str):
            raise TypeError(f"title must be a string, got {type(title).__name__}")

        stripped_title = title.strip()
        if not stripped_title:
            raise EmptyTitleError("Task title cannot be empty or contain only whitespace.")

        if not isinstance(completed, bool):
            raise TypeError(f"completed must be a bool, got {type(completed).__name__}")

        self._title: str = stripped_title
        self._completed: bool = completed
        self._contributors: list[str] = []

        if contributors is not None:
            self._validate_contributors(contributors)

    @property
    def title(self) -> str:
        return self._title

    @property
    def completed(self) -> bool:
        return self._completed

    @property
    def contributors(self) -> list[str]:
        return self._contributors.copy()

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self._completed = True

    def add_contributor(self, name: str) -> None:
        """Add a contributor to the task.

        Args:
            name: The name of the contributor.

        Raises:
            TypeError: If name is not a string.
            EmptyContributorError: If name is empty or contains only whitespace.
        """
        if not isinstance(name, str):
            raise TypeError(f"Contributor name must be a string, got {type(name).__name__}")

        stripped_name = name.strip()
        if not stripped_name:
            raise EmptyContributorError("Contributor name cannot be empty or contain only whitespace.")

        if self._find_contributor_index(stripped_name) is None:
            self._contributors.append(stripped_name)

    def remove_contributor(self, name: str) -> None:
        """Remove a contributor from the task."""
        if not isinstance(name, str):
            raise TypeError(f"Contributor name must be a string, got {type(name).__name__}")

        stripped_name = name.strip()
        index = self._find_contributor_index(stripped_name)
        if index is None:
            raise ContributorNotFoundError(f"Contributor '{stripped_name}' not found.")

        del self._contributors[index]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the task to a JSON-serializable dictionary."""
        return {
            "title": self._title,
            "completed": self._completed,
            "contributors": self._contributors.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Reconstruct a Task instance from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")

        title = data.get("title")
        if title is None:
            raise KeyError("Missing required key: 'title'")

        completed = data.get("completed", False)
        if not isinstance(completed, bool):
            raise TypeError(f"'completed' must be a bool, got {type(completed).__name__}")

        contributors = data.get("contributors")
        if contributors is not None and not isinstance(contributors, list):
            raise TypeError(f"'contributors' must be a list, got {type(contributors).__name__}")

        return cls(title=title, completed=completed, contributors=contributors)

    def _validate_contributors(self, contributors: list[str]) -> None:
        if not isinstance(contributors, list):
            raise TypeError(f"contributors must be a list, got {type(contributors).__name__}")

        for name in contributors:
            self.add_contributor(name)

    def _find_contributor_index(self, name: str) -> int | None:
        normalized_name = name.strip().lower()
        for index, contributor in enumerate(self._contributors):
            if contributor.lower() == normalized_name:
                return index
        return None
