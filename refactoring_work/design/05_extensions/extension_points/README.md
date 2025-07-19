# Extension Points

## Overview

OpenMAS provides well-defined extension points that allow developers to customize and enhance the framework. This document describes the available extension points, their interfaces, and usage examples.

## Extension Point Categories

OpenMAS offers these primary extension point categories:

1. **Agent Extensions** - Customize agent functionality
2. **Communicator Extensions** - Add new communication protocols
3. **Asset Extensions** - Provide new resource types and loaders
4. **Prompt Extensions** - Customize prompt management
5. **LLM Extensions** - Integrate with language models
6. **Reasoning Extensions** - Add custom reasoning approaches
7. **Protocol Adapters** - Bridge between different protocols
8. **Tool Extensions** - Add new tool capabilities

## Agent Extensions

Agent extensions enhance or modify agent capabilities and behavior.

### Agent Type Extension

```python
from openmas.extensions import AgentExtension

class CustomAgentType(AgentExtension):
    """Custom agent type implementation."""
    
    extension_type = "agent"
    extension_name = "custom_agent"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.custom_property = config.get("custom_property", "default")
    
    async def setup(self, agent):
        """Set up the agent extension."""
        # Register custom capabilities
        agent.register_capability(
            "custom_capability",
            "A custom capability provided by the extension",
            parameters={"type": "object", "properties": {}},
            returns={"type": "object", "properties": {}}
        )
        
        # Add custom event handlers
        agent.on("message", self._on_message)
    
    async def _on_message(self, message):
        """Handle incoming messages."""
        # Custom message handling logic
        return {"status": "handled"}
```

### Agent Middleware Extension

```python
from openmas.extensions import AgentMiddlewareExtension

class LoggingMiddleware(AgentMiddlewareExtension):
    """Middleware for logging agent messages."""
    
    extension_type = "agent_middleware"
    extension_name = "logging_middleware"
    
    async def before_process_message(self, agent, message):
        """Called before processing a message."""
        print(f"Incoming message: {message}")
        return message
    
    async def after_process_message(self, agent, message, result):
        """Called after processing a message."""
        print(f"Outgoing result: {result}")
        return result
```

## Communicator Extensions

Communicator extensions add support for new communication protocols or transport mechanisms.

### Protocol Communicator Extension

```python
from openmas.extensions import CommunicatorExtension

class WebSocketCommunicator(CommunicatorExtension):
    """WebSocket-based communicator implementation."""
    
    extension_type = "communicator"
    extension_name = "websocket"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.url = config.get("url", "ws://localhost:8080")
        self.client = None
    
    async def initialize(self):
        """Initialize the communicator."""
        self.client = await self._create_client()
        self.initialized = True
    
    async def send_message(self, message):
        """Send a message over WebSocket."""
        if not self.client:
            raise RuntimeError("WebSocket client not initialized")
        
        await self.client.send(message)
    
    async def receive_message(self):
        """Receive a message from WebSocket."""
        if not self.client:
            raise RuntimeError("WebSocket client not initialized")
        
        return await self.client.receive()
    
    async def _create_client(self):
        """Create a WebSocket client."""
        # Implement WebSocket client creation
        pass
```

## Asset Extensions

Asset extensions provide new resource types and loaders for models, embeddings, and other assets.

### Asset Provider Extension

```python
from openmas.extensions import AssetProviderExtension

class CustomModelProvider(AssetProviderExtension):
    """Provider for custom model types."""
    
    extension_type = "asset_provider"
    extension_name = "custom_model_provider"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.model_directory = config.get("model_directory", "./models")
    
    async def get_asset(self, asset_id):
        """Get an asset by ID."""
        # Load the model from the specified directory
        model_path = os.path.join(self.model_directory, asset_id)
        return await self._load_model(model_path)
    
    async def list_assets(self):
        """List available assets."""
        # List all models in the directory
        models = []
        for filename in os.listdir(self.model_directory):
            if filename.endswith(".model"):
                models.append(filename.replace(".model", ""))
        return models
    
    async def _load_model(self, model_path):
        """Load a model from the specified path."""
        # Implement model loading logic
        pass
```

## Prompt Extensions

Prompt extensions customize prompt management, including templates and context handling.

### Prompt Template Extension

```python
from openmas.extensions import PromptTemplateExtension

class CustomTemplateEngine(PromptTemplateExtension):
    """Custom prompt template engine."""
    
    extension_type = "prompt_template"
    extension_name = "custom_template"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.template_directory = config.get("template_directory", "./templates")
    
    def render_template(self, template_name, variables):
        """Render a template with variables."""
        template_path = os.path.join(self.template_directory, f"{template_name}.tpl")
        with open(template_path, "r") as f:
            template_content = f.read()
        
        # Replace variables in the template
        for key, value in variables.items():
            template_content = template_content.replace(f"{{{key}}}", str(value))
        
        return template_content
    
    def get_template_schema(self, template_name):
        """Get the schema for a template."""
        schema_path = os.path.join(self.template_directory, f"{template_name}.schema.json")
        with open(schema_path, "r") as f:
            return json.load(f)
```

## LLM Extensions

LLM extensions integrate with language models and provide model-specific optimizations.

### LLM Provider Extension

```python
from openmas.extensions import LLMProviderExtension

class CustomLLMProvider(LLMProviderExtension):
    """Provider for custom LLM integration."""
    
    extension_type = "llm_provider"
    extension_name = "custom_llm"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "default")
        self.client = None
    
    async def initialize(self):
        """Initialize the LLM provider."""
        # Initialize the LLM client
        self.client = self._create_client()
        self.initialized = True
    
    async def generate(self, prompt, options=None):
        """Generate text from the LLM."""
        if not self.client:
            raise RuntimeError("LLM client not initialized")
        
        options = options or {}
        response = await self.client.generate(
            prompt=prompt,
            max_tokens=options.get("max_tokens", 1024),
            temperature=options.get("temperature", 0.7)
        )
        
        return response.text
    
    def _create_client(self):
        """Create an LLM client."""
        # Implement LLM client creation
        pass
```

## Reasoning Extensions

Reasoning extensions add custom reasoning approaches to OpenMAS.

### Reasoning Engine Extension

```python
from openmas.extensions import ReasoningExtension

class RuleBasedReasoner(ReasoningExtension):
    """Rule-based reasoning implementation."""
    
    extension_type = "reasoning"
    extension_name = "rule_based"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.rule_file = config.get("rule_file", "rules.json")
        self.rules = []
    
    async def initialize(self):
        """Initialize the reasoning engine."""
        # Load rules from the rule file
        with open(self.rule_file, "r") as f:
            self.rules = json.load(f)
        
        self.initialized = True
    
    async def reason(self, input_data):
        """Perform reasoning on input data."""
        results = []
        
        # Apply rules to the input data
        for rule in self.rules:
            if self._matches_condition(input_data, rule["condition"]):
                results.append(rule["action"])
        
        return results
    
    def _matches_condition(self, data, condition):
        """Check if data matches a condition."""
        # Implement condition matching logic
        pass
```

## Protocol Adapters

Protocol adapters bridge between different communication protocols.

### Protocol Adapter Extension

```python
from openmas.extensions import ProtocolAdapterExtension

class A2AToMCPAdapter(ProtocolAdapterExtension):
    """Adapter from A2A to MCP protocol."""
    
    extension_type = "protocol_adapter"
    extension_name = "a2a_to_mcp"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
    
    def adapt_request(self, request, source_protocol="a2a", target_protocol="mcp"):
        """Adapt a request between protocols."""
        if source_protocol == "a2a" and target_protocol == "mcp":
            # Convert A2A request to MCP format
            return {
                "type": "tool_call",
                "name": request.get("capability", "default"),
                "parameters": request.get("content", {})
            }
        elif source_protocol == "mcp" and target_protocol == "a2a":
            # Convert MCP request to A2A format
            return {
                "type": "request",
                "capability": request.get("name", "default"),
                "content": request.get("parameters", {})
            }
        
        # Unsupported conversion
        raise ValueError(f"Unsupported protocol conversion: {source_protocol} -> {target_protocol}")
    
    def adapt_response(self, response, source_protocol="a2a", target_protocol="mcp"):
        """Adapt a response between protocols."""
        if source_protocol == "a2a" and target_protocol == "mcp":
            # Convert A2A response to MCP format
            return {
                "result": response.get("content", {}),
                "status": "success" if response.get("status") == "success" else "error"
            }
        elif source_protocol == "mcp" and target_protocol == "a2a":
            # Convert MCP response to A2A format
            return {
                "type": "response",
                "status": "success" if not response.get("error") else "error",
                "content": response.get("result", {})
            }
        
        # Unsupported conversion
        raise ValueError(f"Unsupported protocol conversion: {source_protocol} -> {target_protocol}")
```

## Tool Extensions

Tool extensions add new tool capabilities to agents.

### Tool Extension

```python
from openmas.extensions import ToolExtension

class WeatherToolExtension(ToolExtension):
    """Tool for retrieving weather information."""
    
    extension_type = "tool"
    extension_name = "weather_tool"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.api_url = config.get("api_url", "https://api.weather.example.com")
        self.client = None
    
    async def initialize(self):
        """Initialize the tool."""
        # Set up the API client
        self.client = self._create_client()
        self.initialized = True
    
    def get_tool_definition(self):
        """Get the tool definition for agent systems."""
        return {
            "name": "get_weather",
            "description": "Get current weather information for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or coordinates"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "Units for temperature (Celsius or Fahrenheit)"
                    }
                },
                "required": ["location"]
            },
            "returns": {
                "type": "object",
                "properties": {
                    "temperature": {
                        "type": "number",
                        "description": "Current temperature"
                    },
                    "conditions": {
                        "type": "string",
                        "description": "Current weather conditions"
                    },
                    "humidity": {
                        "type": "number",
                        "description": "Current humidity percentage"
                    }
                }
            }
        }
    
    async def invoke(self, parameters):
        """Invoke the tool with parameters."""
        if not self.client:
            raise RuntimeError("Weather API client not initialized")
        
        location = parameters.get("location")
        units = parameters.get("units", "metric")
        
        # Fetch weather data from the API
        weather_data = await self.client.get_weather(location, units)
        
        return {
            "temperature": weather_data["temp"],
            "conditions": weather_data["conditions"],
            "humidity": weather_data["humidity"]
        }
    
    def _create_client(self):
        """Create a weather API client."""
        # Implement API client creation
        pass
```

## Defining New Extension Points

Developers can define new extension points by creating a base extension class:

```python
from openmas.extensions import BaseExtension

class MyCustomExtension(BaseExtension):
    """Base class for custom extensions."""
    
    extension_type = "my_custom_extension"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
    
    async def initialize(self):
        """Initialize the extension."""
        # Initialization logic
        self.initialized = True
    
    async def my_custom_method(self):
        """Custom method for this extension type."""
        raise NotImplementedError("Subclasses must implement my_custom_method")
```

## Extension Point Documentation Standard

Each extension point should be documented using this standard format:

- **Name**: [Extension Point Name]
- **Purpose**: [Brief description of extension point's purpose]
- **Component**: [Parent component]
- **Type**: [Type of extension: communicator, agent, asset, prompt, etc.]
- **Community Usage**: [How this extension point serves the community]
- **Protocol Compatibility**: [List of protocols the extension supports: MCP, A2A, etc.]

## Extension Configuration

Extension configuration follows the unified configuration schema. For the complete schema definition, see [Extension Configuration Schema](/03_configuration/schema/extensions.md).

Basic configuration example:

```yaml
extensions:
  weather_tool:
    type: "tool"
    name: "weather_tool"
    enabled: true
    options:
      api_key: "${WEATHER_API_KEY}"
      api_url: "https://api.weather.example.com"
  
  websocket_communicator:
    type: "communicator"
    name: "websocket"
    enabled: true
    options:
      url: "ws://localhost:8080"
      ping_interval: 30
```

## Protocol Independence

All extension points support working with different protocols through protocol adapters. This ensures that extensions can operate independently of the specific communication protocol being used.

## Reasoning Agnosticism

All extension points maintain OpenMAS's distinctive reasoning agnosticism, ensuring clear separation between communication infrastructure ("body") and reasoning approaches ("brain"). This enables extensions to work consistently regardless of the reasoning approach being used.
