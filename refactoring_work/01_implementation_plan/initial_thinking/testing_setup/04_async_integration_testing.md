# Asynchronous Integration Testing for OpenMAS 0.3.0

## Overview

This document outlines the strategy for implementing and running automated integration tests for asynchronous multi-agent systems in OpenMAS 0.3.0. The approach addresses the challenges of testing multiple agents with asynchronous communication while ensuring reliable, deterministic test results.

## Key Challenges

1. **Asynchronous Operation**: Agents run with async event loops that need coordination
2. **Test Orchestration**: Starting, monitoring, and stopping multiple agents
3. **Timing and Race Conditions**: Ensuring deterministic test outcomes
4. **Resource Management**: Proper cleanup of resources after tests
5. **CI/CD Integration**: Running tests in automated environments

## Solution Architecture

### 1. Test Supervisor Framework

We'll implement a Test Supervisor that manages agent lifecycles and test orchestration:

```python
from typing import Dict, Any, Callable, Optional, Awaitable, List
import asyncio
from openmas.agent import Agent

class TestSupervisor:
    """
    Test supervisor for managing multiple agents in integration tests.

    This class handles agent lifecycle, communication observation, and
    test orchestration for multi-agent tests.
    """

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.observers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self._running = False
        self._tasks: List[asyncio.Task] = []

    async def register_agent(self, agent_id: str, config: Dict[str, Any]) -> Agent:
        """
        Register an agent with the test supervisor.

        Args:
            agent_id: Unique identifier for the agent
            config: Agent configuration

        Returns:
            The created agent instance
        """
        agent = Agent(id=agent_id, config=config)
        self.agents[agent_id] = agent
        self.observers[agent_id] = []
        return agent

    def get_agent(self, agent_id: str) -> Agent:
        """Get an agent by ID."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not registered")
        return self.agents[agent_id]

    def observe_agent_messages(self, agent_id: str,
                              observer: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register an observer for agent messages.

        Args:
            agent_id: ID of the agent to observe
            observer: Callback function that will be called with each message
        """
        if agent_id not in self.observers:
            raise ValueError(f"Agent {agent_id} not registered")
        self.observers[agent_id].append(observer)

    async def _agent_message_handler(self, agent_id: str, message: Dict[str, Any]) -> None:
        """Internal message handler that notifies observers."""
        for observer in self.observers[agent_id]:
            observer(message)

    async def start(self) -> None:
        """Start all registered agents and set up message handling."""
        if self._running:
            return

        # Start each agent
        for agent_id, agent in self.agents.items():
            # Register message handler
            agent.register_message_handler(
                lambda msg, aid=agent_id: self._agent_message_handler(aid, msg)
            )
            # Start the agent
            self._tasks.append(asyncio.create_task(agent.start()))

        # Wait for all agents to start
        if self._tasks:
            await asyncio.gather(*self._tasks)

        self._running = True

    async def stop(self) -> None:
        """Stop all agents and clean up resources."""
        if not self._running:
            return

        # Cancel all running tasks
        for task in self._tasks:
            task.cancel()

        # Stop each agent
        stop_tasks = []
        for agent in self.agents.values():
            stop_tasks.append(asyncio.create_task(agent.stop()))

        # Wait for all agents to stop
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)

        self._tasks = []
        self._running = False
```

### 2. Async Test Fixtures with pytest-asyncio

Use pytest-asyncio to manage async tests with proper fixtures:

```python
# conftest.py
import pytest
import asyncio
from openmas.testing import TestSupervisor

@pytest.fixture
async def test_supervisor():
    """Create and manage a test supervisor for multi-agent tests."""
    supervisor = TestSupervisor()
    yield supervisor
    await supervisor.stop()

@pytest.fixture
async def agent_pair(test_supervisor):
    """Create a pair of test agents for common test scenarios."""
    # Register two agents with the supervisor
    await test_supervisor.register_agent("agent1", {
        "protocols": [{"type": "a2a-http", "options": {"base_url": "http://localhost:8001"}}]
    })

    await test_supervisor.register_agent("agent2", {
        "protocols": [{"type": "a2a-http", "options": {"base_url": "http://localhost:8002"}}]
    })

    # Start the supervisor (which starts all agents)
    await test_supervisor.start()

    # Return the supervisor with agents ready
    return test_supervisor
```

### 3. Integration Test Patterns

Implement standardized patterns for common test scenarios:

#### Request-Response Testing

```python
import pytest
import asyncio
from openmas.testing import wait_for_condition

@pytest.mark.asyncio
async def test_request_response(agent_pair):
    """Test basic request-response pattern between agents."""
    # Get agent references
    agent1 = agent_pair.get_agent("agent1")
    agent2 = agent_pair.get_agent("agent2")

    # Create a future to track response
    response_received = asyncio.Future()

    # Observer function that resolves the future when message arrives
    def message_observer(message):
        if not response_received.done():
            response_received.set_result(message)

    # Register the observer
    agent_pair.observe_agent_messages("agent2", message_observer)

    # Send message from agent1 to agent2
    await agent1.send_message("agent2", {"content": "Hello"})

    # Wait for the response with timeout
    response = await asyncio.wait_for(response_received, timeout=5.0)

    # Verify the response
    assert "content" in response
    assert response["content"] == "Hello"
```

#### Event-Based Testing

```python
@pytest.mark.asyncio
async def test_event_based_communication(agent_pair):
    """Test event-based communication between agents."""
    # Get agent references
    agent1 = agent_pair.get_agent("agent1")
    agent2 = agent_pair.get_agent("agent2")

    # Track received messages
    received_messages = []

    # Observer function that collects messages
    def message_collector(message):
        received_messages.append(message)

    # Register the observer
    agent_pair.observe_agent_messages("agent2", message_collector)

    # Send multiple messages
    await agent1.send_message("agent2", {"event": "start", "id": 1})
    await agent1.send_message("agent2", {"event": "update", "id": 2})
    await agent1.send_message("agent2", {"event": "complete", "id": 3})

    # Wait for all messages to be received
    await wait_for_condition(
        lambda: len(received_messages) >= 3,
        timeout=5.0,
        check_interval=0.1
    )

    # Verify the messages were received in order
    assert len(received_messages) == 3
    assert [msg["event"] for msg in received_messages] == ["start", "update", "complete"]
    assert [msg["id"] for msg in received_messages] == [1, 2, 3]
```

#### Long-Running Test with Controlled Shutdown

```python
@pytest.mark.asyncio
async def test_long_running_agents(test_supervisor):
    """Test agents that run for a longer period with controlled shutdown."""
    # Register agents with longer running operations
    await test_supervisor.register_agent("long_agent1", {
        "protocols": [{"type": "a2a-http"}],
        "processing_delay": 2.0  # Simulated processing delay
    })

    await test_supervisor.register_agent("long_agent2", {
        "protocols": [{"type": "a2a-http"}],
        "processing_delay": 1.5
    })

    # Start the supervisor
    await test_supervisor.start()

    # Get agent references
    agent1 = test_supervisor.get_agent("long_agent1")
    agent2 = test_supervisor.get_agent("long_agent2")

    # Track messages for verification
    messages = []
    done_event = asyncio.Event()

    def message_handler(msg):
        messages.append(msg)
        if len(messages) >= 3:
            done_event.set()

    # Register message handler
    test_supervisor.observe_agent_messages("long_agent2", message_handler)

    # Start periodic message sending task
    async def send_periodic_messages():
        for i in range(3):
            await agent1.send_message("long_agent2", {
                "sequence": i,
                "content": f"Message {i}"
            })
            await asyncio.sleep(1.0)

    # Run the periodic sending task
    send_task = asyncio.create_task(send_periodic_messages())

    # Wait for all messages or timeout
    try:
        await asyncio.wait_for(done_event.wait(), timeout=10.0)

        # Verify messages
        assert len(messages) == 3
        assert [msg["sequence"] for msg in messages] == [0, 1, 2]

    finally:
        # Clean up regardless of test outcome
        send_task.cancel()
        try:
            await send_task
        except asyncio.CancelledError:
            pass
```

### 4. Helper Utilities for Async Testing

Create utility functions to assist with common async testing patterns:

```python
# openmas/testing/utils.py
import asyncio
from typing import Callable, TypeVar, Any, Optional

T = TypeVar('T')

async def wait_for_condition(
    condition_func: Callable[[], bool],
    timeout: float = 5.0,
    check_interval: float = 0.1,
    error_message: str = "Condition not met within timeout"
) -> None:
    """
    Wait for a condition to be met with timeout.

    Args:
        condition_func: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        check_interval: Time between condition checks in seconds
        error_message: Error message if timeout occurs

    Raises:
        asyncio.TimeoutError: If condition not met within timeout
    """
    start_time = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start_time) < timeout:
        if condition_func():
            return
        await asyncio.sleep(check_interval)

    raise asyncio.TimeoutError(error_message)

async def wait_for_value(
    value_func: Callable[[], Optional[T]],
    timeout: float = 5.0,
    check_interval: float = 0.1,
    error_message: str = "Value not available within timeout"
) -> T:
    """
    Wait for a value to become available with timeout.

    Args:
        value_func: Function that returns the value when available or None
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        error_message: Error message if timeout occurs

    Returns:
        The value when it becomes available

    Raises:
        asyncio.TimeoutError: If value not available within timeout
    """
    start_time = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start_time) < timeout:
        value = value_func()
        if value is not None:
            return value
        await asyncio.sleep(check_interval)

    raise asyncio.TimeoutError(error_message)
```

### 5. Mock Network Utilities

Create utilities for mocking network interactions in protocol tests:

```python
# openmas/testing/network.py
import asyncio
import socket
from contextlib import contextmanager
from typing import Iterator, Tuple, Dict, Any, Optional

@contextmanager
def mock_http_server(response_data: Dict[str, Any], port: int = 0) -> Iterator[Tuple[str, int]]:
    """
    Create a mock HTTP server for testing.

    Args:
        response_data: Data to return in HTTP responses
        port: Port to listen on (0 for auto-assignment)

    Yields:
        Tuple of (host, port) for the mock server
    """
    async def handler(reader, writer):
        # Read the request
        data = await reader.read(1024)

        # Prepare response
        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: application/json\r\n"
            b"Connection: close\r\n\r\n"
        )
        response += json.dumps(response_data).encode()

        # Send response
        writer.write(response)
        await writer.drain()
        writer.close()

    # Create server
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(
        asyncio.start_server(handler, '127.0.0.1', port)
    )

    # Get the assigned port
    socket_info = server.sockets[0].getsockname()
    host, port = socket_info[0], socket_info[1]

    try:
        yield (host, port)
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())

def get_free_port() -> int:
    """Get a free port for testing."""
    with socket.socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]
```

## Integration with CI/CD

For running async integration tests in CI/CD pipelines:

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  push:
    branches: [ main, 030 ]
  pull_request:
    branches: [ main, 030 ]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install --all-extras

    - name: Run integration tests
      run: |
        poetry run pytest tests/integration/ -v --asyncio-mode=auto
```

## Best Practices for Async Integration Tests

1. **Always use timeouts**: Never wait indefinitely for async operations
   ```python
   # Good
   await asyncio.wait_for(future, timeout=5.0)

   # Bad
   await future  # No timeout, could hang indefinitely
   ```

2. **Proper cleanup in fixtures**: Ensure all resources are released
   ```python
   @pytest.fixture
   async def agent_fixture():
       agent = Agent(...)
       await agent.start()

       yield agent

       # Always clean up, even if test fails
       await agent.stop()
   ```

3. **Use event-based coordination**: Prefer events over time-based waits
   ```python
   # Good
   event = asyncio.Event()
   agent.on_message(lambda _: event.set())
   await event.wait()

   # Avoid when possible
   await asyncio.sleep(1)  # Arbitrary wait times are brittle
   ```

4. **Isolation between tests**: Ensure tests don't interfere with each other
   ```python
   # Use unique identifiers per test
   @pytest.fixture
   def agent_id():
       return f"test-agent-{uuid.uuid4()}"
   ```

5. **Error propagation**: Ensure errors in async tasks are properly propagated
   ```python
   # Start task and handle exceptions
   task = asyncio.create_task(agent.run())
   try:
       # Test logic here
       await asyncio.sleep(1)
   finally:
       # Cancel task and check for exceptions
       task.cancel()
       try:
           await task
       except asyncio.CancelledError:
           pass  # Expected
       except Exception as e:
           pytest.fail(f"Unexpected error: {e}")
   ```

## Implementation Plan

1. **Create Test Framework** (Week 1)
   - Implement `TestSupervisor` class
   - Create base fixtures for pytest-asyncio
   - Implement helper utilities

2. **Protocol Test Patterns** (Week 2)
   - Implement A2A protocol testing patterns
   - Implement MCP protocol testing patterns
   - Create mock servers for protocol testing

3. **Integration Test Suite** (Week 3)
   - Create multi-protocol test scenarios
   - Implement agent-to-agent communication tests
   - Test protocol-specific features

4. **CI/CD Integration** (Week 4)
   - Configure GitHub Actions for integration tests
   - Implement test reporting and visualization
   - Optimize test execution time

## Conclusion

This approach to async integration testing provides a robust framework for testing OpenMAS's multi-agent, multi-protocol capabilities. The TestSupervisor pattern combined with pytest-asyncio gives us the control and flexibility needed to test complex asynchronous interactions while maintaining reliable, deterministic test results.

By implementing this testing strategy, we'll ensure that OpenMAS 0.3.0 maintains its reasoning agnosticism while providing reliable protocol implementations across A2A, MCP, HTTP, MQTT, and gRPC.
