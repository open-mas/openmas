# OpenMAS Protocols

## Overview

This directory contains documentation for the communication protocols supported by OpenMAS. It details the protocol specifications, implementations, and adaptations that enable agents to communicate effectively while maintaining OpenMAS's core principles of reasoning agnosticism and protocol independence.

## Key Capabilities

OpenMAS protocols provide these core capabilities:

1. **Protocol Agnosticism** - Support for multiple communication protocols while maintaining a clean separation between communication ("body") and reasoning ("brain")
2. **Standard Internal Message Format** - All protocol messages are translated to/from the Internal Message Format (SIMF), which serves as the core intermediary for protocol-independent agent communication
3. **Standardized Interfaces** - Consistent interfaces regardless of protocol, with all protocols implementing the [IProtocolAdapter interface](./iprotocol_adapter_interface.md) and unified configuration through the [schema definition](/03_configuration/schema/protocols.md)
4. **Security Features** - Enterprise-grade security across all protocols, including authentication, authorization, and encryption
5. **Extensibility** - Built-in support for extending and customizing protocol implementations
6. **Discovery Mechanisms** - Protocol-specific agent discovery and capability advertisement
7. **Streaming Support** - First-class support for streaming data across all supported protocols
8. **Reliable Communication** - Error handling, reconnection, and state management across protocols

## Protocol Implementation

All OpenMAS protocols implement the [IProtocolAdapter Interface](./iprotocol_adapter_interface.md), which provides:

- **Consistent API**: Standardized methods for connection management, message sending/receiving, and status monitoring
- **SIMF Integration**: Required translation methods between protocol-specific formats and Standard Internal Message Format
- **Configuration Support**: Integration with the unified configuration schema through Pydantic models
- **Error Handling**: Comprehensive error types and handling for robust protocol operations
- **Capability Declaration**: Methods for declaring and querying protocol-specific capabilities

> **Note on Protocol Interoperability**: OpenMAS supports multiple protocols simultaneously, but meaningful communication between semantically different protocols (particularly A2A and MCP) requires translation through the Internal Message Format Standard (SIMF) via dedicated protocol adapters. OpenMAS does **not** implement direct message passthrough between protocols. Protocol adapters are responsible for bi-directional translation between their native protocol format and the SIMF, which preserves the semantic intent while accounting for protocol differences.

## Communication Patterns

Protocols implement various communication patterns that define how agents exchange information. Each protocol supports different patterns based on its design and capabilities.

### Protocol-Pattern Mapping

For a complete mapping between protocols and communication patterns, see:

- [Protocol to Pattern Mapping](/07_communication_patterns/protocol_pattern_mapping.md) - Definitive mapping between protocols and patterns

### Communication Pattern Documentation

For detailed pattern documentation, see:

- [Communication Patterns Overview](/07_communication_patterns/README.md) - Core concepts and structure
- [Pattern Specifications](/07_communication_patterns/patterns/) - Individual pattern documentation
- [Protocol Adaptations](/07_communication_patterns/adaptations/) - How patterns adapt to protocols

## Supported Protocols

OpenMAS supports several communication protocols, all of which are defined in the [unified configuration schema](/03_configuration/unified_configuration_schema.md) with detailed documentation in [protocol schema](/03_configuration/schema/protocols.md):

### 1. Agent-to-Agent Protocol (A2A)

The [A2A protocol](./a2a/a2a_protocol.md) enables communication between agents:

- Agent discovery and interaction through agent cards
- Capability definition and sharing
- Asynchronous messaging
- Structured data exchange

For configuration details, see the [A2A Protocol Configuration Schema](/03_configuration/schema/protocols.md#a2a-protocol-configuration).

### 2. Model Context Protocol (MCP)

The [Model Context Protocol](./mcp/mcp_protocol.md) focuses on standardizing how AI models and agents connect to external resources:

- Tool definitions and invocation
- Resource access (files, URLs, etc.)
- Streaming capabilities
- Runtime state management

For configuration details, see the [MCP Protocol Configuration Schema](/03_configuration/schema/protocols.md#mcp-protocol-configuration).

### 3. HTTP Protocol

The [HTTP protocol](./http/http_protocol.md) provides standard web communication:

- RESTful API support
- Standard HTTP methods and status codes
- Content negotiation
- Server-Sent Events (SSE) for streaming
- WebHooks for event-based communication

For configuration details, see the [HTTP Protocol Configuration Schema](/03_configuration/schema/protocols.md#http-protocol-configuration).

### 4. MQTT Protocol

The [MQTT protocol](./mqtt/mqtt_protocol.md) enables lightweight publish-subscribe messaging:

- Topic-based message routing
- Quality of Service levels
- Retained messages and Last Will and Testament
- Message queuing for offline clients
- Efficient binary format for constrained devices

For configuration details, see the [MQTT Protocol Configuration Schema](/03_configuration/schema/protocols.md#mqtt-protocol-configuration).

### 5. gRPC Protocol

The [gRPC protocol](./grpc/grpc_protocol.md) provides high-performance RPC capabilities:

- Protocol Buffer-based service definitions
- Binary serialization for efficient data exchange
- Multiple RPC types (unary, server streaming, client streaming, bidirectional)
- HTTP/2-based transport for multiplexing
- Strong typing and code generation

For configuration details, see the [gRPC Protocol Configuration Schema](/03_configuration/schema/protocols.md#grpc-protocol-configuration).

## Documentation Structure

This directory contains comprehensive documentation on OpenMAS protocols:

| Document | Description |
|----------|-------------|
| [Protocol Overview](./openmas_protocols.md) | Overview of protocol support in OpenMAS |
| [Protocol Documentation Standard](./protocol_documentation.md) | Detailed protocol specifications |
| [Multi-Protocol Support](./multi_protocol_support.md) | How OpenMAS supports multiple protocols |
| [A2A Protocol](./a2a/README.md) | A2A protocol implementation details |
| [MCP Protocol](./mcp/README.md) | MCP protocol implementation details |
| [HTTP Protocol](./http/README.md) | HTTP protocol implementation details |
| [MQTT Protocol](./mqtt/README.md) | MQTT protocol implementation details |
| [gRPC Protocol](./grpc/README.md) | gRPC protocol implementation details |

## Protocol Configuration

Protocol configuration follows the unified configuration schema. For the complete and authoritative schema definition, see:

- [Protocol Configuration Schema](/03_configuration/schema/protocols.md) - Definitive schema for all protocols
- [Configuration Guide](./protocol_configuration_guide.md) - Guide to configuring protocols
- [Protocol Integration](./protocol_integration_guide.md) - How to integrate protocols

## Integration with Other Components

Protocols integrate with several other OpenMAS components:

1. **Agent Framework** - Protocol-specific agent communication interfaces
2. **Communication Patterns** - Pattern implementations for each protocol
3. **Topology System** - Protocol support for different agent organizations
4. **Security System** - Protocol-specific security features
5. **Observability System** - Protocol-specific monitoring and logging

## Reasoning Agnosticism

OpenMAS protocols maintain the framework's reasoning agnosticism by:

1. **Clean Separation** - Protocol implementations are separate from reasoning implementations
2. **Consistent Interfaces** - Standard interfaces regardless of reasoning approach
3. **Transport Independence** - Reasoning is independent of transport mechanisms
4. **Data Format Neutrality** - Protocol adaptations handle format conversions

This enables agents using different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to communicate effectively using the same protocols.
