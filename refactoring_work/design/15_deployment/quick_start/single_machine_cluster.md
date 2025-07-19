# Single Machine Cluster: Quick Start Guide

This guide provides a quick start approach to deploying a multi-agent OpenMAS cluster on a single machine. This setup demonstrates how to coordinate multiple agents with different roles in a local environment while maintaining OpenMAS's reasoning-agnostic architecture.

## Overview

In this guide, you'll set up a local cluster with:

1. Multiple agents with different reasoning capabilities
2. Coordinated communication using both A2A and MCP protocols
3. Local orchestration using the OpenMAS CLI tools

## Prerequisites

- OpenMAS CLI tools installed (see [Installation Guide](../../13_cli_tools/installation/installation_guide.md))
- Python 3.9 or higher
- Docker installed (optional, for containerized deployment)

## Step 1: Initialize a New OpenMAS Project

```bash
# Create a new project directory
mkdir openmas-local-cluster
cd openmas-local-cluster

# Initialize a new OpenMAS project
openmas init --name local-cluster --template multi-agent
```

This generates a multi-agent project structure with predefined agent templates.

## Step 2: Configure the Cluster

The `--template multi-agent` option creates a default cluster with several agent types:

- **Coordinator**: Central agent that manages task distribution
- **Worker**: Agents that process tasks
- **Observer**: Agent that monitors system operations
- **Interface**: Agent that provides external API access

Review the generated configuration files:

```bash
ls -la config/
```

You should see configuration files for each agent type.

## Step 3: Customize Agent Capabilities

Edit the configuration files to customize agent capabilities according to your needs. Here's an example for the coordinator agent:

**config/coordinator_config.yaml**:
```yaml
name: coordinator
version: "1.0"
agent_type: coordinator
description: "Central coordinator for the agent cluster"

multi_protocol_capabilities:
  core:
    - name: assign_task
      description: "Assigns tasks to worker agents"
      parameters:
        task_id: string
        task_data: object
        worker_id: string
    - name: monitor_progress
      description: "Monitors task progress"
      parameters:
        task_id: string
  protocol_mapping:
    a2a:
      assign_task:
        function_name: create_task
        parameter_mapping:
          task_id: id
          task_data: data
          worker_id: target
      monitor_progress:
        function_name: get_task_status
        parameter_mapping:
          task_id: id
    mcp:
      assign_task:
        function_name: dispatch_task
        parameter_mapping:
          task_id: task_id
          task_data: payload
          worker_id: recipient

communication:
  primary_protocol: a2a
  protocols:
    a2a:
      mode: server
      endpoint: http://localhost:8000
      authenticator:
        type: basic
        api_key: ${OPENMAS_COORDINATOR_KEY}
    mcp:
      mode: client
      endpoint: http://localhost:8100
      authenticator:
        type: bearer
        token: ${OPENMAS_MCP_TOKEN}

reasoning:
  engine: bdi
  beliefs:
    workers:
      - id: "worker1"
        capabilities: ["text_processing"]
      - id: "worker2"
        capabilities: ["image_processing"]
  desires:
    - maintain_worker_availability
    - distribute_tasks_efficiently
  intentions:
    - monitor_worker_status
    - assign_tasks_by_capability
  plans:
    monitor_worker_status:
      capability: internal.periodic
      parameters:
        interval_seconds: 30
        action: check_workers
    assign_tasks_by_capability:
      capability: internal.event_handler
      parameters:
        event: new_task
        action: route_task
```

## Step 4: Create a Deployment Configuration

Create a deployment configuration file that defines how the agents should be deployed and how they interact:

**deployment.yaml**:
```yaml
version: "1"
environment: local

components:
  coordinator:
    type: agent
    config: config/coordinator_config.yaml
    resources:
      cpu: "0.5"
      memory: "256Mi"
    ports:
      - 8000:8000
  
  worker1:
    type: agent
    config: config/worker1_config.yaml
    resources:
      cpu: "0.5"
      memory: "256Mi"
    depends_on:
      - coordinator
  
  worker2:
    type: agent
    config: config/worker2_config.yaml
    resources:
      cpu: "0.5"
      memory: "256Mi"
    depends_on:
      - coordinator
  
  observer:
    type: agent
    config: config/observer_config.yaml
    resources:
      cpu: "0.2"
      memory: "128Mi"
    depends_on:
      - coordinator
      - worker1
      - worker2
  
  interface:
    type: agent
    config: config/interface_config.yaml
    resources:
      cpu: "0.3"
      memory: "192Mi"
    ports:
      - 8080:8080
    depends_on:
      - coordinator

environment_variables:
  OPENMAS_COORDINATOR_KEY: "${OPENMAS_COORDINATOR_KEY:-local_dev_key}"
  OPENMAS_MCP_TOKEN: "${OPENMAS_MCP_TOKEN:-local_dev_token}"
  OPENMAS_LOG_LEVEL: "info"
```

## Step 5: Deploy the Cluster

Deploy the cluster using the OpenMAS CLI:

```bash
# Export required environment variables
export OPENMAS_COORDINATOR_KEY=your_secure_key
export OPENMAS_MCP_TOKEN=your_secure_token

# Deploy the cluster
openmas deploy up --file deployment.yaml
```

This deploys all the agents in the correct order based on dependencies.

## Step 6: Interact with the Cluster

The interface agent provides an API to interact with the cluster. You can use it to submit tasks:

```bash
# Submit a task via curl
curl -X POST http://localhost:8080/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${OPENMAS_COORDINATOR_KEY}" \
  -d '{"type": "text_processing", "data": {"text": "Process this text"}}'
```

## Step 7: Monitor the Cluster

Monitor the cluster activity:

```bash
# View logs from all components
openmas deploy logs --file deployment.yaml

# View logs from a specific agent
openmas deploy logs --file deployment.yaml --target coordinator
```

## Step 8: Scale the Cluster

You can scale specific components as needed:

```bash
# Scale up worker1 to handle more load
openmas deploy scale --file deployment.yaml --target worker1 --replicas 3
```

## Extending This Example

This single-machine cluster can be extended to:

1. Use different reasoning engines (LLM-based, rule-based, hybrid) for different agents
2. Add more specialized worker agents with different capabilities
3. Implement more complex coordination patterns
4. Deploy to containerized environments using Docker

## Related Documentation

- [Local Deployment](../local/README.md)
- [Containerization](../containerization/README.md)
- [Agent Configuration](../../03_configuration/schema/agents.md)
- [Deploy Command](../../13_cli_tools/commands/deploy.md)
