# Configuration Validation Standard

## Validation Definition
- **Name**: Configuration Validation
- **Purpose**: Standardized approach to configuration validation and error reporting
- **Integration**: Consistent validation across all components

## Validation Schema
```yaml
# Standardized validation configuration schema
type: object
properties:
  # Validation configuration
  validation:
    type: object
    description: "Configuration validation settings"
    properties:
      mode:
        type: string
        description: "Validation mode"
        enum: ["strict", "warning", "permissive"]
        default: "strict"
      schema:
        type: object
        description: "Schema configuration"
        properties:
          path:
            type: string
            description: "Path to schema definitions"
            default: "./schemas"
          format:
            type: string
            description: "Schema format"
            enum: ["json-schema", "pydantic"]
            default: "json-schema"
      on_error:
        type: object
        description: "Error handling configuration"
        properties:
          action:
            type: string
            description: "Action to take on validation error"
            enum: ["fail", "warn", "ignore"]
            default: "fail"
          report_format:
            type: string
            description: "Error report format"
            enum: ["basic", "detailed"]
            default: "detailed"
      runtime_validation:
        type: object
        description: "Runtime validation configuration"
        properties:
          enabled:
            type: boolean
            description: "Whether runtime validation is enabled"
            default: true
          check_references:
            type: boolean
            description: "Whether to check references in configuration"
            default: true
          validate_environment_variables:
            type: boolean
            description: "Whether to validate environment variables"
            default: true
    required:
      - mode
```

## Environment-Specific Validation Configuration
```yaml
# Environment-specific validation configuration
type: object
properties:
  environments:
    type: object
    description: "Environment-specific configurations"
    additionalProperties:
      type: object
      properties:
        validation:
          type: object
          description: "Validation configuration for this environment"
          properties:
            mode:
              type: string
              description: "Validation mode"
              enum: ["strict", "warning", "permissive"]
```

## Validation Modes
| Mode | Description | Use Case |
|------|-------------|----------|
| strict | Fail on any validation error | Production environments |
| warning | Log warnings but continue | Development environments |
| permissive | Ignore validation errors | Testing with partial configs |

## Validation Process
1. **Schema Loading**: [How schemas are loaded]
2. **Pre-validation Checks**: [Pre-validation checks performed]
3. **Schema Validation**: [How schema validation is performed]
4. **Reference Validation**: [How references are validated]
5. **Environment Variable Validation**: [How environment variables are validated]
6. **Post-validation Checks**: [Post-validation checks performed]

## Error Reporting
- **Error Format**: [Standard error format]
- **Error Location**: [How error locations are reported]
- **Error Messages**: [Standard error messages]
- **Suggestions**: [How suggestions are provided]

### Standard Error Format
```json
{
  "error": "Configuration validation failed",
  "validation_errors": [
    {
      "location": "agents.example_agent.communicator.options.port",
      "message": "Port must be between 1024 and 65535",
      "value": 80,
      "constraint": "minimum=1024"
    },
    {
      "location": "agents.missing_agent",
      "message": "Referenced agent 'missing_agent' not found in configuration"
    }
  ],
  "suggestions": [
    "Use a port number above 1024 for non-root users",
    "Check agent references in the topology section"
  ]
}
```

## Validation Implementation
- **Schema Registration**: [How schemas are registered]
- **Validation Functions**: [Standard validation functions]
- **Custom Validators**: [How to implement custom validators]
- **Validation Hooks**: [Validation hooks for components]

## Testing
- **Unit Test Requirements**: [Validation-specific test requirements]
- **Integration Test Requirements**: [Validation integration test requirements]
- **Validation Test Cases**: [Standard validation test cases]

## Usage Examples
```python
# Example validation implementation
from openmas.config import ConfigValidator

def validate_configuration(config, environment="development"):
    # Create validator with configuration
    validator = ConfigValidator(
        config=config,
        environment=environment
    )
    
    # Run validation
    result = validator.validate()
    
    if not result.is_valid:
        if result.action == "fail":
            raise ValidationError(result.format_errors())
        elif result.action == "warn":
            for warning in result.format_warnings():
                logger.warning(warning)
    
    return result.is_valid
``` 