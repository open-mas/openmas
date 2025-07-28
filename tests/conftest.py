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
from openmas.agent.base_agent import Agent, AgentConfig
from openmas.agent.communicator import DefaultCommunicator
from openmas.agent.reasoning.simple_reasoning import SimpleReasoningEngine
from openmas.core.simf import (
    MessageType,
    SIMFMessage,
    create_invocation_message,
    create_invocation_result_message,
    create_text_message,
)
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.test_supervisor import TestSupervisor, supervised_agent_test, supervised_multi_agent_test


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


@pytest.fixture
async def test_supervisor() -> "AsyncGenerator[TestSupervisor, None]":
    """
    TestSupervisor fixture for async test coordination.
    
    Provides sophisticated async lifecycle management, event-based coordination,
    timeout management, and resource cleanup for reliable agent testing.
    """
    import inspect
    
    # Get the test name from the calling test function
    frame = inspect.currentframe()
    test_name = "unknown_test"
    try:
        # Walk up the stack to find the test function
        while frame:
            if frame.f_code.co_name.startswith("test_"):
                test_name = frame.f_code.co_name
                break
            frame = frame.f_back
    finally:
        del frame
    
    async with TestSupervisor(test_name, default_timeout=30.0) as supervisor:
        yield supervisor


@pytest.fixture
async def basic_agent_factory() -> "Callable[[], Agent]":
    """
    Factory for creating basic agents with Body-Brain separation.
    
    Returns a factory function that creates properly configured agents
    with communicator and reasoning engine components.
    """
    def create_agent() -> Agent:
        # Generate unique agent ID
        agent_id = f"test_agent_{int(time.time() * 1000000) % 1000000}"
        
        # Create communicator (body) with agent_id
        communicator = DefaultCommunicator(agent_id=agent_id)
        
        # Create reasoning engine (brain)
        reasoning_engine = SimpleReasoningEngine()
        
        # Create agent with Body-Brain separation
        agent_config = AgentConfig(
            agent_id=agent_id,
            name="Test Agent",
            capabilities=["test_capability"],
            metadata={"description": "Agent for testing"}
        )
        
        return Agent(
            config=agent_config,
            communicator=communicator,
            reasoning_engine=reasoning_engine
        )
    
    return create_agent


@pytest.fixture
async def supervised_agent(test_supervisor: TestSupervisor, basic_agent_factory) -> "AsyncGenerator[Agent, None]":
    """
    Supervised agent fixture with automatic lifecycle management.
    
    Creates an agent using TestSupervisor for proper async resource cleanup.
    """
    agent = basic_agent_factory()
    
    async with test_supervisor.agent_lifecycle(agent) as managed_agent:
        yield managed_agent


@pytest.fixture
async def multi_agent_factory(basic_agent_factory) -> "Callable[[int], Dict[str, Callable[[], Agent]]]":
    """
    Factory for creating multiple agent factories for multi-agent tests.
    
    Args:
        count: Number of agent factories to create
    
    Returns:
        Dictionary mapping agent IDs to agent factory functions
    """
    def create_multi_agent_factories(count: int) -> "Dict[str, Callable[[], Agent]]":
        factories = {}
        for i in range(count):
            agent_id = f"agent_{i}"
            factories[agent_id] = basic_agent_factory
        return factories
    
    return create_multi_agent_factories


# Enhanced timeout management with TestSupervisor integration
@pytest.fixture
def enhanced_timeout_manager(mcp_timeout_manager):
    """
    Enhanced timeout manager with TestSupervisor coordination.
    
    Extends the existing MCP timeout manager with TestSupervisor event coordination.
    """
    class EnhancedTimeoutManager:
        def __init__(self, base_manager):
            self.base_manager = base_manager
            self.default_timeout = base_manager.default_timeout
        
        async def with_timeout(self, coro, timeout=None):
            """Execute coroutine with timeout and TestSupervisor coordination."""
            return await self.base_manager.with_timeout(coro, timeout)
        
        def sync_timeout(self, timeout=None):
            """Get timeout value for sync operations."""
            return self.base_manager.sync_timeout(timeout)
        
        async def supervised_timeout(self, supervisor: TestSupervisor, coro, timeout=None, event_name=None):
            """Execute coroutine with timeout and emit TestSupervisor events."""
            if event_name:
                await supervisor._emit_event(f"{event_name}_started")
            
            try:
                result = await self.with_timeout(coro, timeout)
                if event_name:
                    await supervisor._emit_event(f"{event_name}_completed", {"result": str(result)})
                return result
            except Exception as e:
                if event_name:
                    await supervisor._emit_event(f"{event_name}_failed", {"error": str(e)})
                raise
    
    return EnhancedTimeoutManager(mcp_timeout_manager)


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


@pytest.fixture(scope="session", autouse=True)
def configure_asyncio_for_testing():
    """Configure asyncio settings for reliable testing."""
    # Set asyncio debug mode for better error reporting in tests
    if not os.getenv("PYTEST_DISABLE_ASYNCIO_DEBUG"):
        asyncio.get_event_loop().set_debug(True)
    
    # Configure asyncio policy for consistent behavior
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        # On Windows, use selector event loop for better compatibility
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Pytest hooks for TestSupervisor integration
def pytest_runtest_teardown(item, nextitem):
    """Teardown hook to ensure proper async cleanup."""
    # Force garbage collection to clean up any remaining async resources
    import gc
    gc.collect()
    
    # Check for any remaining tasks and warn if found
    try:
        loop = asyncio.get_running_loop()
        pending_tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
        if pending_tasks:
            import warnings
            warnings.warn(
                f"Test {item.name} left {len(pending_tasks)} pending async tasks. "
                f"This may indicate improper resource cleanup.",
                RuntimeWarning
            )
    except RuntimeError:
        # No running loop, which is fine
        pass
