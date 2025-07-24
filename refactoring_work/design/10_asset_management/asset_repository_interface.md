# Asset Repository Interface

## Overview

The `IAssetRepository` interface defines the contract for low-level asset storage operations within the OpenMAS Asset Management system. This interface abstracts the underlying storage backend (filesystem, database, cloud storage, etc.) and provides a clean separation between high-level asset management logic (handled by `IAssetManager`) and raw data persistence.

## Interface Definition

```python
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, AsyncIterator
from pydantic import BaseModel
from datetime import datetime

class StoredAsset(BaseModel):
    """Represents an asset as stored in the repository."""
    uri: str
    content: bytes
    content_type: str
    size: int
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}

class AssetFilter(BaseModel):
    """Filter criteria for asset queries."""
    content_type_pattern: Optional[str] = None
    metadata_filters: Dict[str, Any] = {}
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    size_min: Optional[int] = None
    size_max: Optional[int] = None

class IAssetRepository(ABC):
    """
    Interface for low-level asset storage operations.
    
    This interface handles the raw persistence of asset data and metadata,
    abstracting the underlying storage backend from the high-level asset
    management logic.
    """

    @abstractmethod
    async def store_asset(self, uri: str, content: bytes, content_type: str, metadata: Dict[str, Any] = None) -> StoredAsset:
        """
        Store an asset in the repository.

        Args:
            uri: Unique identifier for the asset
            content: Raw asset content as bytes
            content_type: MIME type of the asset
            metadata: Optional metadata dictionary

        Returns:
            StoredAsset object with storage details

        Raises:
            AssetStorageError: If storage operation fails
            AssetAlreadyExistsError: If asset with URI already exists
        """
        pass

    @abstractmethod
    async def retrieve_asset(self, uri: str) -> Optional[StoredAsset]:
        """
        Retrieve an asset from the repository.

        Args:
            uri: Unique identifier for the asset

        Returns:
            StoredAsset object if found, None otherwise

        Raises:
            AssetStorageError: If retrieval operation fails
        """
        pass

    @abstractmethod
    async def update_asset(self, uri: str, content: Optional[bytes] = None, content_type: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Optional[StoredAsset]:
        """
        Update an existing asset in the repository.

        Args:
            uri: Unique identifier for the asset
            content: New content (if provided)
            content_type: New content type (if provided)
            metadata: New metadata (if provided, replaces existing metadata)

        Returns:
            Updated StoredAsset object if asset exists, None otherwise

        Raises:
            AssetStorageError: If update operation fails
        """
        pass

    @abstractmethod
    async def delete_asset(self, uri: str) -> bool:
        """
        Delete an asset from the repository.

        Args:
            uri: Unique identifier for the asset

        Returns:
            True if asset was deleted, False if asset didn't exist

        Raises:
            AssetStorageError: If deletion operation fails
        """
        pass

    @abstractmethod
    async def asset_exists(self, uri: str) -> bool:
        """
        Check if an asset exists in the repository.

        Args:
            uri: Unique identifier for the asset

        Returns:
            True if asset exists, False otherwise

        Raises:
            AssetStorageError: If existence check fails
        """
        pass

    @abstractmethod
    async def list_assets(self, filter_criteria: Optional[AssetFilter] = None, limit: Optional[int] = None, offset: int = 0) -> List[str]:
        """
        List asset URIs matching the given criteria.

        Args:
            filter_criteria: Optional filter to apply
            limit: Maximum number of URIs to return
            offset: Number of URIs to skip

        Returns:
            List of asset URIs

        Raises:
            AssetStorageError: If listing operation fails
        """
        pass

    @abstractmethod
    async def search_assets(self, filter_criteria: AssetFilter) -> AsyncIterator[StoredAsset]:
        """
        Search for assets matching the given criteria.

        Args:
            filter_criteria: Filter criteria to apply

        Yields:
            StoredAsset objects matching the criteria

        Raises:
            AssetStorageError: If search operation fails
        """
        pass

    @abstractmethod
    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dictionary containing storage statistics (total_assets, total_size, etc.)

        Raises:
            AssetStorageError: If stats retrieval fails
        """
        pass

    @abstractmethod
    async def cleanup_orphaned_assets(self, referenced_uris: List[str]) -> int:
        """
        Remove assets that are not in the provided reference list.

        Args:
            referenced_uris: List of URIs that should be preserved

        Returns:
            Number of assets cleaned up

        Raises:
            AssetStorageError: If cleanup operation fails
        """
        pass
```

## Exception Classes

```python
class AssetStorageError(Exception):
    """Base exception for asset storage operations."""
    pass

class AssetAlreadyExistsError(AssetStorageError):
    """Raised when attempting to store an asset that already exists."""
    pass
```

## Design Principles

### 1. Storage Backend Abstraction
The interface abstracts all storage implementation details, allowing for different backends (filesystem, database, cloud storage) without changing the high-level asset management logic.

### 2. Async Operations
All operations are asynchronous to support non-blocking I/O operations, which is crucial for scalable asset management.

### 3. Rich Metadata Support
The interface supports arbitrary metadata storage alongside asset content, enabling flexible asset organization and search capabilities.

### 4. Efficient Querying
The `AssetFilter` model provides structured query capabilities, and the `search_assets` method returns an async iterator for memory-efficient processing of large result sets.

### 5. Maintenance Operations
The interface includes maintenance operations like `get_storage_stats` and `cleanup_orphaned_assets` to support operational concerns.

## Relationship to IAssetManager

The `IAssetRepository` serves as the storage layer for the `IAssetManager`. The asset manager handles:
- High-level asset lifecycle management
- Asset validation and processing
- Caching and performance optimization
- Business logic and access control

While the repository handles:
- Raw data persistence
- Storage backend abstraction
- Low-level query operations
- Storage maintenance tasks

This separation allows the asset management system to be both flexible in its storage options and maintainable in its business logic.
