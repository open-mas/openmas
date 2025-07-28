# Programmatic Capability Implementation

## 1. Overview

While the declarative definition specifies a capability's interface, the programmatic implementation provides its logic. This is done by writing a Python method within an agent's class and registering it as a handler for a specific capability ID.

This registration process links the abstract definition in the YAML configuration to a concrete piece of executable code.

## 2. The Capability Handler

A capability handler is an `async` method within an agent class that contains the business logic for the capability. Its signature must match the parameters defined in the capability's declarative schema.

## 3. Registering a Handler

There are two primary ways to register a handler with the agent's `ICapabilityManager`:

1.  **Direct Registration**: Explicitly calling the `register_capability` method on the agent's capability manager instance.
2.  **Decorator-Based Registration**: Using the `@capability_handler` decorator for a more concise and declarative style.

### Method 1: Direct Registration

In this approach, you typically call `register_capability` within the agent's `setup` method or another initialization hook.

**Example:**

```python
from openmas.agent import Agent

class WeatherAgent(Agent):
    async def setup(self):
        """Initializes the agent and registers its capabilities."""
        await super().setup()
        await self.capability_manager.register_capability(
            core_capability_id="get_weather",  # Must match the ID in the YAML config
            handler=self.get_weather_logic
        )

    async def get_weather_logic(self, location: str) -> dict:
        """
        The actual implementation of the 'get_weather' capability.

        Args:
            location: The location provided by the caller.

        Returns:
            A dictionary with weather information.
        """
        # In a real implementation, this would call a weather service.
        print(f"Fetching weather for {location}...")
        return {
            "temperature": 25.5,
            "conditions": "Sunny"
        }
```

### Method 2: Using the `@capability_handler` Decorator

The `@capability_handler` decorator provides a more elegant and readable way to register handlers. The agent's framework will automatically discover and register any methods marked with this decorator during initialization.

**Example:**

```python
from openmas.agent import Agent
from openmas.capabilities import capability_handler

class WeatherAgent(Agent):

    @capability_handler(core_capability_id="get_weather")
    async def get_weather_logic(self, location: str) -> dict:
        """
        The actual implementation of the 'get_weather' capability.
        This handler is registered automatically via its decorator.
        """
        # In a real implementation, this would call a weather service.
        print(f"Fetching weather for {location}...")
        return {
            "temperature": 25.5,
            "conditions": "Sunny"
        }
```

This approach is generally preferred as it keeps the capability's definition and implementation logic co-located.
