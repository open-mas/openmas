"""Tests for the CLI init command."""

from unittest.mock import mock_open, patch

import pytest
from click.testing import CliRunner

from openmas.cli.main import cli


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


def test_init_new_project(temp_dir):
    """Test initializing a new OpenMAS project."""
    # Mock file operations
    with (
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
        patch("yaml.dump"),
        patch("os.getcwd", return_value=str(temp_dir)),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "test_project"])

        # Check for successful execution
        assert result.exit_code == 0
        assert "OpenMAS project 'test_project' created successfully" in result.output

        # Verify directories were created
        mock_mkdir.assert_called()


def test_init_current_directory_with_name(temp_dir):
    """Test initializing an OpenMAS project in the current directory."""
    # Mock file operations
    with (
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
        patch("yaml.dump"),
        patch("os.getcwd", return_value=str(temp_dir)),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", ".", "--name", "current_dir_project"])

        # Check for successful execution
        assert result.exit_code == 0
        assert "OpenMAS project 'current_dir_project' created successfully" in result.output

        # Verify directories were created
        mock_mkdir.assert_called()


def test_init_with_template(temp_dir):
    """Test initializing a project with a specific template."""
    # Mock file operations
    with (
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
        patch("yaml.dump"),
        patch("os.getcwd", return_value=str(temp_dir)),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "test_project", "--template", "mcp-server"])

        # Check for successful execution
        assert result.exit_code == 0
        assert "OpenMAS project 'test_project' created successfully" in result.output

        # Verify directories were created
        mock_mkdir.assert_called()


def test_init_with_poetry_flag(temp_dir):
    """Test initializing a project with Poetry support."""
    # Mock file operations
    with (
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
        patch("yaml.dump"),
        patch("os.getcwd", return_value=str(temp_dir)),
    ):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "test_project", "--poetry"])

        # Check for successful execution
        assert result.exit_code == 0
        assert "OpenMAS project 'test_project' created successfully" in result.output

        # Verify directories were created
        mock_mkdir.assert_called()
