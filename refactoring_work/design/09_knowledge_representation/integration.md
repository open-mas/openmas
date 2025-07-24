# KR&R System Integration Guide

This guide provides a practical walkthrough for developers on how to integrate a custom `ReasoningEngine` with the OpenMAS KR&R System. The integration process is centered around the `IKnowledgeBaseRegistry` and `IKnowledgeBase` interfaces.

## Integration Flow Overview

The core integration pattern for a reasoning engine is as follows:

1.  **Discover**: At initialization, the reasoning engine accesses the `IKnowledgeBaseRegistry` to discover the knowledge bases available in the current agent's context.
2.  **Select**: Based on its needs and configuration, the engine selects the specific knowledge bases it will interact with.
3.  **Access**: The engine requests a handle to each required knowledge base from the registry. This handle is an object that implements the `IKnowledgeBase` interface.
4.  **Interact**: The engine uses the standardized methods on the `IKnowledgeBase` handle (`query`, `assert_fact`, etc.) to read, write, and manage knowledge.

This entire process is asynchronous to ensure non-blocking operation.

## Step-by-Step Code Example

Let's imagine we are building a `SimpleRuleEngine`. This engine needs to access a knowledge base of facts to evaluate its rules.

### 1. Engine Initialization

The reasoning engine would typically receive a reference to the `IKnowledgeBaseRegistry` upon its creation, likely through dependency injection from the agent framework.

```python
from .interfaces import IKnowledgeBase, IKnowledgeBaseRegistry, Fact, Query, QueryResult

class SimpleRuleEngine:
    def __init__(self, registry: IKnowledgeBaseRegistry, config: dict):
        self._registry = registry
        self._config = config
        self._fact_kb: Optional[IKnowledgeBase] = None

    async def initialize(self):
        """Initializes the engine by connecting to its required KB."""
        kb_id = self._config.get("fact_kb_id", "default_facts")
        print(f"Engine trying to connect to KB: {kb_id}")

        # Use the registry to get a handle to the configured KB
        self._fact_kb = await self._registry.get_knowledge_base(kb_id)

        if not self._fact_kb:
            raise ConnectionError(f"Could not connect to knowledge base: {kb_id}")

        print(f"Successfully connected to KB: {kb_id}")
```

### 2. Using the Knowledge Base

Once initialized, the engine can use the `IKnowledgeBase` handle to interact with the knowledge store as part of its reasoning cycle.

```python
class SimpleRuleEngine:
    # ... (init and initialize methods from above)

    async def run_cycle(self):
        """A single reasoning cycle of the engine."""
        if not self._fact_kb:
            print("Engine not initialized.")
            return

        # 1. Query the KB to get current state
        query = Query(query_content="is_a(X, 'widget')")
        result = await self._fact_kb.query(query)

        if result.success:
            print(f"Found {len(result.results)} widgets.")
            for fact in result.results:
                # 2. Perform some reasoning based on the facts
                if self._needs_processing(fact):
                    # 3. Assert a new fact based on reasoning
                    new_fact = Fact(content=f"processed({fact.content})")
                    await self._fact_kb.assert_fact(new_fact)
                    print(f"Asserted new fact: {new_fact.content}")

    def _needs_processing(self, fact: Fact) -> bool:
        # Dummy logic for the example
        return True
```

## 3. Agent Configuration

Finally, the agent's configuration file ties everything together. It specifies which reasoning engine to use and which knowledge base it should connect to.

```yaml
agents:
  rule_based_agent:
    reasoning:
      approach: "simple_rule_engine" # The engine we are building
      fact_kb_id: "production_facts" # Custom config for our engine

    knowledge_management_config:
      enabled: true
      knowledge_bases:
        - kb_id: "production_facts" # The ID we reference above
          type: "symbolic_facts"
          # ... other KB-specific configuration
```

This example demonstrates the clean separation of concerns: the reasoning engine focuses on its logic, the KR&R system manages the data, and the configuration file declaratively links them together.

## Overview

This document describes how the Knowledge Representation and Reasoning (KR&R) system integrates with other components of OpenMAS. Understanding these integration points is essential for implementing knowledge-enabled agents that leverage the full capabilities of the framework.

## Integration with Other Components

### Agent Framework Integration

The KR&R system integrates with the agent framework (`/04_agents/`) through:

- **Reasoning Interface** - Standard interfaces for agents to access reasoning capabilities
- **Belief Management** - Integration with agent belief systems (especially in BDI agents)
- **Decision Support** - Knowledge-based decision making for agent actions
- **Capability Enhancement** - Knowledge-backed capabilities for advanced agent functions

```
Agent ──> Reasoning Interface ──> Knowledge Representation System
```

### Protocol Layer Integration

The KR&R system interacts with the protocol layer (`/02_protocols/`) through:

- **Knowledge Exchange** - Protocol-specific formats for knowledge sharing between agents
- **Semantic Protocols** - Knowledge-aware protocol implementations
- **Query Interfaces** - Protocol methods for querying remote knowledge
- **Context Propagation** - Sharing knowledge context across protocol boundaries

```
Knowledge Representation ──> Knowledge Exchange Format ──> Protocol Implementation
```

### Configuration System Integration

The KR&R system is configured through the configuration system (`/03_configuration/`) via:

- **Representation Configuration** - Selection and parameterization of knowledge representations
- **Reasoning Engine Configuration** - Selection and configuration of reasoning approaches
- **Knowledge Source Configuration** - Configuration of external knowledge sources
- **Performance Tuning** - Configuration of performance-related parameters

```
Configuration ──> KR&R Options ──> Knowledge Representation System
```

### Asset Management Integration

The KR&R system leverages the asset management system (`/10_asset_management/`) for:

- **Ontology Management** - Storage and versioning of ontologies
- **Model Management** - Access to reasoning and machine learning models
- **Knowledge Base Versioning** - Version control for knowledge bases
- **External Knowledge Access** - Managed access to external knowledge sources

```
Knowledge Representation ──> Asset Request ──> Asset Management System
```

### Prompt Management Integration

The KR&R system utilizes the prompt management system (`/11_prompt_management/`) for:

- **LLM-based Reasoning** - Managed prompts for language model reasoning
- **Knowledge Extraction** - Prompts for extracting knowledge from text
- **Reasoning Chains** - Prompt chains for complex reasoning tasks
- **Context Management** - Knowledge-aware context management for prompts

```
Knowledge Representation ──> Prompt Request ──> Prompt Management System
```

### Observability Integration

The KR&R system emits observability data to the observability system (`/12_observability/`) through:

- **Knowledge Operations Logging** - Logging of knowledge access and modifications
- **Reasoning Tracing** - Tracing of reasoning steps and decisions
- **Knowledge Metrics** - Metrics on knowledge base size, access patterns, etc.
- **Performance Monitoring** - Monitoring of reasoning performance

```
Knowledge Representation ──> Logs/Metrics/Traces ──> Observability System
```

## Cross-Representation Integration

The KR&R system supports integration between different knowledge representation formalisms:

1. **Representation Translation** - Converting knowledge between different formats
2. **Multi-Representation Reasoning** - Combining multiple representations for complex reasoning
3. **Semantic Alignment** - Aligning concepts across different knowledge models
4. **Interoperability Mechanisms** - Standard formats for knowledge exchange

## Implementation Considerations

When implementing KR&R integrations:

1. Use the standard interfaces for accessing knowledge and reasoning capabilities
2. Leverage configuration for selecting appropriate representations and reasoning engines
3. Consider performance implications when choosing representation formats
4. Use the asset management system for ontologies and other knowledge assets
5. Ensure proper observability for knowledge operations and reasoning processes

## References

- [Agent Framework](/refactoring_work/00b_overview/04_agents/README.md)
- [Protocol Layer](/refactoring_work/00b_overview/02_protocols/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Asset Management](/refactoring_work/00b_overview/10_asset_management/README.md)
- [Prompt Management](/refactoring_work/00b_overview/11_prompt_management/README.md)
- [Observability System](/refactoring_work/00b_overview/12_observability/README.md)
