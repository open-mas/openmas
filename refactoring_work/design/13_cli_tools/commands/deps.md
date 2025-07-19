# Deps Command

## Overview

The `deps` command manages dependencies for OpenMAS projects. It handles installation, updating, and verification of dependencies required by various OpenMAS components, ensuring that all necessary libraries and tools are properly installed and configured.

## Usage

```bash
openmas deps [subcommand] [options]
```

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `install` | Install dependencies |
| `update` | Update dependencies |
| `check` | Check if dependencies are installed |
| `list` | List installed dependencies |
| `export` | Export dependencies to a requirements file |

## Options

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Path to configuration file |
| `--requirements`, `-r` | Path to requirements file |
| `--dev` | Include development dependencies |
| `--extras` | Extra dependencies to install (comma-separated) |
| `--no-version-check` | Skip version compatibility check |
| `--upgrade` | Upgrade dependencies to latest version |
| `--only-missing` | Only install missing dependencies |

## Dependency Categories

The `deps` command manages several categories of dependencies:

| Category | Description |
|----------|-------------|
| `core` | Core OpenMAS dependencies |
| `protocols` | Protocol-specific dependencies |
| `reasoning` | Reasoning engine dependencies |
| `extensions` | Extension-specific dependencies |
| `dev` | Development and testing dependencies |

## Examples

### Install Core Dependencies

```bash
openmas deps install
```

This installs all core OpenMAS dependencies.

### Install Dependencies from Configuration File

```bash
openmas deps install --file config/agent_config.yaml
```

This automatically detects required dependencies based on the configuration and installs them.

### Install Protocol-Specific Dependencies

```bash
openmas deps install --extras protocols.mcp,protocols.a2a
```

This installs dependencies for the MCP and A2A protocols.

### Update All Dependencies

```bash
openmas deps update
```

This updates all dependencies to their latest compatible versions.

### Check Dependencies

```bash
openmas deps check
```

This checks if all required dependencies are installed and reports any missing or incompatible dependencies.

### Export Dependencies to Requirements File

```bash
openmas deps export --file requirements.txt
```

This exports the project's dependencies to a requirements file.

## Dependency Resolution

The `deps` command uses a sophisticated dependency resolution process:

1. **Detect Required Components**: Analyze project configuration to determine required components
2. **Identify Dependencies**: Map components to their required dependencies
3. **Check Compatibility**: Ensure dependency versions are compatible with each other
4. **Resolution**: Resolve dependency conflicts if needed
5. **Installation**: Install or update dependencies

## Virtual Environments

The `deps` command works with Python virtual environments:

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies in the virtual environment
openmas deps install
```

## Integration with Package Managers

The `deps` command can integrate with different package managers:

- **pip**: Default Python package manager
- **conda**: For environments using Conda
- **poetry**: For projects using Poetry

## Related Commands

- [init](./init.md): Initialize a new OpenMAS project
- [validate](./validate.md): Validate OpenMAS configurations
- [run](./run.md): Run agents and systems

## Related Documentation

- [Installation Guide](../installation/installation_guide.md)
- [Development Environment](../environment/README.md)
- [Development Workflows](../development/developer_workflows.md)
