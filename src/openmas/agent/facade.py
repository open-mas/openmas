"""
OpenMAS Agent Facade Implementation

This module provides the AgentFacade class that implements the Facade Pattern
to provide a simplified, unified interface for OpenMAS agent creation and interaction.
The facade hides the complexity of subsystem initialization and coordination,
providing a clean API for common agent operations.

Based on specifications in:
- refactoring_work/planning/01_READY_TO_START/TASK_facade_pattern_remediation.md
- refactoring_work/design/01_architecture/architectural_patterns.md (lines 255-284)
"""

import uuid
from typing import Any, Dict, List, Optional, Union

from .base_agent import Agent, AgentConfig, IAgentStateManager, IProtocolAdapter
from .factories import AgentComponentFactory
from ..core.simf import SIMFMessage, MessageType, create_text_message, create_invocation_message


class AgentFacade:
    """
    Simplified interface for OpenMAS agent creation and interaction.
    
    Hides the complexity of subsystem initialization and coordination,
    providing a clean API for common agent operations.
    
    Examples:
        # Simple agent creation
        facade = AgentFacade("basic_agent")
        await facade.start()
        
        # Custom configuration
        config = AgentConfig(agent_id="my_agent", name="My Agent")
        facade = AgentFacade(config)
        
        # Preset configurations
        facade = AgentFacade("powerbi_agent")
    """
    
    def __init__(
        self, 
        config: Union[AgentConfig, Dict[str, Any], str],
        state_manager: Optional[IAgentStateManager] = None,
        protocol_adapters: Optional[Dict[str, IProtocolAdapter]] = None
    ):
        """
        Initialize AgentFacade with simplified configuration.
        
        Args:
            config: Agent configuration (AgentConfig, dict, or preset name)
            state_manager: Optional state manager instance
            protocol_adapters: Optional protocol adapters
        """
        # Normalize configuration
        self.config = self._normalize_config(config)
        
        # Initialize subsystems
        self._initialize_subsystems(state_manager, protocol_adapters)
        
        # Create the underlying agent with Body-Brain separation
        self._create_agent()
        
        # Facade state
        self._running = False
    
    def _normalize_config(self, config: Union[AgentConfig, Dict[str, Any], str]) -> AgentConfig:
        """Convert various config formats to AgentConfig."""
        if isinstance(config, str):
            # Load preset configuration
            return self._load_preset_config(config)
        elif isinstance(config, dict):
            # Convert dict to AgentConfig
            return AgentConfig(**config)
        elif isinstance(config, AgentConfig):
            return config
        else:
            raise ValueError(f"Invalid config type: {type(config)}")
    
    def _load_preset_config(self, preset_name: str) -> AgentConfig:
        """Load predefined agent configuration presets."""
        presets = {
            "basic_agent": AgentConfig(
                agent_id=f"basic_{uuid.uuid4().hex[:8]}",
                name="Basic Agent",
                capabilities=["message_handling"],
                protocol_configs={}
            ),
            "powerbi_agent": AgentConfig(
                agent_id=f"powerbi_{uuid.uuid4().hex[:8]}",
                name="PowerBI Data Model Agent",
                capabilities=["data_model_analysis", "query_optimization", "report_generation"],
                protocol_configs={"mcp": {"enabled": True}}
            ),
            "sql_agent": AgentConfig(
                agent_id=f"sql_{uuid.uuid4().hex[:8]}",
                name="SQL Server Agent",
                capabilities=["query_execution", "schema_analysis", "performance_tuning"],
                protocol_configs={"mcp": {"enabled": True}}
            ),
            "analytics_agent": AgentConfig(
                agent_id=f"analytics_{uuid.uuid4().hex[:8]}",
                name="Analytics Agent",
                capabilities=["data_analysis", "statistical_modeling", "visualization"],
                protocol_configs={"mcp": {"enabled": True}}
            )
        }
        
        if preset_name not in presets:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(presets.keys())}")
        
        return presets[preset_name]
    
    def _initialize_subsystems(
        self, 
        state_manager: Optional[IAgentStateManager] = None,
        protocol_adapters: Optional[Dict[str, IProtocolAdapter]] = None
    ) -> None:
        """Initialize all required subsystems with sensible defaults."""
        # Protocol adapters (use defaults if not specified)
        self.protocol_adapters = protocol_adapters or self._create_default_protocol_adapters()
        
        # State manager (use default if not specified)
        self.state_manager = state_manager or self._create_default_state_manager()
    
    def _create_default_protocol_adapters(self) -> Dict[str, IProtocolAdapter]:
        """Create default protocol adapters based on configuration."""
        adapters: dict[str, IProtocolAdapter] = {}
        
        # Create adapters based on protocol configs
        for protocol_name in self.config.protocol_configs:
            if protocol_name == "mcp":
                # Try to create MCP adapter if available
                try:
                    from ..protocols.mcp.adapter import MCPProtocolAdapter
                    adapters["mcp"] = MCPProtocolAdapter(self.config.agent_id)
                except ImportError:
                    # MCP adapter not available, skip
                    pass
                # Add other protocol adapters as they become available
        
        return adapters
    
    def _create_default_state_manager(self) -> Optional[IAgentStateManager]:
        """Create default state manager implementation."""
        # For now, return None (agent will use default behavior)
        # Future: Create DefaultStateManager implementation
        return None
    
    def _create_agent(self) -> None:
        """Create the underlying agent with Body-Brain separation."""
        # Use AgentComponentFactory to create Body-Brain components
        factory = AgentComponentFactory()
        communicator, reasoning_engine = factory.create_basic_components(
            agent_id=self.config.agent_id,
            capabilities=set(self.config.capabilities),
            protocol_adapters=self.protocol_adapters
        )
        
        # Create the underlying agent
        self.agent = Agent(
            config=self.config,
            communicator=communicator,
            reasoning_engine=reasoning_engine,
            state_manager=self.state_manager
        )
    
    # ========================================================================
    # Simplified Lifecycle Management
    # ========================================================================
    
    async def start(self) -> None:
        """Start the agent with simplified interface."""
        if self._running:
            return
        
        await self.agent.start()
        self._running = True
    
    async def stop(self) -> None:
        """Stop the agent with simplified interface."""
        if not self._running:
            return
        
        await self.agent.stop()
        self._running = False
    
    @property
    def is_running(self) -> bool:
        """Check if the agent is running."""
        return self._running
    
    # ========================================================================
    # Simplified Message Processing
    # ========================================================================
    
    async def send_message(
        self, 
        content: Any, 
        target: str, 
        message_type: str = "text"
    ) -> None:
        """
        Send message with simplified interface.
        
        Args:
            content: Message content (text, dict, or SIMFMessage)
            target: Target agent ID
            message_type: Type of message ("text", "capability", etc.)
            
        Returns:
            Response message if any
        """
        # Create SIMF message based on type
        if message_type == "text":
            message = create_text_message(
                text=str(content),
                target_agent_id=target,
                source_agent_id=self.agent.agent_id
            )
        elif message_type == "capability":
            message = create_invocation_message(
                invocation_name=content.get("capability", "unknown"),
                arguments=content.get("parameters", {}),
                target_agent_id=target,
                source_agent_id=self.agent.agent_id
            )
        else:
            # Try to normalize the message
            message = self._normalize_message(content, target)
        
        # Send through agent
        await self.agent.send_message(message)
    
    async def process_message(self, message: Any) -> None:
        """
        Process incoming message with simplified interface.
        
        Args:
            message: Incoming message (dict, SIMFMessage, or other format)
            
        Returns:
            Response message if any
        """
        # Normalize message to SIMF format
        simf_message = self._normalize_message(message)
        
        # Process through agent
        await self.agent._handle_message(simf_message)
    
    def _normalize_message(self, message: Any, target: Optional[str] = None) -> SIMFMessage:
        """Convert various message formats to SIMF."""
        if isinstance(message, SIMFMessage):
            return message
        elif isinstance(message, dict):
            # Convert dict to appropriate SIMF message
            if "capability" in message:
                return create_invocation_message(
                    invocation_name=message["capability"],
                    arguments=message.get("parameters", {}),
                    target_agent_id=target or self.agent.agent_id,
                    source_agent_id=message.get("source", "unknown")
                )
            else:
                return create_text_message(
                    text=message.get("text", str(message)),
                    target_agent_id=target or self.agent.agent_id,
                    source_agent_id=message.get("source", "unknown")
                )
        else:
            # Convert to text message
            return create_text_message(
                text=str(message),
                target_agent_id=target or self.agent.agent_id,
                source_agent_id="unknown"
            )
    
    # ========================================================================
    # Simplified Capability Management
    # ========================================================================
    
    async def add_capability(self, capability: str) -> None:
        """Add capability with simplified interface."""
        capabilities = await self.agent.get_capabilities()
        if capability not in capabilities:
            # Add to reasoning engine's capabilities
            if hasattr(self.agent.reasoning_engine, 'capabilities'):
                self.agent.reasoning_engine.capabilities.add(capability)
            # Also update config for consistency
            if capability not in self.config.capabilities:
                self.config.capabilities.append(capability)
    
    async def remove_capability(self, capability: str) -> None:
        """Remove capability with simplified interface."""
        # Remove from reasoning engine's capabilities
        if hasattr(self.agent.reasoning_engine, 'capabilities'):
            self.agent.reasoning_engine.capabilities.discard(capability)
        # Also update config for consistency
        if capability in self.config.capabilities:
            self.config.capabilities.remove(capability)
    
    async def get_capabilities(self) -> List[str]:
        """Get agent capabilities with simplified interface."""
        capabilities = await self.agent.get_capabilities()
        return list(capabilities)
    
    # ========================================================================
    # Status and Information
    # ========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "agent_id": self.agent.agent_id,
            "name": self.agent.name,
            "running": self._running,
            "capabilities": self.config.capabilities,
            "protocols": list(self.protocol_adapters.keys())
        }
    
    @property
    def agent_id(self) -> str:
        """Get agent ID."""
        return self.agent.agent_id
    
    @property
    def name(self) -> str:
        """Get agent name."""
        return self.agent.name
    
    # ========================================================================
    # Advanced Configuration (Optional)
    # ========================================================================
    
    def add_protocol_adapter(self, protocol: str, adapter: IProtocolAdapter) -> None:
        """Add protocol adapter with simplified interface."""
        self.protocol_adapters[protocol] = adapter
        # Update the communicator's protocol adapters
        if hasattr(self.agent.communicator, 'protocol_adapters'):
            self.agent.communicator.protocol_adapters[protocol] = adapter
