# OpenMAS Topology Patterns

## Overview

This directory contains detailed specifications for the standard topology patterns supported by OpenMAS. Each pattern defines a specific organizational structure for agent collaboration while maintaining OpenMAS's core principles of reasoning agnosticism and protocol independence.

## Available Patterns

OpenMAS provides these standard topology patterns:

| Pattern | Description | Key Use Cases |
|---------|-------------|---------------|
| [Centralized (Hub-Spoke)](./centralized.md) | Central orchestrator with worker agents | Task delegation, workflow coordination, central control systems |
| [Hierarchical (Tree)](./hierarchical.md) | Multi-level organization with delegation | Enterprise systems, organizational hierarchies, multi-level decision making |
| [Peer-to-Peer](./peer_to_peer.md) | Direct communication between equal agents | Distributed systems, collaborative problem-solving, resilient networks |
| [Mesh](./mesh.md) | Fully connected agent network | High-availability systems, redundant communication, complex coordination |
| [Hybrid](./hybrid.md) | Combinations of multiple patterns | Domain-spanning applications, adaptive workflows, complex organizations |

## Pattern Documentation Structure

Each pattern document follows a consistent structure:

1. **Overview** - High-level pattern description
2. **Key Components** - Core elements in the pattern
3. **Communication Flow** - How messages flow between agents
4. **Implementation Considerations** - Guidelines for effective implementation
5. **Use Cases** - Suitable application scenarios
6. **Advantages and Limitations** - Trade-offs and constraints
7. **Reasoning Agnosticism** - How the pattern maintains separation of communication and reasoning
8. **Configuration Schema** - Reference to the unified configuration schema

## Configuration

All topology patterns are configured through the unified configuration schema, which serves as the single source of truth for all OpenMAS configuration. For the complete and authoritative schema definition, see the [Agent Configuration Schema](/03_configuration/schema/agents.md#topology-configuration).

## Reasoning Agnosticism

The topology patterns are designed to maintain strict separation between agent organization (the "body") and reasoning approaches (the "brain"). This allows:

- The same topology to be implemented with different reasoning approaches
- Agents with different reasoning systems to interact within the same topology
- Reasoning approaches to be changed without altering the organizational structure

This distinctive reasoning agnosticism is a key differentiator for OpenMAS compared to other agent frameworks.

## Protocol Independence

These topology patterns are protocol-independent by design, working across all supported protocols (A2A, MCP, HTTP, MQTT, gRPC) through consistent interfaces and abstractions. The same topology configuration can be used regardless of the underlying communication protocol.
