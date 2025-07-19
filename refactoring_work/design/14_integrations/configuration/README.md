# OpenMAS Integration Configuration

## Overview

This directory contains documentation on configuring external integrations in OpenMAS. The integration configuration follows the unified configuration schema, which serves as the single source of truth for all configuration in the OpenMAS framework.

## Configuration Structure

Integration configurations are defined within the `integrations` section of the unified configuration schema. For the complete and authoritative schema definition, see the [Integration Configuration Schema](/03_configuration/schema/integrations.md).

## Key Configuration Components

Integration configuration includes these key components:

### 1. Integration Type

Defines the category of integration:
- Service integrations (cloud services, databases)
- Framework interoperability (LangChain, AutoGen)
- API connections (external tools, platforms)
- Protocol adaptations (external protocols)

### 2. Authentication Configuration

Standardized authentication handling:
- API key management
- OAuth flows
- Basic authentication
- Certificate-based authentication

### 3. Retry and Resilience

Configuration for robust operation:
- Retry policies
- Circuit breaker settings
- Timeout configurations
- Fallback mechanisms

### 4. Protocol-Specific Settings

Protocol adaptations for each integration:
- A2A message format mappings
- MCP tool definitions
- HTTP endpoint configurations
- MQTT topic structures
- gRPC service definitions

## Integration with Reasoning Agnosticism

The integration configuration maintains OpenMAS's distinctive reasoning agnosticism by:

1. Defining interface contracts independent of reasoning approaches
2. Separating integration infrastructure (body) from reasoning logic (brain)
3. Providing consistent capabilities regardless of the underlying reasoning system
4. Enabling different reasoning approaches to access the same external services

## Configuration Examples

For example configurations demonstrating different integration types, refer to the [schema.md](./schema.md) file, which provides guidance and examples while referencing the authoritative unified schema.

## Related Documentation

- [Integration Design Overview](/14_integrations/design/overview.md) - High-level design of the integration system
- [Integration Implementation Guide](/14_integrations/implementation/guide.md) - Implementation details for integration developers
