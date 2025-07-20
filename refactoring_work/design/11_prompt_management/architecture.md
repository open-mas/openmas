# Prompt Management Architecture

## Overview

This document outlines the architecture of the OpenMAS Prompt Management system, which provides centralized management, versioning, and delivery of prompts to language models within agents and other components.

## Architectural Principles

The Prompt Management system is built on these core principles:

1. **Centralized Management**: Single source of truth for prompt templates
2. **Separation of Concerns**: Clear separation between prompt definition and usage
3. **Versioning by Default**: All prompts are explicitly versioned
4. **Dynamic Composition**: Prompts can be composed from reusable components
5. **Context Optimization**: Efficient use of context windows through optimization
6. **Model Agnosticism**: Support for multiple LLM providers and models

## System Components

The Prompt Management system consists of these primary components:

### 1. Template Registry

Central registry for all prompt templates:

- **Template Definition**: Declarative specification of templates
- **Template Discovery**: Dynamic discovery of available templates
- **Inheritance Support**: Template inheritance and composition
- **Version Management**: Management of template versions

### 2. Template Engine

Engine for rendering templates:

- **Variable Substitution**: Replacement of variables with values
- **Conditional Rendering**: Conditional sections based on runtime data
- **Template Functions**: Built-in functions for common operations
- **Composition Support**: Inclusion of subtemplates

### 3. Context Manager

Management of context window usage:

- **Token Counting**: Accurate token counting for different models
- **Context Optimization**: Strategies for maximizing context usage
- **Truncation Logic**: Intelligent truncation when context exceeds limits
- **Priority Management**: Maintaining high-priority content in limited context

### 4. Model Adapter

Adaptation of prompts for different models:

- **Format Conversion**: Converting prompts between different model formats
- **Model-Specific Optimization**: Optimizing prompts for specific models
- **Parameter Management**: Setting appropriate model parameters
- **Response Parsing**: Standardized parsing of model responses

### 5. Prompt Store

Persistent storage for prompts:

- **Prompt Persistence**: Storage of prompt templates
- **Version History**: Historical versions of prompts
- **Metadata Management**: Storage and retrieval of prompt metadata
- **Access Control**: Permission-based access to prompts

## Template Structure

Prompt templates follow this structure:

```yaml
prompts:
  example_prompt:
    description: "Description of the prompt's purpose"
    version: "1.0.0"
    template: "This is a prompt template with {{variable}}."
    variables:
      variable: "default value"
    extends: "base_prompt"
    format: "text"
    models: ["gpt-4", "claude-2"]
    max_tokens: 1000
    stop_sequences: ["\n\n"]
    sampling:
      temperature: 0.7
      top_p: 0.9
    metadata:
      author: "OpenMAS Team"
      tags: ["example", "documentation"]
```

## Context Management

The context manager optimizes context usage through:

### Context Window Components

- **System Instructions**: Core instruction for the LLM
- **Conversation History**: Previous exchanges in the conversation
- **Current Input**: The user's current query or input
- **Function Definitions**: Definitions of available functions
- **External Knowledge**: Relevant knowledge or data
- **Metadata**: Additional context information

### Context Strategies

- **Fixed Allocation**: Fixed token allocation for different components
- **Dynamic Allocation**: Adjusting allocations based on needs
- **Summarization**: Condensing information to save tokens
- **Prioritization**: Keeping high-value information in limited context
- **Progressive Loading**: Adding context only when needed

## Template Inheritance

Templates can inherit from and extend other templates:

```yaml
# Base template
prompts:
  base_template:
    description: "Base template with common structure"
    version: "1.0.0"
    template: |
      System: {{system_instruction}}

      User: {{user_input}}

      Assistant:

# Extended template
prompts:
  specialized_template:
    extends: "base_template"
    description: "Specialized template for specific task"
    version: "1.0.0"
    variables:
      system_instruction: "You are a helpful assistant specialized in coding."
```

## Integration with Other Components

The Prompt Management system integrates with these OpenMAS components:

- **Agent Framework**: Provides prompts to agents
- **Protocol Layer**: Formats prompts for different protocol requirements
- **Asset Management**: Manages prompt templates as assets
- **Configuration System**: Configures the prompt system
- **Observability System**: Monitors prompt usage and performance

## Security Considerations

The system implements these security controls:

- **Template Validation**: Validation of templates to prevent injection
- **Access Control**: Permission-based access to prompt templates
- **Sanitization**: Sanitization of user inputs in templates
- **Audit Logging**: Tracking of prompt operations
- **Version Control**: Management of trusted prompt versions

## References

- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Template System](/refactoring_work/00b_overview/11_prompt_management/templates/README.md)
- [Context Management](/refactoring_work/00b_overview/11_prompt_management/context/README.md)
- [Agent Framework Integration](/refactoring_work/00b_overview/04_agents/integration.md)
