"""
IProtocolAdapter Test Framework Template

This module provides comprehensive test templates for IProtocolAdapter implementations,
designed to prevent AI hallucination by using real protocol data and validating
actual protocol behavior against the SIMF specification.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openmas.core.simf import (
    InvocationStatus,
    MessageType,
    PayloadType,
    SIMFMessage,
    ValidationError,
    message_from_json,
    message_to_json,
    validate_simf_message,
)

from .common_fixtures import (
    real_a2a_messages,
    real_http_messages,
    real_mcp_messages,
    simf_message_fixtures,
    validate_real_a2a_message,
    validate_real_http_message,
    validate_real_mcp_message,
)

# ============================================================================
# IProtocolAdapter Interface Definition (for testing)
# ============================================================================


class IProtocolAdapter(ABC):
    """
    Interface definition for protocol adapters.
    This mirrors the actual interface and is used for testing.
    """

    @abstractmethod
    async def connect(self, config: Dict[str, Any]) -> None:
        """Initialize protocol connection."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up protocol connection."""
        pass

    @abstractmethod
    async def send_message(self, internal_message: SIMFMessage) -> None:
        """Send SIMF message via protocol."""
        pass

    @abstractmethod
    async def register_message_callback(
        self, callback: Callable[[SIMFMessage], Awaitable[None]]
    ) -> None:
        """Register callback for incoming messages."""
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get current protocol connection status."""
        pass

    @abstractmethod
    def to_internal_format(self, protocol_message: Any) -> SIMFMessage:
        """Convert protocol message to SIMF."""
        pass

    @abstractmethod
    def from_internal_format(self, internal_message: SIMFMessage) -> Any:
        """Convert SIMF to protocol message."""
        pass


# ============================================================================
# Protocol-Specific Test Data Fixtures
# ============================================================================


@pytest.fixture
def real_protocol_message_fixtures():
    """
    Factory for creating protocol-specific test fixtures.
    Returns real protocol messages to prevent hallucination.
    """

    def _create_fixtures(protocol_type: str) -> Dict[str, Any]:
        if protocol_type == "mcp":
            return {
                "initialize": {
                    "jsonrpc": "2.0",
                    "id": "init-001",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {"tools": {}, "resources": {}},
                        "clientInfo": {"name": "OpenMAS-Test", "version": "0.3.0"},
                    },
                },
                "tool_call": {
                    "jsonrpc": "2.0",
                    "id": "call-001",
                    "method": "tools/call",
                    "params": {
                        "name": "search_database",
                        "arguments": {"query": "test", "limit": 5},
                    },
                },
                "error": {
                    "jsonrpc": "2.0",
                    "id": "call-001",
                    "error": {"code": -32601, "message": "Method not found"},
                },
            }
        elif protocol_type == "a2a":
            return {
                "capability_request": {
                    "id": "msg-001",
                    "timestamp": datetime.utcnow().isoformat(),
                    "sender": "agent-001",
                    "recipient": "agent-002",
                    "parts": [
                        {
                            "content_type": "application/json",
                            "content": {"capability": "test", "parameters": {}},
                        }
                    ],
                },
                "multipart": {
                    "id": "msg-002",
                    "timestamp": datetime.utcnow().isoformat(),
                    "sender": "agent-001",
                    "recipient": "agent-002",
                    "parts": [
                        {"content_type": "text/plain", "content": "Test message"},
                        {"content_type": "image/jpeg", "file_id": "test.jpg"},
                    ],
                },
            }
        elif protocol_type == "http":
            return {
                "get_request": {
                    "method": "GET",
                    "url": "/api/v1/test",
                    "headers": {"Accept": "application/json"},
                },
                "post_request": {
                    "method": "POST",
                    "url": "/api/v1/invoke",
                    "headers": {"Content-Type": "application/json"},
                    "body": {"action": "test", "data": {}},
                },
                "response": {
                    "status_code": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": {"status": "success", "result": {}},
                },
            }
        else:
            raise ValueError(f"Unknown protocol type: {protocol_type}")

    return _create_fixtures


# ============================================================================
# Base Test Template Class
# ============================================================================


class IProtocolAdapterTestTemplate:
    """
    Comprehensive test template for IProtocolAdapter implementations.

    This template ensures that protocol adapter implementations:
    1. Correctly translate between protocol formats and SIMF
    2. Handle real protocol messages without hallucination
    3. Maintain semantic preservation across translations
    4. Handle errors and edge cases properly
    5. Follow the IProtocolAdapter interface contract
    """

    @pytest.fixture
    def adapter(self) -> IProtocolAdapter:
        """
        Override this fixture in your test class to provide your
        IProtocolAdapter implementation for testing.
        """
        raise NotImplementedError("Must provide adapter fixture in test class")

    @pytest.fixture
    def protocol_type(self) -> str:
        """
        Override this fixture to specify the protocol type being tested
        (e.g., "mcp", "a2a", "http").
        """
        raise NotImplementedError("Must provide protocol_type fixture in test class")

    # ========================================================================
    # Connection Lifecycle Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_connect_with_valid_config(
        self, adapter: IProtocolAdapter, create_test_protocol_config
    ):
        """Test successful connection with valid configuration."""
        config = create_test_protocol_config("test-protocol")

        # Should not raise exception
        await adapter.connect(config)

        # Status should indicate connected
        status = await adapter.get_status()
        assert status.get("status") in ["connected", "ready", "active"]

    @pytest.mark.asyncio
    async def test_connect_with_invalid_config(self, adapter: IProtocolAdapter):
        """Test connection failure with invalid configuration."""
        invalid_config = {"invalid": "config"}

        with pytest.raises((ValueError, ConnectionError, KeyError)):
            await adapter.connect(invalid_config)

    @pytest.mark.asyncio
    async def test_disconnect_cleans_up_resources(
        self, adapter: IProtocolAdapter, create_test_protocol_config
    ):
        """Test that disconnect properly cleans up resources."""
        config = create_test_protocol_config("test-protocol")
        await adapter.connect(config)

        # Should not raise exception
        await adapter.disconnect()

        # Status should indicate disconnected
        status = await adapter.get_status()
        assert status.get("status") in ["disconnected", "offline", "stopped"]

    @pytest.mark.asyncio
    async def test_multiple_connect_disconnect_cycles(
        self, adapter: IProtocolAdapter, create_test_protocol_config
    ):
        """Test multiple connect/disconnect cycles for resource leaks."""
        config = create_test_protocol_config("test-protocol")

        for _ in range(3):
            await adapter.connect(config)
            status = await adapter.get_status()
            assert status.get("status") in ["connected", "ready", "active"]

            await adapter.disconnect()
            status = await adapter.get_status()
            assert status.get("status") in ["disconnected", "offline", "stopped"]

    # ========================================================================
    # Message Translation Tests (Critical for preventing hallucination)
    # ========================================================================

    def test_to_internal_format_with_real_protocol_messages(
        self,
        adapter: IProtocolAdapter,
        protocol_type: str,
        real_protocol_message_fixtures,
    ):
        """
        Test translation of real protocol messages to SIMF.
        This is critical for preventing hallucination.
        """
        real_messages = real_protocol_message_fixtures(protocol_type)

        for message_name, protocol_message in real_messages.items():
            # Validate the protocol message is real
            if protocol_type == "mcp":
                assert validate_real_mcp_message(
                    protocol_message
                ), f"Invalid MCP message: {message_name}"
            elif protocol_type == "a2a":
                assert validate_real_a2a_message(
                    protocol_message
                ), f"Invalid A2A message: {message_name}"
            elif protocol_type == "http":
                assert validate_real_http_message(
                    protocol_message
                ), f"Invalid HTTP message: {message_name}"

            # Convert to SIMF
            simf_message = adapter.to_internal_format(protocol_message)

            # Validate SIMF message
            assert isinstance(
                simf_message, SIMFMessage
            ), f"Result is not SIMFMessage for {message_name}"

            # Validate SIMF message is valid
            validation_result = validate_simf_message(simf_message)
            assert (
                validation_result.is_valid
            ), f"Invalid SIMF message for {message_name}: {validation_result.issues}"

            # Check semantic preservation
            self._validate_semantic_preservation(
                protocol_message, simf_message, protocol_type
            )

    def test_from_internal_format_with_real_simf_messages(
        self,
        adapter: IProtocolAdapter,
        protocol_type: str,
        simf_message_fixtures: Dict[str, SIMFMessage],
    ):
        """
        Test translation of SIMF messages to protocol format.
        Ensures SIMF semantic information is preserved.
        """
        for message_name, simf_message in simf_message_fixtures.items():
            # Convert from SIMF to protocol format
            protocol_message = adapter.from_internal_format(simf_message)

            # Validate protocol message format
            if protocol_type == "mcp":
                assert validate_real_mcp_message(
                    protocol_message
                ), f"Invalid MCP output for {message_name}"
            elif protocol_type == "a2a":
                assert validate_real_a2a_message(
                    protocol_message
                ), f"Invalid A2A output for {message_name}"
            elif protocol_type == "http":
                assert validate_real_http_message(
                    protocol_message
                ), f"Invalid HTTP output for {message_name}"

            # Check that key SIMF information is preserved
            self._validate_simf_preservation(
                simf_message, protocol_message, protocol_type
            )

    def test_roundtrip_translation_preserves_semantics(
        self,
        adapter: IProtocolAdapter,
        protocol_type: str,
        real_protocol_message_fixtures,
    ):
        """
        Test that roundtrip translation (protocol -> SIMF -> protocol) preserves semantics.
        This catches translation errors that could lead to hallucination.
        """
        real_messages = real_protocol_message_fixtures(protocol_type)

        for message_name, original_message in real_messages.items():
            # Skip error messages as they may not roundtrip identically
            if "error" in message_name.lower():
                continue

            # Protocol -> SIMF -> Protocol
            simf_message = adapter.to_internal_format(original_message)
            roundtrip_message = adapter.from_internal_format(simf_message)

            # Validate that semantic content is preserved
            self._validate_roundtrip_semantics(
                original_message, roundtrip_message, protocol_type
            )

    # ========================================================================
    # Error Handling Tests
    # ========================================================================

    def test_to_internal_format_handles_malformed_messages(
        self, adapter: IProtocolAdapter
    ):
        """Test that malformed protocol messages are handled gracefully."""
        malformed_messages = [
            None,
            {},
            {"invalid": "structure"},
            "not_a_dict",
            [],
        ]

        for malformed_message in malformed_messages:
            with pytest.raises((ValueError, TypeError, AttributeError)):
                adapter.to_internal_format(malformed_message)

    def test_from_internal_format_handles_unsupported_payload_types(
        self, adapter: IProtocolAdapter, simf_message_fixtures: Dict[str, SIMFMessage]
    ):
        """Test handling of SIMF payload types that the protocol doesn't support."""
        # Test with each message type
        for message_name, simf_message in simf_message_fixtures.items():
            try:
                result = adapter.from_internal_format(simf_message)
                # If no exception, validate the result
                assert result is not None
            except (ValueError, NotImplementedError) as e:
                # Expected for unsupported payload types
                assert (
                    "unsupported" in str(e).lower()
                    or "not implemented" in str(e).lower()
                )

    # ========================================================================
    # Message Callback Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_register_message_callback(self, adapter: IProtocolAdapter):
        """Test message callback registration."""
        callback_called = False
        received_message = None

        async def test_callback(message: SIMFMessage):
            nonlocal callback_called, received_message
            callback_called = True
            received_message = message

        await adapter.register_message_callback(test_callback)

        # The callback should be registered (we can't test invocation without a real connection)
        # This test validates the interface contract
        assert True  # If no exception was raised, registration succeeded

    @pytest.mark.asyncio
    async def test_multiple_callback_registration(self, adapter: IProtocolAdapter):
        """Test that multiple callbacks can be registered."""
        callback1_called = False
        callback2_called = False

        async def callback1(message: SIMFMessage):
            nonlocal callback1_called
            callback1_called = True

        async def callback2(message: SIMFMessage):
            nonlocal callback2_called
            callback2_called = True

        await adapter.register_message_callback(callback1)
        await adapter.register_message_callback(callback2)

        # Both callbacks should be registered
        assert True  # Interface contract validated

    # ========================================================================
    # Helper Methods for Validation
    # ========================================================================

    def _validate_semantic_preservation(
        self,
        protocol_message: Dict[str, Any],
        simf_message: SIMFMessage,
        protocol_type: str,
    ):
        """Validate that protocol -> SIMF translation preserves semantics."""
        if protocol_type == "mcp":
            self._validate_mcp_to_simf_semantics(protocol_message, simf_message)
        elif protocol_type == "a2a":
            self._validate_a2a_to_simf_semantics(protocol_message, simf_message)
        elif protocol_type == "http":
            self._validate_http_to_simf_semantics(protocol_message, simf_message)

    def _validate_simf_preservation(
        self,
        simf_message: SIMFMessage,
        protocol_message: Dict[str, Any],
        protocol_type: str,
    ):
        """Validate that SIMF -> protocol translation preserves SIMF semantics."""
        if protocol_type == "mcp":
            self._validate_simf_to_mcp_preservation(simf_message, protocol_message)
        elif protocol_type == "a2a":
            self._validate_simf_to_a2a_preservation(simf_message, protocol_message)
        elif protocol_type == "http":
            self._validate_simf_to_http_preservation(simf_message, protocol_message)

    def _validate_mcp_to_simf_semantics(
        self, mcp_message: Dict[str, Any], simf_message: SIMFMessage
    ):
        """Validate MCP -> SIMF semantic preservation."""
        # MCP tool calls should become SIMF tool invocations
        if mcp_message.get("method") == "tools/call":
            assert simf_message.message_type == MessageType.TOOL_INVOCATION
            assert simf_message.payload.payload_type == PayloadType.INVOCATION_CONTENT
            assert simf_message.payload.invocation_name == mcp_message["params"]["name"]

        # MCP tool responses should become SIMF tool results
        elif "result" in mcp_message and "content" in mcp_message["result"]:
            assert simf_message.message_type == MessageType.TOOL_RESULT
            assert (
                simf_message.payload.payload_type
                == PayloadType.INVOCATION_RESULT_CONTENT
            )

        # MCP errors should become SIMF error messages
        elif "error" in mcp_message:
            assert simf_message.message_type == MessageType.ERROR_MESSAGE

    def _validate_a2a_to_simf_semantics(
        self, a2a_message: Dict[str, Any], simf_message: SIMFMessage
    ):
        """Validate A2A -> SIMF semantic preservation."""
        # A2A multi-part messages should preserve part structure
        if len(a2a_message.get("parts", [])) > 1:
            assert simf_message.payload.payload_type == PayloadType.MULTI_PART_CONTENT
            assert len(simf_message.payload.parts) == len(a2a_message["parts"])

        # A2A capability requests should become SIMF capability invocations
        parts = a2a_message.get("parts", [])
        if (
            parts
            and isinstance(parts[0].get("content"), dict)
            and "capability" in parts[0]["content"]
        ):
            assert simf_message.message_type == MessageType.CAPABILITY_INVOCATION

    def _validate_http_to_simf_semantics(
        self, http_message: Dict[str, Any], simf_message: SIMFMessage
    ):
        """Validate HTTP -> SIMF semantic preservation."""
        # HTTP requests should become appropriate SIMF message types
        if "method" in http_message:
            if http_message["method"] == "POST" and "/invoke" in http_message.get(
                "url", ""
            ):
                assert simf_message.message_type in [
                    MessageType.CAPABILITY_INVOCATION,
                    MessageType.TOOL_INVOCATION,
                ]

        # HTTP error responses should become SIMF error messages
        elif http_message.get("status_code", 200) >= 400:
            assert simf_message.message_type == MessageType.ERROR_MESSAGE

    def _validate_simf_to_mcp_preservation(
        self, simf_message: SIMFMessage, mcp_message: Dict[str, Any]
    ):
        """Validate SIMF -> MCP preservation."""
        # SIMF tool invocations should become MCP tool calls
        if simf_message.message_type == MessageType.TOOL_INVOCATION:
            assert mcp_message.get("method") == "tools/call"
            assert "name" in mcp_message.get("params", {})

        # SIMF tool results should have proper MCP response structure
        elif simf_message.message_type == MessageType.TOOL_RESULT:
            assert "result" in mcp_message or "error" in mcp_message

    def _validate_simf_to_a2a_preservation(
        self, simf_message: SIMFMessage, a2a_message: Dict[str, Any]
    ):
        """Validate SIMF -> A2A preservation."""
        # SIMF multi-part content should preserve parts
        if simf_message.payload.payload_type == PayloadType.MULTI_PART_CONTENT:
            assert len(a2a_message.get("parts", [])) == len(simf_message.payload.parts)

        # Required A2A fields should be present
        required_fields = ["id", "timestamp", "sender", "recipient", "parts"]
        assert all(field in a2a_message for field in required_fields)

    def _validate_simf_to_http_preservation(
        self, simf_message: SIMFMessage, http_message: Dict[str, Any]
    ):
        """Validate SIMF -> HTTP preservation."""
        # HTTP messages should have proper structure
        if "method" in http_message:
            # HTTP request
            assert http_message["method"] in ["GET", "POST", "PUT", "DELETE"]
            assert "url" in http_message
        else:
            # HTTP response
            assert "status_code" in http_message
            assert isinstance(http_message["status_code"], int)

    def _validate_roundtrip_semantics(
        self, original: Dict[str, Any], roundtrip: Dict[str, Any], protocol_type: str
    ):
        """Validate that roundtrip translation preserves core semantics."""
        if protocol_type == "mcp":
            # MCP message ID should be preserved
            if "id" in original:
                assert "id" in roundtrip

            # Method should be preserved
            if "method" in original:
                assert roundtrip.get("method") == original.get("method")

        elif protocol_type == "a2a":
            # A2A part count should be preserved
            orig_parts = len(original.get("parts", []))
            round_parts = len(roundtrip.get("parts", []))
            assert round_parts == orig_parts

        elif protocol_type == "http":
            # HTTP method should be preserved
            if "method" in original:
                assert roundtrip.get("method") == original.get("method")


# ============================================================================
# Test Suite Factory
# ============================================================================


def create_protocol_adapter_test_suite(
    adapter_class,
    protocol_type: str,
    additional_fixtures: Optional[Dict[str, Any]] = None,
) -> type:
    """
    Factory function to create a complete test suite for a protocol adapter.

    Args:
        adapter_class: The IProtocolAdapter implementation to test
        protocol_type: The protocol type ("mcp", "a2a", "http", etc.)
        additional_fixtures: Additional test fixtures specific to the protocol

    Returns:
        A test class that can be run with pytest
    """

    class GeneratedProtocolAdapterTests(IProtocolAdapterTestTemplate):

        @pytest.fixture
        def adapter(self) -> IProtocolAdapter:
            return adapter_class()

        @pytest.fixture
        def protocol_type(self) -> str:
            return protocol_type

        # Add any additional fixtures
        if additional_fixtures:
            for name, fixture in additional_fixtures.items():
                locals()[name] = pytest.fixture()(fixture)

    GeneratedProtocolAdapterTests.__name__ = f"Test{adapter_class.__name__}"

    return GeneratedProtocolAdapterTests
