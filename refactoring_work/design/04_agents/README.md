# OpenMAS Agent Framework

## Overview

This directory contains documentation for the OpenMAS Agent Framework, which provides the core components for defining, configuring, and managing agents with reasoning agnosticism. The framework enables agents with different reasoning approaches to operate within a unified system while maintaining consistent communication capabilities.

## Key Capabilities

The OpenMAS Agent Framework provides these core capabilities:

1. **Reasoning Agnosticism** - Clear separation between communication infrastructure ("body") and reasoning approaches ("brain")
2. **Multi-Protocol Support** - Agents can communicate via multiple protocols (A2A, MCP, HTTP, etc.)
3. **Capability Management** - Standardized capability definition, registration, and discovery
4. **Session Lifecycle** - Consistent session creation, management, and termination
5. **Context Persistence** - State management across agent interactions
6. **Topology Integration** - Support for various agent organization patterns

## Agent Reasoning Approaches

OpenMAS supports multiple reasoning approaches within the same framework:

### 1. Rule-Based Reasoning

Simple rule-based agents that use conditional logic for decision-making:
- Pattern matching
- Trigger-action rules
- Decision tables

### 2. BDI Architecture

Belief-Desire-Intention architecture for cognitive agents:
- Belief management
- Goal representation
- Plan selection and execution

### 3. Knowledge Representation & Reasoning (KR&R)

Sophisticated knowledge-based reasoning:
- Multiple knowledge representation formalisms
- Various reasoning mechanisms
- Knowledge management capabilities

### 4. LLM-Based Reasoning

Language Model driven reasoning:
- Prompt-based reasoning
- Tool usage capabilities
- Memory and retrieval augmentation

### 5. Hybrid Reasoning

Combinations of multiple reasoning approaches:
- Rule-LLM hybrids
- BDI-LLM integration
- Symbolic-neural approaches

## Documentation Structure

This directory contains comprehensive documentation on the OpenMAS Agent Framework:

| Document | Description |
|----------|-------------|
| [Agent Framework Overview](./agent_framework_overview.md) | Comprehensive overview of the agent framework |
| [Challenges and Solutions](./challenges_and_solutions.md) | Analysis of previous challenges and how they're addressed |
| [Agent Patterns](./agent_patterns.md) | Design patterns for agent implementation |
| [Agent Capabilities](./agent_capabilities.md) | Agent capability definition and management |
| [Design Principles](./design_principles.md) | Core design principles for the agent framework |
| [Integration](./integration.md) | Integration with other components |
| [Session Management](./session_management.md) | Session creation, tracking, and persistence |
| [Agent Topologies](./agent_topologies.md) | Agent organization patterns and structures |
| [Capabilities Directory](./capabilities/) | Detailed capability documentation |
| [Lifecycle Directory](./lifecycle/) | Agent lifecycle documentation |
| [Protocols Directory](./protocols/) | Protocol integration documentation |
| [Reasoning Directory](./reasoning/) | Reasoning approaches documentation |
| [Sessions Directory](./sessions/) | Detailed session management documentation |
| [Topologies Directory](./topologies/) | Detailed topology documentation |

## Agent Configuration

Agent configuration follows the unified configuration schema. For the complete and authoritative schema definition, see [Agent Configuration Schema](/03_configuration/schema/agents.md).

## Integration with Other Components

The Agent Framework integrates with several other OpenMAS components:

1. **Protocol Layer** - Enables communication via different protocols
2. **Communication Patterns** - Provides standardized message exchange patterns
3. **Topology System** - Supports different agent organization structures
4. **Configuration System** - Schema-driven agent configuration
5. **Security System** - Authentication and authorization for agents
6. **Observability System** - Monitoring and logging of agent activities

## Reasoning Agnosticism

The Agent Framework maintains OpenMAS's distinctive reasoning agnosticism through:

1. **Body-Brain Separation** - Clear separation between communication infrastructure and reasoning
2. **Standard Interfaces** - Consistent interfaces regardless of reasoning approach
3. **Protocol Independence** - Reasoning is independent of communication protocol
4. **Configuration Consistency** - Common configuration patterns across reasoning types

This enables developers to choose the most appropriate reasoning approach for each task while maintaining consistent communication capabilities.
