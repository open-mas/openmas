# Extension System Design

## Overview

The OpenMAS Extension System provides a flexible, configurable approach to extending and customizing the framework. It enables developers to add new functionality, integrate with external systems, and adapt OpenMAS to specific use cases without modifying core components. The design maintains OpenMAS's reasoning agnosticism and supports all protocols directly.

## Core Principles

1. **Clear Extension Points** - Well-defined interfaces for extending functionality
2. **Dynamic Discovery** - Runtime discovery of extensions through a consistent mechanism
3. **Lazy Loading** - Loading extensions only when needed
4. **Configuration-Driven** - Extensions are enabled and configured through YAML
5. **Type Safety** - Type validation and compatibility checking
6. **Protocol Independence** - Extensions work with any communication protocol
7. **Reasoning Agnosticism** - Extensions maintain separation between communication and reasoning
8. **Minimal Overhead** - Efficient discovery with minimal performance impact
9. **Late Binding** - Extensions are discovered at runtime, not compile time
10. **Transparent Operation** - Clear logging of discovery process

## Extension Types

OpenMAS supports these standard extension types:

1. **Communicator Extensions** - Add support for new communication protocols
2. **Agent Extensions** - Extend agent capabilities and behaviors
3. **Asset Extensions** - Add new asset and resource types
4. **Prompt Extensions** - Custom prompt templates and management
5. **LLM Extensions** - Integrate with language models
6. **Reasoning Extensions** - Custom reasoning approaches
7. **Protocol Adapters** - Convert between protocol-specific formats
8. **Tool Extensions** - Add new tool capabilities

## Architecture Implementation

### ExtensionRegistry Class

The `ExtensionRegistry` serves as the central catalog of all available extensions:

```python
class ExtensionRegistry:
    """Registry of all available extensions."""

    def __init__(self):
        """Initialize the registry."""
        self.extensions = {}  # type -> name -> extension_info

    def register_extension(self, extension_type, extension_name, extension_class, metadata=None):
        """Register an extension."""
        if extension_type not in self.extensions:
            self.extensions[extension_type] = {}

        self.extensions[extension_type][extension_name] = {
            "class": extension_class,
            "metadata": metadata or {}
        }

    def get_extension(self, extension_type, extension_name):
        """Get an extension by type and name."""
        if extension_type not in self.extensions:
            return None

        return self.extensions[extension_type].get(extension_name)

    def list_extensions(self, extension_type=None):
        """List all registered extensions of a type."""
        if extension_type is not None:
            return self.extensions.get(extension_type, {})

        return self.extensions
```

### ExtensionLoader Class

The `ExtensionLoader` handles loading and initializing extensions:

```python
class ExtensionLoader:
    """System for loading extensions."""

    def __init__(self, registry):
        """Initialize the loader."""
        self.registry = registry
        self.loaded_extensions = {}  # type -> name -> instance

    def load_extension(self, extension_type, extension_name, config=None):
        """Load and initialize an extension."""
        # Check if already loaded
        if extension_type in self.loaded_extensions and extension_name in self.loaded_extensions[extension_type]:
            return self.loaded_extensions[extension_type][extension_name]

        # Get extension info from registry
        extension_info = self.registry.get_extension(extension_type, extension_name)
        if not extension_info:
            raise ValueError(f"Extension not found: {extension_type}/{extension_name}")

        # Initialize the extension
        extension_class = extension_info["class"]
        extension_instance = extension_class(config or {})

        # Store in loaded extensions
        if extension_type not in self.loaded_extensions:
            self.loaded_extensions[extension_type] = {}

        self.loaded_extensions[extension_type][extension_name] = extension_instance

        return extension_instance
```

### ExtensionDiscovery Class

The `ExtensionDiscovery` finds extensions in various locations:

```python
class ExtensionDiscovery:
    """Discovers available extensions."""

    def __init__(self, registry):
        """Initialize the discovery system."""
        self.registry = registry

    def discover_extensions(self):
        """Find all available extensions."""
        # Discover built-in extensions
        self._discover_builtin_extensions()

        # Discover installed package extensions
        self._discover_package_extensions()

        # Discover local extensions
        self._discover_local_extensions()

    def _discover_builtin_extensions(self):
        """Find built-in extensions."""
        # Implementation for discovering extensions that ship with OpenMAS
        pass

    def _discover_package_extensions(self):
        """Find extensions from installed packages."""
        # Implementation for discovering extensions from installed Python packages
        pass

    def _discover_local_extensions(self):
        """Find extensions in the local project."""
        # Implementation for discovering extensions in the current project
        pass
```

### Extension Base Classes

Base classes for each extension type provide consistent interfaces:

```python
class BaseExtension:
    """Base class for all extensions."""

    def __init__(self, config):
        """Initialize the extension."""
        self.config = config

    def validate_config(self):
        """Validate the extension configuration."""
        pass

class CommunicatorExtension(BaseExtension):
    """Base class for communicator extensions."""

    def create_communicator(self, agent_config):
        """Create a communicator instance."""
        pass

class AgentExtension(BaseExtension):
    """Base class for agent extensions."""

    def enhance_agent(self, agent):
        """Enhance an agent with additional capabilities."""
        pass

class AssetExtension(BaseExtension):
    """Base class for asset extensions."""

    def provide_asset(self, asset_id, context=None):
        """Provide an asset requested by ID."""
        pass

class PromptExtension(BaseExtension):
    """Base class for prompt extensions."""

    def get_template(self, template_id):
        """Get a prompt template by ID."""
        pass

    def render_template(self, template_id, context):
        """Render a template with context."""
        pass

class ReasoningExtension(BaseExtension):
    """Base class for reasoning extensions."""

    def create_reasoner(self, agent_config):
        """Create a reasoner instance."""
        pass
```

## Extension Integration

### Extension Point Registration

Components register extension points through a consistent pattern:

```python
class AgentComponent:
    """Example component with extension points."""

    def __init__(self, config, extension_registry):
        """Initialize with extension registry."""
        self.config = config
        self.extension_registry = extension_registry
        self.extensions = {}

        # Load configured extensions
        self._load_extensions()

    def _load_extensions(self):
        """Load all configured extensions for this component."""
        if "extensions" not in self.config:
            return

        for ext_config in self.config["extensions"]:
            ext_type = ext_config["type"]
            ext_name = ext_config["name"]

            # Load through the registry
            extension = self.extension_registry.load_extension(
                ext_type, ext_name, ext_config.get("config", {})
            )

            # Store by type
            if ext_type not in self.extensions:
                self.extensions[ext_type] = []

            self.extensions[ext_type].append(extension)
```

### Multi-Protocol Support

Extensions can support multiple protocols with format-specific adapters:

```python
class MultiProtocolExtension(BaseExtension):
    """Extension that supports multiple protocols."""

    def __init__(self, config):
        """Initialize with protocol adapters."""
        super().__init__(config)
        self.protocol_adapters = {}

        # Initialize protocol adapters
        self._initialize_protocol_adapters()

    def _initialize_protocol_adapters(self):
        """Initialize protocol-specific adapters."""
        adapters_config = self.config.get("protocol_adapters", {})

        for protocol, adapter_config in adapters_config.items():
            adapter_type = adapter_config["type"]
            adapter = self._create_adapter(adapter_type, adapter_config)
            self.protocol_adapters[protocol] = adapter

    def _create_adapter(self, adapter_type, config):
        """Create a protocol adapter."""
        # Implementation for creating the adapter
        pass

    def get_protocol_adapter(self, protocol):
        """Get adapter for a specific protocol."""
        return self.protocol_adapters.get(protocol)
```

## Extension Discovery Process

Extensions are discovered through a layered process:

1. **Built-in Components** - The framework checks for built-in implementations first
2. **Project Extensions** - It searches paths defined in `extension_paths`
3. **Package Extensions** - It searches installed packages in `packages/`
4. **Python Path** - Finally, it checks the standard Python import path

This approach allows for progressive overrides, where project-specific extensions can customize or replace built-in functionality.

### Discovery Locations

Extensions are discovered in the following locations, in order of precedence:

#### 1. Built-in Extensions

Built-in extensions are included with the core OpenMAS framework:

```
openmas/
├── agent/
│   ├── __init__.py
│   ├── base_agent.py
│   └── builtin/
│       ├── __init__.py
│       ├── http_agent.py
│       └── cli_agent.py
├── communicator/
│   ├── __init__.py
│   ├── base_communicator.py
│   └── builtin/
│       ├── __init__.py
│       ├── http_communicator.py
│       └── mqtt_communicator.py
└── extension/
    ├── __init__.py
    └── registry.py
```

#### 2. Project Extensions

Project extensions are located in the project's extension directories:

```
my_project/
├── extensions/
│   ├── agents/
│   │   └── my_agent.py
│   ├── communicators/
│   │   └── my_communicator.py
│   └── reasoning/
│       └── my_reasoner.py
├── config.yaml
└── main.py
```

#### 3. Package Extensions

Package extensions are installed Python packages with OpenMAS extensions:

```
site-packages/
├── openmas_ext_http/
│   ├── __init__.py
│   └── agents/
│       └── rest_agent.py
└── openmas_ext_nlp/
    ├── __init__.py
    └── reasoning/
        └── nlp_reasoner.py
```

### Discovery Algorithm

The discovery process follows this algorithm:

```python
async def discover_extension(type, name):
    # Check built-in extensions
    if extension_exists_in_builtins(type, name):
        return get_builtin_extension(type, name)

    # Check project extensions
    for path in extension_paths:
        if extension_exists_in_path(path, type, name):
            return get_extension_from_path(path, type, name)

    # Check package extensions
    for package in packages:
        if extension_exists_in_package(package, type, name):
            return get_extension_from_package(package, type, name)

    # Check Python path
    return get_extension_from_python_path(type, name)
```

## Lazy Loading Mechanism

The OpenMAS extension system implements lazy loading to optimize performance:

### Extension Reference

Extension references are lightweight proxies to actual extensions:

```python
class ExtensionReference:
    """A reference to an extension that hasn't been loaded yet."""

    def __init__(self, extension_type, extension_name, registry):
        """Initialize the extension reference."""
        self.extension_type = extension_type
        self.extension_name = extension_name
        self.registry = registry
        self.extension_info = None
        self._resolved_extension = None

    async def resolve(self):
        """Resolve the reference to the actual extension."""
        if self._resolved_extension is not None:
            return self._resolved_extension

        # Get extension info if not already loaded
        if not self.extension_info:
            self.extension_info = self.registry.get_extension_info(self.extension_type, self.extension_name)
            if not self.extension_info:
                raise ValueError(f"Extension not found: {self.extension_type}:{self.extension_name}")

        # Load the extension
        loader = ExtensionLoader(self.registry)
        self._resolved_extension = await loader.load_extension(
            self.extension_type,
            self.extension_name,
            self.extension_info.get("config")
        )

        return self._resolved_extension

    def __getattr__(self, name):
        """Delegate attribute access to the resolved extension."""
        if self._resolved_extension is None:
            raise AttributeError("Extension not yet resolved")

        return getattr(self._resolved_extension, name)
```

### Lazy Dependency Injection

Dependencies are injected only when needed:

```python
async def inject_dependencies(component, dependencies):
    """Inject dependencies into a component."""
    for name, dep_ref in dependencies.items():
        # Ensure the dependency is resolved
        if isinstance(dep_ref, ExtensionReference):
            dependency = await dep_ref.resolve()
        else:
            dependency = dep_ref

        # Set the dependency
        setattr(component, name, dependency)
```

### On-Demand Loading

Extensions are loaded only when actually used:

```python
class LazyExtensionManager:
    """Manager for lazily loading extensions."""

    def __init__(self, registry):
        """Initialize the manager."""
        self.registry = registry
        self.references = {}

    def get_extension_reference(self, extension_type, extension_name):
        """Get a reference to an extension."""
        key = f"{extension_type}:{extension_name}"

        # Create reference if not already exists
        if key not in self.references:
            self.references[key] = ExtensionReference(extension_type, extension_name, self.registry)

        return self.references[key]
```

## Package Registry System

The OpenMAS Package Registry serves as a central repository for discovering, sharing, and managing extensions:

### Package Index

The Package Index is the central catalog of all available packages:

```python
class PackageIndex:
    """Index of all available packages."""

    def __init__(self):
        """Initialize the index."""
        self.packages = {}  # name -> version -> package_info

    def register_package(self, name, version, metadata):
        """Register a package in the index."""
        if name not in self.packages:
            self.packages[name] = {}

        self.packages[name][version] = metadata

    def get_package(self, name, version=None):
        """Get a package by name and optional version."""
        if name not in self.packages:
            return None

        if version is not None:
            return self.packages[name].get(version)

        # Return latest version if no version specified
        versions = sorted(self.packages[name].keys(), key=parse_version)
        latest_version = versions[-1]

        return self.packages[name][latest_version]

    def list_packages(self, query=None):
        """List all packages, optionally filtered by query."""
        result = []

        for name, versions in self.packages.items():
            if query and query.lower() not in name.lower():
                continue

            for version, metadata in versions.items():
                result.append({
                    "name": name,
                    "version": version,
                    "description": metadata.get("description", ""),
                    "author": metadata.get("author", ""),
                    "tags": metadata.get("tags", [])
                })

        return result
```

### Dependency Resolution

The Dependency Resolver handles package dependencies:

```python
class DependencyResolver:
    """System for resolving dependencies."""

    def __init__(self, package_index):
        """Initialize the resolver."""
        self.package_index = package_index

    async def resolve_dependencies(self, dependencies):
        """Resolve a list of dependencies to concrete packages."""
        result = []

        for dep in dependencies:
            name = dep["name"]
            version_constraint = dep.get("version", "*")

            # Find package matching constraint
            package = await self._find_matching_package(name, version_constraint)
            if not package:
                if dep.get("optional", False):
                    continue

                raise ValueError(f"Cannot resolve dependency: {name} {version_constraint}")

            result.append(package)

            # Recursively resolve dependencies
            if "dependencies" in package:
                sub_deps = await self.resolve_dependencies(package["dependencies"])
                result.extend(sub_deps)

        return result

    async def _find_matching_package(self, name, version_constraint):
        """Find a package matching the name and version constraint."""
        # Implementation for finding matching package
        pass
```

## Extension Packaging

Extensions can be distributed as Python packages with a standard structure:

```
my_extension_package/
├── setup.py
├── pyproject.toml
└── my_extension/
    ├── __init__.py       # Entry point with registration hooks
    ├── agents/
    │   └── my_agent.py   # Contains MyAgent class
    ├── reasoning/
    │   └── my_reasoner.py  # Contains MyReasoner class
    └── protocols/
        └── my_protocol.py  # Contains MyProtocol class
```

Package registration happens through entrypoints:

```python
# In setup.py
setup(
    name="my_extension_package",
    # ...
    entry_points={
        "openmas.extensions": [
            "agents = my_extension.agents",
            "reasoning = my_extension.reasoning",
            "protocols = my_extension.protocols",
        ],
    },
)
```

## Configuration Example

Extensions are configured in the unified schema:

```yaml
# System-wide extension configuration
extensions:
  discovery:
    enabled: true
    scan_paths:
      - "extensions/"
      - "custom_extensions/"
    package_scan: true

  # Extension type configurations
  communicators:
    - name: "mqtt_communicator"
      enabled: true
      config:
        broker_url: "mqtt://localhost:1883"

  agents:
    - name: "specialized_agent"
      enabled: true
      config:
        specialization: "financial"

  reasoning:
    - name: "hybrid_reasoner"
      enabled: true
      config:
        symbolic_backend: "prolog"
        neural_backend: "llama"

# Agent-specific extension configuration
agents:
  financial_advisor:
    # Agent type config...

    # Extensions for this agent
    extensions:
      - type: "reasoning"
        name: "hybrid_reasoner"
        config:
          priority: "neural"

      - type: "protocols"
        name: "secure_messaging"
        config:
          encryption: "AES256"
```

## Extension Discovery Process

The extension discovery process follows these steps:

1. **Initialization**: Extension system is initialized during application startup
2. **Built-in Discovery**: Core extensions that ship with OpenMAS are registered
3. **Package Discovery**: Extensions from installed Python packages are found via entrypoints
4. **Local Discovery**: Project-local extensions are found in configured directories
5. **Lazy Loading**: Extensions are only loaded when requested by components
6. **Configuration Validation**: Extension configurations are validated against schemas
7. **Initialization**: Extensions are initialized with their configurations

## Protocol Support in Extensions

Extensions maintain protocol independence by:

1. **Protocol Agnostic APIs**: Core extension interfaces are protocol-independent
2. **Protocol Adapters**: Extensions can provide protocol-specific adapters
3. **Format Conversion**: Support for converting between protocol message formats
4. **Capability Mapping**: Extensions can map capabilities to protocol-specific formats

## Security Considerations

1. **Extension Validation**: Extensions are validated before loading
2. **Sandboxing**: Extensions run in a constrained environment
3. **Permission Management**: Extensions request permissions explicitly
4. **Code Signing**: Extensions can be signed for verification
5. **Vulnerability Scanning**: Extension code can be scanned for security issues

## Extension System API

The Extension System design is implemented through a comprehensive set of interfaces and data models that provide type-safe, protocol-independent extension management. The API includes:

- **IExtensionRegistry**: Central interface for extension registration, discovery, and dependency management
- **IExtensionLoader**: Interface for extension lifecycle management and configuration validation
- **Base Extension Interfaces**: Type-specific interfaces for all extension categories (IAgentExtension, ICommunicatorExtension, IAssetExtension, etc.)
- **Extension Data Models**: Comprehensive Pydantic models for definitions, configurations, and status tracking

For detailed API specifications, see [Extension System API](../extension_system_api.md).

The Extension System API ensures:
1. **Type Safety**: All extension interactions are type-checked and validated
2. **Protocol Independence**: Extensions work seamlessly across all protocols through SIMF integration
3. **Dependency Resolution**: Automatic resolution of extension dependencies with cycle detection
4. **Configuration Validation**: Schema-based validation of extension configurations
5. **Lifecycle Management**: Complete control over extension loading, initialization, and shutdown

## Reasoning Agnosticism in Extensions

Extensions maintain OpenMAS's reasoning agnosticism by:

1. **Clear Separation**: Extensions respect the separation of communication and reasoning
2. **Interface Compliance**: Extensions implement standardized interfaces
3. **Configuration-Driven**: Extensions are configured independently of reasoning approach
4. **Protocol Independence**: Extensions work with any supported protocol
5. **Component Discovery**: Components are automatically discovered and registered
6. **Package Distribution**: Extensions can be packaged and distributed
7. **Dependency Management**: Dependencies between extensions are automatically resolved

This extension system design provides a flexible foundation for extending OpenMAS while preserving its key architectural principles.
