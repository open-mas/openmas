# Dependencies and Build Process for OpenMAS 0.3.0

## Task Overview
Define and configure the dependencies, build process, and packaging for OpenMAS 0.3.0, ensuring compatibility with all required protocols and reasoning approaches.

## Tasks

1. Dependency Management
   - Define core dependencies for the framework
   - Organize optional dependencies by protocol and feature
   - Configure dependency groups for different development tasks

2. Build Process
   - Configure Poetry build settings
   - Setup package distribution configuration
   - Define build artifacts and versioning

3. Development Environment
   - Configure development environment setup
   - Create development scripts
   - Document development workflow

## Core Dependencies

OpenMAS requires the following core dependencies:

| Dependency | Version | Purpose |
|------------|---------|---------|
| `pydantic` | ^2.0.0 | Data validation and configuration |
| `PyYAML` | ^6.0 | YAML configuration processing |
| `requests` | ^2.28.0 | HTTP client for communication |
| `typing-extensions` | ^4.5.0 | Enhanced typing support |
| `jsonschema` | ^4.17.3 | JSON schema validation |
| `jinja2` | ^3.1.2 | Template rendering for prompts |

## Protocol-Specific Dependencies

Dependencies required for specific protocols:

### A2A Protocol
```toml
[tool.poetry.group.a2a.dependencies]
fastapi = "^0.95.1"
uvicorn = "^0.22.0"
websockets = "^11.0.3"
httpx = "^0.24.0"
```

### MCP Protocol
```toml
[tool.poetry.group.mcp.dependencies]
websockets = "^11.0.3"
sseclient-py = "^1.7.2"
```

### MQTT Protocol
```toml
[tool.poetry.group.mqtt.dependencies]
paho-mqtt = "^2.2.1"
```

### gRPC Protocol
```toml
[tool.poetry.group.grpc.dependencies]
grpcio = "^1.54.2"
grpcio-tools = "^1.54.2"
```

## Development Dependencies

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.3.1"
pytest-cov = "^4.1.0"
black = "^23.3.0"
isort = "^5.12.0"
mypy = "^1.3.0"
flake8 = "^6.0.0"
tox = "^4.6.0"
pre-commit = "^3.3.2"
mkdocs = "^1.4.3"
mkdocs-material = "^9.1.15"
mkdocstrings = "^0.22.0"
```

## Optional Feature Configuration

Configure Poetry extras to allow selective installation of protocol support:

```toml
[tool.poetry.extras]
all = ["fastapi", "uvicorn", "websockets", "httpx", "sseclient-py", "paho-mqtt", "grpcio", "grpcio-tools"]
a2a = ["fastapi", "uvicorn", "websockets", "httpx"]
mcp = ["websockets", "sseclient-py"]
mqtt = ["paho-mqtt"]
grpc = ["grpcio", "grpcio-tools"]
```

## Development Environment Setup

Create a script to set up the development environment:

```bash
#!/bin/bash
# scripts/setup_dev.sh
# Script to set up the development environment

set -e

# Install poetry if not already installed
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies
echo "Installing dependencies..."
poetry install --with dev,a2a,mcp,mqtt,grpc

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
poetry run pre-commit install

# Create initial empty directories (if needed)
echo "Creating directory structure..."
mkdir -p src/openmas/{agent,assets,cli,communicators,config,deployment,extensions,integrations,observability,prompts,security,sessions}

echo "Development environment setup complete!"
```

## Build Process

### Build Configuration

```toml
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "openmas"
version = "0.3.0"
description = "OpenMAS - Open Multi-Agent System Framework"
authors = ["OpenMAS Contributors"]
license = "MIT"
readme = "README.md"
repository = "https://github.com/openmas-ai/openmas"
documentation = "https://docs.openmas.ai"
packages = [{include = "openmas", from = "src"}]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
```

### Build Commands

```bash
# Build the package
poetry build

# Run tests
poetry run pytest

# Generate documentation
poetry run mkdocs build

# Publish to PyPI (when ready)
poetry publish
```

## Installation Instructions

Documentation for users on installing OpenMAS:

```markdown
# Installation

## Basic Installation

```bash
pip install openmas
```

## With Protocol Support

Install with specific protocol support:

```bash
# All protocols
pip install "openmas[all]"

# A2A protocol
pip install "openmas[a2a]"

# MCP protocol
pip install "openmas[mcp]"

# MQTT protocol
pip install "openmas[mqtt]"

# gRPC protocol
pip install "openmas[grpc]"
```

## Development Installation

For development, clone the repository and install with Poetry:

```bash
git clone https://github.com/openmas-ai/openmas.git
cd openmas
poetry install --with dev,a2a,mcp,mqtt,grpc
```
```

## Ensuring Reasoning Agnosticism

The OpenMAS framework is designed to be reasoning-agnostic, separating agent communication infrastructure (the "body") from various reasoning approaches (the "brain"). To maintain this principle, the dependencies are structured to avoid forcing specific reasoning approaches.

Key reasoning capabilities supported include:

1. Simple rule-based reasoning
2. BDI (Belief-Desire-Intention) architecture
3. Knowledge Representation and Reasoning (KR&R) module
4. LLM-based reasoning
5. Hybrid reasoning approaches

The dependency structure ensures:

1. Core dependencies enable protocol communication without requiring specific reasoning approaches
2. Protocol dependencies are separated into optional groups
3. Reasoning-specific dependencies can be added as needed by end users

## Success Criteria
- All dependencies properly defined and organized
- Poetry configured for build and package management
- Development environment setup script created
- Installation instructions for all scenarios documented
- Reasoning agnosticism preserved in dependency structure
