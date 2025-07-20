"""
SIMF Serialization Utilities

This module provides serialization utilities for SIMF messages, enabling
efficient conversion between SIMF objects and various formats (JSON, binary)
for transmission over different protocols and storage.
"""

import gzip
import json
import pickle
from datetime import datetime
from enum import Enum
from typing import Optional, Union

from .models import SIMFMessage


class SerializationFormat(str, Enum):
    """Supported serialization formats."""

    JSON = "json"
    JSON_COMPACT = "json_compact"
    JSON_PRETTY = "json_pretty"
    BINARY = "binary"
    BINARY_COMPRESSED = "binary_compressed"


class SerializationError(Exception):
    """Exception raised when serialization/deserialization fails."""

    pass


class SIMFSerializer:
    """
    Comprehensive SIMF message serializer.

    Handles serialization and deserialization of SIMF messages to/from
    various formats with proper error handling and optimization.
    """

    def __init__(self, default_format: SerializationFormat = SerializationFormat.JSON):
        """
        Initialize serializer.

        Args:
            default_format: Default serialization format to use
        """
        self.default_format = default_format

    def serialize(
        self, message: SIMFMessage, format: Optional[SerializationFormat] = None
    ) -> Union[str, bytes]:
        """
        Serialize a SIMF message to the specified format.

        Args:
            message: SIMFMessage to serialize
            format: Serialization format (uses default if None)

        Returns:
            Serialized message as string or bytes

        Raises:
            SerializationError: If serialization fails
        """
        format = format or self.default_format

        try:
            if format == SerializationFormat.JSON:
                return self._serialize_json(message, compact=False, pretty=False)
            elif format == SerializationFormat.JSON_COMPACT:
                return self._serialize_json(message, compact=True, pretty=False)
            elif format == SerializationFormat.JSON_PRETTY:
                return self._serialize_json(message, compact=False, pretty=True)
            elif format == SerializationFormat.BINARY:
                return self._serialize_binary(message, compressed=False)
            elif format == SerializationFormat.BINARY_COMPRESSED:
                return self._serialize_binary(message, compressed=True)
            else:
                raise SerializationError(f"Unsupported serialization format: {format}")

        except Exception as e:
            raise SerializationError(f"Failed to serialize message: {str(e)}") from e

    def deserialize(
        self, data: Union[str, bytes], format: Optional[SerializationFormat] = None
    ) -> SIMFMessage:
        """
        Deserialize data to a SIMF message.

        Args:
            data: Serialized data to deserialize
            format: Expected format (auto-detected if None)

        Returns:
            Deserialized SIMFMessage

        Raises:
            SerializationError: If deserialization fails
        """
        if format is None:
            format = self._detect_format(data)

        try:
            if format in [
                SerializationFormat.JSON,
                SerializationFormat.JSON_COMPACT,
                SerializationFormat.JSON_PRETTY,
            ]:
                return self._deserialize_json(data)
            elif format in [
                SerializationFormat.BINARY,
                SerializationFormat.BINARY_COMPRESSED,
            ]:
                return self._deserialize_binary(data)
            else:
                raise SerializationError(
                    f"Unsupported deserialization format: {format}"
                )

        except Exception as e:
            raise SerializationError(f"Failed to deserialize message: {str(e)}") from e

    def _serialize_json(
        self, message: SIMFMessage, compact: bool = False, pretty: bool = False
    ) -> str:
        """Serialize message to JSON format."""
        # Convert to dictionary using Pydantic's dict method
        message_dict = message.dict()

        # Custom datetime serialization
        def datetime_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        if pretty:
            return json.dumps(
                message_dict, indent=2, default=datetime_serializer, ensure_ascii=False
            )
        elif compact:
            return json.dumps(
                message_dict,
                separators=(",", ":"),
                default=datetime_serializer,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                message_dict, default=datetime_serializer, ensure_ascii=False
            )

    def _deserialize_json(self, data: Union[str, bytes]) -> SIMFMessage:
        """Deserialize JSON data to SIMF message."""
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        message_dict = json.loads(data)

        # Parse datetime fields
        if "timestamp" in message_dict and isinstance(message_dict["timestamp"], str):
            try:
                message_dict["timestamp"] = datetime.fromisoformat(
                    message_dict["timestamp"].replace("Z", "+00:00")
                )
            except ValueError:
                # Fallback to current time if parsing fails
                message_dict["timestamp"] = datetime.utcnow()

        # Handle event payload timestamps
        if (
            message_dict.get("payload", {}).get("payload_type") == "event_content"
            and "timestamp" in message_dict["payload"]
            and isinstance(message_dict["payload"]["timestamp"], str)
        ):
            try:
                message_dict["payload"]["timestamp"] = datetime.fromisoformat(
                    message_dict["payload"]["timestamp"].replace("Z", "+00:00")
                )
            except ValueError:
                message_dict["payload"]["timestamp"] = datetime.utcnow()

        return SIMFMessage(**message_dict)

    def _serialize_binary(
        self, message: SIMFMessage, compressed: bool = False
    ) -> bytes:
        """Serialize message to binary format."""
        # Convert to dictionary first
        message_dict = message.dict()

        # Serialize with pickle
        binary_data = pickle.dumps(message_dict, protocol=pickle.HIGHEST_PROTOCOL)

        if compressed:
            binary_data = gzip.compress(binary_data)

        return binary_data

    def _deserialize_binary(self, data: bytes) -> SIMFMessage:
        """Deserialize binary data to SIMF message."""
        # Try to decompress if it looks compressed
        try:
            # Check if data starts with gzip magic number
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
        except (OSError, ValueError):
            # If decompression fails, assume it's not compressed
            pass

        # Deserialize with pickle
        message_dict = pickle.loads(data)

        return SIMFMessage(**message_dict)

    def _detect_format(self, data: Union[str, bytes]) -> SerializationFormat:
        """Auto-detect the format of serialized data."""
        if isinstance(data, str):
            # Try to parse as JSON
            try:
                json.loads(data)
                return SerializationFormat.JSON
            except (json.JSONDecodeError, ValueError):
                pass
        elif isinstance(data, bytes):
            # Check for gzip compression
            if data[:2] == b"\x1f\x8b":
                return SerializationFormat.BINARY_COMPRESSED

            # Check if it's JSON bytes
            try:
                json.loads(data.decode("utf-8"))
                return SerializationFormat.JSON
            except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
                pass

            # Assume binary pickle format
            return SerializationFormat.BINARY

        raise SerializationError("Unable to detect serialization format")

    def get_message_size(
        self, message: SIMFMessage, format: Optional[SerializationFormat] = None
    ) -> int:
        """
        Get the size of a message when serialized.

        Args:
            message: SIMFMessage to measure
            format: Serialization format (uses default if None)

        Returns:
            Size in bytes
        """
        serialized = self.serialize(message, format)
        if isinstance(serialized, str):
            return len(serialized.encode("utf-8"))
        return len(serialized)

    def is_compatible(self, data: Union[str, bytes]) -> bool:
        """
        Check if data can be deserialized as a SIMF message.

        Args:
            data: Data to check

        Returns:
            True if data appears to be a valid SIMF message
        """
        try:
            message = self.deserialize(data)
            return isinstance(message, SIMFMessage)
        except (SerializationError, ValueError, TypeError):
            return False


# Convenience functions for common serialization patterns
_default_serializer = SIMFSerializer()


def serialize_simf_message(
    message: SIMFMessage, format: SerializationFormat = SerializationFormat.JSON
) -> Union[str, bytes]:
    """Serialize a SIMF message using the default serializer."""
    return _default_serializer.serialize(message, format)


def deserialize_simf_message(data: Union[str, bytes]) -> SIMFMessage:
    """Deserialize data to a SIMF message using the default serializer."""
    return _default_serializer.deserialize(data)


def message_to_json(message: SIMFMessage, pretty: bool = False) -> str:
    """Convert a SIMF message to JSON string."""
    format = SerializationFormat.JSON_PRETTY if pretty else SerializationFormat.JSON
    return _default_serializer.serialize(message, format)


def message_from_json(json_str: str) -> SIMFMessage:
    """Create a SIMF message from JSON string."""
    return _default_serializer.deserialize(json_str, SerializationFormat.JSON)


def message_to_binary(message: SIMFMessage, compressed: bool = True) -> bytes:
    """Convert a SIMF message to binary format."""
    format = (
        SerializationFormat.BINARY_COMPRESSED
        if compressed
        else SerializationFormat.BINARY
    )
    return _default_serializer.serialize(message, format)


def message_from_binary(binary_data: bytes) -> SIMFMessage:
    """Create a SIMF message from binary data."""
    return _default_serializer.deserialize(binary_data)


def get_message_json_size(message: SIMFMessage) -> int:
    """Get the JSON size of a SIMF message in bytes."""
    return _default_serializer.get_message_size(message, SerializationFormat.JSON)


def is_simf_message(data: Union[str, bytes]) -> bool:
    """Check if data represents a valid SIMF message."""
    return _default_serializer.is_compatible(data)
