# Agent-to-Agent (A2A) Protocol

## Protocol Definition

- **Name**: Agent-to-Agent Protocol (A2A)
- **Purpose**: Standardized communication between AI agents with capability discovery and invocation
- **Specification Reference**: [Google Agent-to-Agent Protocol](https://github.com/google/agent-to-agent)
- **OpenMAS Implementation Status**: Fully Supported
- **Reasoning Agnosticism**: Complete separation between A2A communication layer and agent reasoning approaches
- **Protocol Independence**: Can interoperate with other protocols through OpenMAS protocol adapters and the Standard Internal Message Format (SIMF)

## Protocol Overview

The Agent-to-Agent (A2A) protocol is a communication standard designed for interactions between AI agents. It enables standardized discovery, capability advertisement, and invocation between agents, allowing them to leverage each other's functionality in a consistent manner. The protocol emphasizes capability-based interactions, enabling agents to expose specific functionalities that other agents can discover and use.

OpenMAS fully implements the A2A protocol while maintaining its core principle of reasoning agnosticism, allowing agents with different reasoning approaches (rule-based, BDI, LLM-based, etc.) to communicate effectively through a standardized interface.

## Protocol Features

### Core Features

1. **Agent Discovery and Cards**
   - Well-known endpoints (`/.well-known/agent.json`) for standardized discovery
   - Comprehensive agent metadata including name, description, version
   - Capability advertisement with structured definitions
   - Feature support declarations for streaming, notifications, etc.
   - Authentication requirements specification

> **Note on Protocol Interoperability**: While A2A is designed to complement other protocols like MCP, they are not directly interoperable at the message content level due to fundamental differences in their abstractions (e.g., A2A Tasks vs. MCP Tools). In OpenMAS, meaningful communication between A2A and other protocols is achieved through translation to/from the Standard Internal Message Format (SIMF) via dedicated protocol adapters, not through direct message passthrough.

2. **Capability Model**
   - Runtime registration of agent capabilities
   - Capability schema definitions with parameters and returns
   - Capability grouping and organization
   - Capability constraints and permissions
   - Conditional capabilities based on context

3. **Message Exchange**
   - Request-response messaging pattern
   - Event-based communication
   - Streaming capabilities for continuous data exchange
   - Structured error handling and status codes
   - Message correlation for asynchronous patterns

### Extended Features

OpenMAS extends the A2A protocol with additional features:

1. **Enhanced Security**
   - Fine-grained capability-level permissions
   - OAuth 2.0 integration for authentication
   - Rate limiting and quota enforcement
   - Request validation and sanitization

2. **Protocol Bridging**
   - Translation between A2A and other protocols via the Standard Internal Message Format (SIMF)
   - Capability mapping across protocol boundaries through the unified capability model
   - Schema transformation for cross-protocol compatibility via dedicated protocol adapters

3. **Observability**
   - Detailed message logging
   - Performance metrics
   - Capability usage analytics
   - Protocol-specific tracing

## OpenMAS Implementation

### Architecture Integration

The A2A protocol implementation in OpenMAS is built on the protocol-agnostic foundation of the framework. It integrates with the core components as follows:

1. **Agent Framework**: A2A protocol adapters connect to the agent framework, translating between agent capabilities and A2A protocol messages
2. **Capability System**: Agent capabilities are automatically exposed as A2A capabilities with proper schema translation
3. **Configuration System**: A2A protocol options are configured through the unified schema
4. **Security System**: A2A authentication integrates with OpenMAS's security framework

#### Component Interactions

```
┌────────────────┐      ┌─────────────────┐      ┌────────────────┐
│  Agent (Brain) │      │ OpenMAS Core    │      │ A2A Protocol   │
│                │◄────►│                 │◄────►│ Implementation │
└────────────────┘      └─────────────────┘      └────────────────┘
                              │                         │
                              │                         │
                        ┌─────▼─────┐             ┌─────▼─────┐
                        │ Capability │             │ External  │
                        │  Registry  │             │ A2A Agents│
                        └───────────┘             └───────────┘
```

### Configuration

The A2A protocol is configured through the unified configuration schema.

For complete schema information, refer to the [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md) and the protocol-specific details in [Protocol Schema](/03_configuration/schema/protocols.md#a2a-protocol-configuration).

Example minimal configuration:

```yaml
protocols:
  - type: "a2a-http"
    enabled: true
    options:
      base_url: "https://agent-api.example.com"
      agent_card:
        name: "data_analysis_agent"
        display_name: "Data Analysis Agent"
        description: "Performs statistical analysis on datasets"
        version: "1.0.0"
      auth:
        type: "oauth2"
        audience: "https://agent-api.example.com"
```

## Message Structure

### Request Format

```json
{
  "capability": "analyze_dataset",
  "content": {
    "dataset_url": "https://example.com/datasets/customers.csv",
    "analysis_type": "advanced"
  },
  "correlation_id": "request-123"
}
```

### Response Format

```json
{
  "type": "response",
  "content": {
    "insights": [
      {
        "name": "customer_segments",
        "description": "Identified 3 distinct customer segments",
        "confidence": 0.92
      },
      {
        "name": "purchase_patterns",
        "description": "Seasonal purchase patterns detected",
        "confidence": 0.85
      }
    ]
  },
  "status": "success",
  "correlation_id": "request-123"
}
```

### Error Handling

A2A protocol errors follow a standardized format:

```json
{
  "type": "error",
  "error": {
    "code": "invalid_parameters",
    "message": "The provided analysis_type is not supported",
    "details": {
      "parameter": "analysis_type",
      "allowed_values": ["basic", "advanced", "predictive"]
    }
  },
  "correlation_id": "request-123"
}
```

## Communication Patterns

The A2A protocol in OpenMAS implements several standard communication patterns:

1. **Request-Response**: Standard capability invocation with response
2. **Streaming**: Continuous data flow through chunked responses
3. **Event-Based**: Asynchronous notifications and events
4. **Delegation**: Capability delegation between agents

For detailed documentation on communication patterns, see:
- [Protocol Communication Patterns](/07_communication_patterns/protocol_patterns.md)
- [Protocol Adaptations](/07_communication_patterns/protocol_adaptations.md)

## Security Considerations

1. **Authentication**
   - OAuth 2.0 authentication with JWT tokens
   - API key authentication for simple scenarios
   - Custom authentication providers through extension points
   - Session-based authentication for browser contexts

2. **Authorization**
   - Capability-level access control
   - Role-based permissions
   - Scope-based authorization
   - Fine-grained permission management

3. **Data Protection**
   - TLS encryption for all communications
   - Payload encryption for sensitive data
   - PII handling according to privacy regulations
   - Audit logging and compliance tracking

## Usage Examples

### Example 1: Basic Agent Communication

```python
# Client agent using A2A protocol
from openmas.protocols.a2a import A2AProtocol
from openmas.agents import Agent

class ClientAgent(Agent):
    async def setup(self):
        # Initialize A2A protocol
        self.a2a = await self.setup_protocol("a2a-http", {
            "base_url": "https://weather-agent.example.com"
        })
        
    async def get_weather(self, location):
        # Invoke capability through A2A
        response = await self.a2a.invoke_capability(
            "get_weather",
            {
                "location": location,
                "units": "celsius"
            }
        )
        return response["content"]
```

### Example 2: Implementing A2A Capabilities

```python
# Server agent implementing A2A capabilities
from openmas.protocols.a2a import A2AServer
from openmas.agents import Agent

class WeatherAgent(Agent):
    async def setup(self):
        # Initialize A2A server
        self.a2a_server = await self.setup_protocol("a2a-http", {
            "server_mode": True,
            "port": 8080,
            "agent_card": {
                "name": "weather_agent",
                "display_name": "Weather Forecast Agent",
                "description": "Provides weather forecasts for locations worldwide"
            }
        })
        
        # Register capability
        self.register_capability(
            "get_weather",
            self.get_weather,
            {
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City or location name"
                        },
                        "units": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "default": "celsius"
                        }
                    },
                    "required": ["location"]
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "temperature": {"type": "number"},
                        "conditions": {"type": "string"},
                        "humidity": {"type": "number"}
                    }
                }
            }
        )
    
    async def get_weather(self, request):
        location = request.get("location")
        units = request.get("units", "celsius")
        
        # Get weather data from service
        weather_data = await self.weather_service.get_forecast(location, units)
        
        return {
            "temperature": weather_data["temp"],
            "conditions": weather_data["conditions"],
            "humidity": weather_data["humidity"]
        }
```

## Interoperability

### Protocol Bridging

OpenMAS provides bidirectional bridging between A2A and other protocols:

1. **A2A ↔ MCP**: Translation between A2A capabilities and MCP tools
2. **A2A ↔ HTTP/REST**: Mapping A2A capabilities to REST endpoints
3. **A2A ↔ MQTT**: Event-based integration with MQTT topics
4. **A2A ↔ gRPC**: High-performance bridging to gRPC services

### External Systems Integration

A2A protocol in OpenMAS can integrate with:

1. **External A2A Agents**: Seamless integration with any A2A-compliant agent
2. **Web Services**: Integration with REST APIs through protocol adaptation
3. **Legacy Systems**: Bridging to legacy systems through custom adapters
4. **Cloud Providers**: Integration with cloud services through A2A wrappers

## Performance Considerations

1. **Scalability**
   - Horizontal scaling through multiple A2A endpoints
   - Load balancing across multiple instances
   - Connection pooling for improved performance
   - Supports thousands of concurrent connections

2. **Efficiency**
   - Optimized message serialization and deserialization
   - Efficient schema validation
   - Connection reuse for multiple requests
   - Compression support for large payloads

## Protocol Limitations

1. **Standards Compliance**: Currently implements Draft A2A specification, may need updates as the standard evolves
2. **Authentication Complexity**: OAuth2 implementation requires additional setup
3. **Schema Evolution**: Schema changes require careful versioning
4. **Transport Limitations**: HTTP transport has standard HTTP limitations

## Future Roadmap

1. **Enhanced Capability Federation**: Cross-agent capability discovery and federation
2. **Advanced Security Features**: Zero-trust architecture and advanced threat protection
3. **Extended Monitoring**: Improved debugging and tracing tools
4. **Performance Optimizations**: Further optimizations for high-throughput scenarios

## Related Documentation

- [Protocol Schema Documentation](/03_configuration/schema/protocols.md#a2a-protocol-configuration)
- [Communication Patterns](/07_communication_patterns/protocol_patterns.md)
- [Protocol Adaptations](/07_communication_patterns/protocol_adaptations.md)
- [A2A Security Configuration](/03_configuration/security_configuration.md#a2a-protocol-security)
