# Unified Configuration Schema for OpenMAS

Single source of truth for all OpenMAS configurations.

## Schema Definition
- **Name**: Unified Configuration Schema
- **Purpose**: Standardized approach to configuring all OpenMAS components in a coherent manner
- **Protocol Compatibility**: Supports all protocols (A2A, MCP, HTTP, MQTT, gRPC)
- **Component Integration**: Defines consistent integration points between all components

## Unified Schema
```yaml
# Unified OpenMAS configuration schema
type: object
properties:
  # Project metadata
  name:
    type: string
    description: "Name of the OpenMAS project"
  version:
    type: string
    description: "Version of the project"
  description:
    type: string
    description: "Description of the project"

  # Global default configuration
  defaults:
    type: object
    description: "Default configuration for all components"
    properties:
      # Common settings
      common:
        type: object
        description: "Common settings for all components"
        properties:
          log_level:
            type: string
            description: "Default log level"
            enum: ["error", "warning", "info", "debug"]
            default: "info"

      # Default topology configuration
      # For detailed implementation, see: /01_architecture/topology_design.md
      topology:
        type: object
        description: "Global topology configuration"
        # Detailed implementation documentation at: /01_architecture/topology_design.md and /01_architecture/topology_patterns/
        properties:
          pattern:
            type: string
            description: "Topology pattern type"
            enum: ["centralized", "peer_to_peer", "hierarchical", "mesh", "hybrid"]
            default: "centralized"
          roles:
            type: object
            description: "Role definitions within the topology"
            properties:
              types:
                type: array
                description: "Defined roles in this topology"
                items:
                  type: object
                  properties:
                    name:
                      type: string
                      description: "Role name"
                    description:
                      type: string
                      description: "Role description"
          relationships:
            type: object
            description: "Relationship types within the topology"
            properties:
              types:
                type: array
                description: "Defined relationship types"
                items:
                  type: object
                  properties:
                    name:
                      type: string
                      description: "Relationship name"
                    description:
                      type: string
                      description: "Relationship description"
                    communication_pattern:
                      type: string
                      description: "Default communication pattern for this relationship"
                      enum: ["request_response", "publish_subscribe", "streaming", "event_based", "pipeline", "delegation"]

      # Default communication patterns
      communication_patterns:
        type: object
        description: "Default communication patterns configuration"
        additionalProperties:
          type: object
          properties:
            options:
              type: object
              description: "Pattern-specific options"
            protocol_adaptations:
              type: object
              description: "Protocol-specific adaptations"

      # Default protocol configuration
      protocols:
        type: object
        description: "Default protocol configuration"
        properties:
          a2a:
            type: object
            description: "A2A protocol defaults"
            properties:
              base_url:
                type: string
                description: "Base URL for A2A endpoints"
              agent_card:
                type: object
                description: "Default A2A agent card configuration"
                properties:
                  published:
                    type: boolean
                    description: "Whether the agent card is publicly discoverable"
                    default: true
                  well_known_path:
                    type: string
                    description: "Path where agent card can be accessed"
                    default: "/.well-known/agent.json"
                  auth_requirements:
                    type: object
                    description: "Authentication requirements for accessing this agent"
                    properties:
                      required:
                        type: boolean
                        description: "Whether authentication is required"
                        default: false
                      types:
                        type: array
                        description: "Supported authentication types"
                        items:
                          type: string
                          enum: ["none", "api_key", "oauth2", "jwt", "basic"]
              timeout_ms:
                type: integer
                description: "Default timeout in milliseconds for A2A requests"
                default: 30000
          mcp:
            type: object
            description: "MCP protocol defaults"
            properties:
              server_mode:
                type: boolean
                description: "Whether to run in server mode"
                default: false
              client_mode:
                type: boolean
                description: "Whether to run in client mode"
                default: true
              stream_mode:
                type: string
                description: "Streaming mode for MCP"
                enum: ["sse", "websocket", "stdio"]
                default: "sse"
              http_port:
                type: integer
                description: "HTTP port for MCP server"
                default: 8000
              server_name:
                type: string
                description: "Name of the MCP server"
              timeout_ms:
                type: integer
                description: "Default timeout in milliseconds for MCP requests"
                default: 30000
          http:
            type: object
            description: "HTTP protocol defaults"
            properties:
              base_url:
                type: string
                description: "Base URL for HTTP endpoints"
              port:
                type: integer
                description: "HTTP port"
                default: 8080
              timeout_ms:
                type: integer
                description: "Default timeout in milliseconds for HTTP requests"
                default: 30000
              headers:
                type: object
                description: "Default headers for HTTP requests"
              rate_limit:
                type: object
                description: "Rate limiting configuration"
                properties:
                  requests_per_minute:
                    type: integer
                    description: "Maximum requests per minute"
                    default: 60
          mqtt:
            type: object
            description: "MQTT protocol defaults"
            properties:
              broker_url:
                type: string
                description: "MQTT broker URL"
              port:
                type: integer
                description: "MQTT port"
                default: 1883
              client_id:
                type: string
                description: "MQTT client ID"
              qos:
                type: integer
                description: "Quality of Service level"
                enum: [0, 1, 2]
                default: 1
              retain:
                type: boolean
                description: "Whether messages should be retained"
                default: false
              clean_session:
                type: boolean
                description: "Whether to use a clean session"
                default: true
          grpc:
            type: object
            description: "gRPC protocol defaults"
            properties:
              host:
                type: string
                description: "gRPC host"
                default: "localhost"
              port:
                type: integer
                description: "gRPC port"
                default: 50051
              max_message_size_mb:
                type: integer
                description: "Maximum message size in MB"
                default: 4
              timeout_ms:
                type: integer
                description: "Default timeout in milliseconds for gRPC requests"
                default: 30000

      # Default security configuration
      security:
        type: object
        description: "Default security configuration"
        properties:
          authentication:
            type: object
            description: "Authentication configuration"
            properties:
              enabled:
                type: boolean
                description: "Whether authentication is enabled"
                default: true
              default_provider:
                type: string
                description: "Default authentication provider"
                enum: ["jwt", "api_key", "oauth", "none"]
                default: "api_key"

      # Default session management
      sessions:
        type: object
        description: "Default session management configuration"
        properties:
          enabled:
            type: boolean
            description: "Whether session management is enabled"
            default: true
          storage:
            type: object
            description: "Session storage configuration"
            properties:
              type:
                type: string
                description: "Storage backend type"
                enum: ["database", "file", "memory", "redis"]
                default: "memory"
              connection_string:
                type: string
                description: "Connection string for database or redis storage"
              table_name:
                type: string
                description: "Table or collection name for database storage"
              expiration:
                type: integer
                description: "Session expiration time in seconds"
                default: 604800
          # Protocol-specific session configuration
          protocol_sessions:
            type: object
            description: "Protocol-specific session configurations"
            properties:
              # A2A task session configuration
              a2a:
                type: object
                description: "A2A task management configuration"
                properties:
                  enabled:
                    type: boolean
                    description: "Whether A2A task management is enabled"
                    default: true
                  states:
                    type: array
                    description: "Supported task states"
                    default: ["submitted", "working", "input_required", "completed", "failed"]
                    items:
                      type: string
                      enum: ["submitted", "working", "input_required", "completed", "failed"]
                  persistence:
                    type: object
                    description: "Task persistence configuration"
                    properties:
                      ttl_seconds:
                        type: integer
                        description: "Time-to-live for tasks in seconds"
                        default: 3600
                      cleanup_interval:
                        type: integer
                        description: "Interval for cleaning up expired tasks in seconds"
                        default: 300
              # MCP session configuration
              mcp:
                type: object
                description: "MCP session management configuration"
                properties:
                  enabled:
                    type: boolean
                    description: "Whether MCP session management is enabled"
                    default: true
                  session_tracking:
                    type: boolean
                    description: "Whether to track MCP sessions"
                    default: true
                  session_id_header:
                    type: string
                    description: "HTTP header for MCP session ID"
                    default: "X-MCP-Session-ID"
          message_storage:
            type: object
            description: "Configuration for storing messages"
            properties:
              store_messages:
                type: boolean
                description: "Whether to store messages in the session"
                default: true
              store_artifacts:
                type: boolean
                description: "Whether to store artifacts in the session"
                default: true
              retention_policy:
                type: string
                description: "Retention policy for messages"
                enum: ["session", "permanent", "custom"]
                default: "session"

      # Default observability configuration
      observability:
        type: object
        description: "Default observability configuration"
        properties:
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
          metrics:
            type: object
            description: "Metrics collection configuration"
            properties:
              enabled:
                type: boolean
                description: "Whether metrics collection is enabled"
                default: true
              providers:
                type: array
                description: "Metrics providers to use"
                items:
                  type: string
                  enum: ["prometheus", "statsd", "opentelemetry"]
                default: ["prometheus"]
          tracing:
            type: object
            description: "Distributed tracing configuration"
            properties:
              enabled:
                type: boolean
                description: "Whether tracing is enabled"
                default: false
              provider:
                type: string
                description: "Tracing provider to use"
                enum: ["opentelemetry", "jaeger", "zipkin"]
                default: "opentelemetry"
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
              include_details:
                type: boolean
                description: "Whether to include component details in health check"
                default: true

      # Asset and resource management configuration
      asset_management:
        type: object
        description: "Global asset management configuration"
        properties:
          enabled:
            type: boolean
            description: "Whether unified asset management is enabled"
            default: true
          asset_handling:
            type: object
            description: "How to handle assets across protocols"
            properties:
              default_strategy:
                type: string
                description: "Default strategy for asset handling"
                enum: ["inline", "reference", "hybrid"]
                default: "hybrid"
              max_inline_size_kb:
                type: integer
                description: "Maximum size in KB to transfer inline"
                default: 64
              cache_enabled:
                type: boolean
                description: "Whether to cache assets/resources"
                default: true
              cache_ttl_seconds:
                type: integer
                description: "Time to live for cached assets/resources in seconds"
                default: 3600
          protocol_representation:
            type: object
            description: "How assets are represented in different protocols"
            properties:
              content_handling:
                type: object
                description: "How to handle different content types"
                properties:
                  text:
                    type: object
                    description: "How to handle text content"
                    properties:
                      representation:
                        type: string
                        description: "Default representation method"
                        enum: ["inline", "reference", "hybrid"]
                        default: "inline"
                  image:
                    type: object
                    description: "How to handle image content"
                    properties:
                      representation:
                        type: string
                        description: "Default representation method"
                        enum: ["inline", "reference", "hybrid"]
                        default: "hybrid"
                  file:
                    type: object
                    description: "How to handle file content"
                    properties:
                      representation:
                        type: string
                        description: "Default representation method"
                        enum: ["inline", "reference", "hybrid"]
                        default: "reference"
                  data:
                    type: object
                    description: "How to handle structured data content"
                    properties:
                      representation:
                        type: string
                        description: "Default representation method"
                        enum: ["inline", "reference", "hybrid"]
                        default: "inline"

      # Extensions system configuration
      extensions:
        type: object
        description: "Extensions system configuration"
        properties:
          enabled:
            type: boolean
            description: "Whether extensions are enabled"
            default: true
          auto_discovery:
            type: boolean
            description: "Whether to auto-discover extensions"
            default: true
          directories:
            type: array
            description: "Directories to search for extensions"
            items:
              type: string
            default: ["./extensions"]
          allowed_types:
            type: array
            description: "Types of extensions allowed"
            items:
              type: string
              enum: ["communicator", "agent", "asset", "prompt", "llm", "reasoning", "protocol", "protocol_adapter", "tool"]
            default: ["communicator", "agent", "asset", "prompt", "llm", "reasoning", "protocol", "protocol_adapter", "tool"]
          security:
            type: object
            description: "Extension security configuration"
            properties:
              verify_signatures:
                type: boolean
                description: "Whether to verify extension signatures"
                default: false
              isolation_level:
                type: string
                description: "Extension isolation level"
                enum: ["none", "process", "container"]
                default: "none"

      # Prompt management configuration
      prompts:
        type: object
        description: "Prompt management configuration"
        properties:
          template_format:
            type: string
            description: "Default template format for prompts"
            enum: ["text", "jinja2", "handlebars"]
            default: "jinja2"
          include_paths:
            type: array
            description: "Paths to search for prompt templates"
            items:
              type: string
            default: ["./prompts"]
          version_control:
            type: boolean
            description: "Whether to track prompt versions"
            default: true

  # Agent definitions
  agents:
    type: object
    description: "Agent definitions"
    additionalProperties:
      type: object
      properties:
        # Agent class and type
        class:
          type: string
          description: "Agent class path"
        type:
          type: string
          description: "Agent type classification (distinct from reasoning approach)"
          enum: ["assistant", "tool", "manager", "autonomous", "collaborative", "custom"]

        # Agent topology configuration
        # See detailed patterns in: /01_architecture/topology_patterns/
        topology:
          type: object
          description: "Agent-specific topology configuration"
          # For implementation details, see: /01_architecture/topology_design.md
          properties:
            role:
              type: string
              description: "Role of this agent in the topology"
            relationships:
              type: array
              description: "Agent's relationships with other agents"
              items:
                type: object
                properties:
                  agent_id:
                    type: string
                    description: "ID of the related agent"
                  relationship_type:
                    type: string
                    description: "Type of relationship"
                  direction:
                    type: string
                    description: "Direction of relationship"
                    enum: ["incoming", "outgoing", "bidirectional"]
                  communication_pattern:
                    type: string
                    description: "Communication pattern for this relationship"

        # Protocol configuration
        protocols:
          type: array
          description: "Protocol interfaces exposed by this agent"
          items:
            type: object
            properties:
              type:
                type: string
                description: "Protocol type"
                enum: ["mcp-stdio", "mcp-sse", "mcp-streamable", "a2a-http", "a2a-websocket", "a2a-grpc", "grpc", "mqtt", "http", "websocket"]
              enabled:
                type: boolean
                description: "Whether this protocol interface is enabled"
                default: true
              options:
                type: object
                description: "Protocol-specific options"
                properties:
                  # A2A Protocol Options
                  base_url:
                    type: string
                    description: "Base URL for A2A HTTP endpoint"
                  agent_card:
                    type: object
                    description: "A2A Agent Card configuration for discovery and interoperability"
                    properties:
                      name:
                        type: string
                        description: "The name of the agent"
                      description:
                        type: string
                        description: "Detailed description of the agent's purpose and functionality"
                      display_name:
                        type: string
                        description: "Human-friendly display name for the agent"
                      version:
                        type: string
                        description: "Agent version (semantic versioning recommended)"
                      url:
                        type: string
                        description: "URL where the agent's A2A endpoint is accessible"
                      contact_info:
                        type: object
                        description: "Contact information for the agent"
                        properties:
                          name:
                            type: string
                            description: "Name of the contact person or team"
                          email:
                            type: string
                            description: "Email address for contact"
                          url:
                            type: string
                            description: "URL for more information"
                      capabilities:
                        type: array
                        description: "Capabilities provided by this agent"
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
                              description: "JSON Schema for the parameters"
                            returns:
                              type: object
                              description: "JSON Schema for the return value"
                            examples:
                              type: array
                              description: "Example uses of this capability"
                              items:
                                type: object
                      supported_features:
                        type: object
                        description: "A2A features supported by this agent"
                        properties:
                          streaming:
                            type: boolean
                            description: "Whether the agent supports streaming responses"
                            default: false
                          push_notifications:
                            type: boolean
                            description: "Whether the agent supports push notifications"
                            default: false
                      auth_requirements:
                        type: object
                        description: "Authentication requirements for accessing this agent"
                        properties:
                          required:
                            type: boolean
                            description: "Whether authentication is required"
                            default: false
                          types:
                            type: array
                            description: "Supported authentication types"
                            items:
                              type: string
                              enum: ["none", "api_key", "oauth2", "jwt", "basic"]
                      discovery:
                        type: object
                        description: "Discovery configuration"
                        properties:
                          published:
                            type: boolean
                            description: "Whether this agent should be publicly discoverable"
                            default: true
                          well_known_path:
                            type: string
                            description: "Path where the agent card is accessible"
                            default: "/.well-known/agent.json"
                  # MCP Protocol Options
                  server_mode:
                    type: boolean
                    description: "Whether to run in server mode"
                    default: false
                  client_mode:
                    type: boolean
                    description: "Whether to run in client mode"
                    default: true
                  stream_mode:
                    type: string
                    description: "Streaming mode for MCP"
                    enum: ["sse", "websocket", "stdio"]
                    default: "sse"
                  http_port:
                    type: integer
                    description: "HTTP port for MCP server"
                    default: 8000
                  server_name:
                    type: string
                    description: "Name of the MCP server"
                  # HTTP Protocol Options
                  port:
                    type: integer
                    description: "HTTP port"
                    default: 8080
                  timeout_ms:
                    type: integer
                    description: "Timeout in milliseconds for requests"
                    default: 30000
                  headers:
                    type: object
                    description: "Headers for HTTP requests"
                  # MQTT Protocol Options
                  broker_url:
                    type: string
                    description: "MQTT broker URL"
                  mqtt_port:
                    type: integer
                    description: "MQTT port"
                    default: 1883
                  client_id:
                    type: string
                    description: "MQTT client ID"
                  qos:
                    type: integer
                    description: "Quality of Service level"
                    enum: [0, 1, 2]
                    default: 1
                  # gRPC Protocol Options
                  host:
                    type: string
                    description: "gRPC host"
                    default: "localhost"
                  grpc_port:
                    type: integer
                    description: "gRPC port"
                    default: 50051
                  max_message_size_mb:
                    type: integer
                    description: "Maximum message size in MB"
                    default: 4

        # Agent capabilities
        capabilities:
          type: object
          description: "Agent capabilities configuration"
          properties:
            multi_protocol_capabilities:
              type: object
              description: "Multi-protocol capability configuration that defines declarative capability metadata, which must be linked to programmatic handler methods in agent code"
              properties:
                core:
                  type: array
                  description: "Core capability definitions. Each capability defined here must have a corresponding handler method registered in the agent code using register_capability_handler() or equivalent"
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                        description: "Capability identifier. This ID is used to link the declarative capability definition to a programmatic handler in agent code"
                      name:
                        type: string
                        description: "Human-readable name"
                      description:
                        type: string
                        description: "Detailed description"
                      parameters:
                        type: object
                        description: "JSON Schema for the capability parameters"
                      returns:
                        type: object
                        description: "JSON Schema for the return value"
                      examples:
                        type: array
                        description: "Example uses of this capability"
                        items:
                          type: object
                protocol_mapping:
                  type: object
                  description: "Mapping of core capability IDs to protocol-specific identifiers. Each key is a protocol name (e.g., 'a2a', 'mcp') and its value is an object mapping core capability IDs to protocol-specific names"
            # Capability exposure configuration
            capability_exposure:
              type: object
              description: "Configuration for capability exposure across protocols"
              properties:
                default_exposure:
                  type: string
                  description: "Default exposure level for capabilities"
                  enum: ["all", "selective", "none"]
                  default: "all"
                capability_filter:
                  type: object
                  description: "Filter which capabilities are exposed on which protocols"
                  additionalProperties:
                    type: array
                    items:
                      type: string
                capability_renaming:
                  type: object
                  description: "Rename capabilities for specific protocols"
                  additionalProperties:
                    type: object
                    additionalProperties:
                      type: string
            # Knowledge representation configuration (DEPRECATED: Use knowledge_management_config instead)
            knowledge:
              type: object
              description: "DEPRECATED: Use knowledge_management_config at the agent level instead. Will be removed in a future version."
              properties:
                representation_type:
                  type: string
                  description: "DEPRECATED: Use knowledge_management_config.default_knowledge_representation_types instead"
                  enum: ["symbolic", "graph", "vector", "probabilistic", "neural", "hybrid"]
                storage:
                  type: object
                  description: "DEPRECATED: Knowledge storage configuration"
                  properties:
                    type:
                      type: string
                      description: "DEPRECATED: Type of knowledge storage"
                      enum: ["memory", "file", "database", "vector_store", "graph_db"]
                    connection_string:
                      type: string
                      description: "DEPRECATED: Connection string for database storage"
            # Reasoning configuration - defines the agent's "brain"
            reasoning:
              type: object
              description: "The agent's primary reasoning engine configuration (the 'brain')"
              properties:
                approach:
                  type: string
                  description: "The primary reasoning engine to use"
                  enum: ["llm", "rule_based", "hybrid", "bdi", "symbolic_engine", "neural", "probabilistic"]
                implementation:
                  type: string
                  description: "Specific implementation of the reasoning engine"
                options:
                  type: object
                  description: "Reasoning engine specific options"
                security_integration:
                  type: object
                  description: "Configuration for reasoning engine's integration with the security system via the Reasoning Security Interface (RSI)"
                  properties:
                    rsi_enabled:
                      type: boolean
                      description: "Whether this reasoning engine should use the Reasoning Security Interface"
                      default: false
                    rsi_policy_profile:
                      type: string
                      description: "Name of the policy profile that defines the set of fine-grained permissions the reasoner is allowed to check via RSI"
                      default: "standard"
                    permission_check_behavior:
                      type: string
                      description: "How to handle permission check failures in the reasoning engine"
                      enum: ["strict", "warn", "permissive"]
                      default: "strict"

        # Agent-specific security configuration
        security:
          type: object
          description: "Agent-specific security configuration"
          properties:
            authentication:
              type: object
              description: "Authentication configuration"
              properties:
                providers:
                  type: object
                  description: "Authentication provider configuration"

        # Agent-specific session configuration
        sessions:
          type: object
          description: "Agent-specific session configuration"

        # Agent state management configuration
        state:
          type: object
          description: "Agent state management configuration"
          properties:
            # Storage backend configuration
            storage:
              type: object
              description: "Storage backend configuration for agent state"
              properties:
                type:
                  type: string
                  description: "Storage backend type"
                  enum: ["memory", "file", "database", "redis"]
                  default: "memory"

                # File storage options
                directory:
                  type: string
                  description: "Directory path for file storage (when type is 'file')"
                  default: "./agent_state"
                format:
                  type: string
                  description: "File format for file storage (when type is 'file')"
                  enum: ["json", "pickle", "yaml"]
                  default: "json"

                # Database storage options
                connection_string:
                  type: string
                  description: "Connection string for database storage (when type is 'database')"
                table_name:
                  type: string
                  description: "Table or collection name for database storage"
                  default: "agent_state"

                # Redis storage options
                redis_url:
                  type: string
                  description: "Redis URL for Redis storage (when type is 'redis')"
                  default: "redis://localhost:6379/0"
                redis_prefix:
                  type: string
                  description: "Key prefix for Redis storage"
                  default: "agent_state:"
              required:
                - type

            # Expiration settings
            expiration:
              type: object
              description: "Expiration settings for different state scopes"
              properties:
                private_persistent:
                  type: integer
                  description: "Expiration time in seconds for private persistent state (0 for no expiration)"
                  default: 2592000  # 30 days
                session_specific_persistent:
                  type: integer
                  description: "Expiration time in seconds for session-specific persistent state"
                  default: 604800  # 7 days
                in_memory_session_only:
                  type: integer
                  description: "Expiration time in seconds for in-memory session-only state"
                  default: 3600  # 1 hour
                shared:
                  type: integer
                  description: "Expiration time in seconds for shared state"
                  default: 86400  # 1 day

            # Serialization settings
            serialization:
              type: object
              description: "Serialization settings for agent state"
              properties:
                format:
                  type: string
                  description: "Serialization format"
                  enum: ["json", "pickle", "msgpack"]
                  default: "json"
                compress:
                  type: boolean
                  description: "Whether to compress serialized data"
                  default: false
                max_size_bytes:
                  type: integer
                  description: "Maximum size in bytes for a single state entry"
                  default: 1048576  # 1MB

        # Agent-specific observability
        observability:
          type: object
          description: "Agent-specific observability configuration"

        # Agent-specific asset management
        asset_management:
          type: object
          description: "Agent-specific asset management configuration"

        # Agent-specific extensions
        extensions:
          type: object
          description: "Agent-specific extensions configuration"
          properties:
            enabled_extensions:
              type: array
              description: "Extensions enabled for this agent"
              items:
                type: string

        # Agent knowledge management configuration
        knowledge_management_config:
          type: object
          description: "Configuration for how this agent interacts with the KR&R System"
          properties:
            enabled:
              type: boolean
              description: "Whether knowledge management is enabled for this agent"
              default: false
            knowledge_bases:
              type: array
              description: "Knowledge bases this agent's reasoning engine will utilize"
              items:
                type: object
                properties:
                  kb_id:
                    type: string
                    description: "Identifier of the knowledge base managed by the KR&R System"
                  type:
                    type: string
                    description: "Knowledge representation type of this knowledge base"
                    enum: ["symbolic_facts", "graph", "vector", "probabilistic", "hybrid"]
                  read_only:
                    type: boolean
                    description: "Whether this agent has read-only access to the knowledge base"
                    default: false
                required:
                  - kb_id
                  - type
            default_knowledge_representation_types:
              type: array
              description: "Default knowledge representation types this agent's reasoning engine will work with"
              items:
                type: string
                enum: ["symbolic_facts", "graph", "vector", "probabilistic", "hybrid"]
            integration_options:
              type: object
              description: "Additional options for how the reasoning engine integrates with knowledge bases"

        # Agent-specific prompt management
        prompts:
          type: object
          description: "Agent-specific prompt management"
          properties:
            system_prompt:
              type: string
              description: "System prompt for the agent"
            prompt_templates:
              type: object
              description: "Custom prompt templates for this agent"
              additionalProperties:
                type: object
      required:
        - class

  # Environment-specific configuration
  environments:
    type: object
    description: "Environment-specific configuration"
    additionalProperties:
      type: object
      description: "Configuration for a specific environment"

  # Deployment configuration
  deployment:
    type: object
    description: "Deployment configuration"
    properties:
      environment:
        type: string
        description: "Deployment environment"
        enum: ["development", "testing", "staging", "production"]
      services:
        type: object
        description: "Service configuration"

required:
  - name
  - version
  - agents
```

## Configuration Hierarchy

The OpenMAS configuration system follows a clear hierarchy of precedence:

1. **Command Line Arguments** (highest precedence)
2. **Environment Variables**
3. **Environment-Specific Configuration**
4. **Agent-Specific Configuration**
5. **Global Defaults**
6. **Framework Defaults** (lowest precedence)

## Example Configuration

```yaml
# Example OpenMAS Project Configuration
name: "travel_planner"
version: "0.3.0"
description: "Multi-agent travel planning system"

# Global defaults
defaults:
  common:
    log_level: "info"

  # Default topology is centralized
  topology:
    pattern: "centralized"
    roles:
      types:
        - name: "orchestrator"
          description: "Central coordinator"
        - name: "worker"
          description: "Specialized service provider"
    relationships:
      types:
        - name: "orchestrator_to_worker"
          communication_pattern: "request_response"

  # Default communication patterns
  communication_patterns:
    request_response:
      options:
        timeout: 30000
        retry:
          attempts: 3
      protocol_adaptations:
        a2a:
          use_streaming: false
    event_based:
      options:
        event_buffer_size: 100

  # Default protocol configuration
  protocols:
    a2a:
      auth_required: true
      auth_provider: "api_key"
    mcp:
      server_instructions: "Default server instructions"
      tool_registration: "auto"

  # Default security
  security:
    authentication:
      enabled: true
      default_provider: "api_key"

  # Default observability
  observability:
    logging:
      level: "info"
      format: "json"

# Agent definitions
agents:
  # Travel coordinator agent
  travel_coordinator:
    class: "agents.coordinator.TravelCoordinator"
    type: "hybrid"

    # Topology configuration
    topology:
      role: "orchestrator"
      relationships:
        - agent_id: "flight_search"
          relationship_type: "orchestrator_to_worker"
        - agent_id: "hotel_search"
          relationship_type: "orchestrator_to_worker"

    # Protocols exposed
    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8000"
          # Note: A2A Agent Card details should be configured under protocols.ITEM_WHERE_TYPE_IS_A2A.options.agent_card
          # See protocols section above for the proper structure
      - type: "mcp-sse"
        enabled: true
        options:
          server_mode: true
          server_instructions: "Travel coordination service"

    # Capabilities
    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "coordinate_trip"
            name: "Coordinate Trip"
            description: "Coordinates a complete trip itinerary"
        protocol_mapping:
          a2a:
            coordinate_trip: "tasks/coordinate"
          mcp:
            coordinate_trip: "coordinate_trip_tool"

  # Flight search agent
  flight_search:
    class: "agents.flight.FlightSearchAgent"
    type: "rule_based"

    # Topology configuration
    topology:
      role: "worker"
      relationships:
        - agent_id: "travel_coordinator"
          relationship_type: "worker_to_orchestrator"
          communication_pattern: "event_based"

    # Protocols exposed
    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8001"
      - type: "mqtt"
        enabled: true
        options:
          broker_url: "mqtt://localhost:1883"
          topics:
            - "worker/events/#"

# Environment-specific configuration
environments:
  development:
    observability:
      logging:
        level: "debug"

  production:
    observability:
      logging:
        level: "info"
        output: "file"
    security:
      rate_limiting:
        enabled: true

# Deployment configuration
deployment:
  environment: "development"
```

## Environment Variables

All configuration properties can be overridden using environment variables:

- **Naming Convention**: `OPENMAS_[COMPONENT]_[SETTING]`
- **Examples**:
  - `OPENMAS_AGENT_TRAVEL_COORDINATOR_LOG_LEVEL=debug`
  - `OPENMAS_PROTOCOL_A2A_AUTH_REQUIRED=true`
  - `OPENMAS_SECURITY_AUTHENTICATION_ENABLED=true`

## Integration with Pydantic

This schema can be implemented using Pydantic for validation:

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any

class TopologyRole(BaseModel):
    name: str
    description: str

class TopologyRelationshipType(BaseModel):
    name: str
    description: str
    communication_pattern: str

class TopologyConfig(BaseModel):
    pattern: str = "centralized"
    roles: Dict[str, List[TopologyRole]]
    relationships: Dict[str, List[TopologyRelationshipType]]

class AgentRelationship(BaseModel):
    agent_id: str
    relationship_type: str
    direction: Optional[str] = "bidirectional"
    communication_pattern: Optional[str] = None

class AgentTopologyConfig(BaseModel):
    role: str
    relationships: List[AgentRelationship]

class ProtocolInterface(BaseModel):
    type: str
    enabled: bool = True
    options: Dict[str, Any] = {}

class AgentCapabilityCore(BaseModel):
    id: str
    name: str
    description: str

class AgentCapabilities(BaseModel):
    multi_protocol_capabilities: Dict[str, Any] = {}

class AgentConfig(BaseModel):
    class_path: str = Field(..., alias="class")
    type: str
    topology: Optional[AgentTopologyConfig] = None
    protocols: Optional[List[ProtocolInterface]] = None
    capabilities: Optional[AgentCapabilities] = None
    security: Optional[Dict[str, Any]] = None
    sessions: Optional[Dict[str, Any]] = None
    observability: Optional[Dict[str, Any]] = None

class OpenMASConfig(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    defaults: Optional[Dict[str, Any]] = {}
    agents: Dict[str, AgentConfig]
    environments: Optional[Dict[str, Dict[str, Any]]] = {}
    deployment: Optional[Dict[str, Any]] = {}
```

## Benefits of Unified Schema

1. **Consistency**: Standardized structure across all components
2. **Clarity**: Clear hierarchy of configuration precedence
3. **Integration**: Explicit connections between components
4. **Extensibility**: Easy to add new components without breaking changes
5. **Validation**: Single schema enables comprehensive validation
