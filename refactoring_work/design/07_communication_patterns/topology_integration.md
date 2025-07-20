# Communication Patterns and Topology Integration

## Overview

This document describes how communication patterns integrate with agent topologies in OpenMAS. This integration is central to OpenMAS's architecture, defining how agents communicate within different organizational structures.

## Integration Model

The integration between topologies and patterns follows a hierarchical model:

```
┌───────────────────────────────────────────────────┐
│                                                   │
│               Agent Topologies                    │
│           (How Agents are Organized)              │
│                                                   │
│  ┌─────────────┐     ┌─────────────────────────┐  │
│  │  Topology   │     │ Role and Relationship   │  │
│  │  Patterns   │────▶│ Definitions             │  │
│  └─────────────┘     └─────────────────────────┘  │
│                                │                   │
└────────────────────────────────┼───────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────┐
│                                                   │
│            Communication Patterns                 │
│          (How Messages are Exchanged)             │
│                                                   │
│  ┌─────────────┐     ┌─────────────────────────┐  │
│  │  Pattern    │     │ Pattern-Specific        │  │
│  │  Types      │────▶│ Configurations          │  │
│  └─────────────┘     └─────────────────────────┘  │
│                                │                   │
└────────────────────────────────┼───────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────┐
│                                                   │
│              Protocol Layer                       │
│        (How Communication is Implemented)         │
│                                                   │
│  ┌─────────────┐     ┌─────────────────────────┐  │
│  │  Protocol   │     │ Protocol-Specific       │  │
│  │  Adapters   │────▶│ Implementations         │  │
│  └─────────────┘     └─────────────────────────┘  │
│                                                   │
└───────────────────────────────────────────────────┘
```

## Topology-Pattern Mapping

Different topology types and relationships are mapped to appropriate communication patterns:

| Topology Type | Typical Relationships | Recommended Patterns |
|---------------|------------------------|---------------------|
| Hierarchical | Parent-Child | Request-Response, Delegation |
| Peer-to-Peer | Peer | Request-Response, Publish-Subscribe |
| Hub-and-Spoke | Hub-Spoke | Request-Response, Event-Based |
| Mesh | Peer | Request-Response, Publish-Subscribe, Event-Based |
| Pipeline | Upstream-Downstream | Pipeline, Streaming |
| Layered | Upper-Lower | Request-Response, Delegation |

## Configuration Integration

Topology and communication pattern configurations are integrated in the unified configuration schema:

```yaml
agents:
  travel_coordinator:
    topology:
      role: "orchestrator"
      relationships:
        - agent_id: "flight_booker"
          relationship_type: "orchestrator_to_worker"
          direction: "outgoing"
          communication_pattern: "request_response"
        - agent_id: "hotel_booker"
          relationship_type: "orchestrator_to_worker"
          direction: "outgoing"
          communication_pattern: "request_response"
        - agent_id: "itinerary_manager"
          relationship_type: "orchestrator_to_service"
          direction: "outgoing"
          communication_pattern: "delegation"

    patterns:
      request_response:
        options:
          timeout: 30000
      delegation:
        options:
          authority_verification: true
```

In this example:
- The `travel_coordinator` agent has specific relationships with other agents
- Each relationship specifies a communication pattern to use
- The agent also has pattern-specific configurations
- The topology system and pattern system work together through this configuration

## Pattern Selection Logic

The system selects patterns for agent communication following this logic:

1. If a relationship explicitly specifies a pattern, use that pattern
2. If no pattern is specified in the relationship, use the default pattern for that relationship type
3. If no default exists for the relationship type, use the default pattern for the agent
4. If no agent default exists, use the system-wide default pattern (typically Request-Response)

## Topology Types and Pattern Mapping

### Hierarchical Topology

In hierarchical topologies, patterns are typically distributed as follows:

```
             ┌───────────────┐
             │    Root       │
             └───────────────┘
                    │
         Request-Response/Delegation
          ┌─────────┴─────────┐
          │                   │
┌───────────────┐     ┌───────────────┐
│  Branch 1     │     │  Branch 2     │
└───────────────┘     └───────────────┘
         │                    │
  Request-Response      Request-Response
    ┌────┴────┐           ┌───┴───┐
    │         │           │       │
┌───────┐ ┌───────┐   ┌───────┐ ┌───────┐
│ Leaf  │ │ Leaf  │   │ Leaf  │ │ Leaf  │
└───────┘ └───────┘   └───────┘ └───────┘
```

Hierarchical topologies typically use:
- Request-Response between parent and child agents
- Delegation from parent to child for task assignment
- Event-Based patterns for status updates from children to parents

### Hub-and-Spoke Topology

Hub-and-spoke topologies organize patterns as follows:

```
     ┌────────────────────────────────┐
     │            Hub                 │
     └────────────────────────────────┘
              │         │         │
     Request-Response   │    Event-Based
      │                 │         │
┌─────────┐    ┌──────────────┐   ┌─────────┐
│ Spoke 1 │    │   Spoke 2    │   │ Spoke 3 │
└─────────┘    └──────────────┘   └─────────┘
```

Hub-and-spoke topologies typically use:
- Request-Response from hub to spokes for commands
- Event-Based from spokes to hub for status updates
- Publish-Subscribe from hub to all spokes for broadcasts

### Pipeline Topology

Pipeline topologies organize patterns as follows:

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Stage 1 │───▶│  Stage 2 │───▶│  Stage 3 │───▶│  Stage 4 │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     │               │               │               │
     ▼               ▼               ▼               ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Monitor 1│    │ Monitor 2│    │ Monitor 3│    │ Monitor 4│
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

Pipeline topologies typically use:
- Pipeline pattern between sequential stages
- Streaming for continuous data flow through stages
- Event-Based for stage completion notifications
- Request-Response for stage-specific operations

### Mesh Topology

Mesh topologies organize patterns as follows:

```
┌──────────────┐                  ┌──────────────┐
│              │◀─────────────────│              │
│   Node 1     │                  │    Node 2    │
│              │─────────────────▶│              │
└──────────────┘                  └──────────────┘
       ▲  │                              ▲  │
       │  │                              │  │
       │  │                              │  │
       │  ▼                              │  ▼
┌──────────────┐                  ┌──────────────┐
│              │◀─────────────────│              │
│   Node 3     │                  │    Node 4    │
│              │─────────────────▶│              │
└──────────────┘                  └──────────────┘
```

Mesh topologies typically use:
- Request-Response for direct point-to-point communication
- Publish-Subscribe for broadcasting to multiple nodes
- Event-Based for state changes

## Implementation Examples

### Hierarchical Topology Example

```yaml
# Define a hierarchical topology with pattern mapping
topology:
  relationships:
    types:
      - name: "orchestrator_to_worker"
        communication_patterns:
          default: "request_response"
          alternative: "delegation"
      - name: "worker_to_orchestrator"
        communication_patterns:
          default: "event_based"
          alternative: "request_response"

# Configure specific agents within the hierarchy
agents:
  workflow_orchestrator:
    class: "agents.workflow.Orchestrator"
    communicator_type: "a2a"
    topology:
      role: "orchestrator"
      relationships:
        - agent_id: "task_worker_1"
          relationship_type: "orchestrator_to_worker"
          direction: "outgoing"
        - agent_id: "task_worker_2"
          relationship_type: "orchestrator_to_worker"
          direction: "outgoing"
    patterns:
      request_response:
        options:
          timeout: 60000
      delegation:
        options:
          delegation_timeout: 300000

  task_worker_1:
    class: "agents.workflow.Worker"
    communicator_type: "a2a"
    topology:
      role: "worker"
      relationships:
        - agent_id: "workflow_orchestrator"
          relationship_type: "worker_to_orchestrator"
          direction: "outgoing"
    patterns:
      event_based:
        options:
          event_history_size: 50
```

### Pipeline Topology Example

```yaml
# Define a pipeline topology with pattern mapping
topology:
  relationships:
    types:
      - name: "pipeline_stage"
        communication_patterns:
          default: "pipeline"
          alternative: "streaming"
      - name: "monitoring"
        communication_patterns:
          default: "event_based"

# Configure agents in the pipeline
agents:
  content_node_1:
    class: "agents.content.ContentNode"
    communicator_type: "mqtt"
    topology:
      role: "pipeline_stage"
      relationships:
        - agent_id: "content_node_2"
          relationship_type: "pipeline_stage"
          direction: "outgoing"
        - agent_id: "monitor_node"
          relationship_type: "monitoring"
          direction: "outgoing"
    patterns:
      pipeline:
        options:
          stage_timeout: 30000
      event_based:
        options:
          event_history_size: 100

  content_node_2:
    class: "agents.content.ContentNode"
    communicator_type: "mqtt"
    topology:
      role: "pipeline_stage"
      relationships:
        - agent_id: "content_node_3"
          relationship_type: "pipeline_stage"
          direction: "outgoing"
        - agent_id: "monitor_node"
          relationship_type: "monitoring"
          direction: "outgoing"
```

## Runtime Integration

At runtime, the integration between topologies and patterns is managed by these components:

```python
class PatternManager:
    """Manages communication patterns for an agent."""

    def __init__(self, agent_id, patterns_config, pattern_factory):
        """Initialize the pattern manager."""
        self.agent_id = agent_id
        self.patterns_config = patterns_config
        self.pattern_factory = pattern_factory
        self.patterns = {}

    async def initialize(self, topology_manager):
        """Initialize patterns based on topology relationships."""
        relationships = await topology_manager.get_relationships()

        # Create patterns based on relationships
        for relationship in relationships:
            pattern_type = relationship.communication_pattern
            if pattern_type and pattern_type not in self.patterns:
                self.patterns[pattern_type] = await self.pattern_factory.create_pattern(
                    pattern_type,
                    self.patterns_config.get(pattern_type, {})
                )

        # Initialize all patterns
        for pattern in self.patterns.values():
            await pattern.initialize()

    async def get_pattern_for_relationship(self, relationship):
        """Get the appropriate pattern for a relationship."""
        pattern_type = relationship.communication_pattern
        return self.patterns.get(pattern_type)
```

## Best Practices

1. **Match Patterns to Topology**: Select communication patterns that naturally fit the topology type and relationship semantics.

2. **Use Relationship-Specific Pattern Overrides**: When a relationship requires a different pattern than the default for its type, specify it explicitly in the relationship configuration.

3. **Maintain Consistent Patterns**: Within a topology, maintain consistent pattern usage for similar relationships to avoid confusion.

4. **Consider Fallback Patterns**: Configure alternative patterns that can be used when the primary pattern isn't available or appropriate.

5. **Balance Flexibility and Standardization**: While allowing flexibility in pattern selection, establish standard patterns for common relationship types to maintain consistency.

## References

- [Communication Patterns Architecture](/refactoring_work/00b_overview/01_architecture/communication_patterns_architecture.md)
- [Topology Documentation](/refactoring_work/00b_overview/08_topology/)
- [Communication Patterns Configuration](/refactoring_work/00b_overview/03_configuration/schema/communication_patterns.md)
