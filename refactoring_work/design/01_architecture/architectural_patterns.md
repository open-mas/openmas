# Architectural Patterns

## Overview

This document describes the key architectural patterns used throughout the OpenMAS framework. These patterns provide consistent solutions to common architectural problems, ensuring the framework maintains its reasoning-agnostic design and multi-protocol capabilities while following software engineering best practices.

## Core Architectural Patterns

### 1. Body-Brain Separation (Reasoning Agnosticism)

The defining architectural pattern of OpenMAS is the clear separation between communication infrastructure ("body") and reasoning approaches ("brain"). This pattern is fundamental to OpenMAS's reasoning agnosticism.

**Implementation:**
- Communication components handle protocol-specific interactions without reasoning logic
- Reasoning components implement decision-making logic independent of communication protocols
- Adapters connect communication and reasoning components with clean interfaces

**Benefits:**
- Any reasoning approach can work with any communication protocol
- Agents can be implemented with different reasoning approaches (rule-based, BDI, LLM, etc.)
- Protocols can evolve independently of reasoning implementations

**Example:**
```python
class Agent:
    def __init__(self, communicator, reasoning_engine):
        self.communicator = communicator  # "Body" - handles external communication
        self.reasoning = reasoning_engine  # "Brain" - handles decision making

    async def process_message(self, message):
        # Communication layer handles message parsing
        context = self.communicator.parse_message(message)

        # Reasoning layer decides on response
        action = await self.reasoning.decide_action(context)

        # Communication layer formats and sends response
        return self.communicator.format_response(action)
```

### 2. Protocol Adapter Pattern

The Protocol Adapter pattern enables agents to communicate via multiple protocols without protocol-specific code in the agent core.

**Implementation:**
- Protocol-specific adapters translate between protocol formats and internal representations
- Common message format used internally regardless of external protocol
- Protocol capabilities are mapped to agent capabilities

**Benefits:**
- Agents can use multiple protocols simultaneously
- New protocols can be added without modifying agent logic
- Protocol-specific details are isolated in adapters

**Example:**
```python
class McpAdapter(ProtocolAdapter):
    def translate_inbound(self, mcp_message):
        # Convert MCP format to internal format
        return InternalMessage(
            type=mcp_message.type,
            content=mcp_message.content,
            context=mcp_message.context
        )

    def translate_outbound(self, internal_message):
        # Convert internal format to MCP format
        return McpMessage(
            type=internal_message.type,
            content=internal_message.content,
            context=internal_message.context
        )
```

### 3. Capability-Based Design

The Capability-Based Design pattern structures agents around discrete capabilities that define what the agent can do.

**Implementation:**
- Capabilities are well-defined, discrete units of functionality
- Agents expose capabilities through a capability registry
- Capabilities can be discovered and negotiated between agents
- Protocol-specific implementations of capabilities through adapters

**Benefits:**
- Clear definition of agent functionality
- Dynamic discovery of agent capabilities
- Capability negotiation between agents
- Protocol-independent capability definitions

**Example:**
```python
class Agent:
    def __init__(self):
        self.capabilities = CapabilityRegistry()

    def register_capability(self, capability):
        self.capabilities.register(capability)

    async def handle_request(self, request):
        capability_id = request.get_capability_id()

        if not self.capabilities.has(capability_id):
            return ErrorResponse("Capability not supported")

        capability = self.capabilities.get(capability_id)
        return await capability.execute(request)
```

### 4. Multi-Protocol Communication

The Multi-Protocol Communication pattern enables agents to communicate over different protocols transparently.

**Implementation:**
- Protocol-agnostic communication interface
- Protocol-specific implementations
- Dynamic protocol selection based on context
- Protocol negotiation mechanisms

**Benefits:**
- Communication across different protocols
- Adaptability to various environments
- Interoperability with external systems
- Resilience through protocol diversity

**Example:**
```python
class Communicator:
    def __init__(self):
        self.protocols = {}

    def register_protocol(self, protocol_type, protocol_handler):
        self.protocols[protocol_type] = protocol_handler

    async def send_message(self, message, protocol_type=None):
        # Determine protocol to use
        if protocol_type is None:
            protocol_type = self.determine_protocol(message)

        if protocol_type not in self.protocols:
            raise ProtocolError(f"Protocol not supported: {protocol_type}")

        protocol = self.protocols[protocol_type]
        return await protocol.send(message)

    async def receive_message(self, raw_message, protocol_type=None):
        # Determine protocol to use
        if protocol_type is None:
            protocol_type = self.detect_protocol(raw_message)

        if protocol_type not in self.protocols:
            raise ProtocolError(f"Protocol not supported: {protocol_type}")

        protocol = self.protocols[protocol_type]
        return await protocol.receive(raw_message)
```

### 5. Layered Architecture

The Layered Architecture pattern organizes the system into distinct layers with clear responsibilities.

**Implementation:**
- Protocol Layer: Handles external communication protocols
- Agent Layer: Manages agent lifecycle and behavior
- Reasoning Layer: Implements decision-making logic
- Service Layer: Provides shared services and utilities
- Infrastructure Layer: Manages system resources and deployment

**Benefits:**
- Separation of concerns
- Modularity and maintainability
- Testability of individual layers
- Evolution of layers independently
- Clear dependencies between layers

**Example:**
```
┌────────────────────────────────────────────┐
│              Application Layer             │
└───────────────────┬────────────────────────┘
                    │
┌───────────────────▼────────────────────────┐
│                Agent Layer                 │
└───────────────────┬────────────────────────┘
                    │
┌───────────────────▼────────────────────────┐
│              Protocol Layer                │
└───────────────────┬────────────────────────┘
                    │
┌───────────────────▼────────────────────────┐
│              Service Layer                 │
└───────────────────┬────────────────────────┘
                    │
┌───────────────────▼────────────────────────┐
│           Infrastructure Layer             │
└────────────────────────────────────────────┘
```

## Structural Patterns

### 1. Adapter Pattern

The Adapter pattern allows classes with incompatible interfaces to work together.

**Implementation:**
- Protocol adapters convert between protocol formats
- Reasoning adapters provide consistent interfaces to different reasoning approaches
- Legacy system adapters integrate external systems

**Benefits:**
- Makes incompatible interfaces compatible
- Enables reuse of existing code
- Facilitates integration with external systems

**Example:**
```python
class A2aToMcpAdapter:
    def __init__(self, a2a_client):
        self.a2a_client = a2a_client

    async def invoke_tool(self, tool_name, params):
        # Convert MCP tool invocation to A2A capability invocation
        a2a_response = await self.a2a_client.invoke_capability(
            capability="function_execution",
            params={
                "function": tool_name,
                "parameters": params
            }
        )

        # Convert A2A response to MCP response
        return {
            "type": "function_response",
            "name": tool_name,
            "response": a2a_response.result
        }
```

### 2. Facade Pattern

The Facade pattern provides a simplified interface to a complex subsystem.

**Implementation:**
- Agent facades simplify interaction with complex agent systems
- Protocol facades abstract protocol complexities
- Service facades simplify access to complex services

**Benefits:**
- Simplifies client interaction with complex systems
- Reduces dependencies between clients and subsystems
- Promotes loose coupling between subsystems
- Enables incremental refactoring of subsystems

**Example:**
```python
class AgentFacade:
    def __init__(self, config):
        # Initialize complex subsystems
        self.communicator = CommunicatorFactory.create(config)
        self.reasoning = ReasoningFactory.create(config)
        self.lifecycle = LifecycleManager(config)
        self.observation = ObservationSystem(config)

    async def initialize(self):
        # Handle complex initialization
        await self.communicator.initialize()
        await self.reasoning.initialize()
        await self.lifecycle.initialize()
        await self.observation.initialize()

    async def process_message(self, message):
        # Simplified interface for message processing
        return await self.communicator.process(
            message,
            self.reasoning
        )

    async def shutdown(self):
        # Handle complex shutdown
        await self.observation.shutdown()
        await self.lifecycle.shutdown()
        await self.reasoning.shutdown()
        await self.communicator.shutdown()
```

### 3. Bridge Pattern

The Bridge pattern decouples abstraction from implementation, allowing them to vary independently.

**Implementation:**
- Communication abstractions separate from communication implementations
- Reasoning abstractions separate from reasoning implementations
- Protocol abstractions separate from protocol implementations

**Benefits:**
- Separates interface from implementation
- Enables independent evolution of abstractions and implementations
- Supports runtime selection of implementations
- Promotes composition over inheritance

**Example:**
```python
# Abstraction
class Communicator(ABC):
    def __init__(self, implementation):
        self.implementation = implementation

    @abstractmethod
    async def send_message(self, message):
        pass

    @abstractmethod
    async def receive_message(self):
        pass

# Implementation
class CommunicationImplementation(ABC):
    @abstractmethod
    async def send_raw(self, data):
        pass

    @abstractmethod
    async def receive_raw(self):
        pass

# Refined Abstraction
class AsyncCommunicator(Communicator):
    async def send_message(self, message):
        data = self.serialize(message)
        await self.implementation.send_raw(data)

    async def receive_message(self):
        data = await self.implementation.receive_raw()
        return self.deserialize(data)

    def serialize(self, message):
        # Serialize message to raw data
        pass

    def deserialize(self, data):
        # Deserialize raw data to message
        pass

# Concrete Implementation
class HttpCommunication(CommunicationImplementation):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    async def send_raw(self, data):
        async with aiohttp.ClientSession() as session:
            await session.post(self.endpoint, data=data)

    async def receive_raw(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.endpoint) as response:
                return await response.read()
```

### 4. Composite Pattern

The Composite pattern allows treating individual objects and compositions of objects uniformly.

**Implementation:**
- Agent compositions for creating agent hierarchies
- Capability compositions for complex capabilities
- Service compositions for composite services

**Benefits:**
- Uniform treatment of individual and composite objects
- Hierarchical structures are easy to build and navigate
- New components can be added without changing existing code
- Clients remain simple when dealing with complex structures

**Example:**
```python
class Component(ABC):
    @abstractmethod
    async def execute(self, request):
        pass

class LeafAgent(Component):
    async def execute(self, request):
        # Perform actual work
        return self.process_request(request)

    def process_request(self, request):
        # Process the request
        pass

class CompositeAgent(Component):
    def __init__(self):
        self.children = []

    def add(self, component):
        self.children.append(component)

    def remove(self, component):
        self.children.remove(component)

    async def execute(self, request):
        # Delegate to children and aggregate results
        results = []
        for child in self.children:
            result = await child.execute(request)
            results.append(result)
        return self.aggregate_results(results)

    def aggregate_results(self, results):
        # Aggregate results from children
        pass
```

## Behavioral Patterns

### 1. Observer Pattern

The Observer pattern defines a dependency between objects where observers are notified of changes in the subject.

**Implementation:**
- Event systems for notifications
- Agent state observers
- Capability state observers
- System monitors

**Benefits:**
- Loose coupling between subjects and observers
- Support for broadcast communication
- Dynamic relationships between objects
- Consistent notification mechanism

**Example:**
```python
class Subject(ABC):
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def notify(self, event):
        for observer in self.observers:
            observer.update(event)

class Observer(ABC):
    @abstractmethod
    def update(self, event):
        pass

class Agent(Subject):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.state = "initialized"

    def set_state(self, state):
        old_state = self.state
        self.state = state
        self.notify({
            "type": "state_change",
            "agent_id": self.id,
            "old_state": old_state,
            "new_state": state
        })

class AgentMonitor(Observer):
    def update(self, event):
        if event["type"] == "state_change":
            print(f"Agent {event['agent_id']} changed state from {event['old_state']} to {event['new_state']}")
```

### 2. Strategy Pattern

The Strategy pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable.

**Implementation:**
- Reasoning strategies for different approaches
- Communication strategies for different protocols
- Task execution strategies

**Benefits:**
- Algorithms can vary independently from clients
- Eliminates conditional statements
- Provides alternative implementations
- Encapsulates algorithm details

**Example:**
```python
class ReasoningStrategy(ABC):
    @abstractmethod
    async def reason(self, context):
        pass

class RuleBasedReasoning(ReasoningStrategy):
    def __init__(self, rule_set):
        self.rule_set = rule_set

    async def reason(self, context):
        # Apply rules to context
        for rule in self.rule_set:
            if rule.matches(context):
                return rule.execute(context)
        return None

class LlmReasoning(ReasoningStrategy):
    def __init__(self, model, prompt_template):
        self.model = model
        self.prompt_template = prompt_template

    async def reason(self, context):
        # Generate prompt from context
        prompt = self.prompt_template.format(**context)

        # Get response from LLM
        response = await self.model.generate(prompt)

        # Parse response
        return self.parse_response(response)

    def parse_response(self, response):
        # Parse LLM response
        pass

class Agent:
    def __init__(self, reasoning_strategy):
        self.reasoning_strategy = reasoning_strategy

    def set_reasoning_strategy(self, reasoning_strategy):
        self.reasoning_strategy = reasoning_strategy

    async def process(self, context):
        return await self.reasoning_strategy.reason(context)
```

### 3. Command Pattern

The Command pattern encapsulates a request as an object, allowing parameterization of clients with queuing, logging, and undoable operations.

**Implementation:**
- Capability invocations as commands
- Agent operations as commands
- Configuration operations as commands

**Benefits:**
- Decouples sender from receiver
- Commands can be stored and executed later
- Commands can be composed into complex operations
- Commands can be logged, queued, and undone

**Example:**
```python
class Command(ABC):
    @abstractmethod
    async def execute(self):
        pass

    @abstractmethod
    async def undo(self):
        pass

class SendMessageCommand(Command):
    def __init__(self, agent, recipient, content):
        self.agent = agent
        self.recipient = recipient
        self.content = content
        self.message_id = None

    async def execute(self):
        self.message_id = await self.agent.send_message(
            recipient=self.recipient,
            content=self.content
        )
        return self.message_id

    async def undo(self):
        if self.message_id:
            await self.agent.retract_message(self.message_id)

class CommandProcessor:
    def __init__(self):
        self.history = []

    async def execute_command(self, command):
        result = await command.execute()
        self.history.append(command)
        return result

    async def undo_last(self):
        if self.history:
            command = self.history.pop()
            await command.undo()
```

## Design Principles

### 1. Configurability

Implementation details follow these configuration principles:

- **Configuration-Driven**: Core behaviors are controlled through configuration rather than code changes
- **Sensible Defaults**: Implementations provide reasonable defaults that work in most scenarios
- **Explicit Over Implicit**: Configuration options are explicit and well-documented
- **Validation**: Configuration is validated against schemas at runtime

### 2. Observability

Implementations provide comprehensive observability:

- **Structured Logging**: Consistent, structured logging across all components
- **Metrics Exposure**: Key performance and usage metrics exposed for monitoring
- **Traceability**: End-to-end tracing of operations across component boundaries
- **Debug Capabilities**: Implementation includes hooks for debugging and troubleshooting

### 3. Testability

All implementations are designed with testability in mind:

- **Unit Testing**: Components are designed to be easily unit testable
- **Integration Testing**: Integration points are exposed for comprehensive testing
- **Mocking Support**: Dependencies are designed to be easily mockable
- **Observability Testing**: Observability features themselves are testable

### 4. Security

Security principles are embedded in all implementations:

- **Defense in Depth**: Multiple layers of security controls
- **Least Privilege**: Components operate with minimal required permissions
- **Secure by Default**: Security features enabled by default
- **Input Validation**: All inputs are validated before processing

### 5. Performance

Implementation considers performance characteristics:

- **Efficiency**: Resources are used efficiently
- **Scalability**: Components scale horizontally where possible
- **Measurement**: Performance characteristics are measurable
- **Tuning**: Performance-critical parameters are configurable

## Related Documentation

- [Architecture Overview](./architecture_overview.md)
- [Reasoning Agnostic Design](./reasoning_agnostic_design.md)
- [Multi-Protocol Design](./multi_protocol_design.md)
- [Runtime Architecture](./runtime_architecture.md)
- [Unified Configuration Schema](../03_configuration/unified_configuration_schema.md)
