# OpenMAS Architecture Diagrams

This document contains the architectural diagrams referenced in the [Architecture Overview](./architecture_overview.md) document. Centralizing diagrams in this file improves maintainability and organization.

## High-Level Component Architecture

The following diagram illustrates the high-level component architecture of OpenMAS v0.3.0:

```mermaid
graph TD
    %% Main Framework Container
    subgraph OpenMAS["OpenMAS Framework"]
        %% Top Level Components
        subgraph TopLevel["Top-Level Components"]
            Config["Configuration System"]
            CLI["Command Line Interface"]
            AgentFW["Agent Framework"]
            ExtSystem["Extension System"]
        end

        %% Core Components
        subgraph CoreComponents["Core Components"]
            %% First row of core components
            AssetMgmt["Asset Management"]
            KRR["Knowledge Representation & Reasoning System"]
            Protocol["Protocol Layer"]
            PromptMgmt["Prompt Management"]
            SessionMgmt["Session Management"]

            %% Second row of core components
            TopologyMgmt["Topology Management"]
            CommPattern["Communication Pattern Engine"]
            Security["Security System"]
            Observability["Observability System"]
        end

        %% Reasoning Engines
        subgraph ReasoningEngines["Reasoning Engines"]
            RuleBased["Rule-Based Engine"]
            BDI["BDI Engine"]
            LLM["LLM-Based Engine"]
            Hybrid["Hybrid Engine"]
        end

        %% Deployment Options
        subgraph Deployment["Deployment Options"]
            K8s["Kubernetes/Docker"]
            Process["Process-Based"]
            Local["Local Development"]
        end

        %% Agent Topologies
        subgraph Topologies["Agent Topologies"]
            Centralized["Centralized (Hub-Spoke)"]
            P2P["Peer-to-Peer"]
            Hierarchical["Hierarchical (Tree)"]
            Mesh["Mesh"]
        end

        %% Communication Patterns
        subgraph CommPatterns["Communication Patterns"]
            ReqResp["Request-Response"]
            PubSub["Publish-Subscribe"]
            EventBased["Event-Based"]
            Streaming["Streaming"]
            Pipeline["Pipeline/Delegation"]
        end

        %% Protocol Implementations
        subgraph Protocols["Protocol Implementations"]
            A2A["A2A Protocol"]
            MCP["MCP Protocol"]
            HTTP["HTTP Protocol"]
            MQTT["MQTT Protocol"]
            GRPC["gRPC Protocol"]
        end

        %% Component Relationships
        Config --> AgentFW
        Config --> Protocol
        Config --> KRR
        Config --> TopologyMgmt

        AgentFW --> KRR
        AgentFW --> Protocol
        AgentFW --> ReasoningEngines

        Protocol --> Protocols

        KRR -.-> ReasoningEngines
        ReasoningEngines -.-> KRR

        TopologyMgmt --> CommPattern
        CommPattern --> Protocol

        %% Style classes
        classDef core fill:#f9f,stroke:#333,stroke-width:1px;
        classDef engines fill:#bbf,stroke:#333,stroke-width:1px;
        classDef protocols fill:#bfb,stroke:#333,stroke-width:1px;

        class CoreComponents core;
        class ReasoningEngines engines;
        class Protocols protocols;
    end
```

### Key Components Relationships

This diagram highlights the critical relationships between the KR&R System and Reasoning Engines:

```mermaid
graph TD
    %% Main Components
    AgentFW["Agent Framework"]
    ReasoningEngines["Reasoning Engines"]
    KRR["KR&R System"]
    Protocol["Protocol Layer"]

    %% Sub-Components of Reasoning Engines
    subgraph ReasoningEngines["Reasoning Engines (Agent's Brain)"]
        RuleBased["Rule-Based Engine"]
        BDI["BDI Engine"]
        LLM["LLM-Based Engine"]
        Hybrid["Hybrid Engine"]
    end

    %% Sub-Components of KR&R
    subgraph KRR["KR&R System (Knowledge Management)"]
        IKB["IKnowledgeBase Interface"]
        SymbolicKB["Symbolic Knowledge Base"]
        GraphKB["Graph Knowledge Base"]
        VectorKB["Vector Knowledge Base"]
        KBREG["Knowledge Base Registry"]
    end

    %% Component Relationships
    Protocol -->|"Protocol-specific messages"| AgentFW
    AgentFW -->|"Standard Internal Message Format"| ReasoningEngines

    RuleBased -->|"Uses for facts"| IKB
    BDI -->|"Uses for beliefs"| IKB
    LLM -->|"Uses for context"| IKB
    Hybrid -->|"Uses for hybrid knowledge"| IKB

    IKB -->|"Standardized Access"| SymbolicKB
    IKB -->|"Standardized Access"| GraphKB
    IKB -->|"Standardized Access"| VectorKB

    %% Style classes
    classDef engines fill:#bbf,stroke:#333,stroke-width:1px;
    classDef krr fill:#bfb,stroke:#333,stroke-width:1px;
    classDef interface fill:#ff9,stroke:#333,stroke-width:2px;

    class ReasoningEngines,RuleBased,BDI,LLM,Hybrid engines;
    class KRR,SymbolicKB,GraphKB,VectorKB,KBREG krr;
    class IKB interface;
```

## Protocol Integration Architecture

The diagram below illustrates how OpenMAS supports multiple protocols simultaneously:

```mermaid
graph TD
    %% External Components
    A2AClient["A2A Client"]
    MCPClient["MCP Client"]
    HTTPClient["HTTP Client"]
    MQTTBroker["MQTT Broker"]
    GRPCClient["gRPC Client"]

    %% Agent with Protocol Interfaces
    subgraph Agent["OpenMAS Agent"]
        subgraph ProtocolInterfaces["Protocol Interfaces"]
            A2A["A2A Interface"]
            MCP["MCP Interface"]
            HTTP["HTTP Interface"]
            MQTT["MQTT Interface"]
            GRPC["gRPC Interface"]
        end

        subgraph AgentCore["Agent Core"]
            SIMF["Standard Internal Message Format"]
            Framework["Agent Framework"]
            Reasoning["Reasoning Engine"]
            KRRSystem["KR&R System"]
        end

        %% Protocol to SIMF connections
        A2A -->|"to_internal_format()"| SIMF
        MCP -->|"to_internal_format()"| SIMF
        HTTP -->|"to_internal_format()"| SIMF
        MQTT -->|"to_internal_format()"| SIMF
        GRPC -->|"to_internal_format()"| SIMF

        %% Core processing
        SIMF --> Framework
        Framework --> Reasoning
        Reasoning -->|"IKnowledgeBase"| KRRSystem
        Reasoning --> Framework

        %% SIMF to Protocol connections
        Framework --> SIMF
        SIMF -->|"from_internal_format()"| A2A
        SIMF -->|"from_internal_format()"| MCP
        SIMF -->|"from_internal_format()"| HTTP
        SIMF -->|"from_internal_format()"| MQTT
        SIMF -->|"from_internal_format()"| GRPC
    end

    %% External connections
    A2AClient <-->|"A2A Protocol"| A2A
    MCPClient <-->|"MCP Protocol"| MCP
    HTTPClient <-->|"HTTP Protocol"| HTTP
    MQTTBroker <-->|"MQTT Protocol"| MQTT
    GRPCClient <-->|"gRPC Protocol"| GRPC

    %% Style classes
    classDef external fill:#f96,stroke:#333,stroke-width:1px;
    classDef interfaces fill:#bbf,stroke:#333,stroke-width:1px;
    classDef core fill:#bfb,stroke:#333,stroke-width:1px;

    class A2AClient,MCPClient,HTTPClient,MQTTBroker,GRPCClient external;
    class ProtocolInterfaces,A2A,MCP,HTTP,MQTT,GRPC interfaces;
    class AgentCore,SIMF,Framework,Reasoning,KRRSystem core;
```

## Topology and Communication Patterns

The following diagram shows the relationship between agent topologies and communication patterns:

```mermaid
graph TD
    %% Main Components
    subgraph Topologies["Agent Topologies"]
        Centralized["Centralized (Hub-Spoke)"]
        P2P["Peer-to-Peer"]
        Hierarchical["Hierarchical (Tree)"]
        Mesh["Mesh"]
    end

    subgraph Patterns["Communication Patterns"]
        ReqResp["Request-Response"]
        PubSub["Publish-Subscribe"]
        EventBased["Event-Based"]
        Streaming["Streaming"]
        Pipeline["Pipeline/Delegation"]
    end

    subgraph Protocols["Protocol Implementations"]
        A2A["A2A Protocol"]
        MCP["MCP Protocol"]
        HTTP["HTTP Protocol"]
        MQTT["MQTT Protocol"]
        GRPC["gRPC Protocol"]
    end

    %% Relationships
    Topologies -->|"Use"| Patterns
    Patterns -->|"Implemented by"| Protocols

    %% Style classes
    classDef topologies fill:#f9f,stroke:#333,stroke-width:1px;
    classDef patterns fill:#bbf,stroke:#333,stroke-width:1px;
    classDef protocols fill:#bfb,stroke:#333,stroke-width:1px;

    class Topologies,Centralized,P2P,Hierarchical,Mesh topologies;
    class Patterns,ReqResp,PubSub,EventBased,Streaming,Pipeline patterns;
    class Protocols,A2A,MCP,HTTP,MQTT,GRPC protocols;
```

## Security Architecture

The security architecture integrates with all components:

```mermaid
graph TD
    %% Main Components
    ExternalSystems["External Systems"]
    ProtocolLayer["Protocol Layer"]
    AgentFramework["Agent Framework"]
    ReasoningEngine["Reasoning Engine"]

    %% Security Components
    subgraph SecuritySystem["Security System"]
        AuthN["Authentication"]
        AuthZ["Authorization"]
        RSI["Reasoning Security Interface"]
        Crypto["Cryptography"]
        Policies["Security Policies"]
    end

    %% Relationships
    ExternalSystems <-->|"Credentials"| ProtocolLayer
    ProtocolLayer -->|"Validate"| AuthN
    AuthN -->|"Principal Info"| AuthZ
    AuthZ -->|"Permissions"| AgentFramework
    AgentFramework -->|"Security Context"| ReasoningEngine
    ReasoningEngine <-->|"Check Permissions"| RSI
    RSI -->|"Permission Check"| AuthZ

    %% Style classes
    classDef security fill:#f96,stroke:#333,stroke-width:1px;
    classDef external fill:#ccc,stroke:#333,stroke-width:1px;

    class SecuritySystem,AuthN,AuthZ,RSI,Crypto,Policies security;
    class ExternalSystems external;
```

## Observability Architecture

The observability architecture provides monitoring and debugging capabilities:

```mermaid
graph TD
    %% Main Components
    subgraph ObservabilitySystem["Observability System"]
        Logging["Logging"]
        Metrics["Metrics Collection"]
        Tracing["Distributed Tracing"]
        Health["Health Monitoring"]
        Dashboard["Dashboard Integration"]
    end

    %% Integration Points
    AgentFramework["Agent Framework"]
    ProtocolLayer["Protocol Layer"]
    KRRSystem["KR&R System"]
    ReasoningEngines["Reasoning Engines"]

    %% Relationships
    AgentFramework -->|"Log Events"| Logging
    ProtocolLayer -->|"Protocol Metrics"| Metrics
    KRRSystem -->|"KB Operations"| Logging
    ReasoningEngines -->|"Reasoning Traces"| Tracing

    %% Style classes
    classDef observability fill:#9cf,stroke:#333,stroke-width:1px;

    class ObservabilitySystem,Logging,Metrics,Tracing,Health,Dashboard observability;
```

These diagrams provide a visual representation of the OpenMAS v0.3.0 architecture and its key components.
