# OpenMAS Configuration System

## Overview

The OpenMAS Configuration System provides a unified, schema-driven approach to configuring all aspects of the framework. It serves as the cornerstone for OpenMAS's configuration-driven design principle, enabling consistent configuration across all components while maintaining reasoning agnosticism and protocol independence.

## Key Capabilities

The Configuration System offers these core capabilities:

1. **Unified Schema** - A single source of truth for all configuration
2. **Schema Validation** - Robust validation with helpful error messages
3. **Layered Configuration** - Clear precedence rules for configuration inheritance
4. **Environment Integration** - Support for environment variables and profiles
5. **Documentation Generation** - Self-documenting schema for developer reference

## Documentation Structure

This directory contains comprehensive documentation on the OpenMAS Configuration System:

| Document | Description |
|----------|-------------|
| [Unified Configuration Schema](./unified_configuration_schema.md) | **DEFINITIVE SOURCE OF TRUTH** for all configuration schema definitions |
| [Agent Configuration Overview](./agent_configuration_overview.md) | Comprehensive overview of agent configuration |
| [Configuration Validation](./configuration_validation.md) | Validation rules and processes |
| [Environment Variables](./environment_variables.md) | Environment variable integration |
| [Complex Configuration Examples](./complex_configuration_examples.md) | End-to-end configuration examples |
| [Security Configuration](./security_configuration.md) | Security-specific configuration |

### Component-Specific Documentation

The `/schema/` directory contains **documentation-only** resources that explain and provide examples for sections of the unified schema:

| Document | Description |
|----------|-------------|
| [Schema Directory README](./schema/README.md) | Overview of component-specific documentation |
| [Agent Configuration](./schema/agents.md) | Documentation and examples for agent-specific sections of the unified schema |
| [Protocol Configuration](./schema/protocols.md) | Documentation and examples for protocol-specific sections of the unified schema |
| [Protocols Reference](./schema/protocols_reference.md) | Additional protocol reference documentation |
| [Extension Configuration](./schema/extensions.md) | Documentation and examples for extension-specific sections of the unified schema |
| [Integration Configuration](./schema/integrations.md) | Documentation and examples for integration-specific sections of the unified schema |
| [Communication Patterns Configuration](./schema/communication_patterns.md) | Documentation and examples for communication pattern sections of the unified schema |
| [Security Configuration](./schema/security.md) | Documentation and examples for security-specific sections of the unified schema |

**IMPORTANT**: The component-specific files in `/schema/` do NOT define any schema structures. They ONLY document, explain, and provide examples for sections already defined in the `unified_configuration_schema.md`, which is the exclusive source of truth for all configuration schema definitions.

## Configuration Hierarchy

OpenMAS resolves configuration through a clear hierarchy of precedence:

1. **Command Line Arguments** (highest precedence)
2. **Environment Variables**
3. **Environment-Specific Configuration**
4. **Agent-Specific Configuration**
5. **Global Defaults**
6. **Framework Defaults** (lowest precedence)

This allows for flexibility while maintaining consistent defaults and overrides.

## Integration with Other Components

The Configuration System integrates with several other OpenMAS components:

1. **Agent Framework** - Provides configuration for agent capabilities, reasoning, and lifecycle
2. **Protocol Layer** - Configures protocol adaptations and communication settings
3. **Extension System** - Manages extension discovery and configuration
4. **Integration System** - Configures external service connections
5. **Security System** - Defines authentication and authorization policies

## Schema-First Design

OpenMAS follows a schema-first design approach where the configuration schema serves as the contract between components. This ensures:

1. **Consistency** - Common patterns across all configuration
2. **Validation** - Strong validation against the schema
3. **Documentation** - Self-documenting configuration
4. **Evolution** - Clear paths for schema versioning

For detailed implementation guidelines, refer to the [Configuration Validation](/03_configuration/configuration_validation.md) documentation.
