# Message Security

## Overview

This document describes the message security mechanisms used in OpenMAS to protect individual messages. Message security ensures that all messages exchanged between agents, services, and external systems maintain their confidentiality, integrity, and authenticity, even when the transport layer might be compromised. This aligns with OpenMAS's reasoning-agnostic design and multi-protocol support.

## Message Security Layer

OpenMAS implements a comprehensive message security layer that provides end-to-end protection for messages:

```
┌───────────────────────────────────────────────┐
│          Message Security Layer               │
│                                               │
│  ┌─────────────┐  ┌─────────────┐   ┌──────┐  │
│  │ Encryption  │  │ Signing     │   │Format│  │
│  │ Provider    │  │ Provider    │   │Handler│  │
│  └─────────────┘  └─────────────┘   └──────┘  │
│         │                │              │     │
└─────────┼────────────────┼──────────────┼─────┘
          │                │              │
┌─────────▼────┐   ┌───────▼────┐  ┌─────▼─────┐
│ Protocol     │   │ Content    │  │ Credential│
│ Messages     │   │ Validation │  │ Management│
└──────────────┘   └────────────┘  └───────────┘
```

## Message Security Mechanisms

### 1. Message Encryption

End-to-end encryption of messages:

```yaml
message_security:
  encryption:
    enabled: true
    algorithm: "AES-256-GCM"
    key_exchange: "ECDHE-P256"
    per_session_keys: true
    key_rotation_messages: 1000
```

Features:
- **End-to-End Encryption**: Protection against intermediaries
- **Authenticated Encryption**: Confidentiality and authenticity
- **Forward Secrecy**: Protection of past messages
- **Key Management**: Secure key exchange and management
- **Key Rotation**: Regular rotation of encryption keys

### 2. Message Signing

Digital signatures for message integrity and authenticity:

```yaml
message_security:
  signing:
    enabled: true
    algorithm: "Ed25519"
    include_timestamp: true
    hash_algorithm: "SHA-256"
    signature_location: "header"
```

Features:
- **Digital Signatures**: Cryptographic proof of origin
- **Integrity Protection**: Detection of message tampering
- **Non-Repudiation**: Undeniable proof of sender
- **Timestamp Signing**: Protection against replay attacks
- **Selective Signing**: Ability to sign specific message parts

### 3. Message Format Security

Secure message format handling:

```yaml
message_security:
  format:
    validation:
      enabled: true
      schema_validation: true
      content_types: ["application/json", "application/cbor"]
    sanitization:
      enabled: true
      html_sanitization: true
      json_sanitization: true
```

Features:
- **Schema Validation**: Validation against message schemas
- **Content Validation**: Validation of message content
- **Content Type Enforcement**: Strict content type checking
- **Input Sanitization**: Protection against injection attacks
- **Format Verification**: Verification of message format

## Protocol-Specific Message Security

### MCP Message Security

Message security for Model Context Protocol:

```yaml
message_security:
  protocol_specific:
    mcp:
      function_message_signing: true
      function_parameter_validation: true
      response_verification: true
      streaming_message_security:
        chunk_signing: true
        sequence_validation: true
```

Key features:
- **Function Call Security**: Secure function invocations
- **Parameter Validation**: Validation of function parameters
- **Response Verification**: Verification of function responses
- **Streaming Security**: Security for streaming messages
- **Sequence Validation**: Validation of message sequences

### A2A Message Security

Message security for Agent-to-Agent Protocol:

```yaml
message_security:
  protocol_specific:
    a2a:
      agent_card_verification: true
      content_verification: true
      capability_validation: true
      conversation_security:
        thread_validation: true
        contextual_validation: true
```

Key features:
- **Agent Card Security**: Verification of agent identity cards
- **Content Verification**: Verification of message content
- **Capability Validation**: Validation of agent capabilities
- **Conversation Security**: Security for multi-message conversations
- **Contextual Validation**: Validation against conversation context

### HTTP Message Security

Message security for HTTP-based communication:

```yaml
message_security:
  protocol_specific:
    http:
      request_signing: true
      payload_encryption: true
      header_security:
        signature_header: "X-Signature"
        signature_algorithm: "hmac-sha256"
      response_verification:
        verify_signature: true
        verify_content_type: true
```

Key features:
- **Request Signing**: Digital signatures for HTTP requests
- **Payload Encryption**: End-to-end encryption of payloads
- **Header Security**: Security for HTTP headers
- **Response Verification**: Verification of HTTP responses
- **Content Type Enforcement**: Strict content type checking

### MQTT Message Security

Message security for MQTT-based communication:

```yaml
message_security:
  protocol_specific:
    mqtt:
      payload_encryption: true
      payload_signing: true
      topic_validation: true
      qos_validation: true
      retain_flag_security:
        allow_retained: false
        sign_retained: true
```

Key features:
- **Payload Security**: End-to-end security for MQTT payloads
- **Topic Validation**: Validation of MQTT topics
- **QoS Validation**: Validation of Quality of Service
- **Retain Flag Security**: Security for retained messages
- **Last Will Security**: Security for Last Will and Testament

### gRPC Message Security

Message security for gRPC-based communication:

```yaml
message_security:
  protocol_specific:
    grpc:
      message_encryption: true
      message_signing: true
      metadata_security:
        secure_metadata_keys: ["authorization", "x-signature"]
        metadata_validation: true
      stream_security:
        chunk_signing: true
        sequence_validation: true
```

Key features:
- **Message Security**: End-to-end security for gRPC messages
- **Metadata Security**: Security for gRPC metadata
- **Stream Security**: Security for streaming RPCs
- **Message Validation**: Validation of gRPC messages
- **Protocol Buffer Security**: Security for Protocol Buffers

## Secure Messaging Patterns

OpenMAS implements secure versions of common messaging patterns:

### Request-Response Security

```yaml
message_security:
  messaging_patterns:
    request_response:
      request_id_validation: true
      response_correlation: true
      timeout_handling: true
      idempotency_keys: true
```

Features:
- **Request ID**: Secure request identification
- **Response Correlation**: Secure correlation of responses to requests
- **Timeout Handling**: Secure handling of timeouts
- **Idempotency**: Protection against duplicate processing

### Publish-Subscribe Security

```yaml
message_security:
  messaging_patterns:
    pub_sub:
      topic_security: true
      publisher_authentication: true
      subscriber_authentication: true
      content_validation: true
```

Features:
- **Topic Security**: Secure topic management
- **Publisher Authentication**: Verify publisher identity
- **Subscriber Authentication**: Verify subscriber identity
- **Content Validation**: Validation of published content

### Event-Driven Security

```yaml
message_security:
  messaging_patterns:
    event_driven:
      event_validation: true
      source_verification: true
      causal_chain_validation: true
      event_correlation: true
```

Features:
- **Event Validation**: Validation of event structure
- **Source Verification**: Verification of event source
- **Causal Chain**: Validation of event causality
- **Event Correlation**: Secure correlation of related events

## Integration with Reasoning

Message security integrates with OpenMAS's reasoning-agnostic architecture:

```
┌─────────────────────────────────┐
│          Communication Layer    │
│          ("Body")               │
│                                 │
│  ┌───────────────────────────┐  │
│  │  Message Security         │  │
│  └─────────────┬─────────────┘  │
│                │                │
└────────────────┼────────────────┘
                 │
┌────────────────┼────────────────┐
│                │                │
│  ┌─────────────▼─────────────┐  │
│  │  Reasoning Message        │  │
│  │  Interface               │  │
│  └───────────────────────────┘  │
│                                 │
│          Reasoning Layer        │
│          ("Brain")              │
└─────────────────────────────────┘
```

Each reasoning approach interfaces with message security through a standard interface, maintaining the separation between communication and reasoning while ensuring that all messages are secure regardless of the reasoning approach used.

## Message Security Examples

### JSON Message Signing

```json
{
  "header": {
    "messageId": "msg123",
    "sender": "agent1",
    "timestamp": "2023-04-12T15:30:45Z",
    "signature": {
      "algorithm": "Ed25519",
      "value": "base64-encoded-signature",
      "signedFields": ["messageId", "sender", "timestamp", "body"]
    }
  },
  "body": {
    "content": "Hello, world!",
    "type": "greeting"
  }
}
```

### Encrypted Message Format

```json
{
  "header": {
    "messageId": "msg123",
    "sender": "agent1",
    "recipient": "agent2",
    "timestamp": "2023-04-12T15:30:45Z",
    "encryption": {
      "algorithm": "AES-256-GCM",
      "keyId": "key123",
      "iv": "base64-encoded-iv",
      "tag": "base64-encoded-tag"
    }
  },
  "encryptedBody": "base64-encoded-encrypted-content"
}
```

### Message with Secure Capabilities

```json
{
  "header": {
    "messageId": "msg123",
    "sender": "agent1",
    "recipient": "agent2",
    "timestamp": "2023-04-12T15:30:45Z",
    "capabilities": {
      "required": ["conversation"],
      "optional": ["function_execution"],
      "signature": "base64-encoded-signature"
    }
  },
  "body": {
    "content": "Hello, world!",
    "type": "greeting"
  }
}
```

## Key Exchange and Management

Secure key exchange for message encryption:

```yaml
message_security:
  key_management:
    key_exchange:
      protocol: "ECDHE-P256"
      dh_parameters: "rfc7919-ffdhe2048"
    key_storage:
      storage_type: "secure_memory"
      key_cache_ttl: 3600  # seconds
    key_rotation:
      automatic: true
      interval_messages: 1000
      interval_time: 3600  # seconds
```

Features:
- **Diffie-Hellman**: Secure key exchange
- **Forward Secrecy**: Protection of past messages
- **Key Rotation**: Regular rotation of encryption keys
- **Secure Storage**: Secure storage of encryption keys
- **Key Lifecycle**: Complete key lifecycle management

## Secure Content Validation

Validation of message content:

```yaml
message_security:
  content_validation:
    schema_validation:
      enabled: true
      schema_repository: "/path/to/schemas"
      strict_validation: true
    content_types:
      allowed: ["application/json", "application/cbor"]
      default: "application/json"
    sanitization:
      html: true
      json: true
      xml: true
```

Features:
- **Schema Validation**: Validation against message schemas
- **Content Type Validation**: Validation of content types
- **Input Sanitization**: Protection against injection attacks
- **Format Verification**: Verification of message format
- **Structure Validation**: Validation of message structure

## Secure Message Protocols

Implementation of secure message protocols:

```yaml
message_security:
  secure_protocols:
    noise:
      enabled: true
      pattern: "Noise_XX_25519_AESGCM_SHA256"
      psk_mode: false
    signal:
      enabled: false
      ratcheting: true
    custom:
      enabled: false
      protocol: "custom_protocol"
```

Features:
- **Noise Protocol**: Implementation of Noise Protocol Framework
- **Signal Protocol**: Double Ratchet Algorithm
- **Custom Protocols**: Support for custom secure protocols
- **Protocol Negotiation**: Secure protocol negotiation
- **Protocol Compatibility**: Interoperability between protocols

## Best Practices

1. **End-to-End Encryption**: Implement end-to-end message encryption
2. **Message Signing**: Sign messages to ensure authenticity
3. **Content Validation**: Validate message content against schemas
4. **Format Security**: Secure handling of message formats
5. **Key Management**: Implement secure key management
6. **Forward Secrecy**: Ensure forward secrecy for message keys
7. **Replay Protection**: Implement protection against replay attacks
8. **Protocol-Specific Security**: Apply appropriate security for each protocol
9. **Message Isolation**: Maintain isolation between message contexts
10. **Defense in Depth**: Layer security controls for message protection

## Related Documentation

- [Security Principles](../architecture/security_principles.md)
- [Authentication](../authentication/README.md)
- [Authorization](../authorization/README.md)
- [Transport Security](./transport_security.md)
- [Configuration Schema](../../03_configuration/schema/security.md)
