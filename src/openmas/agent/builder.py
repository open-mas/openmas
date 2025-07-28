"""
OpenMAS Agent Builder Implementation

This module provides the AgentBuilder class that implements the Builder Pattern
for fluent agent configuration. It works with the AgentFacade to provide
flexible agent creation without exposing internal complexity.

Based on specifications in:
- refactoring_work/planning/01_READY_TO_START/TASK_facade_pattern_remediation.md
"""

from typing import Any, Dict, List, Optional, Union

from .base_agent import AgentConfig, IAgentStateManager, IProtocolAdapter
from .facade import AgentFacade


class AgentBuilder:
    """
    Builder for fluent agent configuration.
    
    Provides a fluent interface for creating complex agent configurations
    without exposing the underlying complexity of subsystem initialization.
    
    Examples:
        # Simple agent
        agent = (AgentBuilder()
                .with_name("My Agent")
                .with_capability("data_analysis")
                .build())
        
        # Complex agent
        agent = (AgentBuilder()
                .with_id("analytics_001")
                .with_name("Analytics Agent")
                .with_capabilities(["data_analysis", "visualization"])
                .with_protocol("mcp", mcp_adapter)
                .with_state_manager(custom_state_manager)
                .build())
    """
    
    def __init__(self):
        """Initialize the builder with default values."""
        self._agent_id: Optional[str] = None
        self._name: Optional[str] = None
        self._capabilities: List[str] = []
        self._protocol_configs: Dict[str, Dict[str, Any]] = {}
        self._protocol_adapters: Dict[str, IProtocolAdapter] = {}
        self._state_manager: Optional[IAgentStateManager] = None
        self._metadata: Dict[str, Any] = {}
    
    def with_id(self, agent_id: str) -> 'AgentBuilder':
        """Set the agent ID."""
        self._agent_id = agent_id
        return self
    
    def with_name(self, name: str) -> 'AgentBuilder':
        """Set the agent name."""
        self._name = name
        return self
    
    def with_capability(self, capability: str) -> 'AgentBuilder':
        """Add a single capability."""
        if capability not in self._capabilities:
            self._capabilities.append(capability)
        return self
    
    def with_capabilities(self, capabilities: List[str]) -> 'AgentBuilder':
        """Add multiple capabilities."""
        for capability in capabilities:
            self.with_capability(capability)
        return self
    
    def with_protocol(
        self, 
        protocol_name: str, 
        adapter: Optional[IProtocolAdapter] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> 'AgentBuilder':
        """
        Add a protocol configuration.
        
        Args:
            protocol_name: Name of the protocol (e.g., "mcp")
            adapter: Optional protocol adapter instance
            config: Optional protocol configuration
        """
        # Add protocol config
        self._protocol_configs[protocol_name] = config or {"enabled": True}
        
        # Add adapter if provided
        if adapter is not None:
            self._protocol_adapters[protocol_name] = adapter
        
        return self
    
    def with_mcp_protocol(self, adapter: Optional[IProtocolAdapter] = None) -> 'AgentBuilder':
        """Convenience method for adding MCP protocol."""
        return self.with_protocol("mcp", adapter)
    
    def with_state_manager(self, state_manager: IAgentStateManager) -> 'AgentBuilder':
        """Set the state manager."""
        self._state_manager = state_manager
        return self
    
    def with_metadata(self, key: str, value: Any) -> 'AgentBuilder':
        """Add metadata."""
        self._metadata[key] = value
        return self
    
    def with_preset(self, preset_name: str) -> 'AgentBuilder':
        """
        Load a preset configuration and merge with current builder state.
        
        Args:
            preset_name: Name of the preset to load
        """
        # Create a temporary facade to get the preset config
        temp_facade = AgentFacade(preset_name)
        preset_config = temp_facade.config
        
        # Merge preset values (only if not already set)
        if self._agent_id is None:
            self._agent_id = preset_config.agent_id
        if self._name is None:
            self._name = preset_config.name
        
        # Merge capabilities (avoid duplicates)
        for capability in preset_config.capabilities:
            self.with_capability(capability)
        
        # Merge protocol configs
        for protocol, config in preset_config.protocol_configs.items():
            if protocol not in self._protocol_configs:
                self._protocol_configs[protocol] = config
        
        # Merge metadata
        for key, value in preset_config.metadata.items():
            if key not in self._metadata:
                self._metadata[key] = value
        
        return self
    
    def build(self) -> AgentFacade:
        """
        Build the agent facade with the configured settings.
        
        Returns:
            Configured AgentFacade instance
        
        Raises:
            ValueError: If required configuration is missing
        """
        # Validate required fields
        if self._name is None:
            raise ValueError("Agent name is required")
        
        # Generate agent ID if not provided
        if self._agent_id is None:
            import uuid
            self._agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        
        # Create agent configuration
        config = AgentConfig(
            agent_id=self._agent_id,
            name=self._name,
            capabilities=self._capabilities,
            protocol_configs=self._protocol_configs,
            metadata=self._metadata
        )
        
        # Create and return facade
        return AgentFacade(
            config=config,
            state_manager=self._state_manager,
            protocol_adapters=self._protocol_adapters
        )


# ============================================================================
# Convenience Functions
# ============================================================================

def create_agent() -> AgentBuilder:
    """Create a new agent builder."""
    return AgentBuilder()

def create_basic_agent(name: str, capabilities: Optional[List[str]] = None) -> AgentFacade:
    """
    Create a basic agent with minimal configuration.
    
    Args:
        name: Agent name
        capabilities: Optional list of capabilities
        
    Returns:
        Configured AgentFacade instance
    """
    builder = AgentBuilder().with_name(name)
    
    if capabilities:
        builder = builder.with_capabilities(capabilities)
    
    return builder.build()

def create_powerbi_agent(name: Optional[str] = None) -> AgentFacade:
    """
    Create a PowerBI agent with preset configuration.
    
    Args:
        name: Optional custom name (uses preset name if not provided)
        
    Returns:
        Configured AgentFacade for PowerBI workflows
    """
    builder = AgentBuilder().with_preset("powerbi_agent")
    
    if name:
        builder = builder.with_name(name)
    
    return builder.build()

def create_sql_agent(name: Optional[str] = None) -> AgentFacade:
    """
    Create a SQL Server agent with preset configuration.
    
    Args:
        name: Optional custom name (uses preset name if not provided)
        
    Returns:
        Configured AgentFacade for SQL Server workflows
    """
    builder = AgentBuilder().with_preset("sql_agent")
    
    if name:
        builder = builder.with_name(name)
    
    return builder.build()

def create_analytics_agent(name: Optional[str] = None) -> AgentFacade:
    """
    Create an analytics agent with preset configuration.
    
    Args:
        name: Optional custom name (uses preset name if not provided)
        
    Returns:
        Configured AgentFacade for analytics workflows
    """
    builder = AgentBuilder().with_preset("analytics_agent")
    
    if name:
        builder = builder.with_name(name)
    
    return builder.build()
