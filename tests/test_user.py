import pytest
from project_manager.models.user import (
    User,
    EmptyUserNameError,
    DuplicateProjectError,
    ProjectNotFoundError,
)
from project_manager.models.project import Project
from project_manager.models.task import Task

def test_user_creation_and_serialization():
    """Test full dictionary roundtrip mapping logic for deep User structures."""
    task = Task(title="SubTask", completed=True, contributors=["Emmanuel"])
    project = Project(title="SubProject", tasks=[task])
    user = User(name="Emmanuel", email="emmanuel@example.com", projects=[project])
    
    assert user.name == "Emmanuel"
    assert user.email == "emmanuel@example.com"
    
    # Test dictionary export structure
    serialized = user.to_dict()
    assert serialized["name"] == "Emmanuel"
    assert serialized["projects"][0]["title"] == "SubProject"
    
    # Test dictionary reconstruction structure
    reconstructed_user = User.from_dict(serialized)
    assert reconstructed_user.name == "Emmanuel"
    assert reconstructed_user.get_project("SubProject").title == "SubProject"
    assert reconstructed_user.get_project("SubProject").get_task("SubTask").completed is True

def test_user_project_management():
    """Verify adding, getting, and clearing project entities per User."""
    user = User(name="Developer")
    project = Project(title="Dev Project")
    
    user.add_project(project)
    
    with pytest.raises(DuplicateProjectError):
        user.add_project(Project(title="dev project"))
        
    assert user.get_project("DEV PROJECT").title == "Dev Project"
    
    user.remove_project("dev project")
    with pytest.raises(ProjectNotFoundError):
        user.get_project("Dev Project")
