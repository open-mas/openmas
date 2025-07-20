# MCP Best Practices Guide for OpenMAS 0.3.0

**MCP SDK Version**: 1.12.0
**Based on**: 0.2.0 hard-learned lessons + 0.3.0 architectural patterns
**Last Updated**: 2024-12-28

> **📋 For complete MCP environment details (specs, versions, links)**: See [MCP Development Environment Reference](../references/mcp_development_environment.md)

## 📖 Overview

This guide distills critical lessons learned from OpenMAS 0.2.0 MCP integration and applies them to the new 0.3.0 architecture. These practices prevent common pitfalls and ensure reliable MCP integration.

## 🚨 Critical Session Management

### Session Initialization (MANDATORY)

**Problem**: `"Invalid request parameters"` and `"Received request before initialization"` errors.

**Solution**: Always explicitly initialize sessions before ANY MCP operations:

```python
# ✅ CORRECT: Explicit initialization with timeout
async with stdio_client(server_params) as (read, write):
    session = ClientSession(read, write)

    # CRITICAL: Initialize before any operations
    await asyncio.wait_for(session.initialize(), timeout=10.0)

    # Now safe to make requests
    tools = await session.list_tools()
```

**Key Principles**:
- Never assume session is ready without explicit `initialize()`
- Always use timeout to prevent hanging
- Initialize only once per session lifecycle

### Async Context Management

**Pattern**: Use proper async context managers for resource cleanup:

```python
# ✅ CORRECT: Proper async context handling
async def execute_mcp_operation():
    async with stdio_client(server_params) as (read, write):
        session = ClientSession(read, write)
        await asyncio.wait_for(session.initialize(), timeout=10.0)

        try:
            result = await session.call_tool("tool_name", {"arg": "value"})
            return extract_tool_result(result)
        finally:
            # Context manager handles cleanup
            pass
```

## ⏱️ Timeout Management

### Recommended Timeouts

Based on 0.2.0 experience, use these timeout patterns:

```python
# Session initialization
await asyncio.wait_for(session.initialize(), timeout=10.0)

# Tool calls (adjust based on tool complexity)
result = await asyncio.wait_for(
    session.call_tool(name, args),
    timeout=30.0
)

# Server startup (for embedded servers)
await asyncio.wait_for(server.start(), timeout=15.0)
```

### Timeout Strategy
- **Short timeouts for quick operations** (list_tools, list_resources)
- **Longer timeouts for complex operations** (tool execution, file processing)
- **Always provide fallback behavior** on timeout

## 🔧 Tool Execution & Result Handling

### Result Extraction Pattern

**Problem**: MCP 1.12.0 returns complex `CallToolResult` objects, not simple strings.

**Solution**: Robust result extraction:

```python
def extract_tool_result(result: CallToolResult) -> str:
    """Extract meaningful content from MCP tool result."""
    if result.isError:
        raise AgentError(f"Tool execution failed: {result.content}")

    # Try structured content first (preferred)
    if hasattr(result, 'structuredContent') and result.structuredContent:
        return str(result.structuredContent)

    # Fallback to text content
    if result.content and len(result.content) > 0:
        first_content = result.content[0]
        if hasattr(first_content, 'text'):
            return first_content.text

    # Final fallback
    return str(result.content) if result.content else "No result content"
```

### Tool Call Validation

```python
# ✅ Validate tool availability before calling
available_tools = await session.list_tools()
tool_names = [tool.name for tool in available_tools.tools]

if tool_name not in tool_names:
    raise AgentError(f"Tool '{tool_name}' not available. Available: {tool_names}")

# Then safely call the tool
result = await session.call_tool(tool_name, arguments)
```

## 🧪 Testing Patterns

### Anti-Hallucination Testing

**Critical**: Test against REAL MCP implementations, not just mocks:

```python
@pytest.mark.integration
@pytest.mark.mcp
@pytest.mark.real
async def test_real_mcp_integration():
    """Test against actual MCP server implementation."""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "examples.real_mcp_server"]
    )

    async with stdio_client(server_params) as (read, write):
        session = ClientSession(read, write)
        await asyncio.wait_for(session.initialize(), timeout=10.0)

        # Test real MCP protocol flow
        tools = await session.list_tools()
        assert len(tools.tools) > 0, "Real server should provide tools"

        # Test actual tool execution
        if tools.tools:
            result = await session.call_tool(
                tools.tools[0].name,
                {}
            )
            assert not result.isError, f"Tool execution failed: {result.content}"
```

### Test Server Readiness

```python
async def wait_for_server_ready(session: ClientSession, timeout: float = 15.0):
    """Wait for MCP server to be fully ready."""
    start_time = asyncio.get_event_loop().time()

    while (asyncio.get_event_loop().time() - start_time) < timeout:
        try:
            await session.list_tools()  # Simple ping
            return  # Server is ready
        except Exception:
            await asyncio.sleep(0.1)  # Brief wait

    raise TimeoutError(f"Server not ready after {timeout}s")
```

## 🏗️ OpenMAS 0.3.0 Integration Patterns

### SIMF-First Architecture

Unlike 0.2.0 direct integration, 0.3.0 uses SIMF translation:

```python
class MCPAgent(Agent):
    """Agent with MCP tool capabilities via SIMF translation."""

    async def register_capability(self, capability_name: str) -> None:
        """Register MCP tool as agent capability."""
        # Store with consistent naming convention
        self.capabilities[f"mcp_tool_{capability_name}"] = capability_name

        # Register async capability
        await self._register_capability_async(f"mcp_tool_{capability_name}")

    async def execute_capability(self, capability_name: str, **kwargs) -> str:
        """Execute MCP tool via SIMF interface."""
        if not capability_name.startswith("mcp_tool_"):
            return await super().execute_capability(capability_name, **kwargs)

        # Extract tool name from capability name
        tool_name = self.capabilities.get(capability_name)
        if not tool_name:
            raise AgentError(f"Unknown MCP capability: {capability_name}")

        # Execute via MCP session
        result = await self.mcp_session.call_tool(tool_name, kwargs)
        return extract_tool_result(result)
```

### Protocol Adapter Integration

```python
class MCPProtocolAdapter(IProtocolAdapter):
    """Protocol adapter implementing SIMF ↔ MCP translation."""

    async def send_message(self, message: SIMFMessage) -> None:
        """Translate SIMF message to MCP protocol."""
        if message.type == SIMFMessageType.TOOL_CALL:
            # Translate SIMF tool call to MCP format
            mcp_args = self._translate_simf_to_mcp_args(message.content)
            result = await self.session.call_tool(message.tool_name, mcp_args)

            # Translate result back to SIMF
            simf_response = self._translate_mcp_to_simf_result(result)
            await self._send_simf_response(simf_response)
```

## ⚠️ Common Pitfalls & Solutions

### 1. Missing Session Initialization
- **Problem**: Calling MCP methods before `session.initialize()`
- **Solution**: Always initialize explicitly with timeout

### 2. Timeout Handling
- **Problem**: Operations hanging indefinitely
- **Solution**: Use `asyncio.wait_for()` with appropriate timeouts

### 3. Result Object Assumptions
- **Problem**: Assuming tool results are simple strings
- **Solution**: Robust extraction with fallbacks

### 4. Resource Cleanup
- **Problem**: Sessions and connections not properly closed
- **Solution**: Use async context managers consistently

### 5. Error Propagation
- **Problem**: MCP errors not properly translated to agent errors
- **Solution**: Structured error handling with AgentError wrapping

## 🔍 Debugging & Monitoring

### Logging Setup

```python
import logging

# Enable detailed MCP logging
logging.getLogger("mcp").setLevel(logging.DEBUG)
logging.getLogger("openmas.protocols.mcp").setLevel(logging.DEBUG)

# Log session lifecycle
logger.info(f"Initializing MCP session with {server_params}")
logger.debug(f"Available tools: {[t.name for t in tools.tools]}")
logger.debug(f"Tool call result: {result}")
```

### Health Checks

```python
async def mcp_health_check(session: ClientSession) -> bool:
    """Verify MCP session is healthy."""
    try:
        tools = await asyncio.wait_for(session.list_tools(), timeout=5.0)
        return len(tools.tools) >= 0  # Basic connectivity
    except Exception as e:
        logger.warning(f"MCP health check failed: {e}")
        return False
```

## 📊 Performance Considerations

### Connection Management
- **Reuse sessions** when possible (avoid excessive initialization)
- **Pool connections** for high-throughput scenarios
- **Monitor resource usage** and implement cleanup policies

### Optimization Patterns
- **Batch tool calls** when protocol supports it
- **Cache tool metadata** to avoid repeated list_tools calls
- **Implement circuit breakers** for failing external servers

## 🔄 Migration from 0.2.0

### Key Changes

| 0.2.0 Pattern | 0.3.0 Pattern | Reason |
|---------------|---------------|---------|
| Direct MCP integration | SIMF + Protocol Adapter | Architectural consistency |
| Manual session management | Agent framework integration | Better abstraction |
| String-based results | Structured result extraction | MCP 1.12.0 compatibility |
| Ad-hoc error handling | AgentError standardization | Consistent error experience |

### Migration Checklist

- [ ] Replace direct MCP calls with Agent capability pattern
- [ ] Add explicit session initialization
- [ ] Update result extraction to handle complex objects
- [ ] Implement proper timeout handling
- [ ] Add structured logging
- [ ] Create real integration tests
- [ ] Update error handling to use AgentError

---

## 🎯 Summary

**Core Principles for MCP in OpenMAS 0.3.0**:

1. **Always initialize sessions explicitly** before any MCP operations
2. **Use timeouts consistently** to prevent hanging operations
3. **Extract tool results robustly** with proper fallback handling
4. **Test against real implementations** not just mocks
5. **Integrate via SIMF** following 0.3.0 architectural patterns
6. **Handle errors consistently** using AgentError framework
7. **Log comprehensively** for debugging and monitoring

These patterns, learned through 0.2.0 experience and refined for 0.3.0 architecture, ensure reliable and maintainable MCP integration in OpenMAS.
