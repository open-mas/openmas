# Integration Testing Prompt

Use this prompt to guide AI assistants in creating comprehensive integration tests that verify components work correctly together, with special focus on testing against real implementations where appropriate.

## Prompt Template

```
I need to create integration tests for [COMPONENT_NAME] within the OpenMAS framework. These tests should verify the component works correctly with its dependencies and integration points.

## Component Description
[BRIEF_DESCRIPTION_OF_COMPONENT]

## Component Implementation
The component has been implemented as follows:

```python
[COMPONENT_IMPLEMENTATION_CODE]
```

## Integration Points
This component interacts with:
1. [INTEGRATION_POINT_1]: [INTERACTION_DESCRIPTION]
2. [INTEGRATION_POINT_2]: [INTERACTION_DESCRIPTION]

## Test Strategy Decision
For each integration point, specify which approach is more appropriate:

1. [INTEGRATION_POINT_1]:
   - [ ] Mock-based testing (for complex dependencies with well-defined interfaces)
   - [ ] Real implementation testing (for external libraries, databases, or critical system components)
   - Justification: [JUSTIFICATION]

2. [INTEGRATION_POINT_2]:
   - [ ] Mock-based testing
   - [ ] Real implementation testing
   - Justification: [JUSTIFICATION]

## Integration Test Requirements
1. Create tests that verify correct interaction between components
2. For external libraries or APIs, test against REAL implementations (not mocks)
3. For internal components, use appropriate mocking based on the test strategy
4. Include both positive scenarios and error handling cases
5. Verify end-to-end functionality across component boundaries
6. Ensure all returned data and state changes are validated

## Real Implementation Testing Approach
For integration points using real implementations:
1. Document the setup requirements (versions, configuration)
2. Use fixtures that create actual instances of the dependencies
3. Set up the test environment to work with real components
4. Add teardown steps to clean up after tests
5. Document any external requirements (e.g., API keys, databases)

## Mock-Based Testing Approach  
For integration points using mocks:
1. Define explicit interfaces that the mocks must implement
2. Create realistic mock behaviors that simulate real components
3. Validate interaction patterns, not just inputs and outputs
4. Use appropriate mocking libraries (e.g., pytest-mock, unittest.mock)

## Expected Output
Please provide:
1. Complete integration test file(s) with imports
2. Setup code for real implementation testing where appropriate
3. Mock implementations where appropriate
4. Clear explanation of the testing strategy for each integration point
5. Documentation of any external requirements for running tests
```

## How to Use

1. Replace placeholders with specific information about the component:
   - `[COMPONENT_NAME]`: The name of the component
   - `[BRIEF_DESCRIPTION_OF_COMPONENT]`: A concise description of the component's purpose
   - `[COMPONENT_IMPLEMENTATION_CODE]`: The implemented component code
   - `[INTEGRATION_POINT_1]`, etc.: Components or libraries this integrates with
   - `[INTERACTION_DESCRIPTION]`: Description of how they interact

2. For each integration point, decide whether to test against real implementations or to use mocks:
   - Use real implementations for external libraries, APIs, and critical system components
   - Use mocks for complex internal components with well-defined interfaces

3. Provide this prompt to the AI assistant.

4. Review the output tests for:
   - Appropriate balance of real implementation vs. mock-based testing
   - Comprehensive test coverage of integration points
   - Proper setup for real implementation testing
   - Clear documentation of external requirements

## Example

```
I need to create integration tests for the DatabaseConnector component within the OpenMAS framework. These tests should verify the component works correctly with its dependencies and integration points.

## Component Description
The DatabaseConnector provides a unified interface for database operations, supporting both SQL and NoSQL databases through appropriate drivers.

## Component Implementation
The component has been implemented as follows:

```python
class DatabaseConnector:
    """Connects to various database types."""
    
    def __init__(self, config: DbConfig, driver_factory: Optional[DriverFactory] = None):
        """Initialize the database connector.
        
        Args:
            config: Database configuration
            driver_factory: Factory for creating database drivers
        """
        self.config = config
        self.driver_factory = driver_factory or DefaultDriverFactory()
        self.driver = None
        
    async def connect(self) -> None:
        """Connect to the database."""
        driver_class = self.driver_factory.get_driver(self.config.db_type)
        self.driver = driver_class(self.config)
        await self.driver.connect()
        
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query against the database."""
        if not self.driver:
            await self.connect()
        return await self.driver.execute_query(query, params)
        
    async def close(self) -> None:
        """Close the database connection."""
        if self.driver:
            await self.driver.close()
            self.driver = None
```

## Integration Points
This component interacts with:
1. SQLite Driver: Implements database operations for SQLite databases
2. MongoDB Driver: Implements database operations for MongoDB databases

## Test Strategy Decision
For each integration point, specify which approach is more appropriate:

1. SQLite Driver:
   - [ ] Mock-based testing
   - [X] Real implementation testing
   - Justification: SQLite can run in-memory and doesn't require external services, making it practical to test against the real implementation

2. MongoDB Driver:
   - [X] Mock-based testing
   - [ ] Real implementation testing
   - Justification: Setting up MongoDB for every test run requires external infrastructure; mocking with well-defined interfaces is more practical for CI/CD
```

## Notes for AI Assistant Use

This prompt ensures that:
1. Real implementation testing is used when appropriate
2. Mock-based testing is used only when justified
3. The testing approach is explicitly decided for each integration point
4. External requirements are properly documented
5. Tests verify both functional and error handling scenarios
