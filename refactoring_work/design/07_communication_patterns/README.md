# OpenMAS Communication Patterns

## Overview

Communication patterns in OpenMAS define standardized message exchange methods between agents. They provide a protocol-agnostic abstraction layer that ensures consistent communication regardless of the underlying protocol implementation.

## Key Capabilities

The Communication Patterns system offers these core capabilities:

1. **Standardized Interactions** - Pre-defined patterns for common communication scenarios
2. **Protocol Independence** - Consistent patterns across all protocols (A2A, MCP, HTTP, MQTT, gRPC)
3. **Topology Integration** - Seamless mapping between agent relationships and communication methods
4. **Reasoning Agnosticism** - Clear separation from agent reasoning and implementation
5. **Configuration-Driven** - Simple configuration through the unified schema
6. **Extensibility** - Support for custom patterns and adaptations

## Documentation Structure

This directory contains comprehensive documentation on the OpenMAS Communication Patterns system:

| Document | Description |
|----------|-------------|
| [Design Principles](./design_principles.md) | Comprehensive architecture and design principles |
| [Pattern Engine API](./pattern_engine_api.md) | Core interfaces for pattern management and execution |
| [Protocol Adaptations](./protocol_adaptations.md) | How patterns adapt to different protocols |
| [Extending Patterns](./extending_patterns.md) | Guide to extending patterns with custom implementations |
| [Pattern Versioning](./pattern_versioning.md) | Approach to versioning and evolving patterns |

### Protocol Implementation References

For protocol-specific implementations of these patterns, please refer to:

- [Protocol Documentation](/02_protocols/) - Protocol-specific implementation details

### Pattern Specifications

Detailed documentation for each standardized pattern:

| Pattern | Description |
|---------|-------------|
| [Request-Response](./patterns/request_response.md) | Synchronous request and response pattern |
| [Publish-Subscribe](./patterns/publish_subscribe.md) | Asynchronous broadcasting pattern |
| [Event-Based](./patterns/event_based.md) | State change notification pattern |
| [Streaming](./patterns/streaming.md) | Continuous data flow pattern |
| [Pipeline](./patterns/pipeline_part1.md) | Sequential processing pattern (Part 1) |
| [Pipeline Part 2](./patterns/pipeline_part2.md) | Sequential processing pattern (Part 2) |
| [Pipeline Part 3](./patterns/pipeline_part3.md) | Sequential processing pattern (Part 3) |
| [Pipeline Part 4](./patterns/pipeline_part4.md) | Sequential processing pattern (Part 4) |
| [Delegation](./patterns/delegation.md) | Authority transfer pattern (Part 1) |
| [Delegation Part 2](./patterns/delegation_part2.md) | Authority transfer pattern (Part 2) |

### Examples

Example configurations and usage patterns:

| Document | Description |
|----------|-------------|
| [Basic Pattern Examples](./examples/basic_patterns.md) | Simple pattern configuration examples |
| [Advanced Pattern Examples (Part 1)](./examples/advanced_patterns_part1.md) | Complex pattern integration examples |
| [Advanced Pattern Examples (Part 2)](./examples/advanced_patterns_part2.md) | Advanced multi-pattern integration scenarios |

## Related Documentation

- **Architecture**: See [Communication Patterns Design](/01_architecture/communication_patterns_design.md) for high-level design principles.
- **Configuration**: See [Communication Patterns Schema](/03_configuration/schema/communication_patterns.md) for configuration details.
- **Topology Integration**: See [Topology Integration](./topology_integration.md) for how patterns integrate with agent topologies.
- **Protocol Adaptations**: See individual protocol documentation in [Protocols](/02_protocols/) for protocol-specific implementations.

## Implementation Classes

The patterns are implemented through these components:

1. **PatternRegistry** - Central registry of available patterns
2. **PatternFactory** - Creates pattern instances from configuration
3. **PatternImplementation** - Base class for pattern implementations
4. **ProtocolAdapter** - Adapts patterns to specific protocols

## Reasoning Agnosticism

The Communication Patterns system maintains OpenMAS's reasoning agnosticism by:

1. **Protocol Abstraction** - Separating how agents communicate from what they communicate
2. **Implementation Independence** - Patterns work with any agent implementation
3. **Body vs. Brain Separation** - Clear division between communication infrastructure and reasoning

This enables agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to communicate seamlessly using the same patterns.
