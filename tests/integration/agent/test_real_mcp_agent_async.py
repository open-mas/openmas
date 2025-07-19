"""
Real MCP Agent Integration Tests

Anti-Hallucination Testing: Validates MCPAgent against REAL MCP 1.12.0 behavior.

CRITICAL: These tests use actual MCP servers and clients - no mocking allowed
for critical protocol paths. This prevents the 0.2.0 problem where 1000+ tests
passed but none worked with real libraries.

Tests include proper async patterns and timeout handling to prevent demo hanging.
"""

import pytest
import asyncio
from typing import List

from openmas.agent.mcp_agent import MCPAgent
from openmas.core.simf import (
    SIMFMessage, 
    MessageType,
    create_invocation_message,
    create_text_message
)


@pytest.mark.anti_hallucination
@pytest.mark.real
@pytest.mark.mcp
@pytest.mark.asyncio
async def test_mcp_agent_real_initialization(real_mcp_agent, anti_hallucination_validator):
    """
    Test MCPAgent initialization against real MCP server.
    
    Critical: Validates actual MCP 1.12.0 initialization without mocking.
    """
    # Validate no critical MCP modules are mocked
    anti_hallucination_validator([
        "mcp.client.session",
        "mcp.server.fastmcp",
        "mcp.client.stdio"
    ])
    
    # Test real agent initialization
    assert real_mcp_agent.agent_id == "test_agent_001"
    assert real_mcp_agent.name == "Anti-Hallucination Test Agent"
    assert real_mcp_agent.is_running is True
    
    # Verify real MCP session is active
    assert real_mcp_agent.mcp_session is not None
    assert hasattr(real_mcp_agent.mcp_session, "call_tool")
    assert hasattr(real_mcp_agent.mcp_session, "read_resource")


@pytest.mark.anti_hallucination
@pytest.mark.real
@pytest.mark.mcp
@pytest.mark.asyncio
@pytest.mark.timeout
async def test_mcp_agent_real_tool_execution(real_mcp_agent, real_simf_messages, mcp_timeout_manager):
    """
    Test MCPAgent tool execution against real MCP server with timeout handling.
    
    Critical: This validates the complete tool execution pipeline:
    SIMF -> MCP translation -> Real MCP execution -> MCP -> SIMF translation
    """
    # Create real SIMF tool call message
    tool_message = real_simf_messages["tool_call"]("test_add", a=5, b=3)
    
    # Execute with timeout to prevent hanging
    response = await mcp_timeout_manager.with_timeout(
        real_mcp_agent.process_message(tool_message),
        timeout=15
    )
    
    # Validate real execution results
    assert response is not None
    assert isinstance(response, SIMFMessage)
    assert response.content.type == "tool_response"
    
    # Verify actual computation occurred (5 + 3 = 8)
    assert "8" in response.content.text or response.content.metadata.get("result") == 8


@pytest.mark.anti_hallucination
@pytest.mark.real
@pytest.mark.mcp
@pytest.mark.asyncio
@pytest.mark.timeout
async def test_mcp_agent_real_resource_access(real_mcp_agent, real_simf_messages, mcp_timeout_manager):
    """
    Test MCPAgent resource access against real MCP server.
    
    Critical: Validates complete resource access pipeline without mocking.
    """
    # Create real SIMF resource request
    resource_message = real_simf_messages["resource_request"]("test://resource/123")
    
    # Execute with timeout
    response = await mcp_timeout_manager.with_timeout(
        real_mcp_agent.process_message(resource_message),
        timeout=10
    )
    
    # Validate real resource access
    assert response is not None
    assert isinstance(response, SIMFMessage)
    assert response.content.type == "resource_response"
    assert "Real resource content for 123" in response.content.text


@pytest.mark.anti_hallucination
@pytest.mark.real
@pytest.mark.mcp
@pytest.mark.asyncio
async def test_mcp_agent_async_operation_patterns(real_mcp_agent, real_simf_messages, mcp_timeout_manager):
    """
    Test MCPAgent async operation patterns to prevent hanging.
    
    Critical: This validates proper async handling that prevents the demo hanging issue.
    """
    # Test async operation that could cause hanging
    async_message = real_simf_messages["tool_call"]("test_async_operation")
    
    # Execute multiple async operations concurrently
    tasks = [
        mcp_timeout_manager.with_timeout(real_mcp_agent.process_message(async_message), 10)
        for _ in range(3)
    ]
    
    # Wait for all to complete without hanging
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Validate all completed successfully
    assert len(responses) == 3
    for response in responses:
        assert not isinstance(response, Exception)
        assert isinstance(response, SIMFMessage)
        assert "Async operation completed" in response.content.text


@pytest.mark.anti_hallucination
@pytest.mark.real
@pytest.mark.mcp
@pytest.mark.asyncio
@pytest.mark.timeout
async def test_mcp_agent_error_handling_real(real_mcp_agent, mcp_timeout_manager):
    """
    Test MCPAgent error handling with real MCP errors.
    
    Critical: Validates error handling against actual MCP protocol errors.
    """
    # Create invalid tool call that will generate real MCP error
    invalid_message = create_invocation_message(
        invocation_type="tool_call",
        target="non_existent_tool",
        parameters={},
        sender_id="test_sender",
        recipient_id="test_recipient",
        conversation_id="test_conversation",
        protocol_metadata={"protocol": "mcp", "tool_name": "non_existent_tool"}
    )
    
    # Execute with timeout
    response = await mcp_timeout_manager.with_timeout(
        real_mcp_agent.process_message(invalid_message),
        timeout=10
    )
    
    # Validate proper error handling
    assert response is not None
    assert isinstance(response, SIMFMessage)
    assert response.content.type == "error"
    # Should contain actual MCP error information
    assert any(keyword in response.content.text.lower() for keyword in [
        "tool", "not found", "unknown", "error", "invalid"
    ])


@pytest.mark.anti_hallucination
@pytest.mark.real
@pytest.mark.mcp
@pytest.mark.asyncio
async def test_mcp_agent_multiple_tool_sequence(real_mcp_agent, real_simf_messages, mcp_timeout_manager):
    """
    Test MCPAgent handling multiple tool calls in sequence.
    
    Critical: Validates state management across multiple real MCP operations.
    """
    # Execute sequence of real tool calls
    tool_sequence = [
        ("test_add", {"a": 1, "b": 2}),
        ("test_echo", {"message": "Hello MCP"}),
        ("test_add", {"a": 10, "b": 20}),
        ("test_echo", {"message": "Sequence complete"})
    ]
    
    responses = []
    for tool_name, params in tool_sequence:
        message = real_simf_messages["tool_call"](tool_name, **params)
        response = await mcp_timeout_manager.with_timeout(
            real_mcp_agent.process_message(message),
            timeout=10
        )
        responses.append(response)
    
    # Validate all operations completed successfully
    assert len(responses) == 4
    
    # Validate specific results
    assert "3" in responses[0].content.text  # 1 + 2 = 3
    assert "Echo: Hello MCP" in responses[1].content.text
    assert "30" in responses[2].content.text  # 10 + 20 = 30
    assert "Echo: Sequence complete" in responses[3].content.text


@pytest.mark.anti_hallucination
@pytest.mark.real
@pytest.mark.mcp
@pytest.mark.asyncio
async def test_mcp_agent_concurrent_operations(real_mcp_agent, real_simf_messages, mcp_timeout_manager):
    """
    Test MCPAgent handling concurrent operations without conflicts.
    
    Critical: Validates thread safety and proper async handling.
    """
    # Create concurrent tool calls
    concurrent_calls = [
        real_simf_messages["tool_call"]("test_add", a=i, b=i+1)
        for i in range(5)
    ]
    
    # Execute all concurrently
    tasks = [
        mcp_timeout_manager.with_timeout(real_mcp_agent.process_message(msg), 15)
        for msg in concurrent_calls
    ]
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Validate all completed without exceptions
    assert len(responses) == 5
    for i, response in enumerate(responses):
        assert not isinstance(response, Exception)
        assert isinstance(response, SIMFMessage)
        # Validate correct computation (i + (i+1) = 2i+1)
        expected_result = str(2 * i + 1)
        assert expected_result in response.content.text


@pytest.mark.anti_hallucination
@pytest.mark.real
@pytest.mark.mcp
@pytest.mark.asyncio
async def test_mcp_agent_lifecycle_management(mcp_timeout_manager, real_mcp_client_session):
    """
    Test complete MCPAgent lifecycle with proper cleanup.
    
    Critical: Validates proper start/stop patterns that prevent resource leaks.
    """
    # Create agent manually to test lifecycle
    agent = MCPAgent(
        agent_id="lifecycle_test_001",
        name="Lifecycle Test Agent",
        description="Testing lifecycle management",
        mcp_session=real_mcp_client_session
    )
    
    # Test start
    await mcp_timeout_manager.with_timeout(agent.start(), 10)
    assert agent.is_running is True
    
    # Test operation
    message = create_invocation_message(
        invocation_type="tool_call",
        target="test_add",
        parameters={"a": 5, "b": 5},
        sender_id="test_sender",
        recipient_id="test_recipient",
        conversation_id="test_conversation",
        protocol_metadata={"protocol": "mcp", "tool_name": "test_add"}
    )
    
    response = await mcp_timeout_manager.with_timeout(
        agent.process_message(message),
        10
    )
    assert "10" in response.content.text
    
    # Test stop
    await mcp_timeout_manager.with_timeout(agent.stop(), 10)
    assert agent.is_running is False


@pytest.mark.anti_hallucination
@pytest.mark.real
@pytest.mark.mcp
def test_mcp_agent_no_critical_mocking(anti_hallucination_validator):
    """
    Ensure MCPAgent implementation doesn't mock critical MCP paths.
    
    Critical: This prevents the 0.2.0 problem where all tests passed
    but nothing worked with real libraries.
    """
    # Validate that critical MCP modules are not mocked
    critical_modules = [
        "mcp",
        "mcp.client",
        "mcp.client.session",
        "mcp.client.stdio",
        "mcp.server",
        "mcp.server.fastmcp",
        "mcp.server.stdio"
    ]
    
    anti_hallucination_validator(critical_modules)


@pytest.mark.anti_hallucination
@pytest.mark.real
@pytest.mark.mcp
@pytest.mark.asyncio
async def test_mcp_agent_timeout_prevention(mcp_timeout_manager, real_mcp_client_session):
    """
    Test timeout patterns that prevent the demo hanging issue.
    
    Critical: This validates the timeout handling that fixes the hanging demo.
    """
    agent = MCPAgent(
        agent_id="timeout_test_001",
        name="Timeout Test Agent",
        description="Testing timeout handling",
        mcp_session=real_mcp_client_session
    )
    
    try:
        # Test initialization with timeout
        await mcp_timeout_manager.with_timeout(agent.start(), 5)
        
        # Test that operations don't hang
        start_time = asyncio.get_event_loop().time()
        
        message = create_invocation_message(
            invocation_type="tool_call",
            target="test_async_operation",
            parameters={},
            sender_id="test_sender",
            recipient_id="test_recipient",
            conversation_id="test_conversation",
            protocol_metadata={"protocol": "mcp", "tool_name": "test_async_operation"}
        )
        
        response = await mcp_timeout_manager.with_timeout(
            agent.process_message(message),
            5
        )
        
        elapsed = asyncio.get_event_loop().time() - start_time
        
        # Validate operation completed quickly
        assert elapsed < 5
        assert response is not None
        assert "Async operation completed" in response.content.text
        
    finally:
        # Ensure cleanup
        try:
            await mcp_timeout_manager.with_timeout(agent.stop(), 5)
        except Exception:
            pass 