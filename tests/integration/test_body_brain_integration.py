"""
Integration Tests for Body-Brain Separation in OpenMAS Agent Architecture

This module tests Body-Brain separation in realistic scenarios with actual
protocol adapters and reasoning engines.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from openmas.agent.base_agent import Agent, AgentConfig
from openmas.agent.communicator import DefaultCommunicator
from openmas.agent.reasoning.simple_reasoning import SimpleReasoningEngine
from openmas.agent.factories import AgentComponentFactory
from openmas.core.simf import (
    SIMFMessage,
    MessageType,
    create_text_message,
    create_invocation_message,
    create_invocation_result_message,
    InvocationStatus,
)


class MockProtocolAdapter:
    """Mock protocol adapter for integration testing."""
    
    def __init__(self, protocol_name: str):
        self.protocol_name = protocol_name
        self.sent_messages = []
        self.message_callback = None
        self.connected = False
    
    async def connect(self, config: dict):
        """Mock connection."""
        self.connected = True
    
    async def disconnect(self):
        """Mock disconnection."""
        self.connected = False
    
    async def send_message(self, message: SIMFMessage):
        """Mock message sending."""
        self.sent_messages.append(message)
    
    async def register_message_callback(self, callback):
        """Register message callback."""
        self.message_callback = callback
    
    def to_internal_format(self, protocol_message):
        """Convert to SIMF format."""
        return protocol_message  # Simplified for testing
    
    def from_internal_format(self, internal_message: SIMFMessage):
        """Convert from SIMF format."""
        return internal_message  # Simplified for testing
    
    async def simulate_incoming_message(self, message: SIMFMessage):
        """Simulate receiving a message from external source."""
        if self.message_callback:
            await self.message_callback(message)


class TestBodyBrainIntegration:
    """Test Body-Brain separation in realistic scenarios."""
    
    @pytest.fixture
    def mcp_adapter(self):
        """Create mock MCP protocol adapter."""
        return MockProtocolAdapter("mcp")
    
    @pytest.fixture
    def agent_config(self):
        """Create test agent configuration."""
        return AgentConfig(
            agent_id="integration_agent",
            name="Integration Test Agent",
            capabilities=["echo", "status", "calculate"],
            protocol_configs={"mcp": {"server_url": "test://localhost"}}
        )
    
    @pytest.fixture
    def communicator(self, mcp_adapter):
        """Create communicator with protocol adapter."""
        return DefaultCommunicator("integration_agent", {"mcp": mcp_adapter})
    
    @pytest.fixture
    def reasoning_engine(self):
        """Create reasoning engine with capabilities."""
        return SimpleReasoningEngine({"echo", "status", "calculate"})
    
    @pytest.fixture
    def agent(self, agent_config, communicator, reasoning_engine):
        """Create agent with real components."""
        return Agent(
            config=agent_config,
            communicator=communicator,
            reasoning_engine=reasoning_engine
        )
    
    @pytest.mark.asyncio
    async def test_end_to_end_message_processing(self, agent, mcp_adapter):
        """Test complete message processing flow with Body-Brain separation."""
        # Start agent
        await agent.start()
        
        try:
            # Create incoming message
            incoming_message = create_text_message(
                text="Hello agent, how are you?",
                target_agent_id="integration_agent",
                source_agent_id="external_user",
                session_id="integration_session"
            )
            
            # Simulate message reception
            await mcp_adapter.simulate_incoming_message(incoming_message)
            
            # Allow message processing
            await asyncio.sleep(0.1)
            
            # Verify message was sent back through protocol adapter
            assert len(mcp_adapter.sent_messages) == 1
            response = mcp_adapter.sent_messages[0]
            
            assert response.source_agent_id == "integration_agent"
            assert response.target_agent_id == "external_user"
            assert response.session_id == "integration_session"
            
        finally:
            await agent.stop()
    
    @pytest.mark.asyncio
    async def test_capability_invocation_with_body_brain_separation(self, agent, mcp_adapter):
        """Test capability invocation through Body-Brain separation."""
        await agent.start()
        
        try:
            # Create capability invocation message
            invocation_message = create_invocation_message(
                invocation_name="echo",
                arguments={"message": "test echo"},
                target_agent_id="integration_agent",
                message_type=MessageType.CAPABILITY_INVOCATION,
                source_agent_id="external_user",
                session_id="capability_session"
            )
            
            # Simulate message reception
            await mcp_adapter.simulate_incoming_message(invocation_message)
            
            # Allow message processing
            await asyncio.sleep(0.1)
            
            # Verify capability was executed and result sent
            assert len(mcp_adapter.sent_messages) == 1
            response = mcp_adapter.sent_messages[0]
            
            assert response.message_type == MessageType.CAPABILITY_RESULT
            assert response.source_agent_id == "integration_agent"
            
        finally:
            await agent.stop()
    
    @pytest.mark.asyncio
    async def test_reasoning_engine_switching_during_operation(self, agent, mcp_adapter):
        """Test switching reasoning engines during operation."""
        await agent.start()
        
        try:
            # Send message with original reasoning engine
            message1 = create_text_message(
                text="First message",
                target_agent_id="integration_agent",
                source_agent_id="user",
                session_id="switch_session"
            )
            
            await mcp_adapter.simulate_incoming_message(message1)
            await asyncio.sleep(0.1)
            
            original_response_count = len(mcp_adapter.sent_messages)
            
            # Switch reasoning engine
            new_reasoning_engine = SimpleReasoningEngine({"new_capability"})
            agent.set_reasoning_engine(new_reasoning_engine)
            
            # Verify switch
            assert agent.get_reasoning_type() == "rule-based"
            new_capabilities = await agent.get_capabilities()
            assert "new_capability" in new_capabilities
            assert "echo" not in new_capabilities  # Old capability removed
            
            # Send message with new reasoning engine
            message2 = create_text_message(
                text="Second message",
                target_agent_id="integration_agent",
                source_agent_id="user",
                session_id="switch_session"
            )
            
            await mcp_adapter.simulate_incoming_message(message2)
            await asyncio.sleep(0.1)
            
            # Verify both messages were processed
            assert len(mcp_adapter.sent_messages) == original_response_count + 1
            
        finally:
            await agent.stop()
    
    @pytest.mark.asyncio
    async def test_protocol_independence_with_multiple_adapters(self, agent_config, reasoning_engine):
        """Test that reasoning is independent of communication protocol."""
        # Create communicator with multiple protocol adapters
        mcp_adapter = MockProtocolAdapter("mcp")
        http_adapter = MockProtocolAdapter("http")
        
        communicator = DefaultCommunicator(
            "multi_protocol_agent",
            {"mcp": mcp_adapter, "http": http_adapter}
        )
        
        agent = Agent(
            config=agent_config,
            communicator=communicator,
            reasoning_engine=reasoning_engine
        )
        
        await agent.start()
        
        try:
            # Same message content via different protocols
            mcp_message = create_text_message(
                text="protocol test",
                target_agent_id="multi_protocol_agent",
                source_agent_id="mcp_user",
                session_id="protocol_session"
            )
            
            http_message = create_text_message(
                text="protocol test",
                target_agent_id="multi_protocol_agent",
                source_agent_id="http_user",
                session_id="protocol_session"
            )
            
            # Send via MCP
            await mcp_adapter.simulate_incoming_message(mcp_message)
            await asyncio.sleep(0.1)
            
            # Send via HTTP
            await http_adapter.simulate_incoming_message(http_message)
            await asyncio.sleep(0.1)
            
            # Both protocols should have received responses
            assert len(mcp_adapter.sent_messages) == 1
            assert len(http_adapter.sent_messages) == 1
            
            # Responses should be similar (protocol-agnostic reasoning)
            mcp_response = mcp_adapter.sent_messages[0]
            http_response = http_adapter.sent_messages[0]
            
            assert mcp_response.message_type == http_response.message_type
            # Both should be text responses from reasoning engine
            assert mcp_response.message_type == MessageType.PLAIN_TEXT_MESSAGE
            
        finally:
            await agent.stop()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_body_brain_separation(self, agent, mcp_adapter):
        """Test error handling with Body-Brain separation."""
        await agent.start()
        
        try:
            # Create message that will cause reasoning engine error
            error_message = create_invocation_message(
                invocation_name="nonexistent_capability",
                arguments={},
                target_agent_id="integration_agent",
                message_type=MessageType.CAPABILITY_INVOCATION,
                source_agent_id="error_user",
                session_id="error_session"
            )
            
            # Simulate message reception
            await mcp_adapter.simulate_incoming_message(error_message)
            await asyncio.sleep(0.1)
            
            # Verify error response was sent
            assert len(mcp_adapter.sent_messages) == 1
            error_response = mcp_adapter.sent_messages[0]
            
            assert error_response.message_type == MessageType.ERROR_MESSAGE
            assert error_response.source_agent_id == "integration_agent"
            assert error_response.target_agent_id == "error_user"
            
        finally:
            await agent.stop()


class TestFactoryIntegration:
    """Test factory integration with real components."""
    
    def test_agent_component_factory_integration(self):
        """Test AgentComponentFactory creates working components."""
        factory = AgentComponentFactory()
        
        # Create components
        communicator, reasoning_engine = factory.create_basic_components(
            "factory_agent",
            {"test_capability"},
            {"mcp": MockProtocolAdapter("mcp")}
        )
        
        # Verify components are properly configured
        assert isinstance(communicator, DefaultCommunicator)
        assert isinstance(reasoning_engine, SimpleReasoningEngine)
        assert communicator.agent_id == "factory_agent"
        assert "test_capability" in reasoning_engine.capabilities
    
    def test_factory_config_based_creation(self):
        """Test factory creation from configuration."""
        factory = AgentComponentFactory()
        
        config = {
            "communicator": {
                "type": "default",
                "config": {"protocol_adapters": {"mcp": MockProtocolAdapter("mcp")}}
            },
            "reasoning": {
                "type": "simple",
                "config": {"capabilities": ["config_capability"]}
            }
        }
        
        communicator, reasoning_engine = factory.create_components_from_config(
            "config_agent", config
        )
        
        assert isinstance(communicator, DefaultCommunicator)
        assert isinstance(reasoning_engine, SimpleReasoningEngine)
        assert "config_capability" in reasoning_engine.capabilities


class TestReasoningAgnosticism:
    """Test that the architecture truly supports reasoning agnosticism."""
    
    class CustomReasoningEngine(SimpleReasoningEngine):
        """Custom reasoning engine for testing reasoning agnosticism."""
        
        def __init__(self):
            super().__init__({"custom_capability"})
        
        def get_reasoning_type(self) -> str:
            return "custom"
        
        async def decide_action(self, context):
            """Custom decision logic."""
            return {
                "type": "text",
                "content": {"message": "Custom reasoning response"},
                "sender": context.get("sender", "unknown"),
                "session": context.get("session", "default"),
                "target": context.get("sender", "unknown")
            }
    
    @pytest.mark.asyncio
    async def test_custom_reasoning_engine_integration(self):
        """Test that custom reasoning engines work with the architecture."""
        # Create agent with custom reasoning engine
        config = AgentConfig(
            agent_id="custom_agent",
            name="Custom Reasoning Agent",
            capabilities=["custom_capability"]
        )
        
        communicator = DefaultCommunicator("custom_agent", {})
        custom_reasoning = self.CustomReasoningEngine()
        
        agent = Agent(
            config=config,
            communicator=communicator,
            reasoning_engine=custom_reasoning
        )
        
        # Verify custom reasoning engine is used
        assert agent.get_reasoning_type() == "custom"
        
        # Test message processing with custom reasoning
        message = create_text_message(
            text="test custom reasoning",
            target_agent_id="custom_agent",
            source_agent_id="user",
            session_id="custom_session"
        )
        
        # Process message (without protocol adapter for simplicity)
        context = await communicator.parse_message(message)
        action = await custom_reasoning.decide_action(context)
        response = await communicator.format_response(action)
        
        # Verify custom reasoning was used
        assert "Custom reasoning response" in str(response.payload)
    
    @pytest.mark.asyncio
    async def test_reasoning_engine_hot_swapping(self):
        """Test that reasoning engines can be swapped without affecting communication."""
        config = AgentConfig(
            agent_id="swap_agent",
            name="Swap Test Agent",
            capabilities=[]
        )
        
        communicator = DefaultCommunicator("swap_agent", {})
        simple_reasoning = SimpleReasoningEngine({"simple_cap"})
        custom_reasoning = self.CustomReasoningEngine()
        
        agent = Agent(
            config=config,
            communicator=communicator,
            reasoning_engine=simple_reasoning
        )
        
        # Test with simple reasoning
        assert agent.get_reasoning_type() == "rule-based"
        
        # Swap to custom reasoning
        agent.set_reasoning_engine(custom_reasoning)
        assert agent.get_reasoning_type() == "custom"
        
        # Verify communicator is unchanged
        assert agent.communicator is communicator
        
        # Test that new reasoning engine is used
        capabilities = await agent.get_capabilities()
        assert "custom_capability" in capabilities
        assert "simple_cap" not in capabilities
