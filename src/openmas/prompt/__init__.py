"""OpenMAS prompt management module.

This module provides prompt management functionality for OpenMAS agents,
allowing them to manage, version, and reuse prompts across different contexts.
"""

from typing import Any, Optional

from openmas.exceptions import ConfigurationError
from openmas.logging import get_logger
from openmas.prompt.base import (
    FileSystemPromptStorage,
    MemoryPromptStorage,
    Prompt,
    PromptContent,
    PromptManager,
    PromptMetadata,
    PromptStorage,
)

logger = get_logger(__name__)

# Check for MCP availability at module level to avoid repeated checks
HAS_MCP = False
try:
    from mcp.server.fastmcp import FastMCP

    HAS_MCP = True
except ImportError:
    pass


def get_prompt_manager(provider: Optional[str] = None, **kwargs: Any) -> PromptManager:
    """Get a prompt manager based on the specified provider.

    This function creates an appropriate prompt manager based on the provider name.
    It delegates to provider-specific managers as needed.

    Args:
        provider: The provider to use (None or "default" for base PromptManager, "mcp" for MCP integration)
        **kwargs: Additional arguments for the prompt manager

    Returns:
        A prompt manager instance

    Raises:
        ConfigurationError: If the provider is not supported
    """
    # If no provider specified or "default", return base PromptManager
    if provider is None or provider.lower() == "default":
        storage = kwargs.get("storage")
        prompts_base_path = kwargs.get("prompts_base_path")
        return PromptManager(storage=storage, prompts_base_path=prompts_base_path)

    # MCP provider - requires prompt_manager param for delegation
    elif provider.lower() == "mcp":
        if not HAS_MCP:
            logger.warning(
                "MCP provider requested but MCP is not installed. "
                "Install the MCP package with: pip install mcp>=1.7.0"
            )
            raise ConfigurationError("MCP provider requested but MCP is not installed")

        # Import here to avoid circular imports
        from openmas.prompt.providers.mcp import McpPromptManager

        # McpPromptManager requires a base prompt manager
        prompt_manager = kwargs.get("prompt_manager")
        if not prompt_manager:
            # Create a default prompt manager if not provided
            storage = kwargs.get("storage")
            prompts_base_path = kwargs.get("prompts_base_path")
            prompt_manager = PromptManager(storage=storage, prompts_base_path=prompts_base_path)

        return McpPromptManager(prompt_manager=prompt_manager)

    else:
        # Provider not supported
        raise ConfigurationError(f"Unsupported prompt manager provider: {provider}")


__all__ = [
    "Prompt",
    "PromptContent",
    "PromptManager",
    "PromptMetadata",
    "PromptStorage",
    "FileSystemPromptStorage",
    "MemoryPromptStorage",
    "get_prompt_manager",
]
