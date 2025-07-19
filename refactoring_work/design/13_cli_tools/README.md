# OpenMAS CLI Tools

## Overview

This directory contains documentation about OpenMAS Command Line Interface (CLI) tools. These tools are designed to enhance the developer experience when working with OpenMAS components by providing streamlined command-line utilities for common tasks.

## Key Capabilities

The CLI Tools provide these core capabilities:

1. **Command Management**
   - Agent initialization and running
   - Configuration validation
   - Project scaffolding
   - Deployment utilities
   - Dependency management
   - Multi-protocol support (A2A, MCP, HTTP, MQTT, gRPC)
   - Reasoning engine integration (rule-based, BDI, LLM, hybrid, knowledge graph)

2. **Configuration**
   - Configuration generation
   - Environment-specific settings
   - Validation against unified schema
   - Multi-protocol capability mapping
   - Reasoning-agnostic configuration
   - Body-brain separation validation

3. **Development Workflows**
   - Local development support
   - Testing helpers
   - Debugging utilities
   - Protocol-specific workflows
   - Reasoning engine development

4. **Extension**
   - Custom command creation
   - Plugin integration
   - Framework extension points
   - Protocol adapter development
   - Reasoning engine integration

## Directory Structure

- **[commands/](./commands/)**: Command reference documentation
- **[installation/](./installation/)**: CLI installation guides
- **[configuration/](./configuration/)**: CLI configuration documentation
- **[development/](./development/)**: Development workflows
- **[extension/](./extension/)**: CLI extension mechanisms
- **[interoperability/](./interoperability/)**: Component integration

## Integration with Other Components

The CLI Tools integrate with other OpenMAS components while preserving the reasoning-agnostic architecture and multi-protocol capabilities:

- **Agent Framework**: Agent lifecycle management with body-brain separation in `/04_agents/`
- **Configuration**: Schema validation and generation for multi-protocol capability mapping in `/03_configuration/`
- **Protocol Layer**: Protocol-specific commands for all supported protocols (A2A, MCP, HTTP, MQTT, gRPC) in `/02_protocols/`
- **Deployment**: Deployment workflows that maintain reasoning-agnostic principles in `/15_deployment/`
  - Local, containerized, and cloud deployment options
  - Protocol-specific deployment configurations
  - Reasoning engine-specific deployment settings
- **Testing**: Test execution and reporting for multi-protocol and reasoning-agnostic testing in `/16_testing/`
- **Observability**: Logging and monitoring that maintains separation between communication monitoring and reasoning monitoring in `/12_observability/`
- **KR&R Module**: Integration with various reasoning approaches (rule-based, BDI, LLM, hybrid) in `/09_knowledge_representation/`

## Related Documentation

- [Architecture Overview](/01_architecture/architecture_overview.md)
- [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md)
- [Deployment Documentation](/15_deployment/)
  - [Local Deployment](/15_deployment/local/README.md)
  - [Containerization](/15_deployment/containerization/README.md)
  - [Kubernetes Deployment](/15_deployment/kubernetes/README.md)
  - [Cloud Deployment](/15_deployment/cloud/README.md)
  - [Quick Start Guides](/15_deployment/quick_start/README.md)
- [Testing Documentation](/16_testing/)
- [Security Documentation](/17_security/)
