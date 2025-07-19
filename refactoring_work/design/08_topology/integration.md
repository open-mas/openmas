# Topology Integration

## Overview

This document describes how the OpenMAS topology system integrates with other components of the framework. The topology system is designed to work seamlessly with other architectural components while maintaining OpenMAS's core principles of reasoning agnosticism and protocol independence.

## Integration with Agent Framework

The topology system integrates with the Agent Framework in several key ways:

### Agent Lifecycle Integration

```
┌─────────────────┐                    ┌─────────────────┐
│                 │  1. Agent Created  │                 │
│  Agent          │ ─────────────────► │  Topology       │
│  Framework      │                    │  System         │
│                 │ ◄───────────────── │                 │
│                 │  2. Role Assigned  │                 │
└─────────────────┘                    └─────────────────┘
```

1. **Agent Creation**: When an agent is created, the topology system is notified
2. **Role Assignment**: The topology system assigns appropriate roles based on configuration
3. **Capability Registration**: Agent capabilities are registered and matched to roles
4. **Relationship Establishment**: The topology system establishes relationships based on patterns
5. **Agent Termination**: When an agent terminates, the topology updates relationships accordingly

### Implementation Interface

```python
# Example: Agent Framework and Topology Integration
class Agent:
    async def setup(self):
        # Register with topology system
        self.topology_manager = TopologyManager(self)
        await self.topology_manager.register()
        
        # Roles and relationships are established based on configuration
        await self.topology_manager.establish_relationships()
```

## Integration with Communication Patterns

The topology system works closely with communication patterns:

### Pattern Mapping

Each topology relationship maps to specific communication patterns:

| Topology Relationship | Communication Pattern |
|-----------------------|------------------------|
| Orchestrator-Worker   | Request-Response       |
| Coordinator-Subordinate | Delegation           |
| Peer-Peer             | Direct Communication   |
| Mesh Node Connection  | Optimized Routing      |

### Message Flow Control

```
┌─────────────────┐                    ┌─────────────────┐
│                 │  1. Send Request   │                 │
│  Agent          │ ─────────────────► │  Topology       │
│  (Sender)       │                    │  System         │
│                 │ ◄───────────────── │                 │
│                 │  2. Validate Path  │                 │
└─────────────────┘                    └─────────────────┘
        │                                      │
        │                                      ▼
        │                             ┌─────────────────┐
        │                             │  Communication  │
        │                             │  Pattern        │
        │                             │  Subsystem      │
        │                             └────────┬────────┘
        │                                      │
        ▼                                      ▼
┌─────────────────┐                    ┌─────────────────┐
│                 │  3. Deliver Msg    │                 │
│  Agent          │ ◄───────────────── │  Protocol       │
│  (Receiver)     │                    │  Layer          │
└─────────────────┘                    └─────────────────┘
```

1. The topology system validates that communication paths are allowed by the topology
2. Communication patterns determine how messages are structured and exchanged
3. The protocol layer handles the actual transmission

## Integration with Protocol Layer

The topology system maintains protocol independence:

### Protocol Adapters

Each supported protocol has adapters that implement topology-specific features:

| Protocol | Topology Implementation |
|----------|-------------------------|
| A2A      | Agent cards with role capabilities |
| MCP      | Tool specifications based on roles |
| HTTP     | RESTful endpoints reflecting topology |
| MQTT     | Topic structures reflecting relationships |
| gRPC     | Service definitions based on roles |

### Discovery Mechanisms

Different protocols use different discovery mechanisms:

1. **A2A**: Directory-based discovery with capability matching
2. **MCP**: Tool registration and capability advertisement
3. **HTTP**: Service registries and API documentation
4. **MQTT**: Topic discovery and subscription
5. **gRPC**: Service reflection and registry

## Integration with Configuration System

The topology system is configured through the unified configuration schema:

### Schema Integration

```yaml
# Excerpt from unified configuration schema
topology:
  pattern: "hierarchical"
  roles:
    types:
      - name: "orchestrator"
        capabilities: ["task_assignment", "status_monitoring"]
      - name: "worker"
        capabilities: ["task_execution", "status_reporting"]
  relationships:
    types:
      - name: "orchestrator_to_worker"
        communication_pattern: "request_response"
```

### Configuration Validation

The configuration system validates topology configurations:
1. **Pattern Validation**: Ensuring the pattern is supported
2. **Role Validation**: Verifying roles are appropriate for the pattern
3. **Relationship Validation**: Ensuring relationships are valid for the pattern
4. **Capability Validation**: Verifying agents have required capabilities for roles

## Integration with Observability

The topology system integrates with the observability framework:

### Metrics and Monitoring

Key metrics exposed by the topology system:
1. **Topology Health**: Overall health status of the topology
2. **Relationship Status**: Status of individual relationships
3. **Message Flow**: Volume and patterns of messages within the topology
4. **Role Distribution**: Distribution of agents across roles

### Logging and Tracing

The topology system produces logs and traces for:
1. **Topology Changes**: Creation, modification, or deletion of relationships
2. **Role Assignments**: Changes in agent roles
3. **Relationship Events**: Establishment, maintenance, or termination of relationships
4. **Error Conditions**: Issues with topology configuration or operation

## Integration with Security

The topology system enforces security boundaries:

### Authorization

1. **Role-Based Access Control**: Permissions based on agent roles
2. **Relationship-Based Authorization**: Communication allowed only along established relationships
3. **Capability Verification**: Ensuring agents have required capabilities for operations

### Secure Communication

1. **Secure Channels**: Ensuring communication paths are secure
2. **Message Validation**: Verifying message authenticity and integrity
3. **Relationship Verification**: Confirming relationship validity before communication

## Reasoning Agnosticism

Throughout all integrations, the topology system maintains OpenMAS's core principle of reasoning agnosticism:

1. **Interface-Based Integration**: Components interact through well-defined interfaces
2. **Capability-Based Relationships**: Relationships based on capabilities, not reasoning approaches
3. **Protocol-Independent Communication**: Consistent communication regardless of reasoning implementation
4. **Role-Based Organization**: Roles defined by responsibilities, not reasoning mechanisms

## References

- [Topology Architecture](/08_topology/architecture.md)
- [Agent Implementation](/04_agents/topologies/README.md)
- [Communication Patterns](/07_communication_patterns/README.md)
- [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md)
