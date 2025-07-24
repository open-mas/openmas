# Protocol Adaptation for Capabilities

## 1. Overview

A core design goal of the OpenMAS capability system is to separate an agent's intrinsic abilities from the specific protocols used to communicate them. Protocol adaptation is the mechanism that achieves this. It allows a single core capability to be exposed automatically over multiple protocols, each with its own naming conventions and data structures.

This is configured through the `protocol_mapping` section in the agent's YAML configuration.

## 2. The `protocol_mapping` Configuration

The `protocol_mapping` object, located under `multi_protocol_capabilities`, defines how core capabilities are mapped to their protocol-specific representations.

- The keys of this object are protocol identifiers (e.g., `a2a`, `mcp`).
- The value for each protocol is another object where:
    - Keys are the `id` of a core capability.
    - Values are the desired name for that capability within that specific protocol.

### Example `protocol_mapping`

Consider a `get_weather` core capability. We might want to expose it as `get_weather` in the A2A protocol but as `weather_tool` in the MCP protocol.

```yaml
capabilities:
  multi_protocol_capabilities:
    core:
      - id: "get_weather"
        name: "Get Weather"
        # ... other schema details

    protocol_mapping:
      a2a:
        get_weather: "get_weather"  # Expose as 'get_weather' in A2A
      mcp:
        get_weather: "weather_tool" # Expose as 'weather_tool' in MCP
```

## 3. Automatic Protocol Translation

The OpenMAS framework uses this mapping to automatically generate the correct protocol-specific advertisements and handle incoming requests.

### A2A Protocol Adaptation

For the Google A2A protocol, the framework will generate an agent card where the capability `name` is taken from the `protocol_mapping`. The parameter and return schemas are taken directly from the core capability definition.

**Generated A2A Agent Card (Snippet):**

```json
{
  "name": "weather_agent",
  "capabilities": [
    {
      "name": "get_weather", // Name from the a2a mapping
      "description": "Retrieves the current weather for a specified location.",
      "parameters": { /* ...schema... */ },
      "returns": { /* ...schema... */ }
    }
  ]
}
```

### MCP Protocol Adaptation

Similarly, for the Model Context Protocol (MCP), the framework will generate a `tools` definition. The tool `name` is taken from the `mcp` mapping.

**Generated MCP Tool Definition (Snippet):**

```json
{
  "tools": [
    {
      "name": "weather_tool", // Name from the mcp mapping
      "description": "Retrieves the current weather for a specified location.",
      "parameters": { /* ...schema... */ },
      "returns": { /* ...schema... */ }
    }
  ]
}
```

This powerful feature allows developers to define a capability's logic once and have it seamlessly integrate with multiple communication standards, future-proofing the agent's abilities.
