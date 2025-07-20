# Session Management System Design

## Overview

The OpenMAS Session Management system provides a comprehensive framework for handling persistent interactions, state management, and conversation context across all protocols. It ensures consistent session behavior while maintaining OpenMAS's core architectural principles of reasoning agnosticism and protocol independence.

## Core Principles

1. **Protocol Independence** - Session management works consistently across all protocols (A2A, MCP, HTTP, etc.)
2. **Reasoning Agnosticism** - Session handling is completely independent of reasoning approaches
3. **State Persistence** - Reliable storage and retrieval of session state across interactions
4. **Context Preservation** - Effective management of conversation history and context
5. **Consistent Identification** - Unified approach to session identification and tracking
6. **Multi-Agent Support** - First-class support for sessions spanning multiple agents
7. **Configurable Behavior** - Highly configurable through the unified configuration schema

## Architecture Components

The session management system consists of these key components:

### 1. SessionManager

The SessionManager serves as the central coordinator for all session operations:

- Session creation, retrieval, and expiration handling
- Lifecycle management (initialization, maintenance, termination)
- Integration with agent components
- Protocol-specific adaptations

### 2. SessionStorage

The SessionStorage component provides persistence mechanisms for session data:

- Abstract storage interface
- Multiple storage backend implementations
- Serialization and deserialization of session data
- Configurable expiration and cleanup

### 3. ContextManager

The ContextManager handles conversation history and context:

- History tracking and organization
- Context window management
- Intelligent pruning strategies
- Relevance assessment and prioritization

### 4. SessionAnalytics

The SessionAnalytics component provides monitoring and analysis:

- Event tracking and recording
- Performance and utilization metrics
- Analytics data export
- Integration with observability system

## Session Configuration Schema

The session management system uses the following configuration schema, which is part of the unified configuration schema:

```yaml
# Session configuration
sessions:
  # Global session management configuration
  enabled: boolean (optional, default=true)

  # Storage configuration
  storage:
    type: string (memory | file | database | redis)
    # Memory storage
    expiration: integer (optional, seconds)

    # File storage
    directory: string (optional)
    format: string (optional, json | pickle | yaml)

    # Database storage
    connection_string: string (optional)
    table_name: string (optional)

    # Redis storage
    host: string (optional)
    port: integer (optional)
    db: integer (optional)
    prefix: string (optional)

  # Context management
  context:
    max_history_items: integer (optional, default=50)
    max_tokens: integer (optional, default=4000)
    pruning_strategy: string (optional, truncate | summarize | selective)
    pruning_config:
      preserve_system_messages: boolean (optional, default=true)
      preserve_last_n_exchanges: integer (optional, default=5)
      summarization_prompt: string (optional)

  # Protocol-specific session configuration
  protocol_sessions:
    # A2A task session configuration
    a2a:
      enabled: boolean (optional, default=true)
      states: array[string] (optional, states enum)
      persistence:
        ttl_seconds: integer (optional, default=3600)
        cleanup_interval: integer (optional, default=300)
        log_transitions: boolean (optional, default=true)
        allow_custom_states: boolean (optional, default=false)

    # MCP session configuration
    mcp:
      enabled: boolean (optional, default=true)
      session_tracking: boolean (optional, default=true)
      session_id_header: string (optional)
      persistence:
        ttl_seconds: integer (optional, default=3600)

  # Message and artifact storage
  message_storage:
    store_messages: boolean (optional, default=true)
    store_artifacts: boolean (optional, default=true)
    artifact_storage:
      location: string (optional, default=./artifacts)
      inline_threshold_kb: integer (optional, default=64)
      retention_policy: string (optional, session | permanent | custom)

  # User identification
  user_identification:
    enabled: boolean (optional, default=true)
    strategy: string (optional, token | session_id | auth)
    auth:
      provider: string (optional)
      claims: object (optional)

  # Multi-agent session configuration
  multi_agent:
    enabled: boolean (optional, default=false)
    context_sharing:
      strategy: string (optional, shared_db | message_passing)
      scoped_by_conversation: boolean (optional, default=true)
    coordination:
      orchestrator: string (optional)
      synchronization: string (optional, eventual | strict)

  # Analytics configuration
  analytics:
    enabled: boolean (optional, default=false)
    tracking_level: string (optional, minimal | standard | detailed)
    events: array[string] (optional)
    metrics: array[string] (optional)
    destinations: array[object] (optional)
```

## Storage Backends

The session management system supports multiple storage backends:

### Memory Storage

Memory storage keeps session data in memory, suitable for development or ephemeral sessions:

```yaml
sessions:
  storage:
    type: "memory"
    expiration: 3600  # in seconds
```

Memory storage is fast but non-persistent across restarts.

### File Storage

File storage persists sessions to the file system:

```yaml
sessions:
  storage:
    type: "file"
    directory: "./sessions"
    format: "json"  # or pickle, yaml
    expiration: 86400  # in seconds
```

File storage provides simple persistence suitable for single-server deployments.

### Database Storage

Database storage persists sessions to a database:

```yaml
sessions:
  storage:
    type: "database"
    connection_string: "${DB_CONNECTION_STRING}"
    table_name: "agent_sessions"
    expiration: 604800  # in seconds (7 days)
```

Database storage is ideal for production environments with multiple servers.

### Redis Storage

Redis storage uses Redis for session management:

```yaml
sessions:
  storage:
    type: "redis"
    host: "${REDIS_HOST:-localhost}"
    port: "${REDIS_PORT:-6379}"
    db: 0
    prefix: "openmas:session:"
    expiration: 86400  # in seconds
```

Redis storage provides high-performance, distributed session management.

## Context Management

Context management controls how conversation history is handled:

```yaml
sessions:
  context:
    max_history_items: 50
    max_tokens: 4000
    pruning_strategy: "selective"
    pruning_config:
      preserve_system_messages: true
      preserve_last_n_exchanges: 5
      summarization_prompt: "summarize_context"
```

### Pruning Strategies

The session management system supports multiple pruning strategies:

1. **Truncate** - Simple truncation of oldest messages when limits are reached
2. **Summarize** - Summarization of older parts of the conversation
3. **Selective** - Intelligent selection of which messages to preserve based on relevance

## Protocol Integration

### A2A Task Integration

The session management system integrates with the A2A task protocol:

```yaml
sessions:
  protocol_sessions:
    a2a:
      enabled: true
      states: ["submitted", "working", "input_required", "completed", "failed"]
      persistence:
        ttl_seconds: 3600
        log_transitions: true
        allow_custom_states: false
```

A2A task integration maps session concepts to A2A task lifecycle.

### MCP Session Integration

The session management system integrates with the MCP protocol:

```yaml
sessions:
  protocol_sessions:
    mcp:
      enabled: true
      session_tracking: true
      session_id_header: "X-MCP-Session-ID"
      persistence:
        ttl_seconds: 3600
```

MCP session integration provides consistent session handling for MCP interactions.

## User Identification

User identification configures how users are identified in sessions:

```yaml
sessions:
  user_identification:
    enabled: true
    strategy: "auth"
    auth:
      provider: "jwt"
      claims:
        user_id: "sub"
        name: "name"
        email: "email"
```

User identification ensures continuity across multiple interactions from the same user.

## Multi-Agent Sessions

Multi-agent sessions enable context sharing across agents:

```yaml
sessions:
  multi_agent:
    enabled: true
    context_sharing:
      strategy: "shared_db"
      scoped_by_conversation: true
    coordination:
      orchestrator: "coordinator_agent"
      synchronization: "eventual"  # or strict
```

Multi-agent sessions support collaborative agent interactions with shared context.

## Analytics Configuration

Analytics configuration controls session tracking and analysis:

```yaml
sessions:
  analytics:
    enabled: true
    tracking_level: "standard"
    events:
      - "session_start"
      - "session_end"
      - "user_message"
      - "agent_response"
      - "error"
    metrics:
      - "response_time"
      - "token_count"
      - "session_duration"
    destinations:
      - type: "log"
        format: "json"
      - type: "database"
        connection_string: "${ANALYTICS_DB}"
```

Analytics provides insights into session performance and usage patterns.

## Agent-Specific Session Configuration

Individual agents can have specific session configurations:

```yaml
agents:
  example_agent:
    # Agent configuration
    module: "agents.example"
    class: "ExampleAgent"

    # Agent-specific session configuration
    sessions:
      context:
        max_history_items: 100
        pruning_strategy: "summarize"
      storage:
        type: "redis"
        expiration: 172800  # 48 hours
```

This allows customization of session behavior per agent.

## Implementation Architecture

The session management system is implemented with these classes:

### SessionManager

The SessionManager provides centralized session management:

```python
class SessionManager:
    """Central manager for all sessions."""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.storage = self._create_storage(config.get("storage", {}))
        self.context_manager = ContextManager(config.get("context", {}))
        self.analytics = SessionAnalytics(config.get("analytics", {})) if config.get("analytics", {}).get("enabled", False) else None

    def _create_storage(self, storage_config):
        """Create the appropriate storage backend."""
        storage_type = storage_config.get("type", "memory")

        if storage_type == "memory":
            return MemoryStorage(storage_config)
        elif storage_type == "file":
            return FileStorage(storage_config)
        elif storage_type == "database":
            return DatabaseStorage(storage_config)
        elif storage_type == "redis":
            return RedisStorage(storage_config)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")

    async def get_session(self, session_id):
        """Get a session by ID, creating if it doesn't exist."""
        session = await self.storage.get(session_id)
        if not session:
            session = await self.create_session(session_id)
        return session

    async def create_session(self, session_id, metadata=None):
        """Create a new session."""
        session = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "metadata": metadata or {},
            "history": [],
            "state": {}
        }
        await self.storage.set(session_id, session)

        # Track analytics if enabled
        if self.analytics:
            await self.analytics.track_event("session_start", session_id)

        return session

    async def update_session(self, session_id, update_fn):
        """Update a session using an update function."""
        session = await self.get_session(session_id)
        updated_session = update_fn(session)
        updated_session["last_accessed"] = datetime.now().isoformat()
        await self.storage.set(session_id, updated_session)
        return updated_session

    async def add_message(self, session_id, message):
        """Add a message to a session's history."""
        async def _add_message(session):
            if "history" not in session:
                session["history"] = []

            session["history"].append({
                "timestamp": datetime.now().isoformat(),
                "message": message
            })

            # Apply context management
            session["history"] = await self.context_manager.prune_history(session["history"])

            return session

        session = await self.update_session(session_id, _add_message)

        # Track analytics if enabled
        if self.analytics:
            message_type = message.get("role", "unknown")
            await self.analytics.track_event(f"{message_type}_message", session_id)

        return session

    async def set_state(self, session_id, key, value):
        """Set a state value in the session."""
        async def _set_state(session):
            if "state" not in session:
                session["state"] = {}

            session["state"][key] = value
            return session

        return await self.update_session(session_id, _set_state)

    async def get_state(self, session_id, key, default=None):
        """Get a state value from the session."""
        session = await self.get_session(session_id)
        return session.get("state", {}).get(key, default)

    async def end_session(self, session_id):
        """End a session."""
        # Track analytics if enabled
        if self.analytics:
            await self.analytics.track_event("session_end", session_id)

        return await self.storage.delete(session_id)
```

### Context Management

Context management is implemented with a dedicated component:

```python
class ContextManager:
    """Manages conversation context and history."""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.max_history_items = config.get("max_history_items", 50)
        self.max_tokens = config.get("max_tokens", 4000)
        self.strategy = config.get("pruning_strategy", "selective")
        self.pruning_config = config.get("pruning_config", {})

    async def prune_history(self, history):
        """Prune history based on configured strategy."""
        if len(history) <= self.max_history_items:
            return history

        if self.strategy == "truncate":
            return history[-self.max_history_items:]
        elif self.strategy == "summarize":
            return await self._summarize_history(history)
        elif self.strategy == "selective":
            return await self._selective_prune(history)
        else:
            # Default to truncation
            return history[-self.max_history_items:]

    async def _summarize_history(self, history):
        """Summarize older parts of history."""
        # Implementation of history summarization
        pass

    async def _selective_prune(self, history):
        """Selectively prune less important messages."""
        # Implementation of selective pruning
        pass

    async def get_token_count(self, history):
        """Estimate token count for history."""
        # Implementation of token counting
        pass
```

## Reasoning Agnosticism

The session management system maintains OpenMAS's reasoning agnosticism by:

1. **Protocol-Independent Design** - Sessions work consistently regardless of protocol
2. **Reasoning-Independent State** - Session state is independent of reasoning approaches
3. **Content Neutrality** - Session management handles content without reasoning-specific assumptions
4. **Clean Interfaces** - Clear separation between session management and reasoning components

This ensures that agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) can use the same session management infrastructure without modification.

## Protocol Independence

The session management system ensures protocol independence by:

1. **Unified Session Model** - Common session model across all protocols
2. **Protocol-Specific Adapters** - Adapters for protocol-specific behaviors
3. **Protocol-Agnostic Storage** - Storage backends work identically across protocols
4. **Consistent Identification** - Unified approach to session identification

This allows sessions to work consistently whether using A2A, MCP, or other protocols.

## Integration with Other Components

The session management system integrates with several other OpenMAS components:

1. **Agent Framework** - Provides session management for individual agents
2. **Protocol Layer** - Ensures consistent session handling across protocols
3. **Configuration System** - Defines session configuration via unified schema
4. **Asset Management** - Handles session-related assets and attachments
5. **Security System** - Manages authentication and authorization for sessions

This integration ensures a cohesive user experience across the entire framework.
