# Agent Configuration Documentation

> **IMPORTANT NOTE**: This document does NOT define the agent configuration schema. It only provides documentation and examples for the agent configuration section defined in the [Unified Configuration Schema](../unified_configuration_schema.md), which is the single source of truth for all schema definitions.

## Overview

This document explains the agent configuration sections in the unified schema, which define the structure and behavior of agents in OpenMAS. It covers key agent configuration properties including agent type, protocols, capabilities, reasoning approach, and security settings.

## Agent Configuration Section Reference

The agent configuration is defined in the `agents` section of the [Unified Configuration Schema](../unified_configuration_schema.md). The following explains the key components of the agent configuration:

### Core Agent Properties

These properties define the basic identity and type of an agent:

- **class**: The fully qualified class path to the agent implementation
- **type**: The agent's functional classification (assistant, tool, manager, etc.)

For the complete schema definition of these properties, see the `agents` section in the [Unified Configuration Schema](../unified_configuration_schema.md).

### Agent Topology Configuration

The topology configuration defines how an agent relates to other agents within the system:

- **role**: The agent's role within the defined topology
- **relationships**: Connections to other agents, including the relationship type and communication patterns

See the `agents.[agent_id].topology` section in the [Unified Configuration Schema](../unified_configuration_schema.md) for the complete definition.

### Protocol Configuration

Defines which communication protocols the agent supports:

- **type**: The protocol type (e.g., "mcp-sse", "a2a-http", "grpc")
- **enabled**: Whether the protocol interface is active
- **options**: Protocol-specific configuration options

See the `agents.[agent_id].protocols` array in the [Unified Configuration Schema](../unified_configuration_schema.md) for the complete definition.

### Agent Capabilities

Defines the functional capabilities of the agent:

- **multi_protocol_capabilities**: Core capability definitions and their protocol-specific mappings
- **capability_exposure**: Configuration for how capabilities are exposed across different protocols

See the `agents.[agent_id].capabilities` section in the [Unified Configuration Schema](../unified_configuration_schema.md) for the complete definition.

### Session Management

Controls how the agent manages conversation sessions and context:

- **enabled**: Whether session management is active
- **storage**: Configuration for where session data is stored
- **context**: Settings for managing conversation context and history

See the `agents.[agent_id].sessions` section in the [Unified Configuration Schema](../unified_configuration_schema.md) for the complete definition.

### State Management

Configures how the agent manages its persistent state:

- **storage**: Storage backend configuration for agent state (type, connection options)
- **expiration**: Expiration settings for different state scopes
- **serialization**: Serialization format and limits for state data

State management allows agents to persistently store data across sessions and restarts using a standardized API. For details on the state management API, see [Agent State Management API](/refactoring_work/00b_overview/04_agents/agent_state_management_api.md).

See the `agents.[agent_id].state` section in the [Unified Configuration Schema](../unified_configuration_schema.md) for the complete definition.

### Reasoning Configuration

Defines the agent's "brain" - its primary decision-making engine:

- **approach**: The reasoning approach used (e.g., "llm", "rule_based", "bdi")
- **implementation**: Specific implementation class or module
- **security_integration**: Configuration for the Reasoning Security Interface (RSI)

See the `agents.[agent_id].reasoning` section in the [Unified Configuration Schema](../unified_configuration_schema.md) for the complete definition.
                description: "How to handle permission check failures in the reasoning engine"
                enum: ["strict", "warn", "permissive"]
                default: "strict"
          llm:
            type: object
            description: "LLM reasoning configuration"
            properties:
              provider:
                type: string
                description: "LLM provider"
              model:
                type: string
                description: "Model name"
              temperature:
                type: number
                description: "Temperature for generation"
              system_prompt:
                type: string
                description: "System prompt for the LLM"
              tools_enabled:
                type: boolean
                description: "Whether tools are enabled for this LLM"
                default: true
          rule_based:
            type: object
            description: "Rule-based reasoning configuration"
            properties:
              rules_file:
                type: string
                description: "Path to rules definition file"
              engine:
                type: string
                description: "Rule engine to use"
          bdi:
            type: object
            description: "BDI reasoning configuration"
            properties:
              belief_base:
                type: object
                description: "Belief base configuration"
              desires:
                type: array
                description: "Configured desires/goals"
                items:
                  type: object
              plans:
                type: array
                description: "Available plans"
                items:
                  type: object
      
      # Security configuration
      security:
        type: object
        description: "Agent security configuration"
        properties:
          authentication:
            type: object
            description: "Authentication configuration"
            properties:
              required:
                type: boolean
                description: "Whether authentication is required"
                default: false
              methods:
                type: array
                description: "Supported authentication methods"
                items:
                  type: string
                  enum: ["api_key", "jwt", "oauth2", "basic"]
          authorization:
            type: object
            description: "Authorization configuration"
            properties:
              capability_access:
                type: object
                description: "Capability access control"
                additionalProperties:
                  type: array
                  items:
                    type: string
      
      # Knowledge management configuration
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
      
      # Observability configuration
      observability:
        type: object
        description: "Agent observability configuration"
        properties:
          logging:
            type: object
            description: "Logging configuration"
            properties:
              level:
                type: string
                description: "Log level"
                enum: ["debug", "info", "warning", "error"]
                default: "info"
          metrics:
            type: object
            description: "Metrics collection configuration"
            properties:
              enabled:
                type: boolean
                description: "Whether metrics collection is enabled"
                default: true
```

## Agent Configuration Examples

### LLM-Based Agent

Configuration for an LLM-based agent:

```yaml
agents:
  assistant_agent:
    class: "agents.assistant.AssistantAgent"
    type: "assistant"
    
    # Protocol configuration
    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8000"
      
      - type: "mcp-sse"
        enabled: true
        options:
          server_mode: true
          http_port: 8080
    
    # Capabilities
    capabilities:
      definitions:
        - name: "answer_question"
          description: "Answers a user question"
          parameters:
            type: "object"
            properties:
              question:
                type: "string"
                description: "The question to answer"
          returns:
            type: "object"
            properties:
              answer:
                type: "string"
                description: "The answer to the question"
    
    # Reasoning configuration (the "brain")
    reasoning:
      approach: "llm"
      implementation: "openai_chat"
      llm:
        provider: "openai"
        model: "gpt-4"
        temperature: 0.7
        system_prompt: "You are a helpful assistant that answers user questions."
        tools_enabled: true
        
    # Knowledge management configuration
    knowledge_management_config:
      enabled: true
      knowledge_bases:
        - kb_id: "assistant_knowledge"
          type: "vector"
        - kb_id: "user_profiles"
          type: "graph"
          read_only: true
      default_knowledge_representation_types:
        - "vector"
        - "graph"
```

### Rule-Based Agent

Configuration for a rule-based agent:

```yaml
agents:
  monitoring_agent:
    class: "agents.monitoring.MonitoringAgent"
    type: "tool"
    
    # Protocol configuration
    protocols:
      - type: "mqtt"
        enabled: true
        options:
          broker_url: "mqtt://localhost:1883"
          topic_prefix: "system/monitoring"
    
    # Capabilities
    capabilities:
      definitions:
        - name: "check_system_status"
          description: "Checks the status of system components"
          parameters:
            type: "object"
            properties:
              components:
                type: "array"
                items:
                  type: "string"
          returns:
            type: "object"
            properties:
              status:
                type: "object"
                additionalProperties:
                  type: "string"
    
    # Reasoning configuration
    reasoning:
      approach: "rule_based"
      rule_based:
        rules_file: "rules/monitoring_rules.yml"
        engine: "standard"
```

### BDI Agent

Configuration for a BDI (Belief-Desire-Intention) agent:

```yaml
agents:
  autonomous_agent:
    class: "agents.autonomous.AutonomousAgent"
    type: "autonomous"
    
    # Protocol configuration
    protocols:
      - type: "http"
        enabled: true
        options:
          port: 8080
    
    # Capabilities
    capabilities:
      definitions:
        - name: "plan_route"
          description: "Plans a route to a destination"
          parameters:
            type: "object"
            properties:
              start:
                type: "object"
                properties:
                  latitude: { type: "number" }
                  longitude: { type: "number" }
              destination:
                type: "object"
                properties:
                  latitude: { type: "number" }
                  longitude: { type: "number" }
          returns:
            type: "object"
            properties:
              route:
                type: "array"
                items:
                  type: "object"
                  properties:
                    latitude: { type: "number" }
                    longitude: { type: "number" }
    
    # Reasoning configuration
    reasoning:
      approach: "bdi"
      bdi:
        belief_base:
          type: "in_memory"
        desires:
          - name: "reach_destination"
            priority: 10
        plans:
          - name: "navigate_to_goal"
            triggers: ["reach_destination"]
          - name: "avoid_obstacle"
            triggers: ["obstacle_detected"]
```

### Hybrid Agent

Configuration for a hybrid agent combining multiple reasoning approaches:

```yaml
agents:
  hybrid_agent:
    class: "agents.hybrid.HybridAgent"
    type: "collaborative"
    
    # Protocol configuration
    protocols:
      - type: "a2a-http"
        enabled: true
      - type: "grpc"
        enabled: true
    
    # Capabilities
    capabilities:
      definitions:
        - name: "analyze_data"
          description: "Analyzes data using hybrid reasoning"
          parameters:
            type: "object"
            properties:
              data:
                type: "array"
                items:
                  type: "object"
              analysis_type:
                type: "string"
          returns:
            type: "object"
            properties:
              insights:
                type: "array"
                items:
                  type: "object"
              summary:
                type: "string"
    
    # Reasoning configuration
    reasoning:
      approach: "hybrid"
      implementation: "meta_reasoner"
      llm:
        provider: "anthropic"
        model: "claude-3-sonnet"
        temperature: 0.2
      rule_based:
        rules_file: "rules/data_analysis_rules.yml"
      bdi:
        belief_base:
          type: "in_memory"
        plans:
          - name: "analyze_numeric_data"
          - name: "analyze_text_data"
    
    # Knowledge management configuration
    knowledge_management_config:
      enabled: true
      knowledge_bases:
        - kb_id: "domain_knowledge"
          type: "symbolic_facts"
        - kb_id: "semantic_graph"
          type: "graph"
        - kb_id: "vector_database"
          type: "vector"
      default_knowledge_representation_types:
        - "symbolic_facts"
        - "graph"
        - "vector"
```

## Agent Configuration in the Unified Schema

The agent configuration schema is referenced in the unified configuration schema:

```yaml
# Unified schema excerpt
type: object
properties:
  name:
    type: string
  version:
    type: string
  agents:
    $ref: "#/definitions/agents_schema"
  defaults:
    type: object
    properties:
      agents:
        $ref: "#/definitions/agents_schema"
```
