# Development Containers

## Overview

This document describes how to use Docker containers for OpenMAS development environments. Development containers provide consistent, portable environments that make it easier to collaborate and ensure all dependencies are properly configured, regardless of the developer's host operating system.

## Key Benefits

- **Consistency**: All developers work in identical environments
- **Isolation**: Development work doesn't affect the host system
- **Dependency Management**: All required packages are pre-installed
- **Multi-Protocol Development**: Test different protocol implementations simultaneously
- **Cross-Platform**: Works identically on Windows, macOS, and Linux

## Development Container Architecture

OpenMAS development containers are structured to support the reasoning-agnostic design of the framework:

```
┌─────────────────────────────────┐
│ Developer Workspace             │
│ (Mounted code, live reloading)  │
├─────────────────────────────────┤
│ Protocol Layer(s)               │
│ (A2A, MCP, HTTP, etc.)          │
├─────────────────────────────────┤
│ OpenMAS Framework               │
│ (Core libraries)                │
├─────────────────────────────────┤
│ Python Development Environment  │
└─────────────────────────────────┘
```

## Basic Development Container Setup

### Base Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install development tools
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    isort \
    mypy \
    pylint \
    pydocstyle

# Install OpenMAS dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Create volume mount points
VOLUME ["/app/code", "/app/data"]

# Set Python path
ENV PYTHONPATH=/app/code:$PYTHONPATH

# Default command: interactive shell
CMD ["bash"]
```

## Protocol-Specific Development Containers

For developing with specific protocols:

```dockerfile
# A2A Protocol Development Container
FROM openmas-dev-base:latest

# Install A2A protocol dependencies
RUN pip install --no-cache-dir openmas-a2a-protocol

# Set A2A-specific environment variables
ENV OPENMAS_PROTOCOL=a2a
ENV OPENMAS_A2A_DEBUG=true

# Add A2A development utilities
COPY ./tools/a2a/ /app/tools/
```

```dockerfile
# MCP Protocol Development Container
FROM openmas-dev-base:latest

# Install MCP protocol dependencies
RUN pip install --no-cache-dir openmas-mcp-protocol

# Set MCP-specific environment variables
ENV OPENMAS_PROTOCOL=mcp
ENV OPENMAS_MCP_DEBUG=true

# Add MCP development utilities
COPY ./tools/mcp/ /app/tools/
```

## Multi-Container Development with Docker Compose

For developing multi-agent systems with different protocols:

```yaml
version: '3'

services:
  dev-environment:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app/code
      - ./data:/app/data
    ports:
      - "8000:8000"  # For web interfaces
    environment:
      - OPENMAS_ENV=development
    command: bash -c "cd /app/code && python -m openmas.tools.dev_server"
    
  a2a-agent:
    build:
      context: .
      dockerfile: Dockerfile.a2a
    volumes:
      - .:/app/code
    environment:
      - OPENMAS_AGENT_ID=dev-agent-a2a
      - OPENMAS_PROTOCOL=a2a
    ports:
      - "8001:8000"
    depends_on:
      - dev-environment
      
  mcp-agent:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    volumes:
      - .:/app/code
    environment:
      - OPENMAS_AGENT_ID=dev-agent-mcp
      - OPENMAS_PROTOCOL=mcp
    ports:
      - "8002:8000"
    depends_on:
      - dev-environment
```

## VS Code Integration

### Devcontainer Configuration

Create a `.devcontainer/devcontainer.json` file:

```json
{
  "name": "OpenMAS Development",
  "dockerComposeFile": "../docker-compose.dev.yml",
  "service": "dev-environment",
  "workspaceFolder": "/app/code",
  "extensions": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "njpwerner.autodocstring"
  ],
  "settings": {
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true
  },
  "remoteUser": "root"
}
```

## Development Workflows

### Local Development

1. **Starting the Development Environment**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Accessing the Development Container**:
   ```bash
   docker exec -it openmas_dev_environment bash
   ```

3. **Running Tests**:
   ```bash
   # Inside the container
   cd /app/code
   pytest
   ```

4. **Code Formatting**:
   ```bash
   # Inside the container
   cd /app/code
   black .
   isort .
   ```

### Multi-Agent Development

1. **Starting Multiple Agents**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d a2a-agent mcp-agent
   ```

2. **Viewing Logs**:
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f
   ```

3. **Testing Inter-Agent Communication**:
   ```bash
   # Inside the dev container
   cd /app/code/tools
   python test_communication.py --agent1=a2a-agent --agent2=mcp-agent
   ```

## Hot Reloading for Development

To enable automatic code reloading during development:

```dockerfile
# Add to development container
RUN pip install --no-cache-dir watchdog

# Create reload script
COPY ./tools/hot_reload.py /app/tools/

# Use as alternative command
# docker-compose -f docker-compose.dev.yml run --rm dev-environment python /app/tools/hot_reload.py
```

## Debugging Containers

### Remote Debugging with VS Code

Add to your `launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "port": 5678,
      "host": "localhost",
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "/app/code"
        }
      ]
    }
  ]
}
```

Add to your `docker-compose.dev.yml`:

```yaml
services:
  dev-environment:
    # ... other settings
    ports:
      - "5678:5678"  # For debugging
    # Use this command to enable debugging
    command: bash -c "pip install debugpy && python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m your_module"
```

## Best Practices

1. **Mount Code as Volume**: Always mount your code directory as a volume for live editing
2. **Use .dockerignore**: Exclude unnecessary files to speed up builds
3. **Layer Dependencies**: Structure Dockerfiles to leverage caching for faster rebuilds
4. **Environment Variables**: Use environment variables for configuration
5. **Development Tools**: Include linters, formatters, and testing tools in development containers
6. **Protocol Separation**: Use different containers for different protocols to test interoperability
7. **Persistent Data Volumes**: Use volumes for persistent data across container rebuilds
8. **Consistent Tooling**: Ensure all developers use the same container configuration

## Related Documentation

- [Docker Compose Configuration](./docker_compose.md)
- [Testing Containers](./testing_containers.md)
- [Developer Workflows](../local/development_workflows.md)
- [CLI Development Tools](../../13_cli_tools/development/developer_workflows.md)
