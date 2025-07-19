# Prompt Template System

## Overview

This directory contains documentation about the prompt template system in OpenMAS, which provides a flexible and powerful way to define, compose, and render prompt templates for use with language models.

## Template System Features

The prompt template system provides these core features:

1. **Template Definition**
   - Declarative template specification
   - Variable placeholders
   - Conditional sections
   - Template inheritance
   - Component composition

2. **Variable Substitution**
   - Type-safe variable substitution
   - Default values
   - Runtime value provision
   - Nested variable structures
   - Expression evaluation

3. **Template Inheritance**
   - Base templates and extensions
   - Override mechanisms
   - Partial overrides
   - Multiple inheritance
   - Mixin support

4. **Control Flow**
   - Conditional blocks
   - Iteration structures
   - Content inclusion/exclusion
   - Content prioritization
   - Fallback mechanisms

## Template Syntax

The template system supports these syntax elements:

### Variable Placeholders

```
{{variable_name}}
{{variable_name | default: "default value"}}
{{variable_name | filter: "parameter"}}
```

### Conditional Blocks

```
{% if condition %}
  Content when condition is true
{% else %}
  Content when condition is false
{% endif %}
```

### Loops

```
{% for item in items %}
  {{item.name}}: {{item.value}}
{% endfor %}
```

### Template Inclusion

```
{% include "template_name" %}
{% include "template_name" with {variable: "value"} %}
```

### Prioritization Blocks

```
{% prioritized level="high" %}
  High-priority content that should be preserved when context is limited
{% endprioritized %}
```

## Template Configuration

Templates are configured through the unified configuration schema:

```yaml
prompts:
  example_template:
    description: "Example template with variables"
    version: "1.0.0"
    template: |
      System: {{system_instruction}}
      
      {% if context %}
      Context:
      {{context}}
      {% endif %}
      
      User: {{user_input}}
      
      Assistant:
    variables:
      system_instruction: "You are a helpful assistant."
      context: null
      user_input: ""
    extends: "base_template"
    format: "text"
    models: ["gpt-4", "claude-2"]
```

## Template Inheritance Example

```yaml
# Base template
prompts:
  base_template:
    description: "Base conversation template"
    version: "1.0.0"
    template: |
      System: {{system_instruction}}
      
      {% if conversation_history %}
      Previous conversation:
      {{conversation_history}}
      {% endif %}
      
      User: {{user_input}}
      
      Assistant:
    variables:
      system_instruction: "You are a helpful assistant."
      conversation_history: ""
      user_input: ""

# Extended template
prompts:
  coding_template:
    extends: "base_template"
    description: "Coding-specialized template"
    version: "1.0.0"
    variables:
      system_instruction: "You are a helpful coding assistant specialized in {{language}}."
      language: "Python"
```

## Template Usage

Templates are used through the prompt management API:

```python
# Get a template
template = await prompt_manager.get_template("example_template")

# Render a template
rendered = await template.render({
    "user_input": "Hello, how are you?",
    "context": "The conversation is about greetings."
})

# Complete with a template
response = await prompt_manager.render_and_complete(
    "example_template",
    variables={
        "user_input": "Hello, how are you?",
        "context": "The conversation is about greetings."
    },
    model="gpt-4"
)
```

## References

- [Prompt Management Architecture](/refactoring_work/00b_overview/11_prompt_management/architecture.md)
- [Context Management](/refactoring_work/00b_overview/11_prompt_management/context/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
