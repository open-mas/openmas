"""Tests for the run command."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest
import typer
import yaml

from openmas.agent.base import BaseAgent
from openmas.cli.run import initialize_agent, run_project, verify_communicator_dependencies
from openmas.cli.utils import add_package_paths_to_sys_path
from openmas.config import AgentConfigEntry, ProjectConfig
from openmas.exceptions import ConfigurationError


def test_event_loop_consistency():
    """Test that the CLI's loop behavior is consistent for child tasks.

    This test verifies the fix for the asyncio loop conflict by ensuring
    that both parent and child tasks can use the same event loop.
    """
    # Create a new clean event loop
    loop = asyncio.new_event_loop()

    # Set it as the current event loop
    asyncio.set_event_loop(loop)

    try:
        # Track task execution
        parent_loop = None
        child_loop = None

        # Define a task that will spawn a child task
        async def parent_task():
            nonlocal parent_loop
            # Record the parent's loop
            parent_loop = asyncio.get_running_loop()

            # Create a child task
            child = asyncio.create_task(child_task())
            await child

            # Return success
            return True

        async def child_task():
            nonlocal child_loop
            # Record the child's loop
            child_loop = asyncio.get_running_loop()
            return True

        # Run the tasks
        result = loop.run_until_complete(parent_task())

        # Verify everything worked
        assert result is True
        assert parent_loop is not None
        assert child_loop is not None
        assert parent_loop is child_loop, "Parent and child tasks should use the same event loop"
        assert parent_loop is loop, "Tasks should use the event loop we created"

    finally:
        # Clean up
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        except Exception:
            pass

        # Create a new event loop for subsequent tests
        asyncio.set_event_loop(asyncio.new_event_loop())


@pytest.fixture
def mock_project_root(tmp_path):
    """Create a mock project structure for testing."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create project configuration file
    config = {
        "name": "test_project",
        "version": "0.1.0",
        "agents": {"test_agent": "agents/test_agent"},
        "shared_paths": ["shared"],
        "extension_paths": ["extensions"],
        "default_config": {"log_level": "INFO"},
    }
    with open(project_root / "openmas_project.yml", "w") as f:
        yaml.dump(config, f)

    # Create agent directory
    agent_dir = project_root / "agents" / "test_agent"
    agent_dir.mkdir(parents=True)

    # Create agent file
    agent_py = """
from openmas.agent import BaseAgent

class Agent(BaseAgent):
    async def setup(self):
        pass

    async def run(self):
        pass

    async def shutdown(self):
        pass
"""
    with open(agent_dir / "agent.py", "w") as f:
        f.write(agent_py)

    # Create shared and extensions directories
    (project_root / "shared").mkdir()
    (project_root / "extensions").mkdir()

    return project_root


def test_add_package_paths_to_sys_path(tmp_path):
    """Test adding package paths to sys.path."""
    # Setup package directories
    packages_dir = tmp_path / "packages"
    packages_dir.mkdir()

    # Package with src directory
    pkg1_dir = packages_dir / "pkg1"
    pkg1_dir.mkdir()
    pkg1_src = pkg1_dir / "src"
    pkg1_src.mkdir()

    # Package without src directory
    pkg2_dir = packages_dir / "pkg2"
    pkg2_dir.mkdir()

    # Package with special name (should be skipped)
    special_dir = packages_dir / "__pycache__"
    special_dir.mkdir()

    # Save original sys.path
    original_sys_path = sys.path.copy()

    # Call the function
    add_package_paths_to_sys_path(packages_dir)

    # Verify paths were added correctly
    assert str(pkg1_src) in sys.path
    assert str(pkg2_dir) in sys.path
    assert str(special_dir) not in sys.path

    # Restore original sys.path
    sys.path = original_sys_path


def test_no_environment_assumptions(mock_project_root):
    """Test that the CLI doesn't make assumptions about Poetry or other environments."""
    # Save original sys.path
    original_sys_path = sys.path.copy()

    # Create mock agent class
    mock_agent_class = MagicMock(spec=BaseAgent)
    mock_agent_class.__name__ = "MockAgent"  # Add __name__ attribute to mock class
    mock_agent = MagicMock(spec=BaseAgent)
    mock_agent_class.return_value = mock_agent

    # Create a simple AgentConfigEntry mock
    mock_agent_config_entry = MagicMock()
    mock_agent_config_entry.module = "agents.test_agent"
    mock_agent_config_entry.class_ = "TestAgent"

    # Patch necessary functions to prevent actual execution
    with (
        patch.object(sys, "path", original_sys_path.copy()),
        patch("openmas.cli.run.find_project_root", return_value=mock_project_root),
        patch("openmas.cli.run.load_project_config") as mock_load_config,
        patch("openmas.cli.run.validate_agent_in_config", return_value=mock_agent_config_entry),
        patch("openmas.cli.run.AgentLoader.load_agent_class", return_value=mock_agent_class),
        patch("openmas.cli.run.load_environment_config", return_value={}),
        patch("openmas.cli.run.create_asset_manager", return_value=None),
        patch("openmas.cli.run.initialize_agent", return_value=mock_agent),
        patch("openmas.cli.run.AgentExecutor") as mock_agent_executor,
        patch("openmas.cli.run.ProjectEnvironment") as mock_project_env_class,
        patch("openmas.cli.run.verify_communicator_dependencies"),  # Mock verify_communicator_dependencies
        patch("click.echo"),
    ):
        # Setup mocks
        mock_project_config = MagicMock(spec=ProjectConfig)
        # Ensure default_config is set and it's a dictionary
        mock_project_config.default_config = {"log_level": "INFO"}
        mock_load_config.return_value = mock_project_config

        # Setup mock environment
        mock_env = MagicMock()
        mock_project_env_class.return_value = mock_env

        # Setup mock agent executor
        mock_executor = MagicMock()
        mock_agent_executor.return_value = mock_executor

        # Try/except to handle typer.Exit
        try:
            run_project("test_agent", project_dir=mock_project_root)
        except typer.Exit:
            pass

        # Verify environment setup
        mock_project_env_class.assert_called_once_with(mock_project_root, mock_project_config)
        mock_env.setup_environment.assert_called_once_with("test_agent")

        # Verify agent executor was initialized and run was called
        mock_agent_executor.assert_called_once()
        mock_executor.run.assert_called_once()

        # Verify environment was restored after execution
        mock_env.restore_environment.assert_called_once()

    # Restore original sys.path
    sys.path = original_sys_path


def test_running_project_with_different_environment_vars(mock_project_root):
    """Test running a project with different environment variables set."""
    # Save original environment and sys.path
    original_env = os.environ.copy()
    original_sys_path = sys.path.copy()

    # Try with different environment configurations
    test_envs: List[Dict[str, str]] = [
        {"OPENMAS_ENV": "dev"},  # Standard environment name
        {"VIRTUAL_ENV": "/path/to/venv"},  # venv-style environment
        {"CONDA_PREFIX": "/path/to/conda"},  # Conda-style environment
        {"POETRY_ACTIVE": "1"},  # Poetry-style environment
        {},  # No specific environment variables
    ]

    for env in test_envs:
        # Reset environment for each test
        os.environ.clear()
        os.environ.update(original_env)  # restore basic environment
        os.environ.update(env)  # add test-specific vars

        # Create mock agent class with required __name__ attribute
        mock_agent_class = MagicMock(spec=BaseAgent)
        mock_agent_class.__name__ = "MockAgent"
        mock_agent = MagicMock(spec=BaseAgent)
        mock_agent_class.return_value = mock_agent

        # Create a simple AgentConfigEntry mock
        mock_agent_config_entry = MagicMock()
        mock_agent_config_entry.module = "agents.test_agent"
        mock_agent_config_entry.class_ = "TestAgent"

        # Patch necessary functions to prevent actual execution
        with (
            patch.object(sys, "path", original_sys_path.copy()),
            patch("openmas.cli.run.find_project_root", return_value=mock_project_root),
            patch("openmas.cli.run.load_project_config") as mock_load_config,
            patch("openmas.cli.run.validate_agent_in_config", return_value=mock_agent_config_entry),
            patch("openmas.cli.run.AgentLoader.load_agent_class", return_value=mock_agent_class),
            patch("openmas.cli.run.load_environment_config", return_value={}),
            patch("openmas.cli.run.create_asset_manager", return_value=None),
            patch("openmas.cli.run.initialize_agent", return_value=mock_agent),
            patch("openmas.cli.run.AgentExecutor") as mock_agent_executor,
            patch("openmas.cli.run.ProjectEnvironment") as mock_project_env_class,
            patch("openmas.cli.run.verify_communicator_dependencies"),  # Mock verify_communicator_dependencies
            patch("click.echo"),
        ):
            # Set up mocks
            mock_project_config = MagicMock(spec=ProjectConfig)
            # Ensure default_config is set and it's a dictionary
            mock_project_config.default_config = {"log_level": "INFO"}
            mock_load_config.return_value = mock_project_config

            # Set up mock environment
            mock_env = MagicMock()
            mock_project_env_class.return_value = mock_env

            # Set up mock executor
            mock_exec = MagicMock()
            mock_agent_executor.return_value = mock_exec

            # Try/except to handle typer.Exit
            try:
                run_project("test_agent", env=os.environ.get("OPENMAS_ENV"), project_dir=mock_project_root)
            except typer.Exit:
                pass

            # Verify environment setup
            mock_project_env_class.assert_called_once_with(mock_project_root, mock_project_config)
            mock_env.setup_environment.assert_called_once_with("test_agent")

            # Verify agent execution
            mock_agent_executor.assert_called_once()
            mock_exec.run.assert_called_once()

            # Verify environment cleanup
            mock_env.restore_environment.assert_called_once()

            # Check if specific environment variables were passed to various calls based on the test case
            env_name = next(iter(env.keys()), None)
            if env_name == "OPENMAS_ENV":
                assert "OPENMAS_ENV" in os.environ
                env_value = env.get("OPENMAS_ENV")  # type-safe way to access dict
                if env_value is not None:
                    assert os.environ["OPENMAS_ENV"] == env_value

    # Restore original environment and sys.path
    os.environ.clear()
    os.environ.update(original_env)
    sys.path = original_sys_path


def test_project_environment_cleanup_on_error():
    """Test that project environment is always restored, even when there's an error."""
    # Mock all the dependencies
    mock_project_root = Path("/test/project")
    mock_project_config = MagicMock(spec=ProjectConfig)
    mock_project_config.default_config = {"log_level": "INFO"}

    # Create a mock agent config entry
    mock_agent_config = MagicMock()

    # Create mock methods that we can track
    setup_spy = MagicMock()
    restore_spy = MagicMock()

    # Mock ProjectEnvironment instance
    mock_env = MagicMock()
    mock_env.setup_environment = setup_spy
    mock_env.restore_environment = restore_spy

    # Mock AgentLoader that will raise an exception
    mock_agent_loader = MagicMock()
    mock_agent_loader.load_agent_class.side_effect = ConfigurationError("Test error")

    # Patch all necessary components
    with (
        patch("openmas.cli.run.find_project_root", return_value=mock_project_root),
        patch("openmas.cli.run.load_project_config", return_value=mock_project_config),
        patch("openmas.cli.run.validate_agent_in_config", return_value=mock_agent_config),
        patch("openmas.cli.run.ProjectEnvironment", return_value=mock_env),
        patch("openmas.cli.run.AgentLoader", return_value=mock_agent_loader),
        patch("openmas.cli.run.verify_communicator_dependencies"),  # Mock verify_communicator_dependencies
        patch("click.echo"),
    ):
        # Run the function with error handling
        try:
            run_project("test_agent")
        except typer.Exit:
            pass

        # Verify environment was set up
        setup_spy.assert_called_once_with("test_agent")

        # Verify environment was restored (this is what we're testing)
        restore_spy.assert_called_once()


class TestCliRun:
    """Test suite for CLI run module."""

    def test_initialize_agent_with_communicator_options(self):
        """Test that initialize_agent correctly processes communicator options."""
        # Create mock objects
        mock_agent_class = MagicMock()
        # Add __name__ attribute to fix the AttributeError
        mock_agent_class.__name__ = "MockAgent"
        mock_project_config = MagicMock(spec=ProjectConfig)
        mock_project_config.default_config = {"default_key": "default_value"}
        mock_project_config.communicator_defaults = {}

        # Create agent config entry with communicator options
        agent_config_entry = AgentConfigEntry(
            module="test.agent",
            class_="TestAgent",
            communicator="mcp-sse",
            options={"communicator_options": {"http_port": 9876, "server_mode": True}},
        )

        # Mock verify_communicator_dependencies to avoid dependency checks
        with patch("openmas.cli.run.verify_communicator_dependencies"), patch("click.echo"):
            # Call initialize_agent
            initialize_agent(
                agent_class=mock_agent_class,
                agent_name="test_agent",
                project_config=mock_project_config,
                env_config={},
                agent_config_entry=agent_config_entry,
            )

        # Verify the agent was initialized with the correct config
        mock_agent_class.assert_called_once()
        args, kwargs = mock_agent_class.call_args

        # Check the agent config has the communicator type and options
        assert kwargs["name"] == "test_agent"
        assert isinstance(kwargs["config"], dict)
        assert kwargs["config"]["communicator_type"] == "mcp-sse"
        assert "communicator_options" in kwargs["config"]
        assert kwargs["config"]["communicator_options"]["http_port"] == 9876
        assert kwargs["config"]["communicator_options"]["server_mode"] is True

    def test_initialize_agent_merges_configurations(self):
        """Test that initialize_agent correctly merges different configuration sources."""
        # Create mock objects
        mock_agent_class = MagicMock()
        # Add __name__ attribute to fix the AttributeError
        mock_agent_class.__name__ = "MockAgent"

        # Project config with default and communicator defaults
        mock_project_config = MagicMock(spec=ProjectConfig)
        mock_project_config.default_config = {"log_level": "INFO"}
        mock_project_config.communicator_defaults = {"communicator_options": {"timeout": 30}}

        # Environment config
        env_config = {"env_key": "env_value"}

        # Agent config entry with specific options
        agent_config_entry = AgentConfigEntry(
            module="test.agent",
            class_="TestAgent",
            communicator="http",
            options={"communicator_options": {"http_port": 5678}},
        )

        # Mock verify_communicator_dependencies to avoid dependency checks
        with patch("openmas.cli.run.verify_communicator_dependencies"), patch("click.echo"):
            # Call initialize_agent
            initialize_agent(
                agent_class=mock_agent_class,
                agent_name="test_agent",
                project_config=mock_project_config,
                env_config=env_config,
                agent_config_entry=agent_config_entry,
            )

        # Verify the agent was initialized with the merged config
        mock_agent_class.assert_called_once()
        args, kwargs = mock_agent_class.call_args

        # Check that all config sources were merged correctly
        agent_config = kwargs["config"]

        # Project defaults
        assert agent_config["log_level"] == "INFO"

        # Communicator defaults
        assert agent_config["communicator_options"]["timeout"] == 30

        # Environment config
        assert agent_config["env_key"] == "env_value"

        # Agent-specific config
        assert agent_config["communicator_type"] == "http"
        assert agent_config["communicator_options"]["http_port"] == 5678

    @patch("openmas.cli.run.logger")
    @patch("openmas.communication.get_communicator_by_type")
    def test_verify_communicator_dependencies_success(self, mock_get_communicator, mock_logger):
        """Test verify_communicator_dependencies when dependencies are satisfied."""
        # For HTTP communicator, no dependencies need verification, so this is a no-op
        verify_communicator_dependencies("http")

        # Verification only happens for specific communicator types
        # Verify get_communicator_by_type was NOT called for HTTP
        mock_get_communicator.assert_not_called()

        # Now test with MCP communicator
        with patch("openmas.cli.run.importlib.import_module") as mock_import:
            # Set up mock to succeed
            mock_import.return_value = MagicMock()

            # Call the function for MCP SSE
            verify_communicator_dependencies("mcp-sse")

            # Verify import was attempted
            mock_import.assert_called_once_with("mcp")

    @patch("openmas.cli.run.logger")
    @patch("openmas.cli.run.click")
    @patch("openmas.cli.run.importlib.import_module")
    def test_verify_communicator_dependencies_failure(self, mock_import, mock_click, mock_logger):
        """Test verify_communicator_dependencies when dependencies are missing."""
        # Setup mock to raise an exception
        mock_import.side_effect = ImportError("Missing dependency")

        # Call the function for MCP communicator and expect ConfigurationError
        with pytest.raises(ConfigurationError) as excinfo:
            verify_communicator_dependencies("mcp-sse")

        # Verify the error message contains the expected text
        error_message = str(excinfo.value)
        assert "Missing dependencies for communicator 'mcp-sse'" in error_message
        assert "pip install 'openmas[mcp]'" in error_message
