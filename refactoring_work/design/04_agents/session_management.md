# Session Management and Agent Lifecycle Standard

## Session Definition
- **Name**: Session Management
- **Purpose**: Standardized approach to session state persistence and agent lifecycle management
- **Protocol Compatibility**: Supports session management across multiple protocols
- **Task/Session Mapping**: Maps between A2A task lifecycle and MCP session concepts
- **Reasoning Agnosticism**: Maintains separation between session management and reasoning approaches

## Session Schema
```yaml
# Standardized session configuration schema
type: object
properties:
  # System-level session configuration
  sessions:
    type: object
    description: "Global session management configuration"
    properties:
      enabled:
        type: boolean
        description: "Whether session management is enabled"
        default: true
      
      # Storage configuration
      storage:
        type: object
        description: "Session storage configuration"
        properties:
          type:
            type: string
            description: "Storage backend type"
            enum: ["database", "file", "memory", "redis"]
          connection_string:
            type: string
            description: "Connection string for database or redis storage"
          table_name:
            type: string
            description: "Table or collection name for database storage"
          expiration:
            type: integer
            description: "Session expiration time in seconds"
            default: 604800
      
      # Protocol-specific session configuration
      protocol_sessions:
        type: object
        description: "Protocol-specific session configurations"
        properties:
          # A2A task session configuration
          a2a:
            type: object
            description: "A2A task management configuration"
            properties:
              enabled:
                type: boolean
                description: "Whether A2A task management is enabled"
                default: true
              states:
                type: array
                description: "Supported task states"
                default: ["submitted", "working", "input_required", "completed", "failed"]
                items:
                  type: string
                  enum: ["submitted", "working", "input_required", "completed", "failed"]
              persistence:
                type: object
                description: "Task persistence configuration"
                properties:
                  ttl_seconds:
                    type: integer
                    description: "Time-to-live for tasks in seconds"
                    default: 3600
                  cleanup_interval:
                    type: integer
                    description: "Interval for cleaning up expired tasks in seconds"
                    default: 300
                  state_transitions:
                    type: object
                    description: "Configuration for state transition behavior"
                    
          # MCP session configuration
          mcp:
            type: object
            description: "MCP session management configuration"
            properties:
              enabled:
                type: boolean
                description: "Whether MCP session management is enabled"
                default: true
              session_tracking:
                type: boolean
                description: "Whether to track MCP sessions"
                default: true
              session_id_header:
                type: string
                description: "HTTP header for MCP session ID"
                default: "X-MCP-Session-ID"
              persistence:
                type: object
                description: "Session persistence configuration"
                properties:
                  ttl_seconds:
                    type: integer
                    description: "Time-to-live for sessions in seconds"
                    default: 3600
                properties:
                  log_transitions:
                    type: boolean
                    description: "Whether to log state transitions"
                    default: true
                  allow_custom_states:
                    type: boolean
                    description: "Whether to allow custom states beyond A2A standard"
                    default: false
        required:
          - type
      
      # A2A Message and Artifact Storage
      message_storage:
        type: object
        description: "Configuration for storing A2A messages and artifacts"
        properties:
          store_messages:
            type: boolean
            description: "Whether to store messages in the session"
            default: true
          store_artifacts:
            type: boolean
            description: "Whether to store artifacts in the session"
            default: true
          artifact_storage:
            type: object
            description: "Configuration for artifact storage"
            properties:
              location:
                type: string
                description: "Storage location for artifacts"
                default: "./artifacts"
              inline_threshold_kb:
                type: integer
                description: "Threshold in KB for storing artifacts inline vs. as files"
                default: 64
              retention_policy:
                type: string
                description: "Retention policy for artifacts"
                enum: ["session", "permanent", "custom"]
                default: "session"
  
      # Context management configuration
      context:
        type: object
        description: "Context management configuration"
        properties:
          max_history_items:
            type: integer
            description: "Maximum number of history items to store"
            default: 50
          max_tokens:
            type: integer
            description: "Maximum number of tokens in context"
            default: 4000
          pruning_strategy:
            type: string
            description: "Strategy for pruning context when exceeding limits"
            enum: ["fifo", "selective", "summarize"]
            default: "selective"
        
      # A2A task integration
      task_integration:
        type: object
        description: "Integration with A2A task management"
        properties:
          enabled:
            type: boolean
            description: "Whether A2A task integration is enabled"
            default: true
          task_session_mapping:
            type: string
            description: "Mapping between tasks and sessions"
            enum: ["one_to_one", "many_to_one", "one_to_many"]
            default: "one_to_one"
    
    required:
      - enabled
```

## Integration with JSONSchema/Pydantic Validation

This session configuration schema can be directly implemented using Pydantic models for validation:

```python
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Union, Literal, Any
from enum import Enum

class TaskState(str, Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input_required"
    COMPLETED = "completed"
    FAILED = "failed"

class StorageConfig(BaseModel):
    type: Literal["database", "file", "memory", "redis"] = "memory"
    connection_string: Optional[str] = None
    table_name: Optional[str] = None
    expiration: int = 604800  # 7 days default
    
    @validator("connection_string")
    def validate_connection_string(cls, v, values):
        if values.get("type") in ["database", "redis"] and not v:
            raise ValueError(f"Connection string required for {values.get('type')} storage")
        return v

class A2APersistenceConfig(BaseModel):
    ttl_seconds: int = 3600
    cleanup_interval: int = 300
    state_transitions: Dict[str, Any] = Field(default_factory=dict)

class A2ASessionConfig(BaseModel):
    enabled: bool = True
    states: List[TaskState] = Field(default_factory=lambda: list(TaskState))
    persistence: A2APersistenceConfig = Field(default_factory=A2APersistenceConfig)

class MCPSessionConfig(BaseModel):
    enabled: bool = True
    session_tracking: bool = True
    session_id_header: str = "X-MCP-Session-ID"
    persistence: Dict[str, Any] = Field(default_factory=lambda: {"ttl_seconds": 3600})

class ContextConfig(BaseModel):
    max_history_items: int = 50
    max_tokens: int = 4000
    retention_strategy: str = "sliding_window"

class ProtocolSessionsConfig(BaseModel):
    a2a: A2ASessionConfig = Field(default_factory=A2ASessionConfig)
    mcp: MCPSessionConfig = Field(default_factory=MCPSessionConfig)

class SessionConfig(BaseModel):
    enabled: bool = True
    storage: StorageConfig = Field(default_factory=StorageConfig)
    protocol_sessions: ProtocolSessionsConfig = Field(default_factory=ProtocolSessionsConfig)
    context: ContextConfig = Field(default_factory=ContextConfig)
```

Using Pydantic enables:
- Type safety and automatic validation
- IDE support with type hints
- Runtime validation when loading configuration
- JSON Schema generation for documentation
- Seamless integration with OpenAPI for API documentation

## Complete Configuration Examples

### Multi-Protocol Session Configuration

```yaml
# Example of session configuration supporting both A2A and MCP
sessions:
  enabled: true
  storage:
    type: "database"
    connection_string: "${DATABASE_URL}"
    table_name: "sessions"
    expiration: 604800
  protocol_sessions:
    a2a:
      enabled: true
      states: ["submitted", "working", "input_required", "completed", "failed"]
      persistence:
        ttl_seconds: 7200
        cleanup_interval: 600
        state_transitions:
          log_transitions: true
          allow_custom_states: false
    mcp:
      enabled: true
      session_tracking: true
      session_id_header: "X-MCP-Session-ID"
      persistence:
        ttl_seconds: 3600
  context:
    max_history_items: 100
    max_tokens: 8000
    retention_strategy: "sliding_window"
    include_context_metadata: true
```

### A2A-Only Session Configuration

```yaml
# Example of session configuration for A2A-only deployment
sessions:
  enabled: true
  storage:
    type: "memory"
    expiration: 3600
  protocol_sessions:
    a2a:
      enabled: true
      states: ["submitted", "working", "input_required", "completed", "failed"]
      persistence:
        ttl_seconds: 3600
    mcp:
      enabled: false
  context:
    max_history_items: 50
    max_tokens: 4000
```

### MCP-Only Session Configuration

```yaml
# Example of session configuration for MCP-only deployment
sessions:
  enabled: true
  storage:
    type: "redis"
    connection_string: "${REDIS_URL}"
    expiration: 7200
  protocol_sessions:
    a2a:
      enabled: false
    mcp:
      enabled: true
      session_tracking: true
      session_id_header: "X-MCP-Session-ID"
  context:
    max_history_items: 50
    max_tokens: 4000
```

## Agent-Level Session Configuration
```yaml
# Agent-specific session configuration
type: object
properties:
  agents:
    type: object
    description: "Agent configuration"
    additionalProperties:
      type: object
      properties:
        # Agent configuration
        module:
          type: string
          description: "Agent module path"
        class:
          type: string
          description: "Agent class name"
        
        # Agent-specific session configuration
        sessions:
          type: object
          description: "Agent-specific session configuration"
          properties:
            context:
              type: object
              description: "Session context configuration"
              properties:
                max_history_items:
                  type: integer
                  description: "Maximum number of history items to store"
                max_tokens:
                  type: integer
                  description: "Maximum number of tokens in context"
            storage:
              type: object
              description: "Session storage configuration"
              properties:
                expiration:
                  type: integer
                  description: "Session expiration time in seconds"
                # Other storage overrides

        # Session lifecycle hooks
        lifecycle:
          type: object
          description: "Agent lifecycle hooks"
          properties:
            on_startup:
              type: array
              description: "Actions to perform on agent startup"
              items:
                type: string
            on_shutdown:
              type: array
              description: "Actions to perform on agent shutdown"
              items:
                type: string
      required:
        - module
        - class
```

## A2A Protocol Alignment
- **A2A Task Persistence**: Session management aligns with A2A task persistence through:
  - Persistent storage options (database, file, memory, redis)
  - Task delegation and tracking (task_session_mapping)
  - State preservation across agent restarts (lifecycle hooks)

## Session Lifecycle Management
- **Session Creation**: [When and how sessions are created]
- **Session Loading**: [How sessions are loaded from storage]
- **Session Updating**: [How sessions are updated during agent execution]
- **Session Persistence**: [How sessions are persisted to storage]
- **Session Expiration**: [How session expiration is handled]

## A2A Task Lifecycle Management

This section defines how OpenMAS manages the A2A task lifecycle.

### Task States

In accordance with the A2A protocol, tasks can exist in the following states:

1. **submitted**: The initial state when a task is created and sent to the agent
2. **working**: The agent is actively working on the task
3. **input_required**: The agent needs additional input from the client to proceed
4. **completed**: The task has been successfully completed
5. **failed**: The task could not be completed due to an error

### State Transitions

Allowed state transitions follow the A2A protocol specification:

- submitted → working
- submitted → failed
- working → input_required
- working → completed
- working → failed
- input_required → working (after input is provided)
- input_required → failed

### Task Storage

Tasks are stored according to the configured storage mechanism with the following considerations:

- Task ID acts as the unique identifier
- Full state history is maintained (configurable)
- Tasks can be retrieved by ID or queried by state
- Expired tasks are automatically cleaned up based on TTL

## Multi-Agent Session Coordination
- **Shared Sessions**: [How sessions can be shared between agents]
- **Task Delegation**: [How tasks are delegated between agents with session context]
- **Context Synchronization**: [How session context is synchronized between agents]

## Session Performance Considerations
- **Memory Usage**: [Memory usage considerations for different storage types]
- **Performance Impact**: [Performance impact of session management]
- **Scaling Considerations**: [How session management scales with number of agents]

## Testing
- **Unit Test Requirements**: [Session-specific test requirements]
- **Integration Test Requirements**: [Session integration test requirements]
- **Mock vs Real Testing**: [How to test with mock vs real storage backends]

## Usage Examples
```python
# Example session management usage in agent implementation
from openmas.sessions import SessionManager

class MyAgent:
    def __init__(self, config):
        self.session_manager = SessionManager(config["sessions"])
    
    async def on_startup(self):
        # Load session on startup
        self.session = await self.session_manager.load_session(self.agent_id)
    
    async def process_message(self, message):
        # Update session with message
        self.session.add_message(message)
        
        # Use session context in processing
        response = await self.generate_response(self.session.get_context())
        
        # Update session with response
        self.session.add_message(response)
        
        # Persist session
        await self.session_manager.save_session(self.session)
        
        return response
    
    async def on_shutdown(self):
        # Save session on shutdown
        await self.session_manager.save_session(self.session) 