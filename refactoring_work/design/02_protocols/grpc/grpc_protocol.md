# gRPC Protocol

## Protocol Definition

- **Name**: gRPC (Remote Procedure Call)
- **Purpose**: High-performance, language-agnostic RPC framework
- **Specification Reference**: [gRPC Specification](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md)
- **OpenMAS Implementation Status**: Fully Supported
- **Reasoning Agnosticism**: Complete separation between gRPC communication layer and agent reasoning approaches
- **Protocol Independence**: Can interoperate with other protocols through OpenMAS protocol adapters

## Protocol Overview

gRPC is a modern, high-performance Remote Procedure Call (RPC) framework that can run in any environment. It uses Protocol Buffers as the Interface Definition Language (IDL) for service definitions and enables efficient binary serialization. The framework uses HTTP/2 for transport, providing features like bidirectional streaming and flow control.

OpenMAS implements gRPC as a first-class protocol, maintaining the framework's core principle of reasoning agnosticism. This allows agents with different reasoning approaches to communicate efficiently through well-defined service interfaces while preserving the clean separation between the communication layer ("body") and reasoning layer ("brain").

## Protocol Features

### Core Features

1. **Service Definition**
   - Protocol Buffer-based service definitions
   - Strong typing with schema enforcement
   - Code generation for multiple languages
   - Interface versioning support
   - Documentation integration

2. **Binary Serialization**
   - Compact binary wire format
   - Schema-based serialization
   - Efficient encoding/decoding
   - Type safety across language boundaries
   - Backward compatibility support

3. **Bidirectional Streaming**
   - Unary RPC (request-response)
   - Server streaming RPC
   - Client streaming RPC
   - Bidirectional streaming RPC
   - Flow control and backpressure management

### Extended Features

OpenMAS extends gRPC with additional features for agent communication:

1. **Enhanced Security**
   - TLS with mutual authentication
   - Token-based authentication
   - Fine-grained authorization
   - Interceptor-based security
   - Secure credential management

2. **Protocol Bridging**
   - Translation between gRPC and other protocols
   - Service-to-capability mapping
   - Message format conversion
   - Streaming adaptation
   - Cross-protocol error handling

3. **Agent-Specific Extensions**
   - Dynamic service discovery
   - Health checking and monitoring
   - Load balancing strategies
   - Circuit breaking
   - Retry policies

## OpenMAS Implementation

### Architecture Integration

The gRPC protocol implementation in OpenMAS integrates with the core components as follows:

1. **Agent Framework**: gRPC services map to agent capabilities, with automated service generation
2. **Capability System**: Agent capabilities are exposed as gRPC services with proper method mapping
3. **Configuration System**: gRPC options are configured through the unified schema
4. **Security System**: gRPC authentication and authorization integrate with OpenMAS's security framework

#### Component Interactions

```
┌────────────────┐      ┌─────────────────┐      ┌────────────────┐
│  Agent (Brain) │      │ OpenMAS Core    │      │ gRPC Server/   │
│                │◄────►│                 │◄────►│ Client         │
└────────────────┘      └─────────────────┘      └────────────────┘
                              │                         │
                              │                         │
                        ┌─────▼─────┐             ┌─────▼─────┐
                        │ Service   │             │ Proto     │
                        │ Registry  │             │ Files     │
                        └───────────┘             └───────────┘
```

### Configuration

The gRPC protocol is configured through the unified configuration schema.

For complete schema information, refer to the [Protocol Configuration Schema](/03_configuration/schema/protocols.md#grpc-protocol-configuration).

Example minimal configuration:

```yaml
protocols:
  - type: "grpc"
    enabled: true
    options:
      grpc_port: 50051
      max_message_size: 10485760  # 10MB
      service_definitions:
        - "services/agent_service.proto"
```

### Proto File Example

A typical proto file for an OpenMAS agent service:

```protobuf
syntax = "proto3";

package openmas.agents;

service WeatherService {
  // Get current weather conditions for a location
  rpc GetCurrentWeather (WeatherRequest) returns (WeatherResponse) {}
  
  // Subscribe to weather updates for a location
  rpc SubscribeToWeatherUpdates (WeatherRequest) returns (stream WeatherResponse) {}
  
  // Report weather observations from the field
  rpc ReportWeatherObservation (stream ObservationRequest) returns (ObservationResponse) {}
  
  // Interactive weather conversation
  rpc WeatherChat (stream ChatMessage) returns (stream ChatMessage) {}
}

message WeatherRequest {
  string location = 1;
  string units = 2;  // celsius, fahrenheit
  bool include_forecast = 3;
  int32 forecast_days = 4;
}

message WeatherResponse {
  string location = 1;
  double temperature = 2;
  double humidity = 3;
  string conditions = 4;
  repeated ForecastDay forecast = 5;
  string error_message = 6;
}

message ForecastDay {
  string date = 1;
  double high_temperature = 2;
  double low_temperature = 3;
  string conditions = 4;
}

message ObservationRequest {
  string location = 1;
  double temperature = 2;
  double humidity = 3;
  string conditions = 4;
  string observer_id = 5;
  string timestamp = 6;
}

message ObservationResponse {
  bool success = 1;
  string message = 2;
  string observation_id = 3;
}

message ChatMessage {
  string text = 1;
  string sender = 2;
  string timestamp = 3;
  map<string, string> metadata = 4;
}
```

## Message Structure

### Request-Response Format

gRPC messages in OpenMAS are defined using Protocol Buffers. Each message type has a specific structure based on its purpose.

Example of a unary RPC request in binary format (shown in hex representation):

```
00 00 00 00 0A 0B 73 61 6E 2D 66 72 61 6E 63 69 73 63 6F 12 08 63 65 6C 73 69 75 73 18 01 20 03
```

This corresponds to a `WeatherRequest` with:
- location: "san-francisco"
- units: "celsius"
- include_forecast: true
- forecast_days: 3

### Streaming Format

Streaming gRPC in OpenMAS follows the HTTP/2 framing protocol. For server streaming, multiple response messages are sent for a single request:

```
[Initial Response]
{location: "San Francisco", temperature: 22.5, humidity: 65, conditions: "Sunny"}

[Stream Update 1]
{location: "San Francisco", temperature: 23.0, humidity: 64, conditions: "Sunny"}

[Stream Update 2]
{location: "San Francisco", temperature: 23.2, humidity: 63, conditions: "Sunny"}
```

### Error Handling

gRPC error responses use status codes and descriptive messages:

```
Status Code: 3 (INVALID_ARGUMENT)
Message: "Invalid location parameter: Location 'unknown-city' not found"
Details: [
  {"@type":"openmas.ErrorDetails","field":"location","reason":"not_found"}
]
```

OpenMAS maps these gRPC status codes to appropriate application-level errors and provides detailed context for debugging and error recovery.

## Communication Patterns

The gRPC protocol in OpenMAS implements four standard communication patterns:

1. **Unary RPC**: Single request, single response
   ```
   client.GetCurrentWeather(request) → server → single response
   ```

2. **Server Streaming RPC**: Single request, stream of responses
   ```
   client.SubscribeToWeatherUpdates(request) → server → stream of responses
   ```

3. **Client Streaming RPC**: Stream of requests, single response
   ```
   client.ReportWeatherObservation(stream of requests) → server → single response
   ```

4. **Bidirectional Streaming RPC**: Stream of requests, stream of responses
   ```
   client.WeatherChat(stream of messages) ↔ server ↔ stream of responses
   ```

For detailed documentation on communication patterns, see:
- [Protocol Communication Patterns](/07_communication_patterns/protocol_patterns.md)
- [Protocol Adaptations](/07_communication_patterns/protocol_adaptations.md)

## Security Considerations

1. **Authentication**
   - TLS/SSL with certificate validation
   - Token-based authentication
   - OAuth 2.0 integration
   - Custom credential providers
   - Call credentials propagation

2. **Authorization**
   - Method-level access control
   - Interceptor-based authorization
   - Role-based permissions
   - Per-service security policies
   - Authorization metadata

3. **Data Protection**
   - TLS encryption for all communications
   - Message-level encryption for sensitive data
   - Input validation and sanitization
   - Rate limiting and DoS protection
   - Secure credential storage

## Usage Examples

### Example 1: gRPC Server Implementation

```python
# gRPC server implementation in an agent
from openmas.protocols.grpc import GRPCServer
from openmas.agents import Agent
from openmas.utils import proto_utils

class WeatherServiceAgent(Agent):
    async def setup(self):
        # Initialize gRPC server
        self.grpc_server = await self.setup_protocol("grpc", {
            "grpc_port": 50051,
            "max_message_size": 10485760,  # 10MB
            "service_definitions": ["services/weather_service.proto"]
        })
        
        # Register service implementations
        self.grpc_server.register_service(
            "openmas.agents.WeatherService",
            self.get_service_implementation()
        )
        
    def get_service_implementation(self):
        return {
            "GetCurrentWeather": self.get_current_weather,
            "SubscribeToWeatherUpdates": self.subscribe_to_weather_updates,
            "ReportWeatherObservation": self.report_weather_observation,
            "WeatherChat": self.weather_chat
        }
    
    async def get_current_weather(self, request, context):
        # Extract parameters
        location = request.location
        units = request.units
        
        try:
            # Get weather data
            weather_data = await self.weather_service.get_current(location, units)
            
            # Create response
            return proto_utils.create_message("WeatherResponse", {
                "location": location,
                "temperature": weather_data.get("temperature"),
                "humidity": weather_data.get("humidity"),
                "conditions": weather_data.get("conditions"),
                "forecast": [] if not request.include_forecast else [
                    {
                        "date": day.get("date"),
                        "high_temperature": day.get("high"),
                        "low_temperature": day.get("low"),
                        "conditions": day.get("conditions")
                    } for day in weather_data.get("forecast", [])
                ]
            })
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return proto_utils.create_message("WeatherResponse", {
                "location": location,
                "error_message": str(e)
            })
    
    async def subscribe_to_weather_updates(self, request, context):
        # Server streaming implementation
        location = request.location
        units = request.units
        
        # Set up subscription
        subscription = await self.weather_service.subscribe(location, units)
        
        try:
            # Stream updates as they arrive
            async for update in subscription:
                if await context.is_active():
                    yield proto_utils.create_message("WeatherResponse", {
                        "location": location,
                        "temperature": update.get("temperature"),
                        "humidity": update.get("humidity"),
                        "conditions": update.get("conditions")
                    })
                else:
                    break
        finally:
            # Clean up subscription
            await subscription.cancel()
```

### Example 2: gRPC Client Implementation

```python
# gRPC client implementation in an agent
from openmas.protocols.grpc import GRPCClient
from openmas.agents import Agent

class WeatherClientAgent(Agent):
    async def setup(self):
        # Initialize gRPC client
        self.grpc_client = await self.setup_protocol("grpc", {
            "service_definitions": ["services/weather_service.proto"],
            "server_address": "weather-service-agent:50051"
        })
        
        # Create stub for the weather service
        self.weather_stub = self.grpc_client.get_stub("openmas.agents.WeatherService")
    
    async def get_weather_for_location(self, location):
        # Create request message
        request = await self.grpc_client.create_message("WeatherRequest", {
            "location": location,
            "units": "celsius",
            "include_forecast": True,
            "forecast_days": 5
        })
        
        try:
            # Make the gRPC call
            response = await self.weather_stub.GetCurrentWeather(request)
            
            # Process response
            weather_info = {
                "location": response.location,
                "temperature": response.temperature,
                "humidity": response.humidity,
                "conditions": response.conditions,
                "forecast": [{
                    "date": day.date,
                    "high": day.high_temperature,
                    "low": day.low_temperature,
                    "conditions": day.conditions
                } for day in response.forecast]
            }
            
            return weather_info
        except grpc.RpcError as e:
            self.log.error(f"gRPC error: {e.code()}: {e.details()}")
            raise
    
    async def subscribe_to_weather_updates(self, location):
        # Create request message
        request = await self.grpc_client.create_message("WeatherRequest", {
            "location": location,
            "units": "celsius"
        })
        
        # Subscribe to streaming updates
        stream = self.weather_stub.SubscribeToWeatherUpdates(request)
        
        # Process streamed responses
        async for response in stream:
            # Process each update
            update = {
                "location": response.location,
                "temperature": response.temperature,
                "humidity": response.humidity,
                "conditions": response.conditions
            }
            
            # Handle the update
            await self.process_weather_update(update)
```

## Interoperability

### Protocol Bridging

OpenMAS provides bidirectional bridging between gRPC and other protocols:

1. **gRPC ↔ HTTP/REST**: Automatic REST API generation from gRPC service definitions
2. **gRPC ↔ A2A**: gRPC services mapped to A2A capabilities
3. **gRPC ↔ MCP**: gRPC methods mapped to MCP tools
4. **gRPC ↔ MQTT**: Event streaming via MQTT mapped to gRPC streams

### External Systems Integration

gRPC in OpenMAS can integrate with:

1. **External gRPC Services**: Seamless integration with any gRPC service
2. **Cloud gRPC APIs**: Connection to cloud provider gRPC APIs
3. **IDL-Based Systems**: Integration with any system using Protocol Buffers
4. **Legacy Systems**: gRPC-Web and gRPC gateway for legacy compatibility

## Performance Considerations

1. **Scalability**
   - Load balancing for high-volume services
   - Connection pooling for efficient resource usage
   - Health checking and service discovery
   - Graceful shutdown and restart

2. **Efficiency**
   - Binary protocol with minimal overhead
   - Multiplexed connections via HTTP/2
   - Streaming for reduced latency
   - Message compression
   - Connection sharing

## Protocol Limitations

1. **Browser Support**: Limited native browser support (requires gRPC-Web)
2. **Debugging**: Binary format makes debugging more difficult than text-based protocols
3. **Schema Evolution**: Requires careful management of backward compatibility
4. **Connection Management**: More complex connection handling compared to stateless protocols

## Future Roadmap

1. **Service Reflection**: Enhanced runtime service discovery and reflection
2. **Streaming Optimizations**: Advanced backpressure and flow control
3. **Enhanced Transcoding**: Better integration with other protocols
4. **Extended Security**: Enhanced security features and authorization models

## Related Documentation

- [Protocol Schema Documentation](/03_configuration/schema/protocols.md#grpc-protocol-configuration)
- [Communication Patterns](/07_communication_patterns/protocol_patterns.md)
- [Protocol Adaptations](/07_communication_patterns/protocol_adaptations.md)
- [gRPC Security Configuration](/03_configuration/security_configuration.md#grpc-protocol-security)
