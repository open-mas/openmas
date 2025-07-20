# Agent Implementation Guide

This directory contains comprehensive implementation guides and examples for developing agents in OpenMAS 0.3.0, focusing on practical patterns that maintain reasoning agnosticism and protocol independence.

## Overview

The OpenMAS Agent Implementation system provides:
- **Implementation Patterns**: Proven patterns for different agent types
- **Code Examples**: Complete, working examples for various scenarios
- **Best Practices**: Guidelines for maintainable and scalable agent development
- **Integration Guides**: How to integrate with OpenMAS framework components
- **Testing Strategies**: Comprehensive testing approaches for agents

## Implementation Philosophy

OpenMAS agents follow key principles:

1. **Reasoning Agnosticism**: Agents can use any reasoning approach (rule-based, BDI, LLM, hybrid)
2. **Protocol Independence**: Agents work across all protocols without modification
3. **Capability-Driven**: Agents expose capabilities, not implementation details
4. **State Management**: Layered state handling across different scopes
5. **Session Awareness**: Proper session management and context handling

## 🔗 **Foundation: Building Effective Agents**

OpenMAS agent implementation builds on **[Anthropic's "Building Effective Agents"](https://www.anthropic.com/engineering/building-effective-agents)** best practices, extending them with:

- **Protocol Independence**: Work across A2A, MCP, HTTP, MQTT, gRPC without modification
- **Reasoning Agnosticism**: Support for rule-based, BDI, LLM, and hybrid reasoning approaches
- **Multi-Agent Coordination**: Built-in patterns for orchestrator-worker, peer-to-peer, and hierarchical topologies
- **State Management**: Layered state persistence across conversation, session, and permanent scopes
- **Configuration-Driven**: Unified configuration schema for all agent aspects

### **Anthropic Patterns in OpenMAS Context:**

| Anthropic Best Practice | OpenMAS Implementation |
|-------------------------|----------------------|
| **Planning and Reasoning** | Reasoning-agnostic design supports any approach |
| **Tool Use** | Protocol-agnostic tool invocation via SIMF |
| **Multimodal Capabilities** | Asset management system for multimedia content |
| **Long-running Conversations** | Session management with layered state persistence |
| **Agent Handoffs** | Multi-agent coordination patterns and capability discovery |
| **Human-in-the-loop** | Configurable interaction patterns and approval workflows |

## Documentation Structure

This directory contains:

| Document | Description |
|----------|-------------|
| [Implementation Guide](./guide.md) | Step-by-step agent implementation guide |
| [Agent Types](./agent_types.md) | Common agent implementation patterns |
| [Code Examples](./examples.md) | Complete code examples and templates |
| [Best Practices](./best_practices.md) | Guidelines for robust agent development |
| [Testing Guide](./testing.md) | Testing strategies and examples |
| [Integration Patterns](./integration_patterns.md) | Integration with framework components |

## Quick Start Implementation

### Basic Agent Implementation

```python
from openmas.agent import BaseAgent
from openmas.core.simf import SIMFMessage
from typing import Dict, Any

class MyAgent(BaseAgent):
    """Example agent implementation following OpenMAS patterns"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.setup_capabilities()

    def setup_capabilities(self):
        """Register agent capabilities"""
        self.register_capability("process_data", self.process_data)
        self.register_capability("analyze_text", self.analyze_text)

    async def process_message(self, message: SIMFMessage) -> SIMFMessage:
        """Main message processing logic"""

        # Get session context
        session_context = await self.get_session_context()

        # Process based on message type
        if message.message_type == "data_request":
            return await self.handle_data_request(message, session_context)
        elif message.message_type == "analysis_request":
            return await self.handle_analysis_request(message, session_context)
        else:
            return await super().process_message(message)

    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Example capability implementation"""
        # Your data processing logic here
        processed_data = {"result": f"Processed {len(data)} items"}

        # Update agent state
        await self.update_state("last_processed", processed_data)

        return processed_data

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Example text analysis capability"""
        # Your text analysis logic here
        analysis = {
            "length": len(text),
            "word_count": len(text.split()),
            "sentiment": "neutral"  # Placeholder
        }

        return analysis
```

## Agent Types and Patterns

OpenMAS provides proven agent patterns documented in [Agent Patterns](../agent_patterns.md) and [Agent Topologies](../agent_topologies.md). This implementation guide shows how to implement these patterns in practice.

### 1. **Established OpenMAS Patterns (0.2.0 → 0.3.0)**

#### **Orchestrator-Worker Pattern**
*Built into OpenMAS since 0.2.0, enhanced in 0.3.0*

- **Orchestrator Agent**: Central coordination with task delegation capabilities
- **Worker Agent**: Specialized task handling with capability registration
- **0.3.0 Enhancements**: Protocol independence, improved session management, topology integration

#### **Multi-Agent Coordination Patterns**
*New in 0.3.0, building on Anthropic's agent handoff patterns*

- **Peer-to-Peer Agents**: Collaborative agents with capability discovery
- **Hierarchical Agents**: Parent-child relationships with delegation
- **Hub-and-Spoke Agents**: Central hub with specialized spoke agents

### 2. **Protocol-Specific Agent Templates**

- **A2A Agent**: Agent optimized for Agent-to-Agent communication and capability discovery
- **MCP Agent**: Agent with MCP tool integration capabilities and resource management
- **HTTP Agent**: Agent for REST API interactions and web service integration
- **Multi-Protocol Agent**: Agent supporting multiple protocols simultaneously

### 3. **Reasoning Pattern Templates**
*Implementing Anthropic's reasoning best practices*

- **Rule-Based Agent**: Traditional rule-based reasoning with OpenMAS state management
- **LLM Agent**: Large Language Model integration following Anthropic guidelines
- **Hybrid Agent**: Combining multiple reasoning approaches with reasoning agnosticism
- **BDI Agent**: Belief-Desire-Intention framework integration

### 4. **Functional Pattern Templates**
*Based on established OpenMAS component patterns*

- **Data Processing Agent**: Specialized for data transformation using asset management
- **Coordination Agent**: Multi-agent orchestration using topology patterns
- **Interface Agent**: Human-computer interaction with session management
- **Service Agent**: External service integration using protocol adapters

## Configuration Integration

Agents integrate with the unified configuration schema:

```yaml
# Agent configuration example
agents:
  my_agent:
    class: "myproject.agents.MyAgent"
    enabled: true
    protocols: ["a2a", "mcp"]
    capabilities:
      - name: "process_data"
        description: "Process data objects"
      - name: "analyze_text"
        description: "Analyze text content"
    state_management:
      enabled: true
      layers: ["permanent", "session", "conversation"]
    sessions:
      enabled: true
      storage: "memory"
```

## Framework Integration

### State Management Integration

```python
# Layered state management
await self.set_permanent_state("user_preferences", preferences)
await self.set_session_state("conversation_count", count)
await self.set_conversation_state("current_topic", topic)
```

### Capability Registration

```python
# Dynamic capability registration
self.register_capability("custom_task", self.custom_task_handler)
self.register_capability("data_transform", self.transform_data)
```

### Protocol Handling

```python
# Protocol-agnostic message handling
async def process_message(self, message: SIMFMessage) -> SIMFMessage:
    # Message automatically converted to SIMF regardless of source protocol
    # Your logic here works across A2A, MCP, HTTP, MQTT, gRPC
    return response_message
```

## Testing Integration

### Unit Testing

```python
import pytest
from openmas.testing import AgentTestFramework

@pytest.mark.asyncio
async def test_agent_capability():
    # Create test agent
    agent = MyAgent(test_config)

    # Test capability
    result = await agent.process_data({"test": "data"})

    assert result["result"] == "Processed 1 items"
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_multi_protocol_agent():
    # Test agent across multiple protocols
    agent = MultiProtocolAgent(config)

    # Test A2A protocol
    a2a_response = await agent.process_a2a_message(a2a_message)

    # Test MCP protocol
    mcp_response = await agent.process_mcp_message(mcp_message)

    # Verify consistent behavior
    assert a2a_response.success == mcp_response.success
```

## Performance Considerations

### Optimization Patterns

1. **Async Operations**: Use async/await for all I/O operations
2. **State Caching**: Cache frequently accessed state data
3. **Capability Routing**: Route messages efficiently based on capabilities
4. **Resource Management**: Proper cleanup of resources and connections
5. **Memory Management**: Efficient handling of large data sets

### Scaling Patterns

1. **Stateless Design**: Minimize agent state dependencies
2. **Load Distribution**: Design for horizontal scaling
3. **Resource Pooling**: Share expensive resources across instances
4. **Graceful Degradation**: Handle failures and overload gracefully

## Security Considerations

### Security Patterns

1. **Input Validation**: Validate all incoming messages and data
2. **Capability Isolation**: Isolate capabilities from each other
3. **State Protection**: Protect sensitive state data
4. **Communication Security**: Secure inter-agent communication
5. **Error Handling**: Secure error handling without information leakage

## Migration and Versioning

### Version Compatibility

- **Forward Compatibility**: Design agents to handle newer message formats
- **Backward Compatibility**: Support legacy message formats when needed
- **Graceful Degradation**: Handle missing capabilities in other agents
- **Version Negotiation**: Negotiate capabilities and versions with other agents

## Common Patterns

### Error Handling

```python
async def safe_operation(self, operation_data):
    try:
        result = await self.perform_operation(operation_data)
        return self.success_response(result)
    except ValidationError as e:
        return self.error_response("VALIDATION_ERROR", str(e))
    except TimeoutError as e:
        return self.error_response("TIMEOUT", "Operation timed out")
    except Exception as e:
        await self.log_error(e)
        return self.error_response("INTERNAL_ERROR", "Internal processing error")
```

### Capability Discovery

```python
async def discover_agents_with_capability(self, capability_name: str):
    """Find other agents with specific capability"""

    discovered_agents = await self.discovery_service.find_agents({
        "capability": capability_name,
        "protocol": self.preferred_protocol
    })

    return discovered_agents
```

### Multi-Agent Coordination

```python
async def coordinate_with_agents(self, task_data, required_capabilities):
    """Coordinate task across multiple agents"""

    # Find agents with required capabilities
    available_agents = {}
    for capability in required_capabilities:
        agents = await self.discover_agents_with_capability(capability)
        available_agents[capability] = agents

    # Distribute work
    results = {}
    for capability, agents in available_agents.items():
        if agents:
            agent = self.select_best_agent(agents)
            results[capability] = await self.delegate_task(agent, task_data)

    return self.aggregate_results(results)
```

## Getting Started

1. **Choose Agent Type**: Select appropriate agent template for your use case
2. **Implement Core Logic**: Focus on your agent's specific functionality
3. **Register Capabilities**: Expose your agent's capabilities properly
4. **Configure Integration**: Set up configuration and framework integration
5. **Add Testing**: Implement comprehensive testing
6. **Deploy and Monitor**: Deploy with proper observability

For detailed implementation guidance, refer to:
- [Implementation Guide](./guide.md) - Step-by-step implementation process
- [Code Examples](./examples.md) - Complete working examples
- [Best Practices](./best_practices.md) - Guidelines for robust development

## References

### **Foundation & Best Practices**
- **[Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)** - Anthropic's foundational guide for agent development
- [Agent Framework Overview](../agent_framework_overview.md) - OpenMAS agent architecture
- [Agent Patterns](../agent_patterns.md) - Established OpenMAS design patterns
- [Agent Topologies](../agent_topologies.md) - Multi-agent organization patterns

### **OpenMAS Framework Integration**
- [Agent Capabilities](../agent_capabilities.md) - Capability system implementation
- [Session Management](../sessions/) - Session-aware agent development
- [State Management](../state/) - Layered state management
- [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md) - Agent configuration

### **Implementation Support**
- [Testing Framework](../../16_testing/) - Agent testing strategies
- [Observability](../../12_observability/) - Monitoring and debugging
- [Protocol Documentation](../../02_protocols/) - Protocol-specific implementation details

### **Legacy Reference (0.2.0)**
- **[0.2.0 Agent Patterns](../../../0.2.0/docs/guides/patterns.md)** - Original orchestrator-worker implementation
- **[0.2.0 README](../../../0.2.0/README.md)** - Original framework documentation referencing Anthropic best practices
