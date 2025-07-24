# IProtocolExtension Interface

## 1. Overview

The `IProtocolExtension` interface is a specialized extension point that allows developers to add support for new communication protocols to OpenMAS. An extension that implements this interface is responsible for providing the necessary components to integrate a new protocol into the framework's `Protocol Layer`.

This interface acts as a factory for the protocol-specific components defined in the core protocol layer documentation, namely:
- `IMessageTransport`: Handles the low-level sending and receiving of data.
- `IConnectionManager`: Manages the lifecycle of connections.
- `IProtocolAdapter`: Translates between the protocol's native format and the Standard Internal Message Format (SIMF).

## 2. Interface Definition

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any

# Assumes core protocol interfaces are defined and available
# from ...02_protocols.iprotocol_adapter_interface import IProtocolAdapter, IConnectionManager, IMessageTransport

class IProtocolExtension(ABC):
    """The interface for an extension that provides a new communication protocol."""

    @abstractmethod
    def get_protocol_name(self) -> str:
        """Returns the unique, machine-readable name for the protocol (e.g., 'websocket')."""
        pass

    @abstractmethod
    def create_transport(self, config: Dict[str, Any]) -> IMessageTransport:
        """Creates an instance of the message transport for this protocol.

        Args:
            config: The configuration for the transport layer.

        Returns:
            An object that implements the IMessageTransport interface.
        """
        pass

    @abstractmethod
    def create_connection_manager(self, config: Dict[str, Any]) -> IConnectionManager:
        """Creates an instance of the connection manager for this protocol.

        Args:
            config: The configuration for the connection manager.

        Returns:
            An object that implements the IConnectionManager interface.
        """
        pass

    @abstractmethod
    def create_protocol_adapter(self, config: Dict[str, Any]) -> IProtocolAdapter:
        """Creates an instance of the protocol adapter.

        Args:
            config: The configuration for the protocol adapter.

        Returns:
            An object that implements the IProtocolAdapter interface.
        """
        pass
```

## 3. How It's Used

1.  The `IExtensionManager` loads an extension that implements `IExtension`.
2.  During its `load()` method, the extension also registers its `IProtocolExtension` implementation with a central `ProtocolRegistry`.
3.  When the framework needs to configure a communicator for an agent using this protocol, it queries the `ProtocolRegistry`.
4.  It then uses the methods on the `IProtocolExtension` object to construct the full protocol stack (transport, connection manager, and adapter) for that agent.
