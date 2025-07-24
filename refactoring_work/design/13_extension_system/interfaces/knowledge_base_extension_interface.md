# IKnowledgeBaseExtension Interface

## 1. Overview

The `IKnowledgeBaseExtension` interface is a specialized extension point that allows developers to integrate new types of knowledge stores into OpenMAS. This enables agents to connect to and query various data sources—such as vector databases, triple stores, or proprietary knowledge systems—through the standardized `IKnowledgeBase` interface.

An extension implementing this interface provides a factory for creating instances of a specific knowledge base adapter.

## 2. Interface Definition

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any

# Assumes the core IKnowledgeBase interface is defined and available
# from ...06_knowledge_and_reasoning/knowledge_access_interfaces/interfaces import IKnowledgeBase

class IKnowledgeBaseExtension(ABC):
    """The interface for an extension that provides a new knowledge base type."""

    @abstractmethod
    def get_kb_name(self) -> str:
        """Returns the unique, machine-readable name for the knowledge base type (e.g., 'faiss_vector_db')."""
        pass

    @abstractmethod
    def create_kb_instance(self, agent_id: str, config: Dict[str, Any]) -> IKnowledgeBase:
        """Creates an instance of the knowledge base for a specific agent.

        Args:
            agent_id: The ID of the agent this knowledge base will belong to.
            config: The agent-specific configuration for this knowledge base.

        Returns:
            An object that implements the IKnowledgeBase interface.
        """
        pass
```

## 3. How It's Used

1.  The `IExtensionManager` loads an extension that implements `IExtension`.
2.  During its `load()` method, the extension registers its `IKnowledgeBaseExtension` implementation with a central `KnowledgeBaseRegistry`.
3.  When an agent needs to access a knowledge base as defined in its configuration, the framework queries the `KnowledgeBaseRegistry` for the requested type.
4.  It then calls the `create_kb_instance()` method on the corresponding extension to get a new instance of the knowledge base adapter, which is then made available to the agent's reasoning engine.
