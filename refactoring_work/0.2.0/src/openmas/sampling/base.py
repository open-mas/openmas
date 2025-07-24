"""Base classes for sampling in OpenMAS.

This module provides a flexible and extensible sampling system for OpenMAS,
enabling agents to sample from different language models with consistent parameters.
"""

import json
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field

from openmas.prompt.base import Prompt


class SamplingParameters(BaseModel):
    """Parameters for sampling from a language model."""

    provider: str | None = Field(default=None, description="Sampling provider (e.g., 'mcp', 'openai', etc.)")
    model: str | None = Field(default=None, description="Model name or ID to use for sampling")
    temperature: float = 0.7
    max_tokens: int | None = None
    top_p: float | None = None
    top_k: int | None = None
    stop_sequences: list[str] | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    logit_bias: dict[str, float] | None = None
    seed: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary, omitting None values."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class MessageRole(str, Enum):
    """Role of a message in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """A message in a conversation."""

    role: MessageRole
    content: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        result: dict[str, Any] = {"role": self.role.value, "content": self.content}
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class SamplingContext(BaseModel):
    """Context for sampling from a language model."""

    system_prompt: str | None = None
    messages: list[Message] = Field(default_factory=list)
    parameters: SamplingParameters = Field(default_factory=SamplingParameters)
    metadata: dict[str, Any] = Field(default_factory=dict)
    model: str | None = None

    @classmethod
    def from_prompt(
        cls,
        prompt: Prompt,
        context_vars: dict[str, Any] | None = None,
        params: SamplingParameters | None = None,
    ) -> "SamplingContext":
        """Create a sampling context from a prompt.

        Args:
            prompt: The prompt to use
            context_vars: Variables to use for template rendering
            params: Optional sampling parameters

        Returns:
            A sampling context for the given prompt
        """
        system = prompt.get_system_prompt()

        # Start with an empty message list
        messages = []

        # Add examples as messages if available
        for example in prompt.get_examples():
            if "role" in example and "content" in example:
                role_str = example["role"]
                role = MessageRole(role_str)
                content_str = str(example["content"])
                messages.append(Message(role=role, content=content_str))

        # Add the template as a user message if available
        template = prompt.get_template()
        if template and context_vars:
            # Simple template rendering (use a proper template engine in production)
            content = template
            for key, value in context_vars.items():
                if isinstance(value, str | int | float | bool):
                    placeholder = f"{{{{{key}}}}}"
                    content = content.replace(placeholder, str(value))

            messages.append(Message(role=MessageRole.USER, content=content))

        return cls(
            system_prompt=system,
            messages=messages,
            parameters=params or SamplingParameters(),
        )

    def add_message(self, role: MessageRole, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a message to the context.

        Args:
            role: The role of the message
            content: The content of the message
            metadata: Optional metadata for the message
        """
        self.messages.append(Message(role=role, content=content, metadata=metadata))

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        result = {
            "messages": [m.to_dict() for m in self.messages],
            "parameters": self.parameters.to_dict(),
        }
        if self.system_prompt:
            result["system"] = self.system_prompt
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class SamplingResult(BaseModel):
    """Result of a sampling operation."""

    content: str
    finish_reason: str | None = None
    usage: dict[str, int] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    raw_response: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        result: dict[str, Any] = {"content": self.content}
        if self.finish_reason:
            result["finish_reason"] = self.finish_reason
        if self.usage:
            result["usage"] = self.usage
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    def to_json(self, pretty: bool = False) -> str:
        """Convert to JSON."""
        if pretty:
            return json.dumps(self.to_dict(), indent=2)
        return json.dumps(self.to_dict())


@runtime_checkable
class SamplerProtocol(Protocol):
    """Protocol for samplers."""

    async def sample(
        self,
        context: SamplingContext,
        model: str | None = None,
    ) -> SamplingResult:
        """Sample from the language model.

        Args:
            context: The sampling context
            model: Optional model to use

        Returns:
            The sampling result
        """
        ...


class BaseSampler:
    """Base class for samplers."""

    def __init__(self, communicator: Any | None = None) -> None:
        """Initialize the sampler.

        Args:
            communicator: Optional communicator to use for sampling
        """
        self.communicator = communicator

    async def sample(
        self,
        context: SamplingContext,
        model: str | None = None,
    ) -> SamplingResult:
        """Sample from the language model.

        Args:
            context: The sampling context
            model: Optional model to use

        Returns:
            The sampling result

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement sample")

    @classmethod
    def create_context(
        cls,
        system: str | None = None,
        messages: list[dict[str, str]] | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> SamplingContext:
        """Create a sampling context.

        Args:
            system: Optional system prompt
            messages: Optional list of messages
            parameters: Optional sampling parameters

        Returns:
            A sampling context
        """
        params = SamplingParameters(**(parameters or {}))

        msg_list = []
        if messages:
            for msg in messages:
                role = MessageRole(msg["role"])
                content = msg["content"]
                metadata = msg.get("metadata")
                msg_list.append(
                    Message(role=role, content=content, metadata=metadata if isinstance(metadata, dict) else None)
                )

        return SamplingContext(
            system_prompt=system,
            messages=msg_list,
            parameters=params,
        )

    async def sample_from_prompt(
        self,
        prompt: Prompt,
        context_vars: dict[str, Any] | None = None,
        parameters: dict[str, Any] | None = None,
        model: str | None = None,
    ) -> SamplingResult:
        """Sample from a prompt.

        Args:
            prompt: The prompt to sample from
            context_vars: Variables to use for template rendering
            parameters: Optional sampling parameters
            model: Optional model to use

        Returns:
            The sampling result
        """
        params = SamplingParameters(**(parameters or {}))
        context = SamplingContext.from_prompt(prompt, context_vars, params)
        return await self.sample(context, model)
