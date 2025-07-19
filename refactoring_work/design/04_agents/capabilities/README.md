# Agent Capabilities

## Overview

This document describes the capability system in OpenMAS, which provides a standardized way for agents to define, advertise, and invoke their capabilities across different protocols while maintaining OpenMAS's core principle of reasoning agnosticism.

## The Two-Part Capability System

OpenMAS follows a two-part approach to capability definition and implementation:

1. **Declarative Definition (YAML Configuration)**: Capabilities are first declared in the agent's YAML configuration under the `multi_protocol_capabilities` section. This defines the capability's metadata, schemas, and protocol mappings.

2. **Programmatic Implementation (Python Code)**: The actual logic for a capability is implemented as a Python method in the agent class. This method is then registered as the handler for the corresponding capability ID defined in the configuration.

This separation enables several key benefits:
- Clear documentation of capabilities in configuration
- Automatic protocol adaptation and exposure
- Support for reasoning agnosticism through multiple handlers
- Consistent validation across all capability invocations

## Declarative Capability Definition

Capabilities are declared in the agent's YAML configuration under `multi_protocol_capabilities.core`, with these components:

1. **ID** - Unique identifier for the capability (used to link to handlers)
2. **Name** - Human-readable name for the capability
3. **Description** - Detailed explanation of the capability's purpose
4. **Parameters** - JSON Schema defining the expected inputs
5. **Returns** - JSON Schema defining the return value structure
6. **Examples** - Sample invocations for documentation

Example configuration in YAML:

```yaml
agents:
  weather_agent:
    # Agent configuration
    class: "agents.weather.WeatherAgent"
    
    # Capability configuration
    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "get_weather"
            name: "Get Weather"
            description: "Get current weather for a location"
            parameters:
              type: "object"
              properties:
                location:
                  type: "string"
                  description: "City name or coordinates"
              required: ["location"]
            returns:
              type: "object"
              properties:
                temperature:
                  type: "number"
                  description: "Current temperature in Celsius"
                conditions:
                  type: "string"
                  description: "Current weather conditions"
        protocol_mapping:
          a2a:
            get_weather: "get_weather"
          mcp:
            get_weather: "get_weather"
      capability_exposure:
        default_exposure: "all"
```

## Programmatic Capability Implementation

The actual implementation of the capability logic is done in the agent's Python code. There are two key components to this implementation:

1. **Handler Method**: A Python method that contains the capability's logic
2. **Handler Registration**: A mechanism to associate this method with the capability ID defined in the configuration

Example implementation in Python:

```python
from openmas.agent import Agent

class WeatherAgent(Agent):
    def setup(self):
        # Register the handler for the capability defined in configuration
        self.register_capability_handler(
            core_capability_id="get_weather",  # Must match the ID in multi_protocol_capabilities.core
            handler_method=self.get_weather_logic
        )
    
    async def get_weather_logic(self, location):
        # Capability implementation
        weather_data = await self.weather_service.fetch(location)
        return {
            "temperature": weather_data["temp"],
            "conditions": weather_data["conditions"]
        }
```

Alternatively, you can use the decorator syntax for more concise registration:

```python
from openmas.agent import Agent, capability_handler

class WeatherAgent(Agent):
    @capability_handler("get_weather")  # Must match the ID in multi_protocol_capabilities.core
    async def get_weather_logic(self, location):
        # Capability implementation
        weather_data = await self.weather_service.fetch(location)
        return {
            "temperature": weather_data["temp"],
            "conditions": weather_data["conditions"]
        }
```

## Protocol Mappings and Adaptations

A key benefit of the two-part capability system is the ability to map capabilities to different protocols through configuration. The `protocol_mapping` section of the configuration specifies how core capabilities should be exposed in each protocol:

```yaml
multi_protocol_capabilities:
  # Core capability definitions as shown above
  protocol_mapping:
    a2a:
      get_weather: "get_weather"  # Maps core ID to A2A capability name
    mcp:
      get_weather: "weather_tool"  # Maps core ID to MCP tool name
```

These mappings allow protocols to use different naming conventions or structures while maintaining a consistent internal implementation.

### A2A Protocol Adaptation

The framework automatically translates core capabilities to A2A agent card capabilities:

```json
{
  "name": "weather_agent",
  "display_name": "Weather Agent",
  "description": "Provides weather information",
  "capabilities": [
    {
      "name": "get_weather",
      "description": "Get current weather for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name or coordinates"
          }
        },
        "required": ["location"]
      },
      "returns": {
        "type": "object",
        "properties": {
          "temperature": {
            "type": "number",
            "description": "Current temperature in Celsius"
          },
          "conditions": {
            "type": "string",
            "description": "Current weather conditions"
          }
        }
      }
    }
  ]
}
```

### MCP Protocol Adaptation

The same core capability can be exposed as an MCP tool:

```json
{
  "tools": [
    {
      "name": "weather_tool",  // Name from protocol_mapping.mcp
      "description": "Get current weather for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name or coordinates"
          }
        },
        "required": ["location"]
      },
      "returns": {
        "type": "object",
        "properties": {
          "temperature": {
            "type": "number",
            "description": "Current temperature in Celsius"
          },
          "conditions": {
            "type": "string",
            "description": "Current weather conditions"
          }
        }
      }
    }
  ]
}
```

## Capability Types

The two-part capability system can be used to implement various capability types:

### 1. Information Capabilities

Capabilities that provide information:
- Data retrieval
- Question answering
- Status reporting

### 2. Action Capabilities

Capabilities that perform actions:
- State changes
- External API calls
- Resource manipulation

### 3. Reasoning Capabilities

Capabilities that perform reasoning:
- Decision making
- Planning
- Problem solving

### 4. Composite Capabilities

Capabilities that combine multiple other capabilities:
- Workflows
- Multi-step processes
- Coordinated actions

## Reasoning Agnosticism in Capabilities

A key advantage of the two-part capability system is its support for OpenMAS's reasoning agnosticism principle. The same declaratively defined capability can have different implementations based on the agent's reasoning approach:

```yaml
# In agent configuration
agents:
  analysis_agent:
    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "analyze_data"
            name: "Analyze Data"
            description: "Analyze a dataset and return insights"
            parameters:
              type: "object"
              properties:
                data:
                  type: "array"
                  description: "Dataset to analyze"
              required: ["data"]
            # ... other metadata
    reasoning:
      approach: "llm"  # Could be "rule_based", "bdi", etc.
```

```python
class MultiReasoningAgent(Agent):
    def setup(self):
        # Register different handlers for the same core capability ID
        # based on different reasoning approaches
        self.register_capability_handler(
            core_capability_id="analyze_data",
            handler_method=self.analyze_data_llm,
            reasoning="llm"
        )
        
        self.register_capability_handler(
            core_capability_id="analyze_data",
            handler_method=self.analyze_data_rules,
            reasoning="rule_based"
        )
        
        self.register_capability_handler(
            core_capability_id="analyze_data",
            handler_method=self.analyze_data_bdi,
            reasoning="bdi"
        )
    
    async def analyze_data_llm(self, data):
        # LLM-based implementation
        result = await self.llm.analyze(data)
        return result
    
    async def analyze_data_rules(self, data):
        # Rule-based implementation
        result = self.rule_engine.analyze(data)
        return result
    
    async def analyze_data_bdi(self, data):
        # BDI-based implementation
        self.belief_base.update({"data": data})
        result = await self.execute_plan("analyze_data_plan")
        return result
```

With this approach, the agent will automatically select the appropriate handler method based on its configured reasoning approach. This allows the same capability to be implemented differently for different reasoning engines, while maintaining a consistent interface and capability definition.

### Capability Discovery

Agents can discover capabilities of other agents regardless of their reasoning approach. The discovery system uses the declarative definitions from the configuration:

```python
# Discover capabilities of another agent
capabilities = await agent.discover_capabilities("weather_agent")

# Check if agent has a specific capability
has_capability = await agent.has_capability("weather_agent", "get_weather")

# Get capability schema
weather_schema = await agent.get_capability_schema("weather_agent", "get_weather")
```

## Complete Integrated Example

Here's a complete example showing the two-part capability system in action:

### YAML Configuration

```yaml
agents:
  weather_agent:
    # Agent configuration
    class: "agents.weather.WeatherAgent"
    
    # Capability configuration
    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "get_weather"
            name: "Get Weather"
            description: "Get current weather for a location"
            parameters:
              type: "object"
              properties:
                location:
                  type: "string"
                  description: "City name or coordinates"
              required: ["location"]
            returns:
              type: "object"
              properties:
                temperature:
                  type: "number"
                  description: "Current temperature in Celsius"
                conditions:
                  type: "string"
                  description: "Current weather conditions"
        protocol_mapping:
          a2a:
            get_weather: "get_weather"
          mcp:
            get_weather: "weather_tool"
      capability_exposure:
        default_exposure: "all"
    reasoning:
      approach: "llm"
```

### Python Implementation

```python
from openmas.agent import Agent, capability_handler

class WeatherAgent(Agent):
    def setup(self):
        # Register handlers for different reasoning approaches
        self.register_capability_handler(
            core_capability_id="get_weather",
            handler_method=self.get_weather_llm,
            reasoning="llm"
        )
        
        self.register_capability_handler(
            core_capability_id="get_weather",
            handler_method=self.get_weather_rule_based,
            reasoning="rule_based"
        )
    
    async def get_weather_llm(self, location):
        # LLM-based implementation
        context = f"What is the current weather in {location}?"
        response = await self.llm.generate(context)
        parsed_data = self.parse_weather_from_text(response)
        return parsed_data
    
    async def get_weather_rule_based(self, location):
        # Rule-based implementation
        weather_data = await self.weather_service.fetch(location)
        return {
            "temperature": weather_data["temp"],
            "conditions": weather_data["conditions"]
        }
```

## Implementation Flow and Framework Responsibilities

The integration between declarative capability definitions and programmatic implementations follows this sequence:

1. **Agent Configuration Loading**: The framework loads the agent's configuration, including the `multi_protocol_capabilities` section
2. **Agent Initialization**: The agent's `setup` method is called, where capability handlers are registered
3. **Validation**: The framework verifies that each declared capability has a corresponding handler
4. **Protocol Adapter Setup**: Protocol adapters use the `protocol_mapping` to expose capabilities appropriately
5. **Handler Selection**: When a capability is invoked, the framework selects the appropriate handler based on the agent's reasoning approach
6. **Parameter Validation**: Parameters are validated against the schema defined in the configuration
7. **Handler Execution**: The selected handler method is executed with the validated parameters
8. **Return Validation**: The return value is validated against the schema defined in the configuration

## Capability Security

Capabilities include security features that leverage the two-part model:

1. **Authentication** - The protocol layer ensures the caller is authenticated before reaching the capability handler
2. **Authorization** - The framework checks if the caller has permission to use the capability based on the agent's security configuration
3. **Rate Limiting** - The framework can enforce rate limits on capability invocations
4. **Input Validation** - Parameters are validated against the schema defined in the declarative configuration
5. **Output Validation** - Return values are validated against the schema defined in the declarative configuration

## Capability Integration with Other Components

The two-part capability system integrates with several OpenMAS components:

1. **Protocol Layer** - The declarative definitions and protocol mappings enable capabilities to be exposed through different protocols
2. **Topology System** - Capabilities can be used for role assignments in agent topologies
3. **Session Management** - Capability invocations can be tracked within sessions
4. **Observability System** - Both the declarative aspects (configuration, exposure) and programmatic aspects (handler execution) can be monitored

## Best Practices

When defining and implementing agent capabilities:

1. **Maintain Consistency** - Ensure the declarative definition (YAML) and programmatic implementation (Python) are aligned
2. **Use Clear IDs** - Core capability IDs should be meaningful and consistent
3. **Document All Aspects** - Provide clear descriptions in both the YAML configuration and Python code
4. **Leverage Reasoning-Specific Handlers** - Register different handlers for different reasoning approaches when appropriate
5. **Define Complete Schemas** - Comprehensive parameter and return schemas enable better validation and documentation
6. **Use Protocol Mappings Strategically** - Map capability names appropriately for each protocol's conventions
7. **Handle Errors Gracefully** - Implement robust error handling in capability handlers
8. **Test Across Protocols** - Verify that capabilities work correctly across all supported protocols
