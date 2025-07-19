# Reasoning Framework Interfaces

## Overview

This document formalizes the interfaces between different reasoning modules in OpenMAS, enabling seamless integration and interoperability between various reasoning approaches. It also defines the standardized interfaces that `ReasoningEngines` use to interact with knowledge managed by the KR&R System.

## Core Interface Principles

The reasoning interfaces follow these design principles:

1. **Standardized Interfaces**: All reasoning components implement common interfaces for consistency
2. **Loose Coupling**: Components interact through well-defined interfaces without tight dependencies
3. **Extension Points**: Clear extension points for adding new reasoning capabilities
4. **Minimalistic Design**: Interfaces are minimal but complete for their purpose
5. **Protocol Independence**: Reasoning interfaces are independent of communication protocols
6. **Configuration-Driven**: Interface implementations are configurable through the unified schema
7. **Knowledge Agnosticism**: Reasoning engines can work with different knowledge representations through standardized interfaces

## Core Reasoning Interfaces

### IReasoner Interface

The base interface implemented by all reasoning engines:

```python
class IReasoner(ABC):
    """Base interface for all reasoning components."""
    
    @abstractmethod
    async def setup(self, agent: Agent) -> None:
        """Initialize the reasoning component."""
        pass
    
    @abstractmethod
    async def reason(self, percept: Any) -> ReasoningResult:
        """Perform reasoning based on the given percept."""
        pass
    
    @abstractmethod
    async def update_knowledge(self, knowledge: Any) -> None:
        """Update the internal knowledge of the reasoner."""
        pass
    
    @abstractmethod
    async def query_knowledge(self, query: Any) -> Any:
        """Query the internal knowledge base."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources used by the reasoner."""
        pass
```

### IReasoningStrategy Interface

Interface for reasoning strategies that orchestrate multiple reasoning approaches:

```python
class IReasoningStrategy(ABC):
    """Interface for reasoning strategies."""
    
    @abstractmethod
    async def setup(self, agent: Agent) -> None:
        """Initialize the reasoning strategy."""
        pass
    
    @abstractmethod
    async def select_reasoners(self, percept: Any) -> List[IReasoner]:
        """Select reasoners to use for the given percept."""
        pass
    
    @abstractmethod
    async def combine_results(self, results: List[ReasoningResult]) -> ReasoningResult:
        """Combine results from multiple reasoners."""
        pass
    
    @abstractmethod
    async def handle_conflict(self, conflicting_results: List[ReasoningResult]) -> ReasoningResult:
        """Resolve conflicts between results."""
        pass
```

### IKnowledgeBase Interface (Canonical Reference)

> **Migration Note:** The legacy IKnowledgeBase interface and all ambiguous method/type references have been removed. The canonical interface is now defined in `/09_knowledge_representation/knowledge_access_interfaces/interfaces.md` and must be used for all designs, documentation, and implementation.

All IKnowledgeBase methods use explicit async signatures and Pydantic models for all parameters and return values. Specialized operations (graph queries, vector search, etc.) are supported via dedicated methods. See `interfaces.md` for full details and illustrative examples.

## Specialized Reasoning Interfaces

The framework provides specialized interfaces for different reasoning approaches:

### ISymbolicReasoner Interface

Interface for symbolic reasoning engines:

```python
class ISymbolicReasoner(IReasoner):
    """Interface for symbolic reasoning engines."""
    
    @abstractmethod
    async def add_rule(self, rule: Rule) -> None:
        """Add a rule to the symbolic reasoner."""
        pass
    
    @abstractmethod
    async def add_fact(self, fact: Fact) -> None:
        """Add a fact to the symbolic reasoner."""
        pass
    
    @abstractmethod
    async def infer(self, query: Query) -> InferenceResult:
        """Perform inference based on the given query."""
        pass
    
    @abstractmethod
    async def explain(self, result: InferenceResult) -> Explanation:
        """Explain how an inference result was derived."""
        pass
```

### ILLMReasoner Interface

Interface for LLM-based reasoning:

```python
class ILLMReasoner(IReasoner):
    """Interface for LLM-based reasoning."""
    
    @abstractmethod
    async def get_prompt(self, context: Any) -> Prompt:
        """Generate a prompt based on the given context."""
        pass
    
    @abstractmethod
    async def parse_response(self, response: Any) -> ReasoningResult:
        """Parse an LLM response into a reasoning result."""
        pass
    
    @abstractmethod
    async def augment_context(self, context: Any) -> Any:
        """Augment reasoning context with additional knowledge."""
        pass
    
    @abstractmethod
    async def verify_result(self, result: ReasoningResult) -> VerificationResult:
        """Verify an LLM-generated reasoning result."""
        pass
```

## Integration with Agent Framework and KR&R System

The reasoning interfaces integrate with the agent framework and KR&R System through:

1. **Agent Reasoning Component**: Agents are configured with a primary `ReasoningEngine` via `reasoning.approach` that implements the `IReasoner` interface
2. **Knowledge Management Configuration**: Agents specify which knowledge resources their reasoning engine will use via `knowledge_management_config`
3. **KR&R System Integration**: The KR&R System provides implementations of the `IKnowledgeBase` interface for various knowledge representation types
4. **Capability Implementation**: Agent capabilities utilize reasoning interfaces for implementation
5. **Message Processing**: Agent message handlers use reasoning for processing incoming messages

## Configuration Schema

Reasoning interfaces and knowledge base access are configured through the unified configuration schema:

```yaml
agent:
  # Reasoning engine configuration
  reasoning:
    approach: "symbolic_engine"  # The primary reasoning engine ("brain")
    implementation: "rule_based"  # Specific implementation
    config:
      # Implementation-specific configuration
      rules:
        - name: "example_rule"
          condition: "condition_expr"
  
  # Knowledge management configuration
  knowledge_management_config:
    enabled: true
    knowledge_bases:
      - kb_id: "domain_ontology"  # Reference to a knowledge base managed by the KR&R System
        type: "graph"             # The knowledge representation type
      - kb_id: "business_rules"
        type: "symbolic_facts"
    default_knowledge_representation_types:
      - "graph"
      - "symbolic_facts"
```

## Knowledge Base Implementations

The KR&R System provides various implementations of the `IKnowledgeBase` interface, each tailored to a specific knowledge representation type:

1. **SymbolicKnowledgeBase**: For logical facts, rules, and symbolic reasoning
2. **GraphKnowledgeBase**: For semantic networks, RDF graphs, and ontologies
3. **VectorKnowledgeBase**: For vector embeddings and similarity-based retrieval
4. **ProbabilisticKnowledgeBase**: For probabilistic facts and Bayesian reasoning
5. **HybridKnowledgeBase**: Combines multiple representation types under a unified interface

Each implementation handles the translation between the generic `IKnowledgeBase` methods and the specifics of their underlying storage and representation mechanisms.
          action: "action_expr"
```

## References

- [Knowledge Representation Architecture](/refactoring_work/00b_overview/09_knowledge_representation/architecture.md)
- [Hybrid Reasoning](/refactoring_work/00b_overview/09_knowledge_representation/reasoning/hybrid_reasoning.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Agent Framework Integration](/refactoring_work/00b_overview/04_agents/integration.md)
