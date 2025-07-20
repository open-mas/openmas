# OpenMAS Testing Knowledge Base

This directory contains reference information and patterns for testing OpenMAS components.

## Testing Philosophy

OpenMAS follows these testing principles:

1. **Test-Driven Development (TDD)** - Tests are written before implementation
2. **Comprehensive Coverage** - Targeting at least 80% code coverage
3. **Isolation** - Unit tests must completely isolate the component being tested
4. **Dependency Injection** - All dependencies must be injectable to enable mocking
5. **Integration Testing** - Both mock and real integration tests

## Types of Tests

### Unit Tests

Unit tests focus on testing individual components in isolation:

```python
def test_config_loader_loads_valid_yaml(mock_file_reader):
    """Test that ConfigLoader correctly loads valid YAML."""
    # Arrange
    mock_file_reader.read_file.return_value = """
    project_name: test_project
    version: 1.0.0
    """
    loader = ConfigLoader(file_reader=mock_file_reader)

    # Act
    config = loader.load_config()

    # Assert
    assert config.project_name == "test_project"
    assert config.version == "1.0.0"
```

### Mock Integration Tests

Mock integration tests verify component interactions using mocked dependencies:

```python
async def test_agent_communicator_integration_mock(mock_communicator_factory, mock_agent):
    """Test integration between agent and communicator with mocks."""
    # Arrange
    communicator = mock_communicator_factory.create("http")
    mock_agent.communicator = communicator

    # Act
    await mock_agent.send_message("test message")

    # Assert
    communicator.send.assert_called_once_with("test message")
```

### Real Integration Tests

Real integration tests verify interactions with actual dependencies:

```python
@pytest.mark.integration
async def test_mcp_communicator_real_integration(real_mcp_server):
    """Test integration with a real MCP server."""
    # Arrange
    communicator = MCPSSECommunicator(
        config=CommunicatorConfig(
            type="mcp-sse",
            options={"url": real_mcp_server.url}
        )
    )
    await communicator.setup()

    # Act
    response = await communicator.send_prompt("Hello")

    # Assert
    assert response is not None
    assert isinstance(response, str)

    # Cleanup
    await communicator.shutdown()
```

## Test Tools

### Pytest

OpenMAS uses pytest as the primary testing framework:

```python
import pytest

def test_function():
    assert True
```

### Fixtures

Pytest fixtures for common test setup:

```python
@pytest.fixture
def mock_file_reader():
    """Create a mock file reader."""
    reader = MagicMock()
    reader.read_file.return_value = ""
    return reader

@pytest.fixture
def config_loader(mock_file_reader):
    """Create a ConfigLoader with a mock reader."""
    return ConfigLoader(file_reader=mock_file_reader)
```

### Parametrization

Testing multiple scenarios:

```python
@pytest.mark.parametrize("input_value,expected", [
    ("value1", "result1"),
    ("value2", "result2"),
    ("value3", "result3"),
])
def test_function_with_multiple_inputs(input_value, expected):
    assert function(input_value) == expected
```

### Async Testing

Testing async functions:

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected_value
```

## Mocking Strategies

### Dependency Injection

All dependencies should be injectable for testing:

```python
class ServiceWithDependencies:
    def __init__(self, dependency1=None, dependency2=None):
        self.dependency1 = dependency1 or RealDependency1()
        self.dependency2 = dependency2 or RealDependency2()
```

### Interface-Based Mocking

Create mocks based on interfaces:

```python
class FileReaderInterface(Protocol):
    def read_file(self, path: str) -> str: ...

class MockFileReader:
    def read_file(self, path: str) -> str:
        return "mock content"
```

### Factory Pattern for Testing

Use factories to create testable components:

```python
class CommunicatorFactory:
    def create(self, communicator_type: str, config: dict = None) -> BaseCommunicator:
        if communicator_type == "http":
            return HTTPCommunicator(config or {})
        elif communicator_type == "mcp-sse":
            return MCPSSECommunicator(config or {})
        # ...
```

## Running Tests

### Unit Tests

```bash
poetry run tox -e unit
```

### Integration Tests with Mocks

```bash
poetry run tox -e integration-mock
```

### Integration Tests with Real Dependencies

```bash
poetry run tox -e integration-real
```

### Coverage

```bash
poetry run tox -e coverage
```

## Best Practices

1. **Test One Thing at a Time** - Each test should verify one specific behavior
2. **Clear Test Names** - Use descriptive test names that explain what's being tested
3. **Arrange-Act-Assert** - Structure tests with clear setup, action, and verification
4. **Isolate Side Effects** - Avoid tests that affect the environment or other tests
5. **Test Edge Cases** - Include tests for error conditions and edge cases
6. **Avoid Test Logic** - Keep test logic simple; avoid conditionals in tests
7. **Clean Up Resources** - Properly clean up resources in teardown or fixtures
