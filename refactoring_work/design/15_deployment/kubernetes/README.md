# Kubernetes Deployment

This directory contains documentation on deploying OpenMAS agents and systems on Kubernetes clusters.

## Overview

Kubernetes provides a robust platform for deploying OpenMAS agents and systems at scale while maintaining the framework's reasoning-agnostic architecture and multi-protocol capabilities. This approach allows for advanced orchestration, resilience, and operational management of complex multi-agent systems.

## Contents

- [Kubernetes Manifests](./k8s_manifests.md) - Reference manifests for Kubernetes deployment
- [Multi-Agent Orchestration](./multi_agent_orchestration.md) - Guide for orchestrating multiple agents in Kubernetes

## Key Features

- **Protocol-Agnostic Deployment**: Deploy agents that can communicate using various protocols (A2A, MCP, HTTP, MQTT, gRPC)
- **Reasoning-Agnostic Architecture**: Maintain separation between communication infrastructure ("body") and reasoning engines ("brain") in Kubernetes deployments
- **Scalable Deployments**: Horizontal and vertical scaling of agent deployments
- **Self-Healing**: Automatic recovery from failures
- **Resource Management**: Fine-grained control over CPU, memory, and storage allocation
- **Service Discovery**: Automatic service discovery for agent communication
- **Configuration Management**: ConfigMaps and Secrets for configuration
- **Observability**: Integrated monitoring, logging, and tracing
- **Multi-Environment Support**: Consistent deployment across development, staging, and production

## Kubernetes Deployment Architecture

Kubernetes deployments of OpenMAS maintain the framework's distinctive reasoning-agnostic architecture through proper separation of components:

1. **Communication Layer ("Body")**: 
   - Deployed as Kubernetes Deployments/StatefulSets
   - Exposed through Services and Ingress resources
   - Configured via ConfigMaps and Secrets

2. **Reasoning Engines ("Brain")**:
   - Configurable to use multiple reasoning approaches:
     - LLM services (fully managed APIs or self-hosted models)
     - Rule-based engines (deployed alongside communication layer)
     - BDI architecture (belief-desire-intention model)
     - Hybrid approaches (combinations of different reasoning engines)
   - Maintained as separate deployments or sidecar containers

3. **Shared Resources**:
   - Persistent storage for state and knowledge (PersistentVolumes)
   - Messaging infrastructure for coordination (separate deployments)
   - Observability components (Prometheus, Grafana, Jaeger)

## Common Deployment Patterns

### Pattern 1: Agent-per-Pod

Each agent runs in its own pod, providing:
- Clear isolation between agents
- Independent scaling of individual agents
- Simplified resource allocation
- Straightforward lifecycle management

### Pattern 2: Sidecar-Based Deployment

Agent components deployed with sidecars:
- Communication layer in main container
- Reasoning engine in sidecar
- Shared logger/monitoring in additional sidecar
- Common configuration through volume mounts

### Pattern 3: Operator-Managed Deployment

Using a custom Kubernetes operator:
- Define agents as custom resources
- Automated deployment and scaling
- Lifecycle management
- Configuration validation and defaults

## See Also

- [Deployment Configuration](../configuration/README.md)
- [Cloud Deployment](../cloud/README.md)
- [Deploy Command](../../13_cli_tools/commands/deploy.md)
