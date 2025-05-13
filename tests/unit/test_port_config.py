"""Unit tests for port configuration in OpenMAS."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from openmas.agent.base import BaseAgent
from openmas.cli.run import find_project_root, initialize_agent, run_project
from openmas.config import AgentConfig, ProjectConfig


class TestPortConfiguration:
    """Tests for port configuration handling in OpenMAS."""

    def test_project_dir_propagation(self):
        """find_project_root should call _find_project_root with the supplied path."""
        test_path = Path("/test/path")

        with patch("openmas.cli.run._find_project_root") as mock_find:
            mock_find.return_value = test_path
            result = find_project_root(test_path)

            mock_find.assert_called_once_with(test_path)
            assert result == test_path

    def test_run_project_uses_provided_project_dir(self):
        """run_project should pass the supplied project_dir through the call-chain."""
        test_path = Path("/test/path")

        with (
            patch("openmas.cli.run.find_project_root") as mock_find,
            patch("openmas.cli.run.load_project_config"),
            patch("openmas.cli.run.validate_agent_in_config"),
            patch("openmas.cli.run.verify_communicator_dependencies"),
            patch("openmas.cli.run.ProjectEnvironment"),
            patch("openmas.cli.run.AgentLoader"),
            patch("openmas.cli.run.load_agent_class"),
            patch("openmas.cli.run.load_environment_config"),
            patch("openmas.cli.run.create_asset_manager"),
            patch("openmas.cli.run.initialize_agent"),
            patch("openmas.cli.run.AgentExecutor"),
        ):
            mock_find.return_value = test_path
            run_project("test_agent", project_dir=test_path)
            mock_find.assert_called_once_with(test_path)

    def test_initialize_agent_preserves_http_port(self):
        """initialize_agent should keep explicit http_port in communicator_options intact."""
        project_config = ProjectConfig(
            name="test",
            version="0.1.0",
            agents={"test_agent": AgentConfig(name="test_agent")},
        )

        agent_config = AgentConfig(
            name="test_agent",
            communicator_type="mcp-sse",
            communicator_options={"http_port": 9999},
        )

        mock_agent_class = MagicMock()
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        project_root = Path("/test/path")

        initialize_agent(
            mock_agent_class,
            "test_agent",
            project_config,
            {},  # env_config
            agent_config,
            None,  # asset_manager
            project_root,
        )

        mock_agent_class.assert_called_once()
        _, kwargs = mock_agent_class.call_args
        assert kwargs["config"]["communicator_options"]["http_port"] == 9999
        assert kwargs["config"]["communicator_type"] == "mcp-sse"
        assert kwargs["project_root"] == project_root

    def test_agent_executor_uses_passed_project_dir(self):
        """The project_dir passed to run_project should flow to initialize_agent and AgentExecutor."""
        test_path = Path("/test/path")

        mock_agent = MagicMock(spec=BaseAgent)
        mock_agent.config = MagicMock()
        mock_agent.config.communicator_type = "mcp-sse"
        mock_agent.config.communicator_options = {"http_port": 9999}

        mock_agent_class = MagicMock(return_value=mock_agent)
        mock_project_config = MagicMock(spec=ProjectConfig)
        mock_project_config.name = "test"
        mock_project_config.version = "0.1.0"

        mock_agent_config = MagicMock(spec=AgentConfig)
        mock_agent_config.name = "test_agent"
        mock_agent_config.communicator = None
        mock_agent_config.communicator_type = "mcp-sse"
        mock_agent_config.communicator_options = {"http_port": 9999}
        mock_agent_config.module = "test_module"
        mock_agent_config.class_ = "Agent"

        mock_project_config.agents = {"test_agent": mock_agent_config}
        mock_project_config.default_config = {}
        mock_project_config.communicator_defaults = {}

        with (
            patch("openmas.cli.run.find_project_root", return_value=test_path) as mock_find,
            patch("openmas.cli.run.load_project_config", return_value=mock_project_config),
            patch("openmas.cli.run.validate_agent_in_config", return_value=mock_agent_config),
            patch("openmas.cli.run.verify_communicator_dependencies"),
            patch("openmas.cli.run.ProjectEnvironment"),
            patch("openmas.cli.run.AgentLoader"),
            patch("openmas.cli.run.load_agent_class", return_value=mock_agent_class),
            patch("openmas.cli.run.load_environment_config", return_value={}),
            patch("openmas.cli.run.create_asset_manager", return_value=None),
            patch("openmas.cli.run.initialize_agent", return_value=mock_agent) as mock_init,
            patch("openmas.cli.run.AgentExecutor") as mock_executor,
        ):
            run_project("test_agent", project_dir=test_path)

            mock_find.assert_called_once_with(test_path)
            mock_init.assert_called_once()
            init_args, _ = mock_init.call_args
            assert init_args[-1] == test_path

            mock_executor.assert_called_once()
            exec_args, _ = mock_executor.call_args
            assert exec_args[0] == mock_agent
