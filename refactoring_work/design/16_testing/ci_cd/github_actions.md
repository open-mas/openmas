# GitHub Actions for OpenMAS Testing

## Overview

This document describes how to use GitHub Actions to automate the testing and quality assurance processes for OpenMAS. GitHub Actions provides a flexible way to define workflows that can test OpenMAS across multiple protocols, reasoning engines, and deployment configurations.

## Workflow Architecture

### Primary Workflows

OpenMAS uses the following primary GitHub Actions workflows:

1. **Unit Tests**: Runs on every pull request and push to main branches
2. **Integration Tests**: Runs on every pull request and scheduled daily
3. **Protocol Matrix**: Tests across all supported protocols
4. **Reasoning Engine Matrix**: Tests with different reasoning engines
5. **Deployment Verification**: Verifies deployment across different environments
6. **Documentation Checks**: Validates documentation structure and links

### Matrix Strategy

OpenMAS CI uses matrix builds to test multiple combinations of:

- Python versions (3.9, 3.10, 3.11, 3.12)
- Protocols (A2A, MCP, HTTP, MQTT, gRPC)
- Reasoning engines (rule-based, BDI, LLM, KR&R, hybrid)
- Operating systems (Linux, macOS, Windows)

## Workflow Definitions

### Unit Test Workflow

```yaml
name: Unit Tests

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: [3.9, 3.10, 3.11, 3.12]

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
      run: tox
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Protocol Matrix Tests

```yaml
name: Protocol Matrix Tests

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'  # Run daily at midnight

jobs:
  protocol-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        protocol: [a2a, mcp, http, mqtt, grpc]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install tox
    - name: Test with protocol ${{ matrix.protocol }}
      run: tox -e protocol-${{ matrix.protocol }}
```

### Reasoning Engine Matrix

```yaml
name: Reasoning Engine Tests

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 12 * * *'  # Run daily at noon

jobs:
  reasoning-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        reasoning: [rule-based, bdi, llm, kr-symbolic, kr-graph, kr-probabilistic, hybrid]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install tox
    - name: Test with reasoning engine ${{ matrix.reasoning }}
      run: tox -e reasoning-${{ matrix.reasoning }}
```

### Documentation Checks

```yaml
name: Documentation Checks

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  doc-checks:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r doc/requirements.txt
    - name: Check links
      run: |
        cd doc
        python tools/check_links.py
    - name: Validate structure
      run: |
        cd doc
        python tools/validate_structure.py
```

## Workflow Triggers

GitHub Actions workflows for OpenMAS can be triggered by:

1. **Push Events**: When code is pushed to specific branches
2. **Pull Request Events**: When pull requests are created or updated
3. **Scheduled Events**: Regular scheduled runs (daily, weekly)
4. **Manual Events**: Manual triggering via workflow_dispatch
5. **Repository Events**: Repository-specific events like releases

## Configuration Files

GitHub Actions workflows are defined in the `.github/workflows/` directory:

```
.github/workflows/
├── unit_tests.yml
├── integration_tests.yml
├── protocol_matrix.yml
├── reasoning_matrix.yml
├── deployment_tests.yml
└── documentation_checks.yml
```

## Environment Variables and Secrets

OpenMAS CI workflows require various environment variables and secrets:

| Name | Description | Type |
|------|-------------|------|
| `OPENMAS_TEST_ENV` | Test environment (local, ci, prod) | Variable |
| `OPENMAS_PROTOCOL_CONFIG` | Protocol-specific configuration | Variable |
| `OPENMAS_REASONING_CONFIG` | Reasoning engine configuration | Variable |
| `OPENMAS_API_KEY` | API key for external services | Secret |
| `DOCKER_USERNAME` | Docker Hub username | Secret |
| `DOCKER_PASSWORD` | Docker Hub password | Secret |

## Workflow Artifacts

Each CI run produces artifacts that can be downloaded for debugging:

1. **Test Reports**: Detailed test execution reports
2. **Coverage Reports**: Code coverage reports
3. **Log Files**: Log outputs from test execution
4. **Performance Data**: Performance test metrics
5. **Built Packages**: Generated packages and distributions

## Parallelization Strategy

To improve CI performance, OpenMAS tests are parallelized by:

1. **Protocol**: Each protocol runs in parallel
2. **Reasoning Engine**: Each reasoning engine runs in parallel
3. **Test Type**: Unit, integration, and system tests run in parallel
4. **Python Version**: Tests for different Python versions run in parallel

## Custom GitHub Actions

OpenMAS defines custom actions for common CI tasks:

1. **setup-openmas**: Sets up OpenMAS development environment
2. **validate-schema**: Validates OpenMAS configuration schema
3. **check-protocol-compatibility**: Checks compatibility across protocols
4. **reasoning-engine-test**: Tests specific reasoning engine

## Related Documentation

- [Test Matrices](./test_matrices.md)
- [Tox Configuration](../framework/tox_configuration.md)
- [Test Supervisor](../framework/test_supervisor.md)
- [Deployment Pipeline](../../15_deployment/README.md)
