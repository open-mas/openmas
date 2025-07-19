# TDD Test Creation Prompt

Use this prompt to guide AI assistants in creating comprehensive test suites following Test-Driven Development principles.

## Prompt Template

```
I need to create tests following TDD principles for the [COMPONENT_NAME] component of OpenMAS. These tests will drive the implementation of this component.

## Component Description
[BRIEF_DESCRIPTION_OF_COMPONENT]

## Component Interface
The component has this expected interface:

```python
[INTERFACE_DEFINITION]
```

## Pydantic Schema
The component uses these Pydantic schemas:

```python
[PYDANTIC_SCHEMA_CODE]
```

## Test Requirements
1. Create comprehensive unit tests covering all functionality
2. Include both happy path and error case tests
3. Use pytest fixtures for test setup and teardown
4. Mock all external dependencies
5. Provide clear test names that describe the behavior being tested
6. Target at least 90% code coverage
7. Include docstrings explaining test purpose

## Testing Patterns
- Use pytest parametrize for testing multiple scenarios
- Use dependency injection to enable mocking
- Include async tests for async components
- Use pytest fixtures for common test setup

## External Dependencies to Mock
- [DEPENDENCY_1]
- [DEPENDENCY_2]

## Expected Output
Please provide:
1. Complete pytest test file(s) with imports
2. All necessary fixtures
3. Mock implementations or factory functions
4. Clear explanation of testing approach
5. Any helper functions needed for testing
```

## How to Use

1. Replace placeholders with specific information about the component:
   - `[COMPONENT_NAME]`: The name of the component
   - `[BRIEF_DESCRIPTION_OF_COMPONENT]`: A concise description of the component's purpose
   - `[INTERFACE_DEFINITION]`: The expected class/function interfaces to test
   - `[PYDANTIC_SCHEMA_CODE]`: The Pydantic schema the component uses
   - `[DEPENDENCY_1]`, etc.: External dependencies that should be mocked

2. Provide this prompt to the AI assistant.

3. Review the output tests for:
   - Complete test coverage
   - Proper mocking of dependencies
   - Clear test names and descriptions
   - Well-structured fixtures

## Example

```
I need to create tests following TDD principles for the ConfigLoader component of OpenMAS. These tests will drive the implementation of this component.

## Component Description
The ConfigLoader is responsible for loading and validating configuration from YAML files, environment variables, and defaults, then merging them into a complete configuration object.

## Component Interface
The component has this expected interface:

```python
class ConfigLoader:
    """Loads and validates configuration for OpenMAS."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the config loader."""
        
    async def load_config(self) -> ProjectConfig:
        """Load and validate configuration."""
        
    def _load_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """Load a YAML file."""
        
    def _merge_configurations(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries."""
        
    def _apply_environment_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
```

## Pydantic Schema
The component uses these Pydantic schemas:

```python
class ProjectConfig(BaseModel):
    """Top-level project configuration."""
    
    project_name: str = Field(..., description="Name of the OpenMAS project")
    version: str = Field("0.1.0", description="Version of the project")
    description: Optional[str] = Field(None, description="Project description")
    agent_configs: Dict[str, AgentConfig] = Field(default_factory=dict, description="Configuration for agents")
    global_config: GlobalConfig = Field(default_factory=GlobalConfig, description="Global configuration settings")
    
    class Config:
        extra = "forbid"
```

[Rest of prompt follows...] 