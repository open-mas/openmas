# Agent Capabilities and Multi-Protocol Standard

## Agent Definition
- **Name**: [Agent Name]
- **Purpose**: [Brief description of agent's purpose]
- **Base Type**: [Base agent type]
- **Capabilities**: [List of capabilities]
- **Reasoning Approach**: [Reasoning approach used by agent - rule-based, BDI, KR&R, LLM-based, hybrid]
- **Protocol Support**: [List of supported protocols - A2A, MCP, etc.]
- **Reasoning Agnosticism**: [How the agent maintains separation between capabilities and reasoning]

## Agent Schema
```yaml
# Standardized agent configuration schema (within unified schema)
agents:
  agent_name:
    # Agent class and type
    class:
      type: string
      description: "Agent class path"
    type:
      type: string
      description: "Agent reasoning type"
      enum: ["llm", "rule_based", "hybrid", "bdi", "symbolic"]
  
    # Protocol configuration
    protocols:
      type: array
      description: "Protocol interfaces exposed by this agent"
      items:
        type: object
        properties:
          type:
            type: string
            description: "The type of protocol to use"
            enum: ["mcp-stdio", "mcp-sse", "mcp-streamable", "a2a-http", "a2a-websocket", "a2a-grpc", "grpc", "mqtt", "http", "websocket"]
          enabled:
            type: boolean
            description: "Whether this protocol interface is enabled"
            default: true
          options:
            type: object
            description: "Protocol-specific options"
      format_adapters:
        type: object
        description: "Configuration for message format adapters within the agent"
        properties:
          adapters:
            type: array
            description: "Format adapters to convert between protocol-specific message formats within this agent"
            items:
              type: object
              properties:
                source_format:
                  type: string
                  description: "Source message format"
                target_format:
                  type: string
                  description: "Target message format"
                adapter_class:
                  type: string
                  description: "Format adapter class name"
              required: ["source_format", "target_format", "adapter_class"]
  
  # Agent capabilities configuration
  capabilities:
    type: object
    description: "Agent capabilities configuration"
    properties:
      # Capability-specific properties
      tool_usage:
        type: boolean
        description: "Whether the agent can use tools"
      
      memory:
        type: boolean
        description: "Whether the agent has memory"
      
      reasoning:
        type: boolean
        description: "Whether the agent has reasoning capabilities"
      
      # Multi-protocol capability configuration
      multi_protocol_capabilities:
        type: object
        description: "Agent capabilities across different protocols"
        properties:
          # Core capability definition (protocol-agnostic)
          core:
            type: array
            description: "Core capability definitions that can be exposed through multiple protocols"
            items:
              type: object
              properties:
                id:
                  type: string
                  description: "Unique identifier for the capability"
                name:
                  type: string
                  description: "Human-readable name for the capability"
                description:
                  type: string
                  description: "Detailed description"
                parameters:
                  type: object
                  description: "JSON Schema for the capability parameters"
                returns:
                  type: object
                  description: "JSON Schema for the return value"
                examples:
                  type: array
                  description: "Example uses of this capability"
                  items:
                    type: object
                # Protocol-specific overrides can be defined below
                
          # Protocol-specific capability representation
          protocol_mapping:
            type: object
            description: "How capabilities are represented in different protocols"
            properties:
              # A2A representation
              a2a:
                type: object
                description: "A2A-specific capability representation"
                properties:
                  capability_format:
                    type: string
                    description: "Format for A2A capabilities"
                    default: "agent_card"
                  
              # MCP representation
              mcp:
                type: object
                description: "MCP-specific capability representation"
                properties:
                  capability_format:
                    type: string
                    description: "Format for MCP capabilities"
                    default: "tool_definition"
                  
          # Protocol exposure configuration
          capability_exposure:
            type: object
            description: "Configuration for capability exposure across protocols"
            properties:
              default_exposure:
                type: string
                description: "Default exposure level for capabilities"
                enum: ["all", "selective", "none"]
                default: "all"
              capability_filter:
                type: object
                description: "Filter which capabilities are exposed on which protocols"
                additionalProperties:
                  type: array
                  items:
                    type: string
              capability_filter:
                type: object
                description: "Filter which capabilities are exposed on which protocols"
                additionalProperties:
                  type: array
                  items:
                    type: string
  
  # Note on A2A Agent Card configuration
  # A2A Agent Card details must be configured within the agent's A2A protocol options section:
  # protocols.ITEM_WHERE_TYPE_IS_A2A.options.agent_card
  # See the unified configuration schema and protocols.md for full details
            type: boolean
            description: "Whether the agent supports streaming responses"
            default: false
          push_notifications:
            type: boolean
            description: "Whether the agent supports push notifications"
            default: false
      auth_requirements:
        type: object
        description: "Authentication requirements for accessing this agent"
        properties:
          required:
            type: boolean
            description: "Whether authentication is required"
            default: false
          types:
            type: array
            description: "Supported authentication types"
            items:
              type: string
              enum: ["none", "api_key", "oauth2", "jwt", "basic"]
      discovery:
        type: object
        description: "Discovery configuration"
        properties:
          published:
            type: boolean
            description: "Whether this agent should be publicly discoverable"
            default: true
          well_known_path:
            type: string
            description: "Path where the agent card is accessible"
            default: "/.well-known/agent.json"
  
  # Knowledge representation configuration
  knowledge:
    type: object
    description: "Knowledge representation configuration"
    properties:
      representation_type:
        type: string
        description: "Type of knowledge representation"
        enum: ["symbolic", "graph", "vector", "probabilistic", "neural", "hybrid"]
      
      storage:
        type: object
        description: "Knowledge storage configuration"
        properties:
          type:
            type: string
            description: "Type of knowledge storage"
            enum: ["memory", "file", "database", "vector_store", "graph_db"]
          connection_string:
            type: string
            description: "Connection string for database storage"
  
  # Reasoning configuration
  reasoning:
    type: object
    description: "Reasoning configuration"
    properties:
      approach:
        type: string
        description: "Reasoning approach"
        enum: ["rule_based", "bdi", "llm", "hybrid", "symbolic", "probabilistic"]
      
      # BDI-specific configuration
      bdi:
        type: object
        description: "BDI reasoning configuration"
        properties:
          belief_update_strategy:
            type: string
            description: "Strategy for updating beliefs"
            enum: ["incremental", "revision", "update"]
          desire_selection_strategy:
            type: string
            description: "Strategy for selecting desires"
            enum: ["priority", "utility", "context"]
          intention_reconsideration:
            type: boolean
            description: "Whether to reconsider intentions"
            default: true
      
      # LLM-specific configuration
      llm:
        type: object
        description: "LLM reasoning configuration"
        properties:
          model:
            type: string
            description: "LLM model to use"
          system_prompt:
            type: string
            description: "System prompt for reasoning"
          prompt_template:
            type: string
            description: "Reference to prompt template for reasoning"
      
      # Hybrid reasoning configuration
      hybrid:
        type: object
        description: "Hybrid reasoning configuration"
        properties:
          coordination:
            type: string
            description: "Coordination strategy for hybrid reasoning"
            enum: ["sequential", "parallel", "meta", "voting"]
          reasoners:
            type: array
            description: "Reasoners to use in hybrid setup"
            items:
              type: object
              properties:
                type:
                  type: string
                  description: "Type of reasoner"
                  enum: ["rule_based", "bdi", "llm", "symbolic", "probabilistic"]
                config:
                  type: object
                  description: "Reasoner-specific configuration"
  
  # Role configuration
  roles:
    type: array
    description: "Roles that this agent can assume"
    items:
      type: object
      properties:
        name:
          type: string
          description: "Role name"
        capabilities:
          type: array
          description: "Capabilities enabled for this role"
          items:
            type: string
        activation_condition:
          type: string
          description: "Condition for activating this role"
        
  # Agent-specific configuration
  config:
    type: object
    description: "Agent-specific configuration"
    # Agent-specific properties

    required:
      - class
```

## Reasoning Capabilities Matrix
| Reasoning Approach | Description | Knowledge Representation | Use Cases |
|-------------------|-------------|-------------------------|-----------|
| Rule-based | Simple, deterministic decision making | Rules, logic statements | Simple automation, defined processes |
| BDI | Belief-Desire-Intention cognitive architecture | Beliefs (knowledge), Desires (goals), Intentions (plans) | Deliberative agents, complex decision making |
| LLM-based | Language model reasoning | Neural/embeddings | Complex reasoning, natural language understanding |
| Symbolic | Classic symbolic AI approaches | Logic, ontologies, knowledge graphs | Explainable decisions, structured knowledge |
| Probabilistic | Reasoning under uncertainty | Bayesian networks, probability distributions | Uncertain environments, risk analysis |
| Hybrid | Combining multiple approaches | Mixed (symbolic + neural, etc.) | Complex real-world problems, leveraging strengths of each approach |

## Capability Definitions
| Capability | Description | A2A Alignment | Required Configuration |
|------------|-------------|--------------|------------------------|
| Tool Usage | Ability to use tools | A2A Tool Calls | tool_definitions, tool_configs |
| Memory | Ability to remember past interactions | A2A History Context | memory_config |
| Reasoning | Ability to reason about tasks | A2A Chain of Thought | reasoning_config |
| Knowledge Representation | Ability to represent and use knowledge | A2A Knowledge Transport | knowledge_config |
| Learning | Ability to learn from interactions | A2A Feedback Loop | learning_config |
| Planning | Ability to create and execute plans | A2A Plan Structure | planning_config |
| etc. | etc. | etc. | etc. |

## BDI Architecture Components
- **Beliefs**: [How beliefs are represented and updated]
- **Desires**: [How desires/goals are represented and prioritized]
- **Intentions**: [How intentions/plans are formed and executed]
- **Deliberation**: [How the agent decides what to do]
- **Means-End Reasoning**: [How the agent decides how to do things]

## Knowledge Representation Options
- **Symbolic Knowledge**: [Logic, rules, ontologies]
- **Graph Knowledge**: [Knowledge graphs, semantic networks]
- **Vector Knowledge**: [Embeddings, vector stores]
- **Probabilistic Knowledge**: [Bayesian networks, Markov models]
- **Neural Knowledge**: [Weights in neural networks]
- **Hybrid Knowledge**: [Combinations of the above]

## A2A Protocol Alignment
- **A2A Message Types**: [How agent capabilities map to A2A message types]
- **A2A Extensions**: [How agent capabilities map to A2A extensions]
- **Protocol Compatibility**: [Protocol compatibility considerations]

## Lifecycle Management
- **Initialization**: [How agents are initialized]
- **State Management**: [How agent state is managed]
- **Shutdown**: [How agents are shut down]
- **Recovery**: [How agents recover from failures]

## Capability Configuration
- **Tool Usage Configuration**:
  ```yaml
  # Tool usage configuration example
  capabilities:
    tool_usage:
      enabled: true
      tools:
        - name: "web_search"
          description: "Search the web for information"
          parameters:
            query:
              type: "string"
              description: "The search query"
          required_permissions: ["internet_access"]
  ```
- **Memory Configuration**:
  ```yaml
  # Memory configuration example
  capabilities:
    memory:
      enabled: true
      type: "vector"
      storage: "redis"
      connection: "${REDIS_CONNECTION_STRING}"
      max_items: 1000
      recency_bias: 0.8
  ```
- **Reasoning Configuration**:
  ```yaml
  # Reasoning configuration example
  reasoning:
    approach: "hybrid"
    hybrid:
      coordination: "sequential"
      reasoners:
        - type: "symbolic"
          config:
            rules_file: "business_rules.json"
        - type: "llm"
          config:
            model: "claude-3-sonnet-20240229"
            prompt_template: "reasoning_prompt"
  ```

## LLM Integration
- **LLM Requirements**: [LLM requirements for capabilities]
- **Prompt Structures**: [Prompt structures for capabilities]
- **Model Selection**: [Model selection considerations]
- **Reasoning Techniques**: [Chain-of-thought, tree-of-thought, etc.]

## Capability Implementation
- **Required Interfaces**: [Interfaces that must be implemented]
- **Extension Points**: [Extension points for capabilities]
- **Default Implementations**: [Default implementations]

## Testing
- **Unit Test Requirements**: [Capability-specific test requirements]
- **Integration Test Requirements**: [Capability integration test requirements]
- **Capability Verification**: [How to verify capabilities]
- **Reasoning Testing**: [How to test different reasoning approaches]

## Multi-Protocol Capability Structure

OpenMAS uses a sophisticated multi-protocol capability structure that allows agents to define capabilities once and expose them across different protocols. This structure ensures protocol independence while maintaining consistent capability definitions.

## Capability Registration API

The OpenMAS Agent Framework provides a well-defined API for registering, managing, and exposing agent capabilities. This API ensures consistent capability handling across different agent implementations and protocols.

### ICapabilityManager Interface

The `ICapabilityManager` interface is the central component for capability registration and discovery. Agent implementations use this interface to register their capabilities programmatically.

```python
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Type, Union, Any
from pydantic import BaseModel


class CapabilityInfo(BaseModel):
    """Model representing metadata about a registered capability."""
    id: str
    """Unique identifier for the capability."""
    name: str
    """Human-readable name for the capability."""
    description: Optional[str] = None
    """Detailed description of what the capability does."""
    version: str = "1.0"
    """Version of the capability."""
    input_schema: Type[BaseModel]
    """Pydantic model defining the input schema for the capability."""
    output_schema: Type[BaseModel]
    """Pydantic model defining the output schema for the capability."""
    handler_function_name: str
    """Name of the handler function for introspection purposes."""
    input_schema_definition: Dict[str, Any]
    """JSON schema representation of the input Pydantic model."""
    output_schema_definition: Dict[str, Any]
    """JSON schema representation of the output Pydantic model."""
    protocol_specific_names: Dict[str, str] = {}
    """Mapping of protocol names to protocol-specific capability names."""
    examples: List[Dict[str, Any]] = []
    """Example uses of this capability."""


class ICapabilityManager(ABC):
    """Interface for managing agent capabilities.
    
    The ICapabilityManager provides methods for registering, unregistering,
    listing, and invoking capabilities within an agent.
    """
    
    @abstractmethod
    async def register_capability(
        self,
        id: str,
        handler_function: Callable,
        input_schema: Type[BaseModel],
        output_schema: Type[BaseModel],
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "1.0",
        protocol_specific_names: Optional[Dict[str, str]] = None,
        examples: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Register a new capability with the agent.
        
        Args:
            id: Unique identifier for the capability
            handler_function: Async function that implements the capability
            input_schema: Pydantic model defining the input parameters
            output_schema: Pydantic model defining the return value
            name: Human-readable name (defaults to id if not provided)
            description: Detailed description of the capability
            version: Version string for the capability
            protocol_specific_names: Mapping of protocol names to protocol-specific identifiers
            examples: Example uses of this capability with inputs and expected outputs
            
        Raises:
            ValueError: If a capability with the same id is already registered
            TypeError: If input_schema or output_schema are not valid Pydantic models
        """
        pass
    
    @abstractmethod
    async def unregister_capability(self, id: str) -> bool:
        """Unregister a capability from the agent.
        
        Args:
            id: Identifier of the capability to unregister
            
        Returns:
            bool: True if the capability was found and unregistered, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_capabilities(self) -> List[CapabilityInfo]:
        """List all capabilities registered with this agent.
        
        Returns:
            List[CapabilityInfo]: List of capability metadata objects
        """
        pass
    
    @abstractmethod
    async def get_capability_details(self, id: str) -> Optional[CapabilityInfo]:
        """Get detailed information about a specific capability.
        
        Args:
            id: Identifier of the capability
            
        Returns:
            Optional[CapabilityInfo]: Capability metadata if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def invoke_capability(
        self,
        id: str,
        input_data: Union[Dict[str, Any], BaseModel],
        context: 'AgentContext'
    ) -> Any:
        """Invoke a capability with the given input data.
        
        Args:
            id: Identifier of the capability to invoke
            input_data: Input data for the capability (either a dict or Pydantic model)
            context: Agent context object providing access to agent resources
            
        Returns:
            Any: Result of the capability invocation
            
        Raises:
            ValueError: If the capability is not found
            ValidationError: If input data fails validation against the input schema
        """
        pass
    
    @abstractmethod
    async def load_capabilities_from_config(self, config: Dict[str, Any]) -> None:
        """Load capability definitions from configuration.
        
        This method processes the declarative capability definitions from the
        agent's configuration and connects them to the registered handler functions.
        
        Args:
            config: Agent configuration dictionary containing capability definitions
            
        Raises:
            ValueError: If a required handler function is not registered
            ConfigurationError: If the configuration is invalid
        """
        pass
```

### Capability Handler Function Signature

Capability handler functions must follow a specific signature to be compatible with the capability registration system:

```python
async def capability_handler_function(
    input_data: InputModelType,
    context: AgentContext
) -> OutputModelType:
    """Handle a capability invocation.
    
    Args:
        input_data: Validated input data conforming to the input schema
        context: Agent context providing access to agent resources
        
    Returns:
        OutputModelType: Result conforming to the output schema
    """
    # Implementation here
    pass
```

Where:
- `InputModelType` is a Pydantic model class defining the input schema
- `OutputModelType` is a Pydantic model class defining the output schema
- `AgentContext` provides access to agent-specific resources

### AgentContext Object

The `AgentContext` object provides capability handlers with access to agent resources and services:

```python
class AgentContext:
    """Context object passed to capability handlers.
    
    Provides access to agent resources, state, and services.
    """
    
    @property
    def agent_id(self) -> str:
        """Get the unique identifier of the agent."""
        pass
        
    @property
    def session_id(self) -> Optional[str]:
        """Get the current session ID if available."""
        pass
    
    @property
    def logger(self) -> 'Logger':
        """Get the agent's logger."""
        pass
    
    @property
    def state_manager(self) -> 'StateManager':
        """Get the agent's state manager for accessing agent state."""
        pass
    
    @property
    def communication_manager(self) -> 'CommunicationManager':
        """Get the communication manager for sending messages."""
        pass
    
    @property
    def capability_manager(self) -> 'ICapabilityManager':
        """Get the capability manager for accessing other capabilities."""
        pass
    
    @property
    def knowledge_manager(self) -> 'IKnowledgeManager':
        """Get the knowledge manager for accessing knowledge bases."""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """Get the agent's configuration."""
        pass
    
    async def get_session_context(self) -> 'SessionContext':
        """Get the current session context for managing conversation history."""
        pass
```

### Integration with Message Handling

The capability system integrates with the agent's message handling system. When an internal message is received (after being processed by an `IMessageHandler`), it may be routed to invoke a registered capability:

1. The message payload may contain a `capability_id` field indicating which capability to invoke
2. The message protocol adapter may extract capability invocation details from protocol-specific message formats
3. The `invoke_capability` method of the `ICapabilityManager` is called with the appropriate input data
4. The result is converted back to the appropriate protocol-specific format using message adapters

This approach maintains clean separation between the agent's communication layer and reasoning layer, supporting OpenMAS's reasoning agnosticism.

### Complete Example: Registering and Using a Capability

Here's a complete example that demonstrates:
1. Defining input and output Pydantic models
2. Implementing a capability handler function
3. Registering the capability with the agent
4. How an incoming message might trigger the capability

```python
from pydantic import BaseModel, Field
from typing import List, Optional

# 1. Define input and output Pydantic models
class WeatherQueryInput(BaseModel):
    """Input model for the weather query capability."""
    location: str = Field(
        description="City name or geographic coordinates",
        examples=["San Francisco, CA", "37.7749,-122.4194"]
    )
    units: Optional[str] = Field(
        default="metric",
        description="Temperature units (metric or imperial)",
        examples=["metric", "imperial"]
    )
    forecast_days: Optional[int] = Field(
        default=1,
        description="Number of days to forecast (1-7)",
        ge=1,
        le=7
    )


class WeatherCondition(BaseModel):
    """Model representing weather conditions for a specific date."""
    date: str = Field(description="Date in ISO format (YYYY-MM-DD)")
    temperature: float = Field(description="Temperature in requested units")
    condition: str = Field(description="Weather condition description")
    humidity: int = Field(description="Humidity percentage")
    wind_speed: float = Field(description="Wind speed in km/h or mph depending on units")


class WeatherQueryOutput(BaseModel):
    """Output model for the weather query capability."""
    location: str = Field(description="The location that was queried")
    units: str = Field(description="Temperature units used (metric or imperial)")
    current_conditions: WeatherCondition = Field(description="Current weather conditions")
    forecast: Optional[List[WeatherCondition]] = Field(
        default=None,
        description="Weather forecast for requested days"
    )


# 2. Implement the capability handler function
async def get_weather_handler(
    input_data: WeatherQueryInput,
    context: AgentContext
) -> WeatherQueryOutput:
    """Handler for the get_weather capability.
    
    Args:
        input_data: Validated weather query parameters
        context: Agent context with access to resources
        
    Returns:
        WeatherQueryOutput: Weather data for the requested location
    """
    # Log the request
    context.logger.info(f"Weather requested for {input_data.location} in {input_data.units} units")
    
    # In a real implementation, this would call a weather service API
    # For this example, we'll return mock data
    
    # You could use the state manager to cache results
    cache_key = f"weather:{input_data.location}:{input_data.units}"
    cached_result = await context.state_manager.get(cache_key)
    
    if cached_result and not input_data.forecast_days > 1:
        context.logger.info(f"Returning cached weather data for {input_data.location}")
        return cached_result
    
    # Simulate API call to weather service
    # In a real implementation, this might use an HTTP client or dedicated SDK
    current = WeatherCondition(
        date="2025-05-28",
        temperature=22.5 if input_data.units == "metric" else 72.5,
        condition="Partly cloudy",
        humidity=65,
        wind_speed=10.0 if input_data.units == "metric" else 6.2
    )
    
    # Generate forecast if requested
    forecast = None
    if input_data.forecast_days > 1:
        forecast = [
            WeatherCondition(
                date=f"2025-05-{28 + i}",
                temperature=22.0 + i if input_data.units == "metric" else 72.0 + (i * 1.8),
                condition="Sunny" if i % 2 == 0 else "Cloudy",
                humidity=65 - (i * 2),
                wind_speed=(10.0 + i) if input_data.units == "metric" else (6.2 + (i * 0.6))
            )
            for i in range(1, input_data.forecast_days)
        ]
    
    # Create the result
    result = WeatherQueryOutput(
        location=input_data.location,
        units=input_data.units,
        current_conditions=current,
        forecast=forecast
    )
    
    # Cache the result for future requests
    if not input_data.forecast_days > 1:
        await context.state_manager.set(cache_key, result, ttl_seconds=1800)  # 30 minute cache
    
    return result


# 3. Register the capability with the agent during initialization
class WeatherAgent:
    async def initialize(self):
        # Other initialization code...
        
        # Register the weather capability
        await self.capability_manager.register_capability(
            id="get_weather",
            name="Get Weather",
            description="Retrieves current weather conditions and optional forecast for a location",
            handler_function=get_weather_handler,
            input_schema=WeatherQueryInput,
            output_schema=WeatherQueryOutput,
            version="1.0",
            protocol_specific_names={
                "a2a": "getWeatherInfo",     # Name in A2A protocol
                "mcp": "get_weather_data",  # Name in MCP protocol
                "http": "weather"           # Name in HTTP API
            },
            examples=[
                {
                    "input": {"location": "London, UK", "units": "metric"},
                    "output": {
                        "location": "London, UK",
                        "units": "metric",
                        "current_conditions": {
                            "date": "2025-05-28",
                            "temperature": 18.5,
                            "condition": "Rainy",
                            "humidity": 80,
                            "wind_speed": 15.0
                        }
                    }
                }
            ]
        )
        
        # Load capabilities defined in configuration
        await self.capability_manager.load_capabilities_from_config(self.config)


# 4. Example of how an incoming message might trigger this capability

# A2A Protocol Example - receives a JSON payload
async def handle_a2a_message(message):
    # Extract capability invocation from A2A message format
    if message.type == "function" and message.function.name == "getWeatherInfo":
        # Convert A2A parameters to internal format
        input_data = {
            "location": message.function.parameters.get("location"),
            "units": message.function.parameters.get("units", "metric"),
            "forecast_days": message.function.parameters.get("days", 1)
        }
        
        # Create agent context for this invocation
        context = create_agent_context(message.session_id)
        
        # Invoke the capability
        result = await capability_manager.invoke_capability(
            id="get_weather",
            input_data=input_data,
            context=context
        )
        
        # Convert result back to A2A format
        return create_a2a_response(result)

# MCP Protocol Example - Tool calling format
async def handle_mcp_message(message):
    if message.type == "tool_call" and message.name == "get_weather_data":
        # Extract parameters from MCP tool call
        params = message.parameters
        
        # Create agent context
        context = create_agent_context(message.session_id)
        
        # Invoke capability
        result = await capability_manager.invoke_capability(
            id="get_weather",
            input_data=params,
            context=context
        )
        
        # Return result in MCP format
        return create_mcp_tool_response(result)
```

This example demonstrates:

1. **Pydantic Models**: Defining structured input and output schemas with field descriptions, examples, and validation constraints
2. **Handler Function**: Implementing an asynchronous handler that processes the input and returns a validated output
3. **Capability Registration**: Registering the capability with a clear ID, descriptive metadata, and protocol-specific names
4. **Protocol Integration**: How different protocol adapters might extract capability invocation details and route them to the handler

### Core Capability Definition

The `core` section defines protocol-agnostic capabilities that can be exposed through any supported protocol. Each capability has:

- **Unique Identifier** (`id`) - Used for internal referencing and tracking
- **Human-Readable Name** (`name`) - Used for display in UIs and documentation
- **Description** - Detailed explanation of what the capability does
- **Parameters Schema** - JSON Schema defining the input format
- **Returns Schema** - JSON Schema defining the output format
- **Examples** - Sample invocations to demonstrate usage

### Protocol Mapping

The `protocol_mapping` section defines how core capabilities are represented in different protocols:

- **A2A Protocol** - Maps to agent card capabilities format
- **MCP Protocol** - Maps to tool definitions format
- **HTTP Protocol** - Maps to RESTful endpoints
- **MQTT Protocol** - Maps to MQTT topics
- **gRPC Protocol** - Maps to gRPC service definitions

This mapping allows the same capability to be invoked through any supported protocol while maintaining the semantics of the capability.

```yaml
# Example multi-protocol capability mapping
multi_protocol_capabilities:
  core:
    - id: "weather_query"
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
      capability_format: "agent_card"
      mappings:
        - core_id: "weather_query"
          a2a_capability_name: "get_weather"
          content_type: "application/json"
    
    mcp:
      capability_format: "tool_definition"
      mappings:
        - core_id: "weather_query"
          mcp_tool_name: "getWeather"
          requires_confirmation: false
    
    http:
      capability_format: "rest_endpoint"
      mappings:
        - core_id: "weather_query"
          method: "GET"
          path: "/api/weather"
          query_parameters: ["location"]
```

### Capability Exposure

The `capability_exposure` section controls which capabilities are exposed on which protocols:

- **Default Exposure** - Controls the default visibility level
- **Capability Filter** - Fine-grained control over which capabilities are exposed on which protocols

```yaml
# Example capability exposure configuration
capability_exposure:
  default_exposure: "selective"
  capability_filter:
    a2a: ["weather_query", "location_search"]
    mcp: ["weather_query", "forecast_query"]
    http: ["weather_query"]
```

This allows agents to selectively expose capabilities based on protocol characteristics, security considerations, or deployment contexts.

### Runtime Multi-Protocol Support

At runtime, the agent automatically translates between protocol-specific formats using the mappings defined in the configuration. This enables:

1. **Protocol-Agnostic Implementation** - Developers implement capabilities once, independently of protocols
2. **Dynamic Protocol Selection** - Clients can use whichever protocol best suits their needs
3. **Unified Capability Management** - Centralized definition and management of capabilities
4. **Seamless Protocol Integration** - Support for new protocols without changing capability implementations

## Usage Examples
```python
# Example agent configuration and usage
from openmas.agent import Agent
from openmas.reasoning import BDIReasoner, LLMReasoner, HybridReasoner

# Creating an agent with hybrid reasoning
agent = Agent(
    name="customer_support_agent",
    reasoning=HybridReasoner(
        coordination="sequential",
        reasoners=[
            # Use rule-based reasoning for policy checks
            BDIReasoner(
                beliefs_file="support_policies.json",
                desires_file="support_goals.json",
                plans_file="support_procedures.json"
            ),
            # Use LLM for natural language understanding
            LLMReasoner(
                model="claude-3-sonnet-20240229",
                prompt_template="customer_support_reasoning"
            )
        ]
    ),
    capabilities=[
        "ticket_creation",
        "knowledge_base_search",
        "escalation_management"
    ]
)

# Start the agent with role-based activation
agent.activate_role("first_level_support")
agent.start()
``` 