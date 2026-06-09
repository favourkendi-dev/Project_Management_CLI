from __future__ import annotations

from typing import Any

from .project import Project


class EmptyUserNameError(ValueError):
    """Raised when a user name is empty or contains only whitespace."""


class DuplicateProjectError(ValueError):
    """Raised when attempting to add a project with a title that already exists."""


class ProjectNotFoundError(ValueError):
    """Raised when a requested project is not found."""


class User:
    """Represents a user that owns a collection of projects."""

    def __init__(self, name: str, projects: list[Project] | None = None) -> None:
        if not isinstance(name, str):
            raise TypeError(f"name must be a string, got {type(name).__name__}")
        stripped_name = name.strip()
        if not stripped_name:
            raise EmptyUserNameError("User name cannot be empty or contain only whitespace.")
        self._name: str = stripped_name
        self._projects: list[Project] = []
        if projects is not None:
            if not isinstance(projects, list):
                raise TypeError(f"projects must be a list of Project instances, got {type(projects).__name__}")
            for project in projects:
                self.add_project(project)

    @property
    def name(self) -> str:
        return self._name

    @property
    def projects(self) -> list[Project]:
        return self._projects.copy()

    def add_project(self, project: Project) -> None:
        """Add a project to the user.

        Args:
            project: The Project instance to add.

        Raises:
            TypeError: If project is not a Project instance.
            DuplicateProjectError: If a project with the same title already exists.
        """
        if not isinstance(project, Project):
            raise TypeError(f"project must be a Project instance, got {type(project).__name__}")
        if self._find_project_index(project.title) is not None:
            raise DuplicateProjectError(
                f"Project with title '{project.title}' already exists for user '{self._name}'."
            )
        self._projects.append(project)

    def get_project(self, title: str) -> Project:
        """Retrieve a project by title.

        Args:
            title: The title of the project to retrieve.

        Returns:
            The matching Project instance.

        Raises:
            TypeError: If title is not a string.
            ProjectNotFoundError: If no project with the given title exists.
        """
        if not isinstance(title, str):
            raise TypeError(f"title must be a string, got {type(title).__name__}")
        index = self._find_project_index(title)
        if index is None:
            raise ProjectNotFoundError(
                f"Project with title '{title.strip()}' not found for user '{self._name}'."
            )
        return self._projects[index]

    def remove_project(self, title: str) -> None:
        """Remove a project by title.

        Args:
            title: The title of the project to remove.

        Raises:
            TypeError: If title is not a string.
            ProjectNotFoundError: If no project with the given title exists.
        """
        if not isinstance(title, str):
            raise TypeError(f"title must be a string, got {type(title).__name__}")
        index = self._find_project_index(title)
        if index is None:
            raise ProjectNotFoundError(
                f"Project with title '{title.strip()}' not found for user '{self._name}'."
            )
        del self._projects[index]

    def list_projects(self) -> list[Project]:
        """Return a list of all projects owned by the user.

        Returns:
            A shallow copy of the project list.
        """
        return self._projects.copy()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the user to a JSON-serializable dictionary."""
        return {
            "name": self._name,
            "projects": [project.to_dict() for project in self._projects],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        """Reconstruct a User instance from a dictionary.

        Args:
            data: A dictionary containing user data.

        Returns:
            A new User instance.

        Raises:
            KeyError: If required keys are missing.
            TypeError: If values have incorrect types.
            EmptyUserNameError: If the user name is empty after stripping.
            EmptyProjectTitleError: If a project title is empty after stripping.
            DuplicateTaskError: If a duplicate task title is encountered.
            TaskNotFoundError: If a task reference is invalid during reconstruction.
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")

        name = data.get("name")
        if name is None:
            raise KeyError("Missing required key: 'name'")

        projects_data = data.get("projects", [])
        if not isinstance(projects_data, list):
            raise TypeError(f"'projects' must be a list, got {type(projects_data).__name__}")

        projects: list[Project] = []
        for project_data in projects_data:
            if not isinstance(project_data, dict):
                raise TypeError(f"Each project must be a dict, got {type(project_data).__name__}")
            projects.append(Project.from_dict(project_data))

        return cls(name=name, projects=projects)

    def _find_project_index(self, title: str) -> int | None:
        """Find the index of a project by title, case-insensitive.

        Args:
            title: The title to search for.

        Returns:
            The index of the matching project, or None if not found.
        """
        normalized = title.strip().lower()
        for index, project in enumerate(self._projects):
            if project.title.lower() == normalized:
                return index
        return None