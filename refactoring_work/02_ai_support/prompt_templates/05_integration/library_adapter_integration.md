# Library Adapter Integration Test Prompt

Use this prompt to guide AI assistants in creating proper integration tests for library adapters that test against the real library implementations rather than relying on mocks.

## Prompt Template

```
I need you to create/modify an adapter for [LIBRARY_NAME] (version [LIBRARY_VERSION]) that follows OpenMAS integration patterns, with a strong focus on proper integration testing.

## Adapter Requirements

### 1. API Inspection & Analysis
**FIRST** inspect the actual API of [LIBRARY_NAME] version [LIBRARY_VERSION]:
- Run and document outputs from:
  ```python
  # Verify installed version
  pip show [LIBRARY_NAME]
  
  # Examine module structure
  import [LIBRARY_NAME]
  dir([LIBRARY_NAME])
  
  # Explore key classes
  help([LIBRARY_NAME].[KEY_CLASS])
  ```
- Identify the ACTUAL classes, methods, and interfaces available
- Document your findings BEFORE implementing anything

### 2. Adapter Design
Create a MINIMAL adapter that:
- Implements only functionality with verified API endpoints
- Uses explicit interfaces derived from library inspection
- Adapts our system's interfaces to the library's actual interfaces
- Avoids speculative capabilities or methods not confirmed to exist

### 3. Integration Tests
Create integration tests that:
- Import and use the REAL library (not mocks)
- Verify each adapter method correctly calls the corresponding library method
- Include positive tests that demonstrate correct functionality
- Include negative tests that check proper error handling
- Document which parts of the library API are supported and which aren't
- Use appropriate test fixtures that work with the real library

### 4. Dependency Injection
Follow dependency injection principles:
- Make all dependencies explicit in constructor or method parameters
- Provide clear interface definitions
- Allow for configuration options required by the real library
- Separate interface from implementation

## Expected Code Structure

### Interface Definition
```python
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class [INTERFACE_NAME](ABC):
    """Interface for [LIBRARY_NAME] functionality."""
    
    @abstractmethod
    async def [METHOD_NAME](self, param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
        """
        [METHOD_DESCRIPTION]
        
        Args:
            param1: [PARAM_DESCRIPTION]
            param2: [PARAM_DESCRIPTION]
            
        Returns:
            [RETURN_DESCRIPTION]
            
        Raises:
            [EXCEPTION_TYPE]: [EXCEPTION_DESCRIPTION]
        """
        pass
```

### Adapter Implementation
```python
import [LIBRARY_NAME]
from [PACKAGE].interfaces import [INTERFACE_NAME]

class [ADAPTER_NAME]([INTERFACE_NAME]):
    """Adapter for [LIBRARY_NAME]."""
    
    def __init__(self, config: Dict[str, Any], **kwargs):
        """
        Initialize the adapter with necessary configuration.
        
        Args:
            config: Configuration dict for [LIBRARY_NAME]
            **kwargs: Additional configuration options
        """
        # Initialize actual library client/instance
        
    async def [METHOD_NAME](self, param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
        """Implementation using real [LIBRARY_NAME] API."""
        # Call actual library method
```

### Integration Test
```python
import pytest
import [LIBRARY_NAME]
from [PACKAGE].adapters.[ADAPTER_MODULE] import [ADAPTER_NAME]

@pytest.fixture
def [FIXTURE_NAME]():
    """Create a real [LIBRARY_NAME] client for testing."""
    # Setup real library (possibly with test config)
    yield [ADAPTER_INSTANCE]
    # Cleanup if needed

def test_[METHOD_NAME]_integration([FIXTURE_NAME]):
    """Test [METHOD_NAME] with real [LIBRARY_NAME] library."""
    # Arrange: Prepare test data
    
    # Act: Call adapter method
    
    # Assert: Verify correct behavior with real library
    
def test_[METHOD_NAME]_error_handling([FIXTURE_NAME]):
    """Test [METHOD_NAME] error handling with real [LIBRARY_NAME] library."""
    # Arrange: Prepare data that will trigger an error
    
    # Act & Assert: Verify proper error handling
```

## Documentation Requirements
Include documentation that clearly states:
1. Which version of [LIBRARY_NAME] was used for development and testing
2. Which parts of the library API are wrapped by the adapter
3. Any configuration requirements from the underlying library
4. Known limitations or unsupported features
5. How to extend the adapter for additional functionality

## Remember
- If you are unsure about any aspect of the real library's API, ASK for clarification
- Do NOT implement speculative functionality
- VERIFY all capabilities with the actual library before implementing
- Include instructions for installing the correct library version for testing
```

## How to Use

1. Replace placeholders with specific information about the library:
   - `[LIBRARY_NAME]`: The name of the library to adapt
   - `[LIBRARY_VERSION]`: The specific version of the library
   - `[KEY_CLASS]`: Key classes to inspect in the library
   - `[INTERFACE_NAME]`: Name of the interface to implement
   - `[ADAPTER_NAME]`: Name of the adapter implementation
   - `[METHOD_NAME]`: Methods to implement and test
   - Other placeholders as needed

2. Provide this prompt to the AI assistant.

3. Review the output adapter and tests for:
   - Verification that the library API was properly inspected
   - Real integration tests without excessive mocking
   - Proper error handling
   - Clear documentation of supported functionality

## Example

```
I need you to create/modify an adapter for OpenAI (version 1.5.0) that follows OpenMAS integration patterns, with a strong focus on proper integration testing.

## Adapter Requirements

### 1. API Inspection & Analysis
**FIRST** inspect the actual API of OpenAI version 1.5.0:
- Run and document outputs from:
  ```python
  # Verify installed version
  pip show openai
  
  # Examine module structure
  import openai
  dir(openai)
  
  # Explore key classes
  help(openai.OpenAI)
  help(openai.AsyncOpenAI)
  ```
- Identify the ACTUAL classes, methods, and interfaces available
- Document your findings BEFORE implementing anything

### 2. Adapter Design
Create a MINIMAL adapter that:
- Implements only functionality related to chat completions
- Uses explicit interfaces derived from library inspection
- Adapts our system's interfaces to the OpenAI library's actual interfaces
- Avoids speculative capabilities or methods not confirmed to exist

### 3. Integration Tests
Create integration tests that:
- Import and use the REAL OpenAI library (not mocks)
- Verify each adapter method correctly calls the corresponding OpenAI API
- Include positive tests that demonstrate correct functionality
- Include negative tests that check proper error handling
- Document which parts of the OpenAI API are supported and which aren't
- Use appropriate test fixtures that work with the real OpenAI library

### 4. Dependency Injection
Follow dependency injection principles:
- Make all dependencies explicit in constructor or method parameters
- Provide clear interface definitions
- Allow for configuration options required by the real OpenAI library
- Separate interface from implementation
```

## Notes for AI Assistant Use

This prompt ensures that:
1. The AI thoroughly examines the actual library API before implementation
2. All integration tests use the real library, not just mocks
3. The adapter only implements functionality that has been verified to exist
4. Interface and implementation concerns are properly separated
