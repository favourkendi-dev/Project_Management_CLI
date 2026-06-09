from __future__ import annotations

from project_manager.models.project import (
    DuplicateTaskError,
    EmptyProjectTitleError,
    Project,
    TaskNotFoundError,
)
from project_manager.models.task import (
    EmptyContributorError,
    EmptyTitleError,
    Task,
)
from project_manager.models.user import (
    DuplicateProjectError,
    EmptyUserNameError,
    ProjectNotFoundError,
    User,
)
from project_manager.services.storage import (
    DatabaseCorruptionError,
    InvalidDatabaseStructureError,
    InvalidInputError,
    Storage,
)


class DuplicateUserError(ValueError):
    """Raised when attempting to add a user that already exists."""


class UserNotFoundError(ValueError):
    """Raised when a requested user is not found."""


class DuplicateTaskTitleError(ValueError):
    """Raised when attempting to add a task with a duplicate title."""


class TaskAlreadyCompletedError(ValueError):
    """Raised when attempting to complete an already completed task."""


class ContributorNotFoundError(ValueError):
    """Raised when a requested contributor is not found on a task."""


class Manager:
    """Orchestrates all business logic for the project management system."""

    def __init__(self, storage: Storage) -> None:
        if not isinstance(storage, Storage):
            raise TypeError(f"storage must be a Storage instance, got {type(storage).__name__}")
        self._storage: Storage = storage
        self._users: list[User] = []
        self._load_data()

    def add_user(self, name: str) -> User:
        """Add a new user to the system.

        Args:
            name: The name of the user to add.

        Returns:
            The newly created User instance.

        Raises:
            TypeError: If name is not a string.
            EmptyUserNameError: If name is empty or whitespace-only.
            DuplicateUserError: If a user with the same name already exists.
        """
        normalized_name = self._normalize_name(name)
        if self._find_user_index(normalized_name) is not None:
            raise DuplicateUserError(f"User '{normalized_name}' already exists.")
        user = User(name=normalized_name)
        self._users.append(user)
        self._save_data()
        return user

    def get_user(self, name: str) -> User:
        """Retrieve a user by name.

        Args:
            name: The name of the user to retrieve.

        Returns:
            The matching User instance.

        Raises:
            TypeError: If name is not a string.
            EmptyUserNameError: If name is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
        """
        normalized_name = self._normalize_name(name)
        index = self._find_user_index(normalized_name)
        if index is None:
            raise UserNotFoundError(f"User '{normalized_name}' not found.")
        return self._users[index]

    def list_users(self) -> list[User]:
        """Return a list of all users in the system.

        Returns:
            A shallow copy of the user list.
        """
        return self._users.copy()

    def remove_user(self, name: str) -> None:
        """Remove a user from the system.

        Args:
            name: The name of the user to remove.

        Raises:
            TypeError: If name is not a string.
            EmptyUserNameError: If name is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
        """
        normalized_name = self._normalize_name(name)
        index = self._find_user_index(normalized_name)
        if index is None:
            raise UserNotFoundError(f"User '{normalized_name}' not found.")
        del self._users[index]
        self._save_data()

    def add_project(self, user_name: str, project_title: str) -> Project:
        """Add a new project to a user.

        Args:
            user_name: The name of the user who owns the project.
            project_title: The title of the project to add.

        Returns:
            The newly created Project instance.

        Raises:
            TypeError: If inputs are not strings.
            EmptyUserNameError: If user_name is empty or whitespace-only.
            EmptyProjectTitleError: If project_title is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
            DuplicateProjectError: If a project with the same title already exists for the user.
        """
        user = self.get_user(user_name)
        normalized_title = self._normalize_title(project_title)
        project = Project(title=normalized_title)
        user.add_project(project)
        self._save_data()
        return project

    def get_project(self, user_name: str, project_title: str) -> Project:
        """Retrieve a project from a user.

        Args:
            user_name: The name of the user who owns the project.
            project_title: The title of the project to retrieve.

        Returns:
            The matching Project instance.

        Raises:
            TypeError: If inputs are not strings.
            EmptyUserNameError: If user_name is empty or whitespace-only.
            EmptyProjectTitleError: If project_title is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
            ProjectNotFoundError: If the project does not exist for the user.
        """
        user = self.get_user(user_name)
        return user.get_project(project_title)

    def list_projects(self, user_name: str) -> list[Project]:
        """Return a list of all projects for a user.

        Args:
            user_name: The name of the user.

        Returns:
            A list of Project instances.

        Raises:
            TypeError: If user_name is not a string.
            EmptyUserNameError: If user_name is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
        """
        user = self.get_user(user_name)
        return user.list_projects()

    def remove_project(self, user_name: str, project_title: str) -> None:
        """Remove a project from a user.

        Args:
            user_name: The name of the user who owns the project.
            project_title: The title of the project to remove.

        Raises:
            TypeError: If inputs are not strings.
            EmptyUserNameError: If user_name is empty or whitespace-only.
            EmptyProjectTitleError: If project_title is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
            ProjectNotFoundError: If the project does not exist for the user.
        """
        user = self.get_user(user_name)
        user.remove_project(project_title)
        self._save_data()

    def add_task(self, user_name: str, project_title: str, task_title: str) -> Task:
        """Add a new task to a project.

        Args:
            user_name: The name of the user who owns the project.
            project_title: The title of the project.
            task_title: The title of the task to add.

        Returns:
            The newly created Task instance.

        Raises:
            TypeError: If inputs are not strings.
            EmptyUserNameError: If user_name is empty or whitespace-only.
            EmptyProjectTitleError: If project_title is empty or whitespace-only.
            EmptyTitleError: If task_title is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
            ProjectNotFoundError: If the project does not exist for the user.
            DuplicateTaskError: If a task with the same title already exists in the project.
        """
        project = self.get_project(user_name, project_title)
        normalized_task_title = self._normalize_title(task_title)
        task = Task(title=normalized_task_title)
        project.add_task(task)
        self._save_data()
        return task

    def list_tasks(self, user_name: str, project_title: str) -> list[Task]:
        """Return a list of all tasks in a project.

        Args:
            user_name: The name of the user who owns the project.
            project_title: The title of the project.

        Returns:
            A list of Task instances.

        Raises:
            TypeError: If inputs are not strings.
            EmptyUserNameError: If user_name is empty or whitespace-only.
            EmptyProjectTitleError: If project_title is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
            ProjectNotFoundError: If the project does not exist for the user.
        """
        project = self.get_project(user_name, project_title)
        return project.list_tasks()

    def complete_task(self, user_name: str, project_title: str, task_title: str) -> None:
        """Mark a task as completed.

        Args:
            user_name: The name of the user who owns the project.
            project_title: The title of the project.
            task_title: The title of the task to complete.

        Raises:
            TypeError: If inputs are not strings.
            EmptyUserNameError: If user_name is empty or whitespace-only.
            EmptyProjectTitleError: If project_title is empty or whitespace-only.
            EmptyTitleError: If task_title is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
            ProjectNotFoundError: If the project does not exist for the user.
            TaskNotFoundError: If the task does not exist in the project.
            TaskAlreadyCompletedError: If the task is already completed.
        """
        task = self._get_task(user_name, project_title, task_title)
        if task.completed:
            raise TaskAlreadyCompletedError(
                f"Task '{task.title}' is already completed."
            )
        task.mark_complete()
        self._save_data()

    def remove_task(self, user_name: str, project_title: str, task_title: str) -> None:
        """Remove a task from a project.

        Args:
            user_name: The name of the user who owns the project.
            project_title: The title of the project.
            task_title: The title of the task to remove.

        Raises:
            TypeError: If inputs are not strings.
            EmptyUserNameError: If user_name is empty or whitespace-only.
            EmptyProjectTitleError: If project_title is empty or whitespace-only.
            EmptyTitleError: If task_title is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
            ProjectNotFoundError: If the project does not exist for the user.
            TaskNotFoundError: If the task does not exist in the project.
        """
        project = self.get_project(user_name, project_title)
        project.remove_task(task_title)
        self._save_data()

    def add_contributor(
        self,
        user_name: str,
        project_title: str,
        task_title: str,
        contributor_name: str,
    ) -> None:
        """Add a contributor to a task.

        Args:
            user_name: The name of the user who owns the project.
            project_title: The title of the project.
            task_title: The title of the task.
            contributor_name: The name of the contributor to add.

        Raises:
            TypeError: If inputs are not strings.
            EmptyUserNameError: If user_name is empty or whitespace-only.
            EmptyProjectTitleError: If project_title is empty or whitespace-only.
            EmptyTitleError: If task_title is empty or whitespace-only.
            EmptyContributorError: If contributor_name is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
            ProjectNotFoundError: If the project does not exist for the user.
            TaskNotFoundError: If the task does not exist in the project.
        """
        task = self._get_task(user_name, project_title, task_title)
        normalized_contributor = self._normalize_name(contributor_name)
        task.add_contributor(normalized_contributor)
        self._save_data()

    def add_task_contributor(
        self,
        user_name: str,
        project_title: str,
        task_title: str,
        contributor_name: str,
    ) -> None:
        """Add a contributor to an existing project task."""
        task = self._get_task(user_name, project_title, task_title)
        normalized_contributor = self._normalize_name(contributor_name)
        task.add_contributor(normalized_contributor)
        self._save_data()

    def remove_contributor(
        self,
        user_name: str,
        project_title: str,
        task_title: str,
        contributor_name: str,
    ) -> None:
        """Remove a contributor from a task.

        Args:
            user_name: The name of the user who owns the project.
            project_title: The title of the project.
            task_title: The title of the task.
            contributor_name: The name of the contributor to remove.

        Raises:
            TypeError: If inputs are not strings.
            EmptyUserNameError: If user_name is empty or whitespace-only.
            EmptyProjectTitleError: If project_title is empty or whitespace-only.
            EmptyTitleError: If task_title is empty or whitespace-only.
            EmptyContributorError: If contributor_name is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
            ProjectNotFoundError: If the project does not exist for the user.
            TaskNotFoundError: If the task does not exist in the project.
            ContributorNotFoundError: If the contributor is not found on the task.
        """
        task = self._get_task(user_name, project_title, task_title)
        normalized_contributor = self._normalize_name(contributor_name)
        try:
            task.remove_contributor(normalized_contributor)
        except ValueError as exc:
            raise ContributorNotFoundError(str(exc)) from exc
        self._save_data()

    def _load_data(self) -> None:
        """Load all users from persistent storage."""
        try:
            self._users = self._storage.load_users()
        except (
            DatabaseCorruptionError,
            InvalidDatabaseStructureError,
            InvalidInputError,
        ):
            self._users = []
            raise

    def _save_data(self) -> None:
        """Persist all users to storage."""
        self._storage.save_users(self._users)

    def _find_user_index(self, name: str) -> int | None:
        """Find the index of a user by normalized name.

        Args:
            name: The pre-normalized name to search for.

        Returns:
            The index of the matching user, or None if not found.
        """
        for index, user in enumerate(self._users):
            if user.name.lower() == name.lower():
                return index
        return None

    def _get_task(self, user_name: str, project_title: str, task_title: str) -> Task:
        """Retrieve a task from a project owned by a user.

        Args:
            user_name: The name of the user.
            project_title: The title of the project.
            task_title: The title of the task.

        Returns:
            The matching Task instance.

        Raises:
            TypeError: If inputs are not strings.
            EmptyUserNameError: If user_name is empty or whitespace-only.
            EmptyProjectTitleError: If project_title is empty or whitespace-only.
            EmptyTitleError: If task_title is empty or whitespace-only.
            UserNotFoundError: If the user does not exist.
            ProjectNotFoundError: If the project does not exist for the user.
            TaskNotFoundError: If the task does not exist in the project.
        """
        project = self.get_project(user_name, project_title)
        return project.get_task(task_title)

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize a name by stripping whitespace and validating.

        Args:
            name: The raw name input.

        Returns:
            The stripped name.

        Raises:
            TypeError: If name is not a string.
            EmptyUserNameError: If name is empty after stripping.
        """
        if not isinstance(name, str):
            raise TypeError(f"name must be a string, got {type(name).__name__}")
        stripped = name.strip()
        if not stripped:
            raise EmptyUserNameError("Name cannot be empty or contain only whitespace.")
        return stripped

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalize a title by stripping whitespace and validating.

        Args:
            title: The raw title input.

        Returns:
            The stripped title.

        Raises:
            TypeError: If title is not a string.
            EmptyTitleError: If title is empty after stripping.
        """
        if not isinstance(title, str):
            raise TypeError(f"title must be a string, got {type(title).__name__}")
        stripped = title.strip()
        if not stripped:
            raise EmptyTitleError("Title cannot be empty or contain only whitespace.")
        return stripped