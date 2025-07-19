# Encryption

## Overview

This document describes the encryption mechanisms used in OpenMAS to protect data confidentiality and integrity. OpenMAS implements a comprehensive encryption framework that protects data at rest and in transit across all supported protocols while maintaining the reasoning-agnostic architecture.

## Encryption Framework

OpenMAS implements a modular encryption framework that supports different encryption methods:

```
┌───────────────────────────────────────────────┐
│           Encryption Provider                 │
│                                               │
│  ┌─────────────┐  ┌─────────────┐   ┌──────┐  │
│  │ Algorithm   │  │ Key         │   │Format│  │
│  │ Provider    │  │ Management  │   │Handler│  │
│  └─────────────┘  └─────────────┘   └──────┘  │
│         │                │              │     │
└─────────┼────────────────┼──────────────┼─────┘
          │                │              │
┌─────────▼────┐   ┌───────▼────┐  ┌─────▼─────┐
│ Data at Rest │   │ Data in    │  │ Key       │
│ Encryption   │   │ Transit    │  │ Storage   │
└──────────────┘   └────────────┘  └───────────┘
```

## Data Protection Categories

### 1. Data at Rest Encryption

Encryption for stored data:

```yaml
data_protection:
  encryption:
    data_at_rest:
      enabled: true
      algorithm: "AES-256-GCM"
      key_derivation: "PBKDF2"
      key_rotation_days: 90
      secure_storage:
        type: "file"
        path: "/path/to/secure/keystore"
        password_env: "KEYSTORE_PASSWORD"
```

Key features:
- **Storage Encryption**: Encryption of persistent data
- **File-Level Encryption**: Encryption of individual files
- **Database Encryption**: Encryption of database content
- **Memory Protection**: Protection of sensitive data in memory
- **Secure Key Storage**: Protected storage for encryption keys

### 2. Data in Transit Encryption

Encryption for data being transmitted:

```yaml
data_protection:
  encryption:
    data_in_transit:
      transport_layer:
        type: "TLS"
        version: "1.3"
        ciphers: ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"]
      message_layer:
        enabled: true
        algorithm: "AES-256-GCM"
        key_exchange: "ECDHE"
```

Key features:
- **Transport Encryption**: TLS for secure communication
- **Message Encryption**: End-to-end message encryption
- **Perfect Forward Secrecy**: Protection of past communications
- **Cipher Suite Control**: Configuration of encryption algorithms
- **Certificate Management**: Management of TLS certificates

### 3. Key Management

Management of encryption keys:

```yaml
data_protection:
  encryption:
    key_management:
      provider: "local"  # Options: local, kms, vault
      key_derivation: "PBKDF2"
      master_key_env: "MASTER_KEY"
      key_rotation:
        enabled: true
        interval_days: 90
        automatic: true
      key_backup:
        enabled: true
        location: "/path/to/backup"
```

Key features:
- **Key Generation**: Secure generation of encryption keys
- **Key Storage**: Protected storage for keys
- **Key Rotation**: Regular rotation of encryption keys
- **Key Derivation**: Derivation of keys from master keys
- **Key Backup**: Secure backup of encryption keys

## Protocol-Specific Encryption

### MCP Encryption

Encryption for Model Context Protocol:

```yaml
data_protection:
  encryption:
    protocol_specific:
      mcp:
        message_encryption: true
        function_call_encryption: true
        streaming_encryption: true
        algorithms:
          message: "AES-256-GCM"
          function: "AES-256-GCM"
          streaming: "AES-256-CTR"
```

Key features:
- **Message Encryption**: End-to-end encryption of messages
- **Function Call Protection**: Encryption of function calls and parameters
- **Streaming Encryption**: Encryption for streaming content
- **Adaptive Algorithms**: Different algorithms for different contexts

### A2A Encryption

Encryption for Agent-to-Agent Protocol:

```yaml
data_protection:
  encryption:
    protocol_specific:
      a2a:
        agent_card_encryption: true
        message_encryption: true
        content_encryption: true
        algorithms:
          agent_card: "RSA-2048"
          message: "AES-256-GCM"
          content: "AES-256-GCM"
```

Key features:
- **Agent Card Protection**: Encryption of agent identity information
- **Message Encryption**: End-to-end encryption of messages
- **Content Encryption**: Encryption of message content
- **Layered Encryption**: Multiple encryption layers for defense in depth

### HTTP Encryption

Encryption for HTTP-based communication:

```yaml
data_protection:
  encryption:
    protocol_specific:
      http:
        transport_encryption: true
        payload_encryption: true
        header_encryption: false
        algorithms:
          transport: "TLS-1.3"
          payload: "AES-256-GCM"
```

Key features:
- **TLS Transport**: HTTPS for secure communication
- **Payload Encryption**: Encryption of HTTP payloads
- **Header Protection**: Selective encryption of headers
- **Cookie Protection**: Protection of sensitive cookies

### MQTT Encryption

Encryption for MQTT-based communication:

```yaml
data_protection:
  encryption:
    protocol_specific:
      mqtt:
        transport_encryption: true
        payload_encryption: true
        topic_encryption: false
        algorithms:
          transport: "TLS-1.3"
          payload: "AES-256-GCM"
```

Key features:
- **TLS Transport**: MQTT over TLS for secure communication
- **Payload Encryption**: End-to-end encryption of MQTT payloads
- **Topic Protection**: Protection of sensitive topic information
- **QoS Protection**: Ensure security across QoS levels

### gRPC Encryption

Encryption for gRPC-based communication:

```yaml
data_protection:
  encryption:
    protocol_specific:
      grpc:
        transport_encryption: true
        payload_encryption: true
        metadata_encryption: false
        algorithms:
          transport: "TLS-1.3"
          payload: "AES-256-GCM"
```

Key features:
- **TLS Transport**: gRPC over TLS for secure communication
- **Payload Encryption**: End-to-end encryption of payloads
- **Metadata Protection**: Protection of sensitive metadata
- **Stream Protection**: Protection of streaming data

## Data Classification

OpenMAS supports a structured approach to data classification:

```yaml
data_protection:
  classification:
    levels:
      - name: "public"
        description: "Information that can be freely shared"
        encryption_required: false
      - name: "internal"
        description: "Information for internal use only"
        encryption_required: true
        algorithm: "AES-128-GCM"
      - name: "confidential"
        description: "Sensitive information requiring protection"
        encryption_required: true
        algorithm: "AES-256-GCM"
      - name: "restricted"
        description: "Highly sensitive information"
        encryption_required: true
        algorithm: "AES-256-GCM"
        key_rotation_days: 30
```

Features:
- **Sensitivity Levels**: Definition of data sensitivity levels
- **Classification Rules**: Rules for classifying data
- **Protection Requirements**: Requirements for each level
- **Encryption Standards**: Encryption standards for each level
- **Access Controls**: Access control requirements for each level

## Data Minimization

OpenMAS implements data minimization practices:

```yaml
data_protection:
  minimization:
    collection_limits:
      enabled: true
      collect_only_required: true
    retention:
      enabled: true
      default_retention_days: 30
      policies:
        - data_type: "logs"
          retention_days: 90
        - data_type: "messages"
          retention_days: 7
    anonymization:
      enabled: true
      techniques: ["pseudonymization", "generalization"]
```

Features:
- **Collection Minimization**: Only collect necessary data
- **Retention Policies**: Time-limited data retention
- **Data Anonymization**: Removal of identifying information
- **Pseudonymization**: Replacement of identifiers with pseudonyms
- **Purpose Limitation**: Use data only for intended purposes

## Integration with Reasoning

Encryption integrates with OpenMAS's reasoning-agnostic architecture:

```
┌─────────────────────────────────┐
│          Communication Layer    │
│          ("Body")               │
│                                 │
│  ┌───────────────────────────┐  │
│  │  Encryption System        │  │
│  └─────────────┬─────────────┘  │
│                │                │
└────────────────┼────────────────┘
                 │
┌────────────────┼────────────────┐
│                │                │
│  ┌─────────────▼─────────────┐  │
│  │  Reasoning Encryption     │  │
│  │  Interface               │  │
│  └───────────────────────────┘  │
│                                 │
│          Reasoning Layer        │
│          ("Brain")              │
└─────────────────────────────────┘
```

Each reasoning approach can implement encryption differently:

- **LLM Reasoning**: Encryption of prompts and responses
- **Rule-Based Reasoning**: Protection of rule definitions
- **BDI Reasoning**: Encryption of beliefs and intentions
- **Hybrid Reasoning**: Combined encryption approaches

## Configuration

Encryption is configured through the unified configuration schema:

```yaml
# System-level encryption
data_protection:
  encryption:
    data_at_rest:
      # Data at rest encryption settings...
    data_in_transit:
      # Data in transit encryption settings...

# Agent-specific encryption
agents:
  - id: "agent1"
    # Other agent configuration...
    data_protection:
      encryption:
        # Agent-specific encryption settings...

# Protocol-specific encryption
protocols:
  - type: "mcp"
    # Other protocol configuration...
    data_protection:
      encryption:
        # Protocol-specific encryption settings...
```

## Supported Encryption Algorithms

### Symmetric Encryption

- **AES-256-GCM**: Authenticated encryption with associated data
- **AES-256-CBC**: Cipher Block Chaining mode with PKCS#7 padding
- **AES-256-CTR**: Counter mode for stream encryption
- **ChaCha20-Poly1305**: Authenticated encryption for high performance

### Asymmetric Encryption

- **RSA-2048**: Public key cryptography (2048-bit)
- **RSA-4096**: Public key cryptography (4096-bit)
- **ECC P-256**: Elliptic Curve Cryptography (NIST P-256)
- **ECC P-384**: Elliptic Curve Cryptography (NIST P-384)

### Key Derivation

- **PBKDF2**: Password-Based Key Derivation Function 2
- **Argon2id**: Memory-hard key derivation function
- **HKDF**: HMAC-based Key Derivation Function

### Digital Signatures

- **RSA-PSS**: Probabilistic Signature Scheme
- **ECDSA**: Elliptic Curve Digital Signature Algorithm
- **Ed25519**: Edwards-curve Digital Signature Algorithm

## Best Practices

1. **Defense in Depth**: Layer encryption controls
2. **Strong Algorithms**: Use strong, industry-standard algorithms
3. **Key Management**: Implement robust key management
4. **Transport Security**: Always encrypt data in transit
5. **Sensitive Data**: Always encrypt sensitive data at rest
6. **End-to-End Encryption**: Implement end-to-end encryption where possible
7. **Perfect Forward Secrecy**: Protect past communications
8. **Key Rotation**: Regularly rotate encryption keys
9. **Validation**: Validate encryption implementations
10. **Compliance**: Ensure compliance with relevant standards

## Related Documentation

- [Security Principles](../architecture/security_principles.md)
- [Authentication](../authentication/README.md)
- [Authorization](../authorization/README.md)
- [Communication Security](../communication/README.md)
- [Configuration Schema](../../03_configuration/schema/security.md)
