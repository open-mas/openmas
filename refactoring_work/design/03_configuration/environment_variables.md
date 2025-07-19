# Environment Variable Substitution in OpenMAS

## Overview

This document describes how OpenMAS supports environment variable substitution in configuration files, allowing for better security, environment-specific configurations, and deployment flexibility. Environment variables are particularly useful for:

1. **Security** - Keeping sensitive information out of configuration files
2. **Environment-Specific Values** - Different settings across development, staging, and production
3. **Containerization** - Supporting container deployment best practices
4. **CI/CD Integration** - Streamlining continuous integration and deployment

## Substitution Patterns

OpenMAS supports several environment variable substitution patterns:

### 1. Basic Substitution

The basic pattern uses the `${ENV_VAR}` syntax:

```yaml
database:
  host: "${DB_HOST}"
  port: "${DB_PORT}"
  user: "${DB_USER}"
```

### 2. Default Values

You can specify default values using the `:-` separator:

```yaml
database:
  host: "${DB_HOST:-localhost}"  # Use DB_HOST env var or default to localhost
  port: "${DB_PORT:-5432}"       # Use DB_PORT env var or default to 5432
  user: "${DB_USER:-postgres}"   # Use DB_USER env var or default to postgres
```

### 3. Required Variables

To mark an environment variable as required (fail if not set):

```yaml
security:
  api_key: "${API_KEY:?API key is required}"  # Fails if API_KEY is not set
```

### 4. Nested Substitution

Environment variables can be nested in complex strings:

```yaml
integrations:
  service_url: "https://${SERVICE_HOST}:${SERVICE_PORT}/api/v1"
```

### 5. Array and Object Substitution

Environment variables can be used in arrays and nested objects:

```yaml
protocols:
  a2a:
    endpoints:
      - "https://${A2A_HOST_1}/endpoint"
      - "https://${A2A_HOST_2}/endpoint"
```

## Naming Conventions

OpenMAS uses a standardized convention for environment variable names:

### 1. Global Configuration

Global settings follow the pattern: `OPENMAS_[COMPONENT]_[SETTING]`

```
OPENMAS_PROTOCOL_A2A_AUTH_REQUIRED=true
OPENMAS_SECURITY_AUTHENTICATION_ENABLED=true
```

### 2. Agent-Specific Configuration

Agent-specific settings follow the pattern: `OPENMAS_AGENT_[AGENT_NAME]_[SETTING]`

```
OPENMAS_AGENT_TRAVEL_COORDINATOR_LOG_LEVEL=debug
OPENMAS_AGENT_CUSTOMER_SERVICE_CAPABILITY_TIMEOUT=30
```

### 3. Environment-Specific Configuration

Environment-specific settings follow the pattern: `OPENMAS_ENV_[ENV_NAME]_[SETTING]`

```
OPENMAS_ENV_PRODUCTION_DB_HOST=prod-db.example.com
OPENMAS_ENV_STAGING_DB_HOST=staging-db.example.com
```

## Configuration Precedence

When the same setting is specified in multiple places, OpenMAS follows this precedence order (highest to lowest):

1. Command line arguments
2. Environment variables
3. Environment-specific configuration
4. Agent-specific configuration
5. Global defaults
6. Framework defaults

## Sensitive Information

For sensitive information like credentials and API keys, always use environment variables instead of hardcoding values:

```yaml
# GOOD - Reference environment variable
security:
  api_key: "${API_KEY}"
  
# BAD - Hardcoded sensitive information
security:
  api_key: "a1b2c3d4e5f6g7h8i9j0"
```

## Complex Substitution Examples

### Multi-Protocol Agent with Environment Variables

```yaml
agents:
  customer_service:
    class: "agents.CustomerServiceAgent"
    type: "llm"
    protocols:
      - type: "a2a-http"
        enabled: "${ENABLE_A2A:-true}"
        options:
          base_url: "https://${A2A_HOST:-localhost}:${A2A_PORT:-8000}/agents"
          agent_id: "${AGENT_ID:-customer_service}"
      - type: "mcp-sse"
        enabled: "${ENABLE_MCP:-true}"
        options:
          server_mode: ${MCP_SERVER_MODE:-true}
          port: "${MCP_PORT:-3000}"
    security:
      authentication:
        providers:
          api_key:
            api_key: "${CS_AGENT_API_KEY:?API key is required}"
```

### Multi-Environment Configuration

```yaml
environments:
  production:
    database:
      host: "${PROD_DB_HOST:?Production DB host required}"
      port: "${PROD_DB_PORT:-5432}"
      user: "${PROD_DB_USER:?DB user required}"
      password: "${PROD_DB_PASSWORD:?DB password required}"
      ssl: true
  
  staging:
    database:
      host: "${STAGING_DB_HOST:-staging-db}"
      port: "${STAGING_DB_PORT:-5432}"
      user: "${STAGING_DB_USER:-openmas}"
      password: "${STAGING_DB_PASSWORD:?Staging DB password required}"
      ssl: true
  
  development:
    database:
      host: "${DEV_DB_HOST:-localhost}"
      port: "${DEV_DB_PORT:-5432}"
      user: "${DEV_DB_USER:-postgres}"
      password: "${DEV_DB_PASSWORD:-postgres}"
      ssl: false
```

## Implementation Details

OpenMAS resolves environment variables during configuration loading:

1. Parse the configuration file (YAML/JSON)
2. Identify all environment variable patterns
3. Substitute values according to the system environment
4. Apply default values where specified and environment variables aren't set
5. Fail with clear error messages for required variables that are missing
6. Validate the final configuration against the schema

## Best Practices

1. **Security First**: Never store sensitive information directly in configuration files
2. **Descriptive Defaults**: Use descriptive default values that indicate the expected format
3. **Documentation**: Document required environment variables in your project README
4. **Validation**: Fail fast with clear error messages for missing required variables
5. **Containerization**: Design for container-friendly configuration
6. **Dev-Prod Parity**: Minimize environment-specific configuration differences

For further details on configuration schema, see the [Unified Configuration Schema](/03_configuration/schema/unified_schema_overview.md).
