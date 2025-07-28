# CLI Tools System Setup

## Task Overview
Setup the CLI Tools system for OpenMAS 0.3.0, which provides developer productivity enhancements that fully support OpenMAS's reasoning-agnostic architecture and multi-protocol capabilities.

## Design Alignment
**Reference**: `/refactoring_work/design/01_architecture/components_summary.md` sections 194-212 and `/refactoring_work/design/documentation_structure.md` section `13_cli_tools/`
**Architecture**: CLI tools provide project scaffolding, configuration validation, command management, and development workflows while maintaining body-brain separation.

## Tasks

1. Create CLI Tools Directory Structure
   - Setup command management system
   - Create project scaffolding utilities
   - Configure development workflows

2. Implement Core CLI Commands
   - Project creation and initialization
   - Configuration validation and management
   - Agent lifecycle management
   - Deployment utilities

3. Setup Multi-Protocol Support
   - Protocol-specific commands and validation
   - Protocol configuration templates
   - Protocol testing utilities

4. Configure Reasoning Engine Integration
   - Reasoning-specific development workflows
   - Template generation for different reasoning approaches
   - Integration testing commands

## Directory Structure

```
src/openmas/cli_tools/
├── __init__.py                     # CLI tools module initialization
├── commands/                       # CLI command implementations
│   ├── __init__.py
│   ├── project/                   # Project management commands
│   │   ├── __init__.py
│   │   ├── init.py               # Project initialization
│   │   ├── scaffold.py           # Project scaffolding
│   │   └── template.py           # Template management
│   ├── config/                    # Configuration commands
│   │   ├── __init__.py
│   │   ├── validate.py           # Configuration validation
│   │   ├── generate.py           # Configuration generation
│   │   └── migrate.py            # Configuration migration
│   ├── agent/                     # Agent management commands
│   │   ├── __init__.py
│   │   ├── create.py             # Agent creation
│   │   ├── deploy.py             # Agent deployment
│   │   ├── test.py               # Agent testing
│   │   └── monitor.py            # Agent monitoring
│   ├── protocol/                  # Protocol-specific commands
│   │   ├── __init__.py
│   │   ├── a2a_commands.py       # A2A protocol commands
│   │   ├── mcp_commands.py       # MCP protocol commands
│   │   ├── http_commands.py      # HTTP protocol commands
│   │   └── protocol_test.py      # Protocol testing
│   └── development/               # Development workflow commands
│       ├── __init__.py
│       ├── test_runner.py        # Test execution
│       ├── lint_runner.py        # Linting utilities
│       └── docs_generator.py     # Documentation generation
├── scaffolding/                   # Project scaffolding system
│   ├── __init__.py
│   ├── templates/                 # Project templates
│   │   ├── __init__.py
│   │   ├── basic_agent/          # Basic agent template
│   │   ├── multi_protocol_agent/ # Multi-protocol agent template
│   │   ├── reasoning_agent/      # Reasoning-specific templates
│   │   └── integration_project/  # Integration project template
│   ├── generators/                # Code generators
│   │   ├── __init__.py
│   │   ├── agent_generator.py    # Agent code generator
│   │   ├── config_generator.py   # Configuration generator
│   │   └── test_generator.py     # Test code generator
│   └── validators/                # Template validators
│       ├── __init__.py
│       ├── structure_validator.py # Project structure validation
│       └── config_validator.py   # Configuration validation
├── utilities/                     # CLI utilities
│   ├── __init__.py
│   ├── console/                   # Console utilities
│   │   ├── __init__.py
│   │   ├── output.py             # Formatted output
│   │   ├── progress.py           # Progress indicators
│   │   └── interactive.py        # Interactive prompts
│   ├── file_operations/           # File operation utilities
│   │   ├── __init__.py
│   │   ├── template_processor.py # Template processing
│   │   ├── file_manager.py       # File management
│   │   └── directory_utils.py    # Directory utilities
│   └── validation/                # Validation utilities
│       ├── __init__.py
│       ├── schema_validator.py   # Schema validation
│       ├── project_validator.py  # Project validation
│       └── dependency_checker.py # Dependency checking
└── integrations/                  # Integration with other components
    ├── __init__.py
    ├── config_integration.py     # Configuration system integration
    ├── asset_integration.py      # Asset management integration
    └── deployment_integration.py # Deployment system integration
```

## Key Implementation Files

### 1. Main CLI Entry Point (`__init__.py`)

```python
"""
OpenMAS CLI Tools - Developer productivity enhancements.

Provides project scaffolding, configuration validation, and development workflows
that support OpenMAS's reasoning-agnostic architecture and multi-protocol capabilities.
"""

import click
from typing import Optional

from .commands.project import init, scaffold
from .commands.config import validate, generate
from .commands.agent import create, deploy, test
from .commands.protocol import protocol_test
from .commands.development import test_runner, lint_runner

@click.group()
@click.version_option(version="0.3.0")
@click.pass_context
def cli(ctx):
    """OpenMAS CLI Tools - Multi-protocol, reasoning-agnostic agent development."""
    ctx.ensure_object(dict)

# Project commands
@cli.group()
def project():
    """Project management commands."""
    pass

project.add_command(init.init_project)
project.add_command(scaffold.scaffold_project)

# Configuration commands
@cli.group()
def config():
    """Configuration management commands."""
    pass

config.add_command(validate.validate_config)
config.add_command(generate.generate_config)

# Agent commands
@cli.group()
def agent():
    """Agent management commands."""
    pass

agent.add_command(create.create_agent)
agent.add_command(deploy.deploy_agent)
agent.add_command(test.test_agent)

# Protocol commands
@cli.group()
def protocol():
    """Protocol-specific commands."""
    pass

protocol.add_command(protocol_test.test_protocols)

# Development commands
@cli.group()
def dev():
    """Development workflow commands."""
    pass

dev.add_command(test_runner.run_tests)
dev.add_command(lint_runner.run_lint)

if __name__ == "__main__":
    cli()
```

### 2. Project Initialization Command (`commands/project/init.py`)

```python
"""
Project initialization command for OpenMAS CLI.

Creates new OpenMAS projects with proper structure and configuration.
"""

import click
import os
from pathlib import Path
from typing import List, Optional

from ...scaffolding.generators.agent_generator import AgentGenerator
from ...scaffolding.generators.config_generator import ConfigGenerator
from ...utilities.console.output import success, error, info
from ...utilities.console.interactive import confirm, select_option

@click.command()
@click.argument('project_name')
@click.option('--protocols', '-p', multiple=True,
              type=click.Choice(['a2a', 'mcp', 'http', 'mqtt', 'grpc']),
              help='Protocols to include in the project')
@click.option('--reasoning', '-r',
              type=click.Choice(['rule_based', 'bdi', 'llm', 'hybrid', 'symbolic']),
              help='Primary reasoning approach')
@click.option('--template', '-t',
              type=click.Choice(['basic', 'multi_protocol', 'reasoning_focused', 'integration']),
              default='basic',
              help='Project template to use')
@click.option('--interactive', '-i', is_flag=True,
              help='Interactive project setup')
def init_project(project_name: str, protocols: tuple, reasoning: Optional[str],
                template: str, interactive: bool):
    """Initialize a new OpenMAS project."""

    project_path = Path.cwd() / project_name

    if project_path.exists():
        error(f"Directory '{project_name}' already exists")
        return

    # Interactive setup if requested
    if interactive:
        protocols = _interactive_protocol_selection()
        reasoning = _interactive_reasoning_selection()
        template = _interactive_template_selection()

    # Validate selections
    if not protocols:
        protocols = ('a2a',)  # Default protocol

    if not reasoning:
        reasoning = 'rule_based'  # Default reasoning

    try:
        # Create project directory
        project_path.mkdir(parents=True)
        info(f"Creating project '{project_name}'...")

        # Generate project structure
        _create_project_structure(project_path, template)

        # Generate configuration
        config_generator = ConfigGenerator()
        config_generator.generate_project_config(
            project_path,
            protocols=list(protocols),
            reasoning=reasoning
        )

        # Generate agent scaffolding
        agent_generator = AgentGenerator()
        agent_generator.generate_basic_agent(
            project_path,
            protocols=list(protocols),
            reasoning=reasoning
        )

        # Create development files
        _create_development_files(project_path)

        success(f"Project '{project_name}' created successfully!")
        info("Next steps:")
        info(f"  cd {project_name}")
        info("  openmas config validate")
        info("  openmas dev run-tests")

    except Exception as e:
        error(f"Failed to create project: {e}")
        # Cleanup on failure
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)

def _interactive_protocol_selection() -> List[str]:
    """Interactive protocol selection."""
    protocols = []

    info("Select protocols for your project:")
    available_protocols = ['a2a', 'mcp', 'http', 'mqtt', 'grpc']

    for protocol in available_protocols:
        if confirm(f"Include {protocol.upper()} protocol?"):
            protocols.append(protocol)

    if not protocols:
        protocols = ['a2a']  # Ensure at least one protocol

    return protocols

def _interactive_reasoning_selection() -> str:
    """Interactive reasoning approach selection."""
    reasoning_options = [
        ('rule_based', 'Rule-based reasoning (simple if-then logic)'),
        ('bdi', 'BDI reasoning (Belief-Desire-Intention)'),
        ('llm', 'LLM-based reasoning (Large Language Models)'),
        ('symbolic', 'Symbolic reasoning (formal logic)'),
        ('hybrid', 'Hybrid reasoning (combination of approaches)')
    ]

    return select_option("Select primary reasoning approach:", reasoning_options)

def _interactive_template_selection() -> str:
    """Interactive template selection."""
    template_options = [
        ('basic', 'Basic agent template'),
        ('multi_protocol', 'Multi-protocol agent template'),
        ('reasoning_focused', 'Reasoning-focused template'),
        ('integration', 'Integration project template')
    ]

    return select_option("Select project template:", template_options)

def _create_project_structure(project_path: Path, template: str):
    """Create basic project directory structure."""
    directories = [
        'src',
        'tests/unit',
        'tests/integration',
        'config',
        'docs',
        'scripts'
    ]

    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)

def _create_development_files(project_path: Path):
    """Create development configuration files."""

    # Create pyproject.toml
    pyproject_content = '''[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = "OpenMAS agent project"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.9"
openmas = "^0.3.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"
pytest-asyncio = "^0.21"
black = "^23.0"
flake8 = "^6.0"
mypy = "^1.0"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.black]
line-length = 88
target-version = ['py39']

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
'''.format(project_name=project_path.name)

    (project_path / 'pyproject.toml').write_text(pyproject_content)

    # Create README.md
    readme_content = f'''# {project_path.name}

OpenMAS agent project with multi-protocol support and reasoning-agnostic architecture.

## Setup

```bash
poetry install
```

## Configuration

```bash
openmas config validate
```

## Testing

```bash
openmas dev run-tests
```

## Development

This project uses OpenMAS 0.3.0 with support for multiple protocols and reasoning approaches.
'''

    (project_path / 'README.md').write_text(readme_content)
```

## Integration with Other Components

### 1. Configuration System Integration

CLI tools integrate with the configuration system through:

- **Schema Validation**: Validates configurations against unified schema
- **Template Generation**: Generates configuration templates for different setups
- **Migration Support**: Helps migrate configurations between versions
- **Environment Management**: Manages environment-specific configurations

### 2. Asset Management Integration

CLI tools integrate with asset management through:

- **Asset Discovery**: Commands to discover and list available assets
- **Asset Installation**: Commands to install and manage assets
- **Version Management**: Commands to manage asset versions
- **Dependency Resolution**: Automatic asset dependency resolution

## Configuration Integration

CLI tools should be configured through the unified configuration schema:

```yaml
cli_tools:
  templates:
    default_template: "basic"
    custom_template_paths:
      - "~/.openmas/templates"
      - "/usr/local/share/openmas/templates"
  scaffolding:
    auto_install_dependencies: true
    generate_tests: true
    generate_docs: true
  development:
    default_test_runner: "pytest"
    auto_format: true
    lint_on_save: true
  protocols:
    default_protocols: ["a2a"]
    protocol_templates:
      a2a: "templates/a2a_agent.py.j2"
      mcp: "templates/mcp_agent.py.j2"
```

## Success Criteria
- Complete CLI Tools directory structure created
- Core CLI commands implemented (init, scaffold, validate, test)
- Multi-protocol support in all commands
- Reasoning engine integration working
- Project templates for different scenarios available
- Interactive and non-interactive modes functional
- Integration with configuration and asset management systems
- Development workflow commands operational
