# Tox Configuration

## Overview

This document describes the Tox configuration used in OpenMAS to ensure consistent testing across multiple Python environments. Tox is a command-line driven testing tool that manages virtual environments and runs tests across different Python versions and configurations.

## Basic Configuration

The OpenMAS Tox configuration is defined in `tox.ini` at the project root:

```ini
[tox]
envlist = py39, py310, py311, lint, typecheck, docs
isolated_build = True
requires =
    tox>=4.0.0
    virtualenv>=20.0.0

[testenv]
deps =
    pytest>=7.0.0
    pytest-asyncio>=0.18.0
    pytest-cov>=2.12.0
    pytest-mock>=3.6.0
    pytest-timeout>=2.0.0
commands =
    pytest {posargs:tests} --cov=openmas --cov-report=term-missing

[testenv:lint]
deps =
    flake8>=4.0.0
    black>=22.0.0
    isort>=5.10.0
commands =
    flake8 openmas
    black --check openmas
    isort --check-only --profile black openmas

[testenv:typecheck]
deps =
    mypy>=0.9.0
    types-PyYAML
    types-requests
commands =
    mypy openmas

[testenv:docs]
deps =
    sphinx>=4.0.0
    sphinx-rtd-theme>=1.0.0
    myst-parser>=0.15.0
commands =
    sphinx-build -b html docs/source docs/build/html
```

This configuration provides:

- Testing across multiple Python versions (3.9, 3.10, 3.11)
- Code linting and style checking
- Type checking with mypy
- Documentation building

## Environment Matrix

OpenMAS uses a testing matrix across multiple dimensions:

### Python Versions

```ini
[tox]
envlist = py39, py310, py311
```

This ensures compatibility across Python 3.9, 3.10, and 3.11.

### Protocol Testing

```ini
[testenv:protocols]
commands =
    pytest {posargs:tests/unit/protocols} --cov=openmas.protocols --cov-report=term-missing
```

This tests all protocol implementations (MCP, A2A, HTTP, MQTT, gRPC).

### Reasoning Testing

```ini
[testenv:reasoning]
commands =
    pytest {posargs:tests/unit/reasoning} --cov=openmas.reasoning --cov-report=term-missing
```

This tests all reasoning approaches (rule-based, BDI, LLM-based, hybrid), maintaining OpenMAS's reasoning agnosticism.

## Advanced Configuration

### Test Markers

```ini
[pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    system: System tests
    performance: Performance tests
    protocol: Protocol-specific tests
    reasoning: Reasoning-specific tests
    slow: Tests that take more than 1 second to run
```

These markers allow for selective test execution:

```bash
# Run only unit tests
tox -- -m unit

# Run only integration tests
tox -- -m integration

# Run tests for specific protocols
tox -- -m "protocol and mcp"
```

### Environment Variables

```ini
[testenv]
setenv =
    OPENMAS_TEST_MODE = 1
    PYTHONPATH = {toxinidir}
    PROTOCOL_TEST_MODE = memory
passenv =
    OPENMAS_*
    PYTEST_*
```

This sets necessary environment variables for testing.

### Custom Test Commands

```ini
[testenv:coverage]
commands =
    pytest {posargs:tests} --cov=openmas --cov-report=xml:coverage.xml --cov-report=html:coverage_html

[testenv:benchmarks]
commands =
    pytest {posargs:tests/performance} --benchmark-only

[testenv:security]
deps =
    {[testenv]deps}
    bandit>=1.7.0
commands =
    bandit -r openmas
```

These commands support specialized testing needs:

- Comprehensive coverage reporting
- Performance benchmarking
- Security scanning

## CI/CD Integration

The Tox configuration integrates with CI/CD pipelines:

```ini
[testenv:ci]
deps =
    {[testenv]deps}
    {[testenv:lint]deps}
    {[testenv:typecheck]deps}
commands =
    {[testenv]commands}
    {[testenv:lint]commands}
    {[testenv:typecheck]commands}
```

This enables comprehensive testing in CI environments.

## Docker Integration

For containerized testing:

```ini
[testenv:docker]
deps =
    {[testenv]deps}
    docker>=5.0.0
commands =
    pytest {posargs:tests/integration/docker_integration}
```

This tests OpenMAS in Docker containers.

## Parallel Testing

For faster test execution:

```ini
[testenv:parallel]
deps =
    {[testenv]deps}
    pytest-xdist>=2.5.0
commands =
    pytest {posargs:tests} -n auto --cov=openmas --cov-report=term-missing
```

This distributes tests across available CPU cores.

## Example Usage

### Basic Testing

```bash
# Run all tests in all environments
tox

# Run tests in Python 3.9 only
tox -e py39

# Run just the unit tests
tox -- -m unit

# Run just the protocol tests
tox -- tests/unit/protocols
```

### Advanced Testing

```bash
# Run integration tests with coverage report
tox -e integration

# Run protocol tests with xdist for parallel execution
tox -e parallel -- tests/unit/protocols

# Run tests with longer timeout
tox -- --timeout=300

# Run tests with specific markers and exclude slow tests
tox -- -m "unit and not slow"
```

## Directory-Specific Configurations

### Protocol-Specific Testing

```ini
[testenv:mcp]
commands =
    pytest {posargs:tests/unit/protocols/mcp} --cov=openmas.protocols.mcp

[testenv:a2a]
commands =
    pytest {posargs:tests/unit/protocols/a2a} --cov=openmas.protocols.a2a

[testenv:http]
commands =
    pytest {posargs:tests/unit/protocols/http} --cov=openmas.protocols.http
```

### Reasoning-Specific Testing

```ini
[testenv:llm_reasoning]
commands =
    pytest {posargs:tests/unit/reasoning/llm} --cov=openmas.reasoning.llm

[testenv:rule_reasoning]
commands =
    pytest {posargs:tests/unit/reasoning/rule_based} --cov=openmas.reasoning.rule_based

[testenv:bdi_reasoning]
commands =
    pytest {posargs:tests/unit/reasoning/bdi} --cov=openmas.reasoning.bdi
```

## Best Practices

1. **Keep Dependencies Updated**: Regularly update test dependencies
2. **Pin Version Ranges**: Use `>=` to specify minimum versions
3. **Test Matrix Coverage**: Ensure good coverage across Python versions
4. **Isolation**: Keep test environments isolated
5. **Deterministic Tests**: Ensure tests are deterministic and repeatable
6. **Resource Cleanup**: Clean up all resources after tests
7. **CI Integration**: Ensure Tox configuration works with CI systems
8. **Protocol Independence**: Test all supported protocols
9. **Reasoning Agnosticism**: Test all reasoning approaches
10. **Coverage Goals**: Strive for high test coverage

## Related Documentation

- [Directory Structure](./directory_structure.md)
- [Test Supervisor](./test_supervisor.md)
- [Fixtures](./fixtures.md)
- [CI/CD](../ci_cd/README.md)
