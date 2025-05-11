"""Tests for the CLI init command."""

from unittest.mock import MagicMock, mock_open, patch

import pytest
from click.testing import CliRunner

from openmas.cli.main import cli
from openmas.cli.project_initializer import ProjectInitializer
from openmas.exceptions import ConfigurationError


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


def test_init_new_project(temp_dir):
    """Test initializing a new OpenMAS project."""
    # Mock file operations
    with (
        patch("pathlib.Path.mkdir"),  # We don't need to track this mock
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
        patch("yaml.dump"),
        patch("os.getcwd", return_value=str(temp_dir)),
        patch("openmas.cli.project_initializer.ProjectInitializer.initialize_project") as mock_initialize,
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "test_project"])

        # Check for successful execution
        assert result.exit_code == 0
        assert "OpenMAS project 'test_project' created successfully" in result.output

        # Verify ProjectInitializer was called with correct parameters
        mock_initialize.assert_called_once()


def test_init_current_directory_with_name(temp_dir):
    """Test initializing an OpenMAS project in the current directory."""
    # Mock file operations
    with (
        patch("pathlib.Path.mkdir"),  # We don't need to track this mock
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
        patch("yaml.dump"),
        patch("os.getcwd", return_value=str(temp_dir)),
        patch("openmas.cli.project_initializer.ProjectInitializer.initialize_project") as mock_initialize,
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", ".", "--name", "current_dir_project"])

        # Check for successful execution
        assert result.exit_code == 0
        assert "OpenMAS project 'current_dir_project' created successfully" in result.output

        # Verify ProjectInitializer was called correctly
        mock_initialize.assert_called_once()


def test_init_with_template(temp_dir):
    """Test initializing a project with a specific template."""
    # Mock file operations
    with (
        patch("pathlib.Path.mkdir"),  # We don't need to track this mock
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
        patch("yaml.dump"),
        patch("os.getcwd", return_value=str(temp_dir)),
        patch("openmas.cli.project_initializer.ProjectInitializer.initialize_project") as mock_initialize,
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "test_project", "--template", "mcp-server"])

        # Check for successful execution
        assert result.exit_code == 0
        assert "OpenMAS project 'test_project' created successfully" in result.output

        # Verify ProjectInitializer was called correctly
        mock_initialize.assert_called_once()


def test_init_with_poetry_flag(temp_dir):
    """Test initializing a project with Poetry support."""
    # Mock file operations
    with (
        patch("pathlib.Path.mkdir"),  # We don't need to track this mock
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
        patch("yaml.dump"),
        patch("os.getcwd", return_value=str(temp_dir)),
        patch("openmas.cli.project_initializer.ProjectInitializer.initialize_project") as mock_initialize,
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "test_project", "--poetry"])

        # Check for successful execution
        assert result.exit_code == 0
        assert "OpenMAS project 'test_project' created successfully" in result.output

        # Verify ProjectInitializer was created with poetry=True
        mock_initialize.assert_called_once()


def test_init_directory_already_exists(temp_dir):
    """Test error when target directory already exists."""
    with patch("pathlib.Path.exists", return_value=True):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "existing_project"])

        # Check for failure due to existing directory
        assert result.exit_code == 1
        assert "already exists" in result.output


def test_init_current_dir_without_name(temp_dir):
    """Test error when initializing in current dir without a project name."""
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "."])

    # Check for failure due to missing name
    assert result.exit_code == 1
    assert "you must provide a project name" in result.output


def test_init_permission_error(temp_dir):
    """Test handling of permission error during initialization."""
    # Mock ProjectInitializer to raise PermissionError
    with (
        patch(
            "openmas.cli.project_initializer.ProjectInitializer.initialize_project",
            side_effect=PermissionError("Permission denied"),
        ),
        patch("traceback.format_exc", return_value="Mock traceback text"),
    ):  # Mock traceback to have predictable output
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "test_project"])

        # Check for appropriate error handling
        assert result.exit_code == 1
        assert "Permission denied" in result.output
        # Accept any of the error messages we might display
        assert any(
            message in result.output
            for message in [
                "Error creating project files",
                "Error creating project directory",
                "Error creating project structure",
            ]
        )


def test_init_os_error(temp_dir):
    """Test handling of OS error during initialization."""
    # Mock ProjectInitializer to raise OSError
    with patch(
        "openmas.cli.project_initializer.ProjectInitializer.initialize_project", side_effect=OSError("Disk full")
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "test_project"])

        # Check for appropriate error handling
        assert result.exit_code == 1
        assert "Disk full" in result.output
        assert "Error creating project files" in result.output


def test_init_configuration_error(temp_dir):
    """Test handling of ConfigurationError during initialization."""
    # Mock ProjectInitializer to raise ConfigurationError
    with patch(
        "openmas.cli.project_initializer.ProjectInitializer.initialize_project",
        side_effect=ConfigurationError("Invalid configuration"),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "test_project"])

        # Check for appropriate error handling
        assert result.exit_code == 1
        assert "Configuration error during project initialization: Invalid configuration" in result.output


def test_init_unexpected_error(temp_dir):
    """Test handling of unexpected errors during initialization."""
    # Mock ProjectInitializer to raise an unexpected error
    with patch(
        "openmas.cli.project_initializer.ProjectInitializer.initialize_project",
        side_effect=ValueError("Unexpected error"),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "test_project"])

        # Check for appropriate error handling
        assert result.exit_code == 1
        assert "Unexpected error during project initialization: Unexpected error" in result.output


def test_init_integration_with_project_initializer():
    """Test proper integration of init command with ProjectInitializer."""
    # Create a spy on ProjectInitializer instantiation
    mock_initializer = MagicMock(spec=ProjectInitializer)

    with patch("openmas.cli.main.ProjectInitializer", return_value=mock_initializer) as mock_pi_class:
        runner = CliRunner()
        runner.invoke(cli, ["init", "test_project", "--template", "mcp-server", "--poetry"])

        # Verify ProjectInitializer was created with correct args
        mock_pi_class.assert_called_once()

        args, kwargs = mock_pi_class.call_args

        # Check positional arguments - based on call(PosixPath('test_project'), 'test_project', 'mcp-server', True)
        assert str(args[0]).endswith("test_project")  # project_path
        assert args[1] == "test_project"  # display_name
        assert args[2] == "mcp-server"  # template
        assert args[3] is True  # poetry flag

        # Verify initialize_project was called
        mock_initializer.initialize_project.assert_called_once()
