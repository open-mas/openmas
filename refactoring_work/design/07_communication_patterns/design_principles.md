# Communication Patterns Design

## Overview

Communication patterns in OpenMAS provide standardized, protocol-agnostic abstractions for message exchange between agents. These patterns enable consistent communication semantics regardless of the underlying protocol implementation, allowing OpenMAS to maintain its core principle of protocol independence.

## Design Principles

The Communication Patterns system is designed according to these core principles:

1. **Protocol Agnosticism** - Patterns work consistently across all protocols
2. **Reasoning Independence** - Patterns are independent of agent reasoning approaches
3. **Topology Alignment** - Patterns align with and complement agent topology structures
4. **Configuration-Driven** - Patterns are defined through configuration rather than code
5. **Extensibility** - The pattern system supports custom and specialized patterns
6. **Composability** - Patterns can be composed to create complex communication flows

## Architectural Position

Communication patterns sit at a key position in the OpenMAS architecture:

```
┌───────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│                          OpenMAS Architecture                             │
│                                                                           │
├───────────────┬───────────────────────────────────┬───────────────────────┤
│               │                                   │                       │
│  Agent        │  Communication                    │  Protocol Layer       │
│  Topologies   │  Patterns                         │  (Communicators)      │
│               │                                   │                       │
│  ┌─────────┐  │  ┌─────────────────┐             │  ┌─────────────────┐  │
│  │Defines  │  │  │Defines          │             │  │Implements       │  │
│  │How      │  │  │How              │             │  │How              │  │
│  │Agents   │◄─┼──┼─Are Applied to──┼─────────────┼──┼─Enabled Through─┤  │
│  │Organize │  │  │Messages         │             │  │Protocols        │  │
│  └─────────┘  │  │Exchange         │             │  └─────────────────┘  │
│               │  └─────────────────┘             │                       │
│  Reasoning    │                                   │                       │
│  Agnostic     │  Protocol                         │  Protocol-Specific    │
│               │  Agnostic                         │  Implementation       │
│               │                                   │                       │
└───────────────┴───────────────────────────────────┴───────────────────────┘
```

## Core Components

The Communication Patterns system consists of these key components:

### 1. Pattern Registry

The Pattern Registry maintains the catalog of available communication patterns:

```python
class PatternRegistry:
    """Registry of available communication patterns."""
    
    def __init__(self):
        """Initialize the pattern registry."""
        self.patterns = {}
        
    def register_pattern(self, pattern_type, pattern_class):
        """Register a pattern implementation."""
        self.patterns[pattern_type] = pattern_class
        
    def get_pattern(self, pattern_type):
        """Get a pattern implementation by type."""
        if pattern_type not in self.patterns:
            raise ValueError(f"Unknown pattern type: {pattern_type}")
        return self.patterns[pattern_type]
        
    def list_patterns(self):
        """List all available patterns."""
        return list(self.patterns.keys())
```

### 2. Pattern Factory

The Pattern Factory creates pattern instances from configuration:

```python
class PatternFactory:
    """Factory for creating pattern instances."""
    
    def __init__(self, registry, communicator_factory):
        """Initialize the pattern factory."""
        self.registry = registry
        self.communicator_factory = communicator_factory
        
    def create_pattern(self, config, agent_context):
        """Create a pattern instance from configuration."""
        pattern_type = config.get("type")
        pattern_options = config.get("options", {})
        
        # Get the pattern class from the registry
        pattern_class = self.registry.get_pattern(pattern_type)
        
        # Create the pattern instance
        pattern = pattern_class(pattern_options, agent_context)
        
        # Set up protocol adapters
        protocol_adaptations = config.get("protocol_adaptations", {})
        for protocol, adaptation_config in protocol_adaptations.items():
            adapter = self._create_protocol_adapter(protocol, adaptation_config)
            pattern.register_protocol_adapter(protocol, adapter)
            
        return pattern
        
    def _create_protocol_adapter(self, protocol, config):
        """Create a protocol adapter for a pattern."""
        adapter_class = self._get_adapter_class(protocol)
        return adapter_class(config)
```

### 3. Pattern Base Class

The Pattern base class defines the common interface for all patterns:

```python
class Pattern:
    """Base class for communication patterns."""
    
    def __init__(self, options, agent_context):
        """Initialize the pattern."""
        self.options = options
        self.agent_context = agent_context
        self.protocol_adapters = {}
        
    def register_protocol_adapter(self, protocol, adapter):
        """Register a protocol adapter."""
        self.protocol_adapters[protocol] = adapter
        
    def get_protocol_adapter(self, protocol):
        """Get the adapter for a specific protocol."""
        if protocol not in self.protocol_adapters:
            raise ValueError(f"No adapter registered for protocol: {protocol}")
        return self.protocol_adapters[protocol]
        
    async def validate_message(self, message):
        """Validate that a message conforms to this pattern."""
        raise NotImplementedError("Subclasses must implement validate_message")
        
    async def process_incoming(self, message, protocol):
        """Process an incoming message according to this pattern."""
        adapter = self.get_protocol_adapter(protocol)
        return await adapter.process_incoming(message, self)
        
    async def prepare_outgoing(self, message, protocol):
        """Prepare an outgoing message according to this pattern."""
        adapter = self.get_protocol_adapter(protocol)
        return await adapter.prepare_outgoing(message, self)
```

### 4. Protocol Adapter

The Protocol Adapter adapts patterns to specific protocols:

```python
class ProtocolAdapter:
    """Adapts a pattern to a specific protocol."""
    
    def __init__(self, config):
        """Initialize the adapter."""
        self.config = config
        
    async def process_incoming(self, message, pattern):
        """Process an incoming message."""
        raise NotImplementedError("Subclasses must implement process_incoming")
        
    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing message."""
        raise NotImplementedError("Subclasses must implement prepare_outgoing")
```

## Pattern Lifecycle

Communication patterns have a well-defined lifecycle:

1. **Registration** - Patterns are registered with the PatternRegistry at startup
2. **Configuration** - Patterns are configured through the unified configuration schema
3. **Instantiation** - Pattern instances are created by the PatternFactory
4. **Adaptation** - Protocol-specific adapters are attached to pattern instances
5. **Usage** - Patterns process incoming and prepare outgoing messages
6. **Termination** - Patterns are cleaned up when no longer needed

## Protocol Adaptation

A key capability of the Communication Patterns system is protocol adaptation. Each pattern defines how it maps to different protocols:

### A2A Protocol Adaptation

Patterns map to A2A protocol capabilities:

```yaml
# Example: Request-Response pattern for A2A
request_response:
  protocol_adaptations:
    a2a:
      use_tasks: true
      task_type: "request_response"
      response_timeout: 30000
```

### MCP Protocol Adaptation

Patterns map to MCP protocol capabilities:

```yaml
# Example: Request-Response pattern for MCP
request_response:
  protocol_adaptations:
    mcp:
      use_function_calls: true
      function_name: "handle_request"
      async_response: false
```

### HTTP Protocol Adaptation

Patterns map to HTTP protocol capabilities:

```yaml
# Example: Request-Response pattern for HTTP
request_response:
  protocol_adaptations:
    http:
      method: "POST"
      response_codes: [200, 201]
      content_type: "application/json"
```

## Relationship to Topology

Communication patterns are closely integrated with agent topologies. Each relationship in a topology specifies which pattern(s) to use:

```yaml
# Example: Topology with pattern assignments
topology:
  pattern: "centralized"
  roles:
    types:
      - name: "orchestrator"
      - name: "worker"
  relationships:
    types:
      - name: "orchestrator_to_worker"
        communication_pattern: "request_response"
      - name: "worker_to_worker"
        communication_pattern: "publish_subscribe"
```

## Relationship to Communicators

Communication patterns work with protocol-specific communicators:

1. **Pattern Configuration**: Defines the semantic behavior
2. **Protocol Adaptation**: Maps semantics to protocol capabilities
3. **Communicator Implementation**: Handles protocol-specific details

```yaml
# Example: Agent with communicator and pattern
agents:
  travel_coordinator:
    communicator_type: "a2a"
    communicator_options:
      server_mode: true
    patterns:
      request_response:
        options:
          timeout: 30000
      publish_subscribe:
        options:
          topic_prefix: "travel"
```

## Reasoning Agnosticism

Communication patterns maintain OpenMAS's reasoning agnosticism by:

1. **Focusing on Message Exchange**: Patterns define how messages are exchanged, not what they contain
2. **Protocol Abstraction**: Patterns hide protocol details from reasoning components
3. **Body vs. Brain Separation**: Patterns are part of the agent's "body" (communication infrastructure)

This separation ensures that the same patterns can be used with any reasoning approach:

- Rule-based reasoning
- BDI (Belief-Desire-Intention) architecture
- LLM-based reasoning
- Knowledge Representation and Reasoning (KR&R)
- Hybrid approaches

## Configuration Schema

Communication patterns use the unified configuration schema:

```yaml
# Top-level patterns configuration
communication_patterns:
  request_response:
    options:
      timeout: 30000
      retry:
        attempts: 3
        backoff: "exponential"
    protocol_adaptations:
      a2a:
        use_streaming: false
      http:
        method: "POST"
  
  publish_subscribe:
    options:
      delivery_guarantee: "at_least_once"
    protocol_adaptations:
      mqtt:
        qos_level: 1
        retain: true
```

## Security Considerations

Communication patterns incorporate security considerations:

1. **Authentication Integration**: Patterns work with authentication providers
2. **Authorization Checks**: Patterns can perform authorization checks
3. **Encryption Support**: Patterns support end-to-end encryption where needed
4. **Rate Limiting**: Patterns can implement rate limiting
5. **Validation**: Patterns validate messages before processing

```yaml
# Example: Secure pattern configuration
request_response:
  options:
    security:
      require_authentication: true
      authorization_profile: "standard_access"
      encrypt_payload: true
      rate_limit:
        max_requests: 100
        period_seconds: 60
```

## Observability

Communication patterns support observability:

1. **Metrics**: Patterns collect and expose metrics
2. **Logging**: Patterns log important events
3. **Tracing**: Patterns support distributed tracing
4. **Debugging**: Patterns provide debugging information

```yaml
# Example: Observability configuration
request_response:
  options:
    observability:
      metrics_enabled: true
      log_level: "info"
      tracing_enabled: true
      capture_message_samples: true
```

## Pattern Engine API

The Communication Pattern Engine provides the core interfaces for managing and executing patterns in OpenMAS. The engine implements the architectural components described in this document through these key interfaces:

- **IPatternEngine**: Central interface for pattern registration, discovery, validation, and execution
- **IPatternInstance**: Interface for stateful pattern instances that maintain state across multiple messages
- **Pattern Data Models**: Comprehensive Pydantic models for pattern definitions, configurations, and results

For detailed API specifications, see [Pattern Engine API](./pattern_engine_api.md).

The Pattern Engine API ensures:
1. **Protocol Agnosticism**: Patterns work consistently across all protocols through SIMF integration
2. **Reasoning Independence**: Clean separation between pattern logic and reasoning components
3. **Configuration-Driven**: All pattern behavior configurable through unified schema
4. **Extensibility**: Support for custom patterns and protocol adaptations
5. **Observability**: Built-in metrics, tracing, and logging for pattern execution

## Future Directions

The Communication Patterns system will evolve with these future directions:

1. **Advanced Composition**: More sophisticated pattern composition
2. **Machine Learning Integration**: ML-enhanced pattern selection
3. **Self-Adaptive Patterns**: Patterns that adapt based on conditions
4. **Cross-Pattern Optimization**: Optimizing across multiple patterns
5. **Pattern Libraries**: Reusable pattern collections for common scenarios
