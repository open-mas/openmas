# Agent Framework ↔ Communication Pattern Engine

## Relationship Summary
- **Agent Framework → Communication Pattern Engine**: Depends On
- **Communication Pattern Engine → Agent Framework**: Provides To

## Interface Definitions

### Agent Framework → Communication Pattern Engine

#### Methods/Functions

```python
def get_pattern_implementation(pattern_name: str, context: PatternContext,
                             options: Optional[PatternOptions] = None) -> PatternImplementationResult:
    """
    Request a communication pattern implementation.

    Args:
        pattern_name: str - Name of the requested pattern
        context: PatternContext - Context information for pattern initialization
        options: Optional[PatternOptions] - Additional options for pattern instantiation

    Returns:
        PatternImplementationResult - Result containing the instantiated pattern and metadata

    Raises:
        PatternNotFoundError - If the requested pattern is not available
        PatternInitializationError - If the pattern fails to initialize
        InvalidPatternContextError - If the provided context is invalid for the pattern
    """
```

**Data Structures:**

```python
class PatternContext:
    """
    Context information for initializing a communication pattern.
    """
    initiator_id: str  # ID of the agent initiating the pattern
    participants: List[str]  # IDs of participating agents
    session_id: str  # ID of the session where the pattern will be used
    timeout_seconds: int = 60  # Timeout for the pattern execution
    metadata: Dict[str, Any] = {}  # Additional metadata for pattern initialization
    parent_pattern_id: Optional[str] = None  # Parent pattern ID if this is a sub-pattern
    initial_state: Optional[Dict[str, Any]] = None  # Initial state for the pattern
    protocol_type: str = "a2a"  # Protocol type for pattern implementation
    reason: Optional[str] = None  # Reason for using this pattern
    security_context: Optional[SecurityContext] = None  # Security context for the pattern

class PatternOptions:
    """
    Options for pattern instantiation.
    """
    variant: Optional[str] = None  # Specific variant of the pattern to use
    configuration_overrides: Dict[str, Any] = {}  # Overrides for pattern configuration
    validation_level: str = "strict"  # Level of validation for pattern messages (strict, lenient, none)
    allow_auto_correction: bool = False  # Whether to allow automatic correction of minor violations
    max_steps: Optional[int] = None  # Maximum number of steps in the pattern
    timeout_handling: str = "abort"  # How to handle timeouts (abort, extend, simplify)
    monitoring_level: str = "normal"  # Level of monitoring for pattern execution
    recovery_strategy: str = "default"  # Strategy for recovering from failures
    error_handling_policy: Dict[str, str] = {}  # Policies for handling specific error types

class CommunicationPattern:
    """
    Base class for communication pattern implementations.
    """
    pattern_id: str  # Unique identifier for this pattern instance
    pattern_name: str  # Name of the pattern
    pattern_version: str  # Version of the pattern implementation
    state: PatternState  # Current state of the pattern
    context: PatternContext  # Context in which this pattern operates
    start_time: datetime  # When the pattern was instantiated
    timeout_time: Optional[datetime] = None  # When the pattern will timeout
    options: PatternOptions  # Options for this pattern instance
    metadata: Dict[str, Any] = {}  # Additional metadata about the pattern

class PatternState:
    """
    State of a communication pattern.
    """
    state_id: str  # Unique identifier for this state
    status: PatternStatus  # Current status of the pattern
    current_step: int  # Current step in the pattern sequence
    expected_next_participant: Optional[str] = None  # ID of the agent expected to act next
    expected_next_actions: List[str] = []  # Types of actions expected next
    history: List[Dict[str, Any]] = []  # History of state transitions
    last_update_time: datetime  # When the state was last updated
    completion_percentage: float  # Percentage of pattern completion
    active_branches: List[str] = []  # Active branches in branching patterns
    custom_state_data: Dict[str, Any] = {}  # Pattern-specific state data

class PatternStatus(Enum):
    """
    Status of a communication pattern.
    """
    INITIALIZING = "initializing"  # Pattern is being initialized
    ACTIVE = "active"  # Pattern is active and in progress
    PAUSED = "paused"  # Pattern execution is paused
    COMPLETED = "completed"  # Pattern has completed successfully
    FAILED = "failed"  # Pattern has failed to complete
    TIMEOUT = "timeout"  # Pattern has timed out
    VIOLATED = "violated"  # Pattern constraints have been violated
    TERMINATED = "terminated"  # Pattern was terminated before completion

class PatternImplementationResult:
    """
    Result of a pattern implementation request.
    """
    pattern: CommunicationPattern  # The instantiated communication pattern
    pattern_id: str  # Unique identifier for the pattern instance
    initialization_time_ms: int  # Time taken to initialize the pattern in milliseconds
    initialization_success: bool  # Whether initialization was successful
    pattern_name: str  # Name of the pattern
    pattern_variant: Optional[str]  # Variant of the pattern if applicable
    initialization_warnings: List[str] = []  # Any warnings during initialization
    fallback_applied: bool = False  # Whether a fallback pattern was used
    original_pattern_name: Optional[str] = None  # Original requested pattern if fallback was applied
    supported_protocols: List[str] = []  # Protocols supported by this pattern implementation
    metadata: Dict[str, Any] = {}  # Additional metadata about the implementation
```

**Example Usage:**
```python
# Request an implementation of the chain-of-thought pattern for a complex reasoning task
result = pattern_engine.get_pattern_implementation(
    pattern_name="chain_of_thought",
    context=PatternContext(
        initiator_id="user_agent_123",
        participants=["assistant_agent_456", "reasoning_agent_789"],
        session_id="session_abc123",
        timeout_seconds=120,
        metadata={
            "task_type": "complex_reasoning",
            "domain": "mathematical_problem_solving",
            "complexity_level": "high"
        },
        protocol_type="a2a",
        reason="Need structured reasoning for multi-step math problem",
        security_context=SecurityContext(
            security_level="standard",
            permissions=["message_exchange", "state_update"]
        )
    ),
    options=PatternOptions(
        variant="branching",  # Use the branching variant of chain-of-thought
        configuration_overrides={
            "max_chain_length": 8,  # Override default max length
            "allow_branching": True,
            "branch_depth_limit": 3,
            "evaluation_strategy": "comparative"
        },
        validation_level="strict",
        allow_auto_correction=True,
        max_steps=20,
        timeout_handling="extend",  # Extend timeout rather than aborting
        monitoring_level="detailed",  # More detailed monitoring
        recovery_strategy="checkpoint_based",  # Use checkpoints for recovery
        error_handling_policy={
            "logic_error": "attempt_correction",
            "timeout": "simplify_remaining_steps",
            "participant_unavailable": "substitute_agent"
        }
    )
)

if result.initialization_success:
    pattern = result.pattern
    print(f"Successfully initialized {result.pattern_name} pattern (ID: {result.pattern_id})")
    print(f"Initialization time: {result.initialization_time_ms}ms")
    print(f"Pattern variant: {result.pattern_variant}")
    print(f"Pattern status: {pattern.state.status.value}")
    print(f"Expected timeout: {pattern.timeout_time}")

    # Access pattern-specific features based on the variant
    if result.pattern_variant == "branching":
        print(f"Maximum chain length: {pattern.options.configuration_overrides.get('max_chain_length')}")
        print(f"Maximum branch depth: {pattern.options.configuration_overrides.get('branch_depth_limit')}")

    # Check for any initialization warnings
    if result.initialization_warnings:
        print("\nInitialization warnings:")
        for warning in result.initialization_warnings:
            print(f"- {warning}")

    # Begin using the pattern
    # (Next steps would involve starting the pattern execution)
else:
    print(f"Failed to initialize {result.original_pattern_name or result.pattern_name} pattern")

    if result.fallback_applied:
        print(f"Fallback to {result.pattern_name} was applied")

    if result.initialization_warnings:
        print("\nInitialization errors:")
        for warning in result.initialization_warnings:
            print(f"- {warning}")
```

```python
def validate_message_sequence(pattern_id: str, messages: List[Message],
                          validation_options: Optional[ValidationOptions] = None) -> ValidationResult:
    """
    Validate if a sequence of messages follows the pattern constraints.

    Args:
        pattern_id: str - Identifier of the pattern to validate against
        messages: List[Message] - List of messages to validate
        validation_options: Optional[ValidationOptions] - Options for the validation process

    Returns:
        ValidationResult - Result of the validation process with details

    Raises:
        PatternNotFoundError - If the pattern with the given ID is not found
        InvalidMessageFormatError - If any message in the sequence has an invalid format
        ValidationError - If there's an error during the validation process
    """
```

**Data Structures:**

```python
class Message:
    """
    A message exchanged between agents in a communication pattern.
    """
    message_id: str  # Unique identifier for the message
    sender_id: str  # ID of the agent that sent the message
    recipient_ids: List[str]  # IDs of recipient agents
    content: Any  # Content of the message
    content_type: str  # Type of the content (e.g., "text", "json", "binary")
    timestamp: datetime  # When the message was sent
    pattern_id: Optional[str] = None  # ID of the pattern this message is part of
    pattern_step: Optional[int] = None  # Step in the pattern this message represents
    pattern_action: Optional[str] = None  # Action within the pattern this message represents
    correlation_id: Optional[str] = None  # ID to correlate related messages
    session_id: Optional[str] = None  # ID of the session this message belongs to
    metadata: Dict[str, Any] = {}  # Additional metadata about the message
    protocol_info: Dict[str, Any] = {}  # Protocol-specific information

class ValidationOptions:
    """
    Options for message sequence validation.
    """
    validation_level: str = "strict"  # Level of validation (strict, lenient, none)
    allow_out_of_order: bool = False  # Whether to allow messages that are out of order
    ignore_missing_steps: bool = False  # Whether to ignore missing steps in the pattern
    validate_content: bool = True  # Whether to validate message content
    validate_participants: bool = True  # Whether to validate message participants
    validate_timing: bool = False  # Whether to validate message timing
    include_detailed_validation: bool = True  # Whether to include detailed validation information
    max_violations_to_report: int = 10  # Maximum number of violations to report
    protocol_specific_validation: Dict[str, Any] = {}  # Protocol-specific validation options

class ValidationViolation:
    """
    A violation of pattern constraints found during validation.
    """
    violation_id: str  # Unique identifier for the violation
    violation_type: str  # Type of violation (e.g., "sequence", "participant", "content")
    message_id: Optional[str] = None  # ID of the message with the violation
    expected: Any  # What was expected according to the pattern
    actual: Any  # What was actually found in the message
    step_index: Optional[int] = None  # Index of the step where the violation occurred
    severity: str  # Severity of the violation ("error", "warning", "info")
    description: str  # Human-readable description of the violation
    suggested_correction: Optional[Any] = None  # Suggested correction for the violation
    is_correctable: bool = False  # Whether the violation can be automatically corrected

class ValidationResult:
    """
    Result of validating a message sequence against a pattern.
    """
    is_valid: bool  # Whether the sequence is valid according to the pattern
    pattern_id: str  # ID of the pattern used for validation
    validation_time_ms: int  # Time taken for validation in milliseconds
    validation_level: str  # Level of validation that was performed
    total_messages: int  # Total number of messages in the sequence
    valid_messages: int  # Number of valid messages
    violations: List[ValidationViolation] = []  # List of violations found
    is_correctable: bool = False  # Whether all violations can be automatically corrected
    suggested_corrections: Optional[List[Dict[str, Any]]] = None  # Suggested corrections for violations
    current_pattern_state: Optional[PatternState] = None  # Current state of the pattern after validation
    completion_percentage: float  # Percentage of pattern completion
    metadata: Dict[str, Any] = {}  # Additional metadata about the validation
```

**Example Usage:**
```python
# Validate a sequence of messages against a chain-of-thought pattern
validation_result = pattern_engine.validate_message_sequence(
    pattern_id="chain_of_thought_xyz789",
    messages=[
        Message(
            message_id="msg_123",
            sender_id="user_agent_123",
            recipient_ids=["assistant_agent_456"],
            content="Solve the equation: 3x^2 + 5x - 2 = 0",
            content_type="text",
            timestamp=datetime(2025, 5, 25, 15, 30, 0),
            pattern_step=0,
            pattern_action="problem_statement",
            session_id="session_abc123",
            metadata={
                "domain": "mathematics",
                "complexity": "medium"
            }
        ),
        Message(
            message_id="msg_124",
            sender_id="assistant_agent_456",
            recipient_ids=["reasoning_agent_789"],
            content={
                "problem": "3x^2 + 5x - 2 = 0",
                "approach": "quadratic_formula",
                "request": "detailed_solution"
            },
            content_type="json",
            timestamp=datetime(2025, 5, 25, 15, 30, 15),
            pattern_step=1,
            pattern_action="solution_approach",
            session_id="session_abc123",
            correlation_id="msg_123"
        ),
        Message(
            message_id="msg_125",
            sender_id="reasoning_agent_789",
            recipient_ids=["assistant_agent_456"],
            content={
                "step_1": "Identify a=3, b=5, c=-2 in the quadratic formula",
                "step_2": "Calculate discriminant: b^2 - 4ac = 5^2 - 4*3*(-2) = 25 + 24 = 49",
                "step_3": "Calculate roots: x = (-b ± √(b^2 - 4ac)) / (2a)",
                "step_4": "x = (-5 ± √49) / 6 = (-5 ± 7) / 6",
                "step_5": "x = (-5 + 7) / 6 = 2/6 = 1/3 or x = (-5 - 7) / 6 = -12/6 = -2",
                "conclusion": "The solutions are x = 1/3 and x = -2"
            },
            content_type="json",
            timestamp=datetime(2025, 5, 25, 15, 30, 45),
            pattern_step=2,
            pattern_action="detailed_solution",
            session_id="session_abc123",
            correlation_id="msg_124"
        )
    ],
    validation_options=ValidationOptions(
        validation_level="strict",
        allow_out_of_order=False,
        ignore_missing_steps=False,
        validate_content=True,
        validate_participants=True,
        validate_timing=True,
        include_detailed_validation=True,
        protocol_specific_validation={
            "a2a": {
                "verify_message_signatures": True,
                "check_protocol_headers": True
            }
        }
    )
)

if validation_result.is_valid:
    print(f"Message sequence is valid against pattern {validation_result.pattern_id}")
    print(f"Validation completed in {validation_result.validation_time_ms}ms")
    print(f"Pattern completion: {validation_result.completion_percentage:.1f}%")

    # If there's a current pattern state, check what's expected next
    if validation_result.current_pattern_state:
        state = validation_result.current_pattern_state
        if state.expected_next_participant:
            print(f"Next expected participant: {state.expected_next_participant}")
        if state.expected_next_actions:
            print(f"Next expected actions: {', '.join(state.expected_next_actions)}")
else:
    print(f"Message sequence is invalid against pattern {validation_result.pattern_id}")
    print(f"Found {len(validation_result.violations)} violations")

    # Display violations
    for i, violation in enumerate(validation_result.violations, 1):
        print(f"\nViolation {i} ({violation.severity}): {violation.violation_type}")
        print(f"Description: {violation.description}")
        print(f"Expected: {violation.expected}")
        print(f"Actual: {violation.actual}")

        if violation.is_correctable and violation.suggested_correction:
            print(f"Suggested correction: {violation.suggested_correction}")

    # Check if all violations can be automatically corrected
    if validation_result.is_correctable:
        print("\nAll violations can be automatically corrected.")
        # Apply corrections if desired
        # corrected_sequence = pattern_engine.apply_corrections(validation_result.suggested_corrections)
```

```python
def get_next_actions(pattern_id: str, current_state: PatternState,
                  action_options: Optional[ActionOptions] = None) -> NextActionsResult:
    """
    Get possible next actions within a communication pattern.

    Args:
        pattern_id: str - Identifier of the pattern
        current_state: PatternState - Current state of the pattern interaction
        action_options: Optional[ActionOptions] - Options for action retrieval

    Returns:
        NextActionsResult - Result containing possible next actions and metadata

    Raises:
        PatternNotFoundError - If the pattern with the given ID is not found
        InvalidPatternStateError - If the provided pattern state is invalid
        PatternCompletedError - If the pattern is already completed and no further actions are possible
    """
```

**Data Structures:**

```python
class PatternAction:
    """
    An action that can be taken within a communication pattern.
    """
    action_id: str  # Unique identifier for the action
    action_type: str  # Type of the action (e.g., "message", "state_update", "decision")
    description: str  # Human-readable description of the action
    actor_id: str  # ID of the agent that should perform this action
    required: bool  # Whether this action is required for pattern progression
    expected_next_state: Optional[str] = None  # Expected state after this action
    allowed_recipients: Optional[List[str]] = None  # IDs of allowed recipients for this action
    content_requirements: Optional[Dict[str, Any]] = None  # Requirements for action content
    timing_constraints: Optional[Dict[str, Any]] = None  # Timing constraints for this action
    priority: int = 0  # Priority of this action (higher value = higher priority)
    alternatives: List[str] = []  # IDs of alternative actions that could be taken instead
    context_dependent: bool = False  # Whether this action's availability depends on context
    metadata: Dict[str, Any] = {}  # Additional metadata about the action

class ActionOptions:
    """
    Options for retrieving next possible actions.
    """
    include_optional_actions: bool = True  # Whether to include optional actions
    max_actions: Optional[int] = None  # Maximum number of actions to return
    actor_filter: Optional[str] = None  # Filter actions to a specific actor
    action_type_filter: Optional[List[str]] = None  # Filter actions by type
    include_alternatives: bool = True  # Whether to include alternative actions
    prioritize_by: str = "pattern_definition"  # How to prioritize actions (pattern_definition, context, likelihood)
    include_context_dependent: bool = True  # Whether to include context-dependent actions
    context_data: Dict[str, Any] = {}  # Context data for evaluating context-dependent actions
    include_action_details: bool = True  # Whether to include detailed action information

class NextActionsResult:
    """
    Result of retrieving next possible actions in a pattern.
    """
    pattern_id: str  # ID of the pattern
    actions: List[PatternAction]  # List of possible next actions
    query_time_ms: int  # Time taken to retrieve actions in milliseconds
    state_id: str  # ID of the state used for action retrieval
    total_actions_available: int  # Total number of actions available
    returned_actions_count: int  # Number of actions returned
    is_complete: bool = True  # Whether all available actions are included
    pattern_progress: float  # Percentage of pattern completion
    expected_participants: List[str] = []  # Participants expected to take the next actions
    decision_points: List[Dict[str, Any]] = []  # Decision points in the pattern where flow could branch
    path_taken: List[Dict[str, Any]] = []  # Path taken so far in the pattern
    remaining_required_actions: int  # Number of required actions remaining
    metadata: Dict[str, Any] = {}  # Additional metadata about the next actions
```

**Example Usage:**
```python
# Get the next possible actions in a chain-of-thought pattern
next_actions_result = pattern_engine.get_next_actions(
    pattern_id="chain_of_thought_xyz789",
    current_state=current_pattern_state,  # This would be a PatternState object from previous execution
    action_options=ActionOptions(
        include_optional_actions=True,
        max_actions=5,
        actor_filter="assistant_agent_456",  # Only get actions for this agent
        action_type_filter=["message", "reasoning_step"],
        include_alternatives=True,
        prioritize_by="context",  # Prioritize based on context
        context_data={
            "user_intent": "detailed_explanation",
            "complexity_level": "high",
            "previous_interaction_quality": "good"
        },
        include_action_details=True
    )
)

if next_actions_result.actions:
    print(f"Found {next_actions_result.returned_actions_count} possible next actions")
    print(f"Pattern progress: {next_actions_result.pattern_progress:.1f}%")
    print(f"Remaining required actions: {next_actions_result.remaining_required_actions}")

    # Display the expected participants
    if next_actions_result.expected_participants:
        print(f"Expected participants: {', '.join(next_actions_result.expected_participants)}")

    # Display the possible actions
    print("\nPossible next actions:")
    for i, action in enumerate(next_actions_result.actions, 1):
        print(f"\n{i}. {action.action_type}: {action.description}")
        print(f"   Actor: {action.actor_id}")
        print(f"   Priority: {action.priority}")

        if action.required:
            print("   [Required for pattern progression]")

        if action.allowed_recipients:
            print(f"   Recipients: {', '.join(action.allowed_recipients)}")

        if action.content_requirements:
            print("   Content requirements:")
            for key, value in action.content_requirements.items():
                print(f"      - {key}: {value}")

        if action.alternatives:
            print(f"   Alternatives: {', '.join(action.alternatives)}")

    # If there are decision points in the pattern, show them
    if next_actions_result.decision_points:
        print("\nDecision points:")
        for point in next_actions_result.decision_points:
            print(f"- {point['description']} (Options: {', '.join(point['options'])})")

    # Show the path taken so far
    if next_actions_result.path_taken:
        print("\nPath taken so far:")
        for step in next_actions_result.path_taken:
            print(f"- Step {step['step_index']}: {step['action_type']} by {step['actor_id']}")
else:
    print("No further actions available in this pattern")

    if next_actions_result.pattern_progress >= 100.0:
        print("Pattern is complete!")
    else:
        print(f"Pattern is at {next_actions_result.pattern_progress:.1f}% completion but cannot proceed further")
        print("Possible reasons:")
        if "termination_reason" in next_actions_result.metadata:
            print(f"- {next_actions_result.metadata['termination_reason']}")
```

#### Events

```python
class PatternInitializationFailedEvent:
    """
    Event emitted when a pattern fails to initialize.
    """
    event_type: str = "pattern_initialization_failed"  # Type of the event
    pattern_name: str  # Name of the pattern that failed to initialize
    context_id: str  # ID of the context used for initialization
    timestamp: datetime  # When the failure occurred
    error_code: str  # Error code describing the failure
    error_message: str  # Detailed error message
    stack_trace: Optional[str] = None  # Stack trace if available
    initialization_parameters: Dict[str, Any]  # Parameters used for initialization
    fallback_attempted: bool = False  # Whether a fallback pattern was attempted
    fallback_pattern: Optional[str] = None  # Name of the fallback pattern if attempted
    fallback_success: Optional[bool] = None  # Whether the fallback was successful
    source_component: str  # Component that attempted the initialization
    affected_session_id: Optional[str] = None  # ID of the affected session if applicable
    affected_agents: List[str] = []  # Agents affected by this failure
    metadata: Dict[str, Any] = {}  # Additional metadata about the failure
    suggested_actions: Optional[List[str]] = None  # Suggested actions to resolve the issue
```

**Example Payload:**
```json
{
    "event_type": "pattern_initialization_failed",
    "pattern_name": "chain_of_thought",
    "context_id": "ctx_123abc",
    "timestamp": "2025-05-25T15:35:10Z",
    "error_code": "INVALID_CONTEXT",
    "error_message": "Missing required participant 'reasoning_agent' in context",
    "stack_trace": "at PatternFactory.createPattern (pattern_factory.py:156)\n at PatternEngine.getPatternImplementation (pattern_engine.py:78)",
    "initialization_parameters": {
        "pattern_name": "chain_of_thought",
        "context": {
            "initiator_id": "user_agent_123",
            "participants": ["assistant_agent_456"],
            "session_id": "session_abc123",
            "timeout_seconds": 120,
            "protocol_type": "a2a"
        },
        "options": {
            "variant": "branching",
            "validation_level": "strict"
        }
    },
    "fallback_attempted": true,
    "fallback_pattern": "request_response",
    "fallback_success": true,
    "source_component": "pattern_engine",
    "affected_session_id": "session_abc123",
    "affected_agents": ["user_agent_123", "assistant_agent_456"],
    "metadata": {
        "request_id": "req_456def",
        "client_info": "web_interface_v2.5",
        "error_category": "configuration_error"
    },
    "suggested_actions": [
        "Add 'reasoning_agent' to the participants list",
        "Check if 'reasoning_agent' is registered in the topology",
        "Continue with the fallback pattern"
    ]
}
```

```python
class PatternViolationDetectedEvent:
    """
    Event emitted when a pattern constraint is violated.
    """
    event_type: str = "pattern_violation_detected"  # Type of the event
    pattern_id: str  # ID of the pattern where the violation was detected
    violation_id: str  # Unique identifier for this violation
    timestamp: datetime  # When the violation was detected
    violation_type: str  # Type of violation (e.g., "sequence", "participant", "content")
    severity: str  # Severity of the violation ("error", "warning", "info")
    message_id: Optional[str] = None  # ID of the message that caused the violation
    step_index: Optional[int] = None  # Index of the step where the violation occurred
    expected: Any  # What was expected according to the pattern
    actual: Any  # What was actually found
    description: str  # Human-readable description of the violation
    context: Dict[str, Any] = {}  # Context information about the violation
    session_id: str  # ID of the session where the violation occurred
    affected_agents: List[str] = []  # Agents affected by this violation
    is_correctable: bool = False  # Whether the violation can be automatically corrected
    suggested_correction: Optional[Any] = None  # Suggested correction for the violation
    metadata: Dict[str, Any] = {}  # Additional metadata about the violation
    validation_rules_applied: List[str] = []  # Rules that were applied during validation
```

**Example Payload:**
```json
{
    "event_type": "pattern_violation_detected",
    "pattern_id": "chain_of_thought_xyz789",
    "violation_id": "vio_789ghi",
    "timestamp": "2025-05-25T15:40:22Z",
    "violation_type": "sequence",
    "severity": "error",
    "message_id": "msg_125",
    "step_index": 2,
    "expected": {
        "sender_id": "assistant_agent_456",
        "action": "solution_review"
    },
    "actual": {
        "sender_id": "reasoning_agent_789",
        "action": "detailed_solution"
    },
    "description": "Invalid message sequence: expected 'solution_review' from 'assistant_agent_456' but received 'detailed_solution' from 'reasoning_agent_789'",
    "context": {
        "previous_step": {
            "action": "solution_approach",
            "sender": "assistant_agent_456"
        },
        "pattern_state": "reasoning_phase"
    },
    "session_id": "session_abc123",
    "affected_agents": ["user_agent_123", "assistant_agent_456", "reasoning_agent_789"],
    "is_correctable": true,
    "suggested_correction": {
        "action": "insert_missing_step",
        "missing_step": {
            "action": "solution_review",
            "sender_id": "assistant_agent_456",
            "content_template": {
                "review_status": "approved",
                "comments": "The approach looks correct, please proceed with the detailed solution."
            }
        }
    },
    "metadata": {
        "validation_rule_id": "chain_sequence_rule_5",
        "validation_level": "strict",
        "pattern_variant": "branching",
        "detection_mechanism": "step_sequence_validator"
    },
    "validation_rules_applied": [
        "sender_sequence_validation",
        "action_sequence_validation",
        "required_steps_validation"
    ]
}
```

### Communication Pattern Engine → Agent Framework

#### Methods/Functions

```python
def register_pattern_handler(pattern_name: str, handler: PatternHandler,
                           registration_options: Optional[PatternHandlerRegistrationOptions] = None) -> RegistrationResult:
    """
    Register a handler for a specific communication pattern.

    Args:
        pattern_name: str - Name of the pattern to handle
        handler: PatternHandler - Handler implementation for the pattern
        registration_options: Optional[PatternHandlerRegistrationOptions] - Options for handler registration

    Returns:
        RegistrationResult - Result of the registration operation

    Raises:
        PatternAlreadyRegisteredError - If a handler is already registered for this pattern
        InvalidPatternHandlerError - If the provided handler doesn't implement required methods
        UnauthorizedRegistrationError - If the caller is not authorized to register handlers
    """
```

**Data Structures:**

```python
class PatternHandler:
    """
    Interface for pattern handlers that can process pattern-related events and actions.
    """
    def handle_state_change(self, pattern_id: str, old_state: PatternState,
                          new_state: PatternState, change_context: StateChangeContext) -> None:
        """
        Handle a state change in a pattern.
        """
        pass

    def handle_pattern_completion(self, pattern_id: str, final_state: PatternState,
                                result: PatternCompletionResult) -> None:
        """
        Handle the completion of a pattern.
        """
        pass

    def handle_pattern_error(self, pattern_id: str, error_info: PatternErrorInfo) -> None:
        """
        Handle an error in a pattern.
        """
        pass

    def get_supported_pattern_variants(self) -> List[str]:
        """
        Get the pattern variants supported by this handler.
        """
        pass

class PatternHandlerRegistrationOptions:
    """
    Options for registering a pattern handler.
    """
    priority: int = 0  # Priority of this handler (higher value = higher priority)
    supported_variants: List[str] = []  # Pattern variants supported by this handler
    overwrite_existing: bool = False  # Whether to overwrite an existing handler
    metadata: Dict[str, Any] = {}  # Additional metadata about this handler
    security_context: Optional[Dict[str, Any]] = None  # Security context for the registration
    timeout_seconds: int = 30  # Timeout for handler operations in seconds
    supported_protocols: List[str] = []  # Protocols supported by this handler
    feature_flags: Dict[str, bool] = {}  # Feature flags for this handler

class RegistrationResult:
    """
    Result of a pattern handler registration operation.
    """
    success: bool  # Whether the registration was successful
    handler_id: str  # ID assigned to the registered handler
    pattern_name: str  # Name of the pattern the handler was registered for
    supported_variants: List[str]  # Pattern variants supported by the handler
    registration_timestamp: datetime  # When the handler was registered
    is_overwrite: bool = False  # Whether an existing handler was overwritten
    previous_handler_id: Optional[str] = None  # ID of the previous handler if overwritten
    metadata: Dict[str, Any] = {}  # Additional metadata about the registration
```

**Example Usage:**
```python
# Create a custom pattern handler for sequential thinking patterns
class SequentialThinkingHandler(PatternHandler):
    def handle_state_change(self, pattern_id: str, old_state: PatternState,
                          new_state: PatternState, change_context: StateChangeContext) -> None:
        # Process state changes for sequential thinking patterns
        logger.info(f"Sequential thinking pattern {pattern_id} state changed: "
                    f"{old_state.state_name} -> {new_state.state_name}")

        # Track pattern progression metrics
        if new_state.state_name == "reasoning_phase":
            metrics_service.track_reasoning_phase_start(pattern_id, new_state.active_participants)
        elif new_state.state_name == "response_formulation":
            metrics_service.track_response_formulation_start(pattern_id, new_state.active_participants)

    def handle_pattern_completion(self, pattern_id: str, final_state: PatternState,
                                result: PatternCompletionResult) -> None:
        # Handle successful completion of sequential thinking patterns
        logger.info(f"Sequential thinking pattern {pattern_id} completed successfully")

        # Record completion metrics
        metrics_service.record_pattern_completion(
            pattern_id=pattern_id,
            total_steps=final_state.current_step,
            completion_time_ms=result.total_execution_time_ms,
            participants=final_state.active_participants
        )

        # Notify interested components
        event_bus.publish("pattern.completed", {
            "pattern_id": pattern_id,
            "pattern_type": "sequential_thinking",
            "final_state": final_state,
            "result": result
        })

    def handle_pattern_error(self, pattern_id: str, error_info: PatternErrorInfo) -> None:
        # Handle errors in sequential thinking patterns
        logger.error(f"Error in sequential thinking pattern {pattern_id}: {error_info.error_message}")

        # Implement error recovery if possible
        if error_info.is_recoverable:
            recovery_service.attempt_pattern_recovery(
                pattern_id=pattern_id,
                error_type=error_info.error_type,
                recovery_strategy="retry_step"
            )
        else:
            # Notify about unrecoverable error
            alert_service.send_alert(f"Unrecoverable error in pattern {pattern_id}: {error_info.error_message}")

    def get_supported_pattern_variants(self) -> List[str]:
        # Return the variants of sequential thinking pattern supported by this handler
        return ["basic", "recursive", "branching"]

# Register the handler with appropriate options
registration_result = agent_framework.register_pattern_handler(
    pattern_name="sequential_thinking",
    handler=SequentialThinkingHandler(),
    registration_options=PatternHandlerRegistrationOptions(
        priority=10,  # High priority handler
        supported_variants=["basic", "recursive", "branching"],
        overwrite_existing=True,  # Replace any existing handler
        metadata={
            "creator": "reasoning_system",
            "version": "1.2.3",
            "description": "Handles sequential thinking patterns with improved reasoning metrics"
        },
        supported_protocols=["a2a", "mcp"],  # Supports both Google A2A and MCP protocols
        feature_flags={
            "enable_adaptive_reasoning": True,
            "collect_detailed_metrics": True,
            "use_fallback_strategies": True
        }
    )
)

if registration_result.success:
    logger.info(f"Successfully registered sequential thinking handler with ID: {registration_result.handler_id}")

    # If this replaced an existing handler, log that information
    if registration_result.is_overwrite:
        logger.info(f"Replaced previous handler with ID: {registration_result.previous_handler_id}")

    # Print registration metadata
    print(f"Handler registered at: {registration_result.registration_timestamp}")
    print(f"Supported variants: {', '.join(registration_result.supported_variants)}")
else:
    logger.error(f"Failed to register sequential thinking handler")
```

- `agent_framework.notify_pattern_state_change(pattern_id: str, new_state: PatternState,
                             change_context: Optional[StateChangeContext] = None,
                             notification_options: Optional[NotificationOptions] = None) → NotificationResult`
  - **Purpose**: Notify the Agent Framework of pattern state changes
  - **Parameters**:
    - `pattern_id`: Pattern identifier
    - `new_state`: Updated pattern state
    - `change_context`: Context of the state change
    - `notification_options`: Options for notification
  - **Returns**: Notification result
  - **Example**:
    ```python
    agent_framework.notify_pattern_state_change(
        pattern_id="chain_of_thought_123",
        new_state=PatternState.COMPLETED,
        change_context=StateChangeContext(
            change_id="change_123abc",
            change_type="normal",
            change_reason="user_message_received",
            change_timestamp=datetime.now(),
            triggering_action={
                "action_type": "message",
                "message_id": "msg_456def",
                "sender_id": "user_agent_123"
            },
            triggering_agent_id="user_agent_123",
            related_message_ids=["msg_456def"],
            session_id="session_abc123",
            is_expected=True,
            metrics={
                "state_computation_time_ms": 15,
                "state_size_bytes": 2048
            },
            metadata={
                "client_version": "2.5.0",
                "platform": "web",
                "pattern_variant": "branching"
            }
        ),
        notification_options=NotificationOptions(
            priority="high",  # High priority notification
            delivery_mode="sync",  # Deliver synchronously
            notify_participants=True,
            include_state_diff=True,  # Include a diff of the changes
            include_full_state=True,
            retry_on_failure=True,
            max_retries=5,  # Retry up to 5 times
            metadata={
                "originator": "pattern_engine",
                "pattern_type": "chain_of_thought",
                "significant_change": True
            }
        )
    )
    ```

**Data Structures:**

```python
class NotificationOptions:
    """
    Options for pattern state change notifications.
    """
    priority: str = "normal"  # Priority of the notification ("low", "normal", "high", "critical")
    delivery_mode: str = "async"  # Delivery mode ("sync", "async", "batch")
    notify_participants: bool = True  # Whether to notify pattern participants
    include_state_diff: bool = False  # Whether to include a diff of state changes
    include_full_state: bool = True  # Whether to include the full pattern state
    retry_on_failure: bool = True  # Whether to retry on notification failure
    max_retries: int = 3  # Maximum number of retries on failure
    notification_target: Optional[str] = None  # Specific target for the notification
    metadata: Dict[str, Any] = {}  # Additional metadata for the notification

class NotificationResult:
    """
    Result of a pattern state change notification operation.
    """
    notification_id: str  # Unique identifier for this notification
    pattern_id: str  # ID of the pattern this notification is for
    timestamp: datetime  # When the notification was processed
    status: str  # Status of the notification ("delivered", "pending", "failed")
    delivery_time_ms: int  # Time taken to deliver the notification in milliseconds
    target_components: List[str]  # Components that received the notification
    delivery_attempts: int = 1  # Number of delivery attempts made
    error_message: Optional[str] = None  # Error message if delivery failed
    metadata: Dict[str, Any] = {}  # Additional metadata about the notification
```

**Example Usage:**
```python
# Prepare a state change context
change_context = StateChangeContext(
    change_id="change_123abc",
    change_type="normal",
    change_reason="user_message_received",
    change_timestamp=datetime.now(),
    triggering_action={
        "action_type": "message",
        "message_id": "msg_456def",
        "sender_id": "user_agent_123"
    },
    triggering_agent_id="user_agent_123",
    related_message_ids=["msg_456def"],
    session_id="session_abc123",
    is_expected=True,
    metrics={
        "state_computation_time_ms": 15,
        "state_size_bytes": 2048
    },
    metadata={
        "client_version": "2.5.0",
        "platform": "web",
        "pattern_variant": "branching"
    }
)

# Set notification options
notification_options = NotificationOptions(
    priority="high",  # High priority notification
    delivery_mode="sync",  # Deliver synchronously
    notify_participants=True,
    include_state_diff=True,  # Include a diff of the changes
    include_full_state=True,
    retry_on_failure=True,
    max_retries=5,  # Retry up to 5 times
    metadata={
        "originator": "pattern_engine",
        "pattern_type": "chain_of_thought",
        "significant_change": True
    }
)

# Notify the Agent Framework of the pattern state change
notification_result = agent_framework.notify_pattern_state_change(
    pattern_id="chain_of_thought_xyz789",
    new_state=updated_pattern_state,  # This would be a PatternState object with the updated state
    change_context=change_context,
    notification_options=notification_options
)

# Check the notification result
if notification_result.status == "delivered":
    logger.info(
        f"Successfully notified {len(notification_result.target_components)} components "
        f"about pattern state change in {notification_result.delivery_time_ms}ms"
    )

    # Log the notification details
    logger.debug(f"Notification ID: {notification_result.notification_id}")
    logger.debug(f"Notification timestamp: {notification_result.timestamp}")
    logger.debug(f"Target components: {', '.join(notification_result.target_components)}")
else:
    # Handle notification failure
    logger.error(
        f"Failed to notify components about pattern state change: "
        f"{notification_result.error_message} (Attempts: {notification_result.delivery_attempts})"
    )

    # Take remedial action
    if notification_result.delivery_attempts < notification_options.max_retries:
        logger.info("Will retry notification automatically")
    else:
        # Log the failure as a critical issue
        alert_service.send_alert(
            alert_type="notification_failure",
            alert_level="critical",
            message=f"Failed to notify components about pattern state change after "
                    f"{notification_result.delivery_attempts} attempts",
            context={
                "pattern_id": notification_result.pattern_id,
                "notification_id": notification_result.notification_id,
                "error_message": notification_result.error_message
            }
        )
```

#### Events

```python
class PatternCompletedEvent:
    """
    Event emitted when a communication pattern completes.
    """
    event_type: str = "pattern_completed"  # Type of the event
    pattern_id: str  # ID of the pattern that completed
    pattern_name: str  # Name of the pattern
    pattern_variant: str  # Variant of the pattern that was used
    timestamp: datetime  # When the pattern completed
    session_id: str  # ID of the session this pattern was part of
    completion_type: str  # How the pattern completed ("normal", "timeout", "error", "interrupted")
    total_duration_ms: int  # Total duration of the pattern execution in milliseconds
    total_steps: int  # Total number of steps executed in the pattern
    participants: List[str]  # IDs of the participants in the pattern
    initiator_id: str  # ID of the agent that initiated the pattern
    final_state: PatternState  # Final state of the pattern
    validation_status: str  # Validation status of the pattern completion ("valid", "warning", "error")
    content_summary: Optional[Dict[str, Any]] = None  # Summary of content produced during the pattern
    metrics: Dict[str, Any] = {}  # Metrics about the pattern execution
    security_context: Optional[Dict[str, Any]] = None  # Security context for the pattern
    metadata: Dict[str, Any] = {}  # Additional metadata about the pattern completion
```

**Example Payload:**
```json
{
    "event_type": "pattern_completed",
    "pattern_id": "chain_of_thought_xyz789",
    "pattern_name": "chain_of_thought",
    "pattern_variant": "branching",
    "timestamp": "2025-05-25T16:15:30Z",
    "session_id": "session_abc123",
    "completion_type": "normal",
    "total_duration_ms": 3500,
    "total_steps": 8,
    "participants": ["user_agent_123", "assistant_agent_456", "reasoning_agent_789"],
    "initiator_id": "user_agent_123",
    "final_state": {
        "state_id": "state_xyz789_final",
        "pattern_id": "chain_of_thought_xyz789",
        "state_name": "completed",
        "is_terminal": true,
        "current_step": 8,
        "total_steps": 8,
        "active_participants": ["assistant_agent_456"],
        "pending_actions": [],
        "completed_actions": [
            {
                "action_id": "act_001",
                "action_type": "user_query",
                "actor_id": "user_agent_123",
                "timestamp": "2025-05-25T16:12:10Z"
            },
            {
                "action_id": "act_002",
                "action_type": "initial_response",
                "actor_id": "assistant_agent_456",
                "timestamp": "2025-05-25T16:12:45Z"
            },
            {
                "action_id": "act_003",
                "action_type": "reasoning_step",
                "actor_id": "reasoning_agent_789",
                "timestamp": "2025-05-25T16:13:20Z"
            },
            {
                "action_id": "act_004",
                "action_type": "solution_approach",
                "actor_id": "assistant_agent_456",
                "timestamp": "2025-05-25T16:14:00Z"
            },
            {
                "action_id": "act_005",
                "action_type": "solution_review",
                "actor_id": "reasoning_agent_789",
                "timestamp": "2025-05-25T16:14:30Z"
            },
            {
                "action_id": "act_006",
                "action_type": "detailed_solution",
                "actor_id": "assistant_agent_456",
                "timestamp": "2025-05-25T16:15:00Z"
            },
            {
                "action_id": "act_007",
                "action_type": "final_verification",
                "actor_id": "reasoning_agent_789",
                "timestamp": "2025-05-25T16:15:15Z"
            },
            {
                "action_id": "act_008",
                "action_type": "final_response",
                "actor_id": "assistant_agent_456",
                "timestamp": "2025-05-25T16:15:30Z"
            }
        ],
        "last_update_timestamp": "2025-05-25T16:15:30Z",
        "validation_status": "valid",
        "active_branch": null,
        "extension_data": {},
        "metadata": {
            "completion_reason": "final_step_completed"
        }
    },
    "validation_status": "valid",
    "content_summary": {
        "initial_query": "How do I implement a binary search tree in Python?",
        "final_response": "Here's a complete implementation of a binary search tree in Python...",
        "key_reasoning_steps": ["Identified core BST operations", "Discussed implementation approaches", "Verified edge cases"]
    },
    "metrics": {
        "thinking_time_ms": 2200,
        "response_time_ms": 1300,
        "token_count": 3450,
        "reasoning_cycles": 2,
        "user_satisfaction_score": 0.95
    },
    "metadata": {
        "client_id": "web_client_v2.5",
        "user_context": "programming_task",
        "complexity_level": "intermediate",
        "pattern_execution_id": "exec_123def"
    }
}
```

```python
class PatternTransitionEvent:
    """
    Event emitted when a pattern transitions from one state to another.
    """
    event_type: str = "pattern_transition"  # Type of the event
    pattern_id: str  # ID of the pattern that transitioned
    transition_id: str  # Unique identifier for this transition
    timestamp: datetime  # When the transition occurred
    from_state: str  # Name of the previous state
    to_state: str  # Name of the new state
    transition_type: str  # Type of transition ("normal", "timeout", "error", "manual")
    transition_reason: str  # Reason for the transition
    session_id: str  # ID of the session this pattern is part of
    pattern_name: str  # Name of the pattern
    pattern_variant: str  # Variant of the pattern
    triggering_action: Optional[Dict[str, Any]] = None  # Action that triggered the transition
    triggering_agent_id: Optional[str] = None  # ID of the agent that triggered the transition
    active_participants: List[str] = []  # IDs of currently active participants
    next_expected_actions: List[Dict[str, Any]] = []  # Actions expected after this transition
    transition_duration_ms: int  # Time taken to complete the transition in milliseconds
    is_expected: bool = True  # Whether this transition was expected according to the pattern
    metrics: Dict[str, Any] = {}  # Metrics about the transition
    metadata: Dict[str, Any] = {}  # Additional metadata about the transition
```

**Example Payload:**
```json
{
    "event_type": "pattern_transition",
    "pattern_id": "chain_of_thought_xyz789",
    "transition_id": "trans_456ghi",
    "timestamp": "2025-05-25T16:14:00Z",
    "from_state": "reasoning_phase",
    "to_state": "solution_phase",
    "transition_type": "normal",
    "transition_reason": "reasoning_completed",
    "session_id": "session_abc123",
    "pattern_name": "chain_of_thought",
    "pattern_variant": "branching",
    "triggering_action": {
        "action_id": "act_004",
        "action_type": "solution_approach",
        "actor_id": "assistant_agent_456",
        "timestamp": "2025-05-25T16:14:00Z",
        "content_summary": "Proposed solution approach for implementing a binary search tree"
    },
    "triggering_agent_id": "assistant_agent_456",
    "active_participants": ["user_agent_123", "assistant_agent_456", "reasoning_agent_789"],
    "next_expected_actions": [
        {
            "action_type": "solution_review",
            "actor_id": "reasoning_agent_789",
            "description": "Review the proposed solution approach"
        }
    ],
    "transition_duration_ms": 120,
    "is_expected": true,
    "metrics": {
        "state_computation_time_ms": 35,
        "validation_time_ms": 25,
        "notification_time_ms": 60
    },
    "metadata": {
        "transition_sequence": 4,
        "pattern_progress": 0.5,
        "decision_path": "primary",
        "remaining_steps": 4
    }
}
```

## Data Flows

### Pattern Initialization Flow
1. **Agent Framework → Communication Pattern Engine**: Agent Framework requests a pattern implementation
2. **Communication Pattern Engine Processing**: Engine instantiates the pattern with appropriate context
3. **Communication Pattern Engine → Agent Framework**: Engine returns the initialized pattern
4. **Agent Framework Processing**: Agent Framework uses the pattern to structure communication

### Pattern Execution Flow
1. **Agent Framework → Communication Pattern Engine**: Agent Framework requests next valid actions
2. **Communication Pattern Engine Processing**: Engine analyzes current state and determines valid next actions
3. **Communication Pattern Engine → Agent Framework**: Engine returns possible actions
4. **Agent Framework → Protocol Layer**: Agent Framework executes actions through the Protocol Layer
5. **Agent Framework → Communication Pattern Engine**: Agent Framework updates pattern state based on responses

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
communication_patterns:
  enabled_patterns:
    - name: "request_response"
      implementation_class: "RequestResponsePattern"
      timeout_seconds: 30

    - name: "sequential_thinking"
      implementation_class: "SequentialThinkingPattern"
      config:
        max_steps: 10
        history_validation: true

    - name: "chain_of_thought"
      implementation_class: "ChainOfThoughtPattern"
      config:
        max_chain_length: 5
        allow_branching: true

  pattern_validation:
    enabled: true
    validation_level: "strict"  # strict, lenient, none
    auto_correction: false

  custom_patterns_path: "patterns/"

agent_framework:
  pattern_integration:
    default_pattern: "request_response"
    pattern_selection_strategy: "capability_based"
    pattern_timeout_seconds: 120
```

## Error Handling

1. **Pattern Initialization Failures**:
   - Fallback to simpler patterns if complex pattern initialization fails
   - Detailed error logging with initialization parameters
   - Error notification to the agent requesting the pattern

2. **Pattern Constraint Violations**:
   - Based on validation_level, may reject, warn, or ignore violations
   - Automatic correction of minor violations if enabled
   - Escalation of critical violations to human supervisor if configured

3. **Pattern Timeouts**:
   - Configurable timeout handling (abort, extend, simplify)
   - Notification to participants about timeout situation
   - Graceful termination of incomplete pattern sequences

## Extension Points

### 1. Custom Communication Patterns

```python
class CommunicationPattern:
    """
    Interface for implementing custom communication patterns.
    All pattern implementations must implement this interface.
    """
    def initialize(self, context: PatternContext) -> str:
        """
        Initialize the pattern with context information and return a unique pattern instance ID.

        Args:
            context: PatternContext - Context information for pattern initialization

        Returns:
            str - Unique identifier for this pattern instance

        Raises:
            InvalidPatternContextError - If the provided context is invalid for this pattern
            PatternInitializationError - If the pattern could not be initialized
        """
        pass

    def validate_message(self, pattern_id: str, message: Message,
                        validation_options: Optional[ValidationOptions] = None) -> MessageValidationResult:
        """
        Validate if a message conforms to the pattern constraints.

        Args:
            pattern_id: str - ID of the pattern instance
            message: Message - Message to validate
            validation_options: Optional[ValidationOptions] - Options for validation

        Returns:
            MessageValidationResult - Result of the message validation

        Raises:
            PatternNotFoundError - If the pattern with the given ID is not found
            ValidationError - If validation fails critically
        """
        pass

    def get_next_valid_actions(self, pattern_id: str, current_state: PatternState,
                              action_options: Optional[ActionOptions] = None) -> NextActionsResult:
        """
        Get actions that are valid in the current pattern state.

        Args:
            pattern_id: str - ID of the pattern instance
            current_state: PatternState - Current state of the pattern
            action_options: Optional[ActionOptions] - Options for action retrieval

        Returns:
            NextActionsResult - Result containing valid next actions

        Raises:
            PatternNotFoundError - If the pattern with the given ID is not found
            InvalidPatternStateError - If the provided pattern state is invalid
        """
        pass

    def update_state(self, pattern_id: str, message: Message,
                    update_options: Optional[StateUpdateOptions] = None) -> PatternState:
        """
        Update pattern state based on a new message or action.

        Args:
            pattern_id: str - ID of the pattern instance
            message: Message - Message that triggers the state update
            update_options: Optional[StateUpdateOptions] - Options for state update

        Returns:
            PatternState - Updated pattern state

        Raises:
            PatternNotFoundError - If the pattern with the given ID is not found
            InvalidMessageError - If the message is invalid for the current pattern state
            StateUpdateError - If the state update fails
        """
        pass

    def get_supported_protocols(self) -> List[str]:
        """
        Get the list of protocols supported by this pattern implementation.

        Returns:
            List[str] - List of supported protocol identifiers (e.g., ["a2a", "mcp"])
        """
        pass

    def get_metadata(self) -> PatternMetadata:
        """
        Get metadata about this pattern implementation.

        Returns:
            PatternMetadata - Metadata about the pattern
        """
        pass
```

**Data Structures:**

```python
class PatternContext:
    """
    Context information for pattern initialization.
    """
    pattern_name: str  # Name of the pattern to initialize
    session_id: str  # ID of the session this pattern is part of
    initiator_id: str  # ID of the agent initiating the pattern
    participants: List[str]  # IDs of the participants in the pattern
    initial_message: Optional[Message] = None  # Initial message that triggered the pattern
    timeout_seconds: int = 120  # Timeout for the pattern in seconds
    protocol_type: str  # Type of protocol being used ("a2a", "mcp", etc.)
    pattern_variant: Optional[str] = None  # Variant of the pattern to use
    security_context: Optional[Dict[str, Any]] = None  # Security context for the pattern
    custom_config: Dict[str, Any] = {}  # Custom configuration for the pattern
    metadata: Dict[str, Any] = {}  # Additional metadata for the pattern

class StateUpdateOptions:
    """
    Options for pattern state updates.
    """
    validate_message: bool = True  # Whether to validate the message before updating state
    auto_correct: bool = False  # Whether to automatically correct minor validation issues
    update_timestamp: bool = True  # Whether to update the state timestamp
    notify_participants: bool = True  # Whether to notify participants of the state update
    compute_next_actions: bool = True  # Whether to compute next possible actions
    include_message_content: bool = True  # Whether to include full message content in the state
    metadata: Dict[str, Any] = {}  # Additional metadata for the state update

class PatternMetadata:
    """
    Metadata about a communication pattern implementation.
    """
    pattern_name: str  # Name of the pattern
    description: str  # Human-readable description of the pattern
    version: str  # Version of the pattern implementation
    author: str  # Author of the pattern implementation
    supported_protocols: List[str]  # Protocols supported by this pattern
    supported_variants: List[str]  # Variants of this pattern that are supported
    recommended_timeout_seconds: int  # Recommended timeout for this pattern
    average_steps: int  # Average number of steps in this pattern
    complexity_level: str  # Complexity level of the pattern ("simple", "medium", "complex")
    tags: List[str] = []  # Tags for categorizing this pattern
    documentation_url: Optional[str] = None  # URL to documentation for this pattern
    compatible_reasoning_engines: List[str] = []  # Reasoning engines compatible with this pattern
    metadata: Dict[str, Any] = {}  # Additional metadata about the pattern
```

**Example Implementation:**

```python
class SequentialThinkingPattern(CommunicationPattern):
    """
    Implementation of the Sequential Thinking pattern for structured reasoning.

    This pattern enables sequential, step-by-step reasoning with validation at each step,
    supporting both A2A and MCP protocols.
    """
    def initialize(self, context: PatternContext) -> str:
        # Validate the context
        if "reasoning_agent" not in context.participants:
            if context.protocol_type == "a2a":
                # For A2A, we require a dedicated reasoning agent
                raise InvalidPatternContextError("Sequential Thinking pattern requires a reasoning agent")

        # Initialize pattern instance
        pattern_id = f"seq_thinking_{uuid.uuid4().hex[:8]}"

        # Create initial state
        initial_state = PatternState(
            state_id=f"{pattern_id}_initial",
            pattern_id=pattern_id,
            state_name="initial",
            is_terminal=False,
            current_step=0,
            total_steps=context.custom_config.get("max_steps", 10),
            active_participants=[context.initiator_id],
            pending_actions=[{
                "action_type": "initial_query",
                "actor_id": context.initiator_id,
                "description": "Initial query to start the sequential thinking process"
            }],
            completed_actions=[],
            last_update_timestamp=datetime.now(),
            validation_status="valid",
            expected_next_actions=["initial_query"],
            metadata={
                "pattern_variant": context.pattern_variant or "standard",
                "protocol_type": context.protocol_type,
                "session_id": context.session_id
            }
        )

        # Store the state
        self.states[pattern_id] = initial_state
        self.contexts[pattern_id] = context

        # Log the initialization
        logger.info(f"Initialized Sequential Thinking pattern with ID: {pattern_id}")
        logger.debug(f"Pattern context: {context}")

        return pattern_id

    def validate_message(self, pattern_id: str, message: Message,
                        validation_options: Optional[ValidationOptions] = None) -> MessageValidationResult:
        # Implement message validation logic
        # ...

    def get_next_valid_actions(self, pattern_id: str, current_state: PatternState,
                              action_options: Optional[ActionOptions] = None) -> NextActionsResult:
        # Implement next actions logic
        # ...

    def update_state(self, pattern_id: str, message: Message,
                    update_options: Optional[StateUpdateOptions] = None) -> PatternState:
        # Implement state update logic
        # ...

    def get_supported_protocols(self) -> List[str]:
        # This pattern supports both A2A and MCP
        return ["a2a", "mcp"]

    def get_metadata(self) -> PatternMetadata:
        return PatternMetadata(
            pattern_name="sequential_thinking",
            description="A pattern for sequential, step-by-step reasoning with validation at each step",
            version="1.2.0",
            author="OpenMAS Team",
            supported_protocols=["a2a", "mcp"],
            supported_variants=["standard", "recursive", "branching"],
            recommended_timeout_seconds=300,
            average_steps=5,
            complexity_level="medium",
            tags=["reasoning", "thinking", "structured", "step-by-step"],
            documentation_url="https://docs.openmas.org/patterns/sequential_thinking",
            compatible_reasoning_engines=["llm", "symbolic", "hybrid"],
            metadata={
                "created_date": "2025-03-15",
                "last_updated": "2025-05-20",
                "typical_use_cases": ["Problem solving", "Decision making", "Content generation"]
            }
        )
```

### 2. Pattern Visualizers

```python
class PatternVisualizer:
    """
    Interface for implementing custom pattern visualizers.
    """
    def initialize(self, pattern_id: str, pattern_metadata: PatternMetadata) -> str:
        """
        Initialize the visualizer for a specific pattern.

        Args:
            pattern_id: str - ID of the pattern to visualize
            pattern_metadata: PatternMetadata - Metadata about the pattern

        Returns:
            str - Unique identifier for this visualizer instance
        """
        pass

    def update_visualization(self, pattern_id: str, current_state: PatternState) -> VisualizationResult:
        """
        Update the visualization based on the current pattern state.

        Args:
            pattern_id: str - ID of the pattern
            current_state: PatternState - Current state of the pattern

        Returns:
            VisualizationResult - Result of the visualization update
        """
        pass

    def get_visualization_url(self, visualizer_id: str) -> str:
        """
        Get the URL where the visualization can be accessed.

        Args:
            visualizer_id: str - ID of the visualizer instance

        Returns:
            str - URL to access the visualization
        """
        pass

    def get_supported_formats(self) -> List[str]:
        """
        Get the visualization formats supported by this visualizer.

        Returns:
            List[str] - List of supported formats (e.g., ["web", "svg", "png"])
        """
        pass
```

**Example Implementation:**

```python
class GraphPatternVisualizer(PatternVisualizer):
    """
    Visualization of patterns as interactive graphs showing state transitions and message flow.
    """
    def initialize(self, pattern_id: str, pattern_metadata: PatternMetadata) -> str:
        visualizer_id = f"viz_{pattern_id}"

        # Create a new visualization
        self.visualizations[visualizer_id] = {
            "pattern_id": pattern_id,
            "pattern_name": pattern_metadata.pattern_name,
            "pattern_description": pattern_metadata.description,
            "states": [],
            "transitions": [],
            "participants": [],
            "messages": [],
            "created_at": datetime.now(),
            "last_updated": datetime.now()
        }

        # Initialize the graph
        self._initialize_graph(visualizer_id)

        return visualizer_id

    def update_visualization(self, pattern_id: str, current_state: PatternState) -> VisualizationResult:
        visualizer_id = f"viz_{pattern_id}"

        # Update the visualization with the new state
        self._update_graph(visualizer_id, current_state)

        # Generate a snapshot of the current visualization
        snapshot_url = self._generate_snapshot(visualizer_id)

        return VisualizationResult(
            visualizer_id=visualizer_id,
            pattern_id=pattern_id,
            update_timestamp=datetime.now(),
            snapshot_url=snapshot_url,
            live_url=f"{self.base_url}/visualize/{visualizer_id}",
            state_count=len(self.visualizations[visualizer_id]["states"]),
            transition_count=len(self.visualizations[visualizer_id]["transitions"]),
            current_state_name=current_state.state_name,
            visualization_format="web",
            metadata={
                "graph_complexity": "medium",
                "rendering_time_ms": 125
            }
        )

    def get_visualization_url(self, visualizer_id: str) -> str:
        return f"{self.base_url}/visualize/{visualizer_id}"

    def get_supported_formats(self) -> List[str]:
        return ["web", "svg", "png", "json"]

    # Private helper methods
    def _initialize_graph(self, visualizer_id: str) -> None:
        # Initialize the graph structure
        # ...

    def _update_graph(self, visualizer_id: str, current_state: PatternState) -> None:
        # Update the graph with the new state
        # ...

    def _generate_snapshot(self, visualizer_id: str) -> str:
        # Generate a snapshot of the current visualization
        # ...
        return f"{self.base_url}/snapshots/{visualizer_id}/{int(time.time())}.png"
```

## Notes on Multi-Protocol Design

The Agent Framework ↔ Communication Pattern Engine interface supports OpenMAS's multi-protocol design by:

- Providing protocol-agnostic communication patterns that can be applied across different protocols
- Supporting protocol-specific pattern implementations when needed
- Enabling pattern translation between protocols
- Ensuring consistent pattern semantics regardless of underlying protocol

## Notes on A2A and MCP Protocol Support

This interface explicitly supports both Google's A2A protocol and the Model Context Protocol (MCP):

- Communication patterns from the A2A specification (like sequential thinking and chain of thought) are fully supported
- MCP-specific patterns are implemented with the same pattern interface
- Both protocol patterns can be used interchangeably through the unified pattern interface
- Pattern selection can be based on available protocol capabilities

## Example: Sequential Thinking Pattern Implementation

```python
class SequentialThinkingPattern(CommunicationPattern):
    def initialize(self, context: PatternContext) → str:
        # Initialize sequential thinking pattern
        pattern_id = generate_id()
        self.state = {
            "id": pattern_id,
            "thought_number": 0,
            "total_thoughts": context.get("initial_thoughts", 5),
            "thoughts": [],
            "status": "initialized"
        }
        return pattern_id

    def validate_message(self, message: Message) → bool:
        # Validate if message conforms to sequential thinking format
        if message.type != "sequential_thinking_step":
            return False

        required_fields = ["thought", "thoughtNumber", "totalThoughts"]
        return all(field in message.content for field in required_fields)

    def get_next_valid_actions(self, current_state: PatternState) → List[PatternAction]:
        # Get valid next actions for sequential thinking
        actions = []

        if current_state.status == "initialized" or current_state.status == "in_progress":
            if current_state.thought_number < current_state.total_thoughts:
                actions.append(PatternAction(
                    type="next_thought",
                    parameters={
                        "thought_number": current_state.thought_number + 1,
                        "total_thoughts": current_state.total_thoughts
                    }
                ))

            # Allow for revisions of previous thoughts
            if current_state.thought_number > 0:
                actions.append(PatternAction(
                    type="revise_thought",
                    parameters={
                        "thought_number": current_state.thought_number,
                        "revises_thought": list(range(1, current_state.thought_number))
                    }
                ))

            # Allow for adjustment of total thoughts
            actions.append(PatternAction(
                type="adjust_total_thoughts",
                parameters={
                    "new_total": range(current_state.thought_number + 1, current_state.thought_number + 10)
                }
            ))

        return actions

    def update_state(self, message: Message) → PatternState:
        # Update state based on new sequential thinking message
        if message.type == "sequential_thinking_step":
            self.state["thought_number"] = message.content["thoughtNumber"]
            self.state["total_thoughts"] = message.content["totalThoughts"]
            self.state["thoughts"].append(message.content["thought"])

            if not message.content.get("nextThoughtNeeded", True):
                self.state["status"] = "completed"
            else:
                self.state["status"] = "in_progress"

        return PatternState(**self.state)
```
