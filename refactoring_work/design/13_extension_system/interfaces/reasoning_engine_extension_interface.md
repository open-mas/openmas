# IReasoningEngineExtension Interface

## 1. Overview

The `IReasoningEngineExtension` interface is a specialized extension point that allows developers to integrate new reasoning paradigms into OpenMAS. An extension implementing this interface can make a new type of reasoning engine—such as a custom BDI implementation, a new LLM-based reasoner, or a hybrid system—available to be assigned to agents.

This interface acts as a factory for a specific type of reasoning engine, providing a standardized way for the framework to create new instances of that engine for agents.

## 2. Interface Definition

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any

# Assumes the core IReasoningEngine interface is defined and available
# from ...03_reasoning/interfaces import IReasoningEngine

class IReasoningEngineExtension(ABC):
    """The interface for an extension that provides a new reasoning engine."""

    @abstractmethod
    def get_engine_name(self) -> str:
        """Returns the unique, machine-readable name for the reasoning engine (e.g., 'bdi_reasoner_v2')."""
        pass

    @abstractmethod
    def create_engine(self, agent_id: str, config: Dict[str, Any]) -> IReasoningEngine:
        """Creates an instance of the reasoning engine for a specific agent.

        Args:
            agent_id: The ID of the agent this engine will belong to.
            config: The agent-specific configuration for this reasoning engine.

        Returns:
            An object that implements the IReasoningEngine interface.
        """
        pass
```

## 3. How It's Used

1.  The `IExtensionManager` loads an extension that implements `IExtension`.
2.  During its `load()` method, the extension registers its `IReasoningEngineExtension` implementation with a central `ReasoningEngineRegistry`.
3.  When an agent is being constructed, the agent framework looks at the agent's configuration to determine which reasoning engine to use.
4.  It queries the `ReasoningEngineRegistry` for the requested engine name.
5.  It then calls the `create_engine()` method on the corresponding `IReasoningEngineExtension` to get a new instance of the reasoner, which is then assigned to the agent.
