# Test Supervisor

## Overview

The Test Supervisor is a specialized framework component that coordinates and manages multi-agent testing scenarios in OpenMAS. It provides a controlled environment for testing interactions between multiple agents while maintaining OpenMAS's reasoning-agnostic design and multi-protocol support.

## Key Features

- **Agent Lifecycle Management**: Start, stop, and monitor multiple agent processes
- **Message Interception**: Capture and inspect messages between agents
- **State Observation**: Monitor agent state changes
- **Test Scenario Coordination**: Coordinate multi-step test scenarios
- **Deterministic Testing**: Ensure reproducible test results
- **Multi-Protocol Support**: Test across all supported protocols (MCP, A2A, HTTP, MQTT, gRPC)
- **Reasoning-Agnostic Testing**: Test with different reasoning approaches

## Architecture

```
┌───────────────────────────────────────────────┐
│                Test Supervisor                │
│                                               │
│  ┌─────────────┐  ┌─────────────┐   ┌──────┐  │
│  │ Agent       │  │ Message     │   │ State│  │
│  │ Manager     │  │ Interceptor │   │ Store│  │
│  └─────────────┘  └─────────────┘   └──────┘  │
│         │                │              │     │
└─────────┼────────────────┼──────────────┼─────┘
          │                │              │
┌─────────▼────┐   ┌───────▼────┐  ┌─────▼─────┐
│ Test Agent 1 │   │ Test Agent │  │ Test      │
│              │   │ 2          │  │ Assertions│
└──────────────┘   └────────────┘  └───────────┘
```

## Usage

### Basic Setup

```python
import pytest
from openmas.testing import TestSupervisor
from openmas.agents import Agent
from openmas.config import Configuration

@pytest.fixture
async def supervisor():
    """Create and initialize a test supervisor."""
    supervisor = TestSupervisor()
    await supervisor.initialize()

    yield supervisor

    await supervisor.shutdown()

async def test_agent_communication(supervisor):
    """Test communication between two agents."""
    # Create test configurations
    agent1_config = Configuration.from_dict({
        "id": "agent1",
        "name": "Agent 1",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {"type": "mcp", "transport": "memory"}
    })

    agent2_config = Configuration.from_dict({
        "id": "agent2",
        "name": "Agent 2",
        "type": "user",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {"type": "mcp", "transport": "memory"}
    })

    # Add agents to supervisor
    agent1 = await supervisor.add_agent(agent1_config)
    agent2 = await supervisor.add_agent(agent2_config)

    # Test messaging
    message = {
        "content": "Hello, Agent 2!",
        "type": "text"
    }

    response = await supervisor.send_message(
        from_agent=agent1,
        to_agent=agent2,
        message=message
    )

    # Assert on response
    assert response is not None
    assert "Hello" in response["content"]
```

### Advanced Features

#### Message Interception

```python
# Enable message interception
supervisor.intercept_messages(True)

# Send a message
await supervisor.send_message(agent1, agent2, message)

# Get intercepted messages
messages = supervisor.get_intercepted_messages()

# Assert on specific message properties
assert len(messages) == 1
assert messages[0].sender_id == agent1.id
assert messages[0].receiver_id == agent2.id
assert messages[0].content == "Hello, Agent 2!"
```

#### State Observation

```python
# Enable state tracking
supervisor.track_state(True)

# Perform actions that change agent state
await agent1.process_message(message)

# Get state changes
state_changes = supervisor.get_state_changes(agent1.id)

# Assert on state changes
assert len(state_changes) > 0
assert state_changes[-1].current_state == "RESPONDING"
```

#### Controlled Environment

```python
# Set environment variables for the test
supervisor.set_environment({
    "TEST_MODE": "true",
    "OPENMAS_LOG_LEVEL": "DEBUG"
})

# Set controlled time (for deterministic testing)
supervisor.set_time("2025-01-01T12:00:00Z")

# Advance time during test
supervisor.advance_time(seconds=30)
```

## Testing Different Protocols

The supervisor supports testing with different protocols:

```python
# Configure MCP protocol
mcp_config = {
    "protocol": {
        "type": "mcp",
        "transport": "memory"
    }
}

# Configure A2A protocol
a2a_config = {
    "protocol": {
        "type": "a2a",
        "transport": "memory"
    }
}

# Configure HTTP protocol
http_config = {
    "protocol": {
        "type": "http",
        "transport": "http",
        "settings": {
            "host": "localhost",
            "port": 8080
        }
    }
}

# Test with different protocols
for protocol_config in [mcp_config, a2a_config, http_config]:
    agent_config = Configuration.from_dict({
        "id": f"agent_{protocol_config['protocol']['type']}",
        "name": f"Agent {protocol_config['protocol']['type']}",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        **protocol_config
    })

    agent = await supervisor.add_agent(agent_config)
    # Run protocol-specific tests
```

## Testing Different Reasoning Approaches

The supervisor supports testing with different reasoning approaches, in line with OpenMAS's reasoning-agnostic design:

```python
# Configure LLM-based reasoning
llm_config = {
    "reasoning": {
        "type": "llm",
        "model": "test-model",
        "settings": {
            "temperature": 0.7
        }
    }
}

# Configure rule-based reasoning
rule_config = {
    "reasoning": {
        "type": "rule_based",
        "rules_path": "/path/to/test/rules.yaml"
    }
}

# Configure BDI reasoning
bdi_config = {
    "reasoning": {
        "type": "bdi",
        "beliefs_path": "/path/to/test/beliefs.yaml",
        "desires_path": "/path/to/test/desires.yaml",
        "intentions_path": "/path/to/test/intentions.yaml"
    }
}

# Test with different reasoning approaches
for reasoning_config in [llm_config, rule_config, bdi_config]:
    agent_config = Configuration.from_dict({
        "id": f"agent_{reasoning_config['reasoning']['type']}",
        "name": f"Agent {reasoning_config['reasoning']['type']}",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {"type": "mcp", "transport": "memory"},
        **reasoning_config
    })

    agent = await supervisor.add_agent(agent_config)
    # Run reasoning-specific tests
```

## Testing Scenarios

The supervisor supports complex multi-step test scenarios:

```python
# Define a test scenario
scenario = [
    {
        "action": "send_message",
        "from": "agent1",
        "to": "agent2",
        "message": {"content": "Hello, how are you?"},
        "expected_response": {"content_contains": "I'm fine"}
    },
    {
        "action": "send_message",
        "from": "agent2",
        "to": "agent1",
        "message": {"content": "Can you help me with something?"},
        "expected_response": {"content_contains": "assist"}
    },
    {
        "action": "verify_state",
        "agent": "agent1",
        "expected_state": "READY"
    }
]

# Run the scenario
await supervisor.run_scenario(scenario)
```

## Implementation Details

The Test Supervisor implements these components:

### Agent Manager

Manages test agent instances:

```python
class AgentManager:
    """Manages test agent instances."""

    def __init__(self):
        self.agents = {}

    async def add_agent(self, config):
        """Add a new agent for testing."""
        agent = Agent(config)
        await agent.initialize()
        self.agents[agent.id] = agent
        return agent

    async def remove_agent(self, agent_id):
        """Remove a test agent."""
        if agent_id in self.agents:
            await self.agents[agent_id].shutdown()
            del self.agents[agent_id]
```

### Message Interceptor

Intercepts messages between agents:

```python
class MessageInterceptor:
    """Intercepts messages between agents."""

    def __init__(self):
        self.intercepted_messages = []
        self.enabled = False

    def enable(self, enabled=True):
        """Enable or disable message interception."""
        self.enabled = enabled

    def intercept(self, message):
        """Intercept a message."""
        if self.enabled:
            self.intercepted_messages.append(message)

    def get_messages(self):
        """Get all intercepted messages."""
        return self.intercepted_messages

    def clear(self):
        """Clear intercepted messages."""
        self.intercepted_messages = []
```

### State Store

Tracks agent state changes:

```python
class StateStore:
    """Tracks agent state changes."""

    def __init__(self):
        self.state_changes = {}
        self.enabled = False

    def enable(self, enabled=True):
        """Enable or disable state tracking."""
        self.enabled = enabled

    def track_state_change(self, agent_id, previous_state, current_state):
        """Track a state change."""
        if self.enabled:
            if agent_id not in self.state_changes:
                self.state_changes[agent_id] = []

            self.state_changes[agent_id].append({
                "timestamp": time.time(),
                "previous_state": previous_state,
                "current_state": current_state
            })

    def get_state_changes(self, agent_id):
        """Get state changes for an agent."""
        return self.state_changes.get(agent_id, [])

    def clear(self):
        """Clear state changes."""
        self.state_changes = {}
```

## Related Documentation

- [Directory Structure](./directory_structure.md)
- [Fixtures](./fixtures.md)
- [Integration Testing](../integration_testing/README.md)
- [Agent Supervisor](../../15_deployment/local/agent_supervisor.md)
