# TASK: Testing Framework Phase 3 - Comprehensive Testing Framework

**Task ID**: TEST-003  
**Priority**: MEDIUM  
**Type**: Testing Infrastructure  
**Estimated Effort**: 1-2 weeks  
**Dependencies**: TEST-001 (Message Routing), TEST-002 (TestSupervisor)

## Task Overview

Implement the comprehensive testing framework as documented in the setup guidance to achieve ≥85% test coverage across all design components. This includes complete test directory structure, protocol-specific testing patterns, advanced async utilities, CI/CD integration, and comprehensive coverage for all OpenMAS design components.

## Three-Input Task Creation Protocol Compliance

### Input 1: Design Documentation Analysis

**Primary References**:
- `/refactoring_work/setup/testing_setup/01_testing_framework.md` - Complete test directory structure
- `/refactoring_work/setup/testing_setup/02_protocol_testing.md` - Protocol-specific testing patterns
- `/refactoring_work/setup/testing_setup/03_library_adapter_testing.md` - Library integration testing
- `/refactoring_work/setup/testing_setup/05_docker_testing.md` - Containerized testing
- `/refactoring_work/setup/testing_setup/06_tox_configuration.md` - Multi-environment testing

**Design Specification**: Comprehensive testing framework supporting all OpenMAS design components with sophisticated async patterns, protocol testing, and CI/CD integration.

### Input 2: User Business/Personal Needs

**Core Business Value**:
- **Comprehensive Coverage**: Validate all design components for PowerBI/SQL/analytics agent development
- **Quality Assurance**: Prevent 0.2.0-style issues where "tests pass but nothing works with real libraries"
- **Development Confidence**: Reliable test suite that validates architectural changes
- **Rapid Development**: Fast feedback loop for complex agent interactions and protocol integrations

**Business Impact**:
- Enable confident development of specialized business workflow agents
- Validate architectural remediation work (Body-Brain, Facade, Strategy patterns)
- Support multi-protocol agent development for enterprise integrations
- Establish foundation for continuous integration and deployment

### Input 3: Current Codebase Implementation Status

**Current State After TEST-001 & TEST-002**:
- ✅ Integration tests passing (9/9)
- ✅ TestSupervisor implemented for async coordination
- ✅ Test suite completes without hanging
- ✅ Basic test directory structure exists

**Existing Infrastructure to Leverage**:
- ✅ TestSupervisor for async lifecycle management
- ✅ Working message routing and protocol adapters
- ✅ pytest-asyncio configuration
- ✅ Basic test utilities and fixtures
- ✅ Anti-hallucination testing patterns (real MCP integration)

**Missing Components to Build**:
- ⚠️ Complete test directory structure for all design components
- ⚠️ Protocol-specific testing patterns and utilities
- ⚠️ Advanced async testing utilities (network mocking, condition waiting)
- ⚠️ Performance testing and benchmarking
- ⚠️ CI/CD integration with matrix testing
- ⚠️ Comprehensive coverage reporting

## Implementation Specification

### Phase 1: Complete Test Directory Structure

**1.1 Implement Full Test Directory Structure**
```bash
# Based on /refactoring_work/setup/testing_setup/01_testing_framework.md
tests/
├── unit/                           # Unit tests for individual components
│   ├── agent/                      # Agent framework tests
│   │   ├── test_base_agent.py     # ✅ Exists
│   │   ├── test_agent_factory.py  # ✅ Exists
│   │   ├── test_reasoning/         # New: Reasoning engine tests
│   │   └── test_communication/     # New: Communication layer tests
│   ├── core/                       # Core framework tests
│   │   ├── test_simf.py           # ✅ Exists
│   │   ├── test_config.py         # ✅ Exists
│   │   └── test_lifecycle.py      # New: Lifecycle management
│   ├── protocols/                  # Protocol implementation tests
│   │   ├── test_mcp/              # ✅ Partially exists
│   │   ├── test_a2a/              # New: A2A protocol tests
│   │   ├── test_http/             # New: HTTP protocol tests
│   │   └── test_mqtt/             # New: MQTT protocol tests
│   ├── reasoning/                  # Reasoning system tests
│   │   ├── test_kr_r/             # New: KR&R system tests
│   │   ├── test_bdi/              # New: BDI reasoning tests
│   │   └── test_llm_reasoning/    # New: LLM reasoning tests
│   ├── knowledge/                  # Knowledge management tests
│   │   ├── test_knowledge_base.py # New: Knowledge base tests
│   │   └── test_ontology.py       # New: Ontology tests
│   ├── asset_management/          # Asset management tests
│   │   └── test_asset_registry.py # New: Asset registry tests
│   ├── cli/                       # CLI tools tests
│   │   └── test_cli_commands.py   # New: CLI command tests
│   └── observability/             # Observability tests
│       ├── test_metrics.py        # New: Metrics collection
│       └── test_logging.py        # New: Logging system
├── integration/                    # Integration tests
│   ├── test_mcp_integration.py    # ✅ Exists, enhanced
│   ├── test_multi_protocol.py     # New: Multi-protocol scenarios
│   ├── test_agent_coordination.py # ✅ From TEST-002
│   ├── test_reasoning_integration.py # New: Reasoning system integration
│   └── test_end_to_end.py         # New: Complete workflow tests
├── performance/                    # Performance and load tests
│   ├── test_agent_performance.py  # New: Agent performance tests
│   ├── test_protocol_performance.py # New: Protocol performance
│   └── test_load_scenarios.py     # New: Load testing
├── e2e/                           # End-to-end tests
│   ├── test_powerbi_workflow.py   # New: PowerBI agent workflow
│   ├── test_sql_workflow.py       # New: SQL Server agent workflow
│   └── test_analytics_workflow.py # New: Analytics agent workflow
└── utils/                         # Test utilities
    ├── test_supervisor.py         # ✅ From TEST-002
    ├── async_testing.py           # New: Advanced async utilities
    ├── protocol_mocks.py          # New: Protocol mocking utilities
    └── performance_utils.py       # New: Performance testing utilities
```

### Phase 2: Protocol-Specific Testing Patterns

**2.1 Advanced Protocol Testing Utilities**
```python
# tests/utils/protocol_mocks.py
import asyncio
from typing import Any, Dict, List, Callable, Optional
from unittest.mock import AsyncMock, MagicMock
from openmas.protocols.mcp.adapter import MCPAdapter
from openmas.core.simf import SIMFMessage

class MockProtocolServer:
    """Mock protocol server for testing protocol adapters."""
    
    def __init__(self, protocol_type: str):
        self.protocol_type = protocol_type
        self.received_messages: List[Any] = []
        self.response_queue: asyncio.Queue = asyncio.Queue()
        self.message_handlers: Dict[str, Callable] = {}
        self.running = False
    
    async def start(self) -> None:
        """Start mock protocol server."""
        self.running = True
    
    async def stop(self) -> None:
        """Stop mock protocol server."""
        self.running = False
    
    async def send_message(self, message: Any) -> None:
        """Send message to connected adapter."""
        self.received_messages.append(message)
        
        # Trigger response if handler exists
        message_type = getattr(message, 'type', 'unknown')
        if message_type in self.message_handlers:
            response = await self.message_handlers[message_type](message)
            if response:
                await self.response_queue.put(response)
    
    def add_message_handler(self, message_type: str, handler: Callable) -> None:
        """Add handler for specific message type."""
        self.message_handlers[message_type] = handler
    
    async def get_next_response(self, timeout: float = 1.0) -> Any:
        """Get next response from queue."""
        return await asyncio.wait_for(self.response_queue.get(), timeout=timeout)

class ProtocolTestHarness:
    """Test harness for protocol adapter testing."""
    
    def __init__(self, adapter_class, server_class=None):
        self.adapter_class = adapter_class
        self.server_class = server_class or MockProtocolServer
        self.adapter: Optional[Any] = None
        self.server: Optional[MockProtocolServer] = None
    
    async def setup(self) -> None:
        """Set up adapter and mock server."""
        self.adapter = self.adapter_class()
        self.server = self.server_class(self.adapter_class.__name__)
        
        # Connect adapter to server
        if hasattr(self.adapter, 'connect'):
            await self.adapter.connect(self.server)
        
        await self.server.start()
    
    async def teardown(self) -> None:
        """Clean up adapter and server."""
        if self.server:
            await self.server.stop()
        
        if self.adapter and hasattr(self.adapter, 'disconnect'):
            await self.adapter.disconnect()
    
    async def send_to_adapter(self, message: SIMFMessage) -> Any:
        """Send SIMF message through adapter."""
        return await self.adapter.send_message(message)
    
    async def send_from_server(self, protocol_message: Any) -> None:
        """Send protocol-specific message from server."""
        await self.server.send_message(protocol_message)
    
    def get_received_messages(self) -> List[Any]:
        """Get messages received by server."""
        return self.server.received_messages.copy()
```

**2.2 Protocol-Specific Test Patterns**
```python
# tests/protocols/test_mcp/test_mcp_adapter_comprehensive.py
import pytest
from tests.utils.protocol_mocks import ProtocolTestHarness
from tests.utils.test_supervisor import TestSupervisor
from openmas.protocols.mcp.adapter import MCPAdapter
from openmas.core.simf import SIMFMessage

class TestMCPAdapterComprehensive:
    """Comprehensive MCP adapter testing."""
    
    @pytest.fixture
    async def mcp_harness(self):
        """MCP protocol test harness."""
        harness = ProtocolTestHarness(MCPAdapter)
        await harness.setup()
        yield harness
        await harness.teardown()
    
    async def test_mcp_message_translation(self, mcp_harness):
        """Test SIMF to MCP message translation."""
        simf_message = SIMFMessage(
            message_type="capability_request",
            payload={"capability": "data_analysis"},
            sender_id="test_agent"
        )
        
        # Send through adapter
        await mcp_harness.send_to_adapter(simf_message)
        
        # Verify MCP message was generated
        received = mcp_harness.get_received_messages()
        assert len(received) == 1
        
        mcp_message = received[0]
        assert mcp_message['method'] == 'capability_request'
        assert mcp_message['params']['capability'] == 'data_analysis'
    
    async def test_mcp_error_handling(self, mcp_harness):
        """Test MCP error response handling."""
        # Set up error response handler
        async def error_handler(message):
            return {
                'error': {'code': -1, 'message': 'Test error'},
                'id': message.get('id')
            }
        
        mcp_harness.server.add_message_handler('test_request', error_handler)
        
        # Send message that will trigger error
        simf_message = SIMFMessage(
            message_type="test_request",
            payload={"test": "data"},
            sender_id="test_agent"
        )
        
        # Verify error handling
        with pytest.raises(Exception) as exc_info:
            await mcp_harness.send_to_adapter(simf_message)
        
        assert "Test error" in str(exc_info.value)
```

### Phase 3: Advanced Async Testing Utilities

**3.1 Network and Resource Mocking**
```python
# tests/utils/async_testing.py
import asyncio
import time
from typing import Any, Callable, Awaitable, Optional, Dict
from unittest.mock import AsyncMock, patch
from contextlib import asynccontextmanager

class AsyncConditionWaiter:
    """Advanced condition waiting with timeout and interval control."""
    
    def __init__(self, default_timeout: float = 5.0, default_interval: float = 0.1):
        self.default_timeout = default_timeout
        self.default_interval = default_interval
    
    async def wait_for_condition(
        self,
        condition: Callable[[], Awaitable[bool]],
        timeout: Optional[float] = None,
        interval: Optional[float] = None,
        description: str = "condition"
    ) -> None:
        """Wait for async condition to become true."""
        timeout = timeout or self.default_timeout
        interval = interval or self.default_interval
        
        start_time = time.time()
        
        while True:
            if await condition():
                return
            
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(f"Condition '{description}' not met within {timeout}s")
            
            await asyncio.sleep(interval)
    
    async def wait_for_value(
        self,
        getter: Callable[[], Awaitable[Any]],
        expected: Any,
        timeout: Optional[float] = None,
        description: str = "value"
    ) -> Any:
        """Wait for getter to return expected value."""
        async def condition():
            value = await getter()
            return value == expected
        
        await self.wait_for_condition(
            condition, timeout, description=f"{description} == {expected}"
        )
        
        return await getter()
    
    async def wait_for_count(
        self,
        counter: Callable[[], Awaitable[int]],
        expected_count: int,
        timeout: Optional[float] = None,
        description: str = "count"
    ) -> int:
        """Wait for counter to reach expected count."""
        return await self.wait_for_value(
            counter, expected_count, timeout, f"{description} count"
        )

class NetworkMockManager:
    """Manager for network-related mocking in tests."""
    
    def __init__(self):
        self.active_mocks: Dict[str, Any] = {}
    
    @asynccontextmanager
    async def mock_http_client(self, responses: Dict[str, Any]):
        """Mock HTTP client responses."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get = AsyncMock()
            mock_session.return_value.__aenter__.return_value.post = AsyncMock()
            
            # Configure responses
            for url, response in responses.items():
                mock_response = AsyncMock()
                mock_response.json.return_value = response
                mock_response.status = 200
                
                mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            yield mock_session
    
    @asynccontextmanager
    async def mock_websocket_connection(self, message_queue: asyncio.Queue):
        """Mock WebSocket connection."""
        with patch('websockets.connect') as mock_connect:
            mock_ws = AsyncMock()
            mock_ws.send = AsyncMock()
            mock_ws.recv = AsyncMock(side_effect=lambda: message_queue.get())
            
            mock_connect.return_value.__aenter__.return_value = mock_ws
            
            yield mock_ws

class PerformanceProfiler:
    """Performance profiling utilities for tests."""
    
    def __init__(self):
        self.measurements: Dict[str, List[float]] = {}
    
    @asynccontextmanager
    async def measure_time(self, operation_name: str):
        """Measure execution time of async operation."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start_time
            if operation_name not in self.measurements:
                self.measurements[operation_name] = []
            self.measurements[operation_name].append(elapsed)
    
    def get_average_time(self, operation_name: str) -> float:
        """Get average execution time for operation."""
        if operation_name not in self.measurements:
            return 0.0
        
        times = self.measurements[operation_name]
        return sum(times) / len(times)
    
    def assert_performance(
        self,
        operation_name: str,
        max_time: float,
        percentile: float = 95.0
    ) -> None:
        """Assert that operation meets performance requirements."""
        if operation_name not in self.measurements:
            raise AssertionError(f"No measurements for {operation_name}")
        
        times = sorted(self.measurements[operation_name])
        index = int(len(times) * percentile / 100.0)
        percentile_time = times[min(index, len(times) - 1)]
        
        assert percentile_time <= max_time, (
            f"{operation_name} {percentile}th percentile time {percentile_time:.3f}s "
            f"exceeds limit {max_time:.3f}s"
        )
```

### Phase 4: CI/CD Integration

**4.1 GitHub Actions Workflow**
```yaml
# .github/workflows/comprehensive-testing.yml
name: Comprehensive Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run unit tests
      run: |
        python -m pytest tests/unit/ -v --cov=src/openmas --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run integration tests
      run: |
        python -m pytest tests/integration/ -v --timeout=60
    
    - name: Run performance tests
      run: |
        python -m pytest tests/performance/ -v --benchmark-only

  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run end-to-end tests
      run: |
        python -m pytest tests/e2e/ -v --timeout=120

  coverage-report:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, e2e-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run full test suite with coverage
      run: |
        python -m pytest tests/ --cov=src/openmas --cov-report=html --cov-report=term --cov-fail-under=85
    
    - name: Upload coverage report
      uses: actions/upload-artifact@v3
      with:
        name: coverage-report
        path: htmlcov/
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

# MANDATORY: Coverage validation
echo "=== COVERAGE VALIDATION ==="
python -m pytest tests/ --cov=src/openmas --cov-report=term --cov-fail-under=85
if [ $? -ne 0 ]; then
    echo "❌ COVERAGE FAILED: Coverage below 85% threshold."
    exit 1
fi
echo "✅ COVERAGE VALIDATED: ≥85% coverage achieved"

# MANDATORY: Zero regression validation after changes
echo "=== ZERO REGRESSION VALIDATION ==="
python -m pytest tests/ -x --tb=short --timeout=120
if [ $? -ne 0 ]; then
    echo "❌ REGRESSION DETECTED: Tests failing or hanging. REVERT IMMEDIATELY."
    exit 1
fi
echo "✅ ZERO REGRESSION CONFIRMED: All tests pass and complete"
```

### Quality Gate Requirements
1. **#1 REQUIREMENT**: ZERO REGRESSION POLICY - All tests MUST pass and complete
2. Test coverage must be ≥85% across all components
3. All design components must have corresponding test coverage
4. Performance tests must validate acceptable response times
5. CI/CD pipeline must pass all stages
6. End-to-end tests must validate real workflow scenarios

## Success Criteria

### Functional Requirements
- [ ] Complete test directory structure implemented for all design components
- [ ] Protocol-specific testing patterns working for MCP, A2A, HTTP, MQTT
- [ ] Advanced async testing utilities providing reliable coordination
- [ ] Performance testing and benchmarking established
- [ ] CI/CD pipeline with matrix testing operational

### Coverage Requirements
- [ ] ≥85% test coverage across entire codebase
- [ ] All design components have unit tests
- [ ] Integration tests cover multi-protocol scenarios
- [ ] End-to-end tests validate PowerBI/SQL/analytics workflows
- [ ] Performance tests establish baseline metrics

### Quality Requirements
- [ ] All tests continue to pass (zero regression)
- [ ] Test suite completes within 120 seconds
- [ ] CI/CD pipeline passes all stages
- [ ] Coverage reporting integrated with development workflow

## Deliverables

1. **Complete Test Structure**:
   - Full test directory implementation
   - Test files for all design components

2. **Advanced Testing Utilities**:
   - `tests/utils/async_testing.py`
   - `tests/utils/protocol_mocks.py`
   - `tests/utils/performance_utils.py`

3. **CI/CD Integration**:
   - `.github/workflows/comprehensive-testing.yml`
   - Coverage reporting and quality gates

4. **Documentation**:
   - Comprehensive testing guide
   - Protocol testing patterns
   - Performance testing guidelines

## Notes

- Implements complete testing framework from setup documentation
- Achieves ≥85% coverage across all design components
- Establishes foundation for confident architectural development
- Enables validation of specialized business workflow agents
- Prevents 0.2.0-style issues through comprehensive real-world testing

## Anti-Hallucination Safeguards

- Test structure follows documented setup guidance exactly
- Protocol testing uses real adapter implementations
- Performance testing measures actual execution times
- CI/CD integration uses standard GitHub Actions patterns
- No assumptions about non-existent testing infrastructure
