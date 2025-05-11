"""Tests for the ProjectEnvironment class."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from openmas.cli.project_env import ProjectEnvironment
from openmas.config import AgentConfigEntry, ProjectConfig


class TestProjectEnvironment:
    """Tests for the ProjectEnvironment class."""

    def test_setup_environment_path_manipulation(self):
        """Test that setup_environment correctly modifies sys.path."""
        # Mock dependencies
        mock_project_root = Path("/fake/project")

        # Create a realistic project config with proper AgentConfigEntry
        test_agent_entry = AgentConfigEntry(
            module="agents.test_agent",
            class_="Agent",  # Required field
            description="Test agent",
        )

        mock_project_config = MagicMock(spec=ProjectConfig)
        mock_project_config.agents = {"test_agent": test_agent_entry}
        mock_project_config.shared_paths = ["shared"]
        mock_project_config.extension_paths = ["extensions"]

        # Create the ProjectEnvironment instance
        with (
            patch("sys.path", new_callable=list) as mock_sys_path,
            patch("os.environ", {}),
            patch("pathlib.Path.exists", return_value=True),
            patch("openmas.cli.project_env.add_package_paths_to_sys_path") as mock_add_packages,
        ):
            # Setup the test environment
            original_path = ["/original/path1", "/original/path2"]
            mock_sys_path.extend(original_path)

            # Create and call the ProjectEnvironment
            env = ProjectEnvironment(mock_project_root, mock_project_config)
            env.setup_environment("test_agent")

            # Assert sys.path has been modified correctly with expected paths
            assert str(mock_project_root) in mock_sys_path
            assert str(mock_project_root / "agents" / "test_agent") in mock_sys_path
            assert str(mock_project_root / "agents") in mock_sys_path
            assert str(mock_project_root / "shared") in mock_sys_path
            assert str(mock_project_root / "extensions") in mock_sys_path

            # Assert packages were processed
            mock_add_packages.assert_called_once_with(mock_project_root / "packages")

            # Assert environment variables are set correctly
            assert os.environ["OPENMAS_PROJECT_ROOT"] == str(mock_project_root)
            assert os.environ["AGENT_NAME"] == "test_agent"
            assert os.environ["OPENMAS_ENV"] == "development"

    def test_setup_environment_with_path_based_module(self):
        """Test setup_environment with a path-based module name."""
        # Mock dependencies
        mock_project_root = Path("/fake/project")

        # Create a proper AgentConfigEntry with path-based module format
        test_agent_entry = AgentConfigEntry(
            module="agents/test_agent",  # Path-based format
            class_="Agent",  # Required field
            description="Test agent",
        )

        # Create a realistic project config
        mock_project_config = MagicMock(spec=ProjectConfig)
        mock_project_config.agents = {"test_agent": test_agent_entry}
        mock_project_config.shared_paths = []
        mock_project_config.extension_paths = []

        # Create the ProjectEnvironment instance
        with (
            patch("sys.path", new_callable=list) as mock_sys_path,
            patch("os.environ", {}),
            patch("pathlib.Path.exists", return_value=False),
            patch("openmas.cli.project_env.add_package_paths_to_sys_path") as mock_add_packages,
        ):
            # Setup the test environment
            original_path = ["/original/path1", "/original/path2"]
            mock_sys_path.extend(original_path)

            # Create and call the ProjectEnvironment
            env = ProjectEnvironment(mock_project_root, mock_project_config)
            env.setup_environment("test_agent")

            # Assert path-based module path is handled correctly
            assert str(mock_project_root / "agents" / "test_agent") in mock_sys_path
            assert str(mock_project_root / "agents") in mock_sys_path

            # Packages directory doesn't exist in this test
            mock_add_packages.assert_not_called()

    @patch("openmas.cli.project_env.ProjectEnvironment.setup_environment")
    def test_restore_environment(self, mock_setup):
        """Test that restore_environment correctly restores sys.path."""
        # Mock dependencies
        mock_project_root = Path("/fake/project")
        mock_project_config = MagicMock(spec=ProjectConfig)

        # Create a proper AgentConfigEntry
        test_agent_entry = AgentConfigEntry(
            module="dummy_module",
            class_="Agent",  # Required field
        )
        mock_project_config.agents = {"test_agent": test_agent_entry}

        # Create the ProjectEnvironment instance
        with patch("sys.path") as mock_sys_path:
            # Setup original sys.path
            original_path = ["/original/path1", "/original/path2"]
            mock_sys_path.__iter__.return_value = original_path.copy()

            # Create a ProjectEnvironment that stores the original sys.path
            env = ProjectEnvironment(mock_project_root, mock_project_config)

            # Mock that setup_environment was called and modified sys.path
            # by setting the added_paths list directly
            env.original_sys_path = original_path.copy()
            env.added_paths = ["/fake/project", "/fake/project/dummy_module"]

            # Call restore
            env.restore_environment()

            # Verify mock_sys_path was reset to the original value
            mock_sys_path.clear.assert_called_once()
            mock_sys_path.extend.assert_called_once_with(original_path)
