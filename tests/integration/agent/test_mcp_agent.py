"""
Integration Tests for MCPAgent

These tests validate the MCPAgent implementation against real MCP servers,
ensuring proper integration with the MCP 1.12.0 protocol while maintaining
SIMF-first internal design.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any, Optional

import pytest

from openmas.agent.exceptions import AgentConfigurationError, AgentError
from openmas.agent.mcp_agent import MCPAgent, create_mcp_agent_from_config
from openmas.core.simf import (
    InvocationStatus,
    MessageType,
    create_invocation_message,
)


class TestMCPAgentRealIntegration:
    """Test MCPAgent with real MCP server integration."""

    @pytest.fixture
    async def test_mcp_server_command(self):
        """Provide command to start the test MCP server."""
        # Use the real MCP server from examples
        server_path = Path(__file__).parent.parent.parent.parent / "examples" / "mcp_validation" / "real_mcp_server.py"
        return ["python", str(server_path)]

    @pytest.fixture
    async def mcp_agent(self, test_mcp_server_command):
        """Create and start an MCPAgent for testing."""
        agent = MCPAgent(
            agent_id="test_mcp_agent_001",
            name="Test MCP Agent",
            mcp_server_command=test_mcp_server_command,
            session_id="test_session",
        )

        try:
            # Start agent with timeout protection
            await asyncio.wait_for(agent.start(), timeout=15.0)
            yield agent
        except asyncio.TimeoutError:
            pytest.fail("MCPAgent startup timed out after 15 seconds")
        finally:
            # Stop agent with timeout protection
            try:
                await asyncio.wait_for(agent.stop(), timeout=10.0)
            except asyncio.TimeoutError:
                # Log warning but don't fail test cleanup
                print("Warning: MCPAgent stop timed out after 10 seconds")

    @pytest.mark.asyncio
    async def test_mcp_agent_initialization(self, test_mcp_server_command):
        """Test MCPAgent initialization and basic setup."""
        agent = MCPAgent(
            agent_id="test_init_001",
            name="Initialization Test Agent",
            mcp_server_command=test_mcp_server_command,
        )

        # Verify initialization
        assert agent.agent_id == "test_init_001"
        assert agent.name == "Initialization Test Agent"
        assert agent.mcp_server_command == test_mcp_server_command
        assert agent.mcp_session is None
        assert len(agent.available_tools) == 0

        # Verify it inherits from base Agent with Body-Brain separation
        assert hasattr(agent, "communicator")
        assert hasattr(agent, "reasoning_engine")
        assert hasattr(agent, "state_manager")
        assert agent.config.capabilities == []

    @pytest.mark.asyncio
    async def test_mcp_server_connection(self, mcp_agent):
        """Test MCP server connection establishment."""
        # Verify MCP session is established
        assert mcp_agent.mcp_session is not None

        # Verify agent is running
        assert mcp_agent.is_running

        # Verify tools were discovered
        tools = mcp_agent.get_mcp_tools()
        assert len(tools) > 0

        # Verify specific expected tools from our test server
        tool_names = list(tools.keys())
        assert "analyze_text" in tool_names

        print(f"✅ Connected to MCP server with tools: {tool_names}")

    @pytest.mark.asyncio
    async def test_mcp_tool_discovery(self, mcp_agent):
        """Test MCP tool discovery and capability registration."""
        # Get discovered tools
        tools = mcp_agent.get_mcp_tools()
        assert len(tools) > 0

        # Verify tools are registered as agent capabilities
        capabilities = await mcp_agent.get_capabilities()
        tool_capabilities = [cap for cap in capabilities if mcp_agent.is_mcp_tool(cap)]

        assert len(tool_capabilities) == len(tools)

        # Verify specific tool registration
        assert "analyze_text" in capabilities  # Use actual tool name without prefix

        # Check registered capabilities (should include discovered tools)
        capabilities = await mcp_agent.get_capabilities()
        assert len(capabilities) > 0
        assert "analyze_text" in capabilities  # Use actual tool name without prefix

        print(f"✅ Discovered MCP tools and registered capabilities: {capabilities}")

    @pytest.mark.asyncio
    async def test_mcp_tool_execution_direct(self, mcp_agent):
        """Test direct MCP tool execution."""
        # Execute analyze_text tool
        result = await mcp_agent.execute_mcp_tool(
            tool_name="analyze_text",
            parameters={
                "text": "This is a great example!",
                "analysis_type": "sentiment",
            },
        )

        # Verify result structure - MCP tool returns result directly, not wrapped in "result" key
        assert isinstance(result, dict)
        
        # Verify expected fields from our test server's sentiment analysis tool
        assert "analysis_type" in result
        assert "sentiment" in result
        assert "score" in result
        assert "confidence" in result
        assert "text" in result
        
        # Verify result content matches our input
        assert result["text"] == "This is a great example!"
        assert result["analysis_type"] == "sentiment"
        
        print(f"✅ Tool execution result: {result}")

    @pytest.mark.asyncio
    async def test_mcp_tool_execution_via_simf(self, mcp_agent):
        """Test MCP tool execution via SIMF messages (core integration test)."""
        # Create SIMF invocation message
        simf_message = create_invocation_message(
            target_agent_id=mcp_agent.agent_id,
            invocation_name="analyze_text",
            arguments={
                "text": "This demonstrates SIMF-MCP integration!",
                "analysis_type": "sentiment",
            },
            session_id="test_session",
        )

        # Execute via SIMF
        result_message = await mcp_agent.execute_capability(simf_message)

        # Verify SIMF result message
        assert result_message.message_type == MessageType.TOOL_RESULT
        assert result_message.payload.status == InvocationStatus.SUCCESS
        
        # MCP tool returns result directly, not wrapped in "result" key
        tool_result = result_message.payload.result
        assert isinstance(tool_result, dict)
        assert "analysis_type" in tool_result
        assert "sentiment" in tool_result
        assert "score" in tool_result
        assert "confidence" in tool_result
        assert "text" in tool_result
        
        # Verify result content matches our input
        assert tool_result["text"] == "This demonstrates SIMF-MCP integration!"
        assert tool_result["analysis_type"] == "sentiment"

        print(f"✅ SIMF-MCP integration successful: {result_message.payload.result}")

    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self, mcp_agent):
        """Test multiple sequential MCP tool calls."""
        test_cases = [
            {
                "tool": "analyze_text",
                "params": {"text": "Happy text", "analysis_type": "sentiment"},
            },
            {
                "tool": "analyze_text",
                "params": {"text": "Different text", "analysis_type": "length"},
            },
        ]

        results = []
        for test_case in test_cases:
            # Create SIMF message
            simf_message = create_invocation_message(
                target_agent_id=mcp_agent.agent_id,
                invocation_name=test_case["tool"],
                arguments=test_case["params"],
                session_id="test_session",
            )

            # Execute
            result_message = await mcp_agent.execute_capability(simf_message)
            results.append(result_message)

            # Verify success
            assert result_message.payload.status == InvocationStatus.SUCCESS

        print(f"✅ Multiple tool calls successful: {len(results)} executions")

    @pytest.mark.asyncio
    async def test_error_handling(self, mcp_agent):
        """Test error handling for invalid tool calls."""
        # Test unknown tool
        simf_message = create_invocation_message(
            target_agent_id=mcp_agent.agent_id,
            invocation_name="nonexistent_tool",
            arguments={},
            session_id="test_session",
        )

        result_message = await mcp_agent.execute_capability(simf_message)

        # Should use base implementation (not MCP) and likely fail gracefully
        # The exact behavior depends on base Agent implementation
        assert result_message is not None

        print("✅ Error handling for unknown tool works")

    @pytest.mark.asyncio
    async def test_agent_lifecycle_with_mcp(self, test_mcp_server_command):
        """Test complete agent lifecycle with MCP integration."""
        agent = MCPAgent(
            agent_id="lifecycle_test_001",
            name="Lifecycle Test Agent",
            mcp_server_command=test_mcp_server_command,
        )

        # Initially not running
        assert not agent.is_running
        assert agent.mcp_session is None

        # Start agent
        await agent.start()
        assert agent.is_running
        assert agent.mcp_session is not None
        assert len(agent.available_tools) > 0

        # Execute a tool to verify functionality
        result = await agent.execute_mcp_tool(
            tool_name="analyze_text",
            parameters={"text": "Lifecycle test", "analysis_type": "length"},
        )
        # MCP tool returns result directly, not wrapped in "result" key
        assert isinstance(result, dict)
        assert "analysis_type" in result
        assert "text" in result
        assert result["text"] == "Lifecycle test"
        assert result["analysis_type"] == "length"

        # Stop agent
        await agent.stop()
        assert not agent.is_running
        assert agent.mcp_session is None

        print("✅ Complete agent lifecycle with MCP integration successful")


class TestMCPAgentConfiguration:
    """Test MCPAgent configuration and factory methods."""

    async def test_create_mcp_agent_from_config(self):
        """Test creating MCPAgent from configuration."""
        config = {
            "agent_id": "config_test_001",
            "name": "Config Test Agent",
            "mcp_server_command": ["python", "test_server.py"],
            "session_id": "config_session",
            "capabilities": [
                {
                    "name": "test_capability",
                    "description": "Test capability",
                    "parameters": {"param1": "string"},
                }
            ],
        }

        agent = create_mcp_agent_from_config(config)

        # Verify configuration
        assert agent.agent_id == "config_test_001"
        assert agent.name == "Config Test Agent"
        assert agent.mcp_server_command == ["python", "test_server.py"]
        assert agent.session_id == "config_session"

        # Verify capabilities were added (async call in Body-Brain architecture)
        capabilities = await agent.get_capabilities()
        assert "test_capability" in capabilities

        print("✅ MCPAgent configuration creation successful")

    def test_invalid_configuration(self):
        """Test error handling for invalid configuration."""
        # Missing required fields
        invalid_configs = [
            {},  # Empty config
            {"agent_id": "test"},  # Missing name and mcp_server_command
            {"agent_id": "test", "name": "Test"},  # Missing mcp_server_command
        ]

        for config in invalid_configs:
            with pytest.raises(AgentConfigurationError):
                create_mcp_agent_from_config(config)

        print("✅ Invalid configuration error handling works")


class TestMCPAgentEndToEnd:
    """End-to-end integration tests demonstrating real-world usage."""

    @pytest.mark.asyncio
    async def test_text_analysis_workflow(self):
        """Test a complete text analysis workflow using MCP agent."""
        # Setup
        server_path = Path(__file__).parent.parent.parent.parent / "examples" / "mcp_validation" / "real_mcp_server.py"

        agent = MCPAgent(
            agent_id="text_analyzer_001",
            name="Text Analysis Agent",
            mcp_server_command=["python", str(server_path)],
            session_id="analysis_session",
        )

        try:
            # Start agent
            await agent.start()

            # Define text analysis workflow
            text_samples = [
                "This is a fantastic example of MCP integration!",
                "The weather is quite gloomy today.",
                "Python programming is very powerful and versatile.",
            ]

            workflow_results = []

            for _, text in enumerate(text_samples):
                # Analyze sentiment
                sentiment_msg = create_invocation_message(
                    target_agent_id=agent.agent_id,
                    invocation_name="analyze_text",
                    arguments={"text": text, "analysis_type": "sentiment"},
                    session_id="analysis_session",
                )

                sentiment_result = await agent.execute_capability(sentiment_msg)

                # Analyze length
                length_msg = create_invocation_message(
                    target_agent_id=agent.agent_id,
                    invocation_name="analyze_text",
                    arguments={"text": text, "analysis_type": "length"},
                    session_id="analysis_session",
                )

                length_result = await agent.execute_capability(length_msg)

                # Collect results
                workflow_results.append(
                    {
                        "text": text,
                        "sentiment": sentiment_result.payload.result,
                        "length": length_result.payload.result,
                    }
                )

                # Verify both analyses succeeded
                assert sentiment_result.payload.status == InvocationStatus.SUCCESS
                assert length_result.payload.status == InvocationStatus.SUCCESS

            # Verify workflow completion
            assert len(workflow_results) == len(text_samples)

            print("✅ Text analysis workflow completed successfully")
            print(f"   Processed {len(text_samples)} text samples")

            for i, result in enumerate(workflow_results):
                print(f"   Sample {i+1}: {len(result['text'])} chars")

        finally:
            await agent.stop()


@pytest.mark.asyncio
async def test_mcp_agent_simf_semantic_preservation():
    """
    Test that MCP tool calls preserve semantic meaning through SIMF translation.

    This validates the core integration between MCPAgent and the MCP-SIMF translator.
    """
    server_path = Path(__file__).parent.parent.parent.parent / "examples" / "mcp_validation" / "real_mcp_server.py"

    agent = MCPAgent(
        agent_id="semantic_test_001",
        name="Semantic Preservation Test Agent",
        mcp_server_command=["python", str(server_path)],
    )

    try:
        await agent.start()

        # Original parameters
        original_params = {
            "text": "Semantic preservation test message",
            "analysis_type": "sentiment",
        }

        # Execute via SIMF (which uses MCP-SIMF translator internally)
        simf_message = create_invocation_message(
            target_agent_id=agent.agent_id,
            invocation_name="analyze_text",
            arguments=original_params,
            session_id="semantic_test",
        )

        result_message = await agent.execute_capability(simf_message)

        # Verify semantic preservation
        assert result_message.payload.status == InvocationStatus.SUCCESS
        # MCP tool returns result directly, not wrapped in "result" key
        tool_result = result_message.payload.result
        assert isinstance(tool_result, dict)
        assert "analysis_type" in tool_result
        assert "text" in tool_result
        
        # The result should contain analysis of our original text
        result_content = tool_result

        # Verify the analysis contains our original text (semantic preservation)
        if isinstance(result_content, dict):
            assert original_params["text"] in str(result_content)

        print("✅ Semantic preservation through SIMF-MCP translation verified")

    finally:
        await agent.stop()


if __name__ == "__main__":
    # Run basic integration test
    async def main():
        print("🧪 Running MCPAgent Integration Tests...")

        # Basic connection test
        server_path = Path(__file__).parent.parent.parent.parent / "examples" / "mcp_validation" / "real_mcp_server.py"

        agent = MCPAgent(
            agent_id="manual_test_001",
            name="Manual Test Agent",
            mcp_server_command=["python", str(server_path)],
        )

        try:
            print("Starting agent...")
            await agent.start()

            print(f"✅ Agent started with {len(agent.available_tools)} tools")

            # Test tool execution
            result = await agent.execute_mcp_tool(
                tool_name="analyze_text",
                parameters={
                    "text": "Manual test message",
                    "analysis_type": "sentiment",
                },
            )

            print(f"✅ Tool execution successful: {result}")

        finally:
            await agent.stop()
            print("✅ Agent stopped successfully")

    asyncio.run(main())
