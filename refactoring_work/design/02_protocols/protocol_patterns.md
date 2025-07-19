# Protocol-Specific Communication Patterns

## Overview

This document provides an overview of how OpenMAS protocols implement communication patterns. For detailed documentation on protocol-specific implementations of communication patterns, please refer to the dedicated documentation in the [Communication Patterns](/07_communication_patterns/protocol_implementations/README.md) section.

## Protocol and Pattern Relationships

Each OpenMAS protocol implements the standard communication patterns with optimizations for that protocol's specific features and capabilities:

| Protocol | Key Pattern Implementations | Documentation |
|----------|----------------------------|--------------|
| A2A      | Request-Response, Streaming, Publish-Subscribe | [A2A Protocol](/02_protocols/a2a/README.md) |
| MCP      | Tool Calls, Resource Access, Streaming | [MCP Protocol](/02_protocols/mcp/README.md) |
| HTTP     | RESTful APIs, Server-Sent Events, Webhooks | [HTTP Protocol](/02_protocols/http/README.md) |
| MQTT     | Native Pub/Sub, Topic Hierarchy, QoS Levels | [MQTT Protocol](/02_protocols/mqtt/README.md) |
| gRPC     | Unary/Streaming RPC, Strong Typing | [gRPC Protocol](/02_protocols/grpc/README.md) |

## Protocol Configuration for Patterns

For protocol-specific configuration of communication patterns, refer to the [Protocol Configuration Schema](/03_configuration/schema/protocols.md). Additional communication pattern configuration options may be found in the [Extension Configuration Schema](/03_configuration/schema/extensions.md).
