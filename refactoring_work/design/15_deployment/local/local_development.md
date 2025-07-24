# Local Development Guide

## 1. Overview

This document provides comprehensive guidance for setting up and using the OpenMAS framework in a local development environment. Local development is the simplest way to get started with OpenMAS and is ideal for individual developers, testing, and smaller-scale multi-agent scenarios.

## 2. Prerequisites

- **Python 3.9+**
- **Virtual Environment** (recommended)
- **Git**

## 3. Installation

```bash
# 1. Clone the repository
git clone https://github.com/openmas-ai/openmas.git
cd openmas

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# 3. Install in editable mode with development dependencies
pip install -e ".[dev]"
```

## 4. Running OpenMAS Locally

There are two primary methods for running agents locally.

### Method 1: Single Process (Programmatic)

All agents run in the same Python process. This is the simplest method for debugging.

**Example Script (`run_system.py`):**
```python
import asyncio
from openmas.core import MultiAgentSystem
from openmas.config import load_config

async def main():
    # Load configuration from a YAML file
    config = load_config("config.yaml")

    # Create, initialize, and start the system
    system = MultiAgentSystem(config)
    await system.initialize()
    await system.start()

    print("System is running. Press Ctrl+C to shut down.")
    try:
        # Keep the system running indefinitely
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        print("Shutting down system...")
        await system.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
```

**Minimal `config.yaml` for the script above:**
```yaml
version: "0.3.0"
system:
  name: "programmatic_system"

agents:
  - id: "agent_1"
    name: "My First Agent"
    type: "basic"

communication:
  protocol: "mcp" # Use local in-memory transport
  transport: "local"
```

### Method 2: Multi-Process (CLI)

Each agent runs in its own OS process, providing better isolation. This is achieved using the `openmas run` command.

```bash
# In one terminal, start the first agent
openmas run --config agent1_config.yaml

# In a second terminal, start another agent
openmas run --config agent2_config.yaml
```

## 5. Local Development Configuration Examples

OpenMAS is configuration-driven. Below are commented examples for common scenarios.

### Example 1: Minimal Single Agent

This is the simplest possible configuration, useful for testing a single agent's logic.

```yaml
# A minimal configuration for a single agent
version: "0.3.0"

system:
  name: "single_agent_system"

agents:
  - id: "my_agent"
    name: "My Test Agent"
    type: "basic" # The type of reasoning engine to use

# Communication is optional for a single agent but good practice
communication:
  protocol: "mcp"
  transport: "local"
```

### Example 2: Two Agents with A2A Protocol

This example shows two agents configured to communicate over the A2A (Agent-to-Agent) protocol using an HTTP transport.

```yaml
version: "0.3.0"

system:
  name: "a2a_http_system"

agents:
  - id: "agent_one"
    name: "Agent One"
    type: "basic"
    # Agent-specific communication settings
    communication:
      host: "127.0.0.1"
      port: 8001 # Each agent needs a unique port for HTTP

  - id: "agent_two"
    name: "Agent Two"
    type: "basic"
    communication:
      host: "127.0.0.1"
      port: 8002

# Global communication settings
communication:
  protocol: "a2a"       # Use the A2A protocol
  transport: "http"      # Use HTTP for the transport layer
```

## 6. Key CLI Commands for Local Development

### `openmas run`

Starts an OpenMAS agent or system.

| Parameter | Short | Description |
|---|---|---|
| `--config` | `-c` | **(Required)** Path to the YAML configuration file. |
| `--agent-id`| `-a` | ID of a specific agent to run from the config file. If omitted, runs all agents. |
| `--log-level`| `-l` | Overrides the logging level (e.g., `DEBUG`, `INFO`). |

**Example:**
`openmas run -c my_config.yaml -a my_agent_id -l DEBUG`

### `openmas validate`

Validates a configuration file against the unified schema.

| Parameter | Short | Description |
|---|---|---|
| `--config` | `-c` | **(Required)** Path to the YAML configuration file to validate. |

**Example:**
`openmas validate --config my_config.yaml`

## 7. Debugging

- **Logging**: Configure logging levels and outputs in your YAML file under the `observability` key for detailed runtime information.
- **Interactive Debugging**: Use `pdb.set_trace()` in your Python code or your IDE's built-in debugger.

## 8. Related Documentation

- [Agent Supervisor](./agent_supervisor.md)
- [Multi-Agent Local Deployment](./multi_agent_local.md)
- [CLI Tools](../../13_cli_tools/README.md)
