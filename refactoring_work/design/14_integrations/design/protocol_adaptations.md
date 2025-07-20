# Protocol Adaptations for Integrations

This document outlines how the OpenMAS integration system adapts to different communication protocols, ensuring that integrations work consistently regardless of the protocol being used while maintaining OpenMAS's core principle of reasoning agnosticism.

## Protocol Adaptation Architecture

OpenMAS uses a protocol adaptation layer to ensure integrations work with all supported protocols:

```
┌─────────────────────────────────────────┐
│           Agent Framework               │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│         Integration Registry             │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│         Integration Provider             │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│        Protocol Adaptation Layer         │
│                                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │   A2A   │ │   MCP   │ │  HTTP   │   │
│  │ Adapter │ │ Adapter │ │ Adapter │   │
│  └─────────┘ └─────────┘ └─────────┘   │
│                                         │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│        External Integration APIs         │
└─────────────────────────────────────────┘
```

## Protocol Adapter Interface

All protocol adapters implement a common interface to ensure consistency:

```python
class ProtocolAdapter:
    """Base class for protocol adapters."""

    def __init__(self, integration, config):
        self.integration = integration
        self.config = config

    async def initialize(self, context):
        """Initialize the protocol adapter."""
        self.context = context

    async def adapt_request(self, request):
        """Adapt a generic request to protocol-specific format."""
        raise NotImplementedError

    async def adapt_response(self, response):
        """Adapt a protocol-specific response to generic format."""
        raise NotImplementedError

    async def adapt_error(self, error):
        """Adapt an error to protocol-specific format."""
        raise NotImplementedError
```

## A2A Protocol Adapter

The A2A protocol adapter translates between OpenMAS integrations and the Google A2A protocol:

```python
class A2AProtocolAdapter(ProtocolAdapter):
    """Adapter for Google A2A protocol."""

    def __init__(self, integration, config):
        super().__init__(integration, config)
        self.message_format = config.get("message_format", "json")
        self.response_handling = config.get("response_handling", "sync")

    async def adapt_request(self, request):
        """Adapt request for A2A protocol."""
        # A2A uses a specific format for tool calls
        adapted_request = {
            "type": "tool_call",
            "tool": {
                "name": self.integration.id,
                "function_call": {
                    "name": request.get("operation"),
                    "parameters": self._convert_to_a2a_parameters(
                        request.get("parameters", {})
                    )
                }
            },
            "context": {
                "run_id": request.get("context", {}).get("trace_id"),
                "timestamp": datetime.now().isoformat()
            }
        }

        return adapted_request

    async def adapt_response(self, response):
        """Adapt response from A2A protocol."""
        # A2A uses a specific format for tool responses
        if "tool_result" in response and response["tool_result"]:
            adapted_response = {
                "status": "success",
                "data": response["tool_result"].get("content", {}),
                "metadata": response.get("context", {})
            }
        elif "tool_error" in response and response["tool_error"]:
            adapted_response = {
                "status": "error",
                "error": {
                    "code": response["tool_error"].get("code", "unknown_error"),
                    "message": response["tool_error"].get("message", "Unknown error")
                },
                "metadata": response.get("context", {})
            }
        else:
            adapted_response = {
                "status": "unknown",
                "data": response,
                "metadata": {}
            }

        return adapted_response

    def _convert_to_a2a_parameters(self, parameters):
        """Convert generic parameters to A2A format."""
        # A2A expects parameters in a specific format
        if self.message_format == "json":
            return json.dumps(parameters)
        else:
            return parameters
```

## MCP Protocol Adapter

The Model Context Protocol (MCP) adapter translates between OpenMAS integrations and the MCP:

```python
class MCPProtocolAdapter(ProtocolAdapter):
    """Adapter for Model Context Protocol."""

    def __init__(self, integration, config):
        super().__init__(integration, config)
        self.tool_name = config.get("tool_name", integration.id)
        self.result_format = config.get("result_format", "structured")

    async def adapt_request(self, request):
        """Adapt request for MCP."""
        # MCP uses a resource-oriented approach
        resource_name = f"tools/{self.tool_name}"
        operation = request.get("operation", "default")

        adapted_request = {
            "resource": resource_name,
            "operation": operation,
            "body": request.get("parameters", {}),
            "metadata": {
                "trace_id": request.get("context", {}).get("trace_id"),
                "timestamp": datetime.now().isoformat()
            }
        }

        return adapted_request

    async def adapt_response(self, response):
        """Adapt response from MCP."""
        # MCP responses have a specific structure
        if "resource" in response and "state" in response:
            if response["state"] == "SUCCESS":
                adapted_response = {
                    "status": "success",
                    "data": response.get("body", {}),
                    "metadata": response.get("metadata", {})
                }
            elif response["state"] == "ERROR":
                adapted_response = {
                    "status": "error",
                    "error": {
                        "code": response.get("error", {}).get("code", "unknown_error"),
                        "message": response.get("error", {}).get("message", "Unknown error")
                    },
                    "metadata": response.get("metadata", {})
                }
            else:
                adapted_response = {
                    "status": "pending",
                    "data": response.get("body", {}),
                    "metadata": response.get("metadata", {})
                }
        else:
            adapted_response = {
                "status": "unknown",
                "data": response,
                "metadata": {}
            }

        return adapted_response
```

## HTTP Protocol Adapter

The HTTP protocol adapter translates between OpenMAS integrations and HTTP requests/responses:

```python
class HTTPProtocolAdapter(ProtocolAdapter):
    """Adapter for HTTP protocol."""

    def __init__(self, integration, config):
        super().__init__(integration, config)
        self.base_path = config.get("base_path", f"/api/integrations/{integration.id}")
        self.response_format = config.get("response_format", "json")

    async def adapt_request(self, request):
        """Adapt request for HTTP."""
        operation = request.get("operation", "default")
        path = f"{self.base_path}/{operation}"

        adapted_request = {
            "method": request.get("method", "POST"),
            "path": path,
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Trace-ID": request.get("context", {}).get("trace_id", "")
            },
            "body": request.get("parameters", {})
        }

        # Add authentication if available
        auth_headers = await self._get_auth_headers()
        if auth_headers:
            adapted_request["headers"].update(auth_headers)

        return adapted_request

    async def adapt_response(self, response):
        """Adapt response from HTTP."""
        status_code = response.get("status_code", 500)

        if 200 <= status_code < 300:
            adapted_response = {
                "status": "success",
                "data": response.get("body", {}),
                "metadata": {
                    "status_code": status_code,
                    "headers": response.get("headers", {})
                }
            }
        else:
            adapted_response = {
                "status": "error",
                "error": {
                    "code": str(status_code),
                    "message": response.get("body", {}).get("message", "Unknown error")
                },
                "metadata": {
                    "status_code": status_code,
                    "headers": response.get("headers", {})
                }
            }

        return adapted_response

    async def _get_auth_headers(self):
        """Get authentication headers."""
        # Implementation depends on authentication strategy
        return {}
```

## Protocol Adaptation Configuration

Protocol-specific adaptations are configured in the integration configuration:

```yaml
integrations:
  example_api:
    type: "api"
    # Core integration configuration
    config:
      base_url: "https://api.example.com/v1"

    # Protocol-specific adaptations
    protocol_adaptations:
      a2a:
        message_format: "json"
        response_handling: "async"

      mcp:
        tool_name: "example_api_tool"
        result_format: "structured"

      http:
        base_path: "/api/tools/example_api"
        response_format: "json"
```

## Protocol-Specific Features

Each protocol has unique features that require specific adaptations:

### A2A Protocol Features

- **Function Call Format** - A2A has specific function call formats for tools
- **Streaming Support** - Support for streaming responses with chunked outputs
- **Authentication** - A2A has specific authentication mechanisms
- **Context Preservation** - Maintaining context across multiple interactions
- **Agent Cards Integration** - Integration with A2A agent cards

### MCP Protocol Features

- **Resource Orientation** - MCP uses a resource-oriented approach
- **State Management** - Managing resource state throughout operation lifecycle
- **Structured Content** - Standardized content schemas for resources
- **Observability Integration** - Integrated monitoring and observability
- **Session Management** - Protocol-specific session handling

### HTTP Protocol Features

- **RESTful Principles** - Following REST principles for resource access
- **Status Codes** - Using HTTP status codes for response status
- **Header Management** - Standardized header usage
- **Authentication Schemes** - Support for HTTP authentication schemes
- **CORS Handling** - Cross-Origin Resource Sharing support

## Protocol Feature Matrix

| Feature | A2A | MCP | HTTP | MQTT |
|---------|-----|-----|------|------|
| Request/Response | ✓ | ✓ | ✓ | ✓ |
| Streaming | ✓ | ✓ | ✓ | ✓ |
| Event-Based | - | ✓ | - | ✓ |
| State Management | Partial | ✓ | - | - |
| File Transfer | ✓ | ✓ | ✓ | Limited |
| Binary Data | ✓ | ✓ | ✓ | ✓ |
| Authentication | Token | Resource | Multiple | MQTT Auth |

## Protocol Selection Logic

OpenMAS automatically selects the appropriate protocol adapter based on:

1. **Context** - The context in which the integration is being used
2. **Explicit Configuration** - Explicit protocol selection in configuration
3. **Capability Requirements** - Required capabilities for the operation
4. **Default Protocol** - System default protocol if none specified

## Reasoning Agnosticism Across Protocols

The protocol adaptation layer maintains OpenMAS's reasoning agnosticism by:

1. **Clean Separation** - Separating protocol concerns from reasoning concerns
2. **Unified Interface** - Providing a consistent interface regardless of protocol
3. **Data Format Neutrality** - Using reasoning-agnostic data formats in the core interfaces
4. **Capability Discovery** - Protocol-specific capability discovery without reasoning assumptions

This enables agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to use the same integrations across different protocols.

## Protocol Adaptation Development Guide

When developing new protocol adapters:

1. **Implement Core Interface** - Implement the ProtocolAdapter interface
2. **Handle Authentication** - Implement protocol-specific authentication
3. **Transform Data Formats** - Convert between protocol-specific and generic formats
4. **Error Handling** - Implement protocol-specific error handling
5. **Streaming Support** - Add support for streaming if the protocol allows it
6. **Testing** - Create protocol-specific tests
7. **Documentation** - Document protocol-specific features and limitations
