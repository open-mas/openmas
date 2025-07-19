# Centralized Topology Pattern (Hub and Spoke)

> **Note**: This document focuses on the agent implementation aspects of the Centralized topology pattern. For the authoritative documentation on the pattern's core concepts, architecture, and design principles, please refer to the [Centralized Topology Pattern](/08_topology/patterns/centralized.md) documentation.

## Overview

The Centralized (Hub and Spoke) topology pattern is a common organization structure for agent systems where a central orchestrator agent coordinates communication between specialized worker agents. This pattern is particularly useful for task delegation, workflow coordination, and systems that require central control.

This document details how agents implement this pattern in OpenMAS.

## Key Components

### Orchestrator (Hub)
The orchestrator agent is the central coordination point in the topology. It:
- Receives and processes incoming requests
- Delegates tasks to appropriate worker agents
- Aggregates responses from workers
- Manages workflow state and coordination
- Makes decisions based on collected information

### Workers (Spokes)
Worker agents are specialized agents that:
- Perform specific tasks delegated by the orchestrator
- Have focused capabilities for their domain
- Report results back to the orchestrator
- May be unaware of other workers in the system

## Communication Flow

```
                    ┌────────────────┐
                    │   Orchestrator │
                    │     Agent      │
                    └───────┬────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
┌───────────▼──┐   ┌────────▼─────┐   ┌─────▼──────────┐
│   Worker A   │   │   Worker B   │   │   Worker C     │
│ (Specialized)│   │ (Specialized)│   │  (Specialized) │
└──────────────┘   └──────────────┘   └────────────────┘
```

1. **Orchestrator to Worker**: Task delegation (request)
2. **Worker to Orchestrator**: Result reporting (response)
3. **Orchestrator Internal Processing**: Aggregation, decision making

## Configuration Example

```yaml
# Topology definition
topology:
  pattern: "centralized"
  roles:
    types:
      - name: "orchestrator"
        description: "Central coordinator for all tasks"
        capabilities:
          - "task_assignment"
          - "result_aggregation"
          - "workflow_management"
      - name: "worker"
        description: "Specialized agent for specific tasks"
        capabilities:
          - "task_execution"
          - "specialized_processing"
  relationships:
    types:
      - name: "orchestrator_to_worker"
        description: "Task delegation relationship"
        communication_pattern: "request_response"
        direction: "outgoing"
      - name: "worker_to_orchestrator"
        description: "Result reporting relationship"
        communication_pattern: "event_based"
        direction: "incoming"

# Agent-specific configuration
agents:
  travel_coordinator:
    role: "orchestrator"
    relationships:
      - agent_id: "flight_search"
        relationship_type: "orchestrator_to_worker"
      - agent_id: "hotel_search"
        relationship_type: "orchestrator_to_worker"
  
  flight_search:
    role: "worker"
    relationships:
      - agent_id: "travel_coordinator"
        relationship_type: "worker_to_orchestrator"
  
  hotel_search:
    role: "worker"
    relationships:
      - agent_id: "travel_coordinator"
        relationship_type: "worker_to_orchestrator"
```

## Protocol Compatibility

The Centralized topology pattern works with all protocols supported by OpenMAS:

| Protocol | Compatibility Notes |
|----------|---------------------|
| A2A      | Uses agent cards for discovery and tasks API for delegation |
| MCP      | Uses resource management and tool definition for specialized workers |
| HTTP     | Uses RESTful endpoints for orchestration |
| MQTT     | Effective for event-based communication to/from workers |
| gRPC     | High-performance for service-based worker communication |

## Reasoning Agnosticism

This topology pattern preserves OpenMAS's reasoning agnosticism by:

1. **Focusing on Structure**: Defining organization without dictating reasoning approaches
2. **Role-Based Capabilities**: Allowing any reasoning approach in either orchestrator or worker roles
3. **Communication Pattern Independence**: Supporting any internal reasoning process behind standard interfaces

For example, the orchestrator could use:
- LLM-based reasoning for complex task decomposition
- Rule-based reasoning for deterministic workflows
- BDI architecture for goal-directed orchestration

While workers could independently use:
- Specialized ML models for specific tasks
- Knowledge-based reasoning for domain expertise
- Hybrid approaches combining multiple methods

## Use Cases

1. **Travel Planning System**: Orchestrator coordinates flight, hotel, and activity booking through specialized workers
2. **Customer Service**: Orchestrator routes customer inquiries to specialized domain experts
3. **Content Generation**: Orchestrator breaks down content creation into specialized tasks for worker agents
4. **Data Processing Pipeline**: Orchestrator manages the flow of data through specialized processing stages

## Advantages

1. **Centralized Control**: Clear coordination point for complex workflows
2. **Separation of Concerns**: Worker agents can focus on specific capabilities
3. **Simplified Management**: System state is maintained in a central location
4. **Easier Monitoring**: Central point for observability and debugging

## Limitations

1. **Single Point of Failure**: System depends on orchestrator availability
2. **Potential Bottleneck**: High load can overwhelm the orchestrator
3. **Limited Worker Autonomy**: Workers typically only act when instructed
4. **Increased Latency**: All communication flows through the central point

## Implementation Guidance

1. **Orchestrator Design**: Ensure the orchestrator has robust error handling and state management
2. **Worker Specialization**: Design workers with clear, focused capabilities
3. **Message Standardization**: Define clear interfaces between orchestrator and workers
4. **Scaling Considerations**: For high-load systems, consider multiple orchestrators or hierarchical topologies

## Reasoning Agnosticism

The centralized topology pattern maintains OpenMAS's core principle of reasoning agnosticism through:

### Role-Based Separation

In a centralized topology, roles (orchestrator and worker) are defined independently of the reasoning approaches used by the agents. This means:

- The orchestrator can use any reasoning approach (rule-based, BDI, LLM, etc.) to coordinate tasks
- Different worker agents can use different reasoning approaches optimized for their specific tasks
- The same topology can be implemented with different reasoning approaches without changing the structure

### Protocol-Agnostic Communication

Communication between the orchestrator and workers follows protocol-independent patterns:

- Message formats are defined by the protocol, not by reasoning approaches
- Capabilities are exposed consistently regardless of the underlying reasoning
- Protocol adapters handle translation between reasoning-specific and protocol-specific formats

### Capability-Based Interaction

Interactions in the centralized topology are based on capabilities:

- Workers advertise capabilities, not reasoning approaches
- The orchestrator delegates tasks based on capability matching
- Capability interfaces remain consistent across different reasoning implementations

## Configuration Schema

For the complete configuration schema used to define centralized topologies, refer to the [OpenMAS Unified Configuration Schema](/03_configuration/schema/unified_schema_overview.md).

```yaml
# Example configuration for centralized topology
topology:
  pattern: "centralized"
  roles:
    types:
      - name: "orchestrator"
        description: "Central coordination agent"
      - name: "worker"
        description: "Specialized task worker"
  relationships:
    types:
      - name: "orchestration"
        description: "Task delegation from orchestrator to worker"
        communication_pattern: "request_response"
```
