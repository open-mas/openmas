"""
Standard Internal Message Format (SIMF) Implementation

This module provides concrete Pydantic models for the OpenMAS Standard Internal
Message Format, enabling type-safe message handling across all protocol adapters
and reasoning engines.
"""

from .models import (  # Core message structure; Enums; Payload models;;
    # Factory functions
    AssetReferenceContentPayload,
    AssetType,
    BasePayload,
    EventContentPayload,
    InvocationContentPayload,
    InvocationResultContentPayload,
    InvocationStatus,
    KnowledgeRepresentationContentPayload,
    MessageFlowDirection,
    MessageType,
    MultiPartContentPayload,
    PayloadType,
    PayloadUnion,
    SIMFMessage,
    SIMFMetadata,
    StreamContextContentPayload,
    StructuredDataContentPayload,
    TextContentPayload,
    create_asset_reference_message,
    create_error_message,
    create_event_message,
    create_invocation_message,
    create_invocation_result_message,
    create_multipart_message,
    create_structured_data_message,
    create_text_message,
)
from .serialization import (
    SerializationError,
    SerializationFormat,
    SIMFSerializer,
    deserialize_simf_message,
    is_simf_message,
    message_from_binary,
    message_from_json,
    message_to_binary,
    message_to_json,
    serialize_simf_message,
)
from .validation import (
    SIMFValidator,
    ValidationError,
    ValidationIssue,
    ValidationResult,
    validate_simf_message,
)

__all__ = [
    # Core models
    "SIMFMessage",
    "SIMFMetadata",
    # Enums
    "MessageType",
    "PayloadType",
    "MessageFlowDirection",
    "AssetType",
    "InvocationStatus",
    # Payload models
    "BasePayload",
    "TextContentPayload",
    "StructuredDataContentPayload",
    "AssetReferenceContentPayload",
    "MultiPartContentPayload",
    "InvocationContentPayload",
    "InvocationResultContentPayload",
    "StreamContextContentPayload",
    "KnowledgeRepresentationContentPayload",
    "EventContentPayload",
    "PayloadUnion",
    # Factory functions
    "create_text_message",
    "create_structured_data_message",
    "create_asset_reference_message",
    "create_multipart_message",
    "create_invocation_message",
    "create_invocation_result_message",
    "create_error_message",
    "create_event_message",
    # Utilities
    "SIMFValidator",
    "ValidationError",
    "ValidationResult",
    "ValidationIssue",
    "validate_simf_message",
    "SIMFSerializer",
    "SerializationError",
    "SerializationFormat",
    "serialize_simf_message",
    "deserialize_simf_message",
    "message_to_json",
    "message_from_json",
    "message_to_binary",
    "message_from_binary",
    "is_simf_message",
]
