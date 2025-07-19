# HTTP Protocol

## Protocol Definition

- **Name**: Hypertext Transfer Protocol (HTTP)
- **Purpose**: RESTful communication between agents and services
- **Specification Reference**: [HTTP/1.1 RFC 7230-7235](https://tools.ietf.org/html/rfc7230), [HTTP/2 RFC 7540](https://tools.ietf.org/html/rfc7540)
- **OpenMAS Implementation Status**: Fully Supported
- **Reasoning Agnosticism**: Complete separation between HTTP communication layer and agent reasoning approaches
- **Protocol Independence**: Can interoperate with other protocols through OpenMAS protocol adapters

## Protocol Overview

HTTP (Hypertext Transfer Protocol) is the foundation of data communication on the web, providing a standardized way for agents and services to communicate. OpenMAS leverages HTTP's ubiquity and mature ecosystem to enable agent communication through RESTful APIs and web services.

OpenMAS implements HTTP as a first-class protocol, maintaining the framework's core principle of reasoning agnosticism. This allows agents with different reasoning approaches (rule-based, BDI, LLM-based, etc.) to communicate effectively through HTTP while preserving the clean separation between the communication layer ("body") and reasoning layer ("brain").

## Protocol Features

### Core Features

1. **RESTful API Support**
   - Full support for standard HTTP methods (GET, POST, PUT, DELETE, PATCH)
   - Proper usage of HTTP status codes for responses
   - Content negotiation for different formats (JSON, XML, etc.)
   - Standardized header usage for metadata
   - Structured query parameter handling

2. **Synchronous Communication**
   - Request-response pattern implementation
   - Timeout handling and retry mechanisms
   - Error handling with appropriate status codes
   - Correlation ID tracking for request tracing
   - Response caching and conditional requests

3. **Server-Side Events (SSE)**
   - Push-based server-to-client communication
   - Event streaming for real-time updates
   - Reconnection handling
   - Event filtering and categorization
   - Heartbeat mechanism for connection maintenance

### Extended Features

OpenMAS extends HTTP with additional features for agent communication:

1. **Enhanced Security**
   - OAuth 2.0 and OpenID Connect integration
   - API key management and rotation
   - Request signing and verification
   - CORS configuration for web clients
   - Content Security Policy implementation

2. **Protocol Bridging**
   - Translation between HTTP and other protocols (A2A, MCP, etc.)
   - RESTful endpoint mapping to agent capabilities
   - Request/response transformation between protocols
   - Content-type negotiation and conversion

3. **Agent-Specific Extensions**
   - Capability advertisement through HTTP endpoints
   - Service discovery mechanisms
   - Health check endpoints
   - Metrics and monitoring endpoints
   - Documentation endpoints (OpenAPI/Swagger)

## OpenMAS Implementation

### Architecture Integration

The HTTP protocol implementation in OpenMAS integrates with the core components as follows:

1. **Agent Framework**: HTTP endpoints map to agent capabilities, with the framework handling the translation
2. **Capability System**: Agent capabilities are exposed as HTTP endpoints with proper path and method mapping
3. **Configuration System**: HTTP options are configured through the unified schema
4. **Security System**: HTTP authentication integrates with OpenMAS's security framework

#### Component Interactions

```
┌────────────────┐      ┌─────────────────┐      ┌────────────────┐
│  Agent (Brain) │      │ OpenMAS Core    │      │ HTTP Server/   │
│                │◄────►│                 │◄────►│ Client         │
└────────────────┘      └─────────────────┘      └────────────────┘
                              │                         │
                              │                         │
                        ┌─────▼─────┐             ┌─────▼─────┐
                        │ Route     │             │ External  │
                        │ Registry  │             │ Services  │
                        └───────────┘             └───────────┘
```

### Configuration

The HTTP protocol is configured through the unified configuration schema.

For complete schema information, refer to the [Protocol Configuration Schema](/03_configuration/schema/protocols.md#http-protocol-configuration).

Example minimal configuration:

```yaml
protocols:
  - type: "http"
    enabled: true
    options:
      port: 8080
      timeout_ms: 30000
      headers:
        User-Agent: "OpenMAS/0.3.0"
        Accept: "application/json"
      cors_origins:
        - "https://example.com"
      middleware:
        - "cors"
        - "json_body_parser"
        - "authentication"
```

## Message Structure

### Request Format

A typical HTTP request in OpenMAS:

```
GET /weather?location=san-francisco HTTP/1.1
Host: agent-api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
User-Agent: OpenMAS/0.3.0
```

JSON body for POST requests:

```json
{
  "query": "weather forecast",
  "location": "San Francisco",
  "units": "celsius",
  "include_details": true
}
```

### Response Format

A typical HTTP response in OpenMAS:

```
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: req-123
Date: Mon, 19 May 2025 01:32:54 GMT

{
  "temperature": 22,
  "conditions": "Sunny",
  "humidity": 65,
  "forecast": [
    {"day": "Monday", "high": 24, "low": 18, "conditions": "Clear"},
    {"day": "Tuesday", "high": 26, "low": 19, "conditions": "Partly cloudy"}
  ]
}
```

### Error Handling

HTTP error response:

```
HTTP/1.1 400 Bad Request
Content-Type: application/json
X-Request-ID: req-123
Date: Mon, 19 May 2025 01:32:54 GMT

{
  "error": {
    "code": "invalid_parameter",
    "message": "The location parameter is required",
    "details": {
      "parameter": "location"
    }
  },
  "request_id": "req-123"
}
```

## Communication Patterns

The HTTP protocol in OpenMAS implements several standard communication patterns:

1. **Request-Response**: Standard HTTP request with response
2. **Server-Sent Events**: Server-to-client push notifications
3. **Webhooks**: Event notifications via HTTP callbacks
4. **Long Polling**: Extended request-response for near real-time updates

For detailed documentation on communication patterns, see:
- [Protocol Communication Patterns](/07_communication_patterns/protocol_patterns.md)
- [Protocol Adaptations](/07_communication_patterns/protocol_adaptations.md)

## Security Considerations

1. **Authentication**
   - JWT token-based authentication
   - API key authentication
   - OAuth 2.0 integration
   - Session-based authentication
   - Basic and digest authentication

2. **Authorization**
   - Role-based access control
   - Path-based permissions
   - Method-based restrictions
   - Scoped access tokens
   - Rate limiting and throttling

3. **Data Protection**
   - TLS encryption for all communications
   - Request/response validation
   - Content Security Policy
   - CSRF protection
   - Secure cookie handling

## Usage Examples

### Example 1: HTTP Server Implementation

```python
# HTTP server implementation in an agent
from openmas.protocols.http import HTTPServer
from openmas.agents import Agent

class WeatherAgent(Agent):
    async def setup(self):
        # Initialize HTTP server
        self.http_server = await self.setup_protocol("http", {
            "port": 8080,
            "cors_origins": ["https://example.com"]
        })
        
        # Register routes
        self.http_server.route("GET", "/weather/{location}", self.get_weather)
        self.http_server.route("POST", "/forecast", self.get_forecast)
    
    async def get_weather(self, request):
        location = request.path_params.get("location")
        units = request.query_params.get("units", "celsius")
        
        # Get weather data
        weather_data = await self.weather_service.get_current(location, units)
        
        # Return as HTTP response
        return {
            "status": 200,
            "content_type": "application/json",
            "body": weather_data
        }
    
    async def get_forecast(self, request):
        data = await request.json()
        location = data.get("location")
        days = data.get("days", 5)
        
        # Get forecast data
        forecast = await self.weather_service.get_forecast(location, days)
        
        # Return as HTTP response
        return {
            "status": 200,
            "content_type": "application/json",
            "body": forecast
        }
```

### Example 2: HTTP Client Implementation

```python
# HTTP client implementation in an agent
from openmas.protocols.http import HTTPClient
from openmas.agents import Agent

class ClientAgent(Agent):
    async def setup(self):
        # Initialize HTTP client
        self.http_client = await self.setup_protocol("http", {
            "base_url": "https://weather-api.example.com",
            "headers": {
                "Authorization": f"Bearer {self.config.api_key}",
                "Accept": "application/json"
            },
            "timeout_ms": 5000
        })
    
    async def get_weather(self, location):
        # Make HTTP GET request
        response = await self.http_client.get(
            f"/weather/{location}",
            params={"units": "celsius"}
        )
        
        # Check status and return data
        if response.status == 200:
            return response.json()
        else:
            self.log.error(f"Failed to get weather: {response.text}")
            raise Exception(f"Weather API error: {response.status}")
    
    async def submit_feedback(self, feedback_data):
        # Make HTTP POST request
        response = await self.http_client.post(
            "/feedback",
            json=feedback_data
        )
        
        return response.status == 201
```

## Interoperability

### Protocol Bridging

OpenMAS provides bidirectional bridging between HTTP and other protocols:

1. **HTTP ↔ A2A**: RESTful endpoints mapped to A2A capabilities
2. **HTTP ↔ MCP**: HTTP endpoints mapped to MCP tools
3. **HTTP ↔ gRPC**: HTTP/JSON to gRPC/Protobuf conversion
4. **HTTP ↔ MQTT**: Webhook-to-topic translation

### External Systems Integration

HTTP in OpenMAS can integrate with:

1. **Web APIs**: Seamless integration with any HTTP-based API
2. **Legacy Systems**: Integration with existing HTTP services
3. **Cloud Services**: Connection to cloud provider APIs
4. **IoT Platforms**: HTTP-based IoT device management

## Performance Considerations

1. **Scalability**
   - Connection pooling for client operations
   - Load balancing for server operations
   - Horizontal scaling for increased throughput
   - Efficient route matching for high-volume endpoints

2. **Efficiency**
   - Response compression
   - Conditional requests (ETags, If-Modified-Since)
   - Connection keep-alive
   - Response caching
   - JSON serialization optimization

## Protocol Limitations

1. **Statelessness**: HTTP's stateless nature requires additional mechanisms for maintaining session state
2. **Overhead**: HTTP headers add overhead compared to some binary protocols
3. **Bidirectional Communication**: Limited options for server-initiated communication (requires SSE or webhooks)
4. **Binary Data**: Less efficient for large binary data transfers than specialized protocols

## Future Roadmap

1. **HTTP/3 Support**: Implementation of the newer HTTP/3 protocol for improved performance
2. **GraphQL Integration**: Enhanced support for GraphQL APIs alongside REST
3. **WebHook Management**: Advanced webhook registration and management
4. **API Gateway Features**: Implementation of API gateway patterns

## Related Documentation

- [Protocol Schema Documentation](/03_configuration/schema/protocols.md#http-protocol-configuration)
- [Communication Patterns](/07_communication_patterns/protocol_patterns.md)
- [Protocol Adaptations](/07_communication_patterns/protocol_adaptations.md)
- [HTTP Security Configuration](/03_configuration/security_configuration.md#http-protocol-security)
