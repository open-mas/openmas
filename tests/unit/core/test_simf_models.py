"""
Test SIMF (Standard Internal Message Format) Models

This tests the core SIMF Pydantic models to ensure they work correctly
and can be imported properly.
"""

from datetime import datetime
from uuid import uuid4

import pytest

from openmas.core.simf import (
    MessageType,
    PayloadType,
    SIMFMessage,
    create_invocation_message,
    create_text_message,
)


class TestSIMFModels:
    """Test SIMF model functionality."""

    def test_simf_message_creation(self):
        """Test basic SIMF message creation."""
        message = create_text_message(text="Hello, OpenMAS!", target_agent_id="test-agent")

        assert message.target_agent_id == "test-agent"
        assert message.message_type == MessageType.PLAIN_TEXT_MESSAGE
        assert message.payload.payload_type == PayloadType.TEXT_CONTENT
        assert message.payload.text == "Hello, OpenMAS!"

    def test_simf_invocation_message(self):
        """Test SIMF invocation message creation."""
        message = create_invocation_message(
            invocation_name="analyze_text",
            arguments={"text": "Sample text", "analysis_type": "sentiment"},
            target_agent_id="test-agent",
        )

        assert message.message_type == MessageType.TOOL_INVOCATION
        assert message.payload.payload_type == PayloadType.INVOCATION_CONTENT
        assert message.payload.invocation_name == "analyze_text"
        assert message.payload.arguments["text"] == "Sample text"
        assert message.payload.arguments["analysis_type"] == "sentiment"

    def test_simf_message_validation(self):
        """Test SIMF message validation."""
        # Valid message should not raise
        message = create_text_message("Valid message", target_agent_id="test-agent")
        assert isinstance(message, SIMFMessage)

        # Message should have required fields
        assert message.message_id is not None
        assert message.timestamp is not None
        assert message.message_type is not None
        assert message.payload is not None

    def test_simf_message_serialization(self):
        """Test SIMF message serialization (basic)."""
        message = create_text_message(
            text="Serialization test",
            target_agent_id="test-agent",
            source_agent_id="source-agent",
        )

        # Should be able to convert to dict
        message_dict = message.model_dump()
        assert isinstance(message_dict, dict)
        assert message_dict["payload"]["text"] == "Serialization test"
        assert message_dict["source_agent_id"] == "source-agent"

        # Should be able to recreate from dict
        recreated = SIMFMessage.model_validate(message_dict)
        assert recreated.payload.text == "Serialization test"
        assert recreated.source_agent_id == "source-agent"


# Simple function test to verify pytest runs correctly
def test_basic_functionality():
    """Basic test to verify pytest infrastructure works."""
    assert True


def test_imports_work():
    """Test that our core imports work correctly."""
    from openmas.core.simf import MessageType, PayloadType, SIMFMessage

    # Should be able to create enum values
    assert MessageType.PLAIN_TEXT_MESSAGE is not None
    assert PayloadType.TEXT_CONTENT is not None

    # Should be able to reference the class
    assert SIMFMessage is not None
