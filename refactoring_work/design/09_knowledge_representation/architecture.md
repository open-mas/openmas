# Knowledge Representation & Reasoning System Architecture

## Overview

This document outlines the architecture of the Knowledge Representation and Reasoning (KR&R) System in OpenMAS. The KR&R System is a distinct architectural component responsible for **managing and providing access to structured knowledge**. It is *not* a reasoning approach itself but rather an enabling system that various `ReasoningEngines` can leverage. The KR&R System enables agents to build and maintain sophisticated knowledge models while maintaining the core principle of reasoning agnosticism.

## Architectural Principles

The KR&R System architecture in OpenMAS is built on these core principles:

1. **Knowledge Management Focus**: The KR&R System is primarily responsible for managing knowledge, not for reasoning itself
2. **Multiple Representation Support**: Accommodating different knowledge representation formalisms
3. **Reasoning Engine Independence**: Providing knowledge services to any configured `ReasoningEngine`
4. **Standardized Knowledge Interfaces**: Offering consistent interfaces for reasoning engines to interact with knowledge
5. **Extensibility**: Supporting the addition of new knowledge representation types and storage backends

## Architecture Components

The KR&R System consists of these primary components:

### 1. Knowledge Representation Layer

Supports multiple formalisms for representing agent knowledge:

- **Symbolic Representations**: First-order logic, rules, frames
- **Graph-Based Representations**: Semantic networks, knowledge graphs, RDF
- **Probabilistic Representations**: Bayesian networks, Markov logic networks
- **Neural/Embeddings-Based Representations**: Vector embeddings for semantic representation

Each representation is encapsulated as a `KnowledgeRepresentation` type that defines how knowledge is structured and accessed.

### 2. Knowledge Management Layer

Provides facilities for managing knowledge across its lifecycle:

- **Knowledge Acquisition**: Methods for importing and ingesting knowledge
- **Knowledge Storage and Retrieval**: Efficient storage and access to knowledge
- **Knowledge Update**: Maintaining and updating knowledge over time
- **Knowledge Persistence**: Options for in-memory, file-based, or database storage
- **Knowledge Sharing**: Mechanisms for sharing knowledge between agents

### 3. Integration Layer

Provides standardized interfaces for `ReasoningEngines` to interact with knowledge:

- **`IKnowledgeBase` Interface**: Canonical, async, and type-safe interface (see `/09_knowledge_representation/knowledge_access_interfaces/interfaces.md`). All legacy types and ambiguous signatures are deprecated. [Migration complete]

- **Knowledge Base Registry**: Central registry of available knowledge bases. Provides the `IKnowledgeBaseRegistry` interface for listing, filtering, and obtaining accessors for all registered knowledge bases. See [Knowledge Access Interfaces](knowledge_access_interfaces/interfaces.md#knowledge-base-registry-api) for full specification.
- **Knowledge Base Factory**: Creation of appropriate knowledge base implementations
- **External System Integration**: Connections to external knowledge sources

## Relationship with Reasoning Engines

The KR&R System is **not a reasoning system itself** but provides knowledge management services to various `ReasoningEngines`. Different reasoning engines will interact with the KR&R System in different ways:

### 1. Rule-Based Reasoning Engines

May use the KR&R System to access rule sets and facts stored in symbolic knowledge representations.

### 2. BDI Engines

May use the KR&R System to persist and update belief sets and access knowledge about plans and goals.

### 3. Symbolic Reasoning Engines

Will heavily leverage the KR&R System's symbolic knowledge representations for inference and logical operations.

### 4. Vector-Based Reasoning Engines

May use the KR&R System to manage and query vector embeddings for semantic similarity operations.

### 5. LLM-Based Reasoning Engines

May retrieve relevant context from the KR&R System to include in prompts or store intermediate reasoning results.

### 6. Hybrid Reasoning Engines

May use multiple knowledge representation types from the KR&R System to support different reasoning approaches.

## Integration with Other Components

The KR&R System integrates with these OpenMAS components:

- **Agent Framework**: Facilitates access to knowledge bases for configured reasoning engines
- **Configuration System**: Configures knowledge representations and knowledge bases through the new `knowledge_management_config` section
- **Asset Management**: Manages knowledge assets like ontologies, rules, and vector stores
- **Prompt Management**: Provides context retrieval for LLM-based reasoning
- **Observability**: Monitors knowledge operations and access patterns

## Configuration

Agents interact with the KR&R System through the new `knowledge_management_config` section in their configuration:

```yaml
agents:
  example_agent:
    # Agent's primary reasoning engine selection
    reasoning:
      approach: "symbolic_engine"  # This is the "brain" - a reasoning engine
      # ...reasoning engine specific configuration...
    
    # Knowledge management configuration - how the reasoning engine uses the KR&R System
    knowledge_management_config:
      enabled: true
      knowledge_bases:
        - kb_id: "main_ontology"
          type: "graph"
        - kb_id: "domain_rules"
          type: "symbolic_facts"
      default_knowledge_representation_types:
        - "symbolic_facts"
        - "graph"
```

## References

- [Agent Framework](/refactoring_work/00b_overview/04_agents/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Reasoning Agnostic Design](/refactoring_work/00b_overview/01_architecture/reasoning_agnostic_design.md)
- [Knowledge Access Interfaces](/refactoring_work/00b_overview/09_knowledge_representation/knowledge_access_interfaces/interfaces.md)
