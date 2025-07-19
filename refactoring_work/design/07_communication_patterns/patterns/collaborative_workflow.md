# Collaborative Workflow Pattern

## Overview

The Collaborative Workflow pattern enables structured collaboration between multiple agents with specialized roles to solve complex problems that require diverse capabilities. This pattern coordinates agent interactions through defined workflows while maintaining OpenMAS's reasoning agnosticism.

## Key Capabilities

The Collaborative Workflow pattern provides these core capabilities:

1. **Multi-Agent Coordination** - Structured collaboration between specialized agents
2. **Workflow Definition** - Clear definition of collaboration stages and transitions
3. **Role-Based Interaction** - Explicit role assignment and responsibility management
4. **State Tracking** - Shared context and state management across collaborating agents
5. **Protocol Agnosticism** - Works across all supported protocols

## Pattern Structure

### Components

- **Coordinator** - Agent that orchestrates the collaborative workflow
- **Participants** - Specialized agents that contribute to specific workflow stages
- **Workflow Definition** - Schema defining stages, transitions, and responsibilities
- **Shared Context** - Common state accessible to all participating agents

### Message Types

- **workflow_initiation** - Begins the collaborative workflow
- **stage_assignment** - Assigns a participant to a workflow stage
- **stage_completion** - Signals completion of a workflow stage
- **workflow_conclusion** - Final outcome of the collaborative process

## Implementation Example

```python
# Using the Collaborative Workflow pattern
async def collaborative_task(coordinator_agent, problem_description):
    # Initialize collaborative workflow
    workflow = await coordinator_agent.patterns.collaborative_workflow.create(
        workflow_definition={
            "name": "research_analysis_workflow",
            "stages": [
                {"id": "data_collection", "role": "researcher", "depends_on": []},
                {"id": "data_analysis", "role": "analyst", "depends_on": ["data_collection"]},
                {"id": "insights_generation", "role": "insights_agent", "depends_on": ["data_analysis"]},
                {"id": "report_creation", "role": "writer", "depends_on": ["insights_generation"]}
            ]
        },
        initial_context={
            "problem": problem_description,
            "parameters": {"depth": "comprehensive", "format": "structured"}
        },
        participants=[
            {"agent_id": "research_agent_1", "roles": ["researcher"]},
            {"agent_id": "analysis_agent_1", "roles": ["analyst"]},
            {"agent_id": "insights_agent_1", "roles": ["insights_agent"]},
            {"agent_id": "writer_agent_1", "roles": ["writer"]}
        ]
    )
    
    # Start the workflow
    workflow_execution = await workflow.start()
    
    # Monitor progress
    while not workflow_execution.is_complete:
        status = await workflow_execution.get_status()
        current_stage = status.current_stage
        # Optionally provide guidance or intervention
        if current_stage.id == "data_analysis" and current_stage.duration > 300:
            await workflow_execution.provide_guidance(
                stage_id="data_analysis",
                guidance="Consider limiting analysis to key metrics X, Y, Z"
            )
        await asyncio.sleep(10)
    
    # Get final result
    result = await workflow_execution.get_result()
    return result
```

## Protocol Adaptations

The Collaborative Workflow pattern adapts to different protocols:

- **A2A**: Uses capability invocations with role-based routing and workflow context
- **MCP**: Maps to coordinated tool calls with structured inputs/outputs
- **HTTP**: Implements using RESTful endpoints for workflow stages and state management
- **MQTT**: Uses topic hierarchies for workflow stages with shared state
- **gRPC**: Maps to service method calls with workflow context propagation

## Integration with Other Components

- **Topology System**: Naturally maps to hierarchical or hybrid topologies
- **Agent Framework**: Leverages agent capabilities and roles
- **Observability System**: Workflow stages can be monitored and tracked
- **Knowledge Representation**: Shared knowledge can be maintained across the workflow

## Reasoning Agnosticism

This pattern maintains OpenMAS's reasoning agnosticism by:

1. **Role Abstraction** - Agents can fulfill roles regardless of reasoning approach
2. **Standard Interfaces** - Workflow stages have consistent interfaces
3. **Implementation Independence** - Pattern works with any combination of agent implementations

## Related Patterns

- **Pipeline Pattern** - More rigid than Collaborative Workflow, focused on sequential processing
- **Delegation Pattern** - Used within workflow stages for specific task delegation
- **Event-Based Pattern** - Can be used for stage transitions and notifications

## Configuration

```yaml
communication_patterns:
  collaborative_workflow:
    version: "1.0"
    options:
      max_concurrent_stages: 3
      stage_timeout: 600
      workflow_timeout: 3600
      state_persistence: true
```
