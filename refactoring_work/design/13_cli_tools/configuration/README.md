# OpenMAS CLI Configuration

This directory contains documentation on configuring the OpenMAS Command Line Interface (CLI) tools.

## Overview

The OpenMAS CLI can be configured to match your specific development and deployment needs. Configuration options allow you to customize default behaviors, set preferred protocols, define reasoning approaches, and integrate with your existing workflow.

## Contents

- [CLI Configuration](./cli_config.md) - Detailed documentation on available configuration options and how to customize them

## Key Features

- **Protocol Agnostic Configuration**: Configure the CLI to work with any supported protocol (A2A, MCP, HTTP, MQTT, gRPC)
- **Reasoning Agnostic Settings**: Configure default reasoning approaches for various agent types
- **Environment Integration**: Configure how the CLI interacts with your deployment environment
- **Project Configuration**: Set project-specific defaults that align with your development workflow
- **Profile Management**: Create and switch between multiple CLI configuration profiles

## Relationship to Unified Configuration Schema

All CLI configuration options align with the [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md), ensuring consistency between CLI operations and the core OpenMAS framework.

## See Also

- [Installation Guide](../installation/installation_guide.md)
- [Command Reference](../commands/README.md)
- [Developer Workflows](../development/developer_workflows.md)
