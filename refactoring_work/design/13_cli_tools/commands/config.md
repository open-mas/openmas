# Config Command

## Overview

The `config` command provides utilities for managing OpenMAS configuration files. It allows users to create, edit, validate, and convert configuration files, with support for both YAML and JSON formats, and integration with the unified configuration schema.

## Usage

```bash
openmas config [subcommand] [options]
```

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `create` | Create a new configuration file |
| `get` | Get configuration values |
| `set` | Set configuration values |
| `edit` | Edit configuration in default editor |
| `validate` | Validate configuration files |
| `convert` | Convert between configuration formats |
| `merge` | Merge multiple configuration files |
| `schema` | View or export configuration schema |

## Options

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Path to configuration file |
| `--output`, `-o` | Output file path |
| `--format` | Output format (yaml, json) |
| `--template`, `-t` | Template to use for new configuration |
| `--schema`, `-s` | Schema to validate against |
| `--env`, `-e` | Environment for configuration (development, production, testing) |

## Examples

### Create a New Configuration

```bash
openmas config create --template agent --output config/agent_config.yaml
```

This creates a new agent configuration file using the agent template.

### Get Configuration Values

```bash
# Basic configuration access
openmas config get --file config/agent_config.yaml --path "name"

# Accessing nested properties with dot notation
openmas config get --file config/agent_config.yaml --path "multi_protocol_capabilities.core[0].name"

# Accessing protocol-specific configuration
openmas config get --file config/agent_config.yaml --path "communication.protocols.a2a.endpoint"

# Accessing reasoning engine configuration
openmas config get --file config/agent_config.yaml --path "reasoning.engine"
```

This retrieves the agent ID from the configuration file.

### Set Configuration Values

```bash
# Set basic agent properties
openmas config set --file config/agent_config.yaml --path "name" --value "coordination-agent"

# Configure protocol-specific settings (A2A)
openmas config set --file config/agent_config.yaml --path "communication.primary_protocol" --value "a2a"
openmas config set --file config/agent_config.yaml --path "communication.protocols.a2a.endpoint" --value "http://localhost:8080"
openmas config set --file config/agent_config.yaml --path "communication.protocols.a2a.mode" --value "server"

# Configure protocol-specific settings (MCP)
openmas config set --file config/agent_config.yaml --path "communication.protocols.mcp.endpoint" --value "http://localhost:8100"
openmas config set --file config/agent_config.yaml --path "communication.protocols.mcp.mode" --value "client"

# Set reasoning engine
openmas config set --file config/agent_config.yaml --path "reasoning.engine" --value "bdi"

# Configure reasoning components (BDI example)
openmas config set --file config/agent_config.yaml --path "reasoning.beliefs.workers[0].id" --value "worker1"
openmas config set --file config/agent_config.yaml --path "reasoning.desires[0]" --value "distribute_tasks_efficiently"
```

These examples demonstrate how to configure different aspects of an agent, including communication protocols and reasoning engines, aligned with OpenMAS's reasoning-agnostic architecture and multi-protocol design.

### Validate Configuration

```bash
openmas config validate --file config/agent_config.yaml
```

This validates the configuration file against the schema.

### Convert Configuration Format

```bash
openmas config convert --file config/agent_config.yaml --output config/agent_config.json --format json
```

This converts the configuration from YAML to JSON.

### Merge Configurations

```bash
openmas config merge --files config/base_config.yaml config/override_config.yaml --output config/merged_config.yaml
```

This merges multiple configuration files into one, with later files taking precedence.

### View Configuration Schema

```bash
openmas config schema --component agent
```

This displays the schema for agent configurations.

## Configuration Templates

The `config` command provides several built-in templates:

| Template | Description |
|----------|-------------|
| `agent` | Basic agent configuration |
| `multi-agent` | Multi-agent system configuration |
| `protocol` | Protocol adapter configuration |
| `reasoning` | Reasoning engine configuration |
| `deployment` | Deployment configuration |
| `complete` | Complete configuration with all components |

## Configuration Formats

The `config` command supports the following formats:

- **YAML**: Default format for configuration files
- **JSON**: Alternative format with standard JSON syntax
- **TOML**: Additional format for simpler configurations (optional)

## Environment Variables

Configuration files can reference environment variables using the syntax `${VARIABLE_NAME}`. The `config` command can resolve these references:

```bash
openmas config validate --file config/agent_config.yaml --resolve-env
```

## Configuration Hierarchy

OpenMAS uses a hierarchical configuration system:

1. **Default Configuration**: Built-in defaults
2. **Project Configuration**: Configuration files in the project
3. **Environment Configuration**: Environment-specific overrides
4. **Command-line Arguments**: Overrides from the command line

The `config` command can operate on different levels of this hierarchy.

## Related Commands

- [init](./init.md): Initialize a new OpenMAS project
- [validate](./validate.md): Validate OpenMAS configurations
- [run](./run.md): Run agents and systems with configuration

## Related Documentation

- [Configuration Schema](../../03_configuration/unified_configuration_schema.md)
- [Configuration Validation](../../03_configuration/configuration_validation.md)
- [Configuration Patterns](../../03_configuration/patterns/README.md)
