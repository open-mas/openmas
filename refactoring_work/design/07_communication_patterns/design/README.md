# Communication Patterns Design

## Overview

Communication patterns in OpenMAS provide standardized, protocol-agnostic abstractions for message exchange between agents. These patterns enable consistent communication semantics regardless of the underlying protocol implementation, allowing OpenMAS to maintain its core principles of protocol independence and reasoning agnosticism.

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
├───────────────┼───────────────────────────────────┼───────────────────────┤
│               │                                   │                       │
│  Defines      │  Implements                       │  Provides             │
│  agent        │  message exchange                 │  protocol-specific    │
│  relationships│  semantics                        │  transport            │
│               │                                   │                       │
└───────────────┴───────────────────────────────────┴───────────────────────┘
```

Communication patterns bridge between the logical relationships defined by agent topologies and the physical communication mechanisms provided by protocol implementations.

## Pattern Architecture

Each communication pattern is composed of these key components:

```
┌────────────────────────────────────────────────┐
│ Communication Pattern                          │
│                                                │
│  ┌────────────────────────────────────────┐    │
│  │ Pattern Definition                     │    │
│  │ - Name                                 │    │
│  │ - Semantics                            │    │
│  │ - Participants                         │    │
│  │ - Message Flow                         │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  ┌────────────────────────────────────────┐    │
│  │ Protocol Adaptations                   │    │
│  │ - A2A                                  │    │
│  │ - MCP                                  │    │
│  │ - HTTP                                 │    │
│  │ - MQTT                                 │    │
│  │ - gRPC                                 │    │
│  └────────────────────────────────────────┘    │
│                                                │
│  ┌────────────────────────────────────────┐    │
│  │ Configuration Schema                   │    │
│  │ - Pattern Options                      │    │
│  │ - Protocol-Specific Options            │    │
│  │ - Validation Rules                     │    │
│  └────────────────────────────────────────┘    │
│                                                │
└────────────────────────────────────────────────┘
```

## Core Components

### Pattern Registry

Central repository for registered patterns:

```python
class PatternRegistry:
    """Central registry for communication patterns."""

    def __init__(self):
        """Initialize the pattern registry."""
        self._patterns = {}

    def register(self, pattern_name, pattern_class):
        """Register a pattern."""
        self._patterns[pattern_name] = pattern_class
        return self

    def get(self, pattern_name):
        """Get a pattern by name."""
        return self._patterns.get(pattern_name)

    def list_patterns(self):
        """List all registered patterns."""
        return list(self._patterns.keys())
```

### Pattern Factory

Factory for creating pattern instances:

```python
class PatternFactory:
    """Factory for creating pattern instances."""

    def __init__(self, registry, communicator_factory):
        """Initialize the pattern factory."""
        self._registry = registry
        self._communicator_factory = communicator_factory

    def create(self, pattern_name, config):
        """Create a pattern instance."""
        pattern_class = self._registry.get(pattern_name)
        if not pattern_class:
            raise ValueError(f"Unknown pattern: {pattern_name}")

        # Create protocol-specific communicator
        protocol = config.get("protocol", "a2a")
        communicator = self._communicator_factory.create(protocol, config.get("protocol_config", {}))

        # Create and return the pattern instance
        return pattern_class(communicator, config)
```

### Base Pattern

Abstract base class for all patterns:

```python
class BasePattern:
    """Base class for all communication patterns."""

    def __init__(self, communicator, config):
        """Initialize with a communicator and configuration."""
        self.communicator = communicator
        self.config = config

    async def initialize(self):
        """Initialize the pattern."""
        # Implement in subclasses
        pass

    async def shutdown(self):
        """Shut down the pattern."""
        # Implement in subclasses
        pass

    def get_config(self):
        """Get the pattern configuration."""
        return self.config
```

### Protocol Adapter

Base class for protocol-specific adapters:

```python
class ProtocolAdapter:
    """Base class for protocol adapters."""

    def __init__(self, protocol_name):
        """Initialize with protocol name."""
        self.protocol_name = protocol_name

    async def adapt_outgoing(self, message, pattern_name):
        """Adapt an outgoing message to this protocol."""
        raise NotImplementedError

    async def adapt_incoming(self, protocol_message, pattern_name):
        """Adapt an incoming protocol message to the pattern format."""
        raise NotImplementedError
```

## Pattern Lifecycle

Communication patterns follow this lifecycle:

1. **Registration** - Pattern classes are registered with the registry
2. **Configuration** - Patterns are configured via the unified schema
3. **Creation** - Pattern instances are created by the factory
4. **Initialization** - Pattern resources are initialized
5. **Operation** - Pattern is used for communication
6. **Shutdown** - Pattern resources are released

## Pattern Configuration

Patterns are configured through the unified configuration schema:

```yaml
# Pattern configuration example
communication_patterns:
  request_response:
    enabled: true
    timeout: 30
    retry:
      attempts: 3
      interval: 5
    protocol_adaptations:
      a2a:
        capability_name: "request_response"
      http:
        method: "POST"
        response_codes: [200, 201]
      mqtt:
        request_topic: "requests/{agent_id}"
        response_topic: "responses/{agent_id}"
```

## Protocol Adaptation

Each pattern defines how it adapts to different protocols:

```yaml
request_response:
  protocol_adaptations:
    a2a:
      capability_name: "request"
      response_capability: "response"

    mcp:
      tool_name: "request"

    http:
      method: "POST"
      response_codes: [200, 201]

    mqtt:
      request_topic: "requests/{agent_id}"
      response_topic: "responses/{agent_id}"

    grpc:
      service: "RequestService"
      method: "MakeRequest"
```

## Reasoning Agnosticism

The communication patterns system maintains OpenMAS's reasoning agnosticism through:

1. **Semantic Focus** - Patterns define semantics, not reasoning logic
2. **Protocol Independence** - Patterns work with any protocol
3. **Content Agnosticism** - Patterns don't interpret message content
4. **Capability Abstraction** - Patterns expose abstract capabilities
5. **Event-Based Interfaces** - Patterns use event-based programming model

This enables agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to communicate using the same patterns consistently.

## Composability

Patterns can be composed to create complex communication flows:

```python
# Create a pipeline of request-response and delegation patterns
pipeline = CommunicationPipeline([
    factory.create("request_response", config1),
    factory.create("delegation", config2)
])

# Execute the pipeline
result = await pipeline.execute(message)
```

## Extension Points

The communication patterns system offers these extension points:

1. **Custom Patterns** - Define new pattern types
2. **Protocol Adapters** - Add adapters for new protocols
3. **Middleware** - Add processing middleware for patterns
4. **Transformers** - Add message transformers
5. **Validators** - Add message validators

### Custom Pattern Example

```python
from openmas.communication.patterns import BasePattern, register_pattern

@register_pattern("custom_pattern")
class CustomPattern(BasePattern):
    """A custom communication pattern."""

    def __init__(self, communicator, config):
        """Initialize with configuration."""
        super().__init__(communicator, config)
        self.custom_option = config.get("custom_option", "default")

    async def initialize(self):
        """Initialize the pattern."""
        # Register event handlers
        self.communicator.on_message(self._handle_message)

    async def send_message(self, recipient, content):
        """Send a message using this pattern."""
        # Adapt the message based on protocol
        adapted = await self.communicator.adapter.adapt_outgoing(
            {
                "recipient": recipient,
                "content": content,
                "pattern": "custom_pattern"
            },
            "custom_pattern"
        )

        # Send the adapted message
        return await self.communicator.send(adapted)

    async def _handle_message(self, message):
        """Handle an incoming message."""
        # Process the message according to pattern semantics
        return {"status": "processed"}
```

## References

For details on specific patterns, see:

- [Request-Response Pattern](../patterns/request_response.md)
- [Publish-Subscribe Pattern](../patterns/publish_subscribe.md)
- [Delegation Pattern](../patterns/delegation.md)
- [Pipeline Pattern](../patterns/pipeline.md)
- [Event-Based Pattern](../patterns/event_based.md)
- [Streaming Pattern](../patterns/streaming.md)
