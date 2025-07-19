# Protocol Command

## Overview

The `protocol` command manages protocol interfaces for OpenMAS agents. It enables configuring, adding, removing, and inspecting protocol adapters, supporting the full range of protocols defined in the unified configuration schema (MCP, A2A, HTTP, MQTT, gRPC) while maintaining OpenMAS's reasoning-agnostic architecture.

## Usage

```bash
openmas protocol [subcommand] [options]
```

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | List available protocols or protocols configured for an agent |
| `add` | Add a protocol interface to an agent |
| `remove` | Remove a protocol interface from an agent |
| `config` | Configure protocol options |
| `info` | Show detailed information about protocol configuration |
| `validate` | Validate protocol configuration |

## Options

| Option | Description |
|--------|-------------|
| `--agent`, `-a` | Agent ID to configure protocol for |
| `--type`, `-t` | Protocol type (mcp-sse, mcp-stdio, a2a-http, http, mqtt, grpc, etc.) |
| `--options`, `-o` | Protocol options (key=value format) |
| `--mode` | Protocol mode (server, client, both) |
| `--format` | Output format (yaml, json) |
| `--file`, `-f` | File to output protocol configuration |

## Supported Protocols

The `protocol` command supports all protocols defined in the unified configuration schema:

| Protocol Type | Description |
|---------------|-------------|
| `mcp-sse` | Model Context Protocol over Server-Sent Events |
| `mcp-stdio` | Model Context Protocol over Standard IO |
| `mcp-streamable` | Model Context Protocol with streaming support |
| `a2a-http` | Google Agent-to-Agent protocol over HTTP |
| `a2a-websocket` | Google Agent-to-Agent protocol over WebSockets |
| `a2a-grpc` | Google Agent-to-Agent protocol over gRPC |
| `http` | Standard HTTP protocol |
| `websocket` | WebSocket protocol |
| `mqtt` | MQTT protocol |
| `grpc` | gRPC protocol |

## Examples

### List Available Protocols

```bash
openmas protocol list
```

This lists all protocols available in the current OpenMAS installation.

### List Protocols for an Agent

```bash
openmas protocol list --agent customer-assistant
```

This lists all protocols configured for the specified agent.

### Add a Protocol to an Agent

```bash
openmas protocol add mcp customer-assistant --options server_mode=true,http_port=8000
```

This adds the MCP protocol to the specified agent with custom options.

### Configure Protocol Options

```bash
openmas protocol config a2a customer-assistant --set agent_card.name="Customer Assistant"
```

This configures the A2A protocol options for the specified agent.

### Get Protocol Information

```bash
openmas protocol info mcp customer-assistant
```

This shows detailed information about the MCP protocol configuration for the specified agent.

### Remove a Protocol from an Agent

```bash
openmas protocol remove mqtt customer-assistant
```

This removes the MQTT protocol from the specified agent.

## Protocol Configuration and the Unified Schema

The `protocol` command operates directly on the protocol sections of the unified configuration schema. For example, running:

```bash
openmas protocol add mcp customer-assistant --options server_mode=true,http_port=8000
```

Modifies the schema as follows:

```yaml
agents:
  customer-assistant:
    # Other agent configuration...
    protocols:
      - type: "mcp-sse"
        enabled: true
        options:
          server_mode: true
          http_port: 8000
          # Other default options...
```

## Protocol-Specific Configuration

Each protocol type has specific configuration options that can be set with the `protocol config` command:

### MCP Protocol Options

```bash
openmas protocol config mcp customer-assistant --set server_mode=true,stream_mode=sse,http_port=8000
```

### A2A Protocol Options

```bash
openmas protocol config a2a customer-assistant --set agent_card.name="Customer Assistant",agent_card.description="Helps customers with inquiries"
```

### HTTP Protocol Options

```bash
openmas protocol config http customer-assistant --set port=8080,timeout_ms=30000
```

## Protocol Adapter Management

The protocol command can also manage protocol adapters:

```bash
# Create a new protocol adapter
openmas protocol adapter create custom-mqtt --base mqtt

# Install a protocol adapter from a repository
openmas protocol adapter install github.com/example/custom-protocol
```

## Related Commands

- [agent](./agent.md): Manage agents
- [config](./config.md): Configure OpenMAS components
- [run](./run.md): Run agents with specific protocols
- [validate](./validate.md): Validate protocol configurations

## Related Documentation

- [Protocol Architecture](../../02_protocols/README.md)
- [A2A Protocol](../../02_protocols/a2a/README.md)
- [MCP Protocol](../../02_protocols/mcp/README.md)
- [HTTP Protocol](../../02_protocols/http/README.md)
- [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md)
