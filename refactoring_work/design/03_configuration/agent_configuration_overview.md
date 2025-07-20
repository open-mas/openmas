# OpenMAS Agent Configuration Overview

This document provides a comprehensive overview of the agent configuration system in OpenMAS, describing the design principles, structure, and best practices for configuring agents.

## Design Principles

The OpenMAS agent configuration system is built on the following key principles:

1. **Multi-Protocol Support**: Native support for multiple communication protocols (MCP, A2A, HTTP, gRPC, MQTT) with consistent structure, allowing agents to communicate using any protocol.

2. **Protocol Agnosticism**: Clean separation between communication infrastructure and reasoning approaches, allowing any agent to use any protocol while maintaining reasoning flexibility.

3. **Flexible Topologies**: Support for various agent architectures:
   - Orchestrator-worker patterns
   - Gateway patterns
   - Mesh networks
   - Hub-and-spoke models

4. **Multiple Interfaces**: Ability for agents to expose different interfaces for different purposes:
   - Public APIs for clients
   - Internal interfaces for agent-to-agent communication
   - Admin interfaces for management

5. **Schema-Based Validation**: Clear schema definition with validation to catch configuration errors early.

6. **Deployment-First**: Comprehensive environment and deployment configuration for different scenarios.

## Configuration Structure

Agent configuration in OpenMAS follows a structured approach, with several key sections:

### 1. Agent Definition

Defines the basic properties of an agent:

```yaml
agents:
  agent_name:
    class: "package.module.ClassName"
    type: "llm|rule_based|hybrid|bdi|symbolic"
    description: "Agent description"
```

### 2. Protocol Configuration

Specifies which communication protocols the agent supports:

```yaml
agents:
  agent_name:
    # Other agent properties
    protocols:
      - type: "mcp-sse"
        enabled: true
        options:
          # Protocol-specific options
      - type: "a2a-http"
        enabled: true
        options:
          # Protocol-specific options
```

### 3. Capability Configuration

Defines the capabilities provided by the agent:

```yaml
agents:
  agent_name:
    # Other agent properties
    capabilities:
      capability_name:
        description: "Capability description"
        versions: ["1.0", "1.1"]
        input_schema: { /* JSON Schema */ }
        output_schema: { /* JSON Schema */ }
```

### 4. State Management

Configures how agent state is managed:

```yaml
agents:
  agent_name:
    # Other agent properties
    state:
      storage: "memory|redis|database"
      persistence: true|false
      ttl: 3600  # Time-to-live in seconds
```

### 5. Session Management

Configures agent session handling:

```yaml
agents:
  agent_name:
    # Other agent properties
    sessions:
      timeout: 3600  # Session timeout in seconds
      max_history: 100  # Maximum number of messages to retain
      cleanup_interval: 300  # Cleanup interval in seconds
```

### 6. Topology Configuration

Defines the agent's role in the system topology:

```yaml
agents:
  agent_name:
    # Other agent properties
    topology:
      role: "orchestrator|worker|gateway"
      relationships:
        - agent_id: "other_agent"
          relationship_type: "orchestrates|consumes|provides"
          direction: "outgoing|incoming|bidirectional"
```

## Validation Approach

OpenMAS uses a dual schema approach for agent configuration validation:

1. **JSONSchema**: Used for documentation and client-side validation
2. **Pydantic Models**: Used for runtime validation and type checking

This approach ensures both documentation accuracy and runtime safety.

### Common Validation Rules

- **Required Fields**: Certain fields are required for every agent (class, type)
- **Enum Validation**: Values for fields like type, role, etc. are restricted to predefined options
- **Cross-Field Validation**: Some constraints span multiple fields
- **Protocol-Specific Validation**: Each protocol may have specific validation rules

## Configuration Examples

### LLM-Based Agent

```yaml
agents:
  chatbot:
    class: "openmas.agents.LlmAgent"
    type: "llm"
    description: "A conversational assistant"

    protocols:
      - type: "mcp-sse"
        enabled: true
        options:
          server_mode: true
          http_port: 8000

    capabilities:
      answer_question:
        description: "Answers user questions on various topics"
        versions: ["1.0"]
        input_schema:
          type: "object"
          properties:
            question:
              type: "string"
          required: ["question"]

    state:
      storage: "redis"
      persistence: true
      ttl: 86400

    sessions:
      timeout: 3600
      max_history: 50
```

### Rule-Based Agent

```yaml
agents:
  data_processor:
    class: "openmas.agents.RuleBasedAgent"
    type: "rule_based"
    description: "Processes data according to predefined rules"

    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8001"

    capabilities:
      process_data:
        description: "Processes structured data according to rules"
        versions: ["1.0"]
        input_schema:
          type: "object"
          properties:
            data:
              type: "object"
          required: ["data"]

    rules_file: "data_processing_rules.yaml"
```

### Multi-Protocol Agent

```yaml
agents:
  gateway_agent:
    class: "openmas.agents.GatewayAgent"
    type: "hybrid"
    description: "Gateway agent exposing multiple protocols"

    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:9000"
          agent_card:
            name: "Gateway Agent"

      - type: "mcp-sse"
        enabled: true
        options:
          server_mode: true
          http_port: 9001

      - type: "mqtt"
        enabled: true
        options:
          broker_url: "mqtt://localhost:1883"
          topic_prefix: "openmas/gateway"

    capability_exposure:
      - capability: "route_message"
        protocols: ["a2a-http", "mqtt"]
      - capability: "transform_message"
        protocols: ["mcp-sse", "a2a-http"]
```

## Best Practices

1. **Use Environment Variables**: For sensitive or environment-specific values
   ```yaml
   agents:
     api_agent:
       api_key: "${API_KEY}"
   ```

2. **Leverage Defaults**: Define defaults to reduce repetition
   ```yaml
   defaults:
     agents:
       state:
         storage: "memory"
   ```

3. **Group Related Agents**: Use meaningful naming patterns for related agents
   ```yaml
   agents:
     orchestrator:
       # Orchestrator configuration
     worker_data:
       # Data worker configuration
     worker_analytics:
       # Analytics worker configuration
   ```

4. **Start Simple**: Begin with minimal configuration and add complexity as needed

5. **Document Agent Interfaces**: Include clear documentation for all agent capabilities

## Integration with Configuration Schema

For the complete and authoritative agent configuration schema, please refer to the [Agent Configuration Schema](/refactoring_work/00b_overview/03_configuration/schema/agents.md) document, which is part of the unified configuration schema.
