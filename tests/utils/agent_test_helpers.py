"""
Comprehensive test utilities for OpenMAS agent testing.

This module provides helper functions and classes to simplify agent testing
while maintaining compatibility with the Body-Brain separation architecture.
"""

from typing import Any, Dict, List, Optional, Union
from unittest.mock import AsyncMock, MagicMock

from openmas.agent.facade import AgentFacade
from openmas.agent.base_agent import Agent, AgentConfig, IAgentStateManager, IProtocolAdapter
from openmas.core.simf import SIMFMessage


# ============================================================================
# Mock Implementations
# ============================================================================

class TestStateManager(IAgentStateManager):
    """Test state manager implementation."""
    
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
    
    async def list_state_keys(self, scope: str = "PRIVATE_PERSISTENT") -> List[str]:
        prefix = f"{scope}:"
        return [key[len(prefix):] for key in self._state.keys() if key.startswith(prefix)]


class TestProtocolAdapter(IProtocolAdapter):
    """Test protocol adapter implementation."""
    
    def __init__(self):
        self.started = False
        self.messages = []
        self.callbacks = []
    
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
        self.callbacks.append(callback)
    
    def to_internal_format(self, external_message: Any) -> SIMFMessage:
        # Simple conversion for testing
        if isinstance(external_message, SIMFMessage):
            return external_message
        return SIMFMessage(
            target_agent_id="test",
            source_agent_id="test",
            session_id="test",
            message_flow_direction="INBOUND",
            message_type="PLAIN_TEXT_MESSAGE",
            payload={"text": str(external_message)},
            source_protocol_type="test"
        )
    
    def from_internal_format(self, internal_message: SIMFMessage) -> Any:
        return internal_message


# ============================================================================
# Agent Creation Helpers
# ============================================================================

def create_test_agent(
    agent_id: str = "test_agent",
    name: str = "Test Agent",
    capabilities: Optional[List[str]] = None,
    state_manager: Optional[IAgentStateManager] = None,
    protocol_adapters: Optional[Dict[str, IProtocolAdapter]] = None,
    config: Optional[Union[AgentConfig, Dict[str, Any]]] = None
) -> Agent:
    """
    Create a test agent using the AgentFacade for simplified setup.
    
    Args:
        agent_id: Agent identifier
        name: Agent name
        capabilities: List of capabilities
        state_manager: Optional state manager
        protocol_adapters: Optional protocol adapters
        config: Optional custom configuration
        
    Returns:
        Agent instance ready for testing
    """
    if config is None:
        config = AgentConfig(
            agent_id=agent_id,
            name=name,
            capabilities=capabilities or []
        )
    elif isinstance(config, dict):
        config = AgentConfig(**config)
    
    # Use AgentFacade for simplified creation
    facade = AgentFacade(
        config=config,
        state_manager=state_manager,
        protocol_adapters=protocol_adapters
    )
    
    return facade.agent


def create_test_facade(
    preset_or_config: Union[str, AgentConfig, Dict[str, Any]] = "basic_agent",
    **kwargs
) -> AgentFacade:
    """
    Create a test facade with optional customizations.
    
    Args:
        preset_or_config: Preset name, AgentConfig, or config dict
        **kwargs: Additional arguments for AgentFacade
        
    Returns:
        AgentFacade instance ready for testing
    """
    return AgentFacade(preset_or_config, **kwargs)


# ============================================================================
# Async Test Helpers
# ============================================================================

async def assert_agent_capabilities(agent: Agent, expected_capabilities: List[str]):
    """Assert that agent has expected capabilities."""
    actual_capabilities = await agent.get_capabilities()
    for capability in expected_capabilities:
        assert capability in actual_capabilities, f"Expected capability '{capability}' not found in {actual_capabilities}"


async def assert_agent_can_start_stop(agent: Agent):
    """Assert that agent can start and stop properly."""
    assert not agent._running
    await agent.start()
    assert agent._running
    await agent.stop()
    assert not agent._running
