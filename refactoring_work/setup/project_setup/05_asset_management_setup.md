# Asset Management System Setup

## Task Overview
Setup the Asset Management System for OpenMAS 0.3.0, which handles model files, embeddings, asset versioning, and resource management across the multi-protocol, reasoning-agnostic architecture.

## Design Alignment
**Reference**: `/refactoring_work/design/01_architecture/components_summary.md` and `/refactoring_work/design/documentation_structure.md` section `10_asset_management/`
**Architecture**: Asset management provides centralized handling of models, embeddings, and other resources used by reasoning engines and protocol implementations.

## Tasks

1. Create Asset Management Directory Structure
   - Setup asset loading mechanisms
   - Create asset versioning system
   - Configure resource mapping and handling

2. Implement Asset Loading System
   - Model file loaders (various formats)
   - Embedding loaders and managers
   - Resource discovery mechanisms
   - Asset caching strategies

3. Setup Asset Versioning
   - Version tracking for assets
   - Asset update mechanisms
   - Rollback capabilities
   - Dependency management

4. Configure Asset Storage
   - Local storage backends
   - Remote storage integration
   - Asset synchronization
   - Storage optimization

## Directory Structure

```
src/openmas/asset_management/
├── __init__.py                     # Asset management module initialization
├── loaders/                        # Asset loading mechanisms
│   ├── __init__.py
│   ├── model_loaders/             # Model file loaders
│   │   ├── __init__.py
│   │   ├── huggingface_loader.py  # HuggingFace model loader
│   │   ├── onnx_loader.py         # ONNX model loader
│   │   ├── pytorch_loader.py      # PyTorch model loader
│   │   └── tensorflow_loader.py   # TensorFlow model loader
│   ├── embedding_loaders/         # Embedding loaders
│   │   ├── __init__.py
│   │   ├── vector_loader.py       # Vector embedding loader
│   │   ├── text_embeddings.py     # Text embedding loader
│   │   └── multimodal_loader.py   # Multimodal embedding loader
│   ├── resource_loaders/          # General resource loaders
│   │   ├── __init__.py
│   │   ├── file_loader.py         # File-based resource loader
│   │   ├── url_loader.py          # URL-based resource loader
│   │   └── stream_loader.py       # Streaming resource loader
│   └── discovery/                 # Asset discovery
│       ├── __init__.py
│       ├── local_discovery.py     # Local asset discovery
│       ├── remote_discovery.py    # Remote asset discovery
│       └── registry_discovery.py  # Registry-based discovery
├── versioning/                    # Asset versioning system
│   ├── __init__.py
│   ├── version_manager.py         # Version management
│   ├── asset_tracker.py          # Asset tracking
│   ├── dependency_resolver.py     # Dependency resolution
│   └── rollback_manager.py       # Rollback capabilities
├── storage/                       # Asset storage backends
│   ├── __init__.py
│   ├── local_storage.py          # Local file system storage
│   ├── remote_storage.py         # Remote storage (S3, GCS, etc.)
│   ├── cache_manager.py          # Asset caching
│   └── sync_manager.py           # Asset synchronization
├── registry/                      # Asset registry
│   ├── __init__.py
│   ├── asset_registry.py         # Central asset registry
│   ├── metadata_manager.py       # Asset metadata management
│   └── search_interface.py       # Asset search capabilities
└── integrations/                  # Integration with other components
    ├── __init__.py
    ├── reasoning_integration.py   # Integration with reasoning engines
    ├── protocol_integration.py    # Integration with protocols
    └── kr_integration.py          # Integration with KR&R system
```

## Key Implementation Files

### 1. Asset Registry (`registry/asset_registry.py`)

```python
"""
Central asset registry for OpenMAS Asset Management System.

Provides centralized tracking and discovery of all assets across the system.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import json

class AssetType(Enum):
    """Types of assets managed by the system."""
    MODEL = "model"
    EMBEDDING = "embedding"
    DATASET = "dataset"
    CONFIG = "config"
    RESOURCE = "resource"

@dataclass
class AssetMetadata:
    """Metadata for an asset."""
    asset_id: str
    name: str
    asset_type: AssetType
    version: str
    description: str
    tags: List[str]
    file_path: str
    file_hash: str
    size_bytes: int
    created_at: str
    updated_at: str
    dependencies: List[str]
    reasoning_engines: List[str]  # Compatible reasoning engines
    protocols: List[str]  # Compatible protocols

class AssetRegistry:
    """Central registry for all assets in the system."""

    def __init__(self):
        self._assets: Dict[str, AssetMetadata] = {}
        self._name_to_id: Dict[str, str] = {}
        self._type_index: Dict[AssetType, List[str]] = {}

    def register_asset(self, metadata: AssetMetadata) -> bool:
        """Register a new asset in the registry."""
        self._assets[metadata.asset_id] = metadata
        self._name_to_id[metadata.name] = metadata.asset_id

        # Update type index
        if metadata.asset_type not in self._type_index:
            self._type_index[metadata.asset_type] = []
        self._type_index[metadata.asset_type].append(metadata.asset_id)

        return True

    def get_asset(self, asset_id: str) -> Optional[AssetMetadata]:
        """Get asset metadata by ID."""
        return self._assets.get(asset_id)

    def get_asset_by_name(self, name: str) -> Optional[AssetMetadata]:
        """Get asset metadata by name."""
        asset_id = self._name_to_id.get(name)
        return self._assets.get(asset_id) if asset_id else None

    def list_assets_by_type(self, asset_type: AssetType) -> List[AssetMetadata]:
        """List all assets of a specific type."""
        asset_ids = self._type_index.get(asset_type, [])
        return [self._assets[asset_id] for asset_id in asset_ids]

    def search_assets(self, query: str, asset_type: Optional[AssetType] = None) -> List[AssetMetadata]:
        """Search assets by name, description, or tags."""
        results = []
        for asset in self._assets.values():
            if asset_type and asset.asset_type != asset_type:
                continue

            if (query.lower() in asset.name.lower() or
                query.lower() in asset.description.lower() or
                any(query.lower() in tag.lower() for tag in asset.tags)):
                results.append(asset)

        return results

# Global registry instance
asset_registry = AssetRegistry()
```

### 2. Model Loader (`loaders/model_loaders/huggingface_loader.py`)

```python
"""
HuggingFace model loader for OpenMAS Asset Management.

Provides loading capabilities for HuggingFace models with proper versioning and caching.
"""

from typing import Any, Dict, Optional
import os
from pathlib import Path

try:
    from transformers import AutoModel, AutoTokenizer
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

from ..base_loader import BaseAssetLoader
from ...registry.asset_registry import AssetMetadata, AssetType

class HuggingFaceModelLoader(BaseAssetLoader):
    """Loader for HuggingFace models."""

    def __init__(self, cache_dir: Optional[str] = None):
        super().__init__()
        self.cache_dir = cache_dir or os.path.expanduser("~/.openmas/models/huggingface")
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

    def can_load(self, asset_path: str) -> bool:
        """Check if this loader can handle the asset."""
        return HUGGINGFACE_AVAILABLE and (
            asset_path.startswith("huggingface://") or
            "huggingface.co" in asset_path
        )

    async def load_asset(self, asset_metadata: AssetMetadata) -> Any:
        """Load a HuggingFace model."""
        if not HUGGINGFACE_AVAILABLE:
            raise ImportError("transformers library not available")

        model_name = self._extract_model_name(asset_metadata.file_path)

        try:
            # Load model and tokenizer
            model = AutoModel.from_pretrained(
                model_name,
                cache_dir=self.cache_dir,
                trust_remote_code=False  # Security consideration
            )

            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=self.cache_dir,
                trust_remote_code=False
            )

            return {
                "model": model,
                "tokenizer": tokenizer,
                "model_name": model_name
            }

        except Exception as e:
            raise RuntimeError(f"Failed to load HuggingFace model {model_name}: {e}")

    def _extract_model_name(self, asset_path: str) -> str:
        """Extract model name from asset path."""
        if asset_path.startswith("huggingface://"):
            return asset_path.replace("huggingface://", "")
        elif "huggingface.co" in asset_path:
            # Extract from URL
            parts = asset_path.split("/")
            if len(parts) >= 2:
                return "/".join(parts[-2:])

        return asset_path
```

## Integration with Other Components

### 1. Reasoning Engine Integration

Assets integrate with reasoning engines through:

- **Model Loading**: Reasoning engines request models through the asset registry
- **Embedding Access**: Vector-based reasoning engines access embeddings
- **Resource Management**: Shared resources across reasoning approaches
- **Version Consistency**: Ensures consistent asset versions across reasoning engines

### 2. Protocol Integration

Assets integrate with protocols through:

- **A2A Agent Cards**: Model references in agent capability declarations
- **MCP Resources**: Assets exposed as MCP resources
- **HTTP Endpoints**: Asset serving through HTTP protocol
- **Asset Metadata**: Protocol-specific asset metadata exchange

## Configuration Integration

Asset management should be configured through the unified configuration schema:

```yaml
asset_management:
  storage:
    local_cache_dir: "~/.openmas/assets"
    remote_storage:
      type: "s3"  # or "gcs", "azure"
      bucket: "openmas-assets"
      region: "us-west-2"
  loaders:
    huggingface:
      enabled: true
      cache_dir: "~/.openmas/models/huggingface"
      trust_remote_code: false
    onnx:
      enabled: true
      optimization_level: "all"
  versioning:
    auto_versioning: true
    max_versions: 5
    cleanup_policy: "lru"
  registry:
    persistence: true
    backup_interval: "1h"
```

## Success Criteria
- Complete Asset Management directory structure created
- Asset registry with metadata management functional
- Model loaders for major formats implemented
- Asset versioning system operational
- Integration with reasoning engines and protocols established
- Configuration schema alignment maintained
- Caching and storage optimization working
