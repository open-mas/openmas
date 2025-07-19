# Run Command

## Overview

The `run` command starts and manages OpenMAS agents and systems. It supports running individual agents, multi-agent systems, and various deployment configurations while providing monitoring and control capabilities.

## Usage

```bash
openmas run [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--config`, `-c` | Path to configuration file (required) |
| `--agent`, `-a` | Agent ID to run (for multi-agent configurations) |
| `--all` | Run all agents in the configuration |
| `--mode`, `-m` | Run mode (development, production, testing) |
| `--port`, `-p` | Port for the agent or system API |
| `--host` | Host for the agent or system API |
| `--detach`, `-d` | Run in detached mode (background) |
| `--env`, `-e` | Environment variables (format: KEY=VALUE) |
| `--log-file` | Path to log file |
| `--reload` | Enable automatic reload on file changes |
| `--protocol` | Override the protocol to use (a2a, mcp, http, mqtt, grpc) |
| `--reasoning-engine` | Override the reasoning engine (rule, bdi, llm, hybrid, knowledge_graph) |
| `--llm-model` | LLM model to use (applicable with --reasoning-engine=llm) |
| `--reasoning-config` | Path to reasoning engine specific configuration |

## Run Modes

The `run` command supports several run modes:

| Mode | Description |
|------|-------------|
| `development` | Development mode with additional debugging capabilities |
| `production` | Production mode optimized for performance |
| `testing` | Testing mode for running test scenarios |

## Examples

### Run a Single Agent

```bash
openmas run --config config/agent_config.yaml
```

This runs a single agent using the specified configuration file.

### Run Multiple Agents

```bash
openmas run --config config/multi_agent_config.yaml --all
```

This runs all agents defined in the multi-agent configuration file.

### Run a Specific Agent from a Multi-Agent Configuration

```bash
openmas run --config config/multi_agent_config.yaml --agent agent1
```

This runs only the agent with ID "agent1" from the multi-agent configuration.

### Run in Development Mode with Automatic Reload

```bash
openmas run --config config/agent_config.yaml --mode development --reload
```

This runs the agent in development mode with automatic reloading when files change.

### Run in Background

```bash
openmas run --config config/agent_config.yaml --detach
```

This runs the agent in detached mode (background) and returns control to the terminal.

## Runtime Control

When running in interactive mode (not detached), the `run` command provides a command interface for controlling the running agent or system:

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `status` | Show agent/system status |
| `stop` | Stop the agent/system |
| `restart` | Restart the agent/system |
| `logs` | Show logs |
| `info` | Show detailed information |
| `send` | Send a message to an agent |
| `exit` | Exit the command interface |

## Logging

The `run` command provides configurable logging capabilities:

```bash
openmas run --config config/agent_config.yaml --log-file logs/agent.log
```

## Process Management

For detached processes, you can use the following commands to manage them:

```bash
# List running processes
openmas ps

# Stop a running process
openmas stop <process-id>

# View logs from a running process
openmas logs <process-id>
```

## Protocol-Specific Examples

OpenMAS supports multiple communication protocols. Here are examples of running agents with different protocols:

### A2A Protocol

```bash
# Run an agent with A2A protocol
openmas run --config config/agent_config.yaml --protocol a2a
```

### MCP Protocol

```bash
# Run an agent with MCP protocol
openmas run --config config/agent_config.yaml --protocol mcp
```

### Custom Protocol Configuration

```bash
# Run an agent with explicit protocol settings
openmas run --config config/agent_config.yaml --protocol http --env "HTTP_PORT=8080" "HTTP_HOST=0.0.0.0"
```

## Reasoning Engine Examples

OpenMAS's reasoning-agnostic architecture allows for various reasoning approaches:

### Rule-Based Reasoning

```bash
# Run an agent with rule-based reasoning
openmas run --config config/agent_config.yaml --reasoning-engine rule
```

### BDI Architecture

```bash
# Run an agent with BDI reasoning
openmas run --config config/agent_config.yaml --reasoning-engine bdi --reasoning-config config/bdi_config.yaml
```

### LLM-Based Reasoning

```bash
# Run an agent with LLM-based reasoning
openmas run --config config/agent_config.yaml --reasoning-engine llm --llm-model gpt-4
```

### Hybrid Reasoning

```bash
# Run an agent with hybrid reasoning (combining multiple approaches)
openmas run --config config/agent_config.yaml --reasoning-engine hybrid --reasoning-config config/hybrid_config.yaml
```

### Knowledge Graph Reasoning

```bash
# Run an agent with knowledge graph reasoning
openmas run --config config/agent_config.yaml --reasoning-engine knowledge_graph --reasoning-config config/kg_config.yaml
```

## Multi-Protocol System Examples

```bash
# Run a system with agents using different protocols
openmas run --config config/system_config.yaml --all
```

The `system_config.yaml` might contain:

```yaml
agents:
  agent1:
    config: config/agent1_config.yaml
    communication:
      primary_protocol: a2a
  agent2:
    config: config/agent2_config.yaml
    communication:
      primary_protocol: mcp
```

## Related Commands

- [init](./init.md): Initialize a new OpenMAS project
- [validate](./validate.md): Validate OpenMAS configurations
- [config](./config.md): Manage OpenMAS configurations
- [deploy](./deploy.md): Handle OpenMAS deployments

## Related Documentation

- [Agent Configuration](../../04_agents/configuration.md)
- [Deployment Configuration](../../15_deployment/README.md)
- [Runtime Architecture](../../01_architecture/runtime_architecture.md)
