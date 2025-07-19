# IProtocolAdapter Interface

## Overview

The `IProtocolAdapter` interface defines the standard contract for all protocol implementations in OpenMAS. It serves as the foundation for OpenMAS's multi-protocol architecture, enabling agents to communicate across different protocols while maintaining reasoning agnosticism through the Standard Internal Message Format (SIMF).

This interface enables OpenMAS to:

1. Support multiple communication protocols (A2A, MCP, HTTP, MQTT, gRPC) with a consistent interface
2. Translate between protocol-specific messages and the Standard Internal Message Format
3. Manage protocol connections and lifecycle operations
4. Provide protocol-specific configuration and status information
5. Maintain protocol independence in the agent framework

## Interface Definition

```python
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from openmas.agent.models.internal_message_format import InternalMessageFormat


class ConnectionStatus(str, Enum):
    """Current status of a protocol connection."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


class ProtocolError(Exception):
    """Base exception for protocol-related errors."""
    pass


class ConnectionError(ProtocolError):
    """Exception raised for connection-related errors."""
    pass


class MessageTranslationError(ProtocolError):
    """Exception raised for message translation errors."""
    pass


class UnsupportedMessageTypeError(ProtocolError):
    """Exception raised when a message type is not supported by the protocol."""
    pass


class SecurityConfig(BaseModel):
    """Security configuration for protocol connections."""
    enabled: bool = Field(default=True, description="Whether security is enabled")
    auth_type: Optional[str] = Field(default=None, description="Authentication type")
    credentials: Dict[str, Any] = Field(default_factory=dict, description="Authentication credentials")
    encryption: bool = Field(default=True, description="Whether to use encryption")
    verify_certificates: bool = Field(default=True, description="Whether to verify SSL certificates")


class RetryPolicy(BaseModel):
    """Retry policy configuration for protocol operations."""
    enabled: bool = Field(default=True, description="Whether retry is enabled")
    max_attempts: int = Field(default=3, description="Maximum number of retry attempts")
    initial_delay: float = Field(default=1.0, description="Initial delay between retries in seconds")
    backoff_factor: float = Field(default=2.0, description="Backoff multiplier for successive retries")
    max_delay: float = Field(default=60.0, description="Maximum delay between retries in seconds")


class ProtocolConfig(BaseModel):
    """Base configuration for protocol adapters."""
    protocol_type: str = Field(..., description="Protocol type identifier (e.g., 'mcp-sse', 'a2a-http')")
    enabled: bool = Field(default=True, description="Whether this protocol is enabled")
    options: Dict[str, Any] = Field(default_factory=dict, description="Protocol-specific configuration options")
    security: Optional[SecurityConfig] = Field(default=None, description="Security configuration")
    retry_policy: Optional[RetryPolicy] = Field(default=None, description="Retry configuration")
    timeout_seconds: float = Field(default=30.0, description="Default timeout for operations in seconds")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow protocol-specific additional fields


class ProtocolStatus(BaseModel):
    """Current status of a protocol adapter."""
    status: ConnectionStatus = Field(..., description="Current connection state")
    connected_at: Optional[datetime] = Field(default=None, description="When connection was established")
    last_activity: Optional[datetime] = Field(default=None, description="Last message activity timestamp")
    last_error: Optional[str] = Field(default=None, description="Last error message if any")
    error_count: int = Field(default=0, description="Number of errors since last successful operation")
    message_count: int = Field(default=0, description="Total number of messages processed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Protocol-specific status information")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProtocolCapabilities(BaseModel):
    """Capabilities supported by a protocol adapter."""
    supports_streaming: bool = Field(default=False, description="Whether protocol supports streaming messages")
    supports_binary: bool = Field(default=False, description="Whether protocol supports binary data")
    supports_multipart: bool = Field(default=False, description="Whether protocol supports multi-part messages")
    supports_authentication: bool = Field(default=True, description="Whether protocol supports authentication")
    supports_encryption: bool = Field(default=True, description="Whether protocol supports encryption")
    supported_payload_types: List[str] = Field(default_factory=list, description="Supported SIMF payload types")
    max_message_size: Optional[int] = Field(default=None, description="Maximum message size in bytes")


class IProtocolAdapter(ABC):
    """
    Interface for protocol-specific adapters in OpenMAS.
    
    The IProtocolAdapter serves as the bridge between protocol-specific
    communication mechanisms and the OpenMAS Standard Internal Message Format (SIMF).
    It provides a consistent interface for connecting, sending, receiving, and
    translating messages across different protocols.
    
    All protocol adapters must implement this interface to ensure consistent
    behavior and enable OpenMAS's multi-protocol capabilities.
    """
    
    @abstractmethod
    async def connect(self, config: ProtocolConfig) -> None:
        """
        Initialize and establish the protocol connection.
        
        This method performs all necessary setup to enable communication through
        the protocol, including authentication, connection establishment, and
        any protocol-specific initialization.
        
        Args:
            config: Protocol-specific configuration including connection details,
                security settings, and protocol options
                
        Raises:
            ConnectionError: If the connection cannot be established
            ValueError: If the configuration is invalid
            ProtocolError: For other protocol-specific errors
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close the protocol connection and clean up resources.
        
        This method performs graceful shutdown of the protocol connection,
        ensuring all pending operations are completed and resources are
        properly released.
        
        Raises:
            ProtocolError: If the disconnection fails
        """
        pass
    
    @abstractmethod
    async def send_message(self, internal_message: InternalMessageFormat) -> None:
        """
        Send a message using the protocol.
        
        This method converts the internal message format to the protocol-specific
        format and transmits it. The conversion preserves all semantic information
        while adapting to protocol-specific constraints.
        
        Args:
            internal_message: Message in the Standard Internal Message Format
                
        Raises:
            MessageTranslationError: If the message cannot be converted to protocol format
            UnsupportedMessageTypeError: If the message type is not supported
            ConnectionError: If the connection is not available
            ProtocolError: For other protocol-specific errors
        """
        pass
    
    @abstractmethod
    async def register_message_callback(
        self, 
        callback: Callable[[InternalMessageFormat], Awaitable[None]]
    ) -> None:
        """
        Register a callback function for incoming messages.
        
        This method sets up the callback that will be invoked when messages
        are received through the protocol. The callback receives messages
        that have been converted to the Standard Internal Message Format.
        
        Args:
            callback: Async function to call when messages are received.
                Must accept a single InternalMessageFormat parameter.
                
        Raises:
            ValueError: If the callback is invalid
            ProtocolError: If callback registration fails
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> ProtocolStatus:
        """
        Get the current status of the protocol adapter.
        
        Returns:
            ProtocolStatus: Current connection status, activity information,
                and protocol-specific metadata
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> ProtocolCapabilities:
        """
        Get the capabilities supported by this protocol adapter.
        
        Returns:
            ProtocolCapabilities: Information about what features and
                message types this protocol supports
        """
        pass
    
    @abstractmethod
    def to_internal_format(self, protocol_message: Any) -> InternalMessageFormat:
        """
        Convert a protocol-specific message to Standard Internal Message Format.
        
        This method performs the critical translation from the protocol's
        native message format to OpenMAS's standard internal representation.
        All semantic information must be preserved during this conversion.
        
        Args:
            protocol_message: Message in the protocol's native format
            
        Returns:
            InternalMessageFormat: Message converted to SIMF
            
        Raises:
            MessageTranslationError: If the message cannot be converted
            ValueError: If the protocol message is invalid
        """
        pass
    
    @abstractmethod
    def from_internal_format(self, internal_message: InternalMessageFormat) -> Any:
        """
        Convert a Standard Internal Message Format message to protocol-specific format.
        
        This method performs the critical translation from OpenMAS's standard
        internal representation to the protocol's native message format.
        Protocol-specific constraints and requirements must be respected.
        
        Args:
            internal_message: Message in Standard Internal Message Format
            
        Returns:
            Any: Message converted to protocol-specific format
            
        Raises:
            MessageTranslationError: If the message cannot be converted
            UnsupportedMessageTypeError: If the message type is not supported
            ValueError: If the internal message is invalid
        """
        pass
    
    @abstractmethod
    def validate_message(self, internal_message: InternalMessageFormat) -> bool:
        """
        Validate whether a message can be handled by this protocol.
        
        This method checks if the given internal message can be successfully
        converted to the protocol's format and transmitted. It should return
        False for unsupported message types or constraints.
        
        Args:
            internal_message: Message to validate
            
        Returns:
            bool: True if the message can be handled, False otherwise
        """
        pass
    
    # Optional lifecycle methods that adapters can implement
    
    async def health_check(self) -> bool:
        """
        Perform a health check on the protocol connection.
        
        Returns:
            bool: True if the connection is healthy, False otherwise
        """
        try:
            status = await self.get_status()
            return status.status == ConnectionStatus.CONNECTED
        except Exception:
            return False
    
    async def reconnect(self) -> None:
        """
        Attempt to reconnect the protocol.
        
        Default implementation disconnects and reconnects using stored config.
        Adapters can override for protocol-specific reconnection logic.
        
        Raises:
            ConnectionError: If reconnection fails
            ProtocolError: For protocol-specific errors
        """
        await self.disconnect()
        # Note: Subclasses should override to reconnect with stored config
        raise NotImplementedError("Subclasses must implement reconnection logic")
```

## SIMF Integration Requirements

### Message Translation Guidelines

Protocol adapters must preserve semantic information when translating between protocol-specific formats and SIMF:

#### 1. Payload Type Mapping

Each protocol should map its message types to appropriate SIMF payload types:

| SIMF Payload Type | MCP Usage | A2A Usage | HTTP Usage | MQTT Usage | gRPC Usage |
|------------------|-----------|-----------|------------|------------|------------|
| `text_content` | Simple text responses | Text message parts | Plain text responses | Text messages | String responses |
| `structured_data_content` | JSON tool results | Data message parts | JSON responses | JSON messages | Struct messages |
| `asset_reference_content` | Resource references | File message parts | File responses | Binary messages | Binary data |
| `multi_part_content` | Combined responses | Multi-part messages | Multipart HTTP | Message sequences | Stream messages |
| `invocation_content` | Tool calls | Capability invocations | API calls | Command messages | Method calls |
| `invocation_result_content` | Tool results | Task results | API responses | Response messages | Method responses |
| `stream_context_content` | Streaming responses | Streaming data | SSE streams | MQTT streams | gRPC streams |
| `event_content` | Notifications | Event messages | Webhook events | Event messages | Event notifications |

#### 2. Metadata Preservation

Protocol adapters must preserve metadata across translations:

- **Protocol identification**: Set `source_protocol_type` when converting to SIMF
- **Agent identification**: Map protocol-specific sender/receiver to SIMF agent IDs
- **Session context**: Preserve conversation/session identifiers
- **Protocol-specific metadata**: Include in SIMF `metadata` field

#### 3. Error Handling

Protocol adapters must handle translation errors gracefully:

- **Unsupported payload types**: Raise `UnsupportedMessageTypeError`
- **Invalid message format**: Raise `MessageTranslationError`
- **Missing required fields**: Raise `ValueError` with descriptive message

## Protocol-Specific Implementation Examples

### MCP Protocol Adapter Example

```python
class MCPProtocolAdapter(IProtocolAdapter):
    """Example MCP protocol adapter implementation."""
    
    def to_internal_format(self, protocol_message: Dict[str, Any]) -> InternalMessageFormat:
        """Convert MCP message to SIMF."""
        message_id = protocol_message.get("id", str(uuid.uuid4()))
        
        # Determine message type based on MCP message structure
        if "method" in protocol_message:
            if protocol_message["method"] == "tools/call":
                message_type = MessageType.TOOL_INVOCATION
                payload = InvocationContentPayload(
                    payload_type=PayloadType.INVOCATION_CONTENT,
                    invocation_name=protocol_message["params"]["name"],
                    arguments=protocol_message["params"]["arguments"]
                )
            else:
                message_type = MessageType.SYSTEM_COMMAND
                payload = StructuredDataContentPayload(
                    payload_type=PayloadType.STRUCTURED_DATA_CONTENT,
                    data=protocol_message["params"]
                )
        elif "result" in protocol_message:
            message_type = MessageType.TOOL_RESULT
            payload = InvocationResultContentPayload(
                payload_type=PayloadType.INVOCATION_RESULT_CONTENT,
                invocation_name="unknown",  # Would need context to determine
                status="success",
                result=protocol_message["result"]
            )
        else:
            # Handle other MCP message types
            message_type = MessageType.PLAIN_TEXT_MESSAGE
            payload = TextContentPayload(
                payload_type=PayloadType.TEXT_CONTENT,
                text=str(protocol_message)
            )
        
        return InternalMessageFormat(
            message_id=message_id,
            timestamp=datetime.utcnow(),
            source_protocol_type="mcp-sse",
            target_agent_id="local",
            message_flow_direction=MessageFlowDirection.INBOUND,
            message_type=message_type,
            payload=payload,
            metadata={"mcp_method": protocol_message.get("method")}
        )
    
    def from_internal_format(self, internal_message: InternalMessageFormat) -> Dict[str, Any]:
        """Convert SIMF to MCP message."""
        if internal_message.payload.payload_type == PayloadType.INVOCATION_CONTENT:
            return {
                "jsonrpc": "2.0",
                "id": internal_message.message_id,
                "method": "tools/call",
                "params": {
                    "name": internal_message.payload.invocation_name,
                    "arguments": internal_message.payload.arguments
                }
            }
        elif internal_message.payload.payload_type == PayloadType.TEXT_CONTENT:
            return {
                "jsonrpc": "2.0",
                "id": internal_message.message_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": internal_message.payload.text
                        }
                    ]
                }
            }
        else:
            raise UnsupportedMessageTypeError(
                f"Payload type {internal_message.payload.payload_type} not supported by MCP"
            )
```

### A2A Protocol Adapter Example

```python
class A2AProtocolAdapter(IProtocolAdapter):
    """Example A2A protocol adapter implementation."""
    
    def to_internal_format(self, protocol_message: Dict[str, Any]) -> InternalMessageFormat:
        """Convert A2A message to SIMF."""
        # A2A messages can have multiple parts
        parts = protocol_message.get("parts", [])
        
        if len(parts) == 1:
            # Single part - direct mapping
            part = parts[0]
            if part.get("type") == "text":
                payload = TextContentPayload(
                    payload_type=PayloadType.TEXT_CONTENT,
                    text=part["text"]
                )
                message_type = MessageType.PLAIN_TEXT_MESSAGE
            elif part.get("type") == "data":
                payload = StructuredDataContentPayload(
                    payload_type=PayloadType.STRUCTURED_DATA_CONTENT,
                    data=part["data"]
                )
                message_type = MessageType.AGENT_RESPONSE
            else:
                # Handle file parts as asset references
                payload = AssetReferenceContentPayload(
                    payload_type=PayloadType.ASSET_REFERENCE_CONTENT,
                    asset_id=part.get("file_id", "unknown"),
                    asset_type="file",
                    mime_type=part.get("mime_type")
                )
                message_type = MessageType.PLAIN_TEXT_MESSAGE
        else:
            # Multiple parts - create multi-part payload
            part_payloads = []
            for part in parts:
                if part.get("type") == "text":
                    part_payloads.append(TextContentPayload(
                        payload_type=PayloadType.TEXT_CONTENT,
                        text=part["text"]
                    ))
                elif part.get("type") == "data":
                    part_payloads.append(StructuredDataContentPayload(
                        payload_type=PayloadType.STRUCTURED_DATA_CONTENT,
                        data=part["data"]
                    ))
                # Add other part types...
            
            payload = MultiPartContentPayload(
                payload_type=PayloadType.MULTI_PART_CONTENT,
                parts=part_payloads
            )
            message_type = MessageType.MULTI_PART_MESSAGE
        
        return InternalMessageFormat(
            message_id=protocol_message.get("id", str(uuid.uuid4())),
            timestamp=datetime.utcnow(),
            source_protocol_type="a2a-http",
            source_agent_id=protocol_message.get("sender"),
            target_agent_id=protocol_message.get("recipient", "local"),
            message_flow_direction=MessageFlowDirection.INBOUND,
            message_type=message_type,
            payload=payload,
            metadata={
                "a2a_task_id": protocol_message.get("task_id"),
                "a2a_conversation_id": protocol_message.get("conversation_id")
            }
        )
    
    def get_capabilities(self) -> ProtocolCapabilities:
        """Get A2A protocol capabilities."""
        return ProtocolCapabilities(
            supports_streaming=False,
            supports_binary=True,
            supports_multipart=True,
            supports_authentication=True,
            supports_encryption=True,
            supported_payload_types=[
                PayloadType.TEXT_CONTENT,
                PayloadType.STRUCTURED_DATA_CONTENT,
                PayloadType.ASSET_REFERENCE_CONTENT,
                PayloadType.MULTI_PART_CONTENT,
                PayloadType.INVOCATION_CONTENT,
                PayloadType.INVOCATION_RESULT_CONTENT
            ],
            max_message_size=10 * 1024 * 1024  # 10MB
        )
```

## Configuration Integration

Protocol adapters integrate with the unified configuration schema through the `ProtocolConfig` model:

```yaml
# Example agent configuration
agents:
  example_agent:
    protocols:
      - type: "mcp-sse"
        enabled: true
        options:
          server_mode: true
          http_port: 8000
          server_name: "example_agent"
        security:
          enabled: true
          auth_type: "bearer"
          credentials:
            api_key: "${MCP_API_KEY}"
        retry_policy:
          enabled: true
          max_attempts: 3
          initial_delay: 1.0
        timeout_seconds: 30.0
```

## Error Handling and Edge Cases

### Connection Management

- **Connection failures**: Retry according to configured retry policy
- **Network timeouts**: Respect configured timeout values
- **Reconnection**: Implement automatic reconnection with exponential backoff

### Message Translation

- **Large messages**: Handle messages approaching protocol limits
- **Invalid formats**: Provide clear error messages for debugging
- **Missing fields**: Use sensible defaults where possible

### Resource Management

- **Connection pooling**: Reuse connections where appropriate
- **Memory management**: Clean up resources properly
- **Thread safety**: Ensure thread-safe operation for concurrent access

## Testing Guidelines

Protocol adapters should include comprehensive tests:

```python
class TestProtocolAdapter:
    """Example test structure for protocol adapters."""
    
    async def test_connect_success(self):
        """Test successful connection."""
        pass
    
    async def test_connect_failure(self):
        """Test connection failure scenarios."""
        pass
    
    async def test_message_translation_to_simf(self):
        """Test protocol message to SIMF conversion."""
        pass
    
    async def test_message_translation_from_simf(self):
        """Test SIMF to protocol message conversion."""
        pass
    
    async def test_unsupported_message_types(self):
        """Test handling of unsupported message types."""
        pass
    
    async def test_error_conditions(self):
        """Test various error conditions."""
        pass
```

## Related Documentation

- [Standard Internal Message Format](../01_architecture/internal_message_format_standard.md)
- [Multi-Protocol Design](../01_architecture/multi_protocol_design.md)
- [Protocol Configuration Schema](../03_configuration/schema/protocols.md)
- [Message Handler Interface](../04_agents/interfaces/message_handler_interface.md) 