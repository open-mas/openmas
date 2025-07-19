# Integration Testing

## Overview

This directory contains documentation for integration testing in OpenMAS. Integration testing focuses on verifying that different components of the OpenMAS framework work correctly together, with particular attention to communication between agents, protocol implementations, and cross-component interactions.

## Key Integration Test Areas

OpenMAS integration testing focuses on these key areas:

1. **Protocol Testing**: Testing protocol implementations and communications
2. **Async Integration**: Testing asynchronous operations and messaging
3. **Library Adapter Testing**: Testing adapters for external libraries
4. **Docker Integration**: Testing in containerized environments
5. **Multi-Agent Testing**: Testing interactions between multiple agents

## Documentation

- [Async Integration](./async_integration.md): Testing asynchronous operations
- [Protocol Testing](./protocol_testing.md): Testing protocol implementations
- [Library Adapter Testing](./library_adapter_testing.md): Testing adapters for external libraries
- [Docker Integration](./docker_integration.md): Testing in containerized environments
- [Multi-Agent Testing](./multi_agent_testing.md): Testing multi-agent interactions

## Integration Testing Principles

OpenMAS integration testing follows these key principles:

1. **Reasoning Agnosticism**: Tests maintain separation between communication testing and reasoning testing
2. **Multi-Protocol Support**: Integration tests cover all supported protocols (MCP, A2A, HTTP, MQTT, gRPC)
3. **Component Boundaries**: Tests respect component boundaries and interfaces
4. **Real-World Scenarios**: Tests simulate real-world agent interactions
5. **Comprehensive Coverage**: Tests cover both typical and edge-case scenarios

## Related Documentation

- [Testing Framework](../framework/README.md)
- [Unit Testing](../unit_testing/README.md)
- [Test Supervisor](../framework/test_supervisor.md)
- [Local Deployment](../../15_deployment/local/README.md)
