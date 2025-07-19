# Integration Implementation Guide

This document provides guidance on implementing integrations for OpenMAS, including best practices, implementation patterns, and examples that maintain OpenMAS's principles of reasoning agnosticism and protocol independence.

## Integration Implementation Principles

When implementing integrations for OpenMAS, follow these core principles:

1. **Reasoning Agnosticism** - Integrations must be independent of specific reasoning approaches
2. **Protocol Independence** - Integrations should work across all supported protocols
3. **Clear Interfaces** - Well-defined, consistent interfaces for similar integration types
4. **Error Resilience** - Robust error handling, retry logic, and graceful degradation
5. **Security First** - Secure handling of credentials and sensitive data
6. **Extensibility** - Support for extension and customization

## Integration Implementation Structure

A typical integration implementation consists of:

```
my_integration/
├── __init__.py
├── integration.py       # Main integration implementation
├── config.py            # Configuration schemas
├── adapters/            # Protocol-specific adapters
│   ├── a2a.py
│   └── mcp.py
├── clients/             # Service-specific clients
│   └── api_client.py
└── utils/               # Utility functions
    ├── auth.py
    └── formatting.py
```

## Integration Base Classes

OpenMAS provides base classes for different integration types:

### Base Integration Class

All integrations inherit from `BaseIntegration`:

```python
from openmas.integrations import BaseIntegration

class MyIntegration(BaseIntegration):
    """Custom integration implementation."""
    
    def __init__(self, config):
        super().__init__(config)
        self.integration_type = "my_type"
        self.version = "1.0.0"
        
    async def initialize(self, context):
        """Initialize the integration with the provided context."""
        await super().initialize(context)
        
        # Integration-specific initialization
        self.client = self._create_client()
        
    async def cleanup(self):
        """Clean up resources when integration is shutting down."""
        if self.client:
            await self.client.close()
            
    # Additional integration-specific methods
    async def my_operation(self, *args, **kwargs):
        """Custom operation for this integration."""
        # Implementation
```

### Service Integration Example

For integrating with external services:

```python
from openmas.integrations import ServiceIntegration

class CloudStorageIntegration(ServiceIntegration):
    """Integration with cloud storage providers."""
    
    def __init__(self, config):
        super().__init__(config)
        self.provider = config.get("provider")
        self.region = config.get("region")
        self.bucket = config.get("bucket")
        
    async def initialize(self, context):
        """Initialize the cloud storage integration."""
        await super().initialize(context)
        
        # Create provider-specific client
        if self.provider == "aws":
            self.client = await self._create_aws_client()
        elif self.provider == "azure":
            self.client = await self._create_azure_client()
        elif self.provider == "gcp":
            self.client = await self._create_gcp_client()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
            
    async def upload_file(self, local_path, remote_path, metadata=None):
        """Upload a file to cloud storage."""
        try:
            # Provider-agnostic upload implementation
            return await self._upload_file_with_retry(local_path, remote_path, metadata)
        except Exception as e:
            self.logger.error(f"Error uploading file: {str(e)}")
            raise
            
    async def download_file(self, remote_path, local_path):
        """Download a file from cloud storage."""
        try:
            # Provider-agnostic download implementation
            return await self._download_file_with_retry(remote_path, local_path)
        except Exception as e:
            self.logger.error(f"Error downloading file: {str(e)}")
            raise
            
    # Provider-specific client creation
    async def _create_aws_client(self):
        """Create AWS S3 client."""
        # Implementation
        
    # Retry wrapper for resilience
    async def _upload_file_with_retry(self, local_path, remote_path, metadata):
        """Upload with retry logic."""
        # Implementation
```

### API Integration Example

For integrating with external APIs:

```python
from openmas.integrations import ApiIntegration

class RestApiIntegration(ApiIntegration):
    """Integration with REST APIs."""
    
    def __init__(self, config):
        super().__init__(config)
        self.base_url = config.get("base_url")
        self.version = config.get("version")
        self.headers = config.get("headers", {})
        
    async def initialize(self, context):
        """Initialize the REST API integration."""
        await super().initialize(context)
        
        # Create HTTP client
        self.client = await self._create_http_client()
        
        # Set up authentication
        self.auth_manager = await self._create_auth_manager()
        
    async def request(self, method, endpoint, data=None, params=None, headers=None):
        """Make an API request."""
        # Merge headers
        all_headers = {**self.headers}
        if headers:
            all_headers.update(headers)
            
        # Add authentication headers
        auth_headers = await self.auth_manager.get_auth_headers()
        all_headers.update(auth_headers)
        
        # Construct full URL
        url = self._build_url(endpoint)
        
        # Make request with retry logic
        try:
            return await self._request_with_retry(
                method, url, data, params, all_headers
            )
        except Exception as e:
            self.logger.error(f"API request error: {str(e)}")
            raise
            
    # Helper methods
    def _build_url(self, endpoint):
        """Build full URL from endpoint."""
        # Implementation
        
    async def _request_with_retry(self, method, url, data, params, headers):
        """Make HTTP request with retry logic."""
        # Implementation
```

## Authentication Implementation

Implementing secure authentication:

```python
from openmas.integrations.auth import AuthenticationStrategy

class ApiKeyAuthentication(AuthenticationStrategy):
    """API key authentication strategy."""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key_env = config.get("api_key_env")
        self.header_name = config.get("header_name", "Authorization")
        self.prefix = config.get("prefix", "Bearer")
        
    async def initialize(self, context):
        """Initialize the authentication strategy."""
        await super().initialize(context)
        
        # Get credential manager
        self.credential_manager = context.get_credential_manager()
        
        # Retrieve API key
        self.api_key = await self.credential_manager.get_credential(self.api_key_env)
        if not self.api_key:
            raise ValueError(f"API key not found for env variable: {self.api_key_env}")
            
    async def get_auth_headers(self):
        """Get authentication headers."""
        if self.prefix:
            value = f"{self.prefix} {self.api_key}"
        else:
            value = self.api_key
            
        return {self.header_name: value}
        
    async def refresh_credentials(self):
        """Refresh credentials if needed."""
        # Most API keys don't need refreshing, but this method
        # allows for token refresh in subclasses
        pass
```

## Protocol Adaptation

Adapting integrations for protocol-specific requirements:

```python
from openmas.integrations.adapters import ProtocolAdapter

class A2AIntegrationAdapter(ProtocolAdapter):
    """Adapts integrations for A2A protocol."""
    
    def __init__(self, integration, config):
        super().__init__(integration, config)
        self.message_format = config.get("message_format", "json")
        
    async def adapt_request(self, request):
        """Adapt an integration request for A2A protocol."""
        # Convert generic request to A2A-specific format
        adapted_request = {
            "type": "integration_request",
            "integration_id": self.integration.id,
            "operation": request.get("operation"),
            "parameters": self._format_parameters(request.get("parameters", {})),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "trace_id": request.get("context", {}).get("trace_id")
            }
        }
        
        return adapted_request
        
    async def adapt_response(self, response):
        """Adapt an integration response from A2A protocol."""
        # Convert A2A-specific response to generic format
        adapted_response = {
            "status": "success" if response.get("status_code") == 200 else "error",
            "data": response.get("content"),
            "metadata": response.get("metadata", {})
        }
        
        if "error" in response:
            adapted_response["error"] = response["error"]
            
        return adapted_response
        
    def _format_parameters(self, parameters):
        """Format parameters for A2A protocol."""
        # Implementation
```

## Error Handling

Implementing robust error handling:

```python
from openmas.integrations.errors import IntegrationError

class ApiIntegrationError(IntegrationError):
    """Error in API integration."""
    
    def __init__(self, message, status_code=None, response_body=None, request_info=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.request_info = request_info
        
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "status_code": self.status_code,
            "response_body": self.response_body,
            "request_info": {
                "method": self.request_info.get("method") if self.request_info else None,
                "url": self.request_info.get("url") if self.request_info else None,
            }
        }
```

## Integration Registration

Registering your integration with OpenMAS:

```python
# In your integration package's __init__.py
from openmas.integrations import register_integration
from .integration import MyIntegration

# Register the integration
register_integration("my_integration", MyIntegration)
```

## Testing Integrations

Best practices for testing integrations:

```python
import pytest
from openmas.integrations.testing import IntegrationTestCase

class TestMyIntegration(IntegrationTestCase):
    """Tests for MyIntegration."""
    
    async def setup_integration(self):
        """Set up test integration."""
        config = {
            "type": "my_integration",
            "config": {
                "setting1": "value1",
                "setting2": "value2"
            },
            "authentication": {
                "strategy": "api_key",
                "api_key_env": "TEST_API_KEY"
            }
        }
        
        # Set up mock credentials
        self.set_mock_credential("TEST_API_KEY", "test-api-key-value")
        
        # Create and initialize integration
        integration = await self.create_integration("my_integration", config)
        return integration
        
    async def test_basic_functionality(self):
        """Test basic integration functionality."""
        integration = await self.setup_integration()
        
        # Mock external service responses
        self.mock_http_response(
            "GET", 
            "https://api.example.com/resource",
            status=200,
            json={"data": {"id": 123, "name": "Test"}}
        )
        
        # Test integration method
        result = await integration.get_resource("resource")
        
        # Verify results
        assert result["id"] == 123
        assert result["name"] == "Test"
        
    async def test_error_handling(self):
        """Test integration error handling."""
        integration = await self.setup_integration()
        
        # Mock error response
        self.mock_http_response(
            "GET", 
            "https://api.example.com/resource",
            status=429,
            json={"error": "Rate limit exceeded"}
        )
        
        # Test error handling
        with pytest.raises(ApiIntegrationError) as excinfo:
            await integration.get_resource("resource")
            
        # Verify error details
        assert excinfo.value.status_code == 429
        assert "Rate limit exceeded" in str(excinfo.value)
```

## Reasoning Agnosticism

To maintain OpenMAS's reasoning agnosticism:

1. **Avoid Reasoning Assumptions** - Don't assume specific reasoning approaches in integrations
2. **Data Format Neutrality** - Use reasoning-agnostic data formats for requests and responses
3. **Clean Interfaces** - Integration interfaces should be independent of reasoning strategies
4. **Body vs. Brain Separation** - Maintain clear separation between integration infrastructure (body) and reasoning (brain)

## Protocol Independence

To maintain protocol independence:

1. **Protocol Adapters** - Use protocol adapters for protocol-specific behavior
2. **Common Interfaces** - Implement protocol-independent interfaces for core functionality
3. **Message Translation** - Translate between protocol-specific and generic message formats
4. **Configuration Isolation** - Keep protocol-specific configuration separate from core integration configuration

## Security Best Practices

Always follow these security practices:

1. **Never Hardcode Credentials** - Always retrieve credentials from secure sources
2. **Credential Isolation** - Keep credentials separate from core integration logic
3. **Secure Communication** - Always use secure transport protocols (HTTPS, WSS)
4. **Input Validation** - Validate all inputs to prevent injection attacks
5. **Minimal Permissions** - Use credentials with the minimal required permissions

## Integration Development Workflow

Follow this workflow when developing new integrations:

1. **Define Requirements** - Define the integration's purpose and requirements
2. **Create Configuration Schema** - Define the configuration schema for the integration
3. **Implement Core Logic** - Implement the core integration functionality
4. **Add Protocol Adapters** - Implement protocol-specific adaptations
5. **Implement Error Handling** - Add comprehensive error handling
6. **Write Tests** - Create thorough tests for all functionality
7. **Document Usage** - Document how to use the integration
8. **Register with OpenMAS** - Register the integration with the OpenMAS registry
