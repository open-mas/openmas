# Testing Framework Directory Structure

## Overview

This document defines the standardized directory structure for tests in the OpenMAS framework. A consistent test organization ensures tests are discoverable, maintainable, and follow a clear pattern that aligns with OpenMAS's reasoning-agnostic and multi-protocol design principles.

## Root Test Directory

The root test directory is organized as follows:

```
tests/
├── conftest.py              # Shared test fixtures and configuration
├── README.md                # Testing overview and guidelines
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── system/                  # System tests
├── performance/             # Performance tests
└── fixtures/                # Shared test fixtures
```

## Unit Tests

Unit tests are organized by component and follow the package structure:

```
tests/unit/
├── conftest.py              # Unit test fixtures
├── agents/                  # Tests for agent components
│   ├── test_agent.py
│   ├── test_capabilities.py
│   └── test_lifecycle.py
├── protocols/               # Tests for protocol components
│   ├── test_mcp.py
│   ├── test_a2a.py
│   ├── test_http.py
│   └── test_mqtt.py
├── reasoning/               # Tests for reasoning components
│   ├── test_llm_reasoning.py
│   ├── test_rule_reasoning.py
│   └── test_hybrid_reasoning.py
├── configuration/           # Tests for configuration components
│   ├── test_schema.py
│   ├── test_validation.py
│   └── test_environment.py
└── extensions/              # Tests for extension components
    ├── test_plugin.py
    └── test_extension_manager.py
```

## Integration Tests

Integration tests focus on interactions between components:

```
tests/integration/
├── conftest.py              # Integration test fixtures
├── protocol_integration/    # Protocol integration tests
│   ├── test_mcp_http.py
│   ├── test_a2a_http.py
│   ├── test_mqtt_protocol.py
│   └── test_protocol_interop.py
├── agent_integration/       # Agent integration tests
│   ├── test_multi_agent.py
│   ├── test_agent_communication.py
│   └── test_capabilities_integration.py
├── reasoning_integration/   # Reasoning integration tests
│   ├── test_reasoning_agent.py
│   └── test_knowledge_reasoning.py
├── async_integration/       # Asynchronous integration tests
│   ├── test_async_messaging.py
│   └── test_concurrent_agents.py
└── docker_integration/      # Docker-based integration tests
    ├── test_containerized_agents.py
    └── test_distributed_system.py
```

## System Tests

System tests evaluate the complete OpenMAS system:

```
tests/system/
├── conftest.py              # System test fixtures
├── multi_agent_system/      # Multi-agent system tests
│   ├── test_full_system.py
│   ├── test_system_lifecycle.py
│   └── test_system_recovery.py
├── end_to_end/              # End-to-end workflow tests
│   ├── test_assistant_workflow.py
│   ├── test_multi_reasoning.py
│   └── test_protocol_switching.py
└── deployment/              # Deployment tests
    ├── test_local_deployment.py
    ├── test_container_deployment.py
    └── test_distributed_deployment.py
```

## Performance Tests

Performance tests measure system characteristics:

```
tests/performance/
├── conftest.py              # Performance test fixtures
├── benchmarks/              # Standard benchmarks
│   ├── test_messaging_throughput.py
│   ├── test_reasoning_latency.py
│   └── test_multi_agent_scaling.py
├── load/                    # Load testing
│   ├── test_concurrent_users.py
│   └── test_message_volume.py
└── profiling/               # Profiling tests
    ├── test_memory_usage.py
    └── test_cpu_usage.py
```

## Test Fixtures

Shared test fixtures are collected in a dedicated directory:

```
tests/fixtures/
├── agent_fixtures.py        # Agent test fixtures
├── protocol_fixtures.py     # Protocol test fixtures
├── reasoning_fixtures.py    # Reasoning test fixtures
├── configuration_fixtures.py # Configuration test fixtures
└── system_fixtures.py       # System test fixtures
```

## Test Configuration

Global configuration for tests:

```
tests/
├── conftest.py              # pytest configuration
├── pyproject.toml           # Test configuration
└── tox.ini                  # Tox multi-environment testing
```

## Test Resources

Test resources and test data:

```
tests/resources/
├── configurations/          # Test configurations
│   ├── agents/
│   ├── protocols/
│   └── systems/
├── data/                    # Test data
│   ├── messages/
│   ├── knowledge/
│   └── prompts/
└── mocks/                   # Mock resources
    ├── services/
    └── responses/
```

## Protocol-Specific Tests

For each supported protocol, dedicated tests exist:

```
tests/unit/protocols/mcp/    # MCP protocol tests
tests/unit/protocols/a2a/    # A2A protocol tests
tests/unit/protocols/http/   # HTTP protocol tests
tests/unit/protocols/mqtt/   # MQTT protocol tests
tests/unit/protocols/grpc/   # gRPC protocol tests
```

## Reasoning-Agnostic Testing

In line with OpenMAS's reasoning-agnostic design, tests are structured to accommodate different reasoning approaches:

```
tests/unit/reasoning/rule/   # Rule-based reasoning tests
tests/unit/reasoning/bdi/    # BDI reasoning tests
tests/unit/reasoning/kr/     # Knowledge representation tests
tests/unit/reasoning/llm/    # LLM-based reasoning tests
tests/unit/reasoning/hybrid/ # Hybrid reasoning tests
```

## Automatic Test Discovery

Tests are automatically discovered by pytest according to these conventions:

1. Test files must start with `test_`
2. Test functions must start with `test_`
3. Test classes must start with `Test`

## Conventions

### Test File Naming

Test files are named according to the component they test:

- `test_<component>.py` for component tests
- `test_<component1>_<component2>.py` for integration tests

### Test Function Naming

Test functions follow a clear naming pattern:

- `test_<function>_<scenario>_<expected_outcome>()`

Example:
```python
def test_agent_initialization_with_valid_config_succeeds():
    # Test implementation
```

### Test Organization

Each test file is organized into these sections:

1. Imports
2. Constants and configurations
3. Fixtures (if not in conftest.py)
4. Helper functions
5. Test functions or classes

## Related Documentation

- [Test Supervisor](./test_supervisor.md)
- [Fixtures](./fixtures.md)
- [Tox Configuration](./tox_configuration.md)
- [Unit Testing](../unit_testing/README.md)
- [Integration Testing](../integration_testing/README.md)
