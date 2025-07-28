"""
Unit tests for the OpenMAS Base Agent implementation.

These tests validate the core agent functionality including lifecycle management,
SIMF message handling, capability management, and session management.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from openmas.agent.base_agent import Agent, AgentConfig, IAgentStateManager, IProtocolAdapter
from openmas.agent.exceptions import AgentError, AgentLifecycleError, AgentMessageError
from openmas.agent.factories import AgentComponentFactory
from openmas.agent.facade import AgentFacade
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from utils import TestStateManager, TestProtocolAdapter
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


# ============================================================================
# Test Helper Functions - Using Facade Pattern
# ============================================================================

def create_test_agent(config: AgentConfig, state_manager=None, protocol_adapters=None, test_instance=None):
    """Helper function to create agents using simplified AgentFacade interface."""
    # Import here to avoid circular imports
    from openmas.agent.facade import AgentFacade
    
    # Use AgentFacade for simplified agent creation
    facade = AgentFacade(
        config=config,
        state_manager=state_manager,
        protocol_adapters=protocol_adapters
    )
    
    # Track agent for cleanup if test instance provided
    agent = facade.agent
    if test_instance and hasattr(test_instance, 'test_agents'):
        test_instance.test_agents.append(agent)
    
    return agent


@pytest.mark.asyncio
class TestAgent:
    """Test the Agent class."""
    
    def setup_method(self):
        """Set up test method - track agents for cleanup."""
        self.test_agents = []
    
    async def teardown_method(self):
        """Clean up test method - ensure all agents are stopped."""
        for agent in self.test_agents:
            if hasattr(agent, '_running') and agent._running:
                await agent.stop()
        self.test_agents.clear()

    async def test_agent_initialization(self):
        """Test basic agent initialization."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent", capabilities=["test_capability"])

        agent = create_test_agent(config, test_instance=self)

        assert agent.agent_id == "test_agent"
        assert agent.name == "Test Agent"
        capabilities = await agent.get_capabilities()
        assert "test_capability" in capabilities
        assert not agent._running

    async def test_agent_with_dependencies(self):
        """Test agent initialization with dependencies."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        state_manager = MockStateManager()
        protocol_adapters = {"mock": MockProtocolAdapter()}

        agent = create_test_agent(
            config=config,
            state_manager=state_manager,
            protocol_adapters=protocol_adapters,
            test_instance=self
        )

        assert agent.state_manager is state_manager
        # In Body-Brain architecture, protocol adapters are accessed through communicator
        assert hasattr(agent, 'communicator')
        assert hasattr(agent.communicator, 'protocol_adapters')
        assert "mock" in agent.communicator.protocol_adapters

    async def test_agent_lifecycle_start_stop(self):
        """Test agent start and stop lifecycle."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        protocol_adapter = MockProtocolAdapter()
        agent = create_test_agent(config=config, protocol_adapters={"mock": protocol_adapter}, test_instance=self)

        # Test start
        await agent.start()
        assert agent._running
        # In Body-Brain architecture, protocol adapters are managed by communicator
        # Check that the communicator has started and protocol adapters are available
        assert hasattr(agent, 'communicator')
        assert "mock" in agent.communicator.protocol_adapters

        # Test stop
        await agent.stop()
        assert not agent._running

    async def test_agent_double_start(self):
        """Test that starting an already running agent is handled gracefully."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        agent = create_test_agent(config, test_instance=self)

        await agent.start()
        assert agent._running

        # Second start should not raise error
        await agent.start()
        assert agent._running

        await agent.stop()

    async def test_agent_session_management(self):
        """Test agent session management."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        agent = create_test_agent(config, test_instance=self)

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
        agent = create_test_agent(config, test_instance=self)

        # Check initial capabilities (in Body-Brain architecture, capabilities are static from config)
        capabilities = await agent.get_capabilities()
        assert "initial_capability" in capabilities
        
        # In Body-Brain architecture, capabilities are managed through the reasoning engine
        # and are typically static from configuration rather than dynamically registered
        assert hasattr(agent, 'reasoning_engine')
        engine_capabilities = await agent.reasoning_engine.get_capabilities()
        assert "initial_capability" in engine_capabilities

    async def test_agent_message_sending(self):
        """Test agent message sending."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        protocol_adapter = MockProtocolAdapter()
        agent = create_test_agent(config=config, protocol_adapters={"mock": protocol_adapter}, test_instance=self)

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
        """Test agent message receiving and processing."""
        config = AgentConfig(agent_id="receiver", name="Receiver Agent")
        agent = create_test_agent(config, test_instance=self)

        await agent.start()

        # Create test message
        message = create_text_message(text="Hello", target_agent_id="receiver", source_agent_id="other_agent")

        # Simulate message delivery directly to agent's queue (bypassing communicator)
        # This tests the agent's internal message processing capability
        await agent.message_queue.put(message)

        # Receive message
        received_message = await agent.receive_message()
        assert received_message.message_id == message.message_id
        assert received_message.payload.text == "Hello"
        assert received_message.target_agent_id == "receiver"

    async def test_agent_tool_execution(self):
        """Test agent tool execution."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent", capabilities=["test_tool"])
        agent = create_test_agent(config, test_instance=self)

        # Execute tool
        result = await agent.execute_tool("test_tool", {"param": "value"})

        # Check result structure (matches SimpleReasoningEngine._execute_capability return format)
        assert isinstance(result, dict)
        assert result["capability"] == "test_tool"
        assert result["arguments"] == {"param": "value"}
        assert result["executed"] is True
        assert result["reasoning_type"] == "rule-based"

    async def test_agent_tool_execution_unknown_capability(self):
        """Test tool execution with unknown capability."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        agent = create_test_agent(config, test_instance=self)

        # Should raise error for unknown capability
        with pytest.raises(ValueError, match="Capability 'unknown_tool' not registered"):
            await agent.execute_tool("unknown_tool", {})

    async def test_agent_message_callbacks(self):
        """Test agent message callbacks."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        agent = create_test_agent(config, test_instance=self)

        callback_messages = []

        def message_callback(message):
            callback_messages.append(message)

        # Add callback
        agent.add_message_callback(message_callback)

        await agent.start()

        # Create test message and simulate direct delivery to agent's queue
        message = create_text_message(text="Test", target_agent_id="test_agent", source_agent_id="other_agent")
        
        # Simulate message delivery directly to agent's queue (bypassing communicator)
        # This triggers the message processing and callbacks
        await agent.message_queue.put(message)

        # Wait for message processing
        await asyncio.sleep(0.1)

        # Check callback was called
        assert len(callback_messages) > 0
        assert callback_messages[0].message_id == message.message_id

    async def test_agent_protocol_message_handling(self):
        """Test handling messages from protocol adapters."""
        config = AgentConfig(agent_id="test_agent", name="Test Agent")
        protocol_adapter = MockProtocolAdapter()
        agent = create_test_agent(config=config, protocol_adapters={"mock": protocol_adapter}, test_instance=self)

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
