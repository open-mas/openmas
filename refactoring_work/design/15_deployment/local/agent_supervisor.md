# Agent Supervisor

## Overview

The Agent Supervisor is a local deployment tool that manages multiple OpenMAS agents running as separate processes. It provides monitoring, coordination, and lifecycle management for a multi-agent system running on a single machine.

## Key Features

- **Process Management**: Start, stop, and monitor agent processes
- **Configuration Management**: Distribute and validate agent configurations
- **Resource Management**: Monitor and limit resource usage
- **Observability**: Centralized logging and monitoring
- **Coordination**: Facilitate communication between agents
- **State Management**: Maintain system state across agent restarts

## Architecture

```
┌───────────────────────────────────────────────┐
│                Agent Supervisor               │
│                                               │
│  ┌─────────────┐  ┌─────────────┐   ┌──────┐  │
│  │ Process     │  │ Config      │   │ API  │  │
│  │ Manager     │  │ Manager     │   │ Server│  │
│  └─────────────┘  └─────────────┘   └──────┘  │
│         │                │              │     │
└─────────┼────────────────┼──────────────┼─────┘
          │                │              │
┌─────────▼────┐   ┌───────▼────┐  ┌─────▼─────┐
│ Agent Process│   │ Agent      │  │ External  │
│ 1            │   │ Process 2  │  │ Tools     │
└──────────────┘   └────────────┘  └───────────┘
```

## Usage

### Starting the Supervisor

```bash
# Start the agent supervisor with a system configuration
openmas supervisor start --config system_config.yaml
```

### Configuration

The supervisor uses a system configuration file that defines all agents:

```yaml
version: "0.3.0"
supervisor:
  name: "local_development_supervisor"
  host: "localhost"
  port: 8000
  log_level: "INFO"

  # Process management
  process_management:
    max_restarts: 3
    restart_delay: 5  # seconds
    graceful_shutdown_timeout: 10  # seconds

  # Resource limits
  resource_limits:
    max_memory_per_agent: "500MB"
    max_cpu_percent_per_agent: 50
    max_agents: 10

# System agents
agents:
  - id: "agent1"
    name: "Agent 1"
    config_path: "./configs/agent1.yaml"
    autostart: true

  - id: "agent2"
    name: "Agent 2"
    config_path: "./configs/agent2.yaml"
    autostart: true
```

### API

The supervisor provides a REST API for management:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents` | GET | List all agents |
| `/agents/{agent_id}` | GET | Get agent details |
| `/agents/{agent_id}/start` | POST | Start an agent |
| `/agents/{agent_id}/stop` | POST | Stop an agent |
| `/agents/{agent_id}/restart` | POST | Restart an agent |
| `/agents/{agent_id}/logs` | GET | Get agent logs |
| `/system/status` | GET | Get system status |

### CLI Interface

The supervisor can be controlled via CLI:

```bash
# List all managed agents
openmas supervisor agents list

# Start a specific agent
openmas supervisor agents start agent1

# Stop a specific agent
openmas supervisor agents stop agent1

# View agent logs
openmas supervisor agents logs agent1

# View system status
openmas supervisor status
```

## Testing Integration

The Agent Supervisor is particularly useful for testing scenarios:

1. **Integration Testing**: Run multiple agents for integration tests
2. **Performance Testing**: Monitor resource usage during testing
3. **Failure Testing**: Simulate agent failures and restarts
4. **Protocol Testing**: Test communication between agents

## Implementation

The Agent Supervisor is implemented using:

- **Process Management**: Python's `subprocess` module for agent process management
- **API Server**: FastAPI for the management API
- **Configuration Management**: OpenMAS configuration utilities
- **Observability**: OpenMAS observability framework

## Related Documentation

- [Local Development](./local_development.md)
- [Multi-Agent Local Deployment](./multi_agent_local.md)
- [Integration Testing](../../16_testing/integration_testing/multi_agent_testing.md)
- [Test Supervisor](../../16_testing/framework/test_supervisor.md)
