# Distributed Tracing System

## Overview

This directory contains documentation about the distributed tracing system in OpenMAS, which provides end-to-end visibility into request flows, component interactions, and performance characteristics across all parts of the framework.

## Key Features

The distributed tracing system provides these core capabilities:

1. **Trace Collection**
   - End-to-end request tracing
   - Component boundary crossing
   - Causal relationships
   - Timing information
   - Custom attributes

2. **Span Management**
   - Hierarchical span structure
   - Span attributes
   - Span events
   - Span links
   - Status tracking

3. **Context Propagation**
   - Cross-process propagation
   - Cross-thread propagation
   - Cross-language propagation
   - Baggage items
   - Context extraction and injection

4. **Sampling Strategies**
   - Head-based sampling
   - Tail-based sampling
   - Conditional sampling
   - Probability-based sampling
   - Rate limiting

## Trace Structure

OpenMAS traces follow this standard structure:

```json
{
  "trace_id": "1234567890abcdef1234567890abcdef",
  "name": "process_user_request",
  "start_time": "2024-05-20T07:30:00.000000Z",
  "end_time": "2024-05-20T07:30:01.500000Z",
  "spans": [
    {
      "span_id": "abcdef1234567890",
      "parent_span_id": null,
      "name": "process_user_request",
      "start_time": "2024-05-20T07:30:00.000000Z",
      "end_time": "2024-05-20T07:30:01.500000Z",
      "attributes": {
        "component": "agent_manager",
        "user_id": "user-123",
        "request_id": "req-456"
      },
      "events": [
        {
          "name": "request_received",
          "timestamp": "2024-05-20T07:30:00.010000Z",
          "attributes": {
            "request_size": 1024
          }
        },
        {
          "name": "request_validated",
          "timestamp": "2024-05-20T07:30:00.020000Z"
        }
      ],
      "status": {
        "code": "SUCCESS",
        "description": null
      }
    },
    {
      "span_id": "bcdef1234567890a",
      "parent_span_id": "abcdef1234567890",
      "name": "agent_processing",
      "start_time": "2024-05-20T07:30:00.100000Z",
      "end_time": "2024-05-20T07:30:01.400000Z",
      "attributes": {
        "component": "agent",
        "agent_id": "agent-123",
        "agent_type": "assistant"
      },
      "status": {
        "code": "SUCCESS",
        "description": null
      }
    }
  ]
}
```

## Tracer Interface

Traces are created through a simple, consistent interface:

```python
# Get a tracer instance
tracer = tracing.get_tracer("component_name")

# Create a span
with tracer.start_span("operation_name") as span:
    # Add attributes to the span
    span.set_attribute("key", "value")
    span.set_attribute("user_id", user.id)
    
    # Record events
    span.add_event("starting_sub_operation")
    
    # Perform the operation
    result = perform_operation()
    
    # Record more events
    span.add_event("sub_operation_completed", {"status": "success"})
    
    # Set status
    if error:
        span.set_status(Status(StatusCode.ERROR, "Error description"))
    else:
        span.set_status(Status(StatusCode.OK))
    
    return result

# Create nested spans
with tracer.start_span("parent_operation") as parent:
    # Do some work
    parent.add_event("starting_first_child")
    
    with tracer.start_span("child_operation_1", parent=parent) as child1:
        # Child operation 1
        pass
        
    parent.add_event("starting_second_child")
    
    with tracer.start_span("child_operation_2", parent=parent) as child2:
        # Child operation 2
        pass
    
    parent.add_event("children_completed")
```

## Configuration

The tracing system is configured through the unified configuration schema:

```yaml
observability:
  tracing:
    enabled: true
    service_name: "openmas"
    propagation:
      enabled: true
      formats:
        - "w3c"
        - "b3"
    sampling:
      type: "probabilistic"
      rate: 0.1
      rules:
        - condition: "error == true"
          rate: 1.0
        - condition: "duration > 1s"
          rate: 0.5
    exporters:
      jaeger:
        enabled: true
        endpoint: "http://jaeger:14268/api/traces"
        username: "${JAEGER_USERNAME}"
        password: "${JAEGER_PASSWORD}"
      zipkin:
        enabled: false
        endpoint: "http://zipkin:9411/api/v2/spans"
      otlp:
        enabled: false
        endpoint: "https://otlp.example.com:4317"
        protocol: "grpc"
        certificates: "/path/to/certs"
    limits:
      max_attributes_per_span: 128
      max_events_per_span: 128
      max_links_per_span: 128
      max_attribute_value_length: 1024
```

## Key Trace Points

OpenMAS traces these standard operations across components:

### User Request Flow

```
user_request
  ├── request_validation
  ├── agent_selection
  ├── agent_processing
  │    ├── message_parsing
  │    ├── context_preparation
  │    ├── llm_invocation
  │    ├── response_generation
  │    └── post_processing
  └── response_delivery
```

### Agent Communication Flow

```
agent_communication
  ├── message_preparation
  ├── protocol_selection
  ├── protocol_processing
  │    ├── serialization
  │    ├── transport
  │    └── deserialization
  ├── recipient_delivery
  └── acknowledgment
```

### LLM Invocation Flow

```
llm_invocation
  ├── prompt_preparation
  ├── provider_selection
  ├── model_invocation
  │    ├── tokenization
  │    ├── inference
  │    └── response_parsing
  └── result_processing
```

## Integration with Other Components

The tracing system integrates with other observability components:

- **Logging** - Logs can be correlated with traces
- **Metrics** - Metrics can be derived from trace data
- **Alerts** - Trace anomalies can trigger alerts
- **Dashboards** - Traces are visualized in dashboards

## Tracing Patterns

### Context Propagation

Propagating context across components:

```python
async def receive_request(request):
    # Extract context from the request
    context = extract_context(request.headers)
    
    # Start a new span with the extracted context as parent
    with tracer.start_span("process_request", context=context) as span:
        # Process the request
        response = await process_request(request)
        
        # Inject context into the response
        inject_context(response.headers, span.get_context())
        
        return response
```

### Baggage

Using baggage to carry information:

```python
async def authenticate_user(request):
    # Extract context
    context = extract_context(request.headers)
    
    # Start span with context
    with tracer.start_span("authenticate", context=context) as span:
        # Authenticate user
        user = await authenticate(request.credentials)
        
        # Add user information to baggage
        context = set_baggage(span.get_context(), "user_id", user.id)
        context = set_baggage(context, "user_role", user.role)
        
        # Continue processing with enriched context
        return await process_with_context(request, context)
```

### Error Tracking

Tracking errors in traces:

```python
async def process_request(request):
    with tracer.start_span("process_request") as span:
        try:
            # Process the request
            result = await process(request)
            return result
        except ValidationError as e:
            # Record the error details
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, "Validation failed"))
            span.set_attribute("error.type", "validation_error")
            span.set_attribute("error.message", str(e))
            raise
```

## References

- [Observability Architecture](/refactoring_work/00b_overview/12_observability/architecture.md)
- [Logging Subsystem](/refactoring_work/00b_overview/12_observability/logging/README.md)
- [Metrics Collection](/refactoring_work/00b_overview/12_observability/metrics/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
