# Communication Patterns Standard

## Pattern Definition
- **Name**: Communication Patterns
- **Purpose**: Standardized approaches for message exchange between agents
- **Protocol Compatibility**: Works with all protocols (A2A, MCP, HTTP, MQTT, gRPC)
- **Reasoning Agnosticism**: Maintains separation between message exchange patterns and reasoning approaches
- **Topology Independence**: Can be applied within any agent topology (centralized, peer-to-peer, hierarchical, mesh)

## Communication Pattern Schema
```yaml
# Standardized communication pattern configuration schema (within unified schema)
defaults:
  communication_patterns:
    # Pattern definitions by name
    request_response:
      type: object
      description: "Request-response pattern configuration"
      properties:
        # Pattern-specific options
        options:
          type: object
          properties:
            timeout:
              type: integer
              description: "Timeout in seconds"
              default: 30
            retry:
              type: object
              properties:
                enabled:
                  type: boolean
                  default: true
                max_attempts:
                  type: integer
                  default: 3
                backoff:
                  type: string
                  enum: ["fixed", "exponential", "linear"]
                  default: "exponential"

    publish_subscribe:
      type: object
      description: "Publish-subscribe pattern configuration"
      properties:
        # Pattern-specific options
        options:
          type: object
          properties:
            qos:
              type: integer
              description: "Quality of service level"
              enum: [0, 1, 2]
              default: 1
            retain:
              type: boolean
              description: "Whether to retain the message"
              default: false

    event_based:
      type: object
      description: "Event-based pattern configuration"
      properties:
        # Pattern-specific options
        options:
          type: object
          properties:
            event_buffer:
              type: integer
              description: "Event buffer size"
              default: 100
            delivery_guarantee:
              type: string
              enum: ["at-least-once", "at-most-once", "exactly-once"]
              default: "at-least-once"

    streaming:
      type: object
      description: "Streaming pattern configuration"
      properties:
        # Pattern-specific options
        options:
          type: object
          properties:
            buffer_size:
              type: integer
              description: "Stream buffer size"
              default: 1024
            chunk_size:
              type: integer
              description: "Chunk size for transmission"
              default: 4096

    # Protocol-specific adaptations for patterns
    protocol_adaptations:
      a2a:
        type: object
        description: "A2A protocol adaptations"
        properties:
          # (specific adaptations)

      mcp:
        type: object
        description: "MCP protocol adaptations"
        properties:
          # (specific adaptations)

      http:
        type: object
        description: "HTTP protocol adaptations"
        properties:
          method:
            type: string
            description: "HTTP method for the pattern"
            enum: ["GET", "POST", "PUT", "DELETE", "PATCH"]
          status_codes:
            type: object
            description: "HTTP status codes for pattern outcomes"
```

## Standard Communication Patterns

### 1. Request-Response

The request-response pattern involves an agent making a specific request and expecting a response from another agent.

#### Schema

```yaml
request_response:
  timeout: 30  # seconds
  retry:
    enabled: true
    max_attempts: 3
    backoff: "exponential"
```

#### Protocol Implementations

##### A2A Protocol
```json
{
  "type": "request",
  "capability": "weather_forecast",
  "content": {
    "location": "San Francisco",
    "units": "celsius"
  },
  "correlation_id": "request-123"
}
```

Response:
```json
{
  "type": "response",
  "content": {
    "temperature": 22,
    "conditions": "Sunny"
  },
  "correlation_id": "request-123"
}
```

##### MCP Protocol
```json
{
  "type": "tool_call",
  "name": "get_weather",
  "parameters": {
    "location": "San Francisco",
    "units": "celsius"
  }
}
```

Response:
```json
{
  "type": "tool_result",
  "result": {
    "temperature": 22,
    "conditions": "Sunny"
  }
}
```

#### Usage Example
```python
# Agent making a request
response = await agent.request(
    target_agent="weather_agent",
    capability="get_weather",
    content={"location": "San Francisco"},
    options={"timeout": 30}
)
```

### 2. Publish-Subscribe

The publish-subscribe pattern allows agents to publish messages to topics that other agents can subscribe to.

#### Schema

```yaml
publish_subscribe:
  qos: 1
  retain: false
```

#### Protocol Implementations

##### A2A Protocol
```json
{
  "type": "publish",
  "topic": "weather/updates",
  "content": {
    "location": "San Francisco",
    "temperature": 22
  }
}
```

Subscription:
```json
{
  "type": "subscribe",
  "topic": "weather/updates"
}
```

##### MQTT Protocol
```
PUBLISH weather/updates {"location":"San Francisco","temperature":22}
```

#### Usage Example
```python
# Publisher agent
await agent.publish(
    topic="weather/updates",
    content={"location": "San Francisco", "temperature": 22}
)

# Subscriber agent
await agent.subscribe(
    topic="weather/updates",
    handler=handle_weather_update
)
```

### 3. Event-Based

The event-based pattern allows agents to trigger and react to events without direct coupling.

#### Schema

```yaml
event_based:
  event_buffer: 100
  delivery_guarantee: "at-least-once"
```

#### Protocol Implementations

##### A2A Protocol
```json
{
  "type": "event",
  "name": "temperature_alert",
  "content": {
    "location": "San Francisco",
    "temperature": 35,
    "severity": "high"
  },
  "event_id": "evt-123"
}
```

##### HTTP Webhook
```json
POST /webhook/temperature_alert
{
  "location": "San Francisco",
  "temperature": 35,
  "severity": "high",
  "timestamp": "2023-10-15T14:30:00Z"
}
```

#### Usage Example
```python
# Trigger an event
await agent.trigger_event(
    event="temperature_alert",
    content={
        "location": "San Francisco",
        "temperature": 35,
        "severity": "high"
    }
)

# Register event handler
agent.on_event("temperature_alert", handle_temperature_alert)
```

### 4. Streaming

The streaming pattern enables continuous data flow between agents.

#### Schema

```yaml
streaming:
  buffer_size: 1024
  chunk_size: 4096
```

#### Protocol Implementations

##### A2A Protocol
```json
{
  "type": "stream_start",
  "stream_id": "stream-123",
  "content_type": "text/plain"
}

{
  "type": "stream_data",
  "stream_id": "stream-123",
  "sequence": 1,
  "content": "Chunk of data..."
}

{
  "type": "stream_end",
  "stream_id": "stream-123"
}
```

##### HTTP Server-Sent Events
```
event: weather_update
data: {"location":"San Francisco","temperature":22}

event: weather_update
data: {"location":"San Francisco","temperature":23}
```

#### Usage Example
```python
# Create a stream
stream = await agent.create_stream(content_type="text/plain")

# Write to stream
await stream.write("First chunk of data")
await stream.write("Second chunk of data")
await stream.close()

# Read from stream
async for chunk in other_agent.receive_stream(stream_id):
    process_chunk(chunk)
```

### 5. Delegation

The delegation pattern allows agents to delegate tasks or capabilities to other agents.

#### Schema

```yaml
delegation:
  verification: true
  escalation_policy: "retry"
```

#### Protocol Implementations

##### A2A Protocol
```json
{
  "type": "delegate",
  "capability": "image_processing",
  "content": {
    "image_url": "https://example.com/image.jpg",
    "operations": ["resize", "crop"]
  },
  "delegation_id": "task-123"
}
```

Response:
```json
{
  "type": "delegation_result",
  "delegation_id": "task-123",
  "status": "completed",
  "content": {
    "processed_url": "https://example.com/processed.jpg"
  }
}
```

#### Usage Example
```python
# Delegate a task
result = await agent.delegate(
    target_agent="image_processor",
    capability="process_image",
    content={
        "image_url": "https://example.com/image.jpg",
        "operations": ["resize", "crop"]
    }
)
```

### 6. Permission-Based

The permission-based pattern enforces access control between agents based on capabilities.

#### Schema

```yaml
permission_based:
  verification_level: "capability"
  authorization_cache: true
```

#### Protocol Implementations

##### A2A Protocol
```json
{
  "type": "grant_permission",
  "target_agent": "assistant_agent",
  "capability": "get_weather",
  "constraints": {
    "max_calls_per_day": 100,
    "locations": ["San Francisco", "New York"]
  }
}
```

#### Use Cases
- **Use Cases**: Hierarchical agent systems, authority distribution, task specialization
- **Protocol Implementations**:
  - **A2A**: Capability granting
  - **MCP**: Delegated tool access
  - **HTTP**: API tokens with scoped permissions

## Example Implementation

### Request-Response Pattern

```python
from openmas.patterns import RequestResponsePattern
from openmas.agents import Agent

class WeatherAgent(Agent):
    async def setup(self):
        # Register capability with request-response pattern
        self.register_capability(
            "get_weather",
            self.get_weather,
            pattern=RequestResponsePattern(
                timeout=30,
                retry={"enabled": True, "max_attempts": 3}
            )
        )

    async def get_weather(self, request):
        location = request.get("location", "default")
        # Get weather data
        return {
            "temperature": 22,
            "conditions": "Sunny"
        }

class ClientAgent(Agent):
    async def run(self):
        # Use request-response pattern
        try:
            response = await self.request(
                target_agent="weather_agent",
                capability="get_weather",
                content={"location": "San Francisco"}
            )
            print(f"Weather: {response['temperature']}°C, {response['conditions']}")
        except Exception as e:
            print(f"Request failed: {e}")
```

### Publish-Subscribe Pattern

```python
from openmas.patterns import PublishSubscribePattern
from openmas.agents import Agent

class WeatherStation(Agent):
    async def setup(self):
        # Register publisher with publish-subscribe pattern
        self.register_publisher(
            "weather_updates",
            pattern=PublishSubscribePattern(
                qos=1,
                retain=False
            )
        )

    async def run(self):
        # Publish weather updates periodically
        while True:
            await self.publish(
                topic="weather/updates",
                content={"location": "San Francisco", "temperature": 22}
            )
            await asyncio.sleep(600)  # Update every 10 minutes

class WeatherDisplay(Agent):
    async def setup(self):
        # Subscribe to weather updates
        self.subscribe(
            topic="weather/updates",
            handler=self.display_weather
        )

    async def display_weather(self, content):
        print(f"Weather update for {content['location']}: {content['temperature']}°C")
```
