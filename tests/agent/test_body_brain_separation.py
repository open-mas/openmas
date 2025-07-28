"""
Tests for Body-Brain Separation in OpenMAS Agent Architecture

This module tests the proper implementation of Body-Brain separation,
ensuring reasoning agnosticism and protocol independence.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, Set

from openmas.agent.base_agent import Agent, AgentConfig
from openmas.agent.interfaces.communicator import ICommunicator
from openmas.agent.interfaces.reasoning import IReasoningEngine
from openmas.agent.communicator import DefaultCommunicator
from openmas.agent.reasoning.simple_reasoning import SimpleReasoningEngine
from openmas.agent.factories import CommunicatorFactory, ReasoningEngineFactory, AgentComponentFactory
from openmas.core.simf import (
    SIMFMessage,
    MessageType,
    MessageFlowDirection,
    create_text_message,
    create_invocation_message,
)


class MockCommunicator(ICommunicator):
    """Mock communicator for testing."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.parse_calls = []
        self.format_calls = []
        self.send_calls = []
        self.protocol_adapters = {}
    
    async def parse_message(self, message: SIMFMessage) -> Dict[str, Any]:
        context = {
            "message_type": message.message_type.value if hasattr(message.message_type, 'value') else str(message.message_type),
            "content": "test content",
            "sender": message.source_agent_id or "unknown",
            "session": message.session_id,
            "metadata": {"message_id": message.message_id}
        }
        self.parse_calls.append((message, context))
        return context
    
    async def format_response(self, action: Dict[str, Any]) -> SIMFMessage:
        response = create_text_message(
            text=action.get("content", {}).get("message", "test response"),
            target_agent_id=action.get("target", "unknown"),
            source_agent_id=self.agent_id,
            session_id=action.get("session", "default")
        )
        self.format_calls.append((action, response))
        return response
    
    async def send_message(self, message: SIMFMessage) -> None:
        self.send_calls.append(message)
    
    async def register_protocol_adapter(self, protocol_name: str, adapter) -> None:
        self.protocol_adapters[protocol_name] = adapter
    
    async def get_supported_protocols(self) -> list[str]:
        return list(self.protocol_adapters.keys())
    
    async def register_message_callback(self, callback) -> None:
        """Register message callback with protocol adapters (mock implementation)."""
        # Mock implementation - just store the callback for testing
        self.message_callback = callback


class MockReasoningEngine(IReasoningEngine):
    """Mock reasoning engine for testing."""
    
    def __init__(self, reasoning_type: str = "mock", capabilities: Set[str] = None):
        self.reasoning_type = reasoning_type
        self.capabilities = capabilities or {"test_capability"}
        self.decide_calls = []
        self.knowledge_updates = []
    
    async def decide_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        action = {
            "type": "text",
            "content": {"message": f"Mock response to {context.get('message_type', 'unknown')}"},
            "sender": context.get("sender", "unknown"),
            "session": context.get("session", "default"),
            "target": context.get("sender", "unknown")
        }
        self.decide_calls.append((context, action))
        return action
    
    async def update_knowledge(self, knowledge: Dict[str, Any]) -> None:
        self.knowledge_updates.append(knowledge)
    
    async def get_capabilities(self) -> Set[str]:
        return self.capabilities.copy()
    
    def get_reasoning_type(self) -> str:
        return self.reasoning_type


class TestBodyBrainSeparation:
    """Test Body-Brain separation implementation."""
    
    @pytest.fixture
    def agent_config(self):
        """Create test agent configuration."""
        return AgentConfig(
            agent_id="test_agent",
            name="Test Agent",
            capabilities=["test_capability", "echo"]
        )
    
    @pytest.fixture
    def mock_communicator(self):
        """Create mock communicator."""
        return MockCommunicator("test_agent")
    
    @pytest.fixture
    def mock_reasoning_engine(self):
        """Create mock reasoning engine."""
        return MockReasoningEngine("mock", {"test_capability", "echo"})
    
    @pytest.fixture
    def agent(self, agent_config, mock_communicator, mock_reasoning_engine):
        """Create agent with Body-Brain separation."""
        return Agent(
            config=agent_config,
            communicator=mock_communicator,
            reasoning_engine=mock_reasoning_engine
        )
    
    def test_agent_initialization_with_body_brain_separation(self, agent, mock_communicator, mock_reasoning_engine):
        """Test that agent properly initializes with separated components."""
        assert agent.communicator is mock_communicator
        assert agent.reasoning_engine is mock_reasoning_engine
        assert agent.get_reasoning_type() == "mock"
    
    @pytest.mark.asyncio
    async def test_message_processing_uses_body_brain_pattern(self, agent, mock_communicator, mock_reasoning_engine):
        """Test that message processing follows Body-Brain separation pattern."""
        # Create test message
        message = create_text_message(
            text="Hello agent",
            target_agent_id="test_agent",
            source_agent_id="user",
            session_id="test_session"
        )
        
        # Process message
        await agent._handle_message(message)
        
        # Verify Body-Brain separation pattern
        assert len(mock_communicator.parse_calls) == 1
        assert len(mock_reasoning_engine.decide_calls) == 1
        assert len(mock_communicator.format_calls) == 1
        assert len(mock_communicator.send_calls) == 1
        
        # Verify data flow
        parsed_context = mock_communicator.parse_calls[0][1]
        reasoning_context = mock_reasoning_engine.decide_calls[0][0]
        assert parsed_context == reasoning_context
    
    def test_reasoning_engine_swapping(self, agent, mock_communicator):
        """Test runtime reasoning engine swapping."""
        # Create new reasoning engine
        new_reasoning_engine = MockReasoningEngine("new_mock", {"new_capability"})
        
        # Swap reasoning engine
        old_type = agent.get_reasoning_type()
        agent.set_reasoning_engine(new_reasoning_engine)
        new_type = agent.get_reasoning_type()
        
        # Verify swap
        assert old_type == "mock"
        assert new_type == "new_mock"
        assert agent.reasoning_engine is new_reasoning_engine
    
    @pytest.mark.asyncio
    async def test_capabilities_delegated_to_reasoning_engine(self, agent, mock_reasoning_engine):
        """Test that capabilities are properly delegated to reasoning engine."""
        capabilities = await agent.get_capabilities()
        assert capabilities == {"test_capability", "echo"}
        assert capabilities == await mock_reasoning_engine.get_capabilities()
    
    @pytest.mark.asyncio
    async def test_knowledge_update_delegated_to_reasoning_engine(self, agent, mock_reasoning_engine):
        """Test that knowledge updates are delegated to reasoning engine."""
        knowledge = {"key": "value", "test": "data"}
        await agent.update_reasoning_knowledge(knowledge)
        
        assert len(mock_reasoning_engine.knowledge_updates) == 1
        assert mock_reasoning_engine.knowledge_updates[0] == knowledge
    
    @pytest.mark.asyncio
    async def test_send_message_uses_communicator(self, agent, mock_communicator):
        """Test that send_message uses communicator."""
        message = create_text_message(
            text="Test message",
            target_agent_id="other_agent",
            source_agent_id="test_agent",
            session_id="test_session"
        )
        
        await agent.send_message(message)
        
        assert len(mock_communicator.send_calls) == 1
        assert mock_communicator.send_calls[0] is message


class TestCommunicatorImplementation:
    """Test DefaultCommunicator implementation."""
    
    @pytest.fixture
    def protocol_adapter_mock(self):
        """Create mock protocol adapter."""
        adapter = Mock()
        adapter.send_message = AsyncMock()
        return adapter
    
    @pytest.fixture
    def communicator(self, protocol_adapter_mock):
        """Create DefaultCommunicator with mock adapter."""
        return DefaultCommunicator("test_agent", {"mcp": protocol_adapter_mock})
    
    @pytest.mark.asyncio
    async def test_parse_message_extracts_context(self, communicator):
        """Test that parse_message extracts proper context."""
        message = create_text_message(
            text="Hello",
            target_agent_id="test_agent",
            source_agent_id="user",
            session_id="test_session"
        )
        
        context = await communicator.parse_message(message)
        
        assert context["message_type"] == "PLAIN_TEXT_MESSAGE"
        assert context["sender"] == "user"
        assert context["session"] == "test_session"
        assert "metadata" in context
    
    @pytest.mark.asyncio
    async def test_format_response_creates_simf_message(self, communicator):
        """Test that format_response creates proper SIMF message."""
        action = {
            "type": "text",
            "content": {"message": "Response message"},
            "sender": "test_agent",
            "session": "test_session",
            "target": "user"
        }
        
        response = await communicator.format_response(action)
        
        assert isinstance(response, SIMFMessage)
        assert response.source_agent_id == "test_agent"
        assert response.target_agent_id == "user"
        assert response.session_id == "test_session"
    
    @pytest.mark.asyncio
    async def test_send_message_uses_protocol_adapters(self, communicator, protocol_adapter_mock):
        """Test that send_message uses protocol adapters."""
        message = create_text_message(
            text="Test",
            target_agent_id="other_agent",
            source_agent_id="test_agent",
            session_id="test_session"
        )
        
        await communicator.send_message(message)
        
        protocol_adapter_mock.send_message.assert_called_once_with(message)


class TestReasoningEngineImplementation:
    """Test SimpleReasoningEngine implementation."""
    
    @pytest.fixture
    def reasoning_engine(self):
        """Create SimpleReasoningEngine."""
        return SimpleReasoningEngine({"echo", "status", "calculate"})
    
    @pytest.mark.asyncio
    async def test_decide_action_handles_capability_invocation(self, reasoning_engine):
        """Test capability invocation handling."""
        context = {
            "message_type": "CAPABILITY_INVOCATION",
            "invocation_name": "echo",
            "arguments": {"message": "test"},
            "sender": "user",
            "session": "test_session"
        }
        
        action = await reasoning_engine.decide_action(context)
        
        assert action["type"] == "invocation_result"
        assert "result" in action["content"]
    
    @pytest.mark.asyncio
    async def test_decide_action_handles_text_message(self, reasoning_engine):
        """Test text message handling."""
        context = {
            "message_type": "text",
            "content": "Hello agent",
            "sender": "user",
            "session": "test_session"
        }
        
        action = await reasoning_engine.decide_action(context)
        
        assert action["type"] == "text"
        assert "message" in action["content"]
    
    @pytest.mark.asyncio
    async def test_update_knowledge(self, reasoning_engine):
        """Test knowledge base updates."""
        knowledge = {"key": "value", "test": "data"}
        await reasoning_engine.update_knowledge(knowledge)
        
        assert reasoning_engine.knowledge_base["key"] == "value"
        assert reasoning_engine.knowledge_base["test"] == "data"
    
    def test_get_reasoning_type(self, reasoning_engine):
        """Test reasoning type identification."""
        assert reasoning_engine.get_reasoning_type() == "rule-based"


class TestFactories:
    """Test factory classes for component creation."""
    
    def test_communicator_factory_creates_default(self):
        """Test CommunicatorFactory creates DefaultCommunicator."""
        communicator = CommunicatorFactory.create_default_communicator("test_agent")
        assert isinstance(communicator, DefaultCommunicator)
        assert communicator.agent_id == "test_agent"
    
    def test_reasoning_engine_factory_creates_simple(self):
        """Test ReasoningEngineFactory creates SimpleReasoningEngine."""
        reasoning_engine = ReasoningEngineFactory.create_simple_reasoning_engine({"test"})
        assert isinstance(reasoning_engine, SimpleReasoningEngine)
        assert "test" in reasoning_engine.capabilities
    
    def test_agent_component_factory_creates_basic_components(self):
        """Test AgentComponentFactory creates basic components."""
        factory = AgentComponentFactory()
        communicator, reasoning_engine = factory.create_basic_components(
            "test_agent", {"test_capability"}
        )
        
        assert isinstance(communicator, DefaultCommunicator)
        assert isinstance(reasoning_engine, SimpleReasoningEngine)
        assert "test_capability" in reasoning_engine.capabilities


class TestProtocolIndependence:
    """Test that reasoning is independent of communication protocol."""
    
    @pytest.mark.asyncio
    async def test_reasoning_engine_protocol_agnostic(self):
        """Test that reasoning engine decisions are protocol-independent."""
        reasoning_engine = SimpleReasoningEngine({"echo"})
        
        # Same context from different "protocols"
        mcp_context = {
            "message_type": "text",
            "content": "hello",
            "sender": "mcp_user",
            "session": "mcp_session",
            "metadata": {"protocol": "mcp"}
        }
        
        http_context = {
            "message_type": "text",
            "content": "hello",
            "sender": "http_user",
            "session": "http_session",
            "metadata": {"protocol": "http"}
        }
        
        mcp_action = await reasoning_engine.decide_action(mcp_context)
        http_action = await reasoning_engine.decide_action(http_context)
        
        # Reasoning decisions should be similar regardless of protocol
        assert mcp_action["type"] == http_action["type"]
        # Content should be similar (protocol-agnostic reasoning)
        assert "message" in mcp_action["content"]
        assert "message" in http_action["content"]
