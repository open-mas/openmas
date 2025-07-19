# CLI Commands

## Overview

This directory contains documentation for the OpenMAS CLI commands, which allow developers to interact with OpenMAS from the command line. These commands provide functionality for initializing projects, validating configurations, running agents and systems, managing dependencies, and handling deployments.

## Available Commands

- [**init**](./init.md): Initialize new OpenMAS projects
- [**validate**](./validate.md): Validate OpenMAS configurations
- [**run**](./run.md): Run OpenMAS agents and systems
- [**deps**](./deps.md): Manage OpenMAS dependencies
- [**config**](./config.md): Manage OpenMAS configurations
- [**deploy**](./deploy.md): Handle OpenMAS deployments

## Command Structure

All OpenMAS CLI commands follow a consistent structure:

```
openmas <command> [subcommand] [options]
```

For example:

```bash
# Initialize a new project
openmas init --name my-project

# Validate a configuration file
openmas validate --file config.yaml

# Run an agent with a specific configuration
openmas run --config agent_config.yaml

# Install dependencies for a project
openmas deps install
```

## Global Options

These options are available for all OpenMAS CLI commands:

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help message |
| `--version`, `-v` | Show version information |
| `--config`, `-c` | Specify configuration file |
| `--verbose` | Enable verbose output |
| `--quiet` | Suppress output except for errors |
| `--log-level` | Set log level (debug, info, warning, error) |

## Related Documentation

- [CLI Installation](../installation/README.md)
- [CLI Configuration](../configuration/README.md)
- [Development Workflows](../development/README.md)
- [CLI Extension](../extension/README.md)
- [CLI Component Interoperability](../interoperability/README.md)
