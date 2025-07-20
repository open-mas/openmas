# Development Workflows

## Overview

This document outlines common development workflows for building applications with OpenMAS in a local environment. These workflows follow OpenMAS's reasoning-agnostic and multi-protocol design principles.

## Development Lifecycle

The typical OpenMAS development workflow follows these steps:

### 1. Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/openmas-ai/openmas.git
cd openmas

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### 2. Configuration Development

Start by defining your agent system's configuration:

1. Create a configuration directory structure:

```
my_project/
├── configs/
│   ├── system.yaml          # System-wide configuration
│   ├── agents/              # Agent-specific configurations
│   │   ├── agent1.yaml
│   │   └── agent2.yaml
│   ├── protocols/           # Protocol-specific configurations
│   │   ├── mcp_config.yaml
│   │   └── a2a_config.yaml
│   └── observability.yaml   # Observability configuration
└── data/                    # Application data
```

2. Define the system configuration (system.yaml):

```yaml
version: "0.3.0"
system:
  name: "my_agent_system"
  description: "My first OpenMAS agent system"

  # Reference to agent configurations
  agents:
    - file: "./agents/agent1.yaml"
    - file: "./agents/agent2.yaml"

  # Global protocol settings
  protocols:
    - file: "./protocols/mcp_config.yaml"
    - file: "./protocols/a2a_config.yaml"

  # Observability settings
  observability:
    file: "./observability.yaml"
```

3. Validate your configuration:

```bash
openmas validate --config ./configs/system.yaml
```

### 3. Implement Agent Capabilities

Depending on your reasoning approach (keeping with OpenMAS's reasoning agnosticism):

#### For Rule-Based Reasoning:

```python
from openmas.agents import Agent
from openmas.reasoning.rule_based import RuleBasedReasoning

class MyRuleBasedAgent(Agent):
    def __init__(self, config):
        super().__init__(config)
        self.reasoning = RuleBasedReasoning(config.reasoning)

    async def handle_message(self, message):
        # Process message using rule-based reasoning
        response = await self.reasoning.process(message)
        return response
```

#### For LLM-Based Reasoning:

```python
from openmas.agents import Agent
from openmas.reasoning.llm import LLMReasoning

class MyLLMAgent(Agent):
    def __init__(self, config):
        super().__init__(config)
        self.reasoning = LLMReasoning(config.reasoning)

    async def handle_message(self, message):
        # Process message using LLM reasoning
        response = await self.reasoning.process(message)
        return response
```

### 4. Test Locally

Run automated tests:

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run specific test
pytest tests/unit/test_my_component.py
```

### 5. Run the System Locally

Start the multi-agent system:

```bash
# Using the agent supervisor
openmas supervisor start --config ./configs/system.yaml

# Or start individual agents
openmas run --config ./configs/agents/agent1.yaml
openmas run --config ./configs/agents/agent2.yaml
```

### 6. Iterate and Debug

1. Monitor logs:

```bash
# View logs for a specific agent
openmas supervisor logs agent1

# View system logs
cat logs/system.log
```

2. Use the interactive debugging console:

```bash
openmas debug --agent agent1 --port 8888
```

3. Modify configuration and restart:

```bash
# Edit configurations
# Then restart the system or specific agents
openmas supervisor restart agent1
```

## Common Development Patterns

### Pattern 1: Protocol-Agnostic Development

Develop agents that work with multiple protocols:

```python
from openmas.agents import Agent
from openmas.protocols import ProtocolManager

class ProtocolAgnosticAgent(Agent):
    def __init__(self, config):
        super().__init__(config)
        self.protocol_manager = ProtocolManager(config.protocols)

    async def initialize(self):
        await super().initialize()
        # Register protocol handlers
        for protocol in self.protocol_manager.protocols:
            await protocol.register_handler(self.handle_message)

    async def handle_message(self, message, protocol=None):
        # Process message content regardless of protocol
        content = message.get_content()
        # Business logic
        response_content = self.process_content(content)
        # Return using the same protocol
        return protocol.create_response(message, response_content)
```

### Pattern 2: Multi-Agent Local Testing

Test interactions between multiple agents:

```python
import asyncio
from openmas.testing import AgentTestHarness

async def test_agent_conversation():
    # Create a test harness
    harness = AgentTestHarness()

    # Add agents to the harness
    agent1 = await harness.add_agent("./configs/agents/agent1.yaml")
    agent2 = await harness.add_agent("./configs/agents/agent2.yaml")

    # Start interaction
    response = await harness.send_message(
        from_agent=agent1,
        to_agent=agent2,
        content="Hello, how are you?"
    )

    # Verify response
    assert "I'm fine" in response.content

    # Cleanup
    await harness.shutdown()

# Run the test
asyncio.run(test_agent_conversation())
```

### Pattern 3: Component-Based Development

Develop reusable components:

```python
from openmas.components import Component
from openmas.dependency_injection import inject

@inject
class KnowledgeComponent(Component):
    def __init__(self, config, database=None):
        super().__init__(config)
        self.database = database

    async def initialize(self):
        await self.database.connect()

    async def query(self, query_string):
        return await self.database.execute(query_string)

# Usage in an agent
class KnowledgeAgent(Agent):
    @inject
    def __init__(self, config, knowledge=None):
        super().__init__(config)
        self.knowledge = knowledge

    async def handle_message(self, message):
        query = self.extract_query(message)
        result = await self.knowledge.query(query)
        return self.format_response(result)
```

## Development Tools

### OpenMAS CLI

The OpenMAS CLI offers development-specific commands:

```bash
# Generate a new agent from template
openmas generate agent --name MyNewAgent --type assistant

# Package your agent for distribution
openmas package --config ./configs/agents/agent1.yaml

# Profile an agent's performance
openmas profile --agent agent1 --scenario ./scenarios/benchmark.yaml
```

### Local Debugging Tools

```bash
# Start the debugging server
openmas debug-server start

# Connect to a running agent
openmas debug-client connect --agent agent1 --port 8888

# Inspect agent state
agent1.get_state()

# Send test message
agent1.send_test_message(to="agent2", content="Test message")
```

## Best Practices

1. **Configuration First**: Define configurations before implementing code
2. **Component Testing**: Test components in isolation first
3. **Protocol Independence**: Keep business logic independent of protocols
4. **Local Integration**: Test agent interactions locally before deployment
5. **Consistent Conventions**: Follow OpenMAS naming and code conventions
6. **Separation of Concerns**: Keep communication infrastructure (body) separate from reasoning (brain)
7. **Resource Management**: Be mindful of resource usage in local environment
8. **Version Control**: Use git branches for feature development
9. **Documentation**: Keep documentation in sync with code changes

## Related Documentation

- [Local Development](./local_development.md)
- [Agent Supervisor](./agent_supervisor.md)
- [Multi-Agent Local Deployment](./multi_agent_local.md)
- [Testing Framework](../../16_testing/framework/README.md)
- [CLI Tools](../../13_cli_tools/README.md)
