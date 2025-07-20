# Metrics Collection System

## Overview

This directory contains documentation about the metrics collection system in OpenMAS, which provides comprehensive measurement and tracking of system performance, usage patterns, and business metrics across all components of the framework.

## Key Features

The metrics collection system provides these core capabilities:

1. **Metric Types**
   - Counters: Monotonically increasing values
   - Gauges: Values that can go up and down
   - Histograms: Distribution of values
   - Timers: Duration measurements
   - Rate meters: Rate of events over time

2. **Multi-dimensional Metrics**
   - Tag-based dimensions
   - High-cardinality support
   - Dynamic tag values
   - Hierarchical dimensions
   - Default dimension values

3. **Aggregation Support**
   - Multiple aggregation intervals
   - Custom aggregation functions
   - Pre-aggregation optimizations
   - Statistical aggregates
   - Cross-dimensional aggregation

4. **Metric Export**
   - Multiple export endpoints
   - Protocol adaptations
   - Buffered exports
   - Compression
   - Failure handling

## Metric Structure

OpenMAS metrics follow this standard structure:

```json
{
  "name": "request_duration",
  "description": "Duration of request processing in seconds",
  "type": "histogram",
  "unit": "seconds",
  "timestamp": "2024-05-20T07:30:00Z",
  "value": 0.345,
  "dimensions": {
    "component": "agent_manager",
    "operation": "process_request",
    "agent_id": "agent-123",
    "environment": "production"
  },
  "metadata": {
    "sampling_rate": 1.0
  }
}
```

## Metrics Interface

Metrics are recorded through a simple, consistent interface:

```python
# Get a metrics recorder instance
metrics = metrics.get_recorder("component_name")

# Counter operations
metrics.increment("requests_total", 1)
metrics.increment("errors_total", 1, error_type="timeout")

# Gauge operations
metrics.gauge("active_connections", 42)
metrics.gauge("queue_size", lambda: get_queue_size())

# Histogram operations
metrics.histogram("response_size", response.size_bytes)

# Timer operations
with metrics.timer("request_duration"):
    # ... perform operation
    process_request()

# Manual timer
start = time.time()
process_request()
duration = time.time() - start
metrics.record("request_duration", duration)

# Rate meters
metrics.mark("requests_rate")
```

## Configuration

The metrics system is configured through the unified configuration schema:

```yaml
observability:
  metrics:
    enabled: true
    default_dimensions:
      service: "openmas"
      environment: "production"
    export:
      prometheus:
        enabled: true
        port: 9090
        path: "/metrics"
      statsd:
        enabled: false
        host: "statsd.example.com"
        port: 8125
        prefix: "openmas"
      custom:
        enabled: false
        url: "https://metrics.example.com/v1/metrics"
        auth_token: "${METRICS_TOKEN}"
        batch_size: 100
        interval: "10s"
    sampling:
      default_rate: 1.0
      rules:
        - metric: "high_volume_event"
          rate: 0.1
    retention:
      intervals:
        - "10s"
        - "1m"
        - "5m"
        - "1h"
      storage_time: "7d"
    cardinality:
      max_dimensions: 10
      max_values_per_dimension: 1000
```

## Key Metrics

OpenMAS tracks these standard metrics across components:

### System Metrics

```
system.cpu.usage
system.memory.usage
system.disk.usage
system.network.bytes_in
system.network.bytes_out
```

### Application Metrics

```
app.requests.total
app.requests.duration
app.errors.total
app.active_agents
app.messages.total
```

### Protocol Metrics

```
protocol.messages.sent
protocol.messages.received
protocol.errors.total
protocol.connections.active
protocol.latency
```

### Model Metrics

```
model.invocations.total
model.tokens.input
model.tokens.output
model.latency
model.errors.total
```

### Business Metrics

```
business.tasks.completed
business.user.sessions
business.response.quality
business.user.satisfaction
business.task.success_rate
```

## Integration with Other Components

The metrics system integrates with other observability components:

- **Logging** - Metrics can be derived from log events
- **Tracing** - Metrics are automatically associated with trace spans
- **Alerts** - Metric thresholds can trigger alerts
- **Dashboards** - Metrics are visualized in dashboards

## Metrics Collection Patterns

### Component-specific Metrics

Components define their own metrics:

```python
class AgentManager:
    def __init__(self):
        self.metrics = metrics.get_recorder("agent_manager")

    def create_agent(self, agent_type):
        with self.metrics.timer("agent_creation_duration", agent_type=agent_type):
            # Create the agent
            agent = self._create_agent_internal(agent_type)

            # Track agent creation
            self.metrics.increment("agents_created_total", 1, agent_type=agent_type)
            self.metrics.gauge("agents_active", self._get_active_agent_count())

            return agent
```

### Dimensional Data Analysis

Using dimensions for analysis:

```python
# Record metrics with multiple dimensions
metrics.histogram(
    "request_duration",
    duration,
    component="agent_manager",
    operation="process_request",
    agent_type="assistant",
    protocol="mcp"
)

# This allows analysis across different dimensions:
# - Performance by component
# - Performance by operation
# - Performance by agent type
# - Performance by protocol
```

## References

- [Observability Architecture](/refactoring_work/00b_overview/12_observability/architecture.md)
- [Logging Subsystem](/refactoring_work/00b_overview/12_observability/logging/README.md)
- [Distributed Tracing](/refactoring_work/00b_overview/12_observability/tracing/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
