# OpenMAS Typing Standards for Cursor AI

**Purpose**: Comprehensive typing guidance for AI-assisted development in OpenMAS
**Principle**: Generate type-safe, MyPy-compliant code from the start
**Last Updated**: 2025-01-25

## 🎯 **CRITICAL: Zero MyPy Errors Policy**

**MANDATORY**: AI must generate MyPy-compliant code that passes strict type checking without errors.

### **Pre-Generation Type Checklist (REQUIRED)**

Before writing ANY code, ensure:

- [ ] **All functions have return type annotations** - no `-> None` omissions
- [ ] **All parameters have type annotations** - including `**kwargs: Any`
- [ ] **Union types use isinstance() checks** - never direct attribute access
- [ ] **Generic types are parameterized** - `dict[str, Any]`, not `dict`
- [ ] **Optional types are explicit** - `Optional[str]` or `str | None`
- [ ] **Async functions properly typed** - `async def func() -> Awaitable[T]`
- [ ] **Class attributes have type annotations** - including private attributes

## 🛡️ **Union Type Handling (CRITICAL)**

### **SIMF Payload Union Patterns**
```python
# ✅ CORRECT: Type narrowing with isinstance()
def process_payload(payload: PayloadUnion) -> str:
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

# ❌ WRONG: Direct attribute access on union
def process_payload_wrong(payload: PayloadUnion) -> str:
    return payload.text  # MyPy error: union-attr
```

### **MCP Result Type Handling**
```python
# ✅ CORRECT: MCP result type narrowing
async def handle_mcp_result(result: CallToolResult) -> dict[str, Any]:
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

# ❌ WRONG: Assuming result structure
async def handle_mcp_result_wrong(result: CallToolResult) -> dict[str, Any]:
    return result.content.data  # MyPy error: union-attr
```

## 🏗️ **OpenMAS-Specific Type Patterns**

### **Agent Implementation Pattern**
```python
# ✅ CORRECT: Fully typed agent implementation
from typing import Any, Optional
from openmas.agent.base import Agent
from openmas.core.simf.models import SIMFMessage, PayloadUnion

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
                return create_tool_result_message(
                    target_agent_id=simf_message.source_agent_id,
                    result=result,
                    status=InvocationStatus.SUCCESS,
                    session_id=simf_message.session_id,
                    source_protocol_type=simf_message.source_protocol_type
                )
            except Exception as e:
                return create_tool_result_message(
                    target_agent_id=simf_message.source_agent_id,
                    result={"error": str(e)},
                    status=InvocationStatus.FAILURE,
                    session_id=simf_message.session_id,
                    source_protocol_type=simf_message.source_protocol_type
                )
        else:
            raise ValueError(f"Unsupported payload type: {type(simf_message.payload)}")
    
    async def _execute_internal(self, capability_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Internal execution with proper typing."""
        # Implementation here
        return {"result": "success"}

# ❌ WRONG: Missing type annotations
class MyCustomAgent(Agent):
    def __init__(self, agent_id, name, config=None):
        super().__init__(agent_id, name)
        self._config = config or {}
    
    async def execute_capability(self, simf_message):
        # No type checking, potential runtime errors
        capability_name = simf_message.payload.invocation_name  # Could fail
        return create_tool_result_message(...)  # Missing required args
```

### **Protocol Adapter Pattern**
```python
# ✅ CORRECT: Typed protocol adapter
from typing import Any, Optional, Protocol
from openmas.protocols.base import IProtocolAdapter
from openmas.core.simf.models import SIMFMessage

class MCPProtocolAdapter(IProtocolAdapter):
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
            raise ConnectionError(f"Failed to connect to MCP server: {e}")
    
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
        # Implementation details with proper return type
        pass

# ❌ WRONG: Untyped protocol adapter
class MCPProtocolAdapter:
    def __init__(self, config):
        self._config = config
        self._session = None
    
    async def send_message(self, message):
        mcp_request = self._translate_simf_to_mcp(message)
        await self._session.send_request(mcp_request)  # Could be None
```

## 🚫 **MyPy Error Prevention Rules**

### **Union Attribute Errors (union-attr)**
```python
# ✅ PREVENT: Always use isinstance() for union types
def handle_payload(payload: PayloadUnion) -> str:
    if isinstance(payload, TextContentPayload):
        return payload.text  # Safe after type check
    elif isinstance(payload, StructuredDataContentPayload):
        return str(payload.data)  # Safe after type check
    else:
        return "Unknown payload"

# ❌ CAUSES ERROR: Direct attribute access
def handle_payload_wrong(payload: PayloadUnion) -> str:
    return payload.text  # union-attr error
```

### **Missing Annotations (no-untyped-def)**
```python
# ✅ PREVENT: All functions must have complete type annotations
async def process_agent_message(
    agent_id: str, 
    message: SIMFMessage, 
    context: Optional[dict[str, Any]] = None
) -> SIMFMessage:
    """Process message with full type annotations."""
    # Implementation
    pass

# ✅ PREVENT: Even simple functions need annotations
def get_agent_name(self) -> str:
    """Get agent name."""
    return self._name

# ❌ CAUSES ERROR: Missing return type
async def process_agent_message(agent_id: str, message: SIMFMessage):
    pass  # no-untyped-def error
```

### **Assignment Errors (assignment)**
```python
# ✅ PREVENT: Type-compatible assignments
def create_message_data() -> dict[str, Any]:
    """Create message data with proper typing."""
    data: dict[str, Any] = {
        "agent_id": "test_agent",
        "timestamp": datetime.now().isoformat(),
        "payload": {"type": "text", "content": "Hello"}
    }
    return data

# ✅ PREVENT: Proper type casting when needed
def handle_external_data(raw_data: Any) -> dict[str, str]:
    """Handle external data with type validation."""
    if isinstance(raw_data, dict):
        # Safe casting after type check
        return {str(k): str(v) for k, v in raw_data.items()}
    else:
        raise ValueError(f"Expected dict, got {type(raw_data)}")

# ❌ CAUSES ERROR: Type incompatible assignment
def create_message_data_wrong() -> dict[str, str]:
    data: dict[str, str] = {
        "agent_id": "test_agent",
        "timestamp": datetime.now()  # assignment error: datetime not str
    }
    return data
```

### **Call Argument Errors (call-arg)**
```python
# ✅ PREVENT: Correct function signatures
def create_simf_message(
    target_agent_id: str,
    payload: PayloadUnion,
    session_id: str,
    source_protocol_type: str,
    message_type: MessageType = MessageType.CAPABILITY_INVOCATION
) -> SIMFMessage:
    """Create SIMF message with all required arguments."""
    return SIMFMessage(
        message_id=str(uuid.uuid4()),
        target_agent_id=target_agent_id,
        source_agent_id="system",
        message_type=message_type,
        payload=payload,
        session_id=session_id,
        source_protocol_type=source_protocol_type,
        timestamp=datetime.now()
    )

# ✅ PREVENT: Use factory functions correctly
message = create_invocation_message(
    target_agent_id="test_agent",
    invocation_name="test_capability",
    arguments={"param": "value"},
    session_id="test_session"
)

# ❌ CAUSES ERROR: Missing required arguments
message = create_invocation_message(
    target_agent_id="test_agent",
    invocation_name="test_capability"
    # Missing session_id - call-arg error
)
```

## 🔧 **Generic Type Usage**

### **Collection Types**
```python
# ✅ CORRECT: Parameterized generic types
from typing import Any, Dict, List, Optional, Set, Tuple

# Modern type annotations (Python 3.9+)
agent_configs: dict[str, Any] = {}
capability_handlers: dict[str, Callable[[dict[str, Any]], Awaitable[str]]] = {}
message_queue: list[SIMFMessage] = []
active_sessions: set[str] = set()
connection_info: tuple[str, int] = ("localhost", 8080)

# Legacy type annotations (if needed)
agent_configs: Dict[str, Any] = {}
message_queue: List[SIMFMessage] = []

# ❌ WRONG: Unparameterized generics
agent_configs: dict = {}  # Missing type parameters
message_queue: list = []  # Missing type parameters
```

### **Custom Generic Classes**
```python
# ✅ CORRECT: Generic class implementation
from typing import Generic, TypeVar

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

# Usage with type safety
text_processor = MessageProcessor[TextContentPayload](TextContentPayload)
text_processor.register_handler("default", lambda p: p.text)
```

## 🧪 **Testing Type Patterns**

### **Typed Test Fixtures**
```python
# ✅ CORRECT: Typed test fixtures
import pytest
from typing import AsyncGenerator, Generator
from openmas.agent.mcp_agent import MCPAgent

@pytest.fixture
async def mcp_agent() -> AsyncGenerator[MCPAgent, None]:
    """Create MCP agent for testing."""
    agent = MCPAgent(
        agent_id="test_agent",
        name="Test Agent",
        mcp_server_command=["python", "test_server.py"]
    )
    await agent.start()
    try:
        yield agent
    finally:
        await agent.stop()

@pytest.fixture
def sample_simf_message() -> SIMFMessage:
    """Create sample SIMF message."""
    return create_invocation_message(
        target_agent_id="test_agent",
        invocation_name="test_capability",
        arguments={"param": "value"},
        session_id="test_session"
    )

# ❌ WRONG: Untyped fixtures
@pytest.fixture
async def mcp_agent():
    agent = MCPAgent("test_agent", "Test Agent", ["python", "test_server.py"])
    await agent.start()
    yield agent
    await agent.stop()
```

### **Type-Safe Test Assertions**
```python
# ✅ CORRECT: Type-safe test assertions
async def test_agent_execution_typed(mcp_agent: MCPAgent) -> None:
    """Test agent execution with proper typing."""
    result = await mcp_agent.execute_mcp_tool(
        tool_name="analyze_text",
        parameters={"text": "test", "analysis_type": "sentiment"}
    )
    
    # Type-safe assertions
    assert isinstance(result, dict)
    assert "analysis_type" in result
    assert isinstance(result["analysis_type"], str)
    assert result["analysis_type"] == "sentiment"

# ❌ WRONG: Untyped test
async def test_agent_execution_untyped(mcp_agent):
    result = await mcp_agent.execute_mcp_tool("analyze_text", {"text": "test"})
    assert result["analysis_type"] == "sentiment"  # Could fail at runtime
```

## 🔍 **IDE Integration Commands**

### **MyPy Validation Shortcuts**
```bash
# Quick type check for current file
poetry run mypy src/openmas/agent/mcp_agent.py

# Check specific error types
poetry run mypy src/openmas --show-error-codes | grep "union-attr"
poetry run mypy src/openmas --show-error-codes | grep "no-untyped-def"
poetry run mypy src/openmas --show-error-codes | grep "assignment"
poetry run mypy src/openmas --show-error-codes | grep "call-arg"

# Full project type check
poetry run mypy src/openmas

# Type check with verbose output
poetry run mypy src/openmas --verbose
```

### **Quality Enforcement Pipeline**
```bash
# Complete typing validation
echo "=== TYPE CHECKING ==="
poetry run mypy src/openmas --show-error-codes

echo "=== LINTING ==="
poetry run ruff check src/openmas tests

echo "=== FORMATTING ==="
poetry run ruff format src/openmas tests

echo "=== TESTING ==="
python -m pytest tests/ -x --tb=short
```

## 📋 **Quick Reference Checklist**

### **Before Committing Code**
- [ ] All functions have return type annotations
- [ ] All parameters have type annotations (including `**kwargs: Any`)
- [ ] Union types use `isinstance()` checks before attribute access
- [ ] Generic types are properly parameterized (`dict[str, Any]`)
- [ ] Optional types are explicit (`Optional[T]` or `T | None`)
- [ ] No MyPy errors: `poetry run mypy src/openmas`
- [ ] All tests pass: `python -m pytest tests/`

### **Common Type Patterns**
- **SIMF Messages**: Always use factory functions with all required args
- **Union Payloads**: Always use `isinstance()` before accessing attributes
- **MCP Results**: Handle both string and structured result types
- **Async Functions**: Proper `async def` with `Awaitable[T]` return types
- **Error Handling**: Type-specific exception handling with proper annotations

---

## 🎯 **Summary: Type-Safe Development**

**Core Principle**: Generate MyPy-compliant code from the start, never fix typing issues later.

**Type Safety Mindset**:
1. **Annotate everything** - functions, parameters, class attributes
2. **Narrow union types** - always use `isinstance()` checks
3. **Parameterize generics** - `dict[str, Any]`, not `dict`
4. **Handle optionals explicitly** - `Optional[T]` or `T | None`
5. **Validate with MyPy** - run type checking before committing

**Remember**: Type safety prevents runtime errors and improves code maintainability. Every type annotation is documentation that helps both humans and tools understand your code.
