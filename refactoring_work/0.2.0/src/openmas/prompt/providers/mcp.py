"""MCP integration for prompt management.

This module provides integration with the Model Context Protocol (MCP) version 1.7+,
allowing OpenMAS prompts to be used with MCP services.
"""

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

import structlog

from openmas.prompt.base import Prompt, PromptManager, PromptMetadata

# Configure logging
logger = structlog.get_logger(__name__)

# Type for generic return values
T = TypeVar("T")

# Flag to track MCP availability
HAS_MCP = False

# Import MCP types and handle import errors
try:
    # Import core MCP modules for version 1.7+
    import mcp.server.fastmcp  # type: ignore[import]
    import mcp.server.fastmcp.prompts.base  # type: ignore[import]
    import mcp.types  # type: ignore[import]

    # Define variables in a way that makes mypy happy
    _McpPrompt = mcp.server.fastmcp.prompts.base.Prompt
    _FastMCP = mcp.server.fastmcp.FastMCP
    _TextContent = mcp.types.TextContent

    HAS_MCP = True
    logger.debug("MCP imported successfully")
except ImportError as e:
    logger.debug(f"MCP import failed: {e}")

    # Create stub classes that will never be used at runtime (only for type checking)
    _McpPrompt = None  # type: ignore
    _FastMCP = None  # type: ignore
    _TextContent = None  # type: ignore


class McpPromptManager(PromptManager):
    """MCP integration for prompt management.

    This class provides integration with the Model Context Protocol (MCP) version 1.7+,
    allowing OpenMAS prompts to be used with MCP services.
    """

    def __init__(self, prompt_manager: PromptManager) -> None:
        """Initialize the MCP prompt manager.

        Args:
            prompt_manager: The underlying prompt manager to use
        """
        super().__init__(storage=prompt_manager.storage, prompts_base_path=prompt_manager.prompts_base_path)
        self._delegate = prompt_manager

    async def get_prompt(self, prompt_id: str) -> Prompt | None:
        """Get a prompt by ID.

        Args:
            prompt_id: The ID of the prompt to get.

        Returns:
            The prompt, or None if not found.
        """
        return await self._delegate.get_prompt(prompt_id)

    async def get_prompt_by_name(self, name: str) -> Prompt | None:
        """Get a prompt by name.

        Args:
            name: The name of the prompt to get

        Returns:
            The prompt with the given name, or None if not found
        """
        return await self._delegate.get_prompt_by_name(name)

    async def list_prompts(self, tag: str | None = None) -> list[PromptMetadata]:
        """List available prompts.

        Args:
            tag: Optional tag to filter by.

        Returns:
            List of prompt metadata.
        """
        return await self._delegate.list_prompts(tag)

    async def render_prompt(
        self,
        prompt_identifier: str,
        context: dict[str, Any] | None = None,
        system_override: str | None = None,
    ) -> dict[str, Any] | None:
        """Render a prompt with context.

        Args:
            prompt_identifier: The ID or Name of the prompt to render.
            context: Optional context to use for rendering.
            system_override: Optional system prompt override.

        Returns:
            The rendered prompt as a dictionary with system and content fields,
            or None if the prompt was not found.
        """
        return await self._delegate.render_prompt(
            prompt_identifier=prompt_identifier,
            context=context,
            system_override=system_override,
        )

    async def register_all_prompts_with_server(self, server: Any, tag: str | None = None) -> list[str]:
        """Register all prompts with an MCP server.

        Args:
            server: The MCP server to register prompts with
            tag: Optional tag to filter prompts by

        Returns:
            List of registered prompt names
        """
        if not HAS_MCP:
            logger.warning(
                "MCP is not installed but was requested for prompt registration. "
                "Install the MCP package with: pip install mcp>=1.7.0"
            )
            return []

        # Check if the server supports registering prompts via add_prompt method
        if not hasattr(server, "add_prompt") or not callable(server.add_prompt):
            logger.warning(
                "Server does not support registering prompts via add_prompt method. "
                "This is required for MCP 1.7+ integration."
            )
            return []

        # Get all available prompts
        prompt_metadatas = await self.list_prompts(tag)
        registered_prompt_names = []

        # Register each prompt with the server
        for metadata in prompt_metadatas:
            # Load the prompt
            prompt = await self.get_prompt_by_name(metadata.name)
            if not prompt:
                logger.warning(f"Could not load prompt {metadata.id}")
                continue

            try:
                # Create a prompt function that will return MCP-compatible messages
                prompt_fn = await self._create_prompt_function(metadata.name)
                if not prompt_fn:
                    logger.warning(f"Could not create prompt function for {metadata.name}")
                    continue

                # Create MCP Prompt object using the MCP SDK's interface
                if HAS_MCP:
                    # Import and use the actual MCP types
                    from mcp.server.fastmcp.prompts.base import Prompt as McpPrompt  # type: ignore[import]

                    mcp_prompt = McpPrompt.from_function(  # type: ignore[attr-defined]
                        fn=prompt_fn,
                        name=metadata.name,
                        description=metadata.description or "",
                    )

                    # Add the prompt to the MCP server, handling different types of add_prompt methods
                    success = False
                    add_prompt_method = server.add_prompt

                    # Is it an awaitable?
                    if asyncio.iscoroutinefunction(add_prompt_method):
                        # Direct awaitable function
                        result = await add_prompt_method(mcp_prompt)
                        success = result is not False  # Only consider explicit False as failure
                    else:
                        # Regular synchronous call
                        result = add_prompt_method(mcp_prompt)
                        # Some implementations might return a boolean success indicator
                        success = result is not False

                    if success:
                        # Add to registered names if successful
                        registered_prompt_names.append(metadata.name)
                        logger.info(f"Registered prompt {metadata.name} with MCP server")
                    else:
                        logger.warning(f"Failed to register prompt {metadata.name} with MCP server")
            except Exception as e:
                logger.error(f"Error registering prompt {metadata.name}: {str(e)}")
                # Do not add to registered_prompt_names when an exception occurs

        return registered_prompt_names

    async def _create_prompt_function(self, prompt_name: str) -> Callable | None:
        """Create a function compatible with MCP prompt system.

        This creates a function that returns prompt messages in the format
        expected by the MCP framework.

        Args:
            prompt_name: The name of the prompt to use

        Returns:
            A function that can be used with MCP prompt system, or None if the prompt doesn't exist
        """
        if not HAS_MCP:
            return None

        # Check if the prompt exists first
        prompt = await self.get_prompt_by_name(prompt_name)
        if not prompt:
            logger.warning(f"Prompt not found: {prompt_name}")
            return None

        # Import the necessary MCP type only when needed (within the function)
        # This ensures the import is only attempted when HAS_MCP is True
        from mcp.types import TextContent  # type: ignore[import]

        # Define an async function that returns MCP-compatible message format
        async def prompt_function(**kwargs: Any) -> list[dict[str, Any]]:
            """MCP prompt function that returns formatted messages.

            Returns:
                List of messages in MCP format
            """
            # Extract context from kwargs
            context = kwargs.get("context", {})

            # Convert context object to dict if needed
            if not isinstance(context, dict):
                context = {
                    key: getattr(context, key)
                    for key in dir(context)
                    if not key.startswith("_") and not callable(getattr(context, key))
                }

            # Render the prompt with provided context
            result = await self.render_prompt(
                prompt_identifier=prompt_name,
                context=context,
            )

            if not result:
                raise ValueError(f"Error rendering prompt: {prompt_name}")

            # Convert to MCP message format
            messages = []

            # Add system message if present
            if "system" in result and result["system"]:
                messages.append({"role": "user", "content": TextContent(type="text", text=str(result["system"]))})

            # Add content/template if present
            if "content" in result and result["content"]:
                messages.append({"role": "user", "content": TextContent(type="text", text=str(result["content"]))})

            return messages

        return prompt_function

    async def create_prompt_handler(
        self, prompt_name: str, system_prompt_override: str | None = None
    ) -> Callable[[Any], Coroutine[Any, Any, str]] | None:
        """Create a handler function for an MCP prompt.

        This creates a function that can be used to render a prompt on-demand
        with the context passed by the MCP server.

        Args:
            prompt_name: The name of the prompt to use
            system_prompt_override: Optional override for the system prompt

        Returns:
            An async function that can be used as an MCP prompt handler, or None if MCP isn't installed
        """
        if not HAS_MCP:
            logger.warning(
                "MCP is not installed but was requested for prompt handling. "
                "Install the MCP package with: pip install mcp>=1.7.0"
            )
            return None

        # Check if the prompt exists
        prompt_fn = await self._create_prompt_function(prompt_name)
        if not prompt_fn:
            # Generate a fallback handler that returns an error message
            async def error_handler(context: Any) -> str:
                """Handle a prompt request for a non-existent prompt.

                Args:
                    context: The MCP context (ignored)

                Returns:
                    Error message
                """
                return f"Prompt not found: {prompt_name}"

            return error_handler

        async def prompt_handler(context: Any) -> str:
            """Handle a prompt request.

            Args:
                context: The MCP context (dict-like in MCP 1.7+)

            Returns:
                The rendered prompt
            """
            # Extract context variables - in MCP 1.7+ context is dict-like
            context_vars = {}
            if isinstance(context, dict):
                # Standard MCP 1.7+ context
                context_vars = context
            else:
                # Try to extract attributes as a fallback
                for key in dir(context):
                    if not key.startswith("_") and not callable(getattr(context, key)):
                        context_vars[key] = getattr(context, key)

            # Get the prompt again (need the full prompt object for the handler)
            prompt = await self.get_prompt_by_name(prompt_name)
            if not prompt:
                return f"Prompt not found: {prompt_name}"

            # Render the prompt with the context
            result = await self.render_prompt(
                prompt_identifier=prompt.id,
                context=context_vars,
                system_override=system_prompt_override,
            )

            if not result:
                return "Error rendering prompt"

            # Combine system prompt and content for rendering
            combined_result = ""

            # Add system prompt if available
            if "system" in result and result["system"]:
                combined_result += str(result["system"])

            # Add content/template if available
            if "content" in result and result["content"]:
                if combined_result:
                    combined_result += "\n\n"
                combined_result += str(result["content"])

            if not combined_result:
                return "No content available"

            return combined_result

        return prompt_handler
