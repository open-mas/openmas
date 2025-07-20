# Model Context Protocol (MCP)

## Protocol Definition

- **Name**: Model Context Protocol (MCP)
- **Purpose**: Standardized access to external resources for AI models and agents
- **Specification Reference**: [Model Context Protocol](https://github.com/modelcontextprotocol/protocol)
- **OpenMAS Implementation Status**: Fully Supported
- **Reasoning Agnosticism**: Complete separation between MCP communication layer and agent reasoning approaches
- **Protocol Independence**: Can interoperate with other protocols through OpenMAS protocol adapters and the Standard Internal Message Format (SIMF)

## Protocol Overview

The Model Context Protocol (MCP) is designed to standardize how AI models and agents connect to and interact with tools, APIs, data sources, and other external resources. It provides a consistent interface for models to access external functionality, creating a bridge between reasoning systems and the external world.

OpenMAS fully implements the MCP protocol while maintaining its core principle of reasoning agnosticism, allowing agents with different reasoning approaches (rule-based, BDI, LLM-based, etc.) to access external tools and resources through a standardized interface.

## Protocol Features

### Core Features

1. **Tool Registration and Discovery**
   - Structured tool definitions with parameters and return schemas
   - Logical grouping of related tools
   - Runtime discovery of available tools
   - Parameter and return value validation against schemas
   - Consistent capability descriptions across tools

> **Note on Protocol Interoperability**: While MCP is designed to complement other protocols like A2A, they are not directly interoperable at the message content level due to fundamental differences in their abstractions (e.g., MCP Tools vs. A2A Tasks). In OpenMAS, meaningful communication between MCP and other protocols is achieved through translation to/from the Standard Internal Message Format (SIMF) via dedicated protocol adapters, not through direct message passthrough.

2. **Resource Access**
   - Unified interface for different resource types (files, URLs, etc.)
   - Resource conversion and transformation
   - Resource versioning and caching
   - Asynchronous resource loading
   - Resource permissions and access control

3. **Streaming Support**
   - Bidirectional streaming for continuous data exchange
   - Progressive result delivery
   - Chunked content handling
   - Connection management
   - Timeout and error handling

### Extended Features

OpenMAS extends the MCP protocol with additional features:

1. **Security Enhancements**
   - Fine-grained tool-level permissions
   - Authentication mechanisms
   - Rate limiting and quota enforcement
   - Request validation and sanitization

2. **Protocol Bridging**
   - Translation between MCP and other protocols via the Standard Internal Message Format (SIMF)
   - Tool mapping across protocol boundaries through the unified capability model
   - Schema transformation for cross-protocol compatibility via dedicated protocol adapters

3. **Session Management**
   - Session state persistence
   - Context preservation across interactions
   - Session timeout and cleanup
   - Multi-user session isolation

## OpenMAS Implementation

### Architecture Integration

The MCP protocol implementation in OpenMAS is built on the protocol-agnostic foundation of the framework. It integrates with the core components as follows:

1. **Agent Framework**: MCP tools are connected to the agent framework, translating between agent capabilities and MCP messages
2. **Tool System**: Agent capabilities are automatically exposed as MCP tools with proper schema translation
3. **Configuration System**: MCP protocol options are configured through the unified schema
4. **Resource System**: External resources are managed through OpenMAS's asset management

#### Component Interactions

```
┌────────────────┐      ┌─────────────────┐      ┌────────────────┐
│  Agent (Brain) │      │ OpenMAS Core    │      │ MCP Protocol   │
│                │◄────►│                 │◄────►│ Implementation │
└────────────────┘      └─────────────────┘      └────────────────┘
                              │                         │
                              │                         │
                        ┌─────▼─────┐             ┌─────▼─────┐
                        │   Tool    │             │ External  │
                        │  Registry │             │ Resources │
                        └───────────┘             └───────────┘
```

### Configuration

The MCP protocol is configured through the unified configuration schema.

For complete schema information, refer to the [Protocol Configuration Schema](/03_configuration/schema/protocols.md#mcp-protocol-configuration).

Example minimal configuration:

```yaml
protocols:
  - type: "mcp-sse"
    enabled: true
    options:
      server_mode: true
      http_port: 8000
      server_name: "data_processing_agent"
      server_instructions: "This agent helps with data processing tasks."
      tool_registration: "auto"
      stream_mode: "sse"
```

## Message Structure

### Request Format

```json
{
  "type": "tool_call",
  "name": "search_database",
  "parameters": {
    "query": "customer feedback on product XYZ",
    "limit": 10,
    "include_metadata": true
  },
  "correlation_id": "call-123"
}
```

### Response Format

```json
{
  "type": "tool_result",
  "result": {
    "records": [
      {
        "id": "fb-123",
        "content": "Great product, very satisfied!",
        "rating": 5,
        "date": "2025-03-15"
      },
      {
        "id": "fb-124",
        "content": "Works as expected, but could be improved.",
        "rating": 4,
        "date": "2025-03-14"
      }
    ],
    "total_count": 45,
    "average_rating": 4.3
  },
  "correlation_id": "call-123"
}
```

### Error Handling

MCP protocol errors follow a standardized format:

```json
{
  "type": "tool_error",
  "error": {
    "code": "invalid_parameters",
    "message": "Required parameter 'query' is missing",
    "details": {
      "missing_parameters": ["query"]
    }
  },
  "correlation_id": "call-123"
}
```

## Communication Patterns

The MCP protocol in OpenMAS implements several standard communication patterns:

1. **Request-Response**: Standard tool invocation with response
2. **Streaming**: Continuous data flow through chunked responses
3. **Function Calling**: Structured function calls with parameters
4. **Resource Access**: Standardized access to different resource types

For detailed documentation on communication patterns, see:
- [Protocol Communication Patterns](/07_communication_patterns/protocol_patterns.md)
- [Protocol Adaptations](/07_communication_patterns/protocol_adaptations.md)

## Security Considerations

1. **Authentication**
   - Bearer token authentication
   - API key authentication
   - Custom authentication providers through extension points
   - Session-based authentication for browser contexts

2. **Authorization**
   - Tool-level access control
   - Resource-level permissions
   - Scope-based authorization
   - Fine-grained permission management

3. **Data Protection**
   - TLS encryption for all communications
   - Payload validation for security
   - PII handling according to privacy regulations
   - Audit logging and compliance tracking

## Usage Examples

### Example 1: Tool Provider Implementation

```python
# MCP tool provider implementation
from openmas.protocols.mcp import MCPServer
from openmas.tools import ToolRegistry

# Define tools
tool_registry = ToolRegistry()
tool_registry.register_tool(
    name="search_database",
    description="Search the customer database for records",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results",
                "default": 10
            }
        },
        "required": ["query"]
    },
    handler=search_database_handler
)

# Create MCP server
server = MCPServer(
    port=8000,
    name="customer_data_agent",
    description="Provides access to customer data",
    tool_registry=tool_registry
)

# Start server
await server.start()

# Tool handler implementation
async def search_database_handler(params):
    query = params.get("query")
    limit = params.get("limit", 10)

    # Search database
    results = await database.search(query, limit=limit)

    return {
        "records": results,
        "total_count": await database.count(query),
        "average_rating": await database.average_rating(query)
    }
```

### Example 2: Tool Consumer Implementation

```python
# MCP tool consumer implementation
from openmas.protocols.mcp import MCPClient
from openmas.agents import Agent

class DataAnalysisAgent(Agent):
    async def setup(self):
        # Connect to MCP server
        self.mcp_client = await self.setup_protocol("mcp-sse", {
            "server_url": "https://customer-data-agent.example.com/mcp",
            "client_mode": true
        })

        # Discover available tools
        self.tools = await self.mcp_client.list_tools()

    async def search_customer_data(self, query):
        # Call MCP tool
        result = await self.mcp_client.call_tool(
            "search_database",
            {
                "query": query,
                "limit": 100
            }
        )

        # Process result
        return self.analyze_results(result)

    def analyze_results(self, results):
        # Analyze the results
        positive_feedback = [r for r in results["records"] if r["rating"] >= 4]
        negative_feedback = [r for r in results["records"] if r["rating"] <= 2]

        return {
            "positive_count": len(positive_feedback),
            "negative_count": len(negative_feedback),
            "average_rating": results["average_rating"],
            "key_insights": self.extract_insights(results["records"])
        }
```

## Interoperability

### Protocol Bridging

OpenMAS provides bidirectional bridging between MCP and other protocols:

1. **MCP ↔ A2A**: Translation between MCP tools and A2A capabilities
2. **MCP ↔ HTTP/REST**: Mapping MCP tools to REST endpoints
3. **MCP ↔ gRPC**: High-performance bridging to gRPC services
4. **MCP ↔ Custom**: Extension points for custom protocol adaptations

### External Systems Integration

MCP protocol in OpenMAS can integrate with:

1. **External MCP Servers**: Seamless integration with any MCP-compliant server
2. **Web Services**: Integration with REST APIs through protocol adaptation
3. **Data Sources**: Connection to databases and data services
4. **AI Models**: Access to external AI models and services

## Performance Considerations

1. **Scalability**
   - Horizontal scaling through multiple MCP endpoints
   - Load balancing across multiple instances
   - Connection pooling for improved performance
   - Supports thousands of concurrent connections

2. **Efficiency**
   - Optimized message serialization and deserialization
   - Efficient schema validation
   - Resource caching for frequently accessed content
   - Streaming optimization for large data transfers

## Protocol Limitations

1. **Standards Compliance**: Implements Draft MCP specification, may need updates as the standard evolves
2. **Resource Handling**: Large binary resources require special handling
3. **Complex Tools**: Very complex tools may require custom implementations
4. **Streaming Limitations**: Some transport methods have limitations with streaming

## Future Roadmap

1. **Enhanced Tool Discovery**: Semantic tool discovery and matching
2. **Advanced Security Features**: Zero-trust architecture and fine-grained permissions
3. **Extended Resource Types**: Support for more specialized resource types
4. **Performance Optimizations**: Further optimizations for high-throughput scenarios

## Related Documentation

- [Protocol Schema Documentation](/03_configuration/schema/protocols.md#mcp-protocol-configuration)
- [Communication Patterns](/07_communication_patterns/protocol_patterns.md)
- [Protocol Adaptations](/07_communication_patterns/protocol_adaptations.md)
- [MCP Security Configuration](/03_configuration/security_configuration.md#mcp-protocol-security)
