# Validate Command

## Overview

The `validate` command checks OpenMAS configuration files against the unified configuration schema to ensure they are valid and complete. This command helps catch configuration errors before attempting to run agents or systems.

## Usage

```bash
openmas validate [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Path to configuration file (required) |
| `--schema`, `-s` | Path to schema file (default: built-in schema) |
| `--verbose`, `-v` | Show detailed validation results |
| `--fix` | Attempt to fix common validation errors |
| `--output`, `-o` | Write fixed configuration to specified file |
| `--strict` | Enable strict validation (fail on warnings) |
| `--protocol-specific` | Validate protocol-specific sections only (a2a, mcp, http, mqtt, grpc) |
| `--reasoning-specific` | Validate reasoning-specific sections only (rule, bdi, llm, hybrid, knowledge_graph) |
| `--capability-map` | Validate capability mappings across protocols |
| `--body-brain-separation` | Verify proper separation between communication body and reasoning brain |
| `--deep` | Perform deep validation including cross-references and dependency checks |

## Validation Types

The `validate` command performs several types of validation:

| Validation Type | Description |
|----------------|-------------|
| Schema Validation | Validates the configuration against the JSON Schema |
| Reference Validation | Checks that all references within the configuration are valid |
| Dependency Validation | Verifies that required dependencies are configured |
| Protocol Compatibility | Checks that protocol configurations are compatible |
| Reasoning Compatibility | Verifies that reasoning configurations are compatible with protocols |

## Examples

### Validate a Configuration File

```bash
openmas validate --file config/agent_config.yaml
```

This validates the agent configuration file against the built-in schema.

### Validate and Fix a Configuration File

```bash
openmas validate --file config/agent_config.yaml --fix --output config/fixed_agent_config.yaml
```

This validates the configuration, attempts to fix any errors, and writes the fixed configuration to a new file.

### Validate Multiple Configuration Files

```bash
openmas validate --file config/agent_config.yaml config/protocols_config.yaml
```

This validates multiple configuration files and reports errors for each.

## Validation Messages

The `validate` command provides detailed feedback on validation errors:

### Error Types

| Error Type | Description |
|------------|-------------|
| `SchemaError` | Configuration does not match the schema |
| `ReferenceError` | Reference to a non-existent element |
| `DependencyError` | Missing required dependency |
| `CompatibilityError` | Incompatible configuration elements |
| `WarningError` | Potential issues that may cause problems |

### Error Format

```
[ERROR] SchemaError in agent_config.yaml:
  Path: $.protocols[0].settings
  Message: Required property 'type' is missing
```

## Exit Codes

| Exit Code | Description |
|-----------|-------------|
| 0 | Validation successful (no errors) |
| 1 | Validation failed (errors found) |
| 2 | Validation command error (file not found, etc.) |

## Integration with Development Workflows

The `validate` command can be integrated into development workflows:

- **Pre-commit hooks**: Validate configuration files before committing changes
- **CI/CD pipelines**: Validate configurations as part of continuous integration
- **Development scripts**: Validate configurations before running tests

## Related Commands

- [init](./init.md): Initialize a new OpenMAS project
- [config](./config.md): Manage OpenMAS configurations
- [run](./run.md): Run agents and systems

## Advanced Validation Examples

### Validate Multi-Protocol Capability Mappings

```bash
openmas validate --file config/multi_protocol_agent.yaml --capability-map
```

This validates that capabilities are properly mapped across different protocols in an agent configuration, ensuring compatibility with OpenMAS's multi-protocol design.

### Validate Body-Brain Separation

```bash
openmas validate --file config/agent_config.yaml --body-brain-separation
```

This checks that the agent configuration properly separates communication infrastructure ("body") from reasoning components ("brain"), a core principle of OpenMAS's reasoning-agnostic architecture.

### Protocol-Specific Validation

```bash
openmas validate --file config/a2a_agent.yaml --protocol-specific a2a
```

This validates only the A2A protocol-specific sections of the configuration.

### Reasoning-Specific Validation

```bash
openmas validate --file config/llm_agent.yaml --reasoning-specific llm
```

This validates only the LLM reasoning-specific sections of the configuration.

### Deep Validation with Cross-References

```bash
openmas validate --file config/complex_system.yaml --deep
```

This performs a deep validation including cross-references between components, dependency checks, and ensures proper alignment between protocols and reasoning components.

### Example of a Complex Multi-Protocol Configuration

```yaml
# complex_system.yaml
name: complex-multi-protocol-system
version: "1.0"

agents:
  coordinator:
    multi_protocol_capabilities:
      core:
        - name: assign_task
          parameters:
            task_id: string
            task_data: object
            worker_id: string
      protocol_mapping:
        a2a:
          assign_task:
            function_name: create_task
            parameter_mapping:
              task_id: id
              task_data: data
              worker_id: target
        mcp:
          assign_task:
            function_name: dispatch_task
            parameter_mapping:
              task_id: task_id
              task_data: payload
              worker_id: recipient

    communication:
      primary_protocol: a2a
      protocols:
        a2a:
          mode: server
          endpoint: http://localhost:8000
        mcp:
          mode: client
          endpoint: http://localhost:8100

    reasoning:
      engine: bdi
      beliefs:
        workers:
          - id: "worker1"
            capabilities: ["text_processing"]
      desires:
        - distribute_tasks_efficiently
      intentions:
        - assign_tasks_by_capability
```

Validating this configuration would check:
1. Multi-protocol capability mappings between A2A and MCP
2. Proper body-brain separation (communication vs. reasoning)
3. Protocol-specific configuration validity
4. BDI reasoning configuration validity

## Related Documentation

- [Configuration Schema](../../03_configuration/unified_configuration_schema.md)
- [Configuration Validation](../../03_configuration/configuration_validation.md)
- [Development Workflows](../development/developer_workflows.md)
