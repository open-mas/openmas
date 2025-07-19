# Communicator Configuration

This guide explains how to configure communicators in OpenMAS, including port configuration and communicator type selection.

## Communicator Type Selection

You can specify which communicator type to use for an agent in several ways:

1. **Agent-specific configuration in `openmas_project.yml`**:
   ```yaml
   agents:
     my_agent:
       module: agents.my_agent
       class: Agent
       communicator: mcp-sse  # Use MCP/SSE communicator
       options:
         communicator_options:
           server_mode: true
           http_port: 9900  # Custom port
   ```

2. **Environment-specific configuration** (in `config/[env_name].yml`):
   ```yaml
   communicator_type: mcp-sse
   communicator_options:
     server_mode: true
     http_port: 8888
   ```

3. **Default configuration** (in `openmas_project.yml`):
   ```yaml
   default_config:
     communicator_type: http
     communicator_options:
       port: 8000
   ```

4. **Command-line override**:
   ```bash
   # Using "openmas run" CLI
   openmas run my_agent --communicator mcp-sse
   ```

## Port Configuration

### HTTP Communicator

For the HTTP communicator, the port can be specified using the `port` parameter:

```yaml
communicator_options:
  port: 8765
```

### MCP/SSE Communicator

For the MCP/SSE communicator, you can specify the port using the `http_port` parameter:

```yaml
communicator_options:
  http_port: 9900
```

## Project-Wide Communicator Defaults

You can set default communicator settings for all agents in your project using the `communicator_defaults` field in `openmas_project.yml`. This is useful when you want multiple agents to use the same communicator type or share common configuration.

```yaml
# In openmas_project.yml
communicator_defaults:
  type: mcp-sse  # Default communicator type for all agents
  options:
    server_mode: true
    http_port: 8000  # Default port
    http_host: "127.0.0.1"  # All communicator options go inside 'options'
```

The `communicator_defaults` structure:
- `type`: Sets the default `communicator_type` for all agents
- `options`: A dictionary of options to be merged into each agent's `communicator_options`

Agent-specific `communicator` and `communicator_options` settings will override these defaults.

## Configuration Precedence

When multiple sources define the same configuration parameter, they are applied in the following order of precedence (highest to lowest):

1. Command-line arguments
2. Agent-specific configuration
3. Environment-specific configuration
4. Default configuration

This means that settings in agent-specific configuration will override the same settings in environment-specific configuration or default configuration.

## Available Communicator Types

OpenMAS provides the following built-in communicator types:

| Type | Description | Typical Use Case |
|------|-------------|------------------|
| `http` | Standard HTTP-based communicator | Default for most use cases |
| `mcp-sse` | MCP protocol over HTTP with SSE | For connecting to MCP-capable AI systems |
| `mcp-stdio` | MCP protocol over standard I/O | For MCP integration in CLI tools |
| `grpc` | gRPC-based communication | For high-performance microservices |
| `mqtt` | MQTT-based communication | For IoT and distributed messaging |

## Troubleshooting

### Common Issues

1. **Communicator type not found**:
   - Make sure you have installed the required dependencies for the communicator type
   - For MCP communicators, install with `pip install openmas[mcp]`

2. **Port conflict**:
   - If you see an error about the port being in use, try specifying a different port in your configuration
   - Check if another process is already using the port

3. **MCP/SSE configuration ignored**:
   - If your MCP/SSE agent falls back to HTTP, check your PYTHONPATH and ensure MCP is installed
   - Verify your `openmas_project.yml` has the correct structure as shown above
