# Multi-Agent Sessions

## Overview

The OpenMAS Multi-Agent Session system enables collaborative scenarios where multiple agents share context and coordinate within a single session. This capability supports sophisticated agent ecosystems while maintaining OpenMAS's core principles of reasoning agnosticism and protocol independence.

## Core Capabilities

The Multi-Agent Session system provides these key capabilities:

1. **Shared Context** - Sharing conversation history and context across agents
2. **Coordination** - Coordinating activities between collaborating agents
3. **Role Management** - Defining and managing agent roles within sessions
4. **State Synchronization** - Synchronizing session state across distributed agents
5. **Cross-Agent Memory** - Managing shared memory across collaborating agents
6. **Protocol-Agnostic Design** - Working consistently across all protocols

## Configuration

Multi-agent sessions are configured through the unified configuration schema:

```yaml
sessions:
  multi_agent:
    enabled: true
    context_sharing:
      strategy: "shared_db"  # shared_db or message_passing
      scoped_by_conversation: true
    coordination:
      orchestrator: "coordinator_agent"  # ID of coordinating agent
      synchronization: "eventual"  # eventual or strict
    role_management:
      enabled: true
      roles:
        - "initiator"
        - "responder"
        - "observer"
      role_assignment: "dynamic"  # static or dynamic
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `enabled` | Whether multi-agent sessions are enabled | false |
| `context_sharing.strategy` | Strategy for sharing context between agents | "shared_db" |
| `context_sharing.scoped_by_conversation` | Whether context sharing is scoped to conversations | true |
| `coordination.orchestrator` | ID of agent orchestrating the collaboration | null |
| `coordination.synchronization` | Synchronization approach (eventual or strict) | "eventual" |
| `role_management.enabled` | Whether role management is enabled | true |
| `role_management.roles` | Available roles for agents | [] |
| `role_management.role_assignment` | How roles are assigned to agents | "dynamic" |

## Context Sharing

Context sharing enables agents to access each other's conversation history:

```yaml
sessions:
  multi_agent:
    context_sharing:
      strategy: "shared_db"
      scoped_by_conversation: true
      visibility: "all"  # all, selective, or role-based
      include_metadata: true
```

### Context Sharing Strategies

The Multi-Agent Session system supports multiple context sharing strategies:

#### 1. Shared Database

Shared Database strategy uses a common storage backend for context:

```yaml
sessions:
  multi_agent:
    context_sharing:
      strategy: "shared_db"
      storage:
        type: "redis"  # redis, database, or file
        # Storage-specific configuration
```

This is ideal for high-performance, distributed scenarios.

#### 2. Message Passing

Message Passing strategy uses explicit message exchange for context:

```yaml
sessions:
  multi_agent:
    context_sharing:
      strategy: "message_passing"
      protocol: "a2a"  # a2a or direct
      compression: true
```

This works well for loosely coupled agent systems.

### Implementation

```python
class MultiAgentContextManager:
    """Manages context sharing across multiple agents."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.enabled = config.get("enabled", False)
        self.sharing_config = config.get("context_sharing", {})
        self.strategy = self.sharing_config.get("strategy", "shared_db")
        self.scoped_by_conversation = self.sharing_config.get("scoped_by_conversation", True)
        self.visibility = self.sharing_config.get("visibility", "all")
        
        # Set up appropriate storage based on strategy
        self.storage = self._create_storage()
    
    def _create_storage(self):
        """Create appropriate storage for the selected strategy."""
        if self.strategy == "shared_db":
            # Use database for shared context
            storage_config = self.sharing_config.get("storage", {})
            storage_type = storage_config.get("type", "redis")
            
            if storage_type == "redis":
                return RedisContextStorage(storage_config)
            elif storage_type == "database":
                return DatabaseContextStorage(storage_config)
            elif storage_type == "file":
                return FileContextStorage(storage_config)
            else:
                return InMemoryContextStorage(storage_config)
        elif self.strategy == "message_passing":
            # Use message passing for context sharing
            return MessagePassingContextStorage(self.sharing_config)
        else:
            # Default to in-memory storage
            return InMemoryContextStorage({})
    
    async def share_context(self, agent_id, conversation_id, context, metadata=None):
        """Share context from an agent."""
        if not self.enabled:
            return
            
        # Get the context key
        context_key = self._get_context_key(agent_id, conversation_id)
        
        # Store in shared storage
        await self.storage.set(context_key, {
            "agent_id": agent_id,
            "conversation_id": conversation_id,
            "context": context,
            "metadata": metadata or {},
            "updated_at": datetime.now().isoformat()
        })
    
    async def get_shared_context(self, agent_id, conversation_id, requester_metadata=None):
        """Get shared context for an agent and conversation."""
        if not self.enabled:
            return []
            
        shared_context = []
        
        if self.scoped_by_conversation:
            # Get all contexts for this conversation
            context_keys = await self.storage.list_by_conversation(conversation_id)
            
            for key in context_keys:
                if key != self._get_context_key(agent_id, conversation_id):  # Skip own context
                    context_data = await self.storage.get(key)
                    if context_data and self._check_visibility(context_data, requester_metadata):
                        shared_context.append(context_data)
        else:
            # Get all contexts (not scoped by conversation)
            context_keys = await self.storage.list_all()
            
            for key in context_keys:
                if not key.startswith(f"{agent_id}:"):  # Skip own contexts
                    context_data = await self.storage.get(key)
                    if context_data and self._check_visibility(context_data, requester_metadata):
                        shared_context.append(context_data)
        
        return shared_context
    
    def _check_visibility(self, context_data, requester_metadata):
        """Check if context is visible to the requester."""
        if self.visibility == "all":
            return True
            
        if self.visibility == "selective":
            # Check if explicitly shared with requester
            shared_with = context_data.get("metadata", {}).get("shared_with", [])
            requester_id = requester_metadata.get("agent_id")
            return not shared_with or requester_id in shared_with
            
        if self.visibility == "role-based":
            # Check if requester's role has access
            context_roles = context_data.get("metadata", {}).get("visible_to_roles", [])
            requester_role = requester_metadata.get("role")
            return not context_roles or requester_role in context_roles
            
        return True
    
    def _get_context_key(self, agent_id, conversation_id):
        """Get the storage key for a context."""
        if self.scoped_by_conversation:
            return f"{agent_id}:{conversation_id}"
        else:
            return f"{agent_id}"
```

## Coordination

Coordination manages the interaction between collaborating agents:

```yaml
sessions:
  multi_agent:
    coordination:
      orchestrator: "coordinator_agent"
      synchronization: "eventual"
      protocol:
        type: "turn_based"  # turn_based, event_driven, or task_delegation
        config:
          timeout_seconds: 30
```

### Synchronization Approaches

#### 1. Eventual Consistency

Eventual consistency allows for looser coordination:

```yaml
sessions:
  multi_agent:
    coordination:
      synchronization: "eventual"
      consistency_check_interval: 5  # seconds
```

This approach is more flexible but may lead to temporary inconsistencies.

#### 2. Strict Consistency

Strict consistency enforces immediate synchronization:

```yaml
sessions:
  multi_agent:
    coordination:
      synchronization: "strict"
      locking:
        enabled: true
        timeout_ms: 5000
```

This ensures data integrity but may impact performance.

### Implementation

```python
class MultiAgentCoordinator:
    """Coordinates activities between multiple agents."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.enabled = config.get("enabled", False)
        self.coordination_config = config.get("coordination", {})
        self.orchestrator = self.coordination_config.get("orchestrator")
        self.synchronization = self.coordination_config.get("synchronization", "eventual")
        self.protocol_config = self.coordination_config.get("protocol", {})
        self.protocol_type = self.protocol_config.get("type", "turn_based")
        
        # Set up appropriate protocol
        self.protocol = self._create_protocol()
    
    def _create_protocol(self):
        """Create appropriate coordination protocol."""
        if self.protocol_type == "turn_based":
            return TurnBasedProtocol(self.protocol_config)
        elif self.protocol_type == "event_driven":
            return EventDrivenProtocol(self.protocol_config)
        elif self.protocol_type == "task_delegation":
            return TaskDelegationProtocol(self.protocol_config)
        else:
            return TurnBasedProtocol({})
    
    async def register_agent(self, agent_id, metadata=None):
        """Register an agent with the coordinator."""
        if not self.enabled:
            return
            
        await self.protocol.register_participant(agent_id, metadata)
    
    async def unregister_agent(self, agent_id):
        """Unregister an agent from the coordinator."""
        if not self.enabled:
            return
            
        await self.protocol.unregister_participant(agent_id)
    
    async def get_next_action(self, agent_id, conversation_id):
        """Get the next action for an agent."""
        if not self.enabled:
            return {"can_act": True}
            
        return await self.protocol.get_next_action(agent_id, conversation_id)
    
    async def notify_action_complete(self, agent_id, conversation_id, action_data):
        """Notify that an agent has completed an action."""
        if not self.enabled:
            return
            
        await self.protocol.notify_action_complete(agent_id, conversation_id, action_data)
    
    async def get_conversation_state(self, conversation_id):
        """Get the current state of a conversation."""
        if not self.enabled:
            return {"active": True}
            
        return await self.protocol.get_conversation_state(conversation_id)
```

## Role Management

Role management defines and manages agent roles within multi-agent sessions:

```yaml
sessions:
  multi_agent:
    role_management:
      enabled: true
      roles:
        - name: "initiator"
          permissions: ["start_conversation", "invite_agent"]
        - name: "responder"
          permissions: ["respond", "delegate"]
        - name: "observer"
          permissions: ["view"]
      default_role: "responder"
      role_assignment: "dynamic"  # static or dynamic
```

### Role Assignment Strategies

#### 1. Static Assignment

Static assignment defines roles in configuration:

```yaml
sessions:
  multi_agent:
    role_management:
      role_assignment: "static"
      agent_roles:
        coordinator_agent: "initiator"
        assistant_agent: "responder"
        analytics_agent: "observer"
```

#### 2. Dynamic Assignment

Dynamic assignment allows roles to be assigned at runtime:

```yaml
sessions:
  multi_agent:
    role_management:
      role_assignment: "dynamic"
      assignment_strategy: "first_come"  # first_come, capability_based, or rule_based
```

### Implementation

```python
class RoleManager:
    """Manages agent roles in multi-agent sessions."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.enabled = config.get("enabled", False)
        self.roles_config = config.get("role_management", {})
        self.roles = self.roles_config.get("roles", [])
        self.default_role = self.roles_config.get("default_role", "responder")
        self.assignment_strategy = self.roles_config.get("role_assignment", "dynamic")
        
        # Initialize role storage
        self.role_assignments = {}
    
    async def get_agent_role(self, agent_id, conversation_id):
        """Get the role for an agent in a conversation."""
        if not self.enabled:
            return self.default_role
            
        if self.assignment_strategy == "static":
            # Check static role assignments
            agent_roles = self.roles_config.get("agent_roles", {})
            return agent_roles.get(agent_id, self.default_role)
        else:
            # Check dynamic role assignments
            conversation_key = f"{conversation_id}"
            if conversation_key in self.role_assignments:
                return self.role_assignments[conversation_key].get(agent_id, self.default_role)
            
            return self.default_role
    
    async def assign_role(self, agent_id, conversation_id, role):
        """Assign a role to an agent in a conversation."""
        if not self.enabled:
            return
            
        # Validate role
        if role not in [r.get("name") if isinstance(r, dict) else r for r in self.roles]:
            raise ValueError(f"Invalid role: {role}")
            
        conversation_key = f"{conversation_id}"
        if conversation_key not in self.role_assignments:
            self.role_assignments[conversation_key] = {}
            
        self.role_assignments[conversation_key][agent_id] = role
    
    async def check_permission(self, agent_id, conversation_id, permission):
        """Check if an agent has a specific permission."""
        if not self.enabled:
            return True
            
        # Get agent role
        role = await self.get_agent_role(agent_id, conversation_id)
        
        # Find role definition
        role_def = None
        for r in self.roles:
            if isinstance(r, dict) and r.get("name") == role:
                role_def = r
                break
            elif r == role:
                # Simple role without permissions defined
                return True
                
        if not role_def:
            return False
            
        # Check permission
        permissions = role_def.get("permissions", [])
        return permission in permissions
```

## State Synchronization

State synchronization ensures consistent state across distributed agents:

```yaml
sessions:
  multi_agent:
    state_synchronization:
      enabled: true
      strategy: "distributed"  # centralized or distributed
      conflict_resolution: "last_write_wins"  # last_write_wins, merge, or custom
```

### Synchronization Strategies

#### 1. Centralized Synchronization

Centralized synchronization uses a central authority:

```yaml
sessions:
  multi_agent:
    state_synchronization:
      strategy: "centralized"
      authority: "coordinator_agent"
      update_interval_ms: 1000
```

#### 2. Distributed Synchronization

Distributed synchronization uses peer-to-peer updates:

```yaml
sessions:
  multi_agent:
    state_synchronization:
      strategy: "distributed"
      gossip_interval_ms: 500
      quorum_size: 2
```

### Implementation

```python
class StateSynchronizer:
    """Synchronizes state across multiple agents."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.enabled = config.get("enabled", False)
        self.sync_config = config.get("state_synchronization", {})
        self.strategy = self.sync_config.get("strategy", "centralized")
        self.conflict_resolution = self.sync_config.get("conflict_resolution", "last_write_wins")
        
        # Initialize state storage
        self.state_versions = {}
        self.state_storage = {}
    
    async def update_state(self, agent_id, conversation_id, key, value, version=None):
        """Update a state value."""
        if not self.enabled:
            return
            
        state_key = f"{conversation_id}:{key}"
        
        # Get current version number
        current_version = self.state_versions.get(state_key, 0)
        
        # Use provided version or increment
        if version is None:
            version = current_version + 1
            
        # Check version for conflicts
        if self.strategy == "centralized" or version > current_version:
            # Update state
            self.state_storage[state_key] = value
            self.state_versions[state_key] = version
            return True
        elif version == current_version:
            # Same version, resolve conflict
            if self.conflict_resolution == "last_write_wins":
                # Just update with the new value
                self.state_storage[state_key] = value
                return True
            elif self.conflict_resolution == "merge":
                # Attempt to merge values
                merged_value = self._merge_values(self.state_storage[state_key], value)
                self.state_storage[state_key] = merged_value
                self.state_versions[state_key] = version + 1
                return True
        
        # Version conflict
        return False
    
    async def get_state(self, conversation_id, key, default=None):
        """Get a state value."""
        if not self.enabled:
            return default
            
        state_key = f"{conversation_id}:{key}"
        return self.state_storage.get(state_key, default)
    
    async def get_state_version(self, conversation_id, key):
        """Get the version of a state value."""
        if not self.enabled:
            return 0
            
        state_key = f"{conversation_id}:{key}"
        return self.state_versions.get(state_key, 0)
    
    def _merge_values(self, value1, value2):
        """Merge two values."""
        if isinstance(value1, dict) and isinstance(value2, dict):
            # Merge dictionaries
            result = value1.copy()
            result.update(value2)
            return result
        elif isinstance(value1, list) and isinstance(value2, list):
            # Merge lists (deduplicate)
            return list(set(value1 + value2))
        else:
            # Default to newer value
            return value2
```

## Cross-Protocol Support

The Multi-Agent Session system works consistently across all protocols:

### A2A Task Integration

A2A task integration maps multi-agent sessions to A2A tasks:

```yaml
sessions:
  multi_agent:
    protocol_integration:
      a2a:
        enabled: true
        task_sharing: true
        artifact_sharing: true
```

This enables collaboration using A2A's task and artifact mechanisms.

### MCP Integration

MCP integration handles multi-agent sessions in the MCP protocol:

```yaml
sessions:
  multi_agent:
    protocol_integration:
      mcp:
        enabled: true
        resource_sharing: true
        tool_sharing: true
```

This facilitates collaboration through MCP's resources and tools.

## Reasoning Agnosticism

The Multi-Agent Session system maintains OpenMAS's reasoning agnosticism by:

1. **Message Format Neutrality** - Using neutral formats compatible with any reasoning approach
2. **Content Neutrality** - Not making assumptions about the semantics of shared content
3. **Role Flexibility** - Supporting various agent roles regardless of reasoning approach
4. **Configurable Coordination** - Allowing tuning for different reasoning needs

This ensures that agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) can collaborate without compatibility issues.

## Protocol Independence

The Multi-Agent Session system ensures protocol independence by:

1. **Protocol Adapters** - Adapting multi-agent sessions for different protocol requirements
2. **Common Session Model** - Using a standardized internal session representation
3. **Unified Configuration** - Consistent configuration across protocols

This allows multi-agent sessions to work consistently whether using A2A, MCP, or other protocols.

## Use Cases

The Multi-Agent Session system supports various collaborative scenarios:

### 1. Expert Collaboration

Multiple specialized agents collaborate to solve complex problems:

```yaml
agents:
  research_agent:
    class: "agents.specialized.ResearchAgent"
    sessions:
      multi_agent:
        role_management:
          static_role: "information_provider"
  
  synthesis_agent:
    class: "agents.specialized.SynthesisAgent"
    sessions:
      multi_agent:
        role_management:
          static_role: "coordinator"
  
  critic_agent:
    class: "agents.specialized.CriticAgent"
    sessions:
      multi_agent:
        role_management:
          static_role: "reviewer"
```

### 2. Workflow Orchestration

Agents form a workflow with sequential processing:

```yaml
sessions:
  multi_agent:
    coordination:
      protocol:
        type: "task_delegation"
        workflow:
          - agent: "intake_agent"
            next: "processing_agent"
          - agent: "processing_agent"
            next: "quality_agent"
          - agent: "quality_agent"
            next: "delivery_agent"
```

### 3. Distributed Problem Solving

Agents solve parts of a larger problem:

```yaml
sessions:
  multi_agent:
    coordination:
      protocol:
        type: "event_driven"
        events:
          - name: "problem_decomposed"
            subscribers: ["solver_agent_1", "solver_agent_2"]
          - name: "solution_found"
            subscribers: ["integration_agent"]
```

## Integration with Other Components

The Multi-Agent Session system integrates with several other OpenMAS components:

1. **Session Management** - Building upon the core session capabilities
2. **Agent Framework** - Supporting agent-specific roles and capabilities
3. **Topology Management** - Aligning with the agent topology
4. **Communication Pattern Engine** - Using standard communication patterns
5. **Unified Configuration** - Using the schema-based configuration system
