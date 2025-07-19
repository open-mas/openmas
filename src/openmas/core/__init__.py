"""
OpenMAS Core Components

This module contains core functionality for the OpenMAS framework,
including the Standard Internal Message Format (SIMF) and other
foundational components.
"""

from .simf import (
    # Core SIMF models and functionality
    SIMFMessage,
    SIMFMetadata,
    MessageType,
    PayloadType,
    MessageFlowDirection,
    AssetType,
    
    # Payload models
    BasePayload,
    TextContentPayload,
    StructuredDataContentPayload,
    AssetReferenceContentPayload,
    MultiPartContentPayload,
    InvocationContentPayload,
    InvocationResultContentPayload,
    StreamContextContentPayload,
    KnowledgeRepresentationContentPayload,
    EventContentPayload,
    PayloadUnion,
    
    # Factory functions
    create_text_message,
    create_structured_data_message,
    create_asset_reference_message,
    create_multipart_message,
    create_invocation_message,
    create_invocation_result_message,
    create_error_message,
    create_event_message,
    
    # Validation
    SIMFValidator,
    ValidationError,
    ValidationResult,
    validate_simf_message,
    
    # Serialization
    SIMFSerializer,
    SerializationError,
    SerializationFormat,
    serialize_simf_message,
    deserialize_simf_message,
    message_to_json,
    message_from_json,
    message_to_binary,
    message_from_binary,
    is_simf_message,
)

__all__ = [
    # Core SIMF models
    "SIMFMessage",
    "SIMFMetadata",
    "MessageType",
    "PayloadType", 
    "MessageFlowDirection",
    "AssetType",
    
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
    
    # Validation
    "SIMFValidator",
        "ValidationError",
    "ValidationResult", 
    "validate_simf_message",
    
    # Serialization
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