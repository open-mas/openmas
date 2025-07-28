# TASK: Testing Framework Phase 2 - TestSupervisor Implementation

**Task ID**: TEST-002  
**Priority**: HIGH  
**Type**: Testing Infrastructure  
**Estimated Effort**: 1-2 days  
**Dependencies**: TEST-001 (Message Routing Fix)

## Task Overview

Implement the TestSupervisor pattern to resolve test suite hanging issues and establish robust async testing coordination. The current test suite hangs indefinitely due to improper async resource cleanup and coordination. This task implements the sophisticated async agent lifecycle management documented in the testing setup guidance.

## Three-Input Task Creation Protocol Compliance

### Input 1: Design Documentation Analysis

**Primary Reference**: `/refactoring_work/setup/testing_setup/04_async_integration_testing.md`

**Design Specification**: TestSupervisor pattern for sophisticated async agent lifecycle management
- Event-based test orchestration instead of time-based waits
- Proper async resource cleanup and coordination
- Timeout management and condition waiting
- Resource isolation between tests

**Secondary Reference**: `/refactoring_work/planning/TESTING_FRAMEWORK_IMPLEMENTATION_GUIDANCE.md` (Phase 2)

### Input 2: User Business/Personal Needs

**Core Business Value**:
- **Reliable Test Suite**: Developers need tests that run consistently without hanging
- **Fast Feedback Loop**: Test suite must complete quickly for rapid development cycles
- **Robust Async Testing**: Support for complex async agent interactions in PowerBI/SQL/analytics workflows
- **Developer Productivity**: Remove testing friction that blocks architectural remediation work

**Current Pain Points**:
- Test suite hangs indefinitely, requiring manual termination
- Improper async resource cleanup causes resource leaks
- Time-based waits are unreliable and slow
- Cannot reliably test complex agent interactions
- Blocking progress on Body-Brain separation and other architectural work

### Input 3: Current Codebase Implementation Status

**Current Problem**:
```python
# Current test patterns (problematic)
async def test_agent_interaction():
    agent = Agent(config)
    await agent.start()
    
    # PROBLEM: No proper cleanup, resources leak
    # PROBLEM: Time-based waits are unreliable
    await asyncio.sleep(1.0)  # Hope agent is ready
    
    # PROBLEM: No timeout management
    # PROBLEM: No event-based coordination
    # Test hangs here indefinitely
```

**Existing Infrastructure to Leverage**:
- ✅ pytest-asyncio framework already configured
- ✅ Basic async test patterns in `tests/integration/`
- ✅ Agent lifecycle methods (`start()`, `stop()`)
- ✅ Message processing infrastructure from TEST-001
- ✅ Test utilities in `tests/utils/`

**Missing Components to Build**:
- ⚠️ `TestSupervisor` class for async lifecycle management
- ⚠️ Event-based test coordination utilities
- ⚠️ Timeout management and condition waiting
- ⚠️ Async test fixtures with proper cleanup
- ⚠️ Resource isolation patterns

## Implementation Specification

### Phase 1: TestSupervisor Core Implementation

**1.1 TestSupervisor Class**
```python
# tests/utils/test_supervisor.py
import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Awaitable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from openmas.agent.base_agent import Agent
from openmas.core.simf import SIMFMessage

@dataclass
class TestContext:
    """Context for test execution with resource tracking."""
    test_name: str
    agents: List[Agent] = field(default_factory=list)
    tasks: List[asyncio.Task] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)
    events: Dict[str, asyncio.Event] = field(default_factory=dict)
    timeouts: Dict[str, float] = field(default_factory=dict)

class TestSupervisor:
    """
    Sophisticated async test coordination and resource management.
    
    Provides event-based test orchestration, timeout management,
    and proper resource cleanup for complex agent testing scenarios.
    """
    
    def __init__(self, default_timeout: float = 5.0):
        """
        Initialize TestSupervisor.
        
        Args:
            default_timeout: Default timeout for operations in seconds
        """
        self.default_timeout = default_timeout
        self.logger = logging.getLogger("TestSupervisor")
        self._active_contexts: Dict[str, TestContext] = {}
    
    @asynccontextmanager
    async def test_context(self, test_name: str, timeout: float = None):
        """
        Create isolated test context with automatic cleanup.
        
        Args:
            test_name: Name of the test for logging and tracking
            timeout: Test-specific timeout override
            
        Yields:
            TestContext: Isolated context for test execution
        """
        timeout = timeout or self.default_timeout
        context = TestContext(
            test_name=test_name,
            timeouts={"default": timeout}
        )
        
        self._active_contexts[test_name] = context
        self.logger.info(f"Starting test context: {test_name}")
        
        try:
            yield context
        finally:
            await self._cleanup_context(context)
            del self._active_contexts[test_name]
            self.logger.info(f"Cleaned up test context: {test_name}")
    
    async def _cleanup_context(self, context: TestContext) -> None:
        """Clean up all resources in test context."""
        self.logger.debug(f"Cleaning up context: {context.test_name}")
        
        # Stop all agents
        for agent in context.agents:
            try:
                if agent._running:
                    await asyncio.wait_for(agent.stop(), timeout=2.0)
            except Exception as e:
                self.logger.warning(f"Error stopping agent {agent.agent_id}: {e}")
        
        # Cancel all tasks
        for task in context.tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    self.logger.warning(f"Error cancelling task: {e}")
        
        # Clean up custom resources
        for name, resource in context.resources.items():
            try:
                if hasattr(resource, 'cleanup'):
                    await resource.cleanup()
                elif hasattr(resource, 'close'):
                    await resource.close()
            except Exception as e:
                self.logger.warning(f"Error cleaning up resource {name}: {e}")
    
    async def create_agent(
        self, 
        context: TestContext, 
        config: Any, 
        name: str = None
    ) -> Agent:
        """
        Create agent within test context with automatic tracking.
        
        Args:
            context: Test context for resource tracking
            config: Agent configuration
            name: Optional name for agent identification
            
        Returns:
            Agent: Created agent tracked in context
        """
        agent = Agent(config)
        context.agents.append(agent)
        
        if name:
            context.resources[f"agent_{name}"] = agent
        
        self.logger.debug(f"Created agent {agent.agent_id} in context {context.test_name}")
        return agent
    
    async def start_agent(self, context: TestContext, agent: Agent) -> None:
        """
        Start agent with timeout and error handling.
        
        Args:
            context: Test context
            agent: Agent to start
        """
        try:
            await asyncio.wait_for(
                agent.start(), 
                timeout=context.timeouts.get("agent_start", self.default_timeout)
            )
            self.logger.debug(f"Started agent {agent.agent_id}")
        except asyncio.TimeoutError:
            raise TimeoutError(f"Agent {agent.agent_id} failed to start within timeout")
    
    async def wait_for_condition(
        self,
        context: TestContext,
        condition: Callable[[], Awaitable[bool]],
        description: str,
        timeout: float = None,
        check_interval: float = 0.1
    ) -> None:
        """
        Wait for condition to become true with timeout.
        
        Args:
            context: Test context
            condition: Async function that returns bool
            description: Description for logging
            timeout: Timeout in seconds
            check_interval: How often to check condition
        """
        timeout = timeout or context.timeouts.get("condition", self.default_timeout)
        start_time = asyncio.get_event_loop().time()
        
        self.logger.debug(f"Waiting for condition: {description}")
        
        while True:
            try:
                if await condition():
                    self.logger.debug(f"Condition met: {description}")
                    return
            except Exception as e:
                self.logger.warning(f"Error checking condition {description}: {e}")
            
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(f"Condition not met within {timeout}s: {description}")
            
            await asyncio.sleep(check_interval)
    
    async def wait_for_value(
        self,
        context: TestContext,
        value_getter: Callable[[], Awaitable[Any]],
        expected_value: Any,
        description: str,
        timeout: float = None
    ) -> Any:
        """
        Wait for value getter to return expected value.
        
        Args:
            context: Test context
            value_getter: Async function that returns a value
            expected_value: Expected value to wait for
            description: Description for logging
            timeout: Timeout in seconds
            
        Returns:
            The actual value when condition is met
        """
        async def condition():
            value = await value_getter()
            return value == expected_value
        
        await self.wait_for_condition(
            context, condition, f"{description} == {expected_value}", timeout
        )
        
        return await value_getter()
    
    def create_event(self, context: TestContext, name: str) -> asyncio.Event:
        """
        Create named event within test context.
        
        Args:
            context: Test context
            name: Event name
            
        Returns:
            asyncio.Event: Created event
        """
        event = asyncio.Event()
        context.events[name] = event
        return event
    
    async def wait_for_event(
        self,
        context: TestContext,
        event_name: str,
        timeout: float = None
    ) -> None:
        """
        Wait for named event with timeout.
        
        Args:
            context: Test context
            event_name: Name of event to wait for
            timeout: Timeout in seconds
        """
        if event_name not in context.events:
            raise ValueError(f"Event {event_name} not found in context")
        
        timeout = timeout or context.timeouts.get("event", self.default_timeout)
        
        try:
            await asyncio.wait_for(context.events[event_name].wait(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Event {event_name} not set within {timeout}s")
```

### Phase 2: Enhanced Test Fixtures

**2.1 Async Test Fixtures**
```python
# tests/conftest.py (enhancements)
import pytest
import asyncio
from tests.utils.test_supervisor import TestSupervisor

@pytest.fixture
async def test_supervisor():
    """Provide TestSupervisor for async test coordination."""
    supervisor = TestSupervisor(default_timeout=5.0)
    yield supervisor
    # Cleanup handled by supervisor context managers

@pytest.fixture
async def agent_factory(test_supervisor):
    """Factory for creating agents with automatic cleanup."""
    created_agents = []
    
    async def _create_agent(config, context=None):
        if context:
            agent = await test_supervisor.create_agent(context, config)
        else:
            agent = Agent(config)
            created_agents.append(agent)
        return agent
    
    yield _create_agent
    
    # Cleanup agents created outside of contexts
    for agent in created_agents:
        try:
            if agent._running:
                await agent.stop()
        except Exception:
            pass

@pytest.fixture
async def isolated_test_context(test_supervisor, request):
    """Provide isolated test context with automatic cleanup."""
    test_name = request.node.name
    async with test_supervisor.test_context(test_name) as context:
        yield context
```

### Phase 3: Integration Test Modernization

**3.1 Updated Integration Test Patterns**
```python
# tests/integration/test_agent_coordination.py (example)
import pytest
from tests.utils.test_supervisor import TestSupervisor
from openmas.core.config import AgentConfig
from openmas.core.simf import SIMFMessage

class TestAgentCoordination:
    """Test agent coordination using TestSupervisor patterns."""
    
    async def test_agent_message_exchange(self, test_supervisor):
        """Test message exchange between agents using event coordination."""
        async with test_supervisor.test_context("agent_message_exchange") as context:
            # Create agents
            sender_config = AgentConfig(agent_id="sender", name="Sender Agent")
            receiver_config = AgentConfig(agent_id="receiver", name="Receiver Agent")
            
            sender = await test_supervisor.create_agent(context, sender_config, "sender")
            receiver = await test_supervisor.create_agent(context, receiver_config, "receiver")
            
            # Start agents with timeout
            await test_supervisor.start_agent(context, sender)
            await test_supervisor.start_agent(context, receiver)
            
            # Create event for coordination
            message_received_event = test_supervisor.create_event(context, "message_received")
            
            # Set up message tracking
            received_messages = []
            
            async def track_messages(message):
                received_messages.append(message)
                message_received_event.set()
                return SIMFMessage(
                    message_type="acknowledgment",
                    payload={"status": "received"},
                    sender_id=receiver.agent_id
                )
            
            receiver.add_message_callback(track_messages)
            
            # Send message
            test_message = SIMFMessage(
                message_type="test_message",
                payload={"content": "Hello from sender"},
                sender_id=sender.agent_id,
                target_id=receiver.agent_id
            )
            
            await sender.send_message(test_message)
            
            # Wait for message to be received (event-based, not time-based)
            await test_supervisor.wait_for_event(context, "message_received", timeout=3.0)
            
            # Verify message was received
            assert len(received_messages) == 1
            assert received_messages[0].payload["content"] == "Hello from sender"
    
    async def test_agent_capability_discovery(self, test_supervisor):
        """Test agent capability discovery with condition waiting."""
        async with test_supervisor.test_context("capability_discovery") as context:
            # Create agent with capabilities
            config = AgentConfig(
                agent_id="capable_agent",
                name="Capable Agent",
                capabilities=["data_analysis", "report_generation"]
            )
            
            agent = await test_supervisor.create_agent(context, config)
            await test_supervisor.start_agent(context, agent)
            
            # Wait for agent to be ready (condition-based)
            async def agent_ready():
                return agent._running and len(agent.capabilities) > 0
            
            await test_supervisor.wait_for_condition(
                context,
                agent_ready,
                "agent ready with capabilities",
                timeout=2.0
            )
            
            # Verify capabilities
            capabilities = await test_supervisor.wait_for_value(
                context,
                lambda: agent.get_capabilities(),
                {"data_analysis", "report_generation"},
                "agent capabilities loaded"
            )
            
            assert "data_analysis" in capabilities
            assert "report_generation" in capabilities
```

## Quality Enforcement (Phase 2.5)

### Zero Regression Policy
```bash
# MANDATORY: Establish baseline before changes
echo "=== ESTABLISHING BASELINE - TESTS MUST PASS BEFORE CHANGES ==="
python -m pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
    echo "❌ BASELINE FAILED: Tests are broken. Fix before proceeding."
    exit 1
fi
echo "✅ BASELINE ESTABLISHED: All tests passing before changes"

# Test that test suite completes without hanging
echo "=== TESTING SUITE COMPLETION ==="
timeout 30s python -m pytest tests/integration/ -v
if [ $? -eq 124 ]; then
    echo "⚠️ CONFIRMED: Test suite hangs (expected before fix)"
else
    echo "✅ Test suite completed within timeout"
fi

# MANDATORY: Zero regression validation after changes
echo "=== ZERO REGRESSION VALIDATION - TESTS MUST COMPLETE ==="
timeout 60s python -m pytest tests/ -x --tb=short
if [ $? -eq 124 ]; then
    echo "❌ REGRESSION: Test suite still hangs. Fix incomplete."
    exit 1
elif [ $? -ne 0 ]; then
    echo "❌ REGRESSION: Tests failing. REVERT IMMEDIATELY."
    exit 1
fi
echo "✅ ZERO REGRESSION CONFIRMED: All tests pass and complete"
```

### Quality Gate Requirements
1. **#1 REQUIREMENT**: ZERO REGRESSION POLICY - All tests MUST pass AND complete without hanging
2. Test suite must complete within reasonable time (< 60 seconds for full suite)
3. TestSupervisor must provide proper resource cleanup
4. Event-based coordination must be more reliable than time-based waits
5. Timeout management must prevent indefinite hangs
6. All async patterns must follow proper exception handling

## Success Criteria

### Functional Requirements
- [ ] TestSupervisor class implemented with full lifecycle management
- [ ] Test suite runs to completion without hanging
- [ ] Event-based test coordination working reliably
- [ ] Proper async resource cleanup in all tests
- [ ] Timeout management prevents indefinite waits

### Technical Requirements
- [ ] Integration tests modernized to use TestSupervisor patterns
- [ ] Async test fixtures with automatic cleanup
- [ ] Condition waiting utilities for reliable test coordination
- [ ] Resource isolation between tests

### Quality Requirements
- [ ] All tests continue to pass (zero regression)
- [ ] Test suite completes within 60 seconds
- [ ] MyPy strict mode compliance for all new code
- [ ] Comprehensive error handling and logging

## Deliverables

1. **TestSupervisor Implementation**:
   - `tests/utils/test_supervisor.py`

2. **Enhanced Test Fixtures**:
   - `tests/conftest.py` (enhanced)

3. **Modernized Integration Tests**:
   - `tests/integration/test_agent_coordination.py` (example)
   - Updated existing integration tests

4. **Documentation**:
   - TestSupervisor usage guide
   - Async testing patterns documentation

## Notes

- Implements sophisticated async testing patterns from setup documentation
- Resolves test suite hanging issues that block development
- Enables reliable testing of complex agent interactions
- Foundation for comprehensive testing framework (Phase 3)
- Critical for validating architectural remediation work

## Anti-Hallucination Safeguards

- TestSupervisor uses existing Agent lifecycle methods
- Event-based coordination builds on asyncio primitives
- Resource cleanup follows established async patterns
- Integration tests use real Agent and protocol adapter implementations
- No assumptions about non-existent testing infrastructure
