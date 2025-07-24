# ICommunicationManager Interface

## 1. Overview

The `ICommunicationManager` interface provides a high-level, simplified API for agents to perform common communication tasks. It acts as a facade over the more complex `IPatternEngine`, abstracting away the details of pattern execution, message creation, and configuration.

While the `IPatternEngine` manages the lifecycle and registration of patterns, the `ICommunicationManager` provides direct, ergonomic methods for an agent to *use* those patterns (e.g., making a request, publishing an event).

## 2. Relationship to IPatternEngine

- **`ICommunicationManager` (Agent-Facing API)**: Provides simple methods like `request()`, `publish()`. It is responsible for creating the appropriate Standard Internal Message Format (SIMF) message and invoking the `IPatternEngine` with the correct parameters.
- **`IPatternEngine` (Framework-Level API)**: The low-level engine that takes configured pattern requests and executes them, interacting with the protocol layer. It is not typically used directly by agent logic.

## 3. Interface Definition

The `ICommunicationManager` is designed to be injected into an agent's context, providing a clean entry point for all communication.

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional, AsyncIterator
from uuid import UUID

# Assumes SIMF models are available for creating messages internally
# from ...internal_message_format_standard import AnyPayload

class ICommunicationManager(ABC):
    """A simplified, agent-facing interface for using communication patterns."""

    @abstractmethod
    async def request(self, target_agent_id: str, payload: AnyPayload, timeout: float = 30.0) -> AnyPayload:
        """Sends a request to a target agent and waits for a response.

        This method implements the Request-Response pattern.

        Args:
            target_agent_id: The unique ID of the agent to send the request to.
            payload: The payload of the message to send.
            timeout: The maximum time in seconds to wait for a response.

        Returns:
            The payload of the response message.

        Raises:
            TimeoutError: If no response is received within the timeout period.
            CommunicationError: If the request fails for other reasons.
        """
        pass

    @abstractmethod
    async def publish(self, topic: str, payload: AnyPayload) -> None:
        """Publishes a message to a specific topic.

        This method implements the Publish-Subscribe pattern.

        Args:
            topic: The topic to publish the message to.
            payload: The payload of the message to publish.
        """
        pass

    @abstractmethod
    async def send(self, target_agent_id: str, payload: AnyPayload) -> None:
        """Sends a one-way message to a target agent without waiting for a response.

        This method implements a Fire-and-Forget pattern.

        Args:
            target_agent_id: The unique ID of the agent to send the message to.
            payload: The payload of the message to send.
        """
        pass

    @abstractmethod
    async def stream(self, target_agent_id: str, payload: AnyPayload) -> AsyncIterator[AnyPayload]:
        """Initiates a stream with a target agent and yields responses.

        This method implements a Streaming pattern.

        Args:
            target_agent_id: The unique ID of the agent to stream to.
            payload: The initial payload to start the stream.

        Yields:
            Payloads from the stream as they are received.
        """
        # The 'yield' keyword indicates this will be an async generator
        if False:
            yield

```

## 4. Example Usage

```python
import asyncio

# This is a conceptual example showing how an agent would use the injected manager.
async def agent_logic(comm_manager: ICommunicationManager):
    # Example 1: Request-Response
    try:
        print("Sending a request to the weather agent...")
        weather_request_payload = TextContentPayload(text="What is the weather in London?")
        response_payload = await comm_manager.request("weather_agent_id", weather_request_payload)
        print(f"Received weather report: {response_payload.text}")
    except TimeoutError:
        print("The weather agent did not respond in time.")

    # Example 2: Publish-Subscribe
    print("Publishing a system alert...")
    alert_payload = StructuredDataPayload(data={"status": "critical", "component": "database"})
    await comm_manager.publish("system.alerts", alert_payload)
    print("Alert published.")

    # Example 3: Fire-and-Forget
    print("Sending a log message...")
    log_payload = TextContentPayload(text="Agent logic completed successfully.")
    await comm_manager.send("logging_agent_id", log_payload)

    # Example 4: Streaming
    print("Starting a data stream...")
    stream_request = TextContentPayload(text="start_market_data")
    async for data_chunk in comm_manager.stream("market_data_agent_id", stream_request):
        print(f"Received stream data: {data_chunk.data}")

```
