# ISessionManager Interface

## 1. Overview

The `ISessionManager` provides the core API for creating, managing, and retrieving data associated with agent interaction sessions. A session represents a stateful, ordered sequence of interactions between two or more agents, identified by a unique `session_id`. This is critical for any task that requires maintaining context over time, such as multi-step problem solving, conversational AI, or managing long-running tasks.

This interface provides the necessary methods to handle session lifecycle, store arbitrary session data, and access the complete history of messages exchanged within a session.

## 2. Core Concepts

- **Session**: A container for a specific interaction context, identified by a unique `session_id`. It holds both a history of messages and a flexible data store for session-specific state.
- **Session Data**: A key-value store associated with a session, allowing agents to persist state (e.g., user preferences, intermediate calculations) throughout an interaction.
- **Session History**: An immutable, ordered log of all Standard Internal Message Format (SIMF) messages that have been part of the session.

## 3. Data Models

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4

# Assumes the SIMF model is defined and available
# from ..internal_message_format_standard import StandardInternalMessageFormat as SIMF

class Session(BaseModel):
    """Represents the state and metadata of an interaction session."""
    session_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the session.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of session creation.")
    participants: List[str] = Field(default_factory=list, description="List of agent IDs participating in the session.")
    session_data: Dict[str, Any] = Field(default_factory=dict, description="A key-value store for arbitrary session data.")
    history: List[SIMF] = Field(default_factory=list, description="An ordered list of messages exchanged in the session.")

```

## 4. ISessionManager Interface Definition

```python
class ISessionManager(ABC):
    """A formal interface for managing the lifecycle of interaction sessions."""

    @abstractmethod
    async def create_session(self, participants: List[str] = []) -> Session:
        """Creates a new, empty session.

        Args:
            participants: An initial list of agent IDs involved in the session.

        Returns:
            The newly created Session object.
        """
        pass

    @abstractmethod
    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """Retrieves a session by its unique ID.

        Args:
            session_id: The ID of the session to retrieve.

        Returns:
            The Session object if found, otherwise None.
        """
        pass

    @abstractmethod
    async def update_session_data(self, session_id: UUID, data: Dict[str, Any]) -> bool:
        """Updates or adds key-value data to a session's data store.

        Args:
            session_id: The ID of the session to update.
            data: A dictionary of data to merge into the session's data store.

        Returns:
            True if the update was successful, False otherwise.
        """
        pass

    @abstractmethod
    async def add_history_event(self, session_id: UUID, message: SIMF) -> bool:
        """Adds a new message to the end of a session's history.

        Args:
            session_id: The ID of the session to which the message belongs.
            message: The SIMF message to add to the history.

        Returns:
            True if the message was added successfully, False otherwise.
        """
        pass

    @abstractmethod
    async def end_session(self, session_id: UUID) -> bool:
        """Ends a session, potentially archiving it.

        Args:
            session_id: The ID of the session to end.

        Returns:
            True if the session was ended successfully, False otherwise.
        """
        pass
```

## 5. Example Usage

```python
import asyncio

# Conceptual example of an agent using the session manager
async def agent_interaction_flow(session_manager: ISessionManager):
    # 1. Create a new session for an interaction
    new_session = await session_manager.create_session(participants=["agent_A", "agent_B"])
    session_id = new_session.session_id
    print(f"Started new session: {session_id}")

    # 2. Store some initial context in the session data
    initial_context = {"topic": "planning a trip", "user_preferences": {"budget": "moderate"}}
    await session_manager.update_session_data(session_id, initial_context)
    print("Stored initial context in session.")

    # 3. Add messages to the session history as the conversation progresses
    # (These would be SIMF objects in a real implementation)
    message1 = {"message_id": "msg1", "payload": "Hello, let's plan a trip."}
    message2 = {"message_id": "msg2", "payload": "Okay, where to?"}
    await session_manager.add_history_event(session_id, message1)
    await session_manager.add_history_event(session_id, message2)
    print("Added messages to session history.")

    # 4. Retrieve the session to access its full state
    retrieved_session = await session_manager.get_session(session_id)
    if retrieved_session:
        print(f"\nRetrieved session data: {retrieved_session.session_data}")
        print(f"Retrieved session history has {len(retrieved_session.history)} messages.")

    # 5. End the session
    await session_manager.end_session(session_id)
    print(f"\nSession {session_id} has ended.")
```
