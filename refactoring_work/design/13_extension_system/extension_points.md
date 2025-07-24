# OpenMAS Extension Points

## 1. Overview

OpenMAS is designed to be highly extensible, allowing developers to add new capabilities without modifying the core framework. This is achieved through a system of well-defined **Extension Points**. Each extension point is a formal interface (an Abstract Base Class) that a custom extension can implement to integrate new functionality into the system.

An extension is a self-contained package that implements one or more of these extension point interfaces. The OpenMAS framework discovers and loads these extensions at startup, and core components then interact with them through their specific, type-safe interfaces.

This document serves as an index of the available extension points in OpenMAS.

## 2. Core Extension Points

Below are the primary interfaces that can be implemented to extend OpenMAS.

### 2.1. Protocol Extension (`IProtocolExtension`)

- **Purpose**: To add support for new communication protocols (e.g., WebSocket, AMQP).
- **Interface Definition**: See [`protocol_extension_interface.md`](./interfaces/protocol_extension_interface.md)
- **Description**: This is one of the most fundamental extension points. An implementation provides the logic for creating protocol-specific communicators and adapters, allowing the framework to send and receive messages over a new transport layer.

### 2.2. Reasoning Engine Extension (`IReasoningEngineExtension`)

- **Purpose**: To add new reasoning paradigms or models (e.g., a custom BDI implementation, a new LLM provider).
- **Interface Definition**: See [`reasoning_engine_extension_interface.md`](./interfaces/reasoning_engine_extension_interface.md)
- **Description**: In keeping with OpenMAS's reasoning-agnostic design, this extension point allows developers to create new "brains" for agents. The implementation provides the logic for processing inputs and making decisions.

### 2.3. Communication Pattern Extension (`ICommunicationPatternExtension`)

- **Purpose**: To define new high-level communication patterns (e.g., a specialized auction or voting pattern).
- **Interface Definition**: See [`communication_pattern_extension_interface.md`](./interfaces/communication_pattern_extension_interface.md)
- **Description**: This allows for the creation of new reusable interaction templates that go beyond the standard request-response or publish-subscribe patterns.

### 2.4. Topology Pattern Extension (`ITopologyPatternExtension`)

- **Purpose**: To define new algorithms for organizing agents into specific social structures (e.g., a dynamic scale-free network).
- **Interface Definition**: See [`topology_pattern_extension_interface.md`](./interfaces/topology_pattern_extension_interface.md)
- **Description**: This allows for the implementation of custom topology patterns that can be applied by the `Topology Manager`.

### 2.5. Knowledge Base Extension (`IKnowledgeBaseExtension`)

- **Purpose**: To integrate new types of data stores or knowledge representation systems (e.g., a vector database, a triple store).
- **Interface Definition**: See [`knowledge_base_extension_interface.md`](./interfaces/knowledge_base_extension_interface.md)
- **Description**: This allows agents to connect to and query different kinds of knowledge sources through the standardized `IKnowledgeBase` interface.
