# Testing Framework for OpenMAS 0.3.0

## Task Overview
Set up a comprehensive testing framework for OpenMAS 0.3.0, ensuring proper test coverage across all modules and protocols while maintaining the reasoning-agnostic architecture.

## Tasks

1. Testing Directory Structure
   - Create proper test directory structure mirroring the source code
   - Set up unit, integration, and end-to-end test directories
   - Configure test fixtures and utilities

2. Unit Testing Framework
   - Configure pytest for unit testing
   - Set up test discovery patterns
   - Configure code coverage reporting

3. Integration Testing
   - Create protocol-specific integration tests
   - Set up multi-agent system testing
   - Configure environment-specific testing

4. CI/CD Integration
   - Configure GitHub Actions integration for automated testing
   - Set up matrix testing across Python versions
   - Configure reporting and notifications

## Testing Directory Structure

```
tests/
├── conftest.py              # Root test configuration
├── __init__.py              # Test package initialization
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── agent/               # Agent tests
│   │   ├── __init__.py
│   │   ├── test_capabilities.py
│   │   ├── test_lifecycle.py
│   │   └── test_topologies.py
│   ├── assets/              # Asset tests
│   │   ├── __init__.py
│   │   ├── test_loaders.py
│   │   └── test_resources.py
│   ├── protocols/           # Protocol tests (aligned with design)
│   │   ├── __init__.py
│   │   ├── test_a2a.py
│   │   ├── test_mcp.py
│   │   ├── test_http.py
│   │   ├── test_mqtt.py
│   │   └── test_grpc.py
│   ├── communication_patterns/ # Communication patterns tests (aligned with design)
│   │   ├── __init__.py
│   │   ├── test_request_response.py
│   │   ├── test_publish_subscribe.py
│   │   ├── test_event_based.py
│   │   └── test_multi_protocol.py
│   ├── config/              # Configuration tests
│   │   ├── __init__.py
│   │   ├── test_schema.py
│   │   ├── test_validation.py
│   │   └── test_loaders.py
│   ├── extensions/          # Extension system tests
│   │   ├── __init__.py
│   │   ├── test_registration.py
│   │   └── test_discovery.py
│   ├── observability/       # Observability tests
│   │   ├── __init__.py
│   │   ├── test_logging.py
│   │   ├── test_metrics.py
│   │   └── test_tracing.py
│   ├── prompt_management/   # Prompt management tests (aligned with design)
│   │   ├── __init__.py
│   │   ├── test_templates.py
│   │   ├── test_variables.py
│   │   └── test_validation.py
│   ├── security/            # Security tests
│   │   ├── __init__.py
│   │   ├── test_authentication.py
│   │   └── test_authorization.py
│   ├── session_management/  # Session management tests (aligned with design)
│   │   ├── __init__.py
│   │   ├── test_persistence.py
│   │   └── test_coordination.py
│   ├── topology/            # Topology tests (aligned with design)
│   │   ├── __init__.py
│   │   ├── test_centralized.py
│   │   ├── test_decentralized.py
│   │   └── test_hybrid.py
│   ├── knowledge_representation/ # KR&R System tests (missing component)
│   │   ├── __init__.py
│   │   ├── test_knowledge_bases.py
│   │   ├── test_interfaces.py
│   │   ├── test_reasoning_support.py
│   │   └── test_knowledge_access.py
│   ├── asset_management/    # Asset management tests (missing component)
│   │   ├── __init__.py
│   │   ├── test_loaders.py
│   │   ├── test_versioning.py
│   │   └── test_registry.py
│   ├── cli_tools/           # CLI tools tests (missing component)
│   │   ├── __init__.py
│   │   ├── test_commands.py
│   │   ├── test_scaffolding.py
│   │   └── test_project_init.py
│   ├── integrations/        # Integrations tests (missing component)
│   │   ├── __init__.py
│   │   ├── test_services.py
│   │   ├── test_frameworks.py
│   │   └── test_adapters.py
│   └── deployment/          # Deployment tests (missing component)
│       ├── __init__.py
│       ├── test_local.py
│       ├── test_containers.py
│       ├── test_kubernetes.py
│       └── test_cloud.py
├── integration/             # Integration tests
│   ├── __init__.py
│   ├── conftest.py          # Integration test configuration
│   ├── test_a2a_protocol.py # A2A protocol integration
│   ├── test_mcp_protocol.py # MCP protocol integration
│   ├── test_http_protocol.py # HTTP protocol integration
│   ├── test_mqtt_protocol.py # MQTT protocol integration
│   ├── test_grpc_protocol.py # gRPC protocol integration
│   ├── test_multi_protocol.py # Multi-protocol integration
│   └── test_reasoning.py    # Reasoning integration
├── e2e/                     # End-to-end tests
│   ├── __init__.py
│   ├── conftest.py          # E2E test configuration
│   ├── test_agent_system.py # Complete agent system
│   └── test_scenarios.py    # Real-world scenarios
└── fixtures/                # Test fixtures
    ├── __init__.py
    ├── agent_fixtures.py    # Agent test fixtures
    ├── config_fixtures.py   # Configuration fixtures
    ├── protocol_fixtures.py # Protocol test fixtures
    └── mock_data/           # Mock data for testing
        ├── agent_cards/     # Sample agent cards
        ├── configs/         # Sample configurations
        └── messages/        # Sample messages
```

## Pytest Configuration

Create a comprehensive `pytest.ini` file:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Marker definitions
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    a2a: A2A protocol tests
    mcp: MCP protocol tests
    http: HTTP protocol tests
    mqtt: MQTT protocol tests
    grpc: gRPC protocol tests
    config: Configuration tests
    agent: Agent tests
    security: Security tests
    observability: Observability tests
    sessions: Session management tests
    extensions: Extension system tests

# Test discovery and execution options
xfail_strict = true
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
    error::RuntimeWarning

# Verbose output
verbose = true

# Coverage configuration
addopts = --cov=openmas --cov-report=term --cov-report=xml --cov-report=html
```

## Unit Testing Strategy

For each module, implement tests that cover:

1. **Functionality**: Test each function/method for expected behavior
2. **Edge Cases**: Test boundary conditions and unusual inputs
3. **Error Handling**: Test error conditions and verify proper exceptions
4. **Combinations**: Test interactions between components

### Example Unit Test Structure

```python
import pytest
from openmas.agent.capabilities import AgentCapabilities

class TestAgentCapabilities:
    def test_capability_registration(self):
        """Test that capabilities can be registered."""
        # Arrange
        caps = AgentCapabilities()

        # Act
        caps.register("test_capability", {"type": "test"})

        # Assert
        assert "test_capability" in caps.get_all()
        assert caps.get("test_capability")["type"] == "test"

    def test_capability_registration_duplicate(self):
        """Test that duplicate capabilities raise an exception."""
        # Arrange
        caps = AgentCapabilities()
        caps.register("test_capability", {"type": "test"})

        # Act/Assert
        with pytest.raises(ValueError):
            caps.register("test_capability", {"type": "different"})

    def test_capability_discovery(self):
        """Test that capabilities can be discovered."""
        # Arrange
        caps = AgentCapabilities()
        caps.register("test_capability", {"type": "test"})

        # Act
        discovered = caps.discover(capability_type="test")

        # Assert
        assert len(discovered) == 1
        assert "test_capability" in discovered
```

## Integration Testing Strategy

Integration tests verify interactions between components:

1. **Protocol Integration**: Test each protocol's communication patterns
2. **Multi-Protocol Scenarios**: Test agents using multiple protocols
3. **Environment Configuration**: Test configuration loading and validation
4. **Extension Integration**: Test extension loading and registration

### Example Integration Test Structure

```python
import pytest
from openmas.agent import Agent
from openmas.communicators.protocols.a2a import A2ACommunicator

class TestA2AProtocolIntegration:
    def test_agent_a2a_communication(self, a2a_config):
        """Test that agents can communicate using A2A protocol."""
        # Arrange
        agent1 = Agent(id="agent1", config=a2a_config)
        agent2 = Agent(id="agent2", config=a2a_config)

        # Act
        agent1.start()
        agent2.start()
        response = agent1.send_message(agent2.id, {"content": "hello"})

        # Assert
        assert response
        assert response.get("status") == "received"

        # Cleanup
        agent1.stop()
        agent2.stop()

    def test_agent_discovery(self, a2a_config):
        """Test that agents can discover each other using A2A protocol."""
        # Arrange
        agent1 = Agent(id="agent1", config=a2a_config)
        agent2 = Agent(id="agent2", config=a2a_config)

        # Act
        agent1.start()
        agent2.start()
        discovered = agent1.discover_agents()

        # Assert
        assert len(discovered) >= 1
        assert agent2.id in [a.id for a in discovered]

        # Cleanup
        agent1.stop()
        agent2.stop()
```

## End-to-End Testing Strategy

End-to-end tests verify complete user scenarios:

1. **Real-world Scenarios**: Test complete workflows
2. **Multi-Agent Systems**: Test systems with multiple interacting agents
3. **Cross-Protocol Scenarios**: Test scenarios involving multiple protocols

## Test Fixtures

Create test fixtures for commonly used components:

```python
# fixtures/agent_fixtures.py
import pytest
from openmas.agent import Agent

@pytest.fixture
def basic_agent_config():
    """Return a basic agent configuration."""
    return {
        "id": "test-agent",
        "class": "openmas.agent.Agent",
        "protocols": [
            {
                "type": "a2a-http",
                "options": {
                    "base_url": "http://localhost:8000"
                }
            }
        ],
        "capabilities": {
            "text": {
                "enabled": True
            }
        }
    }

@pytest.fixture
def basic_agent(basic_agent_config):
    """Return a basic initialized agent."""
    agent = Agent(config=basic_agent_config)
    yield agent
    # Cleanup
    if agent.is_running:
        agent.stop()
```

## Mocking Strategy

Use pytest-mock for creating test doubles:

1. **Protocol Mocks**: Mock protocol communication
2. **External Service Mocks**: Mock external dependencies
3. **Resource Mocks**: Mock file system, databases, etc.

```python
def test_a2a_communication_with_mock(mocker):
    """Test A2A communication with mocked transport."""
    # Mock the HTTP client
    mock_client = mocker.patch("openmas.communicators.protocols.a2a.http.client.HTTPClient")
    mock_client.return_value.send.return_value = {"status": "success"}

    # Create communicator with mocked client
    communicator = A2ACommunicator(config={"base_url": "http://example.com"})

    # Act
    result = communicator.send_message("agent1", {"content": "test"})

    # Assert
    assert result["status"] == "success"
    mock_client.return_value.send.assert_called_once()
```

## Code Coverage

Configure code coverage reporting:

```python
# conftest.py
import pytest
import coverage

# Start coverage before pytest session
def pytest_sessionstart(session):
    cov = coverage.Coverage(
        source=["openmas"],
        omit=[
            "*/__pycache__/*",
            "*/tests/*",
            "*/0.2.0/*"
        ]
    )
    cov.start()
    session.cov = cov

# Save coverage report after pytest session
def pytest_sessionfinish(session, exitstatus):
    if hasattr(session, "cov"):
        session.cov.stop()
        session.cov.save()
        session.cov.html_report(directory="coverage_html")
        session.cov.xml_report(outfile="coverage.xml")
```

## GitHub Actions Workflow for Testing

```yaml
name: Tests

on:
  push:
    branches: [ main, 030 ]
  pull_request:
    branches: [ main, 030 ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']

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
    - name: Test with pytest
      run: |
        poetry run pytest tests/unit/
    - name: Run integration tests
      run: |
        poetry run pytest tests/integration/
    - name: Upload coverage report
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
```

## Testing Reasoning Agnosticism

Create specific tests to verify reasoning agnosticism:

```python
def test_reasoning_agnosticism():
    """Test that different reasoning approaches can be used with the same communication protocols."""
    # Test with rule-based reasoning
    rule_agent = Agent(id="rule_agent", config={"reasoning": "rule_based"})

    # Test with BDI reasoning
    bdi_agent = Agent(id="bdi_agent", config={"reasoning": "bdi"})

    # Test with LLM reasoning
    llm_agent = Agent(id="llm_agent", config={"reasoning": "llm"})

    # Verify all agents can communicate using the same protocol
    rule_agent.start()
    bdi_agent.start()
    llm_agent.start()

    # Rule agent can send messages to BDI and LLM agents
    assert rule_agent.send_message(bdi_agent.id, {"content": "hello"})
    assert rule_agent.send_message(llm_agent.id, {"content": "hello"})

    # BDI agent can receive messages from rule and LLM agents
    assert bdi_agent.send_message(rule_agent.id, {"content": "hello"})
    assert bdi_agent.send_message(llm_agent.id, {"content": "hello"})

    # LLM agent can communicate with rule and BDI agents
    assert llm_agent.send_message(rule_agent.id, {"content": "hello"})
    assert llm_agent.send_message(bdi_agent.id, {"content": "hello"})

    # Cleanup
    rule_agent.stop()
    bdi_agent.stop()
    llm_agent.stop()
```

## Success Criteria
- Complete testing framework implemented
- Unit tests for all modules
- Integration tests for protocol interactions
- End-to-end tests for full system workflows
- Test coverage report showing ≥85% coverage
- CI/CD integration
- Tests verify reasoning agnosticism
- Tests verify protocol standardization
