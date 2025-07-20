# Integration Configuration Documentation

> **IMPORTANT NOTE**: This document does NOT define the integration configuration schema. It only provides documentation and examples for the integration configuration section defined in the [Unified Configuration Schema](../unified_configuration_schema.md), which is the single source of truth for all schema definitions.

This document explains the external integrations section in the unified schema, which enables OpenMAS to connect with external services, frameworks, and APIs.

## Schema Definition

```yaml
# Integration configuration schema
integrations:
  type: object
  description: "External integration configuration"
  additionalProperties:
    type: object
    properties:
      type:
        type: string
        description: "Type of integration (service, framework, api, database, etc.)"
      description:
        type: string
        description: "Optional description of the integration"
      version:
        type: string
        description: "Optional version specification"
      enabled:
        type: boolean
        description: "Whether the integration is enabled"
        default: true
      config:
        type: object
        description: "Type-specific configuration"
        additionalProperties: true
      authentication:
        type: object
        properties:
          strategy:
            type: string
            enum: ["env_token", "oauth", "api_key", "basic_auth", "certificate"]
            description: "Authentication strategy to use"
          # Strategy-specific properties
          additionalProperties: true
        required: ["strategy"]
      retry:
        type: object
        properties:
          enabled:
            type: boolean
            default: false
          max_retries:
            type: integer
            default: 3
          retry_delay:
            type: integer
            description: "Initial delay in seconds"
            default: 1
          backoff_factor:
            type: number
            description: "Multiplicative factor for backoff"
            default: 1.5
          status_codes:
            type: array
            items:
              type: integer
            description: "Status codes that trigger retry"
            default: [429, 500, 502, 503, 504]
      protocol_adaptations:
        type: object
        description: "Protocol-specific adaptations"
        properties:
          a2a:
            type: object
            description: "A2A protocol adaptations"
            properties:
              message_format:
                type: string
                enum: ["json", "binary", "text"]
                default: "json"
              response_handling:
                type: string
                enum: ["sync", "async"]
                default: "sync"
          mcp:
            type: object
            description: "MCP protocol adaptations"
            properties:
              tool_name:
                type: string
                description: "Tool name for MCP integration"
              result_format:
                type: string
                enum: ["structured", "free_text"]
                default: "structured"
          http:
            type: object
            description: "HTTP protocol adaptations"
            properties:
              base_path:
                type: string
                description: "Base path for HTTP endpoints"
              response_format:
                type: string
                enum: ["json", "binary", "text"]
                default: "json"
```

## Integration Types

The schema supports several integration types, each with type-specific configuration properties:

### Service Integrations

For connecting to external cloud services and platforms:

```yaml
integrations:
  aws_s3:
    type: "service"
    service_type: "cloud_storage"
    description: "AWS S3 bucket integration"
    config:
      provider: "aws"
      service: "s3"
      region: "us-west-2"
      bucket: "openmas-data"
    authentication:
      strategy: "env_token"
      access_key_env: "AWS_ACCESS_KEY_ID"
      secret_key_env: "AWS_SECRET_ACCESS_KEY"
```

### Framework Integrations

For interoperability with other agent frameworks:

```yaml
integrations:
  langchain:
    type: "framework"
    description: "LangChain integration"
    config:
      mode: "agent_wrapper"
      conversion:
        tools: true
        memory: true
        prompts: true
      components:
        agents: ["ReActAgent", "StructuredOutputAgent"]
        tools: ["SerpAPI", "Calculator"]
```

### Database Integrations

For connecting to database systems:

```yaml
integrations:
  postgres:
    type: "database"
    description: "PostgreSQL database integration"
    config:
      host: "${DB_HOST:-localhost}"
      port: "${DB_PORT:-5432}"
      database: "openmas"
      pool_size: 10
      ssl_mode: "require"
    authentication:
      strategy: "env_token"
      username_env: "DB_USER"
      password_env: "DB_PASSWORD"
```

### API Integrations

For connecting to external APIs:

```yaml
integrations:
  github:
    type: "api"
    description: "GitHub API integration"
    config:
      base_url: "https://api.github.com"
      version: "2022-11-28"
      user_agent: "OpenMAS/0.3.0"
    authentication:
      strategy: "oauth"
      token_env: "GITHUB_TOKEN"
    retry:
      enabled: true
      max_retries: 5
      status_codes: [429, 500, 502, 503, 504]
```

### LLM Provider Integrations

For connecting to LLM providers:

```yaml
integrations:
  anthropic:
    type: "llm"
    description: "Anthropic Claude integration"
    config:
      base_url: "https://api.anthropic.com"
      models: ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]
      default_model: "claude-3-sonnet-20240229"
      context_window: 200000
    authentication:
      strategy: "api_key"
      api_key_env: "ANTHROPIC_API_KEY"
```

## Integration Scopes

Integrations can be defined at different scopes:

### Project-Level Integrations

```yaml
# Project configuration
name: "example_project"
version: "1.0.0"

# Project-level integrations
integrations:
  openai:
    type: "llm"
    config:
      base_url: "https://api.openai.com/v1"
      models: ["gpt-4", "gpt-3.5-turbo"]
    authentication:
      strategy: "env_token"
      token_env: "OPENAI_API_KEY"
```

### Agent-Specific Integrations

```yaml
agents:
  example_agent:
    # Agent configuration
    module: "agents.example"
    class: "ExampleAgent"

    # Agent-specific integrations
    integrations:
      slack:
        type: "messaging"
        config:
          channels: ["general", "support"]
        authentication:
          strategy: "oauth"
          token_env: "SLACK_BOT_TOKEN"
```

## Integration with Agent Capabilities

Integrations can be referenced in agent capability definitions:

```yaml
agents:
  example_agent:
    capabilities:
      - name: "search"
        description: "Web search capability"
        integration: "search_api"  # References an integration
        parameters:
          max_results: 10
```

## References in the Unified Schema

The integration configuration schema is referenced in the unified configuration schema:

```yaml
# Unified schema excerpt
type: object
properties:
  name:
    type: string
  version:
    type: string
  integrations:
    $ref: "#/definitions/integrations_schema"
  agents:
    type: object
    additionalProperties:
      type: object
      properties:
        integrations:
          $ref: "#/definitions/integrations_schema"
```
