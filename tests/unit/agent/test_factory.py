"""
Unit tests for the OpenMAS Agent Factory.

These tests validate agent factory functionality including configuration loading,
agent creation, and dependency injection.
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import MagicMock

from openmas.agent import (
    AgentFactory,
    ConfigLoader,
    Agent,
    AgentConfig,
    AgentConfigurationError,
    AgentCreationError,
    default_factory,
    create_agent_from_config,
    create_simple_agent,
    IProtocolAdapter,
    IAgentStateManager,
)


# ============================================================================
# Mock Implementations
# ============================================================================

class CustomAgent(Agent):
    """Custom agent for testing factory registration."""
    
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.custom_attribute = "custom_value"


class MockStateManager(IAgentStateManager):
    """Mock state manager for testing."""
    
    async def set_state(self, key: str, value, scope: str = "PRIVATE_PERSISTENT") -> None:
        pass
    
    async def get_state(self, key: str, scope: str = "PRIVATE_PERSISTENT"):
        return None
    
    async def delete_state(self, key: str, scope: str = "PRIVATE_PERSISTENT") -> bool:
        return True
    
    async def has_state(self, key: str, scope: str = "PRIVATE_PERSISTENT") -> bool:
        return False
    
    async def list_state_keys(self, scope: str = "PRIVATE_PERSISTENT", prefix=None):
        return []


class MockProtocolAdapter(IProtocolAdapter):
    """Mock protocol adapter for testing."""
    
    async def connect(self, config) -> None:
        pass
    
    async def disconnect(self) -> None:
        pass
    
    async def send_message(self, internal_message) -> None:
        pass
    
    async def register_message_callback(self, callback) -> None:
        pass
    
    def to_internal_format(self, protocol_message):
        return MagicMock()
    
    def from_internal_format(self, internal_message):
        return MagicMock()


# ============================================================================
# Test Classes
# ============================================================================

class TestConfigLoader:
    """Test the ConfigLoader class."""
    
    def test_load_json_config(self):
        """Test loading JSON configuration."""
        config_data = {
            "agent_id": "test_agent",
            "name": "Test Agent",
            "capabilities": ["test_capability"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            loaded_config = ConfigLoader.load_from_file(temp_path)
            assert loaded_config == config_data
        finally:
            Path(temp_path).unlink()
    
    def test_load_yaml_config(self):
        """Test loading YAML configuration."""
        config_data = {
            "agent_id": "test_agent",
            "name": "Test Agent",
            "capabilities": ["test_capability"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.safe_dump(config_data, f)
            temp_path = f.name
        
        try:
            loaded_config = ConfigLoader.load_from_file(temp_path)
            assert loaded_config == config_data
        finally:
            Path(temp_path).unlink()
    
    def test_load_nonexistent_file(self):
        """Test loading nonexistent file raises error."""
        with pytest.raises(AgentConfigurationError, match="Configuration file not found"):
            ConfigLoader.load_from_file("nonexistent.json")
    
    def test_load_unsupported_format(self):
        """Test loading unsupported file format raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("some text")
            temp_path = f.name
        
        try:
            with pytest.raises(AgentConfigurationError, match="Unsupported config file format"):
                ConfigLoader.load_from_file(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = {
            "agent_id": "test_agent",
            "name": "Test Agent",
            "capabilities": ["test_capability"],
            "protocol_configs": {"mcp": {"server": "localhost"}}
        }
        
        # Should not raise any exception
        ConfigLoader.validate_config(config)
    
    def test_validate_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        # Missing agent_id
        config = {"name": "Test Agent"}
        with pytest.raises(AgentConfigurationError, match="Missing required field: agent_id"):
            ConfigLoader.validate_config(config)
        
        # Missing name
        config = {"agent_id": "test_agent"}
        with pytest.raises(AgentConfigurationError, match="Missing required field: name"):
            ConfigLoader.validate_config(config)
    
    def test_validate_invalid_field_types(self):
        """Test validation fails for invalid field types."""
        # Invalid agent_id type
        config = {"agent_id": 123, "name": "Test Agent"}
        with pytest.raises(AgentConfigurationError, match="agent_id must be a non-empty string"):
            ConfigLoader.validate_config(config)
        
        # Invalid capabilities type
        config = {"agent_id": "test", "name": "Test Agent", "capabilities": "not_a_list"}
        with pytest.raises(AgentConfigurationError, match="capabilities must be a list"):
            ConfigLoader.validate_config(config)
        
        # Invalid protocol_configs type
        config = {"agent_id": "test", "name": "Test Agent", "protocol_configs": "not_a_dict"}
        with pytest.raises(AgentConfigurationError, match="protocol_configs must be a dictionary"):
            ConfigLoader.validate_config(config)


class TestAgentFactory:
    """Test the AgentFactory class."""
    
    def test_factory_initialization(self):
        """Test basic factory initialization."""
        factory = AgentFactory()
        
        # Should have default agent type registered
        assert "base" in factory.get_registered_agent_types()
        assert factory._agent_types["base"] == Agent
    
    def test_register_agent_type(self):
        """Test registering custom agent types."""
        factory = AgentFactory()
        
        factory.register_agent_type("custom", CustomAgent)
        
        assert "custom" in factory.get_registered_agent_types()
        assert factory._agent_types["custom"] == CustomAgent
    
    def test_register_protocol_adapter(self):
        """Test registering protocol adapters."""
        factory = AgentFactory()
        adapter = MockProtocolAdapter()
        
        factory.register_protocol_adapter("mock", adapter)
        
        assert "mock" in factory.get_registered_protocol_adapters()
        assert factory._protocol_adapters["mock"] == adapter
    
    def test_set_default_state_manager(self):
        """Test setting default state manager."""
        factory = AgentFactory()
        state_manager = MockStateManager()
        
        factory.set_default_state_manager(state_manager)
        
        assert factory._default_state_manager == state_manager
    
    def test_create_agent_from_config(self):
        """Test creating agent from configuration."""
        factory = AgentFactory()
        config = {
            "agent_id": "test_agent",
            "name": "Test Agent",
            "capabilities": ["test_capability"]
        }
        
        agent = factory.create_agent_from_config(config)
        
        assert isinstance(agent, Agent)
        assert agent.agent_id == "test_agent"
        assert agent.name == "Test Agent"
        assert "test_capability" in agent.capabilities
    
    def test_create_custom_agent_from_config(self):
        """Test creating custom agent type from configuration."""
        factory = AgentFactory()
        factory.register_agent_type("custom", CustomAgent)
        
        config = {
            "agent_id": "test_agent",
            "name": "Test Agent",
            "type": "custom"
        }
        
        agent = factory.create_agent_from_config(config, agent_type="custom")
        
        assert isinstance(agent, CustomAgent)
        assert hasattr(agent, "custom_attribute")
        assert agent.custom_attribute == "custom_value"
    
    def test_create_agent_with_dependencies(self):
        """Test creating agent with dependencies."""
        factory = AgentFactory()
        state_manager = MockStateManager()
        protocol_adapter = MockProtocolAdapter()
        
        config = {
            "agent_id": "test_agent",
            "name": "Test Agent",
            "protocol_configs": {"mock": {"server": "localhost"}}
        }
        
        agent = factory.create_agent_from_config(
            config,
            state_manager=state_manager,
            protocol_adapters={"mock": protocol_adapter}
        )
        
        assert agent.state_manager == state_manager
        assert "mock" in agent.protocol_adapters
        assert agent.protocol_adapters["mock"] == protocol_adapter
    
    def test_create_agent_with_registered_dependencies(self):
        """Test creating agent with pre-registered dependencies."""
        factory = AgentFactory()
        state_manager = MockStateManager()
        protocol_adapter = MockProtocolAdapter()
        
        factory.set_default_state_manager(state_manager)
        factory.register_protocol_adapter("mock", protocol_adapter)
        
        config = {
            "agent_id": "test_agent",
            "name": "Test Agent",
            "protocol_configs": {"mock": {"server": "localhost"}}
        }
        
        agent = factory.create_agent_from_config(config)
        
        assert agent.state_manager == state_manager
        assert "mock" in agent.protocol_adapters
        assert agent.protocol_adapters["mock"] == protocol_adapter
    
    def test_create_agent_unknown_type(self):
        """Test creating agent with unknown type raises error."""
        factory = AgentFactory()
        config = {
            "agent_id": "test_agent",
            "name": "Test Agent"
        }
        
        with pytest.raises(AgentCreationError, match="Unknown agent type: unknown"):
            factory.create_agent_from_config(config, agent_type="unknown")
    
    def test_create_agent_invalid_config(self):
        """Test creating agent with invalid config raises error."""
        factory = AgentFactory()
        config = {"agent_id": "test"}  # Missing name
        
        with pytest.raises(AgentCreationError, match="Agent creation failed"):
            factory.create_agent_from_config(config)
    
    def test_create_agent_from_file(self):
        """Test creating agent from configuration file."""
        factory = AgentFactory()
        config_data = {
            "agent_id": "test_agent",
            "name": "Test Agent",
            "capabilities": ["test_capability"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            agent = factory.create_agent_from_file(temp_path)
            assert isinstance(agent, Agent)
            assert agent.agent_id == "test_agent"
            assert agent.name == "Test Agent"
        finally:
            Path(temp_path).unlink()
    
    def test_create_simple_agent(self):
        """Test creating simple agent with minimal configuration."""
        factory = AgentFactory()
        
        agent = factory.create_simple_agent(
            agent_id="simple_agent",
            name="Simple Agent",
            capabilities=["simple_capability"]
        )
        
        assert isinstance(agent, Agent)
        assert agent.agent_id == "simple_agent"
        assert agent.name == "Simple Agent"
        assert "simple_capability" in agent.capabilities


class TestDefaultFactory:
    """Test default factory and convenience functions."""
    
    def test_default_factory_exists(self):
        """Test that default factory is properly initialized."""
        assert default_factory is not None
        assert isinstance(default_factory, AgentFactory)
        assert "base" in default_factory.get_registered_agent_types()
    
    def test_create_agent_from_config_convenience(self):
        """Test convenience function for creating agent from config."""
        config = {
            "agent_id": "convenience_agent",
            "name": "Convenience Agent"
        }
        
        agent = create_agent_from_config(config)
        
        assert isinstance(agent, Agent)
        assert agent.agent_id == "convenience_agent"
        assert agent.name == "Convenience Agent"
    
    def test_create_simple_agent_convenience(self):
        """Test convenience function for creating simple agent."""
        agent = create_simple_agent(
            agent_id="simple_convenience",
            name="Simple Convenience Agent",
            capabilities=["convenience_capability"]
        )
        
        assert isinstance(agent, Agent)
        assert agent.agent_id == "simple_convenience"
        assert agent.name == "Simple Convenience Agent"
        assert "convenience_capability" in agent.capabilities
    
    def test_convenience_registration_functions(self):
        """Test convenience functions for registration."""
        # Clean up any previous registrations for this test
        original_types = default_factory.get_registered_agent_types().copy()
        original_adapters = default_factory.get_registered_protocol_adapters().copy()
        
        try:
            # Test agent type registration
            from openmas.agent import register_agent_type
            register_agent_type("test_custom", CustomAgent)
            assert "test_custom" in default_factory.get_registered_agent_types()
            
            # Test protocol adapter registration
            from openmas.agent import register_protocol_adapter
            adapter = MockProtocolAdapter()
            register_protocol_adapter("test_protocol", adapter)
            assert "test_protocol" in default_factory.get_registered_protocol_adapters()
            
        finally:
            # Clean up registrations
            # Note: In a real implementation, you might want to add cleanup methods
            # For this test, we'll just verify they were registered
            pass


if __name__ == "__main__":
    pytest.main([__file__]) 