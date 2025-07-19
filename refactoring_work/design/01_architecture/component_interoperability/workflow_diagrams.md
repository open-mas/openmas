# OpenMAS End-to-End Workflows

This document illustrates complete workflows that span multiple OpenMAS components, providing a comprehensive view of how components interact in key operational scenarios.

## Agent Message Processing Workflow

```mermaid
sequenceDiagram
    participant EC as External Component
    participant PL as Protocol Layer
    participant AF as Agent Framework
    participant KR as Knowledge & Reasoning
    participant AM as Asset Management
    participant SM as Session Management
    participant OB as Observability
    
    EC->>PL: Send message via protocol
    PL->>OB: Log incoming message
    PL->>SM: Validate session
    SM-->>PL: Session valid
    PL->>AF: Translate to internal message format
    AF->>AM: Retrieve relevant assets
    AM-->>AF: Return assets
    AF->>KR: Request decision
    KR->>KR: Process with reasoning engine
    KR-->>AF: Return action decision
    AF->>OB: Log decision and action
    AF->>PL: Format response
    PL->>OB: Log outgoing message
    PL-->>EC: Send protocol-specific response
```

### Workflow Steps:
1. **Message Reception**: External component sends a message using a specific protocol (A2A, MCP, HTTP, MQTT, gRPC)
2. **Protocol Translation**: Protocol Layer receives the message, logs it, validates the session, and translates it to the internal OpenMAS message format
3. **Asset Retrieval**: Agent Framework requests any necessary assets (knowledge bases, prompts, etc.) from Asset Management
4. **Decision Making**: Agent Framework delegates decision-making to the Knowledge Representation & Reasoning component
5. **Response Generation**: Based on the decision, an appropriate response is generated
6. **Response Delivery**: The response is formatted according to the protocol and sent back to the external component
7. **Observability**: Throughout the process, key events are logged for monitoring and debugging

## Agent Initialization Workflow

```mermaid
sequenceDiagram
    participant CS as Configuration System
    participant AF as Agent Framework
    participant KR as Knowledge & Reasoning
    participant PL as Protocol Layer
    participant TS as Topology System
    participant AM as Asset Management
    participant PM as Prompt Management
    participant ES as Extension System
    participant SS as Security System
    
    CS->>AF: Initialize agent framework
    CS->>KR: Configure reasoning engines
    CS->>PL: Configure protocol handlers
    CS->>TS: Configure topology
    CS->>SS: Apply security policies
    
    AF->>KR: Register reasoning engines
    AF->>AM: Load initial assets
    AF->>PM: Register prompt templates
    AF->>ES: Register extensions
    AF->>PL: Register with protocol handlers
    
    PL->>SS: Authenticate/authorize
    PL->>TS: Register in topology
    
    TS->>AF: Notify topology ready
    AF->>AF: Mark initialization complete
```

### Workflow Steps:
1. **Configuration Loading**: Configuration System loads and validates all configuration parameters
2. **Component Initialization**: Each core component is initialized with its configuration
3. **Registration Phase**: Components register their capabilities with each other
4. **Security Setup**: Security policies are applied across components
5. **Topology Establishment**: Agent relationships and communication paths are established
6. **Readiness Signaling**: Components signal readiness to the Agent Framework

## Capability Invocation Workflow

```mermaid
sequenceDiagram
    participant EC as External Component
    participant PL as Protocol Layer
    participant AF as Agent Framework
    participant KR as Knowledge & Reasoning
    participant ES as Extension System
    participant OB as Observability
    
    EC->>PL: Invoke capability
    PL->>AF: Translate capability request
    AF->>KR: Evaluate capability constraints
    KR-->>AF: Constraints satisfied
    AF->>ES: Forward to capability implementation
    ES->>ES: Execute capability
    ES->>OB: Log capability execution
    ES-->>AF: Return capability result
    AF->>PL: Format capability response
    PL-->>EC: Return capability result
```

### Workflow Steps:
1. **Capability Request**: External component requests a capability invocation 
2. **Request Translation**: Protocol Layer translates the request to the internal format
3. **Constraint Evaluation**: Knowledge & Reasoning evaluates if the capability can be invoked
4. **Capability Execution**: Extension System handles the actual execution of the capability
5. **Result Delivery**: The result is returned through the Protocol Layer to the requester

## Multi-Agent Interaction Workflow

```mermaid
sequenceDiagram
    participant A1 as Agent 1
    participant TS as Topology System
    participant CPE as Communication Pattern Engine
    participant PL as Protocol Layer
    participant A2 as Agent 2
    participant SM as Session Management
    
    A1->>TS: Discover agents
    TS-->>A1: Return agent 2 info
    A1->>CPE: Select communication pattern
    CPE-->>A1: Return pattern implementation
    A1->>SM: Create/join session
    SM-->>A1: Session established
    A1->>PL: Send message to agent 2
    PL->>A2: Deliver message
    A2->>PL: Send response
    PL->>A1: Deliver response
```

### Workflow Steps:
1. **Agent Discovery**: Agent 1 uses Topology System to discover other agents
2. **Pattern Selection**: Communication Pattern Engine provides an appropriate interaction pattern
3. **Session Establishment**: Session Management creates a shared interaction context
4. **Message Exchange**: Agents exchange messages via the Protocol Layer
5. **Interaction Completion**: The multi-agent interaction completes according to the pattern

## Error Handling Workflow

```mermaid
sequenceDiagram
    participant C as Component
    participant OB as Observability
    participant SS as Security System
    participant AF as Agent Framework
    
    C->>C: Error occurs
    C->>OB: Log error details
    OB->>OB: Analyze error severity
    alt Critical Error
        OB->>SS: Security validation
        SS->>AF: Trigger recovery procedure
        AF->>C: Apply correction or shutdown
    else Non-critical Error
        OB->>AF: Notify of error
        AF->>C: Continue with degraded function
    end
    OB->>OB: Update error metrics
```

### Workflow Steps:
1. **Error Detection**: A component detects an error condition
2. **Logging**: Error details are sent to the Observability System
3. **Severity Analysis**: The error severity is assessed
4. **Response Selection**: Based on severity, an appropriate response is selected
5. **Recovery Action**: Recovery procedures are applied as appropriate
6. **Metrics Update**: Error metrics are updated for monitoring
