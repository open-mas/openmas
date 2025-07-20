# Security Configuration Documentation

> **IMPORTANT NOTE**: This document does NOT define the security configuration schema. It only provides documentation and examples for the security configuration sections defined in the [Unified Configuration Schema](../unified_configuration_schema.md), which is the single source of truth for all schema definitions.

This document explains security configuration components in the unified schema. For additional security-specific details, also refer to the [Security Configuration](../security_configuration.md) document.

## Schema References

Security configuration is defined in the [unified configuration schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md) under the `security` root section.

## Security Components

Security configuration in OpenMAS consists of several components:

1. **Authentication** - Identity verification mechanisms
2. **Authorization** - Access control permissions
3. **Encryption** - Data protection measures
4. **Compliance** - Security compliance settings
5. **Rate Limiting** - Request rate controls

## Example Configuration

Below is a simplified example of configuring security settings:

```yaml
# Security configuration example
security:
  authentication:
    enabled: true
    default_provider: "jwt"
    providers:
      jwt:
        secret_key: "${JWT_SECRET}"
        algorithm: "HS256"
        token_expiry_seconds: 3600
      api_key:
        enabled: true
        keys:
          - name: "admin"
            key: "${ADMIN_API_KEY}"
            roles: ["admin"]

  authorization:
    enabled: true
    default_policy: "deny"
    roles:
      - name: "admin"
        permissions: ["*"]
      - name: "user"
        permissions: ["read:*", "write:own"]

  rate_limiting:
    enabled: true
    default_limit: 100
    window_seconds: 60
```

For complete schema details and security best practices, refer to the [Security Configuration](/refactoring_work/00b_overview/03_configuration/security_configuration.md) document.
