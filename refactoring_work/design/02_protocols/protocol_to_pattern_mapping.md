# Protocol to Communication Pattern Mapping

## Overview

This document serves as the definitive mapping between OpenMAS protocols and communication patterns. It addresses the separation of concerns between protocol documentation (in `/02_protocols/`) and communication pattern documentation (in `/07_communication_patterns/`), providing clear cross-references without duplication.

## Protocol and Pattern Relationship

In OpenMAS's architecture:

- **Protocols** (documented in `/02_protocols/`) define the transport mechanisms, message formats, and technical implementations
- **Communication Patterns** (documented in `/07_communication_patterns/`) define abstract message exchange patterns that can be implemented across different protocols

## Protocol to Pattern Mapping

The following table maps each protocol to the communication patterns it supports, with links to both the protocol documentation and the pattern documentation:

| Protocol | Communication Patterns | Implementation Notes |
|----------|------------------------|---------------------|
| [A2A](/refactoring_work/00b_overview/02_protocols/a2a/a2a_protocol.md) | [Request-Response](/refactoring_work/00b_overview/07_communication_patterns/patterns/request_response.md)<br>[Streaming](/refactoring_work/00b_overview/07_communication_patterns/patterns/streaming.md)<br>[Event-Based](/refactoring_work/00b_overview/07_communication_patterns/patterns/event_based.md) | A2A primarily uses capability-based request-response patterns but can support streaming through WebSockets transport and event-based patterns through capability callbacks. |
| [MCP](/refactoring_work/00b_overview/02_protocols/mcp/mcp_protocol.md) | [Request-Response](/refactoring_work/00b_overview/07_communication_patterns/patterns/request_response.md)<br>[Streaming](/refactoring_work/00b_overview/07_communication_patterns/patterns/streaming.md) | MCP naturally supports tool-based request-response patterns and streaming responses, particularly with SSE transport. |
| [HTTP](/refactoring_work/00b_overview/02_protocols/http/http_protocol.md) | [Request-Response](/refactoring_work/00b_overview/07_communication_patterns/patterns/request_response.md)<br>[Streaming](/refactoring_work/00b_overview/07_communication_patterns/patterns/streaming.md) (with SSE) | HTTP is primarily designed for request-response but can support streaming with Server-Sent Events (SSE). |
| [MQTT](/refactoring_work/00b_overview/02_protocols/mqtt/mqtt_protocol.md) | [Publish-Subscribe](/refactoring_work/00b_overview/07_communication_patterns/patterns/publish_subscribe.md)<br>[Event-Based](/refactoring_work/00b_overview/07_communication_patterns/patterns/event_based.md)<br>[Request-Response](/refactoring_work/00b_overview/07_communication_patterns/patterns/request_response.md) (via topics) | MQTT naturally implements pub-sub patterns, but can support request-response through topic pairs and correlation IDs. |
| [gRPC](/refactoring_work/00b_overview/02_protocols/grpc/grpc_protocol.md) | [Request-Response](/refactoring_work/00b_overview/07_communication_patterns/patterns/request_response.md)<br>[Streaming](/refactoring_work/00b_overview/07_communication_patterns/patterns/streaming.md)<br>[Pipeline](/refactoring_work/00b_overview/07_communication_patterns/patterns/pipeline_part1.md) | gRPC supports unary calls (request-response), client streaming, server streaming, and bidirectional streaming. |

## Pattern-First View

The following table provides a pattern-first view, showing which protocols can implement each communication pattern:

| Communication Pattern | Supporting Protocols | Notes |
|----------------------|---------------------|-------|
| [Request-Response](/refactoring_work/00b_overview/07_communication_patterns/patterns/request_response.md) | A2A, MCP, HTTP, MQTT, gRPC | The most widely supported pattern across all protocols. Each protocol implements it differently (HTTP methods, A2A capabilities, MQTT topic pairs, etc.) |
| [Publish-Subscribe](/refactoring_work/00b_overview/07_communication_patterns/patterns/publish_subscribe.md) | MQTT (native), A2A (adapted), gRPC (adapted) | Most naturally supported by MQTT, but can be adapted to other protocols. |
| [Streaming](/refactoring_work/00b_overview/07_communication_patterns/patterns/streaming.md) | gRPC (native), MCP (native), HTTP/SSE, WebSockets | Bidirectional streaming is best supported by gRPC and WebSockets. |
| [Event-Based](/refactoring_work/00b_overview/07_communication_patterns/patterns/event_based.md) | MQTT (native), A2A (with callbacks), WebSockets | Event distribution works best with MQTT's pub/sub model. |
| [Pipeline](/refactoring_work/00b_overview/07_communication_patterns/patterns/pipeline_part1.md) | gRPC (native), HTTP (adapted), MQTT (adapted) | Multi-stage processing works well with gRPC streaming but can be adapted to other protocols. |
| [Delegation](/refactoring_work/00b_overview/07_communication_patterns/patterns/delegation.md) | A2A (native), HTTP, gRPC | Task delegation between agents is a natural fit for A2A protocol. |

## Implementation Guidelines

When implementing communication patterns across different protocols:

### 1. Pattern Selection

Choose the appropriate communication pattern based on your use case:

- **Request-Response**: For synchronous interactions requiring immediate responses
- **Publish-Subscribe**: For many-to-many broadcasting of information
- **Streaming**: For continuous data flows
- **Event-Based**: For state change notifications and reactive systems
- **Pipeline**: For sequential multi-stage processing
- **Delegation**: For task delegation between agents

### 2. Protocol Selection

Select the protocol that best implements your chosen pattern:

- **A2A**: Best for agent-to-agent interactions and capability discovery
- **MCP**: Best for model/agent access to tools and resources
- **HTTP**: Best for RESTful web-based communication
- **MQTT**: Best for lightweight pub/sub messaging
- **gRPC**: Best for high-performance, strongly-typed service communication

### 3. Pattern Implementation

Implement the pattern using protocol-specific mechanisms:

```python
# Example: Implementing request-response pattern across different protocols

# With A2A
async def a2a_request_response(agent, target, capability, params):
    response = await agent.a2a_client.invoke_capability(
        target_agent=target,
        capability=capability,
        parameters=params
    )
    return response

# With HTTP
async def http_request_response(agent, url, method, params):
    response = await agent.http_client.request(
        url=url,
        method=method,
        json=params
    )
    return await response.json()

# With MQTT
async def mqtt_request_response(agent, request_topic, response_topic, message):
    # Generate correlation ID
    correlation_id = str(uuid.uuid4())

    # Create response future
    response_future = asyncio.Future()

    # Set up response handler
    def on_response(topic, payload):
        response_data = json.loads(payload)
        if response_data.get("correlation_id") == correlation_id:
            response_future.set_result(response_data)

    # Subscribe to response topic
    await agent.mqtt_client.subscribe(response_topic, on_response)

    # Publish request with correlation ID
    request_data = {**message, "correlation_id": correlation_id}
    await agent.mqtt_client.publish(request_topic, json.dumps(request_data))

    # Wait for response
    return await response_future
```

## Cross-Reference Guidelines

To maintain clarity and avoid duplication:

1. **Protocol Documentation** (`/02_protocols/`)
   - Focus on protocol-specific details (formats, transport, security)
   - Reference communication patterns with links to `/07_communication_patterns/`
   - Include brief examples of how the protocol implements common patterns
   - Do not duplicate detailed pattern descriptions

2. **Pattern Documentation** (`/07_communication_patterns/`)
   - Focus on protocol-agnostic pattern descriptions
   - Provide abstract examples that can work across protocols
   - Reference protocol-specific implementations
   - Include adaptations for different protocols

## References

- [Communication Patterns Overview](/refactoring_work/00b_overview/07_communication_patterns/README.md)
- [Protocol Integration Guide](/refactoring_work/00b_overview/02_protocols/protocol_integration_guide.md)
- [Protocol Comparison](/refactoring_work/00b_overview/02_protocols/protocol_comparison.md)
