# OpenMAS Agent Framework

## Overview

The OpenMAS Agent Framework is a core component that encapsulates agent creation, capabilities, interactions, and topologies. It provides a standardized, configuration-driven approach to defining and managing intelligent agents, supporting a wide range of agent types, reasoning approaches, and communication protocols.

## Key Features

1. **Standardized Agent Definition**: Consistent approach to defining and configuring agents
2. **Capability Management**: Comprehensive capability registration, discovery, and invocation mechanism
3. **Topology Support**: Built-in support for common agent organization patterns
4. **Protocol Agnosticism**: Seamless integration with multiple communication protocols
5. **Reasoning Agnosticism**: Support for different reasoning approaches (rule-based, LLM, etc.)
6. **State Management**: Efficient handling of agent state and session data
7. **Lifecycle Management**: Standardized agent lifecycle management

## Core Components

The agent framework consists of these fundamental components:

### 1. Agent Core

The base agent implementation that provides:
- Lifecycle management (initialization, execution, termination)
- Capability registration and discovery
- State management
- Protocol integration via standardized message handling
- Configuration handling

### 2. Capability System

Defines how agent capabilities are specified, discovered, and managed:
- Schema-based capability definitions using Pydantic models
- Input/output validation through schema enforcement
- Version management for capability evolution
- Capability discovery and advertisement across protocols
- Cross-protocol capability mapping
- Programmatic capability registration via ICapabilityManager

The Capability System implements the `ICapabilityManager` interface, which provides methods for:
- Registering capability handler functions with their input/output schemas
- Unregistering capabilities when they're no longer needed
- Listing available capabilities for discovery purposes
- Retrieving detailed capability information
- Invoking capabilities with validated input data
- Loading capability definitions from configuration

Capability handler functions follow a standardized signature and receive an `AgentContext` object that provides access to agent resources. For detailed information on the capability registration API, see [Agent Capabilities Documentation](/refactoring_work/00b_overview/04_agents/agent_capabilities.md#capability-registration-api).

### 3. Topology System

Supports various agent organization patterns:
- Orchestrator-Worker pattern
- Mesh networks
- Service registry-based discovery
- Hierarchical organizations
- Custom topology patterns

### 4. Session Management

Handles agent interactions and conversational state:
- Session creation and tracking
- Conversation history management
- Context persistence
- Memory management

### 5. Agent Types

Specialized agent implementations for different use cases:
- Autonomous agents
- Assistive agents
- Tool/service agents
- Multi-agent systems
- Hybrid agents

## Integration with Other Components

The agent framework integrates with:

1. **Protocol System**: For agent communication across different protocols (HTTP, MCP, A2A, etc.)
2. **Configuration System**: For agent configuration and validation
3. **Asset Management**: For handling agent-required assets
4. **Knowledge Representation**: For managing agent knowledge and reasoning
5. **Prompt Management**: For LLM-based agent prompting
6. **Observability System**: For monitoring, logging, and tracing

## Agent Configuration

Agent configuration follows the unified configuration schema. A typical agent configuration includes:

```yaml
agents:
  agent_name:
    # Core agent configuration
    module: "openmas.agents"
    class: "AssistiveAgent"
    description: "An agent that provides assistance with data analysis"
    
    # Capability configuration
    capabilities:
      analyze_data:
        description: "Analyzes datasets and provides insights"
        versions: ["1.0", "1.1"]
        input_schema: {}
        output_schema: {}
      
    # Protocol configuration  
    protocols:
      - type: "a2a-http"
        enabled: true
        options: {}
      - type: "mcp-sse"
        enabled: true
        options: {}
    
    # State configuration
    state:
      storage: "memory"
      persistence: false
      
    # Session configuration
    sessions:
      timeout: 3600
      max_history: 100
```

## Reasoning Agnosticism

The agent framework maintains OpenMAS's reasoning agnosticism principle by:

1. **Clean Separation**: Agent communication layer is separate from reasoning layer
2. **Adapter Pattern**: Reasoning modules use a common interface
3. **Capability Abstraction**: Capabilities are defined independently of their implementation
4. **Protocol Independence**: Communication protocols are agnostic to reasoning approach

## Message Handling

The Agent Framework's message handling system is a critical component that ensures protocol-agnostic processing of messages across different communication protocols. It provides:

### IMessageHandler Interface

A standardized interface that defines how messages are processed within the Agent Framework:

- **Protocol-agnostic processing**: Converts between protocol-specific formats and the standardized internal message format
- **Message routing**: Directs messages to appropriate agent components based on message type and content
- **Bi-directional translation**: Handles both incoming and outgoing message conversion
- **Error handling**: Provides standardized error reporting and recovery mechanisms

### Standard Internal Message Format

A unified message representation used throughout the Agent Framework:

- **Common representation**: Enables communication between components using different protocols
- **Extensible payload system**: Supports various message content types (text, structured data, invocations, etc.)
- **Metadata handling**: Preserves contextual information across protocol boundaries

### Message Processing Flow

1. **Inbound**: Protocol adapters receive messages and pass them to the message handler for conversion to internal format
2. **Routing**: Messages are routed to appropriate agent capabilities or reasoning components
3. **Processing**: Agent components process messages according to their specific logic
4. **Outbound**: Responses are converted back to protocol-specific formats for transmission

This approach maintains the critical separation between communication mechanisms and reasoning approaches, supporting OpenMAS's reasoning agnostic design.

For detailed information on the message handling system, see:
- [IMessageHandler Interface](/refactoring_work/00b_overview/04_agents/interfaces/message_handler_interface.md)
- [Internal Message Format](/refactoring_work/00b_overview/01_architecture/models/internal_message_format.md)
- [Message Processing Models](/refactoring_work/00b_overview/04_agents/models/message_processing.md)

## Additional Resources

- [Agent Capabilities Documentation](/refactoring_work/00b_overview/04_agents/agent_capabilities.md)
- [Agent Topologies Documentation](/refactoring_work/00b_overview/04_agents/agent_topologies.md)
- [Agent Lifecycle Management](/refactoring_work/00b_overview/04_agents/lifecycle/lifecycle_management.md)
- [Session Management](/refactoring_work/00b_overview/04_agents/session_management.md)
- [Agent Design Principles](/refactoring_work/00b_overview/04_agents/design_principles.md)
- [Protocol Integration](/refactoring_work/00b_overview/04_agents/integration.md)
