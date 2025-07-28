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
from collections.abc import Callable
from datetime import datetime
from typing import Any, Awaitable
from uuid import uuid4

from openmas.core.simf import (
    InvocationStatus,
    MessageFlowDirection,
    MessageType,
    SIMFMessage,
    create_error_message,
    create_invocation_result_message,
    create_text_message,
)

# Import Body-Brain separation interfaces
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .interfaces.communicator import ICommunicator
    from .interfaces.reasoning import IReasoningEngine

# ============================================================================
# Abstract Interfaces (Based on Phase 1 Specifications)
# ============================================================================


class IMessageHandler(ABC):
    """
    Interface for protocol-agnostic message handling within the Agent Framework.

    Based on: refactoring_work/design/completed/
    TASK_define_agent_framework_message_handling_api.md
    """

    @abstractmethod
    async def handle_incoming_message(self, raw_message_data: Any, source_protocol_adapter: "IProtocolAdapter") -> None:
        """
        Handle incoming message from a protocol adapter.

        Args:
            raw_message_data: The data as received from the protocol adapter
            source_protocol_adapter: Instance of the adapter that received the message
        """
        pass

    @abstractmethod
    async def prepare_outgoing_message(
        self, internal_message: SIMFMessage, target_protocol_adapter: "IProtocolAdapter"
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

    Based on: refactoring_work/design/completed/
    TASK_detail_agent_framework_state_management_api.md
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
    async def list_state_keys(self, scope: str = "PRIVATE_PERSISTENT", prefix: str | None = None) -> list[str]:
        """List all state keys."""
        pass


class IProtocolAdapter(ABC):
    """
    Interface for protocol adapters.

    Based on: refactoring_work/archive/phase_1/
    TASK_define_iprotocol_adapter_interface.md
    """

    @abstractmethod
    async def connect(self, config: dict[str, Any]) -> None:
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
    async def register_message_callback(self, callback: Callable[[SIMFMessage], Awaitable[None]]) -> None:
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
        protocol_configs: dict[str, dict[str, Any]] | None = None,
        capabilities: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
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
    Refactored Agent with proper Body-Brain separation.
    
    The Agent orchestrates between the Communicator (body) and ReasoningEngine (brain)
    but does not implement communication or reasoning logic directly. This enables
    reasoning agnosticism and protocol independence.
    """

    def __init__(
        self,
        config: AgentConfig,
        communicator: "ICommunicator",
        reasoning_engine: "IReasoningEngine",
        state_manager: IAgentStateManager | None = None,
    ):
        """
        Initialize agent with separated components.
        
        Args:
            config: Agent configuration
            communicator: Communication infrastructure (body)
            reasoning_engine: Reasoning logic (brain)
            state_manager: State management implementation
        """
        self.config = config
        self.agent_id = config.agent_id
        self.name = config.name
        
        # Body-Brain separation components
        self.communicator = communicator
        self.reasoning_engine = reasoning_engine
        
        # Core components
        self.state_manager = state_manager
        
        # Message handling
        self.message_queue: asyncio.Queue[SIMFMessage] | None = None
        self.message_callbacks: list[Callable[[SIMFMessage], None]] = []
        self._running = False
        self._tasks: list[asyncio.Task] = []
        
        # Session management
        self.current_session_id: str | None = None
        self.sessions: dict[str, dict[str, Any]] = {}
        
        # Logging
        self.logger = logging.getLogger(f"openmas.agent.{self.agent_id}")
        self.logger.info(f"Agent {self.agent_id} ({self.name}) initialized with {reasoning_engine.get_reasoning_type()} reasoning")
    
    @property
    def is_running(self) -> bool:
        """Check if the agent is currently running."""
        return self._running

    def __del__(self):
        """Ensure cleanup if stop() wasn't called."""
        if self._running:
            self.logger.warning(f"Agent {self.agent_id} was not properly stopped")
            # Force cleanup without async (best effort)
            self._running = False
            for task in self._tasks:
                if not task.done():
                    task.cancel()

    # ========================================================================
    # Agent Lifecycle Management
    # ========================================================================

    async def start(self) -> None:
        """Start the agent and its components."""
        if self._running:
            self.logger.warning("Agent is already running")
            return

        self.logger.info(f"Starting agent {self.agent_id}")

        # Initialize message queue in current event loop context
        self.message_queue = asyncio.Queue()

        # CRITICAL FIX: Register message handler with protocol adapters
        # This ensures incoming messages from protocol adapters are routed to the agent
        try:
            await self.communicator.register_message_callback(self._handle_protocol_message)
            self.logger.debug("Registered message callback with protocol adapters")
        except Exception as e:
            self.logger.error(f"Failed to register message callback: {e}")
            raise RuntimeError(f"Agent startup failed: Could not register message callback - {e}")

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
            if not task.done():
                task.cancel()

        # Wait for tasks to complete with proper error handling
        if self._tasks:
            try:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            except Exception as e:
                self.logger.debug(f"Task cleanup completed with exceptions: {e}")

        # Clear task list
        self._tasks.clear()

        # Note: Protocol adapters are now managed by the communicator (Body-Brain separation)
        # The communicator handles all protocol-specific cleanup

        # Clear message queue
        if self.message_queue is not None:
            while not self.message_queue.empty():
                try:
                    self.message_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            self.message_queue = None

        self.logger.info(f"Agent {self.agent_id} stopped")

    # ========================================================================
    # SIMF Message Handling (Core Agent API)
    # ========================================================================

    async def send_message(self, message: SIMFMessage) -> None:
        """
        Send a SIMF message using the communicator (Body-Brain separation).

        Args:
            message: The SIMF message to send
        """
        self.logger.debug(f"Sending message {message.message_id} to {message.target_agent_id}")
        
        # Use communicator for all message sending (Body-Brain separation)
        await self.communicator.send_message(message)

    async def receive_message(self) -> SIMFMessage:
        """
        Receive the next available SIMF message.

        Returns:
            The next SIMF message from the queue
        """
        if self.message_queue is None:
            raise RuntimeError("Agent not started - message queue not initialized")
        return await self.message_queue.get()

    async def execute_tool(self, tool_name: str, parameters: dict[str, Any]) -> Any:
        """
        Execute a tool/capability.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        self.logger.info(f"Executing tool {tool_name} with parameters: {parameters}")

        # Process the tool execution
        try:
            result = await self._execute_capability(tool_name, parameters)
            return result

        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            raise

    async def _execute_capability(self, capability_name: str, parameters: dict[str, Any]) -> Any:
        """
        Execute a capability through the reasoning engine (Body-Brain separation).
        
        Args:
            capability_name: Name of the capability to execute
            parameters: Parameters for the capability
            
        Returns:
            Result of capability execution
        """
        # Check if capability is available
        capabilities = await self.get_capabilities()
        if capability_name not in capabilities:
            raise ValueError(f"Capability '{capability_name}' not registered")
        
        # Delegate to reasoning engine for capability execution
        context = {
            "message_type": "CAPABILITY_INVOCATION",
            "invocation_name": capability_name,
            "arguments": parameters,
            "sender": "internal",
            "session": "capability_execution",
            "metadata": {}
        }
        action = await self.reasoning_engine.decide_action(context)
        # For capability invocation, return the result directly from reasoning engine
        if action.get("type") == "invocation_result":
            return action.get("content", {}).get("result", {})
        return action.get("content", {})

    # ========================================================================
    # Session Management
    # ========================================================================

    async def start_session(self, session_config: dict[str, Any] | None = None) -> str:
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
            "active": True,
        }

        self.logger.info(f"Started session {session_id}")
        return session_id

    async def end_session(self, session_id: str | None = None) -> None:
        """End a session."""
        session_id = session_id or self.current_session_id
        if session_id and session_id in self.sessions:
            self.sessions[session_id]["active"] = False
            self.sessions[session_id]["ended_at"] = datetime.utcnow()

            if session_id == self.current_session_id:
                self.current_session_id = None

            self.logger.info(f"Ended session {session_id}")

    # ========================================================================
    # Reasoning Engine Management (Body-Brain Separation)
    # ========================================================================
    
    def set_reasoning_engine(self, reasoning_engine: "IReasoningEngine") -> None:
        """Enable runtime reasoning engine swapping."""
        old_type = self.reasoning_engine.get_reasoning_type()
        self.reasoning_engine = reasoning_engine
        new_type = reasoning_engine.get_reasoning_type()
        self.logger.info(f"Reasoning engine changed from {old_type} to {new_type}")
    
    def get_reasoning_type(self) -> str:
        """Get the current reasoning engine type."""
        return self.reasoning_engine.get_reasoning_type()
    
    async def get_capabilities(self) -> set[str]:
        """Get capabilities from the reasoning engine."""
        return await self.reasoning_engine.get_capabilities()
    
    async def update_reasoning_knowledge(self, knowledge: dict[str, Any]) -> None:
        """Update the reasoning engine's knowledge base."""
        await self.reasoning_engine.update_knowledge(knowledge)
        self.logger.debug("Reasoning engine knowledge updated")

    # ========================================================================
    # IMessageHandler Implementation
    # ========================================================================

    async def handle_incoming_message(self, raw_message_data: Any, source_protocol_adapter: IProtocolAdapter) -> None:
        """Handle incoming message from a protocol adapter."""
        try:
            # Convert to SIMF format
            simf_message = source_protocol_adapter.to_internal_format(raw_message_data)

            # Update message metadata
            simf_message.target_agent_id = self.agent_id
            simf_message.message_flow_direction = MessageFlowDirection.INBOUND

            # Add to processing queue
            if self.message_queue is None:
                raise RuntimeError("Agent not started - message queue not initialized")
            await self.message_queue.put(simf_message)

            self.logger.debug(f"Received message {simf_message.message_id} from protocol")

        except Exception as e:
            self.logger.error(f"Failed to handle incoming message: {e}")
            raise

    async def prepare_outgoing_message(
        self, internal_message: SIMFMessage, target_protocol_adapter: IProtocolAdapter
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
        if self.message_queue is None:
            self.logger.error("Message queue not initialized")
            return

        try:
            while self._running:
                try:
                    # Check if we're still running before each operation
                    if not self._running:
                        break

                    # Wait for message with timeout to allow graceful shutdown
                    message = await asyncio.wait_for(self.message_queue.get(), timeout=0.5)

                    # Double-check we're still running after getting message
                    if not self._running:
                        break

                    await self._handle_message(message)

                except asyncio.TimeoutError:
                    continue  # Timeout is expected, continue loop
                except RuntimeError as e:
                    if "no running event loop" in str(e) or "Event loop is closed" in str(e):
                        self.logger.debug("Event loop closed, stopping message processing")
                        break
                    else:
                        self.logger.error(f"Runtime error processing message: {e}")
                        break
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    # Don't break on general exceptions, but log them
        except asyncio.CancelledError:
            # Handle cancellation gracefully
            self.logger.debug("Message processing task cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in message processing loop: {e}")
        finally:
            self.logger.debug("Message processing loop ended")

    async def _handle_message(self, message: SIMFMessage) -> None:
        """
        Process message using Body-Brain separation pattern.
        
        1. Communicator (body) parses message into context
        2. Reasoning engine (brain) decides on action
        3. Communicator (body) formats and sends response
        """
        self.logger.debug(f"Processing message {message.message_id} of type {message.message_type}")
        
        # Call registered callbacks
        for callback in self.message_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                self.logger.error(f"Error in message callback: {e}")
        
        try:
            # Body-Brain separation: Communicator parses message
            context = await self.communicator.parse_message(message)
            
            # Body-Brain separation: Reasoning engine decides action
            action = await self.reasoning_engine.decide_action(context)
            
            # Body-Brain separation: Communicator formats and sends response
            response = await self.communicator.format_response(action)
            await self.communicator.send_message(response)
            
        except Exception as e:
            self.logger.error(f"Error processing message {message.message_id}: {e}")
            # Send error response
            error_action = {
                "type": "error",
                "content": {
                    "error_code": "MESSAGE_PROCESSING_ERROR",
                    "error_message": str(e)
                },
                "sender": self.agent_id,
                "session": message.session_id,
                "target": message.source_agent_id or "unknown"
            }
            try:
                error_response = await self.communicator.format_response(error_action)
                await self.communicator.send_message(error_response)
            except Exception as format_error:
                self.logger.error(f"Failed to send error response: {format_error}")

    async def _handle_protocol_message(self, simf_message: SIMFMessage) -> None:
        """Handle message from protocol adapter."""
        if self.message_queue is None:
            raise RuntimeError("Agent not started - message queue not initialized")
        await self.message_queue.put(simf_message)





    def add_message_callback(self, callback: Callable[[SIMFMessage], None]) -> None:
        """Add a message callback."""
        self.message_callbacks.append(callback)

    def remove_message_callback(self, callback: Callable[[SIMFMessage], None]) -> None:
        """Remove a message callback."""
        if callback in self.message_callbacks:
            self.message_callbacks.remove(callback)
