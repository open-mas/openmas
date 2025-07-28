"""Tests for port configuration in the MCP SSE communicator.

Note that when using get_server_info, we need to be aware that
FastMCP server is not actually initialized in tests, so we get
a limited set of information from the method.
"""

import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest

from openmas.communication.mcp.sse_communicator import McpSseCommunicator


@pytest.mark.asyncio
async def test_mcp_sse_port_initialization():
    """Test that the McpSseCommunicator properly initializes with the correct port."""
    # Test with integer port
    comm = McpSseCommunicator(agent_name="test_agent", service_urls={}, server_mode=True, http_port=9999)
    assert comm.http_port == 9999

    # Test with string port (should be converted to int in the code)
    comm = McpSseCommunicator(agent_name="test_agent", service_urls={}, server_mode=True, http_port="8888")
    assert comm.http_port == 8888, "String port should be converted to integer"


@pytest.mark.asyncio
async def test_mcp_sse_port_in_get_server_info():
    """Test that the port is properly included in the server info."""
    # Test with integer port
    comm = McpSseCommunicator(
        agent_name="test_agent", service_urls={}, server_mode=True, http_port=7777, http_host="localhost"
    )
    # Mock the FastMCP server
    comm.fastmcp_server = MagicMock()

    server_info = await comm.get_server_info()
    assert server_info["http_port"] == 7777, "Port should be in server info"

    # Test with string port
    comm = McpSseCommunicator(
        agent_name="test_agent", service_urls={}, server_mode=True, http_port="6666", http_host="localhost"
    )
    # Mock the FastMCP server
    comm.fastmcp_server = MagicMock()

    server_info = await comm.get_server_info()
    assert server_info["http_port"] == 6666, "Port should be in server info"


@pytest.mark.asyncio
async def test_mcp_sse_server_uses_configured_port():
    """Test that the McpSseCommunicator uses the configured port when starting the server."""
    # Create a mock FastMCP class
    mock_fastmcp = MagicMock()
    mock_fastmcp_instance = MagicMock()
    mock_fastmcp.return_value = mock_fastmcp_instance

    # Patch the FastMCP class
    with patch("openmas.communication.mcp.sse_communicator.FastMCP", mock_fastmcp):
        # Create communicator with server mode and specific port
        comm = McpSseCommunicator(agent_name="test_agent", service_urls={}, server_mode=True, http_port=9876)

        # Mock the run_sse_async method to prevent actual server startup
        mock_fastmcp_instance.run_sse_async = MagicMock(return_value=asyncio.Future())
        mock_fastmcp_instance.run_sse_async.return_value.set_result(None)

        # Run the server
        await comm._run_fastmcp_server()

        # Verify FastMCP was initialized with the correct port
        mock_fastmcp.assert_called_once()
        _, kwargs = mock_fastmcp.call_args
        assert kwargs["port"] == 9876, "FastMCP should be initialized with the configured port"

        # Verify run_sse_async was called
        mock_fastmcp_instance.run_sse_async.assert_called_once()


@pytest.mark.asyncio
async def test_mcp_sse_server_port_from_string():
    """Test that the McpSseCommunicator correctly handles string port values."""
    # Create a mock FastMCP class
    mock_fastmcp = MagicMock()
    mock_fastmcp_instance = MagicMock()
    mock_fastmcp.return_value = mock_fastmcp_instance

    # Patch the FastMCP class
    with patch("openmas.communication.mcp.sse_communicator.FastMCP", mock_fastmcp):
        # Create communicator with server mode and string port
        comm = McpSseCommunicator(
            agent_name="test_agent",
            service_urls={},
            server_mode=True,
            http_port="7777",  # String port
        )

        # Mock the run_sse_async method to prevent actual server startup
        mock_fastmcp_instance.run_sse_async = MagicMock(return_value=asyncio.Future())
        mock_fastmcp_instance.run_sse_async.return_value.set_result(None)

        # Run the server
        await comm._run_fastmcp_server()

        # Verify FastMCP was initialized with the port as integer
        mock_fastmcp.assert_called_once()
        _, kwargs = mock_fastmcp.call_args
        assert kwargs["port"] == 7777, "FastMCP should receive the port value as integer"


@pytest.mark.asyncio
async def test_no_port_override_in_server():
    """Test that the temporary port override has been removed."""
    # Create a mock FastMCP class
    mock_fastmcp = MagicMock()
    mock_fastmcp_instance = MagicMock()
    mock_fastmcp.return_value = mock_fastmcp_instance

    # Patch the FastMCP class and set the environment variable that used to trigger override
    with patch("openmas.communication.mcp.sse_communicator.FastMCP", mock_fastmcp):
        # Set the environment variable that used to trigger the override
        os.environ["OPENMAS_TEST_PORT_OVERRIDE"] = "true"

        # Create communicator with server mode and specific port
        comm = McpSseCommunicator(agent_name="test_agent", service_urls={}, server_mode=True, http_port=6543)

        # Mock the run_sse_async method to prevent actual server startup
        mock_fastmcp_instance.run_sse_async = MagicMock(return_value=asyncio.Future())
        mock_fastmcp_instance.run_sse_async.return_value.set_result(None)

        # Run the server
        await comm._run_fastmcp_server()

        # Verify FastMCP was initialized with the correct port, not the override value
        mock_fastmcp.assert_called_once()
        _, kwargs = mock_fastmcp.call_args
        assert kwargs["port"] == 6543, "FastMCP should use configured port even with override env var"
        assert kwargs["port"] != 9900, "FastMCP should not use the hardcoded override port"

        # Cleanup environment variable
        del os.environ["OPENMAS_TEST_PORT_OVERRIDE"]
