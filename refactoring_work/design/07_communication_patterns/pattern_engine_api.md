# Communication Pattern Engine API

## Overview

The Communication Pattern Engine API provides the core interfaces for managing and executing communication patterns in OpenMAS. This API enables standardized agent interaction patterns across all protocols while maintaining SIMF compatibility and reasoning agnosticism.

The Pattern Engine serves as the central coordination point for:
- Pattern registration and discovery
- Pattern execution and lifecycle management
- Protocol adaptation and SIMF integration
- Pattern configuration validation and error handling

## Architecture Integration

The Pattern Engine integrates with OpenMAS architecture at this position:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OpenMAS Architecture                         │
├─────────────────┬─────────────────────┬─────────────────────────────┤
│ Agent Framework │ Pattern Engine      │ Protocol Layer              │
│                 │                     │                             │
│ ┌─────────────┐ │ ┌─────────────────┐ │ ┌─────────────────────────┐ │
│ │IMessageHand-│◄┼─┤IPatternEngine   │◄┼─┤IProtocolAdapter         │ │
│ │ler          │ │ │                 │ │ │                         │ │
│ └─────────────┘ │ └─────────────────┘ │ └─────────────────────────┘ │
│                 │                     │                             │
│ Uses patterns   │ Manages patterns    │ Adapts patterns to          │
│ for agent       │ and orchestrates    │ protocol-specific           │
│ communication   │ execution           │ implementations             │
└─────────────────┴─────────────────────┴─────────────────────────────┘
```

## Core Interfaces

### 1. IPatternEngine

The primary interface for pattern management and execution:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel
from datetime import datetime

class IPatternEngine(ABC):
    """
    Core interface for the Communication Pattern Engine.

    Provides pattern registration, discovery, validation, and execution
    capabilities while maintaining protocol independence and SIMF compatibility.
    """

    @abstractmethod
    async def register_pattern(self, pattern: 'PatternDefinition') -> None:
        """
        Register a new communication pattern with the engine.

        Args:
            pattern: Complete pattern definition including metadata and implementation

        Raises:
            PatternError: If pattern registration fails
            PatternConfigError: If pattern definition is invalid
        """
        pass

    @abstractmethod
    async def unregister_pattern(self, pattern_name: str) -> None:
        """
        Unregister a communication pattern from the engine.

        Args:
            pattern_name: Name of the pattern to unregister

        Raises:
            PatternNotFoundError: If pattern does not exist
            PatternError: If pattern has active instances
        """
        pass

    @abstractmethod
    async def execute_pattern(
        self,
        pattern_name: str,
        config: 'PatternConfig',
        message: 'InternalMessageFormat'
    ) -> 'PatternResult':
        """
        Execute a communication pattern for a single message.

        For stateless patterns like request-response, this handles the complete
        pattern execution. For stateful patterns, this creates a pattern instance.

        Args:
            pattern_name: Name of the pattern to execute
            config: Pattern-specific configuration
            message: SIMF message to process with the pattern

        Returns:
            PatternResult containing execution outcome and any response messages

        Raises:
            PatternNotFoundError: If pattern does not exist
            PatternConfigError: If configuration is invalid
            PatternExecutionError: If pattern execution fails
        """
        pass

    @abstractmethod
    async def create_pattern_instance(
        self,
        pattern_name: str,
        config: 'PatternConfig'
    ) -> 'IPatternInstance':
        """
        Create a stateful pattern instance for long-running patterns.

        Used for patterns like streaming, delegation, or collaborative workflow
        that maintain state across multiple messages.

        Args:
            pattern_name: Name of the pattern to instantiate
            config: Pattern-specific configuration

        Returns:
            IPatternInstance for managing the stateful pattern

        Raises:
            PatternNotFoundError: If pattern does not exist
            PatternConfigError: If configuration is invalid
            PatternError: If pattern instance creation fails
        """
        pass

    @abstractmethod
    async def get_available_patterns(self) -> List['PatternInfo']:
        """
        Get list of all registered communication patterns.

        Returns:
            List of PatternInfo objects describing available patterns
        """
        pass

    @abstractmethod
    def supports_protocol(self, pattern_name: str, protocol_type: str) -> bool:
        """
        Check if a pattern supports a specific protocol.

        Args:
            pattern_name: Name of the pattern to check
            protocol_type: Protocol type (e.g., "a2a", "mcp", "http")

        Returns:
            True if pattern supports the protocol, False otherwise

        Raises:
            PatternNotFoundError: If pattern does not exist
        """
        pass

    @abstractmethod
    async def validate_pattern_config(
        self,
        pattern_name: str,
        config: 'PatternConfig'
    ) -> 'ValidationResult':
        """
        Validate pattern configuration without executing.

        Args:
            pattern_name: Name of the pattern to validate config for
            config: Configuration to validate

        Returns:
            ValidationResult indicating if config is valid

        Raises:
            PatternNotFoundError: If pattern does not exist
        """
        pass

    @abstractmethod
    async def get_pattern_capabilities(self, pattern_name: str) -> 'PatternCapabilities':
        """
        Get detailed capabilities and constraints for a pattern.

        Args:
            pattern_name: Name of the pattern to query

        Returns:
            PatternCapabilities describing pattern features

        Raises:
            PatternNotFoundError: If pattern does not exist
        """
        pass

    @abstractmethod
    async def list_pattern_instances(self) -> List['PatternInstanceInfo']:
        """
        Get list of all active pattern instances.

        Returns:
            List of PatternInstanceInfo objects for active instances
        """
        pass

    @abstractmethod
    async def shutdown_pattern_instance(self, instance_id: str) -> None:
        """
        Gracefully shutdown a specific pattern instance.

        Args:
            instance_id: Unique identifier of the pattern instance

        Raises:
            PatternNotFoundError: If instance does not exist
        """
        pass
```

### 2. IPatternInstance

Interface for stateful pattern instances:

```python
class IPatternInstance(ABC):
    """
    Interface for stateful communication pattern instances.

    Used for patterns that maintain state across multiple messages,
    such as streaming, delegation, or collaborative workflows.
    """

    @property
    @abstractmethod
    def instance_id(self) -> str:
        """Unique identifier for this pattern instance."""
        pass

    @property
    @abstractmethod
    def pattern_name(self) -> str:
        """Name of the pattern this instance implements."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """
        Initialize the pattern instance.

        Performs any setup required for the pattern to begin processing
        messages, such as establishing connections or initializing state.

        Raises:
            PatternError: If instance startup fails
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        Gracefully stop the pattern instance.

        Performs cleanup such as closing connections, saving state,
        and releasing resources.

        Raises:
            PatternError: If instance shutdown fails
        """
        pass

    @abstractmethod
    async def process_message(
        self,
        message: 'InternalMessageFormat'
    ) -> Optional['PatternResult']:
        """
        Process an incoming message with this pattern instance.

        Args:
            message: SIMF message to process

        Returns:
            PatternResult if processing generates a response, None otherwise

        Raises:
            PatternExecutionError: If message processing fails
        """
        pass

    @abstractmethod
    async def get_status(self) -> 'PatternInstanceStatus':
        """
        Get current status of the pattern instance.

        Returns:
            PatternInstanceStatus with current state information
        """
        pass

    @abstractmethod
    async def update_config(self, config: 'PatternConfig') -> None:
        """
        Update the configuration of this pattern instance.

        Args:
            config: New pattern configuration

        Raises:
            PatternConfigError: If configuration is invalid
            PatternError: If configuration update fails
        """
        pass

    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get pattern instance metrics and statistics.

        Returns:
            Dictionary containing pattern-specific metrics
        """
        pass
```

## Data Models

### 1. Core Pattern Models

```python
from enum import Enum
from typing import Union, Literal
from datetime import datetime

class PatternType(str, Enum):
    """Enumeration of communication pattern types."""
    REQUEST_RESPONSE = "request_response"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    EVENT_BASED = "event_based"
    STREAMING = "streaming"
    PIPELINE = "pipeline"
    DELEGATION = "delegation"
    COLLABORATIVE_WORKFLOW = "collaborative_workflow"
    CUSTOM = "custom"

class PatternDefinition(BaseModel):
    """
    Complete definition of a communication pattern.

    This model represents a pattern specification that can be
    registered with the Pattern Engine.
    """
    name: str = Field(
        description="Unique identifier for the pattern",
        pattern=r"^[a-z][a-z0-9_]*$"  # Snake case pattern names
    )

    version: str = Field(
        description="Pattern version following semantic versioning",
        pattern=r"^\d+\.\d+\.\d+$"
    )

    description: str = Field(
        description="Human-readable description of the pattern"
    )

    pattern_type: PatternType = Field(
        description="Category of communication pattern"
    )

    supported_protocols: List[str] = Field(
        description="List of protocol types this pattern supports",
        min_items=1
    )

    options_schema: Dict[str, Any] = Field(
        description="JSON schema for pattern-specific options",
        default_factory=dict
    )

    implementation_class: str = Field(
        description="Fully qualified Python class implementing the pattern"
    )

    requires_instance: bool = Field(
        description="Whether pattern requires stateful instances",
        default=False
    )

    metadata: Dict[str, Any] = Field(
        description="Additional pattern metadata",
        default_factory=dict
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "request_response",
                "version": "1.0.0",
                "description": "Synchronous request-response pattern",
                "pattern_type": "request_response",
                "supported_protocols": ["a2a", "mcp", "http"],
                "options_schema": {
                    "type": "object",
                    "properties": {
                        "timeout": {"type": "integer", "default": 30000},
                        "retry_attempts": {"type": "integer", "default": 3}
                    }
                },
                "implementation_class": "openmas.patterns.RequestResponsePattern",
                "requires_instance": False
            }
        }

class PatternConfig(BaseModel):
    """
    Configuration for pattern execution.

    This model contains all the information needed to execute
    a specific pattern with custom options.
    """
    pattern_name: str = Field(
        description="Name of the pattern to execute"
    )

    options: Dict[str, Any] = Field(
        description="Pattern-specific configuration options",
        default_factory=dict
    )

    timeout: Optional[int] = Field(
        description="Pattern execution timeout in milliseconds",
        default=None,
        gt=0
    )

    retry_policy: Optional['RetryPolicy'] = Field(
        description="Retry configuration for pattern execution",
        default=None
    )

    protocol_adaptations: Dict[str, Dict[str, Any]] = Field(
        description="Protocol-specific adaptation configurations",
        default_factory=dict
    )

    observability: Optional['ObservabilityConfig'] = Field(
        description="Observability configuration for pattern execution",
        default=None
    )

    metadata: Dict[str, Any] = Field(
        description="Additional configuration metadata",
        default_factory=dict
    )

class RetryPolicy(BaseModel):
    """Configuration for pattern execution retry behavior."""

    enabled: bool = Field(default=True, description="Whether retries are enabled")

    max_attempts: int = Field(
        default=3,
        description="Maximum number of retry attempts",
        ge=1, le=10
    )

    backoff_strategy: Literal["fixed", "linear", "exponential"] = Field(
        default="exponential",
        description="Backoff strategy for retry delays"
    )

    initial_delay_ms: int = Field(
        default=1000,
        description="Initial delay in milliseconds",
        gt=0
    )

    max_delay_ms: int = Field(
        default=30000,
        description="Maximum delay in milliseconds",
        gt=0
    )

    retry_on_errors: List[str] = Field(
        description="Error types that should trigger retries",
        default_factory=lambda: ["timeout", "connection_error", "temporary_failure"]
    )

class ObservabilityConfig(BaseModel):
    """Configuration for pattern execution observability."""

    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")

    tracing_enabled: bool = Field(default=True, description="Enable distributed tracing")

    log_level: Literal["debug", "info", "warning", "error"] = Field(
        default="info",
        description="Logging level for pattern execution"
    )

    custom_tags: Dict[str, str] = Field(
        description="Custom tags for observability",
        default_factory=dict
    )
```

### 2. Pattern Execution Models

```python
class PatternResult(BaseModel):
    """
    Result of pattern execution.

    Contains the outcome of executing a communication pattern,
    including any generated messages and execution metadata.
    """
    success: bool = Field(
        description="Whether pattern execution succeeded"
    )

    pattern_name: str = Field(
        description="Name of the executed pattern"
    )

    execution_id: str = Field(
        description="Unique identifier for this execution"
    )

    result_data: Optional[Any] = Field(
        description="Pattern-specific result data",
        default=None
    )

    messages: List['InternalMessageFormat'] = Field(
        description="SIMF messages generated during execution",
        default_factory=list
    )

    execution_time_ms: float = Field(
        description="Pattern execution duration in milliseconds",
        ge=0
    )

    error: Optional['PatternExecutionError'] = Field(
        description="Error information if execution failed",
        default=None
    )

    metadata: Dict[str, Any] = Field(
        description="Pattern-specific execution metadata",
        default_factory=dict
    )

    created_at: datetime = Field(
        description="When the pattern execution started",
        default_factory=datetime.now
    )

    completed_at: Optional[datetime] = Field(
        description="When the pattern execution completed",
        default=None
    )

class ValidationResult(BaseModel):
    """Result of pattern configuration validation."""

    valid: bool = Field(description="Whether configuration is valid")

    errors: List[str] = Field(
        description="Validation error messages",
        default_factory=list
    )

    warnings: List[str] = Field(
        description="Validation warning messages",
        default_factory=list
    )

    validated_config: Optional[Dict[str, Any]] = Field(
        description="Validated and normalized configuration",
        default=None
    )
```

### 3. Pattern Information Models

```python
class PatternInfo(BaseModel):
    """Summary information about a registered pattern."""

    name: str = Field(description="Pattern name")
    version: str = Field(description="Pattern version")
    description: str = Field(description="Pattern description")
    pattern_type: PatternType = Field(description="Pattern category")
    supported_protocols: List[str] = Field(description="Supported protocols")
    requires_instance: bool = Field(description="Whether pattern requires instances")
    is_available: bool = Field(description="Whether pattern is currently available")
    registration_time: datetime = Field(description="When pattern was registered")

class PatternCapabilities(BaseModel):
    """Detailed capabilities and constraints for a pattern."""

    pattern_name: str = Field(description="Pattern name")

    supported_message_types: List[str] = Field(
        description="SIMF message types the pattern can handle"
    )

    supported_payload_types: List[str] = Field(
        description="SIMF payload types the pattern supports"
    )

    protocol_capabilities: Dict[str, Dict[str, Any]] = Field(
        description="Protocol-specific capabilities and limitations"
    )

    configuration_options: Dict[str, Any] = Field(
        description="Available configuration options with their schemas"
    )

    performance_characteristics: Dict[str, Any] = Field(
        description="Performance and resource usage characteristics",
        default_factory=dict
    )

    dependencies: List[str] = Field(
        description="Other patterns or services this pattern depends on",
        default_factory=list
    )

class PatternInstanceStatus(BaseModel):
    """Status information for a pattern instance."""

    instance_id: str = Field(description="Pattern instance identifier")
    pattern_name: str = Field(description="Pattern name")
    status: Literal["initializing", "running", "paused", "stopping", "stopped", "error"] = Field(
        description="Current instance status"
    )
    started_at: datetime = Field(description="When instance was started")
    last_activity: Optional[datetime] = Field(description="Last message processing time")
    messages_processed: int = Field(description="Total messages processed", ge=0)
    error_count: int = Field(description="Number of processing errors", ge=0)
    current_config: 'PatternConfig' = Field(description="Current instance configuration")
    metadata: Dict[str, Any] = Field(description="Instance-specific metadata", default_factory=dict)

class PatternInstanceInfo(BaseModel):
    """Summary information about a pattern instance."""

    instance_id: str = Field(description="Pattern instance identifier")
    pattern_name: str = Field(description="Pattern name")
    status: str = Field(description="Current status")
    started_at: datetime = Field(description="Start time")
    messages_processed: int = Field(description="Messages processed count")
    last_activity: Optional[datetime] = Field(description="Last activity time")
```

## Error Hierarchy

```python
class PatternError(Exception):
    """Base exception for pattern-related errors."""

    def __init__(self, message: str, pattern_name: Optional[str] = None, **kwargs):
        super().__init__(message)
        self.pattern_name = pattern_name
        self.metadata = kwargs

class PatternNotFoundError(PatternError):
    """Raised when a requested pattern is not registered."""
    pass

class PatternConfigError(PatternError):
    """Raised when pattern configuration is invalid."""

    def __init__(self, message: str, config_errors: List[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_errors = config_errors or []

class PatternExecutionError(PatternError):
    """Raised when pattern execution fails."""

    def __init__(self, message: str, execution_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.execution_id = execution_id

class PatternRegistrationError(PatternError):
    """Raised when pattern registration fails."""
    pass

class UnsupportedProtocolError(PatternError):
    """Raised when a pattern doesn't support a required protocol."""

    def __init__(self, pattern_name: str, protocol: str, **kwargs):
        message = f"Pattern '{pattern_name}' does not support protocol '{protocol}'"
        super().__init__(message, pattern_name, **kwargs)
        self.protocol = protocol
```

## SIMF Integration Requirements

### 1. Pattern Metadata in SIMF

All pattern execution must preserve pattern information in SIMF metadata:

```python
# Required SIMF metadata fields for pattern execution
pattern_metadata = {
    "communication_pattern": "request_response",  # Pattern name
    "pattern_version": "1.0.0",                   # Pattern version
    "pattern_instance_id": "uuid-string",         # Instance ID (if applicable)
    "pattern_execution_id": "uuid-string",        # Execution ID
    "pattern_config": {...},                      # Pattern configuration
    "protocol_adaptations": {...}                 # Protocol-specific adaptations
}
```

### 2. Cross-Protocol Pattern Execution

Patterns must work seamlessly across different protocols through SIMF:

```python
# Example: Request-response pattern across different protocols
async def execute_cross_protocol_pattern():
    # Agent A uses A2A protocol
    request_message = InternalMessageFormat(
        message_id="req-123",
        target_agent_id="agent-b",
        message_type="USER_QUERY",
        payload={
            "payload_type": "invocation_content",
            "invocation_name": "process_data",
            "arguments": {"data": "sample"}
        },
        metadata={
            "communication_pattern": "request_response",
            "source_protocol_type": "a2a"
        }
    )

    # Pattern engine handles protocol adaptation
    result = await pattern_engine.execute_pattern(
        "request_response",
        PatternConfig(pattern_name="request_response"),
        request_message
    )

    # Agent B receives SIMF message regardless of its protocol (MCP, HTTP, etc.)
```

### 3. Protocol Adaptation Requirements

Each pattern must specify how it adapts to different protocols:

```python
# Example protocol adaptations for request-response pattern
protocol_adaptations = {
    "a2a": {
        "capability_name": "request_response",
        "use_tasks": True,
        "correlation_field": "task_id"
    },
    "mcp": {
        "tool_name": "request",
        "use_function_calls": True,
        "await_response": True
    },
    "http": {
        "method": "POST",
        "response_codes": [200, 201],
        "content_type": "application/json"
    },
    "mqtt": {
        "request_topic": "requests/{agent_id}",
        "response_topic": "responses/{agent_id}",
        "qos": 1
    }
}
```

## Usage Examples

### 1. Basic Pattern Execution

```python
# Register a pattern
pattern_def = PatternDefinition(
    name="request_response",
    version="1.0.0",
    description="Synchronous request-response pattern",
    pattern_type=PatternType.REQUEST_RESPONSE,
    supported_protocols=["a2a", "mcp", "http"],
    implementation_class="openmas.patterns.RequestResponsePattern"
)
await pattern_engine.register_pattern(pattern_def)

# Execute the pattern
config = PatternConfig(
    pattern_name="request_response",
    options={"timeout": 30000, "retry_attempts": 3}
)

message = InternalMessageFormat(
    message_id="msg-123",
    target_agent_id="target-agent",
    message_type="USER_QUERY",
    payload={"payload_type": "text_content", "text": "Hello"}
)

result = await pattern_engine.execute_pattern("request_response", config, message)
```

### 2. Stateful Pattern Instance

```python
# Create a streaming pattern instance
config = PatternConfig(
    pattern_name="streaming",
    options={"buffer_size": 1000, "stream_timeout": 60000}
)

instance = await pattern_engine.create_pattern_instance("streaming", config)
await instance.start()

# Process messages through the instance
for message in incoming_messages:
    result = await instance.process_message(message)
    if result:
        await handle_result(result)

# Clean up
await instance.stop()
```

### 3. Pattern Discovery and Validation

```python
# Discover available patterns
patterns = await pattern_engine.get_available_patterns()
for pattern in patterns:
    print(f"{pattern.name}: {pattern.description}")

    # Check protocol support
    if pattern_engine.supports_protocol(pattern.name, "mcp"):
        print(f"  - Supports MCP protocol")

    # Get detailed capabilities
    capabilities = await pattern_engine.get_pattern_capabilities(pattern.name)
    print(f"  - Supported message types: {capabilities.supported_message_types}")

# Validate configuration
config = PatternConfig(
    pattern_name="request_response",
    options={"timeout": "invalid"}  # Invalid type
)

validation = await pattern_engine.validate_pattern_config("request_response", config)
if not validation.valid:
    print(f"Configuration errors: {validation.errors}")
```

---

This API specification provides a comprehensive interface for managing communication patterns in OpenMAS while maintaining the core principles of protocol independence, reasoning agnosticism, and SIMF compatibility.
