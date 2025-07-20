# Testing Containers

## Overview

This document describes how to use Docker containers for testing OpenMAS components and multi-agent systems. Containerized testing provides consistent, isolated environments that help ensure test reproducibility across different development environments.

## Key Benefits

- **Isolation**: Each test runs in a clean, isolated environment
- **Reproducibility**: Tests run in identical environments regardless of host configuration
- **Parallelization**: Multiple containers can run tests simultaneously
- **Cross-protocol testing**: Test agents using different protocol implementations
- **Resource control**: Limit CPU and memory for performance testing

## Container Testing Architecture

OpenMAS testing containers follow a layered approach:

```
┌─────────────────────────────────┐
│ Test-Specific Container         │
│ (Contains test code and fixtures)│
├─────────────────────────────────┤
│ Protocol-Specific Layer         │
│ (A2A, MCP, HTTP, etc.)          │
├─────────────────────────────────┤
│ Base OpenMAS Layer              │
│ (Core framework)                │
├─────────────────────────────────┤
│ Python Runtime                  │
└─────────────────────────────────┘
```

## Docker Integration Testing

### Prerequisites

- Docker installed on your system
- Docker Compose for multi-container tests
- OpenMAS project with tests directory

### Basic Test Container Setup

The base Dockerfile for OpenMAS testing:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy OpenMAS code
COPY . .

# Install OpenMAS in development mode
RUN pip install -e .

# Run tests by default
CMD ["pytest", "-xvs", "tests/"]
```

### Protocol-Specific Test Containers

For protocol-specific testing, extend the base container:

```dockerfile
# A2A Protocol Test Container
FROM openmas-base:latest

# Install A2A-specific dependencies
RUN pip install --no-cache-dir openmas-a2a-protocol

# Set environment for A2A
ENV OPENMAS_PROTOCOL=a2a

# Use A2A-specific test directory
CMD ["pytest", "-xvs", "tests/protocols/a2a/"]
```

```dockerfile
# MCP Protocol Test Container
FROM openmas-base:latest

# Install MCP-specific dependencies
RUN pip install --no-cache-dir openmas-mcp-protocol

# Set environment for MCP
ENV OPENMAS_PROTOCOL=mcp

# Use MCP-specific test directory
CMD ["pytest", "-xvs", "tests/protocols/mcp/"]
```

### Multi-Container Testing with Docker Compose

For testing multi-agent systems, use Docker Compose:

```yaml
version: '3'

services:
  agent1:
    build:
      context: .
      dockerfile: Dockerfile.agent
    environment:
      - OPENMAS_AGENT_ID=agent1
      - OPENMAS_PROTOCOL=a2a
    volumes:
      - ./tests:/app/tests
    networks:
      - test-network

  agent2:
    build:
      context: .
      dockerfile: Dockerfile.agent
    environment:
      - OPENMAS_AGENT_ID=agent2
      - OPENMAS_PROTOCOL=mcp
    volumes:
      - ./tests:/app/tests
    networks:
      - test-network

  test-supervisor:
    build:
      context: .
      dockerfile: Dockerfile.supervisor
    depends_on:
      - agent1
      - agent2
    volumes:
      - ./tests:/app/tests
    networks:
      - test-network
    command: ["pytest", "-xvs", "tests/integration/multi_agent/"]

networks:
  test-network:
    driver: bridge
```

## Test Supervisor Container

The test supervisor manages multi-agent testing:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy test supervisor code
COPY . .

# Install OpenMAS in development mode
RUN pip install -e .

# Run test supervisor by default
CMD ["python", "-m", "openmas.testing.supervisor"]
```

## Running Container Tests

### Single Container Test

```bash
# Build the test container
docker build -t openmas-test .

# Run tests
docker run --rm openmas-test
```

### Multi-Container Tests

```bash
# Run with Docker Compose
docker-compose -f docker-compose.test.yml up --build

# Run specific test suite
docker-compose -f docker-compose.test.yml run test-supervisor pytest -xvs tests/integration/specific_test.py
```

## Best Practices

1. **Ephemeral Containers**: Ensure containers are ephemeral with no state persistence between test runs
2. **Volume Mounting**: Mount test directories as volumes for faster iteration during development
3. **Tagging Containers**: Use meaningful tags to distinguish between test containers
4. **Environment Variables**: Use environment variables for configuration rather than hardcoded values
5. **Logging**: Configure appropriate logging levels in test containers
6. **Resource Limits**: Set resource limits to simulate production constraints
7. **Networking**: Use Docker networks to isolate test communication
8. **Cross-Protocol Testing**: Test interaction between agents using different protocols

## Integration with CI/CD

Docker test containers integrate seamlessly with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: OpenMAS Docker Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1

      - name: Build and run tests
        run: |
          docker-compose -f docker-compose.test.yml up --build --exit-code-from test-supervisor
```

## Related Documentation

- [Docker Integration in OpenMAS](../containerization/docker_compose.md)
- [Test Supervisor](../../16_testing/framework/test_supervisor.md)
- [Multi-Agent Testing](../../16_testing/integration_testing/multi_agent_testing.md)
