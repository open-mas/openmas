# Architecture Overview for OpenMAS v0.3.0

This document provides a comprehensive architecture overview for the refactored OpenMAS framework (v0.3.0), detailing the core components, their interactions, and the fundamental design principles that enable OpenMAS's unique capabilities.

## Core Architecture Principles

The refactored OpenMAS architecture is guided by these fundamental principles:

1. **Reasoning Agnosticism** - Clear separation between agent "body" (communication infrastructure) and "brain" (reasoning approach)
2. **Modularity** - Well-defined interfaces between components with minimal dependencies
3. **Protocol Agnosticism** - Consistent interfaces across multiple communication protocols 
4. **Topology Flexibility** - Support for various agent organization patterns independent of protocols
5. **Pattern-Based Communication** - Standardized communication patterns across different topologies
6. **Configuration-Driven** - Schema-first design with behavior determined by structured configuration defined in the [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md)
7. **Enterprise Readiness** - Production-grade security, monitoring, and scalability
8. **Extensibility** - Rich extension points with discovery mechanisms
9. **Developer Experience** - Clear conventions and tooling for productivity

## High-Level Component Architecture

The architecture of OpenMAS v0.3.0 consists of several integrated components designed to provide a flexible and powerful framework for agent-based systems. For a visual representation of this architecture, please refer to the [Architecture Diagrams](./architecture_overview_diagrams.md) document, which contains detailed Mermaid.js diagrams showing:

- The complete high-level component architecture
- The relationship between the KR&R System and Reasoning Engines
- Protocol integration architecture
- Topology and communication patterns
- Security architecture
- Observability architecture

> **Important**: A key aspect of the OpenMAS architecture is the clear separation between the **KR&R System** (which provides knowledge management services) and **Reasoning Engines** (which implement the agent's decision-making logic). This separation is fundamental to OpenMAS's reasoning agnostic design.

## Key Components

### Agent Framework

The agent framework provides the foundation for building agents:

- **Agent Lifecycle** - Standardized agent lifecycle management (setup, run, shutdown)
- **Message Handling** - Consistent message processing across protocols
- **Capability Registration** - Easy registration of agent capabilities
- **Topology Integration** - Support for defining and managing agent relationships and organization
- **Pattern Support** - Implementation of standardized communication patterns
- **Role Integration** - Support for role-based agent design
- **State Management** - Persistent agent state handling

### Knowledge Representation & Reasoning (KR&R) System

The KR&R System is a distinct architectural component responsible for **managing and providing access to structured knowledge**. It is *not* a reasoning approach itself but rather an enabling system that various `ReasoningEngines` can leverage:

- **Multiple Knowledge Representations** - Support for symbolic, graph-based, vector, and probabilistic knowledge representation formats
- **Knowledge Base Management** - Tools for knowledge storage, retrieval, update, and persistence
- **Standardized Interfaces** - The `IKnowledgeBase` interface allowing reasoning engines to interact with knowledge regardless of underlying representation
- **Integration Layer** - Connectors to external knowledge sources and systems
- **Knowledge Registry** - Central registry of available knowledge bases
- **Type-Safe Knowledge Access** - Strongly-typed access to knowledge based on representation type

### Configuration System

The configuration system provides a unified approach to configuring all aspects of the framework:

- **Schema-First Design** - Pydantic-based validation models define the configuration contract
- **Environment Integration** - Support for environment variables and profiles
- **Layered Configuration** - Clear precedence rules for configuration inheritance
- **Validation** - Strong validation with helpful error messages

### Asset Management

The asset management subsystem handles the acquisition, verification, and caching of various assets:

- **Model Files** - Management of local models (Gemma, etc.)
- **Embeddings** - Support for embedding models and vector stores
- **Prompt Templates** - Version-controlled prompt templates
- **Source Downloaders** - Plugins for different asset sources (HTTP, HuggingFace, local)
- **Asset Tracking** - Provenance tracking for all assets
- **Versioning** - Asset version control and rollback capabilities
- **Type Safety** - Strongly-typed asset references

### Protocol Layer

The protocol layer provides a unified interface for different communication protocols:

- **Protocol Agnosticism** - Common interface across all protocols
- **Protocol Adapters** - Translators for different protocols
- **Standard Internal Message Format** - Common message representation for all protocols as defined in [internal_message_format_standard.md](./internal_message_format_standard.md)
- **Message Routing** - Intelligent routing based on capabilities
- **Multi-Protocol Support** - Direct support for multiple protocols within a single agent
- **Security** - Authentication and authorization for all protocols
- **Error Handling** - Standardized error handling across protocols
- **Capability Discovery** - Protocol-specific capability advertisement

### Prompt Management

The prompt management subsystem handles the creation, validation, and caching of prompts:

- **Prompt Templates** - Version-controlled prompt templates
- **Prompt Validation** - Validation of prompts against schema
- **Prompt Caching** - Caching of prompts for performance

### Session Management

The session management subsystem provides persistent conversation and state management:

- **Context Preservation** - Maintaining conversation history and context
- **State Persistence** - Storage and retrieval of agent state
- **History Management** - Tracking and querying interaction history
- **Recovery Mechanisms** - Resuming sessions after interruptions
- **Multi-Agent Coordination** - Managing sessions across multiple agents
- **Memory Integration** - Connecting to knowledge bases and memories

### Extension System

The extension system enables modular and discoverable components:

- **Discovery Mechanism** - Runtime discovery of extensions
- **Lazy Loading** - Loading extensions only when needed
- **Extension Points** - Well-defined integration points
- **Package Management** - Installation and updates of extensions
- **Registry Integration** - Sharing and finding community extensions
- **Versioning** - Compatibility checks and dependency management

### Deployment Management

The deployment management subsystem provides enterprise-ready deployment options while maintaining OpenMAS's reasoning-agnostic architecture and multi-protocol capabilities:

- **Reasoning-Agnostic Deployment** - Deployment configurations that maintain body-brain separation
- **Multi-Protocol Support** - Deployment for all supported protocols (A2A, MCP, HTTP, MQTT, gRPC)
- **Kubernetes Support** - Complete K8s manifests and operators with protocol-specific optimizations
- **Docker Support** - Multi-stage container configurations for various reasoning engines
- **Cloud Deployments** - AWS, Azure, and GCP deployment options with reasoning-specific considerations
- **Local Development** - Streamlined local deployment for rapid development
- **CLI Integration** - Seamless integration with CLI tools for automated deployment workflows
- **Environment Management** - Different settings per environment with protocol-specific configurations
- **Security Controls** - Authentication and authorization across protocols
- **Monitoring Integration** - Health checks and observability that separates communication from reasoning

### CLI Tools

The CLI tools provide developer productivity enhancements that fully support OpenMAS's reasoning-agnostic architecture and multi-protocol capabilities:

- **Project Scaffolding** - Quick creation of new projects with protocol and reasoning engine options
- **Configuration Validation** - Schema verification and validation for multi-protocol capability mappings
- **Command Management** - Commands for agent lifecycle, deployment, and configuration with protocol-specific and reasoning-specific options
- **Multi-Protocol Support** - Configuration and validation for all supported protocols (A2A, MCP, HTTP, MQTT, gRPC)
- **Reasoning Engine Integration** - Support for various reasoning approaches (rule-based, BDI, LLM, hybrid, knowledge graph)
- **Deployment Utilities** - Local, containerized, and cloud deployment tools that maintain body-brain separation
- **Development Workflows** - Protocol-specific and reasoning-specific development workflows
- **Extension Management** - Installing and updating extensions across protocols and reasoning engines
- **Integration with Deployment** - Seamless workflow from development to deployment with maintained reasoning-agnostic principles

## Reasoning Agnosticism: A Core Differentiator

What makes OpenMAS unique is its reasoning agnosticism - the clear separation between agent communication ("body") and reasoning approaches ("brain"). This architecture allows OpenMAS to support multiple reasoning paradigms (detailed component interactions are documented in the [Agent Framework ↔ KR&R](./component_interoperability/interactions/agent_framework_krr.md) interface):

1. **Rule-based reasoning** - Simple, deterministic decision making
2. **BDI (Belief-Desire-Intention)** - Cognitive agent architecture for deliberative reasoning
3. **Knowledge Representation and Reasoning (KR&R)** - Supporting multiple formalisms:
   - Symbolic representations (logic, rules)
   - Graph-based knowledge (conceptual, semantic)
   - Probabilistic knowledge (Bayesian networks)
   - Reasoning mechanisms (deductive, inductive, abductive, temporal, spatial)
4. **LLM-based reasoning** - Leveraging language models for complex reasoning
5. **Hybrid approaches** - Combining multiple paradigms for optimal results

This flexibility enables OpenMAS to bridge classical AI approaches with modern neural methods, providing the right reasoning tool for each task while maintaining a consistent agent interface.

## Integration Architecture

The OpenMAS components are designed for seamless integration through:

1. **Configuration-Driven Assembly** - Components are wired together through configuration
2. **Dependency Injection** - Clean component relationships without tight coupling
3. **Event-Driven Communication** - Message-based component interaction
4. **Extension Points** - Well-defined places to plug in custom behavior
5. **Protocol Adapters** - Translating between different communication mechanisms

This integration architecture ensures that OpenMAS remains modular while allowing components to work together effectively.

## Cross-Cutting Concerns

Several cross-cutting concerns are addressed across all components:

1. **Security** - Authentication, authorization, and secure communication
2. **Observability** - Logging, metrics, and tracing across all components
3. **Error Handling** - Consistent error management and recovery
4. **Performance Optimization** - Caching, lazy loading, and resource management
5. **Documentation** - Auto-generated docs and consistent developer guides

## Component Interoperability

The OpenMAS architecture is built on well-defined component interactions and boundaries. Comprehensive documentation of these interactions is available in the [Component Interoperability](./component_interoperability/README.md) documentation and the [Comprehensive Component Interactions](./component_interoperability/component_interactions.md) document, which serves as the single source of truth for all component interaction information.

### Key Interaction Documentation

- **[Comprehensive Component Interactions](./component_interoperability/component_interactions.md)** - Detailed overview of all component interactions, boundaries, and workflows
- **[Component Matrix](./component_interoperability/component_matrix.md)** - Overview of all component relationships
- **[Workflow Diagrams](./component_interoperability/workflow_diagrams.md)** - End-to-end workflows across components
- **[Component Boundaries](./component_interoperability/component_boundaries.md)** - Clear definition of responsibilities

### Core Component Interactions

- **Agent Framework Interactions** - Documented interfaces with Protocol Layer, KR&R, Topology, etc.
- **Configuration System Interactions** - How configuration flows to all components
- **Protocol Layer Interactions** - How protocols interact with other components

This comprehensive documentation ensures clear component boundaries, well-defined interfaces, and maintainable architecture.

## Conclusion

The OpenMAS architecture represents a significant advancement in multi-agent systems by:

1. Providing reasoning agnosticism that bridges classical and neural AI approaches
2. Supporting multiple communication protocols (MCP, A2A) with a consistent interface
3. Offering enterprise-grade deployment and security features
4. Enabling community-driven extensibility through a robust extension system
5. Delivering schema-first development that drives implementation quality

This architecture positions OpenMAS as a flexible, powerful framework for building sophisticated multi-agent systems across a wide range of use cases, from simple automation to complex cognitive agents.

## Component Interactions

The components interact through well-defined interfaces:

1. **Configuration → All Components** - Configuration flows to all components
2. **Asset Management → Agents** - Agents request assets from the asset manager
3. **Protocol Layer → Agents** - Agents communicate through the protocol layer
4. **Deployment → All Components** - Deployment configures how components run
5. **CLI → All Components** - CLI provides management interface to all components

## Extensibility Points

The architecture provides several key extension points:

1. **Protocol Adapters** - Add support for new communication protocols
2. **Asset Sources** - Add new sources for asset acquisition
3. **Deployment Targets** - Support for additional deployment environments
4. **Agent Capabilities** - Easy addition of new agent capabilities
5. **Tool Integrations** - Integration with external tools and services

## Configuration-Driven Architecture

OpenMAS follows a configuration-driven architecture where component behavior is determined by structured configuration defined in the [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md). This approach has several key advantages:

1. **Declarative System Definition** - Systems are defined by what they should do rather than how they do it
2. **Runtime Flexibility** - Components can adapt behavior without code changes
3. **Validation-First Approach** - Configuration is validated against schemas before use
4. **Environment Adaptability** - Configuration can vary by environment (dev, test, prod)
5. **Consistent Interface** - Components interact through standardized configuration patterns

All components follow the unified configuration schema, which provides:
- Schema definitions for [agent configurations](/03_configuration/schema/agents.md)
- Schema definitions for [extension configurations](/03_configuration/schema/extensions.md)
- Schema definitions for [protocol configurations](/03_configuration/schema/protocols.md)
- Schema definitions for [integration configurations](/03_configuration/schema/integrations.md)

For example, an agent's capabilities, protocols, and reasoning approach are all configured through the unified schema:

```yaml
agents:
  example_agent:
    class: "openmas.agents.BaseAgent"
    reasoning:
      type: "llm"
      model: "example-llm"
    protocols:
      - type: "mcp-streamable"
        options:
          server_mode: true
      - type: "a2a-http"
        options:
          client_mode: true
```

This configuration-driven approach ensures OpenMAS maintains its reasoning agnosticism while providing consistent interfaces across all components.

## Implementation Approach

The implementation of this architecture will follow a phased approach:

1. **Core Components First** - Implement configuration and asset management
2. **Protocol Layer Next** - Standardize the protocol interfaces
3. **Deployment Options** - Add support for different deployment options
4. **Refinement** - Iterate based on testing and feedback

This architecture provides a solid foundation for OpenMAS v0.3.0, addressing the current limitations while enabling new capabilities and use cases.
