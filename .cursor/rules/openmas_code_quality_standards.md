# OpenMAS Code Quality Standards

**Purpose**: Proactive code quality guidelines for AI agents and developers
**Principle**: Generate lint-free, production-ready code from the start
**Last Updated**: 2024-12-28

## 🚨 **CRITICAL: Proactive Code Quality**

**MANDATORY**: AI agents MUST generate lint-free code from the start, NOT fix issues afterward.

### **Pre-Generation Checklist (REQUIRED)**

Before writing ANY code, ensure:

- [ ] **88-character line limit enforced** - wrap long lines during generation
- [ ] **Only import what you use** - verify each import is utilized
- [ ] **Type hints for all functions** - parameters, returns, complex variables
- [ ] **Black-compatible formatting** - proper spacing, quotes, structure
- [ ] **No unused variables** - avoid temporary assignments that aren't used
- [ ] **Docstring compliance** - Google-style for all public APIs
- [ ] **Async/await correctness** - proper async context management

## 📏 **Code Formatting Standards**

### **Line Length: 88 Characters**
```python
# ✅ CORRECT: Modern 88-character standard
def process_agent_message(
    agent_id: str, message: SIMFMessage, context: ProcessingContext
) -> SIMFResponse:
    """Process incoming agent message with full context validation."""
    return self.processor.handle_message(agent_id, message, context)

# ❌ WRONG: Exceeds 88 characters
def process_agent_message(agent_id: str, message: SIMFMessage, context: ProcessingContext) -> SIMFResponse:
```

### **Import Organization**
```python
# ✅ CORRECT: Organized imports, only what's used
from typing import Dict, List, Optional
import asyncio
import logging

from openmas.core.simf import SIMFMessage, SIMFMessageType
from openmas.agent.base import Agent
from openmas.exceptions import AgentError

# ❌ WRONG: Unused imports, poor organization
from typing import *
import os, sys, json, asyncio, logging, pathlib
from openmas.core.simf import *
```

### **Type Hints (MANDATORY)**
```python
# ✅ CORRECT: Complete type annotation
async def register_capability(
    self,
    capability_name: str,
    handler: Callable[[Dict[str, Any]], Awaitable[str]]
) -> None:
    """Register async capability with proper type safety."""
    self._capabilities[capability_name] = handler

# ❌ WRONG: Missing type hints
async def register_capability(self, capability_name, handler):
    self._capabilities[capability_name] = handler
```

## 🏗️ **Architecture Compliance**

### **SIMF Integration (MANDATORY)**
```python
# ✅ CORRECT: Protocol-agnostic with SIMF translation
class MCPProtocolAdapter(IProtocolAdapter):
    async def send_message(self, simf_message: SIMFMessage) -> None:
        # Translate SIMF to protocol-specific format
        mcp_request = self._translate_simf_to_mcp(simf_message)
        result = await self.session.call_tool(mcp_request.name, mcp_request.args)
        # Translate back to SIMF
        simf_response = self._translate_mcp_to_simf(result)
        await self._notify_response(simf_response)

# ❌ WRONG: Direct protocol bridging, bypasses SIMF
class MCPDirectAdapter:
    async def bridge_mcp_to_grpc(self, mcp_message):
        # This violates SIMF-first architecture
        grpc_message = convert_mcp_to_grpc(mcp_message)
        return grpc_message
```

### **Interface Implementation**
```python
# ✅ CORRECT: Proper ABC implementation with full typing
from abc import ABC, abstractmethod
from typing import Protocol

class IProtocolAdapter(ABC):
    @abstractmethod
    async def send_message(self, message: SIMFMessage) -> None:
        """Send SIMF message via protocol-specific transport."""
        pass

    @abstractmethod
    async def receive_message(self) -> SIMFMessage:
        """Receive and translate message to SIMF format."""
        pass

# ❌ WRONG: Missing ABC, poor typing
class IProtocolAdapter:
    def send_message(self, message):
        raise NotImplementedError
```

## 🧪 **Testing Standards**

### **Test Coverage Requirements**
- **Minimum 80% coverage** for all new code (enforced in pyproject.toml)
- **Real integration tests** - never mock without testing real implementations first
- **Anti-hallucination validation** - test against actual libraries/APIs

### **Test Structure**
```python
# ✅ CORRECT: Comprehensive test with real validation
import pytest
import asyncio
from unittest.mock import AsyncMock

from openmas.protocols.mcp.adapter import MCPProtocolAdapter
from openmas.core.simf import SIMFMessage, SIMFMessageType

@pytest.mark.integration
@pytest.mark.mcp
@pytest.mark.real
async def test_mcp_adapter_real_integration():
    """Test MCP adapter against real MCP server."""
    # Test with real MCP server, not just mocks
    adapter = MCPProtocolAdapter(config=real_mcp_config)

    # Initialize properly
    await asyncio.wait_for(adapter.initialize(), timeout=10.0)

    # Test actual SIMF message flow
    simf_message = SIMFMessage(
        type=SIMFMessageType.TOOL_CALL,
        tool_name="test_tool",
        arguments={"arg": "value"}
    )

    result = await adapter.send_message(simf_message)
    assert result.type == SIMFMessageType.TOOL_RESPONSE
    assert not result.is_error

# ❌ WRONG: Mock-only test that could pass incorrectly
@pytest.mark.unit
async def test_mcp_adapter_mock_only():
    adapter = MCPProtocolAdapter(config=mock_config)
    adapter.session = AsyncMock()  # This could hide real issues
    # ... rest is unreliable
```

### **Test Markers Usage**
```python
# Use appropriate markers for test organization
@pytest.mark.unit          # Fast unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.mcp           # MCP-specific tests
@pytest.mark.grpc          # gRPC-specific tests
@pytest.mark.mqtt          # MQTT-specific tests
@pytest.mark.async         # Async operation tests
@pytest.mark.real          # Real library/API tests
@pytest.mark.anti_hallucination  # Anti-hallucination validation
```

## 📝 **Documentation Standards**

### **Google-Style Docstrings (MANDATORY)**
```python
# ✅ CORRECT: Complete Google-style documentation
async def execute_capability(
    self,
    capability_name: str,
    **kwargs: Any
) -> str:
    """Execute agent capability with provided arguments.

    Executes the specified capability using the agent's registered
    capability handlers. Supports both sync and async handlers.

    Args:
        capability_name: Name of the capability to execute
        **kwargs: Keyword arguments to pass to the capability handler

    Returns:
        String result from capability execution

    Raises:
        AgentError: If capability is not registered or execution fails
        ValueError: If capability_name is empty or invalid

    Example:
        >>> result = await agent.execute_capability("search", query="test")
        >>> print(result)
        "Search completed: 5 results found"
    """
    if not capability_name:
        raise ValueError("capability_name cannot be empty")

    if capability_name not in self.capabilities:
        raise AgentError(f"Capability '{capability_name}' not registered")

    handler = self.capabilities[capability_name]
    return await handler(**kwargs)

# ❌ WRONG: Minimal or missing documentation
async def execute_capability(self, capability_name: str, **kwargs: Any) -> str:
    """Execute capability."""  # Too brief, missing critical info
    return await self.capabilities[capability_name](**kwargs)
```

### **README Standards**
- **Clear project purpose** and architecture overview
- **Quick start guide** with working examples
- **Configuration examples** with actual values
- **API documentation links** to detailed guides

## 🚫 **Code Prohibitions**

### **Never Do These Things**
```python
# ❌ NEVER: Star imports
from openmas.core.simf import *

# ❌ NEVER: Bare except clauses
try:
    result = await operation()
except:
    pass

# ❌ NEVER: Long functions (>50 lines)
def massive_function_that_does_everything():
    # 100+ lines of mixed concerns
    pass

# ❌ NEVER: Hardcoded values without configuration
def connect_to_server():
    return connect("localhost:8080")  # Should be configurable

# ❌ NEVER: Missing async context management
session = ClientSession()
await session.initialize()
# Missing: async with or try/finally cleanup

# ❌ NEVER: Protocol-specific logic in shared components
class Agent:
    def send_grpc_message(self):  # Violates protocol agnosticism
        pass
```

### **Always Do These Things**
```python
# ✅ ALWAYS: Explicit imports
from openmas.core.simf import SIMFMessage, SIMFMessageType

# ✅ ALWAYS: Specific exception handling
try:
    result = await operation()
except AgentError as e:
    logger.error(f"Agent operation failed: {e}")
    raise
except asyncio.TimeoutError:
    logger.warning("Operation timed out")
    raise AgentError("Operation timeout")

# ✅ ALWAYS: Small, focused functions
async def initialize_session() -> None:
    """Initialize MCP session with timeout."""
    await asyncio.wait_for(self.session.initialize(), timeout=10.0)

async def register_tool(self, tool_name: str) -> None:
    """Register MCP tool as agent capability."""
    await self.register_capability(f"mcp_tool_{tool_name}", tool_name)

# ✅ ALWAYS: Configuration-driven values
def connect_to_server(self, config: ServerConfig) -> Connection:
    return connect(f"{config.host}:{config.port}")

# ✅ ALWAYS: Proper async resource management
async def execute_mcp_operation(self):
    async with stdio_client(self.server_params) as (read, write):
        session = ClientSession(read, write)
        await asyncio.wait_for(session.initialize(), timeout=10.0)
        return await session.list_tools()

# ✅ ALWAYS: Protocol-agnostic shared components
class Agent:
    async def send_message(self, message: SIMFMessage) -> None:
        # Protocol translation handled by adapters
        await self.protocol_adapter.send_message(message)
```

## 🔧 **Development Workflow**

### **Pre-Commit Checklist**
1. **Run formatters**: `black --line-length 88 src/ tests/`
2. **Run linters**: `ruff check src/ tests/`
3. **Type checking**: `mypy src/`
4. **Run tests**: `pytest tests/unit/` (fast feedback)
5. **Coverage check**: `pytest --cov=src tests/`
6. **Integration tests**: `pytest tests/integration/` (when needed)

### **Quality Commands**
```bash
# Format code (run automatically)
black --line-length 88 src/ tests/

# Lint check (must pass)
ruff check src/ tests/

# Type check (must pass)
mypy src/

# Test with coverage (80% minimum)
pytest --cov=src --cov-report=term-missing tests/

# Full quality check
tox -e quality
```

## 📊 **Metrics & Enforcement**

### **Automated Enforcement**
- **Line length**: 88 characters (Black + pre-commit hooks)
- **Import sorting**: isort with Black compatibility
- **Type checking**: mypy with strict mode
- **Test coverage**: 80% minimum threshold
- **Lint compliance**: Zero ruff violations allowed

### **Quality Gates**
- **CI/CD**: All quality checks must pass before merge
- **Pre-commit hooks**: Format and lint automatically
- **Coverage reports**: Generated and tracked over time
- **Documentation**: All public APIs must have complete docstrings

---

## 🎯 **Summary: Excellence by Default**

**Core Principle**: Write it right the first time, not fix it later.

**Quality Mindset**:
1. **Plan before coding** - understand requirements fully
2. **Generate clean code** - apply standards during creation
3. **Test comprehensively** - real implementations, high coverage
4. **Document completely** - clear, helpful, accurate
5. **Validate immediately** - run quality checks after each change

**Remember**: Quality is not a cleanup task—it's how we work from the start. Every line of code should meet production standards from the moment it's written.
