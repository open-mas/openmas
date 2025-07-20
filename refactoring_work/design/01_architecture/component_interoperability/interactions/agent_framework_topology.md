# Agent Framework ↔ Topology System

## Relationship Summary
- **Agent Framework → Topology System**: Depends On
- **Topology System → Agent Framework**: Provides To

## Interface Definitions

### Agent Framework → Topology System

#### Methods/Functions

```python
def discover_agents(criteria: AgentCriteria,
                 discovery_options: Optional[DiscoveryOptions] = None) -> DiscoveryResult:
    """
    Discover agents matching specific criteria in the topology.

    Args:
        criteria: AgentCriteria - Filtering criteria for agent discovery
        discovery_options: Optional[DiscoveryOptions] - Additional options for discovery process

    Returns:
        DiscoveryResult - Result containing matching agents and metadata

    Raises:
        TopologyAccessError - If there's an error accessing the topology system
        InvalidCriteriaError - If the provided criteria are invalid
        DiscoveryTimeoutError - If the discovery process times out
    """
```

**Data Structures:**

```python
class AgentCriteria:
    """
    Criteria for filtering agents in the topology.
    """
    capabilities: Optional[List[str]] = None  # Capabilities that agents must have
    protocols: Optional[List[str]] = None  # Protocols that agents must support
    status: Optional[str] = None  # Required agent status (e.g., "active", "inactive")
    agent_types: Optional[List[str]] = None  # Types of agents to find
    location: Optional[str] = None  # Location identifier for agents
    metadata_filters: Dict[str, Any] = {}  # Additional metadata-based filters
    tags: Optional[List[str]] = None  # Tags that agents must have
    exclude_agent_ids: List[str] = []  # Agent IDs to exclude from results
    capability_versions: Dict[str, str] = {}  # Minimum required versions for capabilities
    max_response_time_ms: Optional[int] = None  # Maximum acceptable response time
    security_level: Optional[str] = None  # Required security level
    search_text: Optional[str] = None  # Free text search across agent properties

class DiscoveryOptions:
    """
    Options for the agent discovery process.
    """
    max_results: Optional[int] = None  # Maximum number of results to return
    timeout_ms: int = 5000  # Timeout for the discovery process in milliseconds
    include_detailed_info: bool = False  # Whether to include detailed agent information
    use_cached_results: bool = True  # Whether to use cached results when available
    sort_by: str = "relevance"  # How to sort results (relevance, name, last_active, etc.)
    sort_order: str = "descending"  # Sort order (ascending or descending)
    include_metrics: bool = False  # Whether to include performance metrics for agents
    result_format: str = "full"  # Format of results (full, summary, minimal)
    search_scope: str = "global"  # Scope of the search (global, local, region)
    protocol_specific_options: Dict[str, Any] = {}  # Protocol-specific discovery options

class AgentInfo:
    """
    Information about an agent in the topology.
    """
    id: str  # Unique identifier for the agent
    name: str  # Human-readable name of the agent
    description: Optional[str] = None  # Description of the agent's purpose
    capabilities: List[str] = []  # List of agent capabilities
    protocols: List[str] = []  # Protocols supported by the agent
    status: str  # Current status of the agent
    agent_type: str  # Type of agent
    version: str  # Agent version
    location: Optional[str] = None  # Location identifier for the agent
    last_active: datetime  # When the agent was last active
    creation_time: datetime  # When the agent was created
    metadata: Dict[str, Any] = {}  # Additional metadata about the agent
    tags: List[str] = []  # Tags associated with the agent
    capability_details: Dict[str, Dict[str, Any]] = {}  # Detailed information about capabilities
    endpoints: Dict[str, str] = {}  # Map of protocol names to endpoint URIs
    metrics: Optional[Dict[str, Any]] = None  # Performance metrics for the agent
    security_info: Optional[Dict[str, Any]] = None  # Security-related information

class DiscoveryResult:
    """
    Result of an agent discovery operation.
    """
    agents: List[AgentInfo]  # List of agents matching the criteria
    total_count: int  # Total number of matching agents
    returned_count: int  # Number of agents returned in this result
    discovery_time_ms: int  # Time taken for discovery in milliseconds
    query_id: str  # Unique identifier for this query
    timestamp: datetime  # When the discovery was performed
    criteria_used: AgentCriteria  # Criteria used for discovery
    is_complete: bool = True  # Whether all matching agents are included
    continuation_token: Optional[str] = None  # Token for pagination if result is not complete
    cache_info: Optional[Dict[str, Any]] = None  # Information about cache usage
    search_scope_used: str  # Scope that was used for the search
```

**Example Usage:**
```python
# Discover AI agents with specific capabilities and protocols
discovery_result = topology.discover_agents(
    criteria=AgentCriteria(
        capabilities=["reasoning", "tool_use", "planning"],
        protocols=["a2a", "mcp"],
        status="active",
        agent_types=["assistant", "specialist"],
        metadata_filters={
            "reasoning_type": ["llm", "symbolic"],
            "min_reliability_score": 0.85
        },
        tags=["production", "approved"],
        capability_versions={
            "reasoning": "2.0.0",
            "tool_use": "1.5.0"
        },
        max_response_time_ms=500
    ),
    discovery_options=DiscoveryOptions(
        max_results=10,
        timeout_ms=3000,
        include_detailed_info=True,
        sort_by="last_active",
        sort_order="descending",
        include_metrics=True,
        search_scope="region",
        protocol_specific_options={
            "a2a": {
                "prefer_direct_connection": True
            }
        }
    )
)

if discovery_result.agents:
    print(f"Found {discovery_result.returned_count} of {discovery_result.total_count} matching agents in {discovery_result.discovery_time_ms}ms")

    # Process each agent
    for agent in discovery_result.agents:
        print(f"\nAgent: {agent.name} (ID: {agent.id})")
        print(f"Type: {agent.agent_type}, Status: {agent.status}")
        print(f"Capabilities: {', '.join(agent.capabilities)}")
        print(f"Protocols: {', '.join(agent.protocols)}")
        print(f"Last active: {agent.last_active}")

        # Check if the agent has a specific capability
        if "reasoning" in agent.capabilities:
            reasoning_details = agent.capability_details.get("reasoning", {})
            print(f"Reasoning type: {reasoning_details.get('type', 'unknown')}")
            print(f"Reasoning version: {reasoning_details.get('version', 'unknown')}")

        # Get endpoints for communication
        if "a2a" in agent.protocols:
            print(f"A2A endpoint: {agent.endpoints.get('a2a', 'unknown')}")

        # Check performance metrics if available
        if agent.metrics:
            print(f"Average response time: {agent.metrics.get('avg_response_time_ms', 'unknown')}ms")
            print(f"Reliability score: {agent.metrics.get('reliability_score', 'unknown')}")

    # Check if there are more results available
    if not discovery_result.is_complete:
        print(f"\nShowing {discovery_result.returned_count} of {discovery_result.total_count} results.")
        print(f"Use continuation token '{discovery_result.continuation_token}' to get more results.")
else:
    print("No agents found matching the criteria.")
    print(f"Search completed in {discovery_result.discovery_time_ms}ms across {discovery_result.search_scope_used} scope.")
```

```python
def register_agent(agent: AgentInfo,
                registration_options: Optional[RegistrationOptions] = None) -> RegistrationResult:
    """
    Register an agent in the topology system.

    Args:
        agent: AgentInfo - Information about the agent to register
        registration_options: Optional[RegistrationOptions] - Additional options for registration

    Returns:
        RegistrationResult - Result of the registration operation

    Raises:
        TopologyAccessError - If there's an error accessing the topology system
        InvalidAgentInfoError - If the provided agent information is invalid
        AgentAlreadyExistsError - If an agent with the same ID already exists and no override is specified
        RegistrationAuthorizationError - If the requester is not authorized to register the agent
    """
```

**Data Structures:**

```python
class RegistrationOptions:
    """
    Options for agent registration.
    """
    override_existing: bool = False  # Whether to override an existing agent with the same ID
    ttl_seconds: Optional[int] = None  # Time-to-live for the registration in seconds
    require_heartbeat: bool = True  # Whether the agent is required to send heartbeats
    heartbeat_interval_seconds: int = 30  # Interval between heartbeats in seconds
    auto_deregister_after_seconds: Optional[int] = None  # Time after which to auto-deregister if no heartbeat
    registration_scope: str = "global"  # Scope of the registration (global, local, region)
    notify_interested_agents: bool = True  # Whether to notify agents that might be interested in this registration
    include_in_discovery: bool = True  # Whether the agent should be included in discovery results
    security_options: Dict[str, Any] = {}  # Security-related options for registration

class RegistrationResult:
    """
    Result of an agent registration operation.
    """
    success: bool  # Whether the registration was successful
    agent_id: str  # ID of the registered agent
    registration_id: str  # Unique identifier for this registration
    registration_time: datetime  # When the registration was performed
    expiration_time: Optional[datetime] = None  # When the registration expires
    status: str  # Status of the registration (e.g., "active", "pending")
    heartbeat_token: Optional[str] = None  # Token to use for heartbeat operations
    warnings: List[str] = []  # Any warnings generated during registration
    registration_scope: str  # Scope of the registration
    metadata: Dict[str, Any] = {}  # Additional metadata about the registration
    override_applied: bool = False  # Whether an existing registration was overridden
```

**Example Usage:**
```python
# Register a reasoning agent with capabilities, protocols, and detailed information
registration_result = topology.register_agent(
    agent=AgentInfo(
        id="reasoning_agent_01",
        name="Advanced Reasoning Agent",
        description="Provides advanced reasoning capabilities using BDI architecture",
        capabilities=["reasoning", "planning", "tool_use", "knowledge_graph_access"],
        protocols=["a2a", "mcp", "http"],
        status="active",
        agent_type="reasoning",
        version="2.5.0",
        location="us-west-datacenter",
        last_active=datetime.now(),
        creation_time=datetime.now(),
        metadata={
            "reasoning_type": "bdi",
            "implementation": "python_advanced_reasoning",
            "max_concurrent_tasks": 50,
            "deployment_environment": "production"
        },
        tags=["production", "reasoning", "bdi", "high_performance"],
        capability_details={
            "reasoning": {
                "type": "bdi",
                "version": "3.2.1",
                "supported_formats": ["json", "xml", "prolog"]
            },
            "planning": {
                "type": "hierarchical",
                "version": "2.0.0",
                "max_plan_steps": 100
            }
        },
        endpoints={
            "a2a": "https://agents.example.com/a2a/reasoning_agent_01",
            "mcp": "https://agents.example.com/mcp/reasoning_agent_01",
            "http": "https://api.example.com/agents/reasoning_agent_01"
        },
        metrics={
            "avg_response_time_ms": 120,
            "reliability_score": 0.98,
            "uptime_percentage": 99.9
        },
        security_info={
            "authentication_required": True,
            "authorization_scheme": "oauth2",
            "security_level": "standard"
        }
    ),
    registration_options=RegistrationOptions(
        override_existing=True,
        ttl_seconds=86400,  # 24 hours
        require_heartbeat=True,
        heartbeat_interval_seconds=60,
        auto_deregister_after_seconds=180,  # 3 minutes without heartbeat
        registration_scope="global",
        notify_interested_agents=True,
        security_options={
            "require_secure_communication": True,
            "verify_agent_identity": True
        }
    )
)

if registration_result.success:
    print(f"Agent {registration_result.agent_id} registered successfully")
    print(f"Registration ID: {registration_result.registration_id}")
    print(f"Registration time: {registration_result.registration_time}")

    if registration_result.expiration_time:
        print(f"Registration expires at: {registration_result.expiration_time}")

    print(f"Heartbeat token: {registration_result.heartbeat_token}")
    print(f"Registration scope: {registration_result.registration_scope}")

    if registration_result.override_applied:
        print("Note: Existing registration was overridden")

    if registration_result.warnings:
        print("\nWarnings:")
        for warning in registration_result.warnings:
            print(f"- {warning}")
else:
    print(f"Agent registration failed with status: {registration_result.status}")
    if registration_result.warnings:
        print("\nWarnings/Errors:")
        for warning in registration_result.warnings:
            print(f"- {warning}")
```

```python
def get_agent_path(source_id: str, target_id: str,
               path_options: Optional[PathOptions] = None) -> PathResult:
    """
    Find a communication path between two agents in the topology.

    Args:
        source_id: str - ID of the source agent
        target_id: str - ID of the target agent
        path_options: Optional[PathOptions] - Options for path finding

    Returns:
        PathResult - Result containing the path information if found

    Raises:
        TopologyAccessError - If there's an error accessing the topology system
        AgentNotFoundError - If either the source or target agent is not found
        PathFindingError - If there's an error during the path finding process
    """
```

**Data Structures:**

```python
class PathOptions:
    """
    Options for agent path finding.
    """
    algorithm: str = "shortest_path"  # Algorithm to use (shortest_path, secure_path, reliable_path)
    max_path_length: Optional[int] = None  # Maximum number of hops in the path
    timeout_ms: int = 5000  # Timeout for the path finding process in milliseconds
    require_common_protocol: bool = True  # Whether all nodes in the path must share a common protocol
    preferred_protocols: Optional[List[str]] = None  # Protocols to prefer when finding a path
    include_inactive_agents: bool = False  # Whether to include inactive agents in the path
    security_level: str = "standard"  # Minimum security level for the path
    fallback_to_less_secure: bool = False  # Whether to fall back to less secure paths if necessary
    include_path_metrics: bool = True  # Whether to include performance metrics for the path
    path_constraints: Dict[str, Any] = {}  # Additional constraints on the path

class AgentNode:
    """
    A node in an agent path.
    """
    agent_id: str  # ID of the agent
    agent_type: str  # Type of agent
    protocols: List[str]  # Protocols supported by the agent
    status: str  # Current status of the agent
    location: Optional[str] = None  # Location identifier for the agent
    metrics: Optional[Dict[str, Any]] = None  # Performance metrics for the agent
    security_level: str  # Security level of the agent
    hop_number: int  # Position of this agent in the path (0-indexed)
    connection_info: Dict[str, Any] = {}  # Information about connections to adjacent nodes

class PathHop:
    """
    A hop between agents in a path.
    """
    from_agent_id: str  # ID of the source agent for this hop
    to_agent_id: str  # ID of the target agent for this hop
    protocol: str  # Protocol used for this hop
    estimated_latency_ms: Optional[int] = None  # Estimated latency for this hop
    security_level: str  # Security level of this hop
    hop_number: int  # Position of this hop in the path (0-indexed)
    metadata: Dict[str, Any] = {}  # Additional metadata about this hop

class PathResult:
    """
    Result of an agent path finding operation.
    """
    success: bool  # Whether a path was found
    source_id: str  # ID of the source agent
    target_id: str  # ID of the target agent
    nodes: List[AgentNode]  # List of agent nodes in the path (including source and target)
    hops: List[PathHop]  # List of hops between agents
    path_length: int  # Number of hops in the path
    total_estimated_latency_ms: Optional[int] = None  # Total estimated latency for the path
    common_protocols: List[str]  # Protocols common to all nodes in the path
    path_security_level: str  # Overall security level of the path
    path_finding_time_ms: int  # Time taken for path finding in milliseconds
    algorithm_used: str  # Algorithm used for path finding
    alternatives_available: bool = False  # Whether alternative paths are available
    path_id: str  # Unique identifier for this path
    expiration_time: Optional[datetime] = None  # When this path information expires
    metadata: Dict[str, Any] = {}  # Additional metadata about the path
```

**Example Usage:**
```python
# Find a secure, reliable path between two agents
path_result = topology.get_agent_path(
    source_id="user_agent_123",
    target_id="knowledge_agent_456",
    path_options=PathOptions(
        algorithm="reliable_path",
        max_path_length=3,  # Maximum 3 hops
        timeout_ms=2000,
        require_common_protocol=True,
        preferred_protocols=["a2a", "mcp"],
        include_inactive_agents=False,
        security_level="high",
        fallback_to_less_secure=False,
        include_path_metrics=True,
        path_constraints={
            "min_reliability_score": 0.9,
            "max_total_latency_ms": 500
        }
    )
)

if path_result.success:
    print(f"Found path from {path_result.source_id} to {path_result.target_id}")
    print(f"Path length: {path_result.path_length} hops")
    print(f"Common protocols: {', '.join(path_result.common_protocols)}")
    print(f"Path security level: {path_result.path_security_level}")

    if path_result.total_estimated_latency_ms:
        print(f"Estimated total latency: {path_result.total_estimated_latency_ms}ms")

    print("\nPath Details:")
    for i, node in enumerate(path_result.nodes):
        print(f"[{i}] Agent: {node.agent_id} (Type: {node.agent_type}, Status: {node.status})")
        if i < len(path_result.nodes) - 1:
            hop = path_result.hops[i]
            print(f"   → Protocol: {hop.protocol}, Security: {hop.security_level}")
            if hop.estimated_latency_ms:
                print(f"   → Estimated latency: {hop.estimated_latency_ms}ms")

    print(f"\nPath will expire at: {path_result.expiration_time}")
    if path_result.alternatives_available:
        print("Alternative paths are available. Use 'get_alternative_paths' for details.")
else:
    print(f"No path found from {path_result.source_id} to {path_result.target_id}")
    print(f"Path finding completed in {path_result.path_finding_time_ms}ms using {path_result.algorithm_used} algorithm")
    print("Possible reasons for failure:")
    if "failure_reasons" in path_result.metadata:
        for reason in path_result.metadata["failure_reasons"]:
            print(f"- {reason}")
```

#### Events

```python
class TopologyLookupFailedEvent:
    """
    Event emitted when agent discovery fails.
    """
    event_type: str = "topology_lookup_failed"  # Type of the event
    query_id: str  # ID of the failed discovery query
    criteria: AgentCriteria  # Criteria used for the lookup
    error_code: str  # Error code describing the failure
    error_message: str  # Detailed error message
    timestamp: datetime  # When the failure occurred
    source_component: str  # Component that attempted the lookup
    retry_attempted: bool  # Whether a retry was attempted
    affected_operations: List[str] = []  # Operations affected by this failure
    metadata: Dict[str, Any] = {}  # Additional metadata about the failure
    suggested_actions: Optional[List[str]] = None  # Suggested actions to resolve the issue
```

**Example Payload:**
```json
{
    "event_type": "topology_lookup_failed",
    "query_id": "query_123abc",
    "criteria": {
        "capabilities": ["reasoning", "tool_use"],
        "protocols": ["a2a"],
        "status": "active",
        "metadata_filters": {
            "reasoning_type": "llm"
        }
    },
    "error_code": "TOPOLOGY_UNAVAILABLE",
    "error_message": "Topology service is temporarily unavailable due to maintenance",
    "timestamp": "2025-05-25T15:42:30Z",
    "source_component": "agent_framework_router",
    "retry_attempted": true,
    "affected_operations": ["message_routing", "capability_discovery"],
    "metadata": {
        "attempts": 3,
        "last_successful_lookup": "2025-05-25T15:30:15Z",
        "region": "us-west"
    },
    "suggested_actions": [
        "Use cached topology information if available",
        "Retry after 5 minutes",
        "Check topology service status"
    ]
}
```

```python
class AgentRegistrationChangedEvent:
    """
    Event emitted when agent registration status changes.
    """
    event_type: str = "agent_registration_changed"  # Type of the event
    agent_id: str  # ID of the affected agent
    previous_status: Optional[str] = None  # Previous registration status (null if newly registered)
    new_status: str  # New registration status
    timestamp: datetime  # When the change occurred
    change_reason: str  # Reason for the status change
    initiator_id: Optional[str] = None  # ID of the entity that initiated the change
    registration_id: str  # ID of the registration entry
    expiration_time: Optional[datetime] = None  # When the registration expires
    capabilities_affected: List[str] = []  # Capabilities affected by this change
    protocols_affected: List[str] = []  # Protocols affected by this change
    metadata: Dict[str, Any] = {}  # Additional metadata about the change
```

**Example Payload:**
```json
{
    "event_type": "agent_registration_changed",
    "agent_id": "reasoning_agent_01",
    "previous_status": "active",
    "new_status": "inactive",
    "timestamp": "2025-05-25T15:40:45Z",
    "change_reason": "heartbeat_timeout",
    "initiator_id": "topology_manager",
    "registration_id": "reg_456def",
    "expiration_time": "2025-05-26T15:40:45Z",
    "capabilities_affected": ["reasoning", "planning", "tool_use"],
    "protocols_affected": ["a2a", "mcp"],
    "metadata": {
        "last_heartbeat": "2025-05-25T15:37:15Z",
        "heartbeat_interval": 60,
        "timeout_threshold": 180,
        "location": "us-west-datacenter",
        "auto_recovery_enabled": true
    }
}
```

### Topology System → Agent Framework

#### Methods/Functions

```python
def notify_topology_change(change: TopologyChange,
                         notification_options: Optional[TopologyNotificationOptions] = None) -> TopologyNotificationResult:
    """
    Notify Agent Framework of changes in the topology.

    Args:
        change: TopologyChange - Object describing the topology change
        notification_options: Optional[TopologyNotificationOptions] - Options for the notification

    Returns:
        TopologyNotificationResult - Result of the notification operation

    Raises:
        InvalidTopologyChangeError - If the topology change is invalid
        NotificationDeliveryError - If there's an error delivering the notification
        TopologyUpdateError - If there's an error updating the topology information
    """
```

**Data Structures:**

```python
class ChangeType(Enum):
    """
    Types of topology changes.
    """
    AGENT_ADDED = "agent_added"  # A new agent was added to the topology
    AGENT_REMOVED = "agent_removed"  # An agent was removed from the topology
    AGENT_UPDATED = "agent_updated"  # An agent's information was updated
    CAPABILITY_ADDED = "capability_added"  # A capability was added to an agent
    CAPABILITY_REMOVED = "capability_removed"  # A capability was removed from an agent
    PROTOCOL_ADDED = "protocol_added"  # A protocol was added to an agent
    PROTOCOL_REMOVED = "protocol_removed"  # A protocol was removed from an agent
    STATUS_CHANGED = "status_changed"  # An agent's status changed
    LOCATION_CHANGED = "location_changed"  # An agent's location changed
    TOPOLOGY_RESET = "topology_reset"  # The topology was reset

class TopologyChange:
    """
    Description of a change in the topology.
    """
    change_type: ChangeType  # Type of the change
    change_id: str  # Unique identifier for this change
    agent_id: str  # ID of the affected agent
    timestamp: datetime  # When the change occurred
    details: Dict[str, Any]  # Details of the change
    affected_capabilities: List[str] = []  # Capabilities affected by this change
    affected_protocols: List[str] = []  # Protocols affected by this change
    source: str  # Source of the change (e.g., "agent_registration", "admin_action")
    metadata: Dict[str, Any] = {}  # Additional metadata about the change
    related_changes: List[str] = []  # IDs of related changes
    priority: str = "normal"  # Priority of this change (low, normal, high)

class TopologyNotificationOptions:
    """
    Options for topology change notifications.
    """
    delivery_mode: str = "standard"  # How to deliver the notification (standard, immediate, batched)
    notification_targets: Optional[List[str]] = None  # Specific targets to notify (None = all affected components)
    exclude_targets: List[str] = []  # Targets to exclude from notification
    include_change_details: bool = True  # Whether to include full change details
    notification_context: Dict[str, Any] = {}  # Additional context for the notification
    batch_with_related: bool = False  # Whether to batch with related changes
    propagate_to_agents: bool = True  # Whether to propagate the notification to affected agents
    require_acknowledgment: bool = False  # Whether acknowledgment is required

class TopologyNotificationResult:
    """
    Result of a topology change notification operation.
    """
    success: bool  # Whether the notification was successful
    notification_id: str  # Unique identifier for the notification
    change_id: str  # ID of the change that was notified
    timestamp: datetime  # When the notification was sent
    delivered_to: List[str]  # Components the notification was delivered to
    failed_deliveries: List[Dict[str, Any]] = []  # Details of failed deliveries
    pending_deliveries: List[str] = []  # Components with pending deliveries
    acknowledgments: List[Dict[str, Any]] = []  # Acknowledgments received
    affected_routing_tables: List[str] = []  # Routing tables affected by this change
    topology_update_status: str  # Status of the topology update
    metadata: Dict[str, Any] = {}  # Additional metadata about the notification
```

**Example Usage:**
```python
# Notify Agent Framework of a new agent being added to the topology
notification_result = agent_framework.notify_topology_change(
    change=TopologyChange(
        change_type=ChangeType.AGENT_ADDED,
        change_id="change_789ghi",
        agent_id="new_reasoning_agent_xyz",
        timestamp=datetime.now(),
        details={
            "name": "Advanced Reasoning Agent XYZ",
            "capabilities": ["reasoning", "planning", "knowledge_graph_access"],
            "protocols": ["a2a", "mcp"],
            "status": "active",
            "agent_type": "reasoning",
            "location": "us-east-datacenter"
        },
        affected_capabilities=["reasoning", "planning", "knowledge_graph_access"],
        affected_protocols=["a2a", "mcp"],
        source="agent_registration",
        metadata={
            "registration_id": "reg_123abc",
            "registrar": "topology_manager",
            "authentication_verified": True
        },
        priority="high"
    ),
    notification_options=TopologyNotificationOptions(
        delivery_mode="immediate",
        notification_targets=["routing_service", "discovery_service", "capability_registry"],
        include_change_details=True,
        propagate_to_agents=True,
        require_acknowledgment=True,
        notification_context={
            "reason": "new_capability_provider",
            "immediate_routing_update": True
        }
    )
)

if notification_result.success:
    print(f"Topology change notification sent successfully at {notification_result.timestamp}")
    print(f"Delivered to: {', '.join(notification_result.delivered_to)}")
    print(f"Topology update status: {notification_result.topology_update_status}")

    if notification_result.affected_routing_tables:
        print(f"Affected routing tables: {', '.join(notification_result.affected_routing_tables)}")

    if notification_result.acknowledgments:
        print("Received acknowledgments:")
        for ack in notification_result.acknowledgments:
            print(f"- From: {ack['component']} at {ack['timestamp']}")

    if notification_result.pending_deliveries:
        print(f"Pending deliveries: {', '.join(notification_result.pending_deliveries)}")
else:
    print("Topology change notification failed")
    if notification_result.failed_deliveries:
        print("Failed deliveries:")
        for failure in notification_result.failed_deliveries:
            print(f"- Component: {failure['component']}, Reason: {failure['reason']}")
```

```python
def validate_agent_status(agent_id: str,
                      validation_options: Optional[StatusValidationOptions] = None) -> AgentStatusResult:
    """
    Verify the current status of an agent in the framework.

    Args:
        agent_id: str - Identifier of the agent to validate
        validation_options: Optional[StatusValidationOptions] - Options for status validation

    Returns:
        AgentStatusResult - Result containing the agent status and related information

    Raises:
        AgentNotFoundError - If the agent is not found in the framework
        ValidationError - If there's an error during validation
        StatusQueryTimeoutError - If the status query times out
    """
```

**Data Structures:**

```python
class AgentStatusEnum(Enum):
    """
    Enumeration of possible agent statuses.
    """
    ACTIVE = "active"  # Agent is active and fully operational
    INACTIVE = "inactive"  # Agent is registered but not active
    INITIALIZING = "initializing"  # Agent is starting up
    SHUTTING_DOWN = "shutting_down"  # Agent is in the process of shutting down
    ERROR = "error"  # Agent is in an error state
    MAINTENANCE = "maintenance"  # Agent is in maintenance mode
    SUSPENDED = "suspended"  # Agent has been administratively suspended
    UNKNOWN = "unknown"  # Agent status is unknown

class StatusValidationOptions:
    """
    Options for agent status validation.
    """
    include_detailed_info: bool = False  # Whether to include detailed status information
    timeout_ms: int = 2000  # Timeout for the validation in milliseconds
    check_heartbeat: bool = True  # Whether to check the agent's heartbeat
    check_connectivity: bool = False  # Whether to test connectivity to the agent
    validate_capabilities: bool = False  # Whether to validate the agent's capabilities
    validate_protocols: bool = False  # Whether to validate the agent's protocols
    validation_context: Dict[str, Any] = {}  # Additional context for validation

class AgentStatusResult:
    """
    Result of an agent status validation.
    """
    agent_id: str  # ID of the agent that was validated
    status: AgentStatusEnum  # Current status of the agent
    validation_time: datetime  # When the validation was performed
    since_time: Optional[datetime] = None  # When the agent entered its current status
    last_heartbeat_time: Optional[datetime] = None  # When the last heartbeat was received
    detailed_status: Optional[Dict[str, Any]] = None  # Detailed status information if requested
    connectivity_check_result: Optional[Dict[str, Any]] = None  # Result of connectivity check if performed
    capability_validation_results: Optional[Dict[str, bool]] = None  # Results of capability validation if performed
    protocol_validation_results: Optional[Dict[str, bool]] = None  # Results of protocol validation if performed
    health_metrics: Optional[Dict[str, Any]] = None  # Health metrics for the agent
    errors: List[Dict[str, Any]] = []  # Any errors encountered during validation
    warnings: List[Dict[str, Any]] = []  # Any warnings generated during validation
```

**Example Usage:**
```python
# Validate an agent's status with detailed checks
status_result = agent_framework.validate_agent_status(
    agent_id="reasoning_agent_01",
    validation_options=StatusValidationOptions(
        include_detailed_info=True,
        timeout_ms=3000,
        check_heartbeat=True,
        check_connectivity=True,
        validate_capabilities=["reasoning", "planning"],
        validate_protocols=["a2a", "mcp"],
        validation_context={
            "origin": "topology_update",
            "criticality": "high"
        }
    )
)

# Process the result
print(f"Agent {status_result.agent_id} status: {status_result.status.value}")
print(f"Validated at: {status_result.validation_time}")

if status_result.last_heartbeat_time:
    heartbeat_age = (status_result.validation_time - status_result.last_heartbeat_time).total_seconds()
    print(f"Last heartbeat: {status_result.last_heartbeat_time} ({heartbeat_age} seconds ago)")

if status_result.status == AgentStatusEnum.ACTIVE:
    print("Agent is active and operational")

    # Check detailed status if available
    if status_result.detailed_status:
        print("\nDetailed Status:")
        for key, value in status_result.detailed_status.items():
            print(f"- {key}: {value}")

    # Check connectivity if tested
    if status_result.connectivity_check_result:
        if status_result.connectivity_check_result.get("successful", False):
            print(f"\nConnectivity check successful")
            print(f"Response time: {status_result.connectivity_check_result.get('response_time_ms', 'unknown')}ms")
        else:
            print("\nConnectivity check failed:")
            print(f"Reason: {status_result.connectivity_check_result.get('failure_reason', 'unknown')}")

    # Check capability validation if performed
    if status_result.capability_validation_results:
        print("\nCapability Validation:")
        for capability, valid in status_result.capability_validation_results.items():
            status = "Valid" if valid else "Invalid"
            print(f"- {capability}: {status}")

    # Check protocol validation if performed
    if status_result.protocol_validation_results:
        print("\nProtocol Validation:")
        for protocol, valid in status_result.protocol_validation_results.items():
            status = "Valid" if valid else "Invalid"
            print(f"- {protocol}: {status}")

    # Check health metrics if available
    if status_result.health_metrics:
        print("\nHealth Metrics:")
        print(f"- CPU Usage: {status_result.health_metrics.get('cpu_usage_percent', 'unknown')}%")
        print(f"- Memory Usage: {status_result.health_metrics.get('memory_usage_percent', 'unknown')}%")
        print(f"- Active Connections: {status_result.health_metrics.get('active_connections', 'unknown')}")
else:
    print(f"Agent is not active: {status_result.status.value}")
    if status_result.since_time:
        in_current_state = (status_result.validation_time - status_result.since_time).total_seconds()
        print(f"In current state for {in_current_state} seconds")

    # Check for errors
    if status_result.errors:
        print("\nErrors:")
        for error in status_result.errors:
            print(f"- {error['message']} (Code: {error['code']})")
```

#### Events

```python
class AgentStatusChangedEvent:
    """
    Event emitted when an agent's status changes.
    """
    event_type: str = "agent_status_changed"  # Type of the event
    agent_id: str  # ID of the affected agent
    previous_status: AgentStatusEnum  # Previous status of the agent
    new_status: AgentStatusEnum  # New status of the agent
    timestamp: datetime  # When the change occurred
    change_reason: str  # Reason for the status change
    initiator_id: Optional[str] = None  # ID of the entity that initiated the change
    expected_duration: Optional[int] = None  # Expected duration of the new status in seconds
    metadata: Dict[str, Any] = {}  # Additional metadata about the change
    affected_capabilities: List[str] = []  # Capabilities affected by this change
    affected_sessions: List[str] = []  # Sessions affected by this change
    health_check_result: Optional[Dict[str, Any]] = None  # Result of any health check performed
```

**Example Payload:**
```json
{
    "event_type": "agent_status_changed",
    "agent_id": "reasoning_agent_01",
    "previous_status": "active",
    "new_status": "maintenance",
    "timestamp": "2025-05-25T15:40:00Z",
    "change_reason": "scheduled_maintenance",
    "initiator_id": "admin_service",
    "expected_duration": 1800,
    "metadata": {
        "maintenance_type": "software_update",
        "maintenance_id": "maint_456def",
        "notification_sent": true,
        "scheduled_return": "2025-05-25T16:10:00Z"
    },
    "affected_capabilities": ["reasoning", "planning", "tool_use"],
    "affected_sessions": ["session_123abc", "session_456def"],
    "health_check_result": {
        "pre_maintenance_check": "passed",
        "critical_systems": "normal",
        "pending_operations": 0
    }
}
```

```python
class AgentCapabilityChangedEvent:
    """
    Event emitted when an agent's capabilities change.
    """
    event_type: str = "agent_capability_changed"  # Type of the event
    agent_id: str  # ID of the affected agent
    timestamp: datetime  # When the change occurred
    added_capabilities: List[Dict[str, Any]] = []  # Capabilities that were added
    removed_capabilities: List[Dict[str, Any]] = []  # Capabilities that were removed
    updated_capabilities: List[Dict[str, Any]] = []  # Capabilities that were updated
    change_reason: str  # Reason for the capability change
    initiator_id: Optional[str] = None  # ID of the entity that initiated the change
    affected_protocols: List[str] = []  # Protocols affected by this change
    affected_sessions: List[str] = []  # Sessions affected by this change
    current_capability_count: int  # Total number of capabilities after the change
    metadata: Dict[str, Any] = {}  # Additional metadata about the change
```

**Example Payload:**
```json
{
    "event_type": "agent_capability_changed",
    "agent_id": "reasoning_agent_01",
    "timestamp": "2025-05-25T15:45:30Z",
    "added_capabilities": [
        {
            "id": "knowledge_graph_query",
            "version": "1.2.0",
            "description": "Ability to query knowledge graphs and return structured results",
            "protocols": ["a2a", "mcp"],
            "parameters_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "graph_id": {"type": "string"},
                    "max_results": {"type": "integer"}
                },
                "required": ["query", "graph_id"]
            }
        }
    ],
    "removed_capabilities": [
        {
            "id": "legacy_database_query",
            "version": "0.9.1",
            "description": "Legacy database querying functionality"
        }
    ],
    "updated_capabilities": [
        {
            "id": "reasoning",
            "version": "2.5.0",
            "previous_version": "2.0.0",
            "description": "Enhanced reasoning with improved performance and accuracy",
            "update_summary": "Performance improvements and new reasoning strategies"
        }
    ],
    "change_reason": "capability_upgrade",
    "initiator_id": "system_updater",
    "affected_protocols": ["a2a", "mcp"],
    "affected_sessions": ["session_789ghi", "session_012jkl"],
    "current_capability_count": 8,
    "metadata": {
        "upgrade_id": "upgrade_789ghi",
        "backward_compatible": true,
        "requires_restart": false,
        "capability_announcement_sent": true
    }
}
```

## Data Flows

### Agent Discovery Flow
1. **Agent Framework → Topology System**: Agent Framework requests agents matching criteria
2. **Topology System Processing**: Topology System searches its registry
3. **Topology System → Agent Framework**: Topology System returns matching agents
4. **Agent Framework Processing**: Agent Framework uses agent information for routing or communication

### Topology Change Notification Flow
1. **Topology System → Agent Framework**: Topology System notifies of topology changes
2. **Agent Framework Processing**: Agent Framework updates internal routing tables
3. **Agent Framework → Protocol Layer**: Agent Framework propagates relevant changes to Protocol Layer

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
topology:
  discovery:
    refresh_interval_seconds: 300
    caching_enabled: true
    cache_ttl_seconds: 60

  registration:
    heartbeat_interval_seconds: 30
    timeout_threshold_seconds: 90
    automatic_deregistration: true

  routing:
    path_finding_algorithm: "shortest_path"
    max_path_length: 5
    fallback_paths_enabled: true

agent_framework:
  topology_integration:
    automatic_registration: true
    status_update_interval_seconds: 15
    capability_broadcast: true
```

## Error Handling

1. **Registration Failures**:
   - Multiple retry attempts with exponential backoff
   - Failed registrations are logged with detailed error information
   - Agent Framework may continue operation in degraded mode without topology registration

2. **Discovery Failures**:
   - Cached results may be used if available
   - Fallback to broader search criteria if specific search fails
   - Alternative discovery mechanisms may be used (direct connection, broadcast)

3. **Stale Topology Information**:
   - Heartbeat mechanism detects agent availability
   - Time-to-live (TTL) settings prevent use of stale information
   - Periodic refresh of topology information

## Extension Points

1. **Discovery Mechanisms**:
   - New discovery mechanisms can be added by implementing the DiscoveryProvider interface
   - DiscoveryProvider interface:
     ```python
     class DiscoveryProvider:
         def discover_agents(self, criteria: AgentCriteria) → List[AgentInfo]:
             # Discover agents matching criteria
             pass

         def get_agent_details(self, agent_id: str) → Optional[AgentInfo]:
             # Get detailed information about a specific agent
             pass
     ```

2. **Topology Visualizers**:
   - Custom visualization components can be added
   - Topology events can be subscribed to for real-time visualization updates

## Notes on Multi-Protocol Design

The Agent Framework ↔ Topology System interface supports OpenMAS's multi-protocol design:

- The Topology System maintains information about which protocols each agent supports
- This enables protocol-aware routing decisions (selecting agents that support specific protocols)
- Agent discovery can filter based on protocol support
- The Agent Framework can use this information to select the appropriate protocol when communicating with another agent

## Notes on Reasoning Agnosticism

The Topology System supports OpenMAS's reasoning agnostic architecture by:

- Including reasoning capabilities in agent metadata
- Allowing discovery of agents based on reasoning capabilities
- Supporting different reasoning paradigms in the agent ecosystem
- Enabling communication between agents using different reasoning approaches
