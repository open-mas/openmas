# Protocol Adaptations for Communication Patterns

## Overview

A key capability of OpenMAS's communication patterns is their ability to adapt across different protocols. This document explains how patterns map to specific protocol implementations while maintaining consistent semantics, enabling OpenMAS's protocol independence.

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

## Adaptation Components

Protocol adaptation relies on these key components:

### 1. Formal Protocol Adapter Interface (`IProtocolAdapter`)

The connection between a protocol-agnostic communication pattern and a specific transport protocol is handled by a series of adapters, each implementing the `IProtocolAdapter` interface. This interface defines a formal contract for translating Standard Internal Message Format (SIMF) messages into the native format of a given protocol, and vice-versa.

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

# Assume SIMF is defined and available
# from ...internal_message_format_standard import StandardInternalMessageFormat as SIMF

class IProtocolAdapter(ABC):
    """Interface for adapting communication patterns to a specific protocol."""

    @abstractmethod
    async def to_protocol_format(self, message: SIMF) -> Any:
        """Translates a SIMF message into the native protocol's format.

        This method inspects the message's type and payload to determine the correct
        transformation logic based on the communication pattern being used.

        Args:
            message: The protocol-agnostic SIMF message.

        Returns:
            A message formatted for the specific protocol (e.g., an HTTP request object,
            an A2A task dictionary).
        """
        pass

    @abstractmethod
    async def from_protocol_format(self, protocol_message: Any) -> SIMF:
        """Translates a native protocol message back into a SIMF message.

        Args:
            protocol_message: The message received from the transport layer.

        Returns:
            A SIMF message that can be processed by the agent framework.
        """
        pass

    @abstractmethod
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> SIMF:
        """Handles a protocol-specific error, translating it into a SIMF error message.

        Args:
            error: The exception raised by the protocol communicator.
            context: Additional context about the failed operation.

        Returns:
            A SIMF message with an ERROR_MESSAGE type.
        """
        pass
```

### 2. Protocol-Specific Adapters

Each protocol has specific adapter implementations:

```python
class A2AProtocolAdapter(ProtocolAdapter):
    """Adapts patterns to A2A protocol."""

    async def process_incoming(self, message, pattern):
        """Process an incoming A2A message."""
        # Extract relevant parts from A2A message
        # Map to pattern-specific format
        return transformed_message

    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing A2A message."""
        # Transform internal message to A2A format
        # Apply pattern-specific formatting
        return a2a_message

class MCPProtocolAdapter(ProtocolAdapter):
    """Adapts patterns to MCP protocol."""

    async def process_incoming(self, message, pattern):
        """Process an incoming MCP message."""
        # Extract relevant parts from MCP message
        # Map to pattern-specific format
        return transformed_message

    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing MCP message."""
        # Transform internal message to MCP format
        # Apply pattern-specific formatting
        return mcp_message
```

### 3. Protocol Adapter Factory (`IProtocolAdapterFactory`)

The `Pattern Engine` uses a factory to retrieve the correct adapter for a given protocol. This factory implements the `IProtocolAdapterFactory` interface.

```python
class IProtocolAdapterFactory(ABC):
    """Interface for a factory that creates protocol-specific adapters."""

    @abstractmethod
    def get_adapter(self, protocol_name: str, config: Dict[str, Any]) -> IProtocolAdapter:
        """Retrieves a configured instance of a protocol adapter.

        Args:
            protocol_name: The name of the protocol (e.g., 'http', 'a2a').
            config: Configuration for the adapter.

        Returns:
            An instance of a class that implements IProtocolAdapter.

        Raises:
            ValueError: If the protocol_name is not supported.
        """
        pass

# Example Implementation
class ProtocolAdapterFactory(IProtocolAdapterFactory):
    """Concrete factory for creating protocol adapters."""

    def __init__(self):
        """Initialize the factory."""
        self.adapter_classes = {
            "a2a": A2AProtocolAdapter,
            "mcp": MCPProtocolAdapter,
            "http": HTTPProtocolAdapter,
            "mqtt": MQTTProtocolAdapter,
            "redis": RedisProtocolAdapter,
            "grpc": GRPCProtocolAdapter
        }

    def create_adapter(self, protocol, config):
        """Create a protocol adapter."""
        if protocol not in self.adapter_classes:
            raise ValueError(f"Unsupported protocol: {protocol}")

        adapter_class = self.adapter_classes[protocol]
        return adapter_class(config)
```

## A2A Protocol Adaptation

### A2A Protocol Capabilities

The A2A protocol offers these key capabilities:

1. **Task-Based Messaging** - Tasks with inputs and outputs
2. **Streaming Support** - Chunked data transfer
3. **Artifacts** - Shared resources between tasks
4. **Function Calling** - Function-based interaction

### A2A Pattern Mappings

Here's how patterns map to A2A protocol features:

#### Request-Response Pattern

```yaml
request_response:
  protocol_adaptations:
    a2a:
      use_tasks: true
      task_type: "request_response"
      response_timeout: 30000
```

**Implementation:**

```python
class A2ARequestResponseAdapter(ProtocolAdapter):
    async def prepare_outgoing(self, message, pattern):
        # Create an A2A task for the request
        task = {
            "type": self.config.get("task_type", "request_response"),
            "input": message.get("content"),
            "metadata": {
                "pattern": "request_response",
                "request_id": message.get("id"),
                "timeout": self.config.get("response_timeout", 30000)
            }
        }
        return task

    async def process_incoming(self, message, pattern):
        # Extract response from A2A task output
        return {
            "id": message.get("metadata", {}).get("request_id"),
            "content": message.get("output"),
            "metadata": {
                "task_id": message.get("id"),
                "pattern": "request_response"
            }
        }
```

#### Publish-Subscribe Pattern

```yaml
publish_subscribe:
  protocol_adaptations:
    a2a:
      use_tasks: true
      task_type: "notification"
      topic_metadata_field: "topic"
```

**Implementation:**

```python
class A2APublishSubscribeAdapter(ProtocolAdapter):
    async def prepare_outgoing(self, message, pattern):
        # Create an A2A task for the publication
        task = {
            "type": self.config.get("task_type", "notification"),
            "input": message.get("content"),
            "metadata": {
                "pattern": "publish_subscribe",
                "topic": message.get("topic"),
                "publisher_id": message.get("publisher_id")
            }
        }
        return task

    async def process_incoming(self, message, pattern):
        # Extract notification from A2A task
        metadata = message.get("metadata", {})
        return {
            "topic": metadata.get(self.config.get("topic_metadata_field", "topic")),
            "content": message.get("input"),
            "publisher_id": metadata.get("publisher_id"),
            "metadata": {
                "task_id": message.get("id"),
                "pattern": "publish_subscribe"
            }
        }
```

#### Event-Based Pattern

```yaml
event_based:
  protocol_adaptations:
    a2a:
      use_tasks: true
      task_type: "event"
      event_type_field: "event_type"
```

#### Streaming Pattern

```yaml
streaming:
  protocol_adaptations:
    a2a:
      use_streaming: true
      chunk_size: 4096
      stream_id_field: "stream_id"
```

#### Pipeline Pattern

```yaml
pipeline:
  protocol_adaptations:
    a2a:
      use_tasks: true
      task_type: "pipeline"
      stage_metadata_field: "stage"
```

#### Delegation Pattern

```yaml
delegation:
  protocol_adaptations:
    a2a:
      use_tasks: true
      task_type: "delegation"
      capability_field: "capabilities"
```

## MCP Protocol Adaptation

### MCP Protocol Capabilities

The MCP (Model Context Protocol) offers these key capabilities:

1. **Function Calling** - Function-based interaction
2. **Stateful Context** - Contextual conversation handling
3. **Tool Use** - Specialized tool invocation
4. **Streaming** - Streaming response support

### MCP Pattern Mappings

Here's how patterns map to MCP protocol features:

#### Request-Response Pattern

```yaml
request_response:
  protocol_adaptations:
    mcp:
      use_function_calls: true
      function_name: "handle_request"
      async_response: false
```

**Implementation:**

```python
class MCPRequestResponseAdapter(ProtocolAdapter):
    async def prepare_outgoing(self, message, pattern):
        # Create an MCP function call for the request
        function_call = {
            "name": self.config.get("function_name", "handle_request"),
            "arguments": {
                "request": message.get("content"),
                "request_id": message.get("id"),
                "metadata": message.get("metadata", {})
            }
        }
        return function_call

    async def process_incoming(self, message, pattern):
        # Extract response from MCP function call result
        return {
            "id": message.get("arguments", {}).get("request_id"),
            "content": message.get("result"),
            "metadata": {
                "function_id": message.get("id"),
                "pattern": "request_response"
            }
        }
```

#### Publish-Subscribe Pattern

```yaml
publish_subscribe:
  protocol_adaptations:
    mcp:
      use_function_calls: true
      publish_function: "publish"
      subscribe_function: "subscribe"
```

#### Event-Based Pattern

```yaml
event_based:
  protocol_adaptations:
    mcp:
      use_function_calls: true
      emit_function: "emit_event"
      handle_function: "handle_event"
```

#### Streaming Pattern

```yaml
streaming:
  protocol_adaptations:
    mcp:
      use_streaming: true
      init_function: "start_stream"
      chunk_function: "stream_chunk"
```

#### Pipeline Pattern

```yaml
pipeline:
  protocol_adaptations:
    mcp:
      use_function_calls: true
      stage_function_prefix: "pipeline_stage_"
```

#### Delegation Pattern

```yaml
delegation:
  protocol_adaptations:
    mcp:
      use_function_calls: true
      function_prefix: "delegate_"
```

## HTTP Protocol Adaptation

### HTTP Protocol Capabilities

The HTTP protocol offers these key capabilities:

1. **REST APIs** - Resource-oriented interfaces
2. **Request-Response** - Standard HTTP methods
3. **Headers** - Metadata in headers
4. **Status Codes** - Standardized response codes
5. **Webhooks** - Callback-based asynchronous communication

### HTTP Pattern Mappings

Here's how patterns map to HTTP protocol features:

#### Request-Response Pattern

```yaml
request_response:
  protocol_adaptations:
    http:
      method: "POST"
      path_template: "/api/{endpoint}"
      response_codes: [200, 201]
      content_type: "application/json"
```

#### Publish-Subscribe Pattern

```yaml
publish_subscribe:
  protocol_adaptations:
    http:
      use_webhooks: true
      subscription_path: "/api/subscribe"
      publication_path: "/api/publish"
      webhook_method: "POST"
```

#### Event-Based Pattern

```yaml
event_based:
  protocol_adaptations:
    http:
      use_webhooks: true
      event_path: "/api/events"
      event_type_header: "X-Event-Type"
```

#### Streaming Pattern

```yaml
streaming:
  protocol_adaptations:
    http:
      use_chunked_encoding: true
      stream_init_path: "/api/streams"
      content_type: "application/octet-stream"
```

#### Pipeline Pattern

```yaml
pipeline:
  protocol_adaptations:
    http:
      use_webhooks: true
      stage_path_template: "/api/pipeline/{pipeline_id}/stage/{stage_id}"
      completion_path: "/api/pipeline/{pipeline_id}/complete"
```

#### Delegation Pattern

```yaml
delegation:
  protocol_adaptations:
    http:
      method: "POST"
      path: "/api/delegate"
      authorization_header: "X-Delegation-Token"
```

## MQTT Protocol Adaptation

### MQTT Protocol Capabilities

The MQTT protocol offers these key capabilities:

1. **Pub/Sub Messaging** - Topic-based publication/subscription
2. **QoS Levels** - Different delivery guarantees
3. **Retained Messages** - Last message persistence
4. **Wild Card Subscriptions** - Pattern-based subscriptions

### MQTT Pattern Mappings

Here's how patterns map to MQTT protocol features:

#### Request-Response Pattern

```yaml
request_response:
  protocol_adaptations:
    mqtt:
      request_topic_template: "request/{recipient_id}"
      response_topic_template: "response/{requester_id}/{request_id}"
      qos_level: 1
```

#### Publish-Subscribe Pattern

```yaml
publish_subscribe:
  protocol_adaptations:
    mqtt:
      topic_template: "{topic}"
      qos_level: 1
      retain: true
```

#### Event-Based Pattern

```yaml
event_based:
  protocol_adaptations:
    mqtt:
      topic_template: "events/{event_type}"
      qos_level: 1
      retain: false
```

#### Streaming Pattern

```yaml
streaming:
  protocol_adaptations:
    mqtt:
      control_topic_template: "stream/{stream_id}/control"
      data_topic_template: "stream/{stream_id}/data"
      qos_level: 0
```

#### Pipeline Pattern

```yaml
pipeline:
  protocol_adaptations:
    mqtt:
      stage_topic_template: "pipeline/{pipeline_id}/stage/{stage_id}"
      completion_topic: "pipeline/{pipeline_id}/complete"
      qos_level: 1
```

#### Delegation Pattern

```yaml
delegation:
  protocol_adaptations:
    mqtt:
      delegation_topic: "delegation/requests"
      result_topic_template: "delegation/results/{delegator_id}"
      qos_level: 2
```

## Redis Protocol Adaptation

Redis is used for both pub/sub and data storage in pattern adaptations.

#### Request-Response Pattern

```yaml
request_response:
  protocol_adaptations:
    redis:
      request_channel_template: "request:{recipient_id}"
      response_channel_template: "response:{requester_id}:{request_id}"
      response_timeout_ms: 30000
```

#### Publish-Subscribe Pattern

```yaml
publish_subscribe:
  protocol_adaptations:
    redis:
      channel_prefix: "pubsub"
      channel_template: "{channel_prefix}:{topic}"
```

## gRPC Protocol Adaptation

gRPC provides strong typing and bi-directional streaming.

#### Request-Response Pattern

```yaml
request_response:
  protocol_adaptations:
    grpc:
      service_name: "RequestService"
      method_name: "HandleRequest"
```

#### Streaming Pattern

```yaml
streaming:
  protocol_adaptations:
    grpc:
      service_name: "StreamService"
      method_name: "StreamData"
      stream_type: "bidirectional"
```

## Cross-Protocol Communication

OpenMAS supports communication between agents using different protocols:

```yaml
agents:
  coordinator:
    communicator_type: "a2a"
    patterns:
      request_response:
        protocol_adaptations:
          a2a:
            use_tasks: true

  worker:
    communicator_type: "mcp"
    patterns:
      request_response:
        protocol_adaptations:
          mcp:
            use_function_calls: true
```

This works because:

1. The pattern maintains consistent semantics across protocols
2. Protocol adapters handle the conversion between protocol formats
3. OpenMAS's message routing system connects the different protocols

## Protocol Feature Compatibility

Each protocol has different capabilities. This chart shows pattern compatibility:

| Pattern | A2A | MCP | HTTP | MQTT | Redis | gRPC |
|---------|-----|-----|------|------|-------|------|
| Request-Response | ✓✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ | ✓✓ | ✓✓✓ |
| Publish-Subscribe | ✓✓ | ✓✓ | ✓✓ | ✓✓✓ | ✓✓✓ | ✓✓ |
| Event-Based | ✓✓✓ | ✓✓ | ✓✓ | ✓✓✓ | ✓✓ | ✓✓ |
| Streaming | ✓✓✓ | ✓✓✓ | ✓✓ | ✓ | ✓ | ✓✓✓ |
| Pipeline | ✓✓✓ | ✓✓ | ✓✓ | ✓ | ✓ | ✓✓ |
| Delegation | ✓✓✓ | ✓✓✓ | ✓✓ | ✓ | ✓ | ✓✓ |

✓✓✓ = Full native support
✓✓ = Good support
✓ = Basic support

## Protocol Selection Guidelines

When choosing which protocol to use with a pattern:

1. **A2A Protocol**: Best for complex agent interactions, especially with LLMs
2. **MCP Protocol**: Best for tool-oriented agent capabilities
3. **HTTP Protocol**: Best for RESTful resource interactions and broad compatibility
4. **MQTT Protocol**: Best for IoT and publish-subscribe scenarios
5. **Redis Protocol**: Best for high-throughput messaging with persistence
6. **gRPC Protocol**: Best for strongly typed, high-performance services

## Adaptation Configuration Guidelines

Follow these guidelines when configuring protocol adaptations:

1. **Be Protocol-Specific**: Each protocol has unique capabilities to leverage
2. **Maintain Semantics**: Ensure consistent pattern semantics across protocols
3. **Handle Errors**: Configure appropriate error handling for each protocol
4. **Consider Performance**: Tune configuration for protocol-specific performance
5. **Security Integration**: Ensure protocol security features are properly configured

## Protocol Extension

To add a new protocol to the adaptation system:

1. **Create Protocol Adapter**: Implement the ProtocolAdapter interface
2. **Register with Factory**: Add to the ProtocolAdapterFactory
3. **Document Capabilities**: Document pattern compatibility
4. **Create Configuration Schema**: Define the configuration schema
5. **Implement Patterns**: Implement all supported patterns

```python
# Example: Adding a new protocol
class NewProtocolAdapter(ProtocolAdapter):
    """Adapts patterns to a new protocol."""

    async def process_incoming(self, message, pattern):
        # Implementation

    async def prepare_outgoing(self, message, pattern):
        # Implementation

# Register with factory
factory.register_adapter("new_protocol", NewProtocolAdapter)
```
