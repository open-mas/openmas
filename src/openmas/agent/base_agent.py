"""
OpenMAS Base Agent Implementation

This module provides the core Agent class that serves as the foundation for all
OpenMAS agents. It integrates SIMF messaging, protocol adapters, and implements
the Phase 1 agent framework interfaces.

Based on specifications in:
- refactoring_work/planning/TASK_basic_agent_framework_implementation.md
- refactoring_work/design/completed/TASK_define_agent_framework_message_handling_api.md
- refactoring_work/design/completed/TASK_detail_agent_framework_state_management_api.md
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

from openmas.core.simf import (
    SIMFMessage,
    MessageType,
    MessageFlowDirection,
    PayloadType,
    create_text_message,
    create_invocation_message,
    create_invocation_result_message,
    create_error_message,
    InvocationStatus,
)


# ============================================================================
# Abstract Interfaces (Based on Phase 1 Specifications)
# ============================================================================

class IMessageHandler(ABC):
    """
    Interface for protocol-agnostic message handling within the Agent Framework.
    
    Based on: refactoring_work/design/completed/TASK_define_agent_framework_message_handling_api.md
    """
    
    @abstractmethod
    async def handle_incoming_message(
        self, 
        raw_message_data: Any, 
        source_protocol_adapter: 'IProtocolAdapter'
    ) -> None:
        """
        Handle incoming message from a protocol adapter.
        
        Args:
            raw_message_data: The data as received from the protocol adapter
            source_protocol_adapter: Instance of the adapter that received the message
        """
        pass
    
    @abstractmethod
    async def prepare_outgoing_message(
        self, 
        internal_message: SIMFMessage, 
        target_protocol_adapter: 'IProtocolAdapter'
    ) -> Any:
        """
        Prepare outgoing message for a protocol adapter.
        
        Args:
            internal_message: The message in SIMF format
            target_protocol_adapter: The protocol adapter that will send the message
            
        Returns:
            The platform-specific message object
        """
        pass


class IAgentStateManager(ABC):
    """
    Interface for agent state management.
    
    Based on: refactoring_work/design/completed/TASK_detail_agent_framework_state_management_api.md
    """
    
    @abstractmethod
    async def set_state(self, key: str, value: Any, scope: str = "PRIVATE_PERSISTENT") -> None:
        """Set state value for a key."""
        pass
    
    @abstractmethod
    async def get_state(self, key: str, scope: str = "PRIVATE_PERSISTENT") -> Any:
        """Get state value for a key."""
        pass
    
    @abstractmethod
    async def delete_state(self, key: str, scope: str = "PRIVATE_PERSISTENT") -> bool:
        """Delete state for a key."""
        pass
    
    @abstractmethod
    async def has_state(self, key: str, scope: str = "PRIVATE_PERSISTENT") -> bool:
        """Check if state exists for a key."""
        pass
    
    @abstractmethod
    async def list_state_keys(self, scope: str = "PRIVATE_PERSISTENT", prefix: Optional[str] = None) -> List[str]:
        """List all state keys."""
        pass


class IProtocolAdapter(ABC):
    """
    Interface for protocol adapters.
    
    Based on: refactoring_work/archive/phase_1/TASK_define_iprotocol_adapter_interface.md
    """
    
    @abstractmethod
    async def connect(self, config: Dict[str, Any]) -> None:
        """Initialize protocol connection."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up protocol connection."""
        pass
    
    @abstractmethod
    async def send_message(self, internal_message: SIMFMessage) -> None:
        """Send SIMF message via protocol."""
        pass
    
    @abstractmethod
    async def register_message_callback(
        self, 
        callback: Callable[[SIMFMessage], None]
    ) -> None:
        """Register callback for incoming messages."""
        pass
    
    @abstractmethod
    def to_internal_format(self, protocol_message: Any) -> SIMFMessage:
        """Convert protocol message to SIMF."""
        pass
    
    @abstractmethod
    def from_internal_format(self, internal_message: SIMFMessage) -> Any:
        """Convert SIMF to protocol message."""
        pass


# ============================================================================
# Agent Configuration
# ============================================================================

class AgentConfig:
    """Configuration for agent instances."""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        protocol_configs: Optional[Dict[str, Dict[str, Any]]] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.protocol_configs = protocol_configs or {}
        self.capabilities = capabilities or []
        self.metadata = metadata or {}


# ============================================================================
# Core Agent Implementation
# ============================================================================

class Agent(IMessageHandler):
    """
    Core OpenMAS Agent implementation.
    
    Provides SIMF-native messaging, protocol adapter integration, and implements
    the Phase 1 agent framework interfaces for a complete agent foundation.
    """
    
    def __init__(
        self,
        config: AgentConfig,
        state_manager: Optional[IAgentStateManager] = None,
        protocol_adapters: Optional[Dict[str, IProtocolAdapter]] = None
    ):
        """
        Initialize the agent.
        
        Args:
            config: Agent configuration
            state_manager: State management implementation
            protocol_adapters: Available protocol adapters
        """
        self.config = config
        self.agent_id = config.agent_id
        self.name = config.name
        
        # Core components
        self.state_manager = state_manager
        self.protocol_adapters = protocol_adapters or {}
        self.capabilities: Set[str] = set(config.capabilities)
        
        # Message handling
        self.message_queue: asyncio.Queue[SIMFMessage] = asyncio.Queue()
        self.message_callbacks: List[Callable[[SIMFMessage], None]] = []
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        # Session management
        self.current_session_id: Optional[str] = None
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Logging
        self.logger = logging.getLogger(f"openmas.agent.{self.agent_id}")
        
        self.logger.info(f"Agent {self.agent_id} ({self.name}) initialized")
    
    # ========================================================================
    # Agent Lifecycle Management
    # ========================================================================
    
    async def start(self) -> None:
        """Start the agent and its components."""
        if self._running:
            self.logger.warning("Agent is already running")
            return
        
        self.logger.info(f"Starting agent {self.agent_id}")
        
        # Start protocol adapters
        for adapter_name, adapter in self.protocol_adapters.items():
            try:
                config = self.config.protocol_configs.get(adapter_name, {})
                await adapter.connect(config)
                await adapter.register_message_callback(self._handle_protocol_message)
                self.logger.info(f"Protocol adapter {adapter_name} started")
            except Exception as e:
                self.logger.error(f"Failed to start protocol adapter {adapter_name}: {e}")
                raise
        
        # Start message processing
        self._running = True
        message_processor = asyncio.create_task(self._process_messages())
        self._tasks.append(message_processor)
        
        self.logger.info(f"Agent {self.agent_id} started successfully")
    
    async def stop(self) -> None:
        """Stop the agent and cleanup resources."""
        if not self._running:
            return
        
        self.logger.info(f"Stopping agent {self.agent_id}")
        
        self._running = False
        
        # Stop all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # Disconnect protocol adapters
        for adapter_name, adapter in self.protocol_adapters.items():
            try:
                await adapter.disconnect()
                self.logger.info(f"Protocol adapter {adapter_name} stopped")
            except Exception as e:
                self.logger.error(f"Error stopping protocol adapter {adapter_name}: {e}")
        
        self.logger.info(f"Agent {self.agent_id} stopped")
    
    # ========================================================================
    # SIMF Message Handling (Core Agent API)
    # ========================================================================
    
    async def send_message(self, message: SIMFMessage) -> None:
        """
        Send a SIMF message to another agent or external system.
        
        Args:
            message: The SIMF message to send
        """
        self.logger.debug(f"Sending message {message.message_id} to {message.target_agent_id}")
        
        # If target is external (has protocol specified), use protocol adapter
        if message.source_protocol_type and message.source_protocol_type in self.protocol_adapters:
            adapter = self.protocol_adapters[message.source_protocol_type]
            await adapter.send_message(message)
        else:
            # Internal message - add to local queue for processing
            await self.message_queue.put(message)
    
    async def receive_message(self) -> SIMFMessage:
        """
        Receive the next available SIMF message.
        
        Returns:
            The next SIMF message from the queue
        """
        return await self.message_queue.get()
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a tool/capability.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        self.logger.info(f"Executing tool {tool_name} with parameters: {parameters}")
        
        # Create invocation message
        invocation_msg = create_invocation_message(
            invocation_name=tool_name,
            arguments=parameters,
            target_agent_id=self.agent_id,
            source_agent_id=self.agent_id,
            session_id=self.current_session_id
        )
        
        # Process the tool execution
        try:
            result = await self._execute_capability(tool_name, parameters)
            
            # Create success result message
            result_msg = create_invocation_result_message(
                invocation_name=tool_name,
                status=InvocationStatus.SUCCESS,
                target_agent_id=self.agent_id,
                result={"output": result},
                source_agent_id=self.agent_id,
                session_id=self.current_session_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            
            # Create error result message
            error_msg = create_error_message(
                error_code="TOOL_EXECUTION_ERROR",
                error_message=str(e),
                target_agent_id=self.agent_id,
                source_agent_id=self.agent_id,
                session_id=self.current_session_id
            )
            
            raise
    
    # ========================================================================
    # Session Management
    # ========================================================================
    
    async def start_session(self, session_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new agent session.
        
        Args:
            session_config: Optional session configuration
            
        Returns:
            Session ID
        """
        session_id = str(uuid4())
        self.current_session_id = session_id
        
        self.sessions[session_id] = {
            "started_at": datetime.utcnow(),
            "config": session_config or {},
            "active": True
        }
        
        self.logger.info(f"Started session {session_id}")
        return session_id
    
    async def end_session(self, session_id: Optional[str] = None) -> None:
        """End a session."""
        session_id = session_id or self.current_session_id
        if session_id and session_id in self.sessions:
            self.sessions[session_id]["active"] = False
            self.sessions[session_id]["ended_at"] = datetime.utcnow()
            
            if session_id == self.current_session_id:
                self.current_session_id = None
            
            self.logger.info(f"Ended session {session_id}")
    
    # ========================================================================
    # Capability Management
    # ========================================================================
    
    async def register_capability(self, capability_name: str) -> None:
        """Register a new capability."""
        self.capabilities.add(capability_name)
        self.logger.info(f"Registered capability: {capability_name}")
    
    async def unregister_capability(self, capability_name: str) -> None:
        """Unregister a capability."""
        self.capabilities.discard(capability_name)
        self.logger.info(f"Unregistered capability: {capability_name}")
    
    def get_capabilities(self) -> List[str]:
        """Get list of available capabilities."""
        return list(self.capabilities)
    
    # ========================================================================
    # IMessageHandler Implementation
    # ========================================================================
    
    async def handle_incoming_message(
        self, 
        raw_message_data: Any, 
        source_protocol_adapter: IProtocolAdapter
    ) -> None:
        """Handle incoming message from a protocol adapter."""
        try:
            # Convert to SIMF format
            simf_message = source_protocol_adapter.to_internal_format(raw_message_data)
            
            # Update message metadata
            simf_message.target_agent_id = self.agent_id
            simf_message.message_flow_direction = MessageFlowDirection.INBOUND
            
            # Add to processing queue
            await self.message_queue.put(simf_message)
            
            self.logger.debug(f"Received message {simf_message.message_id} from protocol")
            
        except Exception as e:
            self.logger.error(f"Failed to handle incoming message: {e}")
            raise
    
    async def prepare_outgoing_message(
        self, 
        internal_message: SIMFMessage, 
        target_protocol_adapter: IProtocolAdapter
    ) -> Any:
        """Prepare outgoing message for a protocol adapter."""
        try:
            # Convert from SIMF to protocol format
            protocol_message = target_protocol_adapter.from_internal_format(internal_message)
            
            self.logger.debug(f"Prepared message {internal_message.message_id} for protocol")
            
            return protocol_message
            
        except Exception as e:
            self.logger.error(f"Failed to prepare outgoing message: {e}")
            raise
    
    # ========================================================================
    # Internal Message Processing
    # ========================================================================
    
    async def _process_messages(self) -> None:
        """Main message processing loop."""
        while self._running:
            try:
                # Wait for message with timeout to allow graceful shutdown
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self._handle_message(message)
                
            except asyncio.TimeoutError:
                continue  # Timeout is expected, continue loop
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    async def _handle_message(self, message: SIMFMessage) -> None:
        """Handle a SIMF message."""
        self.logger.debug(f"Processing message {message.message_id} of type {message.message_type}")
        
        # Call registered callbacks
        for callback in self.message_callbacks:
            try:
                await callback(message) if asyncio.iscoroutinefunction(callback) else callback(message)
            except Exception as e:
                self.logger.error(f"Error in message callback: {e}")
        
        # Handle based on message type
        if message.message_type == MessageType.CAPABILITY_INVOCATION:
            await self._handle_capability_invocation(message)
        elif message.message_type == MessageType.USER_QUERY:
            await self._handle_user_query(message)
        # Add more message type handlers as needed
    
    async def _handle_protocol_message(self, simf_message: SIMFMessage) -> None:
        """Handle message from protocol adapter."""
        await self.message_queue.put(simf_message)
    
    async def _handle_capability_invocation(self, message: SIMFMessage) -> None:
        """Handle capability invocation message."""
        if hasattr(message.payload, 'invocation_name') and hasattr(message.payload, 'arguments'):
            tool_name = message.payload.invocation_name
            parameters = message.payload.arguments
            
            try:
                result = await self._execute_capability(tool_name, parameters)
                
                # Send success response
                response = create_invocation_result_message(
                    invocation_name=tool_name,
                    status=InvocationStatus.SUCCESS,
                    target_agent_id=message.source_agent_id or "unknown",
                    result={"output": result},
                    source_agent_id=self.agent_id,
                    session_id=message.session_id
                )
                await self.send_message(response)
                
            except Exception as e:
                # Send error response
                error_response = create_error_message(
                    error_code="CAPABILITY_ERROR",
                    error_message=str(e),
                    target_agent_id=message.source_agent_id or "unknown",
                    source_agent_id=self.agent_id,
                    session_id=message.session_id
                )
                await self.send_message(error_response)
    
    async def _handle_user_query(self, message: SIMFMessage) -> None:
        """Handle user query message."""
        # Default implementation - can be overridden by subclasses
        self.logger.info(f"Received user query: {message.payload}")
        
        # Echo response for now
        response = create_text_message(
            content=f"Agent {self.name} received your message",
            target_agent_id=message.source_agent_id or "unknown",
            source_agent_id=self.agent_id,
            session_id=message.session_id
        )
        await self.send_message(response)
    
    async def _execute_capability(self, capability_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a capability.
        
        This is a placeholder implementation that should be overridden by subclasses
        or enhanced with a proper capability registry.
        """
        if capability_name not in self.capabilities:
            raise ValueError(f"Capability '{capability_name}' not registered")
        
        # Default implementation - return parameters for testing
        return {
            "capability": capability_name,
            "parameters": parameters,
            "executed_by": self.agent_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def add_message_callback(self, callback: Callable[[SIMFMessage], None]) -> None:
        """Add a message callback."""
        self.message_callbacks.append(callback)
    
    def remove_message_callback(self, callback: Callable[[SIMFMessage], None]) -> None:
        """Remove a message callback."""
        if callback in self.message_callbacks:
            self.message_callbacks.remove(callback) 