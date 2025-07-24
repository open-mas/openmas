# ICommunicationPatternExtension Interface

## 1. Overview

The `ICommunicationPatternExtension` interface is a specialized extension point that allows developers to add new, reusable communication patterns to the OpenMAS framework. While the core framework provides standard patterns like Request-Response and Publish-Subscribe, this extension point allows for the creation of more complex or domain-specific interaction protocols (e.g., Contract Net, Dutch Auction).

An extension implementing this interface provides the logic for a new pattern, which can then be registered with the `IPatternEngine` and used by agents via the `ICommunicationManager`.

## 2. Interface Definition

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any

# Assumes the core IPatternInstance interface is defined and available
# from ...07_communication_patterns/pattern_engine_api import IPatternInstance, PatternDefinition

class ICommunicationPatternExtension(ABC):
    """The interface for an extension that provides a new communication pattern."""

    @abstractmethod
    def get_pattern_definition(self) -> PatternDefinition:
        """Returns the definition of the pattern, including its name, description,
        and configuration schema.

        Returns:
            A PatternDefinition object.
        """
        pass

    @abstractmethod
    def create_pattern_instance(self, config: Dict[str, Any]) -> IPatternInstance:
        """Creates an instance of the communication pattern.

        Args:
            config: The configuration for this specific instance of the pattern.

        Returns:
            An object that implements the IPatternInstance interface.
        """
        pass
```

## 3. How It's Used

1.  The `IExtensionManager` loads an extension that implements `IExtension`.
2.  During its `load()` method, the extension registers its `ICommunicationPatternExtension` implementation with the `IPatternEngine`.
3.  The `IPatternEngine` calls `get_pattern_definition()` to understand the new pattern and its configuration requirements.
4.  When an agent wants to use the pattern (e.g., via the `ICommunicationManager`), the `IPatternEngine` calls `create_pattern_instance()` on the extension to get a stateful object that will manage that specific interaction.
