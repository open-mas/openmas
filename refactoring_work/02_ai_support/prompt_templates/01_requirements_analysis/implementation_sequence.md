# Implementation Sequence Planning Prompt

Use this prompt template to create a detailed implementation sequence for refactoring components, ensuring a logical progression that minimizes integration issues.

## Prompt Template

```
I need to plan the implementation sequence for refactoring the [COMPONENT_NAME] component of OpenMAS. This component is responsible for [BRIEF_DESCRIPTION].

The component has been broken down into these sub-components:
[LIST_OF_SUBCOMPONENTS]

## Task

1. Analyze the dependencies between these sub-components.
2. Create an implementation sequence that:
   - Starts with the most foundational components (least dependencies on other parts)
   - Logically progresses to more complex components
   - Allows for incremental testing
   - Considers existing code that needs to be migrated

3. For each implementation step:
   - Specify which sub-component(s) to implement
   - List the specific interfaces and classes to create
   - Note any dependencies that must be mocked during testing
   - Provide estimations of complexity and testing requirements

## Dependencies to Consider

- Dependencies between sub-components
- External library dependencies
- Integration with other OpenMAS components
- Existing implementations that need to be migrated or refactored

## Expected Output

A numbered implementation sequence with details for each step:

```markdown
## Implementation Sequence

### Step 1: [SUBCOMPONENT_NAME]

**Description:** [Brief description of what will be implemented]

**Interfaces to Define:**
- `interface_name`: [purpose]
- `interface_name`: [purpose]

**Classes to Implement:**
- `class_name`: [purpose]
- `class_name`: [purpose]

**Dependencies to Mock:**
- `dependency`: [purpose]
- `dependency`: [purpose]

**Migration Considerations:**
- [Any existing code that needs to be migrated/refactored]

**Testing Focus:**
- [Key aspects to test]

**Estimated Complexity:** [Low/Medium/High]

### Step 2: [SUBCOMPONENT_NAME]

[...details as above...]
```

Please also include a diagram showing the dependency relationships between steps.
```

## How to Use

1. Replace placeholders with specific information about your refactoring:
   - `[COMPONENT_NAME]`: The name of the component
   - `[BRIEF_DESCRIPTION]`: A concise description of the component's purpose
   - `[LIST_OF_SUBCOMPONENTS]`: A list of the sub-components identified in previous analysis

2. Provide this prompt to the AI assistant.

3. Review the proposed implementation sequence for:
   - Logical progression
   - Appropriate dependency handling
   - Completeness
   - Realistic complexity estimations

4. Use the output as a roadmap for creating specific implementation tasks.

## Example

```
I need to plan the implementation sequence for refactoring the ConfigSystem component of OpenMAS. This component is responsible for loading, validating, and providing configuration to all other components.

The component has been broken down into these sub-components:
1. ConfigLoader - Responsible for loading configuration from YAML files
2. ConfigValidator - Validates configuration against schemas
3. ConfigProvider - Provides configuration to other components
4. EnvironmentIntegration - Handles environment variable integration
5. ConfigMerger - Merges multiple configuration sources

## Task

1. Analyze the dependencies between these sub-components.
2. Create an implementation sequence that:
   - Starts with the most foundational components (least dependencies on other parts)
   - Logically progresses to more complex components
   - Allows for incremental testing
   - Considers existing code that needs to be migrated

[Rest of prompt follows...]
``` 