# Local Development

## Overview

This document provides guidance for setting up and using the OpenMAS framework in a local development environment. Local development is the simplest way to get started with OpenMAS and is ideal for individual developers, testing, and smaller scale multi-agent scenarios.

## Prerequisites

To develop with OpenMAS locally, you'll need:

1. **Python 3.9+**: OpenMAS requires Python 3.9 or newer
2. **Virtual Environment**: Using a virtual environment is strongly recommended
3. **Git**: For version control and accessing the repository
4. **Development Tools**: Code editor or IDE with Python support

## Installation

### Setting Up a Development Environment

```bash
# Clone the repository
git clone https://github.com/openmas-ai/openmas.git
cd openmas

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

The `-e` flag installs OpenMAS in development mode, allowing you to modify the code without reinstalling.

## Local Deployment Patterns

OpenMAS supports several local deployment patterns:

### Single Process Deployment

In single process deployment, all agents run within the same Python process:

```python
from openmas.core import MultiAgentSystem
from openmas.config import load_config

# Load configuration
config = load_config("config.yaml")

# Create a multi-agent system
system = MultiAgentSystem(config)

# Initialize and start the system
async def main():
    await system.initialize()
    await system.start()
    
    # Run your application logic
    # ...
    
    # Shutdown when done
    await system.shutdown()

# Run the main function
import asyncio
asyncio.run(main())
```

This pattern is simplest for development and testing but has limitations for scaling and isolation.

### Multi-Process Deployment

For better isolation, agents can run in separate processes:

```bash
# Start the first agent
python -m openmas.cli run --config agent1_config.yaml

# In another terminal, start the second agent
python -m openmas.cli run --config agent2_config.yaml
```

This pattern provides better isolation and can take advantage of multiple CPU cores.

## Development Workflow

### 1. Configuration-First Development

OpenMAS follows a configuration-first approach:

1. Define your agent and system configuration in YAML
2. Validate the configuration against the schema
3. Run the agents using the configuration

Example configuration:

```yaml
version: "0.3.0"
system:
  name: "local_development_system"
  description: "Local development multi-agent system"

agents:
  - id: "assistant_agent"
    name: "Assistant Agent"
    type: "assistant"
    capabilities:
      - id: "messaging"
        type: "messaging"
      - id: "knowledge_retrieval"
        type: "knowledge_retrieval"
    
  - id: "user_agent"
    name: "User Agent"
    type: "user"
    capabilities:
      - id: "messaging"
        type: "messaging"

communication:
  protocol: "mcp"
  transport: "local"
```

### 2. Iterative Development Cycle

1. Modify configuration or code
2. Run tests to verify changes
3. Start agents locally to test interactions
4. Monitor agent behavior through logs
5. Debug issues using built-in tools
6. Repeat

### 3. Using the CLI Tools

The OpenMAS CLI provides helpful commands for local development:

```bash
# Initialize a new project
openmas init my_project

# Validate configuration
openmas validate --config my_config.yaml

# Run an agent
openmas run --config my_config.yaml

# Check dependencies
openmas deps check
```

## Debugging

### Logging

Configure logging for better visibility:

```yaml
observability:
  logging:
    level: "DEBUG"
    format: "{timestamp} [{level}] {name}: {message}"
    outputs:
      - type: "console"
      - type: "file"
        path: "logs/openmas.log"
```

### Interactive Debugging

Use Python's debugging tools:

```python
import pdb

# Set a breakpoint
pdb.set_trace()
```

Or use your IDE's debugging capabilities.

## Related Documentation

- [Agent Supervisor](./agent_supervisor.md)
- [Multi-Agent Local Deployment](./multi_agent_local.md)
- [Development Workflows](./development_workflows.md)
- [CLI Tools](../../13_cli_tools/README.md)
- [Testing Framework](../../16_testing/framework/README.md)
