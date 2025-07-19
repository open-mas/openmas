# CLI Configuration Reference

This document provides a comprehensive reference for configuring the OpenMAS CLI tools to match your specific project needs.

## Configuration File

The OpenMAS CLI uses a YAML-based configuration file located at:

- **Global config**: `~/.openmas/config.yaml`
- **Project config**: `.openmas/config.yaml` (within a project directory)

Project-specific configurations override global settings.

## Creating or Updating Configuration

You can create or update your configuration using:

```bash
openmas config init  # Create initial configuration
openmas config set category.setting value  # Update specific setting
```

## Configuration Structure

The configuration file structure aligns with the OpenMAS [unified configuration schema](../../03_configuration/unified_configuration_schema.md):

```yaml
cli:
  default_protocol: "a2a"  # Default protocol to use
  default_reasoning: "llm"  # Default reasoning approach

protocols:
  a2a:
    default_endpoint: "http://localhost:8000"
  mcp:
    default_endpoint: "http://localhost:8080"
  http:
    timeout: 30
  grpc:
    max_message_size: 4194304

authentication:
  api_keys:
    openai: "${OPENAI_API_KEY}"
    anthropic: "${ANTHROPIC_API_KEY}"

development:
  default_project_path: "~/projects/openmas"
  templates_path: "~/.openmas/templates"
  enable_auto_validation: true

deployment:
  environments:
    dev:
      url: "http://localhost:8000"
    staging:
      url: "https://staging-api.example.com"
    production:
      url: "https://api.example.com"
  default_environment: "dev"

logging:
  level: "info"  # debug, info, warning, error
  format: "text"  # text, json
  output: "console"  # console, file
  file_path: "~/.openmas/logs/cli.log"
```

## Using Configuration Values

### Access Through Commands

Many commands automatically use configuration values:

```bash
# Uses default_protocol from config
openmas run agent my_agent

# Override with flag
openmas run agent my_agent --protocol mcp
```

### Environment Variable Expansion

Configuration values can reference environment variables:

```yaml
authentication:
  api_keys:
    openai: "${OPENAI_API_KEY}"
```

## Protocol-Specific Configuration

Each protocol has its own configuration section:

### A2A Protocol

```yaml
protocols:
  a2a:
    default_endpoint: "http://localhost:8000"
    timeout: 30
    retry_attempts: 3
    auth_method: "bearer"
```

### MCP Protocol

```yaml
protocols:
  mcp:
    default_endpoint: "http://localhost:8080"
    default_server_mode: "client"
    timeout: 60
```

## Reasoning-Specific Configuration

Configure different reasoning approaches:

```yaml
reasoning:
  llm:
    default_model: "gpt-4"
    temperature: 0.7
    max_tokens: 1024
  rule_based:
    rules_path: "./rules"
  bdi:
    plans_path: "./plans"
    beliefs_path: "./beliefs"
```

## Multi-Profile Configuration

You can create multiple profiles for different workflows:

```yaml
profiles:
  default:
    cli:
      default_protocol: "a2a"
  development:
    cli:
      default_protocol: "http"
      verbose: true
  production:
    cli:
      default_protocol: "grpc"
      verbose: false
```

Switch between profiles:

```bash
openmas --profile development run agent my_agent
```

## Advanced Options

### Hooks and Custom Scripts

Configure pre/post-command hooks:

```yaml
hooks:
  pre_run:
    - script: "scripts/pre_run.sh"
  post_deploy:
    - script: "scripts/post_deploy.sh"
```

### Plugin Configuration

Configure CLI plugins:

```yaml
plugins:
  enabled:
    - "my-openmas-plugin"
  settings:
    my-openmas-plugin:
      option1: "value1"
```

## Validation

Your configuration is automatically validated against the [unified configuration schema](../../03_configuration/unified_configuration_schema.md). You can manually validate:

```bash
openmas validate config
```

## Viewing Current Configuration

View your current configuration:

```bash
openmas config get  # View all configuration
openmas config get protocols.a2a  # View specific section
```

## See Also

- [Command Reference](../commands/README.md)
- [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md)
- [Developer Workflows](../development/developer_workflows.md)
