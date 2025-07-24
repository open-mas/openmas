# Agent State Management Interface

## 1. Overview

The `IAgentState` interface provides a formal contract for managing an agent's internal state. It is designed to be a comprehensive and flexible tool that supports simple key-value storage, robust persistence, and a powerful publish-subscribe mechanism for reactive, event-driven programming within an agent.

This allows for a clean separation of concerns, where an agent's components can access and react to state changes without being tightly coupled.

## 2. IAgentState Interface Definition

```python
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Dict, List, Optional

# Type alias for a callback function that handles state changes.
# The callback receives the key, old value, and new value.
StateChangeCallback = Callable[[str, Any, Any], Coroutine[Any, Any, None]]

class IAgentState(ABC):
    """
    Defines the interface for an agent's state management.

    This interface provides methods for key-value storage, persistence, and a
    publish-subscribe system for state changes.
    """

    # --- Key-Value Store Operations ---

    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        """
        Sets a value for a given key in the agent's state.

        This method will trigger a notification to all subscribers of the key.

        Args:
            key: The key to set.
            value: The value to associate with the key.
        """
        pass

    @abstractmethod
    async def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieves a value for a given key from the agent's state.

        Args:
            key: The key to retrieve.
            default: The default value to return if the key does not exist.

        Returns:
            The value associated with the key, or the default value.
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Deletes a key-value pair from the agent's state.

        This method will trigger a notification to all subscribers of the key.

        Args:
            key: The key to delete.

        Returns:
            True if the key was deleted, False if it did not exist.
        """
        pass

    @abstractmethod
    async def get_all(self) -> Dict[str, Any]:
        """
        Retrieves a copy of the entire agent state.

        Returns:
            A dictionary representing the agent's current state.
        """
        pass

    # --- Persistence Operations ---

    @abstractmethod
    async def save(self) -> None:
        """
        Persists the current state to a durable storage backend.

        The specific backend (e.g., file, database) is determined by the
        implementing class.
        """
        pass

    @abstractmethod
    async def load(self) -> None:
        """
        Loads the state from the durable storage backend, replacing the
        current in-memory state.
        """
        pass

    # --- Publish-Subscribe Operations for State Changes ---

    @abstractmethod
    async def subscribe(
        self, key: str, callback: StateChangeCallback
    ) -> None:
        """
        Subscribes a callback to be notified of changes to a specific key.

        Args:
            key: The key to subscribe to. Can support wildcards (e.g., 'config.*').
            callback: The async function to call when the key's value changes.
        """
        pass

    @abstractmethod
    async def unsubscribe(
        self, key: str, callback: StateChangeCallback
    ) -> None:
        """
        Unsubscribes a callback from notifications for a specific key.

        Args:
            key: The key to unsubscribe from.
            callback: The callback function to remove.
        """
        pass

    @abstractmethod
    async def publish(self, key: str, old_value: Any, new_value: Any) -> None:
        """
        Manually publishes a state change event to all subscribers.

        This is typically called internally by the `set` and `delete` methods,
        but can be used to broadcast custom state-related events.

        Args:
            key: The key that has changed.
            old_value: The previous value of the key.
            new_value: The new value of the key.
        """
        pass
```

## 3. Usage Example

Here is a conceptual example of how this interface might be used within an agent.

```python
class ExampleAgent(Agent):
    async def setup(self):
        await super().setup()
        # Subscribe to changes in the 'config.mode' state variable
        await self.state.subscribe("config.mode", self.on_mode_change)

    async def on_mode_change(self, key: str, old_value: Any, new_value: Any):
        print(f"Agent mode changed from '{old_value}' to '{new_value}'. Reconfiguring... ")
        # Logic to reconfigure the agent based on the new mode

    async def some_action(self):
        # Change the agent's mode, which will trigger the callback
        await self.state.set("config.mode", "aggressive")
```

## Implementation Considerations

### Storage Backends

The Agent State Management API can use various backends:

1. **Memory**: In-memory storage, fastest but not persistent across restarts
2. **File**: File-based storage for simple persistence
3. **Database**: SQL or NoSQL database storage for scalable persistence
4. **Redis**: High-performance distributed storage

### State Namespacing

State keys are automatically namespaced to prevent collisions:

- For `PRIVATE_PERSISTENT`: `agent_id:private:{key}`
- For `SESSION_SPECIFIC_PERSISTENT`: `agent_id:session:{session_id}:{key}`
- For `IN_MEMORY_SESSION_ONLY`: Stored in an in-memory session cache
- For `SHARED`: `shared:{key}`

## Configuration

Agent state management is configured through the unified configuration schema:

```yaml
agents:
  agent_name:
    # Other agent configuration...

    # State configuration
    state:
      # Storage backend configuration
      storage:
        type: "file"  # Options: "memory", "file", "database", "redis"

        # File storage options
        directory: "./agent_state"
        format: "json"

        # Database storage options
        connection_string: "sqlite:///agent_state.db"
        table_name: "agent_state"

        # Redis storage options
        redis_url: "redis://localhost:6379/0"

      # Expiration settings
      expiration:
        private_persistent: 2592000  # 30 days in seconds
        session_specific_persistent: 604800  # 7 days in seconds
        in_memory_session_only: 3600  # 1 hour in seconds
        shared: 86400  # 1 day in seconds

      # Serialization settings
      serialization:
        format: "json"  # Options: "json", "pickle", "msgpack"
        compress: false
        max_size_bytes: 1048576  # 1MB limit per state entry
```

## Usage Examples

### Basic Usage

```python
# Access the state manager through the agent context
state_manager = agent_context.state_manager

# Store a simple counter
await state_manager.set_state("counter", 42)

# Retrieve the counter
counter = await state_manager.get_state("counter")
print(f"Counter value: {counter}")  # Output: Counter value: 42

# Increment the counter
counter += 1
await state_manager.set_state("counter", counter)

# Check if a key exists
if await state_manager.has_state("user_settings"):
    settings = await state_manager.get_state("user_settings")
else:
    settings = {"theme": "light", "language": "en"}
    await state_manager.set_state("user_settings", settings)

# Delete a state entry
await state_manager.delete_state("temporary_data")

# List all keys with a specific prefix
config_keys = await state_manager.list_state_keys(prefix="config_")
```

### Working with Session-Specific State

```python
# Store session-specific data
await state_manager.set_state(
    "conversation_context",
    {"last_topic": "weather", "sentiment": "positive"},
    scope=AgentStateScope.SESSION_SPECIFIC_PERSISTENT
)

# Retrieve session-specific data
context = await state_manager.get_state(
    "conversation_context",
    scope=AgentStateScope.SESSION_SPECIFIC_PERSISTENT
)
```

### Working with Pydantic Models

```python
from pydantic import BaseModel
from typing import List, Optional

class AgentConfiguration(BaseModel):
    name: str
    version: str
    capabilities: List[str]
    description: Optional[str] = None
    is_active: bool = True

# Create and store a configuration
config = AgentConfiguration(
    name="DataAnalysisAgent",
    version="1.0.0",
    capabilities=["data_analysis", "visualization", "reporting"]
)
await state_manager.set_state("agent_configuration", config)

# Retrieve the configuration as a model
retrieved_config = await state_manager.get_state_as_model(
    "agent_configuration",
    AgentConfiguration
)
print(f"Agent name: {retrieved_config.name}")
```

## Integration with Session Management

The Agent State Management API works alongside the Session Management API:

- `SESSION_SPECIFIC_PERSISTENT` scope integrates with the Session Management system
- Session IDs are used to namespace session-specific state
- Session expiration can trigger cleanup of related state entries

For session-specific state that should not persist beyond the current session, use the `IN_MEMORY_SESSION_ONLY` scope or the dedicated Session Management API.

## Error Handling

The Agent State Management API defines a hierarchy of custom exceptions to allow for specific and predictable error handling.

```python
class StateStorageError(Exception):
    """Base exception for all state storage-related errors."""
    pass

class StateSerializationError(StateStorageError):
    """Exception raised when a value cannot be serialized or deserialized.

    This can happen if an object is not supported by the configured
    serialization format (e.g., trying to store a complex, non-Pydantic
    object as JSON).
    """
    pass

class StateNotFoundError(StateStorageError):
    """Exception raised when a specific state key is expected but not found.

    While `get_state` returns `None` for missing keys, this exception can be used
    in more restrictive contexts where the absence of a key is considered
    an error.
    """
    pass

class StateAccessDeniedError(StateStorageError):
    """Exception raised when an agent attempts to access a state entry
    without the required permissions (e.g., accessing another agent's
    private state).
    """
    pass

class StateDeserializationError(StateStorageError):
    """Exception raised when state deserialization fails."""
    pass
class StateBackendError(StateStorageError):
    """Exception raised when there's an error with the storage backend."""
    pass
```

## Implementation Notes

1. **Thread Safety**: All methods are async to ensure thread safety in concurrent environments
2. **Transactions**: The API does not provide explicit transaction support; each operation is atomic
3. **Size Limits**: Consider implementing size limits on state entries to prevent abuse
4. **Security**: Shared state should implement authorization checks
5. **Performance**: Implementations should consider caching for frequently accessed state

## Future Considerations

Potential future enhancements to the API:

1. **Transactional Updates**: Support for atomic multi-key operations
2. **Versioning**: Track state versions for conflict resolution
3. **Schema Evolution**: Handle schema changes gracefully for Pydantic models
4. **Query Capabilities**: More advanced querying for state entries

## Related Documentation

- [Agent Framework Overview](/refactoring_work/00b_overview/04_agents/agent_framework_overview.md)
- [Session Management](/refactoring_work/00b_overview/04_agents/session_management.md)
- [Agent Capabilities](/refactoring_work/00b_overview/04_agents/agent_capabilities.md)
