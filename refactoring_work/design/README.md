# OpenMAS Documentation

## Overview

OpenMAS is a reasoning-agnostic multi-agent framework designed to support multiple communication protocols and reasoning approaches. This documentation provides comprehensive information about OpenMAS v0.3.0, a clean implementation with no backward compatibility requirements for v0.2.0.

## Key Features

- **Reasoning Agnosticism**: Clear separation between communication infrastructure ("body") and reasoning approaches ("brain")
- **Multi-Protocol Support**: Native support for MCP, A2A, HTTP, MQTT, and gRPC protocols
- **Flexible Agent Architecture**: Support for various agent types and topologies
- **Configuration-Driven Design**: Unified configuration schema for all components
- **Enterprise Readiness**: Built-in support for security, observability, and deployment

## Documentation Structure

This documentation is organized into logical components, each with its own section:

### 1. Architecture

[**Architecture Documentation**](/01_architecture/README.md)

Core architectural concepts and design principles:

- [Architecture Overview](/01_architecture/architecture_overview.md) - High-level overview of the OpenMAS architecture
- [Reasoning Agnostic Design](/01_architecture/reasoning_agnostic_design.md) - Details on the body-brain separation
- [Multi-Protocol Design](/01_architecture/multi_protocol_design.md) - How OpenMAS supports multiple protocols
- [Components Summary](/01_architecture/components_summary.md) - Summary of all components in the system

### 2. Protocols

[**Protocol Documentation**](/02_protocols/README.md)

Communication protocol specifications and implementations:

- [MCP Protocol](/02_protocols/mcp/README.md) - Model Context Protocol for LLM communication
- [A2A Protocol](/02_protocols/a2a/README.md) - Agent-to-Agent Protocol for standardized agent communication
- [HTTP Protocol](/02_protocols/http/README.md) - Standard HTTP protocol implementation
- [MQTT Protocol](/02_protocols/mqtt/README.md) - MQTT protocol for IoT and event-driven scenarios
- [gRPC Protocol](/02_protocols/grpc/README.md) - gRPC for high-performance RPC communication

### 3. Configuration

[**Configuration Documentation**](/03_configuration/README.md)

Configuration system and schema definitions:

- [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md) - **DEFINITIVE SOURCE OF TRUTH** for all configuration
- [Agent Configuration](/03_configuration/agent_configuration_overview.md) - Agent-specific configuration overview
- [Configuration Validation](/03_configuration/configuration_validation.md) - Validation rules and processes
- [Schema Documentation](/03_configuration/schema/README.md) - Component-specific schema documentation

### 4. Agent Framework

[**Agent Framework Documentation**](/04_agents/README.md)

Agent system architecture and implementation:

- [Agent Framework Overview](/04_agents/agent_framework_overview.md) - Comprehensive overview of the agent framework
- [Agent Patterns](/04_agents/agent_patterns.md) - Design patterns for agent implementation
- [Agent Capabilities](/04_agents/agent_capabilities.md) - Agent capability definition and management
- [Agent Lifecycle](/04_agents/lifecycle/README.md) - Agent initialization, execution, and termination
- [Session Management](/04_agents/sessions/README.md) - Session creation, tracking, and persistence

### 5. Extensions

[**Extension Documentation**](/05_extensions/README.md)

Extension system and extensibility points:

- [Extension System Overview](/05_extensions/extension_system_overview.md) - Overview of the extension system
- [Extension Points](/05_extensions/extension_points/README.md) - Available extension points
- [Creating Extensions](/05_extensions/creating_extensions.md) - Guide to creating extensions
- [Extension Discovery](/05_extensions/extension_discovery.md) - How extensions are discovered and loaded

### 6. Communication Patterns

[**Communication Patterns Documentation**](/07_communication_patterns/README.md)

Standardized message exchange patterns:

- [Communication Patterns Overview](/07_communication_patterns/README.md) - Overview of communication patterns
- [Request-Response Pattern](/07_communication_patterns/patterns/request_response.md) - Basic request-response pattern
- [Sequential Thinking Pattern](/07_communication_patterns/patterns/sequential_thinking.md) - Pattern for step-by-step reasoning
- [Collaborative Workflow Pattern](/07_communication_patterns/patterns/collaborative_workflow.md) - Pattern for multi-agent collaboration

### 7. Topology

[**Topology Documentation**](/08_topology/README.md)

Agent organization and topology patterns:

- [Topology Architecture](/08_topology/architecture.md) - Overview of topology system architecture
- [Centralized Pattern](/08_topology/patterns/centralized.md) - Centralized topology pattern
- [Hierarchical Pattern](/08_topology/patterns/hierarchical.md) - Hierarchical topology pattern
- [Peer-to-Peer Pattern](/08_topology/patterns/peer_to_peer.md) - Peer-to-peer topology pattern
- [Mesh Pattern](/08_topology/patterns/mesh.md) - Mesh network topology pattern
- [Hybrid Pattern](/08_topology/patterns/hybrid.md) - Combined topology pattern

### 8. Deployment

[**Deployment Documentation**](/15_deployment/README.md)

- [Local Deployment](/15_deployment/local/README.md) - Local development and deployment
- [Containerization](/15_deployment/containerization/README.md) - Docker and container-based deployment
- [Kubernetes](/15_deployment/kubernetes/README.md) - Kubernetes deployment options
- [Cloud Deployment](/15_deployment/cloud/README.md) - Cloud-based deployment options

### 9. Testing

[**Testing Documentation**](/16_testing/README.md)

- [Testing Framework](/16_testing/framework/README.md) - Testing framework and approaches
- [Integration Testing](/16_testing/integration_testing/README.md) - Integration testing guidance
- [Unit Testing](/16_testing/unit_testing/README.md) - Unit testing patterns

### 10. Security

[**Security Documentation**](/17_security/README.md)

- [Security Architecture](/17_security/architecture/README.md) - Security design principles
- [Authentication](/17_security/authentication/README.md) - Authentication mechanisms
- [Communication Security](/17_security/communication/README.md) - Secure communication

### 11. Knowledge Representation

[**Knowledge Representation Documentation**](/09_knowledge_representation/README.md)

Knowledge representation and reasoning:

- [KR&R Overview](/09_knowledge_representation/krr_overview.md) - Overview of knowledge representation and reasoning
- [Knowledge Formalisms](/09_knowledge_representation/formalisms/README.md) - Knowledge representation formalisms
- [Reasoning Mechanisms](/09_knowledge_representation/reasoning/README.md) - Reasoning mechanisms

### 12. Asset Management

[**Asset Management Documentation**](/10_asset_management/README.md)

Asset management and versioning:

- [Asset Management Overview](/10_asset_management/asset_management_overview.md) - Overview of asset management
- [Asset Types](/10_asset_management/types/README.md) - Types of managed assets
- [Asset Versioning](/10_asset_management/versioning/README.md) - Asset versioning strategies

### 13. Prompt Management

[**Prompt Management Documentation**](/11_prompt_management/README.md)

Prompt management for LLM-based agents:

- [Prompt Management Overview](/11_prompt_management/prompt_management_overview.md) - Overview of prompt management
- [Prompt Templates](/11_prompt_management/templates/README.md) - Template system for prompts
- [Prompt Strategies](/11_prompt_management/strategies/README.md) - Prompt engineering strategies

### 14. Observability

[**Observability Documentation**](/12_observability/README.md)

Logging, metrics, and tracing:

- [Observability Overview](/12_observability/observability_overview.md) - Overview of observability system
- [Logging](/12_observability/logging/README.md) - Logging configuration and practices
- [Metrics](/12_observability/metrics/README.md) - Metrics collection and reporting
- [Tracing](/12_observability/tracing/README.md) - Distributed tracing capabilities

### 15. CLI Tools

[**CLI Tools Documentation**](/13_cli_tools/README.md)

Command-line interface and tools:

- [CLI Overview](/13_cli_tools/cli_overview.md) - OpenMAS command-line interface
- [CLI Commands](/13_cli_tools/commands/README.md) - Detailed command reference
- [Development Environment](/13_cli_tools/environment/README.md) - Development environment setup

### 16. Integrations

[**Integrations Documentation**](/14_integrations/README.md)

External service integrations:

- [Integrations Overview](/14_integrations/integrations_overview.md) - Overview of external integrations
- [Service Integrations](/14_integrations/services/README.md) - External service integrations
- [Framework Integrations](/14_integrations/frameworks/README.md) - Framework interoperability

## Key Concepts

### Reasoning Agnosticism

OpenMAS maintains a clear separation between the communication infrastructure ("body") and reasoning approaches ("brain"), allowing:

1. **Multiple Reasoning Approaches**:
   - Rule-based reasoning
   - BDI (Belief-Desire-Intention) architecture
   - Knowledge Representation & Reasoning (KR&R)
   - LLM-based reasoning
   - Hybrid reasoning approaches

2. **Protocol Independence**:
   - Communication protocols operate independently of reasoning approach
   - Any agent can use any protocol without changing its reasoning implementation

### Protocol Support

OpenMAS natively supports multiple communication protocols:

1. **MCP (Model Context Protocol)**:
   - Protocol for communication with language models
   - Supports tools registration and invocation
   - Streaming capabilities

2. **A2A (Agent-to-Agent Protocol)**:
   - Standardized protocol for agent interoperability
   - Agent card discovery mechanism
   - Capability advertisement and invocation

3. **Standard Protocols**:
   - HTTP for RESTful communication
   - MQTT for IoT and event-driven scenarios
   - gRPC for high-performance RPC

### Configuration System

The configuration system follows a structured approach:

1. **Single Source of Truth**:
   - Unified configuration schema for all components
   - Component-specific schemas reference the unified schema
   - Consistent validation across all components

2. **Configuration-Driven Design**:
   - All components configured through a consistent schema
   - Environment-specific configuration
   - Strong validation with helpful error messages

## Getting Started

To get started with OpenMAS, see the [Quick Start Guide](/15_deployment/quick_start/README.md).

For developer tools and CLI documentation, see the [CLI Tools section](/13_cli_tools/README.md).

## Key References

The following key documents should be consulted when implementing this plan:

1. [Documentation Structure](/documentation_structure.md) - Standards for documentation organization
2. [Architecture Overview](/01_architecture/architecture_overview.md) - Comprehensive architecture overview
3. [Components Summary](/01_architecture/components_summary.md) - Detailed component descriptions
4. [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md) - Configuration structures
5. [Component Interoperability](/01_architecture/component_interoperability/README.md) - All Components Interoperability
