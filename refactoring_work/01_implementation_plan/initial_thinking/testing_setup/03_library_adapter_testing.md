# Library Adapter Testing for OpenMAS 0.3.0

## Core Principles
This document establishes critical principles for creating and testing library adapters in OpenMAS 0.3.0, ensuring reliability, maintainability, and proper encapsulation of external dependencies.

## 1. Library API Verification

Before implementing any adapter, always verify the actual API of the library:

### Required Steps
- **Inspect the actual API** of the target library using concrete methods:
  ```python
  # Inspect package metadata
  !pip show [LIBRARY_NAME]

  # Inspect modules and interfaces
  import [LIBRARY_NAME]
  dir([LIBRARY_NAME])
  help([LIBRARY_NAME].[CLASS_OR_FUNCTION])

  # View source code for deeper understanding
  import inspect
  print(inspect.getsource([LIBRARY_NAME].[CLASS_OR_FUNCTION]))
  ```

- **Document the verified API surface** before implementation:
  ```markdown
  ## Library API Documentation
  - Library: [LIBRARY_NAME]
  - Version: [VERSION]
  - Core Classes:
    - Class1: [methods, attributes]
    - Class2: [methods, attributes]
  - Key Functions:
    - function1(param1, param2) -> return_type
    - function2(param1, param2) -> return_type
  - Authentication Methods:
    - [list verified authentication mechanisms]
  ```

- **Create type stubs** for third-party libraries when needed:
  ```python
  # example.pyi
  class ExampleClass:
      def method1(self, param: str) -> bool: ...
      def method2(self, param: int) -> list[str]: ...
  ```

## 2. Adapter Implementation

Create adapters that properly encapsulate external libraries:

### Design Principles
- **Single Responsibility**: Each adapter should focus on a single external library
- **Interface-based**: Define clear interfaces for all adapters
- **Minimal Surface**: Only expose necessary functionality
- **Proper Error Handling**: Translate library-specific errors to OpenMAS exceptions

### Implementation Pattern
```python
from abc import ABC, abstractmethod
from typing import Protocol, Any, TypeVar, Generic

# Define the interface
class LibraryServiceInterface(Protocol):
    def operation1(self, param1: str) -> dict[str, Any]: ...
    def operation2(self, param1: int, param2: bool) -> list[str]: ...

# Create the adapter
class ConcreteLibraryAdapter:
    """Adapter for [LIBRARY_NAME] version [VERSION]."""

    def __init__(self, library_client: Any):
        """
        Initialize the adapter with the library client.

        Args:
            library_client: The actual library client instance

        Note:
            Verified with [LIBRARY_NAME] version [VERSION] on [DATE]
        """
        self.client = library_client

    def operation1(self, param1: str) -> dict[str, Any]:
        """
        Perform operation1 using the library.

        Maps to: library_client.some_actual_method(param1)

        Args:
            param1: The parameter required by the library

        Returns:
            Dictionary result from the library call

        Raises:
            OpenMASAdapterError: If the library operation fails
        """
        try:
            # Only call methods confirmed to exist
            result = self.client.some_actual_method(param1)
            # Transform to the expected interface if needed
            return self._transform_result(result)
        except LibrarySpecificError as e:
            # Translate to OpenMAS exceptions
            raise OpenMASAdapterError(f"Operation failed: {e}")

    def _transform_result(self, raw_result: Any) -> dict[str, Any]:
        """Transform library-specific result to adapter interface format."""
        # Transformation logic here
        return {"key": raw_result.value}
```

## 3. Dependency Injection

Implement proper dependency injection for all adapters:

### Implementation Patterns

#### Factory-based Injection
```python
class LibraryAdapterFactory:
    @classmethod
    def create(cls, config: dict[str, Any]) -> LibraryServiceInterface:
        """Create an adapter instance based on configuration."""
        if "mock" in config and config["mock"]:
            return MockLibraryAdapter()

        # Create the real client with verified API
        real_client = RealLibrary.Client(
            api_key=config["api_key"],
            endpoint=config["endpoint"]
        )

        return ConcreteLibraryAdapter(real_client)
```

#### Constructor Injection
```python
class AgentWithLibraryDependency:
    def __init__(self, library_service: LibraryServiceInterface):
        """
        Initialize with a library service.

        Args:
            library_service: Any implementation of LibraryServiceInterface
        """
        self.library_service = library_service

    def perform_operation(self, param: str) -> dict[str, Any]:
        """Use the injected service to perform operations."""
        return self.library_service.operation1(param)
```

#### Container-based Injection
```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Library client with real implementation
    library_client = providers.Factory(
        RealLibrary.Client,
        api_key=config.api_key,
        endpoint=config.endpoint
    )

    # Adapter with injected client
    library_adapter = providers.Factory(
        ConcreteLibraryAdapter,
        library_client=library_client
    )

    # Service that uses the adapter
    agent_service = providers.Factory(
        AgentWithLibraryDependency,
        library_service=library_adapter
    )
```

## 4. Integration Testing

Integration tests must always use the real library:

### Test Implementation Pattern
```python
import pytest
from unittest.mock import patch, MagicMock

class TestLibraryIntegration:
    @pytest.fixture
    def real_adapter(self):
        """Create a real adapter with the actual library."""
        # Use test credentials or API keys
        real_client = RealLibrary.Client(
            api_key="test_key",
            endpoint="test_endpoint"
        )
        return ConcreteLibraryAdapter(real_client)

    def test_operation1_integration(self, real_adapter):
        """Test operation1 with the real library."""
        # This is an integration test against the real library
        result = real_adapter.operation1("test_param")
        assert "key" in result
        assert isinstance(result["key"], str)

    def test_error_handling_integration(self, real_adapter):
        """Test error handling with the real library."""
        # Test with input that should cause an error
        with pytest.raises(OpenMASAdapterError):
            real_adapter.operation1("invalid_param")

class TestLibraryAdapter:
    @pytest.fixture
    def mock_client(self):
        """Create a mock client for unit testing."""
        mock = MagicMock()
        # Configure mock based on verified API behavior
        mock.some_actual_method.return_value = MagicMock(value="test_value")
        return mock

    @pytest.fixture
    def adapter(self, mock_client):
        """Create adapter with mock client."""
        return ConcreteLibraryAdapter(mock_client)

    def test_operation1_calls_correct_method(self, adapter, mock_client):
        """Test that operation1 calls the correct library method."""
        result = adapter.operation1("test_param")

        # Verify the correct library method was called
        mock_client.some_actual_method.assert_called_once_with("test_param")

        # Verify result transformation
        assert result == {"key": "test_value"}
```

## 5. Documentation Requirements

For each library adapter, provide comprehensive documentation:

### Required Documentation
- **Supported Library Versions**: List explicitly tested versions
- **API Coverage**: Document which parts of the library API are wrapped
- **Unsupported Features**: Clearly note which library features are not supported
- **Error Mapping**: Document how library errors map to OpenMAS exceptions
- **Configuration Options**: Document all configuration options for the adapter
- **Usage Examples**: Provide concrete usage examples with the real library

## 6. Version Checking and Compatibility

Implement version checking to prevent compatibility issues:

```python
import importlib.metadata
import warnings
from packaging import version

class VersionCompatibilityChecker:
    def __init__(self, library_name: str,
                 min_version: str, max_version: str = None):
        self.library_name = library_name
        self.min_version = version.parse(min_version)
        self.max_version = version.parse(max_version) if max_version else None

    def check(self) -> bool:
        """Check if the installed library is compatible."""
        try:
            current_version = version.parse(
                importlib.metadata.version(self.library_name)
            )

            if current_version < self.min_version:
                warnings.warn(
                    f"{self.library_name} version {current_version} is older than "
                    f"the minimum supported version {self.min_version}."
                )
                return False

            if self.max_version and current_version > self.max_version:
                warnings.warn(
                    f"{self.library_name} version {current_version} is newer than "
                    f"the maximum tested version {self.max_version}. "
                    f"Some features may not work as expected."
                )

            return True

        except importlib.metadata.PackageNotFoundError:
            warnings.warn(f"{self.library_name} is not installed.")
            return False
```

## Best Practices Checklist

When implementing a library adapter, always check against this list:

- [ ] Verified actual library API using concrete inspection methods
- [ ] Documented verified API surface before implementation
- [ ] Defined clear interface for the adapter
- [ ] Implemented proper error handling and translation
- [ ] Used dependency injection for all external dependencies
- [ ] Created unit tests with proper mocks
- [ ] Created integration tests against the real library
- [ ] Documented supported and unsupported features
- [ ] Implemented version compatibility checking
- [ ] Provided usage examples with the real library

## Anti-Patterns to Avoid

- ❌ **API Speculation**: Never assume or guess library APIs without verification
- ❌ **Direct Dependency**: Avoid direct dependencies; always use interfaces
- ❌ **Mock-Only Testing**: Never rely solely on mocks; always include integration tests
- ❌ **Over-Adaptation**: Don't try to wrap every single library feature
- ❌ **Hidden Dependencies**: Don't hide dependencies inside implementation details
- ❌ **Version Ignorance**: Don't ignore library version compatibility
- ❌ **Hallucinated Capabilities**: Don't implement features that don't exist in the library

## Summary

Following these principles ensures that all OpenMAS library adapters:

1. **Work correctly** with the actual libraries they wrap
2. **Can be tested** thoroughly with both unit and integration tests
3. **Maintain clear boundaries** between OpenMAS and external dependencies
4. **Can be mocked** for testing other components
5. **Handle errors** appropriately
6. **Document compatibility** clearly
