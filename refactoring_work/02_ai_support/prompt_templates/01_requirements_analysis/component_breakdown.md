# Component Requirements Analysis Prompt

Use this prompt template to break down a large component into manageable sub-components with clear requirements.

## Prompt Template

```
I need to refactor the [COMPONENT_NAME] component of OpenMAS. This component is responsible for [BRIEF_DESCRIPTION]. 

The design documentation is located at:
[DESIGN_DOC_LINK]

## Task

1. Analyze the design documentation and break down this component into logical sub-components.
2. For each sub-component:
   - Provide a name and clear description of its responsibility
   - List its core functions/methods
   - Identify dependencies on other components
   - Note any external libraries it will use
   - Describe its integration points with other OpenMAS components

3. Propose an implementation sequence that:
   - Starts with the components with fewest dependencies
   - Follows a logical progression
   - Allows for incremental testing

## Constraints

- Focus only on the functionality described in the design doc
- Don't introduce unnecessary abstractions
- Identify clear boundaries between sub-components
- Suggest appropriate interfaces for testability
- Consider dependency injection patterns for external dependencies

## Expected Output

For each sub-component:

```markdown
### [Sub-component Name]

**Description:** [Clear description of responsibility]

**Core Functions:**
- `function_name`: [description]
- `function_name`: [description]

**Dependencies:**
- [Internal dependency]: [purpose]
- [External library]: [purpose]

**Integration Points:**
- Interfaces with [component] through [mechanism]

**Implementation Priority:** [number]

**Estimated Complexity:** [Low/Medium/High]
```

Please also include a diagram of the relationship between these sub-components.
```

## How to Use

1. Replace `[COMPONENT_NAME]`, `[BRIEF_DESCRIPTION]`, and `[DESIGN_DOC_LINK]` with specific information about the component.
2. Provide this prompt to the AI assistant.
3. Review the output and refine the sub-component breakdown if needed.
4. Use this breakdown to create specific implementation tasks.

## Example

```
I need to refactor the Configuration System component of OpenMAS. This component is responsible for loading, validating, and providing configuration to all other components.

The design documentation is located at:
/refactoring_work/01_configuration/design/index.md

[Rest of prompt follows...]
``` 