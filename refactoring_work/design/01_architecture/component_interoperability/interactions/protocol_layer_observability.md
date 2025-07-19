# Protocol Layer ↔ Observability System

## Relationship Summary
- **Protocol Layer → Observability System**: Provides To
- **Observability System → Protocol Layer**: Depends On

## Interface Definitions

### Protocol Layer → Observability System

#### Methods/Functions
```python
def log_protocol_message(protocol_type: str, direction: MessageDirection, message_data: ProtocolMessageData,
                        logging_options: Optional[ProtocolLoggingOptions] = None) -> LoggingResult:
    """
    Log protocol-specific message data for observability.
    
    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp")
        direction: MessageDirection - Direction of message (INCOMING or OUTGOING)
        message_data: ProtocolMessageData - Protocol-specific message data
        logging_options: Optional[ProtocolLoggingOptions] - Options for message logging
        
    Returns:
        LoggingResult - Result of the logging operation
        
    Raises:
        LoggingFailureError - If the logging operation fails
        InvalidMessageDataError - If the message data is invalid
    """
```

**Data Structures:**

```python
class MessageDirection(Enum):
    """
    Direction of a protocol message.
    """
    INCOMING = "incoming"  # Message coming into the system
    OUTGOING = "outgoing"  # Message leaving the system
    INTERNAL = "internal"  # Message within the system (between components)

class ProtocolMessageData:
    """
    Protocol message data for observability.
    """
    message_id: str  # Unique identifier for the message
    sender_id: str  # Identifier of the sender
    recipient_id: Optional[str]  # Identifier of the recipient (may be None for broadcasts)
    message_type: str  # Type of message (e.g., "request", "response", "notification")
    content_summary: str  # Summary of message content
    timestamp: datetime  # Time when the message was sent/received
    size_bytes: int  # Size of the message in bytes
    protocol_specific: Dict[str, Any]  # Protocol-specific metadata
    session_id: Optional[str] = None  # Session identifier if applicable
    correlation_id: Optional[str] = None  # Correlation identifier for related messages
    trace_id: Optional[str] = None  # Distributed tracing identifier
    span_id: Optional[str] = None  # Span identifier for tracing
    parent_span_id: Optional[str] = None  # Parent span identifier
    reasoning_component_id: Optional[str] = None  # Identifier of the reasoning component
    sensitivity_level: str = "normal"  # Sensitivity level of the message ("normal", "sensitive", "high")
    content_type: str = "unknown"  # Content type of the message
    success: Optional[bool] = None  # Whether the message represents a successful operation
    duration_ms: Optional[int] = None  # Duration of message processing in milliseconds
    error: Optional[Dict[str, Any]] = None  # Error information if applicable
    tags: List[str] = []  # Tags for categorization
    metadata: Dict[str, Any] = {}  # Additional metadata

class ProtocolLoggingOptions:
    """
    Options for protocol message logging.
    """
    log_level: str = "INFO"  # Log level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    include_content: bool = False  # Whether to include full message content
    content_max_size_bytes: int = 1024  # Maximum size of content to include
    sensitive_field_handling: str = "mask"  # How to handle sensitive fields ("mask", "omit", "hash")
    additional_sensitive_fields: List[str] = []  # Additional sensitive fields to handle
    include_protocol_specific: bool = True  # Whether to include protocol-specific metadata
    include_trace_context: bool = True  # Whether to include trace context
    include_performance_metrics: bool = True  # Whether to include performance metrics
    include_in_search_index: bool = True  # Whether to include in search index
    retention_period_days: int = 90  # Retention period in days
    forward_to_external_systems: List[str] = []  # External systems to forward to
    metadata: Dict[str, Any] = {}  # Additional metadata for the logging operation

class LoggingResult:
    """
    Result of a logging operation.
    """
    success: bool  # Whether the logging operation was successful
    log_id: str  # Unique identifier for the log entry
    timestamp: datetime  # Time when the log was created
    storage_location: str  # Where the log is stored
    retention_until: datetime  # Until when the log will be retained
    log_level: str  # Level the message was logged at
    indexed: bool  # Whether the log was indexed for search
    sanitized_fields: List[str] = []  # Fields that were sanitized
    warnings: List[str] = []  # Warnings generated during logging
    forward_results: Dict[str, bool] = {}  # Results of forwarding to external systems
    metadata: Dict[str, Any] = {}  # Additional metadata about the logging operation
```

**Example Usage:**
```python
# Set up message data for an A2A tool invocation request
a2a_message_data = ProtocolMessageData(
    message_id="a2a_msg_f8c7e612",
    sender_id="external_agent_123",
    recipient_id="local_agent_456",
    message_type="tool_invocation_request",
    content_summary="Request to invoke web_search tool to find information about OpenMAS",
    timestamp=datetime.now(),
    size_bytes=2048,
    protocol_specific={
        "a2a_version": "1.0",
        "tool_name": "web_search",
        "tool_parameters": {
            "query": "OpenMAS agent framework",
            "result_count": 5
        },
        "agent_card_version": "2.1",
        "conversation_id": "conv_abc123",
        "step_id": 5
    },
    session_id="session_xyz789",
    correlation_id="corr_456def",
    trace_id="trace_789ghi",
    span_id="span_012jkl",
    reasoning_component_id="symbolic_reasoner_1",
    content_type="application/json",
    tags=["a2a", "tool_invocation", "web_search"],
    metadata={
        "client_version": "3.2.0",
        "client_platform": "web",
        "priority": "normal"
    }
)

# Configure logging options with sensitive field handling
logging_options = ProtocolLoggingOptions(
    log_level="INFO",
    include_content=True,
    content_max_size_bytes=4096,
    sensitive_field_handling="mask",
    additional_sensitive_fields=[
        "tool_parameters.api_key",
        "agent_card.security_context"
    ],
    include_protocol_specific=True,
    include_trace_context=True,
    include_performance_metrics=True,
    retention_period_days=180,  # Extended retention for important messages
    forward_to_external_systems=["security_monitoring", "compliance_audit"],
    metadata={
        "logging_reason": "tool_invocation_monitoring",
        "compliance_requirement": "tool_usage_audit"
    }
)

# Log the A2A message
try:
    logging_result = observability_system.log_protocol_message(
        protocol_type="a2a",
        direction=MessageDirection.INCOMING,
        message_data=a2a_message_data,
        logging_options=logging_options
    )
    
    # Check the logging result
    if logging_result.success:
        logger.debug(f"Successfully logged A2A message with ID: {logging_result.log_id}")
        logger.debug(f"Log stored at: {logging_result.storage_location}")
        logger.debug(f"Log retention until: {logging_result.retention_until}")
        
        # Check if any fields were sanitized
        if logging_result.sanitized_fields:
            logger.debug(f"Sanitized fields: {', '.join(logging_result.sanitized_fields)}")
        
        # Check forwarding results
        for system, success in logging_result.forward_results.items():
            if success:
                logger.debug(f"Successfully forwarded to {system}")
            else:
                logger.warning(f"Failed to forward to {system}")
    else:
        logger.warning("Logging operation was marked as unsuccessful")
        
        # Check for warnings
        for warning in logging_result.warnings:
            logger.warning(f"Logging warning: {warning}")
    
    # Now log an MCP message to demonstrate multi-protocol support
    mcp_message_data = ProtocolMessageData(
        message_id="mcp_msg_d5e6f789",
        sender_id="mcp_client_789",
        recipient_id="openmas_server",
        message_type="sequential_thinking_request",
        content_summary="Request to perform sequential reasoning about climate data",
        timestamp=datetime.now(),
        size_bytes=3072,
        protocol_specific={
            "mcp_version": "2.0",
            "capability": "sequential_thinking",
            "parameters": {
                "problem_statement": "Analyze climate data trends over the past decade",
                "steps_requested": 5,
                "detail_level": "high"
            },
            "authorization": "Bearer ey..." # Sensitive information
        },
        session_id="mcp_session_123abc",
        correlation_id="mcp_corr_456def",
        trace_id="trace_789ghi",
        span_id="span_345mno",
        reasoning_component_id="statistical_reasoner_2",
        content_type="application/json",
        tags=["mcp", "sequential_thinking", "climate_analysis"],
        metadata={
            "client_version": "2.5.0",
            "client_platform": "api",
            "priority": "high"
        }
    )
    
    # Configure logging options for MCP
    mcp_logging_options = ProtocolLoggingOptions(
        log_level="INFO",
        include_content=True,
        content_max_size_bytes=4096,
        sensitive_field_handling="mask",
        additional_sensitive_fields=[
            "protocol_specific.authorization",
            "protocol_specific.parameters.api_key"
        ],
        include_protocol_specific=True,
        include_trace_context=True,
        include_performance_metrics=True,
        retention_period_days=90,
        forward_to_external_systems=["api_monitoring"],
        metadata={
            "logging_reason": "mcp_request_monitoring",
            "compliance_requirement": "api_usage_audit"
        }
    )
    
    # Log the MCP message
    logging_result = observability_system.log_protocol_message(
        protocol_type="mcp",
        direction=MessageDirection.INCOMING,
        message_data=mcp_message_data,
        logging_options=mcp_logging_options
    )
    
    logger.debug(f"Successfully logged MCP message with ID: {logging_result.log_id}")
    
except LoggingFailureError as e:
    logger.error(f"Failed to log protocol message: {str(e)}")
    
    # Try with reduced logging options if full logging fails
    simplified_options = ProtocolLoggingOptions(
        log_level="WARNING",
        include_content=False,
        include_protocol_specific=False,
        include_trace_context=True,
        forward_to_external_systems=[]
    )
    
    try:
        # Retry with simplified options
        logging_result = observability_system.log_protocol_message(
            protocol_type="a2a",
            direction=MessageDirection.INCOMING,
            message_data=a2a_message_data,
            logging_options=simplified_options
        )
        logger.info(f"Successfully logged with simplified options, log ID: {logging_result.log_id}")
    except Exception as retry_error:
        logger.critical(f"Critical logging failure, even with simplified options: {str(retry_error)}")
        # Use local fallback logging
        local_logger.critical(f"Protocol message {a2a_message_data.message_id} could not be logged to observability system")
        
except InvalidMessageDataError as e:
    logger.error(f"Invalid message data: {str(e)}")
    
    # Create a minimal valid message
    minimal_message_data = ProtocolMessageData(
        message_id=a2a_message_data.message_id if hasattr(a2a_message_data, 'message_id') else "unknown",
        sender_id=a2a_message_data.sender_id if hasattr(a2a_message_data, 'sender_id') else "unknown",
        recipient_id="unknown",
        message_type="unknown",
        content_summary="Invalid message data",
        timestamp=datetime.now(),
        size_bytes=0,
        protocol_specific={},
        error={
            "error_type": "invalid_message_data",
            "error_details": str(e)
        }
    )
    
    # Try logging the minimal message
    logging_result = observability_system.log_protocol_message(
        protocol_type="a2a",
        direction=MessageDirection.INCOMING,
        message_data=minimal_message_data,
        logging_options=ProtocolLoggingOptions(log_level="ERROR")
    )
    
    logger.info(f"Logged minimal message for invalid data, log ID: {logging_result.log_id}")
```

```python
def record_protocol_metric(protocol_type: str, metric_name: str, value: Union[float, int], 
                          labels: Optional[Dict[str, str]] = None, 
                          metric_options: Optional[MetricRecordingOptions] = None) -> MetricRecordingResult:
    """
    Record a protocol-specific metric for observability.
    
    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp")
        metric_name: str - Name of the metric
        value: Union[float, int] - Metric value
        labels: Optional[Dict[str, str]] - Additional metric labels
        metric_options: Optional[MetricRecordingOptions] - Options for metric recording
        
    Returns:
        MetricRecordingResult - Result of the metric recording operation
        
    Raises:
        MetricRecordingError - If the metric recording operation fails
        InvalidMetricError - If the metric definition is invalid
        LabelCardinalityError - If the label cardinality exceeds limits
    """
```

**Data Structures:**

```python
class MetricType(Enum):
    """
    Type of metric.
    """
    COUNTER = "counter"  # Cumulative value that only increases
    GAUGE = "gauge"  # Value that can increase or decrease
    HISTOGRAM = "histogram"  # Distribution of values
    SUMMARY = "summary"  # Statistical summary of values

class MetricUnit(Enum):
    """
    Unit of measurement for a metric.
    """
    BYTES = "bytes"  # Size in bytes
    MILLISECONDS = "milliseconds"  # Time in milliseconds
    SECONDS = "seconds"  # Time in seconds
    COUNT = "count"  # Count of events/items
    PERCENTAGE = "percentage"  # Percentage value
    RATIO = "ratio"  # Ratio value
    CUSTOM = "custom"  # Custom unit

class MetricRecordingOptions:
    """
    Options for recording metrics.
    """
    metric_type: MetricType = MetricType.GAUGE  # Type of metric
    unit: MetricUnit = MetricUnit.COUNT  # Unit of measurement
    description: Optional[str] = None  # Description of the metric
    timestamp: Optional[datetime] = None  # Custom timestamp for the metric
    cumulative: bool = False  # Whether the value is cumulative
    record_as_delta: bool = False  # Whether to record value as delta from previous
    aggregation_temporality: str = "delta"  # Aggregation temporality ("delta" or "cumulative")
    create_if_not_exists: bool = True  # Whether to create the metric if it doesn't exist
    standard_labels: bool = True  # Whether to add standard labels (protocol, environment)
    sample_rate: float = 1.0  # Sample rate for recording (0.0-1.0)
    buckets: Optional[List[float]] = None  # Buckets for histograms
    quantiles: Optional[List[float]] = None  # Quantiles for summaries
    max_label_cardinality: int = 100  # Maximum number of label combinations
    expire_idle_series: bool = True  # Whether to expire idle time series
    custom_unit: Optional[str] = None  # Custom unit for MetricUnit.CUSTOM
    metadata: Dict[str, Any] = {}  # Additional metadata

class MetricRecordingResult:
    """
    Result of a metric recording operation.
    """
    success: bool  # Whether the recording operation was successful
    metric_id: str  # Unique identifier for the metric
    timestamp: datetime  # Time when the metric was recorded
    protocol_type: str  # Protocol type
    metric_name: str  # Name of the metric
    value: Union[float, int]  # Recorded value
    effective_labels: Dict[str, str]  # Effective labels used
    aggregated: bool = False  # Whether the value was aggregated with existing values
    sampled: bool = False  # Whether the value was sampled
    warnings: List[str] = []  # Warnings generated during recording
    storage_backend: str = "prometheus"  # Backend where the metric was stored
    metadata: Dict[str, Any] = {}  # Additional metadata about the recording operation
```

**Example Usage:**
```python
# Recording an A2A protocol message processing time metric
try:
    # Configure metric options for A2A message processing time
    a2a_metric_options = MetricRecordingOptions(
        metric_type=MetricType.HISTOGRAM,
        unit=MetricUnit.MILLISECONDS,
        description="Time to process A2A protocol messages",
        timestamp=datetime.now(),
        create_if_not_exists=True,
        standard_labels=True,
        buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000],  # Time buckets in ms
        metadata={
            "component": "protocol_layer",
            "subsystem": "a2a_processor"
        }
    )
    
    # Record the metric
    result = observability_system.record_protocol_metric(
        protocol_type="a2a",
        metric_name="message_processing_time",
        value=123.45,  # milliseconds
        labels={
            "operation": "tool_invocation",
            "tool_name": "web_search",
            "status": "success",
            "agent_type": "reasoning_agent"
        },
        metric_options=a2a_metric_options
    )
    
    # Check the recording result
    if result.success:
        logger.debug(f"Successfully recorded A2A metric {result.metric_name} with value {result.value}")
        logger.debug(f"Effective labels: {result.effective_labels}")
        
        if result.sampled:
            logger.debug("Metric was sampled")
            
        if result.aggregated:
            logger.debug("Metric was aggregated with existing values")
    else:
        logger.warning("Metric recording was marked as unsuccessful")
        
        # Check for warnings
        for warning in result.warnings:
            logger.warning(f"Metric recording warning: {warning}")
    
    # Record multiple A2A-related metrics to demonstrate different metric types
    
    # 1. Counter metric for total tool invocations
    tool_invocation_options = MetricRecordingOptions(
        metric_type=MetricType.COUNTER,
        unit=MetricUnit.COUNT,
        description="Total number of A2A tool invocations",
        cumulative=True
    )
    
    result = observability_system.record_protocol_metric(
        protocol_type="a2a",
        metric_name="tool_invocation_count",
        value=1,  # Increment by 1
        labels={
            "tool_name": "web_search",
            "status": "success",
            "agent_id": "agent_123"
        },
        metric_options=tool_invocation_options
    )
    
    # 2. Gauge metric for active A2A conversations
    active_conversations_options = MetricRecordingOptions(
        metric_type=MetricType.GAUGE,
        unit=MetricUnit.COUNT,
        description="Number of active A2A conversations"
    )
    
    result = observability_system.record_protocol_metric(
        protocol_type="a2a",
        metric_name="active_conversations",
        value=5,  # Current active conversations
        labels={
            "agent_type": "reasoning_agent",
            "environment": "production"
        },
        metric_options=active_conversations_options
    )
    
    # Now record MCP metrics to demonstrate multi-protocol support
    
    # Configure metric options for MCP request processing
    mcp_metric_options = MetricRecordingOptions(
        metric_type=MetricType.HISTOGRAM,
        unit=MetricUnit.MILLISECONDS,
        description="Time to process MCP capability requests",
        buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000],  # Time buckets in ms
        metadata={
            "component": "protocol_layer",
            "subsystem": "mcp_processor"
        }
    )
    
    # Record MCP processing time metric
    result = observability_system.record_protocol_metric(
        protocol_type="mcp",
        metric_name="capability_processing_time",
        value=235.6,  # milliseconds
        labels={
            "capability": "sequential_thinking",
            "step_type": "reasoning",
            "status": "success",
            "reasoning_engine": "symbolic_reasoner"
        },
        metric_options=mcp_metric_options
    )
    
    logger.debug(f"Successfully recorded MCP metric {result.metric_name} with value {result.value}")
    
    # Record MCP capability invocation count
    capability_invocation_options = MetricRecordingOptions(
        metric_type=MetricType.COUNTER,
        unit=MetricUnit.COUNT,
        description="Total number of MCP capability invocations",
        cumulative=True
    )
    
    result = observability_system.record_protocol_metric(
        protocol_type="mcp",
        metric_name="capability_invocation_count",
        value=1,  # Increment by 1
        labels={
            "capability": "sequential_thinking",
            "client_id": "client_789",
            "status": "success"
        },
        metric_options=capability_invocation_options
    )
    
    # Record MCP reasoning quality metric (specific to sequential thinking capability)
    reasoning_quality_options = MetricRecordingOptions(
        metric_type=MetricType.GAUGE,
        unit=MetricUnit.PERCENTAGE,
        description="Quality score for sequential thinking reasoning"
    )
    
    result = observability_system.record_protocol_metric(
        protocol_type="mcp",
        metric_name="sequential_thinking_quality",
        value=92.5,  # Quality percentage
        labels={
            "reasoning_engine": "symbolic_reasoner",
            "problem_domain": "climate_analysis",
            "agent_id": "reasoning_agent_456"
        },
        metric_options=reasoning_quality_options
    )
    
    logger.debug(f"Successfully recorded MCP quality metric with value {result.value}%")
    
except MetricRecordingError as e:
    logger.error(f"Failed to record protocol metric: {str(e)}")
    
    # Try with simplified options
    try:
        simplified_options = MetricRecordingOptions(
            metric_type=MetricType.GAUGE,  # Simplify to gauge
            description="Simplified metric after recording failure",
            create_if_not_exists=True,
            standard_labels=False  # Minimize label cardinality
        )
        
        # Record a simplified metric
        result = observability_system.record_protocol_metric(
            protocol_type="a2a",
            metric_name="message_processing_time_simplified",
            value=123.45,
            labels={"status": "success"},  # Minimal labels
            metric_options=simplified_options
        )
        
        logger.info(f"Recorded simplified metric after failure, ID: {result.metric_id}")
    except Exception as retry_error:
        logger.critical(f"Critical metric recording failure: {str(retry_error)}")
        # Use local metrics store as fallback
        local_metrics.record("a2a.message_processing_time", 123.45)
        
except InvalidMetricError as e:
    logger.error(f"Invalid metric definition: {str(e)}")
    
    # Try with a standard predefined metric instead
    result = observability_system.record_protocol_metric(
        protocol_type="a2a",
        metric_name="standard.processing_time",  # Use standard metric
        value=123.45,
        labels={"operation": "tool_invocation"}
    )
    
    logger.info(f"Recorded using standard metric after validation error, ID: {result.metric_id}")
    
except LabelCardinalityError as e:
    logger.error(f"Label cardinality exceeded: {str(e)}")
    
    # Try with reduced labels
    minimal_labels = {"operation": "tool_invocation"}  # Just the essential label
    
    result = observability_system.record_protocol_metric(
        protocol_type="a2a",
        metric_name="message_processing_time",
        value=123.45,
        labels=minimal_labels,
        metric_options=MetricRecordingOptions(max_label_cardinality=10)  # Reduce cardinality limit
    )
    
    logger.info(f"Recorded with minimal labels after cardinality error, ID: {result.metric_id}")
```

```python
def start_protocol_span(protocol_type: str, operation_name: str, 
                        parent_context: Optional[SpanContext] = None,
                        span_options: Optional[ProtocolSpanOptions] = None) -> ProtocolSpan:
    """
    Start a distributed tracing span for protocol operations.
    
    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp")
        operation_name: str - Name of the operation being traced
        parent_context: Optional[SpanContext] - Optional parent span context for trace continuity
        span_options: Optional[ProtocolSpanOptions] - Options for span creation and configuration
        
    Returns:
        ProtocolSpan - Active span object for the protocol operation
        
    Raises:
        SpanCreationError - If the span cannot be created
        TracingSystemUnavailableError - If the tracing system is unavailable
        InvalidParentContextError - If the parent context is invalid
    """
```

**Data Structures:**

```python
class SpanKind(Enum):
    """
    Kind of span in relation to its position in the trace.
    """
    INTERNAL = "internal"  # Internal operation within the system
    SERVER = "server"  # Server side of an RPC
    CLIENT = "client"  # Client side of an RPC
    PRODUCER = "producer"  # Producer of an asynchronous message
    CONSUMER = "consumer"  # Consumer of an asynchronous message

class SpanContext:
    """
    Context information for a span, used for propagation across process boundaries.
    """
    trace_id: str  # ID of the trace this span belongs to
    span_id: str  # ID of this span
    trace_flags: int  # Flags for this trace (e.g., sampled flag)
    trace_state: Optional[str] = None  # Vendor-specific trace information
    is_remote: bool = False  # Whether this context was created from remote parent
    
    def is_valid(self) -> bool:
        """
        Check if this context is valid.
        """
        # Implementation details
        pass

class ProtocolSpanOptions:
    """
    Options for protocol span creation and configuration.
    """
    kind: SpanKind = SpanKind.INTERNAL  # Kind of span
    start_time: Optional[datetime] = None  # Custom start time for the span
    attributes: Dict[str, Any] = {}  # Initial attributes to set on the span
    links: List[SpanLink] = []  # Links to other spans
    events: List[SpanEvent] = []  # Initial events to add to the span
    sampling_hint: Optional[str] = None  # Hint for the sampling decision
    record_exceptions: bool = True  # Whether to automatically record exceptions
    protocol_specific_tags: Dict[str, str] = {}  # Protocol-specific tags
    protocol_version: Optional[str] = None  # Version of the protocol
    capture_messaging_info: bool = True  # Whether to capture messaging info
    capture_request_parameters: bool = False  # Whether to capture request parameters
    sanitize_attributes: bool = True  # Whether to sanitize sensitive attributes
    sensitive_attribute_patterns: List[str] = []  # Patterns for sensitive attributes
    correlation_enabled: bool = True  # Whether to enable correlation with logs/metrics
    resource_attribution: Dict[str, str] = {}  # Resource attribution information
    metadata: Dict[str, Any] = {}  # Additional metadata

class SpanLink:
    """
    Link to another span in a different trace.
    """
    context: SpanContext  # Context of the linked span
    attributes: Dict[str, Any] = {}  # Attributes for the link

class SpanEvent:
    """
    Event recorded within a span.
    """
    name: str  # Name of the event
    timestamp: datetime  # Time of the event
    attributes: Dict[str, Any] = {}  # Attributes for the event

class ProtocolSpan:
    """
    Active span object for a protocol operation.
    """
    context: SpanContext  # Context for this span
    operation_name: str  # Name of the operation
    protocol_type: str  # Type of protocol
    start_time: datetime  # Time when the span started
    end_time: Optional[datetime] = None  # Time when the span ended
    status: str = "unset"  # Status of the span ("unset", "ok", "error")
    attributes: Dict[str, Any] = {}  # Attributes of the span
    events: List[SpanEvent] = []  # Events recorded in the span
    links: List[SpanLink] = []  # Links to other spans
    parent_span_id: Optional[str] = None  # ID of the parent span
    kind: SpanKind  # Kind of span
    
    def set_attribute(self, key: str, value: Any) -> None:
        """
        Set an attribute on this span.
        """
        # Implementation details
        pass
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an event to this span.
        """
        # Implementation details
        pass
    
    def record_exception(self, exception: Exception, attributes: Optional[Dict[str, Any]] = None) -> None:
        """
        Record an exception that occurred during the operation.
        """
        # Implementation details
        pass
    
    def set_status(self, status: str, description: Optional[str] = None) -> None:
        """
        Set the status of this span.
        """
        # Implementation details
        pass
    
    def end(self, end_time: Optional[datetime] = None) -> None:
        """
        End this span.
        """
        # Implementation details
        pass
    
    def update_name(self, new_name: str) -> None:
        """
        Update the name of this span.
        """
        # Implementation details
        pass
```

**Example Usage:**
```python
# Example 1: Tracing A2A protocol message processing

# Extract trace context from incoming A2A request
extracted_context = protocol_layer.extract_trace_context(
    protocol_type="a2a",
    request_data=incoming_a2a_request
)

# Configure span options for A2A processing
a2a_span_options = ProtocolSpanOptions(
    kind=SpanKind.SERVER,  # This is a server-side operation
    attributes={
        "protocol.version": "1.0",
        "message.id": incoming_a2a_request.get("message_id", "unknown"),
        "message.type": incoming_a2a_request.get("type", "unknown"),
        "agent.id": incoming_a2a_request.get("agent_id", "unknown"),
        "conversation.id": incoming_a2a_request.get("conversation_id", "unknown"),
        "step.id": incoming_a2a_request.get("step_id", "unknown")
    },
    protocol_specific_tags={
        "a2a.tool_name": incoming_a2a_request.get("tool_name", "unknown"),
        "a2a.agent_card_version": incoming_a2a_request.get("agent_card_version", "unknown")
    },
    protocol_version="1.0",
    capture_messaging_info=True,
    capture_request_parameters=False,  # Don't capture full parameters for privacy
    sanitize_attributes=True,
    sensitive_attribute_patterns=["*.api_key", "*.token", "*.credentials"],
    correlation_enabled=True,
    resource_attribution={
        "service.name": "openmas-a2a-protocol-handler",
        "service.version": "0.3.0",
        "deployment.environment": "production"
    },
    metadata={
        "component": "protocol_layer",
        "subsystem": "a2a_processor"
    }
)

try:
    # Start a span for processing the A2A request
    span = observability_system.start_protocol_span(
        protocol_type="a2a",
        operation_name="process_a2a_tool_invocation",
        parent_context=extracted_context,
        span_options=a2a_span_options
    )
    
    try:
        # Add an event marking the start of request validation
        span.add_event("validation_started", {
            "validation_type": "tool_invocation",
            "timestamp_ms": int(time.time() * 1000)
        })
        
        # Validate the A2A request
        validation_result = validate_a2a_request(incoming_a2a_request)
        
        # Add an event marking the end of request validation
        span.add_event("validation_completed", {
            "validation_success": validation_result.success,
            "validation_duration_ms": validation_result.duration_ms
        })
        
        # Set validation result attributes
        span.set_attribute("validation.success", validation_result.success)
        span.set_attribute("validation.duration_ms", validation_result.duration_ms)
        
        if not validation_result.success:
            span.set_status("error", f"Validation failed: {validation_result.error_message}")
            raise ValidationError(validation_result.error_message)
        
        # Process the A2A tool invocation
        span.add_event("tool_invocation_started")
        
        # Record tool-specific attributes
        span.set_attribute("tool.name", incoming_a2a_request.get("tool_name"))
        span.set_attribute("tool.version", incoming_a2a_request.get("tool_version", "unknown"))
        
        # Invoke the tool
        tool_result = invoke_tool(
            tool_name=incoming_a2a_request.get("tool_name"),
            parameters=incoming_a2a_request.get("parameters", {}),
            context=incoming_a2a_request.get("context", {})
        )
        
        span.add_event("tool_invocation_completed", {
            "success": tool_result.success,
            "duration_ms": tool_result.duration_ms
        })
        
        # Record result attributes
        span.set_attribute("result.success", tool_result.success)
        span.set_attribute("result.duration_ms", tool_result.duration_ms)
        span.set_attribute("result.size_bytes", tool_result.size_bytes)
        
        if tool_result.success:
            span.set_status("ok")
        else:
            span.set_status("error", f"Tool invocation failed: {tool_result.error_message}")
        
        # Create and format A2A response
        span.add_event("response_creation_started")
        
        a2a_response = create_a2a_response(
            request=incoming_a2a_request,
            tool_result=tool_result
        )
        
        span.add_event("response_creation_completed")
        
        # Return the A2A response
        return a2a_response
        
    except ValidationError as e:
        span.record_exception(e)
        span.set_status("error", str(e))
        raise
    except ToolInvocationError as e:
        span.record_exception(e)
        span.set_status("error", str(e))
        raise
    except Exception as e:
        span.record_exception(e)
        span.set_status("error", f"Unexpected error: {str(e)}")
        raise
    finally:
        # Always end the span
        span.end()
        
except SpanCreationError as e:
    logger.error(f"Failed to create A2A protocol span: {str(e)}")
    # Continue processing without tracing
    return process_a2a_request_without_tracing(incoming_a2a_request)
    
except TracingSystemUnavailableError as e:
    logger.error(f"Tracing system unavailable: {str(e)}")
    # Continue processing without tracing
    return process_a2a_request_without_tracing(incoming_a2a_request)


# Example 2: Tracing MCP capability invocation to demonstrate multi-protocol support

# Extract trace context from incoming MCP request
extracted_context = protocol_layer.extract_trace_context(
    protocol_type="mcp",
    request_data=incoming_mcp_request
)

# Configure span options for MCP processing
mcp_span_options = ProtocolSpanOptions(
    kind=SpanKind.SERVER,  # This is a server-side operation
    attributes={
        "protocol.version": "2.0",
        "message.id": incoming_mcp_request.get("message_id", "unknown"),
        "client.id": incoming_mcp_request.get("client_id", "unknown"),
        "session.id": incoming_mcp_request.get("session_id", "unknown")
    },
    protocol_specific_tags={
        "mcp.capability": incoming_mcp_request.get("capability", "unknown"),
        "mcp.capability_version": incoming_mcp_request.get("capability_version", "unknown")
    },
    protocol_version="2.0",
    sanitize_attributes=True,
    sensitive_attribute_patterns=["*.authorization", "*.api_key"],
    resource_attribution={
        "service.name": "openmas-mcp-protocol-handler",
        "service.version": "0.3.0",
        "deployment.environment": "production"
    }
)

try:
    # Start a span for processing the MCP capability request
    span = observability_system.start_protocol_span(
        protocol_type="mcp",
        operation_name="process_mcp_sequential_thinking",
        parent_context=extracted_context,
        span_options=mcp_span_options
    )
    
    try:
        # Add an event marking the start of capability invocation
        span.add_event("capability_invocation_started", {
            "capability": "sequential_thinking",
            "parameters_count": len(incoming_mcp_request.get("parameters", {}))
        })
        
        # Record capability-specific attributes
        span.set_attribute("capability.name", "sequential_thinking")
        span.set_attribute("capability.version", incoming_mcp_request.get("capability_version", "1.0"))
        
        # Process the sequential thinking capability request
        capability_result = process_sequential_thinking(
            parameters=incoming_mcp_request.get("parameters", {}),
            context=incoming_mcp_request.get("context", {})
        )
        
        span.add_event("capability_invocation_completed", {
            "success": capability_result.success,
            "steps_generated": len(capability_result.thinking_steps),
            "duration_ms": capability_result.duration_ms
        })
        
        # Record result attributes
        span.set_attribute("result.success", capability_result.success)
        span.set_attribute("result.steps_count", len(capability_result.thinking_steps))
        span.set_attribute("result.duration_ms", capability_result.duration_ms)
        span.set_attribute("result.confidence", capability_result.confidence)
        
        if capability_result.success:
            span.set_status("ok")
        else:
            span.set_status("error", f"Capability invocation failed: {capability_result.error_message}")
        
        # Create and format MCP response
        mcp_response = create_mcp_response(
            request=incoming_mcp_request,
            capability_result=capability_result
        )
        
        # Return the MCP response
        return mcp_response
        
    except Exception as e:
        span.record_exception(e)
        span.set_status("error", str(e))
        raise
    finally:
        # Always end the span
        span.end()
        
except SpanCreationError as e:
    logger.error(f"Failed to create MCP protocol span: {str(e)}")
    # Continue processing without tracing
    return process_mcp_request_without_tracing(incoming_mcp_request)
```

#### Events
- `protocol_error_occurred`
  - **Purpose**: Notifies when a protocol error occurs
  - **Payload**: Protocol type, error details, context
  - **Subscribers**: Observability System alerting component

- `protocol_traffic_threshold_exceeded`
  - **Purpose**: Notifies when protocol traffic exceeds thresholds
  - **Payload**: Protocol type, traffic metrics, threshold
  - **Subscribers**: Observability System alerting component

### Observability System → Protocol Layer

#### Methods/Functions
```python
def extract_trace_context(protocol_type: str, request_data: Dict[str, Any],
                        extraction_options: Optional[TraceContextExtractionOptions] = None) -> Optional[SpanContext]:
    """
    Extract distributed tracing context from a protocol request.
    
    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp", "http")
        request_data: Dict[str, Any] - Protocol-specific request data
        extraction_options: Optional[TraceContextExtractionOptions] - Options for context extraction
        
    Returns:
        Optional[SpanContext] - Extracted span context or None if no context could be extracted
        
    Raises:
        ProtocolNotSupportedError - If the specified protocol is not supported
        InvalidRequestDataError - If the request data is invalid or malformed
        TraceContextExtractionError - If an error occurs during context extraction
    """
```

**Data Structures:**

```python
class TraceContextExtractionOptions:
    """
    Options for extracting trace context from protocol requests.
    """
    create_new_if_missing: bool = False  # Whether to create a new context if none is found
    ignore_invalid_context: bool = True  # Whether to ignore invalid context
    protocol_version: Optional[str] = None  # Version of the protocol to use for extraction
    custom_extractors: Dict[str, Callable] = {}  # Custom extractors for specific protocols
    custom_header_names: Dict[str, str] = {}  # Custom header names for standard trace context
    trace_id_header: Optional[str] = None  # Custom header name for trace ID
    span_id_header: Optional[str] = None  # Custom header name for span ID
    trace_flags_header: Optional[str] = None  # Custom header name for trace flags
    trace_state_header: Optional[str] = None  # Custom header name for trace state
    debug_mode: bool = False  # Whether to enable debug mode for extraction
    correlation_extraction: bool = True  # Whether to extract correlation context
    correlation_headers: List[str] = []  # Headers to extract for correlation
    metadata: Dict[str, Any] = {}  # Additional metadata for extraction

class InvalidRequestDataError(Exception):
    """
    Error raised when the request data is invalid or malformed.
    """
    pass

class TraceContextExtractionError(Exception):
    """
    Error raised when an error occurs during trace context extraction.
    """
    pass
```

**Example Usage:**
```python
# Example 1: Extracting trace context from A2A protocol request

# Define A2A request data
a2a_request = {
    "message_id": "a2a_msg_123",
    "agent_id": "external_agent_456",
    "conversation_id": "conv_789",
    "step_id": 3,
    "type": "tool_invocation",
    "tool_name": "web_search",
    "parameters": {
        "query": "OpenMAS framework"
    },
    "context": {
        "previous_results": [...]
    },
    "trace_context": {
        "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
        "span_id": "00f067aa0ba902b7",
        "trace_flags": "01",
        "trace_state": "rojo=00f067aa0ba902b7,congo=t61rcWkgMzE"
    }
}

# Configure extraction options for A2A protocol
a2a_extraction_options = TraceContextExtractionOptions(
    create_new_if_missing=True,  # Create a new context if none exists
    ignore_invalid_context=True,
    protocol_version="1.0",
    trace_id_header="trace_context.trace_id",
    span_id_header="trace_context.span_id",
    trace_flags_header="trace_context.trace_flags",
    trace_state_header="trace_context.trace_state",
    correlation_extraction=True,
    correlation_headers=["conversation_id", "step_id"],
    metadata={
        "extraction_source": "a2a_processor",
        "protocol_handler": "a2a_standard_handler"
    }
)

try:
    # Extract trace context from A2A request
    span_context = protocol_layer.extract_trace_context(
        protocol_type="a2a",
        request_data=a2a_request,
        extraction_options=a2a_extraction_options
    )
    
    if span_context:
        logger.debug(f"Successfully extracted trace context from A2A request")
        logger.debug(f"Trace ID: {span_context.trace_id}")
        logger.debug(f"Span ID: {span_context.span_id}")
        
        # Use the extracted context for creating a new span
        span = observability_system.start_protocol_span(
            protocol_type="a2a",
            operation_name="process_a2a_tool_invocation",
            parent_context=span_context
        )
        
        # Process A2A request with the new span
        # ...
    else:
        logger.debug("No trace context found in A2A request, created new context")
        
        # Create a new root span
        span = observability_system.start_protocol_span(
            protocol_type="a2a",
            operation_name="process_a2a_tool_invocation"
        )
        
        # Process A2A request with the new span
        # ...
    
except ProtocolNotSupportedError as e:
    logger.error(f"Protocol not supported for trace context extraction: {str(e)}")
    # Process without tracing
    process_a2a_request_without_tracing(a2a_request)
    
except InvalidRequestDataError as e:
    logger.error(f"Invalid A2A request data for trace context extraction: {str(e)}")
    # Process with a new trace context
    span = observability_system.start_protocol_span(
        protocol_type="a2a",
        operation_name="process_a2a_tool_invocation"
    )
    # Process A2A request with the new span
    # ...
    
except TraceContextExtractionError as e:
    logger.error(f"Error extracting trace context from A2A request: {str(e)}")
    # Process with a new trace context
    span = observability_system.start_protocol_span(
        protocol_type="a2a",
        operation_name="process_a2a_tool_invocation"
    )
    # Process A2A request with the new span
    # ...


# Example 2: Extracting trace context from MCP protocol request to demonstrate multi-protocol support

# Define MCP request data
mcp_request = {
    "message_id": "mcp_msg_456",
    "client_id": "mcp_client_789",
    "session_id": "session_123",
    "capability": "sequential_thinking",
    "capability_version": "1.0",
    "parameters": {
        "problem_statement": "Analyze climate data trends",
        "steps_requested": 5
    },
    "context": {
        "previous_results": [...]
    },
    "headers": {
        "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
        "tracestate": "rojo=00f067aa0ba902b7,congo=t61rcWkgMzE"
    }
}

# Configure extraction options for MCP protocol
mcp_extraction_options = TraceContextExtractionOptions(
    create_new_if_missing=True,
    ignore_invalid_context=True,
    protocol_version="2.0",
    trace_id_header="headers.traceparent",  # MCP uses W3C Trace Context format
    correlation_extraction=True,
    correlation_headers=["session_id"],
    metadata={
        "extraction_source": "mcp_processor",
        "protocol_handler": "mcp_standard_handler"
    }
)

try:
    # Extract trace context from MCP request
    span_context = protocol_layer.extract_trace_context(
        protocol_type="mcp",
        request_data=mcp_request,
        extraction_options=mcp_extraction_options
    )
    
    if span_context:
        logger.debug(f"Successfully extracted trace context from MCP request")
        logger.debug(f"Trace ID: {span_context.trace_id}")
        logger.debug(f"Span ID: {span_context.span_id}")
        
        # Use the extracted context for creating a new span
        span = observability_system.start_protocol_span(
            protocol_type="mcp",
            operation_name="process_mcp_sequential_thinking",
            parent_context=span_context
        )
        
        # Process MCP request with the new span
        # ...
    else:
        logger.debug("No trace context found in MCP request, created new context")
        
        # Create a new root span
        span = observability_system.start_protocol_span(
            protocol_type="mcp",
            operation_name="process_mcp_sequential_thinking"
        )
        
        # Process MCP request with the new span
        # ...
    
except Exception as e:
    logger.error(f"Error in MCP trace context extraction: {str(e)}")
    # Process without tracing
    process_mcp_request_without_tracing(mcp_request)


# Example 3: Extracting trace context from HTTP protocol request

# Define HTTP request data
http_request = {
    "method": "POST",
    "path": "/api/v1/agent/invoke",
    "headers": {
        "content-type": "application/json",
        "traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
        "tracestate": "congo=t61rcWkgMzE"
    },
    "body": {
        "agent_id": "http_agent_123",
        "action": "invoke_tool",
        "tool_name": "database_query",
        "parameters": {
            "query": "SELECT * FROM users LIMIT 10"
        }
    }
}

# Configure extraction options for HTTP protocol
http_extraction_options = TraceContextExtractionOptions(
    create_new_if_missing=False,
    ignore_invalid_context=True,
    correlation_extraction=True,
    correlation_headers=["request-id", "correlation-id"]
)

# Extract trace context from HTTP request
span_context = protocol_layer.extract_trace_context(
    protocol_type="http",
    request_data=http_request,
    extraction_options=http_extraction_options
)

if span_context:
    logger.debug(f"Successfully extracted trace context from HTTP request")
    
    # Use the extracted context
    span = observability_system.start_protocol_span(
        protocol_type="http",
        operation_name="process_http_request",
        parent_context=span_context
    )
    
    # Process HTTP request with the new span
    # ...
else:
    logger.debug("No trace context found in HTTP request")
    
    # Create a new root span
    span = observability_system.start_protocol_span(
        protocol_type="http",
        operation_name="process_http_request"
    )
    
    # Process HTTP request with the new span
    # ...
```

```python
def inject_trace_context(protocol_type: str, span_context: SpanContext, carrier: Dict[str, Any],
                       injection_options: Optional[TraceContextInjectionOptions] = None) -> Dict[str, Any]:
    """
    Inject distributed tracing context into a protocol message.
    
    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp", "http")
        span_context: SpanContext - Current span context to inject
        carrier: Dict[str, Any] - Protocol message carrier to inject context into
        injection_options: Optional[TraceContextInjectionOptions] - Options for context injection
        
    Returns:
        Dict[str, Any] - Modified carrier with trace context injected
        
    Raises:
        ProtocolNotSupportedError - If the specified protocol is not supported
        InvalidSpanContextError - If the span context is invalid
        InvalidCarrierError - If the carrier is invalid or incompatible
        TraceContextInjectionError - If an error occurs during context injection
    """
```

**Data Structures:**

```python
class TraceContextInjectionOptions:
    """
    Options for injecting trace context into protocol messages.
    """
    protocol_version: Optional[str] = None  # Version of the protocol to use for injection
    custom_injectors: Dict[str, Callable] = {}  # Custom injectors for specific protocols
    custom_header_names: Dict[str, str] = {}  # Custom header names for standard trace context
    trace_id_header: Optional[str] = None  # Custom header name for trace ID
    span_id_header: Optional[str] = None  # Custom header name for span ID
    trace_flags_header: Optional[str] = None  # Custom header name for trace flags
    trace_state_header: Optional[str] = None  # Custom header name for trace state
    header_path: str = "headers"  # Path in the carrier where headers should be injected
    use_standard_format: bool = True  # Whether to use standard W3C Trace Context format
    preserve_existing_context: bool = False  # Whether to preserve existing context in the carrier
    include_baggage: bool = True  # Whether to include baggage items
    correlation_injection: bool = True  # Whether to inject correlation context
    correlation_values: Dict[str, str] = {}  # Values to inject for correlation
    metadata: Dict[str, Any] = {}  # Additional metadata for injection

class InvalidSpanContextError(Exception):
    """
    Error raised when the span context is invalid.
    """
    pass

class InvalidCarrierError(Exception):
    """
    Error raised when the carrier is invalid or incompatible.
    """
    pass

class TraceContextInjectionError(Exception):
    """
    Error raised when an error occurs during trace context injection.
    """
    pass
```

**Example Usage:**
```python
# Example 1: Injecting trace context into A2A protocol message

# Get current span context
current_span_context = current_span.context

# Create initial A2A response carrier
a2a_response_carrier = {
    "message_id": "a2a_resp_456",
    "in_response_to": "a2a_msg_123",
    "agent_id": "local_agent_456",
    "conversation_id": "conv_789",
    "step_id": 4,
    "type": "tool_invocation_response",
    "tool_name": "web_search",
    "result": {
        "status": "success",
        "search_results": [
            {
                "title": "OpenMAS: Multi-Protocol Agent Framework",
                "url": "https://example.com/openmas",
                "snippet": "OpenMAS is a reasoning-agnostic agent framework..."
            },
            # More results...
        ]
    }
}

# Configure injection options for A2A protocol
a2a_injection_options = TraceContextInjectionOptions(
    protocol_version="1.0",
    trace_id_header="trace_context.trace_id",
    span_id_header="trace_context.span_id",
    trace_flags_header="trace_context.trace_flags",
    trace_state_header="trace_context.trace_state",
    header_path="trace_context",  # A2A uses a trace_context object
    use_standard_format=False,  # A2A uses its own format
    preserve_existing_context=False,
    include_baggage=True,
    correlation_injection=True,
    correlation_values={
        "conversation_id": "conv_789",  # Ensure conversation ID is propagated
        "step_sequence": "4"  # Step sequence for tracking
    },
    metadata={
        "injection_source": "a2a_processor",
        "protocol_handler": "a2a_standard_handler"
    }
)

try:
    # Inject trace context into A2A response
    a2a_response_with_context = protocol_layer.inject_trace_context(
        protocol_type="a2a",
        span_context=current_span_context,
        carrier=a2a_response_carrier,
        injection_options=a2a_injection_options
    )
    
    logger.debug(f"Successfully injected trace context into A2A response")
    
    # Verify the trace context was injected correctly
    trace_context = a2a_response_with_context.get("trace_context", {})
    if trace_context:
        logger.debug(f"Injected trace ID: {trace_context.get('trace_id')}")
        logger.debug(f"Injected span ID: {trace_context.get('span_id')}")
    
    # Send the A2A response with trace context
    send_a2a_response(a2a_response_with_context)
    
except ProtocolNotSupportedError as e:
    logger.error(f"Protocol not supported for trace context injection: {str(e)}")
    # Send response without trace context
    send_a2a_response(a2a_response_carrier)
    
except InvalidSpanContextError as e:
    logger.error(f"Invalid span context for trace context injection: {str(e)}")
    # Send response without trace context
    send_a2a_response(a2a_response_carrier)
    
except InvalidCarrierError as e:
    logger.error(f"Invalid carrier for trace context injection: {str(e)}")
    # Create a valid carrier and send response
    valid_carrier = fix_a2a_carrier(a2a_response_carrier)
    send_a2a_response(valid_carrier)
    
except TraceContextInjectionError as e:
    logger.error(f"Error injecting trace context into A2A response: {str(e)}")
    # Send response without trace context
    send_a2a_response(a2a_response_carrier)


# Example 2: Injecting trace context into MCP protocol message to demonstrate multi-protocol support

# Create initial MCP response carrier
mcp_response_carrier = {
    "message_id": "mcp_resp_789",
    "in_response_to": "mcp_msg_456",
    "client_id": "mcp_client_789",
    "session_id": "session_123",
    "capability": "sequential_thinking",
    "capability_version": "1.0",
    "status": "success",
    "thinking_steps": [
        {
            "step_number": 1,
            "thought": "First, I need to understand the climate data trends over the past decade."
        },
        {
            "step_number": 2,
            "thought": "Looking at temperature records, there's a clear warming trend..."
        },
        # More steps...
    ],
    "conclusion": "The data shows a consistent warming trend with increasing frequency of extreme weather events.",
    "headers": {}
}

# Configure injection options for MCP protocol
mcp_injection_options = TraceContextInjectionOptions(
    protocol_version="2.0",
    header_path="headers",  # MCP uses headers for context
    use_standard_format=True,  # MCP uses W3C Trace Context format
    preserve_existing_context=False,
    include_baggage=True,
    correlation_injection=True,
    correlation_values={
        "session_id": "session_123"  # Ensure session ID is propagated
    },
    metadata={
        "injection_source": "mcp_processor",
        "protocol_handler": "mcp_standard_handler"
    }
)

try:
    # Inject trace context into MCP response
    mcp_response_with_context = protocol_layer.inject_trace_context(
        protocol_type="mcp",
        span_context=current_span_context,
        carrier=mcp_response_carrier,
        injection_options=mcp_injection_options
    )
    
    logger.debug(f"Successfully injected trace context into MCP response")
    
    # Verify the trace context was injected correctly
    headers = mcp_response_with_context.get("headers", {})
    if "traceparent" in headers:
        logger.debug(f"Injected W3C traceparent: {headers.get('traceparent')}")
    
    # Send the MCP response with trace context
    send_mcp_response(mcp_response_with_context)
    
except Exception as e:
    logger.error(f"Error injecting trace context into MCP response: {str(e)}")
    # Send response without trace context
    send_mcp_response(mcp_response_carrier)


# Example 3: Injecting trace context into HTTP protocol message

# Create initial HTTP response carrier
http_response_carrier = {
    "status": 200,
    "headers": {
        "content-type": "application/json"
    },
    "body": {
        "success": True,
        "agent_id": "http_agent_123",
        "result": {
            "data": [...],  # Query results
            "count": 10
        }
    }
}

# Configure injection options for HTTP protocol
http_injection_options = TraceContextInjectionOptions(
    header_path="headers",
    use_standard_format=True,  # HTTP uses W3C Trace Context format
    preserve_existing_context=False
)

# Inject trace context into HTTP response
http_response_with_context = protocol_layer.inject_trace_context(
    protocol_type="http",
    span_context=current_span_context,
    carrier=http_response_carrier,
    injection_options=http_injection_options
)

# Verify the trace context was injected correctly
headers = http_response_with_context.get("headers", {})
if "traceparent" in headers:
    logger.debug(f"Injected W3C traceparent: {headers.get('traceparent')}")

# Send the HTTP response with trace context
send_http_response(http_response_with_context)
```

```python
def get_observable_protocol_attributes(protocol_type: str, 
                                     attribute_options: Optional[ProtocolAttributeOptions] = None) -> List[ProtocolAttribute]:
    """
    Get observable attributes for a protocol.
    
    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp", "http")
        attribute_options: Optional[ProtocolAttributeOptions] - Options for attribute retrieval
        
    Returns:
        List[ProtocolAttribute] - List of observable protocol attributes
        
    Raises:
        ProtocolNotSupportedError - If the specified protocol is not supported
        AttributeRetrievalError - If an error occurs during attribute retrieval
    """
```

**Data Structures:**

```python
class AttributeCategory(Enum):
    """
    Category of protocol attribute.
    """
    MESSAGE = "message"  # Message-related attribute
    PERFORMANCE = "performance"  # Performance-related attribute
    SECURITY = "security"  # Security-related attribute
    CONTENT = "content"  # Content-related attribute
    METADATA = "metadata"  # Metadata-related attribute
    RELATIONSHIP = "relationship"  # Relationship-related attribute
    CUSTOM = "custom"  # Custom attribute

class AttributeDataType(Enum):
    """
    Data type of protocol attribute.
    """
    STRING = "string"  # String value
    NUMBER = "number"  # Numeric value
    BOOLEAN = "boolean"  # Boolean value
    OBJECT = "object"  # Object value
    ARRAY = "array"  # Array value
    TIMESTAMP = "timestamp"  # Timestamp value
    DURATION = "duration"  # Duration value
    ENUM = "enum"  # Enumerated value

class ProtocolAttribute:
    """
    Observable attribute for a protocol.
    """
    name: str  # Name of the attribute
    path: str  # Path to the attribute in the protocol message
    description: str  # Description of the attribute
    category: AttributeCategory  # Category of the attribute
    data_type: AttributeDataType  # Data type of the attribute
    required: bool  # Whether the attribute is required
    protocol_type: str  # Type of protocol this attribute belongs to
    protocol_version: Optional[str] = None  # Version of the protocol this attribute applies to
    is_sensitive: bool = False  # Whether the attribute contains sensitive data
    sampling_rate: float = 1.0  # Rate at which this attribute should be sampled (0.0-1.0)
    cardinality: Optional[str] = None  # Cardinality of the attribute ("low", "medium", "high")
    example_values: List[Any] = []  # Example values for this attribute
    enum_values: Optional[List[str]] = None  # Possible values if data_type is ENUM
    default_value: Optional[Any] = None  # Default value for this attribute
    unit: Optional[str] = None  # Unit of measurement for numeric attributes
    related_attributes: List[str] = []  # Related attributes
    tags: List[str] = []  # Tags for categorization
    metadata: Dict[str, Any] = {}  # Additional metadata

class ProtocolAttributeOptions:
    """
    Options for retrieving protocol attributes.
    """
    protocol_version: Optional[str] = None  # Version of the protocol to get attributes for
    include_sensitive: bool = False  # Whether to include sensitive attributes
    categories: Optional[List[AttributeCategory]] = None  # Filter by categories
    data_types: Optional[List[AttributeDataType]] = None  # Filter by data types
    required_only: bool = False  # Whether to include only required attributes
    include_metadata: bool = True  # Whether to include metadata attributes
    include_examples: bool = True  # Whether to include example values
    include_internal: bool = False  # Whether to include internal attributes
    max_results: Optional[int] = None  # Maximum number of attributes to return
    tag_filter: Optional[List[str]] = None  # Filter by tags
    search_query: Optional[str] = None  # Search query to filter attributes
    metadata: Dict[str, Any] = {}  # Additional metadata for retrieval

class AttributeRetrievalError(Exception):
    """
    Error raised when an error occurs during attribute retrieval.
    """
    pass
```

**Example Usage:**
```python
# Example 1: Retrieving observable attributes for A2A protocol

# Configure attribute options for A2A protocol
a2a_attribute_options = ProtocolAttributeOptions(
    protocol_version="1.0",
    include_sensitive=False,  # Exclude sensitive attributes
    categories=[AttributeCategory.MESSAGE, AttributeCategory.PERFORMANCE, AttributeCategory.CONTENT],
    required_only=False,  # Include optional attributes
    include_metadata=True,
    include_examples=True,
    include_internal=False,  # Exclude internal attributes
    tag_filter=["monitoring", "metrics", "tracing"]
)

try:
    # Retrieve observable attributes for A2A protocol
    a2a_attributes = protocol_layer.get_observable_protocol_attributes(
        protocol_type="a2a",
        attribute_options=a2a_attribute_options
    )
    
    logger.info(f"Retrieved {len(a2a_attributes)} observable attributes for A2A protocol")
    
    # Process the attributes
    for attr in a2a_attributes:
        logger.debug(f"Attribute: {attr.name} ({attr.category.value}, {attr.data_type.value})")
        logger.debug(f"  Path: {attr.path}")
        logger.debug(f"  Description: {attr.description}")
        
        # Configure monitoring for this attribute
        if attr.category == AttributeCategory.PERFORMANCE:
            # Set up performance monitoring for this attribute
            observability_system.monitor_protocol_attribute(
                protocol_type="a2a",
                attribute_name=attr.name,
                attribute_path=attr.path,
                monitoring_options={
                    "alert_threshold": get_threshold_for_attribute(attr),
                    "sampling_rate": attr.sampling_rate
                }
            )
            logger.info(f"Configured performance monitoring for {attr.name}")
        
        # Set up tracing for message attributes
        if attr.category == AttributeCategory.MESSAGE and "tracing" in attr.tags:
            observability_system.add_span_attribute_mapping(
                protocol_type="a2a",
                attribute_name=attr.name,
                attribute_path=attr.path,
                span_attribute_name=f"a2a.{attr.name}"
            )
            logger.info(f"Added span attribute mapping for {attr.name}")
    
    # Use the attributes to configure dashboards
    dashboard_config = generate_protocol_dashboard_config("a2a", a2a_attributes)
    observability_system.create_protocol_dashboard("a2a", dashboard_config)
    
except ProtocolNotSupportedError as e:
    logger.error(f"Protocol not supported for attribute retrieval: {str(e)}")
    # Use default attributes
    a2a_attributes = get_default_a2a_attributes()
    
except AttributeRetrievalError as e:
    logger.error(f"Error retrieving A2A protocol attributes: {str(e)}")
    # Use default attributes
    a2a_attributes = get_default_a2a_attributes()


# Example 2: Retrieving observable attributes for MCP protocol to demonstrate multi-protocol support

# Configure attribute options for MCP protocol
mcp_attribute_options = ProtocolAttributeOptions(
    protocol_version="2.0",
    include_sensitive=False,
    categories=[AttributeCategory.MESSAGE, AttributeCategory.PERFORMANCE, AttributeCategory.CONTENT],
    data_types=[AttributeDataType.STRING, AttributeDataType.NUMBER, AttributeDataType.TIMESTAMP, AttributeDataType.DURATION],
    include_internal=False,
    tag_filter=["capability", "reasoning"]
)

try:
    # Retrieve observable attributes for MCP protocol
    mcp_attributes = protocol_layer.get_observable_protocol_attributes(
        protocol_type="mcp",
        attribute_options=mcp_attribute_options
    )
    
    logger.info(f"Retrieved {len(mcp_attributes)} observable attributes for MCP protocol")
    
    # Filter for sequential thinking specific attributes
    sequential_thinking_attributes = [attr for attr in mcp_attributes 
                                     if "sequential_thinking" in attr.tags]
    
    logger.info(f"Found {len(sequential_thinking_attributes)} attributes for sequential thinking capability")
    
    # Configure monitoring specifically for sequential thinking
    for attr in sequential_thinking_attributes:
        # Set up capability-specific monitoring
        observability_system.monitor_protocol_attribute(
            protocol_type="mcp",
            attribute_name=attr.name,
            attribute_path=attr.path,
            monitoring_options={
                "capability": "sequential_thinking",
                "alert_threshold": get_threshold_for_attribute(attr),
                "sampling_rate": attr.sampling_rate
            }
        )
        
        # Add example values for documentation
        if attr.example_values:
            logger.debug(f"Example values for {attr.name}: {attr.example_values}")
    
    # Create MCP-specific dashboard
    mcp_dashboard_config = generate_protocol_dashboard_config("mcp", mcp_attributes)
    observability_system.create_protocol_dashboard("mcp", mcp_dashboard_config)
    
except Exception as e:
    logger.error(f"Error handling MCP protocol attributes: {str(e)}")
    # Use default attributes
    mcp_attributes = get_default_mcp_attributes()


# Example 3: Comparing observable attributes across protocols

# Get attributes for both A2A and MCP for comparison
a2a_perf_attributes = protocol_layer.get_observable_protocol_attributes(
    protocol_type="a2a",
    attribute_options=ProtocolAttributeOptions(
        categories=[AttributeCategory.PERFORMANCE],
        required_only=True
    )
)

mcp_perf_attributes = protocol_layer.get_observable_protocol_attributes(
    protocol_type="mcp",
    attribute_options=ProtocolAttributeOptions(
        categories=[AttributeCategory.PERFORMANCE],
        required_only=True
    )
)

# Compare performance attributes across protocols
logger.info(f"A2A has {len(a2a_perf_attributes)} required performance attributes")
logger.info(f"MCP has {len(mcp_perf_attributes)} required performance attributes")

# Find common attributes across protocols
a2a_attr_names = {attr.name for attr in a2a_perf_attributes}
mcp_attr_names = {attr.name for attr in mcp_perf_attributes}
common_attr_names = a2a_attr_names.intersection(mcp_attr_names)

logger.info(f"Found {len(common_attr_names)} common performance attributes across protocols")
logger.info(f"Common attributes: {', '.join(common_attr_names)}")

# Create cross-protocol performance dashboard
cross_protocol_dashboard_config = generate_cross_protocol_dashboard_config(
    protocols=["a2a", "mcp"],
    common_attributes=list(common_attr_names)
)

observability_system.create_dashboard(
    name="Cross-Protocol Performance",
    config=cross_protocol_dashboard_config
)
```

#### Events

```python
class ObservabilityConfigurationUpdatedEvent:
    """
    Event emitted when observability configuration is updated.
    """
    event_name: str = "observability_configuration_updated"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")
    
    class Payload:
        configuration_type: str  # Type of configuration updated ("logging", "metrics", "tracing")
        protocol_types: List[str]  # Protocol types affected by the update
        changes: Dict[str, Dict[str, Any]]  # Map of configuration keys to old and new values
        update_reason: str  # Reason for the configuration update
        effective_timestamp: datetime  # When the configuration becomes effective
        update_source: str  # Source of the configuration update ("user", "system", "api")
        requires_restart: bool = False  # Whether the update requires component restart
        transient: bool = False  # Whether the update is transient or permanent
        partial_update: bool = False  # Whether this is a partial update
        metadata: Dict[str, Any] = {}  # Additional metadata about the configuration update
```

**Example Usage:**
```python
# Subscribe to observability configuration updated event
@event_system.subscribe(ObservabilityConfigurationUpdatedEvent.event_name)
def handle_observability_config_update(event: ObservabilityConfigurationUpdatedEvent):
    payload = event.payload
    config_type = payload.configuration_type
    protocol_types = payload.protocol_types
    
    logger.info(f"Observability configuration update received for {config_type}")
    logger.info(f"Affected protocols: {', '.join(protocol_types)}")
    
    # Handle different configuration types
    if config_type == "logging":
        # Update protocol message logging configuration
        for protocol_type in protocol_types:
            # Get protocol-specific changes
            protocol_changes = payload.changes.get(protocol_type, {})
            
            if protocol_changes:
                logger.info(f"Updating logging configuration for {protocol_type} protocol")
                
                # Update log levels if changed
                if "log_level" in protocol_changes:
                    old_level = protocol_changes["log_level"].get("old")
                    new_level = protocol_changes["log_level"].get("new")
                    logger.info(f"Changing log level from {old_level} to {new_level} for {protocol_type}")
                    protocol_logger.set_level(protocol_type, new_level)
                
                # Update sensitive field handling if changed
                if "sensitive_field_handling" in protocol_changes:
                    old_handling = protocol_changes["sensitive_field_handling"].get("old")
                    new_handling = protocol_changes["sensitive_field_handling"].get("new")
                    logger.info(f"Changing sensitive field handling from {old_handling} to {new_handling}")
                    protocol_logger.update_sensitive_field_handling(protocol_type, new_handling)
    
    elif config_type == "metrics":
        # Update protocol metrics configuration
        for protocol_type in protocol_types:
            protocol_changes = payload.changes.get(protocol_type, {})
            
            if protocol_changes:
                logger.info(f"Updating metrics configuration for {protocol_type} protocol")
                
                # Update collection interval if changed
                if "collection_interval_seconds" in protocol_changes:
                    old_interval = protocol_changes["collection_interval_seconds"].get("old")
                    new_interval = protocol_changes["collection_interval_seconds"].get("new")
                    logger.info(f"Changing metrics collection interval from {old_interval}s to {new_interval}s")
                    metrics_collector.set_collection_interval(protocol_type, new_interval)
    
    elif config_type == "tracing":
        # Update protocol tracing configuration
        for protocol_type in protocol_types:
            protocol_changes = payload.changes.get(protocol_type, {})
            
            if protocol_changes:
                logger.info(f"Updating tracing configuration for {protocol_type} protocol")
                
                # Update sampling rate if changed
                if "sampling_rate" in protocol_changes:
                    old_rate = protocol_changes["sampling_rate"].get("old")
                    new_rate = protocol_changes["sampling_rate"].get("new")
                    logger.info(f"Changing trace sampling rate from {old_rate} to {new_rate}")
                    tracer.set_sampling_rate(protocol_type, new_rate)
    
    # Check if restart is required
    if payload.requires_restart:
        logger.warning(f"Configuration update requires component restart")
        
        # Notify other components about required restart
        event_system.emit("component_restart_required", {
            "component": "protocol_observability",
            "reason": payload.update_reason,
            "scheduled_time": datetime.now() + timedelta(minutes=5)  # Schedule restart in 5 minutes
        })
```

```python
class TraceSamplingChangedEvent:
    """
    Event emitted when trace sampling settings change.
    """
    event_name: str = "trace_sampling_changed"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    
    class Payload:
        protocol_type: str  # Protocol type affected by the sampling change
        old_sampling_rate: float  # Previous sampling rate (0.0-1.0)
        new_sampling_rate: float  # New sampling rate (0.0-1.0)
        pattern_specific_rates: Dict[str, float] = {}  # Pattern-specific sampling rates
        operation_specific_rates: Dict[str, float] = {}  # Operation-specific sampling rates
        sampling_strategy: str  # Sampling strategy ("random", "head_based", "tail_based", "adaptive")
        strategy_parameters: Dict[str, Any] = {}  # Strategy-specific parameters
        effective_timestamp: datetime  # When the sampling change becomes effective
        change_reason: str  # Reason for the sampling change
        temporary: bool = False  # Whether the change is temporary
        duration_seconds: Optional[int] = None  # Duration of temporary change in seconds
        dynamic_adjustment: bool = False  # Whether dynamic adjustment is enabled
        metadata: Dict[str, Any] = {}  # Additional metadata about the sampling change
```

**Example Usage:**
```python
# Subscribe to trace sampling changed event
@event_system.subscribe(TraceSamplingChangedEvent.event_name)
def handle_trace_sampling_change(event: TraceSamplingChangedEvent):
    payload = event.payload
    protocol_type = payload.protocol_type
    old_rate = payload.old_sampling_rate
    new_rate = payload.new_sampling_rate
    
    logger.info(f"Trace sampling rate changed for {protocol_type} protocol")
    logger.info(f"Old rate: {old_rate}, New rate: {new_rate}")
    
    # Apply the new sampling rate to the protocol tracer
    protocol_tracer = get_protocol_tracer(protocol_type)
    protocol_tracer.set_base_sampling_rate(new_rate)
    
    # Apply pattern-specific sampling rates if any
    if payload.pattern_specific_rates:
        for pattern, rate in payload.pattern_specific_rates.items():
            logger.info(f"Setting pattern-specific sampling rate for {pattern}: {rate}")
            protocol_tracer.set_pattern_sampling_rate(pattern, rate)
    
    # Apply operation-specific sampling rates if any
    if payload.operation_specific_rates:
        for operation, rate in payload.operation_specific_rates.items():
            logger.info(f"Setting operation-specific sampling rate for {operation}: {rate}")
            protocol_tracer.set_operation_sampling_rate(operation, rate)
    
    # Configure sampling strategy
    strategy = payload.sampling_strategy
    strategy_params = payload.strategy_parameters
    logger.info(f"Setting sampling strategy to {strategy} with parameters: {strategy_params}")
    protocol_tracer.set_sampling_strategy(strategy, strategy_params)
    
    # Handle temporary changes
    if payload.temporary and payload.duration_seconds:
        # Schedule a task to revert the sampling rate after the specified duration
        duration_seconds = payload.duration_seconds
        logger.info(f"Temporary sampling change will be reverted after {duration_seconds} seconds")
        
        # Set up a scheduled task to revert the change
        scheduler.schedule_task(
            task_name=f"revert_sampling_rate_{protocol_type}_{event.event_id}",
            execution_time=datetime.now() + timedelta(seconds=duration_seconds),
            task_function=revert_sampling_rate,
            task_args={
                "protocol_type": protocol_type,
                "sampling_rate": old_rate,
                "event_id": event.event_id
            }
        )
    
    # Update metrics to track sampling rate changes
    metrics.gauge(
        name="trace_sampling_rate",
        value=new_rate,
        tags=[f"protocol:{protocol_type}", f"reason:{payload.change_reason}"]
    )
    
    # Log the change for auditing
    audit_logger.info(
        message="Trace sampling rate changed",
        context={
            "protocol_type": protocol_type,
            "old_rate": old_rate,
            "new_rate": new_rate,
            "reason": payload.change_reason,
            "temporary": payload.temporary,
            "duration_seconds": payload.duration_seconds,
            "changed_by": payload.metadata.get("changed_by", "system")
        }
    )

# Helper function to revert sampling rate changes
def revert_sampling_rate(protocol_type: str, sampling_rate: float, event_id: str):
    logger.info(f"Reverting temporary sampling rate change for {protocol_type} protocol")
    
    # Get the current tracer
    protocol_tracer = get_protocol_tracer(protocol_type)
    
    # Set the sampling rate back to the original value
    protocol_tracer.set_base_sampling_rate(sampling_rate)
    
    # Clear any pattern-specific and operation-specific sampling rates
    protocol_tracer.clear_pattern_sampling_rates()
    protocol_tracer.clear_operation_sampling_rates()
    
    # Reset the sampling strategy to default
    protocol_tracer.set_sampling_strategy("random", {})
    
    # Log the reversion for auditing
    audit_logger.info(
        message="Temporary trace sampling rate reverted",
        context={
            "protocol_type": protocol_type,
            "sampling_rate": sampling_rate,
            "original_event_id": event_id
        }
    )
    
    # Update metrics to reflect the reversion
    metrics.gauge(
        name="trace_sampling_rate",
        value=sampling_rate,
        tags=[f"protocol:{protocol_type}", "reason:temporary_reversion"]
    )
    
    # Emit an event to notify about the reversion
    event_system.emit("trace_sampling_reverted", {
        "protocol_type": protocol_type,
        "sampling_rate": sampling_rate,
        "original_event_id": event_id,
        "reversion_time": datetime.now()
    })
```

```python
class ProtocolObservabilityCapabilityDiscoveredEvent:
    """
    Event emitted when new observability capabilities are discovered for a protocol.
    """
    event_name: str = "protocol_observability_capability_discovered"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    
    class Payload:
        protocol_type: str  # Protocol type with new observability capabilities
        protocol_version: str  # Version of the protocol
        capability_type: str  # Type of observability capability ("metrics", "tracing", "logging")
        capabilities: List[Dict[str, Any]]  # List of discovered capabilities
        auto_enabled: bool  # Whether the capabilities are automatically enabled
        discovery_method: str  # How the capabilities were discovered
        compatibility_level: str  # Compatibility level with the observability system
        metadata: Dict[str, Any] = {}  # Additional metadata about the discovered capabilities
```

**Example Usage:**
```python
# Subscribe to protocol observability capability discovered event
@event_system.subscribe(ProtocolObservabilityCapabilityDiscoveredEvent.event_name)
def handle_capability_discovery(event: ProtocolObservabilityCapabilityDiscoveredEvent):
    payload = event.payload
    protocol_type = payload.protocol_type
    protocol_version = payload.protocol_version
    capability_type = payload.capability_type
    capabilities = payload.capabilities
    
    logger.info(f"New {capability_type} observability capabilities discovered for {protocol_type} v{protocol_version}")
    logger.info(f"Discovered {len(capabilities)} capabilities")
    
    # Register the capabilities in the observability system
    for capability in capabilities:
        capability_name = capability.get("name")
        capability_description = capability.get("description")
        capability_attributes = capability.get("attributes", [])
        
        logger.info(f"Registering capability: {capability_name} - {capability_description}")
        
        # Register the capability based on its type
        if capability_type == "metrics":
            # Register metrics capabilities
            for attr in capability_attributes:
                metric_name = attr.get("name")
                metric_type = attr.get("type")
                metric_description = attr.get("description")
                metric_unit = attr.get("unit")
                metric_labels = attr.get("labels", [])
                
                logger.info(f"Registering metric: {metric_name} ({metric_type})")
                
                # Register the metric in the metrics registry
                metrics_registry.register_metric(
                    protocol_type=protocol_type,
                    metric_name=metric_name,
                    metric_type=metric_type,
                    description=metric_description,
                    unit=metric_unit,
                    labels=metric_labels,
                    auto_enable=payload.auto_enabled
                )
        
        elif capability_type == "tracing":
            # Register tracing capabilities
            for attr in capability_attributes:
                span_name = attr.get("name")
                span_attributes = attr.get("attributes", [])
                sampling_priority = attr.get("sampling_priority", "normal")
                
                logger.info(f"Registering tracing span: {span_name}")
                
                # Register the span in the tracing registry
                tracing_registry.register_span(
                    protocol_type=protocol_type,
                    span_name=span_name,
                    attributes=span_attributes,
                    sampling_priority=sampling_priority,
                    auto_enable=payload.auto_enabled
                )
        
        elif capability_type == "logging":
            # Register logging capabilities
            for attr in capability_attributes:
                log_event = attr.get("name")
                log_level = attr.get("level", "INFO")
                sensitive_fields = attr.get("sensitive_fields", [])
                
                logger.info(f"Registering log event: {log_event} (level: {log_level})")
                
                # Register the log event in the logging registry
                logging_registry.register_log_event(
                    protocol_type=protocol_type,
                    event_name=log_event,
                    level=log_level,
                    sensitive_fields=sensitive_fields,
                    auto_enable=payload.auto_enabled
                )
    
    # Update the capabilities dashboard
    if payload.auto_enabled:
        observability_system.update_capabilities_dashboard(
            protocol_type=protocol_type,
            capability_type=capability_type,
            capabilities=capabilities
        )
        
        logger.info("Updated capabilities dashboard with newly discovered capabilities")
    
    # Notify admins about the discovery if configured to do so
    if observability_config.get("notify_on_capability_discovery", False):
        notification_service.notify_admins(
            title=f"New {capability_type} observability capabilities discovered",
            message=f"Discovered {len(capabilities)} new {capability_type} capabilities for {protocol_type} v{protocol_version}",
            severity="info",
            context={
                "protocol_type": protocol_type,
                "protocol_version": protocol_version,
                "capability_type": capability_type,
                "capabilities": [cap.get("name") for cap in capabilities],
                "discovery_method": payload.discovery_method,
                "auto_enabled": payload.auto_enabled
            }
        )
```

## Data Flows

### Protocol-Agnostic Observability Architecture

OpenMAS implements a protocol-agnostic observability architecture that maintains a clean separation between protocol-specific telemetry collection and the reasoning engine monitoring. This ensures that the protocol layer observability maintains the framework's reasoning agnostic design.

```
┌────────────────────────────────────────────────────────────────────┐
│                      Observability System                          │
│                                                                    │
│  ┌──────────────────┐    ┌───────────────┐    ┌────────────────┐   │
│  │   Logging System │    │ Metrics System│    │ Tracing System │   │
│  └──────────────────┘    └───────────────┘    └────────────────┘   │
│             ▲                     ▲                    ▲            │
└─────────────┼─────────────────────┼────────────────────┼────────────┘
              │                     │                    │
              │   Protocol-Specific │                    │
              │      Telemetry      │                    │
              │                     │                    │
┌─────────────┼─────────────────────┼────────────────────┼────────────┐
│  ┌──────────▼──────────┐ ┌────────▼────────┐ ┌────────▼────────┐   │
│  │ Protocol-Specific   │ │ Protocol-Specific│ │Protocol-Specific│   │
│  │ Logging Adapters    │ │ Metrics Collectors│ │Tracing Providers│   │
│  └─────────────────────┘ └─────────────────┘ └─────────────────┘   │
│                                                                    │
│                          Protocol Layer                            │
└────────────────────────────────────────────────────────────────────┘
      ▲                    ▲                       ▲
      │                    │                       │
      │                    │                       │
┌─────▼────────┐    ┌─────▼────────┐      ┌───────▼─────────┐
│   A2A         │    │     MCP      │      │  Other Protocol  │
│ Communicator  │    │ Communicator │  ... │  Communicators   │
└──────────────┘    └──────────────┘      └─────────────────┘
```

### Data Flow Directions

#### 1. Protocol Layer → Observability System

##### Message Telemetry Flow
```python
class ProtocolMessageTelemetryFlow:
    """
    Defines how protocol message data flows from protocol layer to observability system.
    """
    # Protocol-specific data extraction
    protocol_message: Dict[str, Any]  # Raw protocol message
    protocol_type: str  # Protocol type identifier (e.g., "a2a", "mcp")
    message_direction: MessageDirection  # INCOMING or OUTGOING
    timestamp: datetime  # When the message was received/sent
    session_id: str  # Session identifier
    protocol_attributes: Dict[str, Any]  # Protocol-specific attributes
    message_size_bytes: int  # Size of the message in bytes
    
    # Protocol-agnostic observability data
    observability_context: Dict[str, Any]  # Context for observability
    logging_level: str  # Level for logging
    metric_labels: Dict[str, str]  # Labels for metrics
    trace_context: Optional[SpanContext]  # Context for distributed tracing
    sensitive_data_handling: str  # How to handle sensitive data
```

**Example: Protocol-Specific to Protocol-Agnostic Transformation**

```python
# Example for A2A protocol
def process_a2a_message_for_observability(a2a_message, direction):
    # Extract A2A-specific attributes
    message_id = a2a_message.get("messageId", "unknown")
    agent_id = a2a_message.get("agent", {}).get("id", "unknown")
    content_type = a2a_message.get("contentType", "unknown")
    turn_id = a2a_message.get("turnId", "unknown")
    task_id = a2a_message.get("taskId", "unknown")
    
    # Transform into protocol-agnostic telemetry
    telemetry = ProtocolMessageTelemetryFlow(
        protocol_message=a2a_message,
        protocol_type="a2a",
        message_direction=direction,
        timestamp=datetime.now(),
        session_id=task_id,  # A2A uses taskId as session identifier
        protocol_attributes={
            "agent_id": agent_id,
            "message_id": message_id,
            "content_type": content_type,
            "turn_id": turn_id
        },
        message_size_bytes=len(json.dumps(a2a_message)),
        observability_context={
            "protocol": "a2a",
            "message_type": determine_a2a_message_type(a2a_message),
            "component": "a2a_communicator"
        },
        logging_level="INFO",
        metric_labels={
            "protocol": "a2a",
            "agent_id": agent_id,
            "content_type": content_type,
            "direction": direction.value
        },
        trace_context=extract_trace_context("a2a", a2a_message),
        sensitive_data_handling="mask"
    )
    
    # Send to observability system
    observability_system.log_protocol_message(
        protocol_type=telemetry.protocol_type,
        direction=telemetry.message_direction,
        message_data=ProtocolMessageData(
            message=telemetry.protocol_message,
            attributes=telemetry.protocol_attributes
        ),
        logging_options=ProtocolLoggingOptions(
            level=telemetry.logging_level,
            sensitive_data_handling=telemetry.sensitive_data_handling
        )
    )
    
    # Record metrics
    observability_system.record_protocol_metric(
        protocol_type=telemetry.protocol_type,
        metric_name="message_size_bytes",
        value=telemetry.message_size_bytes,
        labels=telemetry.metric_labels
    )
    
    # Start span if not already in a trace
    if not telemetry.trace_context:
        span = observability_system.start_protocol_span(
            protocol_type=telemetry.protocol_type,
            operation_name=f"{direction.value.lower()}_message",
            span_options=ProtocolSpanOptions(
                attributes={
                    "message_id": message_id,
                    "agent_id": agent_id,
                    "content_type": content_type
                }
            )
        )
    else:
        # Continue existing trace
        span = observability_system.start_protocol_span(
            protocol_type=telemetry.protocol_type,
            operation_name=f"{direction.value.lower()}_message",
            parent_context=telemetry.trace_context
        )
    
    return span

# Example for MCP protocol
def process_mcp_message_for_observability(mcp_message, direction):
    # Extract MCP-specific attributes
    message_id = mcp_message.get("id", "unknown")
    request_id = mcp_message.get("requestId", "unknown")
    capability = mcp_message.get("capability", "unknown")
    timestamp = mcp_message.get("timestamp", datetime.now())
    
    # Check if this is a tool call/result
    is_tool_call = "toolCall" in mcp_message
    is_tool_result = "toolResult" in mcp_message
    
    # Transform into protocol-agnostic telemetry
    telemetry = ProtocolMessageTelemetryFlow(
        protocol_message=mcp_message,
        protocol_type="mcp",
        message_direction=direction,
        timestamp=timestamp,
        session_id=request_id,  # MCP uses requestId as session identifier
        protocol_attributes={
            "message_id": message_id,
            "capability": capability,
            "is_tool_call": is_tool_call,
            "is_tool_result": is_tool_result,
            "tool_name": mcp_message.get("toolCall", {}).get("name") if is_tool_call else None,
        },
        message_size_bytes=len(json.dumps(mcp_message)),
        observability_context={
            "protocol": "mcp",
            "message_type": determine_mcp_message_type(mcp_message),
            "component": "mcp_communicator"
        },
        logging_level="INFO",
        metric_labels={
            "protocol": "mcp",
            "capability": capability,
            "message_type": "tool_call" if is_tool_call else "tool_result" if is_tool_result else "other",
            "direction": direction.value
        },
        trace_context=extract_trace_context("mcp", mcp_message),
        sensitive_data_handling="mask"
    )
    
    # Send to observability system
    observability_system.log_protocol_message(
        protocol_type=telemetry.protocol_type,
        direction=telemetry.message_direction,
        message_data=ProtocolMessageData(
            message=telemetry.protocol_message,
            attributes=telemetry.protocol_attributes
        ),
        logging_options=ProtocolLoggingOptions(
            level=telemetry.logging_level,
            sensitive_data_handling=telemetry.sensitive_data_handling
        )
    )
    
    # Record metrics
    observability_system.record_protocol_metric(
        protocol_type=telemetry.protocol_type,
        metric_name="message_size_bytes",
        value=telemetry.message_size_bytes,
        labels=telemetry.metric_labels
    )
    
    # For tool calls, record specific metrics
    if is_tool_call:
        observability_system.record_protocol_metric(
            protocol_type=telemetry.protocol_type,
            metric_name="tool_call_count",
            value=1,
            labels={**telemetry.metric_labels, "tool_name": telemetry.protocol_attributes["tool_name"]}
        )
    
    # Start span if not already in a trace
    if not telemetry.trace_context:
        span = observability_system.start_protocol_span(
            protocol_type=telemetry.protocol_type,
            operation_name=f"{direction.value.lower()}_message",
            span_options=ProtocolSpanOptions(
                attributes={
                    "message_id": message_id,
                    "capability": capability,
                    "is_tool_call": is_tool_call,
                    "is_tool_result": is_tool_result
                }
            )
        )
    else:
        # Continue existing trace
        span = observability_system.start_protocol_span(
            protocol_type=telemetry.protocol_type,
            operation_name=f"{direction.value.lower()}_message",
            parent_context=telemetry.trace_context
        )
    
    return span
```

##### Performance Metrics Flow

```python
def collect_protocol_performance_metrics(protocol_type: str):
    """
    Collects performance metrics for a specific protocol and
    sends them to the observability system.
    """
    # Get the protocol adapter
    adapter = protocol_registry.get_adapter(protocol_type)
    
    # Collect protocol-specific metrics
    metrics_data = adapter.collect_performance_metrics()
    
    # Record each metric in the observability system
    for metric_name, metric_value in metrics_data.items():
        labels = {
            "protocol": protocol_type,
            "component": "protocol_adapter"
        }
        
        observability_system.record_protocol_metric(
            protocol_type=protocol_type,
            metric_name=metric_name,
            value=metric_value,
            labels=labels
        )
        
    # Log collection completion
    logger.debug(f"Collected {len(metrics_data)} performance metrics for {protocol_type} protocol")
    
    return len(metrics_data)
```

#### 2. Observability System → Protocol Layer

##### Configuration Updates Flow

```python
def apply_protocol_observability_configuration(protocol_type: str, config: Dict[str, Any]):
    """
    Applies observability configuration updates to a specific protocol.
    """
    # Get the current configuration
    current_config = observability_system.get_protocol_observability_config(protocol_type)
    
    # Track changes for event emission
    changes = {}
    
    # Apply configuration updates
    for key, new_value in config.items():
        old_value = current_config.get(key)
        if old_value != new_value:
            changes[key] = {"old": old_value, "new": new_value}
            current_config[key] = new_value
    
    # If there are changes, save the updated configuration
    if changes:
        observability_system.set_protocol_observability_config(protocol_type, current_config)
        
        # Emit configuration updated event
        event_system.emit(
            event_name="observability_configuration_updated",
            payload=ObservabilityConfigurationUpdatedEvent.Payload(
                configuration_type="protocol",
                protocol_types=[protocol_type],
                changes={protocol_type: changes},
                update_reason="admin_configuration_update",
                effective_timestamp=datetime.now(),
                update_source="api",
                requires_restart=any(key in ["restart_required_setting1", "restart_required_setting2"] for key in changes)
            )
        )
        
        logger.info(f"Applied {len(changes)} configuration updates to {protocol_type} protocol observability")
        
        # Return the applied changes
        return changes
    else:
        logger.info(f"No configuration changes needed for {protocol_type} protocol observability")
        return {}
```

##### Sampling Adjustments Flow

```python
def adjust_protocol_sampling_rates(traffic_metrics: Dict[str, Dict[str, float]]):
    """
    Dynamically adjusts sampling rates for protocols based on traffic metrics.
    """
    for protocol_type, metrics in traffic_metrics.items():
        current_rate = observability_system.get_protocol_sampling_rate(protocol_type)
        message_rate = metrics.get("messages_per_second", 0)
        error_rate = metrics.get("error_rate", 0)
        
        # Calculate new sampling rate based on traffic and error rates
        new_rate = calculate_optimal_sampling_rate(
            protocol_type=protocol_type,
            message_rate=message_rate,
            error_rate=error_rate,
            current_rate=current_rate
        )
        
        # Only update if the rate change is significant
        if abs(new_rate - current_rate) > 0.05:  # 5% threshold for change
            logger.info(f"Adjusting sampling rate for {protocol_type} from {current_rate} to {new_rate}")
            
            # Apply the new sampling rate
            observability_system.set_protocol_sampling_rate(protocol_type, new_rate)
            
            # Emit trace sampling changed event
            event_system.emit(
                event_name="trace_sampling_changed",
                payload=TraceSamplingChangedEvent.Payload(
                    protocol_type=protocol_type,
                    old_sampling_rate=current_rate,
                    new_sampling_rate=new_rate,
                    sampling_strategy="adaptive",
                    strategy_parameters={
                        "message_rate": message_rate,
                        "error_rate": error_rate
                    },
                    effective_timestamp=datetime.now(),
                    change_reason="traffic_based_adjustment",
                    dynamic_adjustment=True
                )
            )
```

### Protocol-Specific to Reasoning-Agnostic Observability

A key aspect of OpenMAS's reasoning agnostic architecture is the separation between protocol-specific monitoring and reasoning engine monitoring. This allows different reasoning approaches to be used with various communication protocols without tight coupling.

```python
# Example: Separating protocol observability from reasoning engine observability

def handle_incoming_message(protocol_type: str, message: Dict[str, Any]):
    # Step 1: Protocol-specific observability (handles the "body")
    protocol_span = None
    if protocol_type == "a2a":
        protocol_span = process_a2a_message_for_observability(message, MessageDirection.INCOMING)
    elif protocol_type == "mcp":
        protocol_span = process_mcp_message_for_observability(message, MessageDirection.INCOMING)
    else:
        # Generic protocol handling
        protocol_span = observability_system.start_protocol_span(
            protocol_type=protocol_type,
            operation_name="incoming_message"
        )
    
    try:
        # Step 2: Protocol-agnostic message conversion (bridge layer)
        internal_message = protocol_adapter.to_internal_format(protocol_type, message)
        
        # Step 3: Reasoning engine observability (handles the "brain")
        # This is deliberately separate from protocol observability to maintain reasoning agnosticism
        reasoning_span = observability_system.start_reasoning_span(
            reasoning_type=agent_config.reasoning_engine_type,  # e.g. "llm", "rule_based", "bdi", "hybrid"
            operation_name="process_message",
            parent_context=protocol_span.context if protocol_span else None
        )
        
        try:
            # Process the message with the appropriate reasoning engine
            response_data = reasoning_engine.process_message(internal_message)
            
            # Record reasoning-specific metrics
            observability_system.record_reasoning_metric(
                reasoning_type=agent_config.reasoning_engine_type,
                metric_name="processing_time_ms",
                value=reasoning_span.elapsed_time_ms,
                labels={
                    "operation": "process_message",
                    "message_type": internal_message.type
                }
            )
            
            # Step 4: Convert response back to protocol-specific format
            protocol_response = protocol_adapter.from_internal_format(protocol_type, response_data)
            
            # Step 5: Protocol-specific observability for the response
            if protocol_type == "a2a":
                process_a2a_message_for_observability(protocol_response, MessageDirection.OUTGOING)
            elif protocol_type == "mcp":
                process_mcp_message_for_observability(protocol_response, MessageDirection.OUTGOING)
            
            return protocol_response
            
        finally:
            # End the reasoning span
            reasoning_span.end()
    
    finally:
        # End the protocol span
        if protocol_span:
            protocol_span.end()
```

This architecture ensures that:

1. **Protocol Communication is Observable**: All protocol-specific communication is properly monitored, regardless of the reasoning engine used.

2. **Reasoning Engines are Observable**: The reasoning process itself can be monitored independently of the communication protocol.

3. **Reasoning Agnosticism is Maintained**: By separating protocol and reasoning observability, different reasoning approaches can be used without changing the protocol layer observability.

4. **End-to-End Tracing is Possible**: By linking protocol spans and reasoning spans, full end-to-end traces can be constructed across the entire system.

5. **Multi-Protocol Support**: The system can handle multiple protocols simultaneously while maintaining a consistent observability approach.

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
observability:
  protocol_monitoring:
    message_logging:
      enabled: true
      log_level: "INFO"
      content_logging:
        enabled: true
        max_size_bytes: 1024
        sensitive_field_handling: "mask"  # mask, omit, hash
      sensitive_fields:
        - "credentials"
        - "password"
        - "api_key"
        - "token"
    
    metrics:
      enabled: true
      collection_interval_seconds: 15
      metrics:
        - name: "protocol_message_count"
          type: "counter"
          description: "Number of protocol messages processed"
          labels: ["protocol", "direction", "status"]
        
        - name: "protocol_message_size"
          type: "histogram"
          description: "Size of protocol messages in bytes"
          labels: ["protocol", "direction"]
          buckets: [100, 1000, 10000, 100000, 1000000]
        
        - name: "protocol_processing_time"
          type: "histogram"
          description: "Time to process protocol messages"
          labels: ["protocol", "message_type"]
          buckets: [1, 10, 50, 100, 500, 1000, 5000]
    
    tracing:
      enabled: true
      sampling_rate: 0.1  # 10% of transactions
      protocol_specific_sampling:
        a2a: 0.5  # 50% of A2A traffic
        mcp: 0.5  # 50% of MCP traffic
        http: 0.1  # 10% of HTTP traffic
      span_attributes:
        - "protocol.type"
        - "protocol.version"
        - "message.id"
        - "message.type"
        - "agent.id"

protocol_layer:
  observability:
    enabled: true
    protocol_specific:
      a2a:
        message_logging:
          enabled: true
          sensitive_fields:
            - "authorization"
            - "agent_card.security"
        metrics:
          enabled: true
          custom_metrics:
            - name: "a2a_tool_invocation_count"
              type: "counter"
              labels: ["tool_name", "status"]
      
      mcp:
        message_logging:
          enabled: true
          sensitive_fields:
            - "x-mcp-api-key"
        metrics:
          enabled: true
          custom_metrics:
            - name: "mcp_capability_invocation_count"
              type: "counter"
              labels: ["capability_name", "status"]
```

## Error Handling

1. **Logging Failures**:
   - Graceful handling of logging failures to prevent impact on core functionality
   - Local buffering of log messages if central logging is unavailable
   - Circuit breaker pattern to prevent cascading failures

2. **Metric Collection Issues**:
   - Sampling of metrics under high load
   - Aggregation of metrics to reduce cardinality issues
   - Fallback to basic metrics if detailed collection fails

3. **Tracing Propagation Errors**:
   - Graceful degradation when trace context is invalid
   - Creation of new trace context when extraction fails
   - Monitoring of trace context propagation failures

## Extension Points

1. **Protocol-Specific Monitors**:
   - Custom monitoring for specific protocols
   - ProtocolMonitor interface:
     ```python
     class ProtocolMonitor:
         def initialize(self, config: Dict[str, Any]) → bool:
             # Initialize monitor with configuration
             pass
         
         def monitor_message(self, direction: MessageDirection, message: Any) → None:
             # Monitor protocol-specific message
             pass
             
         def collect_metrics(self) → List[Metric]:
             # Collect protocol-specific metrics
             pass
     ```

2. **Custom Protocol Observers**:
   - Protocol-specific observation extensions
   - Example configuration:
     ```yaml
     protocol_layer:
       observability:
         extensions:
           - name: "a2a_conversation_quality"
             implementation_class: "A2AConversationQualityMonitor"
             config:
               quality_metrics:
                 - "response_relevance"
                 - "reasoning_quality"
                 - "tool_use_efficiency"
     ```

## Notes on Multi-Protocol Design

The Protocol Layer ↔ Observability System interface supports OpenMAS's multi-protocol design by:

- Providing protocol-specific monitoring adapters
- Supporting consistent observability across different protocols
- Enabling correlation of interactions spanning multiple protocols
- Tracking protocol-specific metrics while maintaining common observability concepts

## Notes on A2A and MCP Protocol Observability

This interface specifically addresses both Google's A2A protocol and the Model Context Protocol (MCP):

### A2A Protocol Observability

A2A protocol has specific observability characteristics:

1. **Tool Usage Monitoring**: Tracking of tool invocations and their outcomes
2. **Agent Card Monitoring**: Monitoring of agent card interactions
3. **Conversation Flow Tracking**: Tracing the flow of conversation steps

Example A2A-specific metrics:
```yaml
metrics:
  - name: "a2a_tool_invocation_count"
    type: "counter"
    labels: ["tool_name", "status"]
  
  - name: "a2a_agent_card_validation_time"
    type: "histogram"
    labels: ["validation_result"]
    buckets: [1, 5, 10, 50, 100]
```

### MCP Protocol Observability

MCP protocol has specific observability characteristics:

1. **Server Capability Monitoring**: Tracking of server capability usage
2. **Request Parameter Analysis**: Monitoring of parameter patterns
3. **Response Quality Metrics**: Tracking response quality markers

Example MCP-specific metrics:
```yaml
metrics:
  - name: "mcp_capability_invocation_count"
    type: "counter"
    labels: ["capability_name", "status"]
  
  - name: "mcp_sequential_thinking_quality"
    type: "gauge"
    labels: ["agent_id"]
```

## Notes on Reasoning Agnosticism

The Protocol Layer ↔ Observability System interface supports OpenMAS's reasoning agnostic architecture by:

- Separating communication observability (protocol layer) from reasoning observability
- Providing correlation identifiers to link communication and reasoning operations
- Supporting monitoring of different reasoning approaches while maintaining protocol separation
- Enabling comprehensive observability without tying protocols to specific reasoning methods

This maintains the "body-brain" separation central to OpenMAS's design while ensuring both components can be effectively monitored.

## Complete Examples

### Example 1: Cross-Protocol Message Observability

This example demonstrates how to implement protocol-agnostic observability that works consistently across multiple protocols (A2A, MCP, HTTP) while maintaining OpenMAS's reasoning agnosticism.

```python
class CrossProtocolObservabilityManager:
    """
    Manages observability across multiple protocols while maintaining reasoning agnosticism.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.protocol_adapters = {}
        self.initialize_protocol_adapters()
        self.logger = logging.getLogger("cross_protocol_observability")
        
    def initialize_protocol_adapters(self):
        """
        Initialize protocol-specific adapters for observability.
        """
        for protocol_type, protocol_config in self.config.get("protocols", {}).items():
            if protocol_config.get("enabled", True):
                adapter_class = self._get_adapter_class_for_protocol(protocol_type)
                self.protocol_adapters[protocol_type] = adapter_class(protocol_config)
                self.logger.info(f"Initialized observability adapter for {protocol_type} protocol")
    
    def _get_adapter_class_for_protocol(self, protocol_type: str) -> Type:
        """
        Get the appropriate adapter class for the protocol type.
        """
        protocol_adapter_map = {
            "a2a": A2AObservabilityAdapter,
            "mcp": MCPObservabilityAdapter,
            "http": HTTPObservabilityAdapter,
            # Additional protocols can be added here
        }
        
        # Return specific adapter if available, otherwise use generic
        return protocol_adapter_map.get(protocol_type, GenericProtocolObservabilityAdapter)
    
    def observe_message(self, protocol_type: str, message: Dict[str, Any], 
                       direction: MessageDirection, context: Optional[Dict[str, Any]] = None):
        """
        Observe a protocol message in a protocol-agnostic way.
        """
        # Check if we have an adapter for this protocol
        if protocol_type in self.protocol_adapters:
            adapter = self.protocol_adapters[protocol_type]
            
            # Protocol-specific observation through the adapter
            observability_data = adapter.process_message(message, direction, context)
            
            # Log the message using the adapter's protocol-specific logic
            logging_result = adapter.log_message(observability_data)
            
            # Record protocol-specific metrics
            metrics_result = adapter.record_metrics(observability_data)
            
            # Handle tracing
            span = None
            if observability_data.should_trace:
                span = adapter.start_span(observability_data)
            
            return {
                "logging_result": logging_result,
                "metrics_result": metrics_result,
                "span": span,
                "observability_data": observability_data
            }
        else:
            self.logger.warning(f"No observability adapter for protocol {protocol_type}")
            return None
    
    def end_observation(self, protocol_type: str, observation_result: Dict[str, Any], 
                       outcome: Dict[str, Any]):
        """
        End observation for a protocol operation.
        """
        if not observation_result:
            return
            
        adapter = self.protocol_adapters.get(protocol_type)
        if not adapter:
            return
            
        # End span if one was started
        if "span" in observation_result and observation_result["span"]:
            adapter.end_span(observation_result["span"], outcome)
            
        # Record outcome metrics
        if "observability_data" in observation_result:
            adapter.record_outcome_metrics(observation_result["observability_data"], outcome)

# Protocol-specific adapters
class A2AObservabilityAdapter:
    """
    Adapter for A2A protocol observability.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("a2a_observability_adapter")
        self.sensitive_fields = config.get("sensitive_fields", ["credentials", "password", "token"])
        
    def process_message(self, message: Dict[str, Any], direction: MessageDirection, 
                        context: Optional[Dict[str, Any]] = None) -> ProtocolObservabilityData:
        """
        Process an A2A message for observability.
        """
        # Extract A2A-specific fields
        message_id = message.get("messageId", "unknown")
        agent_id = message.get("agent", {}).get("id", "unknown")
        turn_id = message.get("turnId", "unknown")
        task_id = message.get("taskId", "unknown")
        content_type = message.get("contentType", "unknown")
        
        # Create standardized observability data
        observability_data = ProtocolObservabilityData(
            protocol_type="a2a",
            direction=direction,
            message_id=message_id,
            protocol_specific_ids={
                "agent_id": agent_id,
                "turn_id": turn_id,
                "task_id": task_id
            },
            message=message,
            message_type=self._determine_message_type(message),
            message_size_bytes=len(json.dumps(message)),
            metadata={
                "content_type": content_type,
                "has_tool_calls": self._has_tool_calls(message)
            },
            timestamp=datetime.now(),
            context=context or {},
            should_trace=self._should_trace(message, context)
        )
        
        return observability_data
    
    def _determine_message_type(self, message: Dict[str, Any]) -> str:
        """
        Determine the A2A message type.
        """
        if "agentResponse" in message:
            return "agent_response"
        elif "userMessage" in message:
            return "user_message"
        elif "functionCall" in message:
            return "function_call"
        elif "functionResponse" in message:
            return "function_response"
        else:
            return "other"
    
    def _has_tool_calls(self, message: Dict[str, Any]) -> bool:
        """
        Check if the A2A message contains tool calls.
        """
        return "functionCall" in message or "functionResponse" in message
    
    def _should_trace(self, message: Dict[str, Any], context: Optional[Dict[str, Any]]) -> bool:
        """
        Determine if this message should be traced.
        """
        # Implement trace sampling logic based on message content and sampling rate
        base_sampling_rate = self.config.get("tracing", {}).get("sampling_rate", 0.1)
        
        # Always trace session start/end
        if message.get("type") in ["START_SESSION", "END_SESSION"]:
            return True
            
        # Always trace errors
        if "error" in message:
            return True
            
        # Apply sampling rate
        return random.random() < base_sampling_rate
    
    def sanitize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize sensitive data in the message.
        """
        sanitized = copy.deepcopy(message)
        
        # Apply jsonpath-based sanitization for known sensitive fields
        for sensitive_path in self.sensitive_fields:
            jsonpath_expr = parse(sensitive_path)
            for match in jsonpath_expr.find(sanitized):
                match.value = "[REDACTED]"
        
        return sanitized
    
    def log_message(self, observability_data: ProtocolObservabilityData) -> LoggingResult:
        """
        Log an A2A message.
        """
        # Sanitize the message
        sanitized_message = self.sanitize_message(observability_data.message)
        
        # Create logging options
        logging_options = ProtocolLoggingOptions(
            level="INFO" if observability_data.metadata.get("is_error") else "DEBUG",
            sensitive_data_handling="mask",
            include_context=True,
            message_format="json"
        )
        
        # Log the message using the observability system
        return observability_system.log_protocol_message(
            protocol_type=observability_data.protocol_type,
            direction=observability_data.direction,
            message_data=ProtocolMessageData(
                message=sanitized_message,
                attributes={
                    "message_id": observability_data.message_id,
                    "message_type": observability_data.message_type,
                    **observability_data.protocol_specific_ids,
                    **observability_data.metadata
                }
            ),
            logging_options=logging_options
        )
    
    def record_metrics(self, observability_data: ProtocolObservabilityData) -> List[MetricRecordingResult]:
        """
        Record metrics for an A2A message.
        """
        results = []
        
        # Common labels for all metrics
        common_labels = {
            "protocol": "a2a",
            "direction": observability_data.direction.value,
            "message_type": observability_data.message_type,
            "agent_id": observability_data.protocol_specific_ids.get("agent_id", "unknown")
        }
        
        # Record message count
        results.append(observability_system.record_protocol_metric(
            protocol_type="a2a",
            metric_name="message_count",
            value=1,
            labels=common_labels
        ))
        
        # Record message size
        results.append(observability_system.record_protocol_metric(
            protocol_type="a2a",
            metric_name="message_size_bytes",
            value=observability_data.message_size_bytes,
            labels=common_labels
        ))
        
        # Record tool-specific metrics if applicable
        if observability_data.metadata.get("has_tool_calls"):
            results.append(observability_system.record_protocol_metric(
                protocol_type="a2a",
                metric_name="tool_call_count",
                value=1,
                labels={
                    **common_labels,
                    "tool_name": self._extract_tool_name(observability_data.message)
                }
            ))
        
        return results
    
    def _extract_tool_name(self, message: Dict[str, Any]) -> str:
        """
        Extract tool name from A2A message.
        """
        if "functionCall" in message:
            return message["functionCall"].get("name", "unknown")
        return "unknown"
    
    def start_span(self, observability_data: ProtocolObservabilityData) -> ProtocolSpan:
        """
        Start a tracing span for an A2A message.
        """
        # Extract trace context if present in the message
        parent_context = None
        if observability_data.direction == MessageDirection.INCOMING:
            parent_context = protocol_layer.extract_trace_context(
                protocol_type="a2a",
                request_data=observability_data.message
            )
        
        # Define span options
        span_options = ProtocolSpanOptions(
            kind=SpanKind.SERVER if observability_data.direction == MessageDirection.INCOMING else SpanKind.CLIENT,
            attributes={
                "protocol.type": "a2a",
                "message.id": observability_data.message_id,
                "message.type": observability_data.message_type,
                "agent.id": observability_data.protocol_specific_ids.get("agent_id"),
                "task.id": observability_data.protocol_specific_ids.get("task_id"),
                "turn.id": observability_data.protocol_specific_ids.get("turn_id"),
                "message.has_tool_calls": observability_data.metadata.get("has_tool_calls", False)
            },
            links=[],
            events=[],
            start_timestamp=observability_data.timestamp
        )
        
        # Start the span
        return observability_system.start_protocol_span(
            protocol_type="a2a",
            operation_name=f"{observability_data.direction.value.lower()}_{observability_data.message_type}",
            parent_context=parent_context,
            span_options=span_options
        )
    
    def end_span(self, span: ProtocolSpan, outcome: Dict[str, Any]):
        """
        End a tracing span for an A2A message.
        """
        # Add outcome attributes to the span
        span.set_attribute("outcome.success", outcome.get("success", True))
        span.set_attribute("outcome.status_code", outcome.get("status_code", 200))
        
        if "error" in outcome:
            span.set_attribute("error", True)
            span.set_attribute("error.message", outcome["error"].get("message", "Unknown error"))
            span.set_attribute("error.type", outcome["error"].get("type", "Unknown"))
        
        # Add events based on outcome
        if outcome.get("events"):
            for event in outcome["events"]:
                span.add_event(
                    name=event["name"],
                    attributes=event.get("attributes", {})
                )
        
        # End the span
        span.end()
    
    def record_outcome_metrics(self, observability_data: ProtocolObservabilityData, 
                              outcome: Dict[str, Any]):
        """
        Record metrics for the message processing outcome.
        """
        # Common labels for all metrics
        common_labels = {
            "protocol": "a2a",
            "message_type": observability_data.message_type,
            "agent_id": observability_data.protocol_specific_ids.get("agent_id", "unknown"),
            "success": str(outcome.get("success", True)).lower()
        }
        
        # Record processing time if available
        if "processing_time_ms" in outcome:
            observability_system.record_protocol_metric(
                protocol_type="a2a",
                metric_name="processing_time_ms",
                value=outcome["processing_time_ms"],
                labels=common_labels
            )
        
        # Record error count if applicable
        if not outcome.get("success", True):
            observability_system.record_protocol_metric(
                protocol_type="a2a",
                metric_name="error_count",
                value=1,
                labels={
                    **common_labels,
                    "error_type": outcome.get("error", {}).get("type", "unknown")
                }
            )

class MCPObservabilityAdapter:
    """
    Adapter for Model Context Protocol (MCP) observability.
    """
    # Implementation similar to A2AObservabilityAdapter but with MCP-specific logic
    # MCP-specific methods for extracting capability invocations, resource references, etc.
    # ...

class HTTPObservabilityAdapter:
    """
    Adapter for HTTP protocol observability.
    """
    # Implementation for HTTP protocol observability
    # ...

class GenericProtocolObservabilityAdapter:
    """
    Generic adapter for protocols without specific implementations.
    """
    # Basic implementation that works with any protocol
    # ...

### Example 2: Reasoning-Agnostic Observability Flow

This example demonstrates how the Protocol Layer observability integrates with different reasoning engines while maintaining OpenMAS's reasoning agnostic architecture.

```python
class ObservabilityCoordinator:
    """
    Coordinates observability across protocol and reasoning layers
    while maintaining reasoning agnosticism.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.protocol_observability = CrossProtocolObservabilityManager(config.get("protocol_observability", {}))
        self.reasoning_observability = ReasoningObservabilityManager(config.get("reasoning_observability", {}))
        self.logger = logging.getLogger("observability_coordinator")
    
    def handle_incoming_message(self, protocol_type: str, message: Dict[str, Any], 
                               reasoning_type: str) -> Dict[str, Any]:
        """
        Handle observability for an incoming message across protocol and reasoning layers.
        This maintains separation of concerns while enabling end-to-end observability.
        
        Args:
            protocol_type: Type of protocol (e.g., "a2a", "mcp")
            message: Protocol-specific message
            reasoning_type: Type of reasoning engine (e.g., "llm", "rule_based", "bdi")
            
        Returns:
            Dictionary with observability results
        """
        # Step 1: Protocol layer observability (handles the "body")
        protocol_observation = self.protocol_observability.observe_message(
            protocol_type=protocol_type,
            message=message,
            direction=MessageDirection.INCOMING
        )
        
        # Protocol-specific span for tracing
        protocol_span = protocol_observation.get("span") if protocol_observation else None
        
        try:
            # Step 2: Protocol-agnostic message conversion
            # This is a key step in the reasoning-agnostic architecture
            protocol_adapter = protocol_registry.get_adapter(protocol_type)
            internal_message = protocol_adapter.to_internal_format(protocol_type, message)
            
            # Step 3: Reasoning engine observability (handles the "brain")
            # This is deliberately separate from protocol observability
            reasoning_context = {
                "protocol_type": protocol_type,
                "message_id": internal_message.id,
                "parent_span": protocol_span.context if protocol_span else None
            }
            
            reasoning_observation = self.reasoning_observability.observe_reasoning_start(
                reasoning_type=reasoning_type,
                message=internal_message,
                context=reasoning_context
            )
            
            # Reasoning-specific span for tracing
            reasoning_span = reasoning_observation.get("span") if reasoning_observation else None
            
            try:
                # Step 4: Process with appropriate reasoning engine
                # Note: This is where different reasoning approaches can be used
                reasoning_engine = reasoning_registry.get_engine(reasoning_type)
                start_time = time.time()
                
                # Process message with reasoning engine
                # The reasoning engine could be LLM-based, rule-based, BDI, hybrid, etc.
                response_data = reasoning_engine.process_message(internal_message)
                
                processing_time_ms = (time.time() - start_time) * 1000
                
                # Step 5: Reasoning engine observability for outcome
                reasoning_outcome = {
                    "success": True,
                    "processing_time_ms": processing_time_ms,
                    "response_type": response_data.type,
                    "events": response_data.events
                }
                
                if reasoning_observation:
                    self.reasoning_observability.observe_reasoning_end(
                        reasoning_type=reasoning_type,
                        observation_result=reasoning_observation,
                        outcome=reasoning_outcome
                    )
                
                # Step 6: Convert back to protocol-specific format
                protocol_response = protocol_adapter.from_internal_format(protocol_type, response_data)
                
                # Step 7: Protocol layer observability for response
                protocol_response_observation = self.protocol_observability.observe_message(
                    protocol_type=protocol_type,
                    message=protocol_response,
                    direction=MessageDirection.OUTGOING,
                    context={"related_span": protocol_span.context if protocol_span else None}
                )
                
                # Step 8: End protocol observation
                protocol_outcome = {
                    "success": True,
                    "processing_time_ms": processing_time_ms,
                    "response_size_bytes": len(json.dumps(protocol_response))
                }
                
                if protocol_observation:
                    self.protocol_observability.end_observation(
                        protocol_type=protocol_type,
                        observation_result=protocol_observation,
                        outcome=protocol_outcome
                    )
                
                return {
                    "protocol_response": protocol_response,
                    "protocol_observation": protocol_observation,
                    "protocol_response_observation": protocol_response_observation,
                    "reasoning_observation": reasoning_observation,
                    "processing_time_ms": processing_time_ms
                }
                
            except Exception as e:
                # Handle reasoning errors
                error_info = {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
                
                # End reasoning observation with error
                if reasoning_observation:
                    self.reasoning_observability.observe_reasoning_end(
                        reasoning_type=reasoning_type,
                        observation_result=reasoning_observation,
                        outcome={
                            "success": False,
                            "error": error_info
                        }
                    )
                
                # End protocol observation with error
                if protocol_observation:
                    self.protocol_observability.end_observation(
                        protocol_type=protocol_type,
                        observation_result=protocol_observation,
                        outcome={
                            "success": False,
                            "error": error_info
                        }
                    )
                
                # Re-raise the exception
                raise
                
        except Exception as e:
            # Handle protocol errors
            self.logger.error(f"Error handling {protocol_type} message: {str(e)}")
            
            # End protocol observation with error if not already ended
            if protocol_observation:
                self.protocol_observability.end_observation(
                    protocol_type=protocol_type,
                    observation_result=protocol_observation,
                    outcome={
                        "success": False,
                        "error": {
                            "type": type(e).__name__,
                            "message": str(e)
                        }
                    }
                )
            
            # Re-raise the exception
            raise

class ReasoningObservabilityManager:
    """
    Manages observability for different reasoning engines,
    supporting OpenMAS's reasoning agnostic architecture.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.reasoning_adapters = {}
        self.initialize_reasoning_adapters()
        self.logger = logging.getLogger("reasoning_observability")
    
    def initialize_reasoning_adapters(self):
        """
        Initialize reasoning-specific adapters for observability.
        Different reasoning approaches get different adapters.
        """
        for reasoning_type, reasoning_config in self.config.get("reasoning_types", {}).items():
            if reasoning_config.get("enabled", True):
                adapter_class = self._get_adapter_class_for_reasoning(reasoning_type)
                self.reasoning_adapters[reasoning_type] = adapter_class(reasoning_config)
                self.logger.info(f"Initialized observability adapter for {reasoning_type} reasoning")
    
    def _get_adapter_class_for_reasoning(self, reasoning_type: str) -> Type:
        """
        Get the appropriate adapter class for the reasoning type.
        Each reasoning approach has specific observability needs.
        """
        reasoning_adapter_map = {
            "llm": LLMReasoningObservabilityAdapter,
            "rule_based": RuleBasedReasoningObservabilityAdapter,
            "bdi": BDIReasoningObservabilityAdapter,
            "hybrid": HybridReasoningObservabilityAdapter,
            "kr_and_r": KRAndRReasoningObservabilityAdapter
        }
        
        # Return specific adapter if available, otherwise use generic
        return reasoning_adapter_map.get(reasoning_type, GenericReasoningObservabilityAdapter)
    
    def observe_reasoning_start(self, reasoning_type: str, message: InternalMessage, 
                               context: Dict[str, Any]):
        """
        Start observability for a reasoning operation.
        """
        # Get the appropriate adapter
        adapter = self.reasoning_adapters.get(reasoning_type)
        if not adapter:
            self.logger.warning(f"No observability adapter for reasoning type {reasoning_type}")
            return None
        
        # Process the message with the adapter
        return adapter.observe_reasoning_start(message, context)
    
    def observe_reasoning_end(self, reasoning_type: str, observation_result: Dict[str, Any], 
                             outcome: Dict[str, Any]):
        """
        End observability for a reasoning operation.
        """
        adapter = self.reasoning_adapters.get(reasoning_type)
        if not adapter:
            return
            
        adapter.observe_reasoning_end(observation_result, outcome)

# Example usage across different protocols and reasoning engines
def process_agent_request(request_data: Dict[str, Any]):
    """
    Process an agent request with appropriate protocol and reasoning observability.
    """
    # Determine protocol type from request
    protocol_type = detect_protocol_type(request_data)
    
    # Get agent configuration
    agent_config = get_agent_config_for_request(request_data)
    
    # Get reasoning type from agent configuration
    # This demonstrates OpenMAS's reasoning agnosticism - different agents can use different reasoning
    reasoning_type = agent_config.get("reasoning_type", "llm")
    
    # Create observability coordinator
    coordinator = ObservabilityCoordinator(get_observability_config())
    
    # Process the request with full observability
    try:
        result = coordinator.handle_incoming_message(
            protocol_type=protocol_type,
            message=request_data,
            reasoning_type=reasoning_type
        )
        
        return result["protocol_response"]
        
    except Exception as e:
        logger.error(f"Error processing agent request: {str(e)}")
        
        # Create appropriate error response based on protocol type
        if protocol_type == "a2a":
            return create_a2a_error_response(request_data, str(e))
        elif protocol_type == "mcp":
            return create_mcp_error_response(request_data, str(e))
        else:
            return {"error": str(e)}
```

These examples demonstrate how OpenMAS implements protocol layer observability while maintaining both multi-protocol support and reasoning agnosticism - two key architectural principles of the framework.    
    for field in sensitive_fields:
        if field_exists(sanitized_message, field):
            if config.get("observability.protocol_monitoring.message_logging.sensitive_field_handling") == "mask":
                set_field_value(sanitized_message, field, "********")
            elif config.get("observability.protocol_monitoring.message_logging.sensitive_field_handling") == "omit":
{{ ... }}
            else:  # hash
                value = get_field_value(sanitized_message, field)
                hashed_value = hash_value(value)
                set_field_value(sanitized_message, field, hashed_value)
    
    # Ensure message doesn't exceed size limit
    content_size_limit = config.get("observability.protocol_monitoring.message_logging.content_logging.max_size_bytes", 1024)
    sanitized_content = truncate_if_needed(sanitized_message, content_size_limit)
    
    # Log the message
    observability_system.log_protocol_message(
        protocol_type="a2a",
        direction=direction,
        message_data=ProtocolMessageData(
            message_id=message_id,
            message_type=message_type,
            content_summary=get_content_summary(message),
            timestamp=datetime.now(),
            size_bytes=calculate_size(message),
            protocol_specific={
                "a2a_version": message.get("version", "unknown"),
                "agent_id": message.get("agent_id", "unknown"),
                "session_id": message.get("session_id", "unknown")
            },
            sanitized_content=sanitized_content
        )
    )
```

This example demonstrates how protocol-specific message logging can be implemented with appropriate handling of sensitive data, maintaining security while enabling effective observability.
