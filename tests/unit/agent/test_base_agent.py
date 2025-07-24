"""
Unit tests for the OpenMAS Base Agent implementation.

These tests validate the core agent functionality including lifecycle management,
SIMF message handling, capability management, and session management.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from openmas.agent import (
    Agent,
    AgentConfig,
    AgentError,
    AgentLifecycleError,
    AgentMessageError,
    IAgentStateManager,
    IProtocolAdapter,
)
from openmas.core.simf import (
    InvocationStatus,
    MessageFlowDirection,
    MessageType,
    SIMFMessage,
    create_invocation_message,
    create_text_message,
)

# ============================================================================
# Mock Implementations
# ============================================================================


class MockStateManager(IAgentStateManager):
    """Mock state manager for testing."""

    def __init__(self):
        self._state = {}

    async def set_state(self, key: str, value, scope: str = "PRIVATE_PERSISTENT") -> None:
        self._state[f"{scope}:{key}"] = value

    async def get_state(self, key: str, scope: str = "PRIVATE_PERSISTENT"):
        return self._state.get(f"{scope}:{key}")

    async def delete_state(self, key: str, scope: str = "PRIVATE_PERSISTENT") -> bool:
        key_with_scope = f"{scope}:{key}"
        if key_with_scope in self._state:
            del self._state[key_with_scope]
            return True
        return False

    async def has_state(self, key: str, scope: str = "PRIVATE_PERSISTENT") -> bool:
        return f"{scope}:{key}" in self._state

    async def list_state_keys(self, scope: str = "PRIVATE_PERSISTENT", prefix=None):
        keys = []
        scope_prefix = f"{scope}:"
        for key in self._state:
            if key.startswith(scope_prefix):
                state_key = key[len(scope_prefix) :]
                if prefix is None or state_key.startswith(prefix):
                    keys.append(state_key)
        return keys


class MockProtocolAdapter(IProtocolAdapter):
    """Mock protocol adapter for testing."""

    def __init__(self, protocol_name: str = "mock"):
        self.protocol_name = protocol_name
        self.connected = False
        self.config = {}
        self.message_callback = None
        self.sent_messages = []

    async def connect(self, config) -> None:
        self.config = config
        self.connected = True

    async def disconnect(self) -> None:
        self.connected = False

    async def send_message(self, internal_message: SIMFMessage) -> None:
        self.sent_messages.append(internal_message)

    async def register_message_callback(self, callback) -> None:
        self.message_callback = callback

    def to_internal_format(self, protocol_message) -> SIMFMessage:
        # Simple mock conversion
        return create_text_message(
            text=str(protocol_message),
            target_agent_id="mock_agent",
            source_agent_id="external",
        )

    def from_internal_format(self, internal_message: SIMFMessage):
        # Simple mock conversion
        return f"MOCK:{internal_message.message_type}:{internal_message.payload}"


# ============================================================================
# Test Classes
# ============================================================================


class TestAgentConfig:
    """Test the AgentConfig class."""

    def test_agent_config_creation(self):
        """Test basic agent configuration creation."""
        config = AgentConfig(
            agent_id="test_agent",
            name="Test Agent",
            capabilities=["test_capability"],
            metadata={"version": "1.0"},
        )

        assert config.agent_id == "test_agent"
        assert config.name == "Test Agent"
        assert config.capabilities == ["test_capability"]
        assert config.metadata == {"version": "1.0"}
        assert config.protocol_configs == {}

    def test_agent_config_with_protocols(self):
        """Test agent configuration with protocol configs."""
        protocol_configs = {
            "mcp": {"server_url": "localhost:8080"},
            "a2a": {"port": 9090},
        }

        config = AgentConfig(agent_id="test_agent", name="Test Agent", protocol_configs=protocol_configs)

        assert config.protocol_configs == protocol_configs


@pytest.mark.asyncio
class TestAgent:
    """Test the Agent class."""

    async def test_agent_initialization(self):
        """Test basic agent initialization."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent", capabilities=["test_capability"])

        agent = Agent(config)

        assert agent.agent_id == "test_agent"
        assert agent.name == "Test Agent"
        assert "test_capability" in agent.capabilities
        assert not agent._running

    async def test_agent_with_dependencies(self):
        """Test agent initialization with dependencies."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        state_manager = MockStateManager()
        protocol_adapters = {"mock": MockProtocolAdapter()}

        agent = Agent(
            config=config,
            state_manager=state_manager,
            protocol_adapters=protocol_adapters,
        )

        assert agent.state_manager is state_manager
        assert "mock" in agent.protocol_adapters

    async def test_agent_lifecycle_start_stop(self):
        """Test agent start and stop lifecycle."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        protocol_adapter = MockProtocolAdapter()
        agent = Agent(config=config, protocol_adapters={"mock": protocol_adapter})

        # Test start
        await agent.start()
        assert agent._running
        assert protocol_adapter.connected
        assert protocol_adapter.message_callback is not None

        # Test stop
        await agent.stop()
        assert not agent._running
        assert not protocol_adapter.connected

    async def test_agent_double_start(self):
        """Test that starting an already running agent is handled gracefully."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        agent = Agent(config)

        await agent.start()
        assert agent._running

        # Second start should not raise error
        await agent.start()
        assert agent._running

        await agent.stop()

    async def test_agent_session_management(self):
        """Test agent session management."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        agent = Agent(config)

        # Start session
        session_id = await agent.start_session({"test": "config"})
        assert session_id is not None
        assert agent.current_session_id == session_id
        assert session_id in agent.sessions
        assert agent.sessions[session_id]["active"]

        # End session
        await agent.end_session(session_id)
        assert not agent.sessions[session_id]["active"]
        assert agent.current_session_id is None

    async def test_agent_capability_management(self):
        """Test agent capability management."""
        config = AgentConfig(
            agent_id="test_agent",
            name="Test Agent",
            capabilities=["initial_capability"],
        )
        agent = Agent(config)

        # Check initial capabilities
        capabilities = agent.get_capabilities()
        assert "initial_capability" in capabilities

        # Register new capability
        await agent.register_capability("new_capability")
        capabilities = agent.get_capabilities()
        assert "new_capability" in capabilities

        # Unregister capability
        await agent.unregister_capability("new_capability")
        capabilities = agent.get_capabilities()
        assert "new_capability" not in capabilities

    async def test_agent_message_sending(self):
        """Test agent message sending."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        protocol_adapter = MockProtocolAdapter()
        agent = Agent(config=config, protocol_adapters={"mock": protocol_adapter})

        await agent.start()

        # Create test message
        message = create_text_message(
            text="Hello World",
            target_agent_id="other_agent",
            source_agent_id="test_agent",
        )
        message.source_protocol_type = "mock"

        # Send message
        await agent.send_message(message)

        # Wait a moment for background processing
        await asyncio.sleep(0.1)

        # Verify message was sent through protocol adapter
        assert len(protocol_adapter.sent_messages) == 1
        assert protocol_adapter.sent_messages[0] == message

        await agent.stop()

    async def test_agent_message_receiving(self):
        """Test agent message receiving."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        agent = Agent(config)

        await agent.start()

        # Create test message
        message = create_text_message(text="Hello", target_agent_id="test_agent", source_agent_id="other_agent")

        # Send message internally
        await agent.send_message(message)

        # Receive message
        received_message = await agent.receive_message()
        assert received_message.message_id == message.message_id

        await agent.stop()

    async def test_agent_tool_execution(self):
        """Test agent tool execution."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent", capabilities=["test_tool"])
        agent = Agent(config)

        # Execute tool
        result = await agent.execute_tool("test_tool", {"param": "value"})

        # Check result structure
        assert isinstance(result, dict)
        assert result["capability"] == "test_tool"
        assert result["parameters"] == {"param": "value"}
        assert result["executed_by"] == "test_agent"

    async def test_agent_tool_execution_unknown_capability(self):
        """Test tool execution with unknown capability."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        agent = Agent(config)

        # Should raise error for unknown capability
        with pytest.raises(ValueError, match="Capability 'unknown_tool' not registered"):
            await agent.execute_tool("unknown_tool", {})

    async def test_agent_message_callbacks(self):
        """Test agent message callbacks."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        agent = Agent(config)

        callback_messages = []

        def message_callback(message):
            callback_messages.append(message)

        # Add callback
        agent.add_message_callback(message_callback)

        await agent.start()

        # Send message
        message = create_text_message(text="Test", target_agent_id="test_agent", source_agent_id="other_agent")
        await agent.send_message(message)

        # Wait for processing
        await asyncio.sleep(0.1)

        # Check callback was called
        assert len(callback_messages) > 0

        await agent.stop()

    async def test_agent_protocol_message_handling(self):
        """Test handling messages from protocol adapters."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        protocol_adapter = MockProtocolAdapter()
        agent = Agent(config=config, protocol_adapters={"mock": protocol_adapter})

        # Track received messages with a callback
        received_messages = []

        def message_callback(message: SIMFMessage):
            received_messages.append(message)

        agent.add_message_callback(message_callback)
        await agent.start()

        # Simulate protocol message
        raw_message = "Hello from protocol"
        await agent.handle_incoming_message(raw_message, protocol_adapter)

        # Wait for processing
        await asyncio.sleep(0.2)

        # Check message was processed via callback
        assert len(received_messages) == 1
        assert "Hello from protocol" in str(received_messages[0].payload)

        await agent.stop()


if __name__ == "__main__":
    pytest.main([__file__])
