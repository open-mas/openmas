# Prompt Management Standardization

## Prompt Definition
- **Name**: [Prompt Name]
- **Purpose**: [Brief description of prompt's purpose]
- **Type**: [Prompt type]
- **Model Compatibility**: [Compatible models]

## Prompt Schema
```yaml
# Standardized prompt configuration schema
type: object
properties:
  # Prompt-specific properties
  type:
    type: string
    description: "The type of prompt"
    enum: ["system", "user", "assistant", "function", "etc"]
  
  # Content configuration
  content:
    type: object
    description: "Prompt content configuration"
    properties:
      template:
        type: string
        description: "Prompt template"
      
      template_format:
        type: string
        description: "Template format"
        enum: ["text", "jinja2", "handlebars", "etc"]
      
      variables:
        type: object
        description: "Template variables"
        # Variable-specific properties
    required:
      - template
  
  # Metadata
  metadata:
    type: object
    description: "Prompt metadata"
    # Metadata-specific properties

required:
  - type
  - content
```

## Prompt Types
| Prompt Type | Description | Usage | Protocol Support |
|-------------|-------------|-------|-----------------|
| System | System instruction | Agent initialization | MCP, A2A |
| User | User message | User input | MCP, A2A |
| Assistant | Assistant message | Agent output | MCP, A2A |
| Function | Function definition | Tool definition | MCP |
| etc. | etc. | etc. | etc. |

## Template Formats
- **Text Format**: [Simple text format]
- **Jinja2 Format**: [Jinja2 template format]
- **Handlebars Format**: [Handlebars template format]
- **Custom Formats**: [How to implement custom formats]

## Variable Types
- **Simple Variables**: [String, number, boolean]
- **Complex Variables**: [Objects, arrays]
- **Function Variables**: [Functions that return values]
- **Context Variables**: [Variables from context]

## Prompt Composition
- **Prompt Chaining**: [How to chain prompts]
- **Prompt Includes**: [How to include sub-prompts]
- **Prompt Inheritance**: [How to inherit from base prompts]

## Protocol Alignment
- **MCP Alignment**: [How prompts align with MCP]
- **A2A Alignment**: [How prompts align with A2A]
- **Protocol-Specific Features**: [Protocol-specific prompt features]

## Prompt Management
- **Prompt Registration**: [How prompts are registered]
- **Prompt Discovery**: [How prompts are discovered]
- **Prompt Versioning**: [How prompts are versioned]

## Testing
- **Unit Test Requirements**: [Prompt-specific test requirements]
- **Integration Test Requirements**: [Prompt integration test requirements]
- **Prompt Validation Tests**: [How to test prompt validation]

## Usage Examples
```python
# Example prompt configuration and usage
``` 