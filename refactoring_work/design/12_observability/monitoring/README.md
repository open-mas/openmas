# Monitoring System

## Overview

This directory contains documentation about the monitoring system in OpenMAS, which provides dashboards, visualizations, and alerting for observability data collected across the framework.

## Key Features

The monitoring system provides these core capabilities:

1. **Dashboards**
   - Pre-built dashboards for common monitoring needs
   - Customizable dashboard creation
   - Multi-signal visualization
   - Drill-down capabilities
   - Dashboard sharing and export

2. **Visualization**
   - Time-series charts
   - Heatmaps and distributions
   - Table views
   - Topology visualizations
   - Status indicators

3. **Alerting**
   - Threshold-based alerts
   - Anomaly detection
   - Alert routing
   - Alert aggregation
   - Escalation policies

4. **Health Checks**
   - Component health monitoring
   - Dependency health monitoring
   - Synthetic monitoring
   - Status pages
   - SLO/SLA tracking

## Dashboard Types

OpenMAS provides these standard dashboard types:

### System Dashboards

```
- System Overview: High-level system status and health
- Resource Utilization: CPU, memory, disk, network usage
- Component Status: Status of all system components
- Deployment Status: Deployment and version information
```

### Protocol Dashboards

```
- Protocol Overview: Summary of all protocol activity
- Protocol Performance: Performance metrics for protocols
- Error Rates: Protocol-specific error analysis
- Message Flows: Visualization of message patterns
```

### Agent Dashboards

```
- Agent Overview: Summary of all agent activity
- Agent Performance: Performance metrics for agents
- Agent Capabilities: Capability usage and performance
- Agent States: Agent state transitions
```

### Model Dashboards

```
- Model Usage: Model invocation patterns
- Token Consumption: Token usage across models
- Response Times: Model response time analysis
- Error Analysis: Model-specific error patterns
```

### User Dashboards

```
- User Activity: User interaction patterns
- Task Completion: Task success metrics
- Response Quality: Quality metrics for responses
- User Satisfaction: User satisfaction indicators
```

## Alerting System

The alerting system supports these alert types:

### Threshold Alerts

```yaml
alerts:
  error_rate:
    description: "Error rate exceeds threshold"
    metric: "app.errors.rate"
    condition: "> 0.05"  # 5% error rate
    severity: "warning"
    notification:
      channels: ["slack", "email"]
      throttle: "15m"
```

### Anomaly Alerts

```yaml
alerts:
  latency_anomaly:
    description: "Unusual latency pattern detected"
    metric: "app.request.duration"
    condition: "anomaly(window=1h, sensitivity=3)"
    severity: "info"
    notification:
      channels: ["slack"]
```

### Composite Alerts

```yaml
alerts:
  service_degradation:
    description: "Service degradation detected"
    condition: "error_rate AND latency_anomaly"
    severity: "critical"
    notification:
      channels: ["slack", "email", "pagerduty"]
      throttle: "5m"
```

## Health Check System

The health check system includes:

### Component Health

```yaml
health_checks:
  agent_manager:
    description: "Agent Manager health"
    type: "http"
    endpoint: "/health/agent-manager"
    interval: "30s"
    timeout: "5s"
    success_criteria: "status == 200"
    dependencies:
      - "database"
      - "model_service"
```

### Synthetic Monitoring

```yaml
synthetic_monitors:
  user_workflow:
    description: "End-to-end user workflow"
    steps:
      - name: "login"
        request:
          url: "/api/login"
          method: "POST"
          body: {"username": "test", "password": "test"}
        success_criteria: "status == 200 && json.token exists"
      - name: "create_agent"
        request:
          url: "/api/agents"
          method: "POST"
          body: {"name": "test_agent", "type": "assistant"}
          headers:
            Authorization: "Bearer {{login.response.json.token}}"
        success_criteria: "status == 201"
    schedule: "5m"
```

## SLO Monitoring

Service Level Objective (SLO) monitoring:

```yaml
slos:
  request_latency:
    description: "Request latency SLO"
    metric: "app.request.duration"
    target: "99% of requests < 200ms"
    window: "30d"
    alerting:
      budget_burn_rate:
        - burn_rate: 1
          alert_after: "1h"
          severity: "info"
        - burn_rate: 10
          alert_after: "5m"
          severity: "critical"
```

## Configuration

The monitoring system is configured through the unified configuration schema:

```yaml
observability:
  monitoring:
    dashboards:
      enabled: true
      refresh_interval: "1m"
      default_timezone: "UTC"
      custom_dashboards_path: "/path/to/custom/dashboards"
    alerting:
      enabled: true
      evaluation_interval: "1m"
      notification_channels:
        slack:
          enabled: true
          webhook_url: "${SLACK_WEBHOOK_URL}"
          channel: "#alerts"
        email:
          enabled: true
          from: "alerts@example.com"
          to: ["team@example.com"]
          smtp:
            host: "smtp.example.com"
            port: 587
            username: "${SMTP_USERNAME}"
            password: "${SMTP_PASSWORD}"
        pagerduty:
          enabled: false
          integration_key: "${PAGERDUTY_KEY}"
    health_checks:
      enabled: true
      path: "/health"
      include_details: true
    status_page:
      enabled: true
      path: "/status"
      public: false
```

## Integration with External Systems

The monitoring system integrates with these external tools:

- **Grafana**: Dashboard visualization
- **Prometheus AlertManager**: Alert management
- **PagerDuty**: On-call management
- **Slack**: Notification delivery
- **StatusPage**: Status page hosting

## Monitoring Patterns

### Multi-Signal Correlation

Correlating signals across observability data:

```yaml
dashboard:
  name: "Request Analysis"
  panels:
    - title: "Request Rate"
      metric: "app.requests.rate"
      type: "time_series"
    - title: "Error Rate"
      metric: "app.errors.rate"
      type: "time_series"
    - title: "Latency"
      metric: "app.request.duration"
      type: "heatmap"
    - title: "Related Logs"
      source: "logs"
      query: "level:ERROR"
      type: "table"
    - title: "Traces"
      source: "traces"
      query: "error=true"
      type: "traces"
```

### SLI/SLO Monitoring

Service Level Indicator/Objective monitoring:

```yaml
sli_dashboard:
  name: "Service SLOs"
  slis:
    - name: "Availability"
      description: "Service availability"
      metric: "app.availability"
      target: 99.9
      time_window: "30d"
      alert_threshold: 99.5
    - name: "Latency"
      description: "Request latency"
      metric: "app.request.duration"
      target: 99
      threshold: "200ms"
      time_window: "30d"
      alert_threshold: 98
```

## References

- [Observability Architecture](/refactoring_work/00b_overview/12_observability/architecture.md)
- [Logging Subsystem](/refactoring_work/00b_overview/12_observability/logging/README.md)
- [Metrics Collection](/refactoring_work/00b_overview/12_observability/metrics/README.md)
- [Distributed Tracing](/refactoring_work/00b_overview/12_observability/tracing/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
