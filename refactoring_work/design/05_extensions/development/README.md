# Extension Development Resources

## Overview

This directory contains resources for developing custom extensions for OpenMAS. Extensions allow developers to customize and extend the framework's functionality while maintaining its core architectural principles of reasoning agnosticism and protocol independence.

## Key Development Resources

### [Extension Development Guide](./guide.md)

The comprehensive [Extension Development Guide](./guide.md) provides detailed instructions for:
- Setting up your development environment
- Implementing extension interfaces
- Registering and configuring extensions
- Testing and deploying extensions
- Best practices and design patterns

### [Custom Extension Tutorial](./tutorial_custom_extension.md)

The [Custom Extension Tutorial](./tutorial_custom_extension.md) offers a step-by-step walkthrough of building a complete, working extension from scratch.

### [Extension Testing Guide](./testing_extensions.md)

The [Extension Testing Guide](./testing_extensions.md) provides best practices for testing extensions effectively.

## Extension Type-Specific Documentation

Before developing an extension, review the detailed documentation for the specific extension type you're interested in implementing. Each extension type has its own interface requirements and integration patterns:

- [Agent Extensions](../extension_types/agent_extensions.md) - Enhance agent capabilities and behaviors
- [Communicator Extensions](../extension_types/communicator_extensions.md) - Add support for new communication protocols
- [Asset Extensions](../extension_types/assets.md) - Handle various types of assets and resources
- [Prompt Extensions](../extension_types/prompts.md) - Manage and customize prompts
- [LLM Extensions](../extension_types/llm_extensions.md) - Integrate with language models
- [Reasoning Extensions](../extension_types/reasoning_extensions.md) - Implement custom reasoning approaches
- [Protocol Adapter Extensions](../extension_types/protocol_adapters.md) - Enable communication between protocols
- [Tool Extensions](../extension_types/tool_extensions.md) - Add new tool capabilities to agents

### 2. Create Extension Package

Create a Python package for your extension:

```
my_extension/
├── __init__.py
├── extension.py
├── config.py
└── README.md
```

In `__init__.py`, expose your extension class:

```python
from .extension import MyExtension

__all__ = ['MyExtension']
```

### 3. Implement Extension Class

Implement your extension by subclassing the appropriate base class:

```python
from openmas.extensions import BaseExtension
from openmas.extensions.registry import ExtensionRegistry
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MyExtension(BaseExtension):
    """My custom extension."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the extension with configuration."""
        super().__init__(config)
        self.config = config
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the extension and set up resources."""
        if self._initialized:
            return True

        # Get configuration values
        enabled = self.config.get("enabled", True)
        if not enabled:
            logger.info("Extension is disabled")
            return False

        # Initialize resources
        try:
            # Set up your extension resources here
            logger.info("Initializing resources")

            # Register capabilities with the extension registry
            registry = ExtensionRegistry.get_instance()

            registry.register_capability(
                "my_capability",
                self.my_capability_method,
                {
                    "description": "Description of my capability",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param1": {
                                "type": "string",
                                "description": "First parameter"
                            },
                            "param2": {
                                "type": "integer",
                                "description": "Second parameter"
                            }
                        },
                        "required": ["param1"]
                    },
                    "returns": {
                        "type": "object",
                        "properties": {
                            "result": {"type": "string"}
                        }
                    }
                },
                protocol_mapping=self.config.get("protocol_mapping", {}).get("my_capability", {})
            )

            self._initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize extension: {e}")
            return False

    async def my_capability_method(self, param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
        """Implementation of my capability."""
        if not self._initialized:
            raise RuntimeError("Extension not initialized")

        # Implement your capability
        result = f"Processed {param1}"
        if param2 is not None:
            result += f" with value {param2}"

        return {"result": result}

    async def shutdown(self) -> bool:
        """Clean up resources and shut down the extension."""
        logger.info("Shutting down extension")
        # Clean up resources here
        self._initialized = False
        return True
    extension_type = "my_extension_type"
    extension_name = "my_extension"

    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.custom_property = config.get("custom_property", "default")

    async def initialize(self):
        """Initialize the extension."""
        # Initialization logic
        self.initialized = True

    async def my_custom_method(self, *args, **kwargs):
        """Custom method for this extension."""
        # Implementation
        pass
```

### 4. Add Configuration Schema

Define a configuration schema for your extension:

```python
# config.py
EXTENSION_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "custom_property": {
            "type": "string",
            "description": "A custom property for the extension"
        },
        "enabled": {
            "type": "boolean",
            "description": "Whether the extension is enabled"
        }
    },
    "required": ["enabled"]
}
```

### 5. Test Your Extension

Create tests for your extension:

```python
# test_extension.py
import unittest
from my_extension import MyExtension

class TestMyExtension(unittest.TestCase):
    def test_initialization(self):
        config = {"custom_property": "test", "enabled": True}
        extension = MyExtension(config)
        self.assertEqual(extension.custom_property, "test")

    async def test_my_custom_method(self):
        config = {"enabled": True}
        extension = MyExtension(config)
        await extension.initialize()
        result = await extension.my_custom_method("test")
        self.assertIsNotNone(result)
```

### 6. Package for Distribution

Create a `setup.py` file to package your extension:

```python
from setuptools import setup, find_packages

setup(
    name="my-openmas-extension",
    version="0.1.0",
    description="My custom OpenMAS extension",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "openmas>=0.3.0"
    ],
    entry_points={
        "openmas.extensions": [
            "my_extension = my_extension:MyExtension"
        ]
    }
)
```

## Extension Type-Specific Development Guides

### Agent Extensions

Agent extensions enhance or modify agent capabilities and behavior.

#### Implementation

```python
from openmas.extensions import AgentExtension

class MyAgentExtension(AgentExtension):
    """My custom agent extension."""

    extension_type = "agent"
    extension_name = "my_agent_extension"

    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)

    async def setup(self, agent):
        """Set up the agent extension."""
        # Register custom capabilities
        agent.register_capability(
            "my_capability",
            "A capability provided by my extension",
            parameters={"type": "object", "properties": {}},
            returns={"type": "object", "properties": {}}
        )

        # Add custom event handlers
        agent.on("message", self._on_message)

    async def _on_message(self, message):
        """Handle incoming messages."""
        # Custom message handling logic
        return {"status": "processed"}
```

#### Best Practices

1. **Maintain Reasoning Agnosticism** - Don't assume a specific reasoning approach
2. **Support Multiple Protocols** - Ensure your capabilities work with different protocols
3. **Clear Documentation** - Document capabilities and parameters clearly
4. **Efficient Resource Usage** - Optimize for performance and minimal resource consumption
5. **Handle Errors Gracefully** - Provide meaningful error messages and recovery strategies

### Communicator Extensions

Communicator extensions add support for new communication protocols or transport mechanisms.

#### Implementation

```python
from openmas.extensions import CommunicatorExtension
import aiohttp

class HTTPCommunicator(CommunicatorExtension):
    """HTTP-based communicator implementation."""

    extension_type = "communicator"
    extension_name = "http"

    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:8000")
        self.session = None

    async def initialize(self):
        """Initialize the communicator."""
        self.session = aiohttp.ClientSession()
        self.initialized = True

    async def shutdown(self):
        """Shut down the communicator."""
        if self.session:
            await self.session.close()
        self.initialized = False

    async def send_message(self, endpoint, message):
        """Send a message via HTTP."""
        if not self.session:
            raise RuntimeError("HTTP session not initialized")

        url = f"{self.base_url}/{endpoint}"
        async with self.session.post(url, json=message) as response:
            return await response.json()

    async def start_server(self, port):
        """Start an HTTP server."""
        # Implementation for server mode
        pass
```

#### Best Practices

1. **Protocol Standards** - Adhere to protocol specifications and standards
2. **Efficient Connection Management** - Handle connections efficiently and avoid leaks
3. **Support Both Client and Server Modes** - When applicable
4. **Secure Default Settings** - Use secure defaults for authentication and encryption
5. **Protocol Adapters** - Provide protocol adapters for easy integration

### Asset Extensions

Asset extensions provide new resource types and loaders for models, embeddings, and other assets.

#### Implementation

```python
from openmas.extensions import AssetExtension
import os

class FileSystemAssetProvider(AssetExtension):
    """File system-based asset provider."""

    extension_type = "asset"
    extension_name = "filesystem_provider"

    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.base_directory = config.get("base_directory", "./assets")

    async def initialize(self):
        """Initialize the asset provider."""
        # Ensure the directory exists
        os.makedirs(self.base_directory, exist_ok=True)
        self.initialized = True

    async def get_asset(self, asset_id, asset_type=None):
        """Get an asset by ID."""
        asset_path = os.path.join(self.base_directory, asset_id)

        if not os.path.exists(asset_path):
            return None

        with open(asset_path, "rb") as f:
            content = f.read()

        return {
            "id": asset_id,
            "type": asset_type or self._guess_type(asset_id),
            "content": content
        }

    async def list_assets(self, asset_type=None):
        """List available assets."""
        assets = []

        for filename in os.listdir(self.base_directory):
            file_type = self._guess_type(filename)
            if asset_type is None or file_type == asset_type:
                assets.append({
                    "id": filename,
                    "type": file_type
                })

        return assets

    def _guess_type(self, filename):
        """Guess the asset type from the filename."""
        if filename.endswith(".txt"):
            return "text"
        elif filename.endswith(".json"):
            return "json"
        elif filename.endswith((".jpg", ".jpeg", ".png")):
            return "image"
        else:
            return "binary"
```

#### Best Practices

1. **Efficient Resource Loading** - Optimize asset loading for performance
2. **Caching Strategy** - Implement appropriate caching for frequently used assets
3. **Type Safety** - Ensure correct type handling for different asset types
4. **Error Handling** - Gracefully handle missing or corrupted assets
5. **Metadata Support** - Provide rich metadata for assets when available

## Protocol-Specific Adaptation

Extensions must support working with different protocols through protocol adapters. This section explains how to implement protocol-specific adaptations while maintaining reasoning agnosticism.

### Protocol Adapter Implementation

Protocol adapters enable cross-protocol communication by translating between different protocols. Here's a comprehensive example of a protocol adapter that supports both A2A and MCP protocols:

```python
from openmas.extensions import ProtocolAdapterExtension
from openmas.extensions.registry import ExtensionRegistry
from openmas.protocols.base import Message, MessageFormat
from openmas.protocols.a2a import A2AMessage
from openmas.protocols.mcp import MCPMessage
from typing import Dict, Any, Optional, Union, List
import logging
import json

logger = logging.getLogger(__name__)

class A2AMCPAdapter(ProtocolAdapterExtension):
    """Protocol adapter that translates between A2A and MCP protocols."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the protocol adapter extension."""
        super().__init__(config)
        self.config = config
        self._initialized = False
        self.registry = None

        # Capability mappings between protocols
        self.a2a_to_mcp_mapping = {}
        self.mcp_to_a2a_mapping = {}

    async def initialize(self) -> bool:
        """Initialize the protocol adapter."""
        if self._initialized:
            return True

        try:
            # Get configuration
            enabled = self.config.get("enabled", True)
            if not enabled:
                logger.info("A2A-MCP Protocol Adapter is disabled")
                return False

            # Initialize protocol mappings from configuration
            mappings = self.config.get("mappings", {})
            self.a2a_to_mcp_mapping = mappings.get("a2a_to_mcp", {})
            self.mcp_to_a2a_mapping = mappings.get("mcp_to_a2a", {})

            # Get extension registry
            self.registry = ExtensionRegistry.get_instance()

            # Register this adapter with the registry
            self.registry.register_protocol_adapter(
                "a2a", "mcp", self.translate_a2a_to_mcp
            )
            self.registry.register_protocol_adapter(
                "mcp", "a2a", self.translate_mcp_to_a2a
            )

            logger.info("A2A-MCP Protocol Adapter initialized successfully")
            self._initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize A2A-MCP Protocol Adapter: {e}")
            return False

    async def translate_a2a_to_mcp(self, message: A2AMessage) -> MCPMessage:
        """Translate an A2A message to MCP format."""
        if not self._initialized:
            raise RuntimeError("Protocol adapter not initialized")

        try:
            # Extract A2A message components
            a2a_capability = message.capability
            a2a_parameters = message.parameters

            # Map A2A capability to MCP tool name
            mcp_tool_name = self.a2a_to_mcp_mapping.get(a2a_capability)
            if not mcp_tool_name:
                # Use the same name if not mapped
                mcp_tool_name = a2a_capability

            # Create equivalent MCP message
            mcp_message = MCPMessage(
                name=mcp_tool_name,
                arguments=a2a_parameters,
                message_id=message.message_id
            )

            return mcp_message

        except Exception as e:
            logger.error(f"Failed to translate A2A to MCP: {e}")
            raise

    async def translate_mcp_to_a2a(self, message: MCPMessage) -> A2AMessage:
        """Translate an MCP message to A2A format."""
        if not self._initialized:
            raise RuntimeError("Protocol adapter not initialized")

        try:
            # Extract MCP message components
            mcp_tool_name = message.name
            mcp_arguments = message.arguments

            # Map MCP tool name to A2A capability
            a2a_capability = self.mcp_to_a2a_mapping.get(mcp_tool_name)
            if not a2a_capability:
                # Use the same name if not mapped
                a2a_capability = mcp_tool_name

            # Create equivalent A2A message
            a2a_message = A2AMessage(
                capability=a2a_capability,
                parameters=mcp_arguments,
                message_id=message.message_id
            )

            return a2a_message

        except Exception as e:
            logger.error(f"Failed to translate MCP to A2A: {e}")
            raise

    async def translate_a2a_response_to_mcp(self, a2a_response: Dict[str, Any]) -> Dict[str, Any]:
        """Translate an A2A response to MCP format."""
        # For simple responses, the format may be compatible
        # For complex responses, additional transformation may be needed
        return {
            "content": a2a_response,
            "content_type": "application/json"
        }

    async def translate_mcp_response_to_a2a(self, mcp_response: Dict[str, Any]) -> Dict[str, Any]:
        """Translate an MCP response to A2A format."""
        # Extract the content from MCP response
        if isinstance(mcp_response, dict) and "content" in mcp_response:
            return mcp_response["content"]
        return mcp_response

    async def shutdown(self) -> bool:
        """Clean up resources and shut down the adapter."""
        logger.info("Shutting down A2A-MCP Protocol Adapter")
        self._initialized = False
        return True

class MyExtensionA2AAdapter(ProtocolAdapterExtension):
    """A2A adapter for my extension."""

    extension_type = "protocol_adapter"
    extension_name = "my_extension_a2a"

    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)

    def adapt_request(self, request):
        """Adapt a request to A2A format."""
        return {
            "type": "request",
            "capability": request.get("method", "default"),
            "content": request.get("params", {})
        }

    def adapt_response(self, response):
        """Adapt a response from A2A format."""
        return {
            "result": response.get("content", {}),
            "status": response.get("status", "success")
        }

    def get_capability_definition(self, capability):
        """Get the A2A capability definition."""
        return {
            "name": capability["name"],
            "description": capability["description"],
            "parameters": capability["parameters"]
        }
```

### Multi-Protocol Support

Implement support for multiple protocols:

```python
from openmas.extensions import MultiProtocolExtension
from openmas.protocols.adapters import A2AAdapter, MCPAdapter

class MyMultiProtocolExtension(MultiProtocolExtension):
    """Extension supporting multiple protocols."""

    extension_type = "my_multi_protocol"
    extension_name = "my_extension"

    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)

        # Register protocol adapters
        self.register_protocol_adapter("a2a", A2AAdapter())
        self.register_protocol_adapter("mcp", MCPAdapter())

    async def handle_request(self, request, protocol="a2a"):
        """Handle a request using the appropriate protocol adapter."""
        adapter = self.get_protocol_adapter(protocol)
        if not adapter:
            raise ValueError(f"Unsupported protocol: {protocol}")

        # Adapt the request to the extension's internal format
        adapted_request = adapter.adapt_request(request)

        # Process the request
        result = await self._process_request(adapted_request)

        # Adapt the response back to the protocol's format
        return adapter.adapt_response(result)

    async def _process_request(self, request):
        """Process a request in the internal format."""
        # Implementation
        pass
```

## Maintaining Reasoning Agnosticism

Extensions should maintain OpenMAS's reasoning agnosticism by following these principles:

### 1. Clear Separation

Keep a clear separation between communication (extension functionality) and reasoning:

```python
# GOOD - Clear separation
class MyExtension(BaseExtension):
    async def process_request(self, request):
        # Handle the communication aspects
        result = await self.delegate_to_reasoner(request)
        return self.format_response(result)

    async def delegate_to_reasoner(self, request):
        # Delegate to the appropriate reasoner through abstract interface
        return await self.reasoner.process(request)

# BAD - Mixing communication and reasoning
class MyExtension(BaseExtension):
    async def process_request(self, request):
        # Directly implementing reasoning logic here
        if request["type"] == "question":
            # Direct LLM call without abstraction
            return await self.llm_client.generate(request["content"])
        else:
            # Rule-based logic hardcoded in the extension
            return self.apply_rules(request["content"])
```

### 2. Abstract Interfaces

Use abstract interfaces for reasoning components:

```python
# GOOD - Abstract reasoning interface
class MyExtension(BaseExtension):
    def __init__(self, config):
        super().__init__(config)
        # Get reasoner through abstract factory
        self.reasoner = ReasonerFactory.create(
            config.get("reasoner_type", "default"),
            config.get("reasoner_config", {})
        )

    async def process(self, input_data):
        # Use abstract reasoning interface
        return await self.reasoner.process(input_data)

# BAD - Concrete reasoning implementation
class MyExtension(BaseExtension):
    def __init__(self, config):
        super().__init__(config)
        # Directly instantiating a specific reasoner type
        self.gpt4_client = GPT4Client(
            api_key=config["api_key"],
            model="gpt-4"
        )

    async def process(self, input_data):
        # Direct dependency on specific reasoning implementation
        return await self.gpt4_client.generate(input_data)
```

### 3. Protocol Independence

Ensure your extension works with any protocol:

```python
# GOOD - Protocol independence
class MyExtension(MultiProtocolExtension):
    def __init__(self, config):
        super().__init__(config)
        # Register multiple protocol adapters
        self.register_protocol_adapter("a2a", A2AAdapter())
        self.register_protocol_adapter("mcp", MCPAdapter())
        self.register_protocol_adapter("http", HTTPAdapter())

    async def process(self, request, protocol):
        # Use the appropriate protocol adapter
        adapter = self.get_protocol_adapter(protocol)
        adapted_request = adapter.adapt_request(request)
        result = await self._process_internal(adapted_request)
        return adapter.adapt_response(result)

# BAD - Protocol dependence
class MyExtension(BaseExtension):
    async def process_a2a_request(self, request):
        # A2A-specific implementation
        return {"content": result, "status": "success"}

    async def process_mcp_request(self, request):
        # MCP-specific implementation
        return {"result": result, "error": None}
```

## Testing Extensions

### Unit Testing

Write unit tests for your extension:

```python
import unittest
from unittest.mock import MagicMock, AsyncMock
from my_extension import MyExtension

class TestMyExtension(unittest.TestCase):
    def setUp(self):
        self.config = {"enabled": True, "custom_property": "test"}
        self.extension = MyExtension(self.config)

    async def test_initialization(self):
        self.assertEqual(self.extension.custom_property, "test")
        self.assertFalse(self.extension.initialized)

        await self.extension.initialize()
        self.assertTrue(self.extension.initialized)

    async def test_my_custom_method(self):
        await self.extension.initialize()

        # Set up mocks
        self.extension._internal_dependency = AsyncMock()
        self.extension._internal_dependency.fetch.return_value = "result"

        # Test the method
        result = await self.extension.my_custom_method("test")

        # Assertions
        self.assertEqual(result, "processed_result")
        self.extension._internal_dependency.fetch.assert_called_once_with("test")
```

### Integration Testing

Test integration with OpenMAS:

```python
import unittest
from openmas.extensions import ExtensionRegistry
from openmas.core import OpenMAS
from my_extension import MyExtension

class TestExtensionIntegration(unittest.TestCase):
    async def setUp(self):
        # Initialize OpenMAS
        self.openmas = OpenMAS()

        # Register the extension
        self.registry = ExtensionRegistry()
        self.registry.register("my_extension_type", "my_extension", MyExtension)

        # Set up configuration
        self.config = {
            "extensions": {
                "my_extension": {
                    "type": "my_extension_type",
                    "name": "my_extension",
                    "enabled": True,
                    "custom_property": "test"
                }
            }
        }

        # Initialize OpenMAS with the configuration
        await self.openmas.initialize(self.config)

    async def test_extension_loading(self):
        # Get the extension instance
        extension = self.openmas.get_extension("my_extension_type", "my_extension")

        # Assertions
        self.assertIsNotNone(extension)
        self.assertIsInstance(extension, MyExtension)
        self.assertTrue(extension.initialized)
        self.assertEqual(extension.custom_property, "test")

    async def test_extension_functionality(self):
        # Get the extension instance
        extension = self.openmas.get_extension("my_extension_type", "my_extension")

        # Test functionality
        result = await extension.my_custom_method("test")

        # Assertions
        self.assertEqual(result, "expected_result")
```

## Packaging and Distribution

### Setup.py

Create a proper `setup.py` for your extension:

```python
from setuptools import setup, find_packages

setup(
    name="openmas-myextension",
    version="0.1.0",
    description="My custom OpenMAS extension",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "openmas>=0.3.0",
        "additional-dependency>=1.0.0"
    ],
    entry_points={
        "openmas.extensions": [
            "my_extension = my_extension:MyExtension"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ]
)
```

### README.md

Document your extension clearly:

```markdown
# My OpenMAS Extension

A custom extension for OpenMAS that [brief description].

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
pip install openmas-myextension
```

## Usage

```python
from openmas.core import OpenMAS

# Configure OpenMAS with the extension
config = {
    "extensions": {
        "my_extension": {
            "type": "my_extension_type",
            "name": "my_extension",
            "enabled": True,
            "custom_property": "value"
        }
    }
}

# Initialize OpenMAS
openmas = OpenMAS()
await openmas.initialize(config)

# Use the extension
extension = openmas.get_extension("my_extension_type", "my_extension")
result = await extension.my_custom_method("input")
```

## Configuration

### Options

- `custom_property`: [Description]
- `another_option`: [Description]

## License

MIT
```

## Best Practices Summary

1. **Maintain Reasoning Agnosticism** - Keep a clear separation between communication and reasoning
2. **Protocol Independence** - Support multiple protocols through adapters
3. **Clear Documentation** - Document your extension thoroughly
4. **Comprehensive Testing** - Write unit and integration tests
5. **Error Handling** - Provide meaningful error messages and graceful recovery
6. **Resource Management** - Properly initialize and clean up resources
7. **Type Safety** - Use proper type hints and validation
8. **Configuration Validation** - Validate configuration options
9. **Secure Defaults** - Use secure default settings
10. **Performance Optimization** - Optimize for performance when possible
