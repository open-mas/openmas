# Deploy Command

## Overview

The `deploy` command manages the deployment of OpenMAS agents and systems across various environments, including local development, containerized environments, and cloud platforms. It provides capabilities for packaging, deploying, monitoring, and scaling OpenMAS deployments while maintaining the reasoning-agnostic architecture.

## Usage

```bash
openmas deploy [subcommand] [options]
```

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `init` | Initialize deployment configuration |
| `build` | Build deployment artifacts |
| `up` | Deploy agents and systems |
| `down` | Terminate deployed agents and systems |
| `status` | Check deployment status |
| `logs` | View logs from deployed components |
| `scale` | Scale deployment components |
| `update` | Update deployment configuration |

## Options

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Path to deployment configuration file |
| `--environment`, `-e` | Deployment environment (local, docker, kubernetes, cloud) |
| `--target`, `-t` | Deployment target (specific agent, service, or component) |
| `--profile`, `-p` | Deployment profile (development, staging, production) |
| `--dry-run` | Simulate deployment without actually deploying |
| `--force` | Force deployment actions regardless of warnings |
| `--timeout` | Timeout for deployment operations |
| `--variables`, `-v` | Variables for deployment configuration (KEY=VALUE) |
| `--protocol-specific` | Deploy only components using a specific protocol (a2a, mcp, http, mqtt, grpc) |
| `--reasoning-specific` | Deploy only components using a specific reasoning engine (rule, bdi, llm, hybrid, knowledge_graph) |
| `--validate-before-deploy` | Validate configuration before deployment |
| `--body-brain-separation` | Enforce strict separation between communication infrastructure (body) and reasoning approaches (brain) |

## Deployment Environments

The `deploy` command supports several deployment environments:

| Environment | Description |
|-------------|-------------|
| `local` | Local development environment |
| `docker` | Docker containers on local or remote hosts |
| `kubernetes` | Kubernetes clusters |
| `aws` | Amazon Web Services cloud deployment |
| `azure` | Microsoft Azure cloud deployment |
| `gcp` | Google Cloud Platform deployment |

## Examples

### Initialize Deployment Configuration

```bash
openmas deploy init --environment docker
```

This initializes deployment configuration for Docker environments.

### Build Deployment Artifacts

```bash
openmas deploy build --file deployment/docker.yaml
```

This builds the deployment artifacts (e.g., Docker images) for the specified configuration.

### Deploy a System

```bash
openmas deploy up --file deployment/docker.yaml
```

This deploys the system according to the specified configuration.

### Check Deployment Status

```bash
openmas deploy status --file deployment/docker.yaml
```

This checks the status of the deployed system.

### View Deployment Logs

```bash
openmas deploy logs --file deployment/docker.yaml --target agent1
```

This views logs from a specific deployed component.

### Scale Deployment

```bash
openmas deploy scale --file deployment/docker.yaml --target agent1 --replicas 3
```

This scales a specific component to the specified number of replicas.

### Terminate Deployment

```bash
openmas deploy down --file deployment/docker.yaml
```

This terminates the deployed system.

## Deployment Configuration

A typical deployment configuration file includes:

```yaml
version: "1"

environment: docker

components:
  agent1:
    type: agent
    config: config/agent1_config.yaml
    replicas: 1
    resources:
      cpu: "0.5"
      memory: "512Mi"
  
  agent2:
    type: agent
    config: config/agent2_config.yaml
    replicas: 1
    resources:
      cpu: "0.5"
      memory: "512Mi"

networking:
  ports:
    - name: api
      port: 8080
      target: agent1
  
storage:
  volumes:
    - name: data
      size: "1Gi"
      path: /data

dependencies:
  - name: redis
    version: "6"
  - name: postgres
    version: "13"
```

## Deployment Profiles

Deployment profiles allow for environment-specific configurations:

```bash
openmas deploy up --file deployment/base.yaml --profile production
```

This applies the production profile to the base deployment configuration.

## Deployment Architecture

The deploy command maintains OpenMAS's reasoning-agnostic architecture:

- **Body-Brain Separation**: Deployment configurations maintain separation between communication infrastructure ("body") and reasoning approaches ("brain")
- **Protocol Independence**: Deployments can use any supported protocol (MCP, A2A, HTTP, MQTT, gRPC) 
- **Component Isolation**: Deployed components maintain proper isolation boundaries

## Protocol-Specific and Reasoning-Specific Deployments

### Protocol-Specific Deployment Examples

```bash
# Deploy only A2A protocol components
openmas deploy up --file deployment.yaml --protocol-specific a2a

# Deploy only MCP protocol components
openmas deploy up --file deployment.yaml --protocol-specific mcp

# Deploy only HTTP protocol components
openmas deploy up --file deployment.yaml --protocol-specific http
```

These commands deploy only the components that use the specified protocol, enabling focused development and testing of specific protocol implementations.

### Reasoning-Specific Deployment Examples

```bash
# Deploy only components with rule-based reasoning
openmas deploy up --file deployment.yaml --reasoning-specific rule

# Deploy only components with BDI reasoning
openmas deploy up --file deployment.yaml --reasoning-specific bdi

# Deploy only components with LLM-based reasoning
openmas deploy up --file deployment.yaml --reasoning-specific llm
```

These commands deploy only the components that use the specified reasoning engine, allowing for focused testing of specific reasoning approaches.

### Body-Brain Separation Enforcement

```bash
# Deploy with strict body-brain separation validation
openmas deploy up --file deployment.yaml --body-brain-separation
```

This command ensures that all deployed components maintain a strict separation between communication infrastructure ("body") and reasoning capabilities ("brain"), which is a core principle of OpenMAS's reasoning-agnostic architecture.

## Schema-Aligned Command Examples

### Multi-Protocol Agent Deployment

This example demonstrates how to deploy agents that use different protocols:

```yaml
# multi_protocol_deployment.yaml
version: "1"
environment: kubernetes

components:
  a2a_agent:
    type: agent
    config: config/a2a_agent_config.yaml
    replicas: 2
    resources:
      cpu: "0.5"
      memory: "512Mi"
    env:
      PROTOCOL: a2a
  
  mcp_agent:
    type: agent
    config: config/mcp_agent_config.yaml
    replicas: 1
    resources:
      cpu: "0.5"
      memory: "512Mi"
    env:
      PROTOCOL: mcp

  protocol_gateway:
    type: gateway
    config: config/gateway_config.yaml
    replicas: 1
    resources:
      cpu: "0.5"
      memory: "256Mi"
    ports:
      - name: http
        port: 8080
        protocol: TCP

networking:
  namespace: openmas-system
  service_account: openmas-agent
```

Command to deploy:

```bash
openmas deploy up --file multi_protocol_deployment.yaml
```

### Reasoning-Agnostic Deployment

This example demonstrates deploying agents with different reasoning engines:

```yaml
# reasoning_agnostic_deployment.yaml
version: "1"
environment: docker

components:
  rule_agent:
    type: agent
    config: config/rule_agent_config.yaml
    reasoning:
      engine: simple_rule
    env:
      OPENMAS_REASONING_ENGINE: rule
  
  bdi_agent:
    type: agent
    config: config/bdi_agent_config.yaml
    reasoning:
      engine: bdi
    env:
      OPENMAS_REASONING_ENGINE: bdi
  
  llm_agent:
    type: agent
    config: config/llm_agent_config.yaml
    reasoning:
      engine: llm
      model: gpt-4
    env:
      OPENMAS_REASONING_ENGINE: llm
      OPENMAS_LLM_MODEL: gpt-4
```

Command to deploy:

```bash
openmas deploy up --file reasoning_agnostic_deployment.yaml
```

### Complex Multi-Environment Deployment

This example demonstrates using deployment profiles for different environments:

```yaml
# base_deployment.yaml
version: "1"
environment: ${ENVIRONMENT:-local}

components:
  coordinator:
    type: agent
    config: config/coordinator_config.yaml
  
  worker:
    type: agent
    config: config/worker_config.yaml
    replicas: ${WORKER_REPLICAS:-1}

profiles:
  development:
    components:
      coordinator:
        env:
          LOG_LEVEL: debug
      worker:
        replicas: 1
        env:
          LOG_LEVEL: debug
  
  production:
    components:
      coordinator:
        resources:
          cpu: "1"
          memory: "1Gi"
      worker:
        replicas: 5
        resources:
          cpu: "0.5"
          memory: "512Mi"
```

Command to deploy with profile:

```bash
# For development
export ENVIRONMENT=docker
openmas deploy up --file base_deployment.yaml --profile development

# For production
export ENVIRONMENT=kubernetes
export WORKER_REPLICAS=10 
openmas deploy up --file base_deployment.yaml --profile production
```

## Related Commands

- [init](./init.md): Initialize a new OpenMAS project
- [config](./config.md): Manage OpenMAS configurations
- [run](./run.md): Run agents and systems locally
- [deps](./deps.md): Manage dependencies

## Related Documentation

- [Deployment Overview](../../15_deployment/README.md)
- [Local Deployment](../../15_deployment/local/README.md)
  - [Local Development](../../15_deployment/local/local_development.md)
  - [Multi-Agent Local](../../15_deployment/local/multi_agent_local.md)
- [Containerization](../../15_deployment/containerization/README.md)
  - [Docker Compose](../../15_deployment/containerization/docker_compose.md)
- [Kubernetes Deployment](../../15_deployment/kubernetes/README.md)
  - [K8s Manifests](../../15_deployment/kubernetes/k8s_manifests.md)
- [Cloud Deployment](../../15_deployment/cloud/README.md)
  - [AWS Deployment](../../15_deployment/cloud/aws.md)
  - [Azure Deployment](../../15_deployment/cloud/azure.md)
  - [GCP Deployment](../../15_deployment/cloud/gcp.md)
- [Deployment Configuration](../../15_deployment/configuration/README.md)
  - [Deployment Variables](../../15_deployment/configuration/deployment_variables.md)
- [Quick Start Guides](../../15_deployment/quick_start/README.md)
  - [Two Agent Setup](../../15_deployment/quick_start/two_agent_setup.md)
  - [Single Machine Cluster](../../15_deployment/quick_start/single_machine_cluster.md)
