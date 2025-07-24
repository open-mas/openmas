# Integrations System Setup

## Task Overview
Setup the Integrations system for OpenMAS 0.3.0, which handles external service connections, framework interoperability, and API integrations while maintaining OpenMAS's reasoning-agnostic architecture and multi-protocol capabilities.

## Design Alignment
**Reference**: `/refactoring_work/design/01_architecture/components_summary.md` and `/refactoring_work/design/documentation_structure.md` section `14_integrations/`
**Architecture**: Integrations provide seamless connectivity with external systems, services, and frameworks while preserving the body-brain separation and multi-protocol support.

## Tasks

1. Create Integrations Directory Structure
   - Setup service connection frameworks
   - Create framework interoperability layers
   - Configure API integration utilities

2. Implement Service Integrations
   - External API connectors
   - Database integrations
   - Message queue integrations
   - Cloud service connectors

3. Setup Framework Interoperability
   - Integration with other agent frameworks
   - Protocol bridging capabilities
   - Data format converters
   - Compatibility layers

4. Configure Integration Management
   - Connection pooling and management
   - Authentication and authorization
   - Rate limiting and throttling
   - Error handling and retry mechanisms

## Directory Structure

```
src/openmas/integrations/
├── __init__.py                     # Integrations module initialization
├── services/                       # External service integrations
│   ├── __init__.py
│   ├── apis/                      # API integrations
│   │   ├── __init__.py
│   │   ├── rest_client.py         # REST API client
│   │   ├── graphql_client.py      # GraphQL API client
│   │   ├── webhook_handler.py     # Webhook handling
│   │   └── rate_limiter.py        # API rate limiting
│   ├── databases/                 # Database integrations
│   │   ├── __init__.py
│   │   ├── sql_connector.py       # SQL database connector
│   │   ├── nosql_connector.py     # NoSQL database connector
│   │   ├── vector_db_connector.py # Vector database connector
│   │   └── cache_connector.py     # Cache system connector
│   ├── messaging/                 # Message queue integrations
│   │   ├── __init__.py
│   │   ├── rabbitmq_connector.py  # RabbitMQ integration
│   │   ├── kafka_connector.py     # Apache Kafka integration
│   │   ├── redis_connector.py     # Redis integration
│   │   └── pubsub_connector.py    # Cloud Pub/Sub integration
│   └── cloud/                     # Cloud service integrations
│       ├── __init__.py
│       ├── aws_connector.py       # AWS services integration
│       ├── gcp_connector.py       # Google Cloud integration
│       ├── azure_connector.py     # Azure services integration
│       └── storage_connector.py   # Cloud storage integration
├── frameworks/                     # Framework interoperability
│   ├── __init__.py
│   ├── agent_frameworks/          # Other agent framework integrations
│   │   ├── __init__.py
│   │   ├── jade_bridge.py         # JADE framework bridge
│   │   ├── spade_bridge.py        # SPADE framework bridge
│   │   ├── mesa_bridge.py         # Mesa framework bridge
│   │   └── autogen_bridge.py      # AutoGen framework bridge
│   ├── ml_frameworks/             # ML framework integrations
│   │   ├── __init__.py
│   │   ├── langchain_bridge.py    # LangChain integration
│   │   ├── llamaindex_bridge.py   # LlamaIndex integration
│   │   ├── crewai_bridge.py       # CrewAI integration
│   │   └── semantic_kernel_bridge.py # Semantic Kernel integration
│   └── protocol_bridges/          # Protocol bridging
│       ├── __init__.py
│       ├── protocol_converter.py  # Protocol format conversion
│       ├── message_translator.py  # Message translation
│       └── capability_mapper.py   # Capability mapping
├── adapters/                       # Integration adapters
│   ├── __init__.py
│   ├── data_adapters/             # Data format adapters
│   │   ├── __init__.py
│   │   ├── json_adapter.py        # JSON data adapter
│   │   ├── xml_adapter.py         # XML data adapter
│   │   ├── protobuf_adapter.py    # Protocol Buffers adapter
│   │   └── avro_adapter.py        # Apache Avro adapter
│   ├── auth_adapters/             # Authentication adapters
│   │   ├── __init__.py
│   │   ├── oauth_adapter.py       # OAuth authentication
│   │   ├── jwt_adapter.py         # JWT authentication
│   │   ├── api_key_adapter.py     # API key authentication
│   │   └── saml_adapter.py        # SAML authentication
│   └── transport_adapters/        # Transport adapters
│       ├── __init__.py
│       ├── http_adapter.py        # HTTP transport adapter
│       ├── websocket_adapter.py   # WebSocket transport adapter
│       ├── grpc_adapter.py        # gRPC transport adapter
│       └── tcp_adapter.py         # TCP transport adapter
├── management/                     # Integration management
│   ├── __init__.py
│   ├── connection_pool.py         # Connection pooling
│   ├── health_monitor.py          # Integration health monitoring
│   ├── retry_manager.py           # Retry and circuit breaker
│   └── metrics_collector.py      # Integration metrics
└── utilities/                      # Integration utilities
    ├── __init__.py
    ├── serialization/             # Data serialization utilities
    │   ├── __init__.py
    │   ├── json_serializer.py     # JSON serialization
    │   ├── binary_serializer.py   # Binary serialization
    │   └── custom_serializer.py   # Custom serialization
    ├── validation/                # Integration validation
    │   ├── __init__.py
    │   ├── schema_validator.py    # Schema validation
    │   ├── data_validator.py      # Data validation
    │   └── endpoint_validator.py  # Endpoint validation
    └── testing/                   # Integration testing utilities
        ├── __init__.py
        ├── mock_server.py         # Mock server for testing
        ├── test_fixtures.py       # Test fixtures
        └── integration_tester.py  # Integration testing framework
```

## Key Implementation Files

### 1. Integration Manager (`__init__.py`)

```python
"""
OpenMAS Integrations System - External service and framework connectivity.

Provides seamless integration with external systems while maintaining
OpenMAS's reasoning-agnostic architecture and multi-protocol capabilities.
"""

from typing import Dict, List, Optional, Any
import asyncio
from dataclasses import dataclass
from enum import Enum

from .management.connection_pool import ConnectionPool
from .management.health_monitor import HealthMonitor
from .management.retry_manager import RetryManager

class IntegrationType(Enum):
    """Types of integrations supported."""
    API = "api"
    DATABASE = "database"
    MESSAGING = "messaging"
    CLOUD = "cloud"
    FRAMEWORK = "framework"

@dataclass
class IntegrationConfig:
    """Configuration for an integration."""
    name: str
    integration_type: IntegrationType
    endpoint: str
    authentication: Dict[str, Any]
    settings: Dict[str, Any]
    health_check_url: Optional[str] = None
    retry_config: Optional[Dict[str, Any]] = None

class IntegrationManager:
    """Central manager for all external integrations."""
    
    def __init__(self):
        self._integrations: Dict[str, Any] = {}
        self._connection_pool = ConnectionPool()
        self._health_monitor = HealthMonitor()
        self._retry_manager = RetryManager()
    
    async def register_integration(self, config: IntegrationConfig) -> bool:
        """Register a new integration."""
        try:
            # Create integration instance based on type
            integration = await self._create_integration(config)
            
            # Test connection
            if await self._test_integration(integration, config):
                self._integrations[config.name] = integration
                
                # Start health monitoring if configured
                if config.health_check_url:
                    await self._health_monitor.add_integration(config.name, config.health_check_url)
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Failed to register integration {config.name}: {e}")
            return False
    
    async def get_integration(self, name: str) -> Optional[Any]:
        """Get a registered integration by name."""
        return self._integrations.get(name)
    
    async def list_integrations(self) -> List[str]:
        """List all registered integrations."""
        return list(self._integrations.keys())
    
    async def health_check(self, name: Optional[str] = None) -> Dict[str, bool]:
        """Perform health check on integrations."""
        if name:
            return {name: await self._health_monitor.check_integration(name)}
        else:
            return await self._health_monitor.check_all_integrations()
    
    async def _create_integration(self, config: IntegrationConfig) -> Any:
        """Create integration instance based on configuration."""
        if config.integration_type == IntegrationType.API:
            from .services.apis.rest_client import RestClient
            return RestClient(config.endpoint, config.authentication, config.settings)
        elif config.integration_type == IntegrationType.DATABASE:
            from .services.databases.sql_connector import SqlConnector
            return SqlConnector(config.endpoint, config.authentication, config.settings)
        # Add other integration types...
        else:
            raise ValueError(f"Unsupported integration type: {config.integration_type}")
    
    async def _test_integration(self, integration: Any, config: IntegrationConfig) -> bool:
        """Test integration connectivity."""
        try:
            if hasattr(integration, 'test_connection'):
                return await integration.test_connection()
            return True
        except Exception:
            return False

# Global integration manager instance
integration_manager = IntegrationManager()
```

### 2. REST API Client (`services/apis/rest_client.py`)

```python
"""
REST API client for OpenMAS integrations.

Provides robust REST API connectivity with authentication, rate limiting,
and error handling while supporting OpenMAS's multi-protocol architecture.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
import json
from dataclasses import dataclass

from ...utilities.serialization.json_serializer import JsonSerializer
from ..management.retry_manager import RetryManager

@dataclass
class ApiResponse:
    """Response from API call."""
    status_code: int
    data: Any
    headers: Dict[str, str]
    success: bool

class RestClient:
    """REST API client with OpenMAS integration features."""
    
    def __init__(self, base_url: str, auth_config: Dict[str, Any], settings: Dict[str, Any]):
        self.base_url = base_url.rstrip('/')
        self.auth_config = auth_config
        self.settings = settings
        self.serializer = JsonSerializer()
        self.retry_manager = RetryManager()
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if not self._session:
            timeout = aiohttp.ClientTimeout(total=self.settings.get('timeout', 30))
            self._session = aiohttp.ClientSession(timeout=timeout)
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> ApiResponse:
        """Perform GET request."""
        return await self._request('GET', endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> ApiResponse:
        """Perform POST request."""
        return await self._request('POST', endpoint, json=data)
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> ApiResponse:
        """Perform PUT request."""
        return await self._request('PUT', endpoint, json=data)
    
    async def delete(self, endpoint: str) -> ApiResponse:
        """Perform DELETE request."""
        return await self._request('DELETE', endpoint)
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> ApiResponse:
        """Perform HTTP request with retry logic."""
        await self._ensure_session()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._build_headers()
        
        # Add authentication headers
        headers.update(self._get_auth_headers())
        
        async def _make_request():
            async with self._session.request(method, url, headers=headers, **kwargs) as response:
                try:
                    if response.content_type == 'application/json':
                        data = await response.json()
                    else:
                        data = await response.text()
                except Exception:
                    data = None
                
                return ApiResponse(
                    status_code=response.status,
                    data=data,
                    headers=dict(response.headers),
                    success=200 <= response.status < 300
                )
        
        # Use retry manager for resilient requests
        return await self.retry_manager.execute_with_retry(_make_request)
    
    def _build_headers(self) -> Dict[str, str]:
        """Build default headers."""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'OpenMAS-Integration-Client/0.3.0'
        }
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on configuration."""
        auth_type = self.auth_config.get('type', 'none')
        
        if auth_type == 'bearer':
            token = self.auth_config.get('token')
            return {'Authorization': f'Bearer {token}'}
        elif auth_type == 'api_key':
            key = self.auth_config.get('key')
            header_name = self.auth_config.get('header', 'X-API-Key')
            return {header_name: key}
        elif auth_type == 'basic':
            import base64
            username = self.auth_config.get('username')
            password = self.auth_config.get('password')
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            return {'Authorization': f'Basic {credentials}'}
        
        return {}
    
    async def test_connection(self) -> bool:
        """Test API connectivity."""
        try:
            health_endpoint = self.settings.get('health_endpoint', '/health')
            response = await self.get(health_endpoint)
            return response.success
        except Exception:
            return False
```

## Integration with Other Components

### 1. Protocol Integration

Integrations work with protocols through:

- **A2A Protocol**: External services exposed as agent capabilities
- **MCP Protocol**: External APIs exposed as MCP resources and tools
- **HTTP Protocol**: Direct HTTP integration for web services
- **Message Protocols**: Integration with message queues and event systems

### 2. Reasoning Engine Integration

Integrations support reasoning engines through:

- **Knowledge Sources**: External knowledge bases and APIs
- **Tool Integration**: External tools and services as reasoning capabilities
- **Data Sources**: External data feeds for reasoning engines
- **Model Services**: External AI/ML model services

## Configuration Integration

Integrations should be configured through the unified configuration schema:

```yaml
integrations:
  services:
    external_api:
      type: "api"
      endpoint: "https://api.example.com"
      authentication:
        type: "bearer"
        token: "${API_TOKEN}"
      settings:
        timeout: 30
        rate_limit: 100
        health_endpoint: "/health"
    vector_database:
      type: "database"
      endpoint: "postgresql://localhost:5432/vectors"
      authentication:
        type: "basic"
        username: "${DB_USER}"
        password: "${DB_PASS}"
  frameworks:
    langchain:
      enabled: true
      bridge_protocols: ["a2a", "mcp"]
      settings:
        chain_timeout: 60
  management:
    connection_pool:
      max_connections: 100
      idle_timeout: 300
    health_monitoring:
      check_interval: 60
      failure_threshold: 3
    retry_policy:
      max_attempts: 3
      backoff_factor: 2
```

## Success Criteria
- Complete Integrations directory structure created
- Service integration clients implemented (API, Database, Messaging, Cloud)
- Framework interoperability bridges functional
- Integration management system operational
- Authentication and authorization adapters working
- Health monitoring and retry mechanisms active
- Configuration schema alignment maintained
- Protocol and reasoning engine integration established
