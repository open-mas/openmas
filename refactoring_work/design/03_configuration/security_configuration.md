# Security Configuration Standard

## Security Definition
- **Name**: Security Configuration
- **Purpose**: Standardized approach to authentication, authorization, and security controls
- **Protocol Compatibility**: Supports authentication and authorization across multiple protocols (A2A, MCP)
- **Reasoning Agnosticism**: Maintains separation between security controls and reasoning approaches

## Security Schema
```yaml
# Standardized security configuration schema
type: object
properties:
  # System-level security configuration
  security:
    type: object
    description: "Global security configuration"
    properties:
      # Authentication configuration
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
            default: "jwt"

          # Provider configurations
          providers:
            type: object
            description: "Authentication provider configurations"
            properties:
              # Protocol-specific authentication providers
              a2a:
                type: object
                description: "A2A protocol authentication configuration"
                properties:
                  enabled:
                    type: boolean
                    description: "Whether A2A authentication is enabled"
                    default: true
                  auth_types:
                    type: array
                    description: "Authentication types supported for A2A"
                    items:
                      type: string
                      enum: ["api_key", "oauth2", "jwt", "basic"]
                    default: ["api_key", "oauth2"]
                  api_key:
                    type: object
                    description: "API key configuration for A2A"
                    properties:
                      header_name:
                        type: string
                        description: "Header name for API key"
                        default: "X-API-Key"
                      key_source:
                        type: string
                        description: "Source of API keys"
                        enum: ["environment", "file", "database"]
                        default: "environment"
                      env_prefix:
                        type: string
                        description: "Environment variable prefix for API keys"
                        default: "OPENMAS_API_KEY_"
                  oauth2:
                    type: object
                    description: "OAuth2 configuration for A2A"
                    properties:
                      auth_url:
                        type: string
                        description: "OAuth2 authorization endpoint"
                      token_url:
                        type: string
                        description: "OAuth2 token endpoint"
                      client_id:
                        type: string
                        description: "OAuth2 client ID"
                      client_secret:
                        type: string
                        description: "OAuth2 client secret environment variable"
                      scopes:
                        type: array
                        description: "OAuth2 scopes"
                        items:
                          type: string
                        default: ["agent.access"]
                  server_identity:
                    type: object
                    description: "Server identity verification for A2A"
                    properties:
                      verify_agent_card:
                        type: boolean
                        description: "Whether to verify agent cards for authenticity"
                        default: true
                      verify_ssl:
                        type: boolean
                        description: "Whether to verify SSL certificates"
                        default: true
                  push_notifications:
                    type: object
                    description: "Authentication for push notifications"
                    properties:
                      webhook_auth_type:
                        type: string
                        description: "Authentication type for webhook"
                        enum: ["bearer", "api_key", "hmac"]
                        default: "bearer"
                      webhook_token_source:
                        type: string
                        description: "Source of webhook authentication token"
                        enum: ["static", "environment", "generated"]
                        default: "environment"

              # MCP protocol authentication providers
              mcp:
                type: object
                description: "MCP protocol authentication configuration"
                properties:
                  enabled:
                    type: boolean
                    description: "Whether MCP authentication is enabled"
                    default: true
                  server_auth_types:
                    type: array
                    description: "Authentication types supported for MCP server mode"
                    items:
                      type: string
                      enum: ["none", "api_key", "oauth", "basic"]
                    default: ["api_key"]
                  client_auth_types:
                    type: array
                    description: "Authentication types supported for MCP client mode"
                    items:
                      type: string
                      enum: ["none", "api_key", "oauth", "basic"]
                    default: ["api_key"]
                  api_key:
                    type: object
                    description: "API key configuration for MCP"
                    properties:
                      header_name:
                        type: string
                        description: "Header name for API key"
                        default: "X-API-Key"
                      key_source:
                        type: string
                        description: "Source of API keys"
                        enum: ["environment", "file", "database"]
                        default: "environment"
                      env_prefix:
                        type: string
                        description: "Environment variable prefix for API keys"
                        default: "OPENMAS_MCP_API_KEY_"
                  oauth:
                    type: object
                    description: "OAuth configuration for MCP"
                    properties:
                      client_id:
                        type: string
                        description: "OAuth client ID"
                      client_secret_env_var:
                        type: string
                        description: "Environment variable name for OAuth client secret"
                        default: "OPENMAS_MCP_OAUTH_CLIENT_SECRET"
                      token_url:
                        type: string
                        description: "OAuth token endpoint URL"
                      scopes:
                        type: array
                        description: "OAuth scopes"
                        items:
                          type: string
                        default: ["mcp.tools.read", "mcp.tools.write"]
                  tool_authorization:
                    type: object
                    description: "Tool-level authorization configuration"
                    properties:
                      enabled:
                        type: boolean
                        description: "Whether tool-level authorization is enabled"
                        default: false
                      default_policy:
                        type: string
                        description: "Default authorization policy for tools"
                        enum: ["allow", "deny"]
                        default: "deny"
                      tool_policies:
                        type: array
                        description: "Per-tool authorization policies"
                        items:
                          type: object
                          properties:
                            tool_name:
                              type: string
                              description: "Name of the tool"
                            allowed_roles:
                              type: array
                              description: "Roles allowed to access this tool"
                              items:
                                type: string
                            allowed_users:
                              type: array
                              description: "User IDs allowed to access this tool"
                              items:
                                type: string

              # Regular JWT provider
              jwt:
                type: object
                description: "JWT authentication configuration"
                properties:
                  secret_key:
                    type: string
                    description: "JWT secret key (or environment variable reference)"
                  algorithm:
                    type: string
                    description: "JWT signing algorithm"
                    enum: ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
                    default: "HS256"
                  token_expiry_seconds:
                    type: integer
                    description: "JWT token expiry in seconds"
                    default: 3600
                required:
                  - secret_key

              api_key:
                type: object
                description: "API key authentication configuration"
                properties:
                  header_name:
                    type: string
                    description: "Header name for API key"
                    default: "X-API-Key"
                  key_source:
                    type: string
                    description: "Source for API keys"
                    enum: ["environment", "file", "database"]
                    default: "environment"
                  key_env_prefix:
                    type: string
                    description: "Environment variable prefix for API keys"
                    default: "OPENMAS_API_KEY_"
                required:
                  - key_source

              oauth:
                type: object
                description: "OAuth authentication configuration"
                properties:
                  auth_url:
                    type: string
                    description: "OAuth authorization URL"
                  token_url:
                    type: string
                    description: "OAuth token URL"
                  client_id:
                    type: string
                    description: "OAuth client ID (or environment variable reference)"
                  client_secret:
                    type: string
                    description: "OAuth client secret (or environment variable reference)"
                required:
                  - auth_url
                  - token_url
                  - client_id
                  - client_secret
        required:
          - enabled

      # Rate limiting configuration
      rate_limiting:
        type: object
        description: "Rate limiting configuration"
        properties:
          enabled:
            type: boolean
            description: "Whether rate limiting is enabled"
            default: true
          max_requests_per_minute:
            type: integer
            description: "Maximum requests per minute"
            default: 100
          per_ip:
            type: boolean
            description: "Whether rate limiting is per IP address"
            default: true

      # Access control configuration
      access_control:
        type: object
        description: "Access control configuration"
        properties:
          enabled:
            type: boolean
            description: "Whether access control is enabled"
            default: true
          default_policy:
            type: string
            description: "Default access policy"
            enum: ["allow", "deny"]
            default: "deny"
          rules:
            type: array
            description: "Access control rules"
            items:
              type: object
              properties:
                path:
                  type: string
                  description: "Path pattern to match"
                policy:
                  type: string
                  description: "Access policy for this path"
                  enum: ["allow", "deny"]
                except_roles:
                  type: array
                  description: "Roles excepted from this policy"
                  items:
                    type: string
              required:
                - path
                - policy
    required:
      - authentication
```

## Integration with JSONSchema/Pydantic Validation

This security configuration schema can be directly implemented using Pydantic models for validation:

```python
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Union, Literal

class AuthProviderConfig(BaseModel):
    enabled: bool = True
    # Additional provider-specific fields

class A2AAuthConfig(AuthProviderConfig):
    api_key_header: str = "X-API-Key"
    agent_card_auth: bool = True

class MCPAuthConfig(AuthProviderConfig):
    api_key_header: str = "X-MCP-API-Key"
    tool_permissions_enabled: bool = True
    tool_permissions: Dict[str, List[str]] = Field(default_factory=dict)

class JWTAuthConfig(AuthProviderConfig):
    secret_key: str
    algorithm: str = "HS256"
    expiration_minutes: int = 30

class AuthenticationConfig(BaseModel):
    enabled: bool = True
    default_provider: str = "jwt"
    providers: Dict[str, Union[A2AAuthConfig, MCPAuthConfig, JWTAuthConfig]]

    # Validate that at least one provider is enabled
    @validator("providers")
    def validate_providers(cls, v):
        if not any(provider.enabled for provider in v.values()):
            raise ValueError("At least one authentication provider must be enabled")
        return v

class RateLimitingConfig(BaseModel):
    enabled: bool = True
    max_requests: int = 100
    time_window: int = 60

class SecurityConfig(BaseModel):
    authentication: AuthenticationConfig
    rate_limiting: Optional[RateLimitingConfig] = None
```

Using Pydantic enables:
- Automatic validation of security configuration
- Type hinting for better IDE support
- Runtime validation when loading configuration
- JSON Schema generation for documentation

## Complete Configuration Examples

### Multi-Protocol Security Configuration

```yaml
# Example of security configuration supporting both A2A and MCP
security:
  authentication:
    enabled: true
    default_provider: "jwt"
    providers:
      a2a:
        enabled: true
        api_key_header: "X-A2A-API-Key"
        agent_card_auth: true
      mcp:
        enabled: true
        api_key_header: "X-MCP-API-Key"
        tool_permissions_enabled: true
        tool_permissions:
          search_tool: ["user", "admin"]
          generate_tool: ["admin"]
      jwt:
        enabled: true
        secret_key: "${JWT_SECRET_KEY}"
        algorithm: "HS256"
        expiration_minutes: 60
  rate_limiting:
    enabled: true
    max_requests: 100
    time_window: 60
    by_endpoint:
      "/api/generate":
        max_requests: 20
        time_window: 60
```

### A2A-Only Security Configuration

```yaml
# Example of security configuration for A2A-only deployment
security:
  authentication:
    enabled: true
    default_provider: "a2a"
    providers:
      a2a:
        enabled: true
        api_key_header: "X-API-Key"
        agent_card_auth: true
      mcp:
        enabled: false
      jwt:
        enabled: true
        secret_key: "${JWT_SECRET_KEY}"
```

### MCP-Only Security Configuration

```yaml
# Example of security configuration for MCP-only deployment
security:
  authentication:
    enabled: true
    default_provider: "mcp"
    providers:
      a2a:
        enabled: false
      mcp:
        enabled: true
        api_key_header: "X-MCP-API-Key"
        tool_permissions_enabled: true
        tool_permissions:
          search_tool: ["user", "admin"]
      jwt:
        enabled: true
        secret_key: "${JWT_SECRET_KEY}"
```

## Environment-Specific Security Configuration
```yaml
# Environment-specific security configuration
type: object
properties:
  environments:
    type: object
    description: "Environment-specific configurations"
    additionalProperties:
      type: object
      properties:
        security:
          type: object
          description: "Security configuration for this environment"
          properties:
            authentication:
              type: object
              description: "Authentication configuration"
              properties:
                enabled:
                  type: boolean
                  description: "Whether authentication is enabled"
            rate_limiting:
              type: object
              description: "Rate limiting configuration"
              properties:
                enabled:
                  type: boolean
                  description: "Whether rate limiting is enabled"
                max_requests_per_minute:
                  type: integer
                  description: "Maximum requests per minute"
```

## Agent-Specific Security Configuration
```yaml
# Agent-specific security configuration
type: object
properties:
  agents:
    type: object
    description: "Agent configuration"
    additionalProperties:
      type: object
      properties:
        # Agent security configuration
        security:
          type: object
          description: "Agent-specific security configuration"
          properties:
            authentication:
              type: object
              description: "Authentication configuration"
              properties:
                provider:
                  type: string
                  description: "Authentication provider for this agent"
                  enum: ["jwt", "api_key", "oauth"]
            access_control:
              type: object
              description: "Access control configuration"
              properties:
                allowed_capabilities:
                  type: array
                  description: "Capabilities allowed for this agent"
                  items:
                    type: string
```

## A2A Protocol Alignment
- **A2A Authentication Models**: Security configuration aligns with A2A authentication models:
  - Multiple authentication providers (JWT, API Key, OAuth)
  - Credential management through environment variables
  - Message validation for authenticated communication

## Security Configuration Precedence
1. **Command-Line Security Flags** (highest precedence)
2. **Agent-Specific Security Configuration**
3. **Environment-Specific Security Configuration**
4. **System-Level Security Configuration** (lowest precedence)

## Security Implementation Guidelines
- **Secret Management**: [Best practices for managing secrets]
- **Environment Variables**: [How to use environment variables for sensitive data]
- **Security Headers**: [HTTP security headers to include]
- **TLS Configuration**: [TLS/SSL configuration requirements]

## Testing
- **Unit Test Requirements**: [Security-specific test requirements]
- **Integration Test Requirements**: [Security integration test requirements]
- **Security Testing**: [How to test security configurations]

## Usage Examples
```python
# Example security middleware implementation
from openmas.security import SecurityMiddleware

async def setup_security(app, config):
    # Initialize security middleware with configuration
    security = SecurityMiddleware(config["security"])

    # Add authentication middleware
    app.add_middleware(security.authentication_middleware)

    # Add rate limiting middleware
    if config["security"]["rate_limiting"]["enabled"]:
        app.add_middleware(security.rate_limiting_middleware)

    # Add access control middleware
    if config["security"]["access_control"]["enabled"]:
        app.add_middleware(security.access_control_middleware)
```
