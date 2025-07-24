# Message Handling Interfaces

## Overview

This document defines the interfaces for handling incoming messages within the OpenMAS Agent Framework. Once a `IProtocolAdapter` translates a protocol-specific message into the Standard Internal Message Format (SIMF), the message is passed to an `IMessageHandler` for processing.

This design includes hooks for pre-processing and post-processing, allowing for modular and extensible message handling pipelines.

## 1. `IMessageHandler` Interface

The `IMessageHandler` is the central component for processing incoming SIMF messages. It orchestrates the flow of a message through any registered hooks and ultimately dispatches it to the appropriate component, such as a reasoning engine.

```python
from abc import ABC, abstractmethod
from typing import Any, List, Dict
from pydantic import BaseModel

# Assumes InternalMessageFormat is defined elsewhere
class InternalMessageFormat(BaseModel):
    message_id: str
    payload: Dict[str, Any]
    # ... other SIMF fields

class HandlingResult(BaseModel):
    """Represents the outcome of a message handling operation."""
    success: bool
    details: str
    actions_taken: List[Any] = []

class IPreProcessingHook(ABC):
    """Interface for a pre-processing hook to be run before the main handler."""
    @abstractmethod
    async def preprocess(self, message: InternalMessageFormat) -> InternalMessageFormat:
        """Processes or transforms a message before it is handled.

        Args:
            message: The incoming message.

        Returns:
            The processed or transformed message.
        """
        ...

class IPostProcessingHook(ABC):
    """Interface for a post-processing hook to be run after the main handler."""
    @abstractmethod
    async def postprocess(self, result: HandlingResult) -> None:
        """Performs actions after a message has been handled, e.g., logging.

        Args:
            result: The result of the handling operation.
        """
        ...

class IMessageHandler(ABC):
    """Interface for handling an incoming internal message."""

    @abstractmethod
    async def handle_message(self, message: InternalMessageFormat) -> HandlingResult:
        """Handles a single message, running it through the pre- and post-processing hooks.

        Args:
            message: The message to be handled, in SIMF.

        Returns:
            A result object summarizing the outcome.
        """
        ...

    @abstractmethod
    def register_pre_hook(self, hook: IPreProcessingHook) -> None:
        """Registers a pre-processing hook."""
        ...

    @abstractmethod
    def register_post_hook(self, hook: IPostProcessingHook) -> None:
        """Registers a post-processing hook."""
        ...
```

## References

-   [Standard Internal Message Format](../internal_message_format_standard.md)
-   [Protocol Layer Interfaces](../../02_protocols/iprotocol_adapter_interface.md)
-   [Agent Framework and Protocol Layer Integration](../agent_framework_protocol_layer.md)
