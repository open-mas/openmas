"""
Default Communicator Implementation for OpenMAS Agent Body-Brain Separation

This module provides the DefaultCommunicator class that implements the ICommunicator
interface, handling all external communication while remaining agnostic to reasoning logic.
"""

import logging
from typing import Any, Dict, List
from openmas.core.simf import (
    SIMFMessage,
    MessageType,
    create_text_message,
    create_invocation_result_message,
    create_error_message,
    InvocationStatus,
)
from .interfaces.communicator import ICommunicator
from .base_agent import IProtocolAdapter


class DefaultCommunicator(ICommunicator):
    """
    Default communicator implementation using protocol adapters.
    
    Handles all external communication protocols while remaining completely
    agnostic to reasoning logic. Provides standardized context parsing and
    response formatting for reasoning engines.
    """
    
    def __init__(self, agent_id: str, protocol_adapters: Dict[str, "IProtocolAdapter"] | None = None):
        """
        Initialize communicator with protocol adapters.
        
        Args:
            agent_id: ID of the agent this communicator serves
            protocol_adapters: Dictionary of protocol adapters
        """
        self.agent_id = agent_id
        self.protocol_adapters = protocol_adapters or {}
        self.logger = logging.getLogger(f"openmas.communicator.{agent_id}")
        # Track which protocol adapter each session is using
        self.session_protocol_map: Dict[str, str] = {}
        
    async def parse_message(self, message: SIMFMessage) -> Dict[str, Any]:
        """
        Parse incoming message into context for reasoning engine.
        
        Converts SIMF message into standardized context dictionary that
        reasoning engines can process without protocol awareness.
        """
        context = {
            "message_type": message.message_type.value if hasattr(message.message_type, 'value') else str(message.message_type),
            "content": self._extract_content(message),
            "sender": message.source_agent_id or "unknown",
            "session": message.session_id,
            "metadata": {
                "message_id": message.message_id,
                "timestamp": message.timestamp,
                "flow_direction": message.message_flow_direction.value if hasattr(message.message_flow_direction, 'value') else str(message.message_flow_direction),
                "target_agent_id": message.target_agent_id,
            }
        }
        
        # Add message-type specific context
        if message.message_type == MessageType.CAPABILITY_INVOCATION:
            if hasattr(message.payload, 'invocation_name') and hasattr(message.payload, 'arguments'):
                context["invocation_name"] = message.payload.invocation_name
                context["arguments"] = message.payload.arguments
                
        return context
    
    async def format_response(self, action: Dict[str, Any]) -> SIMFMessage:
        """
        Format reasoning engine action into SIMF message.
        
        Converts reasoning engine decision into proper SIMF message format
        for protocol adapter transmission.
        """
        action_type = action.get("type", "text")
        content = action.get("content", {})
        sender_id = action.get("sender", self.agent_id)
        session_id = action.get("session", "default")
        target_id = action.get("target", "unknown")
        
        if action_type == "text":
            return create_text_message(
                text=content.get("message", str(content)),
                target_agent_id=target_id,
                source_agent_id=sender_id,
                session_id=session_id
            )
        elif action_type == "invocation_result":
            return create_invocation_result_message(
                invocation_name=content.get("invocation_name", "unknown"),
                status=InvocationStatus.SUCCESS,
                target_agent_id=target_id,
                result=content.get("result", {}),
                message_type=MessageType.CAPABILITY_RESULT,
                source_agent_id=sender_id,
                session_id=session_id
            )
        elif action_type == "error":
            return create_error_message(
                error_code=content.get("error_code", "UNKNOWN_ERROR"),
                error_message=content.get("error_message", str(content)),
                target_agent_id=target_id,
                source_agent_id=sender_id,
                session_id=session_id
            )
        else:
            # Default to text message
            return create_text_message(
                text=f"Unknown action type: {action_type}",
                target_agent_id=target_id,
                source_agent_id=sender_id,
                session_id=session_id
            )
    
    async def send_message(self, message: SIMFMessage) -> None:
        """
        Send SIMF message via appropriate protocol adapter.
        
        Routes message back through the same protocol it came from based on session tracking.
        """
        if not self.protocol_adapters:
            self.logger.warning("No protocol adapters available for message transmission")
            return
        
        # Determine the appropriate protocol adapter based on session tracking
        session_key = f"{message.session_id}:{message.target_agent_id}"
        target_protocol = self.session_protocol_map.get(session_key)
        
        if target_protocol and target_protocol in self.protocol_adapters:
            # Send via the specific protocol adapter
            try:
                adapter = self.protocol_adapters[target_protocol]
                await adapter.send_message(message)
                self.logger.debug(f"Message sent via {target_protocol} protocol (session-specific)")
            except Exception as e:
                self.logger.error(f"Failed to send message via {target_protocol}: {e}")
        else:
            # Fallback: broadcast to all adapters if no specific protocol is tracked
            self.logger.debug(f"No specific protocol found for session {session_key}, broadcasting to all adapters")
            for protocol_name, adapter in self.protocol_adapters.items():
                try:
                    await adapter.send_message(message)
                    self.logger.debug(f"Message sent via {protocol_name} protocol")
                except Exception as e:
                    self.logger.error(f"Failed to send message via {protocol_name}: {e}")
    
    async def register_protocol_adapter(self, protocol_name: str, adapter: "IProtocolAdapter") -> None:
        """
        Register a protocol adapter for communication.
        """
        self.protocol_adapters[protocol_name] = adapter
        self.logger.info(f"Registered protocol adapter: {protocol_name}")
    
    async def get_supported_protocols(self) -> List[str]:
        """
        Get list of supported communication protocols.
        """
        return list(self.protocol_adapters.keys())
    
    async def register_message_callback(self, callback) -> None:
        """
        Register message callback with all protocol adapters.
        
        This method registers the provided callback with all managed protocol
        adapters so that incoming messages are properly routed to the agent.
        
        Args:
            callback: Async callable that handles incoming SIMF messages
        """
        for protocol_name, adapter in self.protocol_adapters.items():
            try:
                # Create a wrapper callback that tracks the source protocol
                async def protocol_callback(message: SIMFMessage, protocol=protocol_name):
                    # Track which protocol this message came from
                    session_key = f"{message.session_id}:{message.source_agent_id}"
                    self.session_protocol_map[session_key] = protocol
                    await callback(message)
                
                await adapter.register_message_callback(protocol_callback)
                self.logger.debug(f"Registered message callback with {protocol_name} adapter")
            except Exception as e:
                self.logger.error(f"Failed to register callback with {protocol_name} adapter: {e}")
    
    def _extract_content(self, message: SIMFMessage) -> Any:
        """
        Extract content from SIMF message payload.
        
        Handles different payload types and extracts the relevant content
        for reasoning engine processing.
        """
        if hasattr(message.payload, 'content'):
            return message.payload.content
        elif hasattr(message.payload, 'text'):
            return message.payload.text
        elif hasattr(message.payload, 'message'):
            return message.payload.message
        else:
            # Return the payload itself if no standard content field
            return message.payload
