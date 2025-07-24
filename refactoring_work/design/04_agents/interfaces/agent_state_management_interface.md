# IAgentState Interface

## 1. Overview

The `IAgentState` interface provides a standardized contract for managing an agent's internal state. It is designed to be a flexible, key-value store that supports data persistence, atomic operations, and a publish-subscribe mechanism for state changes. This allows different components within the agent to access and react to state modifications in a consistent and decoupled manner.

The key responsibilities of an `IAgentState` implementation are:

-   **State Storage**: Persistently store and retrieve key-value data.
-   **Concurrency Control**: Ensure that state modifications are handled safely in a concurrent environment.
-   **State Notifications**: Allow components to subscribe to changes in specific parts of the state.

## 2. Interface Definition

The interface is defined using Python's `abc` module to establish a formal contract. It uses type hints for clarity and supports asynchronous operations.

```python
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Dict, Optional

# Type alias for a callback function that is subscribed to state changes.
# The callback receives the new value of the state key it's subscribed to.
StateChangeCallback = Callable[[Any], Coroutine[Any, Any, None]]

class IAgentState(ABC):
    """
    An interface for managing an agent's internal state.

    Provides asynchronous, thread-safe methods for getting, setting, and deleting
    state variables, as well as a subscription mechanism for state changes.
    """

    @abstractmethod
    async def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieves a value from the state by its key.

        Args:
            key: The unique identifier for the state variable.
            default: The value to return if the key is not found.

        Returns:
            The value associated with the key, or the default value if not found.
        """
        ...

    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        """
        Sets or updates a value in the state.

        If the value for the key changes, this method is responsible for triggering
        any registered callbacks.

        Args:
            key: The unique identifier for the state variable.
            value: The new value to store. Must be serializable.

        Raises:
            StateSerializationError: If the provided value cannot be serialized.
        """
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Deletes a key-value pair from the state.

        Args:
            key: The unique identifier for the state variable to delete.

        Returns:
            True if the key was found and deleted, False otherwise.
        """
        ...

    @abstractmethod
    async def get_all(self) -> Dict[str, Any]:
        """
        Retrieves a copy of the entire agent state.

        Returns:
            A dictionary representing the complete state.
        """
        ...

    @abstractmethod
    async def subscribe(self, key: str, callback: StateChangeCallback) -> None:
        """
        Subscribes a callback function to changes for a specific state key.

        Args:
            key: The key of the state variable to monitor.
            callback: The asynchronous function to call when the value changes.

        Raises:
            KeyNotFoundError: If the key does not exist in the state schema (if one is enforced).
        """
        ...

    @abstractmethod
    async def unsubscribe(self, key: str, callback: StateChangeCallback) -> None:
        """
        Unsubscribes a callback function from a specific state key.

        Args:
            key: The key of the state variable to stop monitoring.
            callback: The callback function to remove.
        """
        ...

    @abstractmethod
    async def load(self) -> None:
        """
        Loads the agent's state from a persistent storage backend (e.g., file, database).
        This is typically called during agent initialization.
        """
        ...

    @abstractmethod
    async def save(self) -> None:
        """
        Saves the current state to the persistent storage backend.
        This can be called periodically or on agent shutdown.
        """
        ...

```

## 3. Custom Exceptions

Implementations of this interface should define and raise specific exceptions to handle error conditions gracefully.

-   `StateSerializationError`: Raised when a value passed to `set()` cannot be serialized by the storage backend.
-   `KeyNotFoundError`: Raised when `subscribe()` is called on a key that is not part of a predefined state schema.

## 4. Example Usage

```python
import asyncio

# Assume 'agent_state' is a concrete implementation of IAgentState

async def on_status_change(new_status: str):
    print(f"Agent status changed to: {new_status}")

async def main():
    # agent_state = MyAgentStateImplementation()
    # await agent_state.load() # Load state from disk

    # Subscribe to a state change
    await agent_state.subscribe("status", on_status_change)

    # Set an initial value, which triggers the callback
    await agent_state.set("status", "initializing")

    # Update the value, which triggers the callback again
    await agent_state.set("status", "running")

    # Get a value
    current_task = await agent_state.get("current_task", default="idle")
    print(f"Current task is: {current_task}")

    # Unsubscribe
    await agent_state.unsubscribe("status", on_status_change)

    # Save state before shutdown
    await agent_state.save()

# asyncio.run(main())
```
