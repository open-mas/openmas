# Tool Extensions

## Overview

Tool Extensions provide a mechanism to add new tool capabilities to OpenMAS agents. They allow developers to implement custom tools that agents can use to interact with external systems, access information, or perform actions while maintaining OpenMAS's reasoning agnosticism and protocol independence.

## Base Class

Tool Extensions must inherit from the `ToolExtension` base class:

```python
from openmas.extensions import ToolExtension

class MyToolExtension(ToolExtension):
    """A custom tool extension."""
```

## Required Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `execute_tool(tool_name, parameters, context)` | Execute a tool with given parameters | `tool_name`: Name of the tool to execute<br>`parameters`: Tool parameters<br>`context`: Execution context | Tool execution result |
| `get_tool_schema()` | Get the schema for the tools provided | None | Dictionary of tool schemas |

## Optional Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `validate_config()` | Validate the extension configuration | None | None, raises exception if invalid |
| `initialize()` | Initialize the extension | None | None |
| `get_supported_protocols()` | Get protocols supported by these tools | None | List of protocol identifiers |
| `get_tool_metadata()` | Get metadata about the tools | None | Dictionary of tool metadata |
| `validate_parameters(tool_name, parameters)` | Validate parameters for a specific tool | `tool_name`: Tool name<br>`parameters`: Parameters to validate | Boolean or raises exception |

## Configuration Schema

Tool Extensions are configured in the unified configuration schema under the `extensions` section with `type: "tool"`:

```yaml
extensions:
  my_tool_extension:
    type: "tool"
    name: "my_tool_extension"
    enabled: true
    options:
      tools:
        - name: "weather_lookup"
          description: "Look up weather information for a location"
          parameters:
            - name: "location"
              type: "string"
              required: true
              description: "Location to check weather for"
            - name: "units"
              type: "string"
              required: false
              description: "Temperature units (celsius or fahrenheit)"
              default: "celsius"
          api_key: "${WEATHER_API_KEY}"
        - name: "calculator"
          description: "Perform calculations"
          parameters:
            - name: "expression"
              type: "string"
              required: true
              description: "Mathematical expression to evaluate"
      # Additional configuration specific to this extension
```

### Options Schema

The `options` block for Tool Extensions supports the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tools` | array | Yes | List of tool definitions |
| `tools[].name` | string | Yes | Unique tool identifier |
| `tools[].description` | string | Yes | Human-readable tool description |
| `tools[].parameters` | array | Yes | Tool parameter definitions |
| `tools[].parameters[].name` | string | Yes | Parameter name |
| `tools[].parameters[].type` | string | Yes | Parameter type (string, number, boolean, array, object) |
| `tools[].parameters[].required` | boolean | Yes | Whether the parameter is required |
| `tools[].parameters[].description` | string | Yes | Parameter description |
| `tools[].parameters[].default` | any | No | Default value if not provided |
| `tools[].protocols` | array | No | Protocol-specific overrides |
| `caching` | object | No | Tool result caching configuration |
| `security` | object | No | Security configuration for tool execution |

For the complete schema definition, refer to the [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md#tool-extension-options).

## Interaction Model

Tool Extensions interact with the OpenMAS framework through the following mechanisms:

1. **Registration**: The extension is registered with the extension registry
2. **Discovery**: The agent framework discovers available tool extensions
3. **Capability Advertising**: The extension's tool schemas are advertised as agent capabilities
4. **Invocation**: When an agent needs to use a tool, it calls the appropriate extension
5. **Result Handling**: The tool's result is returned to the agent for integration into its reasoning

The Agent Framework maintains control over when tools are invoked, while the extension provides the specific tool implementation.

## Code Example

Here's a minimal example of a Tool Extension that implements weather lookup and calculator tools:

```python
from openmas.extensions import ToolExtension
import aiohttp
import json
import os
import re
from typing import Dict, List, Any

class UtilityToolsExtension(ToolExtension):
    """Extension that provides utility tools."""
    
    extension_type = "tool"
    extension_name = "utility_tools"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        options = config.get("options", {})
        
        # Extract tool configurations
        self.tools = {}
        for tool_config in options.get("tools", []):
            tool_name = tool_config.get("name")
            if tool_name:
                self.tools[tool_name] = tool_config
        
        # Initialize session for external API calls
        self.session = None
        
        # Extract API keys
        self.weather_api_key = None
        weather_tool = self.tools.get("weather_lookup", {})
        if weather_tool:
            self.weather_api_key = weather_tool.get("api_key") or os.environ.get("WEATHER_API_KEY")
    
    async def initialize(self):
        """Initialize the extension."""
        self.session = aiohttp.ClientSession()
        self.initialized = True
    
    def validate_config(self):
        """Validate the extension configuration."""
        options = self.config.get("options", {})
        if not options.get("tools"):
            raise ValueError("Tool extension requires 'tools' in options")
        
        # Validate weather tool configuration
        if "weather_lookup" in self.tools and not self.weather_api_key:
            raise ValueError("Weather lookup tool requires an API key")
    
    def get_tool_schema(self):
        """Get the schema for the tools provided."""
        schemas = {}
        
        # Weather lookup tool
        if "weather_lookup" in self.tools:
            schemas["weather_lookup"] = {
                "name": "weather_lookup",
                "description": "Look up weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location to check weather for"
                        },
                        "units": {
                            "type": "string",
                            "description": "Temperature units (celsius or fahrenheit)",
                            "enum": ["celsius", "fahrenheit"],
                            "default": "celsius"
                        }
                    },
                    "required": ["location"]
                }
            }
        
        # Calculator tool
        if "calculator" in self.tools:
            schemas["calculator"] = {
                "name": "calculator",
                "description": "Perform calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            }
        
        return schemas
    
    def get_tool_metadata(self):
        """Get metadata about the tools."""
        metadata = {}
        
        if "weather_lookup" in self.tools:
            metadata["weather_lookup"] = {
                "requires_api_key": True,
                "external_service": "weatherapi.com",
                "rate_limit": "60 calls per minute"
            }
        
        if "calculator" in self.tools:
            metadata["calculator"] = {
                "local_execution": True,
                "safe_execution": True,
                "supported_operations": ["+", "-", "*", "/", "^", "sqrt", "sin", "cos", "tan"]
            }
        
        return metadata
    
    def get_supported_protocols(self):
        """Get protocols supported by these tools."""
        return ["a2a", "mcp", "http"]  # These tools work with all major protocols
    
    async def execute_tool(self, tool_name, parameters, context=None):
        """Execute a tool with given parameters."""
        if not self.initialized:
            await self.initialize()
        
        # Validate the tool exists
        if tool_name not in self.tools:
            return {
                "error": f"Tool not found: {tool_name}"
            }
        
        # Validate parameters
        try:
            self.validate_parameters(tool_name, parameters)
        except ValueError as e:
            return {
                "error": f"Invalid parameters: {str(e)}"
            }
        
        # Execute the appropriate tool
        if tool_name == "weather_lookup":
            return await self._execute_weather_lookup(parameters)
        elif tool_name == "calculator":
            return await self._execute_calculator(parameters)
        else:
            return {
                "error": f"Tool implementation not found: {tool_name}"
            }
    
    def validate_parameters(self, tool_name, parameters):
        """Validate parameters for a specific tool."""
        if tool_name == "weather_lookup":
            if "location" not in parameters:
                raise ValueError("Missing required parameter: location")
            
            units = parameters.get("units", "celsius")
            if units not in ["celsius", "fahrenheit"]:
                raise ValueError("Units must be either 'celsius' or 'fahrenheit'")
        
        elif tool_name == "calculator":
            if "expression" not in parameters:
                raise ValueError("Missing required parameter: expression")
            
            # Check for potentially unsafe expressions
            expression = parameters["expression"]
            if re.search(r'[^0-9+\-*/().\s^sqrt sin cos tan]', expression):
                raise ValueError("Expression contains invalid characters")
    
    async def _execute_weather_lookup(self, parameters):
        """Execute the weather lookup tool."""
        location = parameters["location"]
        units = parameters.get("units", "celsius")
        
        try:
            # Call weather API
            url = f"https://api.weatherapi.com/v1/current.json?key={self.weather_api_key}&q={location}&aqi=no"
            async with self.session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return {
                        "error": f"Weather API error ({response.status}): {error_text}"
                    }
                
                data = await response.json()
                
                # Extract relevant weather information
                current = data.get("current", {})
                temp_c = current.get("temp_c")
                temp_f = current.get("temp_f")
                condition = current.get("condition", {}).get("text")
                humidity = current.get("humidity")
                
                # Format the response based on requested units
                temp = temp_f if units == "fahrenheit" else temp_c
                unit_symbol = "°F" if units == "fahrenheit" else "°C"
                
                return {
                    "location": data.get("location", {}).get("name"),
                    "temperature": temp,
                    "temperature_unit": unit_symbol,
                    "condition": condition,
                    "humidity": humidity
                }
        except Exception as e:
            return {
                "error": f"Error accessing weather information: {str(e)}"
            }
    
    async def _execute_calculator(self, parameters):
        """Execute the calculator tool."""
        expression = parameters["expression"]
        
        try:
            # Replace mathematical functions with Python equivalents
            expression = expression.replace("^", "**")
            expression = re.sub(r'sqrt\(([^)]+)\)', r'math.sqrt(\1)', expression)
            expression = re.sub(r'sin\(([^)]+)\)', r'math.sin(\1)', expression)
            expression = re.sub(r'cos\(([^)]+)\)', r'math.cos(\1)', expression)
            expression = re.sub(r'tan\(([^)]+)\)', r'math.tan(\1)', expression)
            
            # Add math import if needed
            if any(func in expression for func in ["math.sqrt", "math.sin", "math.cos", "math.tan"]):
                import math
            
            # Evaluate the expression safely
            result = eval(expression, {"__builtins__": {}}, {"math": math})
            
            return {
                "result": result,
                "expression": parameters["expression"]
            }
        except Exception as e:
            return {
                "error": f"Error evaluating expression: {str(e)}",
                "expression": parameters["expression"]
            }
```

### Configuration Example

```yaml
extensions:
  utility_tools:
    type: "tool"
    name: "utility_tools"
    enabled: true
    options:
      tools:
        - name: "weather_lookup"
          description: "Look up weather information for a location"
          parameters:
            - name: "location"
              type: "string"
              required: true
              description: "Location to check weather for"
            - name: "units"
              type: "string"
              required: false
              description: "Temperature units (celsius or fahrenheit)"
              default: "celsius"
          api_key: "${WEATHER_API_KEY}"
        - name: "calculator"
          description: "Perform calculations"
          parameters:
            - name: "expression"
              type: "string"
              required: true
              description: "Mathematical expression to evaluate"
      caching:
        enabled: true
        ttl_seconds: 300  # Cache weather results for 5 minutes
```

## Protocol Compatibility

Tool Extensions can define protocol-specific behavior to ensure compatibility with different protocols:

```python
def get_tool_schema(self):
    """Get the schema for the tools provided with protocol-specific variants."""
    base_schemas = {
        # Base schemas as shown earlier
    }
    
    # Add protocol-specific schema overrides
    protocol_schemas = {
        "a2a": {
            # A2A-specific schema adaptations
            "weather_lookup": {
                # A2A-specific schema for weather_lookup
            }
        },
        "mcp": {
            # MCP-specific schema adaptations
        }
    }
    
    return {
        "base": base_schemas,
        "protocol_specific": protocol_schemas
    }
```

## Best Practices

1. **Security First**: Always validate input parameters to prevent injection attacks
2. **Error Handling**: Provide clear, actionable error messages
3. **Resource Management**: Properly manage connections and resources
4. **Protocol Independence**: Design tools to work with multiple protocols when possible
5. **Caching**: Implement appropriate caching for external API calls
6. **Rate Limiting**: Respect API rate limits for external services
7. **Documentation**: Provide clear documentation of tool capabilities and parameters

## Related Documentation

- [Extension System Design](../design/design_extension_system.md)
- [Agent Framework Design](../../06_agent_framework/design_agent_framework.md)
- [Extension Development Guide](../development/guide.md)
- [Multi-Protocol Capability Design](../../01_architecture/multi_protocol_design.md)
