# OpenMAS Agent Topology Implementation

## Overview

This directory contains agent-specific implementation details for topology patterns in OpenMAS. For the authoritative documentation on topology concepts, patterns, and architecture, please refer to the [Topology Documentation](/08_topology/README.md).

This documentation focuses on how agents implement and interact with topologies, while the core architectural concepts and pattern definitions are documented in the dedicated [Topology System](/08_topology/) directory.

## Key Capabilities

The topology system offers these core capabilities:

1. **Standardized Patterns** - Common organizational structures for agent collaboration
2. **Role Definitions** - Clear agent role specifications within topologies
3. **Relationship Management** - Explicit agent relationship definitions
4. **Protocol Independence** - Consistent topology interfaces across all communication protocols
5. **Reasoning Agnosticism** - Complete separation of agent organization from reasoning approaches
6. **Configuration-Driven** - Simple topology setup through the unified schema

## Topology Patterns

OpenMAS supports several standard topology patterns. This directory contains agent-specific implementation details, while the core pattern definitions are in the [Topology Patterns](/08_topology/patterns/) directory.

1. [**Centralized (Hub-Spoke)**](./patterns/pattern_centralized.md) - Central coordinating agent with worker agents ([Core Documentation](/08_topology/patterns/centralized.md))
2. [**Hierarchical (Tree)**](./patterns/pattern_hierarchical.md) - Multi-level organization with authority delegation ([Core Documentation](/08_topology/patterns/hierarchical.md))
3. [**Peer-to-Peer**](./patterns/pattern_peer_to_peer.md) - Direct communication between equal agents ([Core Documentation](/08_topology/patterns/peer_to_peer.md))
4. [**Mesh**](./patterns/pattern_mesh.md) - Fully connected agent network ([Core Documentation](/08_topology/patterns/mesh.md))
5. [**Hybrid**](./patterns/pattern_hybrid.md) - Combination of multiple topology patterns ([Core Documentation](/08_topology/patterns/hybrid.md))

Each pattern has specific use cases, advantages, and limitations that make it suitable for different scenarios. The implementation details in this directory focus on how agents instantiate these patterns.

## Reasoning Agnosticism

The topology patterns maintain OpenMAS's distinctive reasoning agnosticism through:

1. **Structure-Reasoning Separation** - Topology defines organization, not reasoning approach
2. **Role-Based Design** - Agents are defined by their roles in the topology, not their reasoning mechanisms
3. **Protocol-Independent Communication** - Message exchange is defined by the topology, not the reasoning approach
4. **Capability-Based Interaction** - Agents interact based on capabilities, regardless of reasoning implementation

This separation allows the same topology to be implemented with various reasoning approaches (rule-based, BDI, LLM, hybrid) while maintaining consistent organizational structure.

## Configuration

Agent topologies are configured through the unified configuration schema. For the complete and authoritative schema definition, see:

- [Agent Configuration Schema](/03_configuration/schema/agents.md#topology-configuration)
- [Topology Configuration Documentation](/08_topology/configuration/README.md)

This directory focuses on the agent-specific aspects of applying the configuration.

## Integration with Other Components

The topology system integrates with several other OpenMAS components. This directory focuses on the agent implementation aspects of these integrations, while the comprehensive integration architecture is documented in the [Topology Integration](/08_topology/integration.md) documentation.

1. **Agent Framework** - How agents implement topology roles and relationships
2. **Communication Patterns** - How agents use patterns within topologies
3. **Protocol Layer** - Protocol-specific agent implementations
4. **Session Management** - Managing agent state in topology contexts

For detailed agent implementation guidelines and examples, refer to:
- [Agent Implementation Examples](./implementation_examples.md)
- [Topology Integration Architecture](/08_topology/integration.md)
- [Architecture Patterns](/01_architecture/architectural_patterns.md)
- [Runtime Architecture](/01_architecture/runtime_architecture.md)
