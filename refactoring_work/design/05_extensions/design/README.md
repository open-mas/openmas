# Extension System Design

## Overview

The OpenMAS Extension System provides a flexible architecture for customizing and enhancing the framework without modifying core components. This document describes the design principles and architecture of the extension system.

## Architecture

The extension system uses a layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                 OpenMAS Application                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   Extension Registry                        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Discovery   │  │ Dependency  │  │ Loading/Unloading   │  │
│  │ Mechanism   │  │ Resolution  │  │ Mechanism           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   Extension Types                           │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │Communicator │  │   Agent     │  │   Asset     │   ...    │
│  │ Extensions  │  │ Extensions  │  │ Extensions  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                Protocol Adapters                            │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  A2A        │  │    MCP      │  │   HTTP      │   ...    │
│  │  Adapter    │  │   Adapter   │  │  Adapter    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Core Design Components

### 1. Extension Registry

The central repository for all registered extensions:

```python
class ExtensionRegistry:
    """Central registry for all extensions."""

    def __init__(self):
        """Initialize the registry."""
        self._extensions = {}
        self._references = {}
        self._discovery = ExtensionDiscovery(self)

    def register(self, extension_type, extension_name, extension_cls):
        """Register an extension class."""
        if extension_type not in self._extensions:
            self._extensions[extension_type] = {}

        self._extensions[extension_type][extension_name] = extension_cls
        return self

    def get(self, extension_type, extension_name):
        """Get an extension by type and name."""
        if extension_type not in self._extensions:
            return None

        return self._extensions[extension_type].get(extension_name)

    def discover(self, package_paths=None):
        """Discover extensions from specified package paths."""
        return self._discovery.discover(package_paths)

    def create_instance(self, extension_type, extension_name, config):
        """Create an instance of the specified extension."""
        extension_cls = self.get(extension_type, extension_name)
        if not extension_cls:
            # Try lazy loading
            reference = self._references.get((extension_type, extension_name))
            if reference:
                extension_cls = reference.load()

        if extension_cls:
            return extension_cls(config)

        return None
```

### 2. Extension Discovery

Responsible for discovering available extensions:

```python
class ExtensionDiscovery:
    """Discovers available extensions."""

    def __init__(self, registry):
        """Initialize the discovery system."""
        self._registry = registry

    def discover(self, package_paths=None):
        """Discover extensions from the specified paths."""
        # Default to standard paths if none provided
        if not package_paths:
            package_paths = [
                "openmas.extensions",
                "openmas.communicators",
                "openmas.agents",
                "openmas.assets",
                "openmas.prompts"
            ]

        discovered = []
        for package_path in package_paths:
            # Find all modules in the package
            discovered.extend(self._discover_from_package(package_path))

        return discovered

    def _discover_from_package(self, package_path):
        """Discover extensions from a specific package."""
        discovered = []

        # Import the package
        try:
            package = importlib.import_module(package_path)
            # Find extension classes in the package
            for name, obj in inspect.getmembers(package):
                if inspect.isclass(obj) and issubclass(obj, BaseExtension) and obj != BaseExtension:
                    # Get extension metadata
                    extension_type = getattr(obj, "extension_type", None)
                    extension_name = getattr(obj, "extension_name", name)

                    if extension_type:
                        # Register the extension
                        self._registry.register(extension_type, extension_name, obj)
                        discovered.append((extension_type, extension_name, obj))
        except ImportError:
            # Package not found, skip
            pass

        return discovered
```

### 3. Base Extension

The foundation for all extensions:

```python
class BaseExtension:
    """Base class for all extensions."""

    extension_type = None
    extension_name = None

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.initialized = False

    async def initialize(self):
        """Initialize the extension."""
        self.initialized = True

    async def shutdown(self):
        """Clean up resources."""
        self.initialized = False

    def get_config(self):
        """Get the extension configuration."""
        return self.config

    def is_initialized(self):
        """Check if the extension is initialized."""
        return self.initialized
```

### 4. Multi-Protocol Extensions

Extensions that support multiple protocols:

```python
class MultiProtocolExtension(BaseExtension):
    """Extension that supports multiple protocols."""

    def __init__(self, config):
        """Initialize with protocol adapters."""
        super().__init__(config)
        self.protocol_adapters = {}

    def register_protocol_adapter(self, protocol, adapter):
        """Register a protocol adapter."""
        self.protocol_adapters[protocol] = adapter
        return self

    def get_protocol_adapter(self, protocol):
        """Get a protocol adapter for the specified protocol."""
        return self.protocol_adapters.get(protocol)

    def supports_protocol(self, protocol):
        """Check if the extension supports the specified protocol."""
        return protocol in self.protocol_adapters
```

### 5. Extension References

Lazy-loaded references to extensions:

```python
class ExtensionReference:
    """A reference to an extension that hasn't been loaded yet."""

    def __init__(self, extension_type, extension_name, registry):
        """Initialize the extension reference."""
        self.extension_type = extension_type
        self.extension_name = extension_name
        self.registry = registry
        self.module_path = None
        self.class_name = None

    def load(self):
        """Load the extension class."""
        if not self.module_path:
            return None

        try:
            module = importlib.import_module(self.module_path)
            extension_cls = getattr(module, self.class_name)

            # Register the extension
            self.registry.register(
                self.extension_type,
                self.extension_name,
                extension_cls
            )

            return extension_cls
        except (ImportError, AttributeError):
            return None
```

### 6. Dependency Resolver

System for resolving extension dependencies:

```python
class DependencyResolver:
    """System for resolving dependencies."""

    def __init__(self, package_index):
        """Initialize the resolver."""
        self.package_index = package_index

    def resolve_dependencies(self, extension_config):
        """Resolve dependencies for an extension."""
        dependencies = extension_config.get("dependencies", [])
        resolved = []

        for dependency in dependencies:
            name = dependency["name"]
            version = dependency.get("version", "latest")

            # Check if dependency is available
            if self.package_index.has_package(name, version):
                resolved.append((name, version))
            else:
                raise DependencyResolutionError(f"Dependency {name}@{version} not available")

        return resolved
```

## Protocol Adapter Architecture

Protocol adapters enable extensions to work with different protocols:

```python
class ProtocolAdapter:
    """Base class for protocol adapters."""

    def __init__(self, protocol):
        """Initialize with the protocol name."""
        self.protocol = protocol

    def adapt_request(self, request):
        """Adapt a request to the protocol format."""
        raise NotImplementedError

    def adapt_response(self, response):
        """Adapt a response from the protocol format."""
        raise NotImplementedError

    def get_protocol_metadata(self):
        """Get protocol-specific metadata."""
        raise NotImplementedError
```

### A2A Protocol Adapter

```python
class A2AProtocolAdapter(ProtocolAdapter):
    """Adapter for the A2A protocol."""

    def __init__(self):
        """Initialize the A2A adapter."""
        super().__init__("a2a")

    def adapt_request(self, request):
        """Adapt a request to A2A format."""
        # Transform request to A2A format
        return {
            "type": request.get("type", "request"),
            "content": request.get("content", {}),
            "capability": request.get("capability", "default")
        }

    def adapt_response(self, response):
        """Adapt a response from A2A format."""
        # Transform response from A2A format
        return {
            "result": response.get("content", {}),
            "status": response.get("status", "success")
        }

    def get_protocol_metadata(self):
        """Get A2A-specific metadata."""
        return {
            "protocol": "a2a",
            "version": "1.0",
            "capabilities": []
        }
```

### MCP Protocol Adapter

```python
class MCPProtocolAdapter(ProtocolAdapter):
    """Adapter for the MCP protocol."""

    def __init__(self):
        """Initialize the MCP adapter."""
        super().__init__("mcp")

    def adapt_request(self, request):
        """Adapt a request to MCP format."""
        # Transform request to MCP format
        return {
            "type": "tool_call",
            "name": request.get("capability", "default"),
            "parameters": request.get("content", {})
        }

    def adapt_response(self, response):
        """Adapt a response from MCP format."""
        # Transform response from MCP format
        return {
            "result": response.get("result", {}),
            "status": "success" if not response.get("error") else "error"
        }

    def get_protocol_metadata(self):
        """Get MCP-specific metadata."""
        return {
            "protocol": "mcp",
            "version": "1.0",
            "tools": []
        }
```

## Extension Lifecycle

Extensions follow a standard lifecycle:

1. **Discovery** - Extensions are discovered at runtime
2. **Registration** - Extensions are registered with the registry
3. **Configuration** - Extensions are configured based on YAML
4. **Initialization** - Extensions are initialized with required resources
5. **Operation** - Extensions are used during normal operation
6. **Shutdown** - Extensions are gracefully shut down

This lifecycle ensures proper resource management and extension coordination.

## Extension Points

OpenMAS defines clear extension points where custom functionality can be added:

1. **Agent Extensions** - Custom agent types and behaviors
2. **Communicator Extensions** - New communication protocols
3. **Asset Extensions** - New resource types and providers
4. **Prompt Extensions** - Custom prompt templates and managers
5. **LLM Extensions** - Integration with language models
6. **Reasoning Extensions** - Custom reasoning approaches
7. **Protocol Adapters** - Conversion between protocols
8. **Tool Extensions** - Custom tool capabilities

Each extension point has a well-defined interface that extensions must implement.

## Reasoning Agnosticism

The extension system maintains OpenMAS's distinctive reasoning agnosticism through:

1. **Clear Separation** - Extensions respect the separation of communication and reasoning
2. **Interface Compliance** - Extensions implement standardized interfaces
3. **Configuration-Driven** - Extensions are configured independently of reasoning approach
4. **Protocol Independence** - Extensions work with any supported protocol
5. **Component Discovery** - Components are automatically discovered and registered

This enables developers to extend OpenMAS with new capabilities while preserving the separation between communication infrastructure ("body") and reasoning approaches ("brain").
