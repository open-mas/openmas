# Asynchronous Integration Testing

## Overview

This document describes approaches and best practices for testing asynchronous operations and interactions in OpenMAS. Asynchronous operations are fundamental to OpenMAS's architecture, particularly in agent communication, message processing, and event handling.

## Key Asynchronous Testing Scenarios

OpenMAS's asynchronous testing focuses on these key scenarios:

1. **Message Exchange**: Testing asynchronous message passing between agents
2. **Event Processing**: Testing event-driven behavior and callbacks
3. **Concurrent Operations**: Testing behavior with concurrent operations
4. **Task Scheduling**: Testing scheduled and delayed operations
5. **Resource Contention**: Testing behavior under resource contention

## Testing Approach

### Asynchronous Test Fixtures

```python
import pytest
import asyncio
from openmas.testing import AsyncTestHelper

@pytest.fixture
async def async_helper():
    """Create an async test helper."""
    helper = AsyncTestHelper()
    await helper.initialize()

    yield helper

    await helper.shutdown()

@pytest.fixture
async def message_queue():
    """Create a test message queue."""
    queue = asyncio.Queue()

    yield queue

@pytest.fixture
async def event_waiter():
    """Create an event waiter for async testing."""
    events = {}

    def set_event(event_name):
        if event_name not in events:
            events[event_name] = asyncio.Event()
        events[event_name].set()

    async def wait_for_event(event_name, timeout=5.0):
        if event_name not in events:
            events[event_name] = asyncio.Event()
        return await asyncio.wait_for(events[event_name].wait(), timeout)

    yield set_event, wait_for_event
```

### Testing Asynchronous Message Exchange

```python
import pytest
import asyncio
from openmas.testing import TestSupervisor

async def test_async_message_exchange(async_helper):
    """Test asynchronous message exchange between agents."""
    # Create agents
    agent1 = await async_helper.create_agent("agent1", "assistant")
    agent2 = await async_helper.create_agent("agent2", "user")

    # Track received messages
    received_messages = []

    # Register message handler
    async def message_handler(message):
        received_messages.append(message)
        return {"content": "Received", "type": "text"}

    await agent2.register_message_handler(message_handler)

    # Send message asynchronously
    send_task = asyncio.create_task(
        agent1.send_message(
            receiver=agent2.id,
            message={"content": "Hello", "type": "text"}
        )
    )

    # Wait for message processing
    await async_helper.wait_for_condition(
        lambda: len(received_messages) > 0,
        timeout=5.0
    )

    # Verify message was received
    assert len(received_messages) == 1
    assert received_messages[0]["content"] == "Hello"

    # Ensure send task completes
    response = await send_task
    assert response is not None
    assert response["content"] == "Received"
```

### Testing with Multiple Concurrent Operations

```python
async def test_concurrent_operations(async_helper):
    """Test behavior with multiple concurrent operations."""
    # Create test components
    component1 = await async_helper.create_component("component1")
    component2 = await async_helper.create_component("component2")

    # Create tasks for concurrent operations
    results = {}

    async def operation1():
        await asyncio.sleep(0.1)  # Simulate work
        results["op1"] = "completed"

    async def operation2():
        await asyncio.sleep(0.2)  # Simulate work
        results["op2"] = "completed"

    async def operation3():
        await asyncio.sleep(0.15)  # Simulate work
        results["op3"] = "completed"

    # Start all operations concurrently
    task1 = asyncio.create_task(operation1())
    task2 = asyncio.create_task(operation2())
    task3 = asyncio.create_task(operation3())

    # Wait for all tasks to complete
    await asyncio.gather(task1, task2, task3)

    # Verify all operations completed
    assert results == {
        "op1": "completed",
        "op2": "completed",
        "op3": "completed"
    }
```

### Testing Asynchronous Event Handling

```python
async def test_event_handling(async_helper, event_waiter):
    """Test asynchronous event handling."""
    set_event, wait_for_event = event_waiter

    # Create event emitter
    emitter = await async_helper.create_event_emitter()

    # Register event handlers
    event_logs = []

    async def event_handler1(event_data):
        event_logs.append(f"handler1: {event_data}")
        set_event("handler1_called")

    async def event_handler2(event_data):
        event_logs.append(f"handler2: {event_data}")
        set_event("handler2_called")

    # Register handlers
    emitter.on("test_event", event_handler1)
    emitter.on("test_event", event_handler2)

    # Emit event asynchronously
    await emitter.emit("test_event", "test data")

    # Wait for both handlers to be called
    await wait_for_event("handler1_called")
    await wait_for_event("handler2_called")

    # Verify both handlers were called
    assert len(event_logs) == 2
    assert "handler1: test data" in event_logs
    assert "handler2: test data" in event_logs
```

### Testing Timeout Handling

```python
async def test_timeout_handling(async_helper):
    """Test handling of timeouts in asynchronous operations."""
    # Create test component
    component = await async_helper.create_component("timeout_component")

    # Define an operation that times out
    async def slow_operation():
        await asyncio.sleep(2.0)  # Operation takes too long
        return "result"

    # Test operation with timeout
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=1.0)

    # Test resilience after timeout
    result = await component.execute_operation("fast_operation")
    assert result is not None  # Component still works after timeout
```

## Testing Asynchronous Patterns

### 1. Producer-Consumer Pattern

```python
async def test_producer_consumer(async_helper, message_queue):
    """Test producer-consumer pattern."""
    # Define producer and consumer
    async def producer():
        for i in range(5):
            await message_queue.put(f"item-{i}")
            await asyncio.sleep(0.1)  # Simulate work
        await message_queue.put(None)  # Signal end

    async def consumer():
        results = []
        while True:
            item = await message_queue.get()
            if item is None:
                break
            results.append(item)
            message_queue.task_done()
        return results

    # Run producer and consumer concurrently
    producer_task = asyncio.create_task(producer())
    consumer_task = asyncio.create_task(consumer())

    # Wait for both to complete
    await producer_task
    results = await consumer_task

    # Verify all items were processed
    assert results == ["item-0", "item-1", "item-2", "item-3", "item-4"]
```

### 2. Pub-Sub Pattern

```python
async def test_pub_sub(async_helper):
    """Test pub-sub pattern."""
    # Create pub-sub component
    pubsub = await async_helper.create_pubsub()

    # Track received messages
    subscriber1_messages = []
    subscriber2_messages = []

    # Create subscribers
    async def subscriber1(message):
        subscriber1_messages.append(message)

    async def subscriber2(message):
        subscriber2_messages.append(message)

    # Subscribe to topics
    await pubsub.subscribe("topic1", subscriber1)
    await pubsub.subscribe("topic1", subscriber2)
    await pubsub.subscribe("topic2", subscriber2)

    # Publish messages
    await pubsub.publish("topic1", "message for topic1")
    await pubsub.publish("topic2", "message for topic2")

    # Allow time for message delivery
    await asyncio.sleep(0.1)

    # Verify message delivery
    assert len(subscriber1_messages) == 1
    assert subscriber1_messages[0] == "message for topic1"

    assert len(subscriber2_messages) == 2
    assert "message for topic1" in subscriber2_messages
    assert "message for topic2" in subscriber2_messages
```

## Protocol-Specific Asynchronous Testing

OpenMAS supports multiple protocols, each with asynchronous behavior:

### MCP Protocol Testing

```python
async def test_mcp_async_communication(async_helper):
    """Test asynchronous communication with MCP protocol."""
    # Create agents with MCP protocol
    agent1 = await async_helper.create_agent(
        "agent1",
        "assistant",
        protocol_config={"type": "mcp", "transport": "memory"}
    )

    agent2 = await async_helper.create_agent(
        "agent2",
        "user",
        protocol_config={"type": "mcp", "transport": "memory"}
    )

    # Test asynchronous communication
    # (implementation specific to MCP protocol)
```

### A2A Protocol Testing

```python
async def test_a2a_async_communication(async_helper):
    """Test asynchronous communication with A2A protocol."""
    # Create agents with A2A protocol
    agent1 = await async_helper.create_agent(
        "agent1",
        "assistant",
        protocol_config={"type": "a2a", "transport": "memory"}
    )

    agent2 = await async_helper.create_agent(
        "agent2",
        "user",
        protocol_config={"type": "a2a", "transport": "memory"}
    )

    # Test asynchronous communication
    # (implementation specific to A2A protocol)
```

## Testing with Asynchronous Mock Services

```python
async def test_with_async_mock_service(async_helper):
    """Test integration with asynchronous mock services."""
    # Create mock service
    mock_service = await async_helper.create_mock_service(
        name="database",
        responses={
            "query": {"result": ["item1", "item2"]},
            "insert": {"result": "inserted"}
        }
    )

    # Create agent that uses the service
    agent = await async_helper.create_agent(
        "agent1",
        "assistant",
        dependencies={"database": mock_service}
    )

    # Test agent interaction with mock service
    result = await agent.execute_operation("query_database", "test query")

    # Verify result
    assert result == ["item1", "item2"]

    # Verify mock service was called correctly
    assert mock_service.get_call_count("query") == 1
    assert mock_service.get_last_call_args("query") == "test query"
```

## Best Practices

1. **Use Async Fixtures**: Use pytest async fixtures for setup and teardown
2. **Handle Race Conditions**: Design tests to handle timing and race conditions
3. **Set Timeouts**: Always set timeouts to prevent tests from hanging
4. **Clean Up Resources**: Ensure all async resources are properly cleaned up
5. **Test Cancellation**: Test cancellation and interruption scenarios
6. **Mock Time**: Use time mocking for time-dependent asynchronous tests
7. **Isolate Tests**: Keep async tests isolated from each other
8. **Test Error Handling**: Test error handling in asynchronous operations
9. **Protocol Independence**: Test async behavior with all supported protocols
10. **Reasoning Agnosticism**: Maintain separation between communication testing and reasoning testing

## Related Documentation

- [Protocol Testing](./protocol_testing.md)
- [Multi-Agent Testing](./multi_agent_testing.md)
- [Test Supervisor](../framework/test_supervisor.md)
- [Fixtures](../framework/fixtures.md)
