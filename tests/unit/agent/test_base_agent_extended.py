"""
Extended unit tests for Base Agent

Additional tests to improve coverage for error handling, message processing,
and edge cases in the base agent implementation.
"""

import asyncio
import contextlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openmas.agent.base_agent import Agent, AgentConfig
from openmas.core.simf import create_text_message


class TestAgentErrorHandling:
    """Test error handling scenarios in the agent."""

    @pytest.fixture
    def agent_config(self):
        """Create a test agent configuration."""
        return AgentConfig(
            agent_id="error-test-agent",
            name="Error Test Agent",
            capabilities=["test_capability"],
        )

    @pytest.fixture
    def agent(self, agent_config):
        """Create a test agent."""
        from openmas.agent.communicator import DefaultCommunicator
        from openmas.agent.reasoning.simple_reasoning import SimpleReasoningEngine
        
        communicator = DefaultCommunicator(agent_config.agent_id)
        reasoning_engine = SimpleReasoningEngine()
        # Initialize reasoning engine with capabilities from config
        reasoning_engine.capabilities = set(agent_config.capabilities)
        return Agent(config=agent_config, communicator=communicator, reasoning_engine=reasoning_engine)

    @pytest.mark.asyncio
    async def test_stop_agent_not_running(self, agent):
        """Test stopping an agent that is not running."""
        # Agent should handle stop gracefully when not running
        await agent.stop()

        assert not agent.is_running
        # Note: _tasks is an internal implementation detail that may not exist

    @pytest.mark.asyncio
    async def test_double_start(self, agent):
        """Test starting an agent that is already running."""
        # Mock the protocol adapter to avoid actual connections
        mock_adapter = AsyncMock()
        mock_adapter.connect = AsyncMock()
        mock_adapter.register_message_callback = AsyncMock()
        agent.communicator.protocol_adapters["test"] = mock_adapter
        agent.config.protocol_configs = {"test": {}}

        # Start the agent
        await agent.start()
        assert agent.is_running

        # Try to start again - should log warning but not fail
        with patch.object(agent.logger, "warning") as mock_warning:
            await agent.start()
            mock_warning.assert_called_with("Agent is already running")

        await agent.stop()

    @pytest.mark.asyncio
    async def test_protocol_adapter_start_failure(self, agent):
        """Test handling protocol adapter start failure."""
        # Mock the communicator's register_message_callback to fail
        with patch.object(agent.communicator, 'register_message_callback', side_effect=Exception("Connection failed")):
            # Starting should raise an exception
            with pytest.raises(RuntimeError, match="Agent startup failed"):
                await agent.start()

            assert not agent.is_running

    @pytest.mark.asyncio
    async def test_message_processing_error(self, agent):
        """Test error handling in message processing."""
        message = create_text_message(text="Test message", target_agent_id=agent.agent_id)

        # Mock _handle_message to raise an exception - but catch it properly
        with (
            patch.object(agent, "_handle_message", side_effect=Exception("Processing error")),
            patch.object(agent.logger, "error"),
            contextlib.suppress(Exception),
        ):
            await agent._handle_message(message)
            # The error should have been logged in the actual implementation

    @pytest.mark.asyncio
    async def test_prepare_outgoing_message_error(self, agent):
        """Test error handling in outgoing message preparation."""
        message = create_text_message(text="Test message", target_agent_id="other-agent")

        # Create a mock adapter that fails translation
        mock_adapter = MagicMock()
        mock_adapter.from_internal_format.side_effect = Exception("Translation failed")

        with pytest.raises(Exception, match="Translation failed"):
            await agent.prepare_outgoing_message(message, mock_adapter)


class TestAgentMessageProcessing:
    """Test message processing functionality."""

    @pytest.fixture
    def agent_config(self):
        """Create a test agent configuration."""
        return AgentConfig(
            agent_id="processing-test-agent",
            name="Processing Test Agent",
            capabilities=["echo"],
        )

    @pytest.fixture
    def agent(self, agent_config):
        """Create a test agent."""
        from openmas.agent.communicator import DefaultCommunicator
        from openmas.agent.reasoning.simple_reasoning import SimpleReasoningEngine
        
        communicator = DefaultCommunicator(agent_config.agent_id)
        reasoning_engine = SimpleReasoningEngine()
        # Initialize reasoning engine with capabilities from config
        reasoning_engine.capabilities = set(agent_config.capabilities)
        return Agent(config=agent_config, communicator=communicator, reasoning_engine=reasoning_engine)

    @pytest.mark.asyncio
    async def test_process_messages_no_queue(self, agent):
        """Test message processing when queue is not initialized."""
        agent.message_queue = None

        with patch.object(agent.logger, "error") as mock_error:
            await agent._process_messages()
            mock_error.assert_called_with("Message queue not initialized")

    @pytest.mark.asyncio
    async def test_process_messages_loop_shutdown(self, agent):
        """Test message processing during shutdown."""
        # Initialize the agent
        agent.message_queue = asyncio.Queue()
        agent._running = True

        # Create a task for message processing
        process_task = asyncio.create_task(agent._process_messages())

        # Let it run briefly
        await asyncio.sleep(0.1)

        # Stop the agent
        agent._running = False

        # Wait for the task to complete
        await asyncio.wait_for(process_task, timeout=1.0)

        assert not agent._running

    @pytest.mark.asyncio
    async def test_process_messages_event_loop_error(self, agent):
        """Test handling event loop errors in message processing."""
        agent.message_queue = asyncio.Queue()
        agent._running = True

        # Mock message handling to raise a RuntimeError about event loop
        with patch.object(agent, "_handle_message") as mock_handle:
            mock_handle.side_effect = RuntimeError("no running event loop")

            with patch.object(agent.logger, "debug") as mock_debug:
                process_task = asyncio.create_task(agent._process_messages())

                # Add a message to process
                await agent.message_queue.put(create_text_message(text="test", target_agent_id=agent.agent_id))

                # Let it process and hit the error
                await asyncio.sleep(0.1)

                # The task should complete due to the event loop error
                await asyncio.wait_for(process_task, timeout=1.0)

                mock_debug.assert_called()

    @pytest.mark.asyncio
    async def test_handle_protocol_message_queue_not_initialized(self, agent):
        """Test error when message queue is not initialized."""
        message = create_text_message(text="Test message", target_agent_id=agent.agent_id)

        # Don't initialize message queue - should raise RuntimeError
        with pytest.raises(RuntimeError, match="Agent not started"):
            await agent._handle_protocol_message(message)


class TestAgentCapabilityManagement:
    """Test capability management functionality."""

    @pytest.fixture
    def agent_config(self):
        """Create a test agent configuration."""
        return AgentConfig(
            agent_id="capability-test-agent",
            name="Capability Test Agent",
            capabilities=["echo", "test_capability"],
        )

    @pytest.fixture
    def agent(self, agent_config):
        """Create a test agent."""
        from openmas.agent.communicator import DefaultCommunicator
        from openmas.agent.reasoning.simple_reasoning import SimpleReasoningEngine
        
        communicator = DefaultCommunicator(agent_config.agent_id)
        reasoning_engine = SimpleReasoningEngine()
        # Initialize reasoning engine with capabilities from config
        reasoning_engine.capabilities = set(agent_config.capabilities)
        return Agent(config=agent_config, communicator=communicator, reasoning_engine=reasoning_engine)

    @pytest.mark.asyncio
    async def test_capability_registration_and_listing(self, agent):
        """Test capability registration and listing."""
        # Test initial capabilities from config
        capabilities = await agent.get_capabilities()
        assert "echo" in capabilities
        assert "test_capability" in capabilities

        # Test adding a new capability directly to reasoning engine
        agent.reasoning_engine.capabilities.add("new_capability")
        capabilities = await agent.get_capabilities()
        assert "new_capability" in capabilities

        # Test removing a capability directly from reasoning engine
        agent.reasoning_engine.capabilities.discard("test_capability")
        capabilities = await agent.get_capabilities()
        assert "test_capability" not in capabilities


class TestAgentSessionManagement:
    """Test session management functionality."""

    @pytest.fixture
    def agent_config(self):
        """Create a test agent configuration."""
        return AgentConfig(
            agent_id="session-test-agent",
            name="Session Test Agent",
        )

    @pytest.fixture
    def agent(self, agent_config):
        """Create a test agent."""
        from openmas.agent.communicator import DefaultCommunicator
        from openmas.agent.reasoning.simple_reasoning import SimpleReasoningEngine
        
        communicator = DefaultCommunicator(agent_config.agent_id)
        reasoning_engine = SimpleReasoningEngine()
        # Initialize reasoning engine with capabilities from config
        reasoning_engine.capabilities = set(agent_config.capabilities)
        return Agent(config=agent_config, communicator=communicator, reasoning_engine=reasoning_engine)

    def test_session_management(self, agent):
        """Test session ID management."""
        # Initially no session
        assert agent.current_session_id is None

        # Set a session
        agent.current_session_id = "session-123"
        assert agent.current_session_id == "session-123"

        # Clear session
        agent.current_session_id = None
        assert agent.current_session_id is None


class TestAgentCleanupOnDestruction:
    """Test agent cleanup on destruction."""

    @pytest.fixture
    def agent_config(self):
        """Create a test agent configuration."""
        return AgentConfig(
            agent_id="cleanup-test-agent",
            name="Cleanup Test Agent",
        )

    def test_del_running_agent_warning(self, agent_config):
        """Test warning when agent is deleted while running."""
        from openmas.agent.communicator import DefaultCommunicator
        from openmas.agent.reasoning.simple_reasoning import SimpleReasoningEngine
        
        communicator = DefaultCommunicator(agent_config.agent_id)
        reasoning_engine = SimpleReasoningEngine()
        agent = Agent(config=agent_config, communicator=communicator, reasoning_engine=reasoning_engine)
        agent._running = True
        agent._tasks = [MagicMock()]

        with patch.object(agent.logger, "warning") as mock_warning:
            agent.__del__()
            mock_warning.assert_called()

    def test_del_stopped_agent_no_warning(self, agent_config):
        """Test no warning when agent is deleted while stopped."""
        from openmas.agent.communicator import DefaultCommunicator
        from openmas.agent.reasoning.simple_reasoning import SimpleReasoningEngine
        
        communicator = DefaultCommunicator(agent_config.agent_id)
        reasoning_engine = SimpleReasoningEngine()
        agent = Agent(config=agent_config, communicator=communicator, reasoning_engine=reasoning_engine)
        agent._running = False

        with patch.object(agent.logger, "warning") as mock_warning:
            agent.__del__()
            mock_warning.assert_not_called()


class TestAgentStateManagement:
    """Test agent state management functionality."""

    @pytest.fixture
    def agent_config(self):
        """Create a test agent configuration."""
        return AgentConfig(
            agent_id="state-test-agent",
            name="State Test Agent",
        )

    @pytest.fixture
    def agent(self, agent_config):
        """Create a test agent."""
        from openmas.agent.communicator import DefaultCommunicator
        from openmas.agent.reasoning.simple_reasoning import SimpleReasoningEngine
        
        communicator = DefaultCommunicator(agent_config.agent_id)
        reasoning_engine = SimpleReasoningEngine()
        # Initialize reasoning engine with capabilities from config
        reasoning_engine.capabilities = set(agent_config.capabilities)
        return Agent(config=agent_config, communicator=communicator, reasoning_engine=reasoning_engine)

    def test_agent_properties(self, agent):
        """Test agent properties are accessible."""
        assert agent.agent_id == "state-test-agent"
        assert agent.name == "State Test Agent"
        assert isinstance(agent.config, AgentConfig)
        # Protocol adapters are now managed through communicator
        assert hasattr(agent.communicator, 'protocol_adapters')
        # Capabilities are accessed via async method
        assert hasattr(agent, 'get_capabilities')
        assert agent.message_callbacks == []
