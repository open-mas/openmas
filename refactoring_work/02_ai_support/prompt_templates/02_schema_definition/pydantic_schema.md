# Pydantic Schema Creation Prompt

Use this prompt to guide AI assistants in creating well-defined Pydantic schemas for OpenMAS components.

## Prompt Template

```
I need to create Pydantic schema models for the [COMPONENT_NAME] component of OpenMAS.

## Component Description
[BRIEF_DESCRIPTION_OF_COMPONENT]

## Requirements
The schema should:
1. Define all configuration options for this component
2. Include proper validation using Pydantic validators
3. Provide comprehensive type hints
4. Include descriptive Field(..., description="...") annotations for all fields
5. Support proper composition and inheritance where appropriate
6. Include appropriate default values

## Configuration Examples
The schema should support these configuration patterns:

```yaml
[EXAMPLE_CONFIG_YAML]
```

## Related Components
This schema may need to interact with these related components:
- [RELATED_COMPONENT_1]
- [RELATED_COMPONENT_2]

## Constraints
- Use Pydantic v2 syntax and features
- Prefer composition over inheritance
- Make all field descriptions clear and comprehensive
- Use strict validation where appropriate
- Follow OpenMAS naming conventions

## Expected Output
Please provide:
1. Complete Pydantic model definitions with imports
2. Example instantiations demonstrating usage
3. Explanation of validator logic where complex
4. Notes on any design decisions made
```

## How to Use

1. Replace placeholders with specific information about the component:
   - `[COMPONENT_NAME]`: The name of the component
   - `[BRIEF_DESCRIPTION_OF_COMPONENT]`: A concise description of the component's purpose
   - `[EXAMPLE_CONFIG_YAML]`: Example YAML configuration that the schema should validate
   - `[RELATED_COMPONENT_1]`, etc.: Names of components this one interacts with

2. Provide this prompt to the AI assistant.

3. Review the output schema for:
   - Comprehensive field coverage
   - Appropriate validation logic
   - Clear type hints and descriptions
   - Proper use of Pydantic features

## Example

```
I need to create Pydantic schema models for the Communicator component of OpenMAS.

## Component Description
The Communicator component handles all communication between agents, including message formatting, transport, and routing.

## Requirements
The schema should:
1. Define all configuration options for communicators
2. Include proper validation using Pydantic validators
3. Provide comprehensive type hints
4. Include descriptive Field(..., description="...") annotations for all fields
5. Support proper composition and inheritance where appropriate
6. Include appropriate default values

## Configuration Examples
The schema should support these configuration patterns:

```yaml
communicator:
  type: "http"
  options:
    host: "localhost"
    port: 8080
    timeout: 30
    retries: 3
```

## Related Components
This schema may need to interact with these related components:
- AgentConfig
- MessageSchema
- AuthConfig

[Rest of prompt follows...]
