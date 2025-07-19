# Multi-Agent Local Deployment

## Overview

This document provides guidance for deploying and managing multiple OpenMAS agents on a local system. This approach is useful for development, testing, and small-scale production deployments where all agents run on a single machine.

## Deployment Patterns

OpenMAS supports several patterns for local multi-agent deployment:

### 1. Single Process / Multiple Agents

In this pattern, multiple agents run within a single process:

```
┌─────────────────────────────┐
│       Single Process        │
│                             │
│  ┌──────┐  ┌──────┐  ┌──────┐
│  │Agent1│  │Agent2│  │Agent3│
│  └──────┘  └──────┘  └──────┘
│                             │
│  ┌────────────────────────┐ │
│  │   Shared Resources     │ │
│  └────────────────────────┘ │
└─────────────────────────────┘
```

**Benefits:**
- Simplest deployment model
- Shared resources and memory
- Lower overhead

**Limitations:**
- Less isolation between agents
- Single point of failure
- Limited scalability

**Example Configuration:**

```yaml
version: "0.3.0"
system:
  name: "single_process_system"
  process_model: "single"

agents:
  - id: "assistant_agent"
    name: "Assistant Agent"
    type: "assistant"
    capabilities:
      - id: "messaging"
        type: "messaging"
    
  - id: "user_agent"
    name: "User Agent"
    type: "user"
    capabilities:
      - id: "messaging"
        type: "messaging"
      
  - id: "tool_agent"
    name: "Tool Agent"
    type: "tool"
    capabilities:
      - id: "tool_execution"
        type: "tool_execution"
```

### 2. Multiple Processes / Dedicated Agents

In this pattern, each agent runs in its own process:

```
┌─────────────────────────────┐
│        Single Machine       │
│                             │
│  ┌─────────┐  ┌─────────┐   │
│  │Process 1│  │Process 2│   │
│  │ ┌─────┐ │  │ ┌─────┐ │   │
│  │ │Agent│ │  │ │Agent│ │   │
│  │ └─────┘ │  │ └─────┘ │   │
│  └─────────┘  └─────────┘   │
│                             │
└─────────────────────────────┘
```

**Benefits:**
- Better isolation between agents
- Process-level fault tolerance
- Better resource control

**Limitations:**
- Higher overhead
- More complex setup
- Inter-process communication required

**Implementation:**

Each agent is started as a separate process:

```bash
# Start Agent 1
python -m openmas.cli run --config agent1_config.yaml

# Start Agent 2
python -m openmas.cli run --config agent2_config.yaml

# Start Agent 3
python -m openmas.cli run --config agent3_config.yaml
```

### 3. Supervised Multi-Agent System

In this pattern, a supervisor manages multiple agent processes:

```
┌─────────────────────────────────────────┐
│               Single Machine            │
│                                         │
│  ┌─────────────┐                        │
│  │ Supervisor  │                        │
│  └──────┬──────┘                        │
│         │                               │
│  ┌──────┼──────┬──────────┬──────────┐  │
│  │      │      │          │          │  │
│  │ ┌────▼───┐ ┌▼────────┐ ┌▼────────┐│  │
│  │ │Process1│ │Process 2│ │Process 3││  │
│  │ │┌─────┐ │ │┌─────┐  │ │┌─────┐  ││  │
│  │ ││Agent│ │ ││Agent│  │ ││Agent│  ││  │
│  │ │└─────┘ │ │└─────┘  │ │└─────┘  ││  │
│  │ └────────┘ └─────────┘ └─────────┘│  │
│  └───────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

**Benefits:**
- Centralized management
- Process monitoring and restart
- Resource control and distribution
- Simplified deployment

**Implementation:**

Use the Agent Supervisor to manage all agents:

```bash
# Start the agent supervisor with a system configuration
openmas supervisor start --config system_config.yaml
```

The system configuration defines all agents:

```yaml
version: "0.3.0"
supervisor:
  name: "multi_agent_supervisor"
  host: "localhost"
  port: 8000
  
agents:
  - id: "agent1"
    name: "Assistant Agent"
    config_path: "./configs/assistant_agent.yaml"
    autostart: true
    
  - id: "agent2"
    name: "User Agent"
    config_path: "./configs/user_agent.yaml"
    autostart: true
    
  - id: "agent3"
    name: "Tool Agent"
    config_path: "./configs/tool_agent.yaml"
    autostart: true
```

## Communication Between Agents

Local agents can communicate using various transport mechanisms:

### 1. In-Memory Transport (Single Process)

When agents run in the same process, they can use in-memory communication:

```yaml
communication:
  protocol: "mcp"  # or "a2a"
  transport: "memory"
  settings:
    queue_size: 100
```

### 2. Inter-Process Communication

When agents run in separate processes, they can use:

#### HTTP Transport

```yaml
communication:
  protocol: "mcp"  # or "a2a"
  transport: "http"
  settings:
    host: "localhost"
    port: 8080
```

#### WebSocket Transport

```yaml
communication:
  protocol: "mcp"  # or "a2a" 
  transport: "websocket"
  settings:
    host: "localhost"
    port: 8081
```

#### MQTT Transport

```yaml
communication:
  protocol: "mqtt"
  transport: "mqtt"
  settings:
    broker_host: "localhost"
    broker_port: 1883
    topic_prefix: "openmas/"
```

## Observability

For local multi-agent systems, configure observability:

```yaml
observability:
  logging:
    level: "INFO"
    outputs:
      - type: "console"
      - type: "file"
        path: "logs/agent.log"
        
  tracing:
    enabled: true
    exporter:
      type: "console"
      
  metrics:
    enabled: true
    exporters:
      - type: "prometheus"
        endpoint: "localhost:9090"
```

## Resource Management

Configure resource limits for agents:

```yaml
resources:
  memory_limit: "500MB"
  cpu_limit: "1.0"  # CPU cores
  storage:
    temp_dir: "/tmp/openmas"
    max_size: "1GB"
```

## Best Practices

1. **Start Simple**: Begin with a single-process deployment for development
2. **Isolate Complex Agents**: Move resource-intensive agents to separate processes
3. **Use Supervisor**: For complex setups, use the Agent Supervisor
4. **Monitor Resources**: Configure resource monitoring and limits
5. **Standardize Configurations**: Use environment variables for environment-specific settings
6. **Local Service Discovery**: Use the supervisor for service discovery between agents

## Related Documentation

- [Local Development](./local_development.md)
- [Agent Supervisor](./agent_supervisor.md)
- [Development Workflows](./development_workflows.md)
- [Integration Testing](../../16_testing/integration_testing/multi_agent_testing.md)
