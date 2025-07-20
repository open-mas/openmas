# Protocol Adaptations for Communication Patterns

## Overview

A key capability of OpenMAS's communication patterns is their ability to adapt across different protocols. This document explains how patterns map to specific protocol implementations while maintaining consistent semantics, enabling OpenMAS's protocol independence and reasoning agnosticism.

## Adaptation Architecture

Protocol adaptation follows this architectural approach:

```
┌────────────────────────────────────────────────────────────────┐
│ Communication Pattern (Protocol-Agnostic)                      │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ Pattern Semantics and Behavior                            │ │
│ └────────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                           ▼                                    │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ Protocol Adapter Layer                                     │ │
│ └────────────────────────────────────────────────────────────┘ │
│      │               │               │               │         │
└──────┼───────────────┼───────────────┼───────────────┼─────────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ A2A Protocol │ │ MCP Protocol │ │ HTTP Protocol│ │ MQTT Protocol│
│ Adapter      │ │ Adapter      │ │ Adapter      │ │ Adapter      │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ A2A          │ │ MCP          │ │ HTTP         │ │ MQTT         │
│ Communicator │ │ Communicator │ │ Communicator │ │ Communicator │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## Protocol Adapter Interface

All protocol adapters implement a common interface:

```python
class ProtocolAdapter:
    """Base class for protocol adapters."""

    def __init__(self, protocol_name):
        """Initialize with protocol name."""
        self.protocol_name = protocol_name

    async def adapt_outgoing(self, message, pattern_name):
        """Adapt an outgoing message to this protocol."""
        raise NotImplementedError

    async def adapt_incoming(self, protocol_message, pattern_name):
        """Adapt an incoming protocol message to the pattern format."""
        raise NotImplementedError

    def get_pattern_options(self, pattern_name):
        """Get protocol-specific options for a pattern."""
        raise NotImplementedError
```

## Protocol Adapter Registry

Adapters are registered with a central registry:

```python
class ProtocolAdapterRegistry:
    """Registry for protocol adapters."""

    def __init__(self):
        """Initialize the registry."""
        self._adapters = {}

    def register(self, protocol_name, adapter_class):
        """Register an adapter for a protocol."""
        self._adapters[protocol_name] = adapter_class
        return self

    def get(self, protocol_name):
        """Get an adapter for a protocol."""
        adapter_class = self._adapters.get(protocol_name)
        if adapter_class:
            return adapter_class()
        return None
```

## Protocol-Specific Adapters

### A2A Protocol Adapter

```python
class A2AProtocolAdapter(ProtocolAdapter):
    """Adapts patterns to A2A protocol."""

    async def adapt_outgoing(self, message, pattern_name):
        """Adapt an outgoing message to A2A format."""
        # Get pattern-specific options
        options = self.get_pattern_options(pattern_name)

        if pattern_name == "request_response":
            return {
                "type": "request",
                "capability": options.get("capability_name", "request"),
                "content": message.get("content", {}),
                "correlation_id": message.get("correlation_id", str(uuid.uuid4()))
            }
        elif pattern_name == "publish_subscribe":
            return {
                "type": "publish",
                "capability": options.get("capability_name", "publish"),
                "content": {
                    "topic": message.get("topic"),
                    "message": message.get("message", {})
                }
            }
        # Additional patterns...

    async def adapt_incoming(self, protocol_message, pattern_name):
        """Adapt an incoming A2A message to the pattern format."""
        options = self.get_pattern_options(pattern_name)

        if pattern_name == "request_response":
            if protocol_message.get("type") == "response":
                return {
                    "content": protocol_message.get("content", {}),
                    "correlation_id": protocol_message.get("correlation_id"),
                    "status": protocol_message.get("status", "success")
                }
        # Additional patterns...

    def get_pattern_options(self, pattern_name):
        """Get A2A-specific options for a pattern."""
        # Default options for each pattern
        options = {
            "request_response": {
                "capability_name": "request",
                "response_capability": "response"
            },
            "publish_subscribe": {
                "capability_name": "publish",
                "subscribe_capability": "subscribe"
            },
            # Additional patterns...
        }

        return options.get(pattern_name, {})
```

### MCP Protocol Adapter

```python
class MCPProtocolAdapter(ProtocolAdapter):
    """Adapts patterns to MCP protocol."""

    async def adapt_outgoing(self, message, pattern_name):
        """Adapt an outgoing message to MCP format."""
        options = self.get_pattern_options(pattern_name)

        if pattern_name == "request_response":
            return {
                "type": "tool_call",
                "name": options.get("tool_name", "request"),
                "parameters": message.get("content", {}),
                "correlation_id": message.get("correlation_id", str(uuid.uuid4()))
            }
        elif pattern_name == "publish_subscribe":
            return {
                "type": "event",
                "name": options.get("event_name", "publish"),
                "data": {
                    "topic": message.get("topic"),
                    "message": message.get("message", {})
                }
            }
        # Additional patterns...

    async def adapt_incoming(self, protocol_message, pattern_name):
        """Adapt an incoming MCP message to the pattern format."""
        options = self.get_pattern_options(pattern_name)

        if pattern_name == "request_response":
            if protocol_message.get("type") == "tool_result":
                return {
                    "content": protocol_message.get("result", {}),
                    "correlation_id": protocol_message.get("correlation_id"),
                    "status": "error" if protocol_message.get("error") else "success"
                }
        # Additional patterns...

    def get_pattern_options(self, pattern_name):
        """Get MCP-specific options for a pattern."""
        # Default options for each pattern
        options = {
            "request_response": {
                "tool_name": "request",
                "result_type": "tool_result"
            },
            "publish_subscribe": {
                "event_name": "publish",
                "subscribe_event": "subscribe"
            },
            # Additional patterns...
        }

        return options.get(pattern_name, {})
```

### HTTP Protocol Adapter

```python
class HTTPProtocolAdapter(ProtocolAdapter):
    """Adapts patterns to HTTP protocol."""

    async def adapt_outgoing(self, message, pattern_name):
        """Adapt an outgoing message to HTTP format."""
        options = self.get_pattern_options(pattern_name)

        if pattern_name == "request_response":
            return {
                "method": options.get("method", "POST"),
                "url": message.get("url"),
                "headers": {
                    "Content-Type": "application/json",
                    "X-Correlation-ID": message.get("correlation_id", str(uuid.uuid4()))
                },
                "body": message.get("content", {})
            }
        elif pattern_name == "publish_subscribe":
            # For HTTP, publish is typically a POST to a webhook
            return {
                "method": "POST",
                "url": f"{options.get('base_url')}/publish",
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "topic": message.get("topic"),
                    "message": message.get("message", {})
                }
            }
        # Additional patterns...

    async def adapt_incoming(self, protocol_message, pattern_name):
        """Adapt an incoming HTTP message to the pattern format."""
        options = self.get_pattern_options(pattern_name)

        if pattern_name == "request_response":
            # Extract correlation ID from headers
            correlation_id = protocol_message.get("headers", {}).get("X-Correlation-ID")

            return {
                "content": protocol_message.get("body", {}),
                "correlation_id": correlation_id,
                "status": "success" if 200 <= protocol_message.get("status_code", 0) < 300 else "error"
            }
        # Additional patterns...

    def get_pattern_options(self, pattern_name):
        """Get HTTP-specific options for a pattern."""
        # Default options for each pattern
        options = {
            "request_response": {
                "method": "POST",
                "response_codes": [200, 201]
            },
            "publish_subscribe": {
                "base_url": "/api",
                "subscribe_endpoint": "/subscribe"
            },
            # Additional patterns...
        }

        return options.get(pattern_name, {})
```

### MQTT Protocol Adapter

```python
class MQTTProtocolAdapter(ProtocolAdapter):
    """Adapts patterns to MQTT protocol."""

    async def adapt_outgoing(self, message, pattern_name):
        """Adapt an outgoing message to MQTT format."""
        options = self.get_pattern_options(pattern_name)

        if pattern_name == "request_response":
            correlation_id = message.get("correlation_id", str(uuid.uuid4()))
            request_topic = options.get("request_topic", "requests/{agent_id}")
            request_topic = request_topic.format(agent_id=message.get("recipient"))

            return {
                "topic": request_topic,
                "payload": {
                    "content": message.get("content", {}),
                    "correlation_id": correlation_id,
                    "response_topic": options.get("response_topic", "responses/{sender_id}").format(
                        sender_id=message.get("sender")
                    )
                }
            }
        elif pattern_name == "publish_subscribe":
            topic = message.get("topic")
            if not topic.startswith(options.get("topic_prefix", "")):
                topic = f"{options.get('topic_prefix', '')}/{topic}"

            return {
                "topic": topic,
                "payload": message.get("message", {}),
                "qos": options.get("qos", 0),
                "retain": options.get("retain", False)
            }
        # Additional patterns...

    async def adapt_incoming(self, protocol_message, pattern_name):
        """Adapt an incoming MQTT message to the pattern format."""
        options = self.get_pattern_options(pattern_name)

        if pattern_name == "request_response":
            payload = protocol_message.get("payload", {})

            return {
                "content": payload.get("content", {}),
                "correlation_id": payload.get("correlation_id"),
                "status": payload.get("status", "success")
            }
        elif pattern_name == "publish_subscribe":
            topic = protocol_message.get("topic", "")
            prefix = options.get("topic_prefix", "")

            if topic.startswith(prefix):
                topic = topic[len(prefix):].lstrip("/")

            return {
                "topic": topic,
                "message": protocol_message.get("payload", {})
            }
        # Additional patterns...

    def get_pattern_options(self, pattern_name):
        """Get MQTT-specific options for a pattern."""
        # Default options for each pattern
        options = {
            "request_response": {
                "request_topic": "requests/{agent_id}",
                "response_topic": "responses/{sender_id}",
                "qos": 1
            },
            "publish_subscribe": {
                "topic_prefix": "pubsub",
                "qos": 0,
                "retain": False
            },
            # Additional patterns...
        }

        return options.get(pattern_name, {})
```

## Pattern-Specific Adaptations

Each communication pattern defines how it adapts to different protocols.

### Request-Response Pattern

```yaml
# Request-Response adaptations
request_response:
  a2a:
    capability_name: "request"
    response_capability: "response"

  mcp:
    tool_name: "request"
    result_type: "tool_result"

  http:
    method: "POST"
    response_codes: [200, 201]

  mqtt:
    request_topic: "requests/{agent_id}"
    response_topic: "responses/{sender_id}"
    qos: 1

  grpc:
    service: "RequestService"
    method: "MakeRequest"
```

### Publish-Subscribe Pattern

```yaml
# Publish-Subscribe adaptations
publish_subscribe:
  a2a:
    capability_name: "publish"
    subscribe_capability: "subscribe"

  mcp:
    event_name: "publish"
    subscribe_event: "subscribe"

  http:
    publish_endpoint: "/publish"
    subscribe_endpoint: "/subscribe"

  mqtt:
    topic_prefix: "pubsub"
    qos: 0
    retain: false

  grpc:
    service: "PubSubService"
    publish_method: "Publish"
    subscribe_method: "Subscribe"
```

### Delegation Pattern

```yaml
# Delegation adaptations
delegation:
  a2a:
    capability_name: "delegate"
    progress_capability: "progress"
    result_capability: "result"

  mcp:
    tool_name: "delegate"
    progress_event: "progress"
    result_type: "task_result"

  http:
    delegate_endpoint: "/delegate"
    progress_endpoint: "/progress"
    result_endpoint: "/result"

  mqtt:
    task_topic: "tasks/{agent_id}"
    progress_topic: "progress/{task_id}"
    result_topic: "results/{task_id}"

  grpc:
    service: "TaskService"
    delegate_method: "DelegateTask"
    progress_method: "TrackProgress"
    result_method: "GetResult"
```

### Pipeline Pattern

```yaml
# Pipeline adaptations
pipeline:
  a2a:
    capability_name: "pipeline_step"

  mcp:
    tool_name: "pipeline_process"

  http:
    endpoint: "/pipeline/{pipeline_id}/step/{step_id}"

  mqtt:
    input_topic: "pipeline/{pipeline_id}/input/{step_id}"
    output_topic: "pipeline/{pipeline_id}/output/{step_id}"

  grpc:
    service: "PipelineService"
    method: "ProcessStep"
```

### Event-Based Pattern

```yaml
# Event-Based adaptations
event_based:
  a2a:
    capability_name: "broadcast_event"
    handler_capability: "handle_event"

  mcp:
    event_name: "broadcast"
    handler_registration: "register_handler"

  http:
    broadcast_endpoint: "/events/broadcast"
    handler_endpoint: "/events/handlers"

  mqtt:
    event_topic: "events/{event_type}"
    handler_topic: "handlers/{handler_id}"

  grpc:
    service: "EventService"
    broadcast_method: "BroadcastEvent"
    register_method: "RegisterHandler"
```

### Streaming Pattern

```yaml
# Streaming adaptations
streaming:
  a2a:
    capability_name: "stream"

  mcp:
    incremental_response: true
    stream_tool: "create_stream"

  http:
    mode: "sse"  # or "websocket"
    endpoint: "/streams/{stream_id}"

  mqtt:
    data_topic: "streams/{stream_id}/data"
    control_topic: "streams/{stream_id}/control"

  grpc:
    service: "StreamService"
    method: "StreamData"
    bidirectional: true
```

## Protocol-Specific Features

Each protocol offers unique features that can enhance communication patterns:

### HTTP Protocol Features

1. **REST Semantics** - Leveraging HTTP methods (GET, POST, PUT, DELETE)
2. **Status Codes** - Using standard HTTP status codes for responses
3. **Headers** - Using headers for metadata and correlation
4. **Content Negotiation** - Supporting different content types
5. **Caching** - Utilizing HTTP caching mechanisms

### MQTT Protocol Features

1. **QoS Levels** - Different quality of service guarantees
2. **Retained Messages** - Last message persistence
3. **Wild Card Subscriptions** - Pattern-based topic subscriptions
4. **Topic Hierarchies** - Structured topic namespaces
5. **Last Will and Testament** - Messages sent on abnormal disconnection

### gRPC Protocol Features

1. **Service Definitions** - Well-defined service contracts
2. **Streaming** - Unary, server, client, and bidirectional streaming
3. **Binary Protocol** - Efficient binary serialization
4. **Deadline Propagation** - Request timeouts and cancellation
5. **Flow Control** - Built-in backpressure mechanisms

## A2A Protocol Features

1. **Agent Cards** - Agent capability discovery
2. **Named Capabilities** - Standardized capability interfaces
3. **Extensible Schema** - JSON Schema capability definitions
4. **Context Windows** - Context-aware capability invocation
5. **Function Calling** - Capability as function calling abstraction

## MCP Protocol Features

1. **Tool Calling** - Function calling interface
2. **Incremental Responses** - Streaming results
3. **Event System** - Event-based notifications
4. **Streaming Support** - Bidirectional streaming
5. **Context Management** - Context window handling

## Protocol Selection

When selecting a protocol for a pattern, consider:

1. **Latency Requirements** - Real-time vs. batch processing
2. **Reliability Needs** - Delivery guarantees
3. **Payload Size** - Small messages vs. large payloads
4. **Connection Persistence** - Long-lived vs. ephemeral connections
5. **Topology Considerations** - Number and distribution of agents

## Protocol Extension

To add a new protocol to the adaptation system:

1. **Create Protocol Adapter**: Implement the ProtocolAdapter interface
2. **Define Pattern Mappings**: Map each pattern to protocol-specific concepts
3. **Implement Communicator**: Create a communicator that works with the protocol
4. **Register with Registry**: Register the adapter and communicator
5. **Define Configuration Schema**: Add protocol-specific configuration options

## Reasoning Agnosticism

The protocol adaptation system maintains OpenMAS's reasoning agnosticism by:

1. **Semantic Consistency** - Same pattern semantics across all protocols
2. **Communication Abstraction** - Protocols abstract the physical communication
3. **Content Agnosticism** - Messages adapt without interpreting content
4. **Interface Consistency** - Same interfaces regardless of reasoning approach
5. **Extensibility** - Support for new protocols without changing patterns

This enables agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to communicate using the same patterns consistently, regardless of the underlying protocol.
