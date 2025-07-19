# Agent Protocol Integration

## Overview

This document describes how agents in OpenMAS integrate with different communication protocols (A2A, MCP, HTTP, etc.) while maintaining the core principle of reasoning agnosticism.

## Protocol Integration Architecture

OpenMAS uses a layered architecture for protocol integration:

```
┌────────────────────────────────────────────────┐
│                   Agent                        │
│                                                │
│  ┌────────────────────────────────────────┐    │
│  │           Reasoning Layer              │    │
│  │ (LLM, Rule-Based, BDI, Hybrid, etc.)   │    │
│  └─────────────────────┬──────────────────┘    │
│                        │                       │
│  ┌─────────────────────▼──────────────────┐    │
│  │        Protocol Adapter Layer          │    │
│  │                                        │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐   │    │
│  │  │   A2A   │ │   MCP   │ │  HTTP   │   │    │
│  │  │ Adapter │ │ Adapter │ │ Adapter │   │    │
│  │  └─────────┘ └─────────┘ └─────────┘   │    │
│  └─────────────────────┬──────────────────┘    │
│                        │                       │
│  ┌─────────────────────▼──────────────────┐    │
│  │       Communicator Layer               │    │
│  │                                        │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐   │    │
│  │  │   A2A   │ │   MCP   │ │  HTTP   │   │    │
│  │  │Communic.│ │Communic.│ │Communic.│   │    │
│  │  └─────────┘ └─────────┘ └─────────┘   │    │
│  └────────────────────────────────────────┘    │
└────────────────────────────────────────────────┘
```

This architecture ensures:

1. **Protocol Agnosticism** - Agents work with any protocol
2. **Reasoning Agnosticism** - Protocols are independent of reasoning approaches
3. **Consistent Interfaces** - Standard interfaces across all protocols
4. **Dynamic Protocol Selection** - Runtime selection of appropriate protocol

## Protocol Registration

Agents register protocol handlers based on configuration:

```python
from openmas.agent import Agent
from openmas.protocols import A2AHTTPCommunicator, MCPSSECommunicator

class MultiProtocolAgent(Agent):
    async def setup(self):
        # Register protocols from configuration
        await self.register_protocols_from_config()
        
        # Or register protocols explicitly
        a2a = await self.register_protocol(
            "a2a-http",
            A2AHTTPCommunicator,
            options={
                "base_url": "http://localhost:8000",
                "agent_card": {
                    "name": self.agent_id,
                    "description": "Multi-protocol agent"
                }
            }
        )
        
        mcp = await self.register_protocol(
            "mcp-sse",
            MCPSSECommunicator,
            options={
                "server_mode": True,
                "http_port": 8080
            }
        )
        
        # Set up protocol event handlers
        a2a.on_message(self.handle_a2a_message)
        mcp.on_tool_call(self.handle_tool_call)
```

## Protocol-Specific Capabilities

Capabilities are automatically adapted to each protocol:

```python
class WeatherAgent(Agent):
    async def setup(self):
        # Register a capability
        self.register_capability(
            name="get_weather",
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
                        "description": "Current weather conditions"
                    }
                }
            }
        )
    
    @capability("get_weather")
    async def get_weather(self, location):
        # Protocol-agnostic implementation
        weather_data = await self.weather_service.fetch(location)
        return {
            "temperature": weather_data["temp"],
            "conditions": weather_data["conditions"]
        }
```

### A2A Protocol Exposure

The capability is automatically exposed as an A2A capability:

```json
{
  "name": "weather_agent",
  "capabilities": [
    {
      "name": "get_weather",
      "description": "Get current weather for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name or coordinates"
          }
        },
        "required": ["location"]
      }
    }
  ]
}
```

### MCP Protocol Exposure

The same capability is exposed as an MCP tool:

```json
{
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name or coordinates"
          }
        },
        "required": ["location"]
      }
    }
  ]
}
```

### HTTP Protocol Exposure

The capability is exposed as an HTTP endpoint:

```
GET /api/capabilities/get_weather?location=London
```

## Protocol-Specific Message Handling

Agents can handle protocol-specific messages:

```python
class NotificationAgent(Agent):
    async def setup(self):
        # Register protocols
        self.a2a = await self.register_protocol("a2a-http")
        self.mqtt = await self.register_protocol("mqtt")
        
        # Register protocol-specific handlers
        self.a2a.on_message(self.handle_a2a_message)
        self.mqtt.on_message(self.handle_mqtt_message)
    
    async def handle_a2a_message(self, message):
        # Handle A2A-specific message format
        if message.is_notification():
            await self.process_notification(message.content)
    
    async def handle_mqtt_message(self, topic, payload):
        # Handle MQTT-specific message format
        if topic.startswith("notifications/"):
            await self.process_notification(json.loads(payload))
```

## Cross-Protocol Communication

Agents can communicate across different protocols:

```python
class OrchestrationAgent(Agent):
    async def setup(self):
        # Register multiple protocols
        self.a2a = await self.register_protocol("a2a-http")
        self.mcp = await self.register_protocol("mcp-sse")
        self.http = await self.register_protocol("http")
        
        # Register capabilities
        self.register_capability("orchestrate_agents")
    
    @capability("orchestrate_agents")
    async def orchestrate_agents(self, task):
        results = []
        
        # Call an A2A agent
        a2a_result = await self.a2a.call_capability(
            agent_id="data_processing_agent",
            capability="process_data",
            parameters={"data": task["data"]}
        )
        results.append({"agent": "data_processor", "result": a2a_result})
        
        # Call an MCP agent
        mcp_result = await self.mcp.call_tool(
            tool="analyze_results",
            parameters={"results": a2a_result}
        )
        results.append({"agent": "analyzer", "result": mcp_result})
        
        # Call an HTTP agent
        http_result = await self.http.post(
            url="/api/reporting",
            json={"analysis": mcp_result}
        )
        results.append({"agent": "reporter", "result": http_result})
        
        return {
            "task_id": task["id"],
            "status": "completed",
            "results": results
        }
```

## Protocol Discovery

Agents can discover available protocols:

```python
class AdaptiveAgent(Agent):
    async def setup(self):
        # Discover available protocols for another agent
        agent_id = "target_agent"
        protocols = await self.discover_protocols(agent_id)
        
        # Select the optimal protocol
        selected_protocol = self.select_optimal_protocol(protocols)
        
        # Create appropriate communicator
        communicator = await self.create_communicator(
            protocol=selected_protocol,
            target=agent_id
        )
        
        # Use the selected protocol
        await communicator.send_message(
            agent_id=agent_id,
            message={"type": "greeting", "content": "Hello"}
        )
```

## Protocol-Specific Configuration

Agent protocol configuration uses the unified configuration schema. For the complete schema definition, see [Protocol Configuration Schema](/03_configuration/schema/protocols.md) and [Agent Configuration Schema](/03_configuration/schema/agents.md).

Key configuration sections:

```yaml
agents:
  multi_protocol_agent:
    class: "agents.MultiProtocolAgent"
    
    # Protocol configuration
    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8000"
          agent_card:
            name: "Multi-Protocol Agent"
            description: "Agent supporting multiple protocols"
      
      - type: "mcp-sse"
        enabled: true
        options:
          server_mode: true
          http_port: 8080
      
      - type: "mqtt"
        enabled: true
        options:
          broker_url: "mqtt://broker.example.com"
          topic_prefix: "agents/multi_protocol"
```

## Protocol Selection Strategies

Agents can use different strategies for selecting the appropriate protocol:

### Capability-Based Selection

```python
# Configure different protocols for different capabilities
protocol_mapping = {
    "get_weather": "a2a-http",
    "process_image": "mcp-sse",
    "stream_data": "websocket"
}

# Use the appropriate protocol based on capability
protocol = protocol_mapping.get(capability_name, "default_protocol")
result = await agent.invoke_capability(
    capability_name,
    parameters,
    protocol=protocol
)
```

### Priority-Based Selection

```python
# Configure protocol priorities
protocol_priorities = ["a2a-http", "mcp-sse", "http"]

# Try each protocol in order of priority
for protocol in protocol_priorities:
    try:
        result = await agent.invoke_capability(
            capability_name,
            parameters,
            protocol=protocol
        )
        break  # Success, stop trying other protocols
    except ProtocolUnavailableError:
        continue  # Try the next protocol
```

### Feature-Based Selection

```python
# Select protocol based on feature requirements
required_features = ["streaming", "binary_data"]

# Find protocols supporting all required features
compatible_protocols = agent.find_protocols_with_features(required_features)

if compatible_protocols:
    # Use the first compatible protocol
    result = await agent.invoke_capability(
        capability_name,
        parameters,
        protocol=compatible_protocols[0]
    )
```

## Reasoning Agnosticism in Protocol Integration

The protocol integration layer maintains OpenMAS's reasoning agnosticism by:

1. **Independent Message Processing** - Protocol handling is separate from reasoning logic
2. **Reasoning-Agnostic Interfaces** - Protocol interfaces don't assume specific reasoning approaches
3. **Uniform Capability Exposure** - Capabilities work the same regardless of reasoning approach
4. **Protocol Adaptation** - Messages are adapted between protocols without affecting reasoning

This enables agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to use the same protocols consistently.

## Best Practices

When integrating agents with protocols:

1. **Support Multiple Protocols** - Enable agents to work with multiple protocols for flexibility
2. **Use Protocol-Specific Features** - Leverage unique features of each protocol when beneficial
3. **Maintain Protocol Independence** - Keep core agent logic independent of specific protocols
4. **Handle Protocol Fallbacks** - Implement graceful fallbacks when preferred protocols are unavailable
5. **Configure Protocol-Specific Options** - Tune each protocol for optimal performance
6. **Monitor Protocol Usage** - Track protocol performance and usage patterns
