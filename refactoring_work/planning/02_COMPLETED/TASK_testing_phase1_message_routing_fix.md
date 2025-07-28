# TASK: Testing Framework Phase 1 - Message Routing Fix

**Task ID**: TEST-001  
**Priority**: HIGH ✅ COMPLETED  
**Type**: Bug Fix  
**Estimated Effort**: 1-2 hours ✅ COMPLETED  
**Dependencies**: None  
**Status**: ARCHIVED - Successfully completed (immediate fix required)

## Task Overview

Fix the critical message routing issue causing 5/9 integration tests to fail with `len(mcp_adapter.sent_messages) == 0`. The root cause is that protocol adapters are not automatically registering message callbacks with agents, breaking the message processing loop. This is an immediate blocker for all architectural remediation work.

## Three-Input Task Creation Protocol Compliance

### Input 1: Design Documentation Analysis

**Primary Reference**: `/refactoring_work/planning/TESTING_FRAMEWORK_IMPLEMENTATION_GUIDANCE.md` (Phase 1)

**Design Specification**:
- Protocol adapters must automatically register callbacks with agents during startup
- Message processing should not depend on manual callback registration
- Integration tests should validate end-to-end message routing without mocking

**Additional Reference**: `/refactoring_work/setup/testing_setup/04_async_integration_testing.md` - Async agent lifecycle management patterns

### Input 2: User Business/Personal Needs

**Core Business Value**:
- **Unblock Development**: Integration tests must pass to enable architectural remediation work
- **Rapid Feedback**: Developers need reliable test suite for Body-Brain separation implementation
- **Quality Assurance**: End-to-end message routing validation for PowerBI/SQL/analytics agents
- **Development Velocity**: Remove testing friction that slows down daily development

**Current Pain Points**:
- 5/9 integration tests failing, blocking progress on ARCH-001, ARCH-002, ARCH-003
- Message routing broken between agents and protocol adapters
- Cannot validate architectural changes without working integration tests
- Developer confidence undermined by unreliable test suite

### Input 3: Current Codebase Implementation Status

**Current Problem** (`src/openmas/agent/base_agent.py`):
```python
async def start(self) -> None:
    """Start the agent and its components."""
    if self._running:
        self.logger.warning("Agent is already running")
        return

    self.logger.info(f"Starting agent {self.agent_id}")
    
    # MISSING: Protocol adapter callback registration
    # Protocol adapters exist but don't receive messages
    
    self._running = True
    # Start message processing loop but no callbacks registered
```

**Failing Integration Tests**:
- `tests/integration/test_mcp_integration.py` - 5/9 tests failing
- Error pattern: `assert len(mcp_adapter.sent_messages) == 0` (should be > 0)
- Root cause: Messages sent to agents but never reach protocol adapters

**Existing Infrastructure to Leverage**:
- ✅ Protocol adapter interface (`IProtocolAdapter`) with callback support
- ✅ Agent message processing loop in `base_agent.py`
- ✅ MCP adapter implementation with message tracking
- ✅ Integration test structure and patterns
- ✅ 49/49 unit tests passing (isolated components work)

**Missing Components to Fix**:
- ⚠️ Automatic callback registration in `Agent.start()`
- ⚠️ Message routing from agent to protocol adapters
- ⚠️ Proper integration between agent lifecycle and adapter callbacks

## Implementation Specification

### Phase 1: Agent Startup Enhancement

**1.1 Fix Agent.start() Method**
```python
# src/openmas/agent/base_agent.py
async def start(self) -> None:
    """Start the agent and its components."""
    if self._running:
        self.logger.warning("Agent is already running")
        return

    self.logger.info(f"Starting agent {self.agent_id}")
    
    # CRITICAL FIX: Register protocol adapter callbacks
    for protocol_name, adapter in self.protocol_adapters.items():
        if hasattr(adapter, 'set_message_callback'):
            # Register agent's handle_message as callback
            adapter.set_message_callback(self.handle_message)
            self.logger.debug(f"Registered message callback for {protocol_name} adapter")
    
    # Initialize message queue if not already done
    if self.message_queue is None:
        self.message_queue = asyncio.Queue()
    
    # Start message processing task
    if not any(task for task in self._tasks if not task.done()):
        message_task = asyncio.create_task(self._process_message_queue())
        self._tasks.append(message_task)
        self.logger.debug("Started message processing task")
    
    self._running = True
    self.logger.info(f"Agent {self.agent_id} started successfully")

async def _process_message_queue(self) -> None:
    """Process messages from the queue."""
    while self._running:
        try:
            # Wait for message with timeout to allow clean shutdown
            message = await asyncio.wait_for(
                self.message_queue.get(), 
                timeout=0.1
            )
            
            # Process message through handle_message
            response = await self.handle_message(message)
            
            # Send response through appropriate protocol adapter
            if response:
                await self._send_response(response)
                
        except asyncio.TimeoutError:
            # Normal timeout, continue loop
            continue
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

async def _send_response(self, response: SIMFMessage) -> None:
    """Send response through appropriate protocol adapter."""
    # Determine which protocol adapter to use based on message context
    # For now, use first available adapter (can be enhanced later)
    if self.protocol_adapters:
        adapter = next(iter(self.protocol_adapters.values()))
        if hasattr(adapter, 'send_message'):
            await adapter.send_message(response)
```

### Phase 2: Protocol Adapter Interface Validation

**2.1 Ensure MCP Adapter Callback Support**
```python
# src/openmas/protocols/mcp/adapter.py (verify/enhance)
class MCPAdapter(IProtocolAdapter):
    def __init__(self):
        super().__init__()
        self.message_callback: Optional[Callable[[SIMFMessage], Awaitable[SIMFMessage]]] = None
        self.sent_messages: List[Any] = []  # For testing
    
    def set_message_callback(self, callback: Callable[[SIMFMessage], Awaitable[SIMFMessage]]) -> None:
        """Set callback for handling incoming messages."""
        self.message_callback = callback
    
    async def send_message(self, message: SIMFMessage) -> None:
        """Send message through MCP protocol."""
        # Convert SIMF to MCP format and send
        mcp_message = self._simf_to_mcp(message)
        self.sent_messages.append(mcp_message)  # Track for testing
        
        # Actual MCP sending logic here
        # ...
    
    async def receive_message(self, mcp_message: Any) -> None:
        """Receive message from MCP protocol."""
        if self.message_callback:
            # Convert MCP to SIMF format
            simf_message = self._mcp_to_simf(mcp_message)
            
            # Send to agent for processing
            response = await self.message_callback(simf_message)
            
            # Send response back if needed
            if response:
                await self.send_message(response)
```

### Phase 3: Integration Test Validation

**3.1 Verify Test Expectations**
```python
# tests/integration/test_mcp_integration.py (example fix)
async def test_agent_mcp_message_routing():
    """Test that messages route correctly between agent and MCP adapter."""
    # Create agent with MCP adapter
    mcp_adapter = MCPAdapter()
    agent = Agent(
        config=AgentConfig(agent_id="test_agent", name="Test Agent"),
        protocol_adapters={"mcp": mcp_adapter}
    )
    
    # Start agent (this should register callbacks)
    await agent.start()
    
    # Send message to agent
    test_message = SIMFMessage(
        message_type="test_request",
        payload={"test": "data"},
        sender_id="test_sender"
    )
    
    # Process message through agent
    response = await agent.handle_message(test_message)
    
    # Verify message was sent through MCP adapter
    assert len(mcp_adapter.sent_messages) > 0, "Message should have been sent through MCP adapter"
    assert response is not None, "Agent should have generated response"
    
    # Clean up
    await agent.stop()
```

## Quality Enforcement (Phase 2.5)

### Zero Regression Policy
```bash
# MANDATORY: Establish baseline before changes
echo "=== ESTABLISHING BASELINE - TESTS MUST PASS BEFORE CHANGES ==="
python -m pytest tests/unit/ -x --tb=short
if [ $? -ne 0 ]; then
    echo "❌ BASELINE FAILED: Unit tests are broken. Fix before proceeding."
    exit 1
fi
echo "✅ BASELINE ESTABLISHED: Unit tests passing before changes"

# Run integration tests to confirm current failure state
echo "=== CONFIRMING INTEGRATION TEST FAILURES ==="
python -m pytest tests/integration/ -v --tb=short
echo "Expected: 5/9 integration tests should be failing"

# MANDATORY: Zero regression validation after changes
echo "=== ZERO REGRESSION VALIDATION - TESTS MUST PASS AFTER CHANGES ==="
python -m pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
    echo "❌ REGRESSION DETECTED: Tests broken by changes. REVERT IMMEDIATELY."
    exit 1
fi
echo "✅ ZERO REGRESSION CONFIRMED: All tests passing after changes"
```

### Ruff and MyPy Validation
```bash
# Ruff validation
ruff check src/openmas/agent/base_agent.py --config pyproject.toml
ruff check src/openmas/protocols/mcp/adapter.py --config pyproject.toml

# MyPy validation
mypy src/openmas/agent/base_agent.py --strict
mypy src/openmas/protocols/mcp/adapter.py --strict
```

### Quality Gate Requirements
1. **#1 REQUIREMENT**: ZERO REGRESSION POLICY - All unit tests MUST pass before AND after changes
2. All 9/9 integration tests must pass after implementation
3. Message routing must work end-to-end without manual callback registration
4. Protocol adapter callback interface must be properly typed
5. Agent startup must be robust with proper error handling
6. Message processing loop must handle timeouts and exceptions gracefully

## Testing Strategy

### Validation Tests
```python
# tests/integration/test_message_routing_fix.py
class TestMessageRoutingFix:
    """Validate that message routing fix works correctly."""
    
    async def test_automatic_callback_registration(self):
        """Test that protocol adapters automatically register callbacks on agent start."""
        mcp_adapter = MCPAdapter()
        agent = Agent(
            config=AgentConfig(agent_id="test", name="Test"),
            protocol_adapters={"mcp": mcp_adapter}
        )
        
        # Before start, no callback should be registered
        assert mcp_adapter.message_callback is None
        
        # After start, callback should be registered
        await agent.start()
        assert mcp_adapter.message_callback is not None
        
        await agent.stop()
    
    async def test_end_to_end_message_flow(self):
        """Test complete message flow from adapter to agent and back."""
        mcp_adapter = MCPAdapter()
        agent = Agent(
            config=AgentConfig(agent_id="test", name="Test"),
            protocol_adapters={"mcp": mcp_adapter}
        )
        
        await agent.start()
        
        # Simulate incoming MCP message
        mcp_message = {"type": "test", "content": "hello"}
        await mcp_adapter.receive_message(mcp_message)
        
        # Verify message was processed and response sent
        assert len(mcp_adapter.sent_messages) > 0
        
        await agent.stop()
```

## Success Criteria

### Functional Requirements
- [ ] All 9/9 integration tests pass
- [ ] Protocol adapters automatically register callbacks during `Agent.start()`
- [ ] Message routing works end-to-end without manual setup
- [ ] Agent startup is robust with proper error handling
- [ ] Message processing loop handles timeouts and exceptions

### Technical Requirements
- [ ] No changes to public Agent API
- [ ] Protocol adapter interface remains stable
- [ ] Message callback registration is automatic and transparent
- [ ] Proper async patterns used throughout

### Quality Requirements
- [ ] All 49/49 unit tests continue to pass (zero regression)
- [ ] MyPy strict mode compliance for all modified code
- [ ] Ruff linting compliance (line-length=120, ignore=E203)
- [ ] Comprehensive error handling and logging

## Deliverables

1. **Enhanced Agent Class**:
   - `src/openmas/agent/base_agent.py` (enhanced `start()` method)

2. **Validated Protocol Adapter**:
   - `src/openmas/protocols/mcp/adapter.py` (callback interface validation)

3. **Integration Test Validation**:
   - `tests/integration/test_message_routing_fix.py`

4. **Documentation**:
   - Update agent startup documentation
   - Document message routing patterns

## Notes

- This is a **critical blocker** for all architectural remediation work
- Fix is **simple and well-understood** - just missing callback registration
- Implementation follows existing patterns and interfaces
- **No breaking changes** to public APIs
- Enables immediate progress on ARCH-001, ARCH-002, ARCH-003 tasks

## Anti-Hallucination Safeguards

- Fix uses existing `IProtocolAdapter` interface without changes
- Agent startup enhancement follows existing lifecycle patterns
- Message processing uses established `SIMFMessage` format
- Integration tests validate real message routing without mocking
- No assumptions about non-existent infrastructure or capabilities
