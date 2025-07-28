# OpenMAS Typing Guidelines & Patterns

## Table of Contents
1. [Core Typing Principles](#core-typing-principles)
2. [Optional Type Handling](#optional-type-handling)
3. [Union Type Patterns](#union-type-patterns)
4. [SIMF Type Patterns](#simf-type-patterns)
5. [Agent Framework Typing](#agent-framework-typing)
6. [Protocol Integration Types](#protocol-integration-types)
7. [Common MyPy Error Solutions](#common-mypy-error-solutions)
8. [AI Development Patterns](#ai-development-patterns)
9. [Type Annotation Templates](#type-annotation-templates)

---

## Core Typing Principles

### 1. Explicit Optional Types
**Problem**: MyPy now requires explicit Optional types (no implicit optional).

```python
# ❌ WRONG: Implicit Optional (causes mypy errors)
def process_agent(agent_id: str = None) -> dict:
    pass

# ✅ CORRECT: Explicit Optional
from typing import Optional, Dict, Any

def process_agent(agent_id: Optional[str] = None) -> Dict[str, Any]:
    if agent_id is None:
        return {"error": "No agent ID provided"}
    return {"agent_id": agent_id, "status": "processed"}
```

### 2. Generic Type Parameterization
**Problem**: Unparameterized generic types cause mypy warnings.

```python
# ❌ WRONG: Unparameterized generics
config: dict = {}
items: list = []

# ✅ CORRECT: Parameterized generics
from typing import Dict, List, Any

config: Dict[str, Any] = {}
items: List[str] = []
```

### 3. Return Type Annotations
**Problem**: Missing return type annotations on functions.

```python
# ❌ WRONG: Missing return type
def create_message(content):
    return {"content": content, "timestamp": time.time()}

# ✅ CORRECT: Explicit return type
from typing import Dict, Any

def create_message(content: str) -> Dict[str, Any]:
    return {"content": content, "timestamp": time.time()}
```

---

## Optional Type Handling

### Pattern: Exception Classes with Optional Parameters

**Common Error**: `Incompatible default for argument (default has type "None", argument has type "str")`

```python
# ❌ WRONG: Implicit Optional in exception classes
class AgentException(Exception):
    def __init__(self, message: str, agent_id: str = None, details: dict = None):
        super().__init__(message)
        self.agent_id = agent_id
        self.details = details

# ✅ CORRECT: Explicit Optional types
from typing import Optional, Dict, Any

class AgentException(Exception):
    def __init__(
        self, 
        message: str, 
        agent_id: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.agent_id = agent_id
        self.details = details or {}
```

### Pattern: Configuration Classes

```python
# ✅ CORRECT: Configuration with optional fields
from typing import Optional, Dict, Any
from pydantic import BaseModel

class AgentConfig(BaseModel):
    agent_id: str
    name: str
    description: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "forbid"  # Prevent additional fields
```

---

## Union Type Patterns

### Pattern: SIMF Payload Union Handling

**Common Error**: `Union members don't all have 'text' attribute`

```python
# ❌ WRONG: Direct attribute access on union types
from openmas.core.simf.models import ContentPayload

def extract_text(payload: ContentPayload) -> str:
    return payload.text  # Error: not all union members have 'text'

# ✅ CORRECT: Type narrowing with isinstance
from typing import Union
from openmas.core.simf.models import (
    TextContentPayload, 
    StructuredDataContentPayload,
    ContentPayload
)

def extract_text(payload: ContentPayload) -> str:
    """Extract text content from any payload type."""
    if isinstance(payload, TextContentPayload):
        return payload.text
    elif isinstance(payload, StructuredDataContentPayload):
        return str(payload.data)
    else:
        # Handle other payload types
        return f"Unsupported payload type: {type(payload).__name__}"
```

### Pattern: MCP Result Type Handling

```python
# ❌ WRONG: Type mismatch in protocol conversion
from mcp.types import CallToolResult, ListToolsResult

def handle_mcp_result(result: CallToolResult) -> dict:
    return {"tools": result.tools}  # Error: CallToolResult doesn't have 'tools'

# ✅ CORRECT: Proper union type handling
from typing import Dict, Any, Union
from mcp.types import CallToolResult, ListToolsResult, ReadResourceResult

def handle_mcp_result(result: Union[CallToolResult, ListToolsResult, ReadResourceResult]) -> Dict[str, Any]:
    """Handle different MCP result types safely."""
    if isinstance(result, ListToolsResult):
        return {"type": "tools", "data": [tool.model_dump() for tool in result.tools]}
    elif isinstance(result, ReadResourceResult):
        return {"type": "resource", "data": result.contents}
    elif isinstance(result, CallToolResult):
        return {"type": "call_result", "data": result.content}
    else:
        raise ValueError(f"Unsupported MCP result type: {type(result)}")
```

---

## SIMF Type Patterns

### Pattern: Message Creation with Type Safety

```python
# ✅ CORRECT: Type-safe SIMF message creation
from typing import Dict, Any, Optional
from openmas.core.simf.models import SIMFMessage, TextContentPayload, MessageType
from openmas.core.simf.functions import create_text_message

def create_agent_response(
    content: str,
    source_agent_id: str,
    target_agent_id: str,
    session_id: Optional[str] = None
) -> SIMFMessage:
    """Create a properly typed SIMF text message."""
    return create_text_message(
        text=content,
        source_agent_id=source_agent_id,
        target_agent_id=target_agent_id,
        session_id=session_id
    )
```

### Pattern: Payload Factory Functions

```python
# ✅ CORRECT: Type-safe payload creation
from typing import Dict, Any, Union
from openmas.core.simf.models import (
    TextContentPayload,
    StructuredDataContentPayload,
    ContentPayload
)

def create_payload_from_data(data: Union[str, Dict[str, Any]]) -> ContentPayload:
    """Create appropriate payload type based on input data."""
    if isinstance(data, str):
        return TextContentPayload(text=data)
    elif isinstance(data, dict):
        return StructuredDataContentPayload(data=data)
    else:
        raise ValueError(f"Unsupported data type for payload: {type(data)}")
```

---

## Agent Framework Typing

### Pattern: Agent Interface Implementation

```python
# ✅ CORRECT: Properly typed agent implementation
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from openmas.core.simf.models import SIMFMessage

class IAgent(ABC):
    """Base interface for all OpenMAS agents."""
    
    @abstractmethod
    async def process_message(self, message: SIMFMessage) -> Optional[SIMFMessage]:
        """Process incoming SIMF message and optionally return response."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Return list of agent capabilities."""
        pass

class DocumentProcessor(IAgent):
    """Example agent implementation with proper typing."""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.agent_id = agent_id
        self.config = config or {}
    
    async def process_message(self, message: SIMFMessage) -> Optional[SIMFMessage]:
        """Process document-related messages."""
        # Type-safe message processing
        if message.payload and isinstance(message.payload, TextContentPayload):
            processed_text = self._process_text(message.payload.text)
            return create_text_message(
                text=processed_text,
                source_agent_id=self.agent_id,
                target_agent_id=message.source_agent_id
            )
        return None
    
    def _process_text(self, text: str) -> str:
        """Process text content with proper typing."""
        return f"Processed: {text}"
    
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Return agent capabilities."""
        return [
            {
                "name": "text_processing",
                "description": "Process text documents",
                "parameters": {"text": {"type": "string", "required": True}}
            }
        ]
```

---

## Protocol Integration Types

### Pattern: MCP Adapter Type Safety

```python
# ✅ CORRECT: Type-safe protocol adapter
from typing import Dict, Any, Optional, Union, cast
from mcp.types import CallToolResult, ListToolsResult
from openmas.core.simf.models import SIMFMessage

class MCPAdapter:
    """Type-safe MCP protocol adapter."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
    
    def convert_to_simf(
        self, 
        mcp_result: Union[CallToolResult, ListToolsResult]
    ) -> SIMFMessage:
        """Convert MCP result to SIMF message with proper type handling."""
        
        # Type narrowing for different MCP result types
        if isinstance(mcp_result, ListToolsResult):
            # Safe to access .tools attribute
            tools_data = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "schema": tool.inputSchema.model_dump() if tool.inputSchema else {}
                }
                for tool in mcp_result.tools
            ]
            return create_structured_data_message(data={"tools": tools_data})
        
        elif isinstance(mcp_result, CallToolResult):
            # Handle call tool results
            content_data = []
            for content in mcp_result.content:
                if hasattr(content, 'text'):
                    content_data.append({"type": "text", "text": content.text})
                else:
                    content_data.append({"type": "unknown", "data": str(content)})
            
            return create_structured_data_message(data={"result": content_data})
        
        else:
            raise ValueError(f"Unsupported MCP result type: {type(mcp_result)}")
```

---

## Common MyPy Error Solutions

### Error: `Missing named argument "source_protocol_type"`

```python
# ❌ WRONG: Missing required arguments
message = SIMFMessage(
    message_id="123",
    source_agent_id="agent1",
    target_agent_id="agent2"
)

# ✅ CORRECT: Include all required arguments
from openmas.core.simf.models import SIMFMessage, MessageType, ProtocolType

message = SIMFMessage(
    message_id="123",
    source_agent_id="agent1",
    target_agent_id="agent2",
    message_type=MessageType.REQUEST,
    source_protocol_type=ProtocolType.INTERNAL,
    timestamp=datetime.utcnow(),
    payload=None
)
```

### Error: `Function is missing a return type annotation`

```python
# ❌ WRONG: Missing return type
def test_agent_creation():
    agent = create_agent("test")
    assert agent.id == "test"

# ✅ CORRECT: Explicit return type
def test_agent_creation() -> None:
    agent = create_agent("test")
    assert agent.id == "test"
```

---

## AI Development Patterns

### Pattern: Copy-Paste Ready Agent Template

```python
"""
Template for creating new OpenMAS agents with proper typing.
Copy this template and modify as needed.
"""
from typing import Dict, Any, Optional, List
from openmas.agent.base_agent import Agent
from openmas.core.simf.models import SIMFMessage, ContentPayload
from openmas.core.simf.functions import create_text_message

class MyAgent(Agent):
    """Template agent with proper typing patterns."""
    
    def __init__(
        self, 
        agent_id: str, 
        name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(agent_id=agent_id, name=name, config=config)
        self.custom_config = config or {}
    
    async def process_message(self, message: SIMFMessage) -> Optional[SIMFMessage]:
        """Process incoming messages with type safety."""
        try:
            if not message.payload:
                return None
            
            # Type-safe payload handling
            response_text = await self._handle_payload(message.payload)
            
            if response_text:
                return create_text_message(
                    text=response_text,
                    source_agent_id=self.agent_id,
                    target_agent_id=message.source_agent_id,
                    session_id=message.session_id
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return None
    
    async def _handle_payload(self, payload: ContentPayload) -> Optional[str]:
        """Handle different payload types safely."""
        if isinstance(payload, TextContentPayload):
            return f"Processed: {payload.text}"
        elif isinstance(payload, StructuredDataContentPayload):
            return f"Processed data: {len(payload.data)} items"
        else:
            return f"Unsupported payload type: {type(payload).__name__}"
    
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Return agent capabilities with proper typing."""
        return [
            {
                "name": "text_processing",
                "description": "Process text messages",
                "parameters": {
                    "text": {"type": "string", "required": True}
                }
            }
        ]
```

---

## Type Annotation Templates

### Exception Classes
```python
from typing import Optional, Dict, Any

class CustomException(Exception):
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
```

### Configuration Classes
```python
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ComponentConfig(BaseModel):
    name: str
    enabled: bool = True
    parameters: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    
    class Config:
        extra = "forbid"
```

### Async Functions
```python
from typing import Optional, Dict, Any
import asyncio

async def async_operation(
    input_data: Dict[str, Any],
    timeout: Optional[float] = None
) -> Dict[str, Any]:
    """Template for async functions with proper typing."""
    try:
        # Async operation logic here
        await asyncio.sleep(0.1)  # Placeholder
        return {"status": "success", "data": input_data}
    except asyncio.TimeoutError:
        return {"status": "timeout", "error": "Operation timed out"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

---

## Quality Checklist

Before submitting code, ensure:

- [ ] All function parameters have type annotations
- [ ] All function return types are specified
- [ ] Optional parameters use `Optional[Type]` or `Type | None`
- [ ] Generic types are parameterized (`Dict[str, Any]` not `dict`)
- [ ] Union types use `isinstance()` for type narrowing
- [ ] Exception classes have properly typed optional parameters
- [ ] Async functions have proper return type annotations
- [ ] All examples pass `mypy --strict` validation

---

## Integration with Development Workflow

### Pre-commit Hook Validation
All typing patterns in this document are validated by the pre-commit mypy hook.

### Task Creation Integration
When creating new tasks, reference these patterns to ensure type safety from the start.

### AI Assistant Guidelines
AI assistants should follow these patterns when generating OpenMAS code to prevent mypy errors.

---

*This document is part of the OpenMAS 0.3.0 quality infrastructure and should be updated as new typing patterns emerge.*
