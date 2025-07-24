# ITopologyPattern Interface

## 1. Overview

The `ITopologyPattern` interface defines a standardized contract for all topology pattern implementations within OpenMAS (e.g., Centralized, Hierarchical, Peer-to-Peer). It provides a clear set of methods for the `Topology Manager` to use when applying and dynamically managing the structure of the agent network. Each concrete implementation of this interface will contain the specific logic for organizing agents according to its corresponding pattern.

This interface works with the data models (`AgentNode`, `Relationship`) defined in the `ITopologyManager` interface document to ensure consistency.

## 2. Interface Definition

The `ITopologyPattern` interface is defined as an abstract base class. It is expected to be stateful, maintaining the current set of relationships based on the agents it manages.

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Assumes the following models are defined and accessible
# from the ITopologyManager interface definition.
# from .topology_management_interface import AgentNode, Relationship

class ITopologyPattern(ABC):
    """Interface for a specific topology pattern implementation."""

    @abstractmethod
    async def apply(self, agents: List[AgentNode], config: Dict[str, Any]) -> List[Relationship]:
        """Initializes the topology with a set of agents and a configuration.

        This method calculates the initial set of relationships based on the pattern's logic.

        Args:
            agents: A list of all agent nodes to be included in the topology.
            config: A dictionary containing pattern-specific configuration parameters
                    (e.g., the ID of the central orchestrator in a Centralized pattern).

        Returns:
            A list of Relationship objects representing the newly formed topology.
        """
        pass

    @abstractmethod
    async def add_agent(self, agent_to_add: AgentNode) -> List[Relationship]:
        """Adds a new agent to the existing topology.

        This method calculates the new relationships that should be created for the added agent
        and may return relationships that need to be updated or removed.

        Args:
            agent_to_add: The new agent node to integrate into the topology.

        Returns:
            A list of new or modified Relationship objects.
        """
        pass

    @abstractmethod
    async def remove_agent(self, agent_id_to_remove: str) -> List[Relationship]:
        """Removes an agent from the topology.

        This method determines which relationships are affected by the removal of an agent
        and may trigger reorganization logic within the pattern.

        Args:
            agent_id_to_remove: The unique identifier of the agent to remove.

        Returns:
            A list of relationships that should be removed from the topology.
        """
        pass

    @abstractmethod
    async def get_relationships(self) -> List[Relationship]:
        """Retrieves the current set of all relationships in the topology.

        Returns:
            A list of all current Relationship objects.
        """
        pass

```

## 3. Implementation Guidance

- **State Management**: Each class implementing `ITopologyPattern` will need to maintain its own internal state, typically the list of agents and the current relationship graph.
- **Configuration**: The `config` dictionary passed to the `apply` method is crucial for pattern-specific settings. For example, a `Hierarchical` pattern might require layer definitions, while a `Centralized` pattern needs the `orchestrator_id`.
- **Idempotency**: Implementations should be robust. For instance, adding an agent that already exists should not cause an error but should ensure the agent is correctly integrated.

## 4. Example Usage (Conceptual)

This shows how the `Topology Manager` might use a pattern implementation.

```python
import asyncio

async def manage_topology(pattern: ITopologyPattern, initial_agents: List[AgentNode]):
    # Initialize a centralized topology
    config = {"orchestrator_id": "agent-001"}
    initial_relationships = await pattern.apply(initial_agents, config)
    print(f"Topology initialized with {len(initial_relationships)} relationships.")

    # A new agent joins
    new_agent = AgentNode(agent_id="agent-101", roles=["worker"])
    new_relationships = await pattern.add_agent(new_agent)
    print(f"Agent {new_agent.agent_id} added, creating {len(new_relationships)} new relationships.")

    # An agent leaves
    removed_relationships = await pattern.remove_agent("agent-002")
    print(f"Agent agent-002 removed, affecting {len(removed_relationships)} relationships.")

# This is a conceptual example. `pattern` would be a concrete implementation
# like `CentralizedPattern` or `HierarchicalPattern`.
```
