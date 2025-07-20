# Knowledge Access Interfaces for Reasoning Engines

## Overview

This document formalizes the standardized interfaces through which `ReasoningEngines` (the agent's "brain") access knowledge managed by the KR&R System. These interfaces enable different reasoning approaches to interact with knowledge in a consistent way, supporting OpenMAS's reasoning agnosticism by maintaining a clean separation between knowledge management (handled by the KR&R System) and reasoning logic (implemented by various `ReasoningEngines`).

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

### IKnowledgeBase Interface (Precise Specification)

The `IKnowledgeBase` interface is the standardized abstraction layer for reasoning engines to interact with the KR&R System. This version specifies all method signatures, expected types, and supporting data models.

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

# --- Enums ---
class KnowledgeRepresentationType(str, Enum):
    SYMBOLIC_FACT = "symbolic_fact"
    GRAPH_TRIPLE = "graph_triple"
    VECTOR_EMBEDDING = "vector_embedding"
    TEXT_DOCUMENT = "text_document"
    ONTOLOGY_AXIOM = "ontology_axiom"
    PROBABILISTIC_FACT = "probabilistic_fact"
    HYBRID = "hybrid"

class KnowledgeQueryType(str, Enum):
    BY_ID = "by_id"
    BY_REPRESENTATION = "by_representation"
    STRUCTURED_QUERY = "structured_query"
    NATURAL_LANGUAGE_QUERY = "natural_language_query"
    VECTOR_SIMILARITY = "vector_similarity"
    SPARQL = "sparql"

class OperatorType(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"

# --- Content Models ---
class SymbolicFactContent(BaseModel):
    subject: str
    predicate: str
    object_value: Any
    object_type: str

class GraphTripleContent(BaseModel):
    subject_uri: str
    predicate_uri: str
    object_literal: Optional[Any] = None
    object_uri: Optional[str] = None

class VectorEmbeddingContent(BaseModel):
    vector: List[float]
    source_text: Optional[str] = None

class TextDocumentContent(BaseModel):
    text: str
    title: Optional[str] = None

class OntologyAxiomContent(BaseModel):
    axiom: str
    language: Optional[str] = None

class ProbabilisticFactContent(BaseModel):
    fact: str
    probability: float

KnowledgeItemContent = Union[
    SymbolicFactContent,
    GraphTripleContent,
    VectorEmbeddingContent,
    TextDocumentContent,
    OntologyAxiomContent,
    ProbabilisticFactContent
]

# --- Core Data Models ---
class KnowledgeItem(BaseModel):
    item_id: Optional[str] = None
    representation_type: KnowledgeRepresentationType
    content: KnowledgeItemContent
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: Optional[List[str]] = None

class MatchCriterion(BaseModel):
    field: str
    operator: OperatorType
    value: Any

class KnowledgeQuery(BaseModel):
    query_type: KnowledgeQueryType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    representation_type: Optional[KnowledgeRepresentationType] = None
    match_criteria: Optional[List[MatchCriterion]] = None
    metadata_filter: Optional[Dict[str, Any]] = None
    tags_filter: Optional[List[str]] = None
    limit: Optional[int] = 10
    offset: Optional[int] = 0

class KnowledgeItemReceipt(BaseModel):
    item_id: str
    status: str  # e.g. "ADDED", "UPDATED"
    timestamp: datetime

class SimilarityHit(BaseModel):
    item_id: str
    score: float
    knowledge_item: Optional[KnowledgeItem] = None

# --- IKnowledgeBase Interface ---
class IKnowledgeBase(ABC):
    """Standardized interface for knowledge base components."""

    @abstractmethod
    async def add_knowledge(self, knowledge_item: KnowledgeItem) -> KnowledgeItemReceipt:
        """Add a knowledge item to the knowledge base."""
        pass

    @abstractmethod
    async def retrieve_knowledge(self, query: KnowledgeQuery) -> List[KnowledgeItem]:
        """Retrieve knowledge items matching the query."""
        pass

# --- Knowledge Base Registry API ---
from typing import Optional

class KnowledgeBaseInfo(BaseModel):
    """
    Metadata describing a registered knowledge base in the KR&R system.
    """
    kb_name: str  # Unique identifier for the knowledge base
    display_name: Optional[str] = None  # Human-friendly name
    description: Optional[str] = None
    representation_types: List[KnowledgeRepresentationType]  # Supported representations
    tags: Optional[List[str]] = None
    is_writable: bool = False  # Whether the KB allows mutation
    is_external: bool = False  # True if the KB is managed externally
    config: Optional[Dict[str, Any]] = None  # Additional config metadata

class KnowledgeBaseFilterCriteria(BaseModel):
    """
    Criteria for filtering knowledge bases when listing or searching.
    """
    name_pattern: Optional[str] = None  # Wildcard or regex for kb_name/display_name
    representation_types: Optional[List[KnowledgeRepresentationType]] = None
    tags: Optional[List[str]] = None
    is_writable: Optional[bool] = None
    is_external: Optional[bool] = None

class IKnowledgeBaseRegistry(ABC):
    """
    Interface for discovering, listing, and accessing available knowledge bases in the KR&R system.
    """
    @abstractmethod
    async def list_knowledge_bases(
        self,
        filter_criteria: Optional[KnowledgeBaseFilterCriteria] = None
    ) -> List[KnowledgeBaseInfo]:
        """
        List all available knowledge bases, optionally filtered by criteria.
        """
        pass

    @abstractmethod
    async def get_knowledge_base_info(
        self,
        kb_name: str
    ) -> Optional[KnowledgeBaseInfo]:
        """
        Retrieve metadata for a specific knowledge base by unique name.
        """
        pass

    @abstractmethod
    async def get_knowledge_base_accessor(
        self,
        kb_name: str
    ) -> Optional[IKnowledgeBase]:
        """
        Obtain an accessor implementing IKnowledgeBase for the specified knowledge base.
        Returns None if not found or not accessible.
        """
        pass

# Example Usage:
# registry: IKnowledgeBaseRegistry = ...
# kb_list = await registry.list_knowledge_bases()
# kb_accessor = await registry.get_knowledge_base_accessor("facts_kb")
# if kb_accessor:
#     results = await kb_accessor.retrieve_knowledge(...)

        """Retrieve knowledge items matching the query."""
        pass

    @abstractmethod
    async def update_knowledge(self, item_id: str, updated_item_content: KnowledgeItemContent) -> KnowledgeItemReceipt:
        """Update the content of an existing knowledge item."""
        pass

    @abstractmethod
    async def delete_knowledge(self, item_id: str) -> bool:
        """Delete a knowledge item by its ID."""
        pass

    @abstractmethod
    async def query_knowledge_graph(self, sparql_query: str) -> List[Dict[str, Any]]:
        """Run a SPARQL query (for graph-based KBs)."""
        pass

    @abstractmethod
    async def vector_similarity_search(self, vector: List[float], top_k: int) -> List[SimilarityHit]:
        """Perform a vector similarity search (for embedding-based KBs)."""
        pass

    @abstractmethod
    async def get_knowledge_item_by_id(self, item_id: str) -> Optional[KnowledgeItem]:
        """Retrieve a single knowledge item by ID."""
        pass
```

#### Illustrative Usage Examples

```python
# Example: Adding a symbolic fact
fact = KnowledgeItem(
    representation_type=KnowledgeRepresentationType.SYMBOLIC_FACT,
    content=SymbolicFactContent(
        subject="Paris",
        predicate="is_capital_of",
        object_value="France",
        object_type="str"
    ),
    metadata={"source": "Wikidata", "confidence": 0.98},
    tags=["geography", "capital"]
)
receipt = await kb.add_knowledge(fact)

# Example: Adding a text document with embedding
text_doc = KnowledgeItem(
    representation_type=KnowledgeRepresentationType.TEXT_DOCUMENT,
    content=TextDocumentContent(text="OpenMAS is a reasoning-agnostic agent framework."),
    metadata={"source": "manual"}
)
receipt = await kb.add_knowledge(text_doc)

embedding = KnowledgeItem(
    representation_type=KnowledgeRepresentationType.VECTOR_EMBEDDING,
    content=VectorEmbeddingContent(vector=[0.12, 0.77, ...], source_text="OpenMAS is a reasoning-agnostic agent framework."),
    metadata={"linked_doc_id": receipt.item_id}
)
await kb.add_knowledge(embedding)

# Example: Querying by metadata and type
query = KnowledgeQuery(
    query_type=KnowledgeQueryType.STRUCTURED_QUERY,
    representation_type=KnowledgeRepresentationType.SYMBOLIC_FACT,
    match_criteria=[MatchCriterion(field="subject", operator=OperatorType.EQUALS, value="Paris")],
    metadata_filter={"source": "Wikidata"},
    limit=5
)
results = await kb.retrieve_knowledge(query)

# Example: Vector similarity search
hits = await kb.vector_similarity_search(vector=[0.12, 0.77, ...], top_k=3)
```

> **Note:** All data structures are defined as Pydantic models for validation and serialization. The interface supports extension to new knowledge types by adding new content models and enums as needed.

---

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
