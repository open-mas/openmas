# Test Patterns for OpenMAS Unit Testing

## Overview

This document describes common test patterns for unit testing OpenMAS components. These patterns ensure consistent testing approaches across components while preserving OpenMAS's reasoning-agnostic architecture and multi-protocol support.

## Core Test Patterns

### Component Initialization Tests

Test pattern for verifying component initialization:

```python
def test_component_initialization():
    """Test that a component initializes correctly with valid configuration."""
    # Arrange
    config = {
        "id": "test-component",
        "name": "Test Component",
        "enabled": True
    }
    
    # Act
    component = Component(**config)
    
    # Assert
    assert component.id == "test-component"
    assert component.name == "Test Component"
    assert component.is_enabled is True
    assert component.is_initialized() is False
    
    # Act - Initialize
    component.initialize()
    
    # Assert - Post-initialization
    assert component.is_initialized() is True
```

### Configuration Validation Tests

Test pattern for configuration validation:

```python
import pytest

def test_configuration_validation():
    """Test that configuration validation catches invalid configurations."""
    # Arrange - Valid configuration
    valid_config = {
        "id": "test-component",
        "name": "Test Component",
        "enabled": True
    }
    
    # Act & Assert - Valid configuration
    component = Component(**valid_config)  # Should not raise exception
    
    # Arrange - Invalid configuration (missing required field)
    invalid_config = {
        "name": "Test Component",
        "enabled": True
    }
    
    # Act & Assert - Invalid configuration
    with pytest.raises(ConfigurationError) as excinfo:
        component = Component(**invalid_config)
    
    assert "required field 'id'" in str(excinfo.value)
    
    # Arrange - Invalid configuration (wrong type)
    invalid_type_config = {
        "id": "test-component",
        "name": "Test Component",
        "enabled": "not-a-boolean"
    }
    
    # Act & Assert - Invalid type
    with pytest.raises(ConfigurationError) as excinfo:
        component = Component(**invalid_type_config)
    
    assert "expected boolean for field 'enabled'" in str(excinfo.value)
```

### Dependency Injection Tests

Test pattern for dependency injection:

```python
def test_dependency_injection():
    """Test that dependencies can be properly injected."""
    # Arrange
    mock_dependency = MockDependency()
    
    # Act
    component = Component(
        id="test-component",
        dependency=mock_dependency
    )
    
    # Assert
    assert component.dependency is mock_dependency
    
    # Act - Use dependency
    result = component.use_dependency()
    
    # Assert - Dependency was used correctly
    assert result == "expected-result"
    assert mock_dependency.was_called is True
```

### Protocol Independence Tests

Test pattern for protocol-independent functionality:

```python
@pytest.mark.parametrize("protocol", ["a2a", "mcp", "http", "mqtt", "grpc"])
def test_protocol_independence(protocol):
    """Test that core functionality works with any protocol."""
    # Arrange
    mock_protocol_adapter = MockProtocolAdapter(protocol_type=protocol)
    
    component = Component(
        id="test-component",
        protocol_adapter=mock_protocol_adapter
    )
    
    # Act
    result = component.process_message("test-message")
    
    # Assert - Same result regardless of protocol
    assert result == "expected-result"
```

### Body-Brain Separation Tests

Test pattern for verifying body-brain separation:

```python
def test_body_brain_separation():
    """Test that communication infrastructure is separate from reasoning."""
    # Arrange
    mock_body = MockCommunicator()
    mock_brain = MockReasoner()
    
    agent = Agent(
        id="test-agent",
        communicator=mock_body,
        reasoner=mock_brain
    )
    
    # Act - Process incoming message
    result = agent.process_message("test-message")
    
    # Assert - Communication processed by body
    assert mock_body.received_message == "test-message"
    
    # Assert - Reasoning processed by brain
    assert mock_brain.was_invoked is True
    
    # Assert - Body and brain interaction
    assert mock_body.sent_to_brain == "processed-message"
    assert mock_brain.received_from_body == "processed-message"
```

### Error Handling Tests

Test pattern for error handling:

```python
def test_error_handling():
    """Test that component handles errors appropriately."""
    # Arrange
    component = Component(id="test-component")
    
    # Arrange - Mock dependency that will raise exception
    mock_dependency = MockDependency(should_fail=True)
    component.set_dependency(mock_dependency)
    
    # Act & Assert - Expected exception type
    with pytest.raises(ComponentError) as excinfo:
        component.use_dependency()
    
    assert "dependency operation failed" in str(excinfo.value)
    
    # Act - Using error-tolerant method
    result = component.try_use_dependency()
    
    # Assert - Graceful failure
    assert result is None
    assert component.last_error is not None
    assert component.is_operational is True  # Still operational despite error
```

### Lifecycle Tests

Test pattern for component lifecycle:

```python
def test_component_lifecycle():
    """Test the full lifecycle of a component."""
    # Arrange
    component = Component(id="test-component")
    
    # Assert - Initial state
    assert component.is_initialized() is False
    assert component.is_running() is False
    
    # Act - Initialize
    component.initialize()
    
    # Assert - Post-initialization
    assert component.is_initialized() is True
    assert component.is_running() is False
    
    # Act - Start
    component.start()
    
    # Assert - Running state
    assert component.is_running() is True
    
    # Act - Stop
    component.stop()
    
    # Assert - Stopped state
    assert component.is_initialized() is True
    assert component.is_running() is False
    
    # Act - Shutdown
    component.shutdown()
    
    # Assert - Final state
    assert component.is_initialized() is False
    assert component.is_running() is False
```

### Configuration Override Tests

Test pattern for configuration overrides:

```python
def test_configuration_overrides():
    """Test that configuration can be overridden properly."""
    # Arrange - Base configuration
    base_config = {
        "id": "test-component",
        "name": "Test Component",
        "settings": {
            "timeout": 30,
            "retry_count": 3
        }
    }
    
    # Arrange - Override configuration
    override_config = {
        "settings": {
            "timeout": 60
        }
    }
    
    # Act
    component = Component(base_config)
    component.override_config(override_config)
    
    # Assert - Overridden values
    assert component.config["settings"]["timeout"] == 60
    
    # Assert - Non-overridden values preserved
    assert component.config["id"] == "test-component"
    assert component.config["settings"]["retry_count"] == 3
```

## Protocol-Specific Test Patterns

### A2A Protocol Test Pattern

```python
def test_a2a_protocol_adapter():
    """Test A2A protocol adapter specifically."""
    # Arrange
    adapter = A2AProtocolAdapter(
        endpoint="http://localhost:8080",
        agent_card={
            "id": "test-agent",
            "capabilities": [
                {"id": "test-capability"}
            ]
        }
    )
    
    # Act - Process A2A format message
    a2a_message = {
        "capability_id": "test-capability",
        "parameters": {"param1": "value1"}
    }
    
    result = adapter.process_message(a2a_message)
    
    # Assert - A2A specific processing
    assert result["capability_id"] == "test-capability"
    assert adapter.last_message_protocol == "a2a"
```

### MCP Protocol Test Pattern

```python
def test_mcp_protocol_adapter():
    """Test MCP protocol adapter specifically."""
    # Arrange
    adapter = MCPProtocolAdapter(
        endpoint="http://localhost:8100",
        functions=[
            {
                "name": "test_function",
                "parameters": {"param1": {"type": "string"}}
            }
        ]
    )
    
    # Act - Process MCP format message
    mcp_message = {
        "function": "test_function",
        "parameters": {"param1": "value1"}
    }
    
    result = adapter.process_message(mcp_message)
    
    # Assert - MCP specific processing
    assert result["function"] == "test_function"
    assert adapter.last_message_protocol == "mcp"
```

## Reasoning Engine Test Patterns

### Rule-Based Reasoning Test Pattern

```python
def test_rule_engine():
    """Test rule-based reasoning engine."""
    # Arrange
    engine = RuleEngine()
    
    # Add test rule
    engine.add_rule(
        name="test-rule",
        condition="x > 10",
        action="result = x * 2"
    )
    
    # Act - Process with rules
    context = {"x": 15}
    result = engine.process(context)
    
    # Assert
    assert result["result"] == 30
    
    # Act - Process with different context
    context = {"x": 5}
    result = engine.process(context)
    
    # Assert - Rule not triggered
    assert "result" not in result
```

### BDI Reasoning Test Pattern

```python
def test_bdi_engine():
    """Test BDI reasoning engine."""
    # Arrange
    engine = BDIEngine()
    
    # Add beliefs, desires, and plans
    engine.add_belief("location", "home")
    engine.add_desire("reach_destination", {"destination": "work"})
    engine.add_plan(
        name="travel_plan",
        trigger="reach_destination",
        context="location != destination",
        body=["set_location(destination)"]
    )
    
    # Act - Run reasoning cycle
    result = engine.reason()
    
    # Assert
    assert result["selected_plan"] == "travel_plan"
    assert result["new_beliefs"]["location"] == "work"
```

### LLM Reasoning Test Pattern

```python
async def test_llm_engine():
    """Test LLM-based reasoning engine."""
    # Arrange
    mock_llm_provider = MockLLMProvider(
        responses={
            "What is the capital of France?": "The capital of France is Paris."
        }
    )
    
    engine = LLMEngine(llm_provider=mock_llm_provider)
    
    # Act
    result = await engine.reason(
        prompt="What is the capital of France?"
    )
    
    # Assert
    assert "Paris" in result
    assert mock_llm_provider.called_with == "What is the capital of France?"
```

### Knowledge Graph Reasoning Test Pattern

```python
def test_knowledge_graph_engine():
    """Test knowledge graph reasoning engine."""
    # Arrange
    engine = KnowledgeGraphEngine()
    
    # Add test data to graph
    engine.add_node("Alice", type="Person")
    engine.add_node("Bob", type="Person")
    engine.add_relationship("Alice", "knows", "Bob")
    
    # Act - Run query
    result = engine.query(
        "MATCH (a:Person)-[r:knows]->(b:Person) RETURN a.name, b.name"
    )
    
    # Assert
    assert len(result) == 1
    assert result[0]["a.name"] == "Alice"
    assert result[0]["b.name"] == "Bob"
```

## Mocking Patterns

### Protocol Adapter Mocking

```python
class MockProtocolAdapter:
    """Mock protocol adapter for testing."""
    
    def __init__(self, protocol_type="http"):
        self.protocol_type = protocol_type
        self.messages = []
        self.responses = {}
        
    def register_response(self, message, response):
        """Register a response for a specific message."""
        self.responses[str(message)] = response
        
    def send_message(self, message):
        """Mock sending a message."""
        self.messages.append(message)
        return self.responses.get(str(message), {"status": "default-response"})

# Usage in tests
def test_with_mock_protocol():
    """Test using a mock protocol adapter."""
    # Arrange
    mock_adapter = MockProtocolAdapter(protocol_type="a2a")
    mock_adapter.register_response(
        {"capability": "test-capability"},
        {"status": "success", "result": "test-result"}
    )
    
    component = Component(protocol_adapter=mock_adapter)
    
    # Act
    result = component.invoke_capability("test-capability")
    
    # Assert
    assert result["status"] == "success"
    assert result["result"] == "test-result"
    assert len(mock_adapter.messages) == 1
    assert mock_adapter.messages[0]["capability"] == "test-capability"
```

### Reasoning Engine Mocking

```python
class MockReasoner:
    """Mock reasoner for testing."""
    
    def __init__(self):
        self.inputs = []
        self.responses = {}
        self.was_invoked = False
        
    def register_response(self, input_data, response):
        """Register a response for specific input."""
        self.responses[str(input_data)] = response
        
    def reason(self, input_data):
        """Mock reasoning process."""
        self.was_invoked = True
        self.inputs.append(input_data)
        return self.responses.get(str(input_data), {"status": "default-response"})

# Usage in tests
def test_with_mock_reasoner():
    """Test using a mock reasoner."""
    # Arrange
    mock_reasoner = MockReasoner()
    mock_reasoner.register_response(
        {"query": "test-query"},
        {"answer": "test-answer"}
    )
    
    agent = Agent(reasoner=mock_reasoner)
    
    # Act
    result = agent.answer_query("test-query")
    
    # Assert
    assert result == "test-answer"
    assert mock_reasoner.was_invoked is True
    assert len(mock_reasoner.inputs) == 1
    assert mock_reasoner.inputs[0]["query"] == "test-query"
```

## Best Practices

1. **Test Isolation**: Each test should be completely independent
2. **Descriptive Names**: Test names should clearly describe what is being tested
3. **Arrange-Act-Assert**: Structure tests with clear arrangement, action, and assertion phases
4. **Parameterized Testing**: Use parameterized tests for multiple similar test cases
5. **Comprehensive Assertions**: Assert all relevant conditions and state changes
6. **Error Scenario Testing**: Test both success and error scenarios
7. **Protocol-Specific Testing**: Use protocol-specific tests for protocol adapters
8. **Body-Brain Separation**: Maintain separation between communication and reasoning in tests
9. **Mock External Dependencies**: Always mock external services and dependencies
10. **Configuration Testing**: Test components with different configurations

## Related Documentation

- [Protocol-Specific Unit Tests](./protocol_specific_unit_tests.md)
- [Test Framework](../framework/README.md)
- [Integration Testing](../integration_testing/README.md)
- [Testing Tools](../testing_tools/README.md)
