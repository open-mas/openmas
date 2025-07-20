# Communication Patterns

## Overview

This document provides an overview of the standard communication patterns available in OpenMAS. Each pattern defines a specific message exchange method that can be used across all protocols while maintaining OpenMAS's reasoning agnosticism.

## Core Patterns

OpenMAS provides these standardized communication patterns:

### 1. Request-Response

The Request-Response pattern enables synchronous communication where one agent sends a request and receives a response from another agent.

**Key Features:**
- Synchronous or asynchronous operation
- Timeout management
- Retry mechanisms
- Error handling
- Response correlation

**Implementation:**
```python
# Using the Request-Response pattern
async def make_request(agent):
    result = await agent.patterns.request_response.send(
        target_agent="weather_agent",
        content={
            "location": "San Francisco",
            "units": "metric"
        },
        options={
            "timeout": 30,
            "retry": {
                "attempts": 3,
                "interval": 5
            }
        }
    )
    return result
```

**Protocol Adaptations:**
- **A2A**: Uses capability invocation with correlation IDs
- **MCP**: Maps to tool calling with response awaiting
- **HTTP**: Maps to HTTP POST with response handling
- **MQTT**: Uses request and response topics with correlation
- **gRPC**: Maps to unary RPC calls

[Detailed Documentation](./request_response.md)

### 2. Publish-Subscribe

The Publish-Subscribe pattern enables one-to-many communication where publishers send messages to topics and subscribers receive messages from those topics.

**Key Features:**
- Decoupled communication
- Topic-based routing
- Message filtering
- Subscription management
- Topic hierarchies

**Implementation:**
```python
# Publishing a message
await agent.patterns.publish_subscribe.publish(
    topic="weather/updates",
    message={
        "location": "San Francisco",
        "temperature": 22,
        "conditions": "Sunny"
    }
)

# Subscribing to a topic
await agent.patterns.publish_subscribe.subscribe(
    topic="weather/updates",
    handler=handle_weather_update
)
```

**Protocol Adaptations:**
- **A2A**: Uses broadcast capabilities
- **MCP**: Maps to event subscription
- **HTTP**: Uses webhooks or SSE
- **MQTT**: Direct mapping to pub/sub topics
- **gRPC**: Maps to server streaming

[Detailed Documentation](./publish_subscribe.md)

### 3. Delegation

The Delegation pattern enables an agent to delegate a task to another agent and receive the results when complete.

**Key Features:**
- Task delegation
- Progress tracking
- Result handling
- Error management
- Priority levels

**Implementation:**
```python
# Delegating a task
task_id = await agent.patterns.delegation.delegate(
    target_agent="data_processor",
    task={
        "type": "process_data",
        "data": dataset,
        "options": {
            "algorithm": "clustering",
            "params": {"clusters": 5}
        }
    },
    options={
        "priority": "high",
        "progress_updates": True
    }
)

# Receiving progress updates
def on_progress(update):
    print(f"Task {update['task_id']} progress: {update['progress']}%")

agent.patterns.delegation.on_progress(task_id, on_progress)
```

**Protocol Adaptations:**
- **A2A**: Maps to task delegation capabilities
- **MCP**: Uses multi-step tool calling
- **HTTP**: Maps to asynchronous API calls
- **MQTT**: Uses task and result topics
- **gRPC**: Maps to bidirectional streaming

[Detailed Documentation](./delegation.md)

### 4. Pipeline

The Pipeline pattern enables sequential processing of messages through multiple agents forming a processing pipeline.

**Key Features:**
- Sequential processing
- Data transformation
- Error handling at each stage
- Conditional branching
- Monitoring and metrics

**Implementation:**
```python
# Creating a pipeline
pipeline = await agent.patterns.pipeline.create([
    {"agent": "data_collector", "operation": "collect"},
    {"agent": "data_processor", "operation": "process"},
    {"agent": "data_analyzer", "operation": "analyze"}
])

# Processing data through the pipeline
result = await agent.patterns.pipeline.process(
    pipeline_id=pipeline.id,
    input_data={
        "source": "sensors",
        "timeframe": "last_24h"
    }
)
```

**Protocol Adaptations:**
- **A2A**: Maps to sequential capability invocations
- **MCP**: Uses sequential tool calling
- **HTTP**: Maps to chained API calls
- **MQTT**: Uses sequential topic publishing
- **gRPC**: Maps to sequential RPC calls

[Detailed Documentation](./pipeline.md)

### 5. Event-Based

The Event-Based pattern enables reactive communication based on events and handlers.

**Key Features:**
- Event broadcasting
- Handler registration
- Event filtering
- Priority handling
- Batched processing

**Implementation:**
```python
# Broadcasting an event
await agent.patterns.event_based.broadcast(
    event_type="data_updated",
    event_data={
        "source": "database",
        "table": "users",
        "operation": "update",
        "affected_ids": [101, 102, 103]
    }
)

# Registering an event handler
await agent.patterns.event_based.register_handler(
    event_type="data_updated",
    handler=handle_data_update,
    filter={"source": "database", "table": "users"}
)
```

**Protocol Adaptations:**
- **A2A**: Maps to event capabilities
- **MCP**: Uses event notifications
- **HTTP**: Maps to webhooks
- **MQTT**: Direct mapping to event topics
- **gRPC**: Maps to server streaming

[Detailed Documentation](./event_based.md)

### 6. Streaming

The Streaming pattern enables continuous data streaming between agents.

**Key Features:**
- Continuous data flow
- Backpressure handling
- Stream control (pause/resume)
- Batching options
- Completion signaling

**Implementation:**
```python
# Creating a stream
stream = await agent.patterns.streaming.create(
    target_agent="data_source",
    stream_config={
        "data_type": "sensor_readings",
        "batch_size": 100,
        "interval_ms": 500
    }
)

# Consuming a stream
async for batch in stream:
    for reading in batch:
        process_reading(reading)

# Providing a stream
async def generate_readings(request, stream):
    while True:
        reading = await sensor.get_reading()
        await stream.send(reading)
        await asyncio.sleep(0.1)

agent.patterns.streaming.provide("sensor_readings", generate_readings)
```

**Protocol Adaptations:**
- **A2A**: Maps to streaming capabilities
- **MCP**: Uses incremental responses
- **HTTP**: Maps to SSE or WebSockets
- **MQTT**: Uses continuous topic publishing
- **gRPC**: Direct mapping to streaming RPC

[Detailed Documentation](./streaming.md)

## Pattern Selection

When selecting a communication pattern, consider these factors:

1. **Communication Semantics** - What communication model best fits your use case
2. **Latency Requirements** - Whether real-time or delayed communication is needed
3. **Data Volume** - Amount of data being transferred
4. **Coupling Level** - How tightly coupled agents should be
5. **Reliability Needs** - Required delivery guarantees
6. **Topology Alignment** - How the pattern aligns with agent relationships

This table helps select the appropriate pattern:

| Pattern | Use Case | Coupling | Data Volume | Latency |
|---------|----------|----------|-------------|---------|
| Request-Response | Direct queries | Tight | Low-Medium | Low |
| Publish-Subscribe | Event notifications | Loose | Medium | Medium |
| Delegation | Task offloading | Medium | Medium-High | High |
| Pipeline | Sequential processing | Medium | Medium-High | Medium |
| Event-Based | Reactive workflows | Loose | Low | Medium |
| Streaming | Continuous data | Medium | High | Low |

## Pattern Configuration

All patterns are configured through the unified configuration schema. Communication pattern configuration options can be found in the [Protocol Configuration Schema](/03_configuration/schema/protocols.md) and the [Extension Configuration Schema](/03_configuration/schema/extensions.md).

Example configuration:

```yaml
communication_patterns:
  request_response:
    enabled: true
    timeout: 30
    retry:
      attempts: 3
      interval: 5
    protocol_adaptations:
      a2a:
        capability_name: "request_response"
      http:
        method: "POST"
        response_codes: [200, 201]
```

## Pattern Composition

Patterns can be composed to create complex communication workflows:

```python
# Combining delegation with streaming
async def process_large_dataset(agent, dataset):
    # Step 1: Delegate processing task
    task_id = await agent.patterns.delegation.delegate(
        target_agent="data_processor",
        task={"type": "process", "dataset_id": dataset.id}
    )

    # Step 2: Stream results
    stream = await agent.patterns.streaming.create(
        target_agent="data_processor",
        stream_config={"task_id": task_id}
    )

    # Step 3: Process streaming results
    results = []
    async for batch in stream:
        results.extend(batch)

    return results
```

## Protocol Independence

All patterns are designed to work consistently across different protocols. The protocol adaptation layer handles the mapping between pattern semantics and protocol-specific implementations.

This ensures that agent communication logic remains the same regardless of the underlying protocol being used.

## Reasoning Agnosticism

Communication patterns maintain OpenMAS's distinctive reasoning agnosticism by:

1. **Semantic Focus** - Patterns define semantics, not reasoning logic
2. **Protocol Independence** - Patterns work with any protocol
3. **Content Agnosticism** - Patterns don't interpret message content
4. **Abstract Interfaces** - Patterns expose abstract interfaces
5. **Event-Based Programming** - Patterns use event-based programming model

This enables agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to communicate using the same patterns consistently.
