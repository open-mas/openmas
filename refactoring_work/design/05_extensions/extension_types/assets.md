# Asset Extensions

## Overview

Asset extensions provide mechanisms for handling different types of assets and resources across all protocols in OpenMAS. These extensions maintain the framework's core architectural principles of reasoning agnosticism and protocol independence while providing efficient and consistent asset management.

## Extension Type Definition

- **Name**: Asset Extensions
- **Purpose**: Manage and provide access to various types of assets and resources
- **Component**: Asset Management
- **Type**: Extension
- **Community Usage**: Enable developers to add support for custom asset types and storage mechanisms
- **Protocol Compatibility**: All protocols (A2A, MCP, HTTP, MQTT, gRPC)

## Key Capabilities

Asset extensions provide these core capabilities:

1. **Protocol-Independent Asset Access** - Consistent access to assets across protocols
2. **Custom Asset Type Support** - Add support for specialized asset types
3. **Storage Provider Integration** - Connect to various storage backends
4. **Asset Transformation** - Convert assets between different formats
5. **Asset Caching** - Optimize performance through strategic caching
6. **Protocol-Specific Adaptations** - Adapt assets to protocol-specific requirements

## Asset Extension Types

### 1. Asset Providers

Asset providers supply assets from specific sources:

```python
from openmas.extensions import AssetProviderExtension

class FileSystemAssetProvider(AssetProviderExtension):
    """Provider for file system assets."""
    
    extension_type = "asset_provider"
    extension_name = "filesystem_provider"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.base_directory = config.get("base_directory", "./assets")
    
    async def initialize(self):
        """Initialize the provider."""
        # Ensure the directory exists
        os.makedirs(self.base_directory, exist_ok=True)
        self.initialized = True
    
    async def get_asset(self, asset_id, asset_type=None):
        """Get an asset by ID."""
        asset_path = os.path.join(self.base_directory, asset_id)
        
        if not os.path.exists(asset_path):
            return None
        
        with open(asset_path, "rb") as f:
            content = f.read()
        
        return {
            "id": asset_id,
            "type": asset_type or self._guess_type(asset_id),
            "content": content
        }
    
    async def list_assets(self, asset_type=None):
        """List available assets."""
        assets = []
        
        for filename in os.listdir(self.base_directory):
            file_type = self._guess_type(filename)
            if asset_type is None or file_type == asset_type:
                assets.append({
                    "id": filename,
                    "type": file_type
                })
        
        return assets
    
    def _guess_type(self, filename):
        """Guess the asset type from the filename."""
        if filename.endswith(".txt"):
            return "text"
        elif filename.endswith(".json"):
            return "json"
        elif filename.endswith((".jpg", ".jpeg", ".png")):
            return "image"
        else:
            return "binary"
```

### 2. Asset Processors

Asset processors transform assets between formats:

```python
from openmas.extensions import AssetProcessorExtension

class ImageProcessorExtension(AssetProcessorExtension):
    """Extension for processing image assets."""
    
    extension_type = "asset_processor"
    extension_name = "image_processor"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
    
    async def initialize(self):
        """Initialize the processor."""
        # Import image processing libraries
        try:
            import PIL.Image
            self.pil = PIL.Image
            self.initialized = True
        except ImportError:
            raise RuntimeError("PIL is required for ImageProcessorExtension")
    
    async def process(self, asset, options=None):
        """Process an image asset."""
        options = options or {}
        
        # Verify asset type
        if asset["type"] not in ["image/png", "image/jpeg", "image/jpg"]:
            raise ValueError(f"Unsupported image type: {asset['type']}")
        
        # Load image
        img = self.pil.open(BytesIO(asset["content"]))
        
        # Apply transformations
        if "resize" in options:
            width = options["resize"].get("width")
            height = options["resize"].get("height")
            if width and height:
                img = img.resize((width, height))
            
        if "format" in options:
            fmt = options["format"]
            # Convert to new format
            output = BytesIO()
            img.save(output, format=fmt)
            
            return {
                "id": asset["id"],
                "type": f"image/{fmt.lower()}",
                "content": output.getvalue()
            }
            
        # Return the processed asset
        output = BytesIO()
        img.save(output, format=img.format)
        
        return {
            "id": asset["id"],
            "type": asset["type"],
            "content": output.getvalue()
        }
```

### 3. Asset Converters

Asset converters adapt assets between protocols:

```python
from openmas.extensions import AssetConverterExtension

class MCPResourceConverterExtension(AssetConverterExtension):
    """Converts assets to MCP resources."""
    
    extension_type = "asset_converter"
    extension_name = "mcp_resource_converter"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
    
    async def convert_to_protocol(self, asset, protocol, options=None):
        """Convert an asset to protocol format."""
        options = options or {}
        
        if protocol == "mcp":
            return await self._convert_to_mcp(asset, options)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
    
    async def convert_from_protocol(self, protocol_asset, protocol, options=None):
        """Convert from protocol format to asset."""
        options = options or {}
        
        if protocol == "mcp":
            return await self._convert_from_mcp(protocol_asset, options)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
    
    async def _convert_to_mcp(self, asset, options):
        """Convert an asset to MCP resource."""
        asset_type = asset["type"]
        
        if asset_type.startswith("text"):
            # Convert to MCP text resource
            return {
                "type": "text",
                "text": asset["content"].decode("utf-8") if isinstance(asset["content"], bytes) else asset["content"]
            }
            
        elif asset_type.startswith("image"):
            # Convert to MCP image resource
            import base64
            content = asset["content"]
            if isinstance(content, bytes):
                encoded = base64.b64encode(content).decode("ascii")
            else:
                encoded = content
                
            return {
                "type": "image",
                "image": {
                    "data": encoded,
                    "mime_type": asset_type
                }
            }
            
        else:
            # Generic binary data
            import base64
            encoded = base64.b64encode(asset["content"]).decode("ascii")
            
            return {
                "type": "file",
                "file": {
                    "data": encoded,
                    "mime_type": asset_type or "application/octet-stream"
                }
            }
    
    async def _convert_from_mcp(self, mcp_resource, options):
        """Convert from MCP resource to asset."""
        if mcp_resource["type"] == "text":
            return {
                "id": options.get("id", str(uuid.uuid4())),
                "type": "text/plain",
                "content": mcp_resource["text"]
            }
            
        elif mcp_resource["type"] == "image":
            import base64
            decoded = base64.b64decode(mcp_resource["image"]["data"])
            
            return {
                "id": options.get("id", str(uuid.uuid4())),
                "type": mcp_resource["image"].get("mime_type", "image/jpeg"),
                "content": decoded
            }
            
        elif mcp_resource["type"] == "file":
            import base64
            decoded = base64.b64decode(mcp_resource["file"]["data"])
            
            return {
                "id": options.get("id", str(uuid.uuid4())),
                "type": mcp_resource["file"].get("mime_type", "application/octet-stream"),
                "content": decoded
            }
```

## Extension Configuration

Asset extensions are configured through the unified configuration schema. For complete schema information, refer to the [Extension Configuration Schema](/03_configuration/schema/extensions.md#asset-extensions):

```yaml
extensions:
  filesystem_asset_provider:
    type: "asset_provider"
    name: "filesystem_provider"
    enabled: true
    options:
      base_directory: "/path/to/assets"
      cache:
        enabled: true
        max_size: 100  # MB
        ttl: 3600  # seconds
  
  image_processor:
    type: "asset_processor"
    name: "image_processor"
    enabled: true
    options:
      default_format: "JPEG"
      quality: 85
```

## Supported Asset Types

Asset extensions can handle these standard types:

1. **Text Documents** - Structured or unstructured text content
2. **Images** - Various image formats (PNG, JPEG, SVG, etc.)
3. **Audio** - Sound files for voice or other audio content
4. **Video** - Motion picture content in various formats
5. **Structured Data** - JSON, XML, or other structured formats
6. **Binary Files** - Generic binary data
7. **Models** - Machine learning models and weights
8. **Embeddings** - Vector representations for semantic operations

## Protocol Mapping

Asset extensions provide consistent mappings between OpenMAS assets and protocol-specific formats:

### A2A Protocol Mapping

```yaml
asset_mapping:
  a2a:
    text:
      capability: "asset_content"
      format: "text"
    image:
      capability: "asset_content"
      format: "base64"
    file:
      capability: "asset_content"
      format: "base64"
```

### MCP Protocol Mapping

```yaml
asset_mapping:
  mcp:
    text:
      resource_type: "text"
    image:
      resource_type: "image"
    file:
      resource_type: "file"
```

## Implementation Example

Using asset extensions in code:

```python
# Get asset provider extension
asset_provider = extension_registry.get_extension(
    "asset_provider", 
    "filesystem_provider"
)

# Get an asset
asset = await asset_provider.get_asset("example.jpg")

# Process the asset using an extension
image_processor = extension_registry.get_extension(
    "asset_processor",
    "image_processor"
)

processed_asset = await image_processor.process(
    asset,
    options={
        "resize": {
            "width": 800,
            "height": 600
        },
        "format": "PNG"
    }
)

# Convert to protocol format
converter = extension_registry.get_extension(
    "asset_converter",
    "mcp_resource_converter"
)

mcp_resource = await converter.convert_to_protocol(
    processed_asset, 
    "mcp"
)
```

## Reasoning Agnosticism

Asset extensions maintain OpenMAS's reasoning agnosticism by:

1. **Content Agnosticism** - Extensions handle assets without interpreting their meaning
2. **Protocol Independence** - Assets work consistently across all protocols
3. **Abstract Interfaces** - Extensions expose abstract interfaces regardless of reasoning approach
4. **Adapters and Converters** - Adapters bridge between assets and reasoning-specific requirements

This enables agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to work with the same assets consistently.
