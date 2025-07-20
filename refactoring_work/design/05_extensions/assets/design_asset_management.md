# Asset Management System Design

## Overview

The OpenMAS Asset Management system provides a unified approach to handling assets and resources across all protocols and components. It ensures consistent asset representation, efficient transfer strategies, and protocol-agnostic access while preserving OpenMAS's core architectural principles of reasoning agnosticism and multi-protocol support.

## Core Principles

1. **Protocol Independence**: Assets are managed consistently across all protocols (MCP, A2A, HTTP, etc.)
2. **Transfer Strategy Optimization**: Intelligent selection between inline, reference, and hybrid approaches
3. **Consistent Representation**: Standardized asset representation regardless of origin
4. **Efficient Caching**: Optimized resource utilization through strategic caching
5. **Reasoning Agnosticism**: Asset handling is independent of reasoning approaches
6. **Extensible Format Support**: Support for various asset types and formats

## Asset Types

OpenMAS supports these standard asset types:

1. **Text Documents** - Structured or unstructured text content
2. **Images** - Various image formats (PNG, JPEG, SVG, etc.)
3. **Audio** - Sound files for voice or other audio content
4. **Video** - Motion picture content in various formats
5. **Structured Data** - JSON, XML, or other structured formats
6. **Binary Files** - Generic binary data
7. **Models** - Machine learning models and weights
8. **Embeddings** - Vector representations for semantic operations

## Architecture Implementation

### AssetManager Class

The `AssetManager` coordinates asset operations across the system:

```python
class AssetManager:
    """Central manager for assets across protocols."""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.providers = {}
        self.converters = {}
        self.cache = AssetCache(config)

        # Initialize asset providers
        self._initialize_providers()

        # Initialize protocol converters
        self._initialize_converters()

    def _initialize_providers(self):
        """Initialize asset providers from configuration."""
        providers_config = self.config.get("providers", [])
        for provider_config in providers_config:
            provider_type = provider_config["type"]
            provider_name = provider_config["name"]
            provider = self._create_provider(provider_type, provider_config)
            self.providers[provider_name] = provider

    def _initialize_converters(self):
        """Initialize protocol converters."""
        converters_config = self.config.get("protocol_representation", {})
        for protocol, converter_config in converters_config.items():
            converter = AssetProtocolConverter(protocol, converter_config)
            self.converters[protocol] = converter

    def _create_provider(self, provider_type, config):
        """Create an asset provider of the specified type."""
        if provider_type == "file_system":
            return FileSystemProvider(config)
        elif provider_type == "http":
            return HttpProvider(config)
        elif provider_type == "s3":
            return S3Provider(config)
        elif provider_type == "database":
            return DatabaseProvider(config)
        else:
            # Use extension system to find provider
            return self._get_extension_provider(provider_type, config)

    def _get_extension_provider(self, provider_type, config):
        """Get provider from extension system."""
        # Implementation for finding provider in extensions
        pass

    async def get_asset(self, asset_id, options=None):
        """Get an asset by ID."""
        # Check cache first
        cached_asset = self.cache.get(asset_id, options)
        if cached_asset:
            return cached_asset

        # Determine provider from asset ID
        provider_name, local_id = self._parse_asset_id(asset_id)
        if provider_name not in self.providers:
            raise ValueError(f"Unknown asset provider: {provider_name}")

        # Get from provider
        provider = self.providers[provider_name]
        asset = await provider.get_asset(local_id, options)

        # Cache the asset
        self.cache.store(asset_id, asset, options)

        return asset

    def _parse_asset_id(self, asset_id):
        """Parse an asset ID into provider and local ID."""
        # Format: provider:local_id
        parts = asset_id.split(":", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid asset ID format: {asset_id}")

        return parts[0], parts[1]

    async def convert_for_protocol(self, asset, protocol, options=None):
        """Convert an asset for a specific protocol."""
        if protocol not in self.converters:
            raise ValueError(f"No converter for protocol: {protocol}")

        converter = self.converters[protocol]
        return await converter.convert(asset, options)

    async def store_asset(self, asset, provider_name=None, options=None):
        """Store an asset and return its ID."""
        # Use default provider if none specified
        if not provider_name:
            provider_name = self.config.get("default_provider", "file_system")

        if provider_name not in self.providers:
            raise ValueError(f"Unknown asset provider: {provider_name}")

        # Store with provider
        provider = self.providers[provider_name]
        local_id = await provider.store_asset(asset, options)

        # Form full asset ID
        asset_id = f"{provider_name}:{local_id}"

        # Cache the asset
        self.cache.store(asset_id, asset, options)

        return asset_id
```

### Asset Provider Interface

Asset providers implement a common interface for retrieving assets:

```python
class AssetProvider:
    """Base class for asset providers."""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config

    async def get_asset(self, asset_id, options=None):
        """Get an asset by ID."""
        raise NotImplementedError("Subclasses must implement get_asset")

    async def store_asset(self, asset, options=None):
        """Store an asset and return its ID."""
        raise NotImplementedError("Subclasses must implement store_asset")

    async def delete_asset(self, asset_id):
        """Delete an asset by ID."""
        raise NotImplementedError("Subclasses must implement delete_asset")

    async def list_assets(self, prefix=None, limit=100, offset=0):
        """List assets, optionally filtered by prefix."""
        raise NotImplementedError("Subclasses must implement list_assets")
```

### Protocol Converters

Protocol converters translate assets to protocol-specific formats:

```python
class AssetProtocolConverter:
    """Converts assets to protocol-specific formats."""

    def __init__(self, protocol, config):
        """Initialize for a specific protocol."""
        self.protocol = protocol
        self.config = config

        # Default handlers based on asset type
        self.handlers = {
            "text": self._convert_text,
            "image": self._convert_image,
            "audio": self._convert_audio,
            "video": self._convert_video,
            "structured_data": self._convert_structured_data,
            "binary": self._convert_binary,
            "model": self._convert_model,
            "embedding": self._convert_embedding,
        }

    async def convert(self, asset, options=None):
        """Convert an asset to this protocol's format."""
        asset_type = asset.get("type", "binary")

        # Get handler for this asset type
        handler = self.handlers.get(asset_type, self._convert_binary)

        # Convert using handler
        return await handler(asset, options)

    async def _convert_text(self, asset, options):
        """Convert text asset to protocol format."""
        # Protocol-specific implementation
        pass

    async def _convert_image(self, asset, options):
        """Convert image asset to protocol format."""
        # Protocol-specific implementation
        pass

    # Additional conversion methods for other asset types...
```

### Asset Cache

The cache optimizes resource usage and performance:

```python
class AssetCache:
    """Cache for assets to improve performance."""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.enabled = config.get("cache_enabled", True)
        self.ttl = config.get("cache_ttl_seconds", 3600)
        self.max_size = config.get("max_cache_size_mb", 100) * 1024 * 1024
        self.cleanup_interval = config.get("cleanup_interval", 300)

        # Initialize cache storage
        self.cache = {}
        self.size = 0
        self.last_access = {}

        # Start cleanup task if enabled
        if self.enabled:
            self._start_cleanup_task()

    def get(self, asset_id, options=None):
        """Get an asset from cache if available."""
        if not self.enabled:
            return None

        cache_key = self._get_cache_key(asset_id, options)
        if cache_key not in self.cache:
            return None

        # Update last access time
        self.last_access[cache_key] = time.time()

        return self.cache[cache_key]

    def store(self, asset_id, asset, options=None):
        """Store an asset in cache."""
        if not self.enabled:
            return

        cache_key = self._get_cache_key(asset_id, options)

        # Calculate asset size
        asset_size = self._calculate_asset_size(asset)

        # Check if we need to make room
        if self.size + asset_size > self.max_size:
            self._evict_entries(asset_size)

        # Store in cache
        self.cache[cache_key] = asset
        self.size += asset_size
        self.last_access[cache_key] = time.time()

    def _calculate_asset_size(self, asset):
        """Calculate the size of an asset in bytes."""
        # Implementation for size calculation
        pass

    def _evict_entries(self, needed_space):
        """Evict entries to make room for new assets."""
        # Implementation for cache eviction strategy
        pass

    def _get_cache_key(self, asset_id, options):
        """Generate a cache key from asset ID and options."""
        if not options:
            return asset_id

        # Create stable key from options
        options_key = json.dumps(options, sort_keys=True)
        return f"{asset_id}:{options_key}"

    def _start_cleanup_task(self):
        """Start the periodic cleanup task."""
        # Implementation for cleanup task
        pass
```

## Protocol-Specific Implementations

### MCP Resource Conversion

Converting assets to MCP resources:

```python
class MCPResourceConverter(AssetProtocolConverter):
    """Converts assets to MCP resources."""

    async def _convert_text(self, asset, options):
        """Convert text asset to MCP resource."""
        return {
            "type": "text",
            "content": asset["content"],
            "metadata": self._prepare_metadata(asset)
        }

    async def _convert_image(self, asset, options):
        """Convert image asset to MCP resource."""
        # Determine transfer strategy
        strategy = self._get_transfer_strategy(asset, options)

        if strategy == "inline":
            # Return inline image data
            return {
                "type": "image",
                "content": base64.b64encode(asset["content"]).decode("utf-8"),
                "metadata": {
                    **self._prepare_metadata(asset),
                    "encoding": "base64",
                    "mime_type": asset.get("mime_type", "image/png")
                }
            }
        else:
            # Return reference to image
            return {
                "type": "image",
                "content_ref": asset["id"],
                "metadata": {
                    **self._prepare_metadata(asset),
                    "mime_type": asset.get("mime_type", "image/png"),
                    "fetch_url": self._generate_fetch_url(asset["id"])
                }
            }

    def _get_transfer_strategy(self, asset, options):
        """Determine transfer strategy based on asset and options."""
        # Get size in KB
        size_kb = len(asset["content"]) / 1024

        # Get max inline size
        max_inline = options.get("max_inline_size_kb") or self.config.get("max_inline_size_kb", 64)

        # Use inline if under max size
        if size_kb <= max_inline:
            return "inline"
        else:
            return "reference"

    def _prepare_metadata(self, asset):
        """Prepare metadata for MCP resource."""
        metadata = asset.get("metadata", {}).copy()

        # Add asset ID to metadata
        if "id" in asset:
            metadata["asset_id"] = asset["id"]

        return metadata

    def _generate_fetch_url(self, asset_id):
        """Generate URL for fetching asset content."""
        base_url = self.config.get("fetch_base_url", "/assets")
        return f"{base_url}/{asset_id}"
```

### A2A Message Part Conversion

Converting assets to A2A message parts:

```python
class A2APartConverter(AssetProtocolConverter):
    """Converts assets to A2A message parts."""

    async def _convert_text(self, asset, options):
        """Convert text asset to A2A part."""
        return {
            "type": "text",
            "content": asset["content"],
            "metadata": self._prepare_metadata(asset)
        }

    async def _convert_image(self, asset, options):
        """Convert image asset to A2A part."""
        # Determine transfer strategy
        strategy = self._get_transfer_strategy(asset, options)

        if strategy == "inline":
            # Return inline image data
            return {
                "type": "image",
                "content": base64.b64encode(asset["content"]).decode("utf-8"),
                "metadata": {
                    **self._prepare_metadata(asset),
                    "encoding": "base64",
                    "mime_type": asset.get("mime_type", "image/png")
                }
            }
        else:
            # Return reference to image
            return {
                "type": "file",
                "content_uri": self._generate_content_uri(asset["id"]),
                "metadata": {
                    **self._prepare_metadata(asset),
                    "mime_type": asset.get("mime_type", "image/png"),
                    "original_asset_id": asset["id"]
                }
            }

    def _generate_content_uri(self, asset_id):
        """Generate URI for asset content."""
        base_uri = self.config.get("content_base_uri", "asset://")
        return f"{base_uri}{asset_id}"
```

## Configuration Example

```yaml
# Global asset management configuration
asset_management:
  enabled: true

  # Asset handling strategies
  asset_handling:
    default_strategy: "hybrid"
    max_inline_size_kb: 64
    cache_enabled: true
    cache_ttl_seconds: 3600
    max_cache_size_mb: 100
    cleanup_interval: 300

  # Protocol-specific representation
  protocol_representation:
    mcp:
      fetch_base_url: "/api/assets"
      inline_preference: "image,text"
      reference_preference: "audio,video,model"

    a2a:
      content_base_uri: "asset://"
      max_inline_size_kb: 32

    http:
      serve_path: "/assets"
      content_disposition: "inline"

    mqtt:
      max_message_size_kb: 256
      chunking_enabled: true

  # Asset providers
  providers:
    - type: "file_system"
      name: "local"
      config:
        base_path: "./assets"
        directory_structure: "type/hash"

    - type: "http"
      name: "remote"
      config:
        base_url: "https://assets.example.com"

    - type: "s3"
      name: "cloud"
      config:
        bucket: "openmas-assets"
        region: "us-west-2"
        prefix: "assets/"

  # Default provider for new assets
  default_provider: "local"

  # Environment configuration
  environment:
    storage_path: "./storage"
    temp_path: "./temp"
    public_url: "https://example.com/assets"
```

## Asset ID Format

Asset IDs follow a standardized format:

```
provider:type:identifier
```

For example:
- `local:image:a1b2c3d4e5f6` - A local image with hash a1b2c3d4e5f6
- `cloud:model:gpt-4` - A model named gpt-4 in cloud storage
- `remote:text:document123` - A text document with ID document123 from a remote source

## Multi-Protocol Support

The asset management system ensures consistency across protocols by:

1. **Unified Representation**: All assets have a consistent internal representation
2. **Protocol-Specific Converters**: Assets are converted to appropriate formats for each protocol
3. **Transfer Strategy Selection**: Intelligent selection between inline and reference approaches
4. **URI/URL Generation**: Protocol-appropriate identifiers are generated for asset references
5. **Format Adaptation**: Assets are adapted to the capabilities of each protocol

## Reasoning Agnosticism

The asset management system maintains OpenMAS's reasoning agnosticism by:

1. **Interface Consistency**: Providing consistent access regardless of reasoning approach
2. **Content Neutrality**: Supporting assets for any reasoning paradigm (symbolic, neural, hybrid)
3. **Representation Independence**: Separating asset handling from reasoning processing
4. **Capability Exposure**: Exposing asset capabilities consistently across reasoning approaches

This asset management design provides a flexible foundation for handling diverse content types across all OpenMAS protocols and reasoning approaches.
