# OpenMAS Refactoring Prompt Templates

This directory contains a collection of prompt templates designed to guide AI assistants through the OpenMAS refactoring process. These templates follow a structured approach to ensure high-quality, testable, and maintainable implementations.

## Prompt Sequence

The prompts are organized into a logical sequence that should be followed for each component:

1. **Requirements Analysis**
   - Break down components into manageable sub-components
   - Identify interfaces and responsibilities
   - Plan implementation sequence

2. **Schema Definition**
   - Define Pydantic models for configuration and data structures
   - Include validation rules and constraints
   - Document fields and relationships

3. **Test Creation**
   - Write comprehensive unit tests following TDD principles
   - Mock external dependencies
   - Cover both happy paths and error cases

4. **Implementation**
   - Implement components to satisfy the tests
   - Follow design patterns and best practices
   - Include proper error handling and logging

5. **Integration**
   - Connect components together
   - Verify correct interaction
   - Create integration tests

## Available Templates

### 00_ai_continuity

- [test_execution_guide.md](00_ai_continuity/test_execution_guide.md) - Step-by-step test execution instructions
- [quick_continuity_test.md](00_ai_continuity/quick_continuity_test.md) - Ready-to-copy prompt for testing continuity
- [session_continuity_test.md](00_ai_continuity/session_continuity_test.md) - Comprehensive AI session handoff testing

### 01_requirements_analysis

- [component_breakdown.md](01_requirements_analysis/component_breakdown.md) - Break down a component into logical sub-components
- [implementation_sequence.md](01_requirements_analysis/implementation_sequence.md) - Plan the sequence of implementation steps

### 02_schema_definition

- [pydantic_schema.md](02_schema_definition/pydantic_schema.md) - Create Pydantic models for data validation

### 03_test_creation

- [tdd_tests.md](03_test_creation/tdd_tests.md) - Create comprehensive tests following TDD principles
- [integration_tests.md](03_test_creation/integration_tests.md) - Create tests that verify real interactions between components
- [adapter_test_strategy.md](03_test_creation/adapter_test_strategy.md) - Develop strategies for testing adapter classes with both mocks and real implementations

### 04_implementation

- [component_implementation.md](04_implementation/component_implementation.md) - Implement components based on tests

### 05_integration

- [component_integration.md](05_integration/component_integration.md) - Integrate components together
- [library_adapter_integration.md](05_integration/library_adapter_integration.md) - Create adapters that properly integrate with external libraries

## How to Use These Templates

### **AI Continuity Testing (Start Here for Fresh Sessions)**

- **Fresh AI Session**: Use `quick_continuity_test.md` to validate handoff protocols
- **Testing AI System**: Use `session_continuity_test.md` for comprehensive validation

### **Development Workflow**

1. **Start with Requirements Analysis**
   - Use the component breakdown template to analyze each major component
   - Use the implementation sequence template to plan the implementation order

2. **For Each Sub-Component:**
   - Create the Pydantic schema (if applicable)
   - Write tests following TDD principles
   - Implement the component to pass the tests
   - Integrate with other components

3. **Important Guidelines:**
   - Always follow the sequence: requirements → schema → tests → implementation → integration
   - Review the output of each step before proceeding to the next
   - Keep components small and focused
   - Ensure thorough test coverage

## Example Prompt Workflow

For refactoring the configuration system:

1. Use `component_breakdown.md` to break down the configuration system into sub-components
2. Use `implementation_sequence.md` to determine the order of implementation
3. For the first sub-component (e.g., ConfigLoader):
   - Use `pydantic_schema.md` to define the configuration schema
   - Use `tdd_tests.md` to create tests for the ConfigLoader
   - Use `component_implementation.md` to implement the ConfigLoader
4. Repeat step 3 for each sub-component
5. Finally, use `component_integration.md` to integrate all sub-components

Following this structured approach ensures consistent, high-quality implementations that adhere to OpenMAS's architectural principles and testing requirements. 