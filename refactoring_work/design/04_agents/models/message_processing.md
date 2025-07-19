# Message Processing Models

This document defines the supporting data structures and models used in conjunction with the [`IMessageHandler`](../interfaces/message_handler_interface.md) interface for protocol-agnostic message handling within the OpenMAS Agent Framework.

## MessageProcessingStatus

The `MessageProcessingStatus` enum defines the possible states during message processing:

```python
from enum import Enum

class MessageProcessingStatus(str, Enum):
    """
    Status of message processing within the Agent Framework.
    
    This enum represents the different states a message can be in
    during its processing lifecycle, from initial receipt through
    routing, processing, and completion.
    """
    RECEIVED = "received"
    """Message was received by the handler but not yet parsed"""
    
    PARSED = "parsed"
    """Message was successfully parsed into internal format"""
    
    ROUTING = "routing"
    """Message is being routed to an appropriate handler"""
    
    PROCESSING = "processing"
    """Message is being processed by a handler (e.g., reasoning engine, capability)"""
    
    COMPLETED = "completed"
    """Message was successfully processed (no response needed)"""
    
    RESPONSE_READY = "response_ready"
    """A response to the message is ready to be sent"""
    
    FAILED = "failed"
    """Message processing failed due to an error"""
    
    REJECTED = "rejected"
    """Message was rejected (e.g., invalid format, unauthorized)"""
    
    DEFERRED = "deferred"
    """Message processing was deferred (e.g., for asynchronous handling)"""
```

## MessageProcessingResult

The `MessageProcessingResult` class encapsulates the outcome of message processing operations:

```python
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from openmas.agents.models.internal_message_format import InternalMessageFormat

class MessageProcessingResult(BaseModel):
    """
    Result of message processing within the Agent Framework.
    
    This model captures the outcome of processing a message through
    the IMessageHandler interface, including status, any generated
    responses, and error information if applicable.
    """
    status: MessageProcessingStatus = Field(
        ..., 
        description="Status of the message processing"
    )
    
    internal_message: Optional[InternalMessageFormat] = Field(
        None, 
        description="The processed internal message if available"
    )
    
    response_message: Optional[InternalMessageFormat] = Field(
        None, 
        description="Response message if one was generated during processing"
    )
    
    error_message: Optional[str] = Field(
        None, 
        description="Human-readable error message if processing failed"
    )
    
    error_details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Detailed error information if processing failed"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional metadata about the processing operation"
    )
    
    def is_successful(self) -> bool:
        """
        Check if the message processing was successful.
        
        Returns:
            bool: True if the processing completed successfully or a response is ready,
                  False otherwise
        """
        return self.status in [
            MessageProcessingStatus.COMPLETED,
            MessageProcessingStatus.RESPONSE_READY
        ]
    
    def has_response(self) -> bool:
        """
        Check if a response message is available.
        
        Returns:
            bool: True if a response message is available, False otherwise
        """
        return (
            self.status == MessageProcessingStatus.RESPONSE_READY and 
            self.response_message is not None
        )
    
    def has_error(self) -> bool:
        """
        Check if an error occurred during processing.
        
        Returns:
            bool: True if an error occurred, False otherwise
        """
        return self.status in [
            MessageProcessingStatus.FAILED,
            MessageProcessingStatus.REJECTED
        ]
```

## MessageProcessingError

The `MessageProcessingError` class and its subclasses define standard error types for message processing:

```python
class MessageProcessingError(Exception):
    """
    Base exception class for errors during message processing.
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize a new MessageProcessingError.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class MessageFormatError(MessageProcessingError):
    """
    Error raised when a message cannot be parsed into or from the internal format.
    """
    pass


class InvalidMessageError(MessageProcessingError):
    """
    Error raised when a message is well-formed but semantically invalid for processing.
    """
    pass


class MessageRoutingError(MessageProcessingError):
    """
    Error raised when a message cannot be routed to an appropriate handler.
    """
    pass


class CapabilityNotFoundError(MessageProcessingError):
    """
    Error raised when a message targets a capability that doesn't exist.
    """
    pass


class UnsupportedMessageTypeError(MessageProcessingError):
    """
    Error raised when a message type is not supported by a protocol.
    """
    pass


class InvalidPayloadError(MessageProcessingError):
    """
    Error raised when a payload doesn't match a valid payload type.
    """
    pass


class InvalidMessageTypeError(MessageProcessingError):
    """
    Error raised when a message type is not recognized.
    """
    pass
```

## Protocol Adapter Message Conversion

The following illustrates how protocol-specific messages are converted to the internal format and back:

```python
from typing import Any, Dict, Optional, Type
from abc import ABC, abstractmethod

from openmas.agents.models.internal_message_format import InternalMessageFormat

class IMessageConverter(ABC):
    """
    Interface for converting between protocol-specific message formats and
    the standard internal message format.
    
    This interface is typically implemented by protocol adapters to provide
    bi-directional conversion between their native format and the OpenMAS
    internal message format.
    """
    
    @abstractmethod
    def to_internal_format(self, protocol_message: Any) -> InternalMessageFormat:
        """
        Convert a protocol-specific message to the standard internal format.
        
        Args:
            protocol_message: The protocol-specific message
            
        Returns:
            InternalMessageFormat: The message converted to internal format
            
        Raises:
            MessageFormatError: If the message cannot be converted
        """
        pass
    
    @abstractmethod
    def from_internal_format(
        self, 
        internal_message: InternalMessageFormat,
        protocol_specific_options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Convert a message from the standard internal format to protocol-specific format.
        
        Args:
            internal_message: The message in internal format
            protocol_specific_options: Optional protocol-specific configuration
            
        Returns:
            Any: The message converted to the protocol-specific format
            
        Raises:
            MessageFormatError: If the message cannot be converted
            UnsupportedMessageTypeError: If the message type is not supported
        """
        pass
```

## Usage Examples

### Creating and Using a MessageProcessingResult

```python
from datetime import datetime
import uuid

from openmas.agents.models.internal_message_format import (
    InternalMessageFormat, 
    MessageType, 
    MessageFlowDirection,
    TextContentPayload
)
from openmas.agents.models.message_processing import (
    MessageProcessingStatus,
    MessageProcessingResult
)

# Create a successful result with a response
def process_greeting(message):
    # Process the message...
    
    # Create a response message
    response = InternalMessageFormat(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        source_agent_id="agent-001",
        target_agent_id=message.source_agent_id,
        message_flow_direction=MessageFlowDirection.OUTBOUND,
        message_type=MessageType.AGENT_RESPONSE,
        payload=TextContentPayload(text="Hello! How can I assist you today?")
    )
    
    # Return a result with the response
    return MessageProcessingResult(
        status=MessageProcessingStatus.RESPONSE_READY,
        internal_message=message,
        response_message=response
    )

# Create an error result
def handle_invalid_message(error_message, details=None):
    return MessageProcessingResult(
        status=MessageProcessingStatus.FAILED,
        error_message=error_message,
        error_details=details
    )

# Using the result
processing_result = process_greeting(some_message)

if processing_result.has_response():
    # Send the response
    response = processing_result.response_message
    send_response(response)
elif processing_result.has_error():
    # Handle the error
    log_error(processing_result.error_message, processing_result.error_details)
```

### Protocol Adapter Conversion Example

```python
class MCPMessageConverter(IMessageConverter):
    """Example converter for Model Context Protocol messages."""
    
    def to_internal_format(self, mcp_message: Dict[str, Any]) -> InternalMessageFormat:
        """Convert MCP message to internal format."""
        try:
            # Extract core message attributes
            message_id = mcp_message.get("id", str(uuid.uuid4()))
            
            # Map MCP-specific fields to internal format
            internal_message = InternalMessageFormat(
                message_id=message_id,
                session_id=mcp_message.get("conversation_id"),
                timestamp=datetime.now(),
                source_protocol_type="mcp",
                source_agent_id="user",  # Typically from user in MCP
                target_agent_id="agent",  # Target is the agent itself
                message_flow_direction=MessageFlowDirection.INBOUND,
                message_type=self._determine_message_type(mcp_message),
                payload=self._create_payload_from_mcp(mcp_message),
                metadata={}
            )
            
            return internal_message
            
        except Exception as e:
            raise MessageFormatError(f"Failed to convert MCP message: {str(e)}")
    
    def from_internal_format(
        self, 
        internal_message: InternalMessageFormat,
        protocol_specific_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert internal format to MCP message."""
        try:
            # Create MCP message structure
            mcp_message = {
                "id": internal_message.message_id,
                "conversation_id": internal_message.session_id,
                # Map other fields based on payload type
            }
            
            # Handle different payload types
            if internal_message.payload.payload_type == "text_content":
                mcp_message["content"] = internal_message.payload.text
            # Handle other payload types...
            
            return mcp_message
            
        except Exception as e:
            raise MessageFormatError(f"Failed to convert to MCP format: {str(e)}")
    
    # Helper methods
    def _determine_message_type(self, mcp_message: Dict[str, Any]) -> MessageType:
        """Determine the internal message type from an MCP message."""
        if "tool_calls" in mcp_message:
            return MessageType.TOOL_INVOCATION
        else:
            return MessageType.USER_QUERY
    
    def _create_payload_from_mcp(self, mcp_message: Dict[str, Any]) -> Any:
        """Create an appropriate payload object from an MCP message."""
        # Implementation depends on MCP message structure
        pass
```

## Relationship to Other Components

These message processing models work in conjunction with the following components:

- [IMessageHandler Interface](../interfaces/message_handler_interface.md) - The primary interface that uses these models
- [Internal Message Format](../../01_architecture/models/internal_message_format.md) - The standard message format used throughout OpenMAS
- [IProtocolAdapter Interface](../../02_protocols/iprotocol_adapter_interface.md) - Protocol adapters that implement message conversion
