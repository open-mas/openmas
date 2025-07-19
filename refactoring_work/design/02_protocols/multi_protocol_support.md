# Multi-Protocol Support Standard

## Definition
- **Name**: Multi-Protocol Support
- **Purpose**: Standardized approach to supporting multiple protocol interfaces within the same agent
- **Protocol Integration**: Enables interaction between different protocols through the Standard Internal Message Format (SIMF)
- **Reasoning Agnosticism**: Maintains separation between communication protocols and reasoning approaches

## Multi-Protocol Configuration Schema
```yaml
# Standardized multi-protocol configuration within unified schema
agents:
  agent_name:
    # Protocol configuration
    protocols:
      type: array
      description: "Protocol interfaces exposed by this agent"
      items:
        type: object
        properties:
          type:
            type: string
            description: "The type of protocol to use"
            enum: ["mcp-stdio", "mcp-sse", "mcp-streamable", "a2a-http", "a2a-websocket", "a2a-grpc", "grpc", "mqtt", "http", "websocket"]
          enabled:
            type: boolean
            description: "Whether this protocol interface is enabled"
            default: true
          options:
            type: object
            description: "Protocol-specific options"
        required:
          - type
  
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
  
  # Content handling configuration
  content_handling:
    type: object
    description: "Configuration for content handling across protocols"
    properties:
      default_strategy:
        type: string
        description: "Default content handling strategy"
        enum: ["inline", "reference", "hybrid"]
        default: "hybrid"
      max_inline_size_kb:
        type: integer
        description: "Maximum size in KB to transfer inline"
        default: 64
```

## Protocol Semantics Comparison

| Feature | A2A | MCP | Translation Approach |
|---------|-----|-----|----------------------|
| **Messages/Content** | Message parts (text, file, data) | Text content, Resources | SIMF-mediated translation through protocol adapters |
| **Capabilities** | Agent card capabilities | Tools | Unified internal capability model mapped to protocol-specific formats |
| **Authentication** | Agent cards, API keys | Headers, API keys | Protocol-specific authentication with common security model |
| **Streaming** | Supported | Supported | Protocol-specific streaming with common SIMF chunking model |
| **Discovery** | Agent registry | Tool listing | Protocol-specific discovery with unified capability registry |

> **Important**: While A2A and MCP have complementary purposes, they are not directly interoperable at the message content level. Their core abstractions (A2A Tasks vs. MCP Tools), message structures, and lifecycles are fundamentally different. In OpenMAS, meaningful communication between A2A and MCP is mediated through the Standard Internal Message Format (SIMF) via dedicated protocol adapters.

## Integration with Unified Configuration Schema

This multi-protocol configuration is part of the [Unified Configuration Schema](unified_configuration_schema.md), which integrates all OpenMAS components into a coherent whole.

```yaml
# Example within unified schema
name: "example_project"
version: "0.3.0"

# Agent definitions
agents:
  multi_protocol_agent:
    class: "agents.multipurpose.MultiPurposeAgent"
    type: "hybrid"
    
    # Protocol configuration - multiple protocols for a single agent
    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8080"
          agent_card:
            name: "My Agent"
            description: "A multipurpose agent"
            capabilities:
              - name: "search"
```

## Multi-Protocol Configuration Examples

### Single Agent with Multiple Protocol Interfaces

```yaml
# Configure an agent with both A2A and MCP interfaces (in unified schema)
agents:
  my_agent:
    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8080"
          agent_card:
            name: "My Agent"
            description: "A multipurpose agent"
            capabilities:
              - name: "search"
            description: "Search for information"
            parameters:
              type: "object"
              properties:
                query:
                  type: "string"
                limit:
                  type: "integer"
                  default: 10
  
  - type: "mcp-sse"
    enabled: true
    options:
      server_mode: true
      http_port: 8000
      server_name: "My MCP Server"

# Configure consistent capability exposure
capability_exposure:
  default_exposure: "all"
  capability_renaming:
    "mcp-sse":
      "search": "web_search"  # Same capability, different name on MCP
```

### Selective Capability Exposure

```yaml
# Expose different capabilities on different protocols
protocols:
  - type: "a2a-http"
    enabled: true
    options:
      base_url: "http://localhost:8080"
  
  - type: "mcp-sse"
    enabled: true
    options:
      server_mode: true
      http_port: 8000

capability_exposure:
  default_exposure: "selective"
  capability_filter:
    "a2a-http": ["search", "summarize", "translate"]
    "mcp-sse": ["search", "analyze_data", "generate_image"]
```

## Implementation Approaches

### 1. Protocol Interface Adapters with SIMF Translation

The OpenMAS framework uses protocol interface adapters that translate between protocol-specific formats and the Standard Internal Message Format (SIMF):

```python
class MultiProtocolAgent(Agent):
    def __init__(self, config):
        super().__init__(config)
        self.protocol_interfaces = []
        
        # Initialize protocol interfaces based on configuration
        for protocol_config in config.get("protocols", []):
            if not protocol_config.get("enabled", True):
                continue
                
            protocol_type = protocol_config["type"]
            if protocol_type.startswith("a2a-"):
                # A2A adapter handles translation between A2A protocol and SIMF
                self.protocol_interfaces.append(
                    A2AProtocolInterface(self, protocol_config)
                )
            elif protocol_type.startswith("mcp-"):
                self.protocol_interfaces.append(
                    MCPProtocolInterface(self, protocol_config)
                )
            # Additional protocol types...
```

### 2. Unified Capability Registry

Capabilities are registered once and exposed through all enabled protocols:

```python
# Register a capability once, expose through multiple protocols
@agent.register_capability(
    name="search",
    description="Search for information",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 10}
        },
        "required": ["query"]
    }
)
async def search(self, query, limit=10):
    # Implementation using any reasoning approach
    # Can use rule-based, BDI, KR&R, or LLM-based reasoning
    return await self.reasoning_engine.search(query, limit)
```

## Reasoning Agnostic Protocol Support

OpenMAS maintains reasoning agnosticism across protocol interfaces:

1. **Clean Separation**: Protocol interfaces handle only communication, not reasoning
2. **Common Capability API**: Same capability API works with any reasoning approach
3. **Consistent Data Models**: Content handling is consistent regardless of reasoning mechanism
4. **Transparent Interaction**: Clients don't need to know which reasoning approach is used

This design allows agents to leverage any of OpenMAS's reasoning capabilities (rule-based, BDI, KR&R, LLM-based, or hybrid) while exposing consistent protocol interfaces.

## Extensions for Third-Party Protocols

The multi-protocol system is designed to be extended with additional protocol packages:

```yaml
# Extension for MQTT protocol
protocols:
  - type: "mqtt"
    enabled: true
    options:
      broker_url: "mqtt://broker.example.com:1883"
      topics:
        subscribe: ["requests/#"]
        publish: "responses/{client_id}"
      qos: 1
```

Third-party protocol packages can implement the protocol interface for new protocols while maintaining compatibility with the unified capability system and reasoning agnosticism.
