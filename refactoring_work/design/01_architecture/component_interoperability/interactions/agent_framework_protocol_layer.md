# Agent Framework ↔ Protocol Layer

## Relationship Summary
- **Agent Framework → Protocol Layer**: Depends On
- **Protocol Layer → Agent Framework**: Provides To

## Interface Definitions

### Agent Framework → Protocol Layer

#### Methods/Functions

```python
def send_message(message: InternalMessage, protocol_type: ProtocolType, 
               target_info: Optional[TargetInfo] = None) -> MessageSendResult:
    """
    Send a message using the specified protocol.
    
    Args:
        message: InternalMessage - The message in Standard Internal Message Format to be sent
        protocol_type: ProtocolType - Type of protocol to use for sending the message
        target_info: Optional[TargetInfo] - Additional information about the target recipient
            
    Returns:
        MessageSendResult - Result containing the unique message identifier and send status
        
    Raises:
        ProtocolNotAvailableError - If the specified protocol is not available
        MessageTranslationError - If the message cannot be translated to the protocol format
        MessageSendError - If the message cannot be sent
        InvalidTargetError - If the target information is invalid or incomplete
    """
```

**Data Structures:**

```python
class InternalMessage:
    """
    Standard Internal Message Format (SIMF) used for inter-component communication.
    Defined in 00b_overview/01_architecture/internal_message_format_standard.md
    """
    message_id: str  # Unique identifier for the message
    message_type: MessageType  # Enum type defining the message purpose/category
    sender_id: Optional[str] = None  # ID of the sending entity
    recipient_id: Optional[str] = None  # ID of the intended recipient
    created_at: datetime  # When the message was created
    correlation_id: Optional[str] = None  # ID for message correlation/threading
    in_reply_to: Optional[str] = None  # ID of message this is replying to
    payload: MessagePayload  # The actual message content
    metadata: Dict[str, Any] = {}  # Additional metadata about the message

class ProtocolType(Enum):
    """
    Types of communication protocols supported by the Protocol Layer.
    """
    A2A_HTTP = "a2a-http"  # Google's A2A protocol over HTTP
    A2A_WEBSOCKET = "a2a-websocket"  # Google's A2A protocol over WebSockets
    A2A_GRPC = "a2a-grpc"  # Google's A2A protocol over gRPC
    MCP_STDIO = "mcp-stdio"  # Model Context Protocol over stdio
    MCP_SSE = "mcp-sse"  # Model Context Protocol over Server-Sent Events
    MCP_STREAMABLE = "mcp-streamable"  # Model Context Protocol with streaming support
    HTTP = "http"  # Standard HTTP protocol
    WEBSOCKET = "websocket"  # Standard WebSocket protocol
    MQTT = "mqtt"  # MQTT protocol
    GRPC = "grpc"  # gRPC protocol

class TargetInfo:
    """
    Additional information about the target recipient for a message.
    """
    recipient_id: str  # ID of the recipient
    protocol_specific_address: Optional[str] = None  # Protocol-specific address (e.g., URL, topic)
    routing_key: Optional[str] = None  # Optional routing key for message routing
    security_context: Optional[Dict[str, Any]] = None  # Security context for the message
    delivery_constraints: Optional[Dict[str, Any]] = None  # Constraints on message delivery

class MessageSendResult:
    """
    Result of a message send operation.
    """
    message_id: str  # Unique identifier for the message
    status: MessageSendStatus  # Status of the send operation
    timestamp: datetime = datetime.now()  # When the send operation completed
    protocol_specific_metadata: Dict[str, Any] = {}  # Protocol-specific metadata about the send operation
    error_details: Optional[str] = None  # Details if the send failed

class MessageSendStatus(Enum):
    """
    Status of a message send operation.
    """
    SENT = "sent"  # Message was sent successfully
    QUEUED = "queued"  # Message was queued for sending
    FAILED = "failed"  # Message failed to send
    PARTIAL = "partial"  # Message was partially sent (e.g., to some recipients but not others)
```

**Example Usage:**
```python
message_result = protocol_layer.send_message(
    message=InternalMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.AGENT_RESPONSE,
        sender_id="agent-123",
        recipient_id="user-456",
        created_at=datetime.now(),
        payload=MessagePayload(
            payload_type=PayloadType.TEXT_CONTENT,
            content={"text": "Hello, how can I help you today?"}
        )
    ),
    protocol_type=ProtocolType.A2A_HTTP,
    target_info=TargetInfo(
        recipient_id="user-456",
        protocol_specific_address="https://example.com/agents/user-456",
        security_context={"auth_token": "jwt_token_here"}
    )
)
```

```python
def register_agent(agent_id: str, agent_config: AgentConfig) -> AgentRegistrationResult:
    """
    Register an agent with its capabilities in the protocol layer, making it available for communication.
    
    Args:
        agent_id: str - Unique identifier for the agent
        agent_config: AgentConfig - Configuration containing capabilities and protocol settings
            
    Returns:
        AgentRegistrationResult - Result of the registration operation
        
    Raises:
        AgentAlreadyRegisteredError - If an agent with the same ID is already registered
        InvalidCapabilityError - If any of the capabilities are invalid
        UnsupportedProtocolError - If any of the protocols are not supported
        RegistrationError - If the registration fails for other reasons
    """
```

**Data Structures:**

```python
class AgentConfig:
    """
    Configuration for an agent, including its capabilities and protocol settings.
    Reference to the unified configuration schema in 00b_overview/03_configuration/unified_configuration_schema.md
    """
    name: str  # Name of the agent
    description: Optional[str] = None  # Description of the agent
    multi_protocol_capabilities: MultiProtocolCapabilities  # Capabilities of the agent across protocols
    protocol_settings: Dict[ProtocolType, ProtocolSettings] = {}  # Protocol-specific settings
    security: Optional[AgentSecurityConfig] = None  # Security configuration
    metadata: Dict[str, Any] = {}  # Additional metadata about the agent

class MultiProtocolCapabilities:
    """
    Definition of agent capabilities that can be mapped to multiple protocols.
    """
    core: List[CapabilityDefinition]  # Core capability definitions
    protocol_mapping: Dict[ProtocolType, Dict[str, str]] = {}  # Mapping of core capabilities to protocol-specific IDs

class CapabilityDefinition:
    """
    Definition of a single capability provided by an agent.
    """
    id: str  # Unique identifier for the capability
    name: str  # Human-readable name of the capability
    description: str  # Description of what the capability does
    parameters: Optional[List[CapabilityParameter]] = None  # Parameters accepted by the capability
    return_value: Optional[CapabilityReturnValue] = None  # Return value of the capability
    examples: Optional[List[CapabilityExample]] = None  # Examples of using the capability

class ProtocolSettings:
    """
    Protocol-specific settings for an agent.
    """
    enabled: bool = True  # Whether this protocol is enabled for the agent
    address: Optional[str] = None  # Protocol-specific address for the agent
    adapter_config: Dict[str, Any] = {}  # Configuration for the protocol adapter
    visibility: ProtocolVisibility = ProtocolVisibility.PUBLIC  # Visibility of the agent on this protocol

class ProtocolVisibility(Enum):
    """
    Visibility settings for an agent on a specific protocol.
    """
    PUBLIC = "public"  # Agent is visible to all
    PRIVATE = "private"  # Agent is only visible to authorized entities
    INTERNAL = "internal"  # Agent is only visible within the system

class AgentRegistrationResult:
    """
    Result of an agent registration operation.
    """
    success: bool  # Whether the registration was successful
    agent_id: str  # ID of the registered agent
    registered_protocols: List[ProtocolType]  # Protocols the agent was registered for
    registration_timestamp: datetime = datetime.now()  # When the registration occurred
    protocol_specific_identifiers: Dict[ProtocolType, str] = {}  # Protocol-specific identifiers assigned to the agent
    warnings: List[str] = []  # Any warnings that occurred during registration
    error_message: Optional[str] = None  # Error message if registration failed
```

**Example Usage:**
```python
result = protocol_layer.register_agent(
    agent_id="reasoning_agent_01",
    agent_config=AgentConfig(
        name="Reasoning Agent",
        description="An agent that provides reasoning capabilities",
        multi_protocol_capabilities=MultiProtocolCapabilities(
            core=[
                CapabilityDefinition(
                    id="reasoning",
                    name="Reasoning",
                    description="Perform logical reasoning on input data"
                ),
                CapabilityDefinition(
                    id="tool_use",
                    name="Tool Use",
                    description="Use external tools to accomplish tasks"
                )
            ],
            protocol_mapping={
                ProtocolType.A2A_HTTP: {"reasoning": "reasoning", "tool_use": "tool_use"},
                ProtocolType.MCP_SSE: {"reasoning": "reasoning_capability", "tool_use": "tool_usage"}
            }
        ),
        protocol_settings={
            ProtocolType.A2A_HTTP: ProtocolSettings(
                enabled=True,
                address="https://example.com/agents/reasoning_agent_01"
            ),
            ProtocolType.MCP_SSE: ProtocolSettings(
                enabled=True,
                adapter_config={"stream_mode": "full"}
            )
        }
    )
)
```

#### Events

```python
class MessageSendFailedEvent:
    """
    Event fired when a message fails to send.
    """
    message_id: str  # ID of the message that failed to send
    protocol_type: ProtocolType  # Protocol that was being used
    error_code: str  # Error code for the failure
    error_message: str  # Detailed error message
    sender_id: str  # ID of the agent that attempted to send the message
    recipient_id: Optional[str] = None  # ID of the intended recipient, if known
    timestamp: datetime = datetime.now()  # When the failure occurred
    retryable: bool = False  # Whether the send operation can be retried
    retry_after_ms: Optional[int] = None  # Suggested delay before retry, if retryable
    correlation_id: Optional[str] = None  # Correlation ID for tracking related events
    metadata: Dict[str, Any] = {}  # Additional metadata about the failure

    class Payload:
        """
        Payload containing details of the message send failure.
        """
        message_id: str  # ID of the message that failed to send
        protocol_type: str  # String representation of the protocol that was being used
        error_details: Dict[str, Any] = {  # Detailed information about the error
            "code": "",  # Error code for the failure
            "message": "",  # Human-readable error message
            "retryable": False,  # Whether the operation can be retried
            "retry_after_ms": None  # Suggested delay before retry if retryable
        }
        message_details: Dict[str, Any] = {  # Details about the message that failed
            "sender_id": "",  # ID of the sender agent
            "recipient_id": None,  # ID of the intended recipient, if known
            "correlation_id": None,  # For tracking related messages/events
            "message_type": None,  # Type of the message that failed
            "created_at": None  # When the original message was created
        }
        context: Dict[str, Any] = {}  # Additional context information

class ProtocolUnavailableEvent:
    """
    Event fired when a protocol becomes unavailable.
    """
    protocol_type: ProtocolType  # Protocol that became unavailable
    reason: str  # Reason for the unavailability
    error_code: Optional[str] = None  # Error code if applicable
    expected_duration_ms: Optional[int] = None  # Expected duration of unavailability in milliseconds
    affected_agents: List[str] = []  # IDs of agents affected by the unavailability
    timestamp: datetime = datetime.now()  # When the protocol became unavailable
    recovery_action: Optional[str] = None  # Suggested recovery action
    is_transient: bool = True  # Whether the unavailability is expected to be temporary
    
    class Payload:
        """
        Payload containing details of the protocol unavailability.
        """
        protocol_type: str  # String representation of the protocol that's unavailable
        unavailability_details: Dict[str, Any] = {  # Details about the unavailability
            "reason": "",  # Reason for the unavailability
            "error_code": None,  # Error code if applicable
            "expected_duration_ms": None,  # Expected duration of unavailability
            "is_transient": True,  # Whether the unavailability is temporary
            "recovery_action": None  # Suggested recovery action
        }
        affected_resources: Dict[str, Any] = {  # Resources affected by the unavailability
            "agents": [],  # List of affected agent IDs
            "capabilities": [],  # List of affected capability IDs
            "services": []  # List of affected service IDs
        }
        context: Dict[str, Any] = {}  # Additional context information
    metadata: Dict[str, Any] = {}  # Additional metadata about the unavailability
```

**Subscribers:**
- `MessageSendFailedEvent`: Agent Framework Communication Service, Session Management, Observability Service
- `ProtocolUnavailableEvent`: Agent Framework Communication Service, Session Management, Observability Service

**Example: Handling a Message Send Failure**

```python
# Example: Subscribing to MessageSendFailedEvent in Agent Framework
@event_bus.subscribe(MessageSendFailedEvent)
def handle_message_send_failure(event: MessageSendFailedEvent):
    # Log the failure
    logger.error(f"Message {event.message_id} failed to send using {event.protocol_type}: {event.error_message}")
    
    # Check if the message can be retried
    if event.retryable and event.retry_after_ms is not None:
        # Schedule a retry after the suggested delay
        retry_scheduler.schedule_retry(
            message_id=event.message_id,
            sender_id=event.sender_id,
            recipient_id=event.recipient_id,
            delay_ms=event.retry_after_ms
        )
        logger.info(f"Scheduled retry for message {event.message_id} after {event.retry_after_ms}ms")
    else:
        # Notify the sending agent about the permanent failure
        notification_service.notify_permanent_failure(
            agent_id=event.sender_id,
            message_id=event.message_id,
            error_code=event.error_code,
            error_message=event.error_message
        )
```

**Example: Handling Protocol Unavailability**

```python
# Example: Subscribing to ProtocolUnavailableEvent in Agent Framework
@event_bus.subscribe(ProtocolUnavailableEvent)
def handle_protocol_unavailability(event: ProtocolUnavailableEvent):
    # Log the unavailability
    logger.warning(
        f"Protocol {event.protocol_type} became unavailable: {event.reason}. "
        f"Expected duration: {event.expected_duration_ms or 'unknown'}ms"
    )
    
    # Update the protocol availability registry
    protocol_registry.set_availability(event.protocol_type, False)
    
    # If the unavailability affects specific agents, notify them
    for agent_id in event.affected_agents:
        agent_notification_service.notify_protocol_unavailability(
            agent_id=agent_id,
            protocol_type=event.protocol_type,
            reason=event.reason,
            expected_duration_ms=event.expected_duration_ms,
            recovery_action=event.recovery_action
        )
    
    # If a recovery action is suggested, attempt it
    if event.recovery_action and event.is_transient:
        protocol_recovery_service.execute_recovery_action(
            protocol_type=event.protocol_type,
            action=event.recovery_action
        )
```

### Protocol Layer → Agent Framework

The Protocol Layer interacts with the Agent Framework primarily through the `IMessageHandler` interface, which provides protocol-agnostic message handling.

#### Methods/Functions
{{ ... }}

```python
def receive_message(raw_message: Any, protocol_adapter: IProtocolAdapter) -> MessageProcessingResult:
    """
    Deliver a message received from an external source through the protocol layer.
    
    This is typically implemented by forwarding to the IMessageHandler's handle_incoming_message method.
    
    Args:
        raw_message: Any - The raw message data as received from the protocol-specific channel
        protocol_adapter: IProtocolAdapter - The adapter that received the message
            
    Returns:
        MessageProcessingResult - Result of the message processing operation including status and potential response
        
    Raises:
        MessageFormatError - If the message cannot be parsed into the internal format
        InvalidMessageError - If the message is well-formed but invalid for processing
        MessageRoutingError - If the message cannot be routed to an appropriate handler
        CapabilityNotFoundError - If the message targets a capability that doesn't exist
        SecurityViolationError - If the message violates security constraints
    """
```

**Data Structures:**

{{ ... }}
```python
class ProtocolInfo:
    """
    Information about the protocol and context for a received message.
    """
    protocol_type: ProtocolType  # Type of protocol the message was received through
    source_id: str  # ID of the source entity (agent, user, system)
    original_protocol_message: Optional[Any] = None  # The original protocol-specific message format
    transport_metadata: Dict[str, Any] = {}  # Metadata about the transport (headers, connection info, etc.)
    security_context: Optional[SecurityContext] = None  # Security context for the message
    receipt_timestamp: datetime = datetime.now()  # When the message was received
    trace_context: Optional[Dict[str, Any]] = None  # Distributed tracing context if available
    is_streaming: bool = False  # Whether this is part of a streaming message
    stream_id: Optional[str] = None  # ID of the stream if is_streaming is True

class SecurityContext:
    """
    Security information related to a received message.
    """
    authenticated: bool = False  # Whether the sender is authenticated
    principal_id: Optional[str] = None  # ID of the authenticated principal, if any
    principal_type: Optional[str] = None  # Type of the principal (user, agent, system)
    auth_token: Optional[str] = None  # Authentication token, if any
    permissions: List[str] = []  # Permissions associated with the principal
    security_level: str = "default"  # Security level for the message

class MessageReceiptResult:
    """
    Result of a message receipt operation.
    """
    receipt_id: str  # Unique identifier for the receipt operation
    status: MessageReceiptStatus  # Status of the receipt operation
    timestamp: datetime = datetime.now()  # When the receipt operation completed
    accepted: bool  # Whether the message was accepted for processing
    queued_for_processing: bool = False  # Whether the message was queued for processing
    error_message: Optional[str] = None  # Error message if not accepted
    acknowledgement_id: Optional[str] = None  # ID that can be used to acknowledge the message
    metadata: Dict[str, Any] = {}  # Additional metadata about the receipt operation

class MessageReceiptStatus(Enum):
    """
    Status of a message receipt operation.
    """
    ACCEPTED = "accepted"  # Message was accepted for processing
    REJECTED = "rejected"  # Message was rejected
    DEFERRED = "deferred"  # Message processing was deferred
    DUPLICATE = "duplicate"  # Message was a duplicate of a previously received message
    INVALID = "invalid"  # Message was invalid
```

**Example Usage:**
```python
receipt_result = agent_framework.receive_message(
    message=InternalMessage(
        message_id="msg-789",
        message_type=MessageType.USER_QUERY,
        sender_id="user-123",
        recipient_id="agent-456",
        created_at=datetime.now(),
        payload=MessagePayload(
            payload_type=PayloadType.TEXT_CONTENT,
            content={"text": "What's the weather today?"}
        )
    ),
    protocol_info=ProtocolInfo(
        protocol_type=ProtocolType.MCP_SSE,
        source_id="user-123",
        transport_metadata={
            "request_id": "req-456",
            "client_ip": "192.168.1.1",
            "user_agent": "Mozilla/5.0..."
        },
        security_context=SecurityContext(
            authenticated=True,
            principal_id="user-123",
            principal_type="user",
            permissions=["basic_interaction"],
            security_level="standard"
        )
    )
)
```

```python
def validate_capability(capability_id: str, agent_id: str, protocol_type: Optional[ProtocolType] = None) -> CapabilityValidationResult:
    """
    Validate that an agent has a specific capability, optionally for a specific protocol.
    
    Args:
        capability_id: str - Identifier for the capability to validate
        agent_id: str - Identifier of the agent to check
        protocol_type: Optional[ProtocolType] - Protocol to validate the capability for, if applicable
            
    Returns:
        CapabilityValidationResult - Result of the capability validation
        
    Raises:
        AgentNotFoundError - If the agent with the given ID is not found
        UnknownCapabilityError - If the capability is not recognized in the system
        ValidationError - If the validation process encounters an error
    """
```

**Data Structures:**

```python
class CapabilityValidationResult:
    """
    Result of validating an agent's capability.
    """
    is_valid: bool  # Whether the capability is valid for the agent
    capability_id: str  # ID of the validated capability
    agent_id: str  # ID of the agent
    protocol_type: Optional[ProtocolType] = None  # Protocol type, if validated for a specific protocol
    protocol_specific_id: Optional[str] = None  # Protocol-specific ID for the capability, if applicable
    validation_timestamp: datetime = datetime.now()  # When the validation was performed
    parameter_validation: Optional[Dict[str, bool]] = None  # Validation results for specific parameters
    permissions_granted: List[str] = []  # Permissions granted for this capability
    constraints: Dict[str, Any] = {}  # Any constraints on the capability usage
    metadata: Dict[str, Any] = {}  # Additional metadata about the validation
```

**Example Usage:**
```python
validation_result = agent_framework.validate_capability(
    capability_id="reasoning",
    agent_id="reasoning_agent_01",
    protocol_type=ProtocolType.A2A_HTTP
)

if validation_result.is_valid:
    # Proceed with capability invocation
    protocol_layer.send_message(
        message=InternalMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.CAPABILITY_INVOCATION,
            sender_id="user-123",
            recipient_id="reasoning_agent_01",
            created_at=datetime.now(),
            payload=MessagePayload(
                payload_type=PayloadType.TOOL_CALL,
                content={
                    "capability_id": validation_result.protocol_specific_id or "reasoning",
                    "parameters": {...}
                }
            )
        ),
        protocol_type=ProtocolType.A2A_HTTP
    )
else:
    # Handle invalid capability
    print(f"Capability {capability_id} is not valid for agent {agent_id}: {validation_result.metadata.get('reason')}")
```

#### Events

```python
class AgentRegisteredEvent:
    """
    Event fired when an agent is registered with the Agent Framework.
    """
    agent_id: str  # ID of the registered agent
    agent_name: str  # Name of the agent
    supported_protocols: List[ProtocolType]  # Protocols the agent supports
    capabilities: List[str]  # Core capability IDs the agent provides
    registration_timestamp: datetime = datetime.now()  # When the agent was registered
    protocol_specific_identifiers: Dict[ProtocolType, str] = {}  # Protocol-specific identifiers
    visibility: Dict[ProtocolType, ProtocolVisibility] = {}  # Visibility settings by protocol
    agent_type: str = "standard"  # Type of agent (standard, system, etc.)
    owner_id: Optional[str] = None  # ID of the agent owner, if applicable
    metadata: Dict[str, Any] = {}  # Additional metadata about the agent
    
    class Payload:
        """
        Payload containing details of the agent registration.
        """
        agent_id: str  # ID of the registered agent
        agent_details: Dict[str, Any] = {  # Details about the registered agent
            "name": "",  # Name of the agent
            "description": "",  # Description of the agent
            "type": "standard",  # Type of agent (standard, system, etc.)
            "owner_id": None,  # ID of the agent owner, if applicable
            "registration_timestamp": None  # ISO-8601 timestamp of registration
        }
        communication_details: Dict[str, Any] = {  # Details about the agent's communication capabilities
            "supported_protocols": [],  # List of protocol type strings
            "protocol_specific_identifiers": {},  # Protocol-specific identifiers
            "visibility": {}  # Visibility settings by protocol
        }
        capability_details: Dict[str, Any] = {  # Details about the agent's capabilities
            "core_capabilities": [],  # List of core capability IDs
            "protocol_mapped_capabilities": {}  # Protocol-specific capability mappings
        }
        context: Dict[str, Any] = {}  # Additional context information

class CapabilityUpdatedEvent:
    """
    Event fired when an agent's capabilities are updated.
    """
    agent_id: str  # ID of the agent whose capabilities were updated
    updated_capabilities: List[str]  # List of updated capability IDs
    added_capabilities: List[str] = []  # Capabilities that were added
    removed_capabilities: List[str] = []  # Capabilities that were removed
    modified_capabilities: List[str] = []  # Capabilities that were modified
    update_timestamp: datetime = datetime.now()  # When the update occurred
    reason: Optional[str] = None  # Reason for the capability update
    protocol_specific_updates: Dict[ProtocolType, Dict[str, str]] = {}  # Protocol-specific capability mappings that were updated
    initiated_by: Optional[str] = None  # ID of the entity that initiated the update
    metadata: Dict[str, Any] = {}  # Additional metadata about the update
    
    class Payload:
        """
        Payload containing details of the capability update.
        """
        agent_id: str  # ID of the agent whose capabilities were updated
        update_details: Dict[str, Any] = {  # Details about the capability update
            "update_timestamp": None,  # ISO-8601 timestamp of the update
            "reason": None,  # Reason for the update
            "initiated_by": None  # ID of the entity that initiated the update
        }
        capability_changes: Dict[str, Any] = {  # Details about the capability changes
            "added": [],  # List of added capability IDs
            "removed": [],  # List of removed capability IDs
            "modified": []  # List of modified capability IDs
        }
        protocol_specific_changes: Dict[str, Dict[str, Any]] = {}  # Protocol-specific capability mapping changes
        context: Dict[str, Any] = {}  # Additional context information
```

**Subscribers:**
- `AgentRegisteredEvent`: Protocol Layer routing component, agent discovery service, capability registry, observability system
- `CapabilityUpdatedEvent`: Protocol Layer capability registry, agent discovery service, observability system

**Example: Handling Agent Registration**

```python
# Example: Subscribing to AgentRegisteredEvent in Protocol Layer
@event_bus.subscribe(AgentRegisteredEvent)
def handle_agent_registration(event: AgentRegisteredEvent):
    # Log the registration
    logger.info(f"Agent {event.agent_name} (ID: {event.agent_id}) registered with {len(event.capabilities)} capabilities")
    
    # Register the agent in the protocol-specific routing tables
    for protocol_type in event.supported_protocols:
        protocol_id = event.protocol_specific_identifiers.get(protocol_type)
        visibility = event.visibility.get(protocol_type, ProtocolVisibility.PRIVATE)
        
        if protocol_id:
            # A2A protocol registration example
            if protocol_type in [ProtocolType.A2A_HTTP, ProtocolType.A2A_WEBSOCKET, ProtocolType.A2A_GRPC]:
                a2a_registry.register_agent(
                    agent_id=event.agent_id,
                    protocol_id=protocol_id,
                    capabilities=event.capabilities,
                    visibility=visibility,
                    agent_type=event.agent_type
                )
                logger.debug(f"Registered agent {event.agent_id} in A2A registry with protocol {protocol_type}")
            
            # MCP protocol registration example
            elif protocol_type in [ProtocolType.MCP_STDIO, ProtocolType.MCP_SSE, ProtocolType.MCP_STREAMABLE]:
                mcp_registry.register_agent(
                    agent_id=event.agent_id,
                    protocol_id=protocol_id,
                    capabilities=event.capabilities,
                    visibility=visibility,
                    agent_type=event.agent_type
                )
                logger.debug(f"Registered agent {event.agent_id} in MCP registry with protocol {protocol_type}")
    
    # Update agent discovery service
    discovery_service.update_agent_record(
        agent_id=event.agent_id,
        agent_name=event.agent_name,
        capabilities=event.capabilities,
        protocols=event.supported_protocols,
        visibility={p: v for p, v in event.visibility.items()},
        metadata=event.metadata
    )
```

**Example: Handling Capability Updates**

```python
# Example: Subscribing to CapabilityUpdatedEvent in Protocol Layer
@event_bus.subscribe(CapabilityUpdatedEvent)
def handle_capability_update(event: CapabilityUpdatedEvent):
    # Log the capability update
    logger.info(
        f"Agent {event.agent_id} capabilities updated: "
        f"{len(event.added_capabilities)} added, {len(event.removed_capabilities)} removed, "
        f"{len(event.modified_capabilities)} modified"
    )
    
    # Update the agent's capabilities in the capability registry
    capability_registry.update_agent_capabilities(
        agent_id=event.agent_id,
        added=event.added_capabilities,
        removed=event.removed_capabilities,
        modified=event.modified_capabilities,
        reason=event.reason,
        initiated_by=event.initiated_by
    )
    
    # Update protocol-specific capability mappings
    for protocol_type, capability_mappings in event.protocol_specific_updates.items():
        # A2A protocol capability update example
        if protocol_type in [ProtocolType.A2A_HTTP, ProtocolType.A2A_WEBSOCKET, ProtocolType.A2A_GRPC]:
            a2a_registry.update_agent_capabilities(
                agent_id=event.agent_id,
                capability_mappings=capability_mappings
            )
            logger.debug(f"Updated agent {event.agent_id} capabilities in A2A registry for protocol {protocol_type}")
        
        # MCP protocol capability update example
        elif protocol_type in [ProtocolType.MCP_STDIO, ProtocolType.MCP_SSE, ProtocolType.MCP_STREAMABLE]:
            mcp_registry.update_agent_capabilities(
                agent_id=event.agent_id,
                capability_mappings=capability_mappings
            )
            logger.debug(f"Updated agent {event.agent_id} capabilities in MCP registry for protocol {protocol_type}")
    
    # Update agent discovery service
    discovery_service.update_agent_capabilities(
        agent_id=event.agent_id,
        updated_capabilities=event.updated_capabilities,
        timestamp=event.update_timestamp
    )
```

## Data Flows

### Message Routing Flow
1. **External → Protocol Layer**: External component sends a message to the Protocol Layer
2. **Protocol Layer → Agent Framework**: Protocol Layer translates the message and routes it to the Agent Framework
3. **Agent Framework → Protocol Layer**: Agent Framework processes the message and sends a response to the Protocol Layer
4. **Protocol Layer → External**: Protocol Layer translates the response to the appropriate protocol format and sends it

### Agent Registration Flow
1. **Agent Framework → Protocol Layer**: Agent Framework registers an agent with the Protocol Layer
2. **Protocol Layer → External**: Protocol Layer makes the agent available to external components via supported protocols
3. **Protocol Layer → Agent Framework**: Protocol Layer forwards incoming requests to the registered agent

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
protocol_layer:
  supported_protocols:
    - type: "a2a"
      enabled: true
      adapter_class: "A2AProtocolAdapter"
    - type: "mcp"
      enabled: true
      adapter_class: "MCPProtocolAdapter"
  
  default_protocol: "a2a"
  
  connection_settings:
    max_retries: 3
    timeout_seconds: 30

agent_framework:
  message_routing:
    max_queue_size: 1000
    processing_threads: 4
  
  protocol_settings:
    preferred_protocols:
      - "a2a"
      - "mcp"
```

## Error Handling

1. **Connection Failures**:
   - Protocol Layer attempts to reconnect based on `max_retries` configuration
   - If all retries fail, a `message_send_failed` event is triggered
   - Agent Framework can implement fallback strategies

2. **Invalid Messages**:
   - Protocol Layer validates incoming messages before translation
   - Invalid messages are logged and discarded
   - Validation failures are reported to the Observability System

3. **Protocol Mismatches**:
   - If an agent doesn't support a requested protocol, a protocol mismatch error is raised
   - Agent Framework may attempt to use an alternative protocol if available

## Extension Points

1. **Protocol Adapters**:
   - New protocols can be added by implementing the Protocol Adapter interface
   - Protocol Adapter interface:
     ```python
     class ProtocolAdapter:
         def translate_incoming(self, external_message: Any) -> Message:
             # Translate external protocol message to internal format
             pass
         
         def translate_outgoing(self, internal_message: Message) -> Any:
             # Translate internal message to external protocol format
             pass
             
         def send(self, message: Any) -> MessageId:
             # Send message using protocol-specific mechanism
             pass
     ```

2. **Message Transformers**:
   - Additional message transformations can be added to the message pipeline
   - Example: Adding a message sanitizer or enricher

## Notes on Reasoning Agnosticism

According to the OpenMAS reasoning agnostic architecture:

- The Protocol Layer forms part of the agent "body" (communication infrastructure)
- The Agent Framework coordinates between the "body" and "brain" (reasoning component)
- This allows different reasoning approaches to be used with the same communication infrastructure
- Protocol Layer translation of messages should preserve reasoning-specific information for the KR&R component
