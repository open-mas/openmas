# OpenMAS Deployment Documentation

This directory contains comprehensive documentation for deploying OpenMAS agents and systems in various environments.

## Directory Structure

- **[local/](./local/)**: Documentation for local development and deployment
- **[containerization/](./containerization/)**: Documentation for Docker and container-based deployment
- **[kubernetes/](./kubernetes/)**: Documentation for Kubernetes deployment
- **[cloud/](./cloud/)**: Documentation for cloud-based deployment options
- **[configuration/](./configuration/)**: Deployment-specific configuration
- **[quick_start/](./quick_start/)**: Quick start deployment guides

## Key Concepts

OpenMAS deployment follows these key principles:

1. **Reasoning Agnosticism**: Deployment options maintain separation between communication infrastructure and reasoning approaches
2. **Multi-Protocol Support**: Deployment configurations accommodate various communication protocols (A2A, MCP, HTTP, MQTT, gRPC)
3. **Configuration-Driven**: Deployment is driven by the unified configuration schema
4. **Separation of Concerns**: Clear separation between deployment infrastructure and agent functionality

## Related Documentation

- [Architecture Overview](/01_architecture/architecture_overview.md)
- [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md)
- [Testing Documentation](/16_testing/)
- [CLI Tools](/13_cli_tools/)
  - [Deploy Command](/13_cli_tools/commands/deploy.md)
  - [Config Command](/13_cli_tools/commands/config.md)
  - [Run Command](/13_cli_tools/commands/run.md)
  - [CLI Installation](/13_cli_tools/installation/installation_guide.md)
