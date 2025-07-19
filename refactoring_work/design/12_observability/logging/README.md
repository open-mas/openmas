# Logging Subsystem

## Overview

This directory contains documentation about the logging subsystem in OpenMAS, which provides comprehensive, structured logging capabilities across all components of the framework.

## Key Features

The logging subsystem provides these core capabilities:

1. **Structured Logging**
   - JSON-formatted log entries
   - Consistent field naming
   - Type-safe log fields
   - Nested structured data
   - Context enrichment

2. **Log Levels**
   - Standard levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Component-specific level configuration
   - Dynamic level adjustment
   - Level inheritance hierarchy
   - Sampling by level

3. **Context Management**
   - Automatic context propagation
   - Request context tracking
   - User context tracking
   - Operation context tracking
   - Context inheritance

4. **Log Routing**
   - Multiple log destinations
   - Conditional routing rules
   - Format transformation
   - Buffer management
   - Failover handling

## Log Structure

OpenMAS logs follow this standard structure:

```json
{
  "timestamp": "2024-05-20T07:30:00.123456Z",
  "level": "INFO",
  "component": "agent_manager",
  "message": "Agent initialized successfully",
  "context": {
    "request_id": "req-456",
    "operation": "initialize_agent",
    "session_id": "session-789"
  },
  "fields": {
    "agent_id": "agent-123",
    "agent_type": "assistant",
    "duration_ms": 45
  },
  "tags": ["initialization", "agent"],
  "source": {
    "file": "agent_manager.py",
    "line": 123,
    "function": "initialize_agent"
  }
}
```

## Logger Interface

Loggers are accessed through a simple, consistent interface:

```python
# Get a logger instance
logger = logging.get_logger("component_name")

# Basic logging
logger.debug("Debug message")
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Structured logging with fields
logger.info("User registered", 
            user_id="user123", 
            registration_time=datetime.now())

# With context
with logger.context(request_id="req123", operation="registration"):
    logger.info("Starting operation")
    # ... perform operations
    logger.info("Operation completed")

# Error logging with exception info
try:
    # ... some operation
except Exception as e:
    logger.error("Operation failed",
                error=str(e),
                stack_trace=traceback.format_exc())
```

## Configuration

The logging subsystem is configured through the unified configuration schema:

```yaml
observability:
  logging:
    default_level: "INFO"
    component_levels:
      agent_manager: "DEBUG"
      protocol_layer: "WARNING"
    handlers:
      console:
        enabled: true
        format: "text"  # or "json"
      file:
        enabled: true
        path: "/var/log/openmas/application.log"
        rotation:
          max_size: "100MB"
          max_files: 10
      remote:
        enabled: false
        url: "http://logging-service:8080/logs"
        batch_size: 100
        flush_interval: "5s"
    context:
      auto_fields:
        hostname: true
        pid: true
        thread_id: true
      propagation: true
    sensitive_patterns:
      - pattern: "password=.*"
        replacement: "password=***"
      - pattern: "token=.*"
        replacement: "token=***"
```

## Integration with Other Components

The logging subsystem integrates with other observability components:

- **Metrics** - Logs can generate metrics for log volume, error rates, etc.
- **Tracing** - Logs are automatically associated with trace spans
- **Alerts** - Log patterns can trigger alerts
- **Dashboards** - Logs are visualized in dashboards

## Log Processing Patterns

### Filter and Enrich

Logs can be processed in a pipeline to filter and enrich:

```python
# Create a processing pipeline
pipeline = LogPipeline([
    # Add request ID if missing
    RequestIdEnricher(),
    # Filter out health check logs
    HealthCheckFilter(),
    # Add user information
    UserContextEnricher(user_service),
    # Redact sensitive information
    SensitiveDataRedactor(patterns=[r'password=\w+', r'token=\w+'])
])

# Apply the pipeline to a logger
logger = logging.get_logger("component", pipeline=pipeline)
```

### Contextual Logging

Context can be carried through operations:

```python
async def process_request(request):
    # Create a context logger for this request
    logger = logging.get_logger("request_processor")
    
    # Start a logging context
    with logger.context(
        request_id=request.id,
        user_id=request.user_id,
        operation="process_request"
    ):
        logger.info("Request received", request_type=request.type)
        
        # Process the request
        result = await handle_request(request, logger)
        
        logger.info("Request processed", result_status=result.status)
        return result
```

## References

- [Observability Architecture](/refactoring_work/00b_overview/12_observability/architecture.md)
- [Metrics Collection](/refactoring_work/00b_overview/12_observability/metrics/README.md)
- [Distributed Tracing](/refactoring_work/00b_overview/12_observability/tracing/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
