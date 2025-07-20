# Extension Development Guide

## Overview

This guide provides comprehensive instructions for developing extensions for OpenMAS. Extensions allow developers to customize and extend the framework's functionality while maintaining its core architectural principles of reasoning agnosticism and protocol independence.

## Before You Begin

Before developing an extension, you should:

1. **Understand the Extension Type**: Review the specific documentation for the type of extension you want to develop. Each extension type has its own interface requirements and integration patterns:

   - [Agent Extensions](../extension_types/agent_extensions.md) - Enhance agent capabilities and behaviors
   - [Communicator Extensions](../extension_types/communicator_extensions.md) - Add support for new communication protocols
   - [Asset Extensions](../extension_types/assets.md) - Handle various types of assets and resources
   - [Prompt Extensions](../extension_types/prompts.md) - Manage and customize prompts
   - [LLM Extensions](../extension_types/llm_extensions.md) - Integrate with language models
   - [Reasoning Extensions](../extension_types/reasoning_extensions.md) - Implement custom reasoning approaches
   - [Protocol Adapter Extensions](../extension_types/protocol_adapters.md) - Enable communication between protocols
   - [Tool Extensions](../extension_types/tool_extensions.md) - Add new tool capabilities to agents

2. **Review the Architecture**: Understand how extensions fit into the overall OpenMAS architecture, particularly the body-brain separation and multi-protocol support strategies.

3. **Set Up Development Environment**: Ensure you have the necessary development tools and dependencies installed.

## Development Process

### 1. Set Up Project Structure

Extensions can be developed in three ways:

1. **Standalone Package**: Create a separate Python package that can be installed with pip
2. **Extension Directory**: Create an extension in a project's `extensions/` directory
3. **Built-in Extension**: Add an extension directly to a fork of the OpenMAS codebase

For most developers, the standalone package or extension directory approach is recommended.

#### Standalone Package Structure

```
my-openmas-extension/
├── pyproject.toml
├── README.md
├── src/
│   └── myextension/
│       ├── __init__.py
│       └── my_extension.py
└── tests/
    └── test_my_extension.py
```

#### Extension Directory Structure

```
my-openmas-project/
├── extensions/
│   └── my_extension/
│       ├── __init__.py
│       └── my_extension.py
└── config.yaml
```

### 2. Implement the Extension

Each extension type has specific base classes and methods that must be implemented. Refer to the type-specific documentation for details. Here's a general template:

```python
from openmas.extensions import BaseExtension  # Or the specific extension base class

class MyExtension(BaseExtension):
    """My custom extension."""

    extension_type = "my_extension_type"  # e.g., "agent", "communicator", etc.
    extension_name = "my_extension"

    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        # Extract configuration options
        self.my_option = config.get("options", {}).get("my_option", "default_value")

    def validate_config(self):
        """Validate the extension configuration."""
        if "required_option" not in self.config.get("options", {}):
            raise ValueError("Missing required option: required_option")

    async def initialize(self):
        """Initialize the extension."""
        # Perform any setup needed
        self.initialized = True

    # Implement extension-specific methods as required by the extension type
    # See the type-specific documentation for required methods
```

### 3. Register the Extension

Extensions must be registered with the extension registry to be discovered and used. This can be done in several ways:

#### Automatic Registration (Recommended)

Create an entry point in your package's `pyproject.toml`:

```toml
[project.entry-points."openmas.extensions"]
my_extension = "myextension.my_extension:MyExtension"
```

#### Manual Registration

For extensions in a project's `extensions/` directory, register them in code:

```python
from openmas.extensions import extension_registry
from extensions.my_extension.my_extension import MyExtension

extension_registry.register_extension(
    extension_class=MyExtension,
    extension_type="my_extension_type",
    extension_name="my_extension"
)
```

### 4. Configure the Extension

Extensions are configured through the unified configuration schema:

```yaml
extensions:
  my_extension:
    type: "my_extension_type"
    name: "my_extension"
    enabled: true
    options:
      # Extension-specific options
      my_option: "value"
      required_option: "value"
```

### 5. Test the Extension

Comprehensive testing is essential for extensions. See the [Extension Testing Guide](./testing_extensions.md) for detailed instructions.

## Best Practices

### 1. Follow the Single Responsibility Principle

Each extension should have a clear, focused purpose. If you find your extension doing too many things, consider splitting it into multiple extensions.

### 2. Maintain Reasoning Agnosticism

Extensions should not make assumptions about the reasoning approach being used. They should work with any reasoning engine unless specifically designed for one.

### 3. Support Protocol Independence

Unless your extension is specifically for a particular protocol, design it to work with any communication protocol.

### 4. Provide Clear Error Messages

When validation fails or errors occur, provide clear, actionable error messages to help users diagnose and fix issues.

### 5. Document Your Extension

Document your extension thoroughly, including:

- Purpose and capabilities
- Configuration options
- Requirements and dependencies
- Example usage
- Limitations or constraints

### 6. Handle Resources Properly

If your extension uses external resources (files, connections, etc.), ensure they are properly acquired, used, and released.

### 7. Follow OpenMAS Coding Style

Adhere to the OpenMAS coding style and conventions to ensure consistency with the rest of the codebase.

## Common Extension Patterns

### 1. Feature Extension

Adds a specific feature to a component:

```python
class LoggingExtension(AgentExtension):
    """Adds enhanced logging to agents."""

    def enhance_agent(self, agent):
        """Add logging capabilities to agent."""
        agent.logger = self._create_logger(agent.agent_id)
```

### 2. Integration Extension

Integrates with external systems or services:

```python
class DatabaseExtension(AssetExtension):
    """Provides asset access from a database."""

    async def provide_asset(self, asset_id, context=None):
        """Retrieve an asset from the database."""
        return await self.db_connection.fetch_asset(asset_id)
```

### 3. Protocol Extension

Adds support for a new protocol:

```python
class GRPCCommunicatorExtension(CommunicatorExtension):
    """Adds gRPC communication support."""

    def create_communicator(self, agent_config):
        """Create a gRPC communicator instance."""
        return GRPCCommunicator(agent_config)
```

### 4. Transformer Extension

Transforms data between formats:

```python
class PDFTextExtractorExtension(AssetProcessorExtension):
    """Extracts text from PDF assets."""

    async def process_asset(self, asset, context=None):
        """Extract text from a PDF asset."""
        return self._extract_text_from_pdf(asset)
```

## Advanced Topics

### Extension Dependencies

Extensions can depend on other extensions:

```python
class AdvancedExtension(BaseExtension):
    """Extension that depends on another extension."""

    def __init__(self, config):
        super().__init__(config)
        self.dependency_name = config.get("options", {}).get("dependency", "some_extension")

    async def initialize(self):
        """Initialize with dependency."""
        # Get the dependency from the registry
        self.dependency = self.extension_registry.get_extension(
            "some_extension_type",
            self.dependency_name
        )

        if not self.dependency:
            raise ValueError(f"Missing dependency: {self.dependency_name}")

        self.initialized = True
```

### Extension Configuration Validation

Provide comprehensive validation for your extension's configuration:

```python
from pydantic import BaseModel, Field

class MyExtensionConfig(BaseModel):
    """Configuration schema for MyExtension."""

    api_key: str = Field(..., description="API key for external service")
    timeout_ms: int = Field(5000, description="Timeout in milliseconds")
    retry_count: int = Field(3, ge=1, le=10, description="Number of retries")

class MyExtension(BaseExtension):
    """Extension with validated configuration."""

    def validate_config(self):
        """Validate using Pydantic model."""
        options = self.config.get("options", {})
        try:
            self.validated_config = MyExtensionConfig(**options)
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")
```

### Asynchronous Extensions

Most extension methods should be asynchronous to support non-blocking operation:

```python
class AsyncExtension(BaseExtension):
    """Extension with async methods."""

    async def initialize(self):
        """Initialize asynchronously."""
        await self._async_setup()
        self.initialized = True

    async def _async_setup(self):
        """Perform async setup operations."""
        # Async operations here
        pass
```

## Troubleshooting

### Common Issues

1. **Extension Not Found**: Ensure the extension is properly registered and enabled in the configuration.
2. **Configuration Errors**: Verify your configuration against the extension's requirements.
3. **Import Errors**: Check for missing dependencies or incorrect import paths.
4. **Runtime Errors**: Enable debug logging to get more detailed error information.

### Debugging

Enable debug logging to see detailed information about extension discovery and loading:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

- See the [Extension Tutorial](./tutorial_custom_extension.md) for a step-by-step guide to creating a custom extension
- Review the [Extension Testing Guide](./testing_extensions.md) for testing best practices
- Explore the OpenMAS extension ecosystem to see examples of different extension types

## Related Documentation

- [Extension System Design](../design/design_extension_system.md)
- [OpenMAS Architecture Overview](../../01_architecture/architecture_overview.md)
- [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md)
