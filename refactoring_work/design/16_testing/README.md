# OpenMAS Testing Documentation

This directory contains comprehensive documentation for testing OpenMAS agents and systems at various levels, from unit testing to integration and performance testing.

## Directory Structure

- **[framework/](./framework/)**: Testing framework and setup
- **[unit_testing/](./unit_testing/)**: Unit testing guidelines
- **[integration_testing/](./integration_testing/)**: Integration testing approaches
- **[performance_testing/](./performance_testing/)**: Performance testing methodologies
- **[security_testing/](./security_testing/)**: Security testing guidelines
- **[ci_cd/](./ci_cd/)**: Continuous Integration and Continuous Deployment
- **[testing_tools/](./testing_tools/)**: Testing utilities and tools

## Key Testing Principles

OpenMAS testing follows these key principles:

1. **Reasoning Agnosticism**: Test frameworks maintain separation between communication testing and reasoning testing
2. **Multi-Protocol Testing**: Tests accommodate various communication protocols (A2A, MCP, HTTP, MQTT, gRPC)
3. **Test-Driven Development**: Comprehensive test coverage guides the development process
4. **Component-Based Testing**: Tests respect clear component boundaries
5. **Protocol-Specific Testing**: Dedicated tests for each protocol's specific behaviors

## Related Documentation

- [Architecture Overview](/01_architecture/architecture_overview.md)
- [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md)
- [Deployment Documentation](/15_deployment/)
- [CLI Tools](/13_cli_tools/)
