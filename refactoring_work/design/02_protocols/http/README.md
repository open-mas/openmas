# HTTP Protocol Support in OpenMAS

## Overview

The Hypertext Transfer Protocol (HTTP) is a foundational communication protocol for multi-agent systems. OpenMAS provides comprehensive HTTP support while maintaining its core principle of reasoning agnosticism.

**Detailed documentation**: [HTTP Protocol Documentation](./http_protocol.md)

## Protocol Specification

- **Name**: Hypertext Transfer Protocol (HTTP)
- **Version**: HTTP/1.1, HTTP/2
- **Purpose**: RESTful communication between agents and services
- **Transport**: TCP/IP
- **Reasoning Agnosticism**: Complete separation between HTTP communication layer and agent reasoning approaches

## Key Features

### RESTful API Support

OpenMAS implements comprehensive RESTful API capabilities:

- **Standard Methods** - Full support for GET, POST, PUT, DELETE, PATCH
- **Status Codes** - Proper usage of HTTP status codes for responses
- **Content Negotiation** - Support for different content types (JSON, XML, etc.)
- **Headers** - Standardized header usage for metadata
- **Query Parameters** - Structured query parameter handling

### Synchronous Communication

OpenMAS leverages HTTP's synchronous communication model:

- **Request-Response Pattern** - Direct mapping to OpenMAS's request-response pattern
- **Blocking Operations** - Support for synchronous operations when needed
- **Response Handling** - Consistent error and success response formats
- **Timeouts** - Configurable timeouts for all requests

### REST API Design

OpenMAS follows REST API best practices:

- **Resource-Oriented Design** - APIs organized around resources
- **Proper HTTP Method Usage** - Methods matched to operations (GET for retrieval, etc.)
- **Consistent URL Structure** - Predictable URL patterns
- **Versioning** - API versioning strategies
- **Pagination** - Standard pagination for large resource collections

### Authentication and Security

OpenMAS implements HTTP security features:

- **Authentication Methods** - Support for API keys, OAuth2, JWT, and basic auth
- **SSL/TLS** - Secure communication with strong cipher suites
- **CORS Support** - Control over cross-origin requests
- **Rate Limiting** - Protection against abuse
- **Input Validation** - Security against injection attacks

## Protocol Implementation

### HTTP Communicator

OpenMAS provides these HTTP communicator implementations:

```python
# HTTP client communicator
from openmas.protocols.http import HTTPClientCommunicator

client = HTTPClientCommunicator(
    base_url="https://api.example.com",
    headers={
        "User-Agent": "OpenMAS/0.3.0",
        "Accept": "application/json"
    },
    timeout=30  # seconds
)

# HTTP server communicator
from openmas.protocols.http import HTTPServerCommunicator

server = HTTPServerCommunicator(
    host="0.0.0.0",
    port=8080,
    cors_origins=["https://example.com"],
    middleware=[
        logging_middleware,
        auth_middleware
    ]
)
```

### API Route Registration

OpenMAS provides a clean route registration system:

```python
from openmas.protocols.http import route, HTTPServerCommunicator

server = HTTPServerCommunicator(port=8080)

class WeatherAgent(Agent):
    def setup(self):
        # Register HTTP routes
        self.register_routes(server)
    
    @route("GET", "/weather/{city}")
    async def get_weather(self, request):
        city = request.path_params["city"]
        weather_data = await self.fetch_weather(city)
        return {
            "temperature": weather_data["temp"],
            "conditions": weather_data["conditions"],
            "forecast": weather_data["forecast"]
        }
    
    @route("POST", "/alerts/subscribe")
    async def subscribe_alerts(self, request):
        data = await request.json()
        subscription = await self.add_subscription(
            city=data["city"],
            email=data["email"],
            alert_types=data["alert_types"]
        )
        return {"subscription_id": subscription.id}
```

## HTTP with Different Reasoning Approaches

OpenMAS maintains reasoning agnosticism with HTTP by:

- **Interface Abstraction** - HTTP interfaces are independent of reasoning
- **Data Format Neutrality** - Content negotiation supports different formats
- **Message Transformation** - Converting between HTTP requests/responses and reasoning-specific formats

Examples of HTTP with different reasoning types:

### LLM-Based Agents

```python
class LLMWeatherAgent(Agent):
    async def setup(self):
        self.register_routes(server)
    
    @route("POST", "/answer")
    async def answer_question(self, request):
        # Parse request
        data = await request.json()
        question = data["question"]
        
        # LLM reasoning
        response = await self.llm.generate(
            prompt=f"Answer this weather-related question: {question}"
        )
        
        # Return LLM response as HTTP response
        return {
            "answer": response.text,
            "confidence": response.metadata.get("confidence", 0.0)
        }
```

### Rule-Based Agents

```python
class RuleBasedWeatherAgent(Agent):
    async def setup(self):
        self.register_routes(server)
        
        # Define weather forecast rules
        self.rule_engine.add_rules([
            "IF temperature > 30 AND humidity > 70% THEN forecast = 'Hot and humid'",
            "IF temperature > 30 AND humidity < 30% THEN forecast = 'Hot and dry'",
            "IF temperature < 10 AND precipitation > 0 THEN forecast = 'Cold and wet'"
        ])
    
    @route("GET", "/forecast/{city}")
    async def get_forecast(self, request):
        # Get weather data
        city = request.path_params["city"]
        weather_data = await self.fetch_weather_data(city)
        
        # Apply rules to determine forecast
        forecast = self.rule_engine.evaluate(weather_data)
        
        # Return rule-based forecast
        return {
            "city": city,
            "forecast": forecast,
            "data": weather_data
        }
```

## HTTP Protocol Configuration

For HTTP protocol configuration, OpenMAS uses the unified configuration schema. For the complete schema definition, see [Protocol Configuration Schema](/03_configuration/schema/protocols.md).

Key configuration sections:

- **Server Settings** (host, port)
- **Client Settings** (base URL, timeouts)
- **Security Configuration** (TLS, authentication)
- **CORS Settings**
- **Middleware Configuration**

## HTTP Integration with Other Components

HTTP protocol integrates with several OpenMAS components:

1. **Communication Patterns** - HTTP-specific implementations of standard patterns
2. **Agent Capabilities** - Exposing agent capabilities as HTTP endpoints
3. **Security System** - HTTP-specific authentication and authorization
4. **Observability System** - Request logging, metrics collection

## Known Limitations and Future Work

- **Streaming Limitations** - Traditional HTTP has limited streaming capabilities
- **Performance Overhead** - Higher overhead compared to some binary protocols
- **Future Work** - HTTP/3 support planned for future releases
- **GraphQL Integration** - GraphQL support for more flexible API queries
