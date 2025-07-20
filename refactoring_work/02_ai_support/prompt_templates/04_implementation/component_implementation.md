# Component Implementation Prompt

Use this prompt to guide AI assistants in implementing components after TDD tests have been created.

## Prompt Template

```
I need to implement the [COMPONENT_NAME] component of OpenMAS based on the tests that have already been created.

## Component Description
[BRIEF_DESCRIPTION_OF_COMPONENT]

## Component Interface
The component must implement this interface:

```python
[INTERFACE_DEFINITION]
```

## Pydantic Schema
The component uses these Pydantic schemas:

```python
[PYDANTIC_SCHEMA_CODE]
```

## Test Code
These tests define the expected behavior:

```python
[TEST_CODE]
```

## Requirements
1. Implement the component to pass all the tests
2. Use dependency injection for all external dependencies
3. Include comprehensive error handling
4. Add clear docstrings with type hints
5. Follow PEP 8 style guidelines
6. Minimize complexity and maximize readability

## External Dependencies
- [DEPENDENCY_1]: [BRIEF_DESCRIPTION]
- [DEPENDENCY_2]: [BRIEF_DESCRIPTION]

## Implementation Constraints
- Use only the libraries imported in the tests
- Avoid introducing new external dependencies
- All public methods must have docstrings
- All class attributes must be documented
- No mutable default arguments

## Expected Output
Please provide:
1. Complete implementation with imports
2. Any helper functions or classes needed
3. Notes on implementation decisions
4. Suggestions for improvements if applicable
```

## How to Use

1. Replace placeholders with specific information about the component:
   - `[COMPONENT_NAME]`: The name of the component
   - `[BRIEF_DESCRIPTION_OF_COMPONENT]`: A concise description of the component's purpose
   - `[INTERFACE_DEFINITION]`: The required interface to implement
   - `[PYDANTIC_SCHEMA_CODE]`: The Pydantic schema the component uses
   - `[TEST_CODE]`: The tests that the implementation must pass
   - `[DEPENDENCY_1]`, etc.: External dependencies with descriptions

2. Provide this prompt to the AI assistant.

3. Review the output implementation for:
   - Compliance with the interface
   - Test coverage
   - Error handling
   - Code quality and readability
   - Proper dependency injection

## Example

```
I need to implement the ConfigLoader component of OpenMAS based on the tests that have already been created.

## Component Description
The ConfigLoader is responsible for loading and validating configuration from YAML files, environment variables, and defaults, then merging them into a complete configuration object.

## Component Interface
The component must implement this interface:

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

## Test Code
These tests define the expected behavior:

```python
@pytest.fixture
def mock_yaml_file(tmp_path):
    """Create a mock YAML file for testing."""
    yaml_content = """
    project_name: "test_project"
    agent_configs:
      agent1:
        module: "test.agent"
        class_name: "TestAgent"
    """
    config_file = tmp_path / "test_config.yml"
    config_file.write_text(yaml_content)
    return str(config_file)

async def test_load_config_from_file(mock_yaml_file):
    """Test loading configuration from a YAML file."""
    loader = ConfigLoader(config_path=mock_yaml_file)
    config = await loader.load_config()

    assert config.project_name == "test_project"
    assert "agent1" in config.agent_configs
    assert config.agent_configs["agent1"].module == "test.agent"
    assert config.agent_configs["agent1"].class_name == "TestAgent"
```

[Rest of prompt follows...]
