# Multi-Protocol Agent Design

## Overview

One of OpenMAS's distinctive features is its ability to support multiple communication protocols simultaneously within a single agent instance, without requiring protocol bridging. This document explains the multi-protocol architecture, which enables agents to communicate across different protocols while maintaining a consistent internal representation and reasoning process.

## Multi-Protocol Architecture

The following diagram illustrates how a single OpenMAS agent can support multiple protocols concurrently, with the Standard Internal Message Format (SIMF) serving as the central hub for all communication. SIMF's comprehensive payload types ensure semantic fidelity across different protocols and reasoning approaches:

```mermaid
componentDiagram
    component "OpenMAS Agent" as Agent {
        component "Agent Core" as Core {
            component "Agent Framework" as Framework
            component "ReasoningEngine" as Reasoning
            component "KR&R System" as KRR
        }

        component "Protocol Interfaces" as Protocols {
            component "A2A Protocol Interface" as A2A
            component "MCP Protocol Interface" as MCP
            component "HTTP Protocol Interface" as HTTP
            component "MQTT Protocol Interface" as MQTT
            component "gRPC Protocol Interface" as GRPC
        }

        Reasoning --> KRR : uses
    }

    component "A2A Client" as A2AClient
    component "MCP Client" as MCPClient
    component "HTTP Client" as HTTPClient
    component "MQTT Broker" as MQTTBroker
    component "gRPC Client" as GRPCClient

    A2AClient --> A2A : A2A Protocol
    MCPClient --> MCP : MCP Protocol
    HTTPClient --> HTTP : HTTP Protocol
    MQTTBroker --> MQTT : MQTT Protocol
    GRPCClient --> GRPC : gRPC Protocol

    A2A --> Framework : SIMF
    MCP --> Framework : SIMF
    HTTP --> Framework : SIMF
    MQTT --> Framework : SIMF
    GRPC --> Framework : SIMF

    Framework --> Reasoning : SIMF
    Reasoning --> Framework : SIMF

    Framework --> A2A : SIMF
    Framework --> MCP : SIMF
    Framework --> HTTP : SIMF
    Framework --> MQTT : SIMF
    Framework --> GRPC : SIMF
```

This diagram demonstrates the key aspects of the multi-protocol design:

1. **Unified Agent Core**: The agent's central components (Framework, ReasoningEngine, KR&R System) operate independently of any specific protocol

2. **Multiple Protocol Interfaces**: A single agent can have multiple protocol interfaces active simultaneously

3. **Standard Internal Message Format (SIMF)**: All protocol interfaces convert their protocol-specific messages to and from SIMF, providing a consistent representation for the Agent Framework and ReasoningEngine. SIMF's diverse payload types capture the full semantic range needed across protocols.

4. **Protocol Independence**: The reasoning engine interacts only with SIMF messages, completely isolated from protocol-specific details

5. **Bidirectional Flow**: Each protocol interface handles both inbound messages (external → SIMF) and outbound messages (SIMF → external)

## SIMF Payload Types for Cross-Protocol Communication

The Standard Internal Message Format provides a rich set of payload types designed to capture the semantics of all supported protocols:

1. **Core Payload Types**:
   - `text_content`: Simple text messages across all protocols
   - `structured_data_content`: JSON/structured data in any protocol
   - `asset_reference_content`: References to binary assets with enhanced metadata for protocol-specific resource handling
   - `multi_part_content`: Compound messages with multiple parts (directly maps to A2A multi-part messages)

2. **Invocation-Related Types**:
   - `invocation_content`: Capability/tool invocations (maps to A2A capability calls, MCP tool calls, HTTP requests, gRPC method calls)
   - `invocation_result_content`: Results of capability/tool invocations

3. **Specialized Types**:
   - `stream_context_content`: Preserves streaming semantics across different protocols (critical for gRPC streams, SSE, MQTT streams)
   - `knowledge_representation_content`: Formal knowledge structures for symbolic and hybrid reasoning approaches
   - `event_content`: Standardized event notifications (maps to MQTT events, A2A notifications, HTTP webhooks)

These payload types ensure that no semantic information is lost during protocol translation, enabling true cross-protocol interoperability. For complete details on each payload type and protocol-specific mappings, see [Standard Internal Message Format](./internal_message_format_standard.md).

## Protocol Interface Components

Each protocol interface consists of these key components:

1. **Protocol Adapter**: Implements the [IProtocolAdapter interface](../02_protocols/iprotocol_adapter_interface.md) to convert between protocol-specific message formats and SIMF
   - `to_internal_format()`: Converts from protocol format to SIMF, selecting the appropriate payload type based on message content
   - `from_internal_format()`: Converts from SIMF to protocol format, translating payload types to protocol-specific structures
   - `connect()`, `disconnect()`: Manages protocol connection lifecycle
   - `send_message()`, `register_message_callback()`: Handles message transmission and reception
   - `get_status()`, `get_capabilities()`: Provides protocol status and capability information

2. **Protocol-Specific Handler**: Manages protocol-specific communication details
   - Connection management
   - Authentication
   - Protocol-specific metadata

3. **Capability Mapper**: Maps agent capabilities to protocol-specific representations
   - Exposes appropriate capabilities based on protocol constraints
   - Translates capability invocations between protocols

## Unified Configuration

Agents are configured to support multiple protocols through the unified configuration schema:

```yaml
agents:
  multi_protocol_agent:
    # Agent's primary reasoning engine
    reasoning:
      approach: "llm_engine"
      # reasoning-specific config...

    # Multiple protocol configurations
    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8080"
          # A2A-specific options...

      - type: "mcp-sse"
        enabled: true
        options:
          # MCP-specific options...

      - type: "http-rest"
        enabled: true
        options:
          port: 8000
          # HTTP-specific options...
```

## Benefits of Multi-Protocol Support

1. **Protocol Flexibility**: Agents can communicate through the most appropriate protocol for each use case

2. **Ecosystem Integration**: Agents can integrate with diverse systems using their native protocols

3. **Future-Proofing**: New protocols can be added without changing the core agent architecture

4. **Simplified Development**: Developers can use a single agent codebase for multiple protocol integrations

5. **Consistent Reasoning**: The agent's reasoning logic remains consistent regardless of the communication protocol

## Cross-Protocol Communication Examples

The enhanced SIMF payload types enable seamless communication across different protocols. For example:

1. **A2A to MCP Translation**:
   - An A2A multi-part message with text and image parts can be translated to SIMF `multi_part_content`
   - The SIMF message can then be translated to an MCP message with text content and image resources
   - Protocol-specific metadata is preserved in the appropriate SIMF structures

2. **MQTT to HTTP Translation**:
   - An MQTT retained message can be translated to SIMF `event_content` with `is_transient: false`
   - This can be converted to an HTTP POST to a webhook endpoint with appropriate headers

3. **gRPC to SSE Translation**:
   - A gRPC bidirectional stream can be represented as a sequence of SIMF messages with `stream_context_content`
   - These can be translated to Server-Sent Events (SSE) for browser clients

These translations maintain semantic fidelity through the rich SIMF payload types.

## Implementation Considerations

1. **Thread Safety**: Protocol interfaces may run in parallel, requiring thread-safe access to shared components

2. **Message Correlation**: When an agent communicates with the same counterpart over multiple protocols, correlation IDs help track related conversations

3. **Protocol Prioritization**: Configuration options determine which protocol to prefer when multiple options are available

4. **Capability Exposure**: Not all capabilities may be appropriate for all protocols; selective exposure ensures appropriate functionality

5. **Security Context**: Security credentials and context must be properly mapped across protocols

## References

- [Standard Internal Message Format](./internal_message_format_standard.md)
- [Reasoning Agnostic Design](./reasoning_agnostic_design.md)
- [Protocol Adapters](/refactoring_work/00b_overview/05_extensions/protocol_adapters/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Protocol-to-Pattern Mapping](/refactoring_work/00b_overview/02_protocols/protocol_to_pattern_mapping.md)
