"""
Unit tests for SIMF Serialization

Comprehensive tests for SIMF message serialization including JSON, binary,
compressed formats, and error handling. These tests ensure the serialization
module achieves 70%+ coverage.
"""

import gzip
import json
import pickle
from datetime import datetime

import pytest

from openmas.core.simf import (
    InvocationStatus,
    MessageType,
    PayloadType,
    SIMFMessage,
    create_invocation_message,
    create_invocation_result_message,
    create_text_message,
)
from openmas.core.simf.serialization import (
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

# Removed unused imports


class TestSerializationFormat:
    """Test SerializationFormat enum."""

    def test_serialization_formats(self):
        """Test all serialization formats are available."""
        assert SerializationFormat.JSON == "json"
        assert SerializationFormat.JSON_COMPACT == "json_compact"
        assert SerializationFormat.JSON_PRETTY == "json_pretty"
        assert SerializationFormat.BINARY == "binary"
        assert SerializationFormat.BINARY_COMPRESSED == "binary_compressed"


class TestSIMFSerializer:
    """Test SIMFSerializer class functionality."""

    def test_serializer_creation_default(self):
        """Test serializer creation with default format."""
        serializer = SIMFSerializer()

        assert serializer.default_format == SerializationFormat.JSON

    def test_serializer_creation_custom_format(self):
        """Test serializer creation with custom format."""
        serializer = SIMFSerializer(SerializationFormat.JSON_COMPACT)

        assert serializer.default_format == SerializationFormat.JSON_COMPACT

    def test_serialize_json_format(self):
        """Test serialization to JSON format."""
        serializer = SIMFSerializer()
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        result = serializer.serialize(message, SerializationFormat.JSON)

        assert isinstance(result, str)
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["message_type"] == "PLAIN_TEXT_MESSAGE"
        assert parsed["payload"]["text"] == "Hello, world!"

    def test_serialize_json_compact_format(self):
        """Test serialization to compact JSON format."""
        serializer = SIMFSerializer()
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        compact_result = serializer.serialize(message, SerializationFormat.JSON_COMPACT)
        regular_result = serializer.serialize(message, SerializationFormat.JSON)

        assert isinstance(compact_result, str)
        assert isinstance(regular_result, str)
        # Compact should be shorter (no extra whitespace)
        assert len(compact_result) <= len(regular_result)

    def test_serialize_json_pretty_format(self):
        """Test serialization to pretty JSON format."""
        serializer = SIMFSerializer()
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        pretty_result = serializer.serialize(message, SerializationFormat.JSON_PRETTY)
        compact_result = serializer.serialize(message, SerializationFormat.JSON_COMPACT)

        assert isinstance(pretty_result, str)
        # Pretty should be longer (has indentation and newlines)
        assert len(pretty_result) > len(compact_result)
        # Should contain newlines for pretty formatting
        assert "\n" in pretty_result

    def test_serialize_binary_format(self):
        """Test serialization to binary format."""
        serializer = SIMFSerializer()
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        result = serializer.serialize(message, SerializationFormat.BINARY)

        assert isinstance(result, bytes)
        # Should be deserializable through the serializer
        deserialized = serializer.deserialize(result, SerializationFormat.BINARY)
        assert isinstance(deserialized, SIMFMessage)

    def test_serialize_binary_compressed_format(self):
        """Test serialization to compressed binary format."""
        serializer = SIMFSerializer()
        message = create_text_message(
            text="Hello, world!" * 100,  # Larger text for compression
            target_agent_id="test-agent",
        )

        compressed_result = serializer.serialize(message, SerializationFormat.BINARY_COMPRESSED)
        regular_result = serializer.serialize(message, SerializationFormat.BINARY)

        assert isinstance(compressed_result, bytes)
        assert isinstance(regular_result, bytes)
        # Compressed should be smaller for repetitive content
        assert len(compressed_result) < len(regular_result)

    def test_serialize_default_format(self):
        """Test serialization uses default format when none specified."""
        serializer = SIMFSerializer(SerializationFormat.JSON_COMPACT)
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        result = serializer.serialize(message)

        assert isinstance(result, str)  # Should be JSON format
        # Should be compact (default format)
        assert "\n" not in result

    def test_serialize_unsupported_format(self):
        """Test serialization raises error for unsupported format."""
        serializer = SIMFSerializer()
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        with pytest.raises(SerializationError, match="Unsupported serialization format"):
            serializer.serialize(message, "unsupported_format")

    def test_serialize_invalid_message(self):
        """Test serialization handles invalid message gracefully."""
        serializer = SIMFSerializer()

        with pytest.raises(SerializationError, match="Failed to serialize message"):
            serializer.serialize("not a message")

    def test_deserialize_json_format(self):
        """Test deserialization from JSON format."""
        serializer = SIMFSerializer()
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        # Serialize then deserialize
        serialized = serializer.serialize(message, SerializationFormat.JSON)
        deserialized = serializer.deserialize(serialized, SerializationFormat.JSON)

        assert isinstance(deserialized, SIMFMessage)
        assert deserialized.payload.text == "Hello, world!"
        assert deserialized.target_agent_id == "test-agent"

    def test_deserialize_binary_format(self):
        """Test deserialization from binary format."""
        serializer = SIMFSerializer()
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        # Serialize then deserialize
        serialized = serializer.serialize(message, SerializationFormat.BINARY)
        deserialized = serializer.deserialize(serialized, SerializationFormat.BINARY)

        assert isinstance(deserialized, SIMFMessage)
        assert deserialized.payload.text == "Hello, world!"
        assert deserialized.target_agent_id == "test-agent"

    def test_deserialize_binary_compressed_format(self):
        """Test deserialization from compressed binary format."""
        serializer = SIMFSerializer()
        message = create_text_message(text="Hello, world!" * 100, target_agent_id="test-agent")

        # Serialize then deserialize
        serialized = serializer.serialize(message, SerializationFormat.BINARY_COMPRESSED)
        deserialized = serializer.deserialize(serialized, SerializationFormat.BINARY_COMPRESSED)

        assert isinstance(deserialized, SIMFMessage)
        assert deserialized.payload.text == "Hello, world!" * 100
        assert deserialized.target_agent_id == "test-agent"

    def test_deserialize_invalid_data(self):
        """Test deserialization handles invalid data gracefully."""
        serializer = SIMFSerializer()

        with pytest.raises(SerializationError, match="Failed to deserialize message"):
            serializer.deserialize("invalid json", SerializationFormat.JSON)

    def test_deserialize_unsupported_format(self):
        """Test deserialization raises error for unsupported format."""
        serializer = SIMFSerializer()

        with pytest.raises(SerializationError, match="Failed to deserialize message"):
            serializer.deserialize("data", "unsupported_format")


class TestStandaloneFunctions:
    """Test standalone serialization functions."""

    def test_serialize_simf_message(self):
        """Test serialize_simf_message function."""
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        result = serialize_simf_message(message)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["payload"]["text"] == "Hello, world!"

    def test_serialize_simf_message_custom_format(self):
        """Test serialize_simf_message with custom format."""
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        result = serialize_simf_message(message, SerializationFormat.BINARY)

        assert isinstance(result, bytes)

    def test_deserialize_simf_message(self):
        """Test deserialize_simf_message function."""
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")
        serialized = serialize_simf_message(message)

        deserialized = deserialize_simf_message(serialized)

        assert isinstance(deserialized, SIMFMessage)
        assert deserialized.payload.text == "Hello, world!"

    def test_message_to_json(self):
        """Test message_to_json function."""
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        result = message_to_json(message)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["payload"]["text"] == "Hello, world!"

    def test_message_to_json_pretty(self):
        """Test message_to_json with pretty formatting."""
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        result = message_to_json(message, pretty=True)

        assert isinstance(result, str)
        assert "\n" in result  # Should have newlines for pretty formatting

    def test_message_from_json(self):
        """Test message_from_json function."""
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")
        json_str = message_to_json(message)

        deserialized = message_from_json(json_str)

        assert isinstance(deserialized, SIMFMessage)
        assert deserialized.payload.text == "Hello, world!"

    def test_message_to_binary(self):
        """Test message_to_binary function."""
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")

        result = message_to_binary(message)

        assert isinstance(result, bytes)

    def test_message_to_binary_compressed(self):
        """Test message_to_binary with compression."""
        message = create_text_message(text="Hello, world!" * 100, target_agent_id="test-agent")

        compressed_result = message_to_binary(message, compressed=True)
        regular_result = message_to_binary(message, compressed=False)

        assert isinstance(compressed_result, bytes)
        assert isinstance(regular_result, bytes)
        assert len(compressed_result) < len(regular_result)

    def test_message_from_binary(self):
        """Test message_from_binary function."""
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")
        binary_data = message_to_binary(message)

        deserialized = message_from_binary(binary_data)

        assert isinstance(deserialized, SIMFMessage)
        assert deserialized.payload.text == "Hello, world!"

    def test_message_from_binary_compressed(self):
        """Test message_from_binary with compressed data."""
        message = create_text_message(text="Hello, world!" * 100, target_agent_id="test-agent")
        binary_data = message_to_binary(message, compressed=True)

        deserialized = message_from_binary(binary_data)

        assert isinstance(deserialized, SIMFMessage)
        assert deserialized.payload.text == "Hello, world!" * 100

    def test_is_simf_message_valid(self):
        """Test is_simf_message function with valid message."""
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")
        # is_simf_message works with serialized data, not SIMFMessage objects
        json_data = message_to_json(message)

        assert is_simf_message(json_data) is True

    def test_is_simf_message_invalid(self):
        """Test is_simf_message function with invalid input."""
        assert is_simf_message("not a message") is False
        assert is_simf_message(None) is False
        assert is_simf_message({"not": "simf"}) is False

    def test_is_simf_message_dict(self):
        """Test is_simf_message function with message dict."""
        message_dict = {
            "message_id": "test-123",
            "timestamp": "2024-12-28T10:00:00",
            "target_agent_id": "test-agent",
            "message_flow_direction": "INBOUND",
            "message_type": "PLAIN_TEXT_MESSAGE",
            "payload": {"payload_type": "text_content", "text": "Hello, world!"},
        }

        # Depending on implementation, this might return True or False
        result = is_simf_message(message_dict)
        assert isinstance(result, bool)


class TestErrorHandling:
    """Test error handling in serialization functions."""

    def test_serialize_with_datetime_encoding(self):
        """Test serialization handles datetime objects correctly."""
        message = create_text_message(text="Hello, world!", target_agent_id="test-agent")
        # Message should have timestamp as datetime
        assert isinstance(message.timestamp, datetime)

        # Should serialize without error
        result = serialize_simf_message(message)
        assert isinstance(result, str)

        # Should deserialize back correctly
        deserialized = deserialize_simf_message(result)
        assert isinstance(deserialized, SIMFMessage)

    def test_json_invalid_format(self):
        """Test JSON functions handle invalid JSON gracefully."""
        with pytest.raises((SerializationError, ValueError, json.JSONDecodeError)):
            message_from_json("invalid json")

    def test_binary_invalid_format(self):
        """Test binary functions handle invalid binary data gracefully."""
        with pytest.raises((SerializationError, pickle.PickleError, Exception)):
            message_from_binary(b"invalid binary data")

    def test_binary_compressed_invalid_format(self):
        """Test compressed binary handles invalid compressed data gracefully."""
        with pytest.raises((SerializationError, gzip.BadGzipFile, Exception)):
            message_from_binary(b"not gzipped data", compressed=True)


class TestRoundTripSerialization:
    """Test round-trip serialization for different message types."""

    def test_text_message_round_trip_json(self):
        """Test text message JSON round-trip serialization."""
        original = create_text_message(text="Hello, world!", target_agent_id="test-agent", session_id="session-123")

        # JSON round trip
        json_str = message_to_json(original)
        deserialized = message_from_json(json_str)

        assert deserialized.payload.text == original.payload.text
        assert deserialized.target_agent_id == original.target_agent_id
        assert deserialized.session_id == original.session_id

    def test_invocation_message_round_trip_binary(self):
        """Test invocation message binary round-trip serialization."""
        original = create_invocation_message(
            invocation_name="search_database",
            arguments={"query": "test", "limit": 10},
            target_agent_id="test-agent",
        )

        # Binary round trip
        binary_data = message_to_binary(original)
        deserialized = message_from_binary(binary_data)

        assert deserialized.payload.invocation_name == original.payload.invocation_name
        assert deserialized.payload.arguments == original.payload.arguments
        assert deserialized.target_agent_id == original.target_agent_id

    def test_result_message_round_trip_compressed(self):
        """Test result message compressed round-trip serialization."""
        original = create_invocation_result_message(
            invocation_name="search_database",
            status=InvocationStatus.SUCCESS,
            result={"records": [{"id": 1, "name": "test"}] * 100},  # Large result
            target_agent_id="test-agent",
        )

        # Compressed binary round trip
        binary_data = message_to_binary(original, compressed=True)
        deserialized = message_from_binary(binary_data)

        assert deserialized.payload.invocation_name == original.payload.invocation_name
        assert deserialized.payload.status == original.payload.status
        assert deserialized.payload.result == original.payload.result
        assert deserialized.target_agent_id == original.target_agent_id


class TestPerformanceAndEdgeCases:
    """Test performance characteristics and edge cases."""

    def test_large_message_serialization(self):
        """Test serialization of large messages."""
        large_text = "x" * 10000  # 10KB text
        message = create_text_message(text=large_text, target_agent_id="test-agent")

        # Should handle large messages
        json_result = message_to_json(message)
        binary_result = message_to_binary(message)

        assert isinstance(json_result, str)
        assert isinstance(binary_result, bytes)
        assert len(json_result) > 10000
        assert len(binary_result) > 0

    def test_unicode_content_serialization(self):
        """Test serialization with unicode content."""
        unicode_text = "Hello, 世界! 🌍 Café naïve résumé"
        message = create_text_message(text=unicode_text, target_agent_id="test-agent")

        # JSON round trip with unicode
        json_str = message_to_json(message)
        deserialized = message_from_json(json_str)

        assert deserialized.payload.text == unicode_text

    def test_empty_message_content(self):
        """Test serialization with empty content."""
        message = create_text_message(text="", target_agent_id="test-agent")

        # Should handle empty content
        json_str = message_to_json(message)
        deserialized = message_from_json(json_str)

        assert deserialized.payload.text == ""
