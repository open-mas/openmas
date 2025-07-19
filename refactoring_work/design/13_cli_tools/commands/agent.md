# Agent Command

## Overview

The `agent` command provides utilities for managing OpenMAS agents throughout their lifecycle. It allows users to list, create, configure, inspect, and manage relationships between agents, with full support for OpenMAS's reasoning-agnostic architecture.

## Usage

```bash
openmas agent [subcommand] [options]
```

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List all agents in the project |
| `add` | Add a new agent to the project |
| `info` | Show detailed information about an agent |
| `link` | Create a relationship between agents |
| `unlink` | Remove a relationship between agents |
| `remove` | Remove an agent from the project |
| `enable` | Enable an agent |
| `disable` | Disable an agent |

## Options

| Option | Description |
|--------|-------------|
| `--id`, `-i` | Agent ID |
| `--name`, `-n` | Human-readable agent name |
| `--reasoning`, `-r` | Reasoning approach (llm, rule_based, hybrid, bdi, symbolic) |
| `--protocols`, `-p` | Protocols to enable (comma-separated) |
| `--config`, `-c` | Path to agent configuration file |
| `--file`, `-f` | Path to file for output |

## Examples

### List Agents

```bash
openmas agent list
```

This lists all agents defined in the current project.

### Add a New Agent

```bash
openmas agent add customer-assistant --reasoning llm --protocols mcp,a2a
```

This adds a new agent with LLM-based reasoning and support for MCP and A2A protocols.

### Get Agent Details

```bash
openmas agent info customer-assistant
```

This shows detailed information about the specified agent, including capabilities, protocols, and relationships.

### Create Agent Relationships

```bash
openmas agent link customer-assistant knowledge-base --relationship uses --direction outgoing
```

This creates a relationship between two agents, specifying the relationship type and direction.

### Remove an Agent

```bash
openmas agent remove deprecated-agent
```

This removes an agent from the project.

## Agent Creation and the Reasoning-Agnostic Architecture

The `agent` command respects OpenMAS's reasoning-agnostic architecture by:

1. **Body-Brain Separation**: Clearly separates protocol configuration (communication "body") from reasoning configuration (thinking "brain")
2. **Protocol Independence**: Allows multiple protocols to be configured for the same agent
3. **Reasoning Flexibility**: Supports different reasoning approaches (LLM, rule-based, BDI, symbolic, hybrid)

For example:
```bash
# Create an agent with LLM reasoning
openmas agent add assistant1 --reasoning llm

# Create another agent with rule-based reasoning
openmas agent add assistant2 --reasoning rule_based

# Both can use the same protocols
openmas agent add --id assistant1 --protocols mcp,http
openmas agent add --id assistant2 --protocols mcp,http
```

## Integration with Unified Configuration Schema

The `agent` command operates directly on the unified configuration schema. For example, running:

```bash
openmas agent add customer-assistant --reasoning llm --protocols mcp,a2a
```

Modifies the schema as follows:

```yaml
agents:
  customer-assistant:
    class: "openmas.agents.LLMAgent"
    type: "llm"
    # Agent reasoning configuration
    reasoning:
      type: "llm"
      config: 
        # LLM-specific configuration
    # Protocol configurations
    protocols:
      - type: "mcp-sse"
        enabled: true
        options:
          # MCP-specific options
      - type: "a2a-http"
        enabled: true
        options:
          # A2A-specific options
```

## Related Commands

- [init](./init.md): Initialize a new OpenMAS project
- [run](./run.md): Run agents
- [config](./config.md): Configure agent settings
- [protocol](./protocol.md): Manage agent protocol interfaces
- [deploy](./deploy.md): Deploy agents to various environments

## Related Documentation

- [Agent Architecture](../../04_agents/README.md)
- [Reasoning Approaches](../../08_reasoning/README.md)
- [Protocol Configuration](../../02_protocols/README.md)
- [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md)
