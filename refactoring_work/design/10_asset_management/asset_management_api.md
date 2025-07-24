# IAssetManager Interface

## 1. Overview

The Asset Management system provides a standardized framework for registering, storing, retrieving, and managing the lifecycle of assets used by agents within the OpenMAS ecosystem. Assets can include a wide range of resources, such as machine learning models, datasets, prompt templates, configuration files, or any other digital artifact an agent might need to perform its tasks.

The `IAssetManager` interface is the primary entry point for all asset-related operations, ensuring a consistent and secure approach to asset handling across the platform.

## 2. Core Concepts

- **Asset**: A single, versioned resource identified by a unique URI. An asset consists of its binary data and associated metadata.
- **Asset URI (Uniform Resource Identifier)**: A unique identifier for an asset, typically following a scheme like `openmas://<asset_name>:<version>`.
- **Metadata**: A set of key-value pairs describing an asset, including its name, version, type, creator, and other relevant information.
- **Asset Bundle**: A collection of related assets grouped together for a specific purpose, such as for a particular agent or task. Bundles are defined by a manifest file.

## 2.1 Architecture: Manager and Repository Separation

The Asset Management system follows a layered architecture with clear separation of concerns:

- **`IAssetManager`**: Provides high-level asset lifecycle management, including:
  - Asset validation and processing
  - Business logic and access control
  - Caching and performance optimization
  - Asset URI generation and management
  - Metadata enrichment and validation

- **`IAssetRepository`**: Handles low-level storage operations, including:
  - Raw data persistence to storage backends
  - Storage backend abstraction (filesystem, database, cloud storage)
  - Low-level query and search operations
  - Storage maintenance and cleanup tasks

This separation allows the asset management system to be both flexible in its storage options and maintainable in its business logic. The `IAssetManager` delegates all storage operations to an `IAssetRepository` implementation, ensuring clean architectural boundaries.

For the complete `IAssetRepository` interface definition, see [`asset_repository_interface.md`](./asset_repository_interface.md).

## 3. Data Models

We use Pydantic models to define the structure of our asset-related data.

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class AssetMetadata(BaseModel):
    """Defines the metadata for an asset."""
    asset_id: str = Field(..., description="Unique identifier for the asset.")
    name: str = Field(..., description="The human-readable name of the asset.")
    version: str = Field(..., description="The version of the asset (e.g., '1.0.0', 'latest').")
    asset_type: str = Field(..., description="The type of asset (e.g., 'model', 'dataset', 'prompt_template').")
    description: Optional[str] = Field(None, description="A brief description of the asset.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of asset creation.")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization and search.")
    owner_agent_id: Optional[str] = Field(None, description="The ID of the agent that owns this asset.")

class Asset:
    """Represents a downloadable asset, including its metadata and a way to access its content."""
    metadata: AssetMetadata

    @abstractmethod
    async def read_content(self) -> bytes:
        """Reads and returns the binary content of the asset."""
        pass

```

## 4. IAssetManager Interface Definition

```python
class IAssetManager(ABC):
    """A formal interface for managing the lifecycle of digital assets."""

    @abstractmethod
    async def register_asset(
        self, 
        content: bytes, 
        metadata: AssetMetadata
    ) -> str:
        """Registers a new asset with the system.

        Args:
            content: The binary content of the asset.
            metadata: The metadata describing the asset.

        Returns:
            The unique URI of the newly registered asset.
        """
        pass

    @abstractmethod
    async def get_asset(self, asset_uri: str) -> Optional[Asset]:
        """Retrieves an asset by its unique URI.

        Args:
            asset_uri: The URI of the asset to retrieve (e.g., 'openmas://my_model:1.0').

        Returns:
            An Asset object if found, otherwise None.
        """
        pass

    @abstractmethod
    async def find_assets(
        self, 
        name: Optional[str] = None, 
        asset_type: Optional[str] = None, 
        tags: Optional[List[str]] = None
    ) -> List[AssetMetadata]:
        """Finds assets based on metadata criteria.

        Args:
            name: The name of the assets to find.
            asset_type: The type of assets to find.
            tags: A list of tags to match.

        Returns:
            A list of metadata objects for assets that match the criteria.
        """
        pass

    @abstractmethod
    async def delete_asset(self, asset_uri: str) -> bool:
        """Deletes an asset from the system.

        Args:
            asset_uri: The URI of the asset to delete.

        Returns:
            True if the asset was deleted successfully, False otherwise.
        """
        pass

    @abstractmethod
    async def update_asset_metadata(self, asset_uri: str, new_metadata: Dict[str, Any]) -> bool:
        """Updates the metadata of an existing asset.

        Args:
            asset_uri: The URI of the asset to update.
            new_metadata: A dictionary of metadata fields to update.

        Returns:
            True if the metadata was updated successfully, False otherwise.
        """
        pass
```

## 5. Example Usage

```python
import asyncio

# Conceptual example of an agent using the asset manager
async def agent_work(asset_manager: IAssetManager):
    # 1. Register a new prompt template
    prompt_template = "You are a helpful assistant. The user asks: {user_query}"
    prompt_metadata = AssetMetadata(
        asset_id="prompt-template-1",
        name="basic_assistant_prompt",
        version="1.0",
        asset_type="prompt_template",
        tags=["llm", "assistant"]
    )
    
    uri = await asset_manager.register_asset(
        content=prompt_template.encode('utf-8'),
        metadata=prompt_metadata
    )
    print(f"Registered prompt template with URI: {uri}")

    # 2. Find assets by type
    print("\nFinding all prompt templates...")
    prompt_assets_meta = await asset_manager.find_assets(asset_type="prompt_template")
    for meta in prompt_assets_meta:
        print(f"- Found: {meta.name}, version {meta.version}")

    # 3. Retrieve a specific asset
    print(f"\nRetrieving asset: {uri}")
    retrieved_asset = await asset_manager.get_asset(uri)
    if retrieved_asset:
        content = await retrieved_asset.read_content()
        print(f"Retrieved content: '{content.decode('utf-8')}'")

    # 4. Delete the asset
    print(f"\nDeleting asset: {uri}")
    success = await asset_manager.delete_asset(uri)
    if success:
        print("Asset deleted successfully.")

```
