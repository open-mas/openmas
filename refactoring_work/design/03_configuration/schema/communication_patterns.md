# Communication Patterns Configuration Documentation

## Overview

> **IMPORTANT NOTE**: This document does NOT define the communication patterns configuration schema. It only provides documentation and examples for the communication patterns section defined in the [Unified Configuration Schema](../unified_configuration_schema.md), which is the single source of truth for all schema definitions.

This document explains the communication patterns configuration sections in the unified schema, which define standardized message exchange methods and their protocol-specific adaptations.

## Schema Structure

The communication patterns configuration is structured in two main locations:

1. **Global Pattern Definitions** - Define patterns available to all agents
2. **Agent-Specific Pattern Configurations** - Configure patterns for specific agents

## Global Pattern Definitions

Global pattern definitions are specified in the top-level `communication_patterns` section of the unified configuration schema:

```yaml
communication_patterns:
  request_response:
    options:
      timeout: 30000
      retry:
        attempts: 3
      security:
        require_authentication: true
    protocol_adaptations:
      a2a:
        use_streaming: false
      http:
        method: "POST"
  
  publish_subscribe:
    options:
      delivery_guarantee: "at_least_once"
      topic_persistence: true
      message_ttl: 86400
    protocol_adaptations:
      mqtt:
        qos_level: 1
        retain: true
  
  event_based:
    options:
      event_history_size: 100
      filtering_enabled: true
  
  streaming:
    options:
      buffer_size: 1024
      chunk_size: 64
  
  pipeline:
    options:
      stage_timeout: 60000
      error_handling: "continue" # or "abort"
  
  delegation:
    options:
      delegation_timeout: 120000
      authority_verification: true
```

## Agent-Specific Pattern Configurations

Agents can override or extend global pattern configurations:

```yaml
agents:
  travel_coordinator:
    communicator_type: "a2a"
    patterns:
      request_response:
        options:
          timeout: 15000  # Override global timeout
          retry:
            attempts: 5   # Override global retry attempts
        protocol_adaptations:
          a2a:
            use_streaming: true  # Override global A2A setting
      
      # Use other patterns with default configuration
      publish_subscribe: {}
      event_based: {}
```

## Pattern Option Schema Reference

### Request-Response Pattern Schema

The Request-Response pattern supports these configuration options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `timeout` | integer | Request timeout in milliseconds | 30000 |
| `retry.attempts` | integer | Number of retry attempts | 3 |
| `retry.backoff_factor` | number | Exponential backoff multiplier | 1.5 |
| `retry.max_backoff` | integer | Maximum backoff time in milliseconds | 60000 |
| `correlation.use_id` | boolean | Use correlation IDs for requests | true |
| `correlation.id_format` | string | Format for correlation IDs | "uuid" |
| `security.require_authentication` | boolean | Require authentication | true |
| `security.auth_method` | string | Authentication method | "bearer" |
| `metadata.include_timestamp` | boolean | Include timestamps in messages | true |

### Publish-Subscribe Pattern Schema

The Publish-Subscribe pattern supports these configuration options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `delivery_guarantee` | string | Delivery guarantee level (at_most_once, at_least_once, exactly_once) | "at_least_once" |
| `topic_persistence` | boolean | Whether topics should persist without subscribers | false |
| `message_ttl` | integer | Time-to-live for messages in seconds | 86400 |
| `subscription_handling.auto_ack` | boolean | Auto-acknowledge received messages | true |
| `subscription_handling.buffer_size` | integer | Size of message buffer | 100 |
| `subscription_handling.overflow_strategy` | string | Strategy when buffer is full (drop_oldest, drop_newest, block) | "drop_oldest" |

### Event-Based Pattern Schema

The Event-Based pattern supports these configuration options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `event_history_size` | integer | Number of events to retain | 100 |
| `filtering_enabled` | boolean | Enable event filtering | true |
| `filter_expression_format` | string | Format for filter expressions | "simple" |
| `default_priority` | string | Default priority for events | "normal" |
| `event_correlation.enabled` | boolean | Enable event correlation | false |
| `event_correlation.window_size` | integer | Correlation window size in seconds | 60 |
| `event_correlation.strategy` | string | Correlation strategy | "temporal" |

### Streaming Pattern Schema

The Streaming pattern supports these configuration options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `buffer_size` | integer | Stream buffer size in KB | 1024 |
| `chunk_size` | integer | Size of each chunk in KB | 64 |
| `flow_control.enabled` | boolean | Enable flow control | true |
| `flow_control.high_water_mark` | integer | High water mark percentage | 80 |
| `flow_control.low_water_mark` | integer | Low water mark percentage | 20 |
| `compression.enabled` | boolean | Enable stream compression | false |
| `compression.algorithm` | string | Compression algorithm | "gzip" |
| `timeout` | integer | Stream timeout in milliseconds | 300000 |

### Pipeline Pattern Schema

The Pipeline pattern supports these configuration options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `stage_timeout` | integer | Timeout for each stage in milliseconds | 60000 |
| `error_handling` | string | How to handle errors (continue, abort) | "continue" |
| `retry.enabled` | boolean | Enable stage retry | true |
| `retry.max_attempts` | integer | Maximum retry attempts per stage | 3 |
| `monitoring.collect_metrics` | boolean | Collect performance metrics | true |
| `monitoring.stage_completion_events` | boolean | Emit events on stage completion | true |
| `state_persistence.enabled` | boolean | Persist pipeline state | false |
| `state_persistence.strategy` | string | State persistence strategy | "snapshot" |

### Delegation Pattern Schema

The Delegation pattern supports these configuration options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `delegation_timeout` | integer | Delegation timeout in milliseconds | 120000 |
| `authority_verification` | boolean | Verify delegation authority | true |
| `verification_method` | string | Method for authority verification | "token" |
| `status_updates.enabled` | boolean | Enable status updates from delegate | true |
| `status_updates.frequency` | string | Update frequency (on_change, interval) | "on_change" |
| `status_updates.interval` | integer | Update interval in seconds if frequency is interval | 30 |
| `revocation.enabled` | boolean | Allow delegation revocation | true |
| `revocation.grace_period` | integer | Grace period in seconds for revocation | 5 |

## Protocol Adaptation Schema

Protocol adaptations define how patterns map to specific protocols:

```yaml
communication_patterns:
  request_response:
    protocol_adaptations:
      a2a:
        use_streaming: false
        use_agent_cards: true
        error_response_format: "standard"
      
      http:
        method: "POST"
        response_codes: [200, 201]
        content_type: "application/json"
        timeout_header: "X-Request-Timeout"
      
      grpc:
        service_method: "Invoke"
        timeout_metadata: "request-timeout"
        use_streaming: false
      
      mcp:
        function_call_based: true
        timeout_metadata: "timeout"
      
      mqtt:
        request_topic_format: "{agent_id}/request/{correlation_id}"
        response_topic_format: "{agent_id}/response/{correlation_id}"
        qos_level: 1
```

Each protocol adaptation defines protocol-specific options that determine how a particular pattern is implemented over that protocol.

## Custom Pattern Extensions

OpenMAS supports custom pattern extensions through the extension system. Custom patterns follow the same configuration structure:

```yaml
communication_patterns:
  custom_pattern:
    options:
      standard_option: "value"
      x-vendor-option: "custom value"
    protocol_adaptations:
      http:
        x-custom-header: "header-value"
```

Custom options and protocol adaptations should be prefixed with `x-` to avoid conflicts with core options.

## References

- [Communication Patterns Architecture](/refactoring_work/00b_overview/01_architecture/communication_patterns_architecture.md)
- [Communication Patterns Documentation](/refactoring_work/00b_overview/07_communication_patterns/)
- [Unified Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
