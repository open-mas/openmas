# Communication Pattern Versioning and Evolution

This document describes the approach to versioning and evolving OpenMAS communication patterns while maintaining compatibility and supporting agent systems as they grow over time.

## Overview

Communication patterns in OpenMAS evolve to address new requirements, improve performance, and enhance capabilities. The versioning system ensures that:

1. Changes to patterns are transparent and well-documented
2. Existing agent systems continue to function when patterns evolve
3. Newer agents can co-exist with older agents in the same ecosystem
4. Transitions between pattern versions are smooth and manageable

## Versioning Principles

OpenMAS communication patterns follow these versioning principles:

### Semantic Versioning

Patterns follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes that require agents to be updated
- **MINOR**: Functionality added in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

### Interface Stability

Core pattern interfaces remain stable within the same major version, ensuring that agents using a pattern continue to function even as the implementation evolves.

### Compatibility Layers

Patterns include compatibility layers to support older interface versions when major changes are needed.

### Deprecation Process

Features are marked as deprecated before removal, allowing time for transition.

## Pattern Evolution Mechanisms

### 1. Interface Evolution

Interface evolution maintains backward compatibility while adding new capabilities:

```python
class RequestResponsePatternV2(BasePattern):
    """Request-Response pattern with versioned interfaces."""
    
    def __init__(self, config):
        super().__init__(config)
        self.version = config.get("version", "2.0")
        
    # Original interface (v1.x compatible)
    async def send_request(self, target_agent_id, request_type, content):
        """Send a request (compatibility with v1.x)."""
        # Forward to the enhanced implementation with defaults
        return await self.send_request_v2(
            target_agent_id=target_agent_id,
            request_type=request_type,
            content=content,
            options=None
        )
        
    # Enhanced interface (v2.x)
    async def send_request_v2(self, target_agent_id, request_type, content, options=None):
        """Send a request with enhanced options (v2.x)."""
        options = options or {}
        
        # Implementation with enhanced features
        # ...
        
    # Original interface (v1.x compatible)
    async def register_handler(self, request_type, handler):
        """Register a request handler (compatibility with v1.x)."""
        # Forward to the enhanced implementation with defaults
        return await self.register_handler_v2(
            request_type=request_type,
            handler=handler,
            options=None
        )
        
    # Enhanced interface (v2.x)
    async def register_handler_v2(self, request_type, handler, options=None):
        """Register a request handler with enhanced options (v2.x)."""
        options = options or {}
        
        # Implementation with enhanced features
        # ...
```

### 2. Pattern Registry with Version Support

The pattern registry supports retrieving specific versions of patterns:

```python
# In your agent initialization
async def initialize(self, context):
    # Get pattern registry
    pattern_registry = context.get_pattern_registry()
    
    # Get the latest version of a pattern
    self.latest_pattern = await pattern_registry.get_pattern(
        "request_response",
        self.config.get("patterns", {}).get("request_response")
    )
    
    # Get a specific version of a pattern
    self.v1_pattern = await pattern_registry.get_pattern(
        "request_response",
        self.config.get("patterns", {}).get("request_response"),
        version="1.0"
    )
```

### 3. Protocol Adapters Evolution

Protocol adapters evolve to support new protocol features while maintaining compatibility:

```python
class A2AProtocolAdapter:
    """Protocol adapter for A2A with versioning support."""
    
    def __init__(self, config):
        self.config = config
        self.protocol_version = config.get("protocol_version", "1.0")
        
    async def adapt_message(self, pattern_message, target_protocol="a2a"):
        """Adapt a pattern message to the target protocol version."""
        if self.protocol_version.startswith("1."):
            return await self.adapt_message_v1(pattern_message)
        elif self.protocol_version.startswith("2."):
            return await self.adapt_message_v2(pattern_message)
        else:
            raise ValueError(f"Unsupported protocol version: {self.protocol_version}")
            
    async def adapt_message_v1(self, pattern_message):
        """Adapt message for A2A protocol v1.x."""
        # v1.x adaptation logic
        # ...
        
    async def adapt_message_v2(self, pattern_message):
        """Adapt message for A2A protocol v2.x."""
        # v2.x adaptation logic with enhanced features
        # ...
```

## Version Negotiation

When agents connect, they negotiate the pattern version to use:

```python
async def establish_connection(self, target_agent_id):
    """Establish connection with another agent and negotiate pattern versions."""
    # Get local pattern versions
    local_versions = {
        "request_response": "2.1",
        "publish_subscribe": "1.5",
        "event_based": "3.0",
        "delegation": "1.0"
    }
    
    # Send capability message
    response = await self.communicator.send_capability_request(
        target_agent_id,
        {
            "supported_patterns": local_versions,
            "preferred_versions": local_versions
        }
    )
    
    # Process response
    if not response or "supported_patterns" not in response:
        # Use default lowest common versions
        return self.default_pattern_versions
        
    # Negotiate compatible versions
    negotiated_versions = {}
    
    for pattern_type, local_version in local_versions.items():
        if pattern_type in response["supported_patterns"]:
            remote_version = response["supported_patterns"][pattern_type]
            negotiated_versions[pattern_type] = self.negotiate_version(
                pattern_type, local_version, remote_version
            )
        else:
            # Remote agent doesn't support this pattern
            negotiated_versions[pattern_type] = None
            
    return negotiated_versions
    
def negotiate_version(self, pattern_type, local_version, remote_version):
    """Negotiate the highest compatible version between agents."""
    local_parts = [int(p) for p in local_version.split(".")]
    remote_parts = [int(p) for p in remote_version.split(".")]
    
    # Ensure major versions are compatible
    if local_parts[0] != remote_parts[0]:
        # Major version mismatch - use the lower major version
        major = min(local_parts[0], remote_parts[0])
        
        # Get the highest minor version for this major version
        pattern_registry = self.context.get_pattern_registry()
        available_versions = pattern_registry.get_available_versions(pattern_type)
        
        compatible_versions = [v for v in available_versions 
                              if v.startswith(f"{major}.")]
        
        if not compatible_versions:
            # No compatible versions available
            return None
            
        # Use the highest compatible version
        return max(compatible_versions)
    else:
        # Major versions match, use the minimum of each component
        negotiated = [min(local_parts[i], remote_parts[i]) 
                     for i in range(min(len(local_parts), len(remote_parts)))]
        
        return ".".join(str(p) for p in negotiated)
```

## Deprecation and Migration

### 1. Deprecation Process

Features targeted for removal are first marked as deprecated:

```python
# In code
import warnings

class EventBasedPattern:
    """Event-Based pattern implementation."""
    
    async def subscribe(self, event_type, callback):
        """
        Subscribe to events of a specific type.
        
        This method is still supported but will be removed in version 3.0.
        Use subscribe_v2 instead which provides additional filtering options.
        """
        warnings.warn(
            "The subscribe method is deprecated and will be removed in version 3.0. "
            "Use subscribe_v2 instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Forward to new implementation
        return await self.subscribe_v2(event_type, callback)
        
    async def subscribe_v2(self, event_type, callback, filters=None):
        """
        Subscribe to events of a specific type with optional filters.
        
        This is the preferred subscription method as of version 2.0.
        """
        # Enhanced implementation
        # ...
```

### 2. Migration Guides

For major pattern changes, OpenMAS provides migration guides:

```markdown
# Migration Guide: Event-Based Pattern v1.x to v2.x

## Overview

Event-Based Pattern v2.0 introduces enhanced filtering capabilities and
improved performance. This guide covers the steps to migrate from v1.x to v2.x.

## Breaking Changes

1. The `emit_event` method now requires a `context` parameter.
2. Event payload format has changed to a structured format.

## Migration Steps

### 1. Update Event Emissions

**Before (v1.x):**
```python
await event_pattern.emit_event(
    event_type="user_action",
    content="User clicked the button"
)
```

**After (v2.x):**
```python
await event_pattern.emit_event(
    event_type="user_action",
    content={
        "action": "User clicked the button",
        "timestamp": datetime.now().isoformat()
    },
    context={
        "source": "ui_component",
        "session_id": session_id
    }
)
```

### 2. Update Event Subscriptions

**Before (v1.x):**
```python
await event_pattern.subscribe(
    event_type="user_action",
    callback=self.handle_user_action
)
```

**After (v2.x):**
```python
await event_pattern.subscribe_v2(
    event_type="user_action",
    callback=self.handle_user_action,
    filters={
        "context.source": "ui_component"
    }
)
```

## Compatibility

A compatibility layer is provided through v2.x that supports v1.x method
signatures, but using these will trigger deprecation warnings. These
compatibility methods will be removed in v3.0.
```

## Pattern Version Lifecycle

Communication patterns follow a defined lifecycle:

1. **Development**: Initial development and testing of new features
2. **Beta**: New pattern version available for early adopters to test
3. **Release**: Stable version officially supported for production use
4. **Maintenance**: Bug fixes and minor improvements
5. **Deprecated**: Still supported but with deprecation warnings
6. **End-of-Life**: No longer supported or maintained

The OpenMAS documentation clearly indicates the current lifecycle stage of each pattern version.

## Maintaining Multi-Version Support

OpenMAS includes tools to help maintain agents that need to support multiple pattern versions:

### 1. Version Compatibility Testing

```python
from openmas.testing.patterns import VersionCompatibilityTest

# Test if agent works with different pattern versions
test = VersionCompatibilityTest(agent_class=MyAgent)

# Test all pattern versions
await test.test_all_pattern_versions()

# Test specific pattern versions
await test.test_pattern_version(
    pattern_type="request_response",
    versions=["1.0", "2.0", "2.1"]
)
```

### 2. Version Support Matrix

OpenMAS maintains a version support matrix that shows which agent versions support which pattern versions:

```
| Pattern Type      | v1.0    | v1.5    | v2.0    | v2.1    | v3.0    |
|-------------------|---------|---------|---------|---------|---------|
| Request-Response  | ✓       | ✓       | ✓       | ✓       | -       |
| Publish-Subscribe | ✓       | ✓       | -       | -       | -       |
| Event-Based       | ✓       | ✓       | ✓       | ✓       | ✓       |
| Streaming         | -       | ✓       | ✓       | ✓       | ✓       |
| Pipeline          | -       | -       | ✓       | ✓       | ✓       |
| Delegation        | -       | -       | -       | ✓       | ✓       |
```

## Protocol Evolution Support

Pattern versioning also handles evolution of the underlying protocols:

```python
class MCPProtocolAdapter:
    """Protocol adapter for MCP with versioning support."""
    
    def __init__(self, config):
        self.config = config
        self.protocol_version = config.get("protocol_version", "1.0")
        self.features = self.get_supported_features()
        
    def get_supported_features(self):
        """Get features supported by this protocol version."""
        if self.protocol_version.startswith("1.0"):
            return {
                "streaming": False,
                "binary_attachments": False,
                "enhanced_security": False
            }
        elif self.protocol_version.startswith("1.1"):
            return {
                "streaming": True,
                "binary_attachments": False,
                "enhanced_security": False
            }
        elif self.protocol_version.startswith("2.0"):
            return {
                "streaming": True,
                "binary_attachments": True,
                "enhanced_security": True
            }
            
    async def adapt_pattern_message(self, pattern_message):
        """Adapt a pattern message for the MCP protocol."""
        # Adaptation based on protocol version
        if not self.features["streaming"] and pattern_message.get("pattern_type") == "streaming":
            # Handle incompatible pattern
            raise PatternNotSupportedError(
                f"Streaming pattern not supported in MCP {self.protocol_version}"
            )
        
        # Adaptation logic based on protocol version
        if self.protocol_version.startswith("1.0"):
            return await self.adapt_for_v1_0(pattern_message)
        elif self.protocol_version.startswith("1.1"):
            return await self.adapt_for_v1_1(pattern_message)
        elif self.protocol_version.startswith("2.0"):
            return await self.adapt_for_v2_0(pattern_message)
```

## Best Practices for Pattern Evolution

When evolving patterns, follow these best practices:

1. **Minimize Breaking Changes**: Avoid breaking changes whenever possible; add new methods rather than changing existing ones.

2. **Clear Deprecation Paths**: Always provide clear deprecation warnings and migration paths before removing functionality.

3. **Backward Compatibility**: Maintain backward compatibility for at least one major version cycle to allow agents time to update.

4. **Feature Detection**: Use feature detection rather than version checking when possible:

   ```python
   # Less robust:
   if self.pattern_version >= "2.0":
       # Use v2.0 features
   
   # More robust:
   if hasattr(self.pattern, "subscribe_v2"):
       # Use enhanced subscription
   else:
       # Fall back to basic subscription
   ```

5. **Comprehensive Testing**: Test all versions thoroughly, especially compatibility between different versions.

6. **Documentation**: Clearly document version differences, breaking changes, and migration steps.

## Conclusion

OpenMAS's pattern versioning and evolution approach ensures that agent systems can remain functional while benefiting from pattern improvements. By following semantic versioning, providing compatibility layers, and maintaining clear documentation, OpenMAS enables a smooth evolution path for communication patterns.
