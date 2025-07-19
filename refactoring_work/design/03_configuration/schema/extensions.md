# Extensions Configuration Documentation

## Overview

> **IMPORTANT NOTE**: This document does NOT define the extensions configuration schema. It only provides documentation and examples for the extensions configuration section defined in the [Unified Configuration Schema](../unified_configuration_schema.md), which is the single source of truth for all schema definitions.

This document explains the extensions configuration section in the unified schema, which enables the OpenMAS extension system to maintain consistency across all extension types while preserving reasoning agnosticism.

## Schema Definition

```yaml
# Extensions Configuration Schema
type: object
properties:
  extensions:
    type: object
    description: "Configuration for all extensions in the system"
    additionalProperties:
      type: object
      properties:
        type:
          type: string
          description: "The extension type (e.g., agent, communicator, asset)"
          enum:
            - "agent"
            - "communicator"
            - "asset"
            - "prompt"
            - "llm"
            - "reasoning"
            - "protocol"
            - "protocol_adapter"
            - "tool"
        name:
          type: string
          description: "Unique identifier for the extension"
        enabled:
          type: boolean
          description: "Whether the extension is enabled"
          default: true
        options:
          type: object
          description: "Extension-specific configuration options"
        depends_on:
          type: array
          description: "List of extensions this extension depends on"
          items:
            type: string
        protocols:
          type: array
          description: "Supported protocols for protocol-aware extensions"
          items:
            type: object
            properties:
              type:
                type: string
                description: "Protocol type"
                enum:
                  - "a2a"
                  - "mcp"
                  - "http"
                  - "mqtt"
                  - "grpc"
                  - "websocket"
              enabled:
                type: boolean
                description: "Whether this protocol is enabled"
                default: true
              options:
                type: object
                description: "Protocol-specific options"
        isolation:
          type: object
          description: "Isolation settings for the extension"
          properties:
            level:
              type: string
              description: "Isolation level"
              enum:
                - "none"
                - "namespace"
                - "process"
                - "container"
              default: "namespace"
            timeout:
              type: integer
              description: "Maximum execution time in seconds"
              default: 30
            memory_limit:
              type: integer
              description: "Maximum memory usage in MB"
              default: 256
            file_access:
              type: object
              properties:
                allowed_paths:
                  type: array
                  items:
                    type: string
                denied_paths:
                  type: array
                  items:
                    type: string
            network_access:
              type: object
              properties:
                allowed_hosts:
                  type: array
                  items:
                    type: string
                denied_hosts:
                  type: array
                  items:
                    type: string
        permissions:
          type: array
          description: "List of permissions required by the extension"
          items:
            type: string
            enum:
              - "network.connect"
              - "network.listen"
              - "file.read"
              - "file.write"
              - "agent.capability.invoke"
              - "agent.capability.register"
              - "extension.load"
              - "system.exec"
        monitoring:
          type: object
          description: "Monitoring configuration for the extension"
          properties:
            enabled:
              type: boolean
              default: true
            log_level:
              type: string
              enum:
                - "debug"
                - "info"
                - "warning"
                - "error"
              default: "info"
            rate_limits:
              type: object
              properties:
                network_requests:
                  type: integer
                  description: "Maximum network requests per minute"
                capability_invocations:
                  type: integer
                  description: "Maximum capability invocations per minute"
            anomaly_detection:
              type: object
              properties:
                enabled:
                  type: boolean
                  default: true
                sensitivity:
                  type: string
                  enum:
                    - "low"
                    - "medium"
                    - "high"
                  default: "medium"
      required:
        - "type"
        - "name"
```

## Extension Type-Specific Schemas

### Agent Extensions

```yaml
# Agent Extension Schema
type: object
properties:
  type:
    type: string
    enum: ["agent"]
  name:
    type: string
  enabled:
    type: boolean
    default: true
  options:
    type: object
    properties:
      capabilities:
        type: array
        items:
          type: object
          properties:
            name:
              type: string
              description: "Capability name"
            description:
              type: string
              description: "Capability description"
            parameters:
              type: object
              description: "Parameters schema for the capability"
            returns:
              type: object
              description: "Return value schema for the capability"
          required:
            - "name"
      handlers:
        type: array
        items:
          type: object
          properties:
            event:
              type: string
              description: "Event name to handle"
            handler:
              type: string
              description: "Handler method name"
          required:
            - "event"
            - "handler"
```

### Communicator Extensions

```yaml
# Communicator Extension Schema
type: object
properties:
  type:
    type: string
    enum: ["communicator"]
  name:
    type: string
  enabled:
    type: boolean
    default: true
  options:
    type: object
    properties:
      transport:
        type: string
        description: "Transport mechanism (http, websocket, etc.)"
      url:
        type: string
        description: "Connection URL"
      timeout:
        type: integer
        description: "Connection timeout in seconds"
      reconnect:
        type: object
        properties:
          attempts:
            type: integer
            description: "Number of reconnection attempts"
          interval:
            type: integer
            description: "Interval between attempts in milliseconds"
      tls:
        type: object
        properties:
          enabled:
            type: boolean
            description: "Whether TLS is enabled"
          cert_file:
            type: string
            description: "Path to certificate file"
          key_file:
            type: string
            description: "Path to key file"
          ca_file:
            type: string
            description: "Path to CA certificate file"
```

### Asset Extensions

```yaml
# Asset Extension Schema
type: object
properties:
  type:
    type: string
    enum: ["asset"]
  name:
    type: string
  enabled:
    type: boolean
    default: true
  options:
    type: object
    properties:
      base_directory:
        type: string
        description: "Base directory for assets"
      supported_types:
        type: array
        description: "Asset types supported by this provider"
        items:
          type: string
      caching:
        type: object
        properties:
          enabled:
            type: boolean
            description: "Whether caching is enabled"
          max_size:
            type: integer
            description: "Maximum cache size in MB"
          ttl:
            type: integer
            description: "Cache TTL in seconds"
```

### Prompt Extensions

```yaml
# Prompt Extension Schema
type: object
properties:
  type:
    type: string
    enum: ["prompt"]
  name:
    type: string
  enabled:
    type: boolean
    default: true
  options:
    type: object
    properties:
      template_directory:
        type: string
        description: "Directory containing prompt templates"
      default_template:
        type: string
        description: "Default template name"
      variables:
        type: object
        description: "Global variables for prompt templates"
        additionalProperties:
          type: string
```

### Reasoning Extensions

```yaml
# Reasoning Extension Schema
type: object
properties:
  type:
    type: string
    enum: ["reasoning"]
  name:
    type: string
  enabled:
    type: boolean
    default: true
  options:
    type: object
    properties:
      approach:
        type: string
        description: "Primary reasoning approach"
        enum: ["llm", "rule_based", "hybrid", "bdi", "symbolic"]
      knowledge_representation:
        type: string
        description: "Knowledge representation format"
        enum: ["symbolic", "graph", "vector", "probabilistic", "neural", "hybrid"]
      inference_engine:
        type: object
        description: "Configuration for the inference engine"
        properties:
          type:
            type: string
            description: "Type of inference engine"
          options:
            type: object
            description: "Engine-specific options"
```

### Protocol Extensions

```yaml
# Protocol Extension Schema
type: object
properties:
  type:
    type: string
    enum: ["protocol"]
  name:
    type: string
  enabled:
    type: boolean
    default: true
  options:
    type: object
    properties:
      protocol_type:
        type: string
        description: "Type of protocol implementation"
        enum: ["custom", "standard", "extended"]
      transport:
        type: string
        description: "Transport mechanism"
        enum: ["http", "websocket", "mqtt", "grpc", "custom"]
      configuration:
        type: object
        description: "Protocol-specific configuration"
      security:
        type: object
        description: "Protocol security settings"
        properties:
          authentication:
            type: object
            description: "Authentication configuration"
          authorization:
            type: object
            description: "Authorization configuration"
```

### LLM Extensions

```yaml
# LLM Extension Schema
type: object
properties:
  type:
    type: string
    enum: ["llm"]
  name:
    type: string
  enabled:
    type: boolean
    default: true
  options:
    type: object
    properties:
      provider:
        type: string
        description: "LLM provider name"
      api_key:
        type: string
        description: "API key for the LLM provider"
      model:
        type: string
        description: "Model identifier"
      endpoint:
        type: string
        description: "API endpoint URL"
      parameters:
        type: object
        properties:
          temperature:
            type: number
            description: "Temperature parameter for generation"
          max_tokens:
            type: integer
            description: "Maximum tokens to generate"
          stop_sequences:
            type: array
            description: "Sequences that stop generation"
            items:
              type: string
      caching:
        type: object
        properties:
          enabled:
            type: boolean
            description: "Whether response caching is enabled"
          ttl:
            type: integer
            description: "Cache TTL in seconds"
```

### Protocol Adapter Extensions

```yaml
# Protocol Adapter Extension Schema
type: object
properties:
  type:
    type: string
    enum: ["protocol_adapter"]
  name:
    type: string
  enabled:
    type: boolean
    default: true
  options:
    type: object
    properties:
      source_protocol:
        type: string
        description: "Source protocol"
        enum:
          - "a2a"
          - "mcp"
          - "http"
          - "mqtt"
          - "grpc"
          - "websocket"
      target_protocol:
        type: string
        description: "Target protocol"
        enum:
          - "a2a"
          - "mcp"
          - "http"
          - "mqtt"
          - "grpc"
          - "websocket"
      mapping:
        type: object
        description: "Field mapping between protocols"
        additionalProperties:
          type: string
```

### Tool Extensions

```yaml
# Tool Extension Schema
type: object
properties:
  type:
    type: string
    enum: ["tool"]
  name:
    type: string
  enabled:
    type: boolean
    default: true
  options:
    type: object
    properties:
      api_key:
        type: string
        description: "API key for external service"
      api_url:
        type: string
        description: "URL for external service"
      timeout:
        type: integer
        description: "Request timeout in seconds"
      definition:
        type: object
        description: "Tool definition schema"
        properties:
          name:
            type: string
            description: "Tool name"
          description:
            type: string
            description: "Tool description"
          parameters:
            type: object
            description: "Parameters schema"
          returns:
            type: object
            description: "Return value schema"
```

## Configuration Examples

### Basic Agent Extension

```yaml
extensions:
  collaborative_agent:
    type: "agent"
    name: "collaborative_agent"
    enabled: true
    options:
      capabilities:
        - name: "collaborate"
          description: "Collaborate with other agents"
          parameters:
            type: "object"
            properties:
              task:
                type: "string"
                description: "Task to collaborate on"
              agents:
                type: "array"
                items:
                  type: "string"
                description: "Agents to collaborate with"
          returns:
            type: "object"
            properties:
              result:
                type: "string"
                description: "Collaboration result"
      handlers:
        - event: "request"
          handler: "handle_request"
```

### Custom Communicator Extension

```yaml
extensions:
  mqtt_communicator:
    type: "communicator"
    name: "mqtt"
    enabled: true
    options:
      transport: "mqtt"
      url: "mqtt://broker.example.com:1883"
      timeout: 30
      reconnect:
        attempts: 5
        interval: 1000
      tls:
        enabled: true
        cert_file: "/path/to/cert.pem"
        key_file: "/path/to/key.pem"
    protocols:
      - type: "a2a"
        enabled: true
        options:
          capability_format: "json"
      - type: "mcp"
        enabled: true
        options:
          tool_format: "json"
```

### Advanced LLM Extension

```yaml
extensions:
  advanced_llm:
    type: "llm"
    name: "advanced_llm"
    enabled: true
    options:
      provider: "custom_provider"
      api_key: "${CUSTOM_LLM_API_KEY}"
      model: "advanced-model-v2"
      endpoint: "https://api.custom-llm.example.com/v2"
      parameters:
        temperature: 0.7
        max_tokens: 2048
        stop_sequences:
          - "END_OF_RESPONSE"
          - "---"
      caching:
        enabled: true
        ttl: 3600
    isolation:
      level: "process"
      timeout: 60
      memory_limit: 1024
    permissions:
      - "network.connect"
```

## Protocol Independence

The extensions configuration schema supports protocol independence through:

1. **Protocol-Specific Options** - Each extension can have protocol-specific configuration
2. **Protocol Adapters** - Protocol adapter extensions bridge between different protocols
3. **Protocol-Agnostic Core** - Core extension functionality is protocol-independent
4. **Dynamic Protocol Selection** - Extensions can be configured to use different protocols at runtime

This ensures that extensions can operate with any supported protocol.

## Reasoning Agnosticism

The extensions configuration schema maintains OpenMAS's reasoning agnosticism by:

1. **Separation of Concerns** - Extension configurations focus on functionality, not reasoning approaches
2. **Abstract Interfaces** - Configuration references abstract interfaces, not concrete implementations
3. **Uniform Configuration** - Same configuration pattern works for any reasoning approach
4. **Protocol Independence** - Extensions can be configured to work with any protocol

This enables extensions to be configured consistently regardless of the reasoning approach being used (rule-based, BDI, LLM-based, hybrid, etc.).
