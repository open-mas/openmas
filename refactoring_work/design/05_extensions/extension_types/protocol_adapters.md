# Protocol Adapter Extensions

## Overview

Protocol Adapter Extensions enable seamless communication between different protocols in OpenMAS. They translate messages, capabilities, and resources between protocols, allowing agents to interact regardless of which protocol they use. This is a key component in OpenMAS's multi-protocol support strategy.

## Base Class

Protocol Adapter Extensions must inherit from the `ProtocolAdapterExtension` base class:

```python
from openmas.extensions import ProtocolAdapterExtension

class MyProtocolAdapterExtension(ProtocolAdapterExtension):
    """A custom protocol adapter extension."""
```

## Required Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `to_internal_format(message, context)` | Convert a protocol-specific message to the Standard Internal Message Format (SIMF) | `message`: Protocol-specific message<br>`context`: Conversion context | SIMF message |
| `from_internal_format(internal_message, target_protocol, context)` | Convert a SIMF message to a target protocol format | `internal_message`: SIMF message<br>`target_protocol`: Target protocol identifier<br>`context`: Conversion context | Protocol-specific message |

## Optional Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `validate_config()` | Validate the extension configuration | None | None, raises exception if invalid |
| `initialize()` | Initialize the extension | None | None |
| `get_supported_protocols()` | Get protocols supported by this adapter | None | List of protocol identifiers |
| `map_capability(capability, source_protocol, target_protocol)` | Map a capability between protocols | `capability`: Capability to map<br>`source_protocol`: Source protocol<br>`target_protocol`: Target protocol | Mapped capability |
| `map_resource(resource, source_protocol, target_protocol)` | Map a resource between protocols | `resource`: Resource to map<br>`source_protocol`: Source protocol<br>`target_protocol`: Target protocol | Mapped resource |

## Configuration Schema

Protocol Adapter Extensions are configured in the unified configuration schema under the `extensions` section with `type: "protocol_adapter"`:

```yaml
extensions:
  my_protocol_adapter:
    type: "protocol_adapter"
    name: "my_protocol_adapter"
    enabled: true
    options:
      source_protocol: "a2a"
      target_protocol: "mcp"
      mapping_rules:
        capabilities:
          - source: "tool_use"
            target: "function_calling"
          - source: "image_generation"
            target: "image_generation"
        message_types:
          - source: "text"
            target: "text"
          - source: "multipart"
            target: "multipart"
      # Additional configuration specific to this extension
```

### Options Schema

The `options` block for Protocol Adapter Extensions supports the following fields:

| Field | Type | Required | Description |
|-------|------|----------|--------------|
| `source_protocol` | string | Yes | Source protocol identifier |
| `target_protocol` | string | Yes | Target protocol identifier |
| `mapping_rules` | object | Yes | Rules for mapping between protocols |
| `mapping_rules.capabilities` | array | No | Capability mapping rules |
| `mapping_rules.message_types` | array | No | Message type mapping rules |
| `mapping_rules.resources` | array | No | Resource mapping rules |
| `default_behavior` | string | No | Default behavior for unmapped items ("pass_through" or "block") |

For the complete schema definition, refer to the [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md#protocol-adapter-extension-options).

## Interaction Model

Protocol Adapter Extensions interact with the OpenMAS framework through the following mechanisms:

1. **Registration**: The extension is registered with the extension registry
2. **Discovery**: The communicator framework discovers available protocol adapters
3. **Protocol Detection**: When a message is received, its protocol is detected
4. **Internal Conversion**: The message is converted to the Standard Internal Message Format (SIMF)
5. **Processing**: The message is processed by the agent's reasoning engine
6. **Response Generation**: The response is generated in SIMF
7. **Target Conversion**: The SIMF response is converted to the target protocol format

The Protocol Adapter Framework maintains control over when adapters are invoked, while the extension provides the specific protocol conversion implementation.

## Code Example

Here's a minimal example of a Protocol Adapter Extension that converts between A2A and MCP protocols:

```python
from openmas.extensions import ProtocolAdapterExtension
import json
from typing import Dict, List, Any, Optional

class A2AMCPAdapterExtension(ProtocolAdapterExtension):
    """Extension that adapts between A2A and MCP protocols."""
    
    extension_type = "protocol_adapter"
    extension_name = "a2a_mcp_adapter"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        options = config.get("options", {})
        
        # Extract configuration
        self.source_protocol = options.get("source_protocol")
        self.target_protocol = options.get("target_protocol")
        self.mapping_rules = options.get("mapping_rules", {})
        self.default_behavior = options.get("default_behavior", "pass_through")
        
        # Extract specific mapping rules
        self.capability_mappings = self._process_capability_mappings()
        self.message_type_mappings = self._process_message_type_mappings()
        self.resource_mappings = self._process_resource_mappings()
    
    def _process_capability_mappings(self):
        """Process capability mapping rules."""
        mappings = {}
        for mapping in self.mapping_rules.get("capabilities", []):
            source = mapping.get("source")
            target = mapping.get("target")
            if source and target:
                mappings[source] = target
        return mappings
    
    def _process_message_type_mappings(self):
        """Process message type mapping rules."""
        mappings = {}
        for mapping in self.mapping_rules.get("message_types", []):
            source = mapping.get("source")
            target = mapping.get("target")
            if source and target:
                mappings[source] = target
        return mappings
    
    def _process_resource_mappings(self):
        """Process resource mapping rules."""
        mappings = {}
        for mapping in self.mapping_rules.get("resources", []):
            source = mapping.get("source")
            target = mapping.get("target")
            if source and target:
                mappings[source] = target
        return mappings
    
    def validate_config(self):
        """Validate the extension configuration."""
        options = self.config.get("options", {})
        if not options.get("source_protocol"):
            raise ValueError("Protocol adapter requires 'source_protocol' in options")
        if not options.get("target_protocol"):
            raise ValueError("Protocol adapter requires 'target_protocol' in options")
    
    def get_supported_protocols(self):
        """Get protocols supported by this adapter."""
        return [self.source_protocol, self.target_protocol]
    
    async def to_internal_format(self, message, context=None):
        """Convert a protocol-specific message to SIMF."""
        context = context or {}
        protocol = context.get("protocol")
        
        # Handle A2A to SIMF conversion
        if protocol == "a2a":
            return self._a2a_to_internal(message)
        
        # Handle MCP to SIMF conversion
        elif protocol == "mcp":
            return self._mcp_to_internal(message)
        
        # Unsupported protocol
        else:
            raise ValueError(f"Unsupported source protocol: {protocol}")
    
    async def from_internal_format(self, internal_message, target_protocol, context=None):
        """Convert a SIMF message to a target protocol format."""
        context = context or {}
        
        # Handle SIMF to A2A conversion
        if target_protocol == "a2a":
            return self._internal_to_a2a(internal_message, context)
        
        # Handle SIMF to MCP conversion
        elif target_protocol == "mcp":
            return self._internal_to_mcp(internal_message, context)
        
        # Unsupported protocol
        else:
            raise ValueError(f"Unsupported target protocol: {target_protocol}")
    
    def _a2a_to_internal(self, message):
        """Convert A2A message to internal format."""
        # Extract core message properties
        message_id = message.get("id", str(uuid.uuid4()))
        message_type = self._map_message_type(message.get("type"), "a2a", "internal")
        
        # Extract content based on message type
        content = message.get("content", {})
        parts = message.get("parts", [])
        
        # Build the internal message
        internal_message = {
            "id": message_id,
            "timestamp": message.get("timestamp", datetime.datetime.now().isoformat()),
            "protocol": "a2a",
            "message_type": message_type,
            "payload": {
                "type": "content",
                "data": content
            },
            "metadata": message.get("metadata", {})
        }
        
        # Handle multi-part messages
        if parts and message_type == "multipart":
            internal_message["payload"] = {
                "type": "multipart",
                "parts": []
            }
            
            for part in parts:
                internal_part = {
                    "type": part.get("type"),
                    "data": part.get("data")
                }
                internal_message["payload"]["parts"].append(internal_part)
        
        return internal_message
    
    def _mcp_to_internal(self, message):
        """Convert MCP message to internal format."""
        # Extract core message properties
        message_id = message.get("message_id", str(uuid.uuid4()))
        
        # Determine message type based on content
        if "tool_calls" in message:
            message_type = "tool_call"
        elif "content" in message and isinstance(message["content"], list):
            message_type = "multipart"
        else:
            message_type = "text"
        
        # Map to internal message type
        internal_message_type = self._map_message_type(message_type, "mcp", "internal")
        
        # Build the internal message
        internal_message = {
            "id": message_id,
            "timestamp": message.get("created_at", datetime.datetime.now().isoformat()),
            "protocol": "mcp",
            "message_type": internal_message_type,
            "metadata": {
                "role": message.get("role", "user"),
                "name": message.get("name")
            }
        }
        
        # Handle different payload types
        if message_type == "text":
            internal_message["payload"] = {
                "type": "text",
                "data": message.get("content", "")
            }
        elif message_type == "multipart":
            parts = []
            for content_part in message.get("content", []):
                part_type = content_part.get("type")
                part_data = content_part.get("text") if part_type == "text" else content_part.get("image_url")
                
                parts.append({
                    "type": part_type,
                    "data": part_data
                })
            
            internal_message["payload"] = {
                "type": "multipart",
                "parts": parts
            }
        elif message_type == "tool_call":
            tool_calls = []
            for tool_call in message.get("tool_calls", []):
                tool_calls.append({
                    "tool_id": tool_call.get("id"),
                    "tool_name": tool_call.get("function", {}).get("name"),
                    "parameters": json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                })
            
            internal_message["payload"] = {
                "type": "tool_call",
                "tools": tool_calls
            }
        
        return internal_message
    
    def _internal_to_a2a(self, internal_message, context):
        """Convert internal format to A2A message."""
        # Extract core message properties
        message_id = internal_message.get("id")
        internal_type = internal_message.get("message_type")
        payload = internal_message.get("payload", {})
        
        # Map to A2A message type
        a2a_message_type = self._map_message_type(internal_type, "internal", "a2a")
        
        # Build the A2A message
        a2a_message = {
            "id": message_id,
            "timestamp": internal_message.get("timestamp"),
            "type": a2a_message_type,
            "metadata": internal_message.get("metadata", {})
        }
        
        # Handle different payload types
        payload_type = payload.get("type")
        
        if payload_type == "text":
            a2a_message["content"] = payload.get("data", "")
        
        elif payload_type == "multipart":
            parts = []
            for part in payload.get("parts", []):
                parts.append({
                    "type": part.get("type"),
                    "data": part.get("data")
                })
            
            a2a_message["parts"] = parts
        
        elif payload_type == "tool_call":
            # Convert to A2A's action format
            tool_calls = payload.get("tools", [])
            if tool_calls:
                a2a_message["actions"] = []
                
                for tool_call in tool_calls:
                    a2a_message["actions"].append({
                        "name": tool_call.get("tool_name"),
                        "parameters": tool_call.get("parameters", {})
                    })
        
        return a2a_message
    
    def _internal_to_mcp(self, internal_message, context):
        """Convert internal format to MCP message."""
        # Extract core message properties
        message_id = internal_message.get("id")
        internal_type = internal_message.get("message_type")
        payload = internal_message.get("payload", {})
        metadata = internal_message.get("metadata", {})
        
        # Map to MCP message type
        mcp_message_type = self._map_message_type(internal_type, "internal", "mcp")
        
        # Build the MCP message
        mcp_message = {
            "message_id": message_id,
            "created_at": internal_message.get("timestamp"),
            "role": metadata.get("role", "assistant"),
        }
        
        if "name" in metadata:
            mcp_message["name"] = metadata["name"]
        
        # Handle different payload types
        payload_type = payload.get("type")
        
        if payload_type == "text":
            mcp_message["content"] = payload.get("data", "")
        
        elif payload_type == "multipart":
            content_parts = []
            for part in payload.get("parts", []):
                part_type = part.get("type")
                
                if part_type == "text":
                    content_parts.append({
                        "type": "text",
                        "text": part.get("data")
                    })
                elif part_type == "image":
                    content_parts.append({
                        "type": "image_url",
                        "image_url": part.get("data")
                    })
            
            mcp_message["content"] = content_parts
        
        elif payload_type == "tool_call":
            # Convert to MCP's function calling format
            tool_calls = payload.get("tools", [])
            if tool_calls:
                mcp_message["tool_calls"] = []
                
                for i, tool_call in enumerate(tool_calls):
                    mcp_message["tool_calls"].append({
                        "id": tool_call.get("tool_id", f"call_{i}"),
                        "type": "function",
                        "function": {
                            "name": tool_call.get("tool_name"),
                            "arguments": json.dumps(tool_call.get("parameters", {}))
                        }
                    })
        
        return mcp_message
    
    def _map_message_type(self, message_type, source_protocol, target_protocol):
        """Map message type between protocols."""
        # Define the mapping key
        mapping_key = f"{source_protocol}:{message_type}"
        
        # Check if we have a mapping for this message type
        for mapping in self.mapping_rules.get("message_types", []):
            if f"{source_protocol}:{mapping['source']}" == mapping_key:
                return mapping["target"]
        
        # Default mappings for common types
        default_mappings = {
            "a2a:text": "text",
            "a2a:multipart": "multipart",
            "a2a:action": "tool_call",
            "mcp:text": "text",
            "mcp:multipart": "multipart",
            "mcp:tool_call": "tool_call",
            "internal:text": "text",
            "internal:multipart": "multipart",
            "internal:tool_call": "function" if target_protocol == "mcp" else "action"
        }
        
        if mapping_key in default_mappings:
            return default_mappings[mapping_key]
        
        # If no mapping found, return original or raise exception based on default behavior
        if self.default_behavior == "pass_through":
            return message_type
        else:
            raise ValueError(f"No mapping found for message type: {mapping_key}")
    
    def map_capability(self, capability, source_protocol, target_protocol):
        """Map a capability between protocols."""
        # Check capability mappings
        mapping_key = f"{source_protocol}:{capability}"
        
        for mapping in self.mapping_rules.get("capabilities", []):
            if f"{source_protocol}:{mapping['source']}" == mapping_key:
                return mapping["target"]
        
        # Default mappings for common capabilities
        default_mappings = {
            "a2a:text_generation": "text_generation",
            "a2a:tool_use": "function_calling",
            "a2a:image_generation": "image_generation",
            "mcp:text_generation": "text_generation",
            "mcp:function_calling": "tool_use",
            "mcp:image_generation": "image_generation"
        }
        
        if mapping_key in default_mappings:
            return default_mappings[mapping_key]
        
        # If no mapping found, return original or raise exception based on default behavior
        if self.default_behavior == "pass_through":
            return capability
        else:
            raise ValueError(f"No mapping found for capability: {mapping_key}")
    
    def map_resource(self, resource, source_protocol, target_protocol):
        """Map a resource between protocols."""
        # Implementation for resource mapping
        # This would follow a similar pattern to capability mapping
        pass
```

### Configuration Example

```yaml
extensions:
  a2a_mcp_adapter:
    type: "protocol_adapter"
    name: "a2a_mcp_adapter"
    enabled: true
    options:
      source_protocol: "a2a"
      target_protocol: "mcp"
      mapping_rules:
        capabilities:
          - source: "tool_use"
            target: "function_calling"
          - source: "image_generation"
            target: "image_generation"
        message_types:
          - source: "text"
            target: "text"
          - source: "multipart"
            target: "multipart"
          - source: "action"
            target: "function"
        resources:
          - source: "image"
            target: "image_url"
      default_behavior: "pass_through"
```

## Standard Internal Message Format (SIMF)

The Standard Internal Message Format (SIMF) is the unified internal representation used by OpenMAS to process messages regardless of their original protocol. Protocol Adapters convert protocol-specific messages to and from this format.

The SIMF structure follows this basic schema:

```yaml
{
  "id": "unique-message-id",
  "timestamp": "2023-01-01T12:00:00Z",
  "protocol": "source-protocol",
  "message_type": "text|multipart|tool_call|etc",
  "payload": {
    "type": "text|multipart|tool_call|etc",
    "data": "string-content" | { ... } | [ ... ]
  },
  "metadata": {
    # Additional protocol-specific metadata
  }
}
```

Refer to the [Standard Internal Message Format](../../01_architecture/internal_message_format_standard.md) documentation for detailed specification.

## Best Practices

1. **Protocol Fidelity**: Preserve as much of the original message semantics as possible
2. **Graceful Degradation**: When a feature doesn't have a direct mapping, degrade gracefully
3. **Clear Error Handling**: Provide clear error messages for unmappable items
4. **Idempotency**: Ensure adapter operations are idempotent
5. **Metadata Preservation**: Maintain protocol-specific metadata when possible
6. **Versioning Support**: Be explicit about which protocol versions are supported

## Related Documentation

- [Extension System Design](../design/design_extension_system.md)
- [Protocol Adapter Design](../protocol_adapters/design_protocol_adapters.md)
- [Extension Development Guide](../development/guide.md)
- [Multi-Protocol Design](../../01_architecture/multi_protocol_design.md)
- [Standard Internal Message Format](../../01_architecture/internal_message_format_standard.md)