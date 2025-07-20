# Adapter Test Strategy Prompt

Use this prompt to guide AI assistants in creating comprehensive test suites for adapter classes that follow the adapter pattern to integrate external libraries into OpenMAS.

## Prompt Template

```
I need to develop a test strategy for the [ADAPTER_NAME] adapter class which integrates [EXTERNAL_SYSTEM] with OpenMAS. The strategy should include both unit tests and integration tests.

## Adapter Description
[BRIEF_DESCRIPTION_OF_ADAPTER]

## Adapter Interface
```python
[ADAPTER_INTERFACE_CODE]
```

## Adapter Implementation
```python
[ADAPTER_IMPLEMENTATION_CODE]
```

## Test Strategy Requirements

### 1. Unit Test Strategy
Create unit tests that:
- Test the adapter in isolation from the external system
- Use clear, explicit mocks for the external system
- Verify the adapter's transformation and mapping logic
- Test error handling and edge cases
- Validate that the adapter correctly implements its interface

### 2. Integration Test Strategy
Create integration tests that:
- Test the adapter with the REAL external system
- Verify that the adapter correctly interacts with the actual external API
- Test all supported operations against the real implementation
- Include error handling scenarios that might occur in real usage
- Document prerequisites and setup required for running these tests

### 3. Test Fixture Strategy
Develop fixtures that enable:
- Easy switching between mocked and real implementations
- Realistic test data generation
- Proper cleanup of test resources
- Clear distinction between unit and integration test scenarios

## External System Verification
Before implementing tests:
1. Verify the actual API of [EXTERNAL_SYSTEM] version [VERSION]:
   - Document the verified API endpoints, methods, and classes
   - Note any discrepancies between documentation and actual implementation
   - Identify configuration requirements for the real implementation

2. Decide which aspects to test with real implementation vs. mocks:
   | Feature | Test with Real Implementation | Test with Mocks | Justification |
   |---------|-------------------------------|-----------------|---------------|
   | [FEATURE_1] | Yes/No | Yes/No | [JUSTIFICATION] |
   | [FEATURE_2] | Yes/No | Yes/No | [JUSTIFICATION] |

## Expected Output
Please provide:
1. Complete unit test code using mocks
2. Complete integration test code using real implementations
3. Test fixtures that support both testing approaches
4. Documentation of the external system verification
5. Instructions for setting up and running the tests
```

## How to Use

1. Replace placeholders with specific information:
   - `[ADAPTER_NAME]`: The name of the adapter class
   - `[EXTERNAL_SYSTEM]`: The external system or library being adapted
   - `[BRIEF_DESCRIPTION_OF_ADAPTER]`: A concise description of the adapter's purpose
   - `[ADAPTER_INTERFACE_CODE]`: The interface definition that the adapter implements
   - `[ADAPTER_IMPLEMENTATION_CODE]`: The actual adapter implementation code
   - `[VERSION]`: The version of the external system being integrated
   - `[FEATURE_1]`, etc.: Features or methods provided by the adapter

2. Provide this prompt to the AI assistant.

3. Review the output for:
   - Clear separation between unit and integration tests
   - Proper verification of the external system API
   - Realistic test scenarios for both approaches
   - Documentation of prerequisites for integration tests

## Example

```
I need to develop a test strategy for the OpenAIAdapter adapter class which integrates OpenAI API with OpenMAS. The strategy should include both unit tests and integration tests.

## Adapter Description
The OpenAIAdapter provides a standardized interface for OpenMAS to use OpenAI's language models, handling authentication, request formatting, response parsing, and error handling.

## Adapter Interface
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMProviderInterface(ABC):
    """Interface for language model providers."""

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7
    ) -> str:
        """Generate text completion."""
        pass

    @abstractmethod
    async def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 100,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate chat completion."""
        pass
```

## Adapter Implementation
```python
import openai
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from .interfaces import LLMProviderInterface
from .exceptions import LLMProviderError

class OpenAIAdapter(LLMProviderInterface):
    """Adapter for OpenAI API."""

    def __init__(self, api_key: str, organization_id: Optional[str] = None):
        """Initialize the OpenAI adapter."""
        self.client = AsyncOpenAI(api_key=api_key, organization=organization_id)

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7
    ) -> str:
        """Generate text completion using OpenAI."""
        try:
            response = await self.client.completions.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].text.strip()
        except Exception as e:
            raise LLMProviderError(f"OpenAI text generation failed: {str(e)}")

    async def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 100,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate chat completion using OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            raise LLMProviderError(f"OpenAI chat generation failed: {str(e)}")
```

## External System Verification
Before implementing tests:
1. Verify the actual API of OpenAI version 1.5.0:
   - Document the verified API endpoints, methods, and classes
   - Note any discrepancies between documentation and actual implementation
   - Identify configuration requirements for the real implementation

2. Decide which aspects to test with real implementation vs. mocks:
   | Feature | Test with Real Implementation | Test with Mocks | Justification |
   |---------|-------------------------------|-----------------|---------------|
   | generate_text | Yes | Yes | Critical functionality, needs both unit tests for edge cases and real implementation to verify correct API usage |
   | generate_chat_response | Yes | Yes | Primary feature, needs both unit tests for error handling and real implementation tests for response mapping |
   | Authentication | No | Yes | Sensitive credential handling is better tested with mocks to avoid exposing API keys |
```

## Notes for AI Assistant Use

This prompt ensures that:
1. Both unit tests (with mocks) and integration tests (with real implementations) are created
2. The actual external system API is verified before test implementation
3. A clear strategy is defined for which features to test with real implementations vs. mocks
4. Test fixtures support both testing approaches
5. Prerequisites for running integration tests are clearly documented
