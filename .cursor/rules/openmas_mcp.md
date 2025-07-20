# OpenMAS MCP Development Rules

**Version**: MCP 1.12.0 SDK
**Lessons**: Extracted from 0.2.0 hard-learned experience
**Environment Details**: [MCP Development Environment Reference](../docs/references/mcp_development_environment.md)
**Reference**: [Detailed MCP Guide](../docs/guides/mcp_best_practices.md)

## 🚨 Critical Rules (ALWAYS Follow)

### 1. Session Initialization (MANDATORY)
```python
# ✅ ALWAYS do this before ANY MCP operations
await asyncio.wait_for(session.initialize(), timeout=10.0)
```
**Why**: Prevents "Invalid request parameters" and "Received request before initialization" errors

### 2. Use Timeouts (MANDATORY)
```python
# Session init: 10s, Tool calls: 30s, Server startup: 15s
await asyncio.wait_for(operation, timeout=appropriate_timeout)
```
**Why**: Prevents hanging operations that block the entire system

### 3. Robust Result Extraction (MANDATORY)
```python
def extract_tool_result(result: CallToolResult) -> str:
    if result.isError:
        raise AgentError(f"Tool execution failed: {result.content}")

    # Try structured content first, fallback to text
    if hasattr(result, 'structuredContent') and result.structuredContent:
        return str(result.structuredContent)

    if result.content and len(result.content) > 0:
        first_content = result.content[0]
        if hasattr(first_content, 'text'):
            return first_content.text

    return str(result.content) if result.content else "No result content"
```
**Why**: MCP 1.12.0 returns complex objects, not simple strings

## 🧪 Testing Rules

### Anti-Hallucination Testing (MANDATORY)
- **Always test against REAL MCP servers**, not just mocks
- Use `@pytest.mark.real` for integration tests
- Verify actual protocol communication

### Server Readiness
```python
# Wait for server to be fully ready before testing
await wait_for_server_ready(session, timeout=15.0)
```

## 🏗️ OpenMAS 0.3.0 Integration

### SIMF-First Architecture
- **Never bypass SIMF** - always use protocol adapters
- **Agent capabilities**: Use `mcp_tool_{name}` naming convention
- **Error handling**: Wrap MCP errors in `AgentError`

### Protocol Adapter Pattern
```
Agent (SIMF) ↔ MCPProtocolAdapter ↔ MCP SDK ↔ External Server
```

## 🚫 Never Do This

1. **Call MCP methods without `session.initialize()`**
2. **Assume tool results are simple strings**
3. **Skip timeouts on async operations**
4. **Test only with mocks (always test real implementations)**
5. **Bypass SIMF architecture (use protocol adapters)**

## 📊 Quick Reference

| Operation | Timeout | Pattern |
|-----------|---------|---------|
| Session Init | 10s | `await asyncio.wait_for(session.initialize(), timeout=10.0)` |
| Tool Call | 30s | `await asyncio.wait_for(session.call_tool(name, args), timeout=30.0)` |
| Server Start | 15s | `await asyncio.wait_for(server.start(), timeout=15.0)` |

**Remember**: These rules prevent the painful debugging sessions we had in 0.2.0. Follow them strictly!
