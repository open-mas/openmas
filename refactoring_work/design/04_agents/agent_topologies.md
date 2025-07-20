# Agent Topologies and Network Organization Standard

> **Note**: For comprehensive design documentation on topologies, including implementation details and pattern-specific guidance, see the [Topology Design](../01_architecture/topology_design.md) document and the [Topology Patterns](../01_architecture/topology_patterns/) directory.

## Topology Definition
- **Name**: Agent Topologies
- **Purpose**: Standardized approach to agent organization, relationships, and communication patterns
- **Protocol Compatibility**: Works with all protocols (A2A, MCP, HTTP, MQTT, gRPC)
- **Reasoning Agnosticism**: Maintains separation between agent organization (topologies) and reasoning approaches

## Topology Schema
```yaml
# Standardized topology configuration schema (within unified schema)
# Global topology defaults
defaults:
  topology:
    type: object
    description: "Global topology configuration"
    properties:
      # Topology pattern
      pattern:
        type: string
        description: "Topology pattern type"
        enum: ["centralized", "peer_to_peer", "hierarchical", "mesh", "hybrid"]
        default: "centralized"

      # Agent roles
      roles:
        type: object
        description: "Role definitions within the topology"
        properties:
          # Role types and their capabilities
          types:
            type: array
            description: "Defined roles in this topology"
            items:
              type: object
              properties:
                name:
                  type: string
                  description: "Role name (e.g., 'orchestrator', 'worker', 'peer')"
                description:
                  type: string
                  description: "Role description and responsibilities"
                capabilities:
                  type: array
                  description: "Required capabilities for this role"
                  items:
                    type: string

      # Relationship definitions
      relationships:
        type: object
        description: "Relationship types within the topology"
        properties:
          types:
            type: array
            description: "Defined relationship types"
            items:
              type: object
              properties:
                name:
                  type: string
                  description: "Relationship name (e.g., 'parent-child', 'peer', 'service')"
                description:
                  type: string
                  description: "Relationship description"
                communication_pattern:
                  type: string
                  description: "Default communication pattern for this relationship"
                  enum: ["request_response", "publish_subscribe", "streaming", "event_based"]

# Agent-specific topology configuration
agents:
  agent_name:
    topology:
      type: object
      description: "Agent-specific topology configuration"
      properties:
        # Agent's role
        role:
          type: string
          description: "Role of this agent in the topology"

        # Agent's relationships
        relationships:
          type: array
          description: "Agent's relationships with other agents"
          items:
            type: object
            properties:
              agent_id:
                type: string
                description: "ID of the related agent"
              relationship_type:
                type: string
                description: "Type of relationship"
              direction:
                type: string
                description: "Direction of relationship"
                enum: ["incoming", "outgoing", "bidirectional"]
              communication_pattern:
                type: string
                description: "Override of communication pattern for this relationship"
                enum: ["request_response", "publish_subscribe", "streaming", "event_based", "pipeline", "delegation"]
            priority:
              type: integer
              description: "Priority level (1-10, with 1 being highest)"
              minimum: 1
              maximum: 10

required:
  - topology
```

## Topology Patterns

### 1. Centralized (Hub and Spoke)
- **Description**: A central orchestrator agent coordinates communications between specialized worker agents.
- **Use Cases**: Task delegation, centralized coordination, controlled workflow.
- **Key Components**:
  - Hub/Orchestrator: Central coordination agent
  - Spokes/Workers: Specialized task-handling agents
- **Configuration Example**:
  ```yaml
  topology:
    pattern: "centralized"
    roles:
      types:
        - name: "orchestrator"
          description: "Central coordinator for all tasks"
        - name: "worker"
          description: "Specialized agents for specific tasks"
    relationships:
      types:
        - name: "orchestrator_to_worker"
          communication_pattern: "request_response"
  ```

### 2. Peer-to-Peer
- **Description**: Agents operate as equals, directly communicating with each other as needed.
- **Use Cases**: Collaborative workflows, distributed problem-solving, resilient systems.
- **Key Components**:
  - Peers: Equal agents with direct connections
- **Configuration Example**:
  ```yaml
  topology:
    pattern: "peer_to_peer"
    roles:
      types:
        - name: "peer"
          description: "Equal agent with ability to communicate with any other peer"
    relationships:
      types:
        - name: "peer_to_peer"
          communication_pattern: "request_response"
  ```

### 3. Hierarchical
- **Description**: Multi-level organization with delegation of tasks downward and reporting upward.
- **Use Cases**: Complex task decomposition, organizational simulation, nested processing.
- **Key Components**:
  - Parent/Manager: Higher-level coordinating agents
  - Child/Worker: Lower-level specialized agents
- **Configuration Example**:
  ```yaml
  topology:
    pattern: "hierarchical"
    roles:
      types:
        - name: "root"
          description: "Top-level coordinator"
        - name: "manager"
          description: "Mid-level coordinator"
        - name: "worker"
          description: "Leaf-level task executor"
    relationships:
      types:
        - name: "parent_to_child"
          communication_pattern: "request_response"
        - name: "child_to_parent"
          communication_pattern: "event_based"
  ```

### 4. Mesh
- **Description**: Any agent can connect to any other agent in a densely connected network.
- **Use Cases**: Complex collaborative workflows, redundant systems, dynamic reorganization.
- **Key Components**:
  - Nodes: Multi-capable agents with various connections
- **Configuration Example**:
  ```yaml
  topology:
    pattern: "mesh"
    roles:
      types:
        - name: "node"
          description: "Multi-capable agent in mesh network"
    relationships:
      types:
        - name: "node_to_node"
          communication_pattern: "request_response"
  ```

### 5. Hybrid
- **Description**: Combination of different topology patterns for complex systems.
- **Use Cases**: Large-scale systems with varied requirements.
- **Key Components**:
  - Mixed roles from various topology patterns
- **Configuration Example**:
  ```yaml
  topology:
    pattern: "hybrid"
    roles:
      types:
        - name: "orchestrator"
          description: "Central coordinator"
        - name: "peer"
          description: "Peer node in P2P subsystem"
        - name: "worker"
          description: "Specialized task executor"
    relationships:
      types:
        - name: "orchestrator_to_peer"
          communication_pattern: "request_response"
        - name: "peer_to_peer"
          communication_pattern: "publish_subscribe"
  ```

## Integration with Unified Configuration Schema

This topology configuration is part of the [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md), which integrates all OpenMAS components into a coherent whole.

```yaml
# Example within unified schema
name: "travel_planner"
version: "0.3.0"

# Global defaults
defaults:
  # Default topology is centralized
  topology:
    pattern: "centralized"
    roles:
      types:
        - name: "orchestrator"
          description: "Central coordinator"
        - name: "worker"
          description: "Specialized service provider"
    relationships:
      types:
        - name: "orchestrator_to_worker"
          communication_pattern: "request_response"

# Agent definitions
agents:
  # Travel coordinator agent
  travel_coordinator:
    class: "agents.coordinator.TravelCoordinator"
    type: "hybrid"

    # Topology configuration
    topology:
      role: "orchestrator"
      relationships:
        - agent_id: "flight_search"
          relationship_type: "orchestrator_to_worker"
        - agent_id: "hotel_search"
          relationship_type: "orchestrator_to_worker"
```

## Agent Topology Integration

### Integration with Agent Card (A2A)

For agents using the A2A protocol, topology information can be integrated with the Agent Card:

```json
{
  "name": "Orchestrator Agent",
  "description": "Central task coordinator for the travel planning system",
  "url": "https://agent-endpoint.example.com/a2a/api",
  "capabilities": { "streaming": true },
  "skills": [...],

  "topology": {
    "role": "orchestrator",
    "relationships": [
      {
        "agentId": "flight-search",
        "relationshipType": "orchestrator_to_worker",
        "direction": "outgoing"
      },
      {
        "agentId": "hotel-search",
        "relationshipType": "orchestrator_to_worker",
        "direction": "outgoing"
      }
    ]
  }
}
```

### Integration with Multi-Protocol Support

The topology definitions work independently of communication protocols, allowing for:

1. **Protocol-Agnostic Topologies**: Define organization without coupling to specific protocols
2. **Mixed-Protocol Networks**: Combine agents using different protocols within the same topology
3. **Topology-Based Discovery**: Use topology information to discover and connect with appropriate agents

## Topology Implementation

### Definition in Project Configuration

```yaml
# openmas_project.yml
topology:
  pattern: "centralized"
  roles:
    types:
      - name: "orchestrator"
      - name: "worker"
  relationships:
    types:
      - name: "orchestrator_to_worker"
        communication_pattern: "request_response"

agents:
  travel_coordinator:
    class: "agents.coordinator.TravelCoordinator"
    topology:
      role: "orchestrator"
      relationships:
        - agent_id: "flight_search"
          relationship_type: "orchestrator_to_worker"
        - agent_id: "hotel_search"
          relationship_type: "orchestrator_to_worker"

  flight_search:
    class: "agents.flight.FlightSearchAgent"
    topology:
      role: "worker"
      relationships:
        - agent_id: "travel_coordinator"
          relationship_type: "orchestrator_to_worker"
          direction: "incoming"

  hotel_search:
    class: "agents.hotel.HotelSearchAgent"
    topology:
      role: "worker"
      relationships:
        - agent_id: "travel_coordinator"
          relationship_type: "orchestrator_to_worker"
          direction: "incoming"
```

### Example Code: Topology-Aware Agent

```python
from openmas.agent import Agent
from openmas.topology import TopologyManager

class OrchestratorAgent(Agent):
    async def setup(self):
        # Get topology manager
        self.topology_manager = TopologyManager(self)

        # Register capability
        self.register_capability(
            "coordinate_travel_planning",
            self.coordinate_travel,
            protocols=["a2a", "mcp"]
        )

    async def coordinate_travel(self, params):
        # Get worker agents based on topology relationships
        worker_agents = await self.topology_manager.get_related_agents(
            relationship_type="orchestrator_to_worker",
            direction="outgoing"
        )

        # Delegate tasks to appropriate worker agents
        flight_results = await self.topology_manager.invoke_agent(
            agent_id="flight_search",
            capability="search_flights",
            params={"origin": params["origin"], "destination": params["destination"]}
        )

        hotel_results = await self.topology_manager.invoke_agent(
            agent_id="hotel_search",
            capability="search_hotels",
            params={"location": params["destination"]}
        )

        # Combine results
        return {
            "itinerary": {
                "flights": flight_results,
                "hotels": hotel_results
            }
        }
```

## Security and Discovery

### Secure Topology Discovery

1. **Agent Card Integration**: Topology information in Agent Cards facilitates secure discovery
2. **Role-Based Access Control**: Permissions based on agent roles in the topology
3. **Relationship Verification**: Validate relationships during discovery and connection

### Topology Visualization

The standardized topology structure enables visualization of the agent network:

```
[Centralized Topology Visualization]

                          ┌─────────────────┐
                          │  Coordinator    │
                          │     Agent       │
                          └───────┬─────────┘
                                  │
                  ┌───────────────┴──────────────┐
                  │                              │
         ┌────────▼─────────┐         ┌──────────▼───────────┐
         │   Flight Search  │         │      Hotel Search    │
         │      Agent       │         │        Agent         │
         └──────────────────┘         └──────────────────────┘
```

## Environment-Specific Topology Configuration

```yaml
# config/production.yml - Environment-specific topology configuration
topology:
  # Production-specific topology overrides
  agent:
    travel_coordinator:
      relationships:
        - agent_id: "flight_search_prod"
          relationship_type: "orchestrator_to_worker"
        - agent_id: "hotel_search_prod"
          relationship_type: "orchestrator_to_worker"
```

## Topology Templates

The framework provides ready-to-use topology templates for common patterns:

1. **Basic Orchestrator**: Simple centralized pattern with one coordinator and workers
2. **Collaborative Network**: Peer-to-peer pattern for collaborative agents
3. **Command Hierarchy**: Multi-level hierarchical organization
4. **Resilient Mesh**: Fully connected mesh for fault-tolerant systems

These templates can be selected and customized to quickly configure agent networks.
