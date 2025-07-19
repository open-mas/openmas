# Agent Framework ↔ Session Management

## Relationship Summary
- **Agent Framework → Session Management**: Depends On
- **Session Management → Agent Framework**: Provides To

## Interface Definitions

### Agent Framework → Session Management

#### Methods/Functions

```python
def create_session(parameters: SessionParameters) -> Session:
    """
    Create a new session for agent interaction.
    
    Args:
        parameters: SessionParameters - Configuration parameters for the session
        
    Returns:
        Session - The created session object
        
    Raises:
        InvalidSessionParametersError - If the session parameters are invalid
        SessionCreationError - If the session cannot be created
        MaxSessionsExceededError - If the maximum number of sessions has been reached
    """
```

**Data Structures:**

```python
class SessionParameters:
    """
    Parameters for creating a session.
    """
    initiator_id: str  # ID of the agent or entity initiating the session
    participants: List[str]  # IDs of initial session participants
    session_type: str  # Type of session (e.g., "conversation", "task")
    session_id: Optional[str] = None  # Optional custom session ID (auto-generated if None)
    metadata: Dict[str, Any] = {}  # Additional metadata about the session
    timeout_seconds: int = 1800  # Session timeout in seconds
    security_context: Optional[SecurityContext] = None  # Security context for the session
    parent_session_id: Optional[str] = None  # Parent session ID for nested sessions
    persistence_level: str = "standard"  # Level of session persistence (minimal, standard, full)
    capabilities: Optional[List[str]] = None  # Capabilities available in this session
    state_schema: Optional[Dict[str, Any]] = None  # Schema for validating session state
    max_participants: Optional[int] = None  # Maximum number of participants allowed
    priority: str = "normal"  # Priority of the session (low, normal, high)

class Session:
    """
    A session for agent interaction.
    """
    session_id: str  # Unique identifier for the session
    session_type: str  # Type of session
    initiator_id: str  # ID of the agent or entity that initiated the session
    participants: List[str]  # IDs of current session participants
    created_at: datetime  # When the session was created
    updated_at: datetime  # When the session was last updated
    expires_at: Optional[datetime] = None  # When the session expires
    status: SessionStatus  # Current status of the session
    metadata: Dict[str, Any] = {}  # Additional metadata about the session
    state: Dict[str, Any] = {}  # Current session state
    message_count: int = 0  # Number of messages exchanged in the session
    security_context: Optional[SecurityContext] = None  # Security context for the session
    parent_session_id: Optional[str] = None  # Parent session ID for nested sessions
    capabilities: List[str] = []  # Capabilities available in this session
    persistence_level: str  # Level of session persistence
    priority: str  # Priority of the session

class SessionStatus(Enum):
    """
    Status of a session.
    """
    INITIALIZING = "initializing"  # Session is being initialized
    ACTIVE = "active"  # Session is active
    PAUSED = "paused"  # Session is temporarily paused
    COMPLETED = "completed"  # Session has completed successfully
    TERMINATED = "terminated"  # Session was terminated before completion
    EXPIRED = "expired"  # Session has expired due to timeout
    ERROR = "error"  # Session encountered an error
```

**Example Usage:**
```python
session = session_manager.create_session(
    parameters=SessionParameters(
        initiator_id="user_agent_123",
        participants=["assistant_agent_456", "specialist_agent_789"],
        session_type="conversation",
        metadata={
            "topic": "travel_planning",
            "purpose": "vacation_to_japan",
            "user_preferences": {"budget": "medium", "duration": "10_days"}
        },
        timeout_seconds=3600,  # 1 hour timeout
        security_context=SecurityContext(
            authentication_level="standard",
            permissions=["standard_interaction"]
        ),
        capabilities=["travel_search", "itinerary_planning", "booking"],
        priority="high"
    )
)

print(f"Created session {session.session_id} of type {session.session_type}")
print(f"Session will expire at {session.expires_at}")
```

```python
def get_session(session_id: str) -> Optional[Session]:
    """
    Retrieve an existing session by ID.
    
    Args:
        session_id: str - Unique identifier for the session to retrieve
        
    Returns:
        Optional[Session] - The session if found, None otherwise
        
    Raises:
        SessionAccessError - If there's an error accessing the session storage
    """
```

**Example Usage:**
```python
# Retrieve a session by ID
session = session_manager.get_session(session_id="session_789abc")

if session:
    print(f"Found session: {session.session_id}")
    print(f"Status: {session.status.value}")
    print(f"Participants: {', '.join(session.participants)}")
    print(f"Created: {session.created_at}, Expires: {session.expires_at}")
    
    # Check if session is still active
    if session.status == SessionStatus.ACTIVE:
        # Use the session for further processing
        if "assistant_agent_456" in session.participants:
            # Send a message to a participant
            send_message_to_participant(
                session_id=session.session_id,
                recipient_id="assistant_agent_456",
                message="Session retrieved successfully"
            )
    else:
        print(f"Session is not active (status: {session.status.value})")
else:
    print(f"Session not found: session_789abc")
    # Create a new session or handle the missing session case
```

```python
def update_session_state(session_id: str, updates: Dict[str, Any], 
                       validation_options: Optional[StateValidationOptions] = None) -> SessionUpdateResult:
    """
    Update session state with new values.
    
    Args:
        session_id: str - Unique identifier for the session to update
        updates: Dict[str, Any] - Dictionary of state updates to apply
        validation_options: Optional[StateValidationOptions] - Options for state validation
        
    Returns:
        SessionUpdateResult - Result of the update operation including success status and validation details
        
    Raises:
        SessionNotFoundError - If the session does not exist
        SessionStateValidationError - If the updates fail validation
        SessionAccessError - If there's an error accessing the session storage
        SessionStateConflictError - If there's a conflict with concurrent updates
    """
```

**Data Structures:**

```python
class StateValidationOptions:
    """
    Options for session state validation.
    """
    validate_schema: bool = True  # Whether to validate against the session's state schema
    strict_validation: bool = False  # Whether validation errors should cause the update to fail
    allow_new_fields: bool = True  # Whether to allow adding fields not in the schema
    field_permissions: Optional[Dict[str, str]] = None  # Permissions for specific fields (read, write, admin)
    validation_context: Dict[str, Any] = {}  # Additional context for validation
    protocol_specific_validations: Dict[ProtocolType, bool] = {}  # Protocol-specific validation flags

class SessionUpdateResult:
    """
    Result of a session state update operation.
    """
    success: bool  # Whether the update was successful
    session_id: str  # ID of the session that was updated
    updated_at: datetime  # When the update was performed
    update_id: str  # Unique identifier for this update operation
    fields_updated: List[str]  # List of fields that were updated
    fields_rejected: List[str] = []  # List of fields that were rejected
    validation_warnings: List[str] = []  # Warnings from validation
    validation_errors: List[str] = []  # Errors from validation (present if strict_validation=False)
    conflict_fields: List[str] = []  # Fields that had conflicts with concurrent updates
    previous_values: Dict[str, Any] = {}  # Previous values of updated fields
    metadata: Dict[str, Any] = {}  # Additional metadata about the update
```

**Example Usage:**
```python
# Update session state with validation options
result = session_manager.update_session_state(
    session_id="session_789abc",
    updates={
        "status": SessionStatus.ACTIVE,
        "last_message_time": datetime.now(),
        "message_count": 5,
        "current_topic": "flight_booking",
        "user_preferences": {
            "seat_type": "window",
            "meal_preference": "vegetarian"
        }
    },
    validation_options=StateValidationOptions(
        validate_schema=True,
        strict_validation=False,  # Continue with valid updates even if some fail
        allow_new_fields=True,
        field_permissions={
            "status": "admin",  # Only admin can update status
            "user_preferences": "write"  # Anyone can update user preferences
        },
        protocol_specific_validations={
            ProtocolType.A2A_HTTP: True,  # Perform A2A-specific validations
            ProtocolType.MCP_SSE: False   # Skip MCP-specific validations
        }
    )
)

if result.success:
    print(f"Session state updated successfully at {result.updated_at}")
    print(f"Updated fields: {', '.join(result.fields_updated)}")
    
    if result.validation_warnings:
        print("Warnings:")
        for warning in result.validation_warnings:
            print(f"- {warning}")
else:
    print(f"Session state update failed")
    if result.fields_rejected:
        print(f"Rejected fields: {', '.join(result.fields_rejected)}")
    if result.validation_errors:
        print("Validation errors:")
        for error in result.validation_errors:
            print(f"- {error}")
    if result.conflict_fields:
        print(f"Conflict in fields: {', '.join(result.conflict_fields)}")
```

#### Events

```python
class SessionExpiredEvent:
    """
    Event emitted when a session has expired.
    """
    event_type: str = "session_expired"  # Type of the event
    session_id: str  # ID of the expired session
    expired_at: datetime  # When the session expired
    reason: str  # Reason for expiration (e.g., "timeout", "manual_termination", "inactivity")
    initiator_id: Optional[str] = None  # ID of the agent that initiated the termination, if applicable
    metadata: Dict[str, Any] = {}  # Additional metadata about the expiration
    affected_agents: List[str]  # List of agent IDs affected by the session expiration
    recovery_options: Optional[Dict[str, Any]] = None  # Options for session recovery if available
    
    class Payload:
        """
        Payload containing details of the session expiration event.
        """
        session_id: str  # ID of the expired session
        expiration_details: Dict[str, Any] = {  # Details about the session expiration
            "expired_at": None,  # ISO-8601 timestamp of when the session expired
            "reason": "",  # Reason for expiration (timeout, manual_termination, inactivity)
            "initiator_id": None  # ID of the agent that initiated the termination, if applicable
        }
        session_details: Dict[str, Any] = {  # Details about the expired session
            "session_type": "",  # Type of session that expired
            "created_at": None,  # ISO-8601 timestamp of when the session was created
            "last_activity_at": None,  # ISO-8601 timestamp of the last activity in the session
            "total_duration_seconds": 0,  # Total duration of the session in seconds
            "message_count": 0  # Number of messages exchanged in the session
        }
        affected_participants: Dict[str, Any] = {  # Information about affected participants
            "agent_ids": [],  # List of agent IDs affected by the expiration
            "agent_types": {},  # Map of agent IDs to their types
            "notification_status": {}  # Map of agent IDs to their notification status
        }
        recovery_information: Optional[Dict[str, Any]] = None  # Information about session recovery options
        context: Dict[str, Any] = {}  # Additional context information
```

**Example Payload:**
```json
{
    "event_type": "session_expired",
    "session_id": "session_789abc",
    "expired_at": "2025-05-25T14:30:23Z",
    "reason": "timeout",
    "metadata": {
        "last_activity": "2025-05-25T13:00:12Z",
        "timeout_duration": 5400
    },
    "affected_agents": ["user_agent_123", "assistant_agent_456", "specialist_agent_789"],
    "recovery_options": {
        "can_restore": true,
        "restore_within_seconds": 1800,
        "restore_endpoint": "/api/v1/sessions/restore/session_789abc"
    }
}
```

**Example: Handling Session Expiration**

```python
# Example: Subscribing to SessionExpiredEvent in Agent Framework
@event_bus.subscribe(SessionExpiredEvent)
def handle_session_expiration(event: SessionExpiredEvent):
    # Log the session expiration
    logger.info(
        f"Session {event.session_id} expired at {event.expired_at} due to {event.reason}. "
        f"Affected agents: {len(event.affected_agents)}"
    )
    
    # Notify affected agents about the session expiration
    for agent_id in event.affected_agents:
        try:
            agent_notification_service.notify_session_expiration(
                agent_id=agent_id,
                session_id=event.session_id,
                expired_at=event.expired_at,
                reason=event.reason,
                recovery_options=event.recovery_options
            )
            logger.debug(f"Notified agent {agent_id} about session expiration")
        except NotificationError as e:
            logger.error(f"Failed to notify agent {agent_id} about session expiration: {e}")
    
    # Handle recovery options if available
    if event.recovery_options and event.recovery_options.get("can_restore", False):
        # Register session for potential recovery
        session_recovery_service.register_recoverable_session(
            session_id=event.session_id,
            expiry_time=datetime.now() + timedelta(seconds=event.recovery_options.get("restore_within_seconds", 1800))
        )
        logger.info(f"Registered session {event.session_id} for potential recovery within {event.recovery_options.get('restore_within_seconds', 1800)} seconds")
    
    # For A2A protocol sessions, update agent cards to reflect session expiration
    if "a2a" in event.metadata.get("protocols", []):
        a2a_session_manager.update_agent_cards_for_expired_session(
            session_id=event.session_id,
            affected_agents=event.affected_agents,
            expiration_reason=event.reason
        )
        logger.debug(f"Updated A2A agent cards for expired session {event.session_id}")
    
    # For MCP protocol sessions, close any open tool connections
    if "mcp" in event.metadata.get("protocols", []):
        mcp_session_manager.close_tool_connections(
            session_id=event.session_id,
            affected_agents=event.affected_agents
        )
        logger.debug(f"Closed MCP tool connections for expired session {event.session_id}")
```
```

```python
class SessionStateInvalidEvent:
    """
    Event emitted when session state becomes invalid.
    """
    event_type: str = "session_state_invalid"  # Type of the event
    session_id: str  # ID of the affected session
    validation_time: datetime  # When the validation occurred
    validation_errors: List[ValidationError]  # List of validation errors
    invalid_fields: List[str]  # List of fields that failed validation
    current_state_version: int  # Version of the state that failed validation
    last_valid_state_version: Optional[int] = None  # Last known valid state version
    update_id: Optional[str] = None  # ID of the update that caused the invalid state
    severity: str  # Severity of the validation issue (e.g., "warning", "error", "critical")
    metadata: Dict[str, Any] = {}  # Additional metadata about the validation
    suggested_corrections: Optional[Dict[str, Any]] = None  # Suggested corrections to fix the invalid state
    
    class Payload:
        """
        Payload containing details of the session state validation failure.
        """
        session_id: str  # ID of the affected session
        validation_details: Dict[str, Any] = {  # Details about the validation failure
            "validation_time": None,  # ISO-8601 timestamp of when validation occurred
            "severity": "",  # Severity level (warning, error, critical)
            "update_id": None  # ID of the update that caused the invalid state
        }
        state_version_info: Dict[str, Any] = {  # Information about state versions
            "current_version": 0,  # Version of the state that failed validation
            "last_valid_version": None,  # Last known valid state version
            "can_rollback": False  # Whether rollback to last valid version is possible
        }
        validation_results: Dict[str, Any] = {  # Details of the validation results
            "invalid_fields": [],  # List of fields that failed validation
            "errors": []  # List of validation error details
        }
        correction_info: Dict[str, Any] = {  # Information about potential corrections
            "has_suggestions": False,  # Whether correction suggestions are available
            "auto_fix_available": False,  # Whether automatic fix is available
            "suggested_corrections": None  # Suggested corrections to fix the invalid state
        }
        context: Dict[str, Any] = {}  # Additional context information
```

**Example Payload:**
```json
{
    "event_type": "session_state_invalid",
    "session_id": "session_789abc",
    "validation_time": "2025-05-25T15:10:45Z",
    "validation_errors": [
        {
            "field": "user_preferences.budget",
            "error_type": "type_error",
            "expected": "string",
            "received": "integer",
            "message": "Expected string for budget but received integer value 5000"
        },
        {
            "field": "current_topic",
            "error_type": "value_error",
            "expected": "one of [\"flight_booking\", \"hotel_booking\", \"activity_planning\"]",
            "received": "food_recommendations",
            "message": "current_topic must be one of the allowed values"
        }
    ],
    "invalid_fields": ["user_preferences.budget", "current_topic"],
    "current_state_version": 9,
    "last_valid_state_version": 8,
    "update_id": "update_567ghi",
    "severity": "error",
    "metadata": {
        "validation_rule_set": "travel_session_schema_v2",
        "initiated_by": "user_agent_123"
    },
    "suggested_corrections": {
        "user_preferences.budget": "5000",
        "current_topic": "activity_planning"
    }
}
```

### Session Management → Agent Framework

#### Methods/Functions

```python
def validate_session_access(agent_id: str, session_id: str, 
                         access_type: Optional[SessionAccessType] = None) -> SessionAccessResult:
    """
    Validate if an agent has access to a session.
    
    Args:
        agent_id: str - Identifier of the agent requesting access
        session_id: str - Identifier of the session to access
        access_type: Optional[SessionAccessType] - Type of access being requested (read, write, admin)
        
    Returns:
        SessionAccessResult - Result of the access validation check
        
    Raises:
        AgentNotFoundError - If the agent does not exist
        SessionNotFoundError - If the session does not exist
        SecurityValidationError - If there's an error during security validation
    """
```

**Data Structures:**

```python
class SessionAccessType(Enum):
    """
    Types of access to a session.
    """
    READ = "read"  # Read-only access to session data
    WRITE = "write"  # Ability to update session state
    ADMIN = "admin"  # Administrative access (add/remove participants, change settings)
    JOIN = "join"  # Ability to join as a participant
    OBSERVE = "observe"  # Ability to observe but not participate

class SessionAccessResult:
    """
    Result of a session access validation check.
    """
    has_access: bool  # Whether access is granted
    access_type: SessionAccessType  # Type of access that was validated
    session_id: str  # ID of the session that was checked
    agent_id: str  # ID of the agent that requested access
    validation_time: datetime  # When the validation occurred
    expiration_time: Optional[datetime] = None  # When this access validation expires
    access_token: Optional[str] = None  # Token that can be used for subsequent access
    restrictions: Dict[str, Any] = {}  # Any restrictions on the access (e.g., field limitations)
    reason: Optional[str] = None  # Reason for access denial if has_access is False
    security_context: Optional[SecurityContext] = None  # Security context for the access
```

**Example Usage:**
```python
# Check if an agent has admin access to a session
access_result = agent_framework.validate_session_access(
    agent_id="assistant_agent_456",
    session_id="session_789abc",
    access_type=SessionAccessType.ADMIN
)

if access_result.has_access:
    print(f"Agent {access_result.agent_id} has {access_result.access_type.value} access to session {access_result.session_id}")
    print(f"Access validated at {access_result.validation_time} and expires at {access_result.expiration_time}")
    
    # Perform admin operation with the validated access
    if access_result.access_type == SessionAccessType.ADMIN:
        add_participant_to_session(
            session_id=access_result.session_id,
            participant_id="specialist_agent_789",
            access_token=access_result.access_token
        )
else:
    print(f"Access denied: {access_result.reason}")
    # Handle access denial appropriately
    if access_result.reason == "insufficient_permissions":
        request_elevated_permissions(
            agent_id=access_result.agent_id,
            session_id=access_result.session_id,
            required_access_type=SessionAccessType.ADMIN
        )
```

```python
def get_session_capabilities(session_id: str, 
                          capability_filter: Optional[CapabilityFilter] = None) -> SessionCapabilitiesResult:
    """
    Get capabilities available in a session.
    
    Args:
        session_id: str - Identifier of the session to query
        capability_filter: Optional[CapabilityFilter] - Filter criteria for capabilities
        
    Returns:
        SessionCapabilitiesResult - Result containing available capabilities and metadata
        
    Raises:
        SessionNotFoundError - If the session does not exist
        CapabilityFilterError - If the filter criteria are invalid
        SessionAccessError - If there's an error accessing the session
    """
```

**Data Structures:**

```python
class CapabilityFilter:
    """
    Filter criteria for capabilities.
    """
    categories: Optional[List[str]] = None  # Filter by capability categories
    providers: Optional[List[str]] = None  # Filter by capability providers
    protocol_compatibility: Optional[List[str]] = None  # Filter by protocol compatibility
    min_version: Optional[str] = None  # Minimum capability version
    max_version: Optional[str] = None  # Maximum capability version
    include_disabled: bool = False  # Whether to include disabled capabilities
    include_metadata: bool = True  # Whether to include capability metadata
    include_schema: bool = False  # Whether to include capability schema

class Capability:
    """
    A capability available in a session.
    """
    id: str  # Unique identifier for the capability
    name: str  # Human-readable name of the capability
    description: str  # Description of what the capability does
    version: str  # Version of the capability
    category: str  # Category of the capability (e.g., "communication", "data_processing")
    provider: str  # Provider of the capability (typically an agent ID)
    protocol_compatibility: List[str] = []  # Protocols this capability is compatible with
    is_enabled: bool = True  # Whether the capability is currently enabled
    requires_authorization: bool = False  # Whether using the capability requires authorization
    parameters_schema: Optional[Dict[str, Any]] = None  # JSON schema for capability parameters
    return_schema: Optional[Dict[str, Any]] = None  # JSON schema for capability return value
    metadata: Dict[str, Any] = {}  # Additional metadata about the capability

class SessionCapabilitiesResult:
    """
    Result of a session capabilities query.
    """
    session_id: str  # ID of the session that was queried
    capabilities: List[Capability]  # List of available capabilities
    query_time: datetime  # When the query was performed
    total_count: int  # Total number of capabilities available
    filtered_count: int  # Number of capabilities after applying filters
    categories: List[str]  # List of all capability categories in this session
    providers: List[str]  # List of all capability providers in this session
    is_complete: bool = True  # Whether the result includes all matching capabilities
    next_page_token: Optional[str] = None  # Token for pagination if result is not complete
```

**Example Usage:**
```python
# Get all travel-related capabilities in a session provided by a specific agent
result = agent_framework.get_session_capabilities(
    session_id="session_789abc",
    capability_filter=CapabilityFilter(
        categories=["travel", "booking"],
        providers=["travel_agent_123"],
        protocol_compatibility=["a2a", "mcp"],
        include_disabled=False,
        include_schema=True
    )
)

if result.capabilities:
    print(f"Found {len(result.capabilities)} capabilities out of {result.total_count} total")
    print(f"Available categories: {', '.join(result.categories)}")
    
    # Print information about each capability
    for capability in result.capabilities:
        print(f"\nCapability: {capability.name} (v{capability.version})")
        print(f"Description: {capability.description}")
        print(f"Provider: {capability.provider}")
        print(f"Protocol compatibility: {', '.join(capability.protocol_compatibility)}")
        
        # Check if the capability requires authorization
        if capability.requires_authorization:
            print("Requires authorization before use")
            
        # Show parameter schema if available
        if capability.parameters_schema:
            print(f"Parameter requirements: {json.dumps(capability.parameters_schema, indent=2)}")
else:
    print(f"No matching capabilities found in session {result.session_id}")
    print(f"Available categories: {', '.join(result.categories)}")
    print(f"Available providers: {', '.join(result.providers)}")
```

```python
def notify_session_event(session_id: str, event: SessionEvent, 
                       notification_options: Optional[NotificationOptions] = None) -> NotificationResult:
    """
    Notify agent framework of session events.
    
    Args:
        session_id: str - Identifier of the session the event pertains to
        event: SessionEvent - The event to notify about
        notification_options: Optional[NotificationOptions] - Options for the notification
        
    Returns:
        NotificationResult - Result of the notification operation
        
    Raises:
        SessionNotFoundError - If the session does not exist
        EventValidationError - If the event is invalid
        NotificationDeliveryError - If there's an error delivering the notification
    """
```

**Data Structures:**

```python
class SessionEventType(Enum):
    """
    Types of session events.
    """
    PARTICIPANT_JOINED = "participant_joined"  # A participant joined the session
    PARTICIPANT_LEFT = "participant_left"  # A participant left the session
    MESSAGE_SENT = "message_sent"  # A message was sent in the session
    STATE_CHANGED = "state_changed"  # Session state was changed
    CAPABILITY_ADDED = "capability_added"  # A capability was added to the session
    CAPABILITY_REMOVED = "capability_removed"  # A capability was removed from the session
    SESSION_EXTENDED = "session_extended"  # Session expiration was extended
    SESSION_PAUSED = "session_paused"  # Session was paused
    SESSION_RESUMED = "session_resumed"  # Session was resumed
    SESSION_COMPLETED = "session_completed"  # Session was completed
    SESSION_ERROR = "session_error"  # An error occurred in the session
    CUSTOM_EVENT = "custom_event"  # A custom event type

class SessionEvent:
    """
    An event in a session.
    """
    event_type: SessionEventType  # Type of the event
    event_id: str  # Unique identifier for the event
    session_id: str  # ID of the session the event pertains to
    timestamp: datetime  # When the event occurred
    source_agent_id: Optional[str] = None  # ID of the agent that generated the event
    target_agent_ids: List[str] = []  # IDs of agents the event is targeted at (empty for broadcast)
    data: Dict[str, Any]  # Event-specific data
    importance: str = "normal"  # Importance of the event (low, normal, high, critical)
    correlation_id: Optional[str] = None  # ID to correlate related events
    metadata: Dict[str, Any] = {}  # Additional metadata about the event

class NotificationOptions:
    """
    Options for event notifications.
    """
    delivery_mode: str = "standard"  # How to deliver the notification (standard, immediate, batched)
    notification_targets: Optional[List[str]] = None  # Specific targets to notify (None = all participants)
    exclude_targets: List[str] = []  # Targets to exclude from notification
    notification_context: Dict[str, Any] = {}  # Additional context for the notification
    priority: str = "normal"  # Priority of the notification (low, normal, high, critical)
    persistence: bool = True  # Whether to persist the notification
    expiration_seconds: Optional[int] = None  # How long the notification is valid
    require_acknowledgment: bool = False  # Whether acknowledgment is required
    notification_channels: List[str] = ["default"]  # Channels to send the notification through

class NotificationResult:
    """
    Result of a notification operation.
    """
    success: bool  # Whether the notification was successful
    notification_id: str  # Unique identifier for the notification
    event_id: str  # ID of the event that was notified
    session_id: str  # ID of the session the notification pertains to
    timestamp: datetime  # When the notification was sent
    delivered_to: List[str]  # IDs of agents the notification was delivered to
    failed_deliveries: List[Dict[str, Any]] = []  # Details of failed deliveries
    pending_deliveries: List[str] = []  # IDs of agents with pending deliveries
    acknowledgments: List[Dict[str, Any]] = []  # Acknowledgments received
    metadata: Dict[str, Any] = {}  # Additional metadata about the notification
```

**Example Usage:**
```python
# Notify about a participant joining the session
result = agent_framework.notify_session_event(
    session_id="session_789abc",
    event=SessionEvent(
        event_type=SessionEventType.PARTICIPANT_JOINED,
        event_id="event_123def",
        session_id="session_789abc",
        timestamp=datetime.now(),
        source_agent_id="session_manager",
        data={
            "participant_id": "specialist_agent_789",
            "join_time": datetime.now(),
            "role": "specialist",
            "capabilities": ["japan_travel_expert", "itinerary_optimization"]
        },
        importance="normal",
        metadata={
            "invitation_source": "assistant_agent_456",
            "join_reason": "specialized_knowledge_required"
        }
    ),
    notification_options=NotificationOptions(
        delivery_mode="immediate",
        notification_targets=["user_agent_123", "assistant_agent_456"],
        priority="high",
        require_acknowledgment=True,
        notification_channels=["default", "urgent"]
    )
)

if result.success:
    print(f"Notification sent successfully at {result.timestamp}")
    print(f"Delivered to: {', '.join(result.delivered_to)}")
    
    if result.pending_deliveries:
        print(f"Pending deliveries: {', '.join(result.pending_deliveries)}")
        
    if result.acknowledgments:
        print("Received acknowledgments:")
        for ack in result.acknowledgments:
            print(f"- From: {ack['agent_id']} at {ack['timestamp']}")
else:
    print("Notification failed")
    if result.failed_deliveries:
        print("Failed deliveries:")
        for failure in result.failed_deliveries:
            print(f"- Agent: {failure['agent_id']}, Reason: {failure['reason']}")
```

#### Events

```python
class AgentJoinedSessionEvent:
    """
    Event emitted when an agent joins a session.
    """
    event_type: str = "agent_joined_session"  # Type of the event
    session_id: str  # ID of the session the agent joined
    agent_id: str  # ID of the agent that joined
    join_time: datetime  # When the agent joined
    join_method: str  # How the agent joined (e.g., "invitation", "direct", "auto")
    role: str  # Role of the agent in the session (e.g., "participant", "observer", "moderator")
    initiator_id: Optional[str] = None  # ID of the agent that initiated the join, if applicable
    capabilities_shared: List[str] = []  # List of capabilities the agent shared with the session
    metadata: Dict[str, Any] = {}  # Additional metadata about the join
    session_state_access_level: str = "standard"  # Level of access to session state (minimal, standard, full)
    
    class Payload:
        """
        Payload containing details of the agent joining a session event.
        """
        session_id: str  # ID of the session the agent joined
        agent_details: Dict[str, Any] = {  # Details about the agent that joined
            "agent_id": "",  # ID of the agent that joined
            "agent_name": "",  # Name of the agent
            "agent_type": "",  # Type of agent (user, assistant, specialist, etc.)
            "reasoning_approach": ""  # Reasoning approach used by the agent (llm, bdi, rule-based, etc.)
        }
        join_details: Dict[str, Any] = {  # Details about the join event
            "join_time": None,  # ISO-8601 timestamp of when the agent joined
            "join_method": "",  # How the agent joined (invitation, direct, auto)
            "initiator_id": None,  # ID of the agent that initiated the join
            "role": ""  # Role of the agent in the session
        }
        capabilities: Dict[str, Any] = {  # Information about capabilities shared with the session
            "shared_capabilities": [],  # List of capability IDs the agent shared
            "a2a_mapped_capabilities": {},  # A2A protocol-specific capability mappings
            "mcp_mapped_capabilities": {}  # MCP protocol-specific capability mappings
        }
        access_control: Dict[str, Any] = {  # Information about access control
            "session_state_access_level": "standard",  # Level of access to session state
            "participant_visibility": [],  # IDs of participants this agent can see
            "permission_level": "standard"  # Permission level granted to the agent
        }
        context: Dict[str, Any] = {}  # Additional context information
```

**Example Payload:**
```json
{
    "event_type": "agent_joined_session",
    "session_id": "session_789abc",
    "agent_id": "specialist_agent_789",
    "join_time": "2025-05-25T15:20:45Z",
    "join_method": "invitation",
    "role": "specialist",
    "initiator_id": "assistant_agent_456",
    "capabilities_shared": ["japan_travel_expert", "itinerary_optimization", "accommodation_booking"],
    "metadata": {
        "invitation_context": "specialized_knowledge_required",
        "acceptance_time": "2025-05-25T15:20:30Z",
        "expected_duration": "temporary"
    },
    "session_state_access_level": "standard"
}
```

**Example: Handling Agent Joining a Session**

```python
# Example: Subscribing to AgentJoinedSessionEvent in Agent Framework
@event_bus.subscribe(AgentJoinedSessionEvent)
def handle_agent_joined_session(event: AgentJoinedSessionEvent):
    # Log the agent joining
    logger.info(
        f"Agent {event.agent_id} joined session {event.session_id} at {event.join_time} "
        f"via {event.join_method} with role '{event.role}'"
    )
    
    # Update the agent's session registry
    agent_session_registry.register_session_participation(
        agent_id=event.agent_id,
        session_id=event.session_id,
        role=event.role,
        join_time=event.join_time
    )
    
    # Make shared capabilities available to other session participants
    capability_sharing_service.register_shared_capabilities(
        session_id=event.session_id,
        agent_id=event.agent_id,
        capabilities=event.capabilities_shared
    )
    
    # If this is an A2A protocol session, update agent cards
    if "a2a" in event.metadata.get("protocols", []):
        # Create protocol-specific agent card for A2A
        a2a_session_manager.update_agent_participation(
            session_id=event.session_id,
            agent_id=event.agent_id,
            role=event.role,
            capabilities=event.capabilities_shared,
            visible_to=[p for p in event.metadata.get("participants", []) if p != event.agent_id]
        )
        logger.debug(f"Updated A2A agent cards for session {event.session_id} with new participant {event.agent_id}")
    
    # If this is an MCP protocol session, expose agent capabilities as tools
    if "mcp" in event.metadata.get("protocols", []):
        # Register agent capabilities as tools in MCP
        mcp_session_manager.register_agent_tools(
            session_id=event.session_id,
            agent_id=event.agent_id,
            capabilities=event.capabilities_shared,
            tool_access_level=event.session_state_access_level
        )
        logger.debug(f"Registered MCP tools for session {event.session_id} from agent {event.agent_id}")
    
    # Notify other session participants about the new agent
    for participant_id in event.metadata.get("participants", []):
        if participant_id != event.agent_id:
            agent_notification_service.notify_participant_joined(
                recipient_id=participant_id,
                session_id=event.session_id,
                joined_agent_id=event.agent_id,
                role=event.role,
                capabilities=event.capabilities_shared
            )
```
```

```python
class AgentLeftSessionEvent:
    """
    Event emitted when an agent leaves a session.
    """
    event_type: str = "agent_left_session"  # Type of the event
    session_id: str  # ID of the session the agent left
    agent_id: str  # ID of the agent that left
    leave_time: datetime  # When the agent left
    leave_reason: str  # Reason for leaving (e.g., "completed", "ejected", "timeout", "error")
    initiator_id: Optional[str] = None  # ID of the agent that initiated the leave, if applicable
    participation_duration: int  # Duration of participation in seconds
    capabilities_withdrawn: List[str] = []  # List of capabilities the agent withdrew from the session
    metadata: Dict[str, Any] = {}  # Additional metadata about the leave
    can_rejoin: bool = True  # Whether the agent can rejoin the session
    
    class Payload:
        """
        Payload containing details of the agent leaving a session event.
        """
        session_id: str  # ID of the session the agent left
        agent_details: Dict[str, Any] = {  # Details about the agent that left
            "agent_id": "",  # ID of the agent that left
            "agent_name": "",  # Name of the agent
            "agent_type": "",  # Type of agent (user, assistant, specialist, etc.)
            "role": ""  # Role the agent had in the session
        }
        leave_details: Dict[str, Any] = {  # Details about the leave event
            "leave_time": None,  # ISO-8601 timestamp of when the agent left
            "leave_reason": "",  # Reason for leaving (completed, ejected, timeout, error)
            "initiator_id": None,  # ID of the agent that initiated the leave
            "participation_duration": 0,  # Duration of participation in seconds
            "can_rejoin": True  # Whether the agent can rejoin the session
        }
        capabilities: Dict[str, Any] = {  # Information about capabilities withdrawn from the session
            "withdrawn_capabilities": [],  # List of capability IDs the agent withdrew
            "remaining_capabilities": [],  # List of capabilities still available in the session
            "capability_impact": "none"  # Impact of capability withdrawal (none, minimal, significant, critical)
        }
        participation_summary: Dict[str, Any] = {  # Summary of the agent's participation
            "messages_sent": 0,  # Number of messages the agent sent during participation
            "tasks_completed": [],  # List of tasks the agent completed
            "contribution_summary": ""  # Summary of the agent's contribution to the session
        }
        context: Dict[str, Any] = {}  # Additional context information
```

**Example Payload:**
```json
{
    "event_type": "agent_left_session",
    "session_id": "session_789abc",
    "agent_id": "specialist_agent_789",
    "leave_time": "2025-05-25T15:45:30Z",
    "leave_reason": "completed",
    "initiator_id": "specialist_agent_789",
    "participation_duration": 1485,
    "capabilities_withdrawn": ["japan_travel_expert", "itinerary_optimization", "accommodation_booking"],
    "metadata": {
        "exit_message": "Task completed - provided specialized information on Japanese ryokans",
        "completed_tasks": ["accommodation_recommendations", "cultural_experience_advice"],
        "session_contribution_summary": "Provided specialized knowledge on traditional Japanese accommodations and helped optimize the itinerary for cultural experiences."
    },
    "can_rejoin": true
}
```

**Example: Handling Agent Leaving a Session**

```python
# Example: Subscribing to AgentLeftSessionEvent in Agent Framework
@event_bus.subscribe(AgentLeftSessionEvent)
def handle_agent_left_session(event: AgentLeftSessionEvent):
    # Log the agent leaving
    logger.info(
        f"Agent {event.agent_id} left session {event.session_id} at {event.leave_time} "
        f"due to {event.leave_reason} after {event.participation_duration} seconds"
    )
    
    # Update the agent's session registry
    agent_session_registry.update_session_participation(
        agent_id=event.agent_id,
        session_id=event.session_id,
        status="left",
        leave_time=event.leave_time,
        participation_duration=event.participation_duration
    )
    
    # Remove withdrawn capabilities from the session's available capabilities
    capability_sharing_service.withdraw_shared_capabilities(
        session_id=event.session_id,
        agent_id=event.agent_id,
        capabilities=event.capabilities_withdrawn
    )
    
    # If this is an A2A protocol session, update agent cards
    if "a2a" in event.metadata.get("protocols", []):
        # Update protocol-specific agent cards for A2A
        a2a_session_manager.remove_agent_participation(
            session_id=event.session_id,
            agent_id=event.agent_id,
            leave_reason=event.leave_reason,
            can_rejoin=event.can_rejoin
        )
        logger.debug(f"Updated A2A agent cards for session {event.session_id} to remove participant {event.agent_id}")
    
    # If this is an MCP protocol session, remove agent capabilities from available tools
    if "mcp" in event.metadata.get("protocols", []):
        # Unregister agent capabilities as tools in MCP
        mcp_session_manager.unregister_agent_tools(
            session_id=event.session_id,
            agent_id=event.agent_id,
            capabilities=event.capabilities_withdrawn
        )
        logger.debug(f"Unregistered MCP tools for session {event.session_id} from agent {event.agent_id}")
    
    # Notify other session participants about the agent leaving
    for participant_id in event.metadata.get("participants", []):
        if participant_id != event.agent_id:
            agent_notification_service.notify_participant_left(
                recipient_id=participant_id,
                session_id=event.session_id,
                left_agent_id=event.agent_id,
                leave_reason=event.leave_reason,
                contribution_summary=event.metadata.get("session_contribution_summary", ""),
                can_rejoin=event.can_rejoin
            )
    
    # If the agent can rejoin, register it for potential rejoining
    if event.can_rejoin:
        session_rejoining_registry.register_potential_rejoin(
            session_id=event.session_id,
            agent_id=event.agent_id,
            role=event.metadata.get("role", "participant"),
            previous_capabilities=event.capabilities_withdrawn
        )
        logger.debug(f"Registered agent {event.agent_id} for potential rejoining to session {event.session_id}")
```
```

## Data Flows

### Session Creation Flow
1. **Agent Framework → Session Management**: Agent Framework requests session creation
2. **Session Management Processing**: Session manager initializes session state and registers participants
3. **Session Management → Agent Framework**: Session manager returns initialized session
4. **Agent Framework → Participants**: Agent Framework notifies participants of session creation

### Session Update Flow
1. **Agent Framework → Session Management**: Agent Framework sends state updates
2. **Session Management Processing**: Session manager validates and applies updates
3. **Session Management → Agent Framework**: Session manager confirms update success
4. **Session Management → Participants**: Session manager notifies participants of relevant changes

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
session_management:
  session_types:
    - name: "conversation"
      implementation_class: "ConversationSession"
      default_timeout_seconds: 1800
      max_participants: 10
    
    - name: "task"
      implementation_class: "TaskSession"
      default_timeout_seconds: 3600
      max_participants: 5
  
  state_management:
    persistence_enabled: true
    persistence_provider: "redis"
    state_validation: true
  
  timeout_management:
    heartbeat_interval_seconds: 60
    inactivity_timeout_seconds: 600
    extension_allowed: true
    max_extensions: 3

agent_framework:
  session_integration:
    auto_join_sessions: true
    session_capability_sharing: "selective"
    session_event_propagation: true
```

## Error Handling

1. **Session Creation Failures**:
   - Detailed error logging with creation parameters
   - Retry with simplified parameters if complex creation fails
   - Fallback to default session type if specified type is unavailable

2. **Session State Inconsistencies**:
   - State validation before persistence
   - Automatic correction of minor inconsistencies
   - Session freezing for major inconsistencies pending manual resolution

3. **Session Timeouts**:
   - Configurable timeout handling (terminate, extend, notify)
   - Graceful participant notification before timeout
   - Session state archiving for terminated sessions

## Extension Points

1. **Custom Session Types**:
   - New session types can be added by implementing the Session interface
   - Session interface:
     ```python
     class Session:
         def initialize(self, parameters: SessionParameters) → str:
             # Initialize session with parameters and return session ID
             pass
         
         def validate_state_update(self, updates: Dict[str, Any]) → bool:
             # Validate if state updates are valid for this session type
             pass
             
         def add_participant(self, participant_id: str, role: str) → bool:
             # Add a participant to the session
             pass
             
         def remove_participant(self, participant_id: str) → bool:
             # Remove a participant from the session
             pass
     ```

2. **State Persistence Providers**:
   - Custom state persistence mechanisms can be added
   - Default providers include in-memory, Redis, and database options

## Notes on Multi-Protocol Design

The Agent Framework ↔ Session Management interface supports OpenMAS's multi-protocol design by:

- Providing protocol-agnostic session management that works across different protocols
- Supporting protocol-specific session attributes when needed
- Enabling session sharing between agents using different protocols
- Ensuring consistent session semantics regardless of underlying protocol

## Notes on A2A and MCP Protocol Support

This interface explicitly supports both Google's A2A protocol and the Model Context Protocol (MCP):

- Session handling follows A2A specifications for conversation and task sessions
- MCP-specific session attributes are supported
- Session capabilities reflect both A2A and MCP capabilities
- Protocol-specific authentication and authorization are integrated with session validation

## Example: A2A Card Handling in Sessions

```python
class A2ASessionHandler:
    def initialize_with_card(self, agent_card: Dict[str, Any], session_id: str) → bool:
        """Initialize an A2A session using an agent card"""
        # Extract session parameters from A2A card
        session_params = SessionParameters(
            initiator_id=agent_card.get("agent_id"),
            participants=agent_card.get("allowed_agents", []),
            session_type="conversation",
            metadata={
                "api_version": agent_card.get("api_version"),
                "display_name": agent_card.get("display_name"),
                "description": agent_card.get("description"),
            },
            timeout_seconds=agent_card.get("session_timeout_seconds", 1800)
        )
        
        # Create session with extracted parameters
        session = session_manager.create_session(parameters=session_params)
        
        # Register agent capabilities from card
        capabilities = []
        for tool in agent_card.get("tools", []):
            capabilities.append(Capability(
                id=tool.get("name"),
                description=tool.get("description"),
                parameters=tool.get("parameters")
            ))
            
        # Add capabilities to session
        for capability in capabilities:
            session_manager.add_session_capability(
                session_id=session.id,
                capability=capability,
                provider_id=agent_card.get("agent_id")
            )
            
        return True
```
