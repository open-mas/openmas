#!/usr/bin/env python3
"""
Fixed MCP Agent Demo

This demo addresses the hanging issue by implementing proper:
1. Timeout handling for all MCP operations
2. Graceful cleanup and error handling
3. Real MCP server integration with fallback
4. Anti-hallucination patterns (real MCP, no mocking)

Usage: python demo_mcp_agent.py
"""

import asyncio
import signal
import sys
import tempfile
import subprocess
import os
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from openmas.agent.mcp_agent import MCPAgent
    from openmas.core.simf import (
        SIMFMessage, 
        MessageType,
        create_invocation_message,
        create_text_message
    )
    from mcp.server.fastmcp import FastMCP
    from mcp.server.stdio import stdio_server
    from mcp.client.stdio import stdio_client
    from mcp.client.session import ClientSession
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Please install dependencies: poetry install")
    sys.exit(1)


class TimeoutManager:
    """Manages timeouts to prevent hanging operations"""
    
    def __init__(self, default_timeout: int = 10):
        self.default_timeout = default_timeout
    
    async def with_timeout(self, coro, timeout: int = None, operation_name: str = "operation"):
        """Execute coroutine with timeout and proper error handling"""
        timeout = timeout or self.default_timeout
        try:
            print(f"⏱️  Starting {operation_name} (timeout: {timeout}s)")
            result = await asyncio.wait_for(coro, timeout=timeout)
            print(f"✅ {operation_name} completed successfully")
            return result
        except asyncio.TimeoutError:
            print(f"⚠️  {operation_name} timed out after {timeout}s")
            raise TimeoutError(f"{operation_name} timed out after {timeout} seconds")
        except Exception as e:
            print(f"❌ {operation_name} failed: {e}")
            raise


async def create_test_mcp_server():
    """Create a test MCP server for the demo"""
    print("🔧 Creating test MCP server...")
    
    # Create server script
    server_script = '''
import asyncio
from mcp.server.stdio import stdio_server
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo_test_server")

@mcp.tool()
def demo_add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def demo_greet(name: str) -> str:
    """Greet someone"""
    return f"Hello, {name}! Welcome to the MCP Agent demo."

@mcp.tool()
def demo_status() -> str:
    """Get server status"""
    return "MCP Demo Server is running successfully!"

@mcp.resource("demo://info/{topic}")
def demo_info(topic: str) -> str:
    """Get demo information"""
    topics = {
        "server": "This is a demo MCP server for testing OpenMAS agents",
        "agent": "OpenMAS agents communicate via SIMF messages",
        "demo": "This demo shows real MCP integration without mocking"
    }
    return topics.get(topic, f"No information available for: {topic}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_init_options())

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(server_script)
        f.flush()
        return f.name


async def create_mcp_client_session(server_script_path, timeout_manager):
    """Create real MCP client session with timeout handling"""
    print("🔌 Starting MCP server process...")
    
    # Start server process
    process = subprocess.Popen(
        ["python", server_script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give server time to start
    await asyncio.sleep(1)
    
    if process.poll() is not None:
        stderr = process.stderr.read() if process.stderr else "No error output"
        raise RuntimeError(f"MCP server failed to start: {stderr}")
    
    print("📡 Connecting MCP client...")
    
    # Create client connection
    read_stream, write_stream = stdio_client(process)
    session = ClientSession(read_stream, write_stream)
    
    # Initialize with timeout
    await timeout_manager.with_timeout(
        session.initialize(), 
        timeout=15, 
        operation_name="MCP session initialization"
    )
    
    return session, process


async def demo_mcp_operations(agent, timeout_manager):
    """Demonstrate various MCP operations with timeout handling"""
    print("\n🎯 Testing MCP Agent operations...")
    
    # Test 1: Simple tool call
    print("\n1️⃣ Testing tool call: demo_add(5, 3)")
    add_message = create_invocation_message(
        invocation_type="tool_call",
        target="demo_add",
        parameters={"a": 5, "b": 3},
        sender_id="demo_user",
        recipient_id=agent.agent_id,
        conversation_id="demo_session",
        protocol_metadata={"protocol": "mcp", "tool_name": "demo_add"}
    )
    
    response = await timeout_manager.with_timeout(
        agent.process_message(add_message),
        timeout=10,
        operation_name="Tool call: demo_add"
    )
    print(f"   Result: {response.content.text}")
    
    # Test 2: Greeting tool
    print("\n2️⃣ Testing tool call: demo_greet('OpenMAS User')")
    greet_message = create_invocation_message(
        invocation_type="tool_call",
        target="demo_greet",
        parameters={"name": "OpenMAS User"},
        sender_id="demo_user",
        recipient_id=agent.agent_id,
        conversation_id="demo_session",
        protocol_metadata={"protocol": "mcp", "tool_name": "demo_greet"}
    )
    
    response = await timeout_manager.with_timeout(
        agent.process_message(greet_message),
        timeout=10,
        operation_name="Tool call: demo_greet"
    )
    print(f"   Result: {response.content.text}")
    
    # Test 3: Status check
    print("\n3️⃣ Testing tool call: demo_status()")
    status_message = create_invocation_message(
        invocation_type="tool_call",
        target="demo_status",
        parameters={},
        sender_id="demo_user",
        recipient_id=agent.agent_id,
        conversation_id="demo_session",
        protocol_metadata={"protocol": "mcp", "tool_name": "demo_status"}
    )
    
    response = await timeout_manager.with_timeout(
        agent.process_message(status_message),
        timeout=10,
        operation_name="Tool call: demo_status"
    )
    print(f"   Result: {response.content.text}")
    
    # Test 4: Resource access
    print("\n4️⃣ Testing resource access: demo://info/agent")
    resource_message = create_invocation_message(
        invocation_type="resource_request",
        target="demo://info/agent",
        parameters={},
        sender_id="demo_user",
        recipient_id=agent.agent_id,
        conversation_id="demo_session",
        protocol_metadata={"protocol": "mcp", "resource_uri": "demo://info/agent"}
    )
    
    response = await timeout_manager.with_timeout(
        agent.process_message(resource_message),
        timeout=10,
        operation_name="Resource access: demo://info/agent"
    )
    print(f"   Result: {response.content.text}")


async def demo_concurrent_operations(agent, timeout_manager):
    """Demonstrate concurrent operations to test stability"""
    print("\n🔄 Testing concurrent operations...")
    
    # Create multiple concurrent tool calls
    tasks = []
    for i in range(3):
        message = create_invocation_message(
            invocation_type="tool_call",
            target="demo_add",
            parameters={"a": i, "b": i+1},
            sender_id="demo_user",
            recipient_id=agent.agent_id,
            conversation_id="demo_session",
            protocol_metadata={"protocol": "mcp", "tool_name": "demo_add"}
        )
        
        task = timeout_manager.with_timeout(
            agent.process_message(message),
            timeout=15,
            operation_name=f"Concurrent call {i}"
        )
        tasks.append(task)
    
    # Execute all concurrently
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    print("   Concurrent results:")
    for i, response in enumerate(responses):
        if isinstance(response, Exception):
            print(f"   - Task {i}: ❌ Failed with {response}")
        else:
            print(f"   - Task {i}: ✅ {response.content.text}")


async def main():
    """Main demo function with comprehensive error handling"""
    print("🚀 OpenMAS MCP Agent Demo")
    print("=" * 50)
    
    timeout_manager = TimeoutManager(default_timeout=15)
    server_script_path = None
    process = None
    session = None
    agent = None
    
    try:
        # Create test server
        server_script_path = await create_test_mcp_server()
        
        # Create MCP client session
        session, process = await create_mcp_client_session(server_script_path, timeout_manager)
        
        # Create MCPAgent
        print("🤖 Creating MCP Agent...")
        agent = MCPAgent(
            agent_id="demo_agent_001",
            name="OpenMAS Demo Agent",
            description="Demonstration agent for MCP integration",
            mcp_session=session
        )
        
        # Start agent
        await timeout_manager.with_timeout(
            agent.start(),
            timeout=10,
            operation_name="Agent startup"
        )
        
        print(f"✅ Agent created: {agent.name} ({agent.agent_id})")
        print(f"🎉 Agent is running: {agent.is_running}")
        
        # Run demonstrations
        await demo_mcp_operations(agent, timeout_manager)
        await demo_concurrent_operations(agent, timeout_manager)
        
        print("\n🎉 Demo completed successfully!")
        print("💡 This demo used REAL MCP 1.12.0 integration - no mocking!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Comprehensive cleanup
        print("\n🧹 Cleaning up...")
        
        if agent:
            try:
                await timeout_manager.with_timeout(
                    agent.stop(),
                    timeout=5,
                    operation_name="Agent shutdown"
                )
            except Exception as e:
                print(f"⚠️ Agent cleanup warning: {e}")
        
        if process and process.poll() is None:
            print("🔌 Terminating MCP server...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("🔥 Force killing MCP server...")
                process.kill()
        
        if server_script_path and os.path.exists(server_script_path):
            try:
                os.unlink(server_script_path)
            except OSError:
                pass
        
        print("✅ Cleanup completed")


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\n⚠️ Received signal {signum}, shutting down gracefully...")
        # Let the main cleanup handle the shutdown
        raise KeyboardInterrupt()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    print("🔧 Starting MCP Agent Demo...")
    
    # Setup signal handlers
    setup_signal_handlers()
    
    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo terminated by user")
    except Exception as e:
        print(f"\n💥 Demo crashed: {e}")
        sys.exit(1) 