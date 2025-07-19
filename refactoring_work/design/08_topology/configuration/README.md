# Topology Configuration

## Overview

This directory contains documentation about configuring agent topologies in OpenMAS. Topology configuration defines how agents are organized, their relationships, and the structure of their interactions.

## Configuration Structure

Topology configuration includes:

1. **Pattern Selection**
   - Specifies which topology pattern to use (centralized, hierarchical, peer-to-peer, etc.)
   - See: [Topology Patterns](/08_topology/patterns/README.md)

2. **Role Definitions**
   - Defines the roles that agents can take within the topology
   - Associates capabilities with roles
   - See: [Topology Roles](/08_topology/roles/README.md)

3. **Agent Assignments**
   - Maps specific agents to roles within the topology
   - Can be static or dynamic

4. **Relationship Rules**
   - Defines valid communication paths between roles
   - Specifies authority relationships
   - Defines data sharing policies

5. **Discovery Mechanisms**
   - Configuration for how agents find each other within the topology
   - Service discovery integrations

## Configuration Example

```yaml
topology:
  pattern: "hierarchical"
  roles:
    types:
      - name: "orchestrator"
        capabilities: ["task_assignment", "status_monitoring"]
      - name: "coordinator"
        capabilities: ["subtask_delegation", "resource_management"]
      - name: "worker"
        capabilities: ["task_execution", "status_reporting"]
    assignments:
      - agent_id: "central_manager"
        role: "orchestrator"
      - agent_id: "team_lead_1"
        role: "coordinator"
      - agent_id: "team_lead_2"
        role: "coordinator"
      - agent_id: "worker_1"
        role: "worker"
  relationships:
    - from_role: "orchestrator"
      to_role: "coordinator"
      relationship_type: "manages"
    - from_role: "coordinator" 
      to_role: "worker"
      relationship_type: "manages"
  discovery:
    mechanism: "configuration"
    refresh_interval: 300
```

## Integration with Unified Configuration

Topology configuration is part of the unified configuration schema:

- [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md)
- [Agent Configuration Schema](/03_configuration/schema/agents.md)

## Dynamic Configuration

OpenMAS supports dynamic topology configuration through:

1. **Runtime Reconfiguration**
   - API for updating topology during operation
   - Role reassignment mechanisms
   - See: [Dynamic Topology Management](/08_topology/dynamic_management.md)

2. **Self-Organization**
   - Configuration parameters for emergent organization
   - Rules for automatic role assignment
   - See: [Self-Organizing Topologies](/08_topology/self_organization.md)

## Configuration Validation

When configuring topologies, validation ensures:

1. All required roles for a pattern are defined
2. Agents have necessary capabilities for their assigned roles
3. Relationship rules are consistent with the chosen pattern
4. No circular authority relationships exist

## References

- [Topology Patterns](/08_topology/patterns/README.md)
- [Topology Roles](/08_topology/roles/README.md)
- [Agent Configuration](/03_configuration/schema/agents.md)
- [Communication Pattern Configuration](/07_communication_patterns/configuration.md)
