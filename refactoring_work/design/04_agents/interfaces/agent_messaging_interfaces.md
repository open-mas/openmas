# Agent Internal Messaging Interfaces

## Overview

This document defines the interfaces for the agent's internal message management system. After an incoming message is processed by an `IMessageHandler`, it is placed into the agent's `IAgentMessageInbox`. The `IAgentMessageDispatcher` is then responsible for routing these messages to the appropriate internal components, most notably the agent's `IReasoningEngine`.

## 1. `IAgentMessageInbox` Interface

The inbox acts as a thread-safe, asynchronous queue for incoming messages in the Standard Internal Message Format (SIMF).

```python
from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel
import asyncio

# Assumes InternalMessageFormat is defined elsewhere
class InternalMessageFormat(BaseModel):
    message_id: str
    payload: Dict[str, Any]
    # ... other SIMF fields

class IAgentMessageInbox(ABC):
    """An asynchronous, thread-safe inbox for an agent's internal messages."""

    @abstractmethod
    async def post_message(self, message: InternalMessageFormat) -> None:
        """Adds a message to the inbox."""
        ...

    @abstractmethod
    async def get_message(self) -> InternalMessageFormat:
        """Retrieves the next message from the inbox, blocking if empty."""
        ...

    @abstractmethod
    def is_empty(self) -> bool:
        """Returns True if the inbox is empty, False otherwise."""
        ...
```

## 2. `IAgentMessageDispatcher` Interface

The dispatcher's role is to continuously monitor the inbox and route messages to their correct destination based on the message content or metadata.

```python
# Assumes IReasoningEngine is defined elsewhere
class IReasoningEngine(ABC):
    ...

class IAgentMessageDispatcher(ABC):
    """Monitors the message inbox and dispatches messages to internal components."""

    @abstractmethod
    async def start(self, inbox: IAgentMessageInbox, reasoning_engine: IReasoningEngine) -> None:
        """Starts the dispatcher's message processing loop."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stops the dispatcher's message processing loop gracefully."""
        ...
```

## References

-   [Message Handling Interfaces](./message_handling_interfaces.md)
-   [Reasoning Engine Interfaces](../../09_knowledge_representation/reasoning/interfaces.md)
-   [Standard Internal Message Format](../internal_message_format_standard.md)
