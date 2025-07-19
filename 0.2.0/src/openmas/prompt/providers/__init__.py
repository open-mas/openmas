"""Provider implementations for the OpenMAS prompt module.

This package contains provider-specific implementations of the PromptManager interface,
allowing OpenMAS to integrate with various prompt management systems.
"""

from openmas.prompt.providers.mcp import McpPromptManager

__all__ = [
    "McpPromptManager",
]
