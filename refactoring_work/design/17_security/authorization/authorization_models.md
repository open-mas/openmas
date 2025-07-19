# Authorization Models

## Overview

This document describes the authorization models supported by OpenMAS. These models provide mechanisms to control what authenticated entities can do within the system while maintaining OpenMAS's reasoning-agnostic design and multi-protocol support.

## Authorization Framework

OpenMAS implements a flexible authorization framework that supports multiple authorization models through a plugin architecture:

```
┌───────────────────────────────────────────────┐
│          Authorization Provider               │
│                                               │
│  ┌─────────────┐  ┌─────────────┐   ┌──────┐  │
│  │ Policy      │  │ Decision    │   │Policy│  │
│  │ Enforcement │  │ Point       │   │Store │  │
│  └─────────────┘  └─────────────┘   └──────┘  │
│         │                │              │     │
└─────────┼────────────────┼──────────────┼─────┘
          │                │              │
┌─────────▼────┐   ┌───────▼────┐  ┌─────▼─────┐
│ Protocols    │   │ Agents     │  │ Services  │
└──────────────┘   └────────────┘  └───────────┘
```

## Supported Authorization Models

### 1. Role-Based Access Control (RBAC)

Authorization based on roles assigned to entities:

```yaml
authorization:
  model: "rbac"
  settings:
    roles:
      - name: "admin"
        permissions: ["read", "write", "execute", "manage"]
      - name: "user"
        permissions: ["read", "execute"]
      - name: "observer"
        permissions: ["read"]
    assignments:
      - entity_id: "agent1"
        roles: ["admin"]
      - entity_id: "agent2"
        roles: ["user"]
```

Features:
- **Simplicity**: Easy to understand and implement
- **Role Hierarchies**: Support for role inheritance
- **Administration**: Simplified user administration
- **Standardization**: Widely understood model

Limitations:
- **Coarse-Grained**: Limited granularity in access control
- **Static Structure**: Less flexible for dynamic environments
- **Role Explosion**: Can lead to many roles for fine-grained control

### 2. Attribute-Based Access Control (ABAC)

Authorization based on attributes of entities, resources, and environment:

```yaml
authorization:
  model: "abac"
  settings:
    attribute_sources:
      - type: "entity"
        attributes: ["role", "clearance", "department"]
      - type: "resource"
        attributes: ["sensitivity", "owner", "type"]
      - type: "environment"
        attributes: ["time", "location", "risk_level"]
    policies:
      - name: "sensitive_data_access"
        condition: "entity.clearance >= resource.sensitivity && (entity.department == resource.owner || entity.role == 'admin')"
        effect: "allow"
      - name: "time_restriction"
        condition: "environment.time between '09:00' and '17:00'"
        effect: "allow"
```

Features:
- **Fine-Grained Control**: Highly detailed access decisions
- **Context-Aware**: Considers environmental factors
- **Flexible Policies**: Complex policy expressions
- **Dynamic Decisions**: Decisions based on runtime attributes

Limitations:
- **Complexity**: More complex to design and implement
- **Performance**: Policy evaluation can be more expensive
- **Management**: Policy management can be challenging

### 3. Capability-Based Access Control

Authorization based on unforgeable tokens (capabilities) that grant specific permissions:

```yaml
authorization:
  model: "capability"
  settings:
    capability_format: "jwt"
    signing_key: "${CAPABILITY_SIGNING_KEY}"
    capabilities:
      - name: "resource_read"
        resources: ["documents", "messages"]
        actions: ["read"]
      - name: "resource_write"
        resources: ["documents"]
        actions: ["write"]
    delegations:
      - entity_id: "agent1"
        capabilities: ["resource_read", "resource_write"]
        can_delegate: true
      - entity_id: "agent2"
        capabilities: ["resource_read"]
        can_delegate: false
```

Features:
- **Object-Centric**: Focuses on resources rather than subjects
- **Delegation**: Natural support for delegation
- **Principle of Least Privilege**: Easy to enforce minimal permissions
- **No Central Authority**: Can operate without central identity system

Limitations:
- **Capability Management**: Challenges in managing capabilities
- **Revocation**: Difficult to revoke capabilities
- **Privilege Escalation**: Risk if capabilities are not properly protected

### 4. Protocol-Based Access Control

Authorization specific to protocol functionality:

```yaml
authorization:
  model: "protocol_based"
  settings:
    default_policy: "deny"
    protocol_policies:
      mcp:
        function_calls:
          - function: "read_file"
            allowed_entities: ["agent1", "agent2"]
          - function: "write_file"
            allowed_entities: ["agent1"]
      a2a:
        capabilities:
          - capability: "conversation"
            allowed_entities: ["agent1", "agent2"]
          - capability: "function_execution"
            allowed_entities: ["agent1"]
      http:
        endpoints:
          - path: "/api/documents"
            method: "GET"
            allowed_entities: ["agent1", "agent2"]
          - path: "/api/documents"
            method: "POST"
            allowed_entities: ["agent1"]
```

Features:
- **Protocol-Specific**: Tailored to each protocol's needs
- **Explicit Permissions**: Clear mapping of permissions to protocol features
- **Comprehensive Coverage**: Covers all protocol interactions
- **Protocol Independence**: Authorization that works across protocols

### 5. Reasoning-Aligned Access Control

Authorization aligned with reasoning approaches:

```yaml
authorization:
  model: "reasoning_aligned"
  settings:
    reasoning_approaches:
      llm:
        policies:
          - name: "model_access"
            condition: "entity.role == 'admin' || entity.clearance >= 'confidential'"
            effect: "allow"
      rule_based:
        policies:
          - name: "rule_modification"
            condition: "entity.role == 'admin'"
            effect: "allow"
      bdi:
        policies:
          - name: "belief_update"
            condition: "entity.role == 'admin' || entity.role == 'domain_expert'"
            effect: "allow"
```

Features:
- **Reasoning Integration**: Aligned with reasoning approaches
- **Brain-Body Separation**: Maintains separation between communication and reasoning
- **Reasoning-Specific Controls**: Tailored to specific reasoning needs
- **Cross-Reasoning Compatibility**: Works across reasoning approaches

## Protocol-Specific Authorization

### MCP Authorization

Authorization for Model Context Protocol:

```yaml
authorization:
  model: "rbac"
  settings:
    # RBAC settings...
  protocol_specific:
    mcp:
      function_call_authorization: true
      function_policies:
        - function: "read_file"
          required_roles: ["user", "admin"]
        - function: "write_file"
          required_roles: ["admin"]
```

Key features:
- **Function Call Authorization**: Control over which functions can be called
- **Parameter Validation**: Validation of function parameters
- **Resource Access Control**: Control over resource access via functions
- **Tool-Specific Permissions**: Permissions for specific tools

### A2A Authorization

Authorization for Agent-to-Agent Protocol:

```yaml
authorization:
  model: "capability"
  settings:
    # Capability settings...
  protocol_specific:
    a2a:
      capability_verification: true
      capability_policies:
        - capability: "conversation"
          required_capabilities: ["base_communication"]
        - capability: "function_execution"
          required_capabilities: ["advanced_communication"]
```

Key features:
- **Capability Verification**: Verify agent capabilities against policies
- **Protocol Permissions**: Control over protocol features
- **Communication Control**: Control over communication patterns
- **Agent Card Authorization**: Authorization via agent cards

### HTTP Authorization

Authorization for HTTP-based communication:

```yaml
authorization:
  model: "rbac"
  settings:
    # RBAC settings...
  protocol_specific:
    http:
      endpoint_authorization: true
      endpoint_policies:
        - path: "/api/documents"
          method: "GET"
          required_roles: ["user", "admin"]
        - path: "/api/documents"
          method: "POST"
          required_roles: ["admin"]
```

Key features:
- **Endpoint Authorization**: Control over HTTP endpoints
- **Method Authorization**: Control over HTTP methods
- **Path-Based Authorization**: Control based on URL paths
- **Header-Based Policies**: Authorization based on headers

### MQTT Authorization

Authorization for MQTT-based communication:

```yaml
authorization:
  model: "abac"
  settings:
    # ABAC settings...
  protocol_specific:
    mqtt:
      topic_authorization: true
      topic_policies:
        - topic: "documents/#"
          operation: "subscribe"
          condition: "entity.role == 'user' || entity.role == 'admin'"
        - topic: "documents/#"
          operation: "publish"
          condition: "entity.role == 'admin'"
```

Key features:
- **Topic Authorization**: Control over MQTT topics
- **QoS Control**: Control over Quality of Service levels
- **Publish/Subscribe Control**: Separate control for pub/sub operations
- **Hierarchical Policies**: Topic hierarchy-based authorization

### gRPC Authorization

Authorization for gRPC-based communication:

```yaml
authorization:
  model: "rbac"
  settings:
    # RBAC settings...
  protocol_specific:
    grpc:
      service_authorization: true
      service_policies:
        - service: "DocumentService"
          method: "GetDocument"
          required_roles: ["user", "admin"]
        - service: "DocumentService"
          method: "CreateDocument"
          required_roles: ["admin"]
```

Key features:
- **Service Authorization**: Control over gRPC services
- **Method Authorization**: Control over service methods
- **Interceptor-Based**: Authorization via gRPC interceptors
- **Metadata-Based Policies**: Authorization based on metadata

## Integration with Reasoning

Authorization integrates with OpenMAS's reasoning-agnostic architecture through the Reasoning Security Interface (RSI):

```
┌─────────────────────────────────┐
│          Communication Layer    │
│          ("Body")               │
│                                 │
│  ┌───────────────────────────┐  │
│  │  Authorization System     │  │
│  └─────────────┬─────────────┘  │
│                │                │
└────────────────┼────────────────┘
                 │
┌────────────────┼────────────────┐
│                │                │
│  ┌─────────────▼─────────────┐  │
│  │  Reasoning Security       │  │
│  │  Interface (RSI)          │  │
│  └───────────────────────────┘  │
│                                 │
│          Reasoning Layer        │
│          ("Brain")              │
└─────────────────────────────────┘
```

The Reasoning Security Interface (RSI) provides a standardized way for reasoning engines to perform fine-grained permission checks during their execution using the `RSI.check_permission()` method. This method allows reasoning engines to check if the current principal has permission to perform specific actions on specific resources, enabling context-aware security decisions within the reasoning process.

For complete details on how reasoning engines can perform authorization checks, refer to the [Reasoning Security Interface (RSI) specification](../reasoning_security_interface.md).

Each reasoning approach can implement the authorization interface differently:

- **LLM Reasoning**: Authorization for model access and prompt construction
- **Rule-Based Reasoning**: Rules-based authorization policies
- **BDI Reasoning**: Belief-based authorization models
- **Hybrid Reasoning**: Combined authorization approaches

## Combining Authorization Models

OpenMAS supports combining multiple authorization models for comprehensive security:

```yaml
authorization:
  combined_model:
    models:
      - model: "rbac"
        settings:
          # RBAC settings...
        weight: 0.5
      - model: "abac"
        settings:
          # ABAC settings...
        weight: 0.5
    composition_strategy: "all_allow"  # Options: any_allow, all_allow, weighted
```

Features:
- **Defense in Depth**: Multiple authorization layers
- **Model Composition**: Combine strengths of different models
- **Flexible Composition**: Different strategies for combining decisions
- **Weighted Decisions**: Weight authorization models by importance

## Configuration

Authorization is configured through the unified configuration schema:

```yaml
# System-level authorization
authorization:
  model: "rbac"
  settings:
    # RBAC settings...

# Agent-specific authorization
agents:
  - id: "agent1"
    # Other agent configuration...
    authorization:
      model: "capability"
      settings:
        # Capability settings...

# Protocol-specific authorization
protocols:
  - type: "mcp"
    # Other protocol configuration...
    authorization:
      model: "protocol_based"
      settings:
        # Protocol-based settings...
```

## Best Practices

1. **Least Privilege**: Grant minimal necessary permissions
2. **Defense in Depth**: Layer authorization controls
3. **Appropriate Model**: Choose the right authorization model for each context
4. **Explicit Denials**: Prefer explicit denial over implicit access
5. **Regular Review**: Review authorization policies regularly
6. **Comprehensive Coverage**: Ensure all resources are protected
7. **Default Deny**: Use a "deny by default" approach
8. **Authorization Audit**: Maintain authorization audit trails
9. **Consistent Policy**: Maintain consistent policy across protocols
10. **Testing**: Thoroughly test authorization policies

## Related Documentation

- [Security Principles](../architecture/security_principles.md)
- [Authentication](../authentication/README.md)
- [Communication Security](../communication/README.md)
- [Configuration Schema](../../03_configuration/schema/security.md)
