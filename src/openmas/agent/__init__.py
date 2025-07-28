"""
OpenMAS Agent Framework

This module provides the core agent framework for OpenMAS, including:
- Base Agent class with SIMF integration
- Agent factory for creating and configuring agents
- Protocol adapter interfaces
- State management interfaces
- Exception classes

Based on specifications in:
- refactoring_work/planning/TASK_basic_agent_framework_implementation.md
"""

# Core agent classes
from .base_agent import (
    Agent,
    AgentConfig,
    IAgentStateManager,
    IMessageHandler,
    IProtocolAdapter,
)

# Exceptions
from .exceptions import (
    AgentCapabilityError,
    AgentConfigurationError,
    AgentCreationError,
    AgentError,
    AgentLifecycleError,
    AgentMessageError,
    AgentProtocolError,
    AgentSessionError,
    AgentStateError,
)

# Factory functions and classes
from .factory import (
    AgentFactory,
    ConfigLoader,
    create_agent_from_config,
    create_agent_from_file,
    create_simple_agent,
    default_factory,
    register_agent_type,
    register_protocol_adapter,
)

# Facade Pattern - Simplified agent creation interface
from .facade import AgentFacade
from .builder import (
    AgentBuilder,
    create_agent,
    create_basic_agent,
    create_powerbi_agent,
    create_sql_agent,
    create_analytics_agent,
)

# Specialized agent implementations
from .mcp_agent import (
    MCPAgent,
    create_mcp_agent_from_config,
)

# Define what gets exported when using "from openmas.agent import *"
__all__ = [
    # Core classes
    "Agent",
    "AgentConfig",
    "IMessageHandler",
    "IAgentStateManager",
    "IProtocolAdapter",
    # Specialized implementations
    "MCPAgent",
    # Factory
    "AgentFactory",
    "ConfigLoader",
    "default_factory",
    # Convenience functions
    "create_agent_from_config",
    "create_agent_from_file",
    "create_simple_agent",
    "create_mcp_agent_from_config",
    "register_agent_type",
    "register_protocol_adapter",
    # Exceptions
    "AgentError",
    "AgentConfigurationError",
    "AgentCreationError",
    "AgentLifecycleError",
    "AgentMessageError",
    "AgentCapabilityError",
    "AgentSessionError",
    "AgentStateError",
    "AgentProtocolError",
]
