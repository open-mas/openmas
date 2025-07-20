"""
Standard Internal Message Format (SIMF) Pydantic Models

This module provides concrete Pydantic models for the OpenMAS Standard Internal
Message Format, implementing all payload types, validation rules, and factory
functions for creating SIMF-compliant messages.

Based on the SIMF specification in:
refactoring_work/design/01_architecture/internal_message_format_standard.md
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

# ============================================================================
# Enums
# ============================================================================


class MessageType(str, Enum):
    """Message types supported by SIMF."""

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


class PayloadType(str, Enum):
    """Payload types supported by SIMF."""

    TEXT_CONTENT = "text_content"
    STRUCTURED_DATA_CONTENT = "structured_data_content"
    ASSET_REFERENCE_CONTENT = "asset_reference_content"
    MULTI_PART_CONTENT = "multi_part_content"
    INVOCATION_CONTENT = "invocation_content"
    INVOCATION_RESULT_CONTENT = "invocation_result_content"
    STREAM_CONTEXT_CONTENT = "stream_context_content"
    KNOWLEDGE_REPRESENTATION_CONTENT = "knowledge_representation_content"
    EVENT_CONTENT = "event_content"


class MessageFlowDirection(str, Enum):
    """Message flow direction relative to the agent."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"


class AssetType(str, Enum):
    """Asset types supported in asset reference content."""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    DATA = "data"
    MODEL = "model"
    EMBEDDING = "embedding"
    PROMPT_TEMPLATE = "prompt_template"
    BINARY = "binary"


class InvocationStatus(str, Enum):
    """Status values for invocation results."""

    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"


class StreamPosition(str, Enum):
    """Position in a stream sequence."""

    START = "start"
    MIDDLE = "middle"
    END = "end"
    COMPLETE = "complete"  # Single message stream


class KnowledgeFormalism(str, Enum):
    """Knowledge representation formalisms."""

    PREDICATE_LOGIC = "predicate_logic"
    DESCRIPTION_LOGIC = "description_logic"
    RDF = "rdf"
    OWL = "owl"
    PROLOG = "prolog"
    JSON_LD = "json_ld"


class KnowledgeOperation(str, Enum):
    """Knowledge operations."""

    ASSERT = "assert"
    QUERY = "query"
    RETRACT = "retract"
    UPDATE = "update"


class EventSeverity(str, Enum):
    """Event severity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ============================================================================
# Payload Models
# ============================================================================


class BasePayload(BaseModel):
    """Base class for all payload types."""

    payload_type: PayloadType

    class Config:
        extra = "forbid"
        use_enum_values = True


class TextContentPayload(BasePayload):
    """Payload for simple text messages."""

    payload_type: Literal[PayloadType.TEXT_CONTENT] = PayloadType.TEXT_CONTENT
    text: str = Field(..., description="The actual text content")


class StructuredDataContentPayload(BasePayload):
    """Payload for structured data (JSON objects, etc.)."""

    payload_type: Literal[PayloadType.STRUCTURED_DATA_CONTENT] = (
        PayloadType.STRUCTURED_DATA_CONTENT
    )
    data: Dict[str, Any] = Field(..., description="Structured data object")


class AssetReferenceContentPayload(BasePayload):
    """Payload for references to binary assets (images, files, etc.)."""

    payload_type: Literal[PayloadType.ASSET_REFERENCE_CONTENT] = (
        PayloadType.ASSET_REFERENCE_CONTENT
    )
    asset_id: str = Field(..., description="Unique identifier for the asset")
    asset_type: AssetType = Field(..., description="Type of the asset")
    mime_type: Optional[str] = Field(None, description="MIME type of the asset")

    # Protocol-specific resource metadata
    resource_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Protocol-specific resource metadata"
    )


class MultiPartContentPayload(BasePayload):
    """Payload for messages with multiple content parts."""

    payload_type: Literal[PayloadType.MULTI_PART_CONTENT] = (
        PayloadType.MULTI_PART_CONTENT
    )
    parts: List[
        Union[
            TextContentPayload,
            StructuredDataContentPayload,
            AssetReferenceContentPayload,
            # Note: Recursive multi-part is allowed
            "MultiPartContentPayload",
        ]
    ] = Field(..., description="Array of payload objects")


class InvocationContentPayload(BasePayload):
    """Payload for capability or tool invocations."""

    payload_type: Literal[PayloadType.INVOCATION_CONTENT] = (
        PayloadType.INVOCATION_CONTENT
    )
    invocation_name: str = Field(
        ..., description="Name of the capability or tool being invoked"
    )
    arguments: Dict[str, Any] = Field(
        default_factory=dict, description="Arguments for the invocation"
    )


class ErrorInfo(BaseModel):
    """Error information structure."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )


class InvocationResultContentPayload(BasePayload):
    """Payload for results of capability or tool invocations."""

    payload_type: Literal[PayloadType.INVOCATION_RESULT_CONTENT] = (
        PayloadType.INVOCATION_RESULT_CONTENT
    )
    invocation_name: str = Field(
        ..., description="Name of the capability or tool that was invoked"
    )
    status: InvocationStatus = Field(..., description="Status of the invocation")
    result: Optional[Dict[str, Any]] = Field(
        None, description="Result data for successful invocations"
    )
    error: Optional[ErrorInfo] = Field(
        None, description="Error information for failed invocations"
    )


class StreamContextContentPayload(BasePayload):
    """Payload for messages that are part of a streaming sequence."""

    payload_type: Literal[PayloadType.STREAM_CONTEXT_CONTENT] = (
        PayloadType.STREAM_CONTEXT_CONTENT
    )
    stream_id: str = Field(
        ..., description="Identifier for the stream this message belongs to"
    )
    sequence_number: int = Field(..., description="Position in the stream sequence")
    stream_position: StreamPosition = Field(..., description="Position in the stream")
    is_heartbeat: bool = Field(
        default=False, description="Whether this is a keepalive message"
    )
    content: Optional[
        Union[
            TextContentPayload,
            StructuredDataContentPayload,
            AssetReferenceContentPayload,
            InvocationContentPayload,
            InvocationResultContentPayload,
        ]
    ] = Field(None, description="The actual content payload")
    estimated_remaining: Optional[int] = Field(
        None, description="Estimated number of remaining messages"
    )


class KnowledgeRepresentationContentPayload(BasePayload):
    """Payload for formal knowledge structures used in symbolic reasoning."""

    payload_type: Literal[PayloadType.KNOWLEDGE_REPRESENTATION_CONTENT] = (
        PayloadType.KNOWLEDGE_REPRESENTATION_CONTENT
    )
    formalism: KnowledgeFormalism = Field(
        ..., description="Knowledge representation formalism"
    )
    representation: Union[str, Dict[str, Any]] = Field(
        ..., description="The actual knowledge content"
    )
    context_id: Optional[str] = Field(
        None, description="Identifier for the knowledge context/KB"
    )
    operation: Optional[KnowledgeOperation] = Field(
        None, description="Knowledge operation"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional information about the knowledge"
    )


class EventContentPayload(BasePayload):
    """Payload for standardized event notifications."""

    payload_type: Literal[PayloadType.EVENT_CONTENT] = PayloadType.EVENT_CONTENT
    event_type: str = Field(..., description="Type of event (domain-specific)")
    event_source: str = Field(..., description="Source of the event")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When the event occurred"
    )
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data payload")
    severity: Optional[EventSeverity] = Field(None, description="Event severity level")
    is_transient: bool = Field(
        default=True, description="Whether the event is point-in-time or persistent"
    )


# Create PayloadUnion after all payload types are defined
PayloadUnion = Union[
    TextContentPayload,
    StructuredDataContentPayload,
    AssetReferenceContentPayload,
    MultiPartContentPayload,
    InvocationContentPayload,
    InvocationResultContentPayload,
    StreamContextContentPayload,
    KnowledgeRepresentationContentPayload,
    EventContentPayload,
]

# Update MultiPartContentPayload to use PayloadUnion
MultiPartContentPayload.model_rebuild()


# ============================================================================
# Core Message Structure
# ============================================================================


class SIMFMetadata(BaseModel):
    """Additional contextual information for SIMF messages."""

    class Config:
        extra = "allow"  # Allow additional metadata fields


class SIMFMessage(BaseModel):
    """
    Complete Standard Internal Message Format (SIMF) message structure.

    This is the core message format used internally by OpenMAS for all
    protocol-agnostic message handling.
    """

    # Required fields
    message_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this message",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Time when this message was created or processed",
    )
    target_agent_id: str = Field(
        ..., description="Identifier of the agent that should receive this message"
    )
    message_flow_direction: MessageFlowDirection = Field(
        ..., description="Direction of message flow relative to the agent"
    )
    message_type: MessageType = Field(
        ..., description="Type of the message for routing and processing"
    )
    payload: PayloadUnion = Field(..., description="Content of the message")

    # Optional fields
    session_id: Optional[str] = Field(
        None, description="Identifier for the conversation/session"
    )
    source_protocol_type: Optional[str] = Field(
        None, description="Protocol type that the message originated from"
    )
    source_agent_id: Optional[str] = Field(
        None, description="Identifier of the agent that sent this message"
    )
    metadata: Optional[SIMFMetadata] = Field(
        default_factory=SIMFMetadata, description="Additional contextual information"
    )

    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    @field_validator("message_id")
    @classmethod
    def validate_message_id(cls, v):
        """Ensure message ID is not empty."""
        if not v or not v.strip():
            raise ValueError("message_id cannot be empty")
        return v

    @field_validator("target_agent_id")
    @classmethod
    def validate_target_agent_id(cls, v):
        """Ensure target agent ID is not empty."""
        if not v or not v.strip():
            raise ValueError("target_agent_id cannot be empty")
        return v


# ============================================================================
# Factory Functions
# ============================================================================


def create_text_message(
    text: str,
    target_agent_id: str,
    message_type: MessageType = MessageType.PLAIN_TEXT_MESSAGE,
    source_agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> SIMFMessage:
    """Create a SIMF message with text content."""
    return SIMFMessage(
        target_agent_id=target_agent_id,
        source_agent_id=source_agent_id,
        session_id=session_id,
        message_flow_direction=MessageFlowDirection.INBOUND,
        message_type=message_type,
        payload=TextContentPayload(text=text),
        metadata=SIMFMetadata(**metadata) if metadata else SIMFMetadata(),
    )


def create_structured_data_message(
    data: Dict[str, Any],
    target_agent_id: str,
    message_type: MessageType = MessageType.USER_QUERY,
    source_agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> SIMFMessage:
    """Create a SIMF message with structured data content."""
    return SIMFMessage(
        target_agent_id=target_agent_id,
        source_agent_id=source_agent_id,
        session_id=session_id,
        message_flow_direction=MessageFlowDirection.INBOUND,
        message_type=message_type,
        payload=StructuredDataContentPayload(data=data),
        metadata=SIMFMetadata(**metadata) if metadata else SIMFMetadata(),
    )


def create_asset_reference_message(
    asset_id: str,
    asset_type: AssetType,
    target_agent_id: str,
    mime_type: Optional[str] = None,
    resource_metadata: Optional[Dict[str, Any]] = None,
    message_type: MessageType = MessageType.USER_QUERY,
    source_agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> SIMFMessage:
    """Create a SIMF message with asset reference content."""
    return SIMFMessage(
        target_agent_id=target_agent_id,
        source_agent_id=source_agent_id,
        session_id=session_id,
        message_flow_direction=MessageFlowDirection.INBOUND,
        message_type=message_type,
        payload=AssetReferenceContentPayload(
            asset_id=asset_id,
            asset_type=asset_type,
            mime_type=mime_type,
            resource_metadata=resource_metadata,
        ),
        metadata=SIMFMetadata(**metadata) if metadata else SIMFMetadata(),
    )


def create_multipart_message(
    parts: List[PayloadUnion],
    target_agent_id: str,
    message_type: MessageType = MessageType.MULTI_PART_MESSAGE,
    source_agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> SIMFMessage:
    """Create a SIMF message with multiple content parts."""
    return SIMFMessage(
        target_agent_id=target_agent_id,
        source_agent_id=source_agent_id,
        session_id=session_id,
        message_flow_direction=MessageFlowDirection.INBOUND,
        message_type=message_type,
        payload=MultiPartContentPayload(parts=parts),
        metadata=SIMFMetadata(**metadata) if metadata else SIMFMetadata(),
    )


def create_invocation_message(
    invocation_name: str,
    arguments: Dict[str, Any],
    target_agent_id: str,
    message_type: MessageType = MessageType.TOOL_INVOCATION,
    source_agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> SIMFMessage:
    """Create a SIMF message for capability or tool invocation."""
    return SIMFMessage(
        target_agent_id=target_agent_id,
        source_agent_id=source_agent_id,
        session_id=session_id,
        message_flow_direction=MessageFlowDirection.INBOUND,
        message_type=message_type,
        payload=InvocationContentPayload(
            invocation_name=invocation_name, arguments=arguments
        ),
        metadata=SIMFMetadata(**metadata) if metadata else SIMFMetadata(),
    )


def create_invocation_result_message(
    invocation_name: str,
    status: InvocationStatus,
    target_agent_id: str,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[ErrorInfo] = None,
    message_type: MessageType = MessageType.TOOL_RESULT,
    source_agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> SIMFMessage:
    """Create a SIMF message for invocation results."""
    return SIMFMessage(
        target_agent_id=target_agent_id,
        source_agent_id=source_agent_id,
        session_id=session_id,
        message_flow_direction=MessageFlowDirection.OUTBOUND,
        message_type=message_type,
        payload=InvocationResultContentPayload(
            invocation_name=invocation_name, status=status, result=result, error=error
        ),
        metadata=SIMFMetadata(**metadata) if metadata else SIMFMetadata(),
    )


def create_error_message(
    error_code: str,
    error_message: str,
    target_agent_id: str,
    error_details: Optional[Dict[str, Any]] = None,
    source_agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> SIMFMessage:
    """Create a SIMF error message."""
    return SIMFMessage(
        target_agent_id=target_agent_id,
        source_agent_id=source_agent_id,
        session_id=session_id,
        message_flow_direction=MessageFlowDirection.OUTBOUND,
        message_type=MessageType.ERROR_MESSAGE,
        payload=InvocationResultContentPayload(
            invocation_name="error",
            status=InvocationStatus.FAILURE,
            error=ErrorInfo(
                code=error_code, message=error_message, details=error_details
            ),
        ),
        metadata=SIMFMetadata(**metadata) if metadata else SIMFMetadata(),
    )


def create_event_message(
    event_type: str,
    event_source: str,
    event_data: Dict[str, Any],
    target_agent_id: str,
    severity: Optional[EventSeverity] = None,
    is_transient: bool = True,
    source_agent_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> SIMFMessage:
    """Create a SIMF event notification message."""
    return SIMFMessage(
        target_agent_id=target_agent_id,
        source_agent_id=source_agent_id,
        session_id=session_id,
        message_flow_direction=MessageFlowDirection.INBOUND,
        message_type=MessageType.EVENT_NOTIFICATION,
        payload=EventContentPayload(
            event_type=event_type,
            event_source=event_source,
            data=event_data,
            severity=severity,
            is_transient=is_transient,
        ),
        metadata=SIMFMetadata(**metadata) if metadata else SIMFMetadata(),
    )
