# Authentication Mechanisms

## Overview

This document describes the authentication mechanisms supported by OpenMAS. These mechanisms provide secure identity verification for agents, services, and users while maintaining OpenMAS's reasoning-agnostic design and multi-protocol support.

## Authentication Provider Framework

OpenMAS implements a pluggable authentication provider framework that allows different authentication mechanisms to be used interchangeably:

```
┌───────────────────────────────────────────────┐
│          Authentication Provider               │
│                                               │
│  ┌─────────────┐  ┌─────────────┐   ┌──────┐  │
│  │ Credential  │  │ Identity    │   │Token │  │
│  │ Verification│  │ Management  │   │Issuer│  │
│  └─────────────┘  └─────────────┘   └──────┘  │
│         │                │              │     │
└─────────┼────────────────┼──────────────┼─────┘
          │                │              │
┌─────────▼────┐   ┌───────▼────┐  ┌─────▼─────┐
│ Protocols    │   │ Agents     │  │ Services  │
└──────────────┘   └────────────┘  └───────────┘
```

## Supported Authentication Mechanisms

### 1. API Key Authentication

Simple API key-based authentication:

```yaml
authentication:
  provider: "api_key"
  settings:
    key_header: "X-API-Key"
    keys:
      - id: "agent1"
        key: "${AGENT1_API_KEY}"
      - id: "agent2"
        key: "${AGENT2_API_KEY}"
```

Features:
- **Simplicity**: Easy to implement and use
- **Low Overhead**: Minimal processing overhead
- **Stateless**: No server-side state required
- **Key Rotation**: Support for key rotation

Limitations:
- **Limited Security**: Keys must be securely transmitted and stored
- **Limited Context**: No inherent identity information beyond the key
- **No Expiration**: Keys typically don't expire automatically

### 2. JWT Authentication

JSON Web Token (JWT) based authentication:

```yaml
authentication:
  provider: "jwt"
  settings:
    token_header: "Authorization"
    token_prefix: "Bearer"
    signing_key: "${JWT_SIGNING_KEY}"
    algorithm: "HS256"
    expiration: 3600  # seconds
    issuer: "openmas"
    audience: "openmas-agents"
```

Features:
- **Stateless**: No server-side state required
- **Claim-Based**: Rich identity information in claims
- **Expiration**: Automatic token expiration
- **Signature Verification**: Cryptographic signature verification
- **Standard Format**: Industry-standard format

Limitations:
- **Token Size**: Tokens can become large with many claims
- **Revocation**: Difficult to revoke before expiration

### 3. OAuth 2.0 / OpenID Connect

Integration with OAuth 2.0 and OpenID Connect identity providers:

```yaml
authentication:
  provider: "oauth2"
  settings:
    issuer: "https://auth.example.com"
    client_id: "${OAUTH_CLIENT_ID}"
    client_secret: "${OAUTH_CLIENT_SECRET}"
    redirect_uri: "https://api.example.com/callback"
    scopes: ["openid", "profile", "agent"]
    token_endpoint: "https://auth.example.com/token"
    authorize_endpoint: "https://auth.example.com/authorize"
    jwks_uri: "https://auth.example.com/.well-known/jwks.json"
```

Features:
- **Federated Identity**: Integration with external identity providers
- **Delegation**: Support for delegated authentication
- **Rich Identity**: Detailed identity information
- **Standard Flow**: Industry-standard authentication flows
- **Refresh Tokens**: Support for token refresh

Limitations:
- **Complexity**: More complex implementation and configuration
- **External Dependency**: Reliance on external identity providers

### 4. Mutual TLS (mTLS)

Certificate-based mutual authentication:

```yaml
authentication:
  provider: "mtls"
  settings:
    ca_cert: "/path/to/ca.crt"
    client_cert_required: true
    verify_depth: 3
    certificate_header: "X-Client-Cert"
    subject_header: "X-Client-Subject"
```

Features:
- **Strong Authentication**: Cryptographically strong authentication
- **Mutual Authentication**: Both client and server authenticate
- **Certificate Management**: Support for certificate lifecycle
- **Industry Standard**: Based on widely-used TLS standard
- **Identity Binding**: Strong binding to cryptographic identity

Limitations:
- **Certificate Management**: Requires certificate infrastructure
- **Complexity**: More complex to set up and manage
- **Performance**: Higher computational overhead

### 5. HMAC Request Signing

Request signing using HMAC:

```yaml
authentication:
  provider: "hmac_signing"
  settings:
    algorithm: "HMAC-SHA256"
    secret_key: "${HMAC_SECRET_KEY}"
    headers_to_sign: ["(request-target)", "host", "date", "content-type"]
    signature_header: "Signature"
    key_id_required: true
```

Features:
- **Request Integrity**: Ensures request hasn't been tampered with
- **Replay Protection**: Can include timestamp to prevent replay
- **Selective Signing**: Can sign specific headers or content
- **Standard Approach**: Based on HTTP Signatures standard

Limitations:
- **Secret Management**: Requires secure key management
- **Clock Synchronization**: Often relies on synchronized clocks
- **Complexity**: More complex than simple token approaches

## Protocol-Specific Authentication

### MCP Authentication

Authentication for Model Context Protocol:

```yaml
authentication:
  provider: "jwt"
  settings:
    # JWT settings...
  protocol_specific:
    mcp:
      function_call_verification: true
      streaming_auth_interval: 60  # seconds
      message_signing: true
```

Key features:
- **Function Call Verification**: Authentication for function calls
- **Streaming Authentication**: Periodic re-authentication during streams
- **Message Signing**: Cryptographic signatures for messages

### A2A Authentication

Authentication for Agent-to-Agent Protocol:

```yaml
authentication:
  provider: "oauth2"
  settings:
    # OAuth settings...
  protocol_specific:
    a2a:
      agent_card_verification: true
      agent_registry_authentication: true
      card_signature_verification: true
```

Key features:
- **Agent Card Verification**: Verify agent identity through cards
- **Agent Registry**: Authentication against agent registry
- **Card Signatures**: Cryptographic verification of agent cards

### HTTP Authentication

Authentication for HTTP-based communication:

```yaml
authentication:
  provider: "api_key"
  settings:
    # API key settings...
  protocol_specific:
    http:
      header_name: "X-API-Key"
      cookie_support: false
      query_param_support: false
```

Key features:
- **Header-Based**: Authentication via HTTP headers
- **Cookie Support**: Optional cookie-based authentication
- **Query Parameters**: Optional query parameter authentication

### MQTT Authentication

Authentication for MQTT-based communication:

```yaml
authentication:
  provider: "mtls"
  settings:
    # mTLS settings...
  protocol_specific:
    mqtt:
      username_password_fallback: true
      broker_authentication: true
      client_id_validation: true
```

Key features:
- **Client Certificate**: Certificate-based client authentication
- **Username/Password**: Optional username/password fallback
- **Broker Authentication**: Authenticate the MQTT broker

### gRPC Authentication

Authentication for gRPC-based communication:

```yaml
authentication:
  provider: "jwt"
  settings:
    # JWT settings...
  protocol_specific:
    grpc:
      metadata_key: "authorization"
      intercept_unauthenticated: true
      per_rpc_credentials: true
```

Key features:
- **Metadata-Based**: Authentication via gRPC metadata
- **Interceptors**: Authentication interceptors
- **Per-RPC Credentials**: Support for per-RPC authentication

## Multi-Factor Authentication

OpenMAS supports multi-factor authentication through factor composition:

```yaml
authentication:
  multi_factor:
    enabled: true
    required_factors: 2
    factors:
      - provider: "api_key"
        settings:
          # API key settings...
      - provider: "jwt"
        settings:
          # JWT settings...
      - provider: "mtls"
        settings:
          # mTLS settings...
```

Features:
- **Factor Composition**: Combine multiple authentication factors
- **Flexible Requirements**: Configure required number of factors
- **Factor Independence**: Each factor can be independently verified
- **Risk-Based Authentication**: Adjust factor requirements based on risk

## Authentication Workflows

### Agent-to-Agent Authentication

```
┌────────┐                      ┌────────┐
│ Agent1 │                      │ Agent2 │
└───┬────┘                      └───┬────┘
    │                               │
    │  1. Authentication Request    │
    │─────────────────────────────>│
    │                               │
    │  2. Challenge                 │
    │<─────────────────────────────│
    │                               │
    │  3. Challenge Response        │
    │─────────────────────────────>│
    │                               │
    │  4. Verification              │
    │<─────────────────────────────│
    │                               │
    │  5. Secure Communication      │
    │<────────────────────────────>│
```

### Service Authentication

```
┌────────┐                      ┌────────┐
│ Agent  │                      │Service │
└───┬────┘                      └───┬────┘
    │                               │
    │  1. Service Request + Auth    │
    │─────────────────────────────>│
    │                               │
    │  2. Auth Verification         │
    │<─────────────────────────────│
    │                               │
    │  3. Service Response          │
    │<─────────────────────────────│
```

## Integration with Reasoning

Authentication integrates with OpenMAS's reasoning-agnostic architecture through the Reasoning Security Interface (RSI):

```
┌─────────────────────────────────┐
│          Communication Layer    │
│          ("Body")               │
│                                 │
│  ┌───────────────────────────┐  │
│  │  Authentication System    │  │
│  └─────────────┬─────────────┘  │
│                │                │
└────────────────┼────────────────┘
                 │
┌────────────────┼────────────────┐
│                │                │
│  ┌─────────────▼─────────────┐  │
│  │  Reasoning Security       │  │
│  │  Interface (RSI)          │  │
│  └───────────────────────────┘  │
│                                 │
│          Reasoning Layer        │
│          ("Brain")              │
└─────────────────────────────────┘
```

The Reasoning Security Interface (RSI) provides a standardized way for reasoning engines to access authenticated principal information through the `RSI.get_current_principal()` method. This method returns a `SecurityPrincipalInfo` object containing details about the authenticated entity, such as its ID, roles, and attributes.

For complete details on how reasoning engines can access principal information, refer to the [Reasoning Security Interface (RSI) specification](../reasoning_security_interface.md).

Each reasoning approach can implement the authentication interface differently:

- **LLM Reasoning**: Authentication for LLM API access
- **Rule-Based Reasoning**: Authentication rules and policies
- **BDI Reasoning**: Authentication beliefs and intentions
- **Hybrid Reasoning**: Combined authentication approaches

## Configuration

Authentication is configured through the unified configuration schema:

```yaml
# System-level authentication
authentication:
  provider: "jwt"
  settings:
    # JWT settings...

# Agent-specific authentication
agents:
  - id: "agent1"
    # Other agent configuration...
    authentication:
      provider: "api_key"
      settings:
        # API key settings...

# Protocol-specific authentication
protocols:
  - type: "mcp"
    # Other protocol configuration...
    authentication:
      provider: "oauth2"
      settings:
        # OAuth settings...
```

## Best Practices

1. **Multiple Factors**: Use multi-factor authentication for sensitive operations
2. **Secret Management**: Securely manage authentication secrets and credentials
3. **Protocol-Specific Auth**: Use appropriate authentication for each protocol
4. **Expiration Policies**: Implement token expiration and rotation policies
5. **Secure Transport**: Always use authentication over secure transport (TLS)
6. **Least Privilege**: Authenticate with minimal necessary permissions
7. **Audit Trail**: Maintain authentication audit trails
8. **Consistent Identity**: Maintain consistent identity across protocols
9. **Revocation**: Implement credential revocation mechanisms
10. **Protocol Independence**: Design authentication to work across protocols

## Related Documentation

- [Security Principles](../architecture/security_principles.md)
- [Authorization](../authorization/README.md)
- [Communication Security](../communication/README.md)
- [Configuration Schema](../../03_configuration/schema/security.md)
