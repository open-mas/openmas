# OpenMAS Knowledge Representation & Reasoning (KR&R) System

## Overview

This directory contains documentation about the Knowledge Representation and Reasoning (KR&R) System in OpenMAS. The KR&R System is a distinct architectural component responsible for **managing and providing access to structured knowledge**. It is a cornerstone of OpenMAS's reasoning agnostic design, supporting multiple knowledge representation formalisms and providing standardized interfaces for various reasoning engines to access this knowledge.

> **Important**: The KR&R System is *not* a reasoning approach itself but rather an enabling system that various `ReasoningEngines` (the agent's "brain") can leverage through well-defined interfaces like `IKnowledgeBase`.

## Key Capabilities

The KR&R module provides these core capabilities:

1. **Multiple Knowledge Representation Formalisms**
   - Symbolic (logic-based) representations
   - Graph-based representations
   - Probabilistic representations
   - Neural/embedding-based representations

2. **Knowledge Processing Capabilities**
   - Internal inference mechanisms for knowledge bases (e.g., deductive, inductive, abductive)
   - Temporal and spatial data processing
   - Query processing and optimization
   - Consistency checking
   - Similarity search (for vector stores)
   
   > **Note**: These are internal knowledge processing capabilities of the KR&R System itself and should not be confused with the high-level agent reasoning performed by `ReasoningEngines`.

3. **Knowledge Management**
   - Knowledge acquisition
   - Knowledge integration
   - Knowledge evolution
   - Consistency management
   - Uncertainty handling

## Documentation Structure

| Document | Description |
|----------|-------------|
| [KR&R Architecture](./architecture.md) | High-level architecture of the KR&R System |
| [Knowledge Access Interfaces](./knowledge_access_interfaces/README.md) | Interfaces for reasoning engines to access knowledge |
| [Knowledge Representations](./representations/README.md) | Details on knowledge representation formalisms |
| [Integration Guide](./integration.md) | How to integrate KR&R with agent reasoning engines |

## Integration with Other Components

The KR&R System integrates with other OpenMAS components:

- **Agent Framework & Reasoning Engines** - Provides knowledge management and access for agent reasoning engines via standardized interfaces like `IKnowledgeBase` (defined in `./knowledge_access_interfaces/interfaces.md`)
- **Architecture** - Supports the reasoning agnostic design described in `/01_architecture/reasoning_agnostic_design.md` by providing a common knowledge management layer that can be used by any reasoning approach
- **Configuration** - Configured through the unified schema in `/03_configuration/`

> **Important**: The KR&R System is not responsible for an agent's primary decision-making logic. That responsibility belongs to the agent's configured `ReasoningEngine` (the "brain"). The KR&R System's role is to manage and provide access to knowledge that these reasoning engines can leverage.
