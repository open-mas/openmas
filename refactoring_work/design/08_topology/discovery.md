# Topology Discovery

## Overview

Topology Discovery in OpenMAS provides mechanisms for agents to find and connect with each other, enabling the formation and maintenance of topology structures. Discovery is a critical foundation for all topology patterns, allowing agents to establish relationships based on roles, capabilities, and organizational needs.

## Discovery Mechanisms

OpenMAS supports several discovery mechanisms that can be used across different topology patterns:

### 1. Configuration-Based Discovery

The simplest discovery approach where relationships are explicitly defined in configuration:

```yaml
topology:
  discovery:
    mechanism: "configuration"
    agents:
      - id: "coordinator_agent"
        role: "orchestrator"
        relationships:
          - agent_id: "worker_agent_1"
            relationship_type: "orchestrator_to_worker"
          - agent_id: "worker_agent_2"
            relationship_type: "orchestrator_to_worker"
```

**Characteristics:**
- Predictable and deterministic topology
- No runtime discovery overhead
- Requires prior knowledge of all agents
- Limited adaptability to changes

### 2. Registry-Based Discovery

A central registry service that agents can query to find others:

```yaml
topology:
  discovery:
    mechanism: "registry"
    registry_service: "topology_registry"
    query_interval: 60  # Seconds
    registration_ttl: 300  # Seconds
```

**Characteristics:**
- Dynamic agent discovery at runtime
- Centralized point for topology information
- Support for filtering by roles and capabilities
- Potential single point of failure

### 3. Broadcast Discovery

Agents announce their presence and discover others through broadcast messages:

```yaml
topology:
  discovery:
    mechanism: "broadcast"
    announcement_interval: 30  # Seconds
    broadcast_channel: "agent_discovery"
    listen_timeout: 5  # Seconds
```

**Characteristics:**
- Fully decentralized discovery
- No central point of failure
- Higher network overhead
- Well-suited for peer-to-peer and mesh topologies

### 4. Hierarchical Discovery

Discovery through a hierarchical structure of discovery services:

```yaml
topology:
  discovery:
    mechanism: "hierarchical"
    levels:
      - name: "global"
        service: "global_registry"
        scope: "system"
      - name: "domain"
        service: "domain_registry"
        scope: "domain"
      - name: "local"
        service: "local_broadcast"
        scope: "local"
```

**Characteristics:**
- Scalable to large systems
- Combines benefits of registry and broadcast
- Domain-specific discovery boundaries
- More complex implementation

### 5. Capability-Based Discovery

Discovery based on agent capabilities rather than explicit identities:

```yaml
topology:
  discovery:
    mechanism: "capability"
    required_capabilities:
      - capability: "data_processing"
        min_score: 0.8
      - capability: "response_time"
        max_value: 200  # ms
```

**Characteristics:**
- Function-oriented rather than identity-oriented
- Supports load balancing and redundancy
- Enables dynamic role assignment
- Well-suited for self-organizing topologies

## Protocol-Specific Discovery

Different protocols implement discovery mechanisms in protocol-specific ways:

### A2A Protocol Discovery

A2A protocol uses agent cards and directory services:

```yaml
discovery:
  mechanism: "a2a_directory"
  directory_service: "https://directory.example.com"
  agent_card:
    capabilities:
      - "data_processing"
      - "language_translation"
    roles:
      - "worker"
```

### MCP Protocol Discovery

MCP protocol uses tool registration and capability advertisements:

```yaml
discovery:
  mechanism: "mcp_registry"
  tool_registration:
    service_url: "https://registry.example.com"
    capabilities:
      - name: "data_processing"
        description: "Processes various data formats"
```

### MQTT Protocol Discovery

MQTT uses topic-based discovery with presence indicators:

```yaml
discovery:
  mechanism: "mqtt_topics"
  presence_topic: "agents/presence"
  capability_topic: "agents/capabilities"
  role_topic: "agents/roles"
```

## Integration with Topology Patterns

Different topology patterns have specific discovery requirements:

| Topology Pattern | Preferred Discovery Mechanisms |
|------------------|--------------------------------|
| Centralized      | Configuration, Registry |
| Hierarchical     | Hierarchical, Registry |
| Peer-to-Peer     | Broadcast, Capability-based |
| Mesh             | Broadcast, Registry, Capability-based |
| Hybrid           | Combination based on components |

## Implementation Considerations

When implementing topology discovery:

### 1. Security

- **Authentication**: Verify agent identities during discovery
- **Authorization**: Ensure agents can only discover appropriate peers
- **Encryption**: Protect discovery traffic from eavesdropping
- **Validation**: Verify discovered information is legitimate

### 2. Performance

- **Caching**: Cache discovery results to reduce overhead
- **Incremental Updates**: Only transfer changes, not complete state
- **Lazy Loading**: Discover information only when needed
- **Batching**: Group discovery operations for efficiency

### 3. Resilience

- **Fallback Mechanisms**: Support multiple discovery approaches
- **Timeout Handling**: Properly handle discovery failures
- **Stale Data Management**: Handle outdated discovery information
- **Consistency**: Ensure consistent view across distributed agents

## Discovery Configuration Schema

```yaml
# Complete discovery configuration schema
discovery:
  # Primary mechanism
  mechanism: "registry"  # Options: configuration, registry, broadcast, hierarchical, capability
  
  # General settings
  refresh_interval: 60  # Seconds between discovery attempts
  cache_ttl: 300  # Seconds to cache discovery results
  
  # Registry-specific settings
  registry:
    service_url: "https://registry.example.com"
    credentials:
      auth_type: "jwt"
      token: "${ENV_REGISTRY_TOKEN}"
    
  # Broadcast-specific settings
  broadcast:
    channel: "discovery"
    protocol: "multicast"  # Options: multicast, broadcast, gossip
    interval: 30  # Seconds
    
  # Hierarchical-specific settings
  hierarchical:
    levels:
      - name: "global"
        mechanism: "registry"
        scope: "system"
      - name: "local" 
        mechanism: "broadcast"
        scope: "subnet"
        
  # Capability-specific settings
  capability:
    query_params:
      - capability: "data_processing"
        min_score: 0.8
      - capability: "response_time"
        max_value: 200  # ms
        
  # Filters
  filters:
    roles: ["worker", "coordinator"]
    domains: ["finance", "hr"]
    capabilities: ["data_processing", "reporting"]
```

## Reasoning Agnosticism

The topology discovery system maintains OpenMAS's reasoning agnosticism through:

1. **Interface-Based Discovery**: Discovering interfaces and capabilities, not reasoning implementations
2. **Capability Advertisement**: Advertising what agents can do, not how they reason
3. **Protocol-Independent Abstractions**: Core discovery concepts apply across all protocols
4. **Role-Based Discovery**: Finding agents based on roles, not reasoning approaches

## References

- [Topology Architecture](./architecture.md)
- [Dynamic Topology Management](./dynamic_management.md)
- [Self-Organizing Topologies](./self_organization.md)
- [Agent Implementation](/04_agents/topologies/README.md)
- [Protocol Adapters](/02_protocols/README.md)
