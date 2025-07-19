# LLM Extensions

## Overview

LLM Extensions provide a mechanism to integrate various language model providers and inference services with OpenMAS. They enable agents to leverage different AI models while maintaining OpenMAS's reasoning agnosticism and protocol independence.

## Base Class

LLM Extensions must inherit from the `LLMProviderExtension` base class:

```python
from openmas.extensions import LLMProviderExtension

class MyLLMProviderExtension(LLMProviderExtension):
    """A custom LLM provider extension."""
```

## Required Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `generate_completion(prompt, options)` | Generate a completion from the LLM | `prompt`: The prompt to send<br>`options`: Generation options | LLM completion response |
| `generate_embedding(text, options)` | Generate embeddings for text | `text`: The text to embed<br>`options`: Embedding options | Embedding vector |

## Optional Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `validate_config()` | Validate the extension configuration | None | None, raises exception if invalid |
| `initialize()` | Initialize the extension | None | None |
| `get_model_info()` | Get information about available models | None | Dictionary of model metadata |
| `get_token_count(text)` | Count tokens in text | `text`: The text to analyze | Integer token count |
| `stream_completion(prompt, options)` | Stream a completion from the LLM | `prompt`: The prompt to send<br>`options`: Generation options | Async generator of completion chunks |

## Configuration Schema

LLM Extensions are configured in the unified configuration schema under the `extensions` section with `type: "llm_provider"`:

```yaml
extensions:
  my_llm_provider:
    type: "llm_provider"
    name: "my_llm_provider"
    enabled: true
    options:
      api_key: "${MY_LLM_API_KEY}" # Environment variable reference
      base_url: "https://api.llm-provider.com/v1"
      default_model: "my-model-v1"
      timeout_ms: 30000
      cache_enabled: true
      # Additional provider-specific options
```

### Options Schema

The `options` block for LLM Extensions supports the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `api_key` | string | Usually | API key for the LLM provider |
| `base_url` | string | Usually | Base URL for the API endpoint |
| `default_model` | string | Yes | Default model identifier to use |
| `timeout_ms` | integer | No | Request timeout in milliseconds |
| `cache_enabled` | boolean | No | Whether to enable response caching |
| `retry_config` | object | No | Configuration for retrying failed requests |
| `models` | object | No | Model-specific configuration options |

For the complete schema definition, refer to the [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md#llm-provider-extension-options).

## Interaction Model

LLM Extensions interact with the OpenMAS framework through the following mechanisms:

1. **Registration**: The extension is registered with the extension registry
2. **Discovery**: Reasoning engines discover and load the extension during initialization
3. **Inference**: The reasoning engine calls the extension's methods to generate completions or embeddings
4. **Response Handling**: The extension processes the LLM provider's response and returns it in a standardized format
5. **Integration with Reasoning**: The extension's outputs are integrated into the agent's reasoning process

The OpenMAS framework maintains control over when LLM providers are called, while the extension handles the specific integration with external LLM services.

## Code Example

Here's a minimal example of an LLM Extension that integrates with OpenAI's API:

```python
from openmas.extensions import LLMProviderExtension
import aiohttp
import json
import os
import tiktoken
from typing import Dict, List, Any, AsyncGenerator

class OpenAIProviderExtension(LLMProviderExtension):
    """Extension that integrates with OpenAI's API."""
    
    extension_type = "llm_provider"
    extension_name = "openai"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        options = config.get("options", {})
        
        # Extract configuration
        self.api_key = options.get("api_key") or os.environ.get("OPENAI_API_KEY")
        self.base_url = options.get("base_url", "https://api.openai.com/v1")
        self.default_model = options.get("default_model", "gpt-4o")
        self.timeout = options.get("timeout_ms", 30000) / 1000.0  # Convert to seconds
        
        # Set up HTTP session
        self.session = None
        self.encoder = None
    
    async def initialize(self):
        """Initialize the extension."""
        self.session = aiohttp.ClientSession()
        try:
            # Set up tokenizer for the default model
            model_name = "gpt-4" if self.default_model.startswith("gpt-4") else "gpt-3.5-turbo"
            self.encoder = tiktoken.encoding_for_model(model_name)
        except Exception as e:
            self.logger.warning(f"Failed to initialize tokenizer: {e}")
        
        self.initialized = True
    
    def validate_config(self):
        """Validate the extension configuration."""
        if not self.api_key:
            raise ValueError("OpenAI provider requires an API key")
    
    async def generate_completion(self, prompt, options=None):
        """Generate a completion from OpenAI."""
        if not self.initialized:
            await self.initialize()
        
        options = options or {}
        model = options.get("model", self.default_model)
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", 1000)
        
        # Prepare the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Support both string prompts and message arrays
        messages = prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}]
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error ({response.status}): {error_text}")
                
                result = await response.json()
                
                # Extract and return the response
                return {
                    "text": result["choices"][0]["message"]["content"],
                    "model": result["model"],
                    "token_usage": result.get("usage", {})
                }
        except Exception as e:
            self.logger.error(f"Error generating completion: {e}")
            raise
    
    async def stream_completion(self, prompt, options=None):
        """Stream a completion from OpenAI."""
        if not self.initialized:
            await self.initialize()
        
        options = options or {}
        model = options.get("model", self.default_model)
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", 1000)
        
        # Prepare the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Support both string prompts and message arrays
        messages = prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}]
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error ({response.status}): {error_text}")
                
                # Process the streaming response
                buffer = ""
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: ") and not line.startswith("data: [DONE]"):
                        data = line[6:]  # Remove "data: " prefix
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                content = chunk["choices"][0].get("delta", {}).get("content", "")
                                if content:
                                    buffer += content
                                    yield {
                                        "text": content,
                                        "is_complete": False
                                    }
                        except json.JSONDecodeError:
                            pass
                
                # Yield the final complete response
                yield {
                    "text": buffer,
                    "is_complete": True,
                    "model": model
                }
        except Exception as e:
            self.logger.error(f"Error streaming completion: {e}")
            raise
    
    async def generate_embedding(self, text, options=None):
        """Generate embeddings for text."""
        if not self.initialized:
            await self.initialize()
        
        options = options or {}
        model = options.get("embedding_model", "text-embedding-3-small")
        
        # Prepare the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": model,
            "input": text
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=payload,
                timeout=self.timeout
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error ({response.status}): {error_text}")
                
                result = await response.json()
                
                # Extract and return the embeddings
                return {
                    "embedding": result["data"][0]["embedding"],
                    "model": result["model"],
                    "token_usage": result.get("usage", {})
                }
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            raise
    
    def get_token_count(self, text):
        """Count tokens in text."""
        if self.encoder:
            return len(self.encoder.encode(text))
        else:
            # Fallback approximation
            return len(text.split()) * 1.3
    
    def get_model_info(self):
        """Get information about available models."""
        return {
            "models": {
                "gpt-4o": {
                    "description": "GPT-4o model",
                    "max_tokens": 8192,
                    "supports_streaming": True
                },
                "gpt-3.5-turbo": {
                    "description": "GPT-3.5 Turbo model",
                    "max_tokens": 4096,
                    "supports_streaming": True
                },
                "text-embedding-3-small": {
                    "description": "Text embedding model",
                    "embedding_dimensions": 1536
                }
            }
        }
```

### Configuration Example

```yaml
extensions:
  openai:
    type: "llm_provider"
    name: "openai"
    enabled: true
    options:
      api_key: "${OPENAI_API_KEY}"
      default_model: "gpt-4o"
      timeout_ms: 30000
      cache_enabled: true
      models:
        gpt-4o:
          temperature: 0.7
          max_tokens: 1000
        gpt-3.5-turbo:
          temperature: 0.9
          max_tokens: 2000
```

## Best Practices

1. **Secure API Keys**: Never hardcode API keys, use environment variables or secure storage
2. **Error Handling**: Implement robust error handling for API failures
3. **Streaming Support**: When possible, implement streaming for better responsiveness
4. **Efficient Token Usage**: Provide accurate token counting to help manage costs
5. **Cache Responses**: Implement caching for repeated prompts when appropriate
6. **Support Multiple Models**: Allow configuration of different models for different use cases

## Related Documentation

- [Extension System Design](../design/design_extension_system.md)
- [Reasoning System Design](../../08_reasoning/design_reasoning_system.md)
- [Extension Development Guide](../development/guide.md)
- [Knowledge Representation Integration](../../09_knowledge_representation/kr_reasoning_integration.md)
