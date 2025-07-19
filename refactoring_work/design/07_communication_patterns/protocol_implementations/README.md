# Protocol Implementations of Communication Patterns

## Overview

This document describes how OpenMAS's communication patterns are implemented across different protocols (A2A, MCP, HTTP, MQTT, gRPC), ensuring consistent behavior while leveraging protocol-specific features.

## Implementation Principles

OpenMAS implements communication patterns across protocols following these principles:

1. **Pattern Consistency** - Core behavior remains consistent across all protocols
2. **Protocol Optimization** - Each implementation leverages protocol-specific strengths
3. **Reasoning Agnosticism** - All implementations maintain separation from reasoning approaches
4. **Interface Stability** - Agent code remains the same regardless of underlying protocol
5. **Fallback Mechanisms** - Graceful degradation when a protocol lacks certain capabilities

## Protocol-Specific Implementations

### A2A Protocol Implementations

| Pattern | A2A Implementation | A2A-Specific Features |
|---------|-------------------|----------------------|
| Request-Response | A2A capability calls | Structured capability schemas, advanced error responses |
| Publish-Subscribe | A2A notifications | Real-time capability updates, subscription management |
| Event-Based | A2A push notifications | Event filtering, priority levels |
| Streaming | A2A streaming responses | Chunk-based streaming, cancellation support |
| Delegation | A2A capability grants | Capability delegation with access control |

Example A2A implementation of Request-Response:

```python
# A2A request-response implementation
class A2ARequestResponsePattern(RequestResponsePattern):
    """A2A implementation of the request-response pattern."""
    
    async def send_request(self, target, request_data, options=None):
        """Send a request using A2A protocol."""
        # Convert to A2A capability call format
        capability_name = self.mapping.get_capability_name(target)
        capability_params = self.transform.to_a2a_params(request_data)
        
        # Execute A2A capability call
        response = await self.communicator.call_capability(
            target=target,
            capability=capability_name,
            parameters=capability_params,
            options=options
        )
        
        # Transform response back to standard format
        return self.transform.from_a2a_response(response)
```

### MCP Protocol Implementations

| Pattern | MCP Implementation | MCP-Specific Features |
|---------|-------------------|----------------------|
| Request-Response | MCP tool calls | Structured tool schemas, resource access |
| Publish-Subscribe | MCP resource subscriptions | Resource change notifications |
| Event-Based | MCP events | Context preservation across events |
| Streaming | MCP streaming responses | Token-by-token streaming |
| Delegation | MCP tool delegation | Scoped access control |

Example MCP implementation of Streaming pattern:

```python
# MCP streaming implementation
class MCPStreamingPattern(StreamingPattern):
    """MCP implementation of the streaming pattern."""
    
    async def stream_data(self, target, request_data, options=None):
        """Stream data using MCP protocol."""
        # Convert to MCP tool call with streaming
        tool_name = self.mapping.get_tool_name(target)
        tool_params = self.transform.to_mcp_params(request_data)
        
        # Create streaming generator
        async for chunk in self.communicator.stream_tool_call(
            tool=tool_name,
            parameters=tool_params,
            options=options
        ):
            # Transform each chunk to standard format
            yield self.transform.from_mcp_chunk(chunk)
```

### HTTP Protocol Implementations

| Pattern | HTTP Implementation | HTTP-Specific Features |
|---------|-------------------|----------------------|
| Request-Response | HTTP requests | Status codes, headers, content negotiation |
| Publish-Subscribe | Server-Sent Events | Connection management, reconnection |
| Event-Based | Webhooks | Signature verification, retry handling |
| Streaming | HTTP chunked transfer | Progress tracking |
| Delegation | API tokens | Scoped permissions |

Example HTTP implementation of Publish-Subscribe:

```python
# HTTP publish-subscribe implementation
class HTTPPublishSubscribePattern(PublishSubscribePattern):
    """HTTP implementation of the publish-subscribe pattern using SSE."""
    
    async def subscribe(self, topic, callback, options=None):
        """Subscribe to a topic using HTTP Server-Sent Events."""
        # Convert topic to URL path
        path = self.mapping.topic_to_path(topic)
        
        # Create SSE connection
        sse_client = self.communicator.create_sse_client(
            path=path,
            options=options
        )
        
        # Set up event handling
        sse_client.on_message(
            lambda event: callback(self.transform.from_sse_event(event))
        )
        
        # Start listening
        await sse_client.connect()
        return sse_client  # Return subscription handle
```

### MQTT Protocol Implementations

| Pattern | MQTT Implementation | MQTT-Specific Features |
|---------|-------------------|----------------------|
| Request-Response | MQTT request-reply | Correlation IDs, temporary response topics |
| Publish-Subscribe | Native MQTT pub/sub | QoS levels, retained messages |
| Event-Based | MQTT topics | Hierarchical topic structure, wildcards |
| Streaming | Multiple MQTT messages | Sequence numbers, end markers |
| Delegation | MQTT access control | Topic-based permissions |

Example MQTT implementation of Event-Based pattern:

```python
# MQTT event-based implementation
class MQTTEventBasedPattern(EventBasedPattern):
    """MQTT implementation of the event-based pattern."""
    
    async def emit_event(self, event_type, event_data, options=None):
        """Emit an event using MQTT protocol."""
        # Convert event type to MQTT topic
        topic = self.mapping.event_to_topic(event_type)
        
        # Transform event data to MQTT message format
        message = self.transform.to_mqtt_message(event_type, event_data)
        
        # Set QoS level from options or default
        qos = options.get('qos', 1) if options else 1
        
        # Publish message
        await self.communicator.publish(
            topic=topic,
            payload=message,
            qos=qos,
            retain=options.get('retain', False) if options else False
        )
```

### gRPC Protocol Implementations

| Pattern | gRPC Implementation | gRPC-Specific Features |
|---------|-------------------|----------------------|
| Request-Response | Unary RPC | Strong typing, deadlines |
| Publish-Subscribe | Server streaming RPC | Long-lived connections |
| Event-Based | Bidirectional streaming | Event ordering, prioritization |
| Streaming | Client/Bidirectional streaming | Flow control, backpressure |
| Delegation | gRPC metadata | Credential passing, context propagation |

Example gRPC implementation of Request-Response:

```python
# gRPC request-response implementation
class GRPCRequestResponsePattern(RequestResponsePattern):
    """gRPC implementation of the request-response pattern."""
    
    async def send_request(self, target, request_data, options=None):
        """Send a request using gRPC protocol."""
        # Convert target to service and method
        service, method = self.mapping.get_grpc_service_method(target)
        
        # Transform request data to protobuf message
        request_message = self.transform.to_protobuf(request_data)
        
        # Set deadline from options or default
        deadline = options.get('deadline_ms', 30000) if options else 30000
        
        # Execute gRPC call
        response = await self.communicator.call(
            service=service,
            method=method,
            request=request_message,
            timeout=deadline
        )
        
        # Transform protobuf response to standard format
        return self.transform.from_protobuf(response)
```

## Cross-Protocol Pattern Usage

OpenMAS enables seamless pattern usage regardless of protocol through:

### Protocol Adapters

```python
# Using the same pattern with different protocols
request_response = RequestResponsePattern()

# With A2A protocol
a2a_result = await request_response.with_protocol("a2a").send_request(
    target="weather_agent",
    request_data={"location": "San Francisco"}
)

# With HTTP protocol
http_result = await request_response.with_protocol("http").send_request(
    target="weather_agent",
    request_data={"location": "San Francisco"}
)

# Same pattern interface, different protocol implementations
assert a2a_result == http_result  # Results are equivalent
```

### Protocol Fallbacks

```python
# Configuration with protocol fallback chain
pattern_config = {
    "request_response": {
        "protocol_preference": ["a2a", "http", "grpc"],
        "fallback_strategy": "next_in_chain"
    }
}

# Pattern automatically tries each protocol in sequence
result = await request_response.send_request(
    target="weather_agent",
    request_data={"location": "San Francisco"}
)
```

## Reasoning Agnosticism

All protocol implementations maintain OpenMAS's reasoning agnosticism:

1. **Pattern Interface Abstraction** - The pattern interface is independent of reasoning approach
2. **Data Format Independence** - Data conversions are handled by the protocol adapter
3. **Consistent Callbacks** - Event handlers and callbacks work the same across reasoning types

This enables agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to use the same communication patterns with different protocols.
