# Agent Framework ↔ Knowledge Representation & Reasoning (KR&R) System

## Relationship Summary
- **Agent Framework → KR&R System**: Facilitates access to knowledge bases for configured reasoning engines
- **KR&R System → Agent Framework**: Provides knowledge management services through standardized interfaces

## Interface Definitions

### Agent Framework → ReasoningEngine → KR&R System Flow

The Agent Framework does not directly interact with the KR&R System. Instead, it:

1. Instantiates the appropriate `ReasoningEngine` based on the agent's `reasoning.approach` configuration
2. Facilitates the `ReasoningEngine`'s access to knowledge bases managed by the KR&R System based on the agent's `knowledge_management_config`

#### ReasoningEngine Methods (implemented by each reasoning approach)

```python
def process_message(message: InternalMessage, context: ReasoningContext) -> InternalMessage:
    """
    Process a message using the reasoning engine.
    
    Args:
        message: InternalMessage - The message to process in the Standard Internal Message Format
        context: ReasoningContext - A context object containing additional information for reasoning
        
    Returns:
        InternalMessage - Response message in the Standard Internal Message Format
        
    Raises:
        ReasoningError - If the reasoning process fails
        SecurityViolationError - If a security violation is detected during processing
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

class MessageType(Enum):
    """
    Enum of possible message types in the Standard Internal Message Format.
    """
    USER_QUERY = "user_query"  # Query from a user
    AGENT_RESPONSE = "agent_response"  # Response from an agent
    CAPABILITY_INVOCATION = "capability_invocation"  # Request to invoke a capability
    CAPABILITY_RESULT = "capability_result"  # Result of a capability invocation
    # Additional message types as defined in the SIMF standard

class MessagePayload:
    """
    Payload structure for the Standard Internal Message Format.
    """
    payload_type: PayloadType  # Type of payload content
    content: Any  # The actual payload content, type depends on payload_type
    # Structure details defined in SIMF standard

class PayloadType(Enum):
    """
    Types of payload content in the Standard Internal Message Format.
    """
    TEXT_CONTENT = "text_content"  # Plain text content
    STRUCTURED_CONTENT = "structured_content"  # JSON/dict structured content
    TOOL_CALL = "tool_call"  # Tool/capability invocation
    TOOL_RESULT = "tool_result"  # Result of tool/capability invocation
    MULTI_PART = "multi_part"  # Multi-part message with multiple content types
    # Additional payload types as defined in the SIMF standard

class ReasoningContext:
    """
    Context information provided to reasoning engines.
    """
    security_principal_info: SecurityPrincipalInfo  # Information about the authenticated principal
    session_id: str  # ID of the current session
    conversation_history: List[InternalMessage] = []  # Recent conversation history
    agent_state: Dict[str, Any] = {}  # Current agent state information
    environment_info: Dict[str, Any] = {}  # Information about the execution environment
    timestamp: datetime = datetime.now()  # When this context was created
```

**Example Usage:**
```python
response = reasoning_engine.process_message(
    message=InternalMessage(
        message_id="msg-123",
        message_type=MessageType.USER_QUERY,
        created_at=datetime.now(),
        payload=MessagePayload(
            payload_type=PayloadType.TEXT_CONTENT,
            content={"text": "What time is it?"}
        )
    ),
    context=ReasoningContext(
        security_principal_info=SecurityPrincipalInfo(
            id="user-123",
            type="user",
            roles=["standard_user"],
            attributes={"department": "engineering"}
        ),
        session_id="session-456",
        conversation_history=[...],  # Previous messages in conversation
        agent_state={"current_task": "answering_query"}
    )
)
```

```python
def initialize(config: ReasoningEngineConfig, knowledge_client: KnowledgeClient, 
              reasoning_security_interface: Optional[ReasoningSecurityInterface] = None) -> None:
    """
    Initialize the reasoning engine with configuration and necessary client interfaces.
    
    Args:
        config: ReasoningEngineConfig - Engine-specific configuration parameters
        knowledge_client: KnowledgeClient - Client to access knowledge bases managed by the KR&R System
        reasoning_security_interface: Optional[ReasoningSecurityInterface] - Interface for security-related
            operations during reasoning
            
    Raises:
        InvalidConfigurationError - If the provided configuration is invalid
        KnowledgeClientInitializationError - If the knowledge client cannot be initialized
    """
```

**Data Structures:**

```python
class ReasoningEngineConfig:
    """
    Configuration for a reasoning engine.
    """
    approach: str  # The reasoning approach identifier (e.g., "llm", "bdi", "rule_based")
    parameters: Dict[str, Any] = {}  # Engine-specific parameters
    security_integration: SecurityIntegrationConfig = SecurityIntegrationConfig()  # Security integration settings
    resources: Dict[str, str] = {}  # External resources needed by this engine
    performance_constraints: Optional[PerformanceConstraints] = None  # Performance requirements
    
    # Engine-specific sections based on the 'approach'
    llm_config: Optional[LLMReasoningConfig] = None  # Only for LLM-based reasoning
    bdi_config: Optional[BDIReasoningConfig] = None  # Only for BDI reasoning
    rule_based_config: Optional[RuleBasedReasoningConfig] = None  # Only for rule-based reasoning
    symbolic_config: Optional[SymbolicReasoningConfig] = None  # Only for symbolic reasoning
    hybrid_config: Optional[HybridReasoningConfig] = None  # Only for hybrid reasoning

class SecurityIntegrationConfig:
    """
    Configuration for security integration in reasoning engines.
    """
    rsi_enabled: bool = False  # Whether the Reasoning Security Interface is enabled
    authorization_level: str = "standard"  # Level of authorization checks
    secure_data_handling: bool = True  # Whether to apply secure data handling procedures

class KnowledgeClient:
    """
    Client interface for accessing knowledge bases managed by the KR&R System.
    """
    def __init__(self, knowledge_management_config: KnowledgeManagementConfig):
        """
        Initialize the knowledge client with the specified configuration.
        
        Args:
            knowledge_management_config: KnowledgeManagementConfig - Configuration for knowledge management
        """
        pass
        
    def get_knowledge_base(self, kb_id: str) -> IKnowledgeBase:
        """
        Get a specific knowledge base by ID.
        
        Args:
            kb_id: str - The identifier of the knowledge base
            
        Returns:
            IKnowledgeBase - Interface to the requested knowledge base
            
        Raises:
            KnowledgeBaseNotFoundError - If the requested knowledge base doesn't exist
        """
        pass
    
    def query(self, kb_id: str, query: KRRQuery) -> KRRResult:
        """
        Query a specific knowledge base.
        
        Args:
            kb_id: str - The identifier of the knowledge base
            query: KRRQuery - The query to execute
            
        Returns:
            KRRResult - The result of the query
            
        Raises:
            KnowledgeBaseNotFoundError - If the requested knowledge base doesn't exist
            QueryExecutionError - If the query execution fails
        """
        pass
```

**Example Usage:**
```python
reasoning_engine.initialize(
    config=ReasoningEngineConfig(
        approach="symbolic_engine",
        parameters={
            "inference_depth": 3,
            "certainty_threshold": 0.7
        },
        security_integration=SecurityIntegrationConfig(
            rsi_enabled=True,
            authorization_level="strict"
        )
    ),
    knowledge_client=KnowledgeClient(knowledge_management_config),
    reasoning_security_interface=RSIImplementation() if rsi_enabled else None
)
```

### Security Context and Reasoning Security Interface (RSI)

The Agent Framework passes security context information to reasoning engines, allowing them to make security-aware decisions during their execution:

1. **Security Context Propagation**: When invoking a reasoning engine, the Agent Framework includes the authenticated principal information as part of the `ReasoningContext` object.

2. **Reasoning Security Interface (RSI)**: If configured, the Agent Framework provides an implementation of the RSI to the reasoning engine, allowing it to:
   - Access the current principal's information (`get_current_principal()`)
   - Perform fine-grained security checks (`check_permission()`)

3. **Usage Pattern**:
   ```python
   # Inside a reasoning engine implementation
   def process_message(self, message, context):
       # Access security principal information from the context
       principal = context.security_principal_info
       
       # Use the RSI for fine-grained security checks
       if self.rsi:
           # Check if principal has permission to access certain knowledge
           permission_result = self.rsi.check_permission(
               action="access_knowledge",
               resource_identifier="knowledge:sensitive_data",
               context={"message_type": message.message_type}
           )
           
           if permission_result.is_allowed():
               # Access the sensitive knowledge
               sensitive_data = self.knowledge_client.query("sensitive_data_kb", "...") 
           else:
               # Handle permission denied case
               pass
   ```

For more details about the RSI, refer to the [Reasoning Security Interface specification](../../../17_security/reasoning_security_interface.md).

#### KR&R System Interface (IKnowledgeBase)

> **Update:** The `IKnowledgeBase` interface is now precisely specified with explicit method signatures and Pydantic models for all knowledge item and query types. See `/09_knowledge_representation/knowledge_access_interfaces/interfaces.md` for the authoritative definition. All code and documentation should reference this as the single source of truth for knowledge base interaction.

```python
<!--
=========================
[PROPOSED REFACTOR PLAN: IKnowledgeBase Interface]
=========================

This section is flagged for asynchronous human review before any changes are executed.

**Summary:**
The legacy IKnowledgeBase interface below is inconsistent with the new canonical interface defined in `/09_knowledge_representation/knowledge_access_interfaces/interfaces.md`. The canonical interface uses explicit async method signatures, Pydantic models, and supports specialized knowledge operations (e.g., graph and vector search). Migration is required for consistency, maintainability, and type safety.

**Key Inconsistencies:**
- Method names and signatures differ (legacy: add, query, update, delete, get_status; canonical: add_knowledge, retrieve_knowledge, update_knowledge, delete_knowledge, query_knowledge_graph, vector_similarity_search, get_knowledge_item_by_id)
- Legacy types (KRRQuery, KRRResult, KnowledgeAddResult, etc.) are not guaranteed to be Pydantic models or may be undefined
- Error handling is explicit in legacy docstrings, but not in canonical interface
- Canonical interface covers more operations and is extensible for new knowledge types

**Proposed Actions:**
1. Remove the legacy interface definition and replace with a reference and summary of the canonical interface in `interfaces.md`.
2. Update all type references to use the new Pydantic models and enums.
3. Add a note clarifying that error handling is implementation-specific.
4. If status/metadata methods are still required, propose them as optional extensions and flag for further review.
5. List and flag any downstream documentation/code that depends on legacy result/status types for migration.

**Downstream Documentation/Code Affected:**
- `/09_knowledge_representation/reasoning/interfaces.md` (references and describes IKnowledgeBase)
- `/01_architecture/components_summary.md` (references IKnowledgeBase and knowledge access)
- `/09_knowledge_representation/architecture.md` (references interface and method set)
- Any code or docs referring to `KRRQuery`, `KRRResult`, `KnowledgeAddResult`, `KnowledgeUpdateResult`, `KnowledgeDeleteResult`, `KnowledgeBaseStatus`, etc.
- Any test cases or examples using the legacy interface

**Next Steps:**
- Await asynchronous human review and approval of this plan.
- Upon approval, remove the legacy interface and update all references and downstream dependencies as described.
- Update TASK.md to reflect this review and migration plan.

-->
<!--
=========================
[PROPOSED REFACTOR PLAN: IKnowledgeBase Interface]
=========================

This section is flagged for asynchronous human review before any changes are executed.

**Summary:**
The legacy IKnowledgeBase interface below is inconsistent with the new canonical interface defined in `/09_knowledge_representation/knowledge_access_interfaces/interfaces.md`. The canonical interface uses explicit async method signatures, Pydantic models, and supports specialized knowledge operations (e.g., graph and vector search). Migration is required for consistency, maintainability, and type safety.

**Key Inconsistencies:**
- Method names and signatures differ (legacy: add, query, update, delete, get_status; canonical: add_knowledge, retrieve_knowledge, update_knowledge, delete_knowledge, query_knowledge_graph, vector_similarity_search, get_knowledge_item_by_id)
- Legacy types (KRRQuery, KRRResult, KnowledgeAddResult, etc.) are not guaranteed to be Pydantic models or may be undefined
- Error handling is explicit in legacy docstrings, but not in canonical interface
- Canonical interface covers more operations and is extensible for new knowledge types

**Proposed Actions:**
1. Remove the legacy interface definition and replace with a reference and summary of the canonical interface in `interfaces.md`.
2. Update all type references to use the new Pydantic models and enums.
3. Add a note clarifying that error handling is implementation-specific.
4. If status/metadata methods are still required, propose them as optional extensions and flag for further review.
5. List and flag any downstream documentation/code that depends on legacy result/status types for migration.

**Downstream Documentation/Code Affected:**
- `/09_knowledge_representation/reasoning/interfaces.md` (references and describes IKnowledgeBase)
- `/01_architecture/components_summary.md` (references IKnowledgeBase and knowledge access)
- `/09_knowledge_representation/architecture.md` (references interface and method set)
- Any code or docs referring to `KRRQuery`, `KRRResult`, `KnowledgeAddResult`, `KnowledgeUpdateResult`, `KnowledgeDeleteResult`, `KnowledgeBaseStatus`, etc.
- Any test cases or examples using the legacy interface

**Next Steps:**
- Await asynchronous human review and approval of this plan.
- Upon approval, remove the legacy interface and update all references and downstream dependencies as described.
- Update TASK.md to reflect this review and migration plan.

-->

#### Canonical IKnowledgeBase Interface (OpenMAS 0.3.0)

The IKnowledgeBase interface is now defined exclusively in `/09_knowledge_representation/knowledge_access_interfaces/interfaces.md` and should be referenced as the single source of truth for all knowledge base interaction. All legacy interface definitions and types (e.g., KRRQuery, KRRResult, KnowledgeAddResult) are deprecated.

**Canonical Method Signatures (summary):**
- `async def add_knowledge(self, knowledge_item: KnowledgeItem) -> KnowledgeItemReceipt`
- `async def retrieve_knowledge(self, query: KnowledgeQuery) -> List[KnowledgeItem]`
- `async def update_knowledge(self, item_id: str, updated_item_content: KnowledgeItemContent) -> KnowledgeItemReceipt`
- `async def delete_knowledge(self, item_id: str) -> bool`
- `async def query_knowledge_graph(self, sparql_query: str) -> List[Dict[str, Any]]`
- `async def vector_similarity_search(self, vector: List[float], top_k: int) -> List[SimilarityHit]`
- `async def get_knowledge_item_by_id(self, item_id: str) -> Optional[KnowledgeItem]`

All parameters and return values are defined as Pydantic models and enums (see `interfaces.md` for details).

> **Error Handling:**
> Error handling is implementation-specific and should follow Python best practices. The canonical interface does not specify exceptions in the method signatures.

> **Status/Metadata:**
> If knowledge base status/metadata is needed, propose as an extension to the canonical interface and flag for review.

        Get the status of the knowledge base.
        
        Returns:
            KnowledgeBaseStatus - Current status of the knowledge base
        """
        pass
```

**Data Structures:**

```python
# Base classes and type variables for knowledge representation
KnowledgeItem = TypeVar('KnowledgeItem')  # Specific type depends on knowledge representation formalism
KRRQuery = TypeVar('KRRQuery')  # Specific type depends on knowledge representation formalism
KRRResult = TypeVar('KRRResult')  # Specific type depends on knowledge representation formalism

class KnowledgeAddResult:
    """
    Result of an add operation on a knowledge base.
    """
    success: bool  # Whether the operation was successful
    knowledge_id: Optional[str] = None  # ID assigned to the added knowledge, if applicable
    timestamp: datetime = datetime.now()  # When the knowledge was added
    metadata: Dict[str, Any] = {}  # Additional metadata about the operation

class KnowledgeUpdateResult:
    """
    Result of an update operation on a knowledge base.
    """
    success: bool  # Whether the operation was successful
    previous_version: Optional[str] = None  # Reference to previous version, if versioning is supported
    timestamp: datetime = datetime.now()  # When the knowledge was updated
    metadata: Dict[str, Any] = {}  # Additional metadata about the operation

class KnowledgeDeleteResult:
    """
    Result of a delete operation on a knowledge base.
    """
    success: bool  # Whether the operation was successful
    timestamp: datetime = datetime.now()  # When the knowledge was deleted
    metadata: Dict[str, Any] = {}  # Additional metadata about the operation

class KnowledgeBaseStatus:
    """
    Status information for a knowledge base.
    """
    connected: bool  # Whether the knowledge base is connected
    read_only: bool = False  # Whether the knowledge base is in read-only mode
    item_count: int = 0  # Number of knowledge items in the knowledge base
    last_updated: Optional[datetime] = None  # When the knowledge base was last updated
    health: str = "healthy"  # Health status (healthy, degraded, error)
    metadata: Dict[str, Any] = {}  # Additional metadata about the knowledge base
```

**Example Usage:**

```python
# For a symbolic knowledge base
result = await symbolic_kb.add(
    SymbolicFact("location(user, kitchen, 0.9)")
)

# For a graph knowledge base
result = await graph_kb.add(
    GraphTriple(
        subject="user",
        predicate="location",
        object="kitchen",
        metadata={"confidence": 0.9, "source": "perception"}
    )
)

# Querying examples
symbolic_results = await symbolic_kb.query(
    SymbolicQuery("location(user, ?place, ?confidence)")
)

vector_results = await vector_kb.query(
    VectorQuery(
        text="Where is the user?",
        top_k=5,
        similarity_threshold=0.7
    )
)
```

**Type Implementations for Specific Knowledge Representations:**

```python
# Symbolic Knowledge Representation
class SymbolicFact(KnowledgeItem):
    """
    A fact in symbolic knowledge representation.
    """
    expression: str  # The symbolic expression
    certainty: float = 1.0  # Certainty factor (0.0-1.0)
    metadata: Dict[str, Any] = {}  # Additional metadata

class SymbolicQuery(KRRQuery):
    """
    A query for symbolic knowledge representation.
    """
    expression: str  # The query expression with optional variables
    max_results: int = 100  # Maximum number of results to return

# Graph Knowledge Representation
class GraphTriple(KnowledgeItem):
    """
    A subject-predicate-object triple for graph knowledge representation.
    """
    subject: str  # Subject of the triple
    predicate: str  # Predicate/relationship
    object: str  # Object of the triple
    metadata: Dict[str, Any] = {}  # Additional metadata

class GraphQuery(KRRQuery):
    """
    A query for graph knowledge representation.
    """
    pattern: Dict[str, Any]  # Query pattern to match
    filters: List[str] = []  # Additional filters for the query
    max_results: int = 100  # Maximum number of results
```

#### Events

```python
class KnowledgeBaseConnectedEvent:
    """
    Event fired when a connection to a knowledge base is established or changed.
    """
    knowledge_base_id: str  # Unique identifier for the knowledge base
    knowledge_base_type: str  # Type of knowledge base (e.g., "symbolic", "vector", "graph")
    connection_status: ConnectionStatus  # Current connection status
    agent_id: str  # ID of the agent using this knowledge base
    timestamp: datetime = datetime.now()  # When the connection status changed
    metadata: Dict[str, Any] = {}  # Additional metadata about the connection

class ConnectionStatus(Enum):
    """
    Possible connection statuses for a knowledge base.
    """
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTION_ERROR = "connection_error"
    RECONNECTING = "reconnecting"

class KnowledgeOperationCompletedEvent:
    """
    Event fired when a knowledge operation completes.
    """
    operation_type: KnowledgeOperationType  # Type of operation
    knowledge_base_id: str  # ID of the knowledge base
    success: bool  # Whether the operation was successful
    error_message: Optional[str] = None  # Error message if unsuccessful
    duration_ms: int  # Time taken for the operation in milliseconds
    operation_id: str  # Unique identifier for the operation
    agent_id: str  # ID of the agent that initiated the operation
    timestamp: datetime = datetime.now()  # When the operation completed
    result_size: Optional[int] = None  # Size of the result (if applicable)
    metadata: Dict[str, Any] = {}  # Additional metadata about the operation

class KnowledgeOperationType(Enum):
    """
    Types of knowledge operations.
    """
    ADD = "add"
    QUERY = "query"
    UPDATE = "update"
    DELETE = "delete"
    BATCH_ADD = "batch_add"
    BATCH_QUERY = "batch_query"
    BATCH_UPDATE = "batch_update"
    BATCH_DELETE = "batch_delete"
```

**Subscribers:**
- `KnowledgeBaseConnectedEvent`: Agent lifecycle manager, observability system
- `KnowledgeOperationCompletedEvent`: Observability system, performance monitoring components

### KR&R → Agent Framework

#### Methods/Functions

```python
def perception_update(self, perception_data: PerceptionData) -> None:
    """
    Updates the agent's perception data with new information from the environment.
    
    Args:
        perception_data: PerceptionData - Dictionary containing new perception data
        
    Raises:
        InvalidPerceptionDataError - If the perception data format is invalid
        AgentNotReadyError - If the agent is not in a state to receive perception updates
    """

class PerceptionData:
    """
    Data structure for perception updates provided to an agent.
    """
    source: str  # Source of the perception data (e.g., "user_input", "sensor", "environment")
    timestamp: datetime = datetime.now()  # When the perception occurred
    data: Dict[str, Any]  # The actual perception data
    confidence: Optional[float] = None  # Confidence level in the perception (0.0-1.0)
    metadata: Dict[str, Any] = {}  # Additional metadata about the perception
```

**Example Usage:**
```python
agent.perception_update(
    PerceptionData(
        source="user_interaction",
        timestamp=datetime.now(),
        data={
            "user_message": "Help me find a recipe",
            "user_location": "kitchen",
            "time_of_day": "evening"
        },
        confidence=0.95
    )
)
```

```python
def execute_action(self, action: Action) -> ActionResult:
    """
    Execute an action determined by the reasoning engine.
    
    Args:
        action: Action - Object representing the action to take
        
    Returns:
        ActionResult - Result of the action execution
        
    Raises:
        InvalidActionError - If the action is not valid
        ActionExecutionError - If the action execution fails
        PermissionDeniedError - If the agent doesn't have permission to execute the action
    """

class Action:
    """
    Represents an action to be executed by the agent.
    """
    type: ActionType  # Type of action to execute
    parameters: Dict[str, Any]  # Parameters for the action
    priority: int = 0  # Priority of the action (higher means more urgent)
    timeout_ms: Optional[int] = None  # Timeout for action execution in milliseconds
    idempotency_key: Optional[str] = None  # Key to ensure action is only executed once

class ActionType(Enum):
    """
    Types of actions an agent can execute.
    """
    SEND_MESSAGE = "send_message"  # Send a message to a recipient
    INVOKE_CAPABILITY = "invoke_capability"  # Invoke a capability
    ACCESS_RESOURCE = "access_resource"  # Access a resource
    UPDATE_STATE = "update_state"  # Update agent state
    DELEGATE_TASK = "delegate_task"  # Delegate a task to another agent

class ActionResult:
    """
    Result of an action execution.
    """
    success: bool  # Whether the action was successful
    action_id: str  # ID of the executed action
    completion_time: datetime = datetime.now()  # When the action completed
    result_data: Optional[Dict[str, Any]] = None  # Data produced by the action
    error_message: Optional[str] = None  # Error message if unsuccessful
    metadata: Dict[str, Any] = {}  # Additional metadata about the action result
```

**Example Usage:**
```python
result = agent.execute_action(
    Action(
        type=ActionType.SEND_MESSAGE,
        parameters={
            "content": "I can help you find a recipe. What ingredients do you have?",
            "recipient": "user",
            "message_type": "text"
        },
        priority=1
    )
)
```

```python
def goal_status_update(self, goal_id: str, status: GoalStatus, progress: Optional[float] = None) -> None:
    """
    Update the status of a goal in the agent framework.
    
    Args:
        goal_id: str - Unique identifier for the goal
        status: GoalStatus - New status of the goal
        progress: Optional[float] - Optional progress indicator (0.0-1.0)
        
    Raises:
        GoalNotFoundError - If the goal with the specified ID is not found
        InvalidStatusTransitionError - If the status transition is not valid
    """

class GoalStatus(Enum):
    """
    Possible statuses for an agent goal.
    """
    NOT_STARTED = "not_started"  # Goal has not been started yet
    IN_PROGRESS = "in_progress"  # Goal is currently being pursued
    COMPLETED = "completed"  # Goal has been successfully completed
    FAILED = "failed"  # Goal has failed
    BLOCKED = "blocked"  # Goal is blocked by some dependency
    ABANDONED = "abandoned"  # Goal has been abandoned
```

**Example Usage:**
```python
agent.goal_status_update(
    goal_id="goal-123",
    status=GoalStatus.IN_PROGRESS,
    progress=0.45  # 45% complete
)
```

#### Events

```python
class ReasoningDecisionMadeEvent:
    """
    Event fired when a reasoning decision is made.
    """
    decision_id: str  # Unique identifier for the decision
    decision_type: str  # Type of decision made
    agent_id: str  # ID of the agent making the decision
    reasoning_approach: str  # Reasoning approach used (e.g., "llm", "bdi", "rule_based")
    decision_details: Dict[str, Any]  # Details about the decision
    confidence: float  # Confidence level in the decision (0.0-1.0)
    context_summary: str  # Summary of the context in which the decision was made
    related_message_id: Optional[str] = None  # ID of related message if applicable
    timestamp: datetime = datetime.now()  # When the decision was made
    duration_ms: int = 0  # Time taken to make the decision in milliseconds
    metadata: Dict[str, Any] = {}  # Additional metadata about the decision

class KnowledgeQueryFailedEvent:
    """
    Event fired when a knowledge query fails.
    """
    query_id: str  # Unique identifier for the query
    knowledge_base_id: str  # ID of the knowledge base queried
    agent_id: str  # ID of the agent making the query
    query_details: Dict[str, Any]  # Details about the query
    failure_reason: str  # Reason for the failure
    error_code: str  # Error code if available
    attempt_number: int = 1  # Number of attempts made
    timestamp: datetime = datetime.now()  # When the query failed
    stack_trace: Optional[str] = None  # Stack trace if available
    metadata: Dict[str, Any] = {}  # Additional metadata about the failure
```

**Subscribers:**
- `ReasoningDecisionMadeEvent`: Agent action executor, observability system, decision logging components
- `KnowledgeQueryFailedEvent`: Error handling components, observability system, automatic recovery systems

## Data Flows

### Message Processing Flow
1. **Protocol Layer → Agent Framework**: Agent receives a message via a protocol interface
2. **Agent Framework → ReasoningEngine**: Agent Framework passes the message to the configured reasoning engine
3. **ReasoningEngine → KR&R System**: Reasoning engine queries relevant knowledge bases as needed
4. **KR&R System → ReasoningEngine**: Knowledge bases return requested information
5. **ReasoningEngine → Agent Framework**: Reasoning engine returns a processed response
6. **Agent Framework → Protocol Layer**: Agent Framework sends the response via the protocol interface

### Knowledge Management Flow
1. **ReasoningEngine → KR&R System**: Reasoning engine interacts with knowledge bases as configured
2. **KR&R System Processing**: KR&R System manages, indexes, and persists knowledge
3. **KR&R System → ReasoningEngine**: KR&R System provides knowledge access through standardized interfaces
4. **Knowledge Updates**: Knowledge bases can be updated by reasoning engines, external systems, or manual configuration

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
agents:
  example_agent:
    # Agent's primary reasoning engine selection
    reasoning:
      approach: "symbolic_engine"  # The "brain" - a specific reasoning engine
      implementation: "prolog_reasoner"  # Specific implementation
      options:
        rule_files: ["rules/basic.rules", "rules/domain.rules"]
        inference_depth: 5
    
    # Knowledge management configuration - how the reasoning engine uses the KR&R System
    knowledge_management_config:
      enabled: true
      knowledge_bases:
        - kb_id: "main_ontology"  # Reference to a knowledge base managed by the KR&R System
          type: "graph"
        - kb_id: "domain_rules"
          type: "symbolic_facts"
      default_knowledge_representation_types:
        - "symbolic_facts"
        - "graph"

# Global KR&R System configuration
krr_system:
  knowledge_bases:
    - id: "main_ontology"
      type: "graph"
      storage: "neo4j"
      connection:
        uri: "bolt://localhost:7687"
        credentials_secret: "neo4j_credentials"
    
    - id: "domain_rules"
      type: "symbolic_facts"
      storage: "prolog"
      file_path: "kb/domain_rules.pl"
    
    - id: "vector_store"
      type: "vector"
      storage: "qdrant"
      connection:
        uri: "http://localhost:6333"
```

## Error Handling

1. **Knowledge Base Connection Failures**:
   - Connection failures are detected and reported to the observability system
   - Knowledge base operations include retry logic with configurable backoff
   - The KR&R System can provide degraded service with partial knowledge base availability

2. **Knowledge Representation Errors**:
   - Invalid knowledge formats are detected and rejected with specific error messages
   - Knowledge base implementations validate inputs according to their representation types
   - Knowledge validation errors are reported to the observability system

3. **Query Execution Issues**:
   - Query timeouts are configurable per knowledge base type
   - Complex queries can be monitored and terminated if they exceed resource limits
   - Failed queries return structured error information that reasoning engines can handle gracefully

## Extension Points

1. **Reasoning Engines**:
   - New reasoning approaches can be added by implementing the ReasoningEngine interface
   - ReasoningEngine interface:
     ```python
     class ReasoningEngine:
         def decide_action(self, context: Context) → Action:
             # Determine appropriate action based on context
             pass
         
         def evaluate_goal(self, goal: Goal, context: Context) → GoalStatus:
             # Evaluate if a goal is achieved or achievable
             pass
             
         def update_knowledge(self, perception: Perception) → None:
             # Update internal knowledge based on new perception
             pass
     ```

2. **Knowledge Representations**:
   - Multiple knowledge representation formats can be supported
   - Custom belief validation and inference mechanisms can be added

## Notes on Reasoning Agnosticism

The Agent Framework ↔ KR&R interface is central to OpenMAS's reasoning agnostic architecture:

- The KR&R component represents the agent "brain" in the body-brain separation
- Different reasoning paradigms (rule-based, BDI, LLM-based, hybrid) can be used interchangeably
- The Agent Framework maintains a consistent interface to KR&R regardless of the underlying reasoning approach
- This allows OpenMAS to bridge classical AI and modern neural approaches while providing flexibility to choose the right reasoning approach for each task
- The Context and Action objects provide a standardized format for communication between the Agent Framework and any reasoning engine implementation
