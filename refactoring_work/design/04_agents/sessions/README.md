# OpenMAS Session Management

## Overview

The OpenMAS Session Management system provides persistent conversation handling, state management, and context preservation across all protocols while maintaining OpenMAS's core architectural principles of reasoning agnosticism and protocol independence.

## Key Capabilities

The Session Management system offers these core capabilities:

1. **Context Preservation** - Maintaining conversation history and context across interactions
2. **State Persistence** - Storage and retrieval of agent state using various backends
3. **History Management** - Tracking and querying interaction history with intelligent pruning
4. **Protocol Integration** - Consistent session handling across all protocols (A2A, MCP, etc.)
5. **Multi-Agent Sessions** - Managing sessions across multiple collaborating agents
6. **Recovery Mechanisms** - Resuming sessions after interruptions or failures
7. **Reasoning Agnosticism** - Session management independent of reasoning approaches

## Documentation Structure

This directory contains comprehensive documentation on the OpenMAS Session Management system:

| Document | Description |
|----------|-------------|
| [Session Management Design](./design_session_management.md) | Comprehensive architecture and design principles |
| [Session Storage](./session_storage.md) | Storage backends and persistence mechanisms |
| [Context Management](./context_management.md) | Context window management and pruning strategies |
| [Multi-Agent Sessions](./multi_agent_sessions.md) | Session management across multiple agents |

### Protocol Integration

Protocol-specific session handling documentation:

| Document | Description |
|----------|-------------|
| [A2A Task Integration](./protocol_integration/a2a_tasks.md) | Integration with A2A task protocol |
| [MCP Session Integration](./protocol_integration/mcp_sessions.md) | Integration with MCP session handling |

### Examples

Example configurations and usage patterns:

| Document | Description |
|----------|-------------|
| [Basic Session Examples](./examples/basic_session.md) | Basic session configuration examples |
| [Advanced Session Examples](./examples/advanced_session.md) | Advanced session usage patterns |

## Integration with Other Components

The Session Management system integrates with several other OpenMAS components:

1. **Agent Framework** - Provides session management for individual agents
2. **Protocol Layer** - Ensures consistent session handling across protocols
3. **Configuration System** - Defines session configuration via unified schema
4. **Asset Management** - Handles session-related assets and attachments
5. **Security System** - Manages authentication and authorization for sessions

## Configuration

Session management is configured through the unified configuration schema:

```yaml
# Session management configuration
sessions:
  enabled: true
  storage:
    type: "memory"  # memory, file, database, redis
    # Storage-specific configuration
  context:
    max_history_items: 50
    max_tokens: 4000
    pruning_strategy: "selective"
  protocol_sessions:
    a2a:
      enabled: true
      # A2A-specific configuration
    mcp:
      enabled: true
      # MCP-specific configuration
```

For detailed configuration options, see the [Session Management Design](./design_session_management.md) document and the [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md).
