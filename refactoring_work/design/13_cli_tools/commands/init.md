# Init Command

## Overview

The `init` command initializes new OpenMAS projects with the appropriate directory structure, configuration files, and boilerplate code. This is typically the first command you'll use when starting a new OpenMAS project.

## Usage

```bash
openmas init [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--name`, `-n` | Project name (required) |
| `--dir`, `-d` | Directory to create the project in (default: current directory) |
| `--template`, `-t` | Project template to use (default: 'basic') |
| `--protocols` | Protocols to include (comma-separated, e.g., 'mcp,a2a,http,mqtt,grpc') |
| `--reasoning` | Reasoning approaches to include (comma-separated, e.g., 'rule,llm,bdi,hybrid,knowledge_graph') |
| `--config-format` | Configuration format to generate ('yaml' or 'json', default: 'yaml') |
| `--body-brain-separation` | Enable explicit body-brain separation in generated configurations (default: true) |
| `--force`, `-f` | Overwrite existing files |
| `--no-deps` | Skip dependency installation |

## Templates

The `init` command supports the following project templates:

| Template | Description |
|----------|-------------|
| `basic` | Basic agent project with minimal functionality |
| `full` | Complete agent project with all components |
| `minimal` | Minimal project with core functionality only |
| `service` | Service-oriented agent project |
| `multi-agent` | Multi-agent system project |
| `protocol-adapter` | Protocol adapter project |

## Examples

### Initialize a Basic Project

```bash
openmas init --name my-agent
```

This creates a new OpenMAS project with the name "my-agent" using the basic template.

### Initialize a Multi-Agent Project with Specific Protocols

```bash
openmas init --name my-mas --template multi-agent --protocols mcp,a2a
```

This creates a new multi-agent project with MCP and A2A protocol support.

### Initialize a Project with LLM Reasoning

```bash
openmas init --name llm-agent --reasoning llm
```

This creates a new project configured to use LLM-based reasoning.

## Project Structure

The `init` command creates the following project structure:

```
project-name/
├── README.md                     # Project documentation
├── pyproject.toml                # Python project configuration
├── config/                       # Configuration files
│   ├── agent_config.yaml         # Agent configuration
│   ├── protocols_config.yaml     # Protocol configuration
│   └── reasoning_config.yaml     # Reasoning configuration
├── src/                          # Source code
│   └── project_name/             # Python package
│       ├── __init__.py           # Package initialization
│       ├── agent.py              # Agent implementation
│       ├── protocols/            # Protocol adapters
│       └── reasoning/            # Reasoning implementations
└── tests/                        # Test files
    ├── conftest.py               # Test configuration
    ├── test_agent.py             # Agent tests
    ├── test_protocols.py         # Protocol tests
    └── test_reasoning.py         # Reasoning tests
```

## Configuration

The `init` command generates configuration files with reasonable defaults based on the selected template and options. These files follow the OpenMAS unified configuration schema and can be further customized after project creation.

## Related Commands

- [validate](./validate.md): Validate the configuration of an OpenMAS project
- [deps](./deps.md): Manage project dependencies
- [run](./run.md): Run agents and systems

## Related Documentation

- [Project Structure](../development/project_structure.md)
- [Configuration](../configuration/README.md)
- [Development Workflows](../development/developer_workflows.md)
