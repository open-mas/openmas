# Local Deployment

## Overview

This directory contains documentation for deploying OpenMAS in local development environments. Local deployment provides a simple way to run and test OpenMAS agents on a single machine during development.

## Deployment Options

- **Single Process Mode**: Running multiple agents within a single process
- **Multi-Process Mode**: Running agents in separate processes
- **Agent Supervisor**: Local supervision of multiple agent processes
- **Local Development**: Development workflows and tools

## Documentation

- [Local Development](./local_development.md): Guide for setting up local development environment
- [Agent Supervisor](./agent_supervisor.md): Documentation for the agent supervisor
- [Multi-Agent Local](./multi_agent_local.md): Guide for running multiple agents locally
- [Development Workflows](./development_workflows.md): Common development workflows

## Related Documentation

- [Testing Framework](../../16_testing/framework/README.md)
- [CLI Tools](../../13_cli_tools/README.md)
  - [Deploy Command](../../13_cli_tools/commands/deploy.md) - Used for deploying agents locally
  - [Run Command](../../13_cli_tools/commands/run.md) - Used for running agents with various reasoning engines
  - [Config Command](../../13_cli_tools/commands/config.md) - Used for managing agent configurations
- [Configuration](../../03_configuration/README.md)
  - [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md)

## Multi-Protocol Support

Local deployments support all OpenMAS protocols:
- A2A Protocol: Run agents with Google's Agent-to-Agent protocol
- MCP Protocol: Deploy agents using the Model Context Protocol
- HTTP, MQTT, gRPC: Additional protocol options for local development

## Reasoning Engine Support

The local deployment environment supports OpenMAS's reasoning-agnostic architecture:
- Rule-based reasoning for simple agents
- BDI architecture for cognitive agents
- LLM-based reasoning for language model integration
- Hybrid reasoning approaches that combine multiple paradigms
- Knowledge graph reasoning for complex knowledge representation
