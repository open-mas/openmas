# Test Fixtures

## Overview

This document describes the standard test fixtures available in the OpenMAS testing framework. Test fixtures provide reusable test setup and teardown functionality that follows OpenMAS's reasoning-agnostic design principles and multi-protocol support.

## Core Fixtures

### Agent Fixtures

Fixtures for creating and managing test agents:

```python
import pytest
from openmas.testing import AgentFixture
from openmas.config import Configuration

@pytest.fixture
async def test_agent():
    """Create a basic test agent."""
    config = Configuration.from_dict({
        "id": "test_agent",
        "name": "Test Agent",
        "type": "assistant",
        "capabilities": [
            {"id": "messaging", "type": "messaging"}
        ],
        "protocol": {
            "type": "mcp",
            "transport": "memory"
        }
    })

    agent = AgentFixture(config)
    await agent.initialize()

    yield agent

    await agent.shutdown()

@pytest.fixture
async def test_agent_pair():
    """Create a pair of test agents."""
    agent1_config = Configuration.from_dict({
        "id": "agent1",
        "name": "Agent 1",
        "type": "assistant",
        "capabilities": [
            {"id": "messaging", "type": "messaging"}
        ],
        "protocol": {
            "type": "mcp",
            "transport": "memory"
        }
    })

    agent2_config = Configuration.from_dict({
        "id": "agent2",
        "name": "Agent 2",
        "type": "user",
        "capabilities": [
            {"id": "messaging", "type": "messaging"}
        ],
        "protocol": {
            "type": "mcp",
            "transport": "memory"
        }
    })

    agent1 = AgentFixture(agent1_config)
    agent2 = AgentFixture(agent2_config)

    await agent1.initialize()
    await agent2.initialize()

    yield agent1, agent2

    await agent1.shutdown()
    await agent2.shutdown()
```

### Protocol Fixtures

Fixtures for protocol testing:

```python
import pytest
from openmas.testing import ProtocolFixture
from openmas.protocols import ProtocolFactory

@pytest.fixture
async def mcp_protocol():
    """Create an MCP protocol for testing."""
    config = {
        "type": "mcp",
        "transport": "memory",
        "settings": {
            "queue_size": 100
        }
    }

    protocol = ProtocolFactory.create("mcp", config)
    await protocol.initialize()

    yield protocol

    await protocol.shutdown()

@pytest.fixture
async def a2a_protocol():
    """Create an A2A protocol for testing."""
    config = {
        "type": "a2a",
        "transport": "memory",
        "settings": {
            "queue_size": 100
        }
    }

    protocol = ProtocolFactory.create("a2a", config)
    await protocol.initialize()

    yield protocol

    await protocol.shutdown()

@pytest.fixture
async def http_protocol():
    """Create an HTTP protocol for testing."""
    config = {
        "type": "http",
        "transport": "http",
        "settings": {
            "host": "localhost",
            "port": 0  # Use ephemeral port
        }
    }

    protocol = ProtocolFactory.create("http", config)
    await protocol.initialize()

    yield protocol

    await protocol.shutdown()
```

### Reasoning Fixtures

Fixtures for different reasoning approaches, respecting OpenMAS's reasoning agnosticism:

```python
import pytest
from openmas.testing import ReasoningFixture
from openmas.reasoning import ReasoningFactory

@pytest.fixture
async def mock_llm_reasoning():
    """Create a mock LLM reasoning component."""
    config = {
        "type": "llm",
        "model": "test-model",
        "settings": {
            "temperature": 0.7,
            "mock_mode": True,  # Use mock responses
            "mock_responses": [
                {"input": "Hello", "output": "Hi there!"},
                {"input": "Help", "output": "How can I assist you?"}
            ]
        }
    }

    reasoning = ReasoningFactory.create("llm", config)
    await reasoning.initialize()

    yield reasoning

    await reasoning.shutdown()

@pytest.fixture
async def rule_based_reasoning():
    """Create a rule-based reasoning component."""
    config = {
        "type": "rule_based",
        "settings": {
            "rules": [
                {"pattern": "Hello", "response": "Hi there!"},
                {"pattern": "Help", "response": "How can I assist you?"}
            ]
        }
    }

    reasoning = ReasoningFactory.create("rule_based", config)
    await reasoning.initialize()

    yield reasoning

    await reasoning.shutdown()

@pytest.fixture
async def bdi_reasoning():
    """Create a BDI reasoning component."""
    config = {
        "type": "bdi",
        "settings": {
            "beliefs": [
                {"name": "greeting", "value": "Hello"}
            ],
            "desires": [
                {"name": "be_helpful", "priority": 1}
            ],
            "intentions": [
                {"desire": "be_helpful", "action": "respond_greeting"}
            ]
        }
    }

    reasoning = ReasoningFactory.create("bdi", config)
    await reasoning.initialize()

    yield reasoning

    await reasoning.shutdown()
```

### Configuration Fixtures

Fixtures for configuration testing:

```python
import pytest
from openmas.config import Configuration
import tempfile
import os

@pytest.fixture
def test_config():
    """Create a test configuration object."""
    return Configuration.from_dict({
        "version": "0.3.0",
        "system": {
            "name": "test_system",
            "description": "Test system"
        },
        "agents": [
            {
                "id": "agent1",
                "name": "Agent 1",
                "type": "assistant",
                "capabilities": [
                    {"id": "messaging", "type": "messaging"}
                ]
            }
        ],
        "protocols": [
            {
                "type": "mcp",
                "transport": "memory"
            }
        ]
    })

@pytest.fixture
def test_config_file():
    """Create a temporary configuration file."""
    config = {
        "version": "0.3.0",
        "system": {
            "name": "test_system",
            "description": "Test system"
        },
        "agents": [
            {
                "id": "agent1",
                "name": "Agent 1",
                "type": "assistant",
                "capabilities": [
                    {"id": "messaging", "type": "messaging"}
                ]
            }
        ],
        "protocols": [
            {
                "type": "mcp",
                "transport": "memory"
            }
        ]
    }

    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp:
        temp_path = temp.name
        Configuration.to_yaml_file(config, temp_path)

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)
```

## System Fixtures

Fixtures for system-level testing:

```python
import pytest
from openmas.testing import SystemFixture
from openmas.core import MultiAgentSystem
from openmas.config import Configuration

@pytest.fixture
async def test_system():
    """Create a test multi-agent system."""
    config = Configuration.from_dict({
        "version": "0.3.0",
        "system": {
            "name": "test_system",
            "description": "Test system"
        },
        "agents": [
            {
                "id": "agent1",
                "name": "Agent 1",
                "type": "assistant",
                "capabilities": [
                    {"id": "messaging", "type": "messaging"}
                ]
            },
            {
                "id": "agent2",
                "name": "Agent 2",
                "type": "user",
                "capabilities": [
                    {"id": "messaging", "type": "messaging"}
                ]
            }
        ],
        "protocols": [
            {
                "type": "mcp",
                "transport": "memory"
            }
        ]
    })

    system = MultiAgentSystem(config)
    await system.initialize()

    yield system

    await system.shutdown()

@pytest.fixture
async def test_supervisor():
    """Create a test supervisor."""
    from openmas.testing import TestSupervisor

    supervisor = TestSupervisor()
    await supervisor.initialize()

    yield supervisor

    await supervisor.shutdown()
```

## Service Mocks

Fixtures for mocking external services:

```python
import pytest
from openmas.testing.mocks import MockService

@pytest.fixture
async def mock_database():
    """Create a mock database service."""
    service = MockService("database")

    # Configure mock responses
    service.add_response(
        method="query",
        args={"query": "SELECT * FROM users"},
        result=[{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}]
    )

    service.add_response(
        method="insert",
        args={"table": "users", "data": {"name": "User 3"}},
        result={"id": 3, "name": "User 3"}
    )

    await service.start()

    yield service

    await service.stop()

@pytest.fixture
async def mock_llm_service():
    """Create a mock LLM service."""
    service = MockService("llm")

    # Configure mock responses
    service.add_response(
        method="generate",
        args={"prompt": "Hello"},
        result={"text": "Hi there!", "tokens": 5}
    )

    service.add_response(
        method="generate",
        args={"prompt": "Help"},
        result={"text": "How can I assist you?", "tokens": 10}
    )

    await service.start()

    yield service

    await service.stop()
```

## Test Data

Fixtures for test data:

```python
import pytest
import json
import os

@pytest.fixture
def test_messages():
    """Provide test messages."""
    return [
        {
            "id": "msg1",
            "sender": "agent1",
            "receiver": "agent2",
            "content": "Hello, how are you?",
            "type": "text"
        },
        {
            "id": "msg2",
            "sender": "agent2",
            "receiver": "agent1",
            "content": "I'm fine, thank you!",
            "type": "text"
        },
        {
            "id": "msg3",
            "sender": "agent1",
            "receiver": "agent2",
            "content": "Can you help me with something?",
            "type": "text"
        }
    ]

@pytest.fixture
def test_knowledge():
    """Provide test knowledge data."""
    return {
        "concepts": [
            {
                "id": "concept1",
                "name": "Artificial Intelligence",
                "description": "The simulation of human intelligence in machines."
            },
            {
                "id": "concept2",
                "name": "Machine Learning",
                "description": "A subset of AI focused on learning from data."
            }
        ],
        "relationships": [
            {
                "source": "concept2",
                "target": "concept1",
                "type": "is_subset_of"
            }
        ]
    }
```

## Environment Fixtures

Fixtures for environment setup:

```python
import pytest
import os
import tempfile

@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def env_variables():
    """Set up environment variables for testing."""
    # Save original environment
    original_env = dict(os.environ)

    # Set test environment variables
    os.environ["OPENMAS_TEST_MODE"] = "true"
    os.environ["OPENMAS_LOG_LEVEL"] = "DEBUG"
    os.environ["OPENMAS_CONFIG_PATH"] = "/tmp/test-config.yaml"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
```

## Protocol-Specific Fixtures

Fixtures for specific protocols, supporting OpenMAS's multi-protocol design:

```python
import pytest
from openmas.testing import create_protocol_pair

@pytest.fixture
async def mcp_protocol_pair():
    """Create a pair of connected MCP protocols."""
    client, server = await create_protocol_pair("mcp", "memory")

    yield client, server

    await client.shutdown()
    await server.shutdown()

@pytest.fixture
async def a2a_protocol_pair():
    """Create a pair of connected A2A protocols."""
    client, server = await create_protocol_pair("a2a", "memory")

    yield client, server

    await client.shutdown()
    await server.shutdown()

@pytest.fixture
async def http_protocol_pair():
    """Create a pair of connected HTTP protocols."""
    client, server = await create_protocol_pair("http", "http")

    yield client, server

    await client.shutdown()
    await server.shutdown()
```

## Reasoning-Specific Fixtures

Fixtures for specific reasoning approaches, maintaining OpenMAS's reasoning agnosticism:

```python
import pytest
from openmas.testing import create_reasoning_component

@pytest.fixture
async def mock_reasoning():
    """Create a test reasoning component with mocked responses."""
    reasoning = await create_reasoning_component(
        reasoning_type="mock",
        responses={
            "Hello": "Hi there!",
            "Help": "How can I assist you?"
        }
    )

    yield reasoning

    await reasoning.shutdown()
```

## Best Practices

1. **Isolate Tests**: Each test should be independent and not rely on state from other tests
2. **Clean Up Resources**: Always clean up resources in fixture teardown
3. **Use Async Fixtures**: Use async fixtures for asynchronous resources
4. **Keep Fixtures Focused**: Each fixture should serve a single purpose
5. **Use Factory Functions**: Use factory functions for creating variations of fixtures
6. **Document Fixtures**: Document what each fixture provides and its usage
7. **Protocol Independence**: Fixtures should work with all supported protocols
8. **Reasoning Agnosticism**: Fixtures should respect OpenMAS's reasoning-agnostic design

## Related Documentation

- [Directory Structure](./directory_structure.md)
- [Test Supervisor](./test_supervisor.md)
- [Tox Configuration](./tox_configuration.md)
- [Unit Testing](../unit_testing/README.md)
- [Integration Testing](../integration_testing/README.md)
