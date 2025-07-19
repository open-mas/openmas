# Testing OpenMAS Extensions

## Overview

This guide covers comprehensive testing approaches for OpenMAS extensions, ensuring they function correctly, maintain reasoning agnosticism, and work seamlessly across all supported protocols. A well-tested extension is critical for reliability and maintainability.

## Testing Principles

When testing OpenMAS extensions, follow these key principles:

1. **Protocol Independence** - Test across all supported protocols
2. **Reasoning Agnosticism** - Verify functionality with different reasoning approaches
3. **Configuration Validation** - Test with various configuration options
4. **Error Handling** - Verify graceful failure under error conditions
5. **Isolation** - Test components in isolation before integration
6. **Mock External Dependencies** - Use mocks for external services
7. **Performance** - Test resource usage and responsiveness

## Test Types

### 1. Unit Tests

Unit tests focus on individual components of your extension in isolation.

```python
# test_weather_client.py
import pytest
from unittest.mock import patch, MagicMock
from openmas_weather.client import WeatherClient

class TestWeatherClient:
    @pytest.fixture
    def config(self):
        config_mock = MagicMock()
        config_mock.api_key_env = "WEATHER_API_KEY"
        config_mock.base_url = "https://api.example.com"
        config_mock.timeout = 5
        config_mock.units = "metric"
        config_mock.cache_ttl = 60
        return config_mock
    
    @pytest.fixture
    def client(self, config):
        with patch.dict('os.environ', {'WEATHER_API_KEY': 'test_key'}):
            return WeatherClient(config)
    
    @patch('requests.get')
    def test_get_current_weather(self, mock_get, client):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "temperature": 22.5,
            "condition": "Sunny"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call method
        result = client.get_current_weather("London")
        
        # Verify result
        assert result["temperature"] == 22.5
        assert result["condition"] == "Sunny"
        
        # Verify request
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "London" in kwargs["params"].values()
        assert "test_key" in kwargs["params"].values()
```

### 2. Integration Tests

Integration tests verify that the extension components work together correctly.

```python
# test_weather_extension_integration.py
import pytest
import os
from unittest.mock import patch
from openmas_weather.extension import WeatherServiceExtension
from openmas.extensions.registry import ExtensionRegistry

@pytest.fixture(autouse=True)
def setup_registry():
    # Reset the extension registry before each test
    ExtensionRegistry._instance = None
    return ExtensionRegistry.get_instance()

@pytest.fixture
def weather_config():
    return {
        "enabled": True,
        "api": {
            "api_key_env": "TEST_WEATHER_API_KEY",
            "base_url": "https://api.example.com",
            "timeout": 5,
            "units": "metric",
            "cache_ttl": 60
        },
        "default_location": "London",
        "capabilities": ["current_weather", "forecast", "alerts"],
        "protocol_mapping": {
            "a2a-http": {
                "current_weather": "getCurrentWeather"
            },
            "mcp-sse": {
                "current_weather": "get_current_weather_tool"
            }
        }
    }

@pytest.fixture
async def weather_extension(weather_config):
    with patch.dict('os.environ', {'TEST_WEATHER_API_KEY': 'test_key', 'OPENMAS_EXTENSIONS_MOCK': 'true'}):
        extension = WeatherServiceExtension(weather_config)
        await extension.initialize()
        yield extension
        await extension.shutdown()

@pytest.mark.asyncio
async def test_extension_initialization(weather_extension, setup_registry):
    # Verify the extension is initialized
    assert weather_extension._initialized
    
    # Verify capabilities were registered
    capabilities = setup_registry.list_capabilities()
    assert "current_weather" in capabilities
    assert "forecast" in capabilities
    assert "alerts" in capabilities
    
    # Verify protocol mappings
    a2a_mapping = setup_registry.get_protocol_mapping("a2a-http")
    assert "getCurrentWeather" in a2a_mapping
    
    mcp_mapping = setup_registry.get_protocol_mapping("mcp-sse")
    assert "get_current_weather_tool" in mcp_mapping

@pytest.mark.asyncio
async def test_capability_invocation(weather_extension, setup_registry):
    # Invoke capability through registry
    result = await setup_registry.invoke_capability("current_weather", {"location": "Berlin"})
    
    # Verify result
    assert result["location"] == "Berlin"
    assert "temperature" in result
    assert "condition" in result
```

### 3. Protocol-Specific Tests

Test extension functionality through each supported protocol.

```python
# test_weather_protocol_support.py
import pytest
import json
from unittest.mock import patch, MagicMock
from openmas_weather.extension import WeatherServiceExtension
from openmas.protocols.a2a import A2AProtocolHandler
from openmas.protocols.mcp import MCPProtocolHandler

@pytest.fixture
def weather_config():
    return {
        "enabled": True,
        "api": {
            "api_key_env": "TEST_WEATHER_API_KEY",
            "base_url": "https://api.example.com",
            "timeout": 5,
            "units": "metric",
            "cache_ttl": 60
        },
        "default_location": "London",
        "capabilities": ["current_weather"],
        "protocol_mapping": {
            "a2a-http": {
                "current_weather": "getCurrentWeather"
            },
            "mcp-sse": {
                "current_weather": "get_current_weather_tool"
            }
        }
    }

@pytest.fixture
async def initialized_extension(weather_config):
    with patch.dict('os.environ', {'TEST_WEATHER_API_KEY': 'test_key', 'OPENMAS_EXTENSIONS_MOCK': 'true'}):
        extension = WeatherServiceExtension(weather_config)
        await extension.initialize()
        yield extension
        await extension.shutdown()

@pytest.mark.asyncio
async def test_a2a_protocol(initialized_extension):
    # Create mock A2A protocol handler
    a2a_handler = MagicMock(spec=A2AProtocolHandler)
    
    # Create mock A2A request
    a2a_request = {
        "capability": "getCurrentWeather",
        "parameters": {
            "location": "Paris"
        }
    }
    
    # Mock invoke_capability method
    async def mock_invoke(capability, params):
        if capability == "getCurrentWeather":
            # Translate to internal capability name
            internal_capability = "current_weather"
            return await initialized_extension.get_current_weather(params["location"])
        return None
    
    a2a_handler.invoke_capability.side_effect = mock_invoke
    
    # Process request
    response = await a2a_handler.process_capability_request(json.dumps(a2a_request))
    response_data = json.loads(response)
    
    # Verify response
    assert response_data["location"] == "Paris"
    assert "temperature" in response_data
    assert "condition" in response_data

@pytest.mark.asyncio
async def test_mcp_protocol(initialized_extension):
    # Create mock MCP protocol handler
    mcp_handler = MagicMock(spec=MCPProtocolHandler)
    
    # Create mock MCP tool call
    mcp_tool_call = {
        "name": "get_current_weather_tool",
        "arguments": {
            "location": "Tokyo"
        }
    }
    
    # Mock invoke_tool method
    async def mock_invoke(tool_name, arguments):
        if tool_name == "get_current_weather_tool":
            # Translate to internal capability name
            internal_capability = "current_weather"
            return await initialized_extension.get_current_weather(arguments["location"])
        return None
    
    mcp_handler.invoke_tool.side_effect = mock_invoke
    
    # Process tool call
    response = await mcp_handler.process_tool_call(json.dumps(mcp_tool_call))
    response_data = json.loads(response)
    
    # Verify response
    assert response_data["location"] == "Tokyo"
    assert "temperature" in response_data
    assert "condition" in response_data
```

### 4. Reasoning Agnosticism Tests

Ensure your extension works with different reasoning approaches.

```python
# test_reasoning_agnosticism.py
import pytest
from unittest.mock import patch, MagicMock
from openmas_weather.extension import WeatherServiceExtension
from openmas.agents import LLMAgent, RuleBasedAgent, BDIAgent

@pytest.fixture
def weather_config():
    return {
        "enabled": True,
        "api": {
            "api_key_env": "TEST_WEATHER_API_KEY",
            "base_url": "https://api.example.com",
            "timeout": 5,
            "units": "metric",
            "cache_ttl": 60
        },
        "default_location": "London",
        "capabilities": ["current_weather", "forecast"],
        "protocol_mapping": {}
    }

@pytest.fixture
async def initialized_extension(weather_config):
    with patch.dict('os.environ', {'TEST_WEATHER_API_KEY': 'test_key', 'OPENMAS_EXTENSIONS_MOCK': 'true'}):
        extension = WeatherServiceExtension(weather_config)
        await extension.initialize()
        yield extension
        await extension.shutdown()

@pytest.mark.asyncio
async def test_with_llm_agent(initialized_extension):
    # Create mock LLM agent
    llm_agent = MagicMock(spec=LLMAgent)
    
    # Simulate the agent using the capability
    weather_data = await initialized_extension.get_current_weather("Barcelona")
    
    # Verify result with LLM-specific processing
    llm_response = f"The current weather in Barcelona is {weather_data['temperature']}°C and {weather_data['condition']}."
    llm_agent.generate_response.return_value = llm_response
    
    # Verify the agent can process the data
    response = await llm_agent.generate_response(weather_data)
    assert "Barcelona" in response
    assert str(weather_data['temperature']) in response

@pytest.mark.asyncio
async def test_with_rule_based_agent(initialized_extension):
    # Create mock rule-based agent
    rule_agent = MagicMock(spec=RuleBasedAgent)
    
    # Define a mock rule
    def mock_rule(data):
        if data.get("condition") == "Sunny" and data.get("temperature") > 20:
            return "outdoor_activities"
        else:
            return "indoor_activities"
    
    rule_agent.apply_rules.side_effect = mock_rule
    
    # Simulate the agent using the capability
    weather_data = await initialized_extension.get_current_weather("Rome")
    
    # Apply rule engine logic
    result = rule_agent.apply_rules(weather_data)
    
    # Verify rule-based processing works
    if weather_data["condition"] == "Sunny" and weather_data["temperature"] > 20:
        assert result == "outdoor_activities"
    else:
        assert result == "indoor_activities"

@pytest.mark.asyncio
async def test_with_bdi_agent(initialized_extension):
    # Create mock BDI agent
    bdi_agent = MagicMock(spec=BDIAgent)
    
    # Mock belief update
    def mock_update_belief(name, value):
        bdi_agent.beliefs[name] = value
        return True
    
    bdi_agent.beliefs = {}
    bdi_agent.update_belief.side_effect = mock_update_belief
    
    # Simulate the agent using the capability
    weather_data = await initialized_extension.get_forecast("Miami", days=3)
    
    # Update belief with weather data
    bdi_agent.update_belief("forecast_miami", weather_data)
    
    # Verify belief was updated
    assert "forecast_miami" in bdi_agent.beliefs
    assert bdi_agent.beliefs["forecast_miami"] == weather_data
```

### 5. Configuration Tests

Test how your extension behaves with different configuration options.

```python
# test_weather_configuration.py
import pytest
from unittest.mock import patch
from openmas_weather.extension import WeatherServiceExtension

@pytest.mark.asyncio
async def test_disabled_extension():
    config = {
        "enabled": False,
        "api": {
            "api_key_env": "TEST_WEATHER_API_KEY",
            "base_url": "https://api.example.com",
            "timeout": 5,
            "units": "metric",
            "cache_ttl": 60
        }
    }
    
    with patch.dict('os.environ', {'TEST_WEATHER_API_KEY': 'test_key'}):
        extension = WeatherServiceExtension(config)
        result = await extension.initialize()
        assert result is False
        assert extension._initialized is False

@pytest.mark.asyncio
async def test_missing_api_key():
    config = {
        "enabled": True,
        "api": {
            "api_key_env": "NONEXISTENT_API_KEY",
            "base_url": "https://api.example.com",
            "timeout": 5,
            "units": "metric",
            "cache_ttl": 60
        },
        "capabilities": ["current_weather"]
    }
    
    with patch.dict('os.environ', {}, clear=True):
        extension = WeatherServiceExtension(config)
        # Should initialize but log warning about missing API key
        await extension.initialize()
        
        # Should still function with mock implementation
        with patch.dict('os.environ', {'OPENMAS_EXTENSIONS_MOCK': 'true'}):
            extension.client.mock_implementation()
            result = await extension.get_current_weather("Berlin")
            assert result["location"] == "Berlin"

@pytest.mark.asyncio
async def test_selective_capability_enabling():
    config = {
        "enabled": True,
        "api": {
            "api_key_env": "TEST_WEATHER_API_KEY",
            "base_url": "https://api.example.com",
            "timeout": 5,
            "units": "metric",
            "cache_ttl": 60
        },
        "capabilities": ["current_weather"],  # Only enable current_weather, not forecast or alerts
        "protocol_mapping": {}
    }
    
    with patch.dict('os.environ', {'TEST_WEATHER_API_KEY': 'test_key', 'OPENMAS_EXTENSIONS_MOCK': 'true'}):
        extension = WeatherServiceExtension(config)
        await extension.initialize()
        
        # current_weather should work
        result = await extension.get_current_weather("Paris")
        assert result["location"] == "Paris"
        
        # forecast should raise error since it's not enabled
        with pytest.raises(RuntimeError):
            await extension.get_forecast("Paris")
```

### 6. Performance Tests

Test your extension's resource usage and responsiveness.

```python
# test_weather_performance.py
import pytest
import time
import asyncio
from unittest.mock import patch
from openmas_weather.extension import WeatherServiceExtension

@pytest.fixture
def weather_config():
    return {
        "enabled": True,
        "api": {
            "api_key_env": "TEST_WEATHER_API_KEY",
            "base_url": "https://api.example.com",
            "timeout": 5,
            "units": "metric",
            "cache_ttl": 60
        },
        "default_location": "London",
        "capabilities": ["current_weather", "forecast", "alerts"],
        "protocol_mapping": {}
    }

@pytest.fixture
async def initialized_extension(weather_config):
    with patch.dict('os.environ', {'TEST_WEATHER_API_KEY': 'test_key', 'OPENMAS_EXTENSIONS_MOCK': 'true'}):
        extension = WeatherServiceExtension(weather_config)
        await extension.initialize()
        yield extension
        await extension.shutdown()

@pytest.mark.asyncio
async def test_response_time(initialized_extension):
    # Measure response time
    start_time = time.time()
    await initialized_extension.get_current_weather("Tokyo")
    elapsed_time = time.time() - start_time
    
    # Response should be under 500ms (adjust as needed)
    assert elapsed_time < 0.5, f"Response time too slow: {elapsed_time}s"

@pytest.mark.asyncio
async def test_cache_effectiveness(initialized_extension):
    # First request (cache miss)
    start_time = time.time()
    await initialized_extension.get_current_weather("New York")
    first_request_time = time.time() - start_time
    
    # Second request (cache hit)
    start_time = time.time()
    await initialized_extension.get_current_weather("New York")
    second_request_time = time.time() - start_time
    
    # Cache hit should be significantly faster
    assert second_request_time < first_request_time * 0.5, f"Cache not effective: {first_request_time}s vs {second_request_time}s"

@pytest.mark.asyncio
async def test_concurrent_requests(initialized_extension):
    # Create multiple concurrent requests
    locations = ["London", "Paris", "Berlin", "Tokyo", "New York", "Sydney", "Moscow", "Beijing", "Cairo", "Rio"]
    
    start_time = time.time()
    tasks = [initialized_extension.get_current_weather(location) for location in locations]
    results = await asyncio.gather(*tasks)
    elapsed_time = time.time() - start_time
    
    # Verify all requests completed successfully
    assert len(results) == len(locations)
    for i, result in enumerate(results):
        assert result["location"] == locations[i]
    
    # Check overall performance
    assert elapsed_time < 1.0, f"Concurrent performance too slow: {elapsed_time}s for {len(locations)} requests"
```

## Test Infrastructure

### Continuous Integration

Set up CI workflows for your extension to run tests automatically:

```yaml
# .github/workflows/test.yml
name: Test OpenMAS Weather Extension

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
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
        pip install pytest pytest-asyncio pytest-cov
        pip install -e .
    - name: Test with pytest
      run: |
        pytest --cov=openmas_weather --cov-report=xml
      env:
        OPENMAS_EXTENSIONS_MOCK: "true"
        TEST_WEATHER_API_KEY: "test_key_for_ci"
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Test Coverage

Track test coverage to ensure all code paths are tested:

```bash
pytest --cov=openmas_weather --cov-report=html
```

## Testing Best Practices

### 1. Test Fixtures

Use fixtures for common test setup:

```python
@pytest.fixture
def standard_config():
    """Provide a standard extension configuration."""
    return {
        "enabled": True,
        "api": {
            "api_key_env": "TEST_WEATHER_API_KEY",
            "base_url": "https://api.example.com",
            "timeout": 5,
            "units": "metric"
        }
    }

@pytest.fixture
async def initialized_extension(standard_config):
    """Provide an initialized extension instance."""
    with patch.dict('os.environ', {'TEST_WEATHER_API_KEY': 'test_key', 'OPENMAS_EXTENSIONS_MOCK': 'true'}):
        extension = WeatherServiceExtension(standard_config)
        await extension.initialize()
        yield extension
        await extension.shutdown()
```

### 2. Test Parameterization

Test multiple variants using parameterization:

```python
@pytest.mark.parametrize("location,expected_unit", [
    ("New York", "°F"),
    ("London", "°C"),
    ("Tokyo", "°C"),
])
async def test_location_specific_units(initialized_extension, location, expected_unit):
    result = await initialized_extension.get_current_weather(location)
    assert expected_unit in result["temperature_display"]
```

### 3. Mocking External Dependencies

Mock external API calls to avoid network dependencies:

```python
@patch('requests.get')
def test_api_error_handling(mock_get, client):
    # Simulate API error
    mock_get.side_effect = requests.exceptions.RequestException("API error")
    
    # Verify error handling
    with pytest.raises(requests.exceptions.RequestException):
        client.get_current_weather("London")
```

### 4. Test Environment Variables

Set test-specific environment variables:

```python
def test_with_environment():
    with patch.dict('os.environ', {
        'TEST_WEATHER_API_KEY': 'test_key',
        'OPENMAS_EXTENSIONS_MOCK': 'true',
        'OPENMAS_WEATHER_DEFAULT_LOCATION': 'Test City'
    }):
        # Test code that uses these environment variables
        pass
```

### 5. Protocol Simulation

Create protocol simulators to test protocol-specific behavior:

```python
class A2ASimulator:
    """Simulate A2A protocol interactions."""
    
    def __init__(self, registry):
        self.registry = registry
    
    async def call_capability(self, agent_id, capability_name, parameters):
        """Simulate an A2A capability call."""
        # Map external name to internal capability
        internal_capability = self.registry.get_internal_capability(agent_id, "a2a-http", capability_name)
        
        if not internal_capability:
            raise ValueError(f"Unknown capability: {capability_name}")
        
        # Invoke capability
        return await self.registry.invoke_capability(internal_capability, parameters)
```

## Advanced Testing Strategies

### 1. Property-Based Testing

Use property-based testing for complex scenarios:

```python
from hypothesis import given, strategies as st

@given(location=st.text(min_size=2, max_size=100))
async def test_location_property(initialized_extension, location):
    """Test that any location string returns data with matching location."""
    result = await initialized_extension.get_current_weather(location)
    assert result["location"] == location
```

### 2. Chaos Testing

Test resilience against intermittent failures:

```python
@patch('requests.get')
async def test_intermittent_failures(mock_get, initialized_extension):
    # Configure mock to fail every other request
    call_count = 0
    
    def intermittent_failure(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count % 2 == 0:
            raise requests.exceptions.RequestException("Intermittent failure")
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"temperature": 22.5, "condition": "Sunny"}
        mock_response.raise_for_status.return_value = None
        return mock_response
    
    mock_get.side_effect = intermittent_failure
    
    # Test retry logic
    for _ in range(5):
        try:
            result = await initialized_extension.get_current_weather("London")
            assert result["temperature"] == 22.5
        except requests.exceptions.RequestException:
            # Should not reach here if retry logic works
            pytest.fail("Retry logic failed")
```

### 3. Load Testing

Test under high load conditions:

```python
@pytest.mark.asyncio
async def test_high_load(initialized_extension):
    # Generate many concurrent requests
    locations = [f"City{i}" for i in range(100)]
    
    # Execute in batches to avoid overwhelming the system
    for batch_start in range(0, len(locations), 10):
        batch = locations[batch_start:batch_start+10]
        tasks = [initialized_extension.get_current_weather(location) for location in batch]
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results):
            assert result["location"] == batch[i]
```

## Conclusion

Thorough testing ensures your OpenMAS extensions are reliable, maintainable, and work consistently across different reasoning approaches and protocols. By following the approaches outlined in this guide, you can validate that your extensions:

1. Maintain reasoning agnosticism
2. Work correctly with all protocols
3. Handle configuration changes appropriately
4. Manage errors gracefully
5. Perform efficiently under load

Remember that testing is not just about verifying functionality but also about documenting expected behavior and providing examples for other developers.
