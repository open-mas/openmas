# Basic Session Configuration Examples

This document provides basic examples for configuring sessions in OpenMAS agents across different protocols and scenarios.

## Overview

OpenMAS sessions provide persistent conversation handling and state management while maintaining reasoning agnosticism and protocol independence.

## Basic Configuration Examples

### 1. Simple Memory-Based Session

```yaml
# Basic in-memory session configuration
sessions:
  enabled: true
  storage:
    type: "memory"
    max_sessions: 100
  context:
    max_history_items: 20
    max_tokens: 2000
    pruning_strategy: "fifo"  # First In, First Out
```

### 2. File-Based Session Storage

```yaml
# File-based persistent session storage
sessions:
  enabled: true
  storage:
    type: "file"
    directory: "./sessions"
    auto_save: true
    save_interval: 30  # seconds
  context:
    max_history_items: 50
    max_tokens: 4000
    pruning_strategy: "selective"
```

### 3. Protocol-Specific Session Configuration

#### A2A Protocol Sessions

```yaml
sessions:
  enabled: true
  protocol_sessions:
    a2a:
      enabled: true
      task_persistence: true
      capability_tracking: true
      agent_discovery_cache: true
    context:
      max_history_items: 30
      preserve_task_context: true
```

#### MCP Protocol Sessions

```yaml
sessions:
  enabled: true
  protocol_sessions:
    mcp:
      enabled: true
      tool_state_tracking: true
      resource_caching: true
      prompt_history: true
    context:
      max_history_items: 40
      preserve_tool_calls: true
```

## Basic Usage Patterns

### 1. Single Agent Session

```python
from openmas.agent import BaseAgent
from openmas.core.simf import SIMFMessage

class SimpleAgent(BaseAgent):
    async def process_message(self, message: SIMFMessage) -> SIMFMessage:
        # Session automatically managed by framework
        session_id = self.get_current_session_id()
        context = await self.get_session_context(session_id)

        # Your processing logic here
        response = await self.generate_response(message, context)

        # Session automatically updated
        return response
```

### 2. Basic Session Lifecycle

```python
# Manual session management (optional)
agent = SimpleAgent(config)

# Start new session
session_id = await agent.start_session("user_123")

# Process messages within session
message = SIMFMessage(content="Hello", sender="user")
response = await agent.process_message(message, session_id=session_id)

# End session
await agent.end_session(session_id)
```

### 3. Session Context Access

```python
async def handle_message(self, message: SIMFMessage) -> SIMFMessage:
    # Get current session context
    context = await self.get_session_context()

    # Access message history
    recent_messages = context.get_recent_messages(limit=5)

    # Access session metadata
    session_metadata = context.get_metadata()

    # Update session state
    await context.update_state("last_action", "processed_message")

    return await self.generate_response(message, context)
```

## Configuration Validation

### Minimal Required Configuration

```yaml
# Absolute minimum session configuration
sessions:
  enabled: true
  # All other settings use framework defaults
```

### Recommended Basic Configuration

```yaml
# Recommended settings for most use cases
sessions:
  enabled: true
  storage:
    type: "memory"
  context:
    max_history_items: 30
    max_tokens: 3000
    pruning_strategy: "selective"
  protocol_sessions:
    # Enable for protocols you're using
    a2a:
      enabled: true
    mcp:
      enabled: true
```

## Error Handling

### Basic Error Recovery

```python
async def safe_session_operation(self, operation):
    try:
        return await operation()
    except SessionNotFoundError:
        # Create new session if not found
        session_id = await self.start_session()
        return await operation()
    except SessionStorageError:
        # Fallback to memory storage
        await self.fallback_to_memory_storage()
        return await operation()
```

## Testing Session Configuration

### Basic Session Test

```python
import pytest
from openmas.agent import BaseAgent

@pytest.mark.asyncio
async def test_basic_session():
    config = {
        "sessions": {
            "enabled": True,
            "storage": {"type": "memory"}
        }
    }

    agent = BaseAgent(config)

    # Test session creation
    session_id = await agent.start_session("test_user")
    assert session_id is not None

    # Test message processing
    message = SIMFMessage(content="test", sender="test_user")
    response = await agent.process_message(message, session_id=session_id)

    # Test session cleanup
    await agent.end_session(session_id)
```

## Common Patterns

### 1. User-Based Sessions
```yaml
sessions:
  session_id_strategy: "user_based"  # One session per user
  max_concurrent_sessions: 50
```

### 2. Conversation-Based Sessions
```yaml
sessions:
  session_id_strategy: "conversation_based"  # One session per conversation
  auto_expire: true
  expiry_timeout: 3600  # 1 hour
```

### 3. Task-Based Sessions
```yaml
sessions:
  session_id_strategy: "task_based"  # One session per task
  preserve_task_state: true
  task_completion_cleanup: true
```

## Next Steps

- For advanced session patterns, see [Advanced Session Examples](./advanced_session.md)
- For protocol-specific integration, see [Protocol Integration](../protocol_integration/)
- For multi-agent sessions, see [Multi-Agent Sessions](../multi_agent_sessions.md)

## References

- [Session Management Design](../design_session_management.md)
- [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md)
- [Agent Framework Overview](../agent_framework_overview.md)
