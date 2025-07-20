# OpenMAS Design Patterns Knowledge Base

This directory contains reference information about design patterns used in OpenMAS.

## Core Design Patterns

### Dependency Injection

OpenMAS uses dependency injection throughout the framework to enable testability and flexibility:

```python
class Component:
    def __init__(self, dependency=None):
        # Default implementation if none provided
        self.dependency = dependency or DefaultDependency()
```

### Factory Pattern

Factories are used to create instances of components:

```python
class CommunicatorFactory:
    """Factory for creating communicator instances."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def create(self, communicator_type: str, options: Dict[str, Any] = None) -> BaseCommunicator:
        """Create a communicator instance."""
        if communicator_type == "http":
            return HTTPCommunicator(options or {})
        elif communicator_type == "mcp-sse":
            return MCPSSECommunicator(options or {})
        elif communicator_type == "mcp-stdio":
            return MCPStdioCommunicator(options or {})
        else:
            raise ValueError(f"Unknown communicator type: {communicator_type}")
```

### Builder Pattern

Builders are used for complex object construction:

```python
class AgentBuilder:
    """Builder for creating agent instances."""

    def __init__(self):
        self.agent_class = None
        self.config = None
        self.communicator = None
        self.assets = None

    def with_class(self, agent_class: Type[BaseAgent]) -> 'AgentBuilder':
        self.agent_class = agent_class
        return self

    def with_config(self, config: AgentConfig) -> 'AgentBuilder':
        self.config = config
        return self

    def with_communicator(self, communicator: BaseCommunicator) -> 'AgentBuilder':
        self.communicator = communicator
        return self

    def with_assets(self, assets: AssetManager) -> 'AgentBuilder':
        self.assets = assets
        return self

    def build(self) -> BaseAgent:
        if not self.agent_class:
            raise ValueError("Agent class not specified")

        if not self.config:
            raise ValueError("Agent config not specified")

        agent = self.agent_class(config=self.config)

        if self.communicator:
            agent.set_communicator(self.communicator)

        if self.assets:
            agent.set_assets(self.assets)

        return agent
```

### Strategy Pattern

Strategies are used to encapsulate different behaviors:

```python
class SamplingStrategy(Protocol):
    """Interface for sampling strategies."""

    def sample(self, model: str, prompt: str, **kwargs) -> str:
        """Sample from a model."""
        ...

class TemperatureSamplingStrategy:
    """Temperature-based sampling strategy."""

    def __init__(self, temperature: float = 0.7):
        self.temperature = temperature

    def sample(self, model: str, prompt: str, **kwargs) -> str:
        """Sample from a model using temperature sampling."""
        # Implementation
        return "sampled text"
```

### Repository Pattern

Repositories abstract data access:

```python
class PromptRepository(Protocol):
    """Interface for prompt repositories."""

    def get_prompt(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name."""
        ...

    def save_prompt(self, name: str, prompt: PromptTemplate) -> None:
        """Save a prompt template."""
        ...

class FilePromptRepository:
    """File-based prompt repository."""

    def __init__(self, prompts_dir: str):
        self.prompts_dir = prompts_dir

    def get_prompt(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template from a file."""
        # Implementation
        return prompt

    def save_prompt(self, name: str, prompt: PromptTemplate) -> None:
        """Save a prompt template to a file."""
        # Implementation
```

## Architectural Patterns

### Component-Based Architecture

OpenMAS uses a component-based architecture to promote modularity:

```python
# Component interfaces
class AssetManager(Protocol):
    """Interface for asset management."""

    async def load_asset(self, asset_path: str) -> Any:
        """Load an asset."""
        ...

# Component implementation
class FileAssetManager:
    """File-based asset manager."""

    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir

    async def load_asset(self, asset_path: str) -> Any:
        """Load an asset from a file."""
        # Implementation
        return asset
```

### Event-Driven Architecture

Event-driven patterns for communication between components:

```python
class EventBus:
    """Event bus for publishing and subscribing to events."""

    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe to an event type."""
        self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Publish an event."""
        for callback in self.subscribers[event_type]:
            callback(event_data)
```

### Plugin Architecture

OpenMAS uses a plugin architecture for extensions:

```python
class PluginManager:
    """Manager for discovering and loading plugins."""

    def __init__(self, plugins_dir: str):
        self.plugins_dir = plugins_dir
        self.plugins = {}

    def discover_plugins(self) -> List[str]:
        """Discover available plugins."""
        # Implementation
        return plugin_names

    def load_plugin(self, plugin_name: str) -> Any:
        """Load a plugin by name."""
        # Implementation
        return plugin
```

## Best Practices

1. **Interface-First Design** - Define interfaces before implementations
2. **Composition Over Inheritance** - Prefer composition for extensibility
3. **SOLID Principles** - Follow the SOLID principles
4. **Loose Coupling** - Minimize dependencies between components
5. **High Cohesion** - Keep related functionality together
6. **Testability** - Design for testability from the start
7. **Error Handling** - Consistent error handling patterns

## OpenMAS-Specific Patterns

### Communicator Pattern

Standardized communication interfaces:

```python
class BaseCommunicator(ABC):
    """Base class for all communicators."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def setup(self) -> None:
        """Set up the communicator."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shut down the communicator."""
        pass

    @abstractmethod
    async def send_message(self, message: Any, recipient: str) -> None:
        """Send a message to a recipient."""
        pass

    @abstractmethod
    async def receive_message(self) -> Optional[Any]:
        """Receive a message."""
        pass
```

### Asset Management Pattern

Standardized asset access:

```python
class AssetManager:
    """Manager for agent assets."""

    def __init__(self, assets_dir: str, loaders: Dict[str, AssetLoader] = None):
        self.assets_dir = assets_dir
        self.loaders = loaders or {}
        self.cache = {}

    async def load_asset(self, asset_path: str) -> Any:
        """Load an asset."""
        if asset_path in self.cache:
            return self.cache[asset_path]

        extension = Path(asset_path).suffix.lower()
        loader = self.loaders.get(extension)

        if not loader:
            raise ValueError(f"No loader found for asset type: {extension}")

        asset = await loader.load(Path(self.assets_dir) / asset_path)
        self.cache[asset_path] = asset

        return asset
```

### Protocol Adapter Pattern

Adapters for different communication protocols:

```python
class ProtocolAdapter(ABC):
    """Base class for protocol adapters."""

    @abstractmethod
    async def adapt_message(self, message: Any) -> Any:
        """Adapt a message to the protocol format."""
        pass

    @abstractmethod
    async def parse_message(self, message: Any) -> Any:
        """Parse a message from the protocol format."""
        pass
```

## Example Usage

### Factory + Dependency Injection

```python
class AgentFactory:
    """Factory for creating agent instances."""

    def __init__(self, config: ProjectConfig, communicator_factory: CommunicatorFactory = None,
                asset_manager: AssetManager = None):
        self.config = config
        self.communicator_factory = communicator_factory or DefaultCommunicatorFactory()
        self.asset_manager = asset_manager or DefaultAssetManager()

    def create_agent(self, agent_id: str) -> BaseAgent:
        """Create an agent instance."""
        if agent_id not in self.config.agent_configs:
            raise ValueError(f"No configuration found for agent: {agent_id}")

        agent_config = self.config.agent_configs[agent_id]

        # Load the agent class
        agent_class = self._load_agent_class(agent_config.module, agent_config.class_name)

        # Create the communicator
        communicator = self.communicator_factory.create(
            agent_config.communicator.type,
            agent_config.communicator.options
        )

        # Create the agent
        agent = agent_class(config=agent_config)
        agent.set_communicator(communicator)
        agent.set_asset_manager(self.asset_manager)

        return agent
```
