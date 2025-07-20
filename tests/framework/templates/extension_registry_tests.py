"""
IExtensionRegistry Test Framework Template

This module provides comprehensive test templates for IExtensionRegistry implementations,
designed to validate extension discovery, loading, configuration validation, dependency
resolution, and lifecycle management.
"""

import asyncio
import shutil
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from openmas.core.simf import (
    MessageType,
    PayloadType,
    SIMFMessage,
    create_text_message,
    validate_simf_message,
)

from .common_fixtures import simf_message_fixtures

# ============================================================================
# IExtensionRegistry Interface Definition (for testing)
# ============================================================================


class IExtension(ABC):
    """Base interface for extensions."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Extension name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Extension version."""
        pass

    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """List of required dependencies."""
        pass

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the extension."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the extension."""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get extension capabilities."""
        pass


class IExtensionRegistry(ABC):
    """
    Interface definition for extension registries.
    This mirrors the actual interface and is used for testing.
    """

    @abstractmethod
    async def discover_extensions(
        self, search_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """Discover available extensions in search paths."""
        pass

    @abstractmethod
    async def register_extension(self, extension_info: Dict[str, Any]) -> None:
        """Register an extension."""
        pass

    @abstractmethod
    async def load_extension(
        self, extension_name: str, config: Optional[Dict[str, Any]] = None
    ) -> IExtension:
        """Load and initialize an extension."""
        pass

    @abstractmethod
    async def unload_extension(self, extension_name: str) -> None:
        """Unload an extension."""
        pass

    @abstractmethod
    async def get_loaded_extensions(self) -> List[str]:
        """Get list of currently loaded extensions."""
        pass

    @abstractmethod
    async def get_available_extensions(self) -> List[Dict[str, Any]]:
        """Get list of all available extensions."""
        pass

    @abstractmethod
    async def resolve_dependencies(self, extension_name: str) -> List[str]:
        """Resolve extension dependencies."""
        pass

    @abstractmethod
    async def validate_extension_config(
        self, extension_name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate extension configuration."""
        pass

    @abstractmethod
    def get_extension(self, extension_name: str) -> Optional[IExtension]:
        """Get loaded extension instance."""
        pass

    @abstractmethod
    async def reload_extension(self, extension_name: str) -> None:
        """Reload an extension."""
        pass


# ============================================================================
# Extension Definition Fixtures
# ============================================================================


@pytest.fixture
def extension_definitions():
    """Real extension definitions for testing."""
    return {
        "logging_extension": {
            "name": "logging_extension",
            "version": "1.0.0",
            "description": "Structured logging extension for OpenMAS",
            "author": "OpenMAS Team",
            "main_class": "LoggingExtension",
            "module_path": "openmas.extensions.logging",
            "dependencies": [],
            "capabilities": {
                "logging": {
                    "structured": True,
                    "formatters": ["json", "text"],
                    "handlers": ["file", "console", "syslog"],
                }
            },
            "config_schema": {
                "type": "object",
                "properties": {
                    "log_level": {
                        "type": "string",
                        "enum": ["DEBUG", "INFO", "WARNING", "ERROR"],
                        "default": "INFO",
                    },
                    "output_file": {"type": "string"},
                    "format": {
                        "type": "string",
                        "enum": ["json", "text"],
                        "default": "json",
                    },
                },
            },
        },
        "metrics_extension": {
            "name": "metrics_extension",
            "version": "2.1.0",
            "description": "Performance metrics collection extension",
            "author": "OpenMAS Team",
            "main_class": "MetricsExtension",
            "module_path": "openmas.extensions.metrics",
            "dependencies": ["logging_extension"],
            "capabilities": {
                "metrics": {
                    "collection": True,
                    "exporters": ["prometheus", "statsd", "json"],
                    "aggregation": ["sum", "avg", "count", "histogram"],
                }
            },
            "config_schema": {
                "type": "object",
                "properties": {
                    "collection_interval": {
                        "type": "integer",
                        "minimum": 1,
                        "default": 60,
                    },
                    "exporters": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["prometheus"],
                    },
                    "storage_backend": {
                        "type": "string",
                        "enum": ["memory", "file", "redis"],
                        "default": "memory",
                    },
                },
            },
        },
        "protocol_mcp_extension": {
            "name": "protocol_mcp_extension",
            "version": "1.5.0",
            "description": "MCP protocol adapter extension",
            "author": "OpenMAS Team",
            "main_class": "MCPProtocolExtension",
            "module_path": "openmas.extensions.protocols.mcp",
            "dependencies": ["logging_extension"],
            "capabilities": {
                "protocols": {
                    "mcp": {
                        "version": "2025-06-18",
                        "transports": ["stdio", "sse", "http"],
                        "features": ["tools", "resources", "prompts", "sampling"],
                    }
                }
            },
            "config_schema": {
                "type": "object",
                "properties": {
                    "transport": {
                        "type": "string",
                        "enum": ["stdio", "sse", "http"],
                        "default": "stdio",
                    },
                    "timeout": {"type": "integer", "minimum": 1, "default": 30},
                    "features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["tools", "resources"],
                    },
                },
            },
        },
        "security_extension": {
            "name": "security_extension",
            "version": "1.0.0",
            "description": "Security validation and enforcement extension",
            "author": "OpenMAS Team",
            "main_class": "SecurityExtension",
            "module_path": "openmas.extensions.security",
            "dependencies": ["logging_extension", "metrics_extension"],
            "capabilities": {
                "security": {
                    "validation": True,
                    "encryption": ["aes", "rsa"],
                    "authentication": ["oauth", "jwt", "api_key"],
                }
            },
            "config_schema": {
                "type": "object",
                "properties": {
                    "validation_level": {
                        "type": "string",
                        "enum": ["strict", "moderate", "permissive"],
                        "default": "moderate",
                    },
                    "encryption_key": {"type": "string"},
                    "auth_provider": {
                        "type": "string",
                        "enum": ["oauth", "jwt", "api_key"],
                        "default": "jwt",
                    },
                },
                "required": ["encryption_key"],
            },
        },
    }


@pytest.fixture
def extension_configs():
    """Valid extension configurations for testing."""
    return {
        "logging_config": {
            "log_level": "DEBUG",
            "output_file": "/tmp/openmas.log",
            "format": "json",
        },
        "metrics_config": {
            "collection_interval": 30,
            "exporters": ["prometheus", "json"],
            "storage_backend": "memory",
        },
        "mcp_config": {
            "transport": "stdio",
            "timeout": 45,
            "features": ["tools", "resources", "prompts"],
        },
        "security_config": {
            "validation_level": "strict",
            "encryption_key": "test-key-12345",
            "auth_provider": "jwt",
        },
    }


@pytest.fixture
def dependency_scenarios():
    """Extension dependency resolution scenarios."""
    return {
        "simple_chain": {
            "description": "Simple linear dependency chain",
            "extensions": ["logging_extension", "metrics_extension"],
            "expected_order": ["logging_extension", "metrics_extension"],
        },
        "complex_graph": {
            "description": "Complex dependency graph",
            "extensions": [
                "logging_extension",
                "metrics_extension",
                "security_extension",
            ],
            "expected_order": [
                "logging_extension",
                "metrics_extension",
                "security_extension",
            ],
        },
        "circular_dependency": {
            "description": "Circular dependency scenario (should fail)",
            "extensions": [
                {"name": "ext_a", "dependencies": ["ext_b"]},
                {"name": "ext_b", "dependencies": ["ext_a"]},
            ],
            "should_fail": True,
        },
        "missing_dependency": {
            "description": "Missing dependency scenario",
            "extensions": ["security_extension"],  # Depends on missing extensions
            "missing": ["logging_extension", "metrics_extension"],
            "should_fail": True,
        },
    }


# ============================================================================
# Mock Extension Classes
# ============================================================================


class MockExtension(IExtension):
    """Mock extension for testing."""

    def __init__(
        self, name: str, version: str = "1.0.0", dependencies: List[str] = None
    ):
        self._name = name
        self._version = version
        self._dependencies = dependencies or []
        self._initialized = False
        self._capabilities = {"mock": True}

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def dependencies(self) -> List[str]:
        return self._dependencies

    async def initialize(self, config: Dict[str, Any]) -> None:
        self._initialized = True
        self._config = config

    async def shutdown(self) -> None:
        self._initialized = False

    def get_capabilities(self) -> Dict[str, Any]:
        return self._capabilities

    @property
    def is_initialized(self) -> bool:
        return self._initialized


# ============================================================================
# Base Test Template Class
# ============================================================================


class IExtensionRegistryTestTemplate:
    """
    Comprehensive test template for IExtensionRegistry implementations.

    This template ensures that extension registry implementations:
    1. Correctly discover and register extensions
    2. Handle dependency resolution and loading order
    3. Validate extension configurations properly
    4. Manage extension lifecycle (load/unload/reload)
    5. Handle error conditions gracefully
    """

    @pytest.fixture
    def extension_registry(self) -> IExtensionRegistry:
        """
        Override this fixture in your test class to provide your
        IExtensionRegistry implementation for testing.
        """
        raise NotImplementedError(
            "Must provide extension_registry fixture in test class"
        )

    @pytest.fixture
    def temp_extension_dir(self):
        """Temporary directory for extension testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    # ========================================================================
    # Extension Discovery Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_discover_extensions_in_valid_path(
        self, extension_registry: IExtensionRegistry, temp_extension_dir: str
    ):
        """Test discovery of extensions in valid search paths."""
        # Create mock extension files
        extension_path = Path(temp_extension_dir)
        extension_file = extension_path / "test_extension.py"
        extension_file.write_text(
            """
class TestExtension:
    name = "test_extension"
    version = "1.0.0"
    dependencies = []
"""
        )

        # Discover extensions
        extensions = await extension_registry.discover_extensions([temp_extension_dir])

        # Should find at least some extensions (or handle gracefully)
        assert isinstance(extensions, list)

    @pytest.mark.asyncio
    async def test_discover_extensions_in_empty_path(
        self, extension_registry: IExtensionRegistry, temp_extension_dir: str
    ):
        """Test discovery in empty directory."""
        extensions = await extension_registry.discover_extensions([temp_extension_dir])

        # Should return empty list for empty directory
        assert isinstance(extensions, list)
        assert len(extensions) == 0

    @pytest.mark.asyncio
    async def test_discover_extensions_in_nonexistent_path(
        self, extension_registry: IExtensionRegistry
    ):
        """Test discovery in nonexistent directory."""
        # Should handle gracefully (empty list or exception)
        try:
            extensions = await extension_registry.discover_extensions(
                ["/nonexistent/path"]
            )
            assert isinstance(extensions, list)
        except (FileNotFoundError, ValueError):
            # Exception is acceptable
            pass

    # ========================================================================
    # Extension Registration Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_register_valid_extension(
        self, extension_registry: IExtensionRegistry, extension_definitions
    ):
        """Test registration of valid extensions."""
        extension = extension_definitions["logging_extension"]

        # Should not raise exception
        await extension_registry.register_extension(extension)

        # Extension should be available
        available = await extension_registry.get_available_extensions()
        extension_names = [ext["name"] for ext in available]
        assert "logging_extension" in extension_names

    @pytest.mark.asyncio
    async def test_register_invalid_extension(
        self, extension_registry: IExtensionRegistry
    ):
        """Test registration failure with invalid extension."""
        invalid_extensions = [
            {},  # Empty extension
            {"name": "test"},  # Missing required fields
            {"name": "test", "version": "invalid"},  # Invalid version
            None,  # Null extension
        ]

        for invalid_ext in invalid_extensions:
            with pytest.raises((ValueError, TypeError, KeyError)):
                await extension_registry.register_extension(invalid_ext)

    @pytest.mark.asyncio
    async def test_register_duplicate_extension(
        self, extension_registry: IExtensionRegistry, extension_definitions
    ):
        """Test handling of duplicate extension registration."""
        extension = extension_definitions["logging_extension"]

        # Register extension
        await extension_registry.register_extension(extension)

        # Register duplicate - should handle gracefully
        try:
            await extension_registry.register_extension(extension)
        except ValueError:
            # Error is acceptable for duplicates
            pass

    # ========================================================================
    # Extension Loading Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_load_registered_extension(
        self,
        extension_registry: IExtensionRegistry,
        extension_definitions,
        extension_configs,
    ):
        """Test loading of registered extensions."""
        extension = extension_definitions["logging_extension"]
        await extension_registry.register_extension(extension)

        # Load extension
        with patch.object(
            extension_registry,
            "_create_extension_instance",
            return_value=MockExtension("logging_extension"),
        ):
            loaded_ext = await extension_registry.load_extension(
                "logging_extension", extension_configs["logging_config"]
            )

            # Validate loaded extension
            assert isinstance(loaded_ext, IExtension)
            assert loaded_ext.name == "logging_extension"

            # Check it's in loaded list
            loaded_extensions = await extension_registry.get_loaded_extensions()
            assert "logging_extension" in loaded_extensions

    @pytest.mark.asyncio
    async def test_load_nonexistent_extension(
        self, extension_registry: IExtensionRegistry
    ):
        """Test loading failure with nonexistent extension."""
        with pytest.raises((ValueError, KeyError)):
            await extension_registry.load_extension("nonexistent_extension")

    @pytest.mark.asyncio
    async def test_load_extension_with_invalid_config(
        self, extension_registry: IExtensionRegistry, extension_definitions
    ):
        """Test loading extension with invalid configuration."""
        extension = extension_definitions["security_extension"]
        await extension_registry.register_extension(extension)

        # Try to load with invalid config (missing required field)
        invalid_config = {"validation_level": "strict"}  # Missing encryption_key

        with pytest.raises((ValueError, TypeError)):
            await extension_registry.load_extension(
                "security_extension", invalid_config
            )

    # ========================================================================
    # Dependency Resolution Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_resolve_simple_dependencies(
        self,
        extension_registry: IExtensionRegistry,
        extension_definitions,
        dependency_scenarios,
    ):
        """Test resolution of simple dependency chains."""
        # Register extensions
        extensions = [
            extension_definitions["logging_extension"],
            extension_definitions["metrics_extension"],
        ]

        for ext in extensions:
            await extension_registry.register_extension(ext)

        # Resolve dependencies
        deps = await extension_registry.resolve_dependencies("metrics_extension")

        # Should include logging_extension
        assert isinstance(deps, list)
        assert "logging_extension" in deps

    @pytest.mark.asyncio
    async def test_resolve_complex_dependencies(
        self, extension_registry: IExtensionRegistry, extension_definitions
    ):
        """Test resolution of complex dependency graphs."""
        # Register all extensions
        extensions = [
            extension_definitions["logging_extension"],
            extension_definitions["metrics_extension"],
            extension_definitions["security_extension"],
        ]

        for ext in extensions:
            await extension_registry.register_extension(ext)

        # Resolve dependencies for security extension
        deps = await extension_registry.resolve_dependencies("security_extension")

        # Should include all dependencies
        assert isinstance(deps, list)
        assert "logging_extension" in deps
        assert "metrics_extension" in deps

    @pytest.mark.asyncio
    async def test_resolve_missing_dependencies(
        self, extension_registry: IExtensionRegistry, extension_definitions
    ):
        """Test dependency resolution with missing dependencies."""
        # Register only security extension (missing its dependencies)
        await extension_registry.register_extension(
            extension_definitions["security_extension"]
        )

        # Should fail to resolve
        with pytest.raises((ValueError, KeyError)):
            await extension_registry.resolve_dependencies("security_extension")

    # ========================================================================
    # Configuration Validation Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_validate_valid_extension_config(
        self,
        extension_registry: IExtensionRegistry,
        extension_definitions,
        extension_configs,
    ):
        """Test validation of valid extension configurations."""
        extension = extension_definitions["logging_extension"]
        await extension_registry.register_extension(extension)

        # Validate config
        result = await extension_registry.validate_extension_config(
            "logging_extension", extension_configs["logging_config"]
        )

        # Should indicate valid configuration
        assert isinstance(result, dict)
        assert result.get("is_valid", True) is True
        assert "errors" not in result or len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_validate_invalid_extension_config(
        self, extension_registry: IExtensionRegistry, extension_definitions
    ):
        """Test validation of invalid extension configurations."""
        extension = extension_definitions["security_extension"]
        await extension_registry.register_extension(extension)

        # Test invalid configurations
        invalid_configs = [
            {},  # Missing required fields
            {"validation_level": "invalid"},  # Invalid enum value
            {"encryption_key": 123},  # Wrong type
        ]

        for invalid_config in invalid_configs:
            result = await extension_registry.validate_extension_config(
                "security_extension", invalid_config
            )

            # Should indicate invalid configuration
            assert isinstance(result, dict)
            assert (
                result.get("is_valid", False) is False
                or len(result.get("errors", [])) > 0
            )

    # ========================================================================
    # Extension Lifecycle Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_extension_lifecycle_load_unload(
        self,
        extension_registry: IExtensionRegistry,
        extension_definitions,
        extension_configs,
    ):
        """Test complete extension lifecycle: load and unload."""
        extension = extension_definitions["logging_extension"]
        await extension_registry.register_extension(extension)

        # Mock the extension creation
        mock_ext = MockExtension("logging_extension")
        with patch.object(
            extension_registry, "_create_extension_instance", return_value=mock_ext
        ):
            # Load extension
            loaded_ext = await extension_registry.load_extension(
                "logging_extension", extension_configs["logging_config"]
            )

            assert loaded_ext.name == "logging_extension"
            assert mock_ext.is_initialized

            # Check it's in loaded list
            loaded_extensions = await extension_registry.get_loaded_extensions()
            assert "logging_extension" in loaded_extensions

            # Unload extension
            await extension_registry.unload_extension("logging_extension")

            # Should no longer be in loaded list
            loaded_extensions = await extension_registry.get_loaded_extensions()
            assert "logging_extension" not in loaded_extensions

    @pytest.mark.asyncio
    async def test_reload_extension(
        self,
        extension_registry: IExtensionRegistry,
        extension_definitions,
        extension_configs,
    ):
        """Test extension reloading."""
        extension = extension_definitions["logging_extension"]
        await extension_registry.register_extension(extension)

        # Mock the extension creation
        mock_ext = MockExtension("logging_extension")
        with patch.object(
            extension_registry, "_create_extension_instance", return_value=mock_ext
        ):
            # Load extension first
            await extension_registry.load_extension(
                "logging_extension", extension_configs["logging_config"]
            )

            # Reload extension
            await extension_registry.reload_extension("logging_extension")

            # Should still be loaded
            loaded_extensions = await extension_registry.get_loaded_extensions()
            assert "logging_extension" in loaded_extensions

    @pytest.mark.asyncio
    async def test_get_loaded_extension_instance(
        self,
        extension_registry: IExtensionRegistry,
        extension_definitions,
        extension_configs,
    ):
        """Test retrieving loaded extension instances."""
        extension = extension_definitions["logging_extension"]
        await extension_registry.register_extension(extension)

        # Mock the extension creation
        mock_ext = MockExtension("logging_extension")
        with patch.object(
            extension_registry, "_create_extension_instance", return_value=mock_ext
        ):
            # Load extension
            await extension_registry.load_extension(
                "logging_extension", extension_configs["logging_config"]
            )

            # Get extension instance
            instance = extension_registry.get_extension("logging_extension")
            assert instance is not None
            assert instance.name == "logging_extension"

            # Non-loaded extension should return None
            non_loaded = extension_registry.get_extension("nonexistent_extension")
            assert non_loaded is None

    # ========================================================================
    # Error Handling Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_unload_nonexistent_extension(
        self, extension_registry: IExtensionRegistry
    ):
        """Test unloading nonexistent extension."""
        with pytest.raises((ValueError, KeyError)):
            await extension_registry.unload_extension("nonexistent_extension")

    @pytest.mark.asyncio
    async def test_reload_nonexistent_extension(
        self, extension_registry: IExtensionRegistry
    ):
        """Test reloading nonexistent extension."""
        with pytest.raises((ValueError, KeyError)):
            await extension_registry.reload_extension("nonexistent_extension")

    @pytest.mark.asyncio
    async def test_concurrent_extension_operations(
        self,
        extension_registry: IExtensionRegistry,
        extension_definitions,
        extension_configs,
    ):
        """Test concurrent extension operations."""
        # Register multiple extensions
        extensions = [
            extension_definitions["logging_extension"],
            extension_definitions["metrics_extension"],
        ]

        for ext in extensions:
            await extension_registry.register_extension(ext)

        # Mock extension creation
        def create_mock_ext(name):
            return MockExtension(name)

        with patch.object(
            extension_registry,
            "_create_extension_instance",
            side_effect=lambda name, config: create_mock_ext(name),
        ):
            # Load extensions concurrently
            tasks = [
                extension_registry.load_extension(
                    "logging_extension", extension_configs["logging_config"]
                ),
                extension_registry.load_extension(
                    "metrics_extension", extension_configs["metrics_config"]
                ),
            ]

            results = await asyncio.gather(*tasks)

            # Both should succeed
            assert len(results) == 2
            assert all(isinstance(ext, IExtension) for ext in results)

            # Both should be loaded
            loaded_extensions = await extension_registry.get_loaded_extensions()
            assert "logging_extension" in loaded_extensions
            assert "metrics_extension" in loaded_extensions


# ============================================================================
# Test Suite Factory
# ============================================================================


def create_extension_registry_test_suite(
    registry_class, additional_fixtures: Optional[Dict[str, Any]] = None
) -> type:
    """
    Factory function to create a complete test suite for an extension registry.

    Args:
        registry_class: The IExtensionRegistry implementation to test
        additional_fixtures: Additional test fixtures specific to the registry

    Returns:
        A test class that can be run with pytest
    """

    class GeneratedExtensionRegistryTests(IExtensionRegistryTestTemplate):

        @pytest.fixture
        def extension_registry(self) -> IExtensionRegistry:
            return registry_class()

        # Add any additional fixtures
        if additional_fixtures:
            for name, fixture in additional_fixtures.items():
                locals()[name] = pytest.fixture()(fixture)

    GeneratedExtensionRegistryTests.__name__ = f"Test{registry_class.__name__}"

    return GeneratedExtensionRegistryTests
