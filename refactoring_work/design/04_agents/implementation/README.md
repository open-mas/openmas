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

### 1. Protocol-Specific Agent Templates

- **A2A Agent**: Agent optimized for Agent-to-Agent communication
- **MCP Agent**: Agent with MCP tool integration capabilities
- **HTTP Agent**: Agent for REST API interactions
- **Multi-Protocol Agent**: Agent supporting multiple protocols simultaneously

### 2. Reasoning Pattern Templates

- **Rule-Based Agent**: Traditional rule-based reasoning
- **LLM Agent**: Large Language Model integration
- **Hybrid Agent**: Combining multiple reasoning approaches
- **BDI Agent**: Belief-Desire-Intention framework integration

### 3. Functional Pattern Templates

- **Data Processing Agent**: Specialized for data transformation
- **Coordination Agent**: Multi-agent orchestration
- **Interface Agent**: Human-computer interaction
- **Service Agent**: External service integration

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

- [Agent Framework Overview](../agent_framework_overview.md)
- [Agent Capabilities](../agent_capabilities.md)
- [Session Management](../sessions/)
- [State Management](../state/)
- [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md)
- [Testing Framework](../../16_testing/)
- [Observability](../../12_observability/)
