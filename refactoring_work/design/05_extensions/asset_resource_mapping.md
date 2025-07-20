# Unified Asset and Resource Management Standard

## Definition
- **Name**: Unified Asset Management
- **Purpose**: Standardized approach to handling assets consistently across protocol interfaces
- **Protocol Compatibility**: Ensures seamless content handling with A2A, MCP, and extension protocols
- **Reasoning Agnosticism**: Maintains separation between content handling and reasoning approaches

## Assets and Resources Schema

```yaml
# Standardized unified asset management configuration schema
type: object
properties:
  # Global asset management configuration
  asset_management:
    type: object
    description: "Global asset management configuration"
    properties:
      enabled:
        type: boolean
        description: "Whether unified asset management is enabled"
        default: true

      # Universal asset handling
      asset_handling:
        type: object
        description: "How to handle assets across protocols"
        properties:
          default_strategy:
            type: string
            description: "Default strategy for asset handling"
            enum: ["inline", "reference", "hybrid"]
            default: "hybrid"
          max_inline_size_kb:
            type: integer
            description: "Maximum size in KB to transfer inline"
            default: 64
          cache_enabled:
            type: boolean
            description: "Whether to cache assets/resources"
            default: true
          cache_ttl_seconds:
            type: integer
            description: "Time to live for cached assets/resources in seconds"
            default: 3600
          cleanup_interval:
            type: integer
            description: "Cleanup interval for asset cache in seconds"
            default: 300

      # Protocol representation configuration
      protocol_representation:
        type: object
        description: "How assets are represented in different protocols"
        properties:
          content_handling:
            type: object
            description: "How to handle different content types"
            properties:
              text:
                type: object
                description: "How to handle text content"
                properties:
                  representation:
                    type: string
                    description: "Default representation method"
                    enum: ["inline", "reference", "hybrid"]
                    default: "inline"
                  mcp_resource_type:
                    type: string
                    description: "MCP resource type to use"
                    enum: ["text", "file"]
                    default: "text"
                  a2a_part_type:
                    type: string
                    description: "A2A part type to use"
                    enum: ["text", "data", "file"]
                    default: "text"
              image:
                type: object
                description: "How to handle image content"
                properties:
                  representation:
                    type: string
                    description: "Default representation method"
                    enum: ["inline", "reference", "hybrid"]
                    default: "hybrid"
                  mcp_resource_type:
                    type: string
                    description: "MCP resource type to use"
                    enum: ["image", "file"]
                    default: "image"
                  a2a_part_type:
                    type: string
                    description: "A2A part type to use"
                    enum: ["file"]
                    default: "file"
              file:
                type: object
                description: "How to handle file content"
                properties:
                  representation:
                    type: string
                    description: "Default representation method"
                    enum: ["inline", "reference", "hybrid"]
                    default: "reference"
                  mcp_resource_type:
                    type: string
                    description: "MCP resource type to use"
                    enum: ["file"]
                    default: "file"
                  a2a_part_type:
                    type: string
                    description: "A2A part type to use"
                    enum: ["file"]
                    default: "file"
              data:
                type: object
                description: "How to handle structured data content"
                properties:
                  representation:
                    type: string
                    description: "Default representation method"
                    enum: ["inline", "reference", "hybrid"]
                    default: "inline"
                  mcp_resource_type:
                    type: string
                    description: "MCP resource type to use"
                    enum: ["text", "data"]
                    default: "text"
                  a2a_part_type:
                    type: string
                    description: "A2A part type to use"
                    enum: ["data", "text"]
                    default: "data"
              mime_type_mapping:
                type: object
                description: "Mapping of MIME types to resource types"
                properties:
                  "image/*":
                    type: string
                    description: "Resource type for images"
                    default: "image"
                  "audio/*":
                    type: string
                    description: "Resource type for audio"
                    default: "audio"
                  "video/*":
                    type: string
                    description: "Resource type for video"
                    default: "video"
                  "application/json":
                    type: string
                    description: "Resource type for JSON"
                    default: "text"
                  "text/*":
                    type: string
                    description: "Resource type for text"
                    default: "text"
                  "application/octet-stream":
                    type: string
                    description: "Resource type for binary data"
                    default: "file"

      # Environmental Configuration
      environment:
        type: object
        description: "Environmental configuration for asset/resource mapping"
        properties:
          storage_path:
            type: string
            description: "Path for storing assets/resources"
            default: "./assets"
          url_base:
            type: string
            description: "Base URL for accessing assets/resources"
          temp_storage_ttl_seconds:
            type: integer
            description: "Time to live for temporary storage in seconds"
            default: 3600
```

## Protocol-Specific Implementation Details

### MCP Resource System

MCP defines several core resource types:

1. **Text Resource**
   ```json
   {
     "id": "resource_123",
     "type": "text",
     "metadata": {
       "content_type": "text/plain",
       "name": "Example Text"
     }
   }
   ```

2. **File Resource**
   ```json
   {
     "id": "resource_456",
     "type": "file",
     "metadata": {
       "content_type": "application/pdf",
       "name": "document.pdf",
       "size_bytes": 1024000
     }
   }
   ```

3. **Image Resource**
   ```json
   {
     "id": "resource_789",
     "type": "image",
     "metadata": {
       "content_type": "image/jpeg",
       "width": 1920,
       "height": 1080
     }
   }
   ```

### A2A Message Part System

A2A uses message parts for content:

1. **Text Part**
   ```json
   {
     "type": "text",
     "text": "This is a text message part"
   }
   ```

2. **File Part**
   ```json
   {
     "type": "file",
     "file": {
       "mime_type": "application/pdf",
       "file_name": "document.pdf",
       "data": "base64-encoded-data-or-null",
       "uri": "https://example.com/document.pdf"
     }
   }
   ```

3. **Data Part**
   ```json
   {
     "type": "data",
     "data": {
       "key": "value",
       "nested": {"property": 123}
     }
   }
   ```

## Asset Representation Across Protocols

The unified asset system provides consistent asset handling across all protocol interfaces:

### Asset Content Types and Protocol Representations

| OpenMAS Asset Type | MCP Representation | A2A Representation | HTTP Representation | gRPC Representation |
|--------------------|-------------------|-------------------|---------------------|--------------------|
| Text | `text` resource | Text part | Text response | String |
| Image | `image` resource | File part | Binary response | Bytes |
| File | `file` resource | File part | Binary response | Bytes |
| Structured Data | `text` resource (JSON) | Data part | JSON response | Struct |
| URL | `url` resource | File part (with URI) | Redirect | String |

Rather than "mapping" between protocols, OpenMAS represents assets consistently across all protocol interfaces enabled for an agent.

### 2. Content-Based Mapping

Makes mapping decisions based on the content:

1. **Size-Based Logic**
   - Small content (<64KB) → Inline
   - Large content → Reference

2. **Mime-Type Logic**
   - Text-based types → Text parts/resources
   - Binary types → File parts/resources
   - JSON/structured → Data parts or text resources (with JSON)

### 3. Hybrid Mapping

Uses the most efficient approach depending on context:

1. For real-time interactions:
   - Prefer inline for fast access
   - Small files embedded directly

2. For asynchronous or large data:
   - Prefer references
   - Pass URIs instead of content

## OpenMAS Asset Integration

### Asset System Bridge

OpenMAS provides an asset bridge that maps between its internal asset system and protocol-specific representations:

```python
# Example bridge implementation
class AssetProtocolBridge:
    async def asset_to_mcp_resource(self, asset_id: str) -> str:
        """Convert an OpenMAS asset to an MCP resource.

        Returns the MCP resource ID.
        """
        asset = await self.asset_manager.get_asset(asset_id)
        resource_id = f"resource_{uuid.uuid4().hex}"

        # Register with MCP resource registry based on asset type
        if asset.type == "text":
            await self.mcp_registry.register_text_resource(
                resource_id,
                asset.content,
                metadata=asset.metadata
            )
        elif asset.type == "image":
            await self.mcp_registry.register_image_resource(
                resource_id,
                asset.content_url or asset.content,
                metadata=asset.metadata
            )
        elif asset.type == "file":
            await self.mcp_registry.register_file_resource(
                resource_id,
                asset.content_url or asset.content,
                metadata=asset.metadata
            )

        # Store mapping for future reference
        self.asset_resource_map[asset_id] = resource_id
        return resource_id

    async def asset_to_a2a_part(self, asset_id: str) -> Dict[str, Any]:
        """Convert an OpenMAS asset to an A2A message part."""
        asset = await self.asset_manager.get_asset(asset_id)

        if asset.type == "text":
            return {
                "type": "text",
                "text": asset.content
            }
        elif asset.type in ["image", "file"]:
            return {
                "type": "file",
                "file": {
                    "mime_type": asset.metadata.get("content_type", "application/octet-stream"),
                    "file_name": asset.metadata.get("name", f"{asset.id}.bin"),
                    "data": asset.content if asset.size_bytes < self.max_inline_size else None,
                    "uri": asset.content_url if asset.content_url else None
                }
            }
        elif asset.type == "data":
            return {
                "type": "data",
                "data": json.loads(asset.content) if isinstance(asset.content, str) else asset.content
            }
```

## Reasoning Agnostic Asset Management

OpenMAS maintains reasoning agnosticism in asset handling through several approaches:

1. **Protocol Adapters**: Asset transformations happen at the communication layer, independent of reasoning approach
2. **Content Type Independence**: Assets can be used by any reasoning approach (LLM, rule-based, BDI, etc.)
3. **Unified Asset References**: All reasoning approaches reference assets through the same ID system
4. **Clean Asset API**: The asset API provides a clean interface that any reasoning approach can use

This design ensures that different reasoning approaches (LLM, symbolic, hybrid, etc.) can all work with the same assets while the protocol-specific handling happens at the communication layer.

## Example Configurations

### Multi-Protocol Asset Configuration

```yaml
# Unified asset configuration for an agent with multiple protocol interfaces
asset_management:
  enabled: true
  asset_handling:
    default_strategy: "hybrid"
    max_inline_size_kb: 64
    cache_enabled: true

  protocol_representation:
    content_handling:
      text:
        representation: "inline"
        mcp_resource_type: "text"
        a2a_part_type: "text"
      image:
        representation: "hybrid"
        mcp_resource_type: "image"
        a2a_part_type: "file"
      file:
        representation: "reference"
        mcp_resource_type: "file"
        a2a_part_type: "file"
      data:
        representation: "inline"
        mcp_resource_type: "text"
        a2a_part_type: "data"
```

### Large File Handling Configuration

```yaml
# Configuration optimized for large file handling
asset_management:
  enabled: true
  asset_handling:
    default_strategy: "reference"
    max_inline_size_kb: 32
    storage_path: "/data/assets"
    url_base: "https://assets.example.com"

  # File-specific optimizations
  protocol_representation:
    content_handling:
      file:
        representation: "reference"
        generate_presigned_urls: true
        url_expiration_seconds: 3600
```

## Extension Points for Custom Protocol Packages

The unified asset system provides extension points for third-party protocol packages:

```yaml
# Extension for MQTT protocol package
asset_management:
  extensions:
    mqtt:
      enabled: true
      topics:
        assets: "openmas/assets/{asset_id}"
      payload_format: "json"  # or binary, text
      qos: 1
      content_handling:
        text:
          representation: "inline"
          topic_pattern: "openmas/assets/text/{asset_id}"
        binary:
          representation: "reference"
          topic_pattern: "openmas/assets/binary/{asset_id}"
```

```yaml
# Extension for gRPC protocol package
asset_management:
  extensions:
    grpc:
      enabled: true
      streaming_threshold_kb: 64
      content_handling:
        text: "string_field"
        image: "bytes_stream"
        file: "bytes_stream"
        data: "struct_field"
```

These extension points allow protocol packages to integrate with the unified asset system while maintaining OpenMAS's reasoning agnosticism.
