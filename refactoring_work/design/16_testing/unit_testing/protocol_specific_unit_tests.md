# Protocol-Specific Unit Tests for OpenMAS

## Overview

This document provides guidelines for writing protocol-specific unit tests for OpenMAS components. Given OpenMAS's multi-protocol support architecture, each protocol adapter requires specialized testing approaches while maintaining the reasoning-agnostic design principle.

## Protocol Testing Principles

1. **Protocol Isolation**: Test each protocol adapter in isolation
2. **Protocol Conformance**: Verify adherence to protocol specifications
3. **Protocol Independence**: Core functionality should be protocol-agnostic
4. **Protocol-Specific Edge Cases**: Test edge cases unique to each protocol
5. **Body-Brain Separation**: Protocol tests focus on communication ("body") not reasoning ("brain")

## A2A Protocol Testing

### Agent Card Tests

```python
def test_a2a_agent_card():
    """Test A2A protocol agent card generation and validation."""
    # Arrange
    adapter = A2AProtocolAdapter()

    # Valid agent card
    valid_card = {
        "id": "test-agent",
        "name": "Test Agent",
        "description": "A test agent",
        "capabilities": [
            {
                "id": "test-capability",
                "name": "Test Capability",
                "description": "A test capability",
                "parameters": [
                    {
                        "name": "param1",
                        "type": "string",
                        "required": True
                    }
                ]
            }
        ]
    }

    # Act & Assert - Valid card
    result = adapter.validate_agent_card(valid_card)
    assert result is True

    # Invalid card (missing id)
    invalid_card = {
        "name": "Test Agent",
        "capabilities": []
    }

    # Act & Assert - Invalid card
    with pytest.raises(A2AProtocolError) as excinfo:
        adapter.validate_agent_card(invalid_card)

    assert "missing required field 'id'" in str(excinfo.value)
```

### Capability Invocation Tests

```python
def test_a2a_capability_invocation():
    """Test A2A protocol capability invocation."""
    # Arrange
    mock_capability_handler = MockCapabilityHandler()
    mock_capability_handler.register_response(
        capability_id="test-capability",
        parameters={"param1": "value1"},
        response={"result": "test-result"}
    )

    adapter = A2AProtocolAdapter(capability_handler=mock_capability_handler)

    # Valid capability invocation
    invocation = {
        "capability_id": "test-capability",
        "parameters": {"param1": "value1"}
    }

    # Act
    result = adapter.invoke_capability(invocation)

    # Assert
    assert result["result"] == "test-result"
    assert mock_capability_handler.last_invocation["capability_id"] == "test-capability"
    assert mock_capability_handler.last_invocation["parameters"]["param1"] == "value1"

    # Invalid capability invocation (missing capability_id)
    invalid_invocation = {
        "parameters": {"param1": "value1"}
    }

    # Act & Assert - Invalid invocation
    with pytest.raises(A2AProtocolError) as excinfo:
        adapter.invoke_capability(invalid_invocation)

    assert "missing required field 'capability_id'" in str(excinfo.value)
```

### A2A Message Format Tests

```python
def test_a2a_message_format():
    """Test A2A protocol message format handling."""
    # Arrange
    adapter = A2AProtocolAdapter()

    # Valid A2A message
    valid_message = {
        "sender": "agent1",
        "recipient": "agent2",
        "capability_id": "test-capability",
        "parameters": {"param1": "value1"},
        "message_id": "msg-123",
        "conversation_id": "conv-456",
        "timestamp": "2023-01-01T12:00:00Z"
    }

    # Act - Validate message format
    result = adapter.validate_message_format(valid_message)

    # Assert
    assert result is True

    # Act - Parse message
    parsed = adapter.parse_message(valid_message)

    # Assert - Parsed correctly
    assert parsed["sender"] == "agent1"
    assert parsed["capability_id"] == "test-capability"
    assert parsed["parameters"]["param1"] == "value1"

    # Invalid message format (missing required fields)
    invalid_message = {
        "sender": "agent1",
        "parameters": {"param1": "value1"}
    }

    # Act & Assert - Invalid message
    with pytest.raises(A2AProtocolError) as excinfo:
        adapter.validate_message_format(invalid_message)

    assert "missing required field" in str(excinfo.value)
```

## MCP Protocol Testing

### MCP Function Tests

```python
def test_mcp_function_registration():
    """Test MCP protocol function registration and validation."""
    # Arrange
    adapter = MCPProtocolAdapter()

    # Valid function definition
    valid_function = {
        "name": "test_function",
        "description": "A test function",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Test parameter"
                }
            },
            "required": ["param1"]
        }
    }

    # Act - Register function
    adapter.register_function(valid_function)

    # Assert
    assert "test_function" in adapter.get_registered_functions()

    # Invalid function (missing name)
    invalid_function = {
        "description": "Invalid function",
        "parameters": {}
    }

    # Act & Assert - Invalid function
    with pytest.raises(MCPProtocolError) as excinfo:
        adapter.register_function(invalid_function)

    assert "missing required field 'name'" in str(excinfo.value)
```

### MCP Function Invocation Tests

```python
def test_mcp_function_invocation():
    """Test MCP protocol function invocation."""
    # Arrange
    mock_function_handler = MockFunctionHandler()
    mock_function_handler.register_response(
        function_name="test_function",
        parameters={"param1": "value1"},
        response={"result": "test-result"}
    )

    adapter = MCPProtocolAdapter(function_handler=mock_function_handler)

    # Register test function
    adapter.register_function({
        "name": "test_function",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            }
        }
    })

    # Valid function invocation
    invocation = {
        "function": "test_function",
        "parameters": {"param1": "value1"}
    }

    # Act
    result = adapter.invoke_function(invocation)

    # Assert
    assert result["result"] == "test-result"
    assert mock_function_handler.last_invocation["function_name"] == "test_function"
    assert mock_function_handler.last_invocation["parameters"]["param1"] == "value1"

    # Invalid function invocation (unknown function)
    invalid_invocation = {
        "function": "unknown_function",
        "parameters": {}
    }

    # Act & Assert - Invalid invocation
    with pytest.raises(MCPProtocolError) as excinfo:
        adapter.invoke_function(invalid_invocation)

    assert "unknown function" in str(excinfo.value)
```

### MCP Message Format Tests

```python
def test_mcp_message_format():
    """Test MCP protocol message format handling."""
    # Arrange
    adapter = MCPProtocolAdapter()

    # Valid MCP message
    valid_message = {
        "version": "1.0",
        "id": "msg-123",
        "function": "test_function",
        "parameters": {"param1": "value1"}
    }

    # Act - Validate message format
    result = adapter.validate_message_format(valid_message)

    # Assert
    assert result is True

    # Act - Parse message
    parsed = adapter.parse_message(valid_message)

    # Assert - Parsed correctly
    assert parsed["function"] == "test_function"
    assert parsed["parameters"]["param1"] == "value1"

    # Invalid message format (missing required fields)
    invalid_message = {
        "id": "msg-123",
        "parameters": {"param1": "value1"}
    }

    # Act & Assert - Invalid message
    with pytest.raises(MCPProtocolError) as excinfo:
        adapter.validate_message_format(invalid_message)

    assert "missing required field" in str(excinfo.value)
```

## HTTP Protocol Testing

### HTTP Route Tests

```python
def test_http_route_registration():
    """Test HTTP protocol route registration."""
    # Arrange
    adapter = HTTPProtocolAdapter()

    # Valid route handler
    def test_handler(request):
        return {"status": "success"}

    # Act - Register route
    adapter.register_route("GET", "/api/test", test_handler)

    # Assert
    routes = adapter.get_registered_routes()
    assert ("GET", "/api/test") in routes

    # Act - Retrieve handler
    handler = adapter.get_route_handler("GET", "/api/test")

    # Assert
    assert handler is not None
    assert handler == test_handler
```

### HTTP Request-Response Tests

```python
def test_http_request_response():
    """Test HTTP protocol request-response handling."""
    # Arrange
    adapter = HTTPProtocolAdapter()

    # Register test route
    adapter.register_route("GET", "/api/test", lambda req: {"status": "success", "data": req.get("query", {}).get("param1")})

    # Create test request
    request = {
        "method": "GET",
        "path": "/api/test",
        "query": {"param1": "value1"},
        "headers": {"Content-Type": "application/json"},
        "body": {}
    }

    # Act
    response = adapter.process_request(request)

    # Assert
    assert response["status_code"] == 200
    assert response["body"]["status"] == "success"
    assert response["body"]["data"] == "value1"

    # Test invalid route
    invalid_request = {
        "method": "GET",
        "path": "/api/unknown",
        "query": {},
        "headers": {},
        "body": {}
    }

    # Act
    response = adapter.process_request(invalid_request)

    # Assert - Not found
    assert response["status_code"] == 404
```

### HTTP Content Type Tests

```python
def test_http_content_types():
    """Test HTTP protocol content type handling."""
    # Arrange
    adapter = HTTPProtocolAdapter()

    # Register test route
    adapter.register_route("POST", "/api/json", lambda req: {"status": "success", "content_type": req["headers"].get("Content-Type")})

    # JSON request
    json_request = {
        "method": "POST",
        "path": "/api/json",
        "query": {},
        "headers": {"Content-Type": "application/json"},
        "body": {"data": "test-data"}
    }

    # Act
    json_response = adapter.process_request(json_request)

    # Assert
    assert json_response["headers"]["Content-Type"] == "application/json"
    assert json_response["body"]["content_type"] == "application/json"

    # Form request
    form_request = {
        "method": "POST",
        "path": "/api/json",
        "query": {},
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "body": "data=test-data"
    }

    # Act
    form_response = adapter.process_request(form_request)

    # Assert
    assert form_response["body"]["content_type"] == "application/x-www-form-urlencoded"
```

## MQTT Protocol Testing

### MQTT Topic Tests

```python
def test_mqtt_topic_subscription():
    """Test MQTT protocol topic subscription."""
    # Arrange
    adapter = MQTTProtocolAdapter()

    # Mock message handler
    mock_handler = MockMessageHandler()

    # Act - Subscribe to topic
    adapter.subscribe("test/topic", mock_handler.handle_message)

    # Assert
    assert "test/topic" in adapter.get_subscriptions()

    # Act - Process message
    adapter.process_message("test/topic", {"data": "test-data"})

    # Assert
    assert mock_handler.received_topic == "test/topic"
    assert mock_handler.received_message["data"] == "test-data"
```

### MQTT Message Publishing Tests

```python
def test_mqtt_message_publishing():
    """Test MQTT protocol message publishing."""
    # Arrange
    mock_client = MockMQTTClient()
    adapter = MQTTProtocolAdapter(client=mock_client)

    # Act - Publish message
    adapter.publish("test/topic", {"data": "test-data"})

    # Assert
    assert mock_client.published_topic == "test/topic"
    assert mock_client.published_message["data"] == "test-data"

    # Test with QoS
    adapter.publish("test/topic", {"data": "test-data-qos"}, qos=2)

    # Assert QoS was passed
    assert mock_client.published_qos == 2
```

### MQTT Topic Pattern Tests

```python
def test_mqtt_topic_patterns():
    """Test MQTT protocol topic pattern matching."""
    # Arrange
    adapter = MQTTProtocolAdapter()

    # Mock handlers
    exact_handler = MockMessageHandler()
    wildcard_handler = MockMessageHandler()
    multi_level_handler = MockMessageHandler()

    # Subscribe with different patterns
    adapter.subscribe("agents/agent1/status", exact_handler.handle_message)
    adapter.subscribe("agents/+/status", wildcard_handler.handle_message)
    adapter.subscribe("agents/#", multi_level_handler.handle_message)

    # Act - Process message matching exact topic
    adapter.process_message("agents/agent1/status", {"status": "online"})

    # Assert
    assert exact_handler.received_topic == "agents/agent1/status"
    assert wildcard_handler.received_topic == "agents/agent1/status"
    assert multi_level_handler.received_topic == "agents/agent1/status"

    # Act - Process message matching wildcard
    adapter.process_message("agents/agent2/status", {"status": "offline"})

    # Assert
    assert exact_handler.received_topic != "agents/agent2/status"  # Shouldn't match
    assert wildcard_handler.received_topic == "agents/agent2/status"
    assert multi_level_handler.received_topic == "agents/agent2/status"

    # Act - Process message matching multi-level wildcard
    adapter.process_message("agents/agent1/telemetry/cpu", {"cpu": 50})

    # Assert
    assert exact_handler.received_topic != "agents/agent1/telemetry/cpu"  # Shouldn't match
    assert wildcard_handler.received_topic != "agents/agent1/telemetry/cpu"  # Shouldn't match
    assert multi_level_handler.received_topic == "agents/agent1/telemetry/cpu"
```

## gRPC Protocol Testing

### gRPC Service Tests

```python
def test_grpc_service_registration():
    """Test gRPC protocol service registration."""
    # Arrange
    adapter = GRPCProtocolAdapter()

    # Define test service
    test_service = {
        "name": "TestService",
        "methods": [
            {
                "name": "TestMethod",
                "input_type": "TestRequest",
                "output_type": "TestResponse"
            }
        ]
    }

    # Act - Register service
    adapter.register_service(test_service)

    # Assert
    services = adapter.get_registered_services()
    assert "TestService" in services

    # Act - Get service methods
    methods = adapter.get_service_methods("TestService")

    # Assert
    assert len(methods) == 1
    assert methods[0]["name"] == "TestMethod"
```

### gRPC Method Invocation Tests

```python
def test_grpc_method_invocation():
    """Test gRPC protocol method invocation."""
    # Arrange
    mock_method_handler = MockMethodHandler()
    mock_method_handler.register_response(
        service="TestService",
        method="TestMethod",
        request={"param1": "value1"},
        response={"result": "test-result"}
    )

    adapter = GRPCProtocolAdapter(method_handler=mock_method_handler)

    # Register test service
    adapter.register_service({
        "name": "TestService",
        "methods": [
            {
                "name": "TestMethod",
                "input_type": "TestRequest",
                "output_type": "TestResponse"
            }
        ]
    })

    # Act - Invoke method
    result = adapter.invoke_method(
        service="TestService",
        method="TestMethod",
        request={"param1": "value1"}
    )

    # Assert
    assert result["result"] == "test-result"
    assert mock_method_handler.last_invocation["service"] == "TestService"
    assert mock_method_handler.last_invocation["method"] == "TestMethod"
    assert mock_method_handler.last_invocation["request"]["param1"] == "value1"

    # Invalid invocation (unknown service)
    with pytest.raises(GRPCProtocolError) as excinfo:
        adapter.invoke_method(
            service="UnknownService",
            method="TestMethod",
            request={}
        )

    assert "unknown service" in str(excinfo.value)

    # Invalid invocation (unknown method)
    with pytest.raises(GRPCProtocolError) as excinfo:
        adapter.invoke_method(
            service="TestService",
            method="UnknownMethod",
            request={}
        )

    assert "unknown method" in str(excinfo.value)
```

### gRPC Streaming Tests

```python
async def test_grpc_streaming():
    """Test gRPC protocol streaming."""
    # Arrange
    mock_stream_handler = MockStreamHandler()
    adapter = GRPCProtocolAdapter(stream_handler=mock_stream_handler)

    # Register test service with streaming method
    adapter.register_service({
        "name": "StreamService",
        "methods": [
            {
                "name": "StreamMethod",
                "input_type": "StreamRequest",
                "output_type": "StreamResponse",
                "is_server_streaming": True
            }
        ]
    })

    # Prepare test data
    test_messages = [
        {"index": 0, "data": "message-0"},
        {"index": 1, "data": "message-1"},
        {"index": 2, "data": "message-2"}
    ]

    # Configure mock to yield test messages
    mock_stream_handler.set_stream_messages(
        service="StreamService",
        method="StreamMethod",
        request={"stream": True},
        messages=test_messages
    )

    # Act - Create stream
    stream = adapter.create_stream(
        service="StreamService",
        method="StreamMethod",
        request={"stream": True}
    )

    # Assert
    received_messages = []
    async for message in stream:
        received_messages.append(message)

    assert len(received_messages) == 3
    assert received_messages[0]["index"] == 0
    assert received_messages[1]["index"] == 1
    assert received_messages[2]["index"] == 2
    assert received_messages[0]["data"] == "message-0"
```

## Cross-Protocol Tests

### Protocol Conversion Tests

```python
def test_protocol_conversion():
    """Test conversion between protocols."""
    # Arrange
    converter = ProtocolConverter()

    # A2A message
    a2a_message = {
        "capability_id": "test-capability",
        "parameters": {"param1": "value1"}
    }

    # Act - Convert A2A to MCP
    mcp_message = converter.convert(a2a_message, source="a2a", target="mcp")

    # Assert
    assert mcp_message["function"] == "test-capability"
    assert mcp_message["parameters"]["param1"] == "value1"

    # Act - Convert MCP back to A2A
    reconverted = converter.convert(mcp_message, source="mcp", target="a2a")

    # Assert
    assert reconverted["capability_id"] == "test-capability"
    assert reconverted["parameters"]["param1"] == "value1"

    # Act - Convert A2A to HTTP
    http_request = converter.convert(a2a_message, source="a2a", target="http")

    # Assert
    assert http_request["method"] == "POST"
    assert http_request["path"].endswith("/test-capability")
    assert http_request["body"]["param1"] == "value1"
```

### Multi-Protocol Adapter Tests

```python
def test_multi_protocol_adapter():
    """Test adapter that supports multiple protocols."""
    # Arrange
    adapter = MultiProtocolAdapter()

    # Register protocol-specific adapters
    a2a_adapter = MockA2AAdapter()
    mcp_adapter = MockMCPAdapter()
    http_adapter = MockHTTPAdapter()

    adapter.register_protocol_adapter("a2a", a2a_adapter)
    adapter.register_protocol_adapter("mcp", mcp_adapter)
    adapter.register_protocol_adapter("http", http_adapter)

    # Act - Process message with different protocols
    a2a_result = adapter.process_message(
        {"capability_id": "test-capability"},
        protocol="a2a"
    )

    mcp_result = adapter.process_message(
        {"function": "test_function"},
        protocol="mcp"
    )

    http_result = adapter.process_message(
        {"method": "GET", "path": "/api/test"},
        protocol="http"
    )

    # Assert
    assert a2a_adapter.was_called is True
    assert mcp_adapter.was_called is True
    assert http_adapter.was_called is True

    # Assert - Protocol detection
    auto_detected = adapter.process_message(
        {"capability_id": "test-capability"}
    )

    assert a2a_adapter.was_called is True
    assert auto_detected == a2a_result
```

## Protocol Configuration Tests

### Protocol Configuration Validation Tests

```python
def test_protocol_configuration_validation():
    """Test validation of protocol-specific configurations."""
    # Arrange
    validator = ProtocolConfigValidator()

    # Valid A2A configuration
    valid_a2a_config = {
        "enabled": True,
        "endpoint": "http://localhost:8080",
        "mode": "server"
    }

    # Act & Assert - Valid config
    result = validator.validate("a2a", valid_a2a_config)
    assert result is True

    # Invalid A2A configuration (missing endpoint)
    invalid_a2a_config = {
        "enabled": True,
        "mode": "server"
    }

    # Act & Assert - Invalid config
    with pytest.raises(ConfigurationError) as excinfo:
        validator.validate("a2a", invalid_a2a_config)

    assert "missing required field 'endpoint'" in str(excinfo.value)

    # Valid MQTT configuration
    valid_mqtt_config = {
        "enabled": True,
        "broker": {
            "host": "localhost",
            "port": 1883
        },
        "client_id": "test-client"
    }

    # Act & Assert - Valid config
    result = validator.validate("mqtt", valid_mqtt_config)
    assert result is True

    # Invalid MQTT configuration (invalid broker config)
    invalid_mqtt_config = {
        "enabled": True,
        "broker": "localhost:1883",
        "client_id": "test-client"
    }

    # Act & Assert - Invalid config
    with pytest.raises(ConfigurationError) as excinfo:
        validator.validate("mqtt", invalid_mqtt_config)

    assert "expected object for field 'broker'" in str(excinfo.value)
```

### Protocol Feature Configuration Tests

```python
def test_protocol_feature_configuration():
    """Test configuration of protocol-specific features."""
    # Arrange
    a2a_adapter = A2AProtocolAdapter()

    # Configure authentication
    a2a_adapter.configure({
        "authentication": {
            "enabled": True,
            "provider": "jwt",
            "config": {
                "secret_key": "test-key",
                "algorithm": "HS256"
            }
        }
    })

    # Assert
    assert a2a_adapter.is_authentication_enabled() is True
    assert a2a_adapter.get_authentication_provider() == "jwt"

    # Configure rate limiting
    a2a_adapter.configure({
        "rate_limiting": {
            "enabled": True,
            "max_requests": 100,
            "time_window": 60
        }
    })

    # Assert
    assert a2a_adapter.is_rate_limiting_enabled() is True
    assert a2a_adapter.get_rate_limit_config()["max_requests"] == 100
    assert a2a_adapter.get_rate_limit_config()["time_window"] == 60
```

## Best Practices

1. **Test Protocol Specifications**: Verify conformance to protocol specifications
2. **Test Message Formats**: Validate correct handling of protocol-specific message formats
3. **Test Edge Cases**: Cover edge cases unique to each protocol
4. **Test Protocol Features**: Test protocol-specific features like streaming, topic patterns, etc.
5. **Test Error Handling**: Verify proper error handling for protocol-specific errors
6. **Test Configuration**: Validate protocol-specific configuration options
7. **Test Interoperability**: Verify conversion between protocols works correctly
8. **Test Security Features**: Test protocol-specific security features
9. **Maintain Body-Brain Separation**: Focus on communication aspects, not reasoning
10. **Use Mock Services**: Avoid external dependencies in protocol tests

## Related Documentation

- [Test Patterns](./test_patterns.md)
- [Test Framework](../framework/README.md)
- [Protocol Testing](../integration_testing/protocol_testing.md)
- [Multi-Agent Testing](../integration_testing/multi_agent_testing.md)
- [Testing Tools](../testing_tools/README.md)
