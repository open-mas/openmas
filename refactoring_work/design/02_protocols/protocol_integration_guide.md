# OpenMAS Protocol Integration Guide

## Overview

This guide provides comprehensive information on integrating and using multiple protocols within OpenMAS. It serves as a companion to the individual protocol documentation files, focusing on cross-protocol concerns, protocol selection strategies, and multi-protocol integration patterns.

## Protocol Selection Strategy

When designing an OpenMAS agent system, choosing the right protocol(s) is a critical architectural decision. Use this guide to select the most appropriate protocol for your use case:

| Protocol | Best For | Consider When | Example Use Cases |
|----------|----------|---------------|-------------------|
| **A2A** | Agent-to-agent communication | You need standardized agent discovery, capability advertisement, and agent orchestration | - Multi-agent systems with dynamic agent discovery<br>- Systems requiring capability advertisement<br>- Agent orchestration and delegation |
| **MCP** | Model/agent access to tools and resources | You need to connect models and agents with external tools, APIs, and data sources | - Agents needing access to multiple tool APIs<br>- Systems with model-tool interactions<br>- Applications requiring resource access control |
| **HTTP** | RESTful communication | You need web-based, widely supported, RESTful communication | - Web service integration<br>- Client-server agent architectures<br>- API-first agent designs |
| **MQTT** | IoT and event-driven systems | You need lightweight, pub/sub messaging for constrained environments | - IoT device networks<br>- Event-driven architectures<br>- Low-bandwidth environments |
| **gRPC** | High-performance service communication | You need strongly typed, high-performance RPC communication | - Performance-critical systems<br>- Microservice architectures<br>- Type-safe service definitions |

## Complementary Protocol Usage

OpenMAS is designed to leverage the complementary strengths of different protocols. Here's how they work together:

### A2A and MCP: Complementary but Not Directly Interoperable

A2A and MCP serve different but complementary purposes:

- **A2A (horizontal integration)**: Enables agents to find each other, exchange capabilities, and coordinate tasks through standardized task delegation and multi-agent orchestration
- **MCP (vertical integration)**: Connects an agent to its tools, APIs, and resources through standardized tool invocation and resource access

**Important**: While A2A and MCP complement each other functionally, they are **not directly interoperable at the message content/semantic level**. Their core abstractions (A2A Tasks vs. MCP Tools), message structures, and message lifecycles are fundamentally different.

#### OpenMAS SIMF-Mediated Strategy

OpenMAS enables A2A and MCP to work together through the Standard Internal Message Format (SIMF) as a mediation layer:

1. **Dedicated Protocol Adapters**: 
   - The `A2AProtocolAdapter` translates between native A2A messages and SIMF
   - The `MCPProtocolAdapter` translates between native MCP messages and SIMF

2. **Unified Capability Model as an Internal Abstraction**:
   - Capabilities are defined once in a protocol-agnostic manner
   - The SIMF represents these capabilities internally
   - Protocol adapters map these capabilities to their protocol-specific formats

```yaml
# Example of unified capabilities mapped to different protocols
multi_protocol_capabilities:
  core:
    - name: "weather.get_current"
      description: "Get current weather for a location"
      parameters:
        type: "object"
        properties:
          location:
            type: "string"
            description: "Location name"
  protocol_mapping:
    a2a:
      "weather.get_current": "getWeather"
    mcp:
      "weather.get_current": "get_weather_tool"
    http:
      "weather.get_current": "/api/v1/weather"
```

3. **Layered Architecture Approach**:
   - An agent might use A2A for external communication with other agents
   - The same agent might use MCP for its internal tool interactions
   - The SIMF ensures data can flow between these layers when needed
   - For example, data received via A2A might be used to parameterize an MCP tool call

> **Note**: The "unified capability model" represents how a capability is defined once and mapped to different protocol-specific formats in the configuration. At runtime, the actual message translation between protocols is mediated through SIMF, not direct protocol-to-protocol conversion.

## Multi-Protocol Architecture Patterns

### 1. Protocol Specialization Pattern

Use different protocols for specialized functions within your agent system:

```
[A2A Protocol] <-- Agent Orchestration --> [Agent System]
                                              |
[MCP Protocol] <-- Tool Access ------------> |
                                              |
[MQTT Protocol] <-- IoT Device Events -----> |
```

**Example:**
```yaml
protocols:
  a2a:
    enabled: true
    transport:
      type: "http"
      config: { port: 8080, host: "0.0.0.0" }
    # Used for agent discovery and delegation
  
  mcp:
    enabled: true
    transport:
      type: "sse"
      config: { port: 8082, host: "0.0.0.0" }
    # Used for tool invocation
  
  mqtt:
    enabled: true
    transport:
      config:
        broker_url: "mqtt://broker.example.com"
        client_id: "sensor-agent"
    # Used for sensor data ingestion
```

### 2. Protocol Bridging Pattern

Connect agents using different protocols through OpenMAS protocol adapters:

```
[Agent A] <-- A2A --> [OpenMAS Protocol Adapter] <-- MQTT --> [Agent B]
```

**Example:**
```yaml
extensions:
  protocol_adapters:
    - name: "mqtt_to_http"
      enabled: true
      class: "openmas.extensions.protocol_adapters.MQTTToHTTPAdapter"
      config:
        topic_to_path_mapping:
          "sensors/temperature": "/api/v1/sensors/temperature"
        default_http_method: "POST"
```

### 3. Protocol Layering Pattern

Use different protocols at different layers of your architecture:

```
[UI Layer] <-- HTTP --> [API Layer] <-- gRPC --> [Service Layer] <-- MQTT --> [Device Layer]
```

## Protocol Integration Examples

### Example 1: Weather Service with Multiple Protocols

```python
from openmas.agents import Agent
from openmas.protocols import ProtocolManager

class WeatherServiceAgent(Agent):
    async def setup(self):
        # Set up A2A protocol for agent communication
        self.a2a_server = await self.setup_protocol("a2a-http", {
            "server_mode": True,
            "port": 8080,
            "agent_card": {
                "name": "Weather Service Agent",
                "description": "Provides weather forecasts and alerts",
                "capabilities": ["getWeather", "getForecasts", "subscribeAlerts"]
            }
        })
        
        # Set up MCP protocol for tool access
        self.mcp_client = await self.setup_protocol("mcp-sse", {
            "server_mode": False,
            "server_url": "https://weather-api.example.com/mcp"
        })
        
        # Set up MQTT for real-time weather updates
        self.mqtt_client = await self.setup_protocol("mqtt", {
            "broker_url": "mqtt://weather-broker.example.com",
            "client_id": "weather-service-agent",
            "subscribe_topics": ["weather/updates/#"]
        })
        
        # Register capability handlers
        self.register_capability("getWeather", self.handle_get_weather)
        self.register_capability("getForecasts", self.handle_get_forecasts)
        self.register_capability("subscribeAlerts", self.handle_subscribe_alerts)
    
    async def handle_get_weather(self, params):
        # This demonstrates using A2A input to parameterize an MCP tool call
        # The A2A message has already been converted to SIMF by the A2A adapter
        # and the params are extracted from that SIMF representation
        location = params.get("location", "default")
        
        # Invoke MCP tool - OpenMAS handles the SIMF-mediated translation:
        # 1. Creates an SIMF message from the parameters
        # 2. MCP adapter translates SIMF to native MCP format
        # 3. Result is translated back to SIMF, then extracted
        weather_data = await self.mcp_client.invoke_tool("get_weather", {"location": location})
        
        # Format and return data - will be converted to A2A format by the A2A adapter
        return {
            "location": location,
            "temperature": weather_data.get("temperature"),
            "condition": weather_data.get("condition"),
            "timestamp": weather_data.get("timestamp")
        }
```

### Example 2: Protocol Agnostic Capability Implementation

```python
from openmas.capabilities import CapabilityRegistry

# Register a protocol-agnostic capability
registry = CapabilityRegistry.get_instance()

@registry.register_capability("translate_text")
async def translate_text(text, source_language, target_language):
    """
    Translate text between languages.
    This capability can be invoked from any protocol.
    """
    # Implementation is protocol-agnostic
    translation_result = await translation_service.translate(
        text=text,
        source_lang=source_language,
        target_lang=target_language
    )
    
    return {
        "translated_text": translation_result.text,
        "source_language": source_language,
        "target_language": target_language
    }

# This capability is automatically available via any configured protocol
# through the OpenMAS unified capability model and protocol mappings
```

## Cross-Protocol Communication Patterns

OpenMAS supports several communication patterns that work across all protocols:

| Pattern | Description | Supported Protocols | Example Use Case |
|---------|-------------|---------------------|------------------|
| **Request-Response** | Synchronous request with response | All protocols | API calls, data queries |
| **Publish-Subscribe** | Asynchronous event distribution | Primarily MQTT, but supported in all | Event notifications, data streams |
| **Streaming** | Continuous data flow | gRPC, MQTT, MCP, HTTP (SSE) | Real-time data, LLM responses |
| **Command** | One-way instruction | All protocols | Actuator control, agent instructions |
| **Query** | Data retrieval | All protocols | Information requests, state queries |

See [Communication Patterns](/refactoring_work/00b_overview/07_communication_patterns/README.md) for detailed information on implementing these patterns.

## Protocol Security Integration

Security is a critical aspect of multi-protocol systems. OpenMAS provides consistent security patterns across all protocols:

```yaml
# Example security configurations across protocols
protocols:
  a2a:
    security:
      auth_provider: "jwt"
      auth_config:
        secret_key_env: "OPENMAS_A2A_JWT_SECRET"
        token_expiry_seconds: 3600
  
  http:
    security:
      auth_provider: "api_key"
      auth_config:
        header_name: "X-API-Key"
        api_key_env: "OPENMAS_HTTP_API_KEY"
  
  mqtt:
    security:
      auth_config:
        username_env: "OPENMAS_MQTT_USERNAME"
        password_env: "OPENMAS_MQTT_PASSWORD"
        use_tls: true
        ca_cert_path: "/path/to/ca.crt"
```

## Protocol Selection Decision Tree

Use this decision tree to guide your protocol selection:

1. **Do you need agent-to-agent communication with capability discovery?**
   - Yes → Consider A2A
   - No → Continue

2. **Do you need to connect agents/models with tools and external resources?**
   - Yes → Consider MCP
   - No → Continue

3. **Is your system primarily event-driven with many publishers and subscribers?**
   - Yes → Consider MQTT
   - No → Continue

4. **Do you need high-performance RPC with strong typing?**
   - Yes → Consider gRPC
   - No → Continue

5. **Do you need simple RESTful API communication?**
   - Yes → Consider HTTP
   - No → Revisit requirements

> **Important**: You can use multiple protocols together in your OpenMAS application. For example, A2A for agent-to-agent communication and MCP for tool interactions. OpenMAS will handle the SIMF-mediated translation between protocols when needed.

## Protocol Version Compatibility

OpenMAS maintains compatibility with the following protocol versions:

| Protocol | Supported Versions | Compatibility Notes |
|----------|-------------------|---------------------|
| A2A | 0.2.0+ | Full support for the latest version |
| MCP | 1.0+ | Full support for all features |
| HTTP | HTTP/1.1, HTTP/2 | Full support for both versions |
| MQTT | MQTT 3.1.1, MQTT 5.0 | Full support for both versions, with enhanced features in 5.0 |
| gRPC | gRPC on HTTP/2 | Full support |

## Multi-Protocol Observability

OpenMAS provides unified observability across protocols:

```python
# Example: Protocol-agnostic logging middleware
from openmas.observability import MessageObserver

class LoggingObserver(MessageObserver):
    def observe_message(self, message, protocol, direction):
        """Log messages across all protocols."""
        logger.info(f"[{protocol}][{direction}] Message: {message}")
        
# Register with the protocol manager
protocol_manager.add_observer(LoggingObserver())
```

## References

- [A2A Protocol Documentation](/refactoring_work/00b_overview/02_protocols/a2a/a2a_protocol.md)
- [MCP Protocol Documentation](/refactoring_work/00b_overview/02_protocols/mcp/mcp_protocol.md)
- [HTTP Protocol Documentation](/refactoring_work/00b_overview/02_protocols/http/http_protocol.md)
- [MQTT Protocol Documentation](/refactoring_work/00b_overview/02_protocols/mqtt/mqtt_protocol.md)
- [gRPC Protocol Documentation](/refactoring_work/00b_overview/02_protocols/grpc/grpc_protocol.md)
- [Protocol Configuration Guide](/refactoring_work/00b_overview/02_protocols/protocol_configuration_guide.md)
- [Protocol Adapter Extension Points](/refactoring_work/00b_overview/05_extensions/extension_points/protocol_adapter_points.md)
- [Unified Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
