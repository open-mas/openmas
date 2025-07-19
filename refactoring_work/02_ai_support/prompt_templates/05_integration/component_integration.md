# Component Integration Prompt

Use this prompt to guide AI assistants in integrating components after individual implementations are complete.

## Prompt Template

```
I need to integrate the [COMPONENT_NAME] component with other OpenMAS components.

## Component Description
[BRIEF_DESCRIPTION_OF_COMPONENT]

## Component Implementation
The component has been implemented as follows:

```python
[COMPONENT_IMPLEMENTATION_CODE]
```

## Integration Points
This component needs to be integrated with:
1. [COMPONENT_1]: [INTEGRATION_DESCRIPTION]
2. [COMPONENT_2]: [INTEGRATION_DESCRIPTION]

## Integration Requirements
1. Maintain loose coupling between components
2. Use dependency injection for all dependencies
3. Add integration tests to verify correct interaction
4. Ensure error handling across component boundaries
5. Document all integration points clearly

## Expected Changes
You will need to:
1. Modify [FILE_PATH_1] to integrate with the new component
2. Create integration tests in [TEST_FILE_PATH]
3. Update any factory or builder classes to support the new component

## Integration Tests Requirements
The integration tests should verify:
1. Correct interaction between components
2. Proper error handling across boundaries
3. End-to-end functionality involving multiple components

## Expected Output
Please provide:
1. All code changes needed for integration (specify file paths)
2. Integration tests demonstrating correct interaction
3. Documentation updates explaining the integration
4. Notes on any implementation decisions
```

## How to Use

1. Replace placeholders with specific information about the integration:
   - `[COMPONENT_NAME]`: The name of the component to integrate
   - `[BRIEF_DESCRIPTION_OF_COMPONENT]`: A concise description of the component's purpose
   - `[COMPONENT_IMPLEMENTATION_CODE]`: The implemented component code
   - `[COMPONENT_1]`, etc.: Components to integrate with
   - `[INTEGRATION_DESCRIPTION]`: Description of how the integration should work
   - `[FILE_PATH_1]`, etc.: Files that need to be modified
   - `[TEST_FILE_PATH]`: Path for integration tests

2. Provide this prompt to the AI assistant.

3. Review the output integration for:
   - Proper dependency injection
   - Appropriate error handling
   - Clear component boundaries
   - Comprehensive integration tests

## Example

```
I need to integrate the ConfigLoader component with other OpenMAS components.

## Component Description
The ConfigLoader is responsible for loading and validating configuration from YAML files, environment variables, and defaults, then merging them into a complete configuration object.

## Component Implementation
The component has been implemented as follows:

```python
class ConfigLoader:
    """Loads and validates configuration for OpenMAS."""
    
    def __init__(self, config_path: Optional[str] = None, file_reader: Optional[FileReader] = None):
        """Initialize the config loader.
        
        Args:
            config_path: Path to the configuration file
            file_reader: Optional file reader for testing
        """
        self.config_path = config_path
        self.file_reader = file_reader or DefaultFileReader()
        
    async def load_config(self) -> ProjectConfig:
        """Load and validate configuration."""
        if not self.config_path:
            raise ConfigError("No configuration path provided")
            
        yaml_config = self._load_yaml_file(self.config_path)
        env_config = self._apply_environment_variables(yaml_config)
        
        return ProjectConfig(**env_config)
    
    # ... rest of implementation ...
```

## Integration Points
This component needs to be integrated with:
1. ProjectRunner: The ConfigLoader should be used to load configuration before initializing agents
2. AgentFactory: The AgentFactory should use configuration from ConfigLoader to create agents
3. CLI: The CLI should allow specifying a configuration file path

## Integration Requirements
1. Maintain loose coupling between components
2. Use dependency injection for all dependencies
3. Add integration tests to verify correct interaction
4. Ensure error handling across component boundaries
5. Document all integration points clearly

[Rest of prompt follows...] 