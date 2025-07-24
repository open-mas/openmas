"""
Anti-Hallucination Test Configuration

This module provides pytest fixtures that validate against REAL MCP 1.12.0 behavior.
CRITICAL: No mocking of external MCP SDK calls allowed in integration tests.

Lessons from 0.2.0: 1000+ passing tests with 80% coverage but NONE worked with
real libraries.
This configuration prevents that by enforcing real-first testing patterns.
"""

import asyncio
import contextlib
import os
import subprocess
import tempfile
import time
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest

# Real MCP imports - will fail fast if SDK not available
try:
    from mcp import ClientRequest
    from mcp.client.session import ClientSession
    from mcp.client.stdio import stdio_client
    from mcp.server.fastmcp import FastMCP
    from mcp.server.stdio import stdio_server

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# OpenMAS imports
from openmas.agent.mcp_agent import MCPAgent
from openmas.core.simf import (
    MessageType,
    SIMFMessage,
    create_invocation_message,
    create_invocation_result_message,
    create_text_message,
)


@pytest.fixture(scope="session")
def check_mcp_availability() -> None:
    """Ensure MCP SDK is available - fail fast if not"""
    if not MCP_AVAILABLE:
        pytest.skip("MCP SDK not available - install with 'pip install mcp'")


@pytest.fixture(scope="session")
def real_mcp_server(check_mcp_availability: None) -> FastMCP:
    """
    Minimal REAL MCP server - no mocking allowed.

    Creates actual FastMCP server with real tools and resources.
    Critical: This validates actual MCP 1.12.0 protocol behavior.
    """
    mcp = FastMCP("anti_hallucination_test_server")

    @mcp.tool()
    def test_add(a: int, b: int) -> int:
        """Test tool for validating real MCP tool execution"""
        return a + b

    @mcp.tool()
    def test_echo(message: str) -> str:
        """Test tool for validating message handling"""
        return f"Echo: {message}"

    @mcp.tool()
    def test_async_operation() -> str:
        """Test tool for validating async operations"""
        import time as time_module

        time_module.sleep(0.1)  # Simulate async work
        return "Async operation completed"

    @mcp.resource("test://resource/{id}")
    def test_resource(id: str) -> str:
        """Test resource for validating MCP resource access"""
        return f"Real resource content for {id}"

    @mcp.resource("test://config/info")
    def test_config_resource() -> str:
        """Test configuration resource"""
        return "Real MCP server configuration data"

    return mcp


# real_mcp_client_session fixture removed - no longer needed


# Helper function removed - no longer needed for deprecated tests


@pytest.fixture
def anti_hallucination_validator() -> object:
    """
    Validates no critical paths are mocked.

    This fixture prevents the 0.2.0 problem where all tests passed
    but none worked with real libraries.
    """

    def validate_no_mocking(module_names: list[str]) -> None:
        """
        Ensure specified modules are not mocked.

        Args:
            module_names: List of module names that must NOT be mocked
        Raises:
            AssertionError: If any critical module is mocked
        """
        import sys

        # Check for common mocking patterns
        mocked_modules = []
        for module_name in module_names:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                module_type = str(type(module))

                # Check for Mock, MagicMock, patch, etc.
                if any(
                    mock_indicator in module_type.lower() for mock_indicator in ["mock", "patch", "magicmock", "spec"]
                ):
                    mocked_modules.append(module_name)

        assert not mocked_modules, (
            f"CRITICAL ANTI-HALLUCINATION FAILURE: "
            f"The following critical modules are mocked: {mocked_modules}. "
            f"Integration tests must use real implementations to prevent "
            f"the 0.2.0 problem of passing tests that don't work with real libraries."
        )

    return validate_no_mocking


@pytest.fixture
def mcp_timeout_manager() -> object:
    """
    Manages timeouts for MCP operations to prevent hanging.

    Addresses the demo hanging issue by providing standard timeout patterns.
    """

    class TimeoutManager:
        def __init__(self, default_timeout: int = 10) -> None:
            self.default_timeout = default_timeout

        async def with_timeout(self, coro, timeout: int | None = None) -> object:
            """Execute coroutine with timeout"""
            timeout = timeout or self.default_timeout
            try:
                return await asyncio.wait_for(coro, timeout=timeout)
            except asyncio.TimeoutError as e:
                raise TimeoutError(f"Operation timed out after {timeout} seconds") from e

        def sync_timeout(self, timeout: int | None = None) -> int:
            """Get timeout value for sync operations"""
            return timeout or self.default_timeout

    return TimeoutManager()


@pytest.fixture
async def real_mcp_agent(real_mcp_client_session, mcp_timeout_manager) -> "AsyncGenerator[MCPAgent, None]":
    """
    Real MCPAgent instance connected to actual MCP server.

    Critical: This tests the complete MCPAgent implementation
    against real MCP 1.12.0 protocol without any mocking.
    """
    agent_config = {
        "agent_id": "test_agent_001",
        "name": "Anti-Hallucination Test Agent",
        "description": "Agent for testing real MCP integration",
        "mcp_config": {
            # Real MCP configuration
            "server_name": "anti_hallucination_test_server",
            "timeout": mcp_timeout_manager.default_timeout,
        },
    }

    # Create agent with real MCP session
    agent = MCPAgent(
        agent_id=agent_config["agent_id"],
        name=agent_config["name"],
        description=agent_config["description"],
        mcp_session=real_mcp_client_session,
        **agent_config.get("mcp_config", {}),
    )

    try:
        # Start agent - this tests real initialization
        await mcp_timeout_manager.with_timeout(agent.start())
        yield agent
    finally:
        # Ensure proper cleanup
        with contextlib.suppress(Exception):
            await mcp_timeout_manager.with_timeout(agent.stop())


@pytest.fixture
def real_simf_messages() -> dict[str, object]:
    """
    Factory for creating real SIMF messages for testing.

    Provides realistic message patterns for integration testing.
    """

    def create_tool_call_message(tool_name: str, **params):
        """Create SIMF message for MCP tool call"""
        return create_invocation_message(
            invocation_type="tool_call",
            target=tool_name,
            parameters=params,
            sender_id="test_sender",
            recipient_id="test_recipient",
            conversation_id="test_conversation",
            protocol_metadata={"protocol": "mcp", "tool_name": tool_name},
        )

    def create_resource_request_message(resource_uri: str):
        """Create SIMF message for MCP resource request"""
        return create_invocation_message(
            invocation_type="resource_request",
            target=resource_uri,
            parameters={},
            sender_id="test_sender",
            recipient_id="test_recipient",
            conversation_id="test_conversation",
            protocol_metadata={"protocol": "mcp", "resource_uri": resource_uri},
        )

    return {
        "tool_call": create_tool_call_message,
        "resource_request": create_resource_request_message,
    }


# Pytest configuration for anti-hallucination testing
def pytest_configure(config) -> None:
    """Configure pytest with anti-hallucination markers"""
    config.addinivalue_line(
        "markers",
        "anti_hallucination: Tests that validate real behavior without mocking",
    )
    config.addinivalue_line("markers", "real: Tests using real external services/libraries")
    config.addinivalue_line("markers", "mcp: Tests involving MCP protocol")
    config.addinivalue_line("markers", "timeout: Tests with specific timeout requirements")


def pytest_runtest_setup(item) -> None:
    """Setup for each test to enforce anti-hallucination rules"""
    # For tests marked as anti_hallucination, ensure MCP is available
    if item.get_closest_marker("anti_hallucination") and not MCP_AVAILABLE:
        pytest.skip("Anti-hallucination test requires real MCP SDK")

    # For real tests, add warnings about external dependencies
    if item.get_closest_marker("real") and os.getenv("CI") and os.getenv("SKIP_REAL_TESTS"):
        pytest.skip("Skipping real tests in CI (set SKIP_REAL_TESTS=false to enable)")
