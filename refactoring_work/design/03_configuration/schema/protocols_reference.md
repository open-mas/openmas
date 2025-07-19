# Protocol Configuration Reference

## Overview

> **IMPORTANT NOTE**: This document does NOT define the protocol configuration schema. It only provides reference information and examples for the protocol configuration sections defined in the [Unified Configuration Schema](../unified_configuration_schema.md), which is the single source of truth for all schema definitions.

This document provides detailed reference information for protocol-specific configuration in OpenMAS, explaining the configurations already defined in the [Unified Configuration Schema](../unified_configuration_schema.md).

## Protocol Configuration Structure

All protocol configuration follows this basic structure in the unified schema:

```yaml
communicator:
  # Protocol selection
  protocol: "a2a" | "mcp" | "http" | "mqtt" | "grpc"
  
  # Transport configuration
  transport:
    # Transport-specific settings
    
  # Protocol-specific settings
  a2a: { ... }  # Only present when protocol is "a2a"
  mcp: { ... }  # Only present when protocol is "mcp"
  http: { ... } # Only present when protocol is "http"
  mqtt: { ... } # Only present when protocol is "mqtt"
  grpc: { ... } # Only present when protocol is "grpc"
  
  # Common settings
  auth: { ... }
  discovery: { ... }
```

## A2A Protocol Configuration

The A2A protocol configuration focuses on agent cards, capability advertisement, and task management:

```yaml
communicator:
  protocol: "a2a"
  transport:
    type: "http" | "websocket"
    http:
      host: "0.0.0.0"
      port: 8080
      cors_origins: ["*"]
  a2a:
    agent_card:
      name: "Assistant Agent"
      description: "An assistant agent that can answer questions"
      version: "1.0.0"
      contact:
        name: "OpenMAS Team"
        email: "info@openmas.org"
    features:
      streaming: true
      push_notifications: false
      binary_data: true
    task_management:
      storage: "memory" | "redis"
      redis_url: "redis://localhost:6379"  # Only for redis storage
  auth:
    required: true
    types: ["bearer", "basic"]
```

### A2A Configuration Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `a2a.agent_card.name` | string | Name of the agent | Required |
| `a2a.agent_card.description` | string | Description of the agent | Required |
| `a2a.agent_card.version` | string | Version of the agent | "1.0.0" |
| `a2a.agent_card.contact` | object | Contact information | {} |
| `a2a.features.streaming` | boolean | Support for streaming responses | false |
| `a2a.features.push_notifications` | boolean | Support for push notifications | false |
| `a2a.features.binary_data` | boolean | Support for binary data | true |
| `a2a.task_management.storage` | string | Storage backend for tasks | "memory" |

## MCP Protocol Configuration

The MCP protocol configuration focuses on tool registration, resource access, and model context management:

```yaml
communicator:
  protocol: "mcp"
  transport:
    type: "sse" | "websocket" | "stdio"
    sse:
      url: "http://localhost:8080/mcp"
    stdio: {}
  mcp:
    tools:
      - name: "weather_tool"
        description: "Get weather information"
      - name: "calculator_tool"
        description: "Perform calculations"
    resources:
      providers:
        - name: "file_provider"
          type: "file"
          root_dir: "/path/to/resources"
        - name: "url_provider"
          type: "url"
          allowed_domains: ["example.com"]
    session:
      storage: "memory" | "redis"
      redis_url: "redis://localhost:6379"  # Only for redis storage
  auth:
    required: false
```

### MCP Configuration Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `mcp.tools` | array | List of tools to register | [] |
| `mcp.tools[].name` | string | Name of the tool | Required |
| `mcp.tools[].description` | string | Description of the tool | Required |
| `mcp.resources.providers` | array | List of resource providers | [] |
| `mcp.resources.providers[].name` | string | Name of the provider | Required |
| `mcp.resources.providers[].type` | string | Type of provider | Required |
| `mcp.session.storage` | string | Storage backend for sessions | "memory" |

## HTTP Protocol Configuration

```yaml
communicator:
  protocol: "http"
  transport:
    http:
      host: "0.0.0.0"
      port: 8080
      cors_origins: ["*"]
  http:
    endpoints:
      - path: "/api/v1/query"
        method: "POST"
        handler: "query_handler"
      - path: "/api/v1/status"
        method: "GET"
        handler: "status_handler"
    middleware:
      - "logging"
      - "rate_limiter"
      - "auth"
  auth:
    required: true
    types: ["bearer"]
```

## MQTT Protocol Configuration

```yaml
communicator:
  protocol: "mqtt"
  transport:
    mqtt:
      broker: "mqtt://localhost:1883"
      client_id: "openmas-agent"
      keep_alive: 60
  mqtt:
    topics:
      subscribe:
        - "agents/+/requests"
      publish:
        - "agents/{{agent_id}}/responses"
    qos: 1
    retain: false
  auth:
    required: true
    username: "mqtt_user"
    password: "mqtt_password"
```

## gRPC Protocol Configuration

```yaml
communicator:
  protocol: "grpc"
  transport:
    grpc:
      host: "0.0.0.0"
      port: 50051
  grpc:
    proto_file: "agent.proto"
    services:
      - name: "AgentService"
        methods:
          - name: "ProcessQuery"
            handler: "query_handler"
          - name: "GetStatus"
            handler: "status_handler"
    max_message_size: 4194304  # 4MB
  auth:
    required: true
    types: ["oauth"]
```

## Multi-Protocol Configuration

OpenMAS supports configuring multiple protocols for a single agent:

```yaml
communicators:
  - name: "a2a_communicator"
    protocol: "a2a"
    transport:
      type: "http"
      http:
        host: "0.0.0.0"
        port: 8080
    a2a:
      agent_card:
        name: "Multi-Protocol Agent"
        
  - name: "mcp_communicator"
    protocol: "mcp"
    transport:
      type: "sse"
      sse:
        url: "http://localhost:8081/mcp"
    mcp:
      tools:
        - name: "weather_tool"
```

## Protocol-Pattern Mapping

For a complete mapping between protocols and communication patterns, see:

- [Protocol to Pattern Mapping](/refactoring_work/00b_overview/02_protocols/protocol_to_pattern_mapping.md)

## References

- [Unified Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md) - **PRIMARY REFERENCE**
- [Protocol Documentation](/refactoring_work/00b_overview/02_protocols/README.md) - Protocol specification details
- [Communication Patterns](/refactoring_work/00b_overview/07_communication_patterns/README.md) - Pattern implementation details
