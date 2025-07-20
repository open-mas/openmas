# Internal Message Format Pydantic Models

This document provides the formal Pydantic model definitions for the Standard Internal Message Format (SIMF) used within OpenMAS. These models serve as the definitive type definitions for message handling within the Agent Framework.

## Core Models

```python
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class MessageFlowDirection(str, Enum):
    """Direction of message flow relative to the agent."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"

class MessageType(str, Enum):
    """Type of the message for routing and processing."""
    USER_QUERY = "USER_QUERY"
    AGENT_RESPONSE = "AGENT_RESPONSE"
    CAPABILITY_INVOCATION = "CAPABILITY_INVOCATION"
    CAPABILITY_RESULT = "CAPABILITY_RESULT"
    TOOL_INVOCATION = "TOOL_INVOCATION"
    TOOL_RESULT = "TOOL_RESULT"
    EVENT_NOTIFICATION = "EVENT_NOTIFICATION"
    SYSTEM_COMMAND = "SYSTEM_COMMAND"
    ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"
    ERROR_MESSAGE = "ERROR_MESSAGE"
    PLAIN_TEXT_MESSAGE = "PLAIN_TEXT_MESSAGE"
    MULTI_PART_MESSAGE = "MULTI_PART_MESSAGE"

    # Note: This enum is extensible. New message types can be added by extensions.

class PayloadType(str, Enum):
    """Discriminator for the payload structure."""
    TEXT_CONTENT = "text_content"
    STRUCTURED_DATA_CONTENT = "structured_data_content"
    ASSET_REFERENCE_CONTENT = "asset_reference_content"
    MULTI_PART_CONTENT = "multi_part_content"
    INVOCATION_CONTENT = "invocation_content"
    INVOCATION_RESULT_CONTENT = "invocation_result_content"
    STREAM_CONTEXT_CONTENT = "stream_context_content"
    KNOWLEDGE_REPRESENTATION_CONTENT = "knowledge_representation_content"
    EVENT_CONTENT = "event_content"

    # Note: This enum is extensible. New payload types can be added by extensions.

# Base Payload Model
class BasePayload(BaseModel):
    """Base class for all payload types."""
    payload_type: PayloadType = Field(..., description="Discriminator for the payload structure")

# Specific Payload Models
class TextContentPayload(BasePayload):
    """Payload for simple text messages."""
    payload_type: PayloadType = Field(PayloadType.TEXT_CONTENT, description="Text content payload type")
    text: str = Field(..., description="The actual text content")

class StructuredDataContentPayload(BasePayload):
    """Payload for structured data (JSON objects, etc.)."""
    payload_type: PayloadType = Field(PayloadType.STRUCTURED_DATA_CONTENT, description="Structured data content payload type")
    data: Dict[str, Any] = Field(..., description="Any structured data object")

class AssetReferenceContentPayload(BasePayload):
    """Payload for references to binary assets (images, files, etc.)."""
    payload_type: PayloadType = Field(PayloadType.ASSET_REFERENCE_CONTENT, description="Asset reference content payload type")
    asset_id: str = Field(..., description="Unique identifier for the asset")
    asset_type: str = Field(..., description="Type of the asset (e.g., 'image', 'audio', 'video', 'document')")
    mime_type: Optional[str] = Field(None, description="Optional MIME type of the asset")
    resource_metadata: Optional[Dict[str, Any]] = Field(None, description="Optional protocol-specific resource metadata")

class MultiPartContentPayload(BasePayload):
    """Payload for messages with multiple content parts (e.g., text + images)."""
    payload_type: PayloadType = Field(PayloadType.MULTI_PART_CONTENT, description="Multi-part content payload type")
    parts: List[BasePayload] = Field(..., description="Array of other payload objects (each with its own 'payload_type')")

class InvocationContentPayload(BasePayload):
    """Payload for capability or tool invocations."""
    payload_type: PayloadType = Field(PayloadType.INVOCATION_CONTENT, description="Invocation content payload type")
    invocation_name: str = Field(..., description="Name of the capability or tool being invoked")
    arguments: Dict[str, Any] = Field(..., description="Arguments for the invocation")

class InvocationResultContentPayload(BasePayload):
    """Payload for results of capability or tool invocations."""
    payload_type: PayloadType = Field(PayloadType.INVOCATION_RESULT_CONTENT, description="Invocation result content payload type")
    invocation_name: str = Field(..., description="Name of the capability or tool that was invoked")
    status: str = Field(..., description="Status of the invocation ('success', 'failure', or 'pending')")
    result: Optional[Any] = Field(None, description="Optional, result data for successful invocations")
    error: Optional[Dict[str, Any]] = Field(None, description="Optional, error information for failed invocations")

class StreamContextContentPayload(BasePayload):
    """Payload for messages that are part of a streaming sequence."""
    payload_type: PayloadType = Field(PayloadType.STREAM_CONTEXT_CONTENT, description="Stream context content payload type")
    stream_id: str = Field(..., description="Identifier for the stream this message belongs to")
    sequence_number: int = Field(..., description="Position in the stream sequence")
    stream_position: str = Field(..., description="Position in the stream ('start', 'middle', 'end', or 'complete')")
    is_heartbeat: bool = Field(False, description="Whether this is a keepalive message with no content")
    content: Optional[BasePayload] = Field(None, description="The actual content payload (can be any other payload type)")
    estimated_remaining: Optional[int] = Field(None, description="Optional, estimated number of remaining messages")

class KnowledgeRepresentationContentPayload(BasePayload):
    """Payload for formal knowledge structures used in symbolic reasoning or knowledge representation."""
    payload_type: PayloadType = Field(PayloadType.KNOWLEDGE_REPRESENTATION_CONTENT, description="Knowledge representation content payload type")
    formalism: str = Field(..., description="Knowledge representation formalism (e.g., 'predicate_logic', 'description_logic', 'rdf', 'owl', 'prolog')")
    representation: Any = Field(..., description="The actual knowledge content in the specified formalism")
    context_id: Optional[str] = Field(None, description="Optional, identifier for the knowledge context/KB")
    operation: Optional[str] = Field(None, description="Optional, 'assert', 'query', 'retract', 'update'")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional, additional information about the knowledge")

class EventContentPayload(BasePayload):
    """Payload for standardized event notifications."""
    payload_type: PayloadType = Field(PayloadType.EVENT_CONTENT, description="Event content payload type")
    event_type: str = Field(..., description="Type of event (domain-specific)")
    event_source: str = Field(..., description="Source of the event")
    timestamp: str = Field(..., description="When the event occurred (ISO 8601)")
    data: Dict[str, Any] = Field(..., description="Event data payload")
    severity: Optional[str] = Field(None, description="Optional, 'debug', 'info', 'warning', 'error', 'critical'")
    is_transient: bool = Field(True, description="Whether the event represents a point-in-time occurrence or a persistent state change")

# Union type for all possible payload types
PayloadUnion = Union[
    TextContentPayload,
    StructuredDataContentPayload,
    AssetReferenceContentPayload,
    MultiPartContentPayload,
    InvocationContentPayload,
    InvocationResultContentPayload,
    StreamContextContentPayload,
    KnowledgeRepresentationContentPayload,
    EventContentPayload
]

class InternalMessageFormat(BaseModel):
    """
    Standard Internal Message Format used within the OpenMAS Agent Framework.
    This format serves as the critical intermediary between protocol-specific messages
    and reasoning components.
    """
    message_id: str = Field(..., description="Unique identifier for this message, typically a UUID")
    session_id: Optional[str] = Field(None, description="Identifier for the conversation/session this message belongs to")
    timestamp: datetime = Field(..., description="Time when this message was created or processed")
    source_protocol_type: Optional[str] = Field(None, description="Protocol type that the message originated from (e.g., 'a2a-http', 'mcp-sse')")
    source_agent_id: Optional[str] = Field(None, description="Identifier of the agent that sent this message")
    target_agent_id: str = Field(..., description="Identifier of the agent that should receive this message")
    message_flow_direction: MessageFlowDirection = Field(..., description="Direction of message flow relative to the agent")
    message_type: MessageType = Field(..., description="Type of the message for routing and processing")
    payload: PayloadUnion = Field(..., description="Content of the message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional contextual information, flexible key-value data")

    class Config:
        """Configuration for the Pydantic model."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## Usage Examples

### Creating a Simple Text Message

```python
text_message = InternalMessageFormat(
    message_id="123e4567-e89b-12d3-a456-426614174000",
    session_id="session-001",
    timestamp=datetime.now(),
    target_agent_id="agent-001",
    message_flow_direction=MessageFlowDirection.INBOUND,
    message_type=MessageType.USER_QUERY,
    payload=TextContentPayload(
        text="Hello, how can I help you today?"
    )
)
```

### Creating a Capability Invocation Message

```python
invocation_message = InternalMessageFormat(
    message_id="123e4567-e89b-12d3-a456-426614174001",
    session_id="session-001",
    timestamp=datetime.now(),
    source_agent_id="user-001",
    target_agent_id="agent-001",
    message_flow_direction=MessageFlowDirection.INBOUND,
    message_type=MessageType.CAPABILITY_INVOCATION,
    payload=InvocationContentPayload(
        invocation_name="analyze_data",
        arguments={
            "dataset_url": "https://example.com/dataset.csv",
            "analysis_type": "sentiment"
        }
    ),
    metadata={
        "priority": "high",
        "source_location": "web-client"
    }
)
```

### Creating a Multi-Part Message

```python
multi_part_message = InternalMessageFormat(
    message_id="123e4567-e89b-12d3-a456-426614174002",
    session_id="session-001",
    timestamp=datetime.now(),
    source_agent_id="agent-001",
    target_agent_id="user-001",
    message_flow_direction=MessageFlowDirection.OUTBOUND,
    message_type=MessageType.MULTI_PART_MESSAGE,
    payload=MultiPartContentPayload(
        parts=[
            TextContentPayload(
                text="Here's the image analysis you requested:"
            ),
            AssetReferenceContentPayload(
                asset_id="image-001",
                asset_type="image",
                mime_type="image/png"
            ),
            StructuredDataContentPayload(
                data={
                    "analysis_results": {
                        "objects_detected": ["car", "person", "tree"],
                        "confidence_score": 0.92
                    }
                }
            )
        ]
    )
)
```

## Relationship to the Standard Internal Message Format

This Pydantic model implementation directly corresponds to the Standard Internal Message Format (SIMF) defined in [internal_message_format_standard.md](../internal_message_format_standard.md). The model provides a programmatic representation with type validation for the SIMF.
