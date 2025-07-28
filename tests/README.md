# OpenMAS Comprehensive Testing Framework

This document provides comprehensive guidance for testing OpenMAS 0.3.0, including the advanced TestSupervisor framework, protocol-specific testing patterns, performance benchmarking, and CI/CD integration.

## Table of Contents

1. [Overview](#overview)
2. [Test Architecture](#test-architecture)
3. [TestSupervisor Framework](#testsupervisor-framework)
4. [Test Categories](#test-categories)
5. [Running Tests](#running-tests)
6. [Writing Tests](#writing-tests)
7. [Performance Testing](#performance-testing)
8. [Protocol Testing](#protocol-testing)
9. [CI/CD Integration](#cicd-integration)
10. [Coverage Requirements](#coverage-requirements)
11. [Best Practices](#best-practices)

## Overview

OpenMAS 0.3.0 implements a comprehensive testing framework designed to ensure:

- **≥85% test coverage** across all components
- **Zero regression policy** - all existing tests must continue to pass
- **Robust async test coordination** with TestSupervisor
- **Protocol-agnostic testing** supporting MCP, A2A, HTTP, MQTT
- **Performance regression detection** with automated benchmarking
- **Anti-hallucination validation** using real protocol implementations

## Test Architecture

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── agent/              # Agent framework tests
│   ├── protocols/          # Protocol adapter tests
│   ├── reasoning/          # Reasoning engine tests
│   └── utils/              # Utility component tests
├── integration/            # Integration tests
│   ├── agent_communication/
│   ├── protocol_integration/
│   └── multi_agent/
├── protocols/              # Protocol-specific tests
│   ├── test_mcp.py
│   ├── test_a2a.py
│   ├── test_http.py
│   └── test_mqtt.py
├── performance/            # Performance and benchmarking tests
├── e2e/                   # End-to-end scenario tests
├── utils/                 # Testing utilities and frameworks
│   ├── test_supervisor.py     # TestSupervisor implementation
│   ├── protocol_mocks.py      # Protocol testing utilities
│   ├── async_testing.py       # Async testing utilities
│   └── performance_utils.py   # Performance testing utilities
└── conftest.py            # Pytest configuration and fixtures
```

## TestSupervisor Framework

The TestSupervisor provides advanced async test coordination to prevent test hangs and ensure proper resource cleanup.

### Key Features

- **Event-based coordination** replacing unreliable time-based waits
- **Automatic agent lifecycle management** with proper startup/shutdown
- **Resource cleanup guarantees** preventing memory leaks and hanging tests
- **Timeout management** with configurable timeouts per test phase
- **Multi-agent coordination** for complex interaction testing

### Basic Usage

```python
import pytest
from tests.utils import TestSupervisor

@pytest.mark.asyncio
async def test_agent_communication(test_supervisor):
    """Test agent communication with TestSupervisor coordination."""
    
    # Create agents through supervisor
    agent1 = await test_supervisor.create_supervised_agent("agent1", agent_config1)
    agent2 = await test_supervisor.create_supervised_agent("agent2", agent_config2)
    
    # Wait for agents to be ready
    await test_supervisor.wait_for_agents_ready([agent1, agent2])
    
    # Perform test operations
    message = create_text_message("Hello", sender="agent1", target="agent2")
    await agent1.send_message(message)
    
    # Wait for message processing
    await test_supervisor.wait_for_condition(
        lambda: len(agent2.received_messages) > 0,
        timeout=5.0,
        description="Agent2 receives message"
    )
    
    # Assertions
    assert len(agent2.received_messages) == 1
    assert agent2.received_messages[0].content == "Hello"
    
    # Cleanup is automatic via supervisor
```

### Advanced Patterns

```python
@pytest.mark.asyncio
async def test_multi_agent_workflow(test_supervisor):
    """Test complex multi-agent workflow with event coordination."""
    
    # Create multiple agents
    agents = await test_supervisor.create_agent_group([
        ("processor", processor_config),
        ("analyzer", analyzer_config),
        ("reporter", reporter_config)
    ])
    
    # Set up event-based coordination
    workflow_events = []
    
    async def track_workflow_event(event_type, agent_id, data):
        workflow_events.append((event_type, agent_id, data))
    
    test_supervisor.add_event_handler("workflow_step", track_workflow_event)
    
    # Execute workflow
    document = {"content": "Test document", "type": "text"}
    await agents["processor"].process_document(document)
    
    # Wait for workflow completion
    await test_supervisor.wait_for_condition(
        lambda: len(workflow_events) >= 3,  # All steps completed
        timeout=10.0,
        description="Complete workflow execution"
    )
    
    # Verify workflow steps
    assert workflow_events[0][0] == "document_processed"
    assert workflow_events[1][0] == "analysis_completed"
    assert workflow_events[2][0] == "report_generated"
```

## Test Categories

### Unit Tests

Test individual components in isolation:

```python
@pytest.mark.asyncio
async def test_agent_capability_registration():
    """Test agent capability registration."""
    agent = Agent(agent_config)
    
    capability = TestCapability("test_capability")
    await agent.register_capability(capability)
    
    capabilities = await agent.get_capabilities()
    assert "test_capability" in capabilities
```

### Integration Tests

Test component interactions:

```python
@pytest.mark.asyncio
async def test_agent_protocol_integration(test_supervisor):
    """Test agent integration with protocol adapters."""
    
    # Create agent with MCP protocol
    mcp_adapter = MCPAdapter(mcp_config)
    agent = await test_supervisor.create_supervised_agent(
        "test_agent", 
        agent_config,
        protocol_adapters={"mcp": mcp_adapter}
    )
    
    # Test protocol communication
    message = create_invocation_message("test_method", {}, "external_client", "test_agent")
    await mcp_adapter.send_message(message)
    
    # Verify message routing
    await test_supervisor.wait_for_condition(
        lambda: len(agent.received_messages) > 0,
        timeout=5.0
    )
    
    assert agent.received_messages[0].message_type == MessageType.CAPABILITY_INVOCATION
```

### Protocol Tests

Test protocol-specific functionality:

```python
@pytest.mark.asyncio
async def test_mcp_protocol_compliance():
    """Test MCP protocol compliance."""
    
    async with MCPTestHarness() as harness:
        # Test server capabilities
        capabilities = await harness.client.list_capabilities()
        assert "test_capability" in capabilities
        
        # Test method invocation
        result = await harness.client.invoke_capability("test_capability", {"param": "value"})
        assert result["status"] == "success"
        
        # Test error handling
        with pytest.raises(MCPError):
            await harness.client.invoke_capability("nonexistent_capability", {})
```

## Running Tests

### Local Development

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/openmas --cov-report=html

# Run specific test categories
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/protocols/

# Run with TestSupervisor debugging
poetry run pytest -v --tb=short --log-cli-level=DEBUG

# Run performance tests
poetry run pytest tests/performance/ --benchmark-json=results.json
```

### CI/CD Pipeline

The comprehensive testing pipeline runs automatically on:

- **Push to main/develop branches**
- **Pull requests**
- **Nightly scheduled runs**

Pipeline includes:

1. **Matrix Testing**: Python 3.10-3.12 on Ubuntu/macOS/Windows
2. **Coverage Testing**: ≥85% coverage requirement
3. **Performance Testing**: Regression detection with baselines
4. **Protocol Testing**: All supported protocols
5. **Security Scanning**: Dependency and code security checks
6. **Documentation Testing**: Example code validation

## Writing Tests

### Test Structure

Follow this structure for new tests:

```python
"""
Test module docstring describing what is being tested.
"""

import pytest
from tests.utils import TestSupervisor, create_test_agent
from openmas.agent import Agent
from openmas.protocols import MCPAdapter

class TestAgentFeature:
    """Test class for specific agent feature."""
    
    @pytest.mark.asyncio
    async def test_basic_functionality(self, test_supervisor):
        """Test basic functionality with clear description."""
        # Arrange
        agent = await test_supervisor.create_supervised_agent("test", config)
        
        # Act
        result = await agent.perform_action()
        
        # Assert
        assert result.success
        assert result.data == expected_data
    
    @pytest.mark.asyncio
    async def test_error_handling(self, test_supervisor):
        """Test error handling scenarios."""
        agent = await test_supervisor.create_supervised_agent("test", config)
        
        with pytest.raises(ExpectedError):
            await agent.perform_invalid_action()
    
    @pytest.mark.parametrize("input_data,expected", [
        ({"param": "value1"}, "result1"),
        ({"param": "value2"}, "result2"),
    ])
    @pytest.mark.asyncio
    async def test_parameterized(self, test_supervisor, input_data, expected):
        """Test with multiple parameter sets."""
        agent = await test_supervisor.create_supervised_agent("test", config)
        result = await agent.process(input_data)
        assert result == expected
```

### TestSupervisor Integration

Always use TestSupervisor for async tests:

```python
@pytest.mark.asyncio
async def test_with_supervisor(test_supervisor):
    """Proper TestSupervisor usage pattern."""
    
    # Create agents through supervisor
    agent = await test_supervisor.create_supervised_agent("test", config)
    
    # Use supervisor for coordination
    await test_supervisor.wait_for_agent_ready(agent)
    
    # Perform test operations
    await agent.start_operation()
    
    # Wait for completion with timeout
    await test_supervisor.wait_for_condition(
        lambda: agent.operation_complete,
        timeout=10.0,
        description="Operation completion"
    )
    
    # Cleanup is automatic
```

## Performance Testing

### Benchmarking

Use performance utilities for benchmarking:

```python
from tests.utils.performance_utils import PerformanceTester, PerformanceBenchmark

@pytest.mark.asyncio
async def test_agent_startup_performance():
    """Benchmark agent startup time."""
    
    async def create_and_start_agent():
        agent = Agent(test_config)
        await agent.start()
        await agent.stop()
    
    tester = PerformanceTester()
    metrics = await tester.measure_operation(
        "agent_startup",
        create_and_start_agent,
        iterations=50
    )
    
    # Assert performance requirements
    assert metrics.execution_time < 1.0  # < 1 second startup
    assert metrics.memory_usage_mb < 100  # < 100MB memory
```

### Load Testing

```python
@pytest.mark.asyncio
async def test_message_processing_load():
    """Test message processing under load."""
    
    async def send_message():
        message = create_test_message()
        await agent.handle_message(message)
    
    load_tester = LoadTester()
    results = await load_tester.run_concurrent_load_test(
        operation_factory=send_message,
        concurrent_users=10,
        operations_per_user=100
    )
    
    assert results['successful_operations'] >= 950  # 95% success rate
    assert results['avg_response_time'] < 0.1  # < 100ms average
```

## Protocol Testing

### MCP Protocol Testing

```python
@pytest.mark.asyncio
async def test_mcp_integration():
    """Test MCP protocol integration."""
    
    async with MCPTestHarness() as harness:
        # Test capability discovery
        capabilities = await harness.client.list_capabilities()
        assert len(capabilities) > 0
        
        # Test method invocation
        result = await harness.invoke_capability("test_method", {"param": "value"})
        assert result["success"] is True
        
        # Test streaming
        async for chunk in harness.stream_capability("stream_method", {}):
            assert "data" in chunk
```

### A2A Protocol Testing

```python
@pytest.mark.asyncio
async def test_a2a_integration():
    """Test Google A2A protocol integration."""
    
    async with A2ATestHarness() as harness:
        # Test agent registration
        await harness.register_agent("test_agent")
        
        # Test message routing
        message = create_a2a_message("Hello", "agent1", "agent2")
        await harness.send_message(message)
        
        # Verify delivery
        received = await harness.wait_for_message("agent2", timeout=5.0)
        assert received.content == "Hello"
```

## Coverage Requirements

### Minimum Coverage Targets

- **Overall**: ≥85% line coverage
- **Critical Components**: ≥95% line coverage
  - Agent framework
  - Protocol adapters
  - Message routing
  - Security components
- **New Code**: 100% line coverage

### Coverage Exclusions

```python
# pragma: no cover - for defensive code that shouldn't be reached
if sys.platform == "win32":  # pragma: no cover
    # Windows-specific fallback
    pass

# Type checking blocks
if TYPE_CHECKING:  # pragma: no cover
    from typing import Optional
```

### Measuring Coverage

```bash
# Generate coverage report
poetry run pytest --cov=src/openmas --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html

# Check coverage thresholds
poetry run pytest --cov=src/openmas --cov-fail-under=85
```

## Best Practices

### 1. Use TestSupervisor for All Async Tests

```python
# ✅ Good - Uses TestSupervisor
@pytest.mark.asyncio
async def test_with_supervisor(test_supervisor):
    agent = await test_supervisor.create_supervised_agent("test", config)
    # Test logic here

# ❌ Bad - Manual async management
@pytest.mark.asyncio
async def test_without_supervisor():
    agent = Agent(config)
    await agent.start()
    # Test logic here
    await agent.stop()  # Easy to forget!
```

### 2. Write Descriptive Test Names

```python
# ✅ Good - Clear intent
async def test_agent_sends_capability_invocation_message_to_target():
    pass

# ❌ Bad - Unclear intent
async def test_agent_message():
    pass
```

### 3. Use Proper Assertions

```python
# ✅ Good - Specific assertions
assert response.status_code == 200
assert response.data["result"] == "success"
assert len(response.data["items"]) == 3

# ❌ Bad - Generic assertions
assert response
assert response.data
```

### 4. Test Error Conditions

```python
# ✅ Good - Tests both success and failure
async def test_capability_invocation_with_invalid_params(test_supervisor):
    agent = await test_supervisor.create_supervised_agent("test", config)
    
    with pytest.raises(InvalidParameterError) as exc_info:
        await agent.invoke_capability("test_capability", {"invalid": "params"})
    
    assert "invalid parameter" in str(exc_info.value)
```

### 5. Use Fixtures for Common Setup

```python
@pytest.fixture
async def configured_agent(test_supervisor):
    """Fixture providing a fully configured test agent."""
    config = AgentConfig(
        agent_id="test_agent",
        capabilities=["test_capability"],
        protocols=["mcp"]
    )
    return await test_supervisor.create_supervised_agent("test", config)

async def test_with_fixture(configured_agent):
    result = await configured_agent.invoke_capability("test_capability", {})
    assert result.success
```

### 6. Mock External Dependencies

```python
@pytest.mark.asyncio
async def test_with_mocked_external_service(test_supervisor, mock_external_api):
    """Test with mocked external dependencies."""
    mock_external_api.return_value = {"status": "success", "data": "test"}
    
    agent = await test_supervisor.create_supervised_agent("test", config)
    result = await agent.call_external_service()
    
    assert result["status"] == "success"
    mock_external_api.assert_called_once()
```

### 7. Performance Test Critical Paths

```python
@pytest.mark.performance
@pytest.mark.asyncio
async def test_message_routing_performance():
    """Ensure message routing meets performance requirements."""
    
    async def route_message():
        message = create_test_message()
        await message_router.route(message)
    
    tester = PerformanceTester()
    metrics = await tester.measure_operation("message_routing", route_message, iterations=100)
    
    # Performance requirements
    assert metrics.execution_time < 0.01  # < 10ms
    assert metrics.throughput_ops_per_sec > 1000  # > 1000 ops/sec
```

## Troubleshooting

### Common Issues

1. **Test Hangs**: Use TestSupervisor with proper timeouts
2. **Resource Leaks**: Ensure all agents are created through TestSupervisor
3. **Flaky Tests**: Use event-based coordination instead of time-based waits
4. **Coverage Gaps**: Use `--cov-report=term-missing` to identify uncovered lines

### Debug Mode

```bash
# Run with debug logging
poetry run pytest -v --log-cli-level=DEBUG --tb=short

# Run single test with full output
poetry run pytest tests/integration/test_specific.py::test_function -v -s
```

### Performance Issues

```bash
# Profile test execution
poetry run pytest --durations=10

# Memory profiling
poetry run pytest --memray

# Performance regression detection
poetry run python scripts/check_performance_regression.py \
  --current results.json \
  --baseline baseline.json \
  --tolerance 10
```

This comprehensive testing framework ensures OpenMAS 0.3.0 maintains high quality, performance, and reliability while supporting the framework's reasoning-agnostic architecture and multi-protocol communication capabilities.
