# Port Configuration in OpenMAS

When running multiple OpenMAS agents, it's important to configure ports correctly to avoid conflicts. This guide explains how to configure ports for different communicator types.

## HTTP Communicator Port Configuration

The HTTP communicator in OpenMAS uses a port to listen for incoming requests. By default, it uses port 8000, but this can lead to conflicts when running multiple agents.

### Configuration Options

Port configuration can be set in several ways, with the following precedence (highest to lowest):

1. **Constructor Parameter**: Directly passing a `port` parameter when creating the communicator
2. **Communicator Options**: In the `communicator_options` dictionary with the key `port`
3. **Service URL**: Extracted from the agent's own service URL
4. **Fallback Values**: Default values based on agent name or default port 8000

### Configuration Methods

#### In openmas_project.yaml

The recommended way to configure ports is in your `openmas_project.yaml` file:

```yaml
agents:
  my_agent:
    module: myagent
    class: MyAgent
    communicator: http
    options:
      communicator_options:
        port: 8081
```

When running multiple agents, you should assign a unique port to each:

```yaml
agents:
  agent1:
    module: agents.agent1
    class: Agent
    communicator: http
    options:
      communicator_options:
        port: 8081

  agent2:
    module: agents.agent2
    class: Agent
    communicator: http
    options:
      communicator_options:
        port: 8082
```

#### Via Environment Variables

You can also set port configuration via environment variables:

```bash
export COMMUNICATOR_OPTION_PORT=8081
```

#### In Config Files

In `config/default.yml` or `config/<env>.yml`:

```yaml
communicator_options:
  port: 8081
```

## MCP Communicator Configuration

When using Model Context Protocol (MCP) communicators, they have their own specific configuration options.

### MCP SSE Communicator

The MCP SSE communicator uses Server-Sent Events (SSE) for communication:

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

The MCP STDIO communicator communicates via standard input/output:

```yaml
agents:
  my_agent:
    module: myagent
    class: MyAgent
    communicator: mcp-stdio
    options:
      communicator_options:
        server_mode: true
```

## Troubleshooting

If you see errors like "Address already in use", it means there's a port conflict. This can happen when:

1. You're running multiple agents without specifying unique ports
2. Another application is already using the port
3. A previous instance of your agent is still running

### Solutions

1. **Specify Unique Ports**: Always specify a unique port for each agent
2. **Check Running Processes**: Use `lsof -i :<port>` (Unix/Mac) or `netstat -ano | findstr :<port>` (Windows) to see what's using a port
3. **Use Higher Port Numbers**: Ports above 1024 are less likely to be reserved by the system
4. **Enable Debug Logging**: Set the agent's log level to DEBUG to see more information about port configuration
