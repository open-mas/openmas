# Setting Up Your OpenMAS Application

OpenMAS can be used with any standard Python environment and dependency manager. This guide provides multiple approaches for setting up your OpenMAS application, allowing you to choose the method that best fits your workflow.

## Core Requirements

The only fundamental requirement is a Python environment (Python 3.10 or higher) with OpenMAS installed. All the setup methods below achieve this in different ways.

## Setup Method 1: Using `venv` and `pip` (Manual Setup)

This approach uses Python's built-in virtual environment system.

```bash
# Create a new directory for your project
mkdir my_openmas_project
cd my_openmas_project

# Create a virtual environment
python -m venv .venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install OpenMAS
pip install openmas

# Initialize your OpenMAS project structure
openmas init . --name my_project
```

This creates a standard Python virtual environment with OpenMAS installed and generates the proper directory structure for your OpenMAS application.

## Setup Method 2: Using `openmas init` (Recommended for New Projects)

The OpenMAS CLI includes project scaffold generation that works with any environment:

```bash
# Create a new project with standard structure and requirements.txt
openmas init my_project

# Change to the project directory
cd my_project

# Create and activate a virtual environment
python -m venv .venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

### Poetry Support

If you prefer using Poetry for dependency management, the `init` command has a `--poetry` flag:

```bash
# Create a new project with Poetry support
openmas init my_project --poetry

# Change to the project directory
cd my_project

# Install dependencies using Poetry
poetry install

# Run commands through Poetry
poetry run openmas run sample_agent
```

With the `--poetry` flag, OpenMAS generates a `pyproject.toml` file instead of `requirements.txt`, properly configured for an OpenMAS application.

## Setup Method 3: Using Poetry (Manual Setup for Existing Poetry Users)

If you're already using Poetry for other projects, you can integrate OpenMAS into your workflow:

```bash
# Create a new Poetry project
poetry new my_openmas_project --name my_openmas_project
cd my_openmas_project

# Add OpenMAS as a dependency
poetry add openmas

# Use Poetry's shell for development
poetry shell

# Initialize the OpenMAS structure inside your Poetry project
openmas init . --name my_openmas_project
```

Example `pyproject.toml` configuration:

```toml
[tool.poetry]
name = "my-openmas-project"
version = "0.1.0"
description = "An OpenMAS application"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
# Use this setting for applications
package-mode = false

[tool.poetry.dependencies]
python = "^3.10"
openmas = "^0.2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Setup Method 4: Using Conda

Conda users can integrate OpenMAS into their workflow:

```bash
# Create a new conda environment
conda create -n openmas-env python=3.10
conda activate openmas-env

# Install OpenMAS via pip (openmas is not on conda-forge directly)
pip install openmas

# Initialize your OpenMAS project structure
openmas init my_project
cd my_project
```

## Verifying Your Setup

To verify that your OpenMAS environment is properly set up:

```bash
# Check the OpenMAS version and system information
openmas info

# Try listing available agents in your project
openmas list agents
```

## The `openmas_project.yml` File

The central configuration for your OpenMAS application is the `openmas_project.yml` file, which defines:

- Project name and version
- Agent configurations and locations
- Shared code paths
- Extension paths
- Global configuration settings
- Asset definitions

This file is essential for running your OpenMAS agents and is generated automatically by the `openmas init` command:

```yaml
name: my_project
version: 0.1.0
agents:
  sample_agent: agents/sample_agent
shared_paths:
  - shared
extension_paths:
  - extensions
default_config:
  log_level: INFO
  communicator_type: http
dependencies: []
```

No matter which environment manager you use, this file remains the core configuration for your OpenMAS application.

## Running Your Application

To run your agent (using any of the setup methods):

```bash
# If using a virtual environment, activate it first
source .venv/bin/activate  # or the equivalent for your environment

# Run your agent
openmas run sample_agent

# If using Poetry:
poetry run openmas run sample_agent
```

## Next Steps

- [Explore the OpenMAS CLI](../cli/index.md)
- [Learn about agent development](../agent/index.md)
- [Understand asset management](../asset_management.md)
