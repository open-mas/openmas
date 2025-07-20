# Agent Extensions

## Overview

Agent Extensions provide a mechanism to enhance agent capabilities and behaviors beyond the core functionality of OpenMAS agents. They allow developers to add custom behaviors, protocol-specific features, and additional capabilities while maintaining OpenMAS's reasoning agnosticism.

## Base Class

Agent Extensions must inherit from the `AgentExtension` base class:

```python
from openmas.extensions import AgentExtension

class MyAgentExtension(AgentExtension):
    """A custom agent extension."""
```

## Required Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `enhance_agent(agent)` | Primary method to enhance an agent with additional capabilities | `agent`: The agent instance to enhance | None |

## Optional Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `validate_config()` | Validate the extension configuration | None | None, raises exception if invalid |
| `initialize()` | Initialize the extension | None | None |
| `on_agent_startup(agent)` | Called when the agent starts | `agent`: The agent instance | None |
| `on_agent_shutdown(agent)` | Called when the agent shuts down | `agent`: The agent instance | None |
| `pre_message_processing(agent, message)` | Called before a message is processed | `agent`: The agent instance<br>`message`: The incoming message | Modified message or original |
| `post_message_processing(agent, message, response)` | Called after a message is processed | `agent`: The agent instance<br>`message`: The processed message<br>`response`: The response | Modified response or original |

## Configuration Schema

Agent Extensions are configured in the unified configuration schema under the `extensions` section with `type: "agent"`:

```yaml
extensions:
  my_agent_extension:
    type: "agent"
    name: "my_agent_extension"
    enabled: true
    options:
      # Extension-specific options
      feature_flags:
        enable_logging: true
        custom_behavior: true
      priority: 10
      # Additional configuration specific to this extension
```

### Options Schema

The `options` block for Agent Extensions supports the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `feature_flags` | object | No | Feature flags to enable/disable specific functionality |
| `priority` | integer | No | Priority level for extension execution order (higher executes first) |
| `hooks` | array | No | List of agent lifecycle events to hook into |
| `protocol_specific` | object | No | Protocol-specific configuration keyed by protocol name |

For the complete schema definition, refer to the [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md#agent-extension-options).

## Interaction Model

Agent Extensions interact with the OpenMAS Agent Framework through the following mechanisms:

1. **Registration**: The extension is registered with the extension registry
2. **Discovery**: The agent discovers and loads the extension during initialization
3. **Enhancement**: The extension's `enhance_agent` method is called to augment the agent
4. **Lifecycle Hooks**: The extension can hook into agent lifecycle events
5. **Message Processing Hooks**: The extension can intercept and modify messages

The Agent Framework maintains control over the execution flow, calling extensions at appropriate points based on their priority.

## Code Example

Here's a minimal example of an Agent Extension that adds logging capabilities:

```python
from openmas.extensions import AgentExtension
import logging

class LoggingAgentExtension(AgentExtension):
    """Extension that adds enhanced logging to agents."""

    extension_type = "agent"
    extension_name = "logging_extension"

    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.logger = logging.getLogger("agent.extension.logging")
        self.log_level = config.get("options", {}).get("log_level", "INFO")
        self.log_format = config.get("options", {}).get("log_format",
                                                     "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    def validate_config(self):
        """Validate the extension configuration."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            raise ValueError(f"Invalid log_level: {self.log_level}. Must be one of {valid_levels}")

    def enhance_agent(self, agent):
        """Enhance agent with logging capabilities."""
        # Set up handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(self.log_format)
        handler.setFormatter(formatter)

        # Get agent logger and configure it
        agent_logger = logging.getLogger(f"agent.{agent.agent_id}")
        agent_logger.setLevel(getattr(logging, self.log_level))
        agent_logger.addHandler(handler)

        # Add logger to agent
        agent.logger = agent_logger
        agent.log = agent_logger.info  # Shorthand for common logging

        self.logger.info(f"Enhanced agent {agent.agent_id} with logging capabilities")

    def on_agent_startup(self, agent):
        """Log when agent starts up."""
        if hasattr(agent, "logger"):
            agent.logger.info(f"Agent {agent.agent_id} starting up")

    def on_agent_shutdown(self, agent):
        """Log when agent shuts down."""
        if hasattr(agent, "logger"):
            agent.logger.info(f"Agent {agent.agent_id} shutting down")

    def pre_message_processing(self, agent, message):
        """Log incoming messages."""
        if hasattr(agent, "logger"):
            agent.logger.debug(f"Processing message: {message.id}")
        return message

    def post_message_processing(self, agent, message, response):
        """Log outgoing responses."""
        if hasattr(agent, "logger"):
            agent.logger.debug(f"Sending response for message: {message.id}")
        return response
```

### Configuration Example

```yaml
extensions:
  logging_extension:
    type: "agent"
    name: "logging_extension"
    enabled: true
    options:
      log_level: "DEBUG"
      log_format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Best Practices

1. **Respect Reasoning Agnosticism**: Agent Extensions should not assume any specific reasoning approach
2. **Minimal Impact**: Extensions should have minimal impact on agent performance
3. **Graceful Degradation**: Extensions should degrade gracefully if dependencies are missing
4. **Protocol Independence**: Extensions should work with any protocol unless specifically designed for one
5. **Clear Error Handling**: Provide clear error messages for configuration issues

## Related Documentation

- [Extension System Design](../design/design_extension_system.md)
- [Agent Framework Design](../../06_agent_framework/design_agent_framework.md)
- [Extension Development Guide](../development/guide.md)
