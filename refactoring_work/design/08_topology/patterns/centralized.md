# Centralized Topology Pattern

## Overview

The Centralized topology pattern (also known as Hub and Spoke) is a fundamental organization structure for multi-agent systems where a central orchestrator agent coordinates communication between specialized worker agents. This pattern provides clear command and control structure with simplified coordination logic.

## Key Components

### Orchestrator (Hub)
The orchestrator agent serves as the central coordination point, responsible for:
- Receiving and processing incoming requests
- Delegating tasks to appropriate worker agents
- Aggregating responses from workers
- Managing workflow state and coordination
- Making decisions based on collected information

### Workers (Spokes)
Worker agents are specialized agents that:
- Perform specific tasks delegated by the orchestrator
- Have focused capabilities for their domain
- Report results back to the orchestrator
- Often operate independently of other workers

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

## Use Cases

1. **Task Management Systems**: Orchestrator delegates tasks to specialized worker agents
2. **Customer Service**: Orchestrator routes customer inquiries to domain experts
3. **Content Generation**: Orchestrator coordinates specialized content creation tasks
4. **Data Processing Pipelines**: Orchestrator manages flow through processing stages

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

## Configuration Schema

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
```

## Implementation Considerations

1. **Orchestrator Design**: Ensure robust error handling and state management
2. **Worker Specialization**: Design workers with clear, focused capabilities
3. **Message Standardization**: Define clear interfaces between orchestrator and workers
4. **Scaling Considerations**: For high-load systems, consider multiple orchestrators or hierarchical patterns

## Integration with Communication Patterns

The Centralized topology works with several communication patterns:

1. **Request-Response**: Primary pattern for task delegation and completion
2. **Event-Based**: For asynchronous notifications from workers
3. **Publish-Subscribe**: For broadcasting information to multiple workers

## Protocol Compatibility

This topology is compatible with all OpenMAS-supported protocols:

| Protocol | Implementation Approach |
|----------|-------------------------|
| A2A      | Uses agent cards and tasks API |
| MCP      | Uses resource management and tool definitions |
| HTTP     | Uses RESTful endpoints |
| MQTT     | Effective for event-based notifications |
| gRPC     | High-performance service-based communication |

## Related Documentation

- [Agent Implementation of Centralized Topology](/04_agents/topologies/patterns/pattern_centralized.md) - Implementation details for agents
- [Hierarchical Topology](/08_topology/patterns/hierarchical.md) - An extension of the centralized model
- [Communication Patterns](/07_communication_patterns/README.md) - Standard message exchange patterns
