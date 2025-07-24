# CLI Command: `run`

## 1. Overview

The `openmas run` command is the primary tool for starting and managing OpenMAS agents and systems from the command line. It is designed to be flexible, supporting various configurations for local development, testing, and production scenarios.

## 2. Usage

```bash
openmas run --config <path_to_config.yaml> [OPTIONS]
```

## 3. Key Parameters in Detail

| Parameter | Short | Description |
|---|---|---|
| `--config` | `-c` | **(Required)** Specifies the path to the YAML configuration file that defines the agent(s) and system settings. |
| `--agent-id`| `-a` | Runs only the agent with the specified ID from a configuration file that contains multiple agents. If omitted, the command attempts to run the entire system or the single agent defined. |
| `--log-level`| `-l` | Overrides the logging level defined in the configuration file. Accepts standard levels like `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `--detach` | `-d` | Runs the agent or system in a detached (background) mode. The command will return control to the terminal, and the process will continue running in the background. |
| `--reload` | | Enables hot-reloading. The agent/system will automatically restart when source code files are changed. Ideal for development. |

## 4. Practical Scenarios & Examples

Below are examples demonstrating how to use the `run` command in common development scenarios.

### Scenario 1: Running a Single Agent for Development

This is the most common use case for developing and debugging a single agent's logic.

**Command:**
```bash
# Run the agent defined in 'my_agent_config.yaml'
# Enable hot-reloading for code changes and set log level to DEBUG
openmas run --config ./configs/my_agent_config.yaml --reload --log-level DEBUG
```

**Example `configs/my_agent_config.yaml`:**
```yaml
version: "0.3.0"
agents:
  - id: "my_dev_agent"
    name: "My Development Agent"
    type: "basic"
communication:
  protocol: "mcp"
  transport: "local"
observability:
  logging:
    level: "INFO" # Will be overridden by --log-level DEBUG
```

### Scenario 2: Running a Specific Agent from a Multi-Agent System

When you have a large system defined but only want to start one agent to test its interactions.

**Command:**
```bash
# From the multi-agent config, run only the agent with id 'agent_two'
openmas run --config ./configs/multi_agent_system.yaml --agent-id agent_two
```

**Example `configs/multi_agent_system.yaml`:**
```yaml
version: "0.3.0"
system:
  name: "my_multi_agent_system"
agents:
  - id: "agent_one"
    name: "Agent One"
    type: "basic"
    communication:
      port: 8001
  - id: "agent_two" # This agent will be started
    name: "Agent Two"
    type: "basic"
    communication:
      port: 8002
communication:
  protocol: "a2a"
  transport: "http"
```

### Scenario 3: Starting a System in the Background

Useful for running a system as a background service and capturing its logs.

**Command:**
```bash
# Run all agents from the config in detached mode
# Redirect all output to a log file
openmas run --config ./configs/multi_agent_system.yaml --detach --log-file system.log
```
This command will start the processes and immediately return. You can monitor the system's activity by tailing the `system.log` file.

## 5. Overriding Configuration at Runtime

The `run` command allows you to override certain configuration values directly from the command line, which is useful for quick experiments without modifying YAML files.

| Parameter | Description |
|---|---|
| `--port` | Overrides the communication port for an agent. |
| `--host` | Overrides the communication host. |
| `--protocol` | Overrides the communication protocol (e.g., `a2a`, `mcp`). |
| `--reasoning-engine` | Overrides the reasoning engine for an agent. |

**Example:**
```bash
# Run 'agent_one' but force it to use the MCP protocol on port 9000
openmas run -c ./configs/multi_agent_system.yaml -a agent_one --protocol mcp --port 9000
```

## 6. Runtime Control

When running in the foreground (without `--detach`), you can interact with the running system. After the system starts, press `Enter` to access an interactive command prompt for runtime control.

| Command | Description |
|---|---|
| `status` | Show the current status of all agents. |
| `stop` | Gracefully stop the agent or system. |
| `logs` | View the latest logs. |
| `exit` | Exit the interactive prompt and shut down the system. |

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
