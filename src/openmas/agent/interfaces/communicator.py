"""
ICommunicator Interface for OpenMAS Agent Body-Brain Separation

This module defines the ICommunicator interface that represents the "body" of an agent,
handling all external communication while remaining agnostic to reasoning logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, TYPE_CHECKING
from openmas.core.simf import SIMFMessage

if TYPE_CHECKING:
    from openmas.protocols.interfaces import IProtocolAdapter


class ICommunicator(ABC):
    """
    Interface for agent communication infrastructure (body).
    
    The communicator handles all external communication protocols and message
    formatting while remaining completely agnostic to reasoning logic. This
    enables protocol independence and clean separation of concerns.
    """
    
    @abstractmethod
    async def parse_message(self, message: SIMFMessage) -> Dict[str, Any]:
        """
        Parse incoming message into context for reasoning engine.
        
        Converts protocol-specific message format into a standardized context
        dictionary that reasoning engines can process without protocol awareness.
        
        Args:
            message: SIMF message from protocol adapter
            
        Returns:
            Context dictionary with standardized keys:
            - message_type: str
            - content: Any
            - sender: str
            - session: str
            - metadata: Dict[str, Any]
        """
        pass
    
    @abstractmethod
    async def format_response(self, action: Dict[str, Any]) -> SIMFMessage:
        """
        Format reasoning engine action into SIMF message.
        
        Converts reasoning engine decision into proper SIMF message format
        for protocol adapter transmission.
        
        Args:
            action: Action dictionary from reasoning engine with keys:
            - type: str (e.g., "text", "invocation", "error")
            - content: Any
            - sender: str
            - session: str
            
        Returns:
            SIMF message ready for protocol adapter
        """
        pass
    
    @abstractmethod
    async def send_message(self, message: SIMFMessage) -> None:
        """
        Send SIMF message via appropriate protocol adapter.
        
        Args:
            message: SIMF message to send
        """
        pass
    
    @abstractmethod
    async def register_protocol_adapter(self, protocol_name: str, adapter: "IProtocolAdapter") -> None:
        """
        Register a protocol adapter for communication.
        
        Args:
            protocol_name: Name of the protocol (e.g., "mcp", "http")
            adapter: Protocol adapter instance
        """
        pass
    
    @abstractmethod
    async def get_supported_protocols(self) -> List[str]:
        """
        Get list of supported communication protocols.
        
        Returns:
            List of protocol names
        """
        pass
    
    @abstractmethod
    async def register_message_callback(self, callback) -> None:
        """
        Register message callback with all protocol adapters.
        
        This method registers the provided callback with all managed protocol
        adapters so that incoming messages are properly routed to the agent.
        
        Args:
            callback: Async callable that handles incoming SIMF messages
        """
        pass
