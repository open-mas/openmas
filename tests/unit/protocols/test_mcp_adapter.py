"""
Unit tests for MCP Protocol Adapter

Tests the MCPProtocolAdapter implementation including SIMF message translation,
configuration handling, and basic protocol operations.
"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from openmas.core.simf import (
    InvocationStatus,
    MessageType,
    SIMFMessage,
    create_invocation_message,
    create_invocation_result_message,
    create_text_message,
)
from openmas.protocols.mcp import (
    MCPConfig,
    MCPConnectionError,
    MCPProtocolAdapter,
    MCPTransportType,
)
from openmas.protocols.mcp.config import MCPStdioConfig
from openmas.protocols.mcp.message_translator import MCPMessageTranslator


class TestMCPMessageTranslator:
    """Test SIMF-MCP message translation."""

    def test_translator_creation(self):
        """Test translator can be created."""
        translator = MCPMessageTranslator("test-agent")
        assert translator.agent_id == "test-agent"

    def test_mcp_tool_call_to_simf(self):
        """Test translating MCP tool call to SIMF."""
        translator = MCPMessageTranslator("test-agent")

        mcp_message = {
            "jsonrpc": "2.0",
            "id": "test-123",
            "method": "tools/call",
            "params": {
                "name": "analyze_text",
                "arguments": {"text": "Hello world", "type": "sentiment"},
            },
        }

        simf_message = translator.to_internal_format(mcp_message)

        assert isinstance(simf_message, SIMFMessage)
        assert simf_message.message_type == MessageType.TOOL_INVOCATION
        assert simf_message.target_agent_id == "test-agent"
        assert simf_message.payload.invocation_name == "analyze_text"
        assert simf_message.payload.arguments["text"] == "Hello world"
        assert simf_message.payload.arguments["type"] == "sentiment"

    def test_simf_tool_invocation_to_mcp(self):
        """Test translating SIMF tool invocation to MCP."""
        translator = MCPMessageTranslator("test-agent")

        simf_message = create_invocation_message(
            invocation_name="process_data",
            arguments={"input": "test data"},
            target_agent_id="test-agent",
            message_type=MessageType.TOOL_INVOCATION,
        )

        mcp_message = translator.from_internal_format(simf_message)

        assert mcp_message["jsonrpc"] == "2.0"
        assert mcp_message["method"] == "tools/call"
        assert mcp_message["params"]["name"] == "process_data"
        assert mcp_message["params"]["arguments"]["input"] == "test data"

    def test_mcp_result_to_simf(self):
        """Test translating MCP result to SIMF."""
        translator = MCPMessageTranslator("test-agent")

        mcp_message = {
            "jsonrpc": "2.0",
            "id": "test-456",
            "result": {"processed_data": "TRANSFORMED", "status": "success"},
        }

        simf_message = translator.to_internal_format(mcp_message)

        assert isinstance(simf_message, SIMFMessage)
        assert simf_message.message_type == MessageType.TOOL_RESULT
        assert simf_message.payload.status == InvocationStatus.SUCCESS
        assert simf_message.payload.result["processed_data"] == "TRANSFORMED"

    def test_mcp_error_to_simf(self):
        """Test translating MCP error to SIMF."""
        translator = MCPMessageTranslator("test-agent")

        mcp_message = {
            "jsonrpc": "2.0",
            "id": "test-789",
            "error": {
                "code": -1,
                "message": "Tool not found",
                "data": {"tool_name": "missing_tool"},
            },
        }

        simf_message = translator.to_internal_format(mcp_message)

        assert isinstance(simf_message, SIMFMessage)
        assert simf_message.message_type == MessageType.ERROR_MESSAGE
        assert simf_message.payload.error.message == "Tool not found"
        assert simf_message.payload.error.details["data"]["tool_name"] == "missing_tool"


class TestMCPConfig:
    """Test MCP configuration models."""

    def test_stdio_config_creation(self):
        """Test creating stdio configuration."""
        config = MCPConfig(
            transport=MCPTransportType.STDIO,
            stdio_config=MCPStdioConfig(command="python", args=["-m", "test_server"], env={"TEST": "true"}),
        )

        assert config.transport == MCPTransportType.STDIO
        assert config.stdio_config.command == "python"
        assert config.stdio_config.args == ["-m", "test_server"]
        assert config.stdio_config.env["TEST"] == "true"

    def test_config_validation(self):
        """Test configuration validation."""
        # Should require stdio_config for stdio transport
        config = MCPConfig(transport=MCPTransportType.STDIO)

        with pytest.raises(ValueError, match="stdio_config is required"):
            config.validate_transport_config()

        # Should be valid with proper config
        config.stdio_config = MCPStdioConfig(command="test")
        config.validate_transport_config()  # Should not raise


class TestMCPProtocolAdapter:
    """Test MCP Protocol Adapter."""

    def test_adapter_creation(self):
        """Test adapter can be created."""
        adapter = MCPProtocolAdapter("test-agent")
        assert adapter.agent_id == "test-agent"
        assert not adapter.connected
        assert adapter.message_count == 0

    @patch("openmas.protocols.mcp.adapter.MCP_AVAILABLE", False)
    def test_adapter_requires_mcp_sdk(self):
        """Test adapter requires MCP SDK."""
        with pytest.raises(ImportError, match="MCP SDK not available"):
            MCPProtocolAdapter("test-agent")

    def test_message_callback_registration(self):
        """Test message callback registration."""
        adapter = MCPProtocolAdapter("test-agent")

        async def test_callback(message: SIMFMessage):
            pass

        # Should not raise
        asyncio.run(adapter.register_message_callback(test_callback))
        assert adapter.message_callback == test_callback

    def test_message_translation(self):
        """Test message translation methods."""
        adapter = MCPProtocolAdapter("test-agent")

        # Test MCP to SIMF
        mcp_message = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "test", "arguments": {}},
        }

        simf_message = adapter.to_internal_format(mcp_message)
        assert isinstance(simf_message, SIMFMessage)

        # Test SIMF to MCP
        simf_test = create_text_message(text="test message", target_agent_id="test-agent")

        mcp_result = adapter.from_internal_format(simf_test)
        assert "jsonrpc" in mcp_result

    def test_connection_without_config_fails(self):
        """Test connection fails without proper configuration."""
        adapter = MCPProtocolAdapter("test-agent")

        # Missing config should fail
        with pytest.raises(MCPConnectionError):
            asyncio.run(adapter.connect(None))


# asyncio import moved to top of file
