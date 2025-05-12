"""Unit tests for agent configuration handling in OpenMAS."""

from unittest.mock import MagicMock, patch

from openmas.agent.base import BaseAgent


# Create a concrete test agent implementation to avoid abstract class instantiation error
class TestAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    async def setup(self):
        """Setup the agent."""
        pass

    async def run(self):
        """Run the agent."""
        pass

    async def shutdown(self):
        """Shutdown the agent."""
        pass


class TestAgentConfiguration:
    """Test suite for agent configuration handling."""

    def test_communicator_options_passed_to_communicator(self):
        """Test that communicator_options from agent config are passed to the communicator."""
        # Create a mock communicator class
        mock_communicator_class = MagicMock()

        # Create agent with communicator_options
        agent_config = {
            "name": "test_agent",
            "communicator_type": "http",
            "communicator_options": {"port": 9999, "some_option": "value"},
        }

        # Create the agent with the mock communicator class
        agent = TestAgent(config=agent_config, communicator_class=mock_communicator_class)

        # Verify the agent was created with the correct config
        assert agent.name == "test_agent"
        assert agent.config.communicator_type == "http"

        # Verify the communicator was initialized with the correct options
        mock_communicator_class.assert_called_once()
        args, kwargs = mock_communicator_class.call_args

        # Check that name and service_urls were passed as positional args
        assert args[0] == "test_agent"
        assert args[1] == {}  # Empty service_urls

        # Check that communicator_options were passed as kwargs
        assert "port" in kwargs
        assert kwargs["port"] == 9999
        assert "some_option" in kwargs
        assert kwargs["some_option"] == "value"

    @patch("openmas.communication.get_communicator_by_type")
    def test_port_configuration_from_agent_config(self, mock_get_communicator):
        """Test that port configuration is correctly passed from agent config to HTTP communicator."""
        # Create a mock HTTP communicator class
        mock_http_communicator = MagicMock()
        mock_get_communicator.return_value = mock_http_communicator

        # Create agent with port configuration
        agent_config = {"name": "test_agent", "communicator_type": "http", "communicator_options": {"port": 8888}}

        # Create the agent
        agent = TestAgent(config=agent_config)

        # Verify the agent was created successfully
        assert agent.name == "test_agent"

        # Verify the communicator was initialized with the port
        mock_http_communicator.assert_called_once()
        args, kwargs = mock_http_communicator.call_args
        assert "port" in kwargs
        assert kwargs["port"] == 8888

    @patch("openmas.communication.get_communicator_by_type")
    def test_custom_communicator_type_configuration(self, mock_get_communicator):
        """Test that a custom communicator type can be configured."""
        # Create a mock MCP SSE communicator
        mock_mcp_communicator = MagicMock()
        mock_get_communicator.return_value = mock_mcp_communicator

        # Create agent with MCP SSE communicator configuration
        agent_config = {
            "name": "test_agent",
            "communicator_type": "mcp-sse",
            "communicator_options": {"server_mode": True, "server_instructions": "Instructions for the server"},
        }

        # Create the agent
        agent = TestAgent(config=agent_config)

        # Verify the agent was created successfully
        assert agent.name == "test_agent"
        assert agent.config.communicator_type == "mcp-sse"

        # Verify that get_communicator_by_type was called with the correct type
        mock_get_communicator.assert_called_once_with("mcp-sse")

        # Verify the communicator options were passed
        mock_mcp_communicator.assert_called_once()
        args, kwargs = mock_mcp_communicator.call_args
        assert "server_mode" in kwargs
        assert kwargs["server_mode"] is True
        assert "server_instructions" in kwargs
        assert kwargs["server_instructions"] == "Instructions for the server"
