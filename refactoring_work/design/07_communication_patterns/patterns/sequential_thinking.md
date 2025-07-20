# Sequential Thinking Pattern

## Overview

The Sequential Thinking pattern enables step-by-step reasoning processes across agents. It's particularly useful for complex problem-solving that requires breaking down reasoning into discrete, observable steps.

## Key Capabilities

The Sequential Thinking pattern provides these core capabilities:

1. **Step-by-Step Reasoning** - Explicit representation of reasoning steps
2. **Intermediate State Tracking** - Preservation of state between reasoning steps
3. **Observation Points** - Ability to observe and log individual reasoning steps
4. **Reasoning Verification** - Validation of reasoning chain correctness
5. **Protocol Agnosticism** - Works across all supported protocols

## Pattern Structure

### Components

- **Initiator** - Agent that initiates the sequential thinking process
- **Reasoner** - Agent (often the same as initiator) that performs the reasoning steps
- **Observer** - Optional component that monitors the reasoning process
- **Step History** - Ordered collection of reasoning steps and their outcomes

### Message Types

- **sequential_thinking_start** - Initiates the process
- **sequential_thinking_step** - Individual reasoning step
- **sequential_thinking_conclusion** - Final outcome of the reasoning process

## Implementation Example

```python
# Using the Sequential Thinking pattern
async def solve_problem(agent, problem_description):
    # Initialize sequential thinking
    thinking_process = await agent.patterns.sequential_thinking.start(
        initial_context={
            "problem": problem_description,
            "approach": "step-by-step reasoning"
        },
        options={
            "max_steps": 10,
            "log_level": "detailed"
        }
    )

    # Add reasoning steps
    step1 = await thinking_process.add_step({
        "step_name": "problem_understanding",
        "reasoning": "First, I need to understand the key components of the problem..."
    })

    step2 = await thinking_process.add_step({
        "step_name": "identify_constraints",
        "reasoning": "The problem has the following constraints...",
        "constraints": ["constraint1", "constraint2"]
    })

    # Continue with more steps...

    # Conclude reasoning
    conclusion = await thinking_process.conclude({
        "final_answer": "The solution is...",
        "confidence": 0.95,
        "reasoning_summary": "By following steps 1-5, I determined that..."
    })

    return conclusion
```

## Protocol Adaptations

The Sequential Thinking pattern adapts to different protocols:

- **A2A**: Uses capability invocation with sequential step message structure
- **MCP**: Maps to chain-of-thought prompting with structured output
- **HTTP**: Implements using a stateful session with step-by-step POST requests
- **MQTT**: Uses hierarchical topics for each step in the thinking process
- **gRPC**: Maps to bidirectional streaming for continuous reasoning steps

## Integration with Other Components

- **Observability System**: Each thinking step can be logged and monitored
- **Prompt Management**: Templates can be used for each reasoning step
- **Topology Integration**: Supports hierarchical delegation of reasoning steps

## Reasoning Agnosticism

This pattern maintains OpenMAS's reasoning agnosticism by:

1. **Step Abstraction** - Steps are protocol-independent and representation-neutral
2. **Interface Consistency** - Same pattern works across different reasoning approaches
3. **Output Format Standardization** - Common format regardless of underlying implementation

## Related Patterns

- **Pipeline Pattern** - Similar to Sequential Thinking but focused on data processing rather than reasoning
- **Request-Response Pattern** - Used within each step of the sequential thinking process
- **Delegation Pattern** - Can be combined with Sequential Thinking for distributed reasoning

## Configuration

```yaml
communication_patterns:
  sequential_thinking:
    version: "1.0"
    options:
      max_steps: 20
      observation_level: "detailed"
      step_timeout: 60
      persist_steps: true
```
