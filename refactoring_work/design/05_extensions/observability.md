# Logging and Observability Standard

## Observability Definition
- **Name**: Logging and Observability
- **Purpose**: Standardized approach to logging, metrics collection, tracing, and health monitoring
- **Integration**: Consistent observability across all components
- **Protocol Compatibility**: Supports monitoring across multiple protocols (A2A, MCP, etc.)
- **Reasoning Agnosticism**: Maintains clear separation between communication monitoring and reasoning monitoring

## Observability Schema
```yaml
# Standardized observability configuration schema
type: object
properties:
  # System-level observability configuration
  observability:
    type: object
    description: "Global observability configuration"
    properties:
      # Logging configuration
      logging:
        type: object
        description: "Logging configuration"
        properties:
          level:
            type: string
            description: "Log level"
            enum: ["error", "warning", "info", "debug"]
            default: "info"
          format:
            type: string
            description: "Log format"
            enum: ["json", "text"]
            default: "json"
          output:
            type: string
            description: "Log output destination"
            enum: ["file", "stdout", "both"]
            default: "both"
          file:
            type: object
            description: "File logging configuration"
            properties:
              path:
                type: string
                description: "Log file path"
                default: "./logs"
              max_size_mb:
                type: integer
                description: "Maximum log file size in MB"
                default: 100
              max_files:
                type: integer
                description: "Maximum number of log files to keep"
                default: 10
          include_context:
            type: object
            description: "Context to include in logs"
            properties:
              session_id:
                type: boolean
                description: "Include session ID in logs"
                default: true
              agent_id:
                type: boolean
                description: "Include agent ID in logs"
                default: true
              request_id:
                type: boolean
                description: "Include request ID in logs"
                default: true

      # MCP Protocol Monitoring
      mcp_monitoring:
        type: object
        description: "MCP protocol-specific monitoring"
        properties:
          enabled:
            type: boolean
            description: "Whether MCP monitoring is enabled"
            default: true
          # Communication-layer monitoring (agnostic to reasoning approach)
          tool_monitoring:
            type: object
            description: "Monitoring for MCP tools"
            properties:
              track_tool_calls:
                type: boolean
                description: "Whether to track tool calls"
                default: true
              track_tool_errors:
                type: boolean
                description: "Whether to track tool errors"
                default: true
              track_tool_latency:
                type: boolean
                description: "Whether to track tool latency"
                default: true
              track_tool_usage:
                type: boolean
                description: "Whether to track tool usage patterns"
                default: true
              log_level_tools:
                type: string
                description: "Log level for tool calls"
                enum: ["error", "warning", "info", "debug"]
                default: "info"
          server_monitoring:
            type: object
            description: "Monitoring for MCP server mode"
            properties:
              track_connections:
                type: boolean
                description: "Whether to track client connections"
                default: true
              track_server_health:
                type: boolean
                description: "Whether to track server health metrics"
                default: true
              log_level_server:
                type: string
                description: "Log level for server events"
                enum: ["error", "warning", "info", "debug"]
                default: "info"
          client_monitoring:
            type: object
            description: "Monitoring for MCP client mode"
            properties:
              track_connection_status:
                type: boolean
                description: "Whether to track connection status"
                default: true
              track_reconnects:
                type: boolean
                description: "Whether to track reconnection attempts"
                default: true
              log_level_client:
                type: string
                description: "Log level for client events"
                enum: ["error", "warning", "info", "debug"]
                default: "info"
          resource_monitoring:
            type: object
            description: "Monitoring for MCP resources"
            properties:
              track_resources:
                type: boolean
                description: "Whether to track resource usage"
                default: true
              track_resource_size:
                type: boolean
                description: "Whether to track resource sizes"
                default: true
              content_type_metrics:
                type: boolean
                description: "Whether to collect metrics by content type"
                default: true
          # Separation of concerns - only monitor communication aspects
          reasoning_separation:
            type: boolean
            description: "Whether to maintain strict separation between communication and reasoning monitoring"
            default: true

      # A2A Protocol Monitoring
      a2a_monitoring:
        type: object
        description: "A2A protocol-specific monitoring"
        properties:
          enabled:
            type: boolean
            description: "Whether A2A monitoring is enabled"
            default: true
          task_lifecycle:
            type: object
            description: "Monitoring for A2A task lifecycle"
            properties:
              track_state_transitions:
                type: boolean
                description: "Whether to track task state transitions"
                default: true
              log_level_transitions:
                type: string
                description: "Log level for state transitions"
                enum: ["error", "warning", "info", "debug"]
                default: "info"
              metrics_transitions:
                type: boolean
                description: "Whether to collect metrics for transitions"
                default: true
          message_monitoring:
            type: object
            description: "Monitoring for A2A messages"
            properties:
              log_messages:
                type: boolean
                description: "Whether to log messages"
                default: true
              log_message_size:
                type: boolean
                description: "Whether to log message size"
                default: true
              log_level_messages:
                type: string
                description: "Log level for messages"
                enum: ["error", "warning", "info", "debug"]
                default: "debug"
              sensitive_content_handling:
                type: string
                description: "How to handle sensitive content in logs"
                enum: ["redact", "hash", "remove", "preserve"]
                default: "redact"
          artifact_monitoring:
            type: object
            description: "Monitoring for A2A artifacts"
            properties:
              track_artifacts:
                type: boolean
                description: "Whether to track artifacts"
                default: true
              size_metrics:
                type: boolean
                description: "Whether to collect size metrics for artifacts"
                default: true
              content_type_metrics:
                type: boolean
                description: "Whether to collect metrics by content type"
                default: true
              storage_metrics:
                type: boolean
                description: "Whether to collect storage metrics"
                default: true

      # Metrics collection
      metrics:
        type: object
        description: "Metrics collection configuration"
        properties:
          enabled:
            type: boolean
            description: "Whether metrics collection is enabled"
            default: true
          provider:
            type: string
            description: "Metrics provider"
            enum: ["prometheus", "datadog", "cloudwatch"]
            default: "prometheus"
          endpoint:
            type: string
            description: "Metrics endpoint path"
            default: "/metrics"
          collect:
            type: array
            description: "Metrics to collect"
            items:
              type: string
            default: ["request_count", "response_time", "error_rate", "memory_usage"]
          push_interval_seconds:
            type: integer
            description: "Interval for pushing metrics"
            default: 30

      # Distributed tracing
      tracing:
        type: object
        description: "Distributed tracing configuration"
        properties:
          enabled:
            type: boolean
            description: "Whether distributed tracing is enabled"
            default: true
          provider:
            type: string
            description: "Tracing provider"
            enum: ["opentelemetry", "jaeger", "zipkin"]
            default: "opentelemetry"
          sampling_rate:
            type: number
            description: "Tracing sampling rate (0.0 to 1.0)"
            minimum: 0.0
            maximum: 1.0
            default: 0.1
          propagation:
            type: boolean
            description: "Whether to propagate trace context"
            default: true

      # Health checks
      health:
        type: object
        description: "Health check configuration"
        properties:
          enabled:
            type: boolean
            description: "Whether health checks are enabled"
            default: true
          endpoint:
            type: string
            description: "Health check endpoint path"
            default: "/health"
          checks:
            type: array
            description: "Health checks to perform"
            items:
              type: object
              properties:
                name:
                  type: string
                  description: "Health check name"
                timeout_ms:
                  type: integer
                  description: "Health check timeout in milliseconds"
                  default: 1000
              required:
                - name
    required:
      - logging
```

## Environment-Specific Observability Configuration
```yaml
# Environment-specific observability configuration
type: object
properties:
  environments:
    type: object
    description: "Environment-specific configurations"
    additionalProperties:
      type: object
      properties:
        observability:
          type: object
          description: "Observability configuration for this environment"
          properties:
            logging:
              type: object
              description: "Logging configuration"
              properties:
                level:
                  type: string
                  description: "Log level"
                  enum: ["error", "warning", "info", "debug"]
            tracing:
              type: object
              description: "Tracing configuration"
              properties:
                sampling_rate:
                  type: number
                  description: "Tracing sampling rate (0.0 to 1.0)"
                  minimum: 0.0
                  maximum: 1.0
            metrics:
              type: object
              description: "Metrics configuration"
              properties:
                additional_labels:
                  type: object
                  description: "Additional labels for metrics"
                  additionalProperties:
                    type: string
```

## MCP-Specific Monitoring

### Tool Usage Monitoring

The observability system tracks MCP tool usage while maintaining OpenMAS's reasoning agnosticism (separating communication from reasoning):

1. **Tool Call Tracking**:
   - Count of tool calls by tool name
   - Success and failure rates
   - Latency distributions
   - Parameter patterns (with PII protection)

2. **Resource Usage Monitoring**:
   - Resource types and sizes
   - Resource access patterns
   - Resource lifecycle metrics

3. **Transport Monitoring**:
   - Connection establishment latency
   - Connection stability metrics
   - Reconnection patterns
   - Transport-specific performance metrics (SSE vs STDIO)

### Health Checks

Health checks for MCP include specific protocol health verification:

1. **Server Health**: For MCP servers, validates that the server is accepting connections
2. **Tool Health**: Confirms tools are properly registered and executable
3. **Resource Health**: Validates resource access and management
4. **Client Connection Health**: For clients, confirms ability to connect to MCP servers

## Communication vs Reasoning Monitoring

In accordance with OpenMAS's reasoning agnosticism, the observability system maintains a clear separation:

1. **Communication Layer Monitoring**:
   - Protocol-specific metrics (A2A message counts, task states, etc.)
   - Network performance metrics
   - Protocol compliance checks

2. **Reasoning Layer Monitoring** (optional, configurable per reasoning approach):
   - Memory usage metrics
   - Token usage for LLM-based reasoning
   - Inference time metrics for neural approaches
   - Rule evaluations for symbolic approaches
   - Knowledge base access patterns
   - BDI cycle metrics for cognitive agents
   - Symbolic reasoning statistics
   - Hybrid reasoning coordination metrics

3. **Integration Points**:
   - Clean interfaces between monitoring systems
   - Correlation IDs to trace requests across layers
   - Combined dashboards with clear layer separation

## Agent-Specific Observability Configuration
```yaml
# Agent-specific observability configuration
type: object
properties:
  agents:
    type: object
    description: "Agent configuration"
    additionalProperties:
      type: object
      properties:
        # Agent observability configuration
        observability:
          type: object
          description: "Agent-specific observability configuration"
          properties:
            metrics:
              type: object
              description: "Metrics configuration"
              properties:
                custom_metrics:
                  type: array
                  description: "Custom metrics for this agent"
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                        description: "Metric name"
                      type:
                        type: string
                        description: "Metric type"
                        enum: ["counter", "gauge", "histogram", "summary"]
                      description:
                        type: string
                        description: "Metric description"
                    required:
                      - name
                      - type
                      - description
```

## Logging Levels and Usage
| Level | Usage | Examples |
|-------|-------|----------|
| error | Errors that prevent normal operation | Failed connections, API errors |
| warning | Issues that don't prevent operation | Rate limiting, retry attempts |
| info | Normal operational information | Request handling, state changes |
| debug | Detailed debugging information | Message contents, processing steps |

## Protocol-Specific Monitoring

### Communication Layer Monitoring

The observability system tracks protocol-specific metrics while maintaining OpenMAS's reasoning agnosticism (clear separation between communication and reasoning):

#### A2A Protocol Monitoring

1. **Task Lifecycle Metrics**:
   - Transitions between task states (submitted → working → completed/failed)
   - Time spent in each task state
   - Distribution of terminal states (completion vs failure rates)

2. **A2A Message Metrics**:
   - Message counts by role (user vs agent)
   - Part type distribution (text, file, data)
   - File sizes and types processed
   - Response times for different interaction patterns

#### MCP Protocol Monitoring

1. **Session Lifecycle Metrics**:
   - Session creation, activation, and termination rates
   - Session duration and resource utilization
   - Request completion rates and error distribution

2. **MCP Message Metrics**:
   - Request/response counts and latency
   - Content type distribution
   - Streaming metrics (chunks per second, stream duration)
   - Error rates by error type

### Protocol-Independent Monitoring

Observability also provides protocol-agnostic metrics that apply regardless of the communication protocol used:

1. **Cross-Protocol Metrics**:
   - Total active sessions/tasks across all protocols
   - Aggregated throughput and latency
   - Unified error tracking and categorization
   - Resource utilization across protocol handlers

2. **Protocol Adaptation Metrics**:
   - Protocol conversion success/failure rates
   - Adaptation latency measurements
   - Feature compatibility tracking

3. **Communication-Level Monitoring Only**:
   - The monitoring focuses on the communication layer ("body")
   - Avoids intrusive monitoring of reasoning processes ("brain")
   - Preserves the separation between communication and reasoning

### Health Checks

Health checks for A2A include specific protocol health verification:

1. **Agent Card Health**: Verifies agent card accessibility and correctness
2. **Task Processing Health**: Confirms task submissions are being processed
3. **Streaming Capability**: Validates streaming functionality if enabled
4. **Push Notification Health**: Tests webhook functionality if configured

## Metrics Configuration
- **Standard Metrics**: [List of standard metrics collected by default]
- **Custom Metrics**: [How to add custom metrics]
- **Labels/Tags**: [How to use labels/tags with metrics]
- **Aggregation**: [How metrics are aggregated]

## Distributed Tracing
- **Trace Context**: [How trace context is propagated]
- **Span Management**: [How to create and manage spans]
- **Sampling Strategies**: [Different sampling strategies]
- **Trace Visualization**: [How to visualize traces]

## Health Checks
- **System Health**: [System-level health checks]
- **Component Health**: [Component-level health checks]
- **Dependency Health**: [Dependency health checks]
- **Custom Health Checks**: [How to implement custom health checks]

## Testing
- **Unit Test Requirements**: [Observability-specific test requirements]
- **Integration Test Requirements**: [Observability integration test requirements]
- **Mock vs Real Testing**: [How to test with mock vs real observability backends]

## Usage Examples
```python
# Example observability setup
from openmas.observability import ObservabilityManager

def setup_observability(app, config):
    # Initialize observability manager with configuration
    obs = ObservabilityManager(config["observability"])

    # Setup logging
    obs.setup_logging()

    # Setup metrics collection
    if config["observability"]["metrics"]["enabled"]:
        obs.setup_metrics(app)

    # Setup distributed tracing
    if config["observability"]["tracing"]["enabled"]:
        obs.setup_tracing()

    # Setup health checks
    if config["observability"]["health"]["enabled"]:
        obs.setup_health_checks(app)

    return obs
```
