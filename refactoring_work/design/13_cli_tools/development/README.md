# OpenMAS CLI Development Workflows

This directory provides documentation on using the OpenMAS CLI tools within development workflows.

## Overview

The OpenMAS CLI is designed to streamline development workflows by providing commands that align with the unified configuration schema and support OpenMAS's reasoning-agnostic architecture and multi-protocol capabilities.

## Contents

- [Developer Workflows](./developer_workflows.md) - Detailed documentation on common development workflows and how to leverage the CLI to improve productivity

## Key Features

- **Protocol-Agnostic Development**: Workflows for developing agents that can operate across multiple protocols (A2A, MCP, HTTP, MQTT, gRPC)
- **Reasoning-Agnostic Development**: Support for developing agents using different reasoning approaches (LLM-based, rule-based, BDI, hybrid)
- **Integrated Testing**: Command-line testing capabilities aligned with OpenMAS testing architecture
- **Rapid Prototyping**: Quick-start workflows for rapid agent and system development
- **End-to-End Workflows**: Development workflows that span from local prototyping to production deployment

## Relationship to Other Components

The development workflows integrate with multiple OpenMAS components:

- **Unified Configuration**: All workflows respect and leverage the [unified configuration schema](../../03_configuration/unified_configuration_schema.md)
- **Component Interoperability**: CLI commands respect and enforce component boundaries as defined in the architecture
- **Protocol Support**: Development workflows are designed to work with all supported protocols
- **Reasoning Agnosticism**: Development tools maintain separation between communication (body) and reasoning (brain)

## See Also

- [Command Reference](../commands/README.md)
- [Configuration Options](../configuration/cli_config.md)
- [Component Interoperability](../interoperability/component_integration.md)
