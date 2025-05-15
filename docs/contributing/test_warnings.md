# Handling Test Warnings in OpenMAS

This document provides guidance on identifying, addressing, and filtering warnings that may appear during OpenMAS test execution.

## Common Warning Patterns

The OpenMAS test suite may produce various warnings during execution. Some warnings indicate actual problems that need to be fixed, while others are expected behavior or limitations in the testing environment. Below are common warning patterns and how to interpret them:

### 1. "Coroutine was never awaited" Warnings

**Pattern:**
```
RuntimeWarning: coroutine '...' was never awaited
```

**Causes:**
- Creating an async coroutine without awaiting it
- Using a synchronous mock for an async method
- Not properly awaiting mocked async methods in test code

**How to handle:**
- Replace regular `MagicMock` with `AsyncMock` for async methods
- Ensure proper awaiting of all created coroutines
- When testing code that conditionally awaits (e.g., checking if an object has `__await__`), use an `AsyncMock` to properly mock the behavior

**Example solution:**
```python
# INCORRECT
mock_response.raise_for_status = mock.MagicMock()

# CORRECT
mock_response.raise_for_status = mock.AsyncMock()
```

### 2. Resource Warnings

**Pattern:**
```
ResourceWarning: unclosed <socket.socket ... >
```

**Causes:**
- HTTP clients, servers, or connections not properly closed
- Using blocking calls in async code
- Test cleanup not executed due to test failures

**How to handle:**
- Use context managers with async resources
- Ensure test fixtures properly clean up even if tests fail
- Make sure all clients and servers have proper `close()` or `stop()` calls in test teardown

### 3. Deprecation Warnings

**Pattern:**
```
DeprecationWarning: ... is deprecated and will be removed in a future version
```

**Causes:**
- Using deprecated APIs or methods
- Dependencies using deprecated features of other libraries

**How to handle:**
- Update code to use recommended replacement APIs
- For third-party deprecation warnings, consider filtering if you cannot fix them directly

### 4. Import Warnings

**Pattern:**
```
ImportWarning: can't resolve package from __spec__ or __package__
```

**Causes:**
- Package/module import path issues
- Code importing from test directories without proper package structure

**How to handle:**
- Ensure your test imports follow proper Python package structure
- Avoid importing from tests in production code

## Filtering Known Warnings

In some cases, warnings cannot be fixed due to library limitations or expected test behaviors. In these cases, warnings can be filtered. Here's how to apply warning filters in OpenMAS:

### 1. Filtering Warnings in Tests

To filter specific warnings in a test file:

```python
import warnings

# At the top of the test file
warnings.filterwarnings("ignore", message="specific warning pattern")

# Or for a specific test
def test_something():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="specific warning pattern")
        # Test code
```

### 2. Filtering Warnings in pytest Configuration

For persistent filtering across the test suite, add filters to the `pytest.ini` file:

```ini
[pytest]
filterwarnings =
    ignore:coroutine '.*' was never awaited:RuntimeWarning
    ignore:unclosed.*:ResourceWarning
```

### 3. Using the Warning Filter Utilities

OpenMAS provides a utility module at `tests/utils/warning_filters.py` to simplify warning management in tests:

```python
from tests.utils.warning_filters import (
    ignore_coroutine_never_awaited,
    ignore_resource_warnings,
    ignore_deprecated_event_loop,
    catch_warnings_with_filtering
)

# Apply filters at the module level
ignore_coroutine_never_awaited()  # Filters common coroutine warnings for the entire module

# Apply filters for a specific test
def test_with_warnings():
    with catch_warnings_with_filtering(["coroutine '.*' was never awaited", "unclosed"]) as recorded_warnings:
        # Test code that might produce warnings

        # Verify no unexpected warnings
        assert len(recorded_warnings) == 0, f"Unexpected warnings: {[str(w.message) for w in recorded_warnings]}"
```

Available utility functions:

- `ignore_coroutine_never_awaited()`: Filters the common "coroutine was never awaited" warnings
- `ignore_resource_warnings()`: Filters warnings about unclosed sockets and transports
- `ignore_deprecated_event_loop()`: Filters asyncio event loop related deprecation warnings
- `catch_warnings_with_filtering(ignore_list)`: Context manager that catches warnings while filtering specified ones
- `show_test_warnings()`: Forces all warnings to be displayed, useful for debugging

### 4. Documenting Filtered Warnings

If you need to filter a warning, make sure to document:

1. The exact warning being filtered
2. Why filtering is necessary
3. Any future plans to address the warning properly

**Example documentation comment:**
```python
# We're filtering this warning because the underlying library doesn't properly
# handle async cleanup. This will be fixed when we upgrade to library version X.
warnings.filterwarnings("ignore", message="unclosed transport", category=ResourceWarning)
```

## Addressing vs. Filtering

As a general rule, warnings should be fixed rather than filtered. Only filter warnings when:

1. The warning comes from a third-party library you cannot control
2. Fixing the warning would require significant redesign with minimal benefit
3. The warning is a false positive due to test patterns (but document this case)

Always prefer proper fixes like:
- Using `AsyncMock` for async methods
- Properly awaiting coroutines
- Using context managers for resources
- Updating deprecated API usage

## Testing for Warnings

To ensure warnings are properly addressed, OpenMAS test suite includes tests that specifically verify warning behaviors:

```python
def test_no_coroutine_warnings():
    """Test that mocked async methods don't produce coroutine warnings."""
    with warnings.catch_warnings(record=True) as recorded_warnings:
        warnings.simplefilter("always")

        # Test code that shouldn't produce warnings

        # Check no warnings were issued
        assert not any(issubclass(w.category, RuntimeWarning) for w in recorded_warnings)
```

## Common Warning Fixes

### Fixing "Coroutine never awaited" warnings

```python
# In test setup
mock_task = mock.AsyncMock()  # Use AsyncMock for async methods
mock_client.post = mock.AsyncMock(return_value=mock_response)

# In communicator code
if hasattr(response.raise_for_status, "__await__"):
    await response.raise_for_status()  # Handle both sync and async methods
else:
    response.raise_for_status()
```

### Fixing resource warnings

```python
# Use context managers for resources
async with httpx.AsyncClient() as client:
    response = await client.post(url, json=payload)

# For mock objects, ensure cleanup in test teardown
@pytest.fixture
async def client_fixture():
    client = httpx.AsyncClient()
    yield client
    await client.aclose()  # Ensure cleanup
```

### Fixing deprecation warnings

```python
# Check documentation for the library and update to recommended patterns
# For example, replace:
app.on_event("startup")(startup_handler)

# With:
@app.lifespan("startup")
async def startup_handler():
    # startup logic
```
