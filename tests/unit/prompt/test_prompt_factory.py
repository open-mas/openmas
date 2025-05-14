"""Unit tests for the prompt manager factory."""

from unittest.mock import MagicMock, patch

import pytest

from openmas.exceptions import ConfigurationError
from openmas.prompt import PromptManager, get_prompt_manager
from openmas.prompt.providers.mcp import McpPromptManager


class TestGetPromptManager:
    """Test the get_prompt_manager factory function."""

    def test_default_provider(self):
        """Test getting the default prompt manager."""
        manager = get_prompt_manager()
        assert isinstance(manager, PromptManager)
        assert not isinstance(manager, McpPromptManager)

    def test_explicit_default_provider(self):
        """Test getting the default prompt manager with explicit provider."""
        manager = get_prompt_manager(provider="default")
        assert isinstance(manager, PromptManager)
        assert not isinstance(manager, McpPromptManager)

    def test_default_with_params(self):
        """Test getting the default prompt manager with parameters."""
        storage = MagicMock()
        manager = get_prompt_manager(storage=storage, prompts_base_path="/path/to/prompts")
        assert isinstance(manager, PromptManager)
        assert manager.storage == storage
        assert manager.prompts_base_path == "/path/to/prompts"

    def test_unsupported_provider(self):
        """Test getting an unsupported provider raises an error."""
        with pytest.raises(ConfigurationError, match="Unsupported prompt manager provider"):
            get_prompt_manager(provider="unsupported")

    @patch("openmas.prompt.HAS_MCP", True)
    def test_mcp_provider_with_prompt_manager(self):
        """Test getting the MCP prompt manager with an existing prompt manager."""
        prompt_manager = MagicMock()
        manager = get_prompt_manager(provider="mcp", prompt_manager=prompt_manager)
        assert isinstance(manager, McpPromptManager)
        assert manager._delegate == prompt_manager

    @patch("openmas.prompt.HAS_MCP", True)
    def test_mcp_provider_without_prompt_manager(self):
        """Test getting the MCP prompt manager without an explicit prompt manager."""
        manager = get_prompt_manager(provider="mcp")
        assert isinstance(manager, McpPromptManager)
        assert isinstance(manager._delegate, PromptManager)

    @patch("openmas.prompt.HAS_MCP", False)
    def test_mcp_provider_without_mcp_installed(self):
        """Test getting the MCP prompt manager without MCP installed raises an error."""
        with pytest.raises(ConfigurationError, match="MCP provider requested but MCP is not installed"):
            get_prompt_manager(provider="mcp")
