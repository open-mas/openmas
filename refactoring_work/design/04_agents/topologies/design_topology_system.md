# Agent Topology Design

## Overview

The OpenMAS Agent Topology system provides a flexible, configurable approach to organizing multi-agent systems. Topologies define the organizational structure, communication pathways, and role-based relationships between agents, ensuring consistent and efficient interaction patterns regardless of the underlying protocols used.

## Core Principles

1. **Protocol Independence**: Topologies work with any protocol (A2A, MCP, HTTP, etc.)
2. **Role-Based Organization**: Agents are assigned specific roles within the topology
3. **Relationship-Driven**: Inter-agent relationships define communication paths
4. **Pattern Flexibility**: Multiple topology patterns can be composed or combined
5. **Dynamic Discovery**: Topologies support runtime agent discovery
6. **Capability Alignment**: Roles and capabilities are aligned within topologies

## Topology Patterns

OpenMAS supports these standard topology patterns:

1. **Centralized**: Hub-and-spoke model with a central coordinator
2. **Peer-to-Peer**: Flat structure where all agents can communicate directly
3. **Hierarchical**: Tree-like structure with parent-child relationships
4. **Team-Based**: Collaborative groups with specific team objectives
5. **Hybrid**: Combination of different topology patterns for complex systems

## Architecture Implementation

### TopologyManager Class

The `TopologyManager` class manages topology-based interactions:

```python
class TopologyManager:
    def __init__(self, agent):
        self.agent = agent
        self.config = agent.config.get("topology", {})
        self.pattern = self.config.get("pattern", "centralized")
        self.role = self.config.get("role", {}).get("type", "generic")
        self.relationships = {}

        # Initialize pattern strategy based on configuration
        self.pattern_strategy = self._create_pattern_strategy()

        # Initialize relationships from configuration
        self._initialize_relationships()

    def _create_pattern_strategy(self):
        """Create appropriate pattern strategy based on topology pattern."""
        if self.pattern == "centralized":
            return CentralizedPatternStrategy(self)
        elif self.pattern == "peer_to_peer":
            return PeerToPeerPatternStrategy(self)
        elif self.pattern == "hierarchical":
            return HierarchicalPatternStrategy(self)
        elif self.pattern == "team_based":
            return TeamBasedPatternStrategy(self)
        elif self.pattern == "hybrid":
            return HybridPatternStrategy(self)
        else:
            logger.warning(f"Unknown pattern type: {self.pattern}, using centralized")
            return CentralizedPatternStrategy(self)

    def _initialize_relationships(self):
        """Initialize relationships from configuration."""
        relationship_config = self.config.get("relationships", {})
        for rel_type, targets in relationship_config.items():
            self.relationships[rel_type] = targets

    async def get_related_agents(self, relationship_type=None, role=None):
        """Get agents related to this agent based on relationship type and/or role."""
        # Delegate to pattern strategy to find related agents
        return await self.pattern_strategy.get_related_agents(relationship_type, role)

    async def invoke_agent(self, agent_id, capability, params=None):
        """Invoke a capability on a specific agent."""
        # Find the agent with this ID
        agent = await self._find_agent_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")

        # Invoke the capability
        return await self.agent.invoke_remote_capability(agent, capability, params or {})

    async def _find_agent_by_id(self, agent_id):
        """Find an agent by ID in the current topology."""
        # Implementation depends on agent registry/discovery mechanism
        registry = self.agent.get_registry()
        return await registry.get_agent(agent_id)

    def get_role(self):
        """Get this agent's role in the topology."""
        return self.role

    def get_pattern(self):
        """Get the topology pattern."""
        return self.pattern

    def check_relationship(self, other_agent, relationship_type):
        """Check if this agent has a specific relationship with another agent."""
        # Delegate to pattern strategy to check relationship
        return self.pattern_strategy.check_relationship(other_agent, relationship_type)
```

### Pattern Strategy Interface

Pattern strategies encapsulate pattern-specific behavior:

```python
class PatternStrategy:
    """Base class for topology pattern strategies."""

    def __init__(self, topology_manager):
        self.topology_manager = topology_manager
        self.agent = topology_manager.agent

    async def get_related_agents(self, relationship_type=None, role=None):
        """Get agents related to this agent based on relationship type and/or role."""
        raise NotImplementedError("Subclasses must implement this")

    def check_relationship(self, other_agent, relationship_type):
        """Check if this agent has a specific relationship with another agent."""
        raise NotImplementedError("Subclasses must implement this")
```

### Centralized Pattern Implementation

Example implementation for the centralized pattern:

```python
class CentralizedPatternStrategy(PatternStrategy):
    """Strategy for centralized topology pattern."""

    async def get_related_agents(self, relationship_type=None, role=None):
        """Get agents related to this agent based on relationship type and/or role."""
        registry = self.agent.get_registry()

        if self.topology_manager.get_role() == "coordinator":
            # Coordinator can get all worker agents
            if role == "worker" or not role:
                return await registry.get_agents_by_role("worker")
            else:
                return []
        else:
            # Workers can only get coordinator
            if role == "coordinator" or not role:
                return await registry.get_agents_by_role("coordinator")
            else:
                return []

    def check_relationship(self, other_agent, relationship_type):
        """Check if this agent has a specific relationship with another agent."""
        my_role = self.topology_manager.get_role()
        other_role = other_agent.topology_manager.get_role()

        # In centralized topology:
        # - coordinator can communicate with all workers
        # - workers can only communicate with coordinator
        if my_role == "coordinator" and other_role == "worker":
            return True
        elif my_role == "worker" and other_role == "coordinator":
            return True
        else:
            return False
```

### Role Manager

The `RoleManager` handles role-specific capabilities:

```python
class RoleManager:
    """Manages role-specific behavior and capabilities."""

    def __init__(self, agent, role_config):
        self.agent = agent
        self.role_type = role_config.get("type", "generic")
        self.role_params = role_config.get("parameters", {})
        self.capabilities = role_config.get("capabilities", [])

    def get_role_capabilities(self):
        """Get capabilities specific to this role."""
        return self.capabilities

    def check_capability_permission(self, capability_name):
        """Check if this role is allowed to use a capability."""
        return capability_name in self.capabilities

    def get_role_parameters(self):
        """Get role-specific parameters."""
        return self.role_params
```

## Topology Discovery and Registry

The `AgentRegistry` enables topology-based discovery:

```python
class AgentRegistry:
    """Registry for discovering and tracking agents in a topology."""

    def __init__(self, config):
        self.config = config
        self.agents = {}
        self.discovery_providers = []

        # Initialize discovery providers
        self._initialize_discovery_providers()

    def _initialize_discovery_providers(self):
        """Initialize discovery providers from configuration."""
        providers_config = self.config.get("discovery", {}).get("providers", [])
        for provider_config in providers_config:
            provider_type = provider_config.get("type")
            if provider_type == "local":
                self.discovery_providers.append(LocalDiscoveryProvider(provider_config))
            elif provider_type == "registry_service":
                self.discovery_providers.append(RegistryServiceProvider(provider_config))
            elif provider_type == "dns_sd":
                self.discovery_providers.append(DNSSDDiscoveryProvider(provider_config))

    async def register_agent(self, agent):
        """Register an agent with this registry."""
        agent_id = agent.get_id()
        self.agents[agent_id] = agent

        # Register with all discovery providers
        for provider in self.discovery_providers:
            await provider.register_agent(agent)

    async def unregister_agent(self, agent_id):
        """Unregister an agent from this registry."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            del self.agents[agent_id]

            # Unregister from all discovery providers
            for provider in self.discovery_providers:
                await provider.unregister_agent(agent)

    async def get_agent(self, agent_id):
        """Get an agent by ID."""
        # Check local cache first
        if agent_id in self.agents:
            return self.agents[agent_id]

        # Check all discovery providers
        for provider in self.discovery_providers:
            agent = await provider.get_agent(agent_id)
            if agent:
                # Cache the agent
                self.agents[agent_id] = agent
                return agent

        return None

    async def get_agents_by_role(self, role):
        """Get agents by role."""
        result = []

        # Check local cache
        for agent in self.agents.values():
            if agent.topology_manager.get_role() == role:
                result.append(agent)

        # Check all discovery providers
        for provider in self.discovery_providers:
            agents = await provider.get_agents_by_role(role)
            for agent in agents:
                if agent.get_id() not in self.agents:
                    # Cache the agent
                    self.agents[agent.get_id()] = agent
                    result.append(agent)

        return result
```

## Topology-Based Communication

The `TopologyCommunicator` handles topology-aware messaging:

```python
class TopologyCommunicator:
    """Handles communication based on topology configuration."""

    def __init__(self, agent):
        self.agent = agent
        self.topology_manager = agent.topology_manager

    async def send_to_related(self, message, relationship_type=None, role=None):
        """Send a message to all related agents."""
        related_agents = await self.topology_manager.get_related_agents(
            relationship_type, role
        )

        results = []
        for agent in related_agents:
            # Select best protocol for communication
            protocol = self._select_protocol(agent)
            result = await self.agent.send_message(agent, message, protocol)
            results.append(result)

        return results

    async def broadcast(self, message, role=None):
        """Broadcast a message to all agents in the topology."""
        registry = self.agent.get_registry()

        if role:
            agents = await registry.get_agents_by_role(role)
        else:
            agents = list(registry.agents.values())

        results = []
        for agent in agents:
            if agent.get_id() == self.agent.get_id():
                continue  # Skip self

            # Select best protocol for communication
            protocol = self._select_protocol(agent)
            result = await self.agent.send_message(agent, message, protocol)
            results.append(result)

        return results

    def _select_protocol(self, target_agent):
        """Select the best protocol for communicating with target agent."""
        # Get common protocols
        my_protocols = self.agent.get_protocol_types()
        target_protocols = target_agent.get_protocol_types()
        common_protocols = set(my_protocols).intersection(set(target_protocols))

        # Protocol preference order
        preference = ["a2a-grpc", "a2a-websocket", "a2a-http", "mcp-streamable",
                      "mcp-sse", "mcp-stdio", "grpc", "websocket", "http", "mqtt"]

        for protocol in preference:
            if protocol in common_protocols:
                return protocol

        # Default to first common protocol
        if common_protocols:
            return list(common_protocols)[0]

        raise ValueError(f"No common protocol found with agent {target_agent.get_id()}")
```

## Configuration Example

```yaml
# System-wide topology configuration
topology:
  pattern: "hierarchical"
  roles:
    definition:
      # Root role
      supervisor:
        description: "Top-level supervisor agent"
        capabilities: ["delegate", "monitor", "audit"]

      # Middle management role
      manager:
        description: "Mid-level manager agent"
        capabilities: ["delegate", "report", "coordinate"]

      # Worker role
      worker:
        description: "Task execution agent"
        capabilities: ["execute", "report"]

  relationships:
    definition:
      # Hierarchical supervision relationship
      supervises:
        description: "A supervises B"
        permissions: ["delegate", "monitor", "override"]

      # Peer collaboration
      collaborates_with:
        description: "A collaborates with B"
        permissions: ["request", "inform"]

# Agent-specific topology configuration
agents:
  head_agent:
    class: "openmas.agent.SupervisorAgent"
    topology:
      pattern: "hierarchical"
      role:
        type: "supervisor"
      relationships:
        supervises: ["team_a_manager", "team_b_manager"]

  team_a_manager:
    class: "openmas.agent.ManagerAgent"
    topology:
      pattern: "hierarchical"
      role:
        type: "manager"
      relationships:
        supervises: ["worker_1", "worker_2"]
        reports_to: ["head_agent"]

  worker_1:
    class: "openmas.agent.WorkerAgent"
    topology:
      pattern: "hierarchical"
      role:
        type: "worker"
      relationships:
        reports_to: ["team_a_manager"]
        collaborates_with: ["worker_2"]
```

## Agent Topology Integration with Protocols

### A2A Protocol Integration

For A2A protocol, topology information is embedded in agent cards:

```json
{
  "agent_name": "head_agent",
  "description": "Supervisor agent coordinating the system",
  "capabilities": [...],
  "topology": {
    "pattern": "hierarchical",
    "role": {
      "type": "supervisor"
    },
    "relationships": {
      "supervises": ["team_a_manager", "team_b_manager"]
    }
  }
}
```

### MCP Integration

For MCP, topology information is made available through system messages:

```json
{
  "system_message": "This is a supervisor agent in a hierarchical topology, responsible for managing team_a_manager and team_b_manager."
}
```

## Protocol-Agnostic Invocation

The `TopologyManager` enables protocol-agnostic capability invocation:

```python
# Agent code (protocol-agnostic)
result = await self.topology_manager.invoke_agent(
    agent_id="worker_1",
    capability="process_data",
    params={"data": input_data}
)
```

Behind the scenes, the `TopologyManager` will:
1. Find the agent with ID "worker_1" using the registry
2. Determine the best protocol to use for communication
3. Invoke the capability using that protocol

## Security Considerations

1. **Relationship Verification**: Before communication, agents verify their relationship
2. **Role-Based Access Control**: Capabilities are restricted based on role
3. **Secure Discovery**: Agent discovery respects security boundaries
4. **Audit Trail**: Topology-based communication provides clear audit trails

## Benefits of Topology-Based Design

1. **Organizational Clarity**: Clear agent relationships and responsibilities
2. **Protocol Flexibility**: Works with any protocol
3. **Dynamic Reconfiguration**: Runtime topology changes
4. **Role-Based Capabilities**: Capabilities aligned with agent roles
5. **Simplified Routing**: Automatic message routing based on topology
6. **Scalability**: Easily scaled by adding agents in appropriate roles

This topology-based design is a key organizational principle in OpenMAS, providing structure to multi-agent systems while maintaining protocol flexibility and reasoning agnosticism.
