# MCP Protocol Support in OpenMAS

## Overview

The Model Context Protocol (MCP) is a communication standard designed for connecting AI models and agents to tools, APIs, and other external resources. OpenMAS provides comprehensive support for MCP while maintaining its core principle of reasoning agnosticism.

## Documentation

- [MCP Protocol Specification](./mcp_protocol.md) - Complete protocol specification and standards
- [MCP Implementation](./mcp_implementation.md) - Implementation details and code examples

## Protocol Specification

- **Name**: Model Context Protocol (MCP)
- **Version**: 0.1
- **Purpose**: Standardized access to external resources for AI models and agents
- **Transport**: Server-Sent Events (SSE), WebSockets, stdio
- **Reasoning Agnosticism**: Complete separation between MCP communication layer and agent reasoning approaches

## Key Features

### Tool Registration and Discovery

OpenMAS fully implements the MCP tool registration system:

- **Tool Definitions** - Structured tool definitions with parameters and return schemas
- **Tool Categories** - Logical grouping of related tools
- **Dynamic Discovery** - Runtime discovery of available tools
- **Schema Validation** - Parameter and return value validation against schemas
- **Capability Advertisement** - Consistent capability descriptions across tools

### Resource Access

OpenMAS implements MCP resource access capabilities:

- **Unified Resource Interface** - Consistent interface for different resource types
- **Resource Types** - Support for files, URLs, databases, and other resources
- **Resource Transformation** - Conversion between different resource formats
- **Resource Permissions** - Access control for resources
- **Resource Streaming** - Efficient handling of large resources

### State Management

OpenMAS supports MCP state management features:

- **Session State** - Maintaining state across multiple interactions
- **Conversation Context** - Preserving context for better reasoning
- **Tool State** - Per-tool state management
- **Persistent Storage** - Long-term state storage options

### Security Features

OpenMAS implements MCP security features:

- **Tool Authorization** - Controlling access to specific tools
- **Resource Authorization** - Controlling access to specific resources
- **Input Validation** - Protection against malicious inputs
- **Output Sanitization** - Protection against harmful outputs

## Protocol Implementation

### MCP Communicator

OpenMAS provides these MCP communicator implementations:

```python
# SSE-based MCP communicator
from openmas.protocols.mcp import MCPSSECommunicator

communicator = MCPSSECommunicator(
    server_mode=True,
    port=8000,
    server_name="openmas_mcp_server",
    tool_registration="auto"
)

# stdio-based MCP communicator for local integration
from openmas.protocols.mcp import MCPStdioCommunicator

communicator = MCPStdioCommunicator(
    tool_registration="auto",
    streaming=True
)
```

### Tool Registration

OpenMAS automates MCP tool registration:

```python
from openmas.protocols.mcp import register_mcp_tool

@register_mcp_tool(
    name="weather_tool",
    description="Get current weather for a location",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name or coordinates"
            }
        },
        "required": ["location"]
    },
    returns={
        "type": "object",
        "properties": {
            "temperature": {
                "type": "number",
                "description": "Current temperature in Celsius"
            },
            "conditions": {
                "type": "string",
                "description": "Weather conditions"
            }
        }
    }
)
async def get_weather(location):
    # Tool implementation
    weather_data = await weather_api.get_current(location)
    return {
        "temperature": weather_data["temp"],
        "conditions": weather_data["conditions"]
    }
```

## MCP with Different Reasoning Approaches

OpenMAS maintains reasoning agnosticism with MCP by:

- **Tool Interface Abstraction** - MCP tool interfaces are independent of reasoning
- **Resource Abstraction** - Resources are accessible in reasoning-agnostic formats
- **Message Transformation** - Converting between MCP messages and reasoning-specific formats

Examples of MCP with different reasoning types:

### LLM-Based Agents

```python
class LLMAgent(Agent):
    async def setup(self):
        # Register MCP tools accessible to this agent
        self.register_tool("weather_tool")
        self.register_tool("calculator_tool")

    async def process_request(self, user_request):
        # LLM reasoning with MCP tool access
        response = await self.llm.generate(
            prompt=user_request,
            tools=self.get_registered_tools()
        )

        # Handle any tool calls from the LLM
        if response.tool_calls:
            tool_results = []
            for tool_call in response.tool_calls:
                result = await self.execute_tool(
                    tool_call.name,
                    tool_call.parameters
                )
                tool_results.append(result)

            # Continue reasoning with tool results
            final_response = await self.llm.generate(
                prompt=user_request,
                previous_response=response,
                tool_results=tool_results
            )
            return final_response.text

        return response.text
```

### Rule-Based Agents

```python
class RuleBasedAgent(Agent):
    async def setup(self):
        # Register the same MCP tools
        self.register_tool("weather_tool")
        self.register_tool("calculator_tool")

        # Define rules for tool usage
        self.rule_engine.add_rule(
            "IF request contains 'weather' AND request contains a location THEN use weather_tool"
        )

    async def process_request(self, user_request):
        # Rule-based reasoning to determine tools
        tool_decisions = self.rule_engine.evaluate_request(user_request)

        # Execute tools based on rule decisions
        results = {}
        for tool, params in tool_decisions.items():
            results[tool] = await self.execute_tool(tool, params)

        # Generate response based on results
        return self.template_engine.render("response_template", results)
```

## MCP Protocol Configuration

For MCP protocol configuration, OpenMAS uses the unified configuration schema. For the complete schema definition, see [Protocol Configuration Schema](/03_configuration/schema/protocols.md).

Key configuration sections:

- **Server/Client Mode**
- **Transport Options**
- **Tool Registration**
- **Resource Access**
- **Security Settings**

## MCP Integration with Other Components

MCP protocol integrates with several OpenMAS components:

1. **Communication Patterns** - MCP-specific implementations of standard patterns
2. **Asset Management** - MCP access to models and embeddings
3. **Prompt Management** - MCP integration with template systems
4. **Observability System** - MCP-specific monitoring and logging

## Known Limitations and Future Work

- **Tool Composition** - Advanced tool composition features in development
- **Resource Caching** - Optimized resource caching planned
- **Multi-Agent MCP** - Extensions for multi-agent scenarios
- **Federated Tools** - Support for federated tool ecosystems
