# CI/CD Integration for OpenMAS Testing

## Overview

This directory contains documentation for integrating OpenMAS testing with Continuous Integration and Continuous Deployment (CI/CD) pipelines. Proper CI/CD integration is essential for maintaining code quality and ensuring that OpenMAS components work correctly across all supported protocols and reasoning engines.

## Contents

- [GitHub Actions](./github_actions.md) - Using GitHub Actions for OpenMAS CI/CD
- [Test Matrices](./test_matrices.md) - Defining comprehensive test matrices for protocol and reasoning engine combinations

## Key Principles

OpenMAS CI/CD integration follows these key principles:

1. **Protocol Agnosticism**: Tests should run across all supported protocols (A2A, MCP, HTTP, MQTT, gRPC)
2. **Reasoning Engine Independence**: Tests should validate the separation between communication infrastructure and reasoning engines
3. **Comprehensive Coverage**: Test matrices should cover all supported protocol and reasoning engine combinations
4. **Fast Feedback**: Pipeline design should prioritize fast feedback on critical functionality
5. **Artifact Management**: Generated test artifacts should be preserved for debugging and analysis

## Related Documentation

- [Testing Framework](../framework/README.md)
- [Integration Testing](../integration_testing/README.md)
- [Unit Testing](../unit_testing/README.md)
- [Deployment Pipeline](../../15_deployment/README.md)
