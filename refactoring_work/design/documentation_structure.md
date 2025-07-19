# OpenMAS Documentation Structure Guide

## Overview

This document provides a comprehensive guide to the OpenMAS documentation structure. It defines the organization of documentation across all major components of the OpenMAS framework and serves as the authoritative reference for documentation placement.

## Core Organization Principles

The OpenMAS documentation follows these organizational principles:

1. **Component-Based Structure** - Documentation is organized by major system components
2. **Separation of Concerns** - Clear separation between architecture, configuration, implementation, etc.
3. **Progressive Disclosure** - High-level overviews lead to detailed documentation
4. **Cross-Referencing** - Related documents link to each other for easy navigation
5. **Consistency** - Similar components have similar documentation structures

## Top-Level Structure

The documentation is organized into these top-level directories, each focusing on a specific aspect of the system:

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `01_architecture/` | Core architectural concepts | Design principles, component relationships, high-level structure |
| `02_protocols/` | Protocol documentation | Protocol-specific documentation for all supported protocols |
| `03_configuration/` | Configuration system | Configuration schemas, validation, environment integration |
| `04_agents/` | Agent framework | Agent lifecycle, capabilities, state management |
| `05_extensions/` | Extension system | Extension points, discovery mechanisms, package management |
| `06_*` | Reserved for future use | Reserved directory prefix for future expansion |
| `07_communication_patterns/` | Communication patterns | Pattern specifications, examples, adaptations |
| `08_topology/` | Agent topologies | Topology patterns, role definitions, relationship management |
| `09_knowledge_representation/` | KR&R module | Knowledge representations, reasoning approaches |
| `10_asset_management/` | Asset management | Model files, embeddings, asset versioning |
| `11_prompt_management/` | Prompt management | Templates, context management, versioning |
| `12_observability/` | Observability system | Logging, metrics, tracing, monitoring |
| `13_cli_tools/` | CLI tools | Command line tools, installation, configuration, development workflows |
| `14_integrations/` | External integrations | Service connections, framework interoperability, API integrations |
| `15_deployment/` | Deployment | Deployment options, environments, containerization, cloud platforms |
| `16_testing/` | Testing | Testing framework, patterns, integration testing, performance testing |
| `17_security/` | Security | Security architecture, authentication, authorization, data protection |

## Detailed Directory Structure

Each top-level directory has a consistent internal structure:

```
/XX_component_name/
├── README.md                 # Component overview, navigation, key concepts
├── subcomponent1/            # Major subcomponent directory
│   ├── README.md             # Subcomponent overview
│   └── detailed_docs.md      # Detailed documentation
├── subcomponent2/            # Another subcomponent directory
├── design_principles.md      # Core design principles (if applicable)
└── integration.md            # Integration with other components
```

### Architecture Directory Structure

The architecture directory follows a specific structure for component-specific architectural documentation:

```
/01_architecture/
├── README.md                   # Architecture documentation overview
├── architecture_overview.md    # High-level system architecture
├── component_name_design.md    # Component-specific architectural design
└── system_wide_concept.md      # System-wide architectural concepts
```

For component-specific architecture documentation, use the naming convention `component_name_design.md` (e.g., `communication_patterns_design.md`, `multi_protocol_design.md`).

Component-level implementation details should NOT be included in architecture documents. Implementation details belong in their respective component directories (e.g., `/07_communication_patterns/`).

## Document Types and Placement Guidelines

### 1. Architecture Documentation

**Location**: `01_architecture/`

Architecture documents describe high-level design principles, component relationships, and system structure. They focus on "what" and "why" rather than "how".

Types of documents that belong here:
- Core design principles (`component_name_design.md`)
- Component relationship diagrams
- System boundaries and interfaces
- Architectural decisions and rationales

Examples: 
- `01_architecture/reasoning_agnostic_design.md`
- `01_architecture/communication_patterns_design.md`
- `01_architecture/multi_protocol_design.md`

Do NOT create component subdirectories inside the architecture directory. All component-specific architectural documents should be direct children of the `01_architecture/` directory using the `component_name_design.md` naming convention.

### 2. Protocol Documentation

**Location**: `02_protocols/`

Protocol documents describe specific communication protocols supported by OpenMAS. They focus on the protocol's structure, capabilities, and OpenMAS's implementation.

Types of documents that belong here:
- Protocol specifications
- Protocol-specific features
- OpenMAS adaptations of standard protocols
- Protocol compliance information

Example: `02_protocols/a2a/specification.md`

### 3. Configuration Documentation

**Location**: `03_configuration/`

Configuration documents describe the configuration system, schemas, and options for all components.

Types of documents that belong here:
- Schema documentation
- Configuration options
- Environment variable integration
- Validation rules

#### Configuration Directory Structure

The configuration documentation follows this specific structure:

```
/03_configuration/
├── README.md                         # Overview of configuration system
├── unified_configuration_schema.md   # The definitive, complete schema (single source of truth)
├── configuration_validation.md       # Validation rules and processes
├── environment_variables.md          # Environment variable integration
├── complex_configuration_examples.md # End-to-end configuration examples
├── security_configuration.md         # Security-specific configuration
└── schema/                           # Component-specific schema documentation
    ├── README.md                     # Schema directory overview
    ├── agents.md                     # Agent-specific schema
    ├── protocols.md                  # Protocol-specific schema
    ├── extensions.md                 # Extension-specific schema
    ├── integrations.md               # Integration-specific schema
    ├── communication_patterns.md      # Communication patterns schema
    └── observability.md              # Observability-specific schema
```

Important principles:
- `unified_configuration_schema.md` is the **single source of truth** for all configuration
- Component schemas in the `/schema/` directory reference the unified schema without duplication
- Each component schema focuses on component-specific documentation and examples

Example: `03_configuration/patterns/communication_patterns_config.md`

### 4. Agent Documentation

**Location**: `04_agents/`

Agent documents describe the agent framework, lifecycle, capabilities, and state management.

Types of documents that belong here:
- Agent lifecycle
- Agent capabilities
- State management
- Session handling

Example: `04_agents/lifecycle/agent_lifecycle.md`

### 5. Extension Documentation

**Location**: `05_extensions/`

Extension documents describe the extension system, extension points, and package management.

Types of documents that belong here:
- Extension point specifications
- Extension discovery mechanisms
- Package management
- Extension development guides

Example: `05_extensions/extension_points/creating_extensions.md`

### 6. Implementation Documentation

**Location**: Distributed across `/15_deployment/`, `/16_testing/`, and `/17_security/` directories

Implementation documents describe internal implementation details, deployment options, and testing approaches.

Types of documents that belong here:
- Deployment guides
- Testing strategies
- Internal structures
- Performance considerations

Example: `/15_deployment/kubernetes/k8s_manifests.md`

### 7. Communication Pattern Documentation

**Location**: `07_communication_patterns/`

Communication pattern documents describe standardized message exchange methods, their implementations, and examples.

Types of documents that belong here:
- Pattern specifications
- Pattern examples
- Protocol adaptations
- Pattern extension guidelines
- Pattern versioning

Example: `07_communication_patterns/patterns/request_response.md`

### 8. Topology Documentation

**Location**: `08_topology/`

Topology documents describe agent organization patterns, roles, and relationships.

Types of documents that belong here:
- Topology pattern specifications
- Role definitions
- Relationship management
- Topology configuration

Example: `08_topology/centralized/hub_spoke_topology.md`

### 9. Knowledge Representation Documentation

**Location**: `09_knowledge_representation/`

Knowledge representation documents describe the KR&R module, knowledge representations, and reasoning approaches.

Types of documents that belong here:
- Knowledge representation formats
- Reasoning approach specifications
- Knowledge management
- Reasoning integration

Example: `09_knowledge_representation/knowledge_access_interfaces/interfaces.md`

### 10. Asset Management Documentation

**Location**: `10_asset_management/`

Asset management documents describe the handling of models, embeddings, and other assets.

Types of documents that belong here:
- Model file management
- Embedding handling
- Asset versioning
- Protocol-specific asset adaptations

Example: `10_asset_management/model_files/model_loading.md`

### 11. Prompt Management Documentation

**Location**: `11_prompt_management/`

Prompt management documents describe template handling, context management, and versioning.

Types of documents that belong here:
- Template specifications
- Context management
- Prompt versioning
- Template libraries

Example: `11_prompt_management/templates/template_structure.md`

### 12. Observability Documentation

**Location**: `12_observability/`

Observability documents describe logging, metrics, tracing, and monitoring.

Types of documents that belong here:
- Logging system
- Metrics collection
- Distributed tracing
- Monitoring integration

Example: `12_observability/tracing/distributed_tracing.md`

### 13. CLI Tools Documentation

**Location**: `13_cli_tools/`

CLI tools documentation describes command-line utilities that support OpenMAS's reasoning-agnostic architecture and multi-protocol capabilities.

Types of documents that belong here:
- Command reference documentation (init, run, config, validate, deploy)
- Protocol-specific command options
- Reasoning engine integration guides
- Multi-protocol capability configuration
- Project scaffolding with protocol and reasoning engine options
- Development workflows for various reasoning approaches
- CLI installation and configuration
- Extension management across protocols

Example: `13_cli_tools/commands/deploy.md`

### 14. Integration Documentation

**Location**: `14_integrations/`

Integration documents describe external service connections, framework interoperability, and API integrations.

Types of documents that belong here:
- Integration design principles
- Configuration schemas for integrations
- Implementation guides
- Protocol adaptations
- Service-specific integration details
- Framework interoperability specifications

Example: `14_integrations/design/protocol_adaptations.md`

### 15. Deployment Documentation

**Location**: `15_deployment/`

Deployment documents describe the options and processes for deploying OpenMAS agents and systems across various environments, while maintaining the reasoning-agnostic architecture and multi-protocol capabilities.

Types of documents that belong here:
- Local deployment guides with protocol-specific configurations
- Containerization documentation for various reasoning engines
- Kubernetes deployment with multi-protocol support
- Cloud platform deployments (AWS, Azure, GCP) with reasoning-agnostic configurations
- Deployment configuration templates for different protocols and reasoning approaches
- Quick start deployment guides for common multi-protocol scenarios
- CLI tools integration examples for automated deployment workflows
- Deployment patterns that maintain body-brain separation
- Multi-region deployment with protocol-specific optimizations
- Protocol-specific deployment considerations (A2A, MCP, HTTP, MQTT, gRPC)
- Reasoning-specific deployment options (rule-based, BDI, LLM, hybrid, knowledge graph)

Example: `15_deployment/cloud/aws.md`

### 16. Testing Documentation

**Location**: `16_testing/`

Testing documents describe the framework, patterns, and processes for testing OpenMAS components, with special attention to testing multi-protocol capabilities and reasoning-agnostic architecture.

Types of documents that belong here:
- Testing framework documentation
- Unit testing patterns
- Integration testing approaches
- Protocol-specific testing
- Performance testing
- CI/CD integration

Example: `16_testing/integration_testing/multi_agent_testing.md`

### 17. Security Documentation

**Location**: `17_security/`

Security documents describe the security architecture, mechanisms, and best practices for OpenMAS, ensuring secure communication across protocols and reasoning approaches.

Types of documents that belong here:
- Security architecture
- Authentication mechanisms
- Authorization models
- Data protection
- Communication security
- Security best practices

Example: `17_security/communication/protocol_security.md`

## Cross-Component Documentation

Some documentation spans multiple components. These should be placed in the most relevant directory and cross-referenced from other related directories.

Example: Communication patterns and topologies are tightly related. The primary documentation lives in their respective directories, but each should reference the other.

## README.md Standards

Each directory should have a README.md file that:

1. Provides an overview of the component/subcomponent
2. Lists and links to all contained documents
3. References related documentation in other directories
4. Explains key concepts and terminology
5. Gives guidance on when to use different subcomponents

## Documentation Naming Conventions

1. Use lowercase with underscores for file names: `agent_lifecycle.md`
2. Use descriptive names that indicate the content: `request_response_pattern.md`
3. For multi-part documents, use suffixes: `pipeline_part1.md`
4. For README files, use `README.md` (capitalized)

## Version-Specific Documentation

When documentation differs across versions, use one of these approaches:

1. Include version information in the document title: `a2a_protocol_v1.md`
2. Create version-specific directories: `v1/`, `v2/`
3. Include version tabs within the document (for HTML/web documentation)

## Documentation Migration Process

When moving documentation from one location to another:

1. Create the document in the new location
2. Update all references to point to the new location
3. Add a redirect notice to the old location
4. Remove the old document only after confirming all references are updated

## Expanding the Documentation Structure

If new components are added to OpenMAS, they should:

1. Follow the existing directory structure patterns
2. Be assigned a number following the current sequence
3. Include all standard document types (README, design principles, etc.)
4. Be cross-referenced from related components

## Conclusion

This document serves as the authoritative guide for OpenMAS documentation structure. By following these guidelines, we ensure documentation remains organized, discoverable, and consistent as the system grows. All contributors should reference this document when adding or modifying documentation to maintain structural integrity.

For questions or proposed changes to the structure, please submit an issue or pull request addressing the documentation structure specifically.
