# Observability Integration

## Overview

This document describes how the Observability system integrates with other components of OpenMAS. Understanding these integration points is essential for implementing observable components that leverage the full capabilities of the framework.

## Integration with Other Components

### Agent Framework Integration

The Observability system integrates with the agent framework (`/04_agents/`) through:

- **Agent Lifecycle Monitoring**: Tracking agent creation, initialization, and termination
- **Agent Activity Logging**: Logging of agent actions and decisions
- **Performance Metrics**: Collection of agent performance metrics
- **Error Tracking**: Monitoring of agent errors and exceptions
- **Message Tracing**: Tracing of messages through agents

```
Agent ──> Instrumentation ──> Observability System
```

### Protocol Layer Integration

The Observability system integrates with the protocol layer (`/02_protocols/`) through:

- **Protocol Metrics**: Collection of protocol-specific performance metrics
- **Message Logging**: Structured logging of protocol messages
- **Protocol Tracing**: End-to-end tracing of protocol interactions
- **Error Monitoring**: Tracking of protocol-level errors
- **Protocol Debugging**: Tools for debugging protocol interactions

```
Protocol ──> Instrumentation ──> Observability System
```

### Configuration System Integration

The Observability system is configured through the configuration system (`/03_configuration/`) via:

- **Observability Settings**: Configuration of observability features
- **Log Levels**: Configuration of component-specific log levels
- **Metric Collection**: Configuration of metric collection parameters
- **Trace Sampling**: Configuration of trace sampling strategies
- **Alert Rules**: Definition of alerting rules

```
Configuration ──> Observability Settings ──> Observability System
```

### Implementation Integration

The Observability system provides insights into the deployment, testing, and security layers through:

- **Deployment Monitoring**: Monitoring of deployment status and health
- **Resource Utilization**: Tracking of resource usage
- **System Health**: Overall system health monitoring
- **Component Status**: Status of individual components
- **Version Tracking**: Monitoring of component versions

```
Implementation ──> Health Metrics ──> Observability System
```

### Knowledge Representation Integration

The Observability system monitors the knowledge representation system (`/09_knowledge_representation/`) through:

- **Knowledge Operation Logging**: Logging of knowledge access and modifications
- **Reasoning Tracing**: Tracing of reasoning steps
- **Knowledge Metrics**: Metrics on knowledge base size and usage
- **Performance Monitoring**: Monitoring of reasoning performance
- **Error Tracking**: Tracking of knowledge-related errors

```
Knowledge Representation ──> Instrumentation ──> Observability System
```

### Asset Management Integration

The Observability system monitors the asset management system (`/10_asset_management/`) through:

- **Asset Operation Logging**: Logging of asset lifecycle events
- **Asset Metrics**: Metrics on asset usage and storage
- **Performance Monitoring**: Monitoring of asset loading and processing
- **Error Tracking**: Tracking of asset-related errors
- **Cache Performance**: Monitoring of asset cache performance

```
Asset Management ──> Instrumentation ──> Observability System
```

### Prompt Management Integration

The Observability system monitors the prompt management system (`/11_prompt_management/`) through:

- **Prompt Usage Logging**: Logging of prompt template usage
- **Token Metrics**: Metrics on token usage and efficiency
- **Performance Monitoring**: Monitoring of prompt rendering and processing
- **Error Tracking**: Tracking of prompt-related errors
- **Context Analytics**: Analysis of context window utilization

```
Prompt Management ──> Instrumentation ──> Observability System
```

## Cross-Cutting Integration Concerns

Several integration aspects cut across multiple components:

1. **Common Instrumentation**: Consistent instrumentation across components
2. **Context Propagation**: Propagation of observability context between components
3. **Error Correlation**: Correlation of errors across component boundaries
4. **Performance Measurement**: End-to-end performance measurement
5. **Resource Attribution**: Attribution of resource usage to components

## Implementation Considerations

When implementing observability integration:

1. Use the standard observability interfaces for consistency
2. Follow the tagging conventions for proper correlation
3. Consider performance impact, especially in high-throughput components
4. Provide appropriate context in all observability data
5. Respect privacy boundaries for sensitive information

## Integration Patterns

### Standard Component Instrumentation

```python
class ObservableComponent:
    def __init__(self, component_name, component_id=None):
        self.logger = logging.get_logger(
            component_name, 
            component_id=component_id
        )
        self.metrics = metrics.get_recorder(
            component_name, 
            component_id=component_id
        )
        self.tracer = tracing.get_tracer(
            component_name, 
            component_id=component_id
        )
    
    def operation(self, *args, **kwargs):
        with self.tracer.start_span("operation") as span:
            for key, value in kwargs.items():
                if key not in self._sensitive_params:
                    span.set_attribute(key, str(value))
            
            self.metrics.increment("operations_total", 1)
            start_time = time.time()
            
            try:
                self.logger.debug("Starting operation", operation="operation")
                result = self._operation_impl(*args, **kwargs)
                self.logger.info("Operation completed", operation="operation")
                return result
            except Exception as e:
                self.logger.error(
                    "Operation failed",
                    operation="operation",
                    error=str(e)
                )
                self.metrics.increment("operation_errors", 1)
                raise
            finally:
                duration = time.time() - start_time
                self.metrics.record("operation_duration", duration)
```

### Trace Context Propagation

```python
async def handle_request(request, context):
    # Extract trace context from request
    trace_context = extract_trace_context(request)
    
    # Create new span using the parent context
    with tracer.start_span("handle_request", parent=trace_context) as span:
        span.set_attribute("request_type", request.type)
        
        # Process the request
        response = await process_request(request)
        
        # Inject trace context into response
        inject_trace_context(response, tracer.current_span().context)
        
        return response
```

### Metric Collection

```python
def process_batch(batch):
    batch_size = len(batch)
    metrics.gauge("batch_size", batch_size)
    
    start_time = time.time()
    processed = 0
    errors = 0
    
    for item in batch:
        try:
            process_item(item)
            processed += 1
        except Exception:
            errors += 1
    
    duration = time.time() - start_time
    
    metrics.counter("items_processed_total", processed)
    metrics.counter("items_error_total", errors)
    metrics.histogram("batch_processing_duration", duration)
    metrics.gauge("processing_rate", processed / duration if duration > 0 else 0)
```

## References

- [Agent Framework](/refactoring_work/00b_overview/04_agents/README.md)
- [Protocol Layer](/refactoring_work/00b_overview/02_protocols/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Deployment Documentation](/refactoring_work/00b_overview/15_deployment/README.md)
- [Testing Documentation](/refactoring_work/00b_overview/16_testing/README.md)
- [Security Documentation](/refactoring_work/00b_overview/17_security/README.md)
- [Knowledge Representation](/refactoring_work/00b_overview/09_knowledge_representation/README.md)
- [Asset Management](/refactoring_work/00b_overview/10_asset_management/README.md)
- [Prompt Management](/refactoring_work/00b_overview/11_prompt_management/README.md)
