# A2A Protocol Support in OpenMAS

## Overview

The Agent-to-Agent (A2A) protocol is a communication standard designed for interactions between AI agents. OpenMAS provides comprehensive support for A2A while maintaining its core principle of reasoning agnosticism.

## Documentation

- [A2A Protocol Specification](./a2a_protocol.md) - Complete protocol specification and standards
- [A2A Implementation](./a2a_implementation.md) - Implementation details and code examples

## Protocol Specification

- **Name**: Agent-to-Agent Protocol (A2A)
- **Version**: 1.0
- **Purpose**: Standardized communication between AI agents
- **Transport**: HTTP, WebSockets, gRPC
- **Reasoning Agnosticism**: Complete separation between A2A communication layer and agent reasoning approaches

## Key Features

### Agent Discovery and Cards

OpenMAS fully implements the A2A agent card specification:

- **Well-Known Endpoints** - Standard `/.well-known/agent.json` discovery
- **Agent Metadata** - Name, description, version, and contact information
- **Capability Advertisement** - Structured capability definitions with parameters and return schemas
- **Feature Support** - Streaming, push notifications, and other feature advertisements
- **Authentication Requirements** - Authentication types and requirements

### Capability Model

OpenMAS implements the A2A capability model with these features:

- **Capability Registration** - Runtime registration of agent capabilities
- **Capability Discovery** - Dynamic discovery of other agents' capabilities
- **Parameter Schemas** - JSON Schema validation for capability parameters
- **Return Type Schemas** - JSON Schema validation for capability returns
- **Example Usage** - Example capability invocations for documentation

### Message Structure

OpenMAS supports the full A2A message format:

- **Roles** - Support for both user and agent roles
- **Part Types** - Support for text, binary data, and structured JSON parts
- **Tool Calls** - Support for tool request and response formats
- **Streaming** - Incremental message updates through streaming
- **Citations** - Source attribution through citation format

### Authentication and Security

OpenMAS implements A2A security features:

- **Authentication Methods** - Support for API keys, OAuth2, JWT, and basic auth
- **Authorization** - Capability-based access control
- **Rate Limiting** - Protection against abuse
- **Encrypted Communication** - TLS for all transports

## Protocol Implementation

### A2A Communicator

OpenMAS provides these A2A communicator implementations:

```python
# HTTP-based A2A communicator
from openmas.protocols.a2a import A2AHTTPCommunicator

communicator = A2AHTTPCommunicator(
    base_url="https://agent-api.example.com",
    agent_card={
        "name": "data_analysis_agent",
        "display_name": "Data Analysis Agent",
        "description": "Performs statistical analysis on datasets",
        "version": "1.0.0"
    },
    auth={
        "required": True,
        "types": ["api_key"]
    }
)

# WebSocket-based A2A communicator
from openmas.protocols.a2a import A2AWebSocketCommunicator

communicator = A2AWebSocketCommunicator(
    url="wss://agent-api.example.com/ws",
    agent_card=agent_card,
    streaming=True
)
```

### Agent Card Generation

OpenMAS automates agent card generation from agent capabilities:

```python
from openmas.protocols.a2a import generate_agent_card

agent_card = generate_agent_card(
    agent=my_agent,
    base_url="https://my-agent.example.com",
    contact_info={
        "name": "OpenMAS Team",
        "email": "support@example.com"
    }
)
```

## A2A with Different Reasoning Approaches

OpenMAS maintains reasoning agnosticism with A2A by:

- **Interface Abstraction** - A2A communication interfaces are independent of reasoning
- **Capability Adapters** - Adapting different reasoning outputs to A2A format
- **Message Transformation** - Converting between A2A messages and reasoning-specific formats

Examples of A2A with different reasoning types:

### LLM-Based Agents

```python
class LLMAgent(Agent):
    async def setup(self):
        # A2A capability registration
        self.register_capability(
            name="answer_question",
            description="Answers questions using LLM reasoning",
            parameters={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to answer"
                    }
                }
            },
            returns={
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The answer to the question"
                    }
                }
            }
        )

    @capability("answer_question")
    async def answer_question(self, question):
        # LLM-specific reasoning implementation
        response = await self.llm.generate(prompt=f"Question: {question}\nAnswer:")
        return {"answer": response.text}
```

### Rule-Based Agents

```python
class RuleBasedAgent(Agent):
    async def setup(self):
        # A2A capability registration (same interface)
        self.register_capability(
            name="evaluate_condition",
            description="Evaluates a condition using rule-based reasoning",
            parameters={
                "type": "object",
                "properties": {
                    "condition": {
                        "type": "string",
                        "description": "The condition to evaluate"
                    },
                    "facts": {
                        "type": "object",
                        "description": "The facts to evaluate against"
                    }
                }
            },
            returns={
                "type": "object",
                "properties": {
                    "result": {
                        "type": "boolean",
                        "description": "The result of the evaluation"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Explanation of the result"
                    }
                }
            }
        )

    @capability("evaluate_condition")
    async def evaluate_condition(self, condition, facts):
        # Rule-based reasoning implementation
        result = self.rule_engine.evaluate(condition, facts)
        return {
            "result": result.value,
            "explanation": result.explanation
        }
```

## A2A Protocol Configuration

For A2A protocol configuration, OpenMAS uses the unified configuration schema. For the complete schema definition, see [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md), with protocol-specific details in [Protocol Schema](/03_configuration/schema/protocols.md).

Key configuration sections:

- **Agent Card Configuration**
- **Transport Options**
- **Authentication Settings**
- **Discovery Configuration**
- **Feature Flags**

## A2A Integration with Other Components

A2A protocol integrates with several OpenMAS components:

1. **Communication Patterns** - A2A-specific implementations of standard patterns
2. **Topology System** - A2A support for agent organization patterns
3. **Security System** - A2A-specific authentication and authorization
4. **Observability System** - A2A-specific monitoring and logging

## Known Limitations and Future Work

- **Partial Streaming Support** - Some A2A streaming features are in development
- **Advanced Authentication Flows** - Additional OAuth flows planned for future releases
- **Tool Ecosystem Integration** - Expanded integration with A2A tool ecosystem in progress
