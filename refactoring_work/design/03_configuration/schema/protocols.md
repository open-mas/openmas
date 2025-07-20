# Protocol Configuration Documentation

> **IMPORTANT NOTE**: This document does NOT define the protocol configuration schema. It only provides documentation and examples for the protocol configuration sections defined in the [Unified Configuration Schema](../unified_configuration_schema.md), which is the single source of truth for all schema definitions.

## Protocol and Communicator Types

OpenMAS supports multiple protocol types through its communicator architecture:

| Protocol | Description | Transport Types |
|----------|-------------|------------------|
| MCP | Model Context Protocol | stdio, SSE, streamable |
| A2A | Agent-to-Agent Protocol | HTTP, WebSocket, gRPC |
| HTTP | Standard HTTP REST | HTTP |
| gRPC | Google RPC | gRPC |
| MQTT | Message Queuing Telemetry Transport | MQTT |
| WebSocket | WebSocket Protocol | WebSocket |

Each protocol maintains OpenMAS's reasoning agnostic design by separating communication infrastructure from reasoning approaches.

## Protocol Configuration Components

The protocol configuration is defined in two main locations within the [Unified Configuration Schema](../unified_configuration_schema.md):

1. **Global defaults**: Under `defaults.protocols` section
2. **Agent-specific**: Under `agents.[agent_id].protocols` arrays for each agent

The following sections explain key protocol configuration components but do not define the schema itself.

### Core Protocol Properties

These properties define the basic protocol interface for an agent:

- **type**: Protocol identifier (e.g., "mcp-sse", "a2a-http", "grpc")
- **enabled**: Whether the protocol interface is active

See the `agents.[agent_id].protocols` array items in the [Unified Configuration Schema](../unified_configuration_schema.md) for the complete definition.

### A2A Protocol Options

Key configuration options for the Agent-to-Agent protocol include:

- **base_url**: The base URL for the A2A endpoint
- **agent_card**: Configuration for the A2A discovery mechanism
  - **name**: Agent name
  - **description**: Agent purpose
  - **capabilities**: Capabilities exposed via A2A
  - **supported_features**: Protocol features supported
  - **auth_requirements**: Authentication requirements
  - **discovery**: Configuration for agent discovery

See the `agents.[agent_id].protocols[].options` (where type is an A2A variant) in the [Unified Configuration Schema](../unified_configuration_schema.md) for the complete definition.

### MCP Protocol Options

Key configuration options for the Model Context Protocol include:

- **server_mode**: Whether to run in server mode
- **client_mode**: Whether to run in client mode
- **stream_mode**: Streaming mode for MCP (sse, websocket, stdio)
- **http_port**: HTTP port for MCP server
- **tool_registration**: How tools are registered with the agent

See the `agents.[agent_id].protocols[].options` (where type is an MCP variant) in the [Unified Configuration Schema](../unified_configuration_schema.md) for the complete definition.

### HTTP Protocol Options

Key configuration options for the HTTP protocol include:

- **port**: HTTP port
- **timeout_ms**: Request timeout in milliseconds
- **headers**: Default headers for HTTP requests
- **cors_origins**: Allowed CORS origins
- **middleware**: HTTP middleware configuration

See the `agents.[agent_id].protocols[].options` (where type is "http") in the [Unified Configuration Schema](../unified_configuration_schema.md) for the complete definition.

### MQTT Protocol Options

Key configuration options for MQTT include:

- **broker_url**: MQTT broker URL
- **mqtt_port**: MQTT broker port
- **client_id**: MQTT client identifier

See the `agents.[agent_id].protocols[].options` (where type is "mqtt") in the [Unified Configuration Schema](../unified_configuration_schema.md) for the complete definition.
            type: string
            description: "MQTT client ID"
          topic_prefix:
            type: string
            description: "Prefix for all MQTT topics"
          qos:
            type: integer
            description: "MQTT Quality of Service level"
            enum: [0, 1, 2]
            default: 1

          # gRPC Protocol Options
          grpc_port:
            type: integer
            description: "gRPC server port"
            default: 50051
          max_message_size:
            type: integer
            description: "Maximum message size in bytes"
          service_definitions:
            type: array
            description: "gRPC service definitions"
            items:
              type: string
```

## Protocol Configurations

### A2A Protocol Configuration

Configuration for Agent-to-Agent Protocol:

```yaml
protocols:
  - type: "a2a-http"
    enabled: true
    options:
      base_url: "https://agent-api.example.com"
      agent_card:
        name: "data_analysis_agent"
        display_name: "Data Analysis Agent"
        description: "Performs statistical analysis on datasets"
        version: "1.0.0"
        capabilities:
          - name: "analyze_dataset"
            description: "Analyzes a dataset and returns statistical insights"
            parameters:
              type: "object"
              properties:
                dataset_url:
                  type: "string"
                  description: "URL to the dataset"
                analysis_type:
                  type: "string"
                  enum: ["basic", "advanced", "predictive"]
            returns:
              type: "object"
              properties:
                insights:
                  type: "array"
                  items:
                    type: "object"
                    properties:
                      name:
                        type: "string"
                      value:
                        type: "number"
                      explanation:
                        type: "string"
        supported_features:
          streaming: true
          push_notifications: false
        auth_requirements:
          required: true
          types: ["api_key"]
        discovery:
          published: true
          well_known_path: "/.well-known/agent.json"
```

### MCP Protocol Configuration

Configuration for Model Context Protocol:

```yaml
protocols:
  - type: "mcp-sse"
    enabled: true
    options:
      server_mode: true
      http_port: 8000
      server_name: "data_processing_agent"
      server_instructions: "This agent helps with data processing tasks."
      tool_registration: "auto"
      stream_mode: "sse"
```

### HTTP Protocol Configuration

Configuration for HTTP communication:

```yaml
protocols:
  - type: "http"
    enabled: true
    options:
      port: 8080
      timeout_ms: 30000
      headers:
        User-Agent: "OpenMAS/0.3.0"
        Accept: "application/json"
      cors_origins:
        - "https://example.com"
        - "https://api.example.com"
      middleware:
        - name: "logging"
          enabled: true
        - name: "authentication"
          enabled: true
          type: "jwt"
```

### MQTT Protocol Configuration

Configuration for MQTT messaging:

```yaml
protocols:
  - type: "mqtt"
    enabled: true
    options:
      broker_url: "mqtt://broker.example.com"
      mqtt_port: 1883
      client_id: "agent_1234"
      topic_prefix: "openmas/agents"
      qos: 1
```

### gRPC Protocol Configuration

Configuration for gRPC communication:

```yaml
protocols:
  - type: "grpc"
    enabled: true
    options:
      grpc_port: 50051
      max_message_size: 10485760  # 10MB
      service_definitions:
        - "services/agent_service.proto"
```

## Protocol Configuration in Agents

Protocol configuration within agent definitions:

```yaml
agents:
  weather_agent:
    class: "agents.weather.WeatherAgent"
    type: "hybrid"

    # Protocol configuration
    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8000"
          agent_card:
            name: "Weather Agent"
            description: "Provides weather forecasts and alerts"

      - type: "mcp-sse"
        enabled: true
        options:
          client_mode: true
          server_name: "weather_tools"

      - type: "mqtt"
        enabled: true
        options:
          topic_prefix: "openmas/weather"
```

## Default Protocol Configuration

Global defaults for protocols:

```yaml
defaults:
  protocols:
    a2a:
      auth_required: true
      auth_provider: "api_key"
    mcp:
      server_instructions: "Default server instructions"
      tool_registration: "auto"
    http:
      timeout_ms: 30000
    mqtt:
      qos: 1
    grpc:
      max_message_size: 4194304  # 4MB
```
