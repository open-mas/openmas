# ITopologyPatternExtension Interface

## 1. Overview

The `ITopologyPatternExtension` interface is a specialized extension point that allows developers to add new topology patterns to OpenMAS. A topology pattern defines the structure of relationships between a set of agents. While OpenMAS may ship with standard patterns like Centralized or Peer-to-Peer, this extension point allows for the creation of custom patterns, such as dynamic social networks or domain-specific hierarchical structures.

An extension implementing this interface provides a factory for creating instances of a class that conforms to the `ITopologyPattern` interface.

## 2. Interface Definition

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any

# Assumes the core ITopologyPattern interface is defined and available
# from ...08_topology/interfaces/topology_pattern_interface import ITopologyPattern

class ITopologyPatternExtension(ABC):
    """The interface for an extension that provides a new topology pattern."""

    @abstractmethod
    def get_pattern_name(self) -> str:
        """Returns the unique, machine-readable name for the topology pattern (e.g., 'scale_free_network')."""
        pass

    @abstractmethod
    def create_pattern(self, config: Dict[str, Any]) -> ITopologyPattern:
        """Creates an instance of the topology pattern.

        Args:
            config: The configuration for this instance of the pattern.

        Returns:
            An object that implements the ITopologyPattern interface.
        """
        pass
```

## 3. How It's Used

1.  The `IExtensionManager` loads an extension that implements `IExtension`.
2.  During its `load()` method, the extension registers its `ITopologyPatternExtension` implementation with a central `TopologyPatternRegistry`.
3.  When a user or a system component wants to apply a topology to a group of agents, it requests the pattern by name from the `Topology Manager`.
4.  The `Topology Manager` queries the `TopologyPatternRegistry` and uses the `create_pattern()` method on the corresponding extension to get a new instance of the pattern logic.
5.  This instance is then used to calculate and apply the relationships between agents.
