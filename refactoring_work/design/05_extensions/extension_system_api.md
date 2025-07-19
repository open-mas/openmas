# Extension System API

## Overview

The Extension System API provides the core interfaces for managing pluggable components in OpenMAS. This API enables a flexible architecture where developers can extend and customize the framework without modifying core components, while maintaining SIMF compatibility, protocol independence, and reasoning agnosticism.

The Extension System serves as the foundation for:
- Extension registration and discovery
- Extension lifecycle management and dependency resolution
- Type-safe extension interfaces for all extension categories
- Configuration validation and error handling
- Integration with core OpenMAS components

## Architecture Integration

The Extension System integrates with OpenMAS architecture at this position:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OpenMAS Architecture                         │
├─────────────────┬─────────────────────┬─────────────────────────────┤
│ Core Components │ Extension System    │ Extension Implementations   │
│                 │                     │                             │
│ ┌─────────────┐ │ ┌─────────────────┐ │ ┌─────────────────────────┐ │
│ │Agent        │◄┼─┤IExtensionRegist-│◄┼─┤IAgentExtension          │ │
│ │Framework    │ │ │ry               │ │ │ICommunicatorExtension   │ │
│ │             │ │ │                 │ │ │IAssetExtension          │ │
│ │IPattern     │◄┼─┤IExtensionLoader │◄┼─┤IPromptExtension         │ │
│ │Engine       │ │ │                 │ │ │ILLMExtension            │ │
│ │             │ │ │                 │ │ │IReasoningExtension      │ │
│ │IProtocol    │◄┼─┤Extension        │◄┼─┤IProtocolAdapterExt.     │ │
│ │Adapter      │ │ │Discovery        │ │ │IToolExtension           │ │
│ └─────────────┘ │ └─────────────────┘ │ └─────────────────────────┘ │
│                 │                     │                             │
│ Uses extensions │ Manages extensions  │ Implements extension        │
│ through         │ and coordinates     │ functionality with          │
│ interfaces      │ lifecycle           │ specific capabilities       │
└─────────────────┴─────────────────────┴─────────────────────────────┘
```

## Core Interfaces

### 1. IExtensionRegistry

The primary interface for extension registration and discovery:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Type
from pydantic import BaseModel
from datetime import datetime

class IExtensionRegistry(ABC):
    """
    Core interface for the Extension Registry.
    
    Provides extension registration, discovery, and metadata management
    while maintaining type safety and validation across all extension types.
    """
    
    @abstractmethod
    async def register_extension(self, extension: 'ExtensionDefinition') -> None:
        """
        Register a new extension with the registry.
        
        Args:
            extension: Complete extension definition including metadata and entry point
            
        Raises:
            ExtensionRegistrationError: If extension registration fails
            ExtensionConfigError: If extension definition is invalid
            ExtensionError: If extension name conflicts with existing extension
        """
        pass
    
    @abstractmethod
    async def unregister_extension(self, extension_name: str) -> None:
        """
        Unregister an extension from the registry.
        
        Args:
            extension_name: Name of the extension to unregister
            
        Raises:
            ExtensionNotFoundError: If extension does not exist
            ExtensionError: If extension has active instances
        """
        pass
    
    @abstractmethod
    async def discover_extensions(self) -> None:
        """
        Discover available extensions from all configured sources.
        
        Discovers extensions from:
        - Built-in extensions (shipped with OpenMAS)
        - Package-based extensions (via Python entry points)
        - Directory-based extensions (local extension directories)
        
        Raises:
            ExtensionDiscoveryError: If discovery process fails
        """
        pass
    
    @abstractmethod
    async def get_available_extensions(
        self, 
        extension_type: Optional[str] = None
    ) -> List['ExtensionInfo']:
        """
        Get list of all registered extensions, optionally filtered by type.
        
        Args:
            extension_type: Optional filter by extension type
            
        Returns:
            List of ExtensionInfo objects describing available extensions
        """
        pass
    
    @abstractmethod
    async def get_extension_definition(self, extension_name: str) -> 'ExtensionDefinition':
        """
        Get the complete definition for a specific extension.
        
        Args:
            extension_name: Name of the extension to retrieve
            
        Returns:
            ExtensionDefinition with complete extension specification
            
        Raises:
            ExtensionNotFoundError: If extension does not exist
        """
        pass
    
    @abstractmethod
    def supports_extension_type(self, extension_type: str) -> bool:
        """
        Check if a specific extension type is supported.
        
        Args:
            extension_type: Extension type to check (e.g., "agent", "communicator")
            
        Returns:
            True if extension type is supported, False otherwise
        """
        pass
    
    @abstractmethod
    async def validate_extension_dependencies(
        self, 
        extension_name: str
    ) -> 'ValidationResult':
        """
        Validate that all dependencies for an extension are satisfied.
        
        Args:
            extension_name: Name of the extension to validate
            
        Returns:
            ValidationResult indicating if dependencies are satisfied
            
        Raises:
            ExtensionNotFoundError: If extension does not exist
        """
        pass
    
    @abstractmethod
    async def get_extension_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the dependency graph for all registered extensions.
        
        Returns:
            Dictionary mapping extension names to their dependencies
        """
        pass
    
    @abstractmethod
    async def resolve_loading_order(
        self, 
        extension_names: List[str]
    ) -> List[str]:
        """
        Resolve the correct loading order for a set of extensions.
        
        Args:
            extension_names: List of extension names to order
            
        Returns:
            List of extension names in dependency-resolved order
            
        Raises:
            ExtensionDependencyError: If circular dependencies are detected
        """
        pass


### 2. IExtensionLoader

Interface for extension loading and lifecycle management:

```python
class IExtensionLoader(ABC):
    """
    Interface for extension loading and lifecycle management.
    
    Handles the instantiation, configuration, and lifecycle of extension
    instances while managing dependencies and ensuring proper initialization order.
    """
    
    @abstractmethod
    async def load_extension(
        self, 
        extension_name: str, 
        config: 'ExtensionConfig'
    ) -> 'IExtension':
        """
        Load an extension instance with the given configuration.
        
        Args:
            extension_name: Name of the extension to load
            config: Configuration for the extension instance
            
        Returns:
            IExtension instance ready for use
            
        Raises:
            ExtensionNotFoundError: If extension is not registered
            ExtensionConfigError: If configuration is invalid
            ExtensionLoadError: If extension loading fails
        """
        pass
    
    @abstractmethod
    async def unload_extension(self, extension_id: str) -> None:
        """
        Unload a specific extension instance.
        
        Args:
            extension_id: Unique identifier of the extension instance
            
        Raises:
            ExtensionNotFoundError: If extension instance does not exist
            ExtensionError: If extension cannot be safely unloaded
        """
        pass
    
    @abstractmethod
    async def reload_extension(self, extension_id: str) -> None:
        """
        Reload a specific extension instance with its current configuration.
        
        Args:
            extension_id: Unique identifier of the extension instance
            
        Raises:
            ExtensionNotFoundError: If extension instance does not exist
            ExtensionLoadError: If extension reload fails
        """
        pass
    
    @abstractmethod
    async def get_loaded_extensions(self) -> List['ExtensionInstanceInfo']:
        """
        Get list of all currently loaded extension instances.
        
        Returns:
            List of ExtensionInstanceInfo objects for loaded instances
        """
        pass
    
    @abstractmethod
    async def get_extension_status(self, extension_id: str) -> 'ExtensionStatus':
        """
        Get the current status of a specific extension instance.
        
        Args:
            extension_id: Unique identifier of the extension instance
            
        Returns:
            ExtensionStatus with current state information
            
        Raises:
            ExtensionNotFoundError: If extension instance does not exist
        """
        pass
    
    @abstractmethod
    async def validate_extension_config(
        self, 
        extension_name: str, 
        config: 'ExtensionConfig'
    ) -> 'ValidationResult':
        """
        Validate extension configuration without loading the extension.
        
        Args:
            extension_name: Name of the extension to validate config for
            config: Configuration to validate
            
        Returns:
            ValidationResult indicating if config is valid
            
        Raises:
            ExtensionNotFoundError: If extension is not registered
        """
        pass
    
    @abstractmethod
    async def load_extensions_batch(
        self, 
        extensions: List[tuple[str, 'ExtensionConfig']]
    ) -> List['IExtension']:
        """
        Load multiple extensions in dependency-resolved order.
        
        Args:
            extensions: List of (extension_name, config) tuples to load
            
        Returns:
            List of loaded IExtension instances in loading order
            
        Raises:
            ExtensionDependencyError: If dependencies cannot be resolved
            ExtensionLoadError: If any extension fails to load
        """
        pass
```

### 3. Base Extension Interfaces

#### IExtension (Base Interface)

```python
class IExtension(ABC):
    """
    Base interface for all OpenMAS extensions.
    
    Provides common lifecycle methods and metadata access that all
    extension types must implement for consistent management.
    """
    
    @property
    @abstractmethod
    def extension_id(self) -> str:
        """Unique identifier for this extension instance."""
        pass
    
    @property
    @abstractmethod
    def extension_name(self) -> str:
        """Name of the extension this instance implements."""
        pass
    
    @property
    @abstractmethod
    def extension_type(self) -> str:
        """Type of extension (e.g., 'agent', 'communicator')."""
        pass
    
    @abstractmethod
    async def initialize(self, config: 'ExtensionConfig') -> None:
        """
        Initialize the extension with the given configuration.
        
        Args:
            config: Extension configuration
            
        Raises:
            ExtensionConfigError: If configuration is invalid
            ExtensionError: If initialization fails
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """
        Gracefully shutdown the extension and release resources.
        
        Raises:
            ExtensionError: If shutdown fails
        """
        pass
    
    @abstractmethod
    async def get_metadata(self) -> 'ExtensionMetadata':
        """
        Get metadata about this extension instance.
        
        Returns:
            ExtensionMetadata with instance information
        """
        pass
    
    @abstractmethod
    async def validate_config(self, config: 'ExtensionConfig') -> 'ValidationResult':
        """
        Validate a configuration for this extension type.
        
        Args:
            config: Configuration to validate
            
        Returns:
            ValidationResult indicating if config is valid
        """
        pass
    
    @abstractmethod
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status information for this extension instance.
        
        Returns:
            Dictionary containing health status information
        """
        pass
```

#### Type-Specific Extension Interfaces

```python
class IAgentExtension(IExtension):
    """Interface for agent enhancement extensions."""
    
    @abstractmethod
    async def enhance_agent(self, agent: 'Agent') -> None:
        """
        Enhance an agent with additional capabilities.
        
        Args:
            agent: The agent instance to enhance
        """
        pass
    
    @abstractmethod
    async def get_provided_capabilities(self) -> List[str]:
        """Get list of capabilities this extension provides."""
        pass


class ICommunicatorExtension(IExtension):
    """Interface for communication protocol extensions."""
    
    @abstractmethod
    async def create_communicator(self, agent_config: Dict[str, Any]) -> 'Communicator':
        """
        Create a communicator instance for an agent.
        
        Args:
            agent_config: Agent configuration dictionary
            
        Returns:
            Communicator instance for the agent
        """
        pass
    
    @abstractmethod
    def get_supported_protocols(self) -> List[str]:
        """Get list of protocols supported by this extension."""
        pass


class IAssetExtension(IExtension):
    """Interface for asset management extensions."""
    
    @abstractmethod
    async def provide_asset(
        self, 
        asset_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Provide an asset by its identifier.
        
        Args:
            asset_id: Unique identifier for the asset
            context: Optional context for asset retrieval
            
        Returns:
            The requested asset
        """
        pass
    
    @abstractmethod
    def get_supported_asset_types(self) -> List[str]:
        """Get list of asset types supported by this extension."""
        pass


class IPromptExtension(IExtension):
    """Interface for prompt management extensions."""
    
    @abstractmethod
    async def get_template(self, template_id: str) -> str:
        """
        Get a prompt template by identifier.
        
        Args:
            template_id: Unique identifier for the template
            
        Returns:
            The prompt template string
        """
        pass
    
    @abstractmethod
    async def render_template(
        self, 
        template_id: str, 
        context: Dict[str, Any]
    ) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_id: Template identifier
            context: Context variables for rendering
            
        Returns:
            Rendered prompt string
        """
        pass


class ILLMExtension(IExtension):
    """Interface for language model integration extensions."""
    
    @abstractmethod
    async def generate_completion(
        self, 
        prompt: str, 
        options: Dict[str, Any]
    ) -> str:
        """
        Generate a completion from the language model.
        
        Args:
            prompt: Input prompt
            options: Generation options
            
        Returns:
            Generated completion
        """
        pass
    
    @abstractmethod
    async def generate_embedding(
        self, 
        text: str, 
        options: Dict[str, Any]
    ) -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            options: Embedding options
            
        Returns:
            Embedding vector
        """
        pass


class IReasoningExtension(IExtension):
    """Interface for reasoning approach extensions."""
    
    @abstractmethod
    async def create_reasoner(self, agent_config: Dict[str, Any]) -> 'Reasoner':
        """
        Create a reasoner instance for an agent.
        
        Args:
            agent_config: Agent configuration dictionary
            
        Returns:
            Reasoner instance
        """
        pass
    
    @abstractmethod
    def get_reasoning_capabilities(self) -> List[str]:
        """Get list of reasoning capabilities provided."""
        pass


class IProtocolAdapterExtension(IExtension):
    """Interface for protocol adaptation extensions."""
    
    @abstractmethod
    async def adapt_message(
        self, 
        message: Any, 
        source_protocol: str, 
        target_protocol: str
    ) -> Any:
        """
        Adapt a message between protocols.
        
        Args:
            message: Message to adapt
            source_protocol: Source protocol identifier
            target_protocol: Target protocol identifier
            
        Returns:
            Adapted message
        """
        pass
    
    @abstractmethod
    def get_supported_protocol_pairs(self) -> List[tuple[str, str]]:
        """Get list of supported (source, target) protocol pairs."""
        pass


class IToolExtension(IExtension):
    """Interface for tool capability extensions."""
    
    @abstractmethod
    async def execute_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Any:
        """
        Execute a tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            context: Execution context
            
        Returns:
            Tool execution result
        """
        pass
    
    @abstractmethod
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all tools provided by this extension."""
        pass
```

## Data Models

### 1. Core Extension Models

```python
from enum import Enum
from typing import Union, Literal, Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ExtensionType(str, Enum):
    """Enumeration of extension types."""
    AGENT = "agent"
    COMMUNICATOR = "communicator"
    ASSET = "asset"
    PROMPT = "prompt"
    LLM = "llm"
    REASONING = "reasoning"
    PROTOCOL_ADAPTER = "protocol_adapter"
    TOOL = "tool"
    CUSTOM = "custom"

class ExtensionState(str, Enum):
    """Enumeration of extension states."""
    REGISTERED = "registered"
    LOADING = "loading"
    LOADED = "loaded"
    INITIALIZING = "initializing"
    RUNNING = "running"
    ERROR = "error"
    STOPPING = "stopping"
    STOPPED = "stopped"
    UNLOADED = "unloaded"

class ExtensionDependency(BaseModel):
    """Specification of an extension dependency."""
    
    name: str = Field(description="Name of the required extension")
    
    version_constraint: str = Field(
        description="Version constraint (e.g., '>=1.0.0', '~=1.2.0')",
        default="*"
    )
    
    optional: bool = Field(
        description="Whether this dependency is optional",
        default=False
    )
    
    extension_type: Optional[ExtensionType] = Field(
        description="Required extension type",
        default=None
    )

class ExtensionDefinition(BaseModel):
    """
    Complete definition of an extension.
    
    This model represents an extension specification that can be
    registered with the Extension Registry.
    """
    name: str = Field(
        description="Unique identifier for the extension",
        pattern=r"^[a-z][a-z0-9_]*$"  # Snake case extension names
    )
    
    version: str = Field(
        description="Extension version following semantic versioning",
        pattern=r"^\d+\.\d+\.\d+$"
    )
    
    extension_type: ExtensionType = Field(
        description="Type of extension"
    )
    
    description: str = Field(
        description="Human-readable description of the extension"
    )
    
    author: str = Field(
        description="Extension author or organization"
    )
    
    license: str = Field(
        description="Extension license (e.g., 'MIT', 'Apache-2.0')"
    )
    
    dependencies: List[ExtensionDependency] = Field(
        description="List of extension dependencies",
        default_factory=list
    )
    
    supported_protocols: List[str] = Field(
        description="List of protocols this extension supports",
        default_factory=lambda: ["*"]  # Default to all protocols
    )
    
    entry_point: str = Field(
        description="Fully qualified Python class implementing the extension"
    )
    
    config_schema: Dict[str, Any] = Field(
        description="JSON schema for extension configuration",
        default_factory=dict
    )
    
    metadata: Dict[str, Any] = Field(
        description="Additional extension metadata",
        default_factory=dict
    )
    
    minimum_openmas_version: str = Field(
        description="Minimum required OpenMAS version",
        default="0.3.0"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "weather_tool",
                "version": "1.0.0",
                "extension_type": "tool",
                "description": "Provides weather information tools",
                "author": "OpenMAS Community",
                "license": "MIT",
                "dependencies": [],
                "supported_protocols": ["a2a", "mcp", "http"],
                "entry_point": "weather_extension.WeatherToolExtension",
                "config_schema": {
                    "type": "object",
                    "properties": {
                        "api_key": {"type": "string"},
                        "default_units": {"type": "string", "default": "metric"}
                    }
                }
            }
        }

class ExtensionConfig(BaseModel):
    """
    Configuration for an extension instance.
    
    This model contains all the information needed to configure
    a specific extension instance.
    """
    extension_name: str = Field(
        description="Name of the extension to configure"
    )
    
    enabled: bool = Field(
        description="Whether this extension is enabled",
        default=True
    )
    
    priority: int = Field(
        description="Extension loading/execution priority (higher = earlier)",
        default=50,
        ge=0, le=100
    )
    
    options: Dict[str, Any] = Field(
        description="Extension-specific configuration options",
        default_factory=dict
    )
    
    protocol_options: Dict[str, Dict[str, Any]] = Field(
        description="Protocol-specific configuration options",
        default_factory=dict
    )
    
    environment: Dict[str, str] = Field(
        description="Environment variables for the extension",
        default_factory=dict
    )
    
    metadata: Dict[str, Any] = Field(
        description="Additional configuration metadata",
        default_factory=dict
    )

class ExtensionStatus(BaseModel):
    """Runtime status information for an extension instance."""
    
    extension_id: str = Field(description="Unique instance identifier")
    
    extension_name: str = Field(description="Extension name")
    
    extension_type: ExtensionType = Field(description="Extension type")
    
    status: ExtensionState = Field(description="Current extension state")
    
    loaded_at: datetime = Field(description="When extension was loaded")
    
    last_activity: Optional[datetime] = Field(
        description="Last activity timestamp",
        default=None
    )
    
    error_count: int = Field(
        description="Number of errors encountered",
        default=0,
        ge=0
    )
    
    last_error: Optional[str] = Field(
        description="Last error message",
        default=None
    )
    
    current_config: ExtensionConfig = Field(
        description="Current extension configuration"
    )
    
    health_status: Dict[str, Any] = Field(
        description="Health status information",
        default_factory=dict
    )
    
    metadata: Dict[str, Any] = Field(
        description="Instance-specific metadata",
        default_factory=dict
    )
```

### 2. Extension Information Models

```python
class ExtensionInfo(BaseModel):
    """Summary information about a registered extension."""
    
    name: str = Field(description="Extension name")
    version: str = Field(description="Extension version")
    extension_type: ExtensionType = Field(description="Extension type")
    description: str = Field(description="Extension description")
    author: str = Field(description="Extension author")
    supported_protocols: List[str] = Field(description="Supported protocols")
    dependencies: List[str] = Field(description="Dependency names")
    is_available: bool = Field(description="Whether extension is available for loading")
    registration_time: datetime = Field(description="When extension was registered")

class ExtensionInstanceInfo(BaseModel):
    """Summary information about an extension instance."""
    
    extension_id: str = Field(description="Extension instance identifier")
    extension_name: str = Field(description="Extension name")
    extension_type: ExtensionType = Field(description="Extension type")
    status: ExtensionState = Field(description="Current status")
    loaded_at: datetime = Field(description="Load time")
    error_count: int = Field(description="Error count")
    last_activity: Optional[datetime] = Field(description="Last activity time")

class ExtensionMetadata(BaseModel):
    """Detailed metadata for an extension instance."""
    
    extension_id: str = Field(description="Extension instance identifier")
    extension_name: str = Field(description="Extension name")
    extension_type: ExtensionType = Field(description="Extension type")
    version: str = Field(description="Extension version")
    capabilities: List[str] = Field(description="Capabilities provided")
    supported_protocols: List[str] = Field(description="Supported protocols")
    resource_usage: Dict[str, Any] = Field(description="Resource usage statistics")
    performance_metrics: Dict[str, Any] = Field(description="Performance metrics")
    custom_metadata: Dict[str, Any] = Field(description="Extension-specific metadata")

class ValidationResult(BaseModel):
    """Result of extension configuration or dependency validation."""
    
    valid: bool = Field(description="Whether validation passed")
    
    errors: List[str] = Field(
        description="Validation error messages",
        default_factory=list
    )
    
    warnings: List[str] = Field(
        description="Validation warning messages",
        default_factory=list
    )
    
    validated_config: Optional[Dict[str, Any]] = Field(
        description="Validated and normalized configuration",
        default=None
    )
    
    dependency_resolution: Optional[List[str]] = Field(
        description="Resolved dependency loading order",
        default=None
    )
```

## Error Hierarchy

```python
class ExtensionError(Exception):
    """Base exception for extension-related errors."""
    
    def __init__(self, message: str, extension_name: Optional[str] = None, **kwargs):
        super().__init__(message)
        self.extension_name = extension_name
        self.metadata = kwargs

class ExtensionNotFoundError(ExtensionError):
    """Raised when a requested extension is not registered."""
    pass

class ExtensionConfigError(ExtensionError):
    """Raised when extension configuration is invalid."""
    
    def __init__(self, message: str, config_errors: List[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_errors = config_errors or []

class ExtensionLoadError(ExtensionError):
    """Raised when extension loading fails."""
    
    def __init__(self, message: str, load_stage: str = "unknown", **kwargs):
        super().__init__(message, **kwargs)
        self.load_stage = load_stage

class ExtensionRegistrationError(ExtensionError):
    """Raised when extension registration fails."""
    pass

class ExtensionDependencyError(ExtensionError):
    """Raised when extension dependencies cannot be resolved."""
    
    def __init__(self, message: str, dependency_chain: List[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.dependency_chain = dependency_chain or []

class ExtensionDiscoveryError(ExtensionError):
    """Raised when extension discovery fails."""
    pass

class ExtensionVersionError(ExtensionError):
    """Raised when extension version constraints cannot be satisfied."""
    
    def __init__(self, message: str, required_version: str = None, available_version: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.required_version = required_version
        self.available_version = available_version
```

## Extension Discovery and Dependency Resolution

### 1. Discovery Mechanisms

The Extension System supports three discovery mechanisms:

```python
# Built-in Extension Discovery
# Extensions that ship with OpenMAS core
BUILTIN_EXTENSIONS = [
    "openmas.extensions.basic_agent_extension",
    "openmas.extensions.http_communicator_extension", 
    "openmas.extensions.file_asset_extension"
]

# Package-based Discovery
# Extensions from installed Python packages via entry points
# setup.py example:
setup(
    name="my-openmas-extension",
    entry_points={
        "openmas.extensions": [
            "my_tool = my_extension.tool:MyToolExtension",
            "my_agent = my_extension.agent:MyAgentExtension",
        ],
    },
)

# Directory-based Discovery  
# Local extensions in configured directories
EXTENSION_DIRECTORIES = [
    "extensions/",
    "custom_extensions/",
    os.path.expanduser("~/.openmas/extensions/")
]
```

### 2. Dependency Resolution Algorithm

```python
async def resolve_dependencies(extensions: List[str]) -> List[str]:
    """
    Resolve extension dependencies and return loading order.
    
    Uses topological sorting with cycle detection.
    """
    # 1. Build dependency graph
    graph = {}
    for ext_name in extensions:
        definition = await registry.get_extension_definition(ext_name)
        graph[ext_name] = [dep.name for dep in definition.dependencies if not dep.optional]
    
    # 2. Detect circular dependencies
    def has_cycle(node, visited, rec_stack):
        visited[node] = True
        rec_stack[node] = True
        
        for neighbor in graph.get(node, []):
            if not visited.get(neighbor, False):
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif rec_stack.get(neighbor, False):
                return True
                
        rec_stack[node] = False
        return False
    
    # 3. Topological sort for loading order
    def topological_sort():
        visited = {}
        stack = []
        
        def dfs(node):
            visited[node] = True
            for neighbor in graph.get(node, []):
                if not visited.get(neighbor, False):
                    dfs(neighbor)
            stack.append(node)
        
        for node in extensions:
            if not visited.get(node, False):
                dfs(node)
                
        return stack[::-1]  # Reverse for correct order
    
    return topological_sort()
```

## Integration with Core Components

### 1. Protocol Adapter Integration

```python
# Extensions can extend protocol support
class CustomProtocolAdapter(IProtocolAdapterExtension):
    async def adapt_message(self, message, source_protocol, target_protocol):
        # Custom protocol adaptation logic
        if source_protocol == "custom" and target_protocol == "mcp":
            return self._convert_custom_to_mcp(message)
        # ... other adaptations
        
    def get_supported_protocol_pairs(self):
        return [("custom", "mcp"), ("custom", "a2a")]
```

### 2. Pattern Engine Integration

```python
# Extensions can provide new communication patterns
class CustomPatternExtension(IAgentExtension):
    async def enhance_agent(self, agent):
        # Register custom pattern with pattern engine
        custom_pattern = CustomPattern(self.config.options)
        await agent.pattern_engine.register_pattern(custom_pattern)
```

### 3. SIMF Integration

```python
# Extensions must work with SIMF for message handling
class MessageProcessingExtension(IAgentExtension):
    async def process_message(self, message: InternalMessageFormat):
        # Process SIMF message
        if message.payload.payload_type == "invocation_content":
            # Handle tool invocation
            result = await self._execute_tool(message.payload.invocation_name, 
                                              message.payload.arguments)
            
            # Return SIMF response
            return InternalMessageFormat(
                message_id=str(uuid.uuid4()),
                target_agent_id=message.source_agent_id,
                message_type="TOOL_RESULT",
                payload={
                    "payload_type": "invocation_result_content",
                    "invocation_name": message.payload.invocation_name,
                    "status": "success",
                    "result": result
                },
                metadata={
                    "extension_id": self.extension_id,
                    "original_message_id": message.message_id
                }
            )
```

## Usage Examples

### 1. Extension Registration and Discovery

```python
# Register a custom extension
extension_def = ExtensionDefinition(
    name="weather_tool",
    version="1.0.0", 
    extension_type=ExtensionType.TOOL,
    description="Provides weather information tools",
    author="OpenMAS Community",
    license="MIT",
    entry_point="weather_extension.WeatherToolExtension",
    config_schema={
        "type": "object",
        "properties": {
            "api_key": {"type": "string", "description": "Weather API key"},
            "default_units": {"type": "string", "default": "metric"}
        },
        "required": ["api_key"]
    }
)

await extension_registry.register_extension(extension_def)

# Discover all available extensions
await extension_registry.discover_extensions()

# Get available tool extensions
tool_extensions = await extension_registry.get_available_extensions("tool")
for ext in tool_extensions:
    print(f"Tool Extension: {ext.name} - {ext.description}")
```

### 2. Extension Loading and Configuration

```python
# Configure and load an extension
config = ExtensionConfig(
    extension_name="weather_tool",
    enabled=True,
    priority=75,
    options={
        "api_key": "your-weather-api-key",
        "default_units": "metric",
        "cache_timeout": 300
    },
    protocol_options={
        "mcp": {
            "tool_name_prefix": "weather_"
        },
        "a2a": {
            "capability_namespace": "weather"
        }
    }
)

# Validate configuration
validation = await extension_loader.validate_extension_config("weather_tool", config)
if not validation.valid:
    print(f"Configuration errors: {validation.errors}")
    return

# Load the extension
weather_extension = await extension_loader.load_extension("weather_tool", config)

# Check extension status
status = await extension_loader.get_extension_status(weather_extension.extension_id)
print(f"Extension status: {status.status}")
```

### 3. Batch Extension Loading with Dependencies

```python
# Load multiple extensions with automatic dependency resolution
extensions_to_load = [
    ("weather_tool", weather_config),
    ("translation_tool", translation_config), 
    ("database_agent", db_agent_config)
]

# Extensions will be loaded in dependency-resolved order
loaded_extensions = await extension_loader.load_extensions_batch(extensions_to_load)

for ext in loaded_extensions:
    print(f"Loaded: {ext.extension_name} ({ext.extension_type})")
    metadata = await ext.get_metadata()
    print(f"  Capabilities: {metadata.capabilities}")
```

### 4. Custom Extension Implementation

```python
from openmas.extensions import IToolExtension, ExtensionConfig, ValidationResult

class WeatherToolExtension(IToolExtension):
    """Example tool extension implementation."""
    
    def __init__(self):
        self._extension_id = str(uuid.uuid4())
        self._api_key = None
        self._default_units = "metric"
    
    @property
    def extension_id(self) -> str:
        return self._extension_id
        
    @property  
    def extension_name(self) -> str:
        return "weather_tool"
        
    @property
    def extension_type(self) -> str:
        return "tool"
    
    async def initialize(self, config: ExtensionConfig) -> None:
        """Initialize the weather tool extension."""
        self._api_key = config.options.get("api_key")
        self._default_units = config.options.get("default_units", "metric")
        
        if not self._api_key:
            raise ExtensionConfigError("api_key is required")
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a weather tool."""
        if tool_name == "get_weather":
            location = parameters.get("location")
            units = parameters.get("units", self._default_units)
            
            # Call weather API
            weather_data = await self._fetch_weather(location, units)
            return {
                "location": location,
                "temperature": weather_data["temperature"],
                "conditions": weather_data["conditions"],
                "humidity": weather_data["humidity"]
            }
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for weather tools."""
        return {
            "get_weather": {
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location to get weather for"
                        },
                        "units": {
                            "type": "string", 
                            "enum": ["metric", "imperial"],
                            "description": "Temperature units"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    
    async def _fetch_weather(self, location: str, units: str) -> Dict[str, Any]:
        """Fetch weather data from API."""
        # Implementation details...
        pass
```

---

This Extension System API provides a comprehensive foundation for building a pluggable architecture in OpenMAS while maintaining the core principles of protocol independence, reasoning agnosticism, and SIMF compatibility. 