# Publish-Subscribe Pattern

## Overview

The Publish-Subscribe pattern is an asynchronous communication pattern where publishers broadcast messages to channels or topics, and subscribers receive messages from the topics they're interested in. This pattern enables efficient one-to-many communication and decouples publishers from subscribers.

## Pattern Characteristics

- **Synchronicity**: Asynchronous, non-blocking communication
- **Cardinality**: One-to-many (1:N) or many-to-many (M:N)
- **Flow Control**: Publishers emit, subscribers consume
- **Topic-Based**: Messages organized by topic/channel
- **Loose Coupling**: Publishers don't know subscribers

## Core Capabilities

The Publish-Subscribe pattern provides these key capabilities:

1. **Topic-Based Messaging** - Organization of messages by topic/channel
2. **Subscription Management** - Dynamic addition and removal of subscribers
3. **Message Filtering** - Topic-based and content-based filtering
4. **Delivery Guarantees** - Configurable message delivery guarantees
5. **Retained Messages** - Optional persistence of last message on a topic
6. **Wild Card Subscriptions** - Pattern matching for subscriptions

## Sequence Diagram

```
┌────────────┐                     ┌────────────┐       ┌────────────┐
│            │                     │            │       │            │
│ Publisher  │                     │ Topic      │       │ Subscriber │
│            │                     │            │       │            │
└────────────┘                     └────────────┘       └────────────┘
      │                                  │                    │
      │  1. Publish Message              │                    │
      │ ─────────────────────────────────>                    │
      │                                  │                    │
      │                                  │  2. Notify         │
      │                                  │ ───────────────────>
      │                                  │                    │
      │                                  │  3. Deliver Message│
      │                                  │ ───────────────────>
      │                                  │                    │
      │                                  │                    │  4. Process Message
      │                                  │                    │
```

## Message Format

### Publish Message

```yaml
{
  "id": "publish-123",
  "type": "publish",
  "topic": "system/status/service-1",
  "content": {
    # Topic-specific content
  },
  "metadata": {
    "pattern": "publish_subscribe",
    "timestamp": "2025-05-18T10:32:45Z",
    "publisher_id": "status_monitor",
    "retention": true
  }
}
```

### Subscribe Message

```yaml
{
  "id": "subscribe-456",
  "type": "subscribe",
  "topic": "system/status/#",  # Wild card subscription
  "metadata": {
    "pattern": "publish_subscribe",
    "timestamp": "2025-05-18T10:30:12Z",
    "subscriber_id": "dashboard_agent",
    "qos": 1
  }
}
```

### Notification Message

```yaml
{
  "id": "notification-789",
  "type": "notification",
  "topic": "system/status/service-1",
  "content": {
    # Topic-specific content
  },
  "metadata": {
    "pattern": "publish_subscribe",
    "timestamp": "2025-05-18T10:32:47Z",
    "publisher_id": "status_monitor",
    "original_message_id": "publish-123"
  }
}
```

## Configuration Options

The Publish-Subscribe pattern has these configuration options:

```yaml
publish_subscribe:
  options:
    delivery_guarantee: "at_least_once"  # at_most_once, at_least_once, exactly_once
    topic_structure:
      format: "{agent_id}/{topic}"
      dynamic_segments: ["agent_id"]
    subscription_handling:
      buffer_size: 100
      overflow_strategy: "drop_oldest"  # drop_oldest, drop_newest, block
    retention:
      enabled: true
      max_retained_messages: 100
    filtering:
      content_based: false
      header_based: true
    security:
      require_authentication: true
      authorization_profile: "default"
    observability:
      metrics_enabled: true
      log_level: "info"
      tracing_enabled: true
```

## Implementation

### Pattern Class

```python
class PublishSubscribePattern(Pattern):
    """Implementation of the Publish-Subscribe pattern."""
    
    def __init__(self, options, agent_context):
        """Initialize the pattern."""
        super().__init__(options, agent_context)
        self.delivery_guarantee = options.get("delivery_guarantee", "at_least_once")
        self.topic_structure = options.get("topic_structure", {})
        self.subscription_handling = options.get("subscription_handling", {})
        self.retention = options.get("retention", {})
        
        # Initialize subscriptions
        self.subscriptions = {}
        self.message_handlers = {}
        
    async def publish(self, topic, content, metadata=None):
        """Publish a message to a topic."""
        # Format the topic
        formatted_topic = self._format_topic(topic)
        
        # Create publish message
        message = {
            "id": str(uuid.uuid4()),
            "type": "publish",
            "topic": formatted_topic,
            "content": content,
            "metadata": metadata or {}
        }
        
        # Add pattern metadata
        message["metadata"].update({
            "pattern": "publish_subscribe",
            "timestamp": datetime.now().isoformat(),
            "publisher_id": self.agent_context.agent_id,
            "retention": self.retention.get("enabled", False)
        })
        
        # Get the protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare the outgoing message
        prepared_message = await adapter.prepare_outgoing(message, self)
        
        # Send the message (broadcast)
        await self.agent_context.communicator.broadcast_message(
            prepared_message, topic=formatted_topic)
            
        return message["id"]
        
    async def subscribe(self, topic, handler=None):
        """Subscribe to a topic."""
        # Format the topic
        formatted_topic = self._format_topic(topic)
        
        # Create subscription message
        message = {
            "id": str(uuid.uuid4()),
            "type": "subscribe",
            "topic": formatted_topic,
            "metadata": {
                "pattern": "publish_subscribe",
                "timestamp": datetime.now().isoformat(),
                "subscriber_id": self.agent_context.agent_id,
                "qos": self._get_qos_level()
            }
        }
        
        # Get the protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare the outgoing message
        prepared_message = await adapter.prepare_outgoing(message, self)
        
        # Send the subscription message
        await self.agent_context.communicator.subscribe(
            prepared_message, topic=formatted_topic)
            
        # Register the handler
        if handler:
            self.message_handlers[formatted_topic] = handler
            
        # Track the subscription
        self.subscriptions[formatted_topic] = {
            "id": message["id"],
            "created_at": datetime.now().isoformat()
        }
        
        return message["id"]
        
    async def unsubscribe(self, topic):
        """Unsubscribe from a topic."""
        # Format the topic
        formatted_topic = self._format_topic(topic)
        
        # Create unsubscribe message
        message = {
            "id": str(uuid.uuid4()),
            "type": "unsubscribe",
            "topic": formatted_topic,
            "metadata": {
                "pattern": "publish_subscribe",
                "timestamp": datetime.now().isoformat(),
                "subscriber_id": self.agent_context.agent_id
            }
        }
        
        # Get the protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare the outgoing message
        prepared_message = await adapter.prepare_outgoing(message, self)
        
        # Send the unsubscribe message
        await self.agent_context.communicator.unsubscribe(
            prepared_message, topic=formatted_topic)
            
        # Remove the handler
        if formatted_topic in self.message_handlers:
            del self.message_handlers[formatted_topic]
            
        # Remove the subscription
        if formatted_topic in self.subscriptions:
            del self.subscriptions[formatted_topic]
            
        return True
        
    async def process_incoming(self, message, protocol):
        """Process an incoming message."""
        adapter = self.get_protocol_adapter(protocol)
        transformed = await adapter.process_incoming(message, self)
        
        if transformed.get("type") == "notification":
            # Handle notification
            topic = transformed.get("topic")
            
            # Find matching handlers
            for pattern, handler in self.message_handlers.items():
                if self._topic_matches(topic, pattern):
                    # Call the handler
                    await handler(transformed)
                    
        return transformed
        
    async def prepare_outgoing(self, message, protocol):
        """Prepare an outgoing message."""
        adapter = self.get_protocol_adapter(protocol)
        return await adapter.prepare_outgoing(message, self)
        
    def on_message(self, topic, handler):
        """Register a message handler for a topic."""
        formatted_topic = self._format_topic(topic)
        self.message_handlers[formatted_topic] = handler
        
    def _format_topic(self, topic):
        """Format a topic according to the configured structure."""
        format_str = self.topic_structure.get("format")
        if not format_str:
            return topic
            
        # Apply dynamic segments
        format_args = {}
        for segment in self.topic_structure.get("dynamic_segments", []):
            if segment == "agent_id":
                format_args[segment] = self.agent_context.agent_id
                
        # Format the topic
        try:
            return format_str.format(topic=topic, **format_args)
        except Exception:
            return topic
            
    def _get_qos_level(self):
        """Get the QoS level based on delivery guarantee."""
        if self.delivery_guarantee == "at_most_once":
            return 0
        elif self.delivery_guarantee == "at_least_once":
            return 1
        elif self.delivery_guarantee == "exactly_once":
            return 2
        else:
            return 1
            
    def _topic_matches(self, topic, pattern):
        """Check if a topic matches a subscription pattern."""
        # Convert MQTT-style wildcards to regex
        if "#" in pattern:
            pattern = pattern.replace("#", ".*")
        if "+" in pattern:
            pattern = pattern.replace("+", "[^/]+")
            
        # Escape regex special characters in the pattern
        pattern = "^" + re.escape(pattern).replace("\\+", "[^/]+").replace("\\#", ".*") + "$"
        
        # Check if the topic matches the pattern
        return bool(re.match(pattern, topic))
```

## Protocol Adaptations

### MQTT Protocol Adaptation

MQTT protocol adapts the Publish-Subscribe pattern naturally:

```yaml
publish_subscribe:
  protocol_adaptations:
    mqtt:
      topic_template: "{topic}"
      qos_level: 1
      retain: true
```

**Adapter Implementation:**

```python
class MQTTPublishSubscribeAdapter(ProtocolAdapter):
    """Adapts the Publish-Subscribe pattern to MQTT protocol."""
    
    async def process_incoming(self, message, pattern):
        """Process an incoming MQTT message."""
        # MQTT messages already have topic
        topic = message.get("topic")
        payload = message.get("payload")
        
        try:
            # Parse JSON payload
            content = json.loads(payload)
        except Exception:
            # Use raw payload as content
            content = payload
            
        return {
            "id": str(uuid.uuid4()),  # MQTT doesn't have message IDs
            "type": "notification",
            "topic": topic,
            "content": content,
            "metadata": {
                "pattern": "publish_subscribe",
                "timestamp": datetime.now().isoformat(),
                "qos": message.get("qos", 0)
            }
        }
        
    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing MQTT message."""
        if message.get("type") == "publish":
            # Prepare a publish message
            topic = message.get("topic")
            content = message.get("content")
            
            # Get QoS and retention
            qos = pattern.config.get("qos_level", 1)
            retain = pattern.config.get("retain", False)
            
            # Override from message metadata
            if "qos" in message.get("metadata", {}):
                qos = message["metadata"]["qos"]
            if "retention" in message.get("metadata", {}):
                retain = message["metadata"]["retention"]
                
            return {
                "topic": topic,
                "payload": json.dumps(content),
                "qos": qos,
                "retain": retain
            }
        elif message.get("type") == "subscribe":
            # Prepare a subscribe message
            topic = message.get("topic")
            qos = message.get("metadata", {}).get("qos", 1)
            
            return {
                "topic": topic,
                "qos": qos
            }
        elif message.get("type") == "unsubscribe":
            # Prepare an unsubscribe message
            topic = message.get("topic")
            
            return {
                "topic": topic
            }
```

### A2A Protocol Adaptation

A2A protocol adapts the Publish-Subscribe pattern using tasks:

```yaml
publish_subscribe:
  protocol_adaptations:
    a2a:
      use_tasks: true
      task_type: "notification"
      topic_metadata_field: "topic"
```

**Adapter Implementation:**

```python
class A2APublishSubscribeAdapter(ProtocolAdapter):
    """Adapts the Publish-Subscribe pattern to A2A protocol."""
    
    async def process_incoming(self, message, pattern):
        """Process an incoming A2A message."""
        if message.get("type") == pattern.config.get("task_type", "notification"):
            # Extract notification from A2A task
            metadata = message.get("metadata", {})
            topic = metadata.get(pattern.config.get("topic_metadata_field", "topic"))
            
            return {
                "id": message.get("id"),
                "type": "notification",
                "topic": topic,
                "content": message.get("input"),
                "metadata": {
                    "pattern": "publish_subscribe",
                    "timestamp": metadata.get("timestamp"),
                    "publisher_id": metadata.get("publisher_id")
                }
            }
            
        return message
        
    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing A2A message."""
        if message.get("type") == "publish":
            # Create an A2A task for the publication
            task = {
                "type": pattern.config.get("task_type", "notification"),
                "input": message.get("content"),
                "metadata": {
                    "pattern": "publish_subscribe",
                    "timestamp": message.get("metadata", {}).get("timestamp"),
                    "publisher_id": message.get("metadata", {}).get("publisher_id"),
                    "topic": message.get("topic")
                }
            }
            return task
        
        return message
```

## Integration with Topologies

The Publish-Subscribe pattern is commonly used in these topology relationships:

1. **Peer-to-Peer**: Broadcasting information between peers
2. **Centralized**: Workers reporting status to orchestrator
3. **Mesh**: Non-targeted broadcast across mesh nodes
4. **Event-Driven**: Broadcasting state changes and events

**Example Configuration:**

```yaml
topology:
  pattern: "peer_to_peer"
  roles:
    types:
      - name: "peer"
  relationships:
    types:
      - name: "peer_to_peer"
        communication_patterns:
          primary: "publish_subscribe"
```

## Use Cases

### 1. Status Broadcasting

An agent broadcasts status information to interested parties:

```python
# Status monitor publishing updates
await pubsub_pattern.publish(
    topic="system/status/service-1",
    content={
        "status": "healthy",
        "metrics": {
            "cpu": 23.5,
            "memory": 45.2,
            "requests": 156
        },
        "timestamp": datetime.now().isoformat()
    }
)

# Dashboard agent subscribing to status updates
await pubsub_pattern.subscribe(
    topic="system/status/#",  # Subscribe to all service statuses
    handler=self.handle_status_update
)

async def handle_status_update(self, message):
    """Handle a status update notification."""
    service_id = message.get("topic").split("/")[-1]
    status = message.get("content", {}).get("status")
    metrics = message.get("content", {}).get("metrics", {})
    
    # Update dashboard with status
    await self.dashboard.update_service_status(service_id, status, metrics)
```

### 2. Event Broadcasting

Broadcasting events to multiple interested subscribers:

```yaml
# Event broadcaster configuration
agents:
  event_broadcaster:
    class: "agents.event.EventBroadcaster"
    patterns:
      publish_subscribe:
        options:
          topic_structure:
            format: "events/{topic}"
    topology:
      role: "broadcaster"
      relationships:
        - agent_id: "*"  # All agents
          relationship_type: "broadcaster_to_subscriber"
          communication_pattern: "publish_subscribe"
```

### 3. Content Distribution

Distributing content updates to subscribers:

```python
# Content publisher publishing new content
await pubsub_pattern.publish(
    topic="content/articles/new",
    content={
        "id": "article-123",
        "title": "New Developments in AI",
        "summary": "Recent breakthroughs in artificial intelligence...",
        "url": "https://example.com/articles/123",
        "published_at": datetime.now().isoformat()
    }
)

# Content subscriber receiving updates
await pubsub_pattern.subscribe(
    topic="content/articles/#",
    handler=self.handle_new_content
)

async def handle_new_content(self, message):
    """Handle new content notification."""
    topic_parts = message.get("topic").split("/")
    content_type = topic_parts[1] if len(topic_parts) > 1 else "unknown"
    content = message.get("content", {})
    
    # Process new content
    if content_type == "articles":
        await self.content_manager.add_article(content)
    elif content_type == "videos":
        await self.content_manager.add_video(content)
```

## Security Considerations

The Publish-Subscribe pattern includes these security features:

1. **Topic Authorization**: Permissions for publishing and subscribing to topics
2. **Content Validation**: Validate published content before distribution
3. **Rate Limiting**: Prevent flooding with excessive publications
4. **Access Control**: Topic-based access control for subscribers
5. **Encryption**: Optional payload encryption

**Security Configuration:**

```yaml
publish_subscribe:
  options:
    security:
      require_authentication: true
      topic_permissions:
        - topic: "system/#"
          roles: ["admin", "system"]
          operations: ["publish", "subscribe"]
        - topic: "public/#"
          roles: ["*"]
          operations: ["subscribe"]
      content_validation: true
      encrypt_payload: false
```

## Observability

The Publish-Subscribe pattern supports observability:

1. **Publication Metrics**: Count, rate, size
2. **Subscription Metrics**: Count, active subscribers
3. **Delivery Tracking**: Success/failure rates
4. **Topic Analytics**: Most/least active topics

**Metrics Example:**

```
publish_count{agent="status_monitor",topic="system/status/#"} 1250
active_subscribers{topic="system/status/#"} 8
message_delivery_success_rate{topic="system/status/#"} 0.998
average_message_size_bytes{topic="system/status/#"} 512
```

## Protocol Independence

The Publish-Subscribe pattern works consistently across protocols:

- **MQTT**: Native pub/sub with topics and QoS
- **Redis**: Using Redis pub/sub channels
- **A2A**: Using notification tasks
- **WebSockets**: Using channel-based messaging
- **HTTP**: Using webhooks and server-sent events

This protocol independence enables agents to use the same pattern regardless of the underlying protocol implementation.
