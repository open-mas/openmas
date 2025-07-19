# Tox Configuration for OpenMAS 0.3.0

## Overview

This document outlines the comprehensive tox configuration for OpenMAS 0.3.0, designed to support the framework's reasoning-agnostic architecture and multi-protocol approach. The configuration provides specialized environments for testing different components, running integration tests, and ensuring code quality.

## Complete tox.ini Configuration

```ini
[tox]
envlist = py38, py39, py310, py311, lint, type, docs, integration-{a2a,mcp,hybrid}
isolated_build = True

# Main unit test environment
[testenv]
description = Run all unit tests
deps =
    pytest>=7.0.0
    pytest-asyncio>=0.18.0
    pytest-cov>=3.0.0
    pytest-mock>=3.10.0
commands =
    pytest {posargs:tests/unit} --cov=openmas --cov-report=xml

# Debug environment for quick troubleshooting
[testenv:debug]
description = Run specific tests with extra verbosity for debugging
deps = {[testenv]deps}
    pytest-watch>=4.2.0
commands =
    pytest {posargs} -vvs

# Component-specific unit test environments
[testenv:unit-protocols]
description = Test protocol implementations only
deps = {[testenv]deps}
commands =
    pytest {posargs:tests/unit/protocols} --cov=openmas.protocols --cov-report=xml

[testenv:unit-reasoning]
description = Test reasoning modules only
deps = {[testenv]deps}
commands =
    pytest {posargs:tests/unit/reasoning} --cov=openmas.reasoning --cov-report=xml

[testenv:unit-core]
description = Test core agent functionality
deps = {[testenv]deps}
commands =
    pytest {posargs:tests/unit/core} --cov=openmas.core --cov-report=xml

# Protocol bridge testing environment
[testenv:unit-protocol-interop]
description = Test communication between different protocol implementations
deps = {[testenv]deps}
commands =
    pytest {posargs:tests/unit/protocols/interop} --cov=openmas.protocols --cov-report=xml

# Reasoning swap testing
[testenv:unit-reasoning-swap]
description = Test swapping reasoning implementations in agents
deps = {[testenv]deps}
commands =
    pytest {posargs:tests/unit/reasoning/swap} --cov=openmas.reasoning --cov-report=xml

# Code quality
[testenv:lint]
description = Run code quality checks
deps =
    ruff>=0.1.0
    black>=23.0.0
commands =
    black --check src tests
    ruff check --select E,F,I,D,UP,N,B,SIM src tests

# Type checking
[testenv:type]
description = Check type annotations
deps =
    mypy>=1.0.0
    types-requests
    types-PyYAML
commands =
    mypy src

# Documentation
[testenv:docs]
description = Build documentation
deps =
    sphinx>=6.0.0
    sphinx-rtd-theme>=1.0.0
    myst-parser>=1.0.0
commands =
    sphinx-build -b html docs/source docs/build/html

# Integration tests (Docker-based)
[testenv:integration-a2a]
description = Run A2A protocol integration tests
deps =
    pytest>=7.0.0
    pytest-asyncio>=0.18.0
    docker-compose>=2.0.0
    requests>=2.28.0
commands =
    docker-compose -f tests/integration/docker/docker-compose.a2a.yml up --build --exit-code-from test-controller

[testenv:integration-mcp]
description = Run MCP protocol integration tests
deps = {[testenv:integration-a2a]deps}
commands =
    docker-compose -f tests/integration/docker/docker-compose.mcp.yml up --build --exit-code-from test-controller

[testenv:integration-hybrid]
description = Run multi-protocol integration tests
deps = {[testenv:integration-a2a]deps}
commands = 
    docker-compose -f tests/integration/docker/docker-compose.hybrid.yml up --build --exit-code-from test-controller

# Reasoning-specific environments
[testenv:reasoning-rule]
description = Test rule-based reasoning implementation
deps = {[testenv]deps}
commands =
    pytest {posargs:tests/unit/reasoning/rule_based}

[testenv:reasoning-bdi]
description = Test BDI reasoning implementation
deps = {[testenv]deps}
commands =
    pytest {posargs:tests/unit/reasoning/bdi}

[testenv:reasoning-llm]
description = Test LLM-based reasoning implementation
deps = {[testenv]deps}
    requests-mock>=1.10.0
commands =
    pytest {posargs:tests/unit/reasoning/llm_based}

# Development environment
[testenv:dev]
description = Set up a development environment with all dependencies
deps =
    -r requirements-dev.txt
usedevelop = True
commands =

# Pre-commit hooks
[testenv:pre-commit]
description = Run pre-commit hooks on all files
deps =
    pre-commit>=3.0.0
commands =
    pre-commit run --all-files

# Configuration validation
[testenv:config-validate]
description = Validate configuration files against schema
deps =
    pyyaml>=6.0
    jsonschema>=4.0.0
commands =
    python -m openmas.cli config validate --schema-path schema/config.json --config-path tests/fixtures/configs/
```

## Corresponding pyproject.toml Configuration

```toml
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "openmas"
version = "0.3.0"
description = "Open Multi-Agent System Framework"
authors = ["OpenMAS Contributors"]
readme = "README.md"
packages = [{include = "openmas", from = "src"}]

[tool.poetry.dependencies]
python = ">=3.8,<3.12"
pyyaml = "^6.0"
requests = "^2.28.0"
asyncio = "^3.4.3"
aiohttp = "^3.8.3"
typing-extensions = "^4.5.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-asyncio = "^0.18.0"
pytest-cov = "^3.0.0"
pytest-mock = "^3.10.0"
pytest-watch = "^4.2.0"
black = "^23.0.0"
ruff = "^0.1.0"
mypy = "^1.0.0"
types-requests = "*"
types-PyYAML = "*"
sphinx = "^6.0.0"
sphinx-rtd-theme = "^1.0.0"
myst-parser = "^1.0.0"
pre-commit = "^3.0.0"
docker-compose = "^2.0.0"

[tool.black]
line-length = 88
target-version = ["py38", "py39", "py310", "py311"]
include = '\.pyi?$'

[tool.ruff]
line-length = 88
target-version = "py38"
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "D",   # pydocstyle
    "UP",  # pyupgrade
    "N",   # pep8-naming
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
    "ARG", # flake8-unused-arguments
    "ERA", # eradicate
    "COM", # flake8-commas
    "PT",  # flake8-pytest-style
]
ignore = [
    "D203",  # one-blank-line-before-class (conflicts with D211)
    "D212",  # multi-line-summary-first-line (conflicts with D213)
]

[tool.ruff.per-file-ignores]
"tests/*" = ["D", "ANN"]

[tool.ruff.isort]
known-first-party = ["openmas"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
strict_optional = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false
```

## Key Features of the Configuration

### 1. Unit Testing

- **Base Environment**: Run all unit tests with coverage reports
- **Component-Specific**: Separate environments for testing protocols, reasoning modules, and core functionality
- **Debug Environment**: Quick troubleshooting with increased verbosity
- **Specialized Tests**:
  - Protocol interoperability tests
  - Reasoning module swap tests
  - Individual reasoning approach tests

### 2. Integration Testing with Docker

- **Protocol-Specific**: Separate environments for A2A, MCP, and hybrid protocol testing
- **Docker Integration**: Uses Docker Compose to create isolated test environments
- **Real Component Testing**: Tests against actual protocol implementations, not mocks

### 3. Code Quality and Documentation

- **Modern Linting**: Ruff for comprehensive and fast linting (replacing flake8 and isort)
- **Formatting**: Black for consistent code style
- **Type Checking**: MyPy for static type analysis
- **Documentation**: Sphinx with RTD theme and Markdown support

### 4. Developer Experience

- **Development Environment**: Complete environment for interactive development
- **Pre-commit Hooks**: Ensures code quality checks run before commits
- **Configuration Validation**: Validates configuration files against schemas

### 5. CI/CD Integration

The tox configuration is designed to integrate seamlessly with CI/CD pipelines:

```yaml
# Example GitHub Actions job using tox
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
        test-group: [unit, lint, type, integration-a2a, integration-mcp]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install tox tox-gh-actions
      
      - name: Test with tox
        run: |
          # Map test-group to tox environments
          if [ "${{ matrix.test-group }}" == "unit" ]; then
            TOX_ENV="py"
          elif [ "${{ matrix.test-group }}" == "lint" ]; then
            TOX_ENV="lint"
          elif [ "${{ matrix.test-group }}" == "type" ]; then
            TOX_ENV="type"
          else
            TOX_ENV="${{ matrix.test-group }}"
          fi
          
          tox -e $TOX_ENV
```

## Usage Examples

### Running Unit Tests

```bash
# Run all unit tests
tox

# Run only protocol tests
tox -e unit-protocols

# Run tests for a specific file
tox -e debug tests/unit/protocols/test_a2a_protocol.py

# Run tests with specific pytest arguments
tox -- -xvs tests/unit/core
```

### Running Integration Tests

```bash
# Run A2A protocol integration tests
tox -e integration-a2a

# Run MCP protocol integration tests
tox -e integration-mcp
```

### Code Quality Checks

```bash
# Run linting
tox -e lint

# Run type checking
tox -e type

# Run pre-commit hooks
tox -e pre-commit
```

### Building Documentation

```bash
# Build HTML documentation
tox -e docs
```

### Development Environment

```bash
# Set up a development environment
tox -e dev
```

## Alignment with OpenMAS Architecture

This tox configuration specifically supports OpenMAS's reasoning-agnostic architecture by:

1. **Separate Testing Environments**: Testing protocol implementations independently from reasoning modules
2. **Protocol Interoperability**: Dedicated environments for testing protocol interactions
3. **Reasoning Swapping**: Specialized tests for validating the ability to swap reasoning approaches
4. **Real Integration Testing**: Docker-based environments for testing actual components

The configuration ensures comprehensive testing of OpenMAS's unique architecture while providing developers with flexible, focused testing tools.
