# ITopologyManager Interface

## 1. Overview

The `ITopologyManager` interface provides a standardized contract for querying and interacting with the agent network topology within the OpenMAS framework. It allows components to discover agents, understand their roles and relationships, and get information about the overall structure of the network. This interface is central to enabling dynamic communication, role-based interactions, and adaptive behaviors in a multi-agent system.

## 2. Data Models

To ensure clear and consistent data exchange, the interface uses the following Pydantic models.

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

class AgentNode(BaseModel):
    """Represents a single agent within the topology."""
    agent_id: str = Field(..., description="The unique identifier of the agent.")
    roles: List[str] = Field(default_factory=list, description="A list of roles assigned to the agent.")
    capabilities: List[str] = Field(default_factory=list, description="A list of capabilities the agent possesses.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the agent.")

class Relationship(BaseModel):
    """Represents a directed relationship between two agents."""
    source_agent_id: str = Field(..., description="The ID of the agent where the relationship originates.")
    target_agent_id: str = Field(..., description="The ID of the agent where the relationship terminates.")
    relationship_type: str = Field(..., description="The nature of the relationship (e.g., 'reports_to', 'peer_of', 'supervises').")
    weight: float = Field(1.0, description="A weight or cost associated with the relationship.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the relationship.")

class TopologyPattern(BaseModel):
    """Describes the overall pattern of the topology."""
    pattern_name: Literal["Centralized", "Hierarchical", "Peer-to-Peer", "Mesh", "Hybrid"] = Field(..., description="The name of the topology pattern.")
    description: str = Field(..., description="A brief description of the pattern.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Configuration parameters of the current topology instance.")

```

## 3. Interface Definition

The `ITopologyManager` interface is defined as an abstract base class with the following asynchronous methods.

```python
class ITopologyManager(ABC):
    """Interface for querying the agent network topology."""

    @abstractmethod
    async def get_agent_by_id(self, agent_id: str) -> Optional[AgentNode]:
        """Retrieves a single agent by its unique identifier.

        Args:
            agent_id: The ID of the agent to retrieve.

        Returns:
            An AgentNode object if found, otherwise None.
        """
        pass

    @abstractmethod
    async def list_agents(self, role: Optional[str] = None, capability: Optional[str] = None) -> List[AgentNode]:
        """Lists all agents in the topology, with optional filtering.

        Args:
            role: If provided, only returns agents with this role.
            capability: If provided, only returns agents with this capability.

        Returns:
            A list of AgentNode objects matching the criteria.
        """
        pass

    @abstractmethod
    async def get_agent_relationships(self, agent_id: str) -> List[Relationship]:
        """Retrieves all outgoing relationships for a specific agent.

        Args:
            agent_id: The ID of the agent whose relationships are to be retrieved.

        Returns:
            A list of Relationship objects.
        """
        pass

    @abstractmethod
    async def get_neighbors(self, agent_id: str) -> List[AgentNode]:
        """Retrieves the direct neighbors of a specific agent.

        Args:
            agent_id: The ID of the agent whose neighbors are to be retrieved.

        Returns:
            A list of AgentNode objects representing the neighbors.
        """
        pass

    @abstractmethod
    async def get_topology_pattern(self) -> TopologyPattern:
        """Returns information about the current topology pattern.

        Returns:
            A TopologyPattern object describing the current topology.
        """
        pass

```

## 4. Example Usage

```python
import asyncio

async def query_topology(topology_manager: ITopologyManager, agent_id: str):
    # Get details about a specific agent
    agent = await topology_manager.get_agent_by_id(agent_id)
    if agent:
        print(f"Agent Found: {agent.agent_id}, Roles: {agent.roles}")

        # Find its neighbors
        neighbors = await topology_manager.get_neighbors(agent_id)
        print(f"Neighbors of {agent_id}: {[n.agent_id for n in neighbors]}")

    # Find all agents with the 'supervisor' role
    supervisors = await topology_manager.list_agents(role="supervisor")
    print(f"Supervisors: {[s.agent_id for s in supervisors]}")

    # Get the overall topology structure
    pattern = await topology_manager.get_topology_pattern()
    print(f"Topology Pattern: {pattern.pattern_name}")

# This is a conceptual example. `topology_manager` would be injected by the framework.
# await query_topology(topology_manager, "agent-007")
```
