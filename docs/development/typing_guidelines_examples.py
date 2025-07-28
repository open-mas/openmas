"""
Validation examples for OpenMAS Typing Guidelines.
All code in this file must pass mypy --strict validation.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import asyncio

# Import OpenMAS types for validation
OPENMAS_AVAILABLE = False
try:
    from openmas.core.simf.models import (  # type: ignore[import-untyped]
        SIMFMessage,
        TextContentPayload,
        StructuredDataContentPayload,
        ContentPayload,
        MessageType,
        ProtocolType,
    )
    from openmas.core.simf.functions import create_text_message  # type: ignore[import-untyped]
    from openmas.agent.base_agent import Agent  # type: ignore[import-untyped]

    OPENMAS_AVAILABLE = True
except ImportError:
    # Mock types for validation when OpenMAS not available
    class MockTextContentPayload:
        def __init__(self, text: str) -> None:
            self.text = text

    class MockStructuredDataContentPayload:
        def __init__(self, data: Dict[str, Any]) -> None:
            self.data = data

    # Use mock types when OpenMAS not available
    TextContentPayload = MockTextContentPayload  # type: ignore
    StructuredDataContentPayload = MockStructuredDataContentPayload  # type: ignore
    ContentPayload = Union[MockTextContentPayload, MockStructuredDataContentPayload]  # type: ignore


# Example 1: Exception Classes with Optional Parameters
class AgentException(Exception):
    """Properly typed exception class."""

    def __init__(self, message: str, agent_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.agent_id = agent_id
        self.details = details or {}


# Example 2: Union Type Handling
def extract_text_from_payload(payload: ContentPayload) -> str:
    """Extract text content from any payload type with proper type narrowing."""
    if isinstance(payload, TextContentPayload):
        return payload.text
    elif isinstance(payload, StructuredDataContentPayload):
        return str(payload.data)
    else:
        return f"Unsupported payload type: {type(payload).__name__}"


# Example 3: Optional Parameter Handling
def process_agent_request(
    agent_id: str,
    request_data: Dict[str, Any],
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Process agent request with proper optional parameter typing."""
    result = {"agent_id": agent_id, "processed": True, "timestamp": datetime.utcnow().isoformat()}

    if session_id is not None:
        result["session_id"] = session_id

    if metadata is not None:
        result["metadata"] = metadata

    return result


# Example 4: Generic Type Parameterization
def create_typed_config() -> Dict[str, Any]:
    """Create configuration with proper generic typing."""
    config: Dict[str, Any] = {}
    items: List[str] = []

    config["items"] = items
    config["enabled"] = True

    return config


# Example 5: Async Function with Proper Typing
async def async_message_processor(messages: List[Dict[str, Any]], timeout: Optional[float] = None) -> Dict[str, Any]:
    """Process messages asynchronously with proper typing."""
    try:
        processed_count = 0
        for message in messages:
            # Simulate async processing
            await asyncio.sleep(0.01)
            processed_count += 1

        return {"status": "success", "processed_count": processed_count, "total_messages": len(messages)}
    except asyncio.TimeoutError:
        return {"status": "timeout", "error": "Processing timed out"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Example 6: Protocol Result Handling (Mock MCP types for validation)
class MockCallToolResult:
    """Mock MCP result type for validation."""

    def __init__(self, content: List[Any]) -> None:
        self.content = content


class MockListToolsResult:
    """Mock MCP result type for validation."""

    def __init__(self, tools: List[Any]) -> None:
        self.tools = tools


def handle_protocol_result(result: Union[MockCallToolResult, MockListToolsResult]) -> Dict[str, Any]:
    """Handle different protocol result types safely."""
    if isinstance(result, MockListToolsResult):
        return {"type": "tools", "data": [str(tool) for tool in result.tools]}
    elif isinstance(result, MockCallToolResult):
        return {"type": "call_result", "data": [str(content) for content in result.content]}
    else:
        raise ValueError(f"Unsupported result type: {type(result)}")


# Example 7: Agent Template with Proper Typing
class ExampleAgent:
    """Example agent implementation with proper typing patterns."""

    def __init__(self, agent_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.agent_id = agent_id
        self.name = name
        self.config = config or {}
        self.capabilities: List[Dict[str, Any]] = []

    def add_capability(self, name: str, description: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """Add capability with proper typing."""
        capability = {"name": name, "description": description, "parameters": parameters or {}}
        self.capabilities.append(capability)

    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Return agent capabilities with proper typing."""
        return self.capabilities.copy()

    def process_text(self, text: str) -> str:
        """Process text with proper return type annotation."""
        return f"Processed by {self.name}: {text}"


# Example 8: Factory Functions with Type Safety
def create_agent_from_config(config: Dict[str, Any]) -> ExampleAgent:
    """Create agent from configuration with type safety."""
    agent_id = config.get("agent_id")
    name = config.get("name")

    if not isinstance(agent_id, str):
        raise ValueError("agent_id must be a string")

    if not isinstance(name, str):
        raise ValueError("name must be a string")

    agent_config = config.get("config")
    if agent_config is not None and not isinstance(agent_config, dict):
        raise ValueError("config must be a dictionary")

    return ExampleAgent(agent_id=agent_id, name=name, config=agent_config)


# Example 9: Error Handling with Types
def safe_json_parse(data: str) -> Optional[Dict[str, Any]]:
    """Parse JSON safely with proper typing."""
    try:
        import json

        result = json.loads(data)
        if isinstance(result, dict):
            return result
        else:
            return None
    except (json.JSONDecodeError, ValueError):
        return None


# Example 10: Test Function with Proper Typing
def test_agent_creation() -> None:
    """Test function with proper return type annotation."""
    agent = ExampleAgent("test-agent", "Test Agent")
    assert agent.agent_id == "test-agent"
    assert agent.name == "Test Agent"
    assert len(agent.get_capabilities()) == 0

    agent.add_capability("test", "Test capability")
    assert len(agent.get_capabilities()) == 1


# Example 11: Complex Union Type Handling
def process_mixed_data(data: Union[str, Dict[str, Any], List[Any]]) -> Dict[str, Any]:
    """Process different data types with proper union handling."""
    if isinstance(data, str):
        return {"type": "string", "length": len(data), "content": data}
    elif isinstance(data, dict):
        return {"type": "dict", "keys": list(data.keys()), "content": data}
    elif isinstance(data, list):
        return {"type": "list", "length": len(data), "content": data}
    else:
        # This should never happen due to type annotation, but mypy requires it
        raise ValueError(f"Unsupported data type: {type(data)}")


if __name__ == "__main__":
    # Example usage that validates typing
    print("Running typing validation examples...")

    # Test exception
    try:
        raise AgentException("Test error", agent_id="test", details={"code": 500})
    except AgentException as e:
        print(f"Caught exception: {e}")

    # Test agent creation
    test_agent_creation()
    print("Agent creation test passed")

    # Test data processing
    result = process_mixed_data("hello")
    print(f"String processing result: {result}")

    result = process_mixed_data({"key": "value"})
    print(f"Dict processing result: {result}")

    print("All typing validation examples completed successfully!")
