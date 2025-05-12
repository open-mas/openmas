# Communicator Configuration in OpenMAS

Communicators handle the exchange of messages between agents and other services in OpenMAS. This guide explains how to configure different communicator types.

## Available Communicator Types

OpenMAS supports several communicator types, each suited for different use cases:

- **HTTP** (`http`): The default communicator, uses JSON-RPC over HTTP
- **Model Context Protocol SSE** (`mcp-sse`): Uses the Model Context Protocol over Server-Sent Events
- **Model Context Protocol STDIO** (`mcp-stdio`): Uses the Model Context Protocol over standard input/output
- **gRPC** (`grpc`): Uses gRPC for high-performance communication
- **MQTT** (`mqtt`): Uses MQTT for message-based communication

## Configuration in openmas_project.yaml

The recommended way to configure communicators is in your `openmas_project.yaml` file:

```yaml
agents:
  my_agent:
    module: myagent
    class: MyAgent
    communicator: http  # Specify the communicator type here
    options:
      communicator_options:
        # Communicator-specific options go here
        port: 8081
```

## HTTP Communicator

The HTTP communicator is the default and requires the least setup. It's suitable for most use cases.

### Options

- `port`: The port to listen on (default: 8000)
- `timeout`: Request timeout in seconds (default: 30)

```yaml
agents:
  my_agent:
    module: myagent
    class: MyAgent
    communicator: http
    options:
      communicator_options:
        port: 8081
        timeout: 60
```

## MCP Communicators

Model Context Protocol (MCP) communicators allow integration with AI models that support MCP, like Anthropic's Claude.

### MCP SSE Communicator

The MCP SSE communicator uses Server-Sent Events for communication.

#### Required Dependencies

The MCP communicators require the `mcp` package:

```bash
pip install 'openmas[mcp]'
```

#### Options

- `server_mode`: Whether to operate in server mode (default: false)
- `server_instructions`: Instructions for the server when in server mode
- `port`: Port number when using HTTP transport (for SSE)

```yaml
agents:
  my_agent:
    module: myagent
    class: MyAgent
    communicator: mcp-sse
    options:
      communicator_options:
        server_mode: true
        server_instructions: "You are a helpful assistant."
```

### MCP STDIO Communicator

The MCP STDIO communicator uses standard input/output for communication.

#### Options

- `server_mode`: Whether to operate in server mode (default: false)
- `server_instructions`: Instructions for the server when in server mode
- `service_args`: Additional arguments for services

```yaml
agents:
  my_agent:
    module: myagent
    class: MyAgent
    communicator: mcp-stdio
    options:
      communicator_options:
        server_mode: true
        server_instructions: "You are a helpful assistant."
```

## gRPC Communicator

The gRPC communicator provides high-performance communication through Google's RPC framework.

### Required Dependencies

To use gRPC, install the required dependencies:

```bash
pip install 'openmas[grpc]'
```

### Options

- `port`: The port to listen on (default: 50051)

```yaml
agents:
  my_agent:
    module: myagent
    class: MyAgent
    communicator: grpc
    options:
      communicator_options:
        port: 50051
```

## MQTT Communicator

The MQTT communicator uses the Message Queuing Telemetry Transport protocol for lightweight messaging.

### Required Dependencies

To use MQTT, install the required dependencies:

```bash
pip install 'openmas[mqtt]'
```

### Options

- `broker_host`: MQTT broker hostname (default: "localhost")
- `broker_port`: MQTT broker port (default: 1883)
- `topic_prefix`: Prefix for MQTT topics (default: "openmas")

```yaml
agents:
  my_agent:
    module: myagent
    class: MyAgent
    communicator: mqtt
    options:
      communicator_options:
        broker_host: "mqtt.example.com"
        broker_port: 1883
        topic_prefix: "my_project"
```

## Default Configuration

You can provide default communicator configuration for all agents in your project:

```yaml
name: My Project
version: 1.0.0
communicator_defaults:
  # Default options for all communicators
  timeout: 30

agents:
  agent1:
    module: agents.agent1
    class: Agent
    communicator: http
    # This agent will use the default timeout of 30

  agent2:
    module: agents.agent2
    class: Agent
    communicator: http
    options:
      communicator_options:
        # This agent overrides the default timeout
        timeout: 60
```

## Environment Variables

You can also configure communicator options via environment variables:

```bash
# Set the communicator type
export COMMUNICATOR_TYPE=http

# Set communicator options as JSON
export COMMUNICATOR_OPTIONS='{"port": 8081, "timeout": 60}'

# Set individual communicator options
export COMMUNICATOR_OPTION_PORT=8081
export COMMUNICATOR_OPTION_TIMEOUT=60
```

## Troubleshooting

### Missing Dependencies

If you see errors about missing dependencies, make sure you've installed the required packages:

```bash
# For MCP
pip install 'openmas[mcp]'

# For gRPC
pip install 'openmas[grpc]'

# For MQTT
pip install 'openmas[mqtt]'
```

### Common Errors

- **TypeError: Connection refused**: Check that the port is correct and not already in use
- **ImportError: No module named 'mcp'**: Install the MCP package with `pip install 'openmas[mcp]'`
- **Cannot import name 'GrpcCommunicator'**: Install gRPC dependencies with `pip install 'openmas[grpc]'`

### Debugging

Set the agent's log level to DEBUG to see more information about communicator configuration:

```yaml
agents:
  my_agent:
    module: myagent
    class: MyAgent
    options:
      log_level: DEBUG
```
