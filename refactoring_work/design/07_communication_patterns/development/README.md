# Extending Communication Patterns

## Overview

This document provides a comprehensive guide to extending and customizing the communication patterns in OpenMAS. It covers the development process, best practices, and examples for creating custom patterns that integrate seamlessly with the framework while maintaining reasoning agnosticism.

## Development Workflow

### 1. Choose Extension Approach

There are several ways to extend the communication pattern system:

1. **Create Custom Pattern** - Develop an entirely new pattern
2. **Extend Existing Pattern** - Add functionality to an existing pattern
3. **Create Protocol Adapter** - Add protocol support to existing patterns
4. **Add Pattern Middleware** - Create processing middleware for patterns
5. **Create Pattern Composition** - Combine patterns to create complex workflows

### 2. Create Pattern Implementation

Implement your pattern by subclassing the base pattern class:

```python
from openmas.communication.patterns import BasePattern, register_pattern

@register_pattern("custom_pattern")
class CustomPattern(BasePattern):
    """A custom communication pattern."""

    def __init__(self, communicator, config):
        """Initialize with a communicator and configuration."""
        super().__init__(communicator, config)
        self.custom_option = config.get("custom_option", "default")

    async def initialize(self):
        """Initialize the pattern."""
        # Set up event handlers
        self.communicator.on_message(self._handle_message)
        self.initialized = True

    async def shutdown(self):
        """Clean up resources."""
        self.initialized = False

    async def send_message(self, recipient, content, options=None):
        """Send a message using this pattern."""
        options = options or {}

        # Create message object
        message = {
            "recipient": recipient,
            "content": content,
            "options": options,
            "pattern": "custom_pattern",
            "sender": self.communicator.agent_id
        }

        # Send message through communicator
        return await self.communicator.send_message(message)

    async def _handle_message(self, message):
        """Handle an incoming message."""
        if message.get("pattern") != "custom_pattern":
            return  # Not for this pattern

        # Process message according to pattern semantics
        return {"status": "processed"}
```

### 3. Define Protocol Adaptations

Define how your pattern adapts to different protocols:

```python
# Protocol adaptation for custom pattern
@register_protocol_adapter("custom_pattern", "a2a")
class CustomPatternA2AAdapter(ProtocolAdapter):
    """A2A adapter for custom pattern."""

    async def adapt_outgoing(self, message, pattern_options=None):
        """Adapt an outgoing message to A2A format."""
        options = pattern_options or {}

        return {
            "type": "request",
            "capability": options.get("capability_name", "custom_pattern"),
            "content": message.get("content", {}),
            "metadata": {
                "pattern": "custom_pattern",
                "sender": message.get("sender")
            }
        }

    async def adapt_incoming(self, protocol_message, pattern_options=None):
        """Adapt an incoming A2A message to the pattern format."""
        options = pattern_options or {}

        return {
            "pattern": "custom_pattern",
            "sender": protocol_message.get("metadata", {}).get("sender"),
            "content": protocol_message.get("content", {})
        }
```

### 4. Create Configuration Schema

Define a configuration schema for your pattern:

```python
# Custom pattern schema
CUSTOM_PATTERN_SCHEMA = {
    "type": "object",
    "properties": {
        "enabled": {
            "type": "boolean",
            "description": "Whether the pattern is enabled",
            "default": true
        },
        "custom_option": {
            "type": "string",
            "description": "A custom option for the pattern",
            "default": "default"
        },
        "protocol_adaptations": {
            "type": "object",
            "description": "Protocol-specific adaptations",
            "properties": {
                "a2a": {
                    "type": "object",
                    "properties": {
                        "capability_name": {
                            "type": "string",
                            "description": "Capability name for A2A",
                            "default": "custom_pattern"
                        }
                    }
                },
                "http": {
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "HTTP endpoint for the pattern",
                            "default": "/custom"
                        },
                        "method": {
                            "type": "string",
                            "description": "HTTP method",
                            "enum": ["GET", "POST", "PUT", "DELETE"],
                            "default": "POST"
                        }
                    }
                }
                # Additional protocol configurations...
            }
        }
    }
}
```

### 5. Register Your Pattern

Register your pattern with the pattern registry:

```python
from openmas.communication.patterns import PatternRegistry

# Get the registry
registry = PatternRegistry.get_instance()

# Register your pattern
registry.register("custom_pattern", CustomPattern)
```

### 6. Test Your Pattern

Create tests for your pattern:

```python
import unittest
from openmas.communication.patterns import PatternFactory

class TestCustomPattern(unittest.TestCase):
    async def setUp(self):
        """Set up the test environment."""
        # Create a communicator mock
        self.communicator = MockCommunicator()

        # Create pattern config
        self.config = {
            "custom_option": "test",
            "protocol_adaptations": {
                "a2a": {
                    "capability_name": "test_capability"
                }
            }
        }

        # Create the pattern
        factory = PatternFactory()
        self.pattern = factory.create("custom_pattern", self.communicator, self.config)
        await self.pattern.initialize()

    async def test_send_message(self):
        """Test sending a message with the pattern."""
        # Set up communicator mock
        self.communicator.send_message.return_value = {"status": "sent"}

        # Send a message
        result = await self.pattern.send_message(
            recipient="test_agent",
            content={"action": "test"},
            options={"priority": "high"}
        )

        # Check results
        self.assertEqual(result["status"], "sent")
        self.communicator.send_message.assert_called_once()

        # Check message format
        call_args = self.communicator.send_message.call_args[0][0]
        self.assertEqual(call_args["pattern"], "custom_pattern")
        self.assertEqual(call_args["recipient"], "test_agent")
        self.assertEqual(call_args["content"]["action"], "test")
```

## Pattern Type-Specific Implementation Guides

### 1. Synchronous Patterns

For patterns with request-response semantics:

```python
@register_pattern("synchronous_pattern")
class SynchronousPattern(BasePattern):
    """A synchronous communication pattern."""

    def __init__(self, communicator, config):
        """Initialize with configuration."""
        super().__init__(communicator, config)
        self.timeout = config.get("timeout", 30)
        self._pending_requests = {}

    async def send_request(self, recipient, content, options=None):
        """Send a synchronous request."""
        options = options or {}
        correlation_id = str(uuid.uuid4())

        # Create request future
        request_future = asyncio.Future()
        self._pending_requests[correlation_id] = request_future

        # Create message
        message = {
            "recipient": recipient,
            "content": content,
            "options": options,
            "pattern": "synchronous_pattern",
            "correlation_id": correlation_id,
            "sender": self.communicator.agent_id
        }

        # Send message
        await self.communicator.send_message(message)

        # Wait for response with timeout
        try:
            return await asyncio.wait_for(request_future, self.timeout)
        except asyncio.TimeoutError:
            del self._pending_requests[correlation_id]
            return {"status": "error", "error": "timeout"}

    async def _handle_message(self, message):
        """Handle an incoming message."""
        if message.get("pattern") != "synchronous_pattern":
            return  # Not for this pattern

        correlation_id = message.get("correlation_id")
        if not correlation_id:
            return  # No correlation ID

        # Check if we have a pending request
        future = self._pending_requests.get(correlation_id)
        if future and not future.done():
            # Resolve the future with the response
            future.set_result({
                "status": "success",
                "content": message.get("content", {})
            })
            # Clean up
            del self._pending_requests[correlation_id]
```

### 2. Asynchronous Patterns

For patterns with fire-and-forget semantics:

```python
@register_pattern("async_pattern")
class AsyncPattern(BasePattern):
    """An asynchronous communication pattern."""

    def __init__(self, communicator, config):
        """Initialize with configuration."""
        super().__init__(communicator, config)
        self._handlers = {}

    async def send_notification(self, recipients, notification_type, content):
        """Send an asynchronous notification."""
        if isinstance(recipients, str):
            recipients = [recipients]

        # Create notification message
        base_message = {
            "content": content,
            "pattern": "async_pattern",
            "notification_type": notification_type,
            "sender": self.communicator.agent_id,
            "timestamp": time.time()
        }

        # Send to all recipients
        results = []
        for recipient in recipients:
            message = {**base_message, "recipient": recipient}
            result = await self.communicator.send_message(message)
            results.append(result)

        return results

    async def register_handler(self, notification_type, handler):
        """Register a handler for a notification type."""
        self._handlers[notification_type] = handler

    async def _handle_message(self, message):
        """Handle an incoming message."""
        if message.get("pattern") != "async_pattern":
            return  # Not for this pattern

        notification_type = message.get("notification_type")
        if not notification_type:
            return  # No notification type

        # Find and call the appropriate handler
        handler = self._handlers.get(notification_type)
        if handler:
            return await handler(message)
```

### 3. Streaming Patterns

For patterns with streaming semantics:

```python
@register_pattern("streaming_pattern")
class StreamingPattern(BasePattern):
    """A streaming communication pattern."""

    def __init__(self, communicator, config):
        """Initialize with configuration."""
        super().__init__(communicator, config)
        self.batch_size = config.get("batch_size", 100)
        self._streams = {}
        self._stream_producers = {}

    async def create_stream(self, target, stream_id=None, options=None):
        """Create a new stream."""
        options = options or {}
        stream_id = stream_id or str(uuid.uuid4())

        # Create stream object
        stream = Stream(self, stream_id, target, options)
        self._streams[stream_id] = stream

        # Initialize the stream
        await stream.initialize()

        return stream

    async def provide_stream(self, stream_id, producer_func):
        """Register a stream producer."""
        self._stream_producers[stream_id] = producer_func

    async def _handle_message(self, message):
        """Handle an incoming message."""
        if message.get("pattern") != "streaming_pattern":
            return  # Not for this pattern

        stream_id = message.get("stream_id")
        if not stream_id:
            return  # No stream ID

        message_type = message.get("type")

        if message_type == "stream_request":
            # Handle stream request
            producer = self._stream_producers.get(stream_id)
            if producer:
                # Create response stream
                stream = await self.create_stream(
                    target=message.get("sender"),
                    stream_id=f"response_{stream_id}"
                )

                # Start producer
                asyncio.create_task(producer(message, stream))

                return {"status": "stream_started"}

        elif message_type == "stream_data":
            # Handle incoming stream data
            stream = self._streams.get(stream_id)
            if stream:
                await stream._receive_data(message.get("content"))
```

## Protocol Adapter Implementation

Create adapters for protocol-specific behavior:

### HTTP Protocol Adapter

```python
@register_protocol_adapter("request_response", "http")
class RequestResponseHTTPAdapter(ProtocolAdapter):
    """HTTP adapter for request-response pattern."""

    async def adapt_outgoing(self, message, pattern_options=None):
        """Adapt an outgoing message to HTTP format."""
        options = pattern_options or {}

        # Determine HTTP method
        method = options.get("method", "POST")

        # Construct URL
        base_url = options.get("base_url", "")
        endpoint = options.get("endpoint", "/request")
        url = f"{base_url}{endpoint}"

        # Replace URL parameters if present
        if "{recipient}" in url:
            url = url.replace("{recipient}", message.get("recipient", ""))

        # Construct HTTP request
        http_request = {
            "method": method,
            "url": url,
            "headers": {
                "Content-Type": "application/json",
                "X-Correlation-ID": message.get("correlation_id", ""),
                "X-Sender": message.get("sender", "")
            },
            "body": message.get("content", {})
        }

        return http_request

    async def adapt_incoming(self, protocol_message, pattern_options=None):
        """Adapt an incoming HTTP message to the pattern format."""
        options = pattern_options or {}

        # Extract correlation ID from headers
        headers = protocol_message.get("headers", {})
        correlation_id = headers.get("X-Correlation-ID", "")
        sender = headers.get("X-Sender", "")

        # Construct pattern message
        message = {
            "pattern": "request_response",
            "content": protocol_message.get("body", {}),
            "correlation_id": correlation_id,
            "sender": sender,
            "status": "success" if 200 <= protocol_message.get("status_code", 0) < 300 else "error"
        }

        return message
```

### MQTT Protocol Adapter

```python
@register_protocol_adapter("publish_subscribe", "mqtt")
class PublishSubscribeMQTTAdapter(ProtocolAdapter):
    """MQTT adapter for publish-subscribe pattern."""

    async def adapt_outgoing(self, message, pattern_options=None):
        """Adapt an outgoing message to MQTT format."""
        options = pattern_options or {}

        # Determine topic
        topic_prefix = options.get("topic_prefix", "")
        topic = message.get("topic", "")

        if topic_prefix and not topic.startswith(topic_prefix):
            full_topic = f"{topic_prefix}/{topic}"
        else:
            full_topic = topic

        # Construct MQTT message
        mqtt_message = {
            "topic": full_topic,
            "payload": message.get("message", {}),
            "qos": options.get("qos", 0),
            "retain": options.get("retain", False)
        }

        return mqtt_message

    async def adapt_incoming(self, protocol_message, pattern_options=None):
        """Adapt an incoming MQTT message to the pattern format."""
        options = pattern_options or {}

        # Extract topic
        topic = protocol_message.get("topic", "")
        topic_prefix = options.get("topic_prefix", "")

        if topic_prefix and topic.startswith(topic_prefix):
            topic = topic[len(topic_prefix):].lstrip("/")

        # Construct pattern message
        message = {
            "pattern": "publish_subscribe",
            "topic": topic,
            "message": protocol_message.get("payload", {})
        }

        return message
```

## Pattern Middleware

Create middleware to process messages:

```python
class LoggingMiddleware:
    """Middleware for logging pattern messages."""

    def __init__(self, log_level="info"):
        """Initialize with log level."""
        self.log_level = log_level

    async def process_outgoing(self, message, pattern, next_middleware):
        """Process an outgoing message."""
        # Log outgoing message
        logger.log(
            self.log_level,
            f"Outgoing {pattern} message to {message.get('recipient')}: {message}"
        )

        # Pass to next middleware
        return await next_middleware(message)

    async def process_incoming(self, message, pattern, next_middleware):
        """Process an incoming message."""
        # Log incoming message
        logger.log(
            self.log_level,
            f"Incoming {pattern} message from {message.get('sender')}: {message}"
        )

        # Pass to next middleware
        return await next_middleware(message)
```

## Pattern Composition

Compose patterns to create complex workflows:

```python
class PatternPipeline:
    """Pipeline of communication patterns."""

    def __init__(self, patterns):
        """Initialize with a list of patterns."""
        self.patterns = patterns

    async def execute(self, initial_input):
        """Execute the pattern pipeline."""
        current_input = initial_input

        for pattern, step_config in self.patterns:
            # Transform input if needed
            if "input_transform" in step_config:
                transform_func = step_config["input_transform"]
                step_input = transform_func(current_input)
            else:
                step_input = current_input

            # Determine pattern method
            method_name = step_config.get("method", "send")
            pattern_method = getattr(pattern, method_name)

            # Execute pattern
            step_result = await pattern_method(
                **step_config.get("params", {}),
                **step_input
            )

            # Transform output if needed
            if "output_transform" in step_config:
                transform_func = step_config["output_transform"]
                current_input = transform_func(step_result)
            else:
                current_input = step_result

        return current_input
```

## Pattern Factory

Create a factory for instantiating patterns:

```python
class PatternFactory:
    """Factory for creating pattern instances."""

    def __init__(self, registry=None, communicator_factory=None):
        """Initialize the factory."""
        self.registry = registry or PatternRegistry.get_instance()
        self.communicator_factory = communicator_factory

    def create(self, pattern_name, communicator=None, config=None):
        """Create a pattern instance."""
        config = config or {}

        # Get pattern class
        pattern_class = self.registry.get(pattern_name)
        if not pattern_class:
            raise ValueError(f"Unknown pattern: {pattern_name}")

        # Create communicator if needed
        if not communicator and self.communicator_factory:
            protocol = config.get("protocol", "a2a")
            communicator = self.communicator_factory.create(
                protocol,
                config.get("protocol_config", {})
            )

        # Create and return the pattern
        return pattern_class(communicator, config)
```

## Configuration Examples

### Complex Pattern Configuration

```yaml
communication_patterns:
  # Define a complex request-response pattern
  request_response:
    enabled: true
    version: "1.2.0"
    timeout: 30
    retry:
      attempts: 3
      interval: 5
    middleware:
      - logging:
          log_level: "info"
      - metrics:
          track_latency: true
    protocol_adaptations:
      a2a:
        capability_name: "request_response"
        response_capability: "response"
      http:
        method: "POST"
        endpoint: "/api/request/{recipient}"
        response_codes: [200, 201]
      mqtt:
        request_topic: "requests/{agent_id}"
        response_topic: "responses/{agent_id}"
        qos: 1
```

### Pattern Pipeline Configuration

```yaml
communication_pipelines:
  data_processing:
    enabled: true
    steps:
      - pattern: "request_response"
        target: "data_collector"
        method: "send_request"
        params:
          content:
            action: "collect_data"
            source: "database"

      - pattern: "delegation"
        target: "data_processor"
        method: "delegate"
        input_transform: "transform_to_processing_task"

      - pattern: "streaming"
        target: "data_analyzer"
        method: "create_stream"
        input_transform: "setup_analysis_stream"
```

## Pattern Usage Examples

### Custom Pattern Example

```python
# Creating a custom pattern
custom_pattern = factory.create(
    "custom_pattern",
    communicator,
    {
        "custom_option": "value",
        "protocol_adaptations": {
            "a2a": {"capability_name": "custom_capability"}
        }
    }
)

# Initialize the pattern
await custom_pattern.initialize()

# Use the pattern
result = await custom_pattern.send_message(
    recipient="target_agent",
    content={"action": "custom_action", "data": {...}},
    options={"priority": "high"}
)
```

### Pattern Pipeline Example

```python
# Create patterns for the pipeline
request_pattern = factory.create("request_response", communicator, config1)
delegation_pattern = factory.create("delegation", communicator, config2)
streaming_pattern = factory.create("streaming", communicator, config3)

# Define transformations
def transform_to_processing_task(result):
    """Transform collection result to processing task."""
    return {
        "task": {
            "type": "process_data",
            "data": result["content"]["data"]
        }
    }

def setup_analysis_stream(result):
    """Set up streaming analysis."""
    return {
        "stream_config": {
            "data_type": "processed_data",
            "task_id": result["task_id"]
        }
    }

# Create the pipeline
pipeline = PatternPipeline([
    (request_pattern, {
        "method": "send_request",
        "params": {
            "recipient": "data_collector",
            "content": {"action": "collect_data", "source": "database"}
        }
    }),
    (delegation_pattern, {
        "method": "delegate",
        "input_transform": transform_to_processing_task
    }),
    (streaming_pattern, {
        "method": "create_stream",
        "input_transform": setup_analysis_stream
    })
])

# Execute the pipeline
result = await pipeline.execute({})
```

## Best Practices

1. **Pattern Semantics** - Clearly define the semantics of your pattern
2. **Protocol Independence** - Ensure your pattern works with all protocols
3. **Error Handling** - Implement robust error handling and recovery
4. **Configuration Flexibility** - Use configuration-driven behavior
5. **Protocol Adapters** - Create adapters for all supported protocols
6. **Testing** - Thoroughly test patterns with different protocols
7. **Documentation** - Document pattern semantics, options, and examples
8. **Versioning** - Follow versioning guidelines for pattern evolution
9. **Performance** - Optimize patterns for efficiency
10. **Composability** - Design patterns to work well in compositions

## Reasoning Agnosticism

When developing custom patterns, maintain OpenMAS's reasoning agnosticism by:

1. **Semantic Focus** - Patterns should define semantics, not reasoning logic
2. **Protocol Independence** - Patterns should work with any protocol
3. **Content Agnosticism** - Patterns shouldn't interpret message content
4. **Abstract Interfaces** - Patterns should expose abstract interfaces
5. **Event-Based Interfaces** - Patterns should use event-based programming model

This enables agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to communicate using your patterns consistently.
