# Library Adapter Testing

## Overview

This document describes the approaches and best practices for testing library adapters in OpenMAS. Library adapters provide interfaces between OpenMAS components and external libraries, maintaining OpenMAS's reasoning-agnostic design while enabling integration with various AI reasoning libraries, communication libraries, and service integrations.

## Library Adapter Test Focus Areas

Library adapter testing in OpenMAS focuses on these key areas:

1. **Interface Conformance**: Ensuring adapters implement the expected interfaces
2. **Functional Equivalence**: Verifying adapters provide equivalent functionality across libraries
3. **Error Handling**: Testing adaptation of library-specific errors to OpenMAS error model
4. **Resource Management**: Testing proper resource acquisition and release
5. **Configuration Mapping**: Testing translation between OpenMAS configurations and library configurations
6. **Performance Characteristics**: Measuring performance impact of adapter layers

## Common Library Adapter Categories

OpenMAS implements adapters for several categories of libraries:

### 1. Reasoning Library Adapters

Adapters for different reasoning approaches (respecting OpenMAS's reasoning agnosticism):

- **LLM Library Adapters**: Adapters for LangChain, LlamaIndex, etc.
- **Symbolic Reasoning Adapters**: Adapters for Prolog, rule engines, etc.
- **BDI Reasoning Adapters**: Adapters for BDI frameworks
- **Graph Reasoning Adapters**: Adapters for graph-based reasoning libraries

### 2. Protocol Library Adapters

Adapters for different communication protocols (supporting OpenMAS's multi-protocol design):

- **MCP Library Adapters**: Adapters for Model Context Protocol implementations
- **A2A Library Adapters**: Adapters for Agent-to-Agent Protocol implementations
- **HTTP Library Adapters**: Adapters for HTTP client/server libraries
- **MQTT Library Adapters**: Adapters for MQTT client libraries
- **gRPC Library Adapters**: Adapters for gRPC implementations

### 3. Service Integration Adapters

Adapters for external services:

- **Database Adapters**: Adapters for database libraries
- **Message Queue Adapters**: Adapters for message queue systems
- **Cloud Service Adapters**: Adapters for cloud platform services
- **Observability Adapters**: Adapters for monitoring and logging services

## Testing Approach

### Adapter Test Fixtures

```python
import pytest
from openmas.testing import AdapterTestHarness

@pytest.fixture
async def llm_adapter_harness():
    """Create a test harness for LLM adapters."""
    harness = AdapterTestHarness("llm")
    await harness.initialize()

    yield harness

    await harness.shutdown()

@pytest.fixture
async def http_adapter_harness():
    """Create a test harness for HTTP adapters."""
    harness = AdapterTestHarness("http")
    await harness.initialize()

    yield harness

    await harness.shutdown()

@pytest.fixture
async def database_adapter_harness():
    """Create a test harness for database adapters."""
    harness = AdapterTestHarness("database")
    await harness.initialize()

    yield harness

    await harness.shutdown()
```

### Interface Conformance Testing

```python
@pytest.mark.parametrize("adapter_type,adapter_name", [
    ("llm", "langchain"),
    ("llm", "llamaindex"),
    ("database", "sqlalchemy"),
    ("database", "mongodb"),
    ("http", "aiohttp"),
    ("http", "httpx")
])
async def test_adapter_interface_conformance(request, adapter_type, adapter_name):
    """Test that adapters conform to their expected interfaces."""
    # Get adapter harness
    harness = request.getfixturevalue(f"{adapter_type}_adapter_harness")

    # Create adapter instance
    adapter = await harness.create_adapter(adapter_name)

    # Get expected interface
    interface = harness.get_expected_interface()

    # Verify adapter implements all required methods
    for method_name, method_signature in interface.methods.items():
        assert hasattr(adapter, method_name), f"Adapter {adapter_name} missing method: {method_name}"

        # Verify method signature
        method = getattr(adapter, method_name)
        assert harness.check_signature_compatibility(method, method_signature), \
            f"Method signature mismatch for {method_name} in {adapter_name}"

    # Verify adapter implements all required properties
    for property_name, property_type in interface.properties.items():
        assert hasattr(adapter, property_name), f"Adapter {adapter_name} missing property: {property_name}"
```

### Functional Equivalence Testing

```python
@pytest.mark.parametrize("adapter_name", ["langchain", "llamaindex"])
async def test_llm_adapter_functional_equivalence(llm_adapter_harness, adapter_name):
    """Test functional equivalence across different LLM adapters."""
    # Create adapter instance
    adapter = await llm_adapter_harness.create_adapter(adapter_name)

    # Test prompts
    test_prompts = [
        "Hello, world!",
        "What is the capital of France?",
        "Explain the concept of machine learning."
    ]

    # Test with mock responses
    for prompt in test_prompts:
        # Configure mock underlying library to return consistent responses
        await llm_adapter_harness.configure_mock_response(
            adapter_name=adapter_name,
            input=prompt,
            output="Mock response for: " + prompt
        )

        # Execute through adapter
        response = await adapter.generate(prompt)

        # Verify response format is consistent across adapters
        assert "text" in response, f"Adapter {adapter_name} missing 'text' in response"
        assert response["text"] == "Mock response for: " + prompt
```

### Error Handling Testing

```python
@pytest.mark.parametrize("adapter_type,adapter_name,error_type", [
    ("llm", "langchain", "rate_limit"),
    ("llm", "llamaindex", "timeout"),
    ("database", "sqlalchemy", "connection"),
    ("database", "mongodb", "authentication"),
    ("http", "aiohttp", "network"),
    ("http", "httpx", "server")
])
async def test_adapter_error_handling(request, adapter_type, adapter_name, error_type):
    """Test that adapters properly handle and translate library-specific errors."""
    # Get adapter harness
    harness = request.getfixturevalue(f"{adapter_type}_adapter_harness")

    # Create adapter instance
    adapter = await harness.create_adapter(adapter_name)

    # Configure harness to trigger a specific error
    await harness.configure_error(
        adapter_name=adapter_name,
        error_type=error_type
    )

    # Attempt operation that will trigger error
    with pytest.raises(Exception) as excinfo:
        if adapter_type == "llm":
            await adapter.generate("This will cause an error")
        elif adapter_type == "database":
            await adapter.query("SELECT * FROM non_existent")
        elif adapter_type == "http":
            await adapter.request("GET", "http://will-cause-error.com")

    # Verify error is properly translated to OpenMAS error model
    error = excinfo.value
    assert harness.check_error_translation(error, error_type), \
        f"Error translation failed for {error_type} in {adapter_name}"

    # Verify error includes appropriate metadata
    assert hasattr(error, "source_library"), "Error missing source_library attribute"
    assert error.source_library == adapter_name, f"Error source_library should be {adapter_name}"
```

### Resource Management Testing

```python
@pytest.mark.parametrize("adapter_type,adapter_name", [
    ("llm", "langchain"),
    ("database", "sqlalchemy"),
    ("http", "aiohttp")
])
async def test_adapter_resource_management(request, adapter_type, adapter_name):
    """Test that adapters properly manage resources."""
    # Get adapter harness
    harness = request.getfixturevalue(f"{adapter_type}_adapter_harness")

    # Create adapter instance
    adapter = await harness.create_adapter(adapter_name)

    # Start resource tracking
    await harness.start_resource_tracking(adapter)

    # Initialize adapter resources
    await adapter.initialize()

    # Verify resources were acquired
    resource_status = await harness.get_resource_status(adapter)
    assert resource_status.active, f"Adapter {adapter_name} failed to acquire resources"

    # Use the adapter
    if adapter_type == "llm":
        await adapter.generate("Test prompt")
    elif adapter_type == "database":
        await adapter.query("SELECT 1")
    elif adapter_type == "http":
        await adapter.request("GET", "http://example.com")

    # Shutdown adapter
    await adapter.shutdown()

    # Verify resources were released
    resource_status = await harness.get_resource_status(adapter)
    assert not resource_status.active, f"Adapter {adapter_name} failed to release resources"
    assert resource_status.leaks == 0, f"Adapter {adapter_name} has resource leaks"
```

### Configuration Mapping Testing

```python
@pytest.mark.parametrize("adapter_type,adapter_name", [
    ("llm", "langchain"),
    ("llm", "llamaindex"),
    ("database", "sqlalchemy"),
    ("http", "aiohttp")
])
async def test_configuration_mapping(request, adapter_type, adapter_name):
    """Test adapter configuration mapping."""
    # Get adapter harness
    harness = request.getfixturevalue(f"{adapter_type}_adapter_harness")

    # Define OpenMAS configuration
    openmas_config = harness.get_test_configuration(adapter_name)

    # Create adapter with configuration
    adapter = await harness.create_adapter(adapter_name, config=openmas_config)

    # Extract library-specific configuration
    library_config = harness.extract_library_configuration(adapter)

    # Verify configuration mapping
    mapping_result = harness.verify_configuration_mapping(
        openmas_config=openmas_config,
        library_config=library_config,
        adapter_name=adapter_name
    )

    assert mapping_result.is_valid, f"Configuration mapping invalid: {mapping_result.errors}"
```

### Performance Impact Testing

```python
@pytest.mark.parametrize("adapter_type,adapter_name", [
    ("llm", "langchain"),
    ("llm", "llamaindex"),
    ("database", "sqlalchemy"),
    ("http", "aiohttp")
])
async def test_adapter_performance_impact(request, adapter_type, adapter_name):
    """Test performance impact of adapter layer."""
    # Get adapter harness
    harness = request.getfixturevalue(f"{adapter_type}_adapter_harness")

    # Create adapter instance
    adapter = await harness.create_adapter(adapter_name)

    # Get direct library instance (without adapter)
    direct_lib = await harness.get_direct_library_instance(adapter_name)

    # Prepare test workload
    workload = harness.get_performance_workload(adapter_type)

    # Measure performance through adapter
    adapter_stats = await harness.measure_performance(
        target=adapter,
        workload=workload,
        iterations=100
    )

    # Measure performance with direct library access
    direct_stats = await harness.measure_performance(
        target=direct_lib,
        workload=workload,
        iterations=100
    )

    # Calculate overhead
    overhead_percent = ((adapter_stats.avg_latency / direct_stats.avg_latency) - 1.0) * 100

    # Assert reasonable overhead
    assert overhead_percent < 10.0, f"Adapter {adapter_name} has excessive overhead: {overhead_percent:.2f}%"

    # Log performance metrics
    print(f"Adapter {adapter_name} overhead: {overhead_percent:.2f}%")
    print(f"Adapter latency: {adapter_stats.avg_latency:.3f}ms")
    print(f"Direct latency: {direct_stats.avg_latency:.3f}ms")
```

## Adapter-Specific Testing Strategies

### LLM Library Adapter Testing

```python
async def test_langchain_adapter_specific_features(llm_adapter_harness):
    """Test LangChain-specific adapter features."""
    # Create LangChain adapter
    adapter = await llm_adapter_harness.create_adapter("langchain")

    # Test LangChain-specific feature: chains
    chain_config = {
        "type": "sequential_chain",
        "steps": [
            {"prompt": "Summarize: {input}"},
            {"prompt": "Translate to French: {input}"}
        ]
    }

    # Create chain through adapter
    chain = await adapter.create_chain(chain_config)

    # Configure mock responses
    await llm_adapter_harness.configure_mock_response(
        adapter_name="langchain",
        input="Summarize: Hello world",
        output="Greeting"
    )

    await llm_adapter_harness.configure_mock_response(
        adapter_name="langchain",
        input="Translate to French: Greeting",
        output="Salutation"
    )

    # Run chain
    result = await chain.run("Hello world")

    # Verify result
    assert result == "Salutation"
```

### Database Adapter Testing

```python
async def test_sqlalchemy_adapter_specific_features(database_adapter_harness):
    """Test SQLAlchemy-specific adapter features."""
    # Create SQLAlchemy adapter
    adapter = await database_adapter_harness.create_adapter("sqlalchemy")

    # Configure test database
    await database_adapter_harness.configure_test_database(adapter, [
        "CREATE TABLE test (id INT, name TEXT)",
        "INSERT INTO test VALUES (1, 'Item 1')",
        "INSERT INTO test VALUES (2, 'Item 2')"
    ])

    # Test SQLAlchemy-specific feature: ORM
    orm_config = {
        "model_name": "TestModel",
        "table_name": "test",
        "columns": [
            {"name": "id", "type": "Integer", "primary_key": True},
            {"name": "name", "type": "String"}
        ]
    }

    # Create ORM model through adapter
    TestModel = await adapter.create_orm_model(orm_config)

    # Query using ORM
    results = await adapter.query_orm(TestModel)

    # Verify results
    assert len(results) == 2
    assert results[0].id == 1
    assert results[0].name == "Item 1"
    assert results[1].id == 2
    assert results[1].name == "Item 2"
```

## Testing Against Real Libraries

For comprehensive testing, OpenMAS also includes integration tests against real libraries:

```python
@pytest.mark.real_library
@pytest.mark.parametrize("adapter_name,library_name,library_version", [
    ("langchain", "langchain", "0.0.267"),
    ("llamaindex", "llama-index", "0.8.54"),
    ("sqlalchemy", "sqlalchemy", "2.0.23"),
    ("aiohttp", "aiohttp", "3.8.5")
])
async def test_against_real_library(adapter_name, library_name, library_version):
    """Test adapter against real library."""
    try:
        # Import the real library
        module = importlib.import_module(library_name)

        # Check version
        if hasattr(module, "__version__"):
            assert module.__version__ == library_version, \
                f"Expected {library_name} version {library_version}, got {module.__version__}"

        # Create the adapter
        adapter_class = importlib.import_module(f"openmas.adapters.{adapter_name}").Adapter
        adapter = adapter_class()

        # Initialize the adapter
        await adapter.initialize()

        # Execute basic operation
        try:
            if adapter_name in ["langchain", "llamaindex"]:
                result = await adapter.generate("Test with real library")
                assert isinstance(result, dict)
                assert "text" in result
            elif adapter_name == "sqlalchemy":
                # Use in-memory SQLite for testing
                result = await adapter.execute("SELECT 1")
                assert result is not None
            elif adapter_name == "aiohttp":
                result = await adapter.request("GET", "http://httpbin.org/get")
                assert result.status == 200
        finally:
            # Cleanup
            await adapter.shutdown()
    except ImportError:
        pytest.skip(f"Library {library_name} not installed")
```

## External Service Testing

For adapters to external services, mock services are used to simulate the service behavior:

```python
@pytest.mark.parametrize("service_type", ["database", "message_queue", "cloud_storage"])
async def test_service_adapter_with_mock(adapter_mocks, service_type):
    """Test service adapters with mock services."""
    # Get the mock service
    mock_service = adapter_mocks.get_mock_service(service_type)

    # Create adapter for the service
    adapter = await adapter_mocks.create_adapter(service_type)

    # Configure adapter to use mock service
    await adapter.initialize(endpoint=mock_service.endpoint)

    # Configure expected operations and responses
    if service_type == "database":
        mock_service.expect_query("SELECT * FROM test", [{"id": 1, "name": "Test"}])
        result = await adapter.query("SELECT * FROM test")
        assert len(result) == 1
        assert result[0]["id"] == 1
    elif service_type == "message_queue":
        mock_service.expect_publish("test-topic", "test-message")
        await adapter.publish("test-topic", "test-message")
        assert mock_service.verify_expectations()
    elif service_type == "cloud_storage":
        mock_service.expect_upload("test-file.txt", b"test content")
        await adapter.upload("test-file.txt", b"test content")
        assert mock_service.verify_expectations()

    # Shutdown adapter
    await adapter.shutdown()
```

## Reasoning Adapter Testing (Respecting Reasoning Agnosticism)

```python
@pytest.mark.parametrize("reasoning_type,adapter_name", [
    ("llm", "langchain"),
    ("llm", "llamaindex"),
    ("rule_based", "drools"),
    ("bdi", "jadex"),
    ("graph", "networkx")
])
async def test_reasoning_adapter(reasoning_adapter_harness, reasoning_type, adapter_name):
    """Test reasoning adapters with different reasoning approaches."""
    # Create reasoning adapter
    adapter = await reasoning_adapter_harness.create_adapter(reasoning_type, adapter_name)

    # Configure test scenario
    scenario = reasoning_adapter_harness.get_scenario(reasoning_type)

    # Configure mock responses for the adapter
    await reasoning_adapter_harness.configure_mock_responses(adapter, scenario)

    # Run reasoning process
    result = await adapter.process(scenario.input)

    # Verify reasoning result structure (consistent across reasoning types)
    assert "result" in result, f"Reasoning result missing 'result' field for {reasoning_type}/{adapter_name}"
    assert "confidence" in result, f"Reasoning result missing 'confidence' field for {reasoning_type}/{adapter_name}"
    assert "explanation" in result, f"Reasoning result missing 'explanation' field for {reasoning_type}/{adapter_name}"

    # Verify result matches expected output (customized for reasoning type)
    assert scenario.validates_result(result), f"Reasoning result validation failed for {reasoning_type}/{adapter_name}"
```

## Best Practices

1. **Interface Contracts**: Define clear interface contracts for all adapters
2. **Test Multiple Libraries**: Test adapters against all supported libraries
3. **Configuration Testing**: Test configuration mapping thoroughly
4. **Error Translation**: Ensure consistent error translation across adapters
5. **Resource Management**: Verify proper resource acquisition and release
6. **Performance Monitoring**: Measure and track adapter performance overhead
7. **Versioning**: Test against specific library versions
8. **Compatibility Matrix**: Maintain a compatibility matrix for all adapters
9. **Mock Integration**: Use mocks for external service dependencies
10. **Real Integration**: Include tests against real libraries where possible
11. **Consistency Across Reasoning Types**: Ensure consistent behavior across different reasoning approaches
12. **Protocol Independence**: Ensure adapters work with all supported protocols

## Related Documentation

- [Protocol Testing](./protocol_testing.md)
- [Component Interoperability](../../01_architecture/component_interoperability/README.md)
- [Extensions](../../05_extensions/README.md)
- [Integrations](../../14_integrations/README.md)
