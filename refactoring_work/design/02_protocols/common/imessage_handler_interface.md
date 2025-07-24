# IMessageHandler Interface

## Overview

The `IMessageHandler` interface defines a standardized contract for components within the OpenMAS Agent Framework that are responsible for processing incoming messages. Its primary role is to decouple protocol adapters from the internal message processing logic. Protocol adapters are responsible for receiving raw messages from a specific protocol, translating them into the `InternalMessageFormat`, and then passing them to an `IMessageHandler` for further processing.

This separation of concerns ensures that the core agent logic remains protocol-agnostic and that protocol adapters can be developed and tested independently.

## Interface Definition

```python
from abc import ABC, abstractmethod

# The InternalMessageFormat is defined in the architecture models.
# from openmas.models import InternalMessageFormat

class IMessageHandler(ABC):
    """
    Defines the contract for handling incoming messages that have been
    translated into the standard internal format.
    """

    @abstractmethod
    async def handle_message(self, internal_message: 'InternalMessageFormat') -> None:
        """
        Processes a single incoming message.

        This method is the designated entry point for messages that have been
        received and translated by a protocol adapter. Implementations of this
        method will contain the logic for routing the message to the
        appropriate agent, service, or component within the framework.

        Args:
            internal_message: The message in the Standard Internal Message Format.

        Raises:
            Exception: Implementations may raise exceptions for handling errors
                       during message processing.
        """
        pass
```

## Example Usage

A protocol adapter would use an `IMessageHandler` as follows:

```python
# In a hypothetical protocol adapter...

class SomeProtocolAdapter(IProtocolAdapter):
    def __init__(self, message_handler: IMessageHandler):
        self._message_handler = message_handler
        # ... other initializations

    async def _on_raw_message_received(self, raw_message: Any):
        # 1. Translate the raw message to the internal format
        internal_message = self.to_internal_format(raw_message)

        # 2. Pass the translated message to the handler
        await self._message_handler.handle_message(internal_message)

```
