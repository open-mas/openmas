# Multi-Protocol Agent Design

## Overview

One of OpenMAS's distinctive features is its ability to support multiple communication protocols simultaneously within a single agent instance, without requiring protocol bridging. This document explains the multi-protocol architecture, which enables agents to communicate across different protocols while maintaining a consistent internal representation and reasoning process.

## Multi-Protocol Architecture

The following diagram illustrates how a single OpenMAS agent can support multiple protocols concurrently, with the Standard Internal Message Format (SIMF) serving as the central hub for all communication. SIMF's comprehensive payload types ensure semantic fidelity across different protocols and reasoning approaches:

```mermaid
componentDiagram
    component "OpenMAS Agent" as Agent {
        component "Agent Core" as Core {
            component "IMessageHandler" as Handler
            component "Agent Framework" as Framework
            component "ReasoningEngine" as Reasoning
            component "KR&R System" as KRR
        }

        component "Protocol Adapters" as Adapters {
            component "A2A Protocol Adapter" as A2A
            component "MCP Protocol Adapter" as MCP
            component "HTTP Protocol Adapter" as HTTP
            component "MQTT Protocol Adapter" as MQTT
            component "gRPC Protocol Adapter" as GRPC
        }

        Reasoning --> KRR : uses
        Handler --> Framework : SIMF
        Framework --> Reasoning : SIMF
        Reasoning --> Framework : SIMF
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

    A2A --> Handler : SIMF
    MCP --> Handler : SIMF
    HTTP --> Handler : SIMF
    MQTT --> Handler : SIMF
    GRPC --> Handler : SIMF

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

## Core Communication Components

OpenMAS's protocol layer is built on a clear separation of concerns, with two primary interfaces ensuring modularity and flexibility:

1.  **Protocol Adapter (`IProtocolAdapter`)**: This component is a pure translator and connection manager. Its sole responsibilities are:
    - **Connection Lifecycle**: Managing the connection to the external endpoint (`connect()`, `disconnect()`, `get_status()`).
    - **Message Translation**: Converting messages between the protocol-specific format and the Standard Internal Message Format (SIMF) (`to_internal_format()`, `from_internal_format()`).
    - It does **not** handle message dispatching or contain any business logic. See the full [IProtocolAdapter interface definition](../02_protocols/iprotocol_adapter_interface.md).

2.  **Message Handler (`IMessageHandler`)**: This component acts as the entry point for all inbound communications into the agent's core logic. Its responsibilities are:
    - **Receiving Inbound Messages**: It receives messages in the SIMF format from one or more protocol adapters.
    - **Processing and Dispatching**: It contains the logic to process the inbound message and route it to the appropriate component within the Agent Framework.
    - This clean handoff ensures that the agent's core is completely decoupled from the transport protocol. See the full [IMessageHandler interface definition](../02_protocols/common/imessage_handler_interface.md).

3.  **Agent Framework**: For outbound messages, the Agent Framework constructs a SIMF message and passes it directly to the appropriate `IProtocolAdapter`'s `from_internal_format()` method for translation and transmission.

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
- [IProtocolAdapter Interface](../02_protocols/iprotocol_adapter_interface.md)
- [IMessageHandler Interface](../02_protocols/common/imessage_handler_interface.md)
- [Configuration Schema](../03_configuration/unified_configuration_schema.md)
- [Protocol-to-Pattern Mapping](../02_protocols/protocol_to_pattern_mapping.md)
