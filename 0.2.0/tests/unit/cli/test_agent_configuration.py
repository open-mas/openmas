"""Unit tests for agent configuration in the CLI."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from openmas.cli.run import initialize_agent
from openmas.config import AgentConfig, ProjectConfig


@pytest.fixture
def mock_agent_class():
    """Create a mock agent class for testing."""
    mock_agent = MagicMock()
    mock_agent_class = MagicMock()
    mock_agent_class.return_value = mock_agent
    return mock_agent_class


@pytest.fixture
def mock_project_config():
    """Create a mock project configuration."""
    config = MagicMock(spec=ProjectConfig)
    config.default_config = {"log_level": "INFO"}
    config.communicator_defaults = {"type": "mcp-sse", "options": {"server_mode": True, "http_port": 8000}}
    return config


@pytest.fixture
def agent_config_entry():
    """Create an agent config entry for testing."""
    return AgentConfig(
        name="test_agent",
        module="agents.test_agent",
        class_="TestAgent",
        communicator="http",
        communicator_options={"timeout": 30},
    )


def test_initialize_agent_with_direct_config(mock_agent_class, mock_project_config, agent_config_entry):
    """Test that agent configuration is properly applied."""
    # Update the agent config entry with direct configuration
    agent_config_entry.communicator = "mcp-sse"
    agent_config_entry.communicator_options = {"server_mode": True, "http_port": 9900, "http_host": "127.0.0.1"}

    # Create a test project root
    test_project_root = Path("/test/path")

    # Initialize agent
    with patch("openmas.cli.run.verify_communicator_dependencies"), patch("click.echo"):
        initialize_agent(
            agent_class=mock_agent_class,
            agent_name="test_agent",
            project_config=mock_project_config,
            env_config={},
            agent_config_entry=agent_config_entry,
            asset_manager=None,
            project_root=test_project_root,
        )

    # Verify that the configuration was passed correctly
    mock_agent_class.assert_called_once()
    _, kwargs = mock_agent_class.call_args

    # Verify config values
    assert kwargs["config"].communicator == "mcp-sse"
    assert kwargs["config"].communicator_options["server_mode"] is True
    assert kwargs["config"].communicator_options["http_port"] == 9900
    assert kwargs["config"].communicator_options["http_host"] == "127.0.0.1"


def test_config_merge_precedence(mock_agent_class, mock_project_config, agent_config_entry):
    """Test the correct precedence order for configuration merging."""
    # Set up conflicting configurations with different priorities

    # 1. Default config (lowest priority)
    mock_project_config.communicator_defaults = {
        "type": "mcp-sse",
        "options": {"server_mode": True, "http_port": 8000, "http_host": "0.0.0.0"},
    }

    # 2. Environment-specific config (middle priority)
    env_config = {"communicator_options": {"http_port": 7777}}

    # 3. Agent-specific config in AgentConfig (highest priority)
    agent_config_entry.communicator_options = {"http_port": 9900, "http_host": "127.0.0.1"}

    # Create a test project root
    test_project_root = Path("/test/path")

    # Initialize agent
    with patch("openmas.cli.run.verify_communicator_dependencies"), patch("click.echo"):
        initialize_agent(
            agent_class=mock_agent_class,
            agent_name="test_agent",
            project_config=mock_project_config,
            env_config=env_config,
            agent_config_entry=agent_config_entry,
            asset_manager=None,
            project_root=test_project_root,
        )

    # Verify that the configuration was passed correctly
    mock_agent_class.assert_called_once()
    _, kwargs = mock_agent_class.call_args

    # Test that agent-specific config takes precedence
    assert kwargs["config"].communicator_options["http_port"] == 9900
    assert kwargs["config"].communicator_options["http_host"] == "127.0.0.1"
    # Ensure other values are from the correct sources
    assert kwargs["config"].communicator_type == "http"  # From agent_config_entry.communicator
