# Event-Based Pattern

## Overview

The Event-Based pattern is an asynchronous communication pattern where agents emit events when significant state changes or actions occur. Other agents can register interest in specific event types and receive notifications when those events happen. This pattern enables reactive, loosely-coupled communication between agents.

## Pattern Characteristics

- **Synchronicity**: Asynchronous, reactive communication
- **Cardinality**: Many-to-many (M:N)
- **Flow Control**: Event-driven, push-based
- **Coupling**: Loose coupling between emitters and handlers
- **State-Oriented**: Focused on state changes and occurrences

## Core Capabilities

The Event-Based pattern provides these key capabilities:

1. **Event Emission** - Publishing events when state changes or actions occur
2. **Event Subscription** - Registering interest in specific event types
3. **Event Filtering** - Filtering events based on type and content
4. **Event Routing** - Directing events to interested handlers
5. **Event Ordering** - Maintaining event sequence when necessary
6. **Event Correlation** - Connecting related events

## Sequence Diagram

```
┌────────────┐                     ┌────────────┐       ┌────────────┐
│            │                     │            │       │            │
│   Emitter  │                     │Event Router│       │  Handler   │
│            │                     │            │       │            │
└────────────┘                     └────────────┘       └────────────┘
      │                                  │                    │
      │  1. Emit Event                   │                    │
      │ ─────────────────────────────────>                    │
      │                                  │                    │
      │                                  │  2. Route Event    │
      │                                  │ ───────────────────>
      │                                  │                    │
      │                                  │                    │  3. Handle Event
      │                                  │                    │
      │                                  │  4. Acknowledge    │
      │                                  │ <───────────────────
      │                                  │                    │
```

## Message Format

### Event Message

```yaml
{
  "id": "event-123",
  "type": "event",
  "event_type": "status_changed",
  "content": {
    "entity_id": "service-1",
    "previous_status": "starting",
    "new_status": "running",
    "changed_at": "2025-05-18T10:32:45Z"
  },
  "metadata": {
    "pattern": "event_based",
    "timestamp": "2025-05-18T10:32:45Z",
    "emitter_id": "service_monitor",
    "severity": "info",
    "correlation_id": "deployment-789"
  }
}
```

### Subscription Message

```yaml
{
  "id": "subscription-456",
  "type": "event_subscription",
  "event_types": ["status_changed", "error_occurred"],
  "filters": [
    {
      "field": "content.entity_id",
      "operator": "startsWith",
      "value": "service-"
    }
  ],
  "metadata": {
    "pattern": "event_based",
    "timestamp": "2025-05-18T10:30:12Z",
    "subscriber_id": "dashboard_agent",
    "expiration": "2025-05-18T22:30:12Z"
  }
}
```

### Acknowledgment Message

```yaml
{
  "id": "acknowledgment-789",
  "type": "event_acknowledgment",
  "event_id": "event-123",
  "status": "processed",
  "metadata": {
    "pattern": "event_based",
    "timestamp": "2025-05-18T10:32:47Z",
    "handler_id": "dashboard_agent",
    "processing_time_ms": 42
  }
}
```

## Configuration Options

The Event-Based pattern has these configuration options:

```yaml
event_based:
  options:
    event_structure:
      include_metadata: true
      include_source: true
      include_correlation: true
    event_handling:
      ordering: "timestamp"  # timestamp, sequence, none
      deduplicate: true
      max_retry: 3
    filtering:
      enabled: true
      criteria:
        - field: "event_type"
          operator: "in"
          values: ["status_change", "error"]
    persistence:
      enabled: false
      ttl_seconds: 86400
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
class EventBasedPattern(Pattern):
    """Implementation of the Event-Based pattern."""

    def __init__(self, options, agent_context):
        """Initialize the pattern."""
        super().__init__(options, agent_context)
        self.event_structure = options.get("event_structure", {})
        self.event_handling = options.get("event_handling", {})
        self.filtering = options.get("filtering", {})
        self.persistence = options.get("persistence", {})

        # Initialize event handlers
        self.event_handlers = {}
        self.event_filters = {}

    async def emit_event(self, event_type, content, metadata=None):
        """Emit an event."""
        # Create event message
        event = {
            "id": str(uuid.uuid4()),
            "type": "event",
            "event_type": event_type,
            "content": content,
            "metadata": metadata or {}
        }

        # Add pattern metadata
        event["metadata"].update({
            "pattern": "event_based",
            "timestamp": datetime.now().isoformat(),
            "emitter_id": self.agent_context.agent_id
        })

        # Add correlation ID if available
        if self.event_structure.get("include_correlation", True):
            correlation_id = self.agent_context.get_correlation_id()
            if correlation_id:
                event["metadata"]["correlation_id"] = correlation_id

        # Get the protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)

        # Prepare the outgoing message
        prepared_event = await adapter.prepare_outgoing(event, self)

        # Emit the event (broadcast)
        await self.agent_context.communicator.broadcast_message(
            prepared_event, event_type=event_type)

        # Persist event if configured
        if self.persistence.get("enabled", False):
            await self._persist_event(event)

        return event["id"]

    async def subscribe_to_events(self, event_types, handler=None, filters=None):
        """Subscribe to events."""
        if isinstance(event_types, str):
            event_types = [event_types]

        # Create subscription message
        subscription = {
            "id": str(uuid.uuid4()),
            "type": "event_subscription",
            "event_types": event_types,
            "filters": filters or [],
            "metadata": {
                "pattern": "event_based",
                "timestamp": datetime.now().isoformat(),
                "subscriber_id": self.agent_context.agent_id
            }
        }

        # Get the protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)

        # Prepare the outgoing message
        prepared_subscription = await adapter.prepare_outgoing(subscription, self)

        # Send the subscription
        await self.agent_context.communicator.subscribe_to_events(
            prepared_subscription, event_types=event_types)

        # Register the handler
        if handler:
            for event_type in event_types:
                if event_type not in self.event_handlers:
                    self.event_handlers[event_type] = []
                self.event_handlers[event_type].append(handler)

                # Store filters
                if filters:
                    if event_type not in self.event_filters:
                        self.event_filters[event_type] = {}
                    self.event_filters[event_type][handler] = filters

        return subscription["id"]

    async def unsubscribe_from_events(self, event_types, handler=None):
        """Unsubscribe from events."""
        if isinstance(event_types, str):
            event_types = [event_types]

        # Create unsubscription message
        unsubscription = {
            "id": str(uuid.uuid4()),
            "type": "event_unsubscription",
            "event_types": event_types,
            "metadata": {
                "pattern": "event_based",
                "timestamp": datetime.now().isoformat(),
                "subscriber_id": self.agent_context.agent_id
            }
        }

        # Get the protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)

        # Prepare the outgoing message
        prepared_unsubscription = await adapter.prepare_outgoing(unsubscription, self)

        # Send the unsubscription
        await self.agent_context.communicator.unsubscribe_from_events(
            prepared_unsubscription, event_types=event_types)

        # Remove the handler
        if handler:
            for event_type in event_types:
                if event_type in self.event_handlers:
                    if handler in self.event_handlers[event_type]:
                        self.event_handlers[event_type].remove(handler)

                    # Remove filters
                    if event_type in self.event_filters and handler in self.event_filters[event_type]:
                        del self.event_filters[event_type][handler]
        else:
            # Remove all handlers for these event types
            for event_type in event_types:
                if event_type in self.event_handlers:
                    del self.event_handlers[event_type]
                if event_type in self.event_filters:
                    del self.event_filters[event_type]

        return True

    async def process_incoming(self, message, protocol):
        """Process an incoming message."""
        adapter = self.get_protocol_adapter(protocol)
        transformed = await adapter.process_incoming(message, self)

        if transformed.get("type") == "event":
            # Handle event
            event_type = transformed.get("event_type")

            # Check if we have handlers for this event type
            handlers = []
            if event_type in self.event_handlers:
                handlers.extend(self.event_handlers[event_type])
            if "*" in self.event_handlers:  # Wildcard handlers
                handlers.extend(self.event_handlers["*"])

            # Apply filters
            for handler in list(handlers):
                if event_type in self.event_filters and handler in self.event_filters[event_type]:
                    filters = self.event_filters[event_type][handler]
                    if not self._matches_filters(transformed, filters):
                        handlers.remove(handler)

            # Call handlers
            for handler in handlers:
                await handler(transformed)

            # Send acknowledgment if needed
            if self.event_handling.get("acknowledge", False):
                await self._send_acknowledgment(transformed)

        return transformed

    async def prepare_outgoing(self, message, protocol):
        """Prepare an outgoing message."""
        adapter = self.get_protocol_adapter(protocol)
        return await adapter.prepare_outgoing(message, self)

    def on_event(self, event_type, handler, filters=None):
        """Register an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

        # Store filters
        if filters:
            if event_type not in self.event_filters:
                self.event_filters[event_type] = {}
            self.event_filters[event_type][handler] = filters

    async def _send_acknowledgment(self, event):
        """Send an acknowledgment for an event."""
        ack = {
            "id": str(uuid.uuid4()),
            "type": "event_acknowledgment",
            "event_id": event.get("id"),
            "status": "processed",
            "metadata": {
                "pattern": "event_based",
                "timestamp": datetime.now().isoformat(),
                "handler_id": self.agent_context.agent_id
            }
        }

        # Get the protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)

        # Prepare the outgoing message
        prepared_ack = await adapter.prepare_outgoing(ack, self)

        # Send the acknowledgment to the emitter
        emitter_id = event.get("metadata", {}).get("emitter_id")
        if emitter_id:
            await self.agent_context.communicator.send_message(
                prepared_ack, target_agent_id=emitter_id)

    async def _persist_event(self, event):
        """Persist an event."""
        # Implementation depends on storage backend
        # This is a placeholder
        pass

    def _matches_filters(self, event, filters):
        """Check if an event matches filters."""
        if not filters:
            return True

        for filter_spec in filters:
            field = filter_spec.get("field")
            operator = filter_spec.get("operator")
            value = filter_spec.get("value")

            # Extract field value
            field_parts = field.split(".")
            field_value = event
            for part in field_parts:
                if isinstance(field_value, dict) and part in field_value:
                    field_value = field_value[part]
                else:
                    field_value = None
                    break

            # Apply operator
            if operator == "equals":
                if field_value != value:
                    return False
            elif operator == "notEquals":
                if field_value == value:
                    return False
            elif operator == "in":
                if field_value not in value:
                    return False
            elif operator == "notIn":
                if field_value in value:
                    return False
            elif operator == "startsWith":
                if not isinstance(field_value, str) or not field_value.startswith(value):
                    return False
            elif operator == "endsWith":
                if not isinstance(field_value, str) or not field_value.endswith(value):
                    return False
            elif operator == "contains":
                if not isinstance(field_value, str) or value not in field_value:
                    return False

        return True
```

## Protocol Adaptations

### A2A Protocol Adaptation

A2A protocol adapts the Event-Based pattern using tasks:

```yaml
event_based:
  protocol_adaptations:
    a2a:
      use_tasks: true
      task_type: "event"
      event_type_field: "event_type"
```

**Adapter Implementation:**

```python
class A2AEventBasedAdapter(ProtocolAdapter):
    """Adapts the Event-Based pattern to A2A protocol."""

    async def process_incoming(self, message, pattern):
        """Process an incoming A2A message."""
        if message.get("type") == pattern.config.get("task_type", "event"):
            # Extract event from A2A task
            metadata = message.get("metadata", {})
            event_type = metadata.get(pattern.config.get("event_type_field", "event_type"))

            return {
                "id": message.get("id"),
                "type": "event",
                "event_type": event_type,
                "content": message.get("input"),
                "metadata": metadata
            }

        return message

    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing A2A message."""
        if message.get("type") == "event":
            # Create an A2A task for the event
            task = {
                "type": pattern.config.get("task_type", "event"),
                "input": message.get("content"),
                "metadata": message.get("metadata", {})
            }

            # Ensure event_type is in metadata
            task["metadata"][pattern.config.get("event_type_field", "event_type")] = message.get("event_type")

            return task

        return message
```

### MCP Protocol Adaptation

MCP protocol adapts the Event-Based pattern using function calls:

```yaml
event_based:
  protocol_adaptations:
    mcp:
      use_function_calls: true
      emit_function: "emit_event"
      handle_function: "handle_event"
```

**Adapter Implementation:**

```python
class MCPEventBasedAdapter(ProtocolAdapter):
    """Adapts the Event-Based pattern to MCP protocol."""

    async def process_incoming(self, message, pattern):
        """Process an incoming MCP message."""
        if message.get("type") == "function_call" and message.get("name") == pattern.config.get("handle_function", "handle_event"):
            # Extract event from function call
            args = message.get("arguments", {})

            return {
                "id": message.get("id"),
                "type": "event",
                "event_type": args.get("event_type"),
                "content": args.get("content"),
                "metadata": args.get("metadata", {})
            }

        return message

    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing MCP message."""
        if message.get("type") == "event":
            # Create a function call for the event
            function_call = {
                "type": "function_call",
                "name": pattern.config.get("emit_function", "emit_event"),
                "arguments": {
                    "event_type": message.get("event_type"),
                    "content": message.get("content"),
                    "metadata": message.get("metadata", {})
                }
            }
            return function_call

        return message
```

## Integration with Topologies

The Event-Based pattern is commonly used in these topology relationships:

1. **Centralized**: Workers reporting events to orchestrator
2. **Mesh**: State change notification across mesh nodes
3. **Event-Driven**: Core pattern for event-driven architectures
4. **Hierarchical**: Bubbling up events through hierarchy

**Example Configuration:**

```yaml
topology:
  pattern: "centralized"
  roles:
    types:
      - name: "orchestrator"
      - name: "worker"
  relationships:
    types:
      - name: "worker_to_orchestrator"
        communication_patterns:
          primary: "event_based"
```

## Use Cases

### 1. Status Change Notifications

Agents emit events when their status changes:

```python
# Service agent emitting status change
await events_pattern.emit_event(
    event_type="status_changed",
    content={
        "entity_id": "service-1",
        "previous_status": "starting",
        "new_status": "running",
        "changed_at": datetime.now().isoformat()
    },
    metadata={
        "severity": "info"
    }
)

# Monitoring agent subscribing to status changes
await events_pattern.subscribe_to_events(
    event_types=["status_changed", "error_occurred"],
    handler=self.handle_status_event,
    filters=[
        {
            "field": "content.entity_id",
            "operator": "startsWith",
            "value": "service-"
        }
    ]
)

async def handle_status_event(self, event):
    """Handle a status change event."""
    event_type = event.get("event_type")
    content = event.get("content", {})

    if event_type == "status_changed":
        entity_id = content.get("entity_id")
        new_status = content.get("new_status")

        # Update monitoring dashboard
        await self.dashboard.update_status(entity_id, new_status)

        # Check for critical status
        if new_status == "critical":
            await self.alert_critical_status(entity_id, content)
```

### 2. Workflow Events

Events driving workflow progression:

```yaml
# Workflow engine configuration
agents:
  workflow_engine:
    class: "agents.workflow.WorkflowEngine"
    patterns:
      event_based:
        options:
          event_structure:
            include_correlation: true
          event_handling:
            ordering: "sequence"
    topology:
      role: "orchestrator"
      relationships:
        - agent_id: "*"  # All worker agents
          relationship_type: "orchestrator_to_worker"
          communication_pattern: "event_based"
```

### 3. System Monitoring

Monitoring system health through events:

```python
# System monitor subscribing to various events
await events_pattern.subscribe_to_events(
    event_types=[
        "resource_exceeded",
        "error_occurred",
        "security_alert",
        "performance_degradation"
    ],
    handler=self.handle_system_event
)

async def handle_system_event(self, event):
    """Handle a system event."""
    event_type = event.get("event_type")
    content = event.get("content", {})
    metadata = event.get("metadata", {})
    severity = metadata.get("severity", "info")

    # Log the event
    self.logger.log(
        self._severity_to_log_level(severity),
        f"System event: {event_type}",
        extra={
            "event_id": event.get("id"),
            "content": content,
            "metadata": metadata
        }
    )

    # Take action based on event type and severity
    if severity in ["error", "critical"]:
        await self.alert_administrators(event)

    if event_type == "resource_exceeded":
        await self.handle_resource_exceeded(content)
    elif event_type == "security_alert":
        await self.handle_security_alert(content)
```

## Security Considerations

The Event-Based pattern includes these security features:

1. **Event Authorization**: Permissions for emitting and receiving events
2. **Event Validation**: Validate event content before processing
3. **Rate Limiting**: Prevent flooding with excessive events
4. **Access Control**: Event type-based access control
5. **Audit Logging**: Tracking of critical events

**Security Configuration:**

```yaml
event_based:
  options:
    security:
      require_authentication: true
      event_type_permissions:
        - event_type: "security_*"
          roles: ["admin", "security"]
          operations: ["emit", "receive"]
        - event_type: "status_*"
          roles: ["*"]
          operations: ["receive"]
      content_validation: true
      rate_limit:
        max_events: 100
        period_seconds: 60
```

## Observability

The Event-Based pattern supports observability:

1. **Event Metrics**: Count, rate, by type
2. **Handler Metrics**: Processing time, success rate
3. **Correlation**: Tracing related events
4. **Event Analytics**: Most frequent events, patterns

**Metrics Example:**

```
event_emit_count{agent="service_monitor",event_type="status_changed"} 542
event_handling_time_ms{agent="dashboard",event_type="status_changed"} 12.5
event_error_rate{agent="dashboard"} 0.002
active_event_subscriptions{agent="dashboard"} 5
```

## Protocol Independence

The Event-Based pattern works consistently across protocols:

- **A2A**: Using event-type tasks
- **MCP**: Using function calls for events
- **MQTT**: Using topic-based event routing
- **WebSockets**: Using event messages
- **HTTP**: Using webhooks for event delivery

This protocol independence enables agents to emit and handle events using the same pattern regardless of the underlying protocol implementation.
