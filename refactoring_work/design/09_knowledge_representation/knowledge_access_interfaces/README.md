# Knowledge Access Interfaces

This directory contains the formal definitions for the interfaces that govern all interactions with the Knowledge Representation & Reasoning (KR&R) System in OpenMAS.

## Single Source of Truth

To ensure consistency and clarity, all KR&R interface definitions, including core data models and the primary `IKnowledgeBase` and `IKnowledgeBaseRegistry` contracts, are consolidated into a single document:

-   **[KR&R System Interfaces](./interfaces.md)**: This document is the canonical source for all KR&R API contracts.

Reasoning engines and other components that need to interact with the KR&R system should adhere strictly to the interfaces defined in that file. This approach supports the framework's core principles of modularity, type safety, and reasoning agnosticism.

## Overview

This directory contains documentation about the standardized interfaces through which `ReasoningEngines` (the agent's "brain") access knowledge managed by the OpenMAS Knowledge Representation and Reasoning (KR&R) System. These interfaces enable different reasoning approaches to interact with various knowledge representations in a consistent way, supporting OpenMAS's reasoning agnosticism.

> **Important**: The interfaces defined here (particularly `IKnowledgeBase`) serve as the critical abstraction layer between the KR&R System (which manages knowledge) and various `ReasoningEngines` (which make decisions based on that knowledge). This clean separation is fundamental to OpenMAS's reasoning agnostic design.

## Supporting Multiple Reasoning Approaches

The interfaces defined in this directory are designed to support various reasoning approaches used by agent `ReasoningEngines`, including:

1. **Rule-Based Reasoning Engines**
   - Access symbolic facts and rules via `IKnowledgeBase.query()`
   - Store inferred knowledge via `IKnowledgeBase.add()`
   - Check for specific conditions via `IKnowledgeBase.exists()`

2. **BDI (Belief-Desire-Intention) Reasoning Engines**
   - Access and update beliefs via knowledge base operations
   - Retrieve goal-related knowledge and plans
   - Store execution state and intention information

3. **Symbolic Reasoning Engines**
   - Access formalized knowledge for logical inference
   - Store derived theorems and logical consequences
   - Execute knowledge base operations with formal logic queries

4. **Probabilistic Reasoning Engines**
   - Access uncertainty information and probability distributions
   - Retrieve evidence for Bayesian updates
   - Store posterior distributions and inference results

5. **LLM-Based Reasoning Engines**
   - Retrieve relevant context via vector queries
   - Access structured knowledge for grounding
   - Store reasoning traces and intermediate results

6. **Hybrid Reasoning Engines**
   - Leverage multiple knowledge representation formats
   - Coordinate access between symbolic and neural components
   - Store results from various reasoning subsystems

## Documentation Structure

| Document | Description |
|----------|-------------|
| [Knowledge Access Interfaces](./interfaces.md) | Standard interfaces for reasoning engines to access knowledge |
| [Hybrid Reasoning Support](./hybrid_reasoning.md) | How the interfaces support combining multiple reasoning approaches |

> **Note**: All documents in this directory focus on how reasoning engines interface with the KR&R System's managed knowledge, not on the internal implementation details of the reasoning engines themselves, which are documented in `/04_agents/reasoning/`.

## Abstracting Knowledge Representation Details

A key benefit of the interfaces defined in this directory is that they abstract away the implementation details of different knowledge representations, allowing reasoning engines to focus on their decision-making logic rather than the specifics of knowledge storage and retrieval. These interfaces enable reasoning engines to work with:

- **Symbolic Representations** - Without needing to know the specific logic formalism or syntax
- **Graph Representations** - Without having to understand graph database query languages
- **Vector Representations** - Without dealing with embedding generation or vector math details
- **Probabilistic Representations** - Without implementing probability distribution mechanisms

## Implementation Considerations

When implementing reasoning engines that use these interfaces:

1. **Focus on the interface contract** - Rely on the methods defined in `IKnowledgeBase` rather than assumptions about the underlying implementation
2. **Use appropriate query formats** - Different knowledge base implementations may expect different query formats (specified in their documentation)
3. **Handle representation-specific features** - Some knowledge representations have unique capabilities exposed through type-specific interfaces
4. **Consider performance implications** - Different operations may have different performance characteristics depending on the underlying representation
5. **Configure knowledge access** - Use the `knowledge_management_config` section in the agent configuration to specify which knowledge bases a reasoning engine should access
