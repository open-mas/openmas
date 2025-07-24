# CLI Command: `validate`

## 1. Overview

The `openmas validate` command is a crucial tool for ensuring that your OpenMAS configuration files are correctly structured and adhere to the framework's schema. Running this command before `run` can save significant time by catching errors early.

## 2. Usage

```bash
openmas validate --file <path_to_config.yaml> [OPTIONS]
```

## 3. Key Parameters

| Parameter | Short | Description |
|---|---|---|
| `--file` | `-f` | **(Required)** Specifies the path to the YAML configuration file to be validated. |
| `--schema`| `-s` | Specifies a path to a custom schema file. If omitted, `validate` uses the built-in schema corresponding to the OpenMAS version. |
| `--verbose`| `-v` | Provides a more detailed output, showing every check performed, not just the errors. |

## 4. Practical Scenarios & Examples

### Scenario 1: Basic Validation of a Configuration File

This is the most common use case.

**Command:**
```bash
openmas validate --file ./configs/my_agent_config.yaml
```

**Example Output (Success):**
```
✅ Validation successful: ./configs/my_agent_config.yaml is valid.
```

**Example Output (Failure):**
```
❌ Validation failed for ./configs/my_agent_config.yaml:

[ERROR] SchemaError
  - Path: agents[0].communication
  - Message: "'protocl' is not one of ['protocol']"
  - Help: Did you mean 'protocol'?

[ERROR] SchemaError
  - Path: agents[0].name
  - Message: "'name' is a required property"
```

This output clearly indicates two errors:
1. A typo (`protocl` instead of `protocol`).
2. A missing `name` field for the first agent.

### Scenario 2: Validating Multiple Files at Once

You can pass multiple file paths to validate them in a single command.

**Command:**
```bash
openmas validate -f ./configs/agent1.yaml ./configs/agent2.yaml
```

**Example Output:**
```
✅ Validation successful: ./configs/agent1.yaml is valid.
❌ Validation failed for ./configs/agent2.yaml:

[ERROR] SchemaError
  - Path: version
  - Message: "'0.2.0' does not match '^0.3.0'"

Found 1 error(s) in 2 file(s).
```

### Scenario 3: Validating Against a Custom Schema

If you have extended the OpenMAS schema for custom components, you can validate against your version.

**Command:**
```bash
openmas validate -f ./configs/my_custom_agent.yaml -s ./schemas/my_extended_schema.json
```

## 5. Exit Codes for Automation

The `validate` command uses exit codes to signal its result, making it easy to integrate into automated scripts and CI/CD pipelines.

| Exit Code | Meaning |
|---|---|
| `0` | Success. All files are valid. |
| `1` | Failure. At least one validation error was found. |
| `2` | Command Error. E.g., a specified file was not found. |

**Example CI/CD Script:**

```yaml
# .github/workflows/ci.yml
jobs:
  lint-and-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install OpenMAS
        run: pip install openmas

      - name: Validate all configurations
        run: openmas validate --file ./configs/*.yaml
```
If any configuration file in the `configs/` directory is invalid, the `validate` command will exit with code `1`, causing the CI pipeline to fail as expected.

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
