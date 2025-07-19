"""Tests for environment variables handling in CLI."""

import os
from unittest.mock import MagicMock, patch

import pytest

from openmas.config import AgentConfig, ProjectConfig


@pytest.fixture
def mock_project_config():
    """Create a mocked project config."""
    agent_config = AgentConfig(name="test_agent", module="test_agent_module", class_="Agent")
    config = ProjectConfig(
        name="test_project",
        description="Test project for environment vars",
        version="0.1.0",
        agents={"test_agent": agent_config},
    )
    return config


def test_running_project_with_different_environment_vars(mock_project_config):
    """Test that running a project with different environment vars works correctly."""
    original_env = os.environ.copy()

    try:
        # Mock the necessary components
        with (
            patch("openmas.cli.run.load_project_config", return_value=mock_project_config),
            patch("openmas.cli.run.find_project_root", return_value="."),
            patch("openmas.cli.run.AgentLoader") as mock_agent_loader,
            patch("openmas.cli.run.ProjectEnvironment") as mock_proj_env,
            patch("openmas.cli.run.AgentExecutor"),  # We don't need to store this mock
            patch("openmas.cli.run.load_agent_class"),
            patch("openmas.cli.run.initialize_agent"),
            patch("openmas.cli.run.validate_agent_in_config", return_value=mock_project_config.agents["test_agent"]),
        ):
            # Configure mocks
            mock_agent = MagicMock()
            mock_agent_class = MagicMock(return_value=mock_agent)
            mock_agent_loader.return_value.load_agent_class.return_value = mock_agent_class

            # Import the function we want to test
            from openmas.cli.run import run_project

            # Test with development environment
            with patch.dict(os.environ, {"OPENMAS_ENV": "development"}, clear=True):
                # Run the function that we're testing
                run_project("test_agent")

                # Verify environment was used correctly
                mock_proj_env_instance = mock_proj_env.return_value
                mock_proj_env_instance.setup_environment.assert_called_once_with("test_agent")
                assert os.environ.get("OPENMAS_ENV") == "development"

            # Test with production environment
            mock_proj_env.reset_mock()
            with patch.dict(os.environ, {"OPENMAS_ENV": "production"}, clear=True):
                # Run the function that we're testing
                run_project("test_agent")

                # Verify environment was used correctly
                mock_proj_env_instance = mock_proj_env.return_value
                mock_proj_env_instance.setup_environment.assert_called_once_with("test_agent")
                assert os.environ.get("OPENMAS_ENV") == "production"

    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)
