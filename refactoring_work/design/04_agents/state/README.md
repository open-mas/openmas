# Agent State Management

This directory contains comprehensive documentation for agent state management in OpenMAS 0.3.0, focusing on multi-layered state persistence, synchronization strategies, and protocol-agnostic state handling.

## Overview

OpenMAS agent state management provides:
- Multi-layered state architecture (permanent, session, conversation, temporary)
- Protocol-agnostic state persistence and retrieval
- Distributed state synchronization across agent topologies
- State versioning and conflict resolution
- Performance-optimized state access patterns

## Key Concepts

### State Layers

OpenMAS implements a hierarchical state management system with distinct layers:

1. **Permanent State**: Persistent across all sessions and restarts
2. **Session State**: Persistent for the duration of a session
3. **Conversation State**: Scoped to individual conversations
4. **Temporary State**: Request-scoped, automatically cleaned up

### State Synchronization

State synchronization strategies ensure consistency across distributed agent topologies:
- **Immediate**: Real-time synchronization for critical state
- **Periodic**: Batched synchronization for performance optimization
- **On-Change**: Event-driven synchronization for reactive state
- **Manual**: Explicit synchronization control for specialized scenarios

### Protocol Independence

State management operates independently of communication protocols, ensuring:
- Consistent state access patterns across A2A, MCP, HTTP, MQTT, gRPC
- Protocol-specific state optimizations without breaking abstraction
- State migration capabilities when switching protocols

## Architecture

### State Management Components

```mermaid
graph TD
    A[Agent] --> B[State Manager]
    B --> C[State Layer Manager]
    B --> D[State Synchronizer]
    B --> E[State Persistence Engine]

    C --> F[Permanent Layer]
    C --> G[Session Layer]
    C --> H[Conversation Layer]
    C --> I[Temporary Layer]

    D --> J[Sync Strategies]
    D --> K[Conflict Resolution]

    E --> L[Storage Backends]
    E --> M[Serialization]
    E --> N[Versioning]
```

### State Access Patterns

The state management system supports multiple access patterns:

- **Direct Access**: `await agent.get_state("key")`
- **Layered Access**: `await agent.get_state_layer("session").get("key")`
- **Typed Access**: `await agent.get_typed_state(UserPreferences)`
- **Batch Access**: `await agent.get_state_batch(["key1", "key2"])`
- **Reactive Access**: `await agent.watch_state("key", callback)`

## Documentation Structure

This directory contains the following documentation:

| Document | Description |
|----------|-------------|
| [State Layers](./state_layers.md) | Detailed specification of state layer hierarchy |
| [Synchronization Strategies](./synchronization.md) | State sync patterns and conflict resolution |
| [Storage Backends](./storage_backends.md) | Available persistence implementations |
| [Performance Optimization](./performance.md) | State access optimization techniques |
| [Protocol Integration](./protocol_integration.md) | Protocol-specific state handling |
| [Migration Guide](./migration.md) | State migration patterns and versioning |

## Configuration

### Basic State Management Configuration

```yaml
state_management:
  enabled: true

  # State layers configuration
  layers:
    permanent:
      enabled: true
      storage: "database"
      sync_strategy: "immediate"
    session:
      enabled: true
      storage: "memory"
      sync_strategy: "periodic"
      sync_interval: 60
    conversation:
      enabled: true
      storage: "memory"
      sync_strategy: "on_change"
    temporary:
      enabled: true
      storage: "memory"
      sync_strategy: "none"
      auto_cleanup: true
      cleanup_interval: 300

  # Storage configuration
  storage:
    database:
      type: "postgresql"
      connection_string: "postgresql://user:pass@localhost/openmas"
      table_prefix: "agent_state_"
    memory:
      type: "in_memory"
      max_size: "100MB"
    file:
      type: "filesystem"
      directory: "./state_data"
      format: "json"

  # Synchronization configuration
  synchronization:
    conflict_resolution: "last_writer_wins"
    enable_versioning: true
    max_versions: 10
    distributed_sync: true
```

### Advanced State Management Configuration

```yaml
state_management:
  enabled: true

  # Advanced features
  advanced:
    state_compression:
      enabled: true
      algorithm: "gzip"
      threshold: 1024  # bytes

    state_encryption:
      enabled: true
      algorithm: "AES-256-GCM"
      key_rotation: true
      rotation_interval: 86400  # 24 hours

    state_partitioning:
      enabled: true
      strategy: "agent_id_hash"
      partitions: 16

    distributed_caching:
      enabled: true
      cache_type: "redis"
      cache_ttl: 3600
      cache_clusters: ["redis-1:6379", "redis-2:6379"]

  # Performance optimizations
  performance:
    lazy_loading: true
    state_prefetching: true
    batch_operations: true
    connection_pooling:
      enabled: true
      pool_size: 20
      max_idle: 5
```

## Usage Examples

### Basic State Operations

```python
from openmas.agent import BaseAgent

class StatefulAgent(BaseAgent):
    async def initialize_state(self):
        """Initialize agent state layers"""

        # Set permanent preferences
        await self.set_permanent_state("user_preferences", {
            "language": "en",
            "timezone": "UTC",
            "theme": "default"
        })

        # Initialize session state
        await self.set_session_state("session_start_time", datetime.utcnow())
        await self.set_session_state("message_count", 0)

        # Set conversation context
        await self.set_conversation_state("conversation_id", str(uuid.uuid4()))

    async def process_message_with_state(self, message):
        """Process message using state context"""

        # Access state from different layers
        preferences = await self.get_permanent_state("user_preferences")
        message_count = await self.get_session_state("message_count", default=0)
        conversation_id = await self.get_conversation_state("conversation_id")

        # Process message with state context
        response = await self.generate_response(message, {
            "preferences": preferences,
            "message_count": message_count,
            "conversation_id": conversation_id
        })

        # Update state
        await self.set_session_state("message_count", message_count + 1)
        await self.set_conversation_state("last_message_time", datetime.utcnow())

        return response
```

### Advanced State Patterns

```python
class AdvancedStatefulAgent(BaseAgent):
    async def use_typed_state(self):
        """Use typed state for better type safety"""

        from dataclasses import dataclass

        @dataclass
        class UserProfile:
            name: str
            email: str
            preferences: dict
            created_at: datetime

        # Set typed state
        profile = UserProfile(
            name="John Doe",
            email="john@example.com",
            preferences={"theme": "dark"},
            created_at=datetime.utcnow()
        )

        await self.set_typed_state("user_profile", profile)

        # Get typed state
        retrieved_profile = await self.get_typed_state("user_profile", UserProfile)

        return retrieved_profile

    async def use_reactive_state(self):
        """Set up reactive state watching"""

        async def on_preference_change(key, old_value, new_value):
            """Handle preference changes"""
            await self.log_state_change(f"Preference {key} changed from {old_value} to {new_value}")

            # Trigger dependent updates
            if key == "theme":
                await self.update_ui_theme(new_value)

        # Watch for preference changes
        await self.watch_state("user_preferences", on_preference_change)

    async def use_distributed_state(self):
        """Handle distributed state synchronization"""

        # Create state with distributed sync
        await self.set_distributed_state("shared_knowledge", {
            "facts": ["fact1", "fact2"],
            "updated_by": self.agent_id,
            "updated_at": datetime.utcnow()
        })

        # Subscribe to distributed state changes
        async def on_knowledge_update(agent_id, state_data):
            await self.integrate_shared_knowledge(state_data)

        await self.subscribe_to_distributed_state("shared_knowledge", on_knowledge_update)
```

## Integration with Other Components

### Session Management Integration

State management integrates seamlessly with session management:

```python
# State is automatically scoped to sessions
session_id = await agent.start_session("user123")

# Session state is automatically isolated
await agent.set_session_state("session_data", {"key": "value"})

# State is automatically cleaned up when session ends
await agent.end_session(session_id)
```

### Protocol Integration

State management works consistently across all protocols:

```python
# A2A protocol - capability-based state
await agent.set_state("available_capabilities", ["analysis", "reporting"])

# MCP protocol - tool state
await agent.set_state("tool_states", {"calculator": "initialized"})

# HTTP protocol - request state
await agent.set_state("request_context", {"endpoint": "/api/v1/process"})
```

### Topology Integration

State management supports various agent topologies:

```python
# Hierarchical topology - parent-child state inheritance
if self.is_parent_agent():
    await self.share_state_with_children("shared_config", config_data)

# Peer-to-peer topology - distributed state consensus
if self.is_peer_agent():
    await self.propose_state_change("consensus_data", new_data)

# Hub-and-spoke topology - centralized state coordination
if self.is_hub_agent():
    await self.coordinate_spoke_state_updates()
```

## Testing State Management

### Unit Tests

```python
@pytest.mark.asyncio
async def test_state_layer_isolation():
    """Test that state layers are properly isolated"""

    agent = TestAgent()

    # Set state in different layers
    await agent.set_permanent_state("key", "permanent_value")
    await agent.set_session_state("key", "session_value")
    await agent.set_conversation_state("key", "conversation_value")

    # Verify isolation
    assert await agent.get_permanent_state("key") == "permanent_value"
    assert await agent.get_session_state("key") == "session_value"
    assert await agent.get_conversation_state("key") == "conversation_value"

@pytest.mark.asyncio
async def test_state_synchronization():
    """Test state synchronization across agents"""

    agent1 = TestAgent("agent1")
    agent2 = TestAgent("agent2")

    # Set distributed state on agent1
    await agent1.set_distributed_state("shared_data", {"value": 42})

    # Wait for synchronization
    await asyncio.sleep(0.1)

    # Verify agent2 received the update
    shared_data = await agent2.get_distributed_state("shared_data")
    assert shared_data["value"] == 42
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_cross_protocol_state_consistency():
    """Test state consistency across protocol switches"""

    # Start with A2A agent
    a2a_agent = A2AAgent()
    await a2a_agent.set_state("user_data", {"name": "Alice"})

    # Switch to MCP agent (same underlying agent)
    mcp_agent = MCPAgent.from_agent(a2a_agent)

    # Verify state persisted across protocol switch
    user_data = await mcp_agent.get_state("user_data")
    assert user_data["name"] == "Alice"
```

## Performance Considerations

### State Access Optimization

1. **Caching**: Frequently accessed state is cached in memory
2. **Lazy Loading**: State is loaded only when needed
3. **Batch Operations**: Multiple state operations are batched
4. **Connection Pooling**: Database connections are pooled for efficiency

### Memory Management

1. **Automatic Cleanup**: Temporary state is automatically cleaned up
2. **Compression**: Large state objects are compressed
3. **Partitioning**: State is partitioned for better performance
4. **TTL Management**: State with time-to-live is automatically expired

### Distributed Synchronization

1. **Conflict Resolution**: Efficient algorithms for resolving state conflicts
2. **Delta Synchronization**: Only changes are synchronized, not full state
3. **Asynchronous Updates**: Non-critical state updates are asynchronous
4. **Circuit Breakers**: Protection against cascading synchronization failures

## Security Considerations

### State Encryption

```yaml
# Encrypt sensitive state data
state_management:
  security:
    encryption:
      enabled: true
      sensitive_keys: ["api_keys", "user_credentials", "private_data"]
      algorithm: "AES-256-GCM"
```

### Access Control

```yaml
# Control state access by component
state_management:
  security:
    access_control:
      enabled: true
      rules:
        - pattern: "user_*"
          permissions: ["read", "write"]
          principals: ["user_agents"]
        - pattern: "system_*"
          permissions: ["read"]
          principals: ["all_agents"]
```

## Troubleshooting

### Common Issues

1. **State Conflicts**: Use appropriate conflict resolution strategies
2. **Memory Leaks**: Ensure proper cleanup of temporary state
3. **Sync Failures**: Implement retry logic and circuit breakers
4. **Performance Issues**: Use caching and batch operations

### Debugging Tools

```python
# State debugging utilities
async def debug_agent_state(agent):
    """Debug agent state across all layers"""

    debug_info = {
        "agent_id": agent.agent_id,
        "state_layers": {},
        "sync_status": {},
        "performance_metrics": {}
    }

    # Get state from all layers
    for layer in ["permanent", "session", "conversation", "temporary"]:
        layer_state = await agent.get_state_layer(layer)
        debug_info["state_layers"][layer] = {
            "size": len(layer_state),
            "keys": list(layer_state.keys())
        }

    return debug_info
```

## Migration and Versioning

### State Schema Migration

```python
class StateSchemaManager:
    async def migrate_state_schema(self, from_version: str, to_version: str):
        """Migrate state schema between versions"""

        migration_path = self.get_migration_path(from_version, to_version)

        for migration in migration_path:
            await self.apply_migration(migration)

    async def apply_migration(self, migration):
        """Apply a single state migration"""

        # Load existing state
        existing_state = await self.load_all_state()

        # Transform state according to migration
        transformed_state = await migration.transform(existing_state)

        # Save transformed state
        await self.save_all_state(transformed_state)
```

## References

- [Agent Framework Overview](../agent_framework_overview.md)
- [Session Management](../sessions/)
- [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md)
- [State Management API](../../completed/TASK_detail_agent_framework_state_management_api.md)
- [Performance Optimization](../../12_observability/)
- [Security Guidelines](../../17_security/)
