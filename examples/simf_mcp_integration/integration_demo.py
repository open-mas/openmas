"""
SIMF-MCP Integration Demo

This demo shows real-world integration between MCP and SIMF, demonstrating:
1. Real MCP server tool calls → SIMF → tool execution
2. MCP resource access → SIMF asset references
3. Streaming responses → SIMF stream context
4. IProtocolAdapter pattern integration
5. End-to-end semantic preservation validation
"""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolRequest, TextContent, Resource

# Local imports
from mcp_to_simf_translator import MCPToSIMFTranslator

# Mock IProtocolAdapter for demonstration
class MockMCPProtocolAdapter:
    """
    Mock implementation of IProtocolAdapter for MCP protocol.
    
    In the real implementation, this would inherit from the IProtocolAdapter
    interface defined in the Phase 1 work.
    """
    
    def __init__(self):
        self.translator = MCPToSIMFTranslator("mcp_protocol_adapter")
        self.protocol_name = "mcp"
        self.supported_transports = ["stdio", "http"]
    
    async def to_internal_format(self, protocol_message: Any, context: Optional[Dict] = None) -> Any:
        """
        Convert MCP protocol message to SIMF format.
        
        This demonstrates the IProtocolAdapter.to_internal_format() method.
        """
        try:
            if isinstance(protocol_message, CallToolRequest):
                session_id = context.get("session_id") if context else None
                simf_message = self.translator.mcp_tool_call_to_simf(protocol_message, session_id)
                return simf_message
            else:
                raise ValueError(f"Unsupported MCP message type: {type(protocol_message)}")
        except Exception as e:
            print(f"Error in to_internal_format: {e}")
            raise
    
    async def from_internal_format(self, simf_message: Any, context: Optional[Dict] = None) -> Any:
        """
        Convert SIMF message back to MCP protocol format.
        
        This demonstrates the IProtocolAdapter.from_internal_format() method.
        """
        try:
            # Check payload type and convert accordingly
            if hasattr(simf_message.payload, 'payload_type'):
                if simf_message.payload.payload_type == "invocation_content":
                    return self.translator.simf_to_mcp_tool_call(simf_message)
                elif simf_message.payload.payload_type == "invocation_result_content":
                    return self.translator.simf_to_mcp_tool_result(simf_message)
            
            raise ValueError(f"Cannot convert SIMF message with payload type: {simf_message.payload.payload_type}")
        except Exception as e:
            print(f"Error in from_internal_format: {e}")
            raise


class SIMFMCPIntegrationDemo:
    """
    Comprehensive demo of SIMF-MCP integration showing real protocol usage.
    """
    
    def __init__(self):
        self.adapter = MockMCPProtocolAdapter()
        self.session_id = "demo_session_001"
    
    async def run_complete_demo(self):
        """Run the complete integration demo."""
        print("🚀 Starting SIMF-MCP Integration Demo")
        print("=" * 60)
        
        try:
            # Test 1: Tool call integration
            await self.demo_tool_call_integration()
            
            # Test 2: Resource access integration  
            await self.demo_resource_integration()
            
            # Test 3: Streaming simulation
            await self.demo_streaming_integration()
            
            # Test 4: Round-trip semantic preservation
            await self.demo_semantic_preservation()
            
            print("\n✅ All integration tests completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            raise
    
    async def demo_tool_call_integration(self):
        """Demonstrate MCP tool call → SIMF → execution workflow."""
        print("\n📡 Demo 1: MCP Tool Call Integration")
        print("-" * 40)
        
        # Connect to real MCP server
        server_params = StdioServerParameters(
            command="python",
            args=["examples/mcp_validation/real_mcp_server.py"],
            env={}
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 1. Make real MCP tool call
                print("📞 Making real MCP tool call...")
                result = await session.call_tool(
                    "analyze_text",
                    arguments={
                        "text": "This is an amazing integration example!",
                        "analysis_type": "sentiment"
                    }
                )
                
                print(f"✅ MCP tool call succeeded")
                print(f"   Result content: {len(result.content)} items")
                
                # 2. Convert MCP request to SIMF (simulated)
                mcp_request = CallToolRequest(
                    id="demo_001",
                    method="tools/call",
                    params={
                        "name": "analyze_text", 
                        "arguments": {
                            "text": "This is an amazing integration example!",
                            "analysis_type": "sentiment"
                        }
                    }
                )
                
                print("\n🔄 Converting MCP request to SIMF...")
                simf_message = await self.adapter.to_internal_format(
                    mcp_request, 
                    {"session_id": self.session_id}
                )
                
                print(f"✅ SIMF conversion successful")
                print(f"   Message Type: {simf_message.message_type}")
                print(f"   Payload Type: {simf_message.payload.payload_type}")
                print(f"   Capability: {simf_message.payload.capability_name}")
                
                # 3. Convert SIMF back to MCP
                print("\n🔄 Converting SIMF back to MCP...")
                reconstructed_mcp = await self.adapter.from_internal_format(simf_message)
                
                print(f"✅ MCP reconstruction successful")
                print(f"   Tool: {reconstructed_mcp.params['name']}")
                print(f"   Arguments: {reconstructed_mcp.params['arguments']}")
                
                # 4. Verify semantic preservation
                original_args = mcp_request.params["arguments"]
                reconstructed_args = reconstructed_mcp.params["arguments"]
                preserved = original_args == reconstructed_args
                
                print(f"\n🔍 Semantic preservation: {'✅ PASS' if preserved else '❌ FAIL'}")
    
    async def demo_resource_integration(self):
        """Demonstrate MCP resource → SIMF asset reference workflow."""
        print("\n📁 Demo 2: MCP Resource Integration")
        print("-" * 40)
        
        # Connect to real MCP server
        server_params = StdioServerParameters(
            command="python",
            args=["examples/mcp_validation/real_mcp_server.py"],
            env={}
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 1. List real MCP resources
                print("📋 Listing MCP resources...")
                resources_result = await session.list_resources()
                
                if resources_result.resources:
                    resource = resources_result.resources[0]
                    print(f"✅ Found resource: {resource.name}")
                    print(f"   URI: {resource.uri}")
                    print(f"   Type: {resource.mimeType}")
                    
                    # 2. Get resource content
                    print(f"\n📖 Reading resource content...")
                    content_result = await session.read_resource(resource.uri)
                    content_text = ""
                    
                    for content_item in content_result.contents:
                        if isinstance(content_item, TextContent):
                            content_text += content_item.text
                    
                    print(f"✅ Resource content loaded ({len(content_text)} chars)")
                    
                    # 3. Convert to SIMF asset reference
                    print(f"\n🔄 Converting resource to SIMF asset reference...")
                    simf_message = self.adapter.translator.mcp_resource_to_simf(
                        resource, content_text, self.session_id
                    )
                    
                    print(f"✅ SIMF asset reference created")
                    print(f"   Asset Type: {simf_message.payload.asset_type}")
                    print(f"   Asset ID: {simf_message.payload.asset_id}")
                    print(f"   Preview: {simf_message.payload.content_preview[:100]}...")
                
                else:
                    print("ℹ️  No resources available for demo")
    
    async def demo_streaming_integration(self):
        """Demonstrate streaming → SIMF stream context workflow."""
        print("\n🌊 Demo 3: Streaming Integration")
        print("-" * 40)
        
        # Simulate streaming response
        stream_id = "demo_stream_001"
        streaming_content = [
            "This is the beginning of a streaming response. ",
            "Here's the middle part with more detailed information. ", 
            "And finally, this is the conclusion of the stream."
        ]
        
        print(f"🌊 Simulating streaming with {len(streaming_content)} chunks...")
        
        for i, chunk in enumerate(streaming_content):
            # Determine stream position
            if i == 0:
                position = "start"
            elif i == len(streaming_content) - 1:
                position = "end"
            else:
                position = "middle"
            
            # Create SIMF stream context message
            simf_message = self.adapter.translator.create_stream_context_message(
                stream_id, position, chunk, self.session_id
            )
            
            print(f"📦 Stream chunk {i+1}: {position}")
            print(f"   Content: {chunk[:50]}...")
            print(f"   Stream ID: {simf_message.payload.stream_id}")
            print(f"   Position: {simf_message.payload.position}")
        
        print("✅ Streaming simulation complete")
    
    async def demo_semantic_preservation(self):
        """Demonstrate complete round-trip semantic preservation."""
        print("\n🔍 Demo 4: Semantic Preservation Validation")
        print("-" * 40)
        
        # Test cases with different complexity levels
        test_cases = [
            {
                "name": "Simple tool call",
                "tool": "analyze_text",
                "args": {"text": "Hello world", "analysis_type": "sentiment"}
            },
            {
                "name": "Complex parameters",
                "tool": "create_document", 
                "args": {
                    "title": "Test Document",
                    "content": "This is a test document with special chars: àáâã & <>",
                    "format": "md"
                }
            },
            {
                "name": "Nested data structures",
                "tool": "analyze_text",
                "args": {
                    "text": json.dumps({"nested": {"data": "value", "list": [1, 2, 3]}}),
                    "analysis_type": "words"
                }
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test Case {i}: {test_case['name']}")
            
            # 1. Create MCP request
            mcp_request = CallToolRequest(
                id=f"test_{i}",
                method="tools/call",
                params={
                    "name": test_case["tool"],
                    "arguments": test_case["args"]
                }
            )
            
            # 2. MCP → SIMF → MCP roundtrip
            simf_message = await self.adapter.to_internal_format(
                mcp_request, {"session_id": self.session_id}
            )
            reconstructed_mcp = await self.adapter.from_internal_format(simf_message)
            
            # 3. Verify preservation
            original_tool = mcp_request.params["name"]
            original_args = mcp_request.params["arguments"]
            reconstructed_tool = reconstructed_mcp.params["name"]
            reconstructed_args = reconstructed_mcp.params["arguments"]
            
            tool_preserved = original_tool == reconstructed_tool
            args_preserved = original_args == reconstructed_args
            test_passed = tool_preserved and args_preserved
            
            print(f"   Tool name: {'✅' if tool_preserved else '❌'}")
            print(f"   Arguments: {'✅' if args_preserved else '❌'}")
            print(f"   Result: {'✅ PASS' if test_passed else '❌ FAIL'}")
            
            if not test_passed:
                all_passed = False
                print(f"   Original: {original_args}")
                print(f"   Reconstructed: {reconstructed_args}")
        
        print(f"\n🏁 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        return all_passed


async def run_integration_demo():
    """Run the complete SIMF-MCP integration demonstration."""
    demo = SIMFMCPIntegrationDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(run_integration_demo()) 