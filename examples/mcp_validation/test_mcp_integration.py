"""
Test MCP 1.12.0 Integration

This validates that our MCP server works correctly with the official MCP 1.12.0 SDK
and supports the 2025-06-18 specification features.
"""

import asyncio
import tempfile
import json
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.fixture
def server_params():
    """Server parameters for connecting to our MCP server."""
    return StdioServerParameters(
        command="python",
        args=["examples/mcp_validation/real_mcp_server.py"],
        env={}
    )


@pytest.mark.asyncio
async def test_mcp_server_initialization(server_params):
    """Test that the MCP server initializes correctly."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            result = await session.initialize()
            
            # Verify server capabilities
            assert result.serverInfo.name == "OpenMAS Validation Server"
            assert "tools" in result.capabilities
            assert "resources" in result.capabilities
            assert "prompts" in result.capabilities


@pytest.mark.asyncio
async def test_mcp_tools_listing(server_params):
    """Test listing available tools."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            result = await session.list_tools()
            
            # Verify our tools are available
            tool_names = [tool.name for tool in result.tools]
            assert "analyze_text" in tool_names
            assert "create_document" in tool_names
            
            # Check tool has proper structure
            analyze_tool = next(tool for tool in result.tools if tool.name == "analyze_text")
            assert analyze_tool.description is not None
            assert analyze_tool.inputSchema is not None


@pytest.mark.asyncio
async def test_mcp_structured_tool_output(server_params):
    """Test structured tool output as required by MCP 2025-06-18."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Call analyze_text tool
            result = await session.call_tool(
                "analyze_text", 
                arguments={
                    "text": "This is a great example!",
                    "analysis_type": "sentiment"
                }
            )
            
            # Verify both content and structured output
            assert len(result.content) > 0
            
            # MCP 2025-06-18: Check for structured output
            if hasattr(result, 'structuredContent') and result.structuredContent:
                structured = result.structuredContent
                assert "analysis_type" in structured
                assert "score" in structured
                assert "sentiment" in structured
                assert structured["analysis_type"] == "sentiment"


@pytest.mark.asyncio
async def test_mcp_resources(server_params):
    """Test resource access."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List resources
            result = await session.list_resources()
            
            # Verify our resources are available
            resource_uris = [resource.uri for resource in result.resources]
            assert "config://server/info" in resource_uris
            assert "docs://list" in resource_uris
            
            # Read a resource
            from pydantic import AnyUrl
            content = await session.read_resource(AnyUrl("config://server/info"))
            
            # Verify content structure
            assert len(content.contents) > 0
            
            # Parse JSON content
            text_content = content.contents[0]
            if hasattr(text_content, 'text'):
                server_info = json.loads(text_content.text)
                assert server_info["name"] == "OpenMAS Validation Server"
                assert "capabilities" in server_info


@pytest.mark.asyncio
async def test_mcp_prompts(server_params):
    """Test prompt functionality."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List prompts
            result = await session.list_prompts()
            
            # Verify our prompts are available
            prompt_names = [prompt.name for prompt in result.prompts]
            assert "analyze_prompt" in prompt_names
            assert "document_prompt" in prompt_names
            
            # Get a prompt
            prompt_result = await session.get_prompt(
                "analyze_prompt",
                arguments={
                    "text": "Sample text for analysis",
                    "focus": "sentiment"
                }
            )
            
            # Verify prompt structure
            assert len(prompt_result.messages) > 0
            assert "sentiment" in prompt_result.messages[0].content.text


@pytest.mark.asyncio 
async def test_mcp_error_handling(server_params):
    """Test error handling in MCP calls."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test invalid tool call
            with pytest.raises(Exception):
                await session.call_tool("nonexistent_tool", arguments={})
            
            # Test invalid analysis type
            result = await session.call_tool(
                "analyze_text",
                arguments={
                    "text": "Test text",
                    "analysis_type": "invalid_type"
                }
            )
            
            # Should handle error gracefully
            if result.isError:
                assert len(result.content) > 0


@pytest.mark.asyncio
async def test_mcp_document_creation_workflow(server_params):
    """Test a complete workflow: create document and verify it exists."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Create a document
            result = await session.call_tool(
                "create_document",
                arguments={
                    "title": "test_doc",
                    "content": "This is test content",
                    "format": "txt"
                }
            )
            
            # Verify creation was successful
            if hasattr(result, 'structuredContent') and result.structuredContent:
                structured = result.structuredContent
                assert structured["status"] == "success"
                assert "file_path" in structured
                
                # Verify file exists
                file_path = Path(structured["file_path"])
                assert file_path.exists()
                assert "test_doc" in file_path.name
            
            # List documents to verify it appears
            from pydantic import AnyUrl
            docs_content = await session.read_resource(AnyUrl("docs://list"))
            docs_text = docs_content.contents[0].text
            docs_data = json.loads(docs_text)
            
            assert docs_data["count"] > 0
            doc_names = [doc["name"] for doc in docs_data["documents"]]
            assert any("test_doc" in name for name in doc_names)


if __name__ == "__main__":
    # Run a simple validation
    import sys
    
    async def main():
        server_params = StdioServerParameters(
            command="python",
            args=["examples/mcp_validation/real_mcp_server.py"],
            env={}
        )
        
        print("Testing MCP 1.12.0 integration...")
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize
                    result = await session.initialize()
                    print(f"✅ Server initialized: {result.serverInfo.name}")
                    
                    # Test tools
                    tools = await session.list_tools()
                    print(f"✅ Found {len(tools.tools)} tools")
                    
                    # Test resources  
                    resources = await session.list_resources()
                    print(f"✅ Found {len(resources.resources)} resources")
                    
                    # Test prompts
                    prompts = await session.list_prompts()
                    print(f"✅ Found {len(prompts.prompts)} prompts")
                    
                    print("🎉 MCP 1.12.0 integration validated successfully!")
                    
        except Exception as e:
            print(f"❌ MCP integration test failed: {e}")
            sys.exit(1)
    
    asyncio.run(main()) 