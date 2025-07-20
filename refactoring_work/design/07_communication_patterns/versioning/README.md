# Pattern Versioning

## Overview

This document describes the approach to versioning and evolving communication patterns in OpenMAS. It outlines how pattern versions are managed, documented, and updated while ensuring compatibility and maintaining OpenMAS's reasoning agnosticism.

## Versioning Principles

OpenMAS follows these principles for communication pattern versioning:

1. **Semantic Versioning** - Patterns follow semantic versioning (MAJOR.MINOR.PATCH)
2. **Compatibility Guarantees** - Clear compatibility guarantees between versions
3. **Protocol Independence** - Version changes apply consistently across all protocols
4. **Documentation Standards** - Thorough documentation of version changes
5. **Migration Paths** - Clear paths for migrating between versions
6. **Runtime Version Negotiation** - Dynamic negotiation of compatible versions

## Version Structure

Communication patterns use a three-part version number:

```
MAJOR.MINOR.PATCH
```

- **MAJOR** - Incompatible changes requiring adaptation
- **MINOR** - Backwards-compatible feature additions
- **PATCH** - Backwards-compatible bug fixes

## Pattern Version Management

### Version Specification

Patterns specify their version in configuration:

```yaml
communication_patterns:
  request_response:
    version: "1.2.0"
    options:
      timeout: 30
      retry:
        attempts: 3
```

### Version Registry

Versions are tracked in a central registry:

```python
class PatternVersionRegistry:
    """Registry for pattern versions."""

    def __init__(self):
        """Initialize the registry."""
        self._versions = {}

    def register_version(self, pattern_name, version, implementation):
        """Register a pattern version."""
        if pattern_name not in self._versions:
            self._versions[pattern_name] = {}

        self._versions[pattern_name][version] = implementation

    def get_version(self, pattern_name, version):
        """Get a specific pattern version."""
        if pattern_name not in self._versions:
            return None

        return self._versions[pattern_name].get(version)

    def get_latest_version(self, pattern_name):
        """Get the latest version of a pattern."""
        if pattern_name not in self._versions or not self._versions[pattern_name]:
            return None

        # Sort versions and return the latest
        versions = list(self._versions[pattern_name].keys())
        versions.sort(key=lambda v: [int(x) for x in v.split('.')])
        return self._versions[pattern_name][versions[-1]]

    def get_compatible_version(self, pattern_name, target_version):
        """Get a version compatible with the target version."""
        if pattern_name not in self._versions:
            return None

        # Parse target version
        target_major, target_minor, target_patch = map(int, target_version.split('.'))

        # Find compatible versions (same major version)
        compatible_versions = []
        for version in self._versions[pattern_name]:
            major, minor, patch = map(int, version.split('.'))
            if major == target_major:
                compatible_versions.append((version, minor, patch))

        if not compatible_versions:
            return None

        # Sort by minor and patch version, and return the latest
        compatible_versions.sort(key=lambda v: (v[1], v[2]))
        return self._versions[pattern_name][compatible_versions[-1][0]]
```

### Version-Aware Patterns

Patterns aware of versioning requirements:

```python
class VersionedPattern(BasePattern):
    """Base class for versioned patterns."""

    def __init__(self, communicator, config):
        """Initialize with a communicator and configuration."""
        super().__init__(communicator, config)
        self.version = config.get("version", "1.0.0")

    async def negotiate_version(self, target_agent, min_version=None):
        """Negotiate a compatible version with the target agent."""
        # Query target agent for supported versions
        supported_versions = await self.communicator.query_capabilities(
            target_agent,
            capability="version_info",
            parameters={"pattern": self.__class__.__name__}
        )

        if not supported_versions or "versions" not in supported_versions:
            # Default to this version if no information
            return self.version

        # Find compatible version
        my_major, my_minor, my_patch = map(int, self.version.split('.'))
        min_major = my_major

        if min_version:
            min_major, _, _ = map(int, min_version.split('.'))

        compatible_versions = []
        for version in supported_versions["versions"]:
            major, minor, patch = map(int, version.split('.'))
            if major >= min_major:
                compatible_versions.append((version, major, minor, patch))

        if not compatible_versions:
            raise VersionNegotiationError(f"No compatible version found with {target_agent}")

        # Sort by version components and pick the highest compatible version
        compatible_versions.sort(key=lambda v: (v[1], v[2], v[3]))
        return compatible_versions[-1][0]
```

## Version Compatibility

### Forward Compatibility

Patterns are designed to be forward compatible within the same major version:

```python
class RequestResponsePattern(VersionedPattern):
    """Request-Response pattern implementation."""

    async def send_request(self, target_agent, content, options=None):
        """Send a request using this pattern."""
        options = options or {}

        # Negotiate version
        negotiated_version = await self.negotiate_version(target_agent)
        major, minor, patch = map(int, negotiated_version.split('.'))

        # Prepare the message
        message = {
            "recipient": target_agent,
            "content": content,
            "correlation_id": str(uuid.uuid4()),
            "pattern_version": negotiated_version
        }

        # Add version-specific fields
        if major == 1:
            if minor >= 1:
                # Version 1.1.0+ supports timeout
                message["timeout"] = options.get("timeout", 30)

            if minor >= 2:
                # Version 1.2.0+ supports retry
                message["retry"] = options.get("retry", {"attempts": 0})

        # Send the message
        return await self._send_message(message)
```

### Backward Compatibility

Patterns handle older versions through fallback mechanisms:

```python
class RequestResponseHandler:
    """Handler for request-response messages."""

    async def handle_request(self, request):
        """Handle an incoming request."""
        # Extract version
        version = request.get("pattern_version", "1.0.0")
        major, minor, patch = map(int, version.split('.'))

        # Process based on version
        if major == 1:
            # Base functionality for all 1.x versions
            response = {
                "correlation_id": request.get("correlation_id"),
                "content": await self._process_request(request.get("content", {})),
                "status": "success"
            }

            # Version-specific enhancements
            if minor >= 1:
                # Version 1.1.0+ supports response metadata
                response["metadata"] = {
                    "processing_time": self._calculate_processing_time()
                }

            if minor >= 2:
                # Version 1.2.0+ supports partial responses
                response["is_partial"] = False

            return response
        else:
            # Unsupported major version
            return {
                "correlation_id": request.get("correlation_id"),
                "status": "error",
                "error": {
                    "code": "UNSUPPORTED_VERSION",
                    "message": f"Unsupported version: {version}"
                }
            }
```

## Version Evolution

### Adding New Features

New features are added in minor version increments:

```python
# Version 1.0.0 - Basic request-response
@register_pattern_version("request_response", "1.0.0")
class RequestResponseV1_0_0(BasePattern):
    async def send_request(self, target_agent, content):
        # Basic implementation
        pass

# Version 1.1.0 - Added timeout support
@register_pattern_version("request_response", "1.1.0")
class RequestResponseV1_1_0(RequestResponseV1_0_0):
    async def send_request(self, target_agent, content, timeout=30):
        # Enhanced with timeout
        pass

# Version 1.2.0 - Added retry support
@register_pattern_version("request_response", "1.2.0")
class RequestResponseV1_2_0(RequestResponseV1_1_0):
    async def send_request(self, target_agent, content, timeout=30, retry=None):
        # Enhanced with retry
        pass
```

### Breaking Changes

Breaking changes require major version increments:

```python
# Version 1.0.0 - Original API
@register_pattern_version("delegation", "1.0.0")
class DelegationV1_0_0(BasePattern):
    async def delegate(self, target_agent, task):
        # Original implementation
        pass

# Version 2.0.0 - Completely new API
@register_pattern_version("delegation", "2.0.0")
class DelegationV2_0_0(BasePattern):
    async def create_task(self, task_definition):
        # New API
        pass

    async def assign_task(self, task_id, target_agent):
        # New API
        pass
```

## Protocol Adaptation Versioning

Pattern versions adapt consistently across protocols:

```yaml
# Version-specific protocol adaptations
request_response:
  version: "1.2.0"
  protocol_adaptations:
    a2a:
      "1.0.0":
        capability_name: "request_v1"
      "1.1.0":
        capability_name: "request_v1_1"
      "1.2.0":
        capability_name: "request_v1_2"

    mcp:
      "1.0.0":
        tool_name: "request_v1"
      "1.1.0":
        tool_name: "request_v1_1"
      "1.2.0":
        tool_name: "request_v1_2"
```

## Protocol Negotiation

Patterns negotiate protocol versions at runtime:

```python
async def negotiate_protocol_version(self, pattern_name, version, target_agent, protocol):
    """Negotiate a compatible protocol version."""
    try:
        # Query target agent for supported protocol versions
        supported_versions = await self.communicator.query_capabilities(
            target_agent,
            capability="protocol_versions",
            parameters={
                "pattern": pattern_name,
                "protocol": protocol
            }
        )

        if not supported_versions or "versions" not in supported_versions:
            # Default to requested version
            return version

        # Find compatible version (same major version)
        requested_major = int(version.split('.')[0])
        compatible_versions = []

        for supported_version in supported_versions["versions"]:
            supported_major = int(supported_version.split('.')[0])
            if supported_major == requested_major:
                compatible_versions.append(supported_version)

        if not compatible_versions:
            # No compatible version found
            raise VersionNegotiationError(
                f"No compatible {protocol} version for {pattern_name} found with {target_agent}"
            )

        # Sort and pick highest compatible version
        compatible_versions.sort(key=lambda v: [int(x) for x in v.split('.')])
        return compatible_versions[-1]

    except Exception as e:
        # Default to requested version on error
        return version
```

## Version Documentation

Each pattern version is thoroughly documented:

### Documentation Format

```markdown
# Request-Response Pattern (Version 1.2.0)

## Overview

The Request-Response pattern enables synchronous communication where one agent sends a request and receives a response.

## Version History

| Version | Release Date | Changes |
|---------|-------------|---------|
| 1.0.0   | 2023-01-15  | Initial version with basic request-response |
| 1.1.0   | 2023-05-20  | Added timeout support |
| 1.2.0   | 2023-10-10  | Added retry support |

## Features

### Base Features (1.0.0)
- Synchronous request-response
- Correlation ID tracking
- Error handling

### Added in 1.1.0
- Timeout configuration
- Response metadata

### Added in 1.2.0
- Automatic retry
- Partial response handling

## Breaking Changes

None (all changes are backward compatible)

## Migration Guide

Upgrading from 1.1.0 to 1.2.0 requires no changes.
```

## Version Migration

Guidelines for migrating between pattern versions:

### Deprecation Process

1. **Announcement** - Versions scheduled for deprecation are announced
2. **Grace Period** - Minimum 6-month period before deprecation
3. **Migration Guide** - Detailed guide for upgrading
4. **Dual Support** - Both old and new versions supported during transition
5. **Removal** - Deprecated version removed after grace period

### Migration Example

```markdown
# Migrating from Request-Response 1.0.0 to 1.2.0

## Step 1: Update Configuration
```yaml
communication_patterns:
  request_response:
    version: "1.2.0"  # Previously "1.0.0"
    options:
      timeout: 30     # New in 1.1.0
      retry:          # New in 1.2.0
        attempts: 3
        interval: 5
```

## Step 2: Update Code

```python
# Old code (1.0.0)
result = await agent.patterns.request_response.send(
    target_agent="service_agent",
    content={"action": "get_data"}
)

# New code (1.2.0)
result = await agent.patterns.request_response.send(
    target_agent="service_agent",
    content={"action": "get_data"},
    options={
        "timeout": 30,
        "retry": {
            "attempts": 3,
            "interval": 5
        }
    }
)
```
```

## Testing Versioned Patterns

Approaches for testing versioned patterns:

```python
class PatternVersionTest(unittest.TestCase):
    """Tests for pattern versioning."""

    async def test_version_negotiation(self):
        """Test version negotiation."""
        # Create agents with different versions
        agent1 = TestAgent(patterns={"request_response": {"version": "1.2.0"}})
        agent2 = TestAgent(patterns={"request_response": {"version": "1.0.0"}})

        # Negotiate version
        version = await agent1.patterns.request_response.negotiate_version(agent2.id)

        # Should negotiate to 1.0.0 (agent2's version)
        self.assertEqual(version, "1.0.0")

    async def test_forward_compatibility(self):
        """Test newer agent with older agent."""
        # Create agents with different versions
        newer_agent = TestAgent(patterns={"request_response": {"version": "1.2.0"}})
        older_agent = TestAgent(patterns={"request_response": {"version": "1.0.0"}})

        # Newer agent communicates with older agent
        result = await newer_agent.patterns.request_response.send(
            target_agent=older_agent.id,
            content={"action": "test"}
        )

        # Should succeed despite version difference
        self.assertEqual(result["status"], "success")

    async def test_backward_compatibility(self):
        """Test older agent with newer agent."""
        # Create agents with different versions
        newer_agent = TestAgent(patterns={"request_response": {"version": "1.2.0"}})
        older_agent = TestAgent(patterns={"request_response": {"version": "1.0.0"}})

        # Older agent communicates with newer agent
        result = await older_agent.patterns.request_response.send(
            target_agent=newer_agent.id,
            content={"action": "test"}
        )

        # Should succeed despite version difference
        self.assertEqual(result["status"], "success")
```

## Reasoning Agnosticism

Pattern versioning maintains OpenMAS's reasoning agnosticism by:

1. **Semantic Stability** - Version changes preserve consistent semantics
2. **Protocol Independence** - Versions adapt consistently across protocols
3. **Interface Compatibility** - Compatible interfaces across versions
4. **Content Agnosticism** - Version handling doesn't interpret message content
5. **Reasoning Separation** - Versioning independent of reasoning approach

This enables agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to communicate using different pattern versions consistently.
