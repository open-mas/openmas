# OpenMAS Quick Start Deployment Guides

This directory contains simplified guides for getting started with OpenMAS deployments quickly. These quick start guides provide the essential steps to deploy OpenMAS agents and systems in various environments.

## Available Quick Start Guides

- [**Two Agent Setup**](./two_agent_setup.md): A simple guide for deploying two communicating agents on a single machine
- [**Single Machine Cluster**](./single_machine_cluster.md): Guide for running a multi-agent cluster on a single machine

## Key Concepts

These quick start guides follow these principles:

1. **Simplicity First**: Focused on getting a working system quickly with minimal configuration
2. **Protocol Agnostic**: Examples for both A2A and MCP protocols
3. **Reasoning Agnostic**: Support for different reasoning approaches (LLM-based, rule-based, BDI)
4. **Local Development**: Optimized for local development environments

## Prerequisites

Before using these quick start guides, ensure you have:

1. OpenMAS CLI tools installed (see [CLI Installation Guide](../../13_cli_tools/installation/installation_guide.md))
2. Python 3.9 or higher
3. Docker (for containerized deployments)

## Related Documentation

- [Deployment Overview](../README.md)
- [Local Deployment](../local/README.md)
- [CLI Tools](../../13_cli_tools/README.md)
- [Deploy Command](../../13_cli_tools/commands/deploy.md)
