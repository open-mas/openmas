# Test Matrices for OpenMAS

## Overview

This document defines the test matrices used in OpenMAS CI/CD pipelines. Test matrices ensure comprehensive coverage across protocols, reasoning engines, and other dimensions important to OpenMAS's reasoning-agnostic, multi-protocol architecture.

## Core Test Dimensions

OpenMAS test matrices cover the following key dimensions:

1. **Protocols**: A2A, MCP, HTTP, MQTT, gRPC
2. **Reasoning Engines**: Rule-based, BDI, LLM, KR&R (symbolic, graph, probabilistic), Hybrid
3. **Python Versions**: 3.9, 3.10, 3.11, 3.12
4. **Operating Systems**: Linux, macOS, Windows
5. **Deployment Environments**: Local, Container, Kubernetes, Cloud (AWS, Azure, GCP)

## Protocol-Reasoning Matrix

The Protocol-Reasoning Matrix ensures that all protocol adapters work correctly with all reasoning engines, validating OpenMAS's reasoning-agnostic architecture:

| Protocol | Rule-based | BDI | LLM | KR-Symbolic | KR-Graph | KR-Probabilistic | Hybrid |
|----------|------------|-----|-----|-------------|----------|-----------------|--------|
| A2A      | ✓          | ✓   | ✓   | ✓           | ✓        | ✓               | ✓      |
| MCP      | ✓          | ✓   | ✓   | ✓           | ✓        | ✓               | ✓      |
| HTTP     | ✓          | ✓   | ✓   | ✓           | ✓        | ✓               | ✓      |
| MQTT     | ✓          | ✓   | ✓   | ✓           | ✓        | ✓               | ✓      |
| gRPC     | ✓          | ✓   | ✓   | ✓           | ✓        | ✓               | ✓      |

## Test Types Matrix

The Test Types Matrix defines what types of tests are run for each component:

| Component | Unit | Integration | E2E | Performance | Security |
|-----------|------|------------|-----|-------------|----------|
| Agents    | ✓    | ✓          | ✓   | ✓           | ✓        |
| Protocols | ✓    | ✓          | ✓   | ✓           | ✓        |
| Reasoning | ✓    | ✓          | ✓   | ✓           | ✓        |
| Extensions| ✓    | ✓          | ✓   | ✓           | ✓        |
| CLI Tools | ✓    | ✓          | ✓   | -           | ✓        |

## Deployment Environment Matrix

The Deployment Environment Matrix ensures OpenMAS works correctly across different deployment scenarios:

| Protocol | Local | Docker | Kubernetes | AWS | Azure | GCP |
|----------|-------|--------|------------|-----|-------|-----|
| A2A      | ✓     | ✓      | ✓          | ✓   | ✓     | ✓   |
| MCP      | ✓     | ✓      | ✓          | ✓   | ✓     | ✓   |
| HTTP     | ✓     | ✓      | ✓          | ✓   | ✓     | ✓   |
| MQTT     | ✓     | ✓      | ✓          | ✓   | ✓     | ✓   |
| gRPC     | ✓     | ✓      | ✓          | ✓   | ✓     | ✓   |

## Multi-Agent Communication Matrix

The Multi-Agent Communication Matrix tests communication patterns between different agent types:

| Sender \ Receiver | Rule-based | BDI | LLM | KR&R | Hybrid |
|-------------------|------------|-----|-----|------|--------|
| Rule-based        | ✓          | ✓   | ✓   | ✓    | ✓      |
| BDI               | ✓          | ✓   | ✓   | ✓    | ✓      |
| LLM               | ✓          | ✓   | ✓   | ✓    | ✓      |
| KR&R              | ✓          | ✓   | ✓   | ✓    | ✓      |
| Hybrid            | ✓          | ✓   | ✓   | ✓    | ✓      |

## Capability Testing Matrix

The Capability Testing Matrix ensures that all agent capabilities work across protocols:

| Capability | A2A | MCP | HTTP | MQTT | gRPC |
|------------|-----|-----|------|------|------|
| Text Generation | ✓   | ✓   | ✓    | ✓    | ✓    |
| Image Analysis  | ✓   | ✓   | ✓    | ✓    | ✓    |
| Knowledge Query | ✓   | ✓   | ✓    | ✓    | ✓    |
| Task Planning   | ✓   | ✓   | ✓    | ✓    | ✓    |
| Multi-Agent Coordination | ✓ | ✓ | ✓  | ✓   | ✓   |

## Configuration Schema Matrix

The Configuration Schema Matrix validates schema compatibility across components:

| Component | Basic Schema | Extended Schema | Full Schema |
|-----------|--------------|----------------|-------------|
| Agents    | ✓            | ✓              | ✓           |
| Protocols | ✓            | ✓              | ✓           |
| Reasoning | ✓            | ✓              | ✓           |
| Extensions| ✓            | ✓              | ✓           |
| Security  | ✓            | ✓              | ✓           |
| Observability | ✓        | ✓              | ✓           |

## Implementation Strategy

### Matrix Execution

Test matrices are executed using a combination of:

1. **GitHub Actions Matrix Strategy**: Primary execution method using matrix jobs
2. **Tox Environments**: Define test environments according to the matrix dimensions
3. **Parametrized Tests**: Use pytest parametrization for fine-grained test combinations

### Configuration

Matrix test configuration is defined in:

```
.github/workflows/matrix_config.yml
tox.ini
tests/conftest.py
```

### Matrix Prioritization

Not all matrix combinations are executed on every CI run due to resource constraints. The prioritization strategy is:

1. **Smoke Tests**: Basic tests across all dimensions
2. **Critical Path Tests**: Full matrix for critical components
3. **Daily Full Matrix**: Complete matrix execution daily
4. **Weekly Extensive Tests**: Performance and stress testing weekly

## Test Report Aggregation

Results from matrix tests are aggregated into:

1. **Summary Report**: Overall pass/fail status
2. **Dimension Report**: Status per dimension (protocol, reasoning engine, etc.)
3. **Compatibility Matrix**: Visual representation of compatibility
4. **Regression Analysis**: Comparison with previous runs

## Best Practices

1. **Parameterize Tests**: Write tests that can run against different protocols and reasoning engines
2. **Use Common Test Fixtures**: Share fixtures across test modules
3. **Isolate Protocol-Specific Logic**: Keep protocol-specific test code separate
4. **Tag Tests by Dimension**: Use markers to identify which dimension a test belongs to
5. **Test Protocol Adapters Separately**: Validate adapters before testing full integration

## Related Documentation

- [GitHub Actions](./github_actions.md)
- [Tox Configuration](../framework/tox_configuration.md)
- [Test Framework](../framework/README.md)
- [Integration Testing](../integration_testing/README.md)
- [Multi-Agent Testing](../integration_testing/multi_agent_testing.md)
