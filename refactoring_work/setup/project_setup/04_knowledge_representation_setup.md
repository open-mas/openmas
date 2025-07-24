# Knowledge Representation & Reasoning (KR&R) System Setup

## Task Overview
Setup the Knowledge Representation & Reasoning (KR&R) System for OpenMAS 0.3.0, which provides knowledge management services to reasoning engines while maintaining clear separation from agent decision-making logic.

## Design Alignment
**Reference**: `/refactoring_work/design/01_architecture/components_summary.md` sections 25-40
**Architecture**: The KR&R System is a distinct component that manages and provides access to structured knowledge but is NOT responsible for an agent's primary decision-making logic.

## Tasks

1. Create KR&R System Directory Structure
   - Setup knowledge base implementations
   - Create knowledge access interfaces
   - Setup reasoning engine support utilities

2. Implement Knowledge Access Interfaces
   - Create `IKnowledgeBase` interface (canonical, async, type-safe)
   - Setup knowledge base registry
   - Configure external knowledge integration

3. Setup Knowledge Representations
   - Symbolic facts representation
   - Graph-based knowledge structures
   - Vector-based knowledge storage
   - Probabilistic knowledge formats

4. Configure Knowledge Processing
   - Query optimization mechanisms
   - Consistency checking utilities
   - Similarity search capabilities
   - Knowledge base management tools

## Directory Structure

```
src/openmas/knowledge_representation/
├── __init__.py                     # KR&R module initialization
├── interfaces/                     # Knowledge access interfaces
│   ├── __init__.py
│   ├── knowledge_base.py          # IKnowledgeBase interface
│   ├── query_interface.py         # Query interfaces
│   └── registry.py                # Knowledge base registry
├── knowledge_bases/               # Knowledge base implementations
│   ├── __init__.py
│   ├── symbolic/                  # Symbolic knowledge bases
│   │   ├── __init__.py
│   │   ├── fact_base.py          # Fact-based knowledge
│   │   └── rule_base.py          # Rule-based knowledge
│   ├── graph/                     # Graph-based knowledge
│   │   ├── __init__.py
│   │   ├── knowledge_graph.py    # Knowledge graph implementation
│   │   └── ontology.py           # Ontology management
│   ├── vector/                    # Vector-based knowledge
│   │   ├── __init__.py
│   │   ├── embeddings.py         # Embedding-based knowledge
│   │   └── similarity.py         # Similarity search
│   └── probabilistic/             # Probabilistic knowledge
│       ├── __init__.py
│       ├── bayesian.py           # Bayesian networks
│       └── uncertainty.py        # Uncertainty handling
├── processing/                    # Knowledge processing utilities
│   ├── __init__.py
│   ├── optimization/              # Query optimization
│   │   ├── __init__.py
│   │   ├── query_planner.py      # Query planning
│   │   └── indexing.py           # Knowledge indexing
│   ├── validation/                # Consistency checking
│   │   ├── __init__.py
│   │   ├── consistency.py        # Consistency validation
│   │   └── integrity.py          # Integrity constraints
│   └── search/                    # Search capabilities
│       ├── __init__.py
│       ├── similarity_search.py  # Similarity search
│       └── semantic_search.py    # Semantic search
└── reasoning/                     # Reasoning engine support
    ├── __init__.py
    ├── connectors/                # Reasoning engine connectors
    │   ├── __init__.py
    │   ├── rule_based.py         # Rule-based engine connector
    │   ├── bdi_connector.py      # BDI engine connector
    │   └── llm_connector.py      # LLM engine connector
    └── utilities/                 # Reasoning utilities
        ├── __init__.py
        ├── knowledge_mapper.py   # Knowledge mapping utilities
        └── context_builder.py    # Context building for reasoning
```

## Key Implementation Files

### 1. IKnowledgeBase Interface (`interfaces/knowledge_base.py`)

```python
"""
Knowledge base interface for OpenMAS KR&R System.

Provides canonical, async, and type-safe access to knowledge bases.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class IKnowledgeBase(ABC, Generic[T]):
    """
    Canonical interface for knowledge base access.
    
    This interface provides type-safe, async access to knowledge bases
    while maintaining separation from reasoning logic.
    """
    
    @abstractmethod
    async def query(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[T]:
        """Execute a query against the knowledge base."""
        pass
    
    @abstractmethod
    async def store(self, knowledge: T) -> bool:
        """Store knowledge in the knowledge base."""
        pass
    
    @abstractmethod
    async def update(self, knowledge_id: str, knowledge: T) -> bool:
        """Update existing knowledge in the knowledge base."""
        pass
    
    @abstractmethod
    async def delete(self, knowledge_id: str) -> bool:
        """Delete knowledge from the knowledge base."""
        pass
    
    @abstractmethod
    async def get_schema(self) -> Dict[str, Any]:
        """Get the schema for this knowledge base."""
        pass
```

### 2. Knowledge Base Registry (`interfaces/registry.py`)

```python
"""
Knowledge base registry for the KR&R System.

Provides central registry of available knowledge bases that reasoning engines can access.
"""

from typing import Dict, List, Optional, Type
from .knowledge_base import IKnowledgeBase

class KnowledgeBaseRegistry:
    """Central registry for knowledge bases."""
    
    def __init__(self):
        self._knowledge_bases: Dict[str, IKnowledgeBase] = {}
        self._knowledge_base_types: Dict[str, Type[IKnowledgeBase]] = {}
    
    def register_knowledge_base(self, name: str, knowledge_base: IKnowledgeBase) -> None:
        """Register a knowledge base instance."""
        self._knowledge_bases[name] = knowledge_base
        self._knowledge_base_types[name] = type(knowledge_base)
    
    def get_knowledge_base(self, name: str) -> Optional[IKnowledgeBase]:
        """Get a registered knowledge base by name."""
        return self._knowledge_bases.get(name)
    
    def list_knowledge_bases(self) -> List[str]:
        """List all registered knowledge base names."""
        return list(self._knowledge_bases.keys())
    
    def get_knowledge_base_type(self, name: str) -> Optional[Type[IKnowledgeBase]]:
        """Get the type of a registered knowledge base."""
        return self._knowledge_base_types.get(name)

# Global registry instance
knowledge_base_registry = KnowledgeBaseRegistry()
```

## Integration with Reasoning Engines

The KR&R System integrates with reasoning engines through:

1. **Standardized Interfaces**: All reasoning engines access knowledge through `IKnowledgeBase`
2. **Registry Pattern**: Reasoning engines discover available knowledge bases through the registry
3. **Type Safety**: Strong typing ensures correct knowledge access patterns
4. **Async Support**: Non-blocking knowledge operations for performance

## Configuration Integration

The KR&R System should be configured through the unified configuration schema:

```yaml
knowledge_representation:
  knowledge_bases:
    - name: "facts"
      type: "symbolic"
      config:
        storage_backend: "memory"
        persistence: true
    - name: "embeddings"
      type: "vector"
      config:
        dimension: 768
        similarity_metric: "cosine"
  processing:
    query_optimization: true
    consistency_checking: true
    similarity_threshold: 0.8
```

## Success Criteria
- Complete KR&R System directory structure created
- `IKnowledgeBase` interface implemented with type safety
- Knowledge base registry functional
- Integration points with reasoning engines established
- Configuration schema alignment maintained
- Clear separation between knowledge management and reasoning logic
