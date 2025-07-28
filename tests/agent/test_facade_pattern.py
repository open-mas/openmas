"""
Unit tests for the OpenMAS Facade Pattern implementation.

These tests validate the AgentFacade and AgentBuilder classes that provide
simplified interfaces for agent creation and interaction.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from openmas.agent.facade import AgentFacade
from openmas.agent.builder import (
    AgentBuilder, 
    create_agent, 
    create_basic_agent,
    create_powerbi_agent,
    create_sql_agent,
    create_analytics_agent
)
from openmas.agent.base_agent import AgentConfig, IAgentStateManager, IProtocolAdapter
from openmas.core.simf import SIMFMessage, MessageType, create_text_message


# ============================================================================
# Mock Implementations for Testing
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
    
    async def list_state_keys(self, scope: str = "PRIVATE_PERSISTENT") -> list[str]:
        prefix = f"{scope}:"
        return [key[len(prefix):] for key in self._state.keys() if key.startswith(prefix)]


class MockProtocolAdapter(IProtocolAdapter):
    """Mock protocol adapter for testing."""
    
    def __init__(self):
        self.started = False
        self.messages = []
    
    async def start(self) -> None:
        self.started = True
    
    async def stop(self) -> None:
        self.started = False
    
    async def send_message(self, message: SIMFMessage) -> None:
        self.messages.append(message)
    
    def is_running(self) -> bool:
        return self.started
    
    async def connect(self) -> None:
        pass
    
    async def disconnect(self) -> None:
        pass
    
    def register_message_callback(self, callback) -> None:
        pass
    
    def to_internal_format(self, external_message) -> SIMFMessage:
        return external_message
    
    def from_internal_format(self, internal_message: SIMFMessage):
        return internal_message


# ============================================================================
# AgentFacade Tests
# ============================================================================

@pytest.mark.asyncio
class TestAgentFacade:
    """Test the AgentFacade class."""
    
    async def test_facade_initialization_with_preset(self):
        """Test facade initialization with preset configuration."""
        facade = AgentFacade("basic_agent")
        
        assert facade.agent_id.startswith("basic_")
        assert facade.name == "Basic Agent"
        assert "message_handling" in await facade.get_capabilities()
        assert not facade.is_running
    
    async def test_facade_initialization_with_config_dict(self):
        """Test facade initialization with configuration dictionary."""
        config = {
            "agent_id": "test_agent",
            "name": "Test Agent",
            "capabilities": ["test_capability"]
        }
        
        facade = AgentFacade(config)
        
        assert facade.agent_id == "test_agent"
        assert facade.name == "Test Agent"
        assert "test_capability" in await facade.get_capabilities()
    
    async def test_facade_initialization_with_agent_config(self):
        """Test facade initialization with AgentConfig object."""
        config = AgentConfig(
            agent_id="config_agent",
            name="Config Agent",
            capabilities=["config_capability"]
        )
        
        facade = AgentFacade(config)
        
        assert facade.agent_id == "config_agent"
        assert facade.name == "Config Agent"
        assert "config_capability" in await facade.get_capabilities()
    
    async def test_facade_with_dependencies(self):
        """Test facade initialization with custom dependencies."""
        state_manager = MockStateManager()
        protocol_adapters = {"mock": MockProtocolAdapter()}
        
        facade = AgentFacade(
            "basic_agent",
            state_manager=state_manager,
            protocol_adapters=protocol_adapters
        )
        
        assert facade.state_manager == state_manager
        assert "mock" in facade.protocol_adapters
    
    async def test_facade_lifecycle_management(self):
        """Test facade start/stop lifecycle."""
        facade = AgentFacade("basic_agent")
        
        # Initially not running
        assert not facade.is_running
        
        # Start the facade
        await facade.start()
        assert facade.is_running
        
        # Stop the facade
        await facade.stop()
        assert not facade.is_running
    
    async def test_facade_capability_management(self):
        """Test facade capability management."""
        facade = AgentFacade("basic_agent")
        
        # Add capability
        await facade.add_capability("new_capability")
        capabilities = await facade.get_capabilities()
        assert "new_capability" in capabilities
        
        # Remove capability
        await facade.remove_capability("new_capability")
        capabilities = await facade.get_capabilities()
        assert "new_capability" not in capabilities
    
    async def test_facade_message_processing(self):
        """Test facade message processing."""
        facade = AgentFacade("basic_agent")
        await facade.start()
        
        # Test text message
        message = {"text": "Hello, agent!"}
        response = await facade.process_message(message)
        
        # Should process without error (response may be None for basic processing)
        # The important thing is that no exception was raised
        assert True  # Processing completed successfully
        
        await facade.stop()
    
    async def test_facade_send_message(self):
        """Test facade message sending."""
        facade = AgentFacade("basic_agent")
        await facade.start()
        
        # Test sending text message
        response = await facade.send_message(
            content="Hello, world!",
            target="target_agent",
            message_type="text"
        )
        
        # Should send without error
        # Note: Response may be None if no target agent to respond
        
        await facade.stop()
    
    async def test_facade_status_information(self):
        """Test facade status information."""
        facade = AgentFacade("basic_agent")
        
        status = facade.get_status()
        
        assert "agent_id" in status
        assert "name" in status
        assert "running" in status
        assert "capabilities" in status
        assert "protocols" in status
        
        assert status["running"] == False  # Not started yet
    
    async def test_facade_preset_configurations(self):
        """Test all preset configurations."""
        presets = ["basic_agent", "powerbi_agent", "sql_agent", "analytics_agent"]
        
        for preset in presets:
            facade = AgentFacade(preset)
            
            # Each preset should have valid configuration
            assert facade.agent_id is not None
            assert facade.name is not None
            capabilities = await facade.get_capabilities()
            assert len(capabilities) > 0
    
    async def test_facade_invalid_preset(self):
        """Test facade with invalid preset name."""
        with pytest.raises(ValueError, match="Unknown preset"):
            AgentFacade("invalid_preset")
    
    async def test_facade_invalid_config_type(self):
        """Test facade with invalid configuration type."""
        with pytest.raises(ValueError, match="Invalid config type"):
            AgentFacade(123)  # Invalid type


# ============================================================================
# AgentBuilder Tests
# ============================================================================

@pytest.mark.asyncio
class TestAgentBuilder:
    """Test the AgentBuilder class."""
    
    async def test_builder_basic_configuration(self):
        """Test basic builder configuration."""
        facade = (AgentBuilder()
                 .with_name("Builder Agent")
                 .with_capability("test_capability")
                 .build())
        
        assert facade.name == "Builder Agent"
        assert "test_capability" in await facade.get_capabilities()
    
    async def test_builder_fluent_interface(self):
        """Test builder fluent interface."""
        facade = (AgentBuilder()
                 .with_id("builder_001")
                 .with_name("Fluent Agent")
                 .with_capabilities(["cap1", "cap2"])
                 .with_protocol("mcp")
                 .build())
        
        assert facade.agent_id == "builder_001"
        assert facade.name == "Fluent Agent"
        capabilities = await facade.get_capabilities()
        assert "cap1" in capabilities
        assert "cap2" in capabilities
    
    async def test_builder_with_state_manager(self):
        """Test builder with custom state manager."""
        state_manager = MockStateManager()
        
        facade = (AgentBuilder()
                 .with_name("State Agent")
                 .with_state_manager(state_manager)
                 .build())
        
        assert facade.state_manager == state_manager
    
    async def test_builder_with_protocol_adapter(self):
        """Test builder with protocol adapter."""
        adapter = MockProtocolAdapter()
        
        facade = (AgentBuilder()
                 .with_name("Protocol Agent")
                 .with_protocol("mock", adapter)
                 .build())
        
        assert "mock" in facade.protocol_adapters
        assert facade.protocol_adapters["mock"] == adapter
    
    async def test_builder_with_preset(self):
        """Test builder with preset configuration."""
        facade = (AgentBuilder()
                 .with_preset("powerbi_agent")
                 .with_name("Custom PowerBI Agent")  # Override preset name
                 .build())
        
        assert facade.name == "Custom PowerBI Agent"
        capabilities = await facade.get_capabilities()
        assert "data_model_analysis" in capabilities  # From preset
    
    async def test_builder_auto_generated_id(self):
        """Test builder with auto-generated agent ID."""
        facade = (AgentBuilder()
                 .with_name("Auto ID Agent")
                 .build())
        
        # Should have auto-generated ID
        assert facade.agent_id.startswith("agent_")
        assert len(facade.agent_id) > 6  # Should include UUID part
    
    async def test_builder_missing_name_error(self):
        """Test builder error when name is missing."""
        with pytest.raises(ValueError, match="Agent name is required"):
            AgentBuilder().build()
    
    async def test_builder_metadata(self):
        """Test builder metadata functionality."""
        facade = (AgentBuilder()
                 .with_name("Metadata Agent")
                 .with_metadata("version", "1.0")
                 .with_metadata("author", "test")
                 .build())
        
        # Metadata should be in the config
        assert facade.config.metadata["version"] == "1.0"
        assert facade.config.metadata["author"] == "test"


# ============================================================================
# Convenience Function Tests
# ============================================================================

@pytest.mark.asyncio
class TestConvenienceFunctions:
    """Test convenience functions for agent creation."""
    
    async def test_create_agent_function(self):
        """Test create_agent convenience function."""
        builder = create_agent()
        
        assert isinstance(builder, AgentBuilder)
        
        # Should be able to build an agent
        facade = builder.with_name("Convenience Agent").build()
        assert facade.name == "Convenience Agent"
    
    async def test_create_basic_agent_function(self):
        """Test create_basic_agent convenience function."""
        facade = create_basic_agent("Basic Test Agent", ["test_cap"])
        
        assert facade.name == "Basic Test Agent"
        assert "test_cap" in await facade.get_capabilities()
    
    async def test_create_powerbi_agent_function(self):
        """Test create_powerbi_agent convenience function."""
        facade = create_powerbi_agent("Custom PowerBI")
        
        assert facade.name == "Custom PowerBI"
        capabilities = await facade.get_capabilities()
        assert "data_model_analysis" in capabilities
    
    async def test_create_sql_agent_function(self):
        """Test create_sql_agent convenience function."""
        facade = create_sql_agent()
        
        assert "SQL Server Agent" in facade.name
        capabilities = await facade.get_capabilities()
        assert "query_execution" in capabilities
    
    async def test_create_analytics_agent_function(self):
        """Test create_analytics_agent convenience function."""
        facade = create_analytics_agent()
        
        assert "Analytics Agent" in facade.name
        capabilities = await facade.get_capabilities()
        assert "data_analysis" in capabilities


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
class TestFacadeIntegration:
    """Test facade integration with underlying agent systems."""
    
    async def test_facade_agent_integration(self):
        """Test that facade properly integrates with underlying Agent."""
        facade = AgentFacade("basic_agent")
        
        # Facade should have created underlying agent
        assert facade.agent is not None
        assert facade.agent.agent_id == facade.agent_id
        assert facade.agent.name == facade.name
    
    async def test_facade_body_brain_separation(self):
        """Test that facade properly uses Body-Brain separation."""
        facade = AgentFacade("basic_agent")
        
        # Should have communicator and reasoning engine
        assert hasattr(facade.agent, 'communicator')
        assert hasattr(facade.agent, 'reasoning_engine')
        assert facade.agent.communicator is not None
        assert facade.agent.reasoning_engine is not None
    
    async def test_facade_replaces_complex_agent_creation(self):
        """Test that facade can replace complex agent creation patterns."""
        # This is what tests were doing before (complex)
        # factory = AgentComponentFactory()
        # communicator, reasoning_engine = factory.create_basic_components(...)
        # agent = Agent(config, communicator, reasoning_engine, state_manager)
        
        # This is what tests can do now (simple)
        facade = AgentFacade("basic_agent")
        
        # Should work just as well
        await facade.start()
        capabilities = await facade.get_capabilities()
        assert len(capabilities) > 0
        await facade.stop()
    
    async def test_facade_message_handling_compatibility(self):
        """Test that facade message handling is compatible with SIMF."""
        facade = AgentFacade("basic_agent")
        await facade.start()
        
        # Create a proper SIMF message
        simf_message = create_text_message(
            text="Test message",
            target_agent_id=facade.agent_id,
            source_agent_id="test_source"
        )
        
        # Should be able to process it
        response = await facade.process_message(simf_message)
        
        # Response should be valid (may be None if no specific response)
        if response is not None:
            assert isinstance(response, SIMFMessage)
        
        await facade.stop()
