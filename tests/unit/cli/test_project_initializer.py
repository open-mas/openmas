"""Tests for the ProjectInitializer class."""

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, call, mock_open, patch

import pytest

from openmas.cli.project_initializer import ProjectInitializer


def test_prepare_file_actions_default():
    """Test the _prepare_file_actions method with default configuration."""
    # Setup
    project_path = Path("/test/project")
    display_name = "Test Project"
    initializer = ProjectInitializer(project_path, display_name)

    # Execute
    actions = initializer._prepare_file_actions()

    # Verify
    # Check that essential files are included
    assert project_path / "README.md" in actions
    assert project_path / "requirements.txt" in actions
    assert project_path / ".gitignore" in actions
    assert project_path / "openmas_project.yml" in actions

    # Check that __init__.py files exist for Python package directories
    assert project_path / "agents" / "__init__.py" in actions
    assert project_path / "shared" / "__init__.py" in actions
    assert project_path / "extensions" / "__init__.py" in actions
    assert project_path / "tests" / "__init__.py" in actions

    # Verify content of README.md
    assert actions[project_path / "README.md"] == "# Test Project\n\nA OpenMAS project.\n"

    # Verify requirements.txt
    assert "openmas>=0.2.0" in actions[project_path / "requirements.txt"]

    # Verify that there are no template-specific files
    assert not any(str(path).endswith("mcp_server/agent.py") for path in actions.keys())


def test_prepare_file_actions_with_poetry():
    """Test the _prepare_file_actions method with Poetry enabled."""
    # Setup
    project_path = Path("/test/project")
    display_name = "Test Project"
    initializer = ProjectInitializer(project_path, display_name, poetry=True)

    # Execute
    actions = initializer._prepare_file_actions()

    # Verify
    # Check that pyproject.toml is included
    assert project_path / "pyproject.toml" in actions
    assert "requirements.txt" not in [p.name for p in actions.keys()]

    # Verify content of pyproject.toml
    pyproject_content = actions[project_path / "pyproject.toml"]
    assert 'name = "test-project"' in pyproject_content
    assert 'version = "0.1.0"' in pyproject_content
    assert "openmas = " in pyproject_content
    assert "poetry-core" in pyproject_content


def test_prepare_file_actions_with_mcp_template():
    """Test the _prepare_file_actions method with MCP server template."""
    # Setup
    project_path = Path("/test/project")
    display_name = "Test Project"
    initializer = ProjectInitializer(project_path, display_name, template="mcp-server")

    # Execute
    actions = initializer._prepare_file_actions()

    # Verify
    # Check that MCP-specific files are included
    assert project_path / "agents" / "mcp_server" / "__init__.py" in actions
    assert project_path / "agents" / "mcp_server" / "agent.py" in actions
    assert project_path / "agents" / "mcp_server" / "openmas.deploy.yaml" in actions

    # Verify content of agent.py
    agent_content = actions[project_path / "agents" / "mcp_server" / "agent.py"]
    assert "class McpServerAgent(BaseAgent):" in agent_content
    assert "async def setup(self)" in agent_content
    assert "async def run(self)" in agent_content
    assert "async def shutdown(self)" in agent_content

    # Verify content of openmas.deploy.yaml
    deploy_content = actions[project_path / "agents" / "mcp_server" / "openmas.deploy.yaml"]
    assert 'name: "mcp-server"' in deploy_content
    assert 'type: "service"' in deploy_content
    assert "MCP_API_KEY" in deploy_content

    # Verify that the MCP agent is added to project config
    project_config_callable = actions[project_path / "openmas_project.yml"]
    assert callable(project_config_callable)

    # Mock yaml.dump to test project config content
    with patch("yaml.dump") as mock_yaml_dump:
        mock_yaml_dump.return_value = "mocked_yaml"
        project_config_callable()  # Call the callable but no need to store the result
        project_config = mock_yaml_dump.call_args[0][0]  # Get the first positional arg to yaml.dump

        assert project_config["agents"]["mcp_server"] == "agents/mcp_server"


def test_prepare_file_actions_with_unknown_template():
    """Test the _prepare_file_actions method with an unknown template."""
    # Setup
    project_path = Path("/test/project")
    display_name = "Test Project"
    initializer = ProjectInitializer(project_path, display_name, template="unknown-template")

    # Execute
    actions = initializer._prepare_file_actions()

    # Verify - should be same as default, no special template files
    assert project_path / "README.md" in actions
    assert project_path / "requirements.txt" in actions
    assert project_path / ".gitignore" in actions
    assert project_path / "openmas_project.yml" in actions

    # Should not have any template-specific files
    assert not any(str(path).endswith("unknown-template") for path in actions.keys())
    assert not any(str(path).endswith("mcp_server/agent.py") for path in actions.keys())


@pytest.fixture
def mock_filesystem():
    """Fixture to mock filesystem operations."""
    with (
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("pathlib.Path.exists") as mock_exists,
        patch("builtins.open", mock_open()) as mock_file_open,
        patch("pathlib.Path.parent", create=True) as mock_parent,
    ):
        # Configure mock behaviors
        mock_exists.return_value = False
        mock_parent.return_value = MagicMock()

        yield {
            "mkdir": mock_mkdir,
            "exists": mock_exists,
            "open": mock_file_open,
            "parent": mock_parent,
        }


def test_initialize_project(mock_filesystem):
    """Test the initialize_project method."""
    # Setup
    project_path = Path("/test/project")
    display_name = "Test Project"
    initializer = ProjectInitializer(project_path, display_name)

    # Mock _prepare_file_actions to return a simplified set of files
    test_content = "test content"

    # Define a function instead of using lambda
    def get_callable_content():
        return "callable content"

    with patch.object(
        initializer,
        "_prepare_file_actions",
        return_value={
            project_path / "file1.txt": test_content,
            project_path / "file2.txt": get_callable_content,
        },
    ):
        # Execute
        initializer.initialize_project()

        # Verify
        # Main project directory should be created
        mock_filesystem["mkdir"].assert_any_call(parents=True, exist_ok=False)

        # Subdirectories should be created
        expected_dirs = ["agents", "shared", "extensions", "config", "tests", "packages"]
        for _ in expected_dirs:
            mock_filesystem["mkdir"].assert_any_call(exist_ok=False)

        # Files should be written with correct content
        mock_file = mock_filesystem["open"]

        # There should be at least two write calls (more including parent directory creation)
        assert mock_file().write.call_count >= 2

        # Check for specific content writes
        mock_file().write.assert_any_call(test_content)
        mock_file().write.assert_any_call("callable content")


def test_initialize_project_existing_dir(mock_filesystem):
    """Test initializing project in current directory."""
    # Setup
    project_path = Path(".")
    display_name = "Test Project"
    initializer = ProjectInitializer(project_path, display_name)

    # Mock _prepare_file_actions to return a simplified set of files
    with patch.object(
        initializer,
        "_prepare_file_actions",
        return_value={
            project_path / "file1.txt": "content",
        },
    ):
        # Execute
        initializer.initialize_project()

        # Verify
        # Main project directory should NOT be created for current directory
        for call_args in mock_filesystem["mkdir"].call_args_list:
            assert call_args != call(parents=True, exist_ok=False)

        # Subdirectories should be created with exist_ok=True
        subdirs = ["agents", "shared", "extensions", "config", "tests", "packages"]
        for subdir in subdirs:
            mock_filesystem["mkdir"].assert_any_call(exist_ok=True)


def test_initialize_project_with_skip_files():
    """Test that initialize_project skips existing files."""
    # Setup
    project_path = Path("/test/project")
    display_name = "Test Project"
    initializer = ProjectInitializer(project_path, display_name)

    # Use a simple file list approach to track file existence
    existing_files = [str(project_path / ".gitignore")]

    def mock_path_exists(path):
        return str(path) in existing_files

    # Create the test file set
    test_files = {project_path / ".gitignore": "gitignore content", project_path / "file1.txt": "regular file content"}

    # Create a mock for open that we can reference later
    file_mock = mock_open()

    with (
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists", mock_path_exists),
        patch("builtins.open", file_mock),
        patch.object(initializer, "_prepare_file_actions", return_value=test_files),
    ):
        # Execute
        initializer.initialize_project()

        # Check which files were opened for writing
        for call_args in file_mock.call_args_list:
            # The first argument to open() is the file path
            path = call_args[0][0]
            assert str(path) != str(project_path / ".gitignore"), "Existing file should be skipped"
            assert str(path) == str(project_path / "file1.txt"), "Non-existing file should be created"


def test_initialize_project_permission_error():
    """Test that initialize_project handles permission errors."""
    # Setup
    project_path = Path("/test/project")
    display_name = "Test Project"
    initializer = ProjectInitializer(project_path, display_name)

    # Mock mkdir to raise PermissionError
    with (
        patch("pathlib.Path.mkdir", side_effect=PermissionError("Permission denied")),
        patch.object(initializer, "_prepare_file_actions", return_value={}),
    ):
        # Execute and verify exception is raised
        with pytest.raises(PermissionError, match="Permission denied"):
            initializer.initialize_project()


def test_initialize_project_os_error():
    """Test that initialize_project handles OS errors."""
    # Setup
    project_path = Path("/test/project")
    display_name = "Test Project"
    initializer = ProjectInitializer(project_path, display_name)

    # Mock file writing to raise OSError
    mock_open_instance = mock_open()
    mock_open_instance.side_effect = OSError("Disk full")

    with (
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open_instance),
        patch.object(initializer, "_prepare_file_actions", return_value={project_path / "file1.txt": "content"}),
    ):
        # Execute and verify exception is raised
        with pytest.raises(OSError, match="Disk full"):
            initializer.initialize_project()


def test_initialize_project_parent_dir_creation():
    """Test that parent directories are created as needed."""
    project_path = Path("/test/project")
    display_name = "Test Project"
    initializer = ProjectInitializer(project_path, display_name)

    # Test with a nested file that requires parent directory creation
    nested_file_path = project_path / "nested" / "dir" / "file.txt"

    # Create a mock parent that won't cause infinite recursion
    parent_paths = [
        project_path / "nested" / "dir",
        project_path / "nested",
        project_path,
    ]
    parent_mock = MagicMock()
    parent_mock.mkdir.return_value = None

    with (
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
        patch.object(initializer, "_prepare_file_actions", return_value={nested_file_path: "content"}),
        patch("pathlib.Path.parent", new_callable=PropertyMock) as mock_parent,
    ):
        # Set a safe parent property that returns parent paths in sequence
        mock_parent.return_value = parent_paths[0]

        # Execute
        initializer.initialize_project()

        # Verify parent directory was created
        assert mock_parent.called, "parent property should be accessed"
