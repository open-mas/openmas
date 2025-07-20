# Test Frameworks for OpenMAS

## Overview

This document describes the test frameworks used in OpenMAS for unit testing, integration testing, and system testing. These frameworks are selected to support OpenMAS's reasoning-agnostic architecture and multi-protocol support.

## Primary Test Frameworks

### pytest

[pytest](https://docs.pytest.org/) is the primary test framework used for OpenMAS testing:

```python
# Example test case using pytest
def test_agent_initialization():
    agent = Agent(id="test-agent", name="Test Agent")
    assert agent.id == "test-agent"
    assert agent.name == "Test Agent"
    assert agent.is_initialized() is False

    agent.initialize()
    assert agent.is_initialized() is True
```

Key pytest extensions used:

1. **pytest-asyncio**: For testing async functionality
2. **pytest-mock**: For mocking dependencies
3. **pytest-cov**: For code coverage reporting
4. **pytest-xdist**: For parallel test execution
5. **pytest-benchmark**: For performance benchmarking

### unittest

The standard library `unittest` framework is used for some legacy tests and specific test cases:

```python
import unittest

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.agent = Agent(id="test-agent", name="Test Agent")

    def test_initialization(self):
        self.assertEqual(self.agent.id, "test-agent")
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertFalse(self.agent.is_initialized())

        self.agent.initialize()
        self.assertTrue(self.agent.is_initialized())
```

### tox

[tox](https://tox.readthedocs.io/) is used for testing across multiple Python versions and environments:

```ini
# Example tox.ini configuration
[tox]
envlist = py39, py310, py311, py312

[testenv]
deps =
    pytest
    pytest-asyncio
    pytest-mock
    pytest-cov
commands =
    pytest --cov=openmas {posargs:tests/}

[testenv:lint]
deps =
    flake8
    black
commands =
    flake8 openmas tests
    black --check openmas tests
```

## Protocol-Specific Testing

Each supported protocol has specific testing utilities:

### A2A Protocol Testing

```python
from openmas.testing.protocols import A2ATestClient, A2ATestServer

async def test_a2a_capability():
    # Setup A2A test server with test capabilities
    server = A2ATestServer(capabilities=["test-capability"])
    await server.start()

    # Test client to invoke capabilities
    client = A2ATestClient()
    response = await client.invoke_capability(
        server_url=server.url,
        capability_id="test-capability",
        parameters={"param1": "value1"}
    )

    assert response.status_code == 200
    assert response.result["success"] is True

    await server.stop()
```

### MCP Protocol Testing

```python
from openmas.testing.protocols import MCPTestClient, MCPTestServer

async def test_mcp_function_call():
    # Setup MCP test server with test functions
    server = MCPTestServer(functions=["test_function"])
    await server.start()

    # Test client to invoke functions
    client = MCPTestClient()
    response = await client.invoke_function(
        server_url=server.url,
        function_name="test_function",
        parameters={"param1": "value1"}
    )

    assert response.status_code == 200
    assert response.result["success"] is True

    await server.stop()
```

### HTTP Protocol Testing

```python
from openmas.testing.protocols import HTTPTestClient, HTTPTestServer

async def test_http_endpoint():
    # Setup HTTP test server with test endpoints
    server = HTTPTestServer(endpoints=["/api/test"])
    await server.start()

    # Test client to call endpoints
    client = HTTPTestClient()
    response = await client.get(
        url=f"{server.url}/api/test",
        params={"param1": "value1"}
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    await server.stop()
```

### MQTT Protocol Testing

```python
from openmas.testing.protocols import MQTTTestClient, MQTTTestBroker

async def test_mqtt_messaging():
    # Setup MQTT test broker
    broker = MQTTTestBroker()
    await broker.start()

    # Test clients for publishing and subscribing
    publisher = MQTTTestClient()
    subscriber = MQTTTestClient()

    # Subscribe to test topic
    messages = []
    await subscriber.connect(broker.url)
    await subscriber.subscribe("test/topic", lambda msg: messages.append(msg))

    # Publish test message
    await publisher.connect(broker.url)
    await publisher.publish("test/topic", {"data": "test-data"})

    # Wait for message delivery
    await asyncio.sleep(0.1)

    assert len(messages) == 1
    assert messages[0]["data"] == "test-data"

    await publisher.disconnect()
    await subscriber.disconnect()
    await broker.stop()
```

### gRPC Protocol Testing

```python
from openmas.testing.protocols import GRPCTestClient, GRPCTestServer

async def test_grpc_service():
    # Setup gRPC test server with test service
    server = GRPCTestServer(services=["TestService"])
    await server.start()

    # Test client to call service methods
    client = GRPCTestClient()
    response = await client.call(
        server_url=server.url,
        service="TestService",
        method="TestMethod",
        request={"param1": "value1"}
    )

    assert response.success is True
    assert response.data["result"] == "expected-result"

    await server.stop()
```

## Reasoning Engine Testing

Each reasoning engine type has specialized testing utilities:

### Rule-Based Reasoning Testing

```python
from openmas.testing.reasoning import RuleEngineTestHarness

def test_rule_execution():
    # Setup rule engine test harness
    harness = RuleEngineTestHarness()

    # Define test rules
    harness.add_rule(
        name="test-rule",
        condition="x > 10",
        action="result = x * 2"
    )

    # Execute rules with test data
    result = harness.execute({"x": 15})

    assert result["result"] == 30
```

### BDI Reasoning Testing

```python
from openmas.testing.reasoning import BDITestHarness

def test_bdi_reasoning():
    # Setup BDI test harness
    harness = BDITestHarness()

    # Add test beliefs, desires, and intentions
    harness.add_belief("location", "home")
    harness.add_desire("reach_destination", {"destination": "work"})
    harness.add_plan(
        name="travel_plan",
        trigger="reach_destination",
        context="location != destination",
        body=["set_location(destination)"]
    )

    # Execute BDI reasoning cycle
    harness.execute_cycle()

    assert harness.get_belief("location") == "work"
```

### LLM-Based Reasoning Testing

```python
from openmas.testing.reasoning import LLMTestHarness

async def test_llm_reasoning():
    # Setup LLM test harness with mock responses
    harness = LLMTestHarness()
    harness.mock_completion(
        prompt="Solve the math problem: 5 + 7",
        response="The answer is 12."
    )

    # Execute LLM reasoning
    result = await harness.reason(
        task="Solve the math problem: 5 + 7"
    )

    assert "12" in result
```

### Knowledge Graph Reasoning Testing

```python
from openmas.testing.reasoning import KGTestHarness

def test_knowledge_graph_reasoning():
    # Setup knowledge graph test harness
    harness = KGTestHarness()

    # Add test nodes and relationships
    harness.add_node("Alice", type="Person")
    harness.add_node("Bob", type="Person")
    harness.add_relationship("Alice", "knows", "Bob")

    # Execute test query
    result = harness.query(
        "MATCH (a:Person)-[r:knows]->(b:Person) RETURN a.name, b.name"
    )

    assert len(result) == 1
    assert result[0]["a.name"] == "Alice"
    assert result[0]["b.name"] == "Bob"
```

## Integration Test Framework

OpenMAS uses a specialized multi-agent test framework for integration testing:

```python
from openmas.testing.integration import MultiAgentTestHarness

async def test_agent_interaction():
    # Setup multi-agent test harness
    harness = MultiAgentTestHarness()

    # Configure test agents
    harness.add_agent(
        id="agent1",
        capabilities=["request-data"],
        protocol="http"
    )
    harness.add_agent(
        id="agent2",
        capabilities=["provide-data"],
        protocol="http"
    )

    # Start test environment
    await harness.start()

    # Execute test scenario
    result = await harness.execute_scenario([
        {"agent": "agent1", "action": "invoke_capability", "args": {
            "target": "agent2",
            "capability": "provide-data",
            "parameters": {"query": "test-query"}
        }}
    ])

    # Verify results
    assert result["status"] == "success"
    assert "data" in result["response"]

    # Stop test environment
    await harness.stop()
```

## Property-Based Testing

OpenMAS uses property-based testing with Hypothesis:

```python
from hypothesis import given, strategies as st

@given(
    agent_id=st.text(min_size=1, max_size=50),
    capabilities=st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10)
)
def test_agent_properties(agent_id, capabilities):
    # Test agent creation with various inputs
    agent = Agent(id=agent_id, capabilities=capabilities)

    # Properties that should hold
    assert agent.id == agent_id
    assert len(agent.capabilities) == len(capabilities)
    assert agent.is_initialized() is False

    # Initialization should work for all valid inputs
    agent.initialize()
    assert agent.is_initialized() is True
```

## Test Fixtures

Common test fixtures used across OpenMAS tests:

```python
import pytest

@pytest.fixture
def config_file(tmp_path):
    """Create a temporary configuration file for testing."""
    config = {
        "version": "0.3.0",
        "agent": {
            "id": "test-agent",
            "name": "Test Agent",
            "capabilities": [
                {"id": "test-capability", "name": "Test Capability"}
            ]
        },
        "protocols": {
            "http": {"enabled": True, "port": 8080}
        }
    }
    config_path = tmp_path / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    return config_path

@pytest.fixture
async def agent_server():
    """Start a test agent server for integration tests."""
    server = TestAgentServer()
    await server.start()
    yield server
    await server.stop()
```

## Test Data Management

OpenMAS tests use these strategies for test data management:

1. **Fixture Files**: Standard test data files in `tests/fixtures/`
2. **Generators**: Dynamic test data generators for specialized scenarios
3. **Test Data API**: Internal API for accessing consistent test data
4. **Mock Data Services**: Mock external services for integration testing

## Test Configuration

Test configuration is managed via:

1. **pytest.ini**: Basic pytest configuration
2. **tox.ini**: Environment configuration
3. **conftest.py**: Fixtures and test setup
4. **environment variables**: Dynamic test configuration

## Related Documentation

- [Mock Services](./mock_services.md)
- [Test Framework](../framework/README.md)
- [Integration Testing](../integration_testing/README.md)
- [Tox Configuration](../framework/tox_configuration.md)
