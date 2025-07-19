# Agent State Management API

## Overview

The Agent State Management API provides a standardized interface for agents to persistently save, load, and manage their internal state within the OpenMAS Agent Framework. This API ensures that agents can maintain their state across restarts and sessions, providing mechanisms for data persistence with well-defined scopes and serialization approaches.

## Key Concepts

### State vs. Session

- **Agent State**: Long-lived data belonging to an agent that persists beyond individual sessions (e.g., learned preferences, configuration, counters)
- **Session State**: Temporary data tied to a specific interaction session (handled by the Session Management API)

### State Scopes

State scopes define the visibility and lifetime of stored state data:

- **Private Persistent**: State private to the agent, persists across agent restarts
- **Session-Specific Persistent**: State associated with a particular session ID, persists if the session can be resumed
- **In-Memory Session-Only**: State tied to the current active session, lost when session ends or agent restarts
- **Shared**: State that can be accessed by other agents (with proper authorization)

### Data Serialization

The API handles serialization and deserialization of various data types:

- Native support for JSON-serializable primitives (str, int, float, bool, list, dict)
- Automatic handling of Pydantic models (serialized to JSON and deserialized back to models)
- Support for bytes storage for binary data

## IAgentStateManager Interface

The `IAgentStateManager` interface defines the core methods for agent state management:

```python
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class AgentStateScope(str, Enum):
    """Defines the scope and lifetime of agent state data."""
    
    PRIVATE_PERSISTENT = "private_persistent"
    """State private to the agent that persists across restarts."""
    
    SESSION_SPECIFIC_PERSISTENT = "session_specific_persistent"
    """State associated with a specific session that persists if the session can be resumed."""
    
    IN_MEMORY_SESSION_ONLY = "in_memory_session_only"
    """State tied to the current active session, lost when the session ends or the agent restarts."""
    
    SHARED = "shared"
    """State that can be accessed by other agents (with proper authorization)."""


class IAgentStateManager:
    """Interface for managing agent state persistence."""
    
    async def set_state(self, key: str, value: Any, scope: AgentStateScope = AgentStateScope.PRIVATE_PERSISTENT) -> None:
        """
        Store a value in the agent's state.
        
        Args:
            key: A string identifier for the state entry
            value: The data to be stored (must be serializable)
            scope: The visibility/lifetime scope of the state
            
        Raises:
            ValueError: If the value cannot be serialized
            StateStorageError: If there's an error with the storage backend
        """
        pass
    
    async def get_state(self, key: str, scope: AgentStateScope = AgentStateScope.PRIVATE_PERSISTENT) -> Optional[Any]:
        """
        Retrieve a value from the agent's state.
        
        Args:
            key: The identifier for the state entry to retrieve
            scope: The scope to look for the state in
            
        Returns:
            The deserialized state value, or None if not found
            
        Raises:
            StateStorageError: If there's an error with the storage backend
        """
        pass
    
    async def get_state_as_model(self, key: str, model_class: Type[T], scope: AgentStateScope = AgentStateScope.PRIVATE_PERSISTENT) -> Optional[T]:
        """
        Retrieve a value from the agent's state and convert it to a Pydantic model.
        
        Args:
            key: The identifier for the state entry to retrieve
            model_class: The Pydantic model class to convert the value to
            scope: The scope to look for the state in
            
        Returns:
            The state value converted to the specified Pydantic model, or None if not found
            
        Raises:
            ValueError: If the stored value cannot be converted to the specified model
            StateStorageError: If there's an error with the storage backend
        """
        pass
    
    async def delete_state(self, key: str, scope: AgentStateScope = AgentStateScope.PRIVATE_PERSISTENT) -> bool:
        """
        Delete a value from the agent's state.
        
        Args:
            key: The identifier for the state entry to delete
            scope: The scope to delete the state from
            
        Returns:
            True if deletion was successful or key didn't exist, False on failure
            
        Raises:
            StateStorageError: If there's an error with the storage backend
        """
        pass
    
    async def has_state(self, key: str, scope: AgentStateScope = AgentStateScope.PRIVATE_PERSISTENT) -> bool:
        """
        Check if a key exists in the agent's state.
        
        Args:
            key: The identifier to check for
            scope: The scope to check in
            
        Returns:
            True if the key exists, False otherwise
            
        Raises:
            StateStorageError: If there's an error with the storage backend
        """
        pass
    
    async def list_state_keys(self, scope: AgentStateScope = AgentStateScope.PRIVATE_PERSISTENT, prefix: Optional[str] = None) -> List[str]:
        """
        List all keys in the agent's state, optionally filtered by prefix.
        
        Args:
            scope: The scope to list keys from
            prefix: Optional prefix to filter keys by
            
        Returns:
            A list of keys in the specified scope
            
        Raises:
            StateStorageError: If there's an error with the storage backend
        """
        pass
    
    async def clear_scope(self, scope: AgentStateScope) -> None:
        """
        Clear all state entries in a specific scope.
        
        Args:
            scope: The scope to clear
            
        Raises:
            StateStorageError: If there's an error with the storage backend
        """
        pass
```

## Serialization and Supported Types

The state manager handles serialization and deserialization automatically:

1. **Primitive Types**: Basic Python types (str, int, float, bool, list, dict) are serialized directly to JSON
2. **Pydantic Models**: Automatically serialized to JSON and deserialized back to model instances
3. **Bytes Data**: Raw binary data is stored with appropriate encoding

### Handling Pydantic Models

Pydantic models are serialized to JSON and can be retrieved in two ways:

1. Using `get_state()` which returns the raw deserialized dict
2. Using `get_state_as_model()` which automatically converts the data to a specified Pydantic model

Example:

```python
# Define a Pydantic model
from pydantic import BaseModel

class UserPreferences(BaseModel):
    theme: str = "light"
    notifications_enabled: bool = True
    display_name: str = "User"

# Storing a model
prefs = UserPreferences(theme="dark", display_name="Alice")
await agent_context.state_manager.set_state("user_preferences", prefs)

# Retrieving as a dict
prefs_dict = await agent_context.state_manager.get_state("user_preferences")
# prefs_dict = {"theme": "dark", "notifications_enabled": True, "display_name": "Alice"}

# Retrieving as a model
prefs_model = await agent_context.state_manager.get_state_as_model("user_preferences", UserPreferences)
# prefs_model is a UserPreferences instance
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

The Agent State Management API defines these exceptions:

```python
class StateStorageError(Exception):
    """Base exception for state storage errors."""
    pass

class StateSerializationError(StateStorageError):
    """Exception raised when state serialization fails."""
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

1. **State Change Notifications**: Subscribe to state changes with a callback mechanism
2. **Transactional Updates**: Support for atomic multi-key operations
3. **Versioning**: Track state versions for conflict resolution
4. **Schema Evolution**: Handle schema changes gracefully for Pydantic models
5. **Query Capabilities**: More advanced querying for state entries

## Related Documentation

- [Agent Framework Overview](/refactoring_work/00b_overview/04_agents/agent_framework_overview.md)
- [Session Management](/refactoring_work/00b_overview/04_agents/session_management.md)
- [Agent Capabilities](/refactoring_work/00b_overview/04_agents/agent_capabilities.md)
