# Reasoning Framework Interfaces

## Overview

This document formalizes the standardized interfaces for reasoning components in OpenMAS. The central piece is the `IReasoningEngine` interface, which provides a single, consistent entry point for the Agent Framework to invoke any reasoning process, from simple rule-based logic to complex hybrid strategies.

## Core Interface Principles

1.  **Standardized Invocation**: A single, universal `IReasoningEngine` interface is used to execute a reasoning cycle.
2.  **Composition over Inheritance**: Specialized reasoning logic is composed within an `IReasoningEngine` implementation rather than requiring a complex hierarchy of inherited interfaces.
3.  **Pydantic-Driven Contracts**: All data structures for inputs (`ReasoningInput`) and outputs (`ReasoningResult`) are defined as Pydantic models, ensuring clear, type-safe, and self-documenting contracts.
4.  **Decoupled Services**: Core services like knowledge bases and session management are provided to the engine during initialization, promoting loose coupling.

## Core Reasoning Interface

### `IReasoningEngine` (Standardized Invocation Contract)

The `IReasoningEngine` interface is the definitive, high-level contract for all reasoning components. It abstracts the internal complexity of any reasoning process into a single, well-defined entry point.

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

# --- Forward references to interfaces defined in other modules ---
# These are defined in detail in their respective interface documents.
class IKnowledgeBaseRegistry(ABC):
    ...

class ISessionManager(ABC):
    ...

# --- Standardized Input/Output Data Models ---

class ReasoningInput(BaseModel):
    """Standardized input for a reasoning cycle."""
    trigger_event: str = Field(..., description="The event that initiated the reasoning cycle (e.g., 'message_received', 'scheduled_task').")
    input_data: Dict[str, Any] = Field(..., description="The primary data for the reasoning cycle, such as a message payload or task parameters.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context, like message headers or trace IDs.")

class ReasoningResult(BaseModel):
    """Standardized output from a reasoning cycle."""
    actions: List[Dict[str, Any]] = Field(..., description="A list of proposed actions for the agent to execute, e.g., sending a message, calling a capability.")
    new_internal_state: Optional[Dict[str, Any]] = Field(None, description="Any proposed changes to the agent's internal state.")
    confidence_score: Optional[float] = Field(None, description="A score indicating the engine's confidence in its result.")
    explanation: Optional[str] = Field(None, description="A human-readable explanation of the reasoning process.")

# --- Core Engine Interface ---

class IReasoningEngine(ABC):
    """Base interface for all reasoning engines, defining the standard invocation method."""

    @abstractmethod
    async def setup(
        self,
        config: Dict[str, Any],
        knowledge_registry: IKnowledgeBaseRegistry,
        session_manager: ISessionManager
    ) -> None:
        """Initialize the reasoning engine with its configuration and access to core services."""
        ...

    @abstractmethod
    async def execute_cycle(self, input_data: ReasoningInput) -> ReasoningResult:
        """Perform a single, complete reasoning cycle based on the given input."""
        ...

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up any resources used by the reasoning engine."""
        ...
```

## Specialized Reasoning Models

While the `IReasoningEngine` interface is universal, implementations can use specialized internal models. The following are provided as examples of Pydantic models that specific engines (e.g., a symbolic or LLM-based engine) might use internally. They are not part of the formal interface itself.

```python
# --- Models for a potential Symbolic Engine ---
class Fact(BaseModel):
    """Represents a basic assertion."""
    subject: str
    predicate: str
    object: Any

class Rule(BaseModel):
    """Represents an if-then rule."""
    name: str
    conditions: List[Fact]
    conclusion: Fact

class Query(BaseModel):
    """Represents a query against a symbolic knowledge base."""
    pattern: List[Fact]

# --- Models for a potential LLM-based Engine ---
class Prompt(BaseModel):
    """Represents a structured prompt for an LLM."""
    template_name: str
    context: Dict[str, Any]
    instructions: Optional[str] = None

class VerificationResult(BaseModel):
    """Represents the result of verifying an LLM output."""
    is_valid: bool
    reasoning: Optional[str] = None
```

## Integration with Agent Framework

The reasoning engine integrates with the agent framework as follows:

1.  **Configuration**: An agent's configuration in the unified schema specifies which `IReasoningEngine` implementation to use.
2.  **Instantiation**: The Agent Framework instantiates the specified engine.
3.  **Setup**: The framework calls the engine's `setup()` method, injecting the necessary dependencies (`IKnowledgeBaseRegistry`, `ISessionManager`).
4.  **Invocation**: When a trigger event occurs (e.g., a message arrives), the framework constructs a `ReasoningInput` object and calls the engine's `execute_cycle()` method.
5.  **Action**: The framework processes the `ReasoningResult` to execute actions, update state, etc.

## References

-   [Knowledge Access Interfaces](./../knowledge_access_interfaces/interfaces.md)
-   [Reasoning Agnostic Design](/refactoring_work/design/01_architecture/reasoning_agnostic_design.md)
-   [Unified Configuration Schema](/refactoring_work/design/03_configuration/unified_configuration_schema.md)
