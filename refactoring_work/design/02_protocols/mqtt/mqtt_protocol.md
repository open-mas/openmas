# MQTT Protocol

## Protocol Definition

- **Name**: Message Queuing Telemetry Transport (MQTT)
- **Purpose**: Lightweight publish-subscribe messaging transport for IoT and agent communication
- **Specification Reference**: [MQTT v5.0](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html), [MQTT v3.1.1](http://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
- **OpenMAS Implementation Status**: Fully Supported
- **Reasoning Agnosticism**: Complete separation between MQTT communication layer and agent reasoning approaches
- **Protocol Independence**: Can interoperate with other protocols through OpenMAS protocol adapters

## Protocol Overview

MQTT (Message Queuing Telemetry Transport) is a lightweight, publish-subscribe messaging protocol designed for constrained devices and low-bandwidth, high-latency, or unreliable networks. It is ideal for Internet of Things (IoT) applications and distributed agent systems that require efficient communication with minimal overhead.

OpenMAS implements MQTT as a first-class protocol, maintaining the framework's core principle of reasoning agnosticism. This allows agents with different reasoning approaches to communicate effectively through MQTT topics while preserving the clean separation between the communication layer ("body") and reasoning layer ("brain").

## Protocol Features

### Core Features

1. **Publish-Subscribe Messaging**
   - Topic-based message routing
   - Multi-level topic hierarchies with wildcards
   - Retained messages for state persistence
   - Last Will and Testament messages
   - Quality of Service levels (QoS 0, 1, 2)

2. **Lightweight Communication**
   - Minimal protocol overhead
   - Efficient binary packet format
   - Low bandwidth consumption
   - Battery-friendly for constrained devices
   - Small code footprint

3. **Reliability Features**
   - Session persistence
   - Durable subscriptions
   - Message queuing for offline clients
   - Automatic reconnection handling
   - Unacknowledged message tracking

### Extended Features

OpenMAS extends MQTT with additional features for agent communication:

1. **Enhanced Security**
   - TLS/SSL support with certificate validation
   - Username/password authentication
   - OAuth token authentication
   - Access control lists (ACLs)
   - Topic permission management

2. **Protocol Bridging**
   - Translation between MQTT and other protocols
   - Topic-to-endpoint mapping
   - Message format conversion
   - QoS level translation
   - Session state management

3. **Agent-Specific Extensions**
   - Automatic topic namespacing for agents
   - Capability advertisement over MQTT
   - Dynamic topic discovery
   - Heartbeat mechanisms
   - Agent presence detection

## OpenMAS Implementation

### Architecture Integration

The MQTT protocol implementation in OpenMAS integrates with the core components as follows:

1. **Agent Framework**: MQTT topics map to agent capabilities and messaging patterns
2. **Event System**: MQTT's pub-sub model aligns naturally with OpenMAS's event system
3. **Configuration System**: MQTT broker settings and topic structures are configured through the unified schema
4. **Security System**: MQTT authentication and ACLs integrate with OpenMAS's security framework

#### Component Interactions

```
┌────────────────┐      ┌─────────────────┐      ┌────────────────┐
│  Agent (Brain) │      │ OpenMAS Core    │      │ MQTT Client    │
│                │◄────►│                 │◄────►│                │
└────────────────┘      └─────────────────┘      └────────────────┘
                              │                         │
                              │                         │
                        ┌─────▼─────┐             ┌─────▼─────┐
                        │ Topic     │             │  MQTT     │
                        │ Registry  │             │  Broker   │
                        └───────────┘             └───────────┘
```

### Configuration

The MQTT protocol is configured through the unified configuration schema.

For complete schema information, refer to the [Protocol Configuration Schema](/03_configuration/schema/protocols.md#mqtt-protocol-configuration).

Example minimal configuration:

```yaml
protocols:
  - type: "mqtt"
    enabled: true
    options:
      broker_url: "mqtt://broker.example.com"
      mqtt_port: 1883
      client_id: "agent_1234"
      topic_prefix: "openmas/agents"
      qos: 1
```

## Message Structure

### Topic Structure

OpenMAS uses a standardized MQTT topic structure:

```
openmas/agents/{agent_id}/{capability}/{operation}
```

Examples:
- `openmas/agents/weather_agent/forecasts/daily`
- `openmas/agents/inventory_agent/stock/updates`
- `openmas/agents/+/status` (wildcard subscription for all agent statuses)

### Publish Message Format

Standard JSON payload format for publishing messages:

```json
{
  "message_id": "msg-123456",
  "timestamp": "2025-05-19T01:47:38Z",
  "content_type": "application/json",
  "data": {
    "temperature": 22.5,
    "humidity": 65,
    "conditions": "Partly Cloudy",
    "location": "San Francisco"
  },
  "metadata": {
    "source": "weather_sensor_1",
    "reliability": 0.95
  }
}
```

### Subscribe Message Format

Subscription request structure:

```json
{
  "topics": ["openmas/agents/weather_agent/forecasts/+"],
  "qos": 1,
  "subscription_id": "sub-789",
  "options": {
    "retain_handling": "send",
    "no_local": false
  }
}
```

### Error Handling

Error messages follow a standard format:

```json
{
  "error": true,
  "code": "connection_lost",
  "message": "Connection to broker lost",
  "timestamp": "2025-05-19T01:48:12Z",
  "context": {
    "topic": "openmas/agents/weather_agent/forecasts/daily",
    "message_id": "msg-123456"
  }
}
```

## Communication Patterns

The MQTT protocol in OpenMAS supports several communication patterns. For a complete documentation of each pattern, please refer to the dedicated communication patterns documentation.

| Pattern | Implementation in MQTT | Reference |
|---------|------------------------|----------|
| **Publish-Subscribe** | Native MQTT pattern using topics and subscriptions | [Publish-Subscribe Pattern](/07_communication_patterns/patterns/publish_subscribe.md) |
| **Request-Response** | Implemented using topic pairs and correlation IDs | [Request-Response Pattern](/07_communication_patterns/patterns/request_response.md) |
| **Event-Based** | Notification of state changes via retained messages | [Event-Based Pattern](/07_communication_patterns/patterns/event_based.md) |

For a complete mapping of all protocols to communication patterns, see the [Protocol to Pattern Mapping](/02_protocols/protocol_to_pattern_mapping.md) document.

## Security Considerations

1. **Authentication**
   - Username/password authentication
   - TLS client certificates
   - JWT token authentication
   - Custom authentication plugins

2. **Authorization**
   - Topic-based access control
   - Subscription limitations
   - Publish restrictions
   - QoS limitations

3. **Data Protection**
   - TLS encryption for all communications
   - Payload encryption for sensitive data
   - Topic namespacing for isolation
   - Secure broker configuration

## Usage Examples

### Example 1: MQTT Publisher Implementation

```python
# MQTT publisher implementation in an agent
from openmas.protocols.mqtt import MQTTClient
from openmas.agents import Agent
import json

class WeatherPublisherAgent(Agent):
    async def setup(self):
        # Initialize MQTT client
        self.mqtt_client = await self.setup_protocol("mqtt", {
            "broker_url": "mqtt://broker.example.com",
            "client_id": "weather_publisher_agent",
            "topic_prefix": "openmas/agents/weather"
        })

        # Set up periodic data publishing
        self.add_task(self.publish_weather_data, interval=300)  # every 5 minutes

    async def publish_weather_data(self):
        # Get weather data
        weather_data = await self.weather_service.get_current()

        # Format message
        message = {
            "message_id": self.generate_id(),
            "timestamp": self.get_timestamp(),
            "data": weather_data,
            "metadata": {
                "source": "national_weather_service",
                "location": "san-francisco"
            }
        }

        # Publish to topic
        result = await self.mqtt_client.publish(
            "forecasts/current",  # Will be prefixed with topic_prefix
            json.dumps(message),
            qos=1,
            retain=True
        )

        if result.is_published:
            self.log.info(f"Published weather data with ID {message['message_id']}")
        else:
            self.log.error(f"Failed to publish weather data: {result.error}")
```

### Example 2: MQTT Subscriber Implementation

```python
# MQTT subscriber implementation in an agent
from openmas.protocols.mqtt import MQTTClient
from openmas.agents import Agent
import json

class WeatherMonitorAgent(Agent):
    async def setup(self):
        # Initialize MQTT client
        self.mqtt_client = await self.setup_protocol("mqtt", {
            "broker_url": "mqtt://broker.example.com",
            "client_id": "weather_monitor_agent",
            "topic_prefix": "openmas/agents"
        })

        # Subscribe to weather topics
        await self.mqtt_client.subscribe(
            "weather/forecasts/#",  # Will be prefixed with topic_prefix
            qos=1,
            callback=self.handle_weather_update
        )

        self.log.info("Subscribed to weather forecast topics")

    async def handle_weather_update(self, topic, payload, properties):
        try:
            # Parse message
            message = json.loads(payload)

            # Extract data
            weather_data = message.get("data", {})
            metadata = message.get("metadata", {})

            # Process the weather update
            location = metadata.get("location", "unknown")
            temperature = weather_data.get("temperature")
            conditions = weather_data.get("conditions")

            self.log.info(f"Weather update for {location}: {temperature}°C, {conditions}")

            # Take appropriate actions based on the weather
            await self.evaluate_weather_conditions(location, weather_data)

        except Exception as e:
            self.log.error(f"Error processing weather update: {e}")

    async def evaluate_weather_conditions(self, location, weather_data):
        # Agent-specific logic to evaluate and respond to weather conditions
        if weather_data.get("alerts"):
            await self.notify_weather_alert(location, weather_data["alerts"])
```

## Interoperability

### Protocol Bridging

OpenMAS provides bidirectional bridging between MQTT and other protocols:

1. **MQTT ↔ HTTP**: Topic events mapped to webhooks and vice versa
2. **MQTT ↔ WebSocket**: Real-time web communication through MQTT topics
3. **MQTT ↔ A2A**: MQTT topics mapped to A2A agent capabilities
4. **MQTT ↔ gRPC**: High-performance bridging between streaming gRPC and MQTT

### External Systems Integration

MQTT in OpenMAS can integrate with:

1. **IoT Platforms**: Seamless integration with IoT devices and platforms
2. **Message Brokers**: Connection to enterprise messaging systems
3. **Event Streams**: Integration with event streaming platforms
4. **Cloud Services**: MQTT services from cloud providers

## Performance Considerations

1. **Scalability**
   - Support for clustered MQTT brokers
   - Connection sharing across agent instances
   - Topic filtering optimization
   - Message batching for high-throughput scenarios

2. **Efficiency**
   - QoS level selection based on message importance
   - Topic structure optimization
   - Payload compression for large messages
   - Keep-alive interval tuning

## Protocol Limitations

1. **Message Size**: Some brokers limit maximum message size
2. **Topic Limitations**: Maximum topic length and hierarchy depth varies by broker
3. **QoS Overhead**: Higher QoS levels add protocol overhead
4. **State Management**: Requires additional mechanisms for complex state management

## Future Roadmap

1. **MQTT 5.0 Features**: Full support for all MQTT 5.0 features
2. **Shared Subscriptions**: Enhanced support for load balancing with shared subscriptions
3. **Message Schemas**: Schema validation for MQTT messages
4. **Semantic Topics**: Topic organization based on semantic relationships

## Related Documentation

- [Protocol Schema Documentation](/03_configuration/schema/protocols.md#mqtt-protocol-configuration)
- [Communication Patterns](/07_communication_patterns/protocol_patterns.md)
- [Protocol Adaptations](/07_communication_patterns/protocol_adaptations.md)
- [MQTT Security Configuration](/03_configuration/security_configuration.md#mqtt-protocol-security)
