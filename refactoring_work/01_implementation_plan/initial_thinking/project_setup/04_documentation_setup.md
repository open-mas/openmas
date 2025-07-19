# Documentation Setup for OpenMAS 0.3.0

## Task Overview
Set up the documentation system for OpenMAS 0.3.0, ensuring comprehensive coverage of the enhanced unified configuration schema, protocol support, and reasoning agnosticism, while preserving and updating valuable documentation from the 0.2.0 version.

## Tasks

1. Documentation Structure
   - Create directory structure for documentation
   - Set up MkDocs with appropriate theme and plugins
   - Configure auto-generation of API documentation
   - Preserve existing styling assets (images, overrides)

2. Preserve and Update Key Documentation
   - Preserve and update `why_openmas.md` (key positioning document)
   - Preserve and update `use_cases` directory and content
   - Preserve and update `core_concepts` directory and content
   - Ensure consistent styling and navigation

3. Core Documentation
   - Create overview and introduction documents
   - Document architectural principles, emphasizing reasoning agnosticism
   - Create installation and quickstart guides

4. Protocol Documentation
   - Create standardized documentation for all supported protocols (A2A, MCP, HTTP, MQTT, gRPC)
   - Document protocol-specific configuration options
   - Document agent card structures and capability definitions

5. Configuration Documentation
   - Document the unified configuration schema in detail
   - Create examples for different configuration scenarios
   - Document validation and loading mechanisms

6. Migration Guide
   - Create guide for migrating from 0.2.0 to 0.3.0
   - Document API changes and deprecations
   - Provide examples of updated configuration formats

7. New Guides
   - Create fresh guides based on 0.3.0 architecture
   - Include protocol-specific guides for all supported protocols
   - Create advanced usage examples

## Documentation Structure

```
docs/
├── index.md                # Home page
├── why_openmas.md          # Why choose OpenMAS (preserved and updated)
├── installation.md         # Installation guide
├── quickstart.md           # Getting started guide
├── core_concepts/          # Core concepts (preserved and updated)
│   ├── index.md            # Core concepts overview
│   ├── reasoning.md        # Reasoning approaches
│   ├── protocols.md        # Protocol support
│   └── ... (other preserved concepts)
├── use_cases/              # Use cases (preserved and updated)
│   ├── index.md            # Use cases overview
│   └── ... (use case documentation)
├── architecture/           # Architectural documentation
│   ├── index.md            # Architecture overview
│   ├── reasoning.md        # Reasoning agnosticism
│   ├── protocols.md        # Protocol support
│   └── extension.md        # Extension system
├── configuration/          # Configuration documentation
│   ├── index.md            # Configuration overview
│   ├── schema.md           # Unified schema
│   ├── environments.md     # Environment configuration
│   └── validation.md       # Validation mechanisms
├── protocols/              # Protocol-specific documentation
│   ├── index.md            # Protocol overview
│   ├── a2a/                # A2A protocol documentation
│   │   ├── index.md        # A2A overview
│   │   ├── agent_cards.md  # Agent card specification
│   │   ├── capabilities.md # Capability definitions
│   │   └── config.md       # Configuration options
│   ├── mcp/                # MCP protocol documentation
│   │   ├── index.md        # MCP overview
│   │   ├── server_mode.md  # Server mode configuration
│   │   ├── client_mode.md  # Client mode configuration
│   │   └── config.md       # Configuration options
│   ├── http/               # HTTP protocol documentation
│   ├── mqtt/               # MQTT protocol documentation
│   └── grpc/               # gRPC protocol documentation
├── agents/                 # Agent documentation
│   ├── index.md            # Agent overview
│   ├── capabilities.md     # Agent capabilities
│   ├── topologies.md       # Agent topologies
│   └── lifecycle.md        # Agent lifecycle
├── assets/                 # Asset documentation
│   ├── index.md            # Asset overview
│   ├── loaders.md          # Asset loaders
│   └── resources.md        # Resource mapping
├── security/               # Security documentation
│   ├── index.md            # Security overview
│   ├── authentication.md   # Authentication mechanisms
│   └── authorization.md    # Authorization controls
├── observability/          # Observability documentation
│   ├── index.md            # Observability overview
│   ├── logging.md          # Logging configuration
│   ├── metrics.md          # Metrics collection
│   └── tracing.md          # Distributed tracing
├── guides/                 # Guides (completely new)
│   ├── index.md            # Guides overview
│   ├── protocol_guides/    # Protocol-specific guides
│   └── advanced/           # Advanced usage guides
├── api/                    # API reference
│   ├── index.md            # API overview
│   └── ... (auto-generated)
├── migration/              # Migration guides
│   └── 0.2.0_to_0.3.0.md   # Migration from 0.2.0 to 0.3.0
├── examples/               # Usage examples
│   ├── index.md            # Examples overview
│   ├── simple_agent.md     # Simple agent example
│   ├── a2a_agents.md       # A2A protocol examples
│   ├── mcp_agents.md       # MCP protocol examples
│   └── hybrid_agents.md    # Hybrid protocol examples
├── images/                 # Image resources (preserved)
│   └── ... (images for documentation)
└── overrides/              # Theme overrides (preserved)
    └── ... (custom styling)
```

## MkDocs Configuration

```yaml
site_name: OpenMAS Documentation
site_description: Open Multi-Agent System Framework Documentation
site_url: https://docs.openmas.ai
repo_url: https://github.com/openmas-ai/openmas
repo_name: openmas-ai/openmas

theme:
  name: material
  palette:
    primary: indigo
    accent: indigo
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.annotate

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.inlinehilite
  - pymdownx.tabbed
  - pymdownx.critic
  - pymdownx.tasklist:
      custom_checkbox: true
  - admonition
  - toc:
      permalink: true

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          selection:
            docstring_style: google
          rendering:
            show_source: true
  - mermaid2

nav:
  - Home: index.md
  - Why OpenMAS: why_openmas.md
  - Getting Started:
    - Installation: installation.md
    - Quickstart: quickstart.md
  - Core Concepts: core_concepts/index.md
  - Use Cases: use_cases/index.md
  - Architecture:
    - Overview: architecture/index.md
    - Reasoning Agnosticism: architecture/reasoning.md
    - Protocol Support: architecture/protocols.md
    - Extension System: architecture/extension.md
  - Configuration:
    - Overview: configuration/index.md
    - Unified Schema: configuration/schema.md
    - Environments: configuration/environments.md
    - Validation: configuration/validation.md
  - Protocols:
    - Overview: protocols/index.md
    - A2A Protocol:
      - Overview: protocols/a2a/index.md
      - Agent Cards: protocols/a2a/agent_cards.md
      - Capabilities: protocols/a2a/capabilities.md
      - Configuration: protocols/a2a/config.md
    - MCP Protocol:
      - Overview: protocols/mcp/index.md
      - Server Mode: protocols/mcp/server_mode.md
      - Client Mode: protocols/mcp/client_mode.md
      - Configuration: protocols/mcp/config.md
    - HTTP Protocol: protocols/http.md
    - MQTT Protocol: protocols/mqtt.md
    - gRPC Protocol: protocols/grpc.md
  - Agents:
    - Overview: agents/index.md
    - Capabilities: agents/capabilities.md
    - Topologies: agents/topologies.md
    - Lifecycle: agents/lifecycle.md
  - Assets: 
    - Overview: assets/index.md
    - Loaders: assets/loaders.md
    - Resources: assets/resources.md
  - Security:
    - Overview: security/index.md
    - Authentication: security/authentication.md
    - Authorization: security/authorization.md
  - Observability:
    - Overview: observability/index.md
    - Logging: observability/logging.md
    - Metrics: observability/metrics.md
    - Tracing: observability/tracing.md
  - Guides:
    - Overview: guides/index.md
    - Protocol Guides: guides/protocol_guides/index.md
    - Advanced Guides: guides/advanced/index.md
  - API Reference: api/index.md
  - Migration:
    - 0.2.0 to 0.3.0: migration/0.2.0_to_0.3.0.md
  - Examples:
    - Overview: examples/index.md
    - Simple Agent: examples/simple_agent.md
    - A2A Agents: examples/a2a_agents.md
    - MCP Agents: examples/mcp_agents.md
    - Hybrid Agents: examples/hybrid_agents.md
```

## Tasks for Preserving Documentation Assets

### 1. Documentation Preservation and Migration
- Copy existing `docs/why_openmas.md` to new structure
- Review and update content to align with 0.3.0 architecture
- Preserve valuable context while ensuring alignment with new features

### 2. Core Concepts Preservation
- Copy and organize existing `docs/core_concepts` directory
- Update content to reflect 0.3.0 enhancements
- Ensure reasoning agnosticism is properly emphasized
- Align with protocol standardization

### 3. Use Cases Preservation
- Copy and organize existing `docs/use_cases` directory
- Update use cases to showcase 0.3.0 capabilities
- Add new use cases for protocol-specific features

### 4. Styling Assets Migration
- Copy `docs/images` directory to preserve visual assets
- Copy `docs/overrides` directory to maintain consistent styling
- Ensure all custom styling is properly applied to the new structure

## Success Criteria
- Complete documentation structure created
- MkDocs configured with appropriate plugins
- Core concepts and valuable content preserved and updated
- All styling elements preserved (images, overrides)
- Protocol-specific documentation standardized
- Configuration documentation aligned with unified schema
- Migration guide created
- Fresh guides developed for 0.3.0
- API reference auto-generation configured
