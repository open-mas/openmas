# Unit Testing

## Overview

This directory contains documentation for unit testing OpenMAS components. Unit testing is essential to ensure that individual components function correctly while maintaining OpenMAS's reasoning-agnostic architecture and multi-protocol support.

## Contents

- [Test Patterns](./test_patterns.md) - Common patterns for unit testing OpenMAS components
- [Protocol-Specific Unit Tests](./protocol_specific_unit_tests.md) - Guidelines for testing protocol-specific functionality

## Key Unit Testing Principles

OpenMAS unit tests follow these key principles:

1. **Body-Brain Separation**: Tests maintain the separation between communication infrastructure ("body") and reasoning engines ("brain")
2. **Protocol Independence**: Core functionality is tested independently of specific protocols
3. **Isolation**: Components are tested in isolation with dependencies properly mocked
4. **Component Coverage**: All components have comprehensive unit test coverage
5. **Boundary Testing**: Tests cover edge cases and boundary conditions
6. **Configuration Testing**: Tests validate component behavior with different configurations

## Test Organization

Unit tests are organized by component:

```
tests/unit/
├── agents/         # Agent component tests
├── protocols/      # Protocol adapter tests
│   ├── a2a/        # A2A protocol tests
│   ├── mcp/        # MCP protocol tests
│   ├── http/       # HTTP protocol tests
│   ├── mqtt/       # MQTT protocol tests
│   └── grpc/       # gRPC protocol tests
├── reasoning/      # Reasoning engine tests
│   ├── rule_based/ # Rule-based reasoning tests
│   ├── bdi/        # BDI reasoning tests
│   ├── llm/        # LLM-based reasoning tests
│   └── kr/         # Knowledge representation tests
├── extensions/     # Extension mechanism tests
├── configuration/  # Configuration system tests
└── core/           # Core utilities and common code tests
```

## Related Documentation

- [Test Patterns](./test_patterns.md)
- [Protocol-Specific Unit Tests](./protocol_specific_unit_tests.md)
- [Test Framework](../framework/README.md)
- [Integration Testing](../integration_testing/README.md)
- [Testing Tools](../testing_tools/README.md)
