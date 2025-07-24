# Configuration Testing Strategy

This document outlines the strategy for testing configuration handling in OpenMAS modules, ensuring that configuration values are correctly passed from their source to their point of use.

## Goals

Configuration testing aims to:

- Verify that configuration values are correctly loaded from all sources (YAML files, environment variables, CLI arguments)
- Ensure proper precedence when configuration comes from multiple sources
- Detect when changes to configuration handling logic might break existing configurations
- Provide confidence that user-specified configuration values are honored throughout the system

## Configuration Testing Process

### 1. Configuration Pathway Mapping

**Goal**: Identify all configuration entry points and their flow through the system.

**Process**:
1. Document all configuration sources (YAML files, ENV vars, CLI args) for the module
2. Trace each configuration value from source to final usage point
3. Create a "configuration pathway diagram" showing these flows
4. Identify critical configuration values that need the highest test coverage

**Example**: For the prompt module, document how `prompts_dir` flows from project configuration to the `PromptManager` class.

### 2. Value Assertion Testing

**Goal**: Verify configuration values are correctly passed through the entire system.

**Process**:
1. For each critical configuration path:
   - Define a "source to sink" test that verifies a value set at the source appears correctly at the usage point
   - Start with simple, static values (e.g., setting `prompts_dir="/custom/path"`)
   - Progress to boundary values and special cases

**Example**: Test that a custom prompt directory set in configuration is actually used when loading prompts.

### 3. Precedence Validation Testing

**Goal**: Verify correct precedence order when configuration comes from multiple sources.

**Process**:
1. Create test fixtures that set up configurations at multiple levels
2. Design tests that set conflicting values at different precedence levels
3. Verify the highest precedence value always wins
4. Document all precedence rules in the test suite for future reference

**Example**: Test that environment variables override YAML configurations, and CLI arguments override environment variables.

### 4. Configuration Change Detection

**Goal**: Detect when changes to configuration handling logic might break existing configs.

**Process**:
1. Create a set of "golden path" configuration files representing real-world usage
2. Develop tests that load these configurations and verify key properties
3. Automate these tests to run whenever configuration-related code changes
4. Flag when a code change causes a previously working configuration to fail

**Example**: Create a test configuration file that represents a typical production setup, and verify it loads correctly.

### 5. Module-Specific Configuration Isolation

**Goal**: Test the module's configuration in isolation from other modules.

**Process**:
1. Create test fixtures that mock dependencies outside the module
2. Design tests that verify only module-specific configurations
3. Test that module configuration doesn't interfere with other modules
4. Test that other module configurations don't affect the module's functionality

**Example**: For the prompt module, isolate testing of the `PromptManager` configuration from agent configurations.

### 6. Integration Point Testing

**Goal**: Test the specific integration points between the module and configuration system.

**Process**:
1. Identify all places where the module calls configuration code
2. Create targeted tests for each integration point
3. Verify error handling at each integration point
4. Test configuration reload/refresh scenarios

**Example**: Test how `PromptManager` integrates with the `ConfigLoader` class.

### 7. Documentation and Knowledge Transfer

**Goal**: Ensure the testing approach is documented and repeatable.

**Process**:
1. Document common configuration testing patterns discovered
2. Create example tests that can be used as references
3. Add configuration testing guidelines to the project documentation

## Implementation Structure

Configuration tests should be organized as follows:

### Unit Tests

Location: `tests/unit/{module}/config/`

Purpose: Test individual configuration mechanisms in isolation, mocking external dependencies

Example: `tests/unit/prompt/config/test_prompt_config_loading.py`

### Integration Tests

Location: `tests/integration/config/{module}/`

Purpose: Test configurations across multiple components

Example: `tests/integration/config/prompt/test_prompt_config_integration.py`

### End-to-End Tests

Location: `tests/integration/core/config/`

Purpose: Test configuration working end-to-end with real files and environment variables

Example: `tests/integration/core/config/test_end_to_end_config.py`

## Test Fixtures

The following fixtures are recommended for configuration testing:

- `temp_config_file`: Creates a temporary configuration file with specified content
- `temp_env_vars`: Sets temporary environment variables for a test
- `config_loader`: Provides an isolated configuration loader instance
- `golden_config`: Loads a predefined "golden path" configuration

## Priority Implementation Order

For new modules, implement these steps in the following order:

1. Configuration Pathway Mapping (to understand the system)
2. Value Assertion Testing (to catch the most critical issues)
3. Precedence Validation Testing (to ensure hierarchy works)
4. Module-Specific Configuration Isolation (to make tests maintainable)

Later phases can include Configuration Change Detection, Integration Point Testing, and Documentation improvements.
