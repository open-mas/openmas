# Declarative Capability Definition

## 1. Overview

In OpenMAS, a capability's interface is defined declaratively in the agent's YAML configuration file. This approach separates the capability's definition (the "what") from its implementation (the "how"), providing a clear, machine-readable contract that the framework can use for validation, protocol adaptation, and discovery.

## 2. Structure of a Core Capability Definition

Capabilities are defined in a list under the `multi_protocol_capabilities.core` section of an agent's configuration. Each capability definition is an object with the following key fields:

| Field | Type | Description |
|---|---|---|
| `id` | `string` | **(Required)** A unique, machine-friendly identifier for the capability. This ID is used to link the declarative definition to its programmatic handler. |
| `name` | `string` | A human-readable name for the capability. |
| `description` | `string` | A detailed explanation of what the capability does. |
| `parameters` | `object` | A JSON Schema object defining the expected input parameters for the capability. |
| `returns` | `object` | A JSON Schema object defining the structure of the value returned by the capability. |

## 3. Example Definition

Here is an example of a `get_weather` capability defined in an agent's configuration file.

```yaml
version: "0.3.0"
agents:
  - id: "weather_agent"
    name: "Weather Agent"
    class: "my_agents.weather.WeatherAgent"
    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "get_weather"
            name: "Get Weather"
            description: "Retrieves the current weather for a specified location."
            parameters:
              type: "object"
              properties:
                location:
                  type: "string"
                  description: "The city and state, e.g., 'San Francisco, CA'"
              required: ["location"]
            returns:
              type: "object"
              properties:
                temperature:
                  type: "number"
                  description: "Current temperature in Celsius."
                conditions:
                  type: "string"
                  description: "A brief description of current weather conditions (e.g., 'Clear', 'Cloudy')."
```

This declarative definition provides all the information needed for another agent (or a human) to understand and invoke this capability without needing to inspect its source code.
