"""Test the environment cleanup behavior in the run_project function."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

import openmas.cli.run
from openmas.cli.run import run_project
from openmas.config import ProjectConfig
from openmas.exceptions import ConfigurationError


def test_environment_cleanup_on_error():
    """Test that project environment is always restored, even when there's an error."""
    # Create a class to track method calls
    setup_called = False
    restore_called = False

    class TestProjectEnvironment:
        def __init__(self, project_root, project_config):
            self.project_root = project_root
            self.project_config = project_config

        def setup_environment(self, agent_name):
            nonlocal setup_called
            setup_called = True
            # Raise an error to trigger finally block
            raise ConfigurationError("Test error")

        def restore_environment(self):
            nonlocal restore_called
            restore_called = True

    # Save original class for restoration
    original_env_class = openmas.cli.run.ProjectEnvironment

    try:
        # Replace with our test class
        openmas.cli.run.ProjectEnvironment = TestProjectEnvironment

        # Patch dependencies
        with (
            patch("openmas.cli.run.find_project_root") as mock_find_root,
            patch("openmas.cli.run.load_project_config") as mock_load_config,
            patch("openmas.cli.run.validate_agent_in_config"),
            patch("click.echo"),
        ):
            # Configure mocks
            mock_find_root.return_value = Path("/test/project")
            mock_load_config.return_value = MagicMock(spec=ProjectConfig)

            # Call the function with expected error
            with pytest.raises(typer.Exit):
                run_project("test_agent")

            # Verify both methods were called
            assert setup_called, "setup_environment was not called"
            assert restore_called, "restore_environment was not called in finally block"

    finally:
        # Restore original class
        openmas.cli.run.ProjectEnvironment = original_env_class
