# Authorization

## Overview

This directory contains documentation about the authorization mechanisms in OpenMAS. Authorization determines what authenticated entities (agents, services, users) are permitted to do within the system, providing fine-grained access control across all supported protocols while maintaining OpenMAS's reasoning-agnostic design.

## Key Authorization Components

OpenMAS's authorization system consists of these key components:

1. **Authorization Models**: Different approaches to access control
2. **Permission System**: Granular permission definitions
3. **Policy Enforcement**: Mechanisms to enforce authorization policies
4. **Protocol-Specific Authorization**: Authorization tailored to each protocol
5. **Capability-Based Authorization**: Authorization based on agent capabilities

## Documentation

- [Authorization Models](./authorization_models.md): Detailed documentation of authorization models and approaches

## Related Documentation

- [Security Architecture](../architecture/README.md)
- [Authentication](../authentication/README.md)
- [Communication Security](../communication/README.md)
- [Configuration Schema](../../03_configuration/schema/security.md)
