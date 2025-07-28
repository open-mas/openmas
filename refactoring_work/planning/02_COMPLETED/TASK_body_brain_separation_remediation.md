# TASK: Body-Brain Separation (Reasoning Agnosticism) Remediation

**Task ID**: ARCH-001  
**Priority**: CRITICAL  
**Type**: Architectural Remediation  
**Estimated Effort**: 3-4 days  
**Dependencies**: None (foundational)

## Task Overview

Implement proper Body-Brain separation in the OpenMAS Agent architecture to achieve reasoning agnosticism as specified in the design documentation. The current Agent implementation violates this core architectural principle by embedding both communication logic ("body") and reasoning logic ("brain") within a single monolithic class.

## Three-Input Task Creation Protocol Compliance

### Input 1: Design Documentation Analysis

**Primary Reference**: `/refactoring_work/design/01_architecture/architectural_patterns.md` (lines 24-39)

**Design Specification**:
```python
class Agent:
    def __init__(self, communicator, reasoning_engine):
        self.communicator = communicator  # "Body" - handles external communication
        self.reasoning = reasoning_engine  # "Brain" - handles decision making

    async def process_message(self, message):
        # Communication layer handles message parsing
        context = self.communicator.parse_message(message)
        # Reasoning layer decides on response
        action = await self.reasoning.decide_action(context)
        # Convert back to standard formats and sends response
        return self.communicator.format_response(action)
```

**Architectural Principle**: Clear separation between communication infrastructure (body) and reasoning logic (brain) to enable reasoning agnosticism and protocol independence.

### Input 2: User Business/Personal Needs

**Core Business Value**:
- **Reasoning Flexibility**: Enable swapping between different reasoning approaches (rule-based, BDI, LLM, hybrid) without changing communication infrastructure
- **Protocol Independence**: Support multiple communication protocols (MCP, A2A, HTTP) without affecting reasoning logic
- **Extensibility**: Allow addition of new reasoning engines and communication protocols independently
- **Testing & Development**: Enable independent testing and development of reasoning vs. communication components

**Real-World Use Cases**:
- PowerBI agent using rule-based reasoning for data queries but LLM reasoning for natural language interpretation
- SQL Server agent switching between deterministic query optimization and AI-assisted query generation
- Analytics workflow agents combining multiple reasoning approaches for different task types

### Input 3: Current Codebase Implementation Status

**Current Violation** (`src/openmas/agent/base_agent.py` lines 174-220):
```python
class Agent(IMessageHandler):
    def __init__(self, config: AgentConfig, state_manager, protocol_adapters):
        # VIOLATION: No separate communicator or reasoning_engine parameters
        # VIOLATION: Agent directly manages both communication AND reasoning logic
        self.protocol_adapters = protocol_adapters or {}
        self.capabilities: set[str] = set(config.capabilities)
        # ... direct management of both "body" and "brain" concerns
```

**Existing Infrastructure to Leverage**:
- `IMessageHandler` interface for message processing
- `SIMFMessage` internal message format
- `IProtocolAdapter` interface for protocol abstraction
- `AgentConfig` configuration system
- 232 passing tests demonstrating foundation works

**Missing Components to Build**:
- `ICommunicator` interface and implementation
- `IReasoningEngine` interface and implementation
- Refactored `Agent` class with proper separation
- Factory classes for creating communicator and reasoning components

## Implementation Specification

### Phase 1: Interface Design

**1.1 Create ICommunicator Interface**
```python
# src/openmas/agent/interfaces/communicator.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from openmas.core.simf import SIMFMessage

class ICommunicator(ABC):
    """Interface for agent communication infrastructure (body)."""
    
    @abstractmethod
    async def parse_message(self, raw_message: Any) -> Dict[str, Any]:
        """Parse incoming message into context for reasoning."""
        pass
    
    @abstractmethod
    async def format_response(self, action: Dict[str, Any]) -> SIMFMessage:
        """Format reasoning decision into outbound message."""
        pass
    
    @abstractmethod
    async def send_message(self, message: SIMFMessage, target: str) -> bool:
        """Send message through appropriate protocol."""
        pass
    
    @abstractmethod
    def get_supported_protocols(self) -> List[str]:
        """Get list of supported communication protocols."""
        pass
```

**1.2 Create IReasoningEngine Interface**
```python
# src/openmas/agent/interfaces/reasoning.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class IReasoningEngine(ABC):
    """Interface for agent reasoning logic (brain)."""
    
    @abstractmethod
    async def decide_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make reasoning decision based on context."""
        pass
    
    @abstractmethod
    async def update_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """Update reasoning engine's knowledge base."""
        pass
    
    @abstractmethod
    def get_reasoning_type(self) -> str:
        """Get type of reasoning engine (e.g., 'rule-based', 'llm', 'bdi')."""
        pass
```

### Phase 2: Implementation Classes

**2.1 Default Communicator Implementation**
```python
# src/openmas/agent/communicator.py
class DefaultCommunicator(ICommunicator):
    """Default communicator implementation using protocol adapters."""
    
    def __init__(self, protocol_adapters: Dict[str, IProtocolAdapter]):
        self.protocol_adapters = protocol_adapters
        self.preferred_protocols = ["mcp", "simf", "http"]
    
    async def parse_message(self, raw_message: Any) -> Dict[str, Any]:
        """Extract context from message for reasoning."""
        if isinstance(raw_message, SIMFMessage):
            return {
                "message_type": raw_message.message_type,
                "payload": raw_message.payload,
                "sender": raw_message.sender_id,
                "session": raw_message.session_id
            }
        # Handle other message types...
    
    async def format_response(self, action: Dict[str, Any]) -> SIMFMessage:
        """Convert reasoning decision to SIMF message."""
        return SIMFMessage(
            message_type=action.get("type", "response"),
            payload=action.get("content", {}),
            sender_id=action.get("sender"),
            session_id=action.get("session")
        )
```

**2.2 Simple Reasoning Engine Implementation**
```python
# src/openmas/agent/reasoning/simple_reasoning.py
class SimpleReasoningEngine(IReasoningEngine):
    """Simple rule-based reasoning engine for basic agent behavior."""
    
    def __init__(self, capabilities: Set[str]):
        self.capabilities = capabilities
        self.knowledge_base: Dict[str, Any] = {}
    
    async def decide_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean decision making interface.
        
        Converts context format to ReasoningContext for strategy processing.
        """
        message_type = context.get("message_type")
        payload = context.get("payload", {})
        
        if message_type == "capability_request":
            capability = payload.get("capability")
            if capability in self.capabilities:
                return {
                    "type": "capability_response",
                    "content": {"status": "success", "result": f"Executed {capability}"},
                    "sender": context.get("sender"),
                    "session": context.get("session")
                }
            else:
                return {
                    "type": "error_response",
                    "content": {"error": f"Capability {capability} not supported"},
                    "sender": context.get("sender"),
                    "session": context.get("session")
                }
        
        # Default response
        return {
            "type": "acknowledgment",
            "content": {"message": "Message received"},
            "sender": context.get("sender"),
            "session": context.get("session")
        }
```

### Phase 3: Agent Refactoring

**3.1 Refactor Agent Class**
```python
# src/openmas/agent/base_agent.py (refactored)
class Agent(IMessageHandler):
    """
    Refactored Agent with proper Body-Brain separation.
    
    The Agent orchestrates between the Communicator (body) and ReasoningEngine (brain)
    but does not implement communication or reasoning logic directly.
    """
    
    def __init__(
        self,
        config: AgentConfig,
        communicator: ICommunicator,
        reasoning_engine: IReasoningEngine,
        state_manager: IAgentStateManager | None = None,
    ):
        """
        Initialize agent with separated components.
        
        Args:
            config: Agent configuration
            communicator: Communication infrastructure (body)
            reasoning_engine: Reasoning logic (brain)
            state_manager: State management implementation
        """
        self.config = config
        self.agent_id = config.agent_id
        self.name = config.name
        
        # Body-Brain separation
        self.communicator = communicator
        self.reasoning_engine = reasoning_engine
        
        # Core components
        self.state_manager = state_manager
        
        # Message handling
        self.message_queue: asyncio.Queue[SIMFMessage] | None = None
        self.message_callbacks: list[Callable[[SIMFMessage], None]] = []
        self._running = False
        self._tasks: list[asyncio.Task] = []
        
        # Session management
        self.current_session_id: str | None = None
        self.sessions: dict[str, dict[str, Any]] = {}
        
        # Logging
        self.logger = logging.getLogger(f"openmas.agent.{self.agent_id}")
        self.logger.info(f"Agent {self.agent_id} ({self.name}) initialized with {reasoning_engine.get_reasoning_type()} reasoning")
    
    async def handle_message(self, message: SIMFMessage) -> SIMFMessage | None:
        """
        Process message using Body-Brain separation pattern.
        
        1. Communicator (body) parses message into context
        2. ReasoningEngine (brain) decides on action
        3. Communicator (body) formats response
        """
        try:
            # Body: Parse message into reasoning context
            context = await self.communicator.parse_message(message)
            
            # Brain: Make reasoning decision
            action = await self.reasoning_engine.decide_action(context)
            
            # Body: Format response
            response = await self.communicator.format_response(action)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            # Return error response through communicator
            error_action = {
                "type": "error_response",
                "content": {"error": str(e)},
                "sender": self.agent_id,
                "session": message.session_id
            }
            return await self.communicator.format_response(error_action)
    
    def set_reasoning_engine(self, reasoning_engine: IReasoningEngine) -> None:
        """Enable runtime reasoning engine swapping."""
        old_type = self.reasoning_engine.get_reasoning_type()
        self.reasoning_engine = reasoning_engine
        new_type = reasoning_engine.get_reasoning_type()
        self.logger.info(f"Reasoning engine changed from {old_type} to {new_type}")
```

### Phase 4: Factory Classes

**4.1 Component Factories**
```python
# src/openmas/agent/factories.py
class CommunicatorFactory:
    """Factory for creating communicator instances."""
    
    @staticmethod
    def create(config: AgentConfig, protocol_adapters: Dict[str, IProtocolAdapter]) -> ICommunicator:
        """Create communicator based on configuration."""
        return DefaultCommunicator(protocol_adapters)

class ReasoningEngineFactory:
    """Factory for creating reasoning engine instances."""
    
    @staticmethod
    def create(config: AgentConfig) -> IReasoningEngine:
        """Create reasoning engine based on configuration."""
        reasoning_type = config.reasoning_type if hasattr(config, 'reasoning_type') else 'simple'
        
        if reasoning_type == 'simple':
            return SimpleReasoningEngine(set(config.capabilities))
        # Future: Add LLM, BDI, hybrid reasoning engines
        else:
            raise ValueError(f"Unknown reasoning type: {reasoning_type}")

class AgentFactory:
    """Factory for creating complete agents with proper separation."""
    
    @staticmethod
    def create(
        config: AgentConfig,
        protocol_adapters: Dict[str, IProtocolAdapter] | None = None,
        state_manager: IAgentStateManager | None = None
    ) -> Agent:
        """Create agent with proper Body-Brain separation."""
        protocol_adapters = protocol_adapters or {}
        
        # Create separated components
        communicator = CommunicatorFactory.create(config, protocol_adapters)
        reasoning_engine = ReasoningEngineFactory.create(config)
        
        # Create agent with separated components
        return Agent(config, communicator, reasoning_engine, state_manager)
```

## Quality Enforcement (Phase 2.5)

### Ruff Configuration Compliance
```bash
# Validate ruff configuration
ruff check src/openmas/agent/ --config pyproject.toml
# Expected: line-length=120, ignore=E203, select=["E", "F", "I", "UP", "N", "B", "SIM"]
```

### MyPy Type Checking
```bash
# Strict typing validation
mypy src/openmas/agent/interfaces/ --strict
mypy src/openmas/agent/communicator.py --strict
mypy src/openmas/agent/reasoning/ --strict
mypy src/openmas/agent/base_agent.py --strict
mypy src/openmas/agent/factories.py --strict

# Specific error prevention
mypy src/openmas/agent/ --strict --show-error-codes | grep -E "(union-attr|no-untyped-def|assignment|call-arg)"
```

### Zero Regression Policy
```bash
# MANDATORY: Establish baseline before changes
echo "=== ESTABLISHING BASELINE - TESTS MUST PASS BEFORE CHANGES ==="
python -m pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
    echo "❌ BASELINE FAILED: Tests are already broken. Fix before proceeding."
    exit 1
fi
echo "✅ BASELINE ESTABLISHED: All tests passing before changes"

# MANDATORY: Zero regression validation after changes
echo "=== ZERO REGRESSION VALIDATION - TESTS MUST PASS AFTER CHANGES ==="
python -m pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
    echo "❌ REGRESSION DETECTED: Tests broken by changes. REVERT IMMEDIATELY."
    echo "❌ TASK FAILED: Cannot complete task with broken tests."
    exit 1
fi
echo "✅ ZERO REGRESSION CONFIRMED: All tests still passing after changes"
```

### Quality Gate Requirements
1. **#1 REQUIREMENT**: ZERO REGRESSION POLICY - All tests MUST pass before AND after changes (MANDATORY)
2. All new interfaces must have complete type annotations
3. All implementations must pass mypy --strict validation
4. Union type handling must use isinstance() checks where applicable
5. All public methods must have proper docstrings
6. Factory classes must handle configuration edge cases
7. Error handling must be comprehensive with proper logging
8. Integration tests must validate Body-Brain separation

## Testing Strategy

### Unit Tests
```python
# tests/agent/test_body_brain_separation.py
class TestBodyBrainSeparation:
    """Test proper Body-Brain separation implementation."""
    
    def test_communicator_interface_compliance(self):
        """Test that communicator implements ICommunicator correctly."""
        # Test interface compliance
        
    def test_reasoning_engine_interface_compliance(self):
        """Test that reasoning engine implements IReasoningEngine correctly."""
        # Test interface compliance
        
    def test_agent_separation(self):
        """Test that Agent properly separates body and brain concerns."""
        # Mock communicator and reasoning engine
        # Verify Agent delegates correctly
        
    def test_reasoning_engine_swapping(self):
        """Test runtime reasoning engine swapping."""
        # Create agent with one reasoning engine
        # Swap to different reasoning engine
        # Verify behavior changes appropriately
        
    def test_protocol_independence(self):
        """Test that reasoning is independent of communication protocol."""
        # Same reasoning engine with different communicators
        # Verify reasoning decisions are protocol-independent
```

### Integration Tests
```python
# tests/integration/test_body_brain_integration.py
class TestBodyBrainIntegration:
    """Test Body-Brain separation in realistic scenarios."""
    
    async def test_mcp_protocol_with_simple_reasoning(self):
        """Test MCP communication with simple reasoning engine."""
        # End-to-end test with real MCP messages
        
    async def test_reasoning_engine_switching(self):
        """Test switching reasoning engines during operation."""
        # Start with simple reasoning
        # Switch to different reasoning engine
        # Verify seamless transition
```

## Success Criteria

### Functional Requirements
- [ ] `ICommunicator` and `IReasoningEngine` interfaces implemented
- [ ] `DefaultCommunicator` handles protocol abstraction correctly
- [ ] `SimpleReasoningEngine` provides basic reasoning capability
- [ ] `Agent` class properly delegates to separated components
- [ ] Factory classes create components with proper configuration
- [ ] Runtime reasoning engine swapping works correctly

### Architectural Requirements
- [ ] Complete Body-Brain separation achieved
- [ ] Reasoning agnosticism enabled (can swap reasoning engines)
- [ ] Protocol independence maintained (reasoning unaware of protocols)
- [ ] No reasoning logic embedded in Agent class
- [ ] No communication logic embedded in reasoning engines

### Quality Requirements
- [ ] All 232+ tests continue to pass (zero regression)
- [ ] MyPy strict mode compliance for all new code
- [ ] Ruff linting compliance (line-length=120, ignore=E203)
- [ ] Complete type annotations for all interfaces and implementations
- [ ] Comprehensive error handling and logging

### Design Alignment
- [ ] Implementation matches `/refactoring_work/design/01_architecture/architectural_patterns.md` specification
- [ ] Enables future reasoning engine implementations (LLM, BDI, hybrid)
- [ ] Supports multi-protocol communication without reasoning changes
- [ ] Enables clean agent configurations for future development

## Deliverables

1. **Interface Definitions**:
   - `src/openmas/agent/interfaces/communicator.py`
   - `src/openmas/agent/interfaces/reasoning.py`

2. **Implementation Classes**:
   - `src/openmas/agent/communicator.py`
   - `src/openmas/agent/reasoning/simple_reasoning.py`

3. **Refactored Core**:
   - `src/openmas/agent/base_agent.py` (refactored)
   - `src/openmas/agent/factories.py`

4. **Test Suite**:
   - `tests/agent/test_body_brain_separation.py`
   - `tests/integration/test_body_brain_integration.py`

5. **Documentation Updates**:
   - Update agent documentation to reflect Body-Brain separation
   - Add reasoning engine development guide
   - Update configuration examples

## Notes

- This task is foundational for OpenMAS reasoning agnosticism
- Enables future specialized reasoning engines for PowerBI, SQL Server, analytics workflows
- Maintains compatibility with existing SIMF and protocol adapter infrastructure
- Sets architectural foundation for Facade and Strategy pattern implementations
- Critical for preventing the monolithic agent design that limits extensibility

## Anti-Hallucination Safeguards

- All interfaces reference existing `IMessageHandler` and `SIMFMessage` patterns
- Implementation leverages existing `AgentConfig` and `IProtocolAdapter` infrastructure
- Factory pattern follows existing OpenMAS configuration conventions
- Testing strategy builds on existing 232 passing tests
- No assumptions about non-existent infrastructure or capabilities
