# IPromptManager Interface

## 1. Overview

The `IPromptManager` provides a specialized, high-level interface for managing and rendering prompt templates. While prompt templates are stored and retrieved as generic assets via the `IAssetManager`, the `IPromptManager` adds the critical capability of rendering these templates with dynamic context, making them ready for use by a reasoning engine (e.g., an LLM).

This separation of concerns allows the `IAssetManager` to remain a generic content-addressable storage system, while the `IPromptManager` focuses exclusively on the logic of prompt preparation.

## 2. Relationship to IAssetManager

- The `IPromptManager` is a consumer of the `IAssetManager`.
- It uses the `IAssetManager` to fetch the raw content of prompt templates, which are identified by their asset URIs.
- It assumes that prompt templates are stored as assets with the type `prompt_template`.

## 3. Data Models

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# Depends on the IAssetManager being defined elsewhere
# from ..asset_management.asset_management_api import IAssetManager

class PromptTemplate(BaseModel):
    """Represents a prompt template retrieved from the asset manager."""
    uri: str = Field(..., description="The unique asset URI of the prompt template.")
    content: str = Field(..., description="The raw, unformatted content of the template.")
    variables: list[str] = Field(..., description="A list of variables expected by the template (e.g., ['user_query', 'history']).")

class RenderedPrompt(BaseModel):
    """Represents a prompt that has been rendered with context."""
    uri: str = Field(..., description="The URI of the template used.")
    content: str = Field(..., description="The final, formatted prompt string.")
    context: Dict[str, Any] = Field(..., description="The context variables used for rendering.")

```

## 4. IPromptManager Interface Definition

```python
class IPromptManager(ABC):
    """A formal interface for fetching, rendering, and managing prompt templates."""

    def __init__(self, asset_manager: IAssetManager):
        """Initializes the prompt manager with a dependency on an asset manager."""
        self._asset_manager = asset_manager

    @abstractmethod
    async def get_template(self, uri: str) -> Optional[PromptTemplate]:
        """Retrieves and parses a prompt template from the asset manager.

        Args:
            uri: The asset URI of the prompt template.

        Returns:
            A PromptTemplate object if the asset is found and is a valid template,
            otherwise None.
        """
        pass

    @abstractmethod
    async def render_prompt(self, uri: str, context: Dict[str, Any]) -> RenderedPrompt:
        """Renders a prompt template with the given context.

        This method fetches the template, validates that all necessary variables
        are present in the context, and returns the formatted string.

        Args:
            uri: The asset URI of the prompt template to render.
            context: A dictionary of key-value pairs to inject into the template.

        Returns:
            A RenderedPrompt object containing the final string and context.

        Raises:
            ValueError: If the template is not found or if required context
                        variables are missing.
        """
        pass
```

## 5. Example Usage

```python
import asyncio

# Conceptual example showing how an agent's reasoning component would use the prompt manager.
async def run_reasoning_cycle(prompt_manager: IPromptManager):
    template_uri = "openmas://basic_assistant_prompt:1.0"

    # 1. Get the template to inspect its variables (optional)
    template = await prompt_manager.get_template(template_uri)
    if template:
        print(f"Prompt template expects variables: {template.variables}")

    # 2. Define the context for rendering
    user_context = {
        "user_query": "What is the capital of France?",
        "history": "User previously asked about European capitals."
    }

    # 3. Render the prompt
    try:
        rendered_prompt = await prompt_manager.render_prompt(template_uri, user_context)
        print("\n--- Rendered Prompt ---")
        print(rendered_prompt.content)
        print("-----------------------")

        # The rendered_prompt.content would now be sent to an LLM

    except ValueError as e:
        print(f"Error rendering prompt: {e}")

```
