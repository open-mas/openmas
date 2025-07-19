# Protocol Testing

## Overview

This document describes the approaches and best practices for testing protocol implementations in OpenMAS. Protocol testing ensures that all supported communication protocols (MCP, A2A, HTTP, MQTT, gRPC) work correctly both individually and in multi-protocol scenarios, aligning with OpenMAS's multi-protocol design principles.

## Protocol Test Focus Areas

Protocol testing in OpenMAS focuses on these key areas:

1. **Protocol Conformance**: Verifying protocol implementation conforms to specifications
2. **Message Serialization**: Testing message encoding and decoding
3. **Transport Integration**: Testing protocol operation across different transports
4. **Error Handling**: Testing protocol behavior in error scenarios
5. **Cross-Protocol Compatibility**: Testing communication between different protocols
6. **Security Features**: Testing authentication and encryption features

## Testing Approach

### Protocol-Specific Test Fixtures

```python
import pytest
from openmas.testing import ProtocolTestHarness

@pytest.fixture
async def mcp_harness():
    """Create an MCP protocol test harness."""
    harness = ProtocolTestHarness("mcp")
    await harness.initialize()
    
    yield harness
    
    await harness.shutdown()

@pytest.fixture
async def a2a_harness():
    """Create an A2A protocol test harness."""
    harness = ProtocolTestHarness("a2a")
    await harness.initialize()
    
    yield harness
    
    await harness.shutdown()

@pytest.fixture
async def http_harness():
    """Create an HTTP protocol test harness."""
    harness = ProtocolTestHarness("http")
    await harness.initialize()
    
    yield harness
    
    await harness.shutdown()

@pytest.fixture
async def mqtt_harness():
    """Create an MQTT protocol test harness."""
    harness = ProtocolTestHarness("mqtt")
    await harness.initialize()
    
    yield harness
    
    await harness.shutdown()

@pytest.fixture
async def grpc_harness():
    """Create a gRPC protocol test harness."""
    harness = ProtocolTestHarness("grpc")
    await harness.initialize()
    
    yield harness
    
    await harness.shutdown()
```

### Protocol Conformance Testing

```python
import pytest
from openmas.testing import ProtocolValidator

@pytest.mark.parametrize("protocol_type", ["mcp", "a2a", "http", "mqtt", "grpc"])
async def test_protocol_conformance(protocol_type):
    """Test protocol conformance to specifications."""
    # Create protocol validator
    validator = ProtocolValidator(protocol_type)
    
    # Validate protocol implementation
    validation_result = await validator.validate()
    
    # Assert compliance
    assert validation_result.is_compliant
    assert len(validation_result.violations) == 0
```

### Testing Message Serialization

```python
@pytest.mark.parametrize("protocol_type", ["mcp", "a2a", "http", "mqtt", "grpc"])
async def test_message_serialization(request, protocol_type):
    """Test message serialization across protocols."""
    # Get protocol harness
    harness = request.getfixturevalue(f"{protocol_type}_harness")
    
    # Test message
    test_message = {
        "id": "msg-123",
        "sender": "agent1",
        "receiver": "agent2",
        "content": "Hello, world!",
        "content_type": "text/plain",
        "timestamp": "2025-01-01T12:00:00Z",
        "metadata": {
            "conversation_id": "conv-456",
            "sequence": 1
        }
    }
    
    # Serialize message
    serialized = await harness.serialize_message(test_message)
    
    # Deserialize message
    deserialized = await harness.deserialize_message(serialized)
    
    # Assert message integrity
    assert deserialized["id"] == test_message["id"]
    assert deserialized["sender"] == test_message["sender"]
    assert deserialized["receiver"] == test_message["receiver"]
    assert deserialized["content"] == test_message["content"]
    assert deserialized["content_type"] == test_message["content_type"]
    assert deserialized["timestamp"] == test_message["timestamp"]
    assert deserialized["metadata"]["conversation_id"] == test_message["metadata"]["conversation_id"]
    assert deserialized["metadata"]["sequence"] == test_message["metadata"]["sequence"]
```

### Testing Transport Integration

```python
@pytest.mark.parametrize("protocol_type,transport_type", [
    ("mcp", "memory"),
    ("mcp", "http"),
    ("mcp", "websocket"),
    ("a2a", "memory"),
    ("a2a", "http"),
    ("a2a", "websocket"),
    ("http", "http"),
    ("mqtt", "mqtt"),
    ("grpc", "grpc")
])
async def test_transport_integration(request, protocol_type, transport_type):
    """Test protocol operation across different transports."""
    # Get protocol harness
    harness = request.getfixturevalue(f"{protocol_type}_harness")
    
    # Configure transport
    await harness.configure_transport(transport_type)
    
    # Create client and server
    client, server = await harness.create_endpoint_pair()
    
    # Test message
    test_message = {
        "content": "Hello via transport",
        "metadata": {"transport": transport_type}
    }
    
    # Send message from client to server
    await client.send_message(server.id, test_message)
    
    # Receive message at server
    received = await harness.wait_for_message(server, timeout=5.0)
    
    # Assert message was received correctly
    assert received is not None
    assert received["content"] == test_message["content"]
    assert received["metadata"]["transport"] == transport_type
```

### Testing Error Handling

```python
@pytest.mark.parametrize("protocol_type", ["mcp", "a2a", "http", "mqtt", "grpc"])
async def test_error_handling(request, protocol_type):
    """Test protocol error handling."""
    # Get protocol harness
    harness = request.getfixturevalue(f"{protocol_type}_harness")
    
    # Create client and server
    client, server = await harness.create_endpoint_pair()
    
    # Stop the server to force an error
    await server.shutdown()
    
    # Attempt to send message to stopped server
    with pytest.raises(Exception) as excinfo:
        await client.send_message(server.id, {"content": "This should fail"})
    
    # Assert error was handled appropriately
    assert "connection" in str(excinfo.value).lower() or "unreachable" in str(excinfo.value).lower()
    
    # Verify client remains operational
    assert await client.is_healthy()
```

### Testing Cross-Protocol Compatibility

```python
async def test_cross_protocol_compatibility(mcp_harness, a2a_harness):
    """Test communication between different protocols."""
    # Create protocol bridge
    bridge = await mcp_harness.create_protocol_bridge(a2a_harness)
    
    # Create endpoints on each protocol
    mcp_endpoint = await mcp_harness.create_endpoint("mcp_agent")
    a2a_endpoint = await a2a_harness.create_endpoint("a2a_agent")
    
    # Register endpoints with bridge
    await bridge.register(mcp_endpoint, a2a_endpoint)
    
    # Test message
    test_message = {
        "content": "Cross-protocol message",
        "metadata": {"cross_protocol": True}
    }
    
    # Send message from MCP to A2A
    await mcp_endpoint.send_message(a2a_endpoint.id, test_message)
    
    # Receive message at A2A endpoint
    received = await a2a_harness.wait_for_message(a2a_endpoint, timeout=5.0)
    
    # Assert message was received correctly
    assert received is not None
    assert received["content"] == test_message["content"]
    assert received["metadata"]["cross_protocol"] == True
    
    # Send message from A2A to MCP
    response = {
        "content": "Cross-protocol response",
        "metadata": {"cross_protocol": True}
    }
    await a2a_endpoint.send_message(mcp_endpoint.id, response)
    
    # Receive message at MCP endpoint
    received_response = await mcp_harness.wait_for_message(mcp_endpoint, timeout=5.0)
    
    # Assert response was received correctly
    assert received_response is not None
    assert received_response["content"] == response["content"]
```

### Testing Security Features

```python
@pytest.mark.parametrize("protocol_type", ["mcp", "a2a", "http", "mqtt", "grpc"])
async def test_authentication(request, protocol_type):
    """Test protocol authentication."""
    # Get protocol harness
    harness = request.getfixturevalue(f"{protocol_type}_harness")
    
    # Configure authentication
    auth_config = {
        "type": "api_key",
        "key": "test-api-key"
    }
    await harness.configure_authentication(auth_config)
    
    # Create authenticated client and server
    server = await harness.create_server(auth_enabled=True)
    client = await harness.create_client(auth_config=auth_config)
    
    # Test authenticated communication
    test_message = {"content": "Authenticated message"}
    await client.send_message(server.id, test_message)
    
    # Verify message was received
    received = await harness.wait_for_message(server, timeout=5.0)
    assert received is not None
    assert received["content"] == test_message["content"]
    
    # Create unauthenticated client
    unauthenticated_client = await harness.create_client(auth_config=None)
    
    # Attempt unauthenticated communication
    with pytest.raises(Exception) as excinfo:
        await unauthenticated_client.send_message(server.id, {"content": "Unauthenticated"})
    
    # Assert authentication error
    assert "authentication" in str(excinfo.value).lower() or "unauthorized" in str(excinfo.value).lower()
```

## Protocol-Specific Tests

### MCP Protocol Tests

```python
async def test_mcp_specific_features(mcp_harness):
    """Test MCP-specific protocol features."""
    # Create MCP endpoints
    client = await mcp_harness.create_endpoint("mcp_client")
    server = await mcp_harness.create_endpoint("mcp_server")
    
    # Test function calling feature of MCP
    function_call_message = {
        "content": "Call function",
        "function_call": {
            "name": "test_function",
            "arguments": {
                "arg1": "value1",
                "arg2": 42
            }
        }
    }
    
    # Register function handler
    function_calls = []
    async def function_handler(call):
        function_calls.append(call)
        return {"result": "success"}
    
    await server.register_function_handler("test_function", function_handler)
    
    # Send function call
    await client.send_message(server.id, function_call_message)
    
    # Wait for function to be called
    await mcp_harness.wait_until(lambda: len(function_calls) > 0, timeout=5.0)
    
    # Assert function was called correctly
    assert len(function_calls) == 1
    assert function_calls[0]["name"] == "test_function"
    assert function_calls[0]["arguments"]["arg1"] == "value1"
    assert function_calls[0]["arguments"]["arg2"] == 42
```

### A2A Protocol Tests

```python
async def test_a2a_specific_features(a2a_harness):
    """Test A2A-specific protocol features."""
    # Create A2A endpoints
    client = await a2a_harness.create_endpoint("a2a_client")
    server = await a2a_harness.create_endpoint("a2a_server")
    
    # Test card feature of A2A
    card_message = {
        "content": "A2A card message",
        "cards": [
            {
                "card_type": "text",
                "content": "Card content",
                "metadata": {"card_id": "card-123"}
            }
        ]
    }
    
    # Send card message
    await client.send_message(server.id, card_message)
    
    # Receive message
    received = await a2a_harness.wait_for_message(server, timeout=5.0)
    
    # Assert card was received correctly
    assert received is not None
    assert "cards" in received
    assert len(received["cards"]) == 1
    assert received["cards"][0]["card_type"] == "text"
    assert received["cards"][0]["content"] == "Card content"
    assert received["cards"][0]["metadata"]["card_id"] == "card-123"
```

## Integration with Agent Testing

```python
from openmas.testing import TestSupervisor

async def test_protocol_agent_integration(mcp_harness):
    """Test protocol integration with agents."""
    # Create test supervisor
    supervisor = TestSupervisor()
    await supervisor.initialize()
    
    try:
        # Create agents using MCP protocol
        agent1_config = {
            "id": "agent1",
            "name": "Agent 1",
            "type": "assistant",
            "capabilities": [{"id": "messaging", "type": "messaging"}],
            "protocol": {"type": "mcp", "transport": "memory"}
        }
        
        agent2_config = {
            "id": "agent2",
            "name": "Agent 2",
            "type": "user",
            "capabilities": [{"id": "messaging", "type": "messaging"}],
            "protocol": {"type": "mcp", "transport": "memory"}
        }
        
        # Add agents to supervisor
        agent1 = await supervisor.add_agent(agent1_config)
        agent2 = await supervisor.add_agent(agent2_config)
        
        # Test protocol functionality in agent context
        message = {"content": "Agent protocol test"}
        
        # Send message between agents
        await supervisor.send_message(
            from_agent=agent1,
            to_agent=agent2,
            message=message
        )
        
        # Verify protocol handled the message correctly
        messages = await supervisor.get_received_messages(agent2.id)
        assert len(messages) == 1
        assert messages[0]["content"] == message["content"]
    
    finally:
        # Shutdown supervisor
        await supervisor.shutdown()
```

## Performance Testing

```python
import pytest
import time
import asyncio
from openmas.testing import PerformanceHarness

@pytest.mark.performance
@pytest.mark.parametrize("protocol_type", ["mcp", "a2a", "http", "mqtt", "grpc"])
async def test_protocol_throughput(request, protocol_type):
    """Test protocol message throughput."""
    # Get protocol harness
    harness = request.getfixturevalue(f"{protocol_type}_harness")
    
    # Create performance harness
    perf_harness = PerformanceHarness(harness)
    
    # Configure test
    message_count = 1000
    message_size = 1024  # bytes
    
    # Run throughput test
    result = await perf_harness.measure_throughput(
        message_count=message_count,
        message_size=message_size
    )
    
    # Assert minimum performance
    assert result.messages_per_second > 100, f"{protocol_type} throughput below threshold"
    assert result.failed_messages == 0, f"{protocol_type} had failed messages"
    
    # Log performance metrics
    print(f"{protocol_type} throughput: {result.messages_per_second:.2f} msgs/sec")
    print(f"{protocol_type} bandwidth: {result.bandwidth_mbps:.2f} Mbps")
```

## Protocol Compliance Matrix

For comprehensive protocol testing, OpenMAS uses a protocol compliance matrix to ensure all features are tested across all protocols:

| Feature | MCP | A2A | HTTP | MQTT | gRPC |
|---------|-----|-----|------|------|------|
| Message Sending | ✓ | ✓ | ✓ | ✓ | ✓ |
| Message Receiving | ✓ | ✓ | ✓ | ✓ | ✓ |
| Function Calling | ✓ | - | - | - | ✓ |
| Card Support | - | ✓ | - | - | - |
| Streaming | ✓ | ✓ | ✓ | - | ✓ |
| Authentication | ✓ | ✓ | ✓ | ✓ | ✓ |
| Encryption | ✓ | ✓ | ✓ | ✓ | ✓ |
| Error Handling | ✓ | ✓ | ✓ | ✓ | ✓ |
| Reconnection | ✓ | ✓ | ✓ | ✓ | ✓ |
| Multiplexing | ✓ | - | - | ✓ | ✓ |
| Quality of Service | - | - | - | ✓ | - |

## Best Practices

1. **Test All Protocols**: Ensure all supported protocols are tested
2. **Protocol-Agnostic Tests**: Write protocol-agnostic tests where possible
3. **Protocol-Specific Tests**: Write protocol-specific tests for unique features
4. **Cross-Protocol Testing**: Test communication between different protocols
5. **Comprehensive Coverage**: Test all protocol features and error scenarios
6. **Performance Testing**: Measure and track protocol performance metrics
7. **Real-World Scenarios**: Test protocols in realistic usage scenarios
8. **Security Testing**: Test authentication and encryption features
9. **Scaling Testing**: Test protocol behavior under high load
10. **Compliance Verification**: Verify protocol implementations comply with specifications

## Related Documentation

- [Async Integration](./async_integration.md)
- [Multi-Agent Testing](./multi_agent_testing.md)
- [Docker Integration](./docker_integration.md)
- [Protocol Documentation](../../02_protocols/README.md)
