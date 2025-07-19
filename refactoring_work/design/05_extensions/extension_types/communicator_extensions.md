# Communicator Extensions

## Overview

Communicator Extensions provide a mechanism to add support for new communication protocols, transports, and connection management features to OpenMAS. They allow developers to extend the communication capabilities of agents while maintaining the framework's reasoning agnosticism.

## Base Class

Communicator Extensions must inherit from the `CommunicatorExtension` base class:

```python
from openmas.extensions import CommunicatorExtension

class MyCommunicatorExtension(CommunicatorExtension):
    """A custom communicator extension."""
```

## Required Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `create_communicator(agent_config)` | Create a communicator instance for an agent | `agent_config`: Agent configuration dictionary | Communicator instance |

## Optional Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `validate_config()` | Validate the extension configuration | None | None, raises exception if invalid |
| `initialize()` | Initialize the extension | None | None |
| `get_supported_protocols()` | Get list of protocols supported by this extension | None | List of protocol identifiers |
| `pre_message_send(communicator, message)` | Called before a message is sent | `communicator`: The communicator instance<br>`message`: The outgoing message | Modified message or original |
| `post_message_receive(communicator, message)` | Called after a message is received | `communicator`: The communicator instance<br>`message`: The incoming message | Modified message or original |

## Configuration Schema

Communicator Extensions are configured in the unified configuration schema under the `extensions` section with `type: "communicator"`:

```yaml
extensions:
  my_communicator_extension:
    type: "communicator"
    name: "my_communicator_extension"
    enabled: true
    options:
      protocols:
        - "custom_protocol"
      transport:
        type: "websocket"
        config:
          timeout_ms: 5000
          reconnect: true
      # Additional configuration specific to this extension
```

### Options Schema

The `options` block for Communicator Extensions supports the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `protocols` | array | Yes | List of protocol identifiers this extension supports |
| `transport` | object | Yes | Transport configuration |
| `transport.type` | string | Yes | Transport type (e.g., "websocket", "http", "mqtt") |
| `transport.config` | object | No | Transport-specific configuration |
| `connection_retry` | object | No | Connection retry configuration |
| `serialization` | object | No | Message serialization configuration |

For the complete schema definition, refer to the [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md#communicator-extension-options).

## Interaction Model

Communicator Extensions interact with the OpenMAS Communicator Framework through the following mechanisms:

1. **Registration**: The extension is registered with the extension registry
2. **Discovery**: The agent framework discovers available communicator extensions
3. **Creation**: When an agent needs a communicator for a specific protocol, it calls the appropriate extension
4. **Communication**: The created communicator handles the actual message transport
5. **Messaging Hooks**: The extension can intercept and modify messages before sending and after receiving

The Communicator Framework maintains control over the communicator lifecycle, while the extension provides the implementation for specific protocols.

## Code Example

Here's a minimal example of a Communicator Extension that adds WebSocket support:

```python
from openmas.extensions import CommunicatorExtension
from openmas.communicator import BaseCommunicator
import websockets
import asyncio
import json

class WebSocketCommunicator(BaseCommunicator):
    """WebSocket communicator implementation."""
    
    def __init__(self, config):
        super().__init__(config)
        self.uri = config.get("uri", "ws://localhost:8765")
        self.connection = None
        self.connected = False
        self.message_queue = asyncio.Queue()
        self.receive_task = None
    
    async def connect(self):
        """Connect to the WebSocket server."""
        try:
            self.connection = await websockets.connect(self.uri)
            self.connected = True
            self.receive_task = asyncio.create_task(self._receive_loop())
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.connection:
            await self.connection.close()
            self.connected = False
            if self.receive_task:
                self.receive_task.cancel()
        return True
    
    async def send_message(self, message):
        """Send a message to the WebSocket server."""
        if not self.connected:
            await self.connect()
        
        try:
            await self.connection.send(json.dumps(message.to_dict()))
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    async def receive_message(self):
        """Receive a message from the queue."""
        return await self.message_queue.get()
    
    async def _receive_loop(self):
        """Background task to receive messages."""
        while self.connected:
            try:
                raw_message = await self.connection.recv()
                message_dict = json.loads(raw_message)
                message = self.message_class.from_dict(message_dict)
                await self.message_queue.put(message)
            except Exception as e:
                if self.connected:  # Only log if still supposed to be connected
                    self.logger.error(f"Error receiving message: {e}")
                    await asyncio.sleep(1)  # Avoid tight loop on error

class WebSocketCommunicatorExtension(CommunicatorExtension):
    """Extension that adds WebSocket communication support."""
    
    extension_type = "communicator"
    extension_name = "websocket"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.protocols = config.get("options", {}).get("protocols", ["websocket"])
    
    def validate_config(self):
        """Validate the extension configuration."""
        options = self.config.get("options", {})
        if "protocols" not in options:
            raise ValueError("WebSocket communicator extension requires 'protocols' in options")
    
    def get_supported_protocols(self):
        """Get list of supported protocols."""
        return self.protocols
    
    def create_communicator(self, agent_config):
        """Create a WebSocket communicator instance."""
        # Extract WebSocket-specific configuration
        communicator_config = agent_config.get("communicator", {})
        websocket_config = communicator_config.get("websocket", {})
        
        # Create communicator instance
        return WebSocketCommunicator(websocket_config)
    
    def pre_message_send(self, communicator, message):
        """Called before a message is sent."""
        # Add a timestamp if not present
        if "timestamp" not in message.metadata:
            message.metadata["timestamp"] = datetime.datetime.now().isoformat()
        return message
```

### Configuration Example

```yaml
extensions:
  websocket:
    type: "communicator"
    name: "websocket"
    enabled: true
    options:
      protocols:
        - "websocket"
      transport:
        type: "websocket"
        config:
          timeout_ms: 5000
          reconnect: true
```

## Best Practices

1. **Protocol Independence**: Clearly document which protocols the extension supports
2. **Graceful Fallbacks**: Provide graceful fallbacks for connection failures
3. **Security Considerations**: Implement appropriate security measures for the protocol
4. **Message Validation**: Validate incoming and outgoing messages
5. **Performance Optimization**: Optimize for high-throughput scenarios
6. **Reasoning Agnosticism**: Maintain the separation between communication and reasoning

## Related Documentation

- [Extension System Design](../design/design_extension_system.md)
- [Communicator Framework Design](../../04_communicator/design_communicator_framework.md)
- [Extension Development Guide](../development/guide.md)
- [Protocol Documentation](../../02_protocols/README.md)
