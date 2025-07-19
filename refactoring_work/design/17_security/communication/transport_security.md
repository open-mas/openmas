# Transport Security

## Overview

This document describes the transport security mechanisms used in OpenMAS to protect communication channels. Transport security ensures that all data transmitted between agents, services, and external systems is protected against interception, tampering, and impersonation while maintaining OpenMAS's reasoning-agnostic design and multi-protocol support.

## Transport Security Layer

OpenMAS implements a comprehensive transport security layer that provides secure communication channels:

```
┌───────────────────────────────────────────────┐
│         Transport Security Layer              │
│                                               │
│  ┌─────────────┐  ┌─────────────┐   ┌──────┐  │
│  │ Protocol    │  │ Certificate │   │Cipher│  │
│  │ Handler     │  │ Manager     │   │Suite │  │
│  └─────────────┘  └─────────────┘   └──────┘  │
│         │                │              │     │
└─────────┼────────────────┼──────────────┼─────┘
          │                │              │
┌─────────▼────┐   ┌───────▼────┐  ┌─────▼─────┐
│ TLS/DTLS     │   │ X.509      │  │ Crypto    │
│ Handling     │   │ Certificates│  │ Providers │
└──────────────┘   └────────────┘  └───────────┘
```

## Transport Security Mechanisms

### 1. TLS (Transport Layer Security)

Secure transport using TLS:

```yaml
transport_security:
  tls:
    enabled: true
    version: "1.3"
    certificate:
      source: "file"  # Options: file, acme, vault
      cert_file: "/path/to/cert.pem"
      key_file: "/path/to/key.pem"
    cipher_suites:
      - "TLS_AES_256_GCM_SHA384"
      - "TLS_CHACHA20_POLY1305_SHA256"
    verification:
      client_auth: "request"  # Options: none, request, require
      ca_file: "/path/to/ca.pem"
```

Features:
- **TLS 1.3**: Latest TLS protocol with improved security and performance
- **Strong Ciphers**: Modern authenticated encryption ciphers
- **Certificate Management**: Comprehensive certificate management
- **Client Authentication**: Optional mutual TLS authentication
- **Perfect Forward Secrecy**: Protection of past communications

### 2. DTLS (Datagram Transport Layer Security)

Secure transport for datagram-based protocols:

```yaml
transport_security:
  dtls:
    enabled: true
    version: "1.2"
    certificate:
      source: "file"
      cert_file: "/path/to/cert.pem"
      key_file: "/path/to/key.pem"
    cipher_suites:
      - "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384"
      - "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
    retry_handling:
      max_retries: 5
      timeout_ms: 1000
```

Features:
- **Datagram Support**: Secure transport for UDP-based protocols
- **Retry Handling**: Robust handling of packet loss
- **Anti-Replay**: Protection against replay attacks
- **Datagram Integrity**: Integrity protection for datagrams
- **Low Overhead**: Optimized for efficiency in datagram contexts

### 3. Certificate Management

Management of X.509 certificates:

```yaml
transport_security:
  certificate_management:
    provider: "acme"  # Options: manual, acme, vault
    acme:
      directory_url: "https://acme-v02.api.letsencrypt.org/directory"
      email: "admin@example.com"
      domains: ["api.example.com", "*.example.com"]
      challenge_type: "http-01"
      renewal_days_before: 30
    rotation:
      enabled: true
      interval_days: 90
      automatic: true
```

Features:
- **Automated Management**: Automated certificate issuance and renewal
- **Multi-Domain Support**: Support for multiple domains
- **Wildcard Certificates**: Support for wildcard certificates
- **Certificate Rotation**: Regular rotation of certificates
- **Revocation Handling**: Handling of certificate revocation

### 4. Secure Connection Management

Management of secure connections:

```yaml
transport_security:
  connection_management:
    session_tickets: false
    session_timeout: 3600  # seconds
    connection_timeout: 30  # seconds
    max_connections: 1000
    idle_connection_timeout: 600  # seconds
```

Features:
- **Session Management**: Secure session management
- **Connection Limits**: Protection against resource exhaustion
- **Timeout Controls**: Security-focused timeout controls
- **Connection Reuse**: Secure connection reuse
- **Graceful Shutdown**: Secure connection termination

## Protocol-Specific Transport Security

### MCP Transport Security

Transport security for Model Context Protocol:

```yaml
transport_security:
  protocol_specific:
    mcp:
      tls:
        enabled: true
        version: "1.3"
      client_verification:
        enabled: true
        mode: "required"
      streaming_security:
        keepalive_interval: 30  # seconds
        rekey_interval: 3600  # seconds
```

Key features:
- **TLS Transport**: Secure TLS transport for MCP
- **Client Verification**: Verification of client identity
- **Streaming Security**: Specific controls for streaming communication
- **Rekeying**: Periodic renewal of encryption keys

### A2A Transport Security

Transport security for Agent-to-Agent Protocol:

```yaml
transport_security:
  protocol_specific:
    a2a:
      tls:
        enabled: true
        version: "1.3"
      agent_verification:
        enabled: true
        mode: "required"
      communication_channels:
        secure_establishment: true
        channel_isolation: true
```

Key features:
- **TLS Transport**: Secure TLS transport for A2A
- **Agent Verification**: Verification of agent identity
- **Secure Channels**: Secure communication channel establishment
- **Channel Isolation**: Isolation between communication channels

### HTTP Transport Security

Transport security for HTTP-based communication:

```yaml
transport_security:
  protocol_specific:
    http:
      tls:
        enabled: true
        version: "1.3"
      hsts:
        enabled: true
        max_age: 31536000  # 1 year
        include_subdomains: true
        preload: true
      policy_headers:
        content_security_policy: "default-src 'self'"
        referrer_policy: "strict-origin-when-cross-origin"
```

Key features:
- **HTTPS**: HTTP over TLS for secure communication
- **HSTS**: HTTP Strict Transport Security
- **Security Headers**: HTTP security headers
- **CSP**: Content Security Policy
- **XSS Protection**: Cross-site scripting protection

### MQTT Transport Security

Transport security for MQTT-based communication:

```yaml
transport_security:
  protocol_specific:
    mqtt:
      tls:
        enabled: true
        version: "1.3"
      client_verification:
        enabled: true
        mode: "required"
      broker_verification:
        enabled: true
        ca_file: "/path/to/broker-ca.pem"
```

Key features:
- **TLS Transport**: MQTT over TLS for secure communication
- **Client Verification**: Verification of client identity
- **Broker Verification**: Verification of broker identity
- **Secure Connect**: Secure connection establishment

### gRPC Transport Security

Transport security for gRPC-based communication:

```yaml
transport_security:
  protocol_specific:
    grpc:
      tls:
        enabled: true
        version: "1.3"
      mtls:
        enabled: true
        client_ca: "/path/to/client-ca.pem"
      channel_credentials:
        per_rpc_credentials: true
        channel_binding: true
```

Key features:
- **TLS Transport**: gRPC over TLS for secure communication
- **mTLS**: Mutual TLS authentication
- **Channel Credentials**: Secure channel credentials
- **Channel Binding**: Binding between channel and message security

## Integration with Reasoning

Transport security integrates with OpenMAS's reasoning-agnostic architecture:

```
┌─────────────────────────────────┐
│          Communication Layer    │
│          ("Body")               │
│                                 │
│  ┌───────────────────────────┐  │
│  │  Transport Security       │  │
│  └─────────────┬─────────────┘  │
│                │                │
└────────────────┼────────────────┘
                 │
┌────────────────┼────────────────┐
│                │                │
│  ┌─────────────▼─────────────┐  │
│  │  Reasoning Transport      │  │
│  │  Interface               │  │
│  └───────────────────────────┘  │
│                                 │
│          Reasoning Layer        │
│          ("Brain")              │
└─────────────────────────────────┘
```

Each reasoning approach interfaces with transport security through a standard interface, maintaining the separation between communication and reasoning while ensuring that all communication is secure regardless of the reasoning approach used.

## TLS Configuration Examples

### Basic Server TLS Configuration

```yaml
transport_security:
  tls:
    enabled: true
    version: "1.3"
    certificate:
      source: "file"
      cert_file: "/path/to/cert.pem"
      key_file: "/path/to/key.pem"
    cipher_suites:
      - "TLS_AES_256_GCM_SHA384"
      - "TLS_CHACHA20_POLY1305_SHA256"
    verification:
      client_auth: "none"
```

### Mutual TLS Configuration

```yaml
transport_security:
  tls:
    enabled: true
    version: "1.3"
    certificate:
      source: "file"
      cert_file: "/path/to/cert.pem"
      key_file: "/path/to/key.pem"
    cipher_suites:
      - "TLS_AES_256_GCM_SHA384"
      - "TLS_CHACHA20_POLY1305_SHA256"
    verification:
      client_auth: "require"
      ca_file: "/path/to/ca.pem"
      verify_depth: 3
      crl_file: "/path/to/crl.pem"
```

### Client TLS Configuration

```yaml
transport_security:
  tls:
    enabled: true
    version: "1.3"
    client:
      certificate:
        source: "file"
        cert_file: "/path/to/client-cert.pem"
        key_file: "/path/to/client-key.pem"
      server_verification:
        enabled: true
        ca_file: "/path/to/server-ca.pem"
        hostname_verification: true
```

## Certificate Generation Examples

### Self-Signed Certificate Generation

```bash
# Generate CA key and certificate
openssl genrsa -out ca.key 4096
openssl req -new -x509 -key ca.key -out ca.crt -days 365 -subj "/CN=OpenMAS CA"

# Generate server key and CSR
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=api.example.com"

# Sign the server certificate with the CA
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365
```

### Let's Encrypt ACME Configuration

```yaml
transport_security:
  certificate_management:
    provider: "acme"
    acme:
      directory_url: "https://acme-v02.api.letsencrypt.org/directory"
      email: "admin@example.com"
      domains: ["api.example.com"]
      challenge_type: "http-01"
      renewal_days_before: 30
      http_challenge:
        port: 80
        proxy: false
```

## Secure Configuration Verification

OpenMAS provides tools to verify the security of transport configurations:

```yaml
transport_security:
  verification:
    enabled: true
    checks:
      - tls_version_check
      - cipher_suite_strength
      - certificate_validity
      - key_length_check
      - protocol_downgrade_check
    schedule:
      startup: true
      interval_hours: 24
```

Features:
- **Automated Checks**: Automated verification of security configuration
- **Compliance Verification**: Verification against security standards
- **Regular Checks**: Scheduled verification of configuration
- **Configuration Validation**: Validation of transport configuration
- **Security Alerts**: Alerts for security issues

## Best Practices

1. **Modern TLS**: Use TLS 1.3 where possible
2. **Strong Ciphers**: Use strong, authenticated encryption ciphers
3. **Certificate Management**: Implement robust certificate management
4. **Certificate Validation**: Always validate certificates
5. **Mutual Authentication**: Use mutual TLS where appropriate
6. **Perfect Forward Secrecy**: Ensure PFS is enabled
7. **Regular Rotation**: Regularly rotate certificates and keys
8. **Security Headers**: Use appropriate HTTP security headers
9. **Connection Management**: Implement secure connection management
10. **Protocol Version Control**: Control acceptable protocol versions

## Related Documentation

- [Security Principles](../architecture/security_principles.md)
- [Authentication](../authentication/README.md)
- [Authorization](../authorization/README.md)
- [Message Security](./message_security.md)
- [Configuration Schema](../../03_configuration/schema/security.md)
