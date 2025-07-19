# OpenMAS CLI Extension

This directory contains documentation on extending the OpenMAS Command Line Interface (CLI) tools.

## Overview

The OpenMAS CLI is designed to be extensible, allowing developers to add custom commands, integrate with additional protocols, and support various reasoning approaches. This extensibility aligns with OpenMAS's core architecture principles of reasoning agnosticism and multi-protocol support.

## Contents

- [Custom Commands](./custom_commands.md) - Guide to creating and integrating custom CLI commands

## Key Features

- **Custom Command Creation**: Framework for adding new commands to the CLI
- **Protocol Extensions**: Support for extending the CLI with commands for new protocols
- **Reasoning Extensions**: Framework for adding commands that support new reasoning approaches
- **Plugin Architecture**: Plugin system for third-party extensions to the CLI
- **Command Hooks**: Pre and post-execution hooks for customizing command behavior

## Relationship to Unified Configuration Schema

CLI extensions must align with the [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md), ensuring that custom commands maintain compatibility with the core configuration structure. This guarantees that extended functionality respects the single source of truth principle for configuration.

## Reasoning Agnosticism Support

CLI extensions maintain the separation between communication (body) and reasoning (brain) components, allowing for protocol-agnostic command development that can work with various reasoning approaches. This design aligns with OpenMAS's distinctive reasoning-agnostic architecture.

## See Also

- [Command Reference](../commands/README.md)
- [Configuration Options](../configuration/cli_config.md)
- [Component Interoperability](../interoperability/component_integration.md)
