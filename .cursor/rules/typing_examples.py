#!/usr/bin/env python3
"""
OpenMAS Typing Standards Examples - Validation File

This file contains practical examples of all typing patterns from the Cursor rules.
It serves as both documentation and validation that all examples pass MyPy.

Run: poetry run mypy .cursor/rules/typing_examples.py
"""

import asyncio
import json
import uuid
from collections.abc import Awaitable, Callable

# Import OpenMAS types (these would be real imports in actual code)
# For validation purposes, we'll define minimal stubs
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Generic, Optional, Protocol, TypeVar


# Minimal type stubs for validation
class MessageType(Enum):
    CAPABILITY_INVOCATION = "capability_invocation"
    TOOL_RESULT = "tool_result"


class InvocationStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


@dataclass
class TextContentPayload:
    text: str


@dataclass
class StructuredDataContentPayload:
    data: dict[str, Any]


@dataclass
class InvocationRequestContentPayload:
    invocation_name: str
    arguments: Optional[dict[str, Any]] = None


@dataclass
class InvocationResultContentPayload:
    result: dict[str, Any]
    status: InvocationStatus


# Union type for SIMF payloads
PayloadUnion = (
    TextContentPayload
    | StructuredDataContentPayload
    | InvocationRequestContentPayload
    | InvocationResultContentPayload
)


@dataclass
class SIMFMessage:
    message_id: str
    target_agent_id: str
    source_agent_id: str
    message_type: MessageType
    payload: PayloadUnion
    session_id: str
    source_protocol_type: str
    timestamp: datetime


# MCP result type stubs
@dataclass
class Tool:
    name: str
    description: str

    def model_dump(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description}


@dataclass
class ListToolsResult:
    tools: list[Tool]


@dataclass
class CallToolResult:
    content: str | dict[str, Any]


MCPResult = ListToolsResult | CallToolResult


class ClientSession:
    async def initialize(self) -> None:
        pass

    async def send_request(self, request: dict[str, Any]) -> None:
        pass


# Example 1: Union Type Handling (CORRECT)
def process_payload_correct(payload: PayloadUnion) -> str:
    """Process SIMF payload with proper type narrowing."""
    if isinstance(payload, TextContentPayload):
        return f"Text: {payload.text}"
    elif isinstance(payload, StructuredDataContentPayload):
        return f"Data: {payload.data}"
    elif isinstance(payload, InvocationRequestContentPayload):
        return f"Invocation: {payload.invocation_name}"
    elif isinstance(payload, InvocationResultContentPayload):
        return f"Result: {payload.result}"
    else:
        # Handle remaining union members
        return f"Unknown payload type: {type(payload)}"


# Example 2: MCP Result Type Handling (CORRECT)
async def handle_mcp_result_correct(result: MCPResult) -> dict[str, Any]:
    """Handle MCP tool result with proper type checking."""
    if isinstance(result, ListToolsResult):
        return {"tools": [tool.model_dump() for tool in result.tools]}
    elif isinstance(result, CallToolResult):
        # Parse JSON string to dict if needed
        if isinstance(result.content, str):
            try:
                return json.loads(result.content)
            except json.JSONDecodeError:
                return {"raw_content": result.content}
        return {"content": result.content}
    else:
        return {"unknown_result": str(result)}


# Example 3: Agent Implementation Pattern (CORRECT)
class Agent:
    """Base agent class stub."""
    
    def __init__(self, agent_id: str, name: str) -> None:
        self.agent_id = agent_id
        self.name = name


class MyCustomAgent(Agent):
    """Custom agent with proper typing."""
    
    def __init__(self, agent_id: str, name: str, config: Optional[dict[str, Any]] = None) -> None:
        """Initialize agent with typed parameters."""
        super().__init__(agent_id, name)
        self._config: dict[str, Any] = config or {}
        self._custom_data: dict[str, Any] = {}
    
    async def execute_capability(self, simf_message: SIMFMessage) -> SIMFMessage:
        """Execute capability with proper SIMF message handling."""
        # Type-safe payload handling
        if isinstance(simf_message.payload, InvocationRequestContentPayload):
            capability_name = simf_message.payload.invocation_name
            arguments = simf_message.payload.arguments or {}
            
            # Execute with proper error handling
            try:
                result = await self._execute_internal(capability_name, arguments)
                return self._create_success_message(simf_message, result)
            except Exception as e:
                return self._create_error_message(simf_message, str(e))
        else:
            raise ValueError(f"Unsupported payload type: {type(simf_message.payload)}")
    
    async def _execute_internal(self, capability_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Internal execution with proper typing."""
        # Implementation here
        return {"result": "success", "capability": capability_name, "args": arguments}
    
    def _create_success_message(self, original: SIMFMessage, result: dict[str, Any]) -> SIMFMessage:
        """Create success response message."""
        return SIMFMessage(
            message_id=str(uuid.uuid4()),
            target_agent_id=original.source_agent_id,
            source_agent_id=self.agent_id,
            message_type=MessageType.TOOL_RESULT,
            payload=InvocationResultContentPayload(
                result=result,
                status=InvocationStatus.SUCCESS
            ),
            session_id=original.session_id,
            source_protocol_type=original.source_protocol_type,
            timestamp=datetime.now()
        )
    
    def _create_error_message(self, original: SIMFMessage, error: str) -> SIMFMessage:
        """Create error response message."""
        return SIMFMessage(
            message_id=str(uuid.uuid4()),
            target_agent_id=original.source_agent_id,
            source_agent_id=self.agent_id,
            message_type=MessageType.TOOL_RESULT,
            payload=InvocationResultContentPayload(
                result={"error": error},
                status=InvocationStatus.FAILURE
            ),
            session_id=original.session_id,
            source_protocol_type=original.source_protocol_type,
            timestamp=datetime.now()
        )


# Example 4: Protocol Adapter Pattern (CORRECT)
class IProtocolAdapter(Protocol):
    """Protocol adapter interface."""
    
    async def connect(self) -> None:
        """Establish connection."""
        ...
    
    async def send_message(self, message: SIMFMessage) -> None:
        """Send SIMF message."""
        ...


class MCPProtocolAdapter:
    """MCP protocol adapter with comprehensive typing."""
    
    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize adapter with typed configuration."""
        self._config = config
        self._session: Optional[ClientSession] = None
    
    async def connect(self) -> None:
        """Establish MCP connection with proper error handling."""
        try:
            # Type-safe session creation
            self._session = await self._create_session()
            await self._session.initialize()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MCP server: {e}") from e
    
    async def send_message(self, message: SIMFMessage) -> None:
        """Send SIMF message via MCP protocol."""
        if self._session is None:
            raise RuntimeError("Not connected to MCP server")
        
        # Type-safe message translation
        mcp_request = self._translate_simf_to_mcp(message)
        await self._session.send_request(mcp_request)
    
    def _translate_simf_to_mcp(self, message: SIMFMessage) -> dict[str, Any]:
        """Translate SIMF message to MCP format with type safety."""
        if isinstance(message.payload, InvocationRequestContentPayload):
            return {
                "method": "tools/call",
                "params": {
                    "name": message.payload.invocation_name,
                    "arguments": message.payload.arguments or {}
                }
            }
        else:
            raise ValueError(f"Unsupported SIMF payload type: {type(message.payload)}")
    
    async def _create_session(self) -> ClientSession:
        """Create MCP session with proper typing."""
        return ClientSession()


# Example 5: Generic Type Usage (CORRECT)
T = TypeVar('T')
PayloadT = TypeVar('PayloadT', bound=PayloadUnion)


class MessageProcessor(Generic[PayloadT]):
    """Generic message processor with type safety."""
    
    def __init__(self, payload_type: type[PayloadT]) -> None:
        self._payload_type = payload_type
        self._handlers: dict[str, Callable[[PayloadT], str]] = {}
    
    def register_handler(self, name: str, handler: Callable[[PayloadT], str]) -> None:
        """Register typed handler."""
        self._handlers[name] = handler
    
    def process(self, payload: PayloadT) -> str:
        """Process payload with type safety."""
        if isinstance(payload, self._payload_type):
            # Type-safe processing
            return self._handlers.get("default", lambda p: str(p))(payload)
        else:
            raise ValueError(f"Expected {self._payload_type}, got {type(payload)}")


# Example 6: Error Prevention Patterns (CORRECT)
def create_message_data_correct() -> dict[str, Any]:
    """Create message data with proper typing."""
    data: dict[str, Any] = {
        "agent_id": "test_agent",
        "timestamp": datetime.now().isoformat(),
        "payload": {"type": "text", "content": "Hello"}
    }
    return data


def handle_external_data_correct(raw_data: Any) -> dict[str, str]:
    """Handle external data with type validation."""
    if isinstance(raw_data, dict):
        # Safe casting after type check
        return {str(k): str(v) for k, v in raw_data.items()}
    else:
        raise ValueError(f"Expected dict, got {type(raw_data)}")


# Example 7: Factory Functions (CORRECT)
def create_invocation_message(
    target_agent_id: str,
    invocation_name: str,
    arguments: Optional[dict[str, Any]] = None,
    session_id: str = "default_session",
    source_protocol_type: str = "internal"
) -> SIMFMessage:
    """Create SIMF invocation message with all required arguments."""
    return SIMFMessage(
        message_id=str(uuid.uuid4()),
        target_agent_id=target_agent_id,
        source_agent_id="system",
        message_type=MessageType.CAPABILITY_INVOCATION,
        payload=InvocationRequestContentPayload(
            invocation_name=invocation_name,
            arguments=arguments
        ),
        session_id=session_id,
        source_protocol_type=source_protocol_type,
        timestamp=datetime.now()
    )


def create_tool_result_message(
    target_agent_id: str,
    result: dict[str, Any],
    status: InvocationStatus,
    session_id: str,
    source_protocol_type: str
) -> SIMFMessage:
    """Create SIMF tool result message."""
    return SIMFMessage(
        message_id=str(uuid.uuid4()),
        target_agent_id=target_agent_id,
        source_agent_id="system",
        message_type=MessageType.TOOL_RESULT,
        payload=InvocationResultContentPayload(
            result=result,
            status=status
        ),
        session_id=session_id,
        source_protocol_type=source_protocol_type,
        timestamp=datetime.now()
    )


# Example 8: Collection Types (CORRECT)
def manage_agent_data() -> None:
    """Demonstrate proper collection typing."""
    # Modern type annotations (Python 3.9+)
    agent_configs: dict[str, Any] = {}
    active_sessions: set[str] = set()
    connection_info: tuple[str, int] = ("localhost", 8080)
    
    # Usage examples
    agent_configs["test_agent"] = {"name": "Test Agent", "enabled": True}
    active_sessions.add("session_123")
    
    # Type-safe operations
    host, port = connection_info
    print(f"Connecting to {host}:{port}")
    
    # Example of capability handlers (used for demonstration)
    capability_handlers: dict[str, Callable[[dict[str, Any]], Awaitable[str]]] = {}
    message_queue: list[SIMFMessage] = []
    print(f"Initialized {len(capability_handlers)} handlers and {len(message_queue)} messages")


# Example 9: Async Function Typing (CORRECT)
async def process_messages_async(
    messages: list[SIMFMessage],
    processor: Callable[[SIMFMessage], Awaitable[str]]
) -> list[str]:
    """Process messages asynchronously with proper typing."""
    results: list[str] = []
    for message in messages:
        result = await processor(message)
        results.append(result)
    return results


async def simple_message_processor(message: SIMFMessage) -> str:
    """Simple message processor with proper async typing."""
    return f"Processed message {message.message_id}"


# Example 10: Usage Demonstration
async def demonstrate_typing_patterns() -> None:
    """Demonstrate all typing patterns working together."""
    # Create a custom agent
    agent = MyCustomAgent("demo_agent", "Demo Agent", {"debug": True})
    
    # Create a test message
    test_message = create_invocation_message(
        target_agent_id="demo_agent",
        invocation_name="test_capability",
        arguments={"param": "value"},
        session_id="demo_session"
    )
    
    # Process the message
    result_message = await agent.execute_capability(test_message)
    
    # Handle the result with type safety
    if isinstance(result_message.payload, InvocationResultContentPayload):
        print(f"Result status: {result_message.payload.status}")
        print(f"Result data: {result_message.payload.result}")
    
    # Demonstrate collection processing
    messages = [test_message]
    processed = await process_messages_async(messages, simple_message_processor)
    print(f"Processed {len(processed)} messages")
    
    # Demonstrate generic processor
    text_processor = MessageProcessor[TextContentPayload](TextContentPayload)
    text_processor.register_handler("default", lambda p: p.text)
    
    text_payload = TextContentPayload("Hello, world!")
    processed_text = text_processor.process(text_payload)
    print(f"Processed text: {processed_text}")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_typing_patterns())
