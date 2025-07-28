# Agent Capability Manager Interface

## 1. Overview

The `ICapabilityManager` interface defines the formal contract for managing an agent's capabilities. It provides a standardized set of methods for registering, discovering, and invoking capabilities, ensuring consistency and interoperability across the OpenMAS framework. This manager is a key component of the agent's internal architecture.

## 2. ICapabilityManager Interface Definition

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Coroutine, Callable

class ICapabilityManager(ABC):
    """
    Manages the registration, discovery, and invocation of agent capabilities.

    This interface abstracts the underlying mechanisms for handling an agent's
    abilities, providing a consistent way to interact with them regardless of
    the protocol or reasoning engine in use.
    """

    @abstractmethod
    async def register_capability(
        self,
        core_capability_id: str,
        handler: Callable[..., Coroutine[Any, Any, Any]],
        reasoning_approach: str = "default"
    ) -> None:
        """
        Registers a handler function for a specific capability.

        Args:
            core_capability_id: The unique identifier for the core capability,
                                as defined in the agent's configuration.
            handler: The async function that implements the capability's logic.
            reasoning_approach: The reasoning approach this handler is associated with.
                                Allows for different implementations of the same
                                capability (e.g., 'llm', 'rule_based').
        """
        pass

    @abstractmethod
    async def get_capability_schema(self, core_capability_id: str) -> Dict[str, Any]:
        """
        Retrieves the declarative schema for a given capability.

        Args:
            core_capability_id: The unique identifier for the core capability.

        Returns:
            A dictionary representing the JSON schema of the capability, including
            parameters, return values, and description.
        """
        pass

    @abstractmethod
    async def list_capabilities(self) -> List[Dict[str, Any]]:
        """
        Lists all registered capabilities for the agent.

        Returns:
            A list of dictionaries, where each dictionary contains the schema
            for a registered capability.
        """
        pass

    @abstractmethod
    async def has_capability(self, core_capability_id: str) -> bool:
        """
        Checks if a specific capability is registered with the manager.

        Args:
            core_capability_id: The unique identifier for the core capability.

        Returns:
            True if the capability is registered, False otherwise.
        """
        pass

    @abstractmethod
    async def invoke_capability(
        self,
        core_capability_id: str,
        reasoning_approach: str,
        **kwargs: Any
    ) -> Any:
        """
        Invokes a registered capability with the given parameters.

        The manager will select the appropriate handler based on the agent's
        current reasoning approach.

        Args:
            core_capability_id: The unique identifier for the capability to invoke.
            reasoning_approach: The reasoning approach to use for selecting the handler.
            **kwargs: The parameters to pass to the capability handler.

        Returns:
            The result of the capability's execution.

        Raises:
            CapabilityNotFoundError: If the capability is not registered.
            InvalidParametersError: If the provided kwargs do not match the
                                    capability's schema.
        """
        pass
```

## 3. Decorator for Registration

To simplify the registration process, a decorator can be provided that utilizes the `ICapabilityManager`.

```python
import functools

def capability_handler(core_capability_id: str, reasoning_approach: str = "default"):
    """
    A decorator to register a method as a capability handler.

    This decorator should be used on methods within an Agent class. It registers
    the decorated method with the agent's capability manager during initialization.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(agent, *args, **kwargs):
            # The registration logic would be handled by the agent's setup process,
            # which inspects the class for this decorator.
            return await func(agent, *args, **kwargs)

        # Attach metadata to the function for the agent's setup process to find.
        wrapper._is_capability_handler = True
        wrapper._core_capability_id = core_capability_id
        wrapper._reasoning_approach = reasoning_approach
        return wrapper
    return decorator
```
