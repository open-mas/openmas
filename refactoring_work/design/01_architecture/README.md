# OpenMAS Architecture Documentation

This directory contains cross-component architecture documentation for OpenMAS 0.3.0. It focuses on high-level principles and how components integrate together.

## Core Architecture Documents

- [Architecture Overview](./architecture_overview.md) - High-level architecture and key principles
- [Components Summary](./components_summary.md) - Comprehensive list of all components
- [Multi-Protocol Design](./multi_protocol_design.md) - How OpenMAS supports multiple protocols directly
- [Reasoning-Agnostic Design](./reasoning_agnostic_design.md) - Separation of agent "body" and "brain"
- [Internal Message Format Standard](./internal_message_format_standard.md) - Standardized message representation for protocol and reasoning agnosticism
- [Communication Patterns Design](./communication_patterns_design.md) - High-level design of communication patterns
- [Topology-Pattern-Communicator Integration](./topology_pattern_communicator.md) - How key components integrate
- [OpenMAS vs. Other Frameworks](./openmas_vs_others.md) - Comparative analysis
- [Architectural Patterns](./architectural_patterns.md) - Common design patterns used throughout OpenMAS
- [Runtime Architecture](./runtime_architecture.md) - Execution model and runtime behavior
- [Component Interoperability](./component_interoperability/README.md) - Comprehensive documentation of component interactions

## Component Documentation Structure

Detailed documentation for individual components is organized in the following directories:

| Component | Documentation Location |
|-----------|------------------------|
| **Agent Framework** | `/04_agents/` |
| **Knowledge & Reasoning** | `/09_knowledge_representation/` |
| **Communication System** | `/02_protocols/` |
| **Configuration System** | `/03_configuration/` |
| **Topology System** | `/08_topology/` |
| **Communication Patterns** | `/07_communication_patterns/` |
| **Extension System** | `/05_extensions/` |
| **Asset Management** | `/10_asset_management/` |
| **Prompt Management** | `/11_prompt_management/` |
| **Session Management** | `/04_agents/sessions/` |
| **Observability System** | `/12_observability/` |
| **CLI Tools** | `/13_cli_tools/` |
| **External Integrations** | `/14_integrations/` |

## File Naming Conventions

Consistent file naming is used throughout the documentation:

- `design_*.md` - Detailed design documents
- `pattern_*.md` - Pattern documentation
- `guide_*.md` - Implementation guides

## Key Architectural Differentiators

1. **Reasoning Agnosticism**: Complete separation between communication infrastructure ("body") and reasoning approaches ("brain"), enabling support for rule-based, BDI, LLM-based, and hybrid reasoning.

2. **Direct Multi-Protocol Support**: Native support for multiple protocols (MCP, A2A, HTTP, MQTT, gRPC) without protocol bridging, allowing agents to communicate through multiple protocols simultaneously.

3. **Unified Configuration Schema**: Single source of truth for all configuration in `/03_configuration/unified_configuration_schema.md`.

This architecture documentation provides the foundation for understanding the OpenMAS framework design.
