# Model Context Protocol (MCP) Knowledge Base

This directory contains reference information for implementing the Model Context Protocol (MCP) in OpenMAS.

## MCP Overview

The Model Context Protocol (MCP) is a standardized protocol for interacting with language models, providing a structured way to:

1. **Request completions** from language models
2. **Receive content** from models
3. **Call tools** from within model completions
4. **Stream results** back to clients

## Key MCP Concepts

OpenMAS implements all six key MCP concepts:

1. **Resources** - Standardized access to different content types
2. **Prompts** - Structured templates with variables
3. **Tools** - Discoverable agent capabilities
4. **Sampling** - Parameters for model inference
5. **Roots** - Entry points for resource access
6. **Transports** - Both SSE and STDIO implementations

## Implementations in OpenMAS

OpenMAS provides two main MCP implementations:

1. **MCP SSE** - Server-Sent Events implementation for web integration
2. **MCP STDIO** - Standard I/O implementation for CLI and local usage

## Reference Documentation

### Official MCP Documentation

- [MCP Architecture](https://modelcontextprotocol.io/docs/concepts/architecture)
- [MCP Resources](https://modelcontextprotocol.io/docs/concepts/resources)
- [MCP Prompts](https://modelcontextprotocol.io/docs/concepts/prompts)
- [MCP Tools](https://modelcontextprotocol.io/docs/concepts/tools)
- [MCP Sampling](https://modelcontextprotocol.io/docs/concepts/sampling)
- [MCP Roots](https://modelcontextprotocol.io/docs/concepts/roots)
- [MCP Transports](https://modelcontextprotocol.io/docs/concepts/transports)

### MCP Python SDK

The OpenMAS MCP implementation uses Anthropic's python-sdk 1.6 which internally uses the FastMCP library.

- **GitHub**: [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- **PyPI**: [mcp](https://pypi.org/project/mcp/)

### Import Examples

```python
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.types import TextContent, CallToolResult
from mcp.server.fastmcp import FastMCP, Context
```

## OpenMAS MCP Guides

### Tutorial Guides

- [MCP SSE Tool Call Tutorial](../../../site/guides/mcp_sse_tool_call_tutorial/)
- [MCP STDIO Tool Call Tutorial](../../../site/guides/mcp_stdio_tool_call_tutorial/)

### Integration Guides

- [MCP Developer Guide](../../../site/guides/mcp_developer_guide/)
- [MCP Integration Guide](../../../site/guides/mcp_integration/)

## OpenMAS MCP Examples

- [MCP SSE Tool Call Example](../../../examples/example_08_mcp/01_mcp_sse_tool_call/)
- [MCP STDIO Tool Call Example](../../../examples/example_08_mcp/02_mcp_stdio_tool_call/)

## Common Patterns

### MCP Server Setup

```python
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent, CallToolResult

async def handle_tool_call(ctx: Context, name: str, parameters: dict) -> CallToolResult:
    """Handle tool calls from the model."""
    # Tool implementation here
    return CallToolResult(content=result)

app = FastMCP()
app.tool("tool_name", handle_tool_call)
```

### MCP Client Setup

```python
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

async with ClientSession() as session:
    async with session.connect("http://localhost:8000/mcp", transport=sse_client) as connection:
        prompt = {
            "role": "user",
            "content": "Hello, can you help me with a task?"
        }

        async for event in connection.completion([prompt]):
            if event.type == "content":
                print(event.content.text, end="", flush=True)
