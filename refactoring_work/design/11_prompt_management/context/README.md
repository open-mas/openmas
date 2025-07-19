# Prompt Context Management

## Overview

This directory contains documentation about the context management system in OpenMAS, which optimizes the usage of language model context windows across conversations, ensuring efficient and effective communication with LLMs.

## Context Management Features

The context management system provides these core capabilities:

1. **Context Window Optimization**
   - Context component prioritization
   - Intelligent context truncation
   - Token budget management
   - Context compression techniques
   - Adaptive context sizing

2. **Conversation History Management**
   - Selective history inclusion
   - Conversation summarization
   - Key information retention
   - Memory management
   - Context refreshing

3. **Token Management**
   - Accurate token counting for different models
   - Token budget allocation
   - Token usage optimization
   - Token limit enforcement
   - Token usage analytics

4. **Context Composition**
   - Component-based context assembly
   - Dynamic context adjustment
   - Context sharing across agents
   - Cross-conversation context
   - Multi-session context management

## Context Components

A typical LLM context window includes these components:

### System Instructions

Core instructions that define the LLM's role and capabilities:

```
System: You are a helpful AI assistant specialized in coding tasks.
You provide concise, accurate responses and can write code in multiple
programming languages.
```

### Conversation History

Previous exchanges in the conversation:

```
User: How do I create a Python function?
Assistant: You can create a Python function using the `def` keyword. Here's a simple example:

```python
def greet(name):
    return f"Hello, {name}!"
```

To call this function, you would use: `greet("World")`
```

### Current Input

The user's current query or input:

```
User: How can I add optional parameters to the function?
```

### Function Definitions

Definitions of functions the LLM can call:

```
Available tools:
- search_web(query: string): Searches the web for information
- get_weather(location: string, unit: string = "celsius"): Gets weather for a location
```

### External Knowledge

Relevant knowledge or data:

```
Context:
Python functions support optional parameters by assigning default values in the parameter list.
Parameters with default values must come after parameters without default values.
```

### Response Format

Instructions on how to format the response:

```
Format your response as follows:
1. Explanation
2. Code example
3. Common pitfalls
```

## Context Management Strategies

The system implements several strategies for context management:

### Fixed Allocation Strategy

Allocates a fixed token budget to each context component:

```yaml
context:
  strategy: "fixed_allocation"
  components:
    system: 500
    history: 2000
    current_input: 500
    functions: 500
    knowledge: 500
```

### Priority-Based Strategy

Allocates tokens based on component priority when context is limited:

```yaml
context:
  strategy: "priority_based"
  components:
    - name: "system"
      priority: 1  # Highest priority
      min_tokens: 200
    - name: "current_input"
      priority: 2
      min_tokens: 100
    - name: "functions"
      priority: 3
      min_tokens: 0
    - name: "history"
      priority: 4
      min_tokens: 0
    - name: "knowledge"
      priority: 5
      min_tokens: 0
```

### Adaptive Strategy

Dynamically adjusts token allocation based on conversation needs:

```yaml
context:
  strategy: "adaptive"
  max_tokens: 4000
  adaptation_rules:
    - condition: "current_input.tokens > 1000"
      action: "reduce_history(50%)"
    - condition: "contains(current_input, 'code')"
      action: "increase_knowledge(+500)"
```

### Summarization Strategy

Uses summarization to compress context components:

```yaml
context:
  strategy: "summarization"
  components:
    history:
      max_exchanges: 10
      summarize_beyond: 5
      summary_prompt: "summarize_conversation"
```

## Context Management API

The context manager is used through this API:

```python
# Create a new context
context = await context_manager.create_context(
    system="You are a helpful assistant.",
    max_tokens=4000
)

# Add conversation history
await context.add_history(
    [{"role": "user", "content": "Hello"},
     {"role": "assistant", "content": "Hi there"}]
)

# Add current input
await context.set_current_input("How can you help me?")

# Add knowledge
await context.add_knowledge("This user is interested in Python programming.")

# Generate the complete prompt
prompt = await context.generate_prompt(model="gpt-4")
```

## Token Counting

The system provides accurate token counting for different models:

```python
# Count tokens for a specific model
token_count = await token_counter.count_tokens(
    text="This is some text to count tokens for.",
    model="gpt-4"
)

# Check if content fits in budget
fits_budget = await token_counter.fits_in_budget(
    text="Content to check",
    budget=1000,
    model="gpt-4"
)
```

## References

- [Prompt Management Architecture](/refactoring_work/00b_overview/11_prompt_management/architecture.md)
- [Template System](/refactoring_work/00b_overview/11_prompt_management/templates/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
