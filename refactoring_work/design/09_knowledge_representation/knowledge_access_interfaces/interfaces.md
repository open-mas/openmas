# KR&R System Interfaces

This document is the single source of truth for the primary interfaces used to interact with the OpenMAS Knowledge Representation and Reasoning (KR&R) System. All interactions with knowledge bases are governed by these contracts to ensure consistency, type safety, and adherence to the framework's reasoning-agnostic design.


## 1. IKnowledgeBase Interface

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
        ...

    @abstractmethod
    async def retrieve_knowledge(self, query: KnowledgeQuery) -> List[Union[KnowledgeItem, SimilarityHit]]:
        """
        Retrieve knowledge items matching the query.

        This single method handles all types of queries, including structured
        queries, vector similarity searches, and direct ID lookups, by using
        the `KnowledgeQuery` model.

        Returns:
            A list of `KnowledgeItem` for most queries, or a list of
            `SimilarityHit` for vector similarity searches.
        """
        ...

    @abstractmethod
    async def update_knowledge(self, item_id: str, updated_item_content: KnowledgeItemContent) -> KnowledgeItemReceipt:
        """Update the content of an existing knowledge item."""
        ...

    @abstractmethod
    async def delete_knowledge(self, item_id: str) -> bool:
        """Delete a knowledge item by its ID."""
        ...

    @abstractmethod
    async def get_knowledge_item_by_id(self, item_id: str) -> Optional[KnowledgeItem]:
        """Retrieve a single knowledge item by its unique ID."""
        ...
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
query = KnowledgeQuery(
    query_type=KnowledgeQueryType.VECTOR_SIMILARITY,
    parameters={"query_vector": [0.12, 0.77, ...], "top_k": 3}
)
hits = await kb.retrieve_knowledge(query)

## 2. `IKnowledgeBaseRegistry` Interface

The `IKnowledgeBaseRegistry` is the central discovery service for all available knowledge bases within the KR&R System. A reasoning engine uses this registry to find and get a handle to the specific knowledge bases it needs to perform its tasks.

```python
# --- Registry-specific Models ---
class KBInfo(BaseModel):
    """Provides metadata about a registered Knowledge Base."""
    kb_id: str = Field(..., description="The unique identifier for the knowledge base.")
    description: str = Field(..., description="A human-readable description of the KB's purpose and content.")
    representation_types: List[KnowledgeRepresentationType] = Field(..., description="A list of knowledge representation types supported by this KB.")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the KB.")


# --- IKnowledgeBaseRegistry Interface ---
class IKnowledgeBaseRegistry(ABC):
    """Interface for discovering and accessing knowledge bases."""

    @abstractmethod
    async def list_knowledge_bases(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[KBInfo]:
        """Lists available knowledge bases, optionally filtered by criteria.

        Args:
            filter_criteria: A dictionary to filter KBs, e.g., `{"representation_type": "graph_triple"}`.

        Returns:
            A list of KBInfo objects matching the criteria.
        """
        ...

    @abstractmethod
    async def get_knowledge_base_accessor(self, kb_id: str) -> Optional[IKnowledgeBase]:
        """Retrieves an accessor object for a specific knowledge base.

        Args:
            kb_id: The unique identifier of the knowledge base to access.

        Returns:
            An instance of a class implementing IKnowledgeBase, or None if not found.
        """
        ...
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

- [Knowledge Representation Architecture](/refactoring_work/design/09_knowledge_representation/architecture.md)
- [Hybrid Reasoning](/refactoring_work/00b_overview/09_knowledge_representation/reasoning/hybrid_reasoning.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Agent Framework Integration](/refactoring_work/00b_overview/04_agents/integration.md)
