# Request-Response Pattern

## Overview

The Request-Response pattern is a synchronous communication pattern where an agent sends a request to another agent and waits for a response. This pattern is one of the most fundamental communication patterns in OpenMAS and serves as the foundation for many agent interactions.

## Pattern Characteristics

- **Synchronicity**: Typically synchronous, with the requester waiting for a response
- **Cardinality**: One-to-one (1:1) communication
- **Flow Control**: Request initiates, response completes
- **Error Handling**: Explicit error handling in responses
- **State**: Stateless or session-based

## Core Capabilities

The Request-Response pattern provides these key capabilities:

1. **Synchronous Communication** - Direct, time-bounded interactions
2. **Request Verification** - Validation of requests before processing
3. **Response Correlation** - Matching responses to their originating requests
4. **Error Handling** - Standardized error response formats
5. **Retry Mechanism** - Configurable retry policies for failed requests
6. **Timeout Management** - Handling of non-responsive targets

## Sequence Diagram

```
┌────────────┐                         ┌────────────┐
│            │                         │            │
│ Requester  │                         │ Responder  │
│            │                         │            │
└────────────┘                         └────────────┘
      │                                      │
      │  1. Send Request                     │
      │ ─────────────────────────────────────>
      │                                      │
      │                                      │  2. Process Request
      │                                      │
      │  3. Return Response                  │
      │ <─────────────────────────────────────
      │                                      │
      │  4. Process Response                 │
      │                                      │
      │                                      │
```

## Message Format

### Request Message

```yaml
{
  "id": "request-123",
  "type": "request",
  "content": {
    # Request-specific content
  },
  "metadata": {
    "pattern": "request_response",
    "timestamp": "2025-05-18T10:32:45Z",
    "requester_id": "agent-1",
    "timeout_ms": 30000
  }
}
```

### Response Message

```yaml
{
  "id": "response-123",
  "request_id": "request-123",
  "type": "response",
  "content": {
    # Response-specific content
  },
  "status": "success",  # or "error"
  "metadata": {
    "pattern": "request_response",
    "timestamp": "2025-05-18T10:32:47Z",
    "responder_id": "agent-2",
    "processing_time_ms": 120
  }
}
```

### Error Response

```yaml
{
  "id": "response-123",
  "request_id": "request-123",
  "type": "response",
  "status": "error",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found",
    "details": {
      # Error-specific details
    }
  },
  "metadata": {
    "pattern": "request_response",
    "timestamp": "2025-05-18T10:32:46Z",
    "responder_id": "agent-2"
  }
}
```

## Configuration Options

The Request-Response pattern has these configuration options:

```yaml
request_response:
  options:
    timeout: 30000  # Timeout in milliseconds
    synchronous: true  # Whether to block waiting for response
    retry:
      attempts: 3  # Number of retry attempts
      backoff: "exponential"  # Backoff strategy: none, linear, exponential
      initial_delay: 1000  # Initial retry delay in milliseconds
    response_handling:
      handle_partial: false  # Whether to handle partial responses
      aggregate_responses: false  # Whether to aggregate multiple responses
    error_handling:
      retry_on_codes: [500, 503]  # Error codes to retry on
      fallback_response: null  # Fallback response if all retries fail
    security:
      require_authentication: true  # Whether authentication is required
      authorization_profile: "default"  # Authorization profile to use
    observability:
      metrics_enabled: true  # Whether to collect metrics
      log_level: "info"  # Log level
      tracing_enabled: true  # Whether to enable distributed tracing
```

## Implementation

### Pattern Class

```python
class RequestResponsePattern(Pattern):
    """Implementation of the Request-Response pattern."""

    def __init__(self, options, agent_context):
        """Initialize the pattern."""
        super().__init__(options, agent_context)
        self.timeout = options.get("timeout", 30000)
        self.synchronous = options.get("synchronous", True)
        self.retry_config = options.get("retry", {})
        self.response_handling = options.get("response_handling", {})
        self.error_handling = options.get("error_handling", {})

        # Initialize request tracking
        self.pending_requests = {}

    async def send_request(self, content, target_agent_id, metadata=None):
        """Send a request to a target agent."""
        # Generate request ID
        request_id = str(uuid.uuid4())

        # Create request message
        request = {
            "id": request_id,
            "type": "request",
            "content": content,
            "metadata": metadata or {}
        }

        # Add pattern metadata
        request["metadata"].update({
            "pattern": "request_response",
            "timestamp": datetime.now().isoformat(),
            "requester_id": self.agent_context.agent_id,
            "timeout_ms": self.timeout
        })

        # Track the request if synchronous
        if self.synchronous:
            self.pending_requests[request_id] = {
                "future": asyncio.Future(),
                "created_at": datetime.now()
            }

        # Get the protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)

        # Prepare the outgoing message
        prepared_request = await adapter.prepare_outgoing(request, self)

        # Send the request
        await self.agent_context.communicator.send_message(
            prepared_request, target_agent_id)

        # If synchronous, wait for response
        if self.synchronous:
            try:
                # Wait for response with timeout
                response = await asyncio.wait_for(
                    self.pending_requests[request_id]["future"],
                    timeout=self.timeout / 1000
                )
                return response
            except asyncio.TimeoutError:
                # Handle timeout
                del self.pending_requests[request_id]
                return {
                    "id": f"timeout-{request_id}",
                    "request_id": request_id,
                    "type": "response",
                    "status": "error",
                    "error": {
                        "code": "TIMEOUT",
                        "message": f"Request timed out after {self.timeout}ms"
                    }
                }
        else:
            # For asynchronous, just return the request ID
            return {
                "request_id": request_id
            }

    async def handle_response(self, response):
        """Handle a response to a previous request."""
        request_id = response.get("request_id")

        if not request_id or request_id not in self.pending_requests:
            # No matching request found
            return

        # Get the pending request
        pending = self.pending_requests[request_id]

        # Complete the future
        if not pending["future"].done():
            pending["future"].set_result(response)

        # Clean up
        del self.pending_requests[request_id]

    async def process_incoming(self, message, protocol):
        """Process an incoming message."""
        adapter = self.get_protocol_adapter(protocol)
        transformed = await adapter.process_incoming(message, self)

        if transformed.get("type") == "request":
            # Handle incoming request
            await self.agent_context.message_handler.handle_request(transformed)
        elif transformed.get("type") == "response":
            # Handle incoming response
            await self.handle_response(transformed)

        return transformed

    async def prepare_outgoing(self, message, protocol):
        """Prepare an outgoing message."""
        adapter = self.get_protocol_adapter(protocol)
        return await adapter.prepare_outgoing(message, self)
```

## Protocol Adaptations

### A2A Protocol Adaptation

A2A protocol adapts the Request-Response pattern using tasks:

```yaml
request_response:
  protocol_adaptations:
    a2a:
      use_tasks: true
      task_type: "request_response"
      response_timeout: 30000
```

**Adapter Implementation:**

```python
class A2ARequestResponseAdapter(ProtocolAdapter):
    """Adapts the Request-Response pattern to A2A protocol."""

    async def process_incoming(self, message, pattern):
        """Process an incoming A2A message."""
        if message.get("type") == pattern.config.get("task_type", "request_response"):
            # This is a request
            return {
                "id": message.get("id"),
                "type": "request",
                "content": message.get("input"),
                "metadata": message.get("metadata", {})
            }
        else:
            # This is a response
            metadata = message.get("metadata", {})
            return {
                "id": message.get("id"),
                "request_id": metadata.get("request_id"),
                "type": "response",
                "content": message.get("output"),
                "status": "success" if not message.get("error") else "error",
                "error": message.get("error"),
                "metadata": metadata
            }

    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing A2A message."""
        if message.get("type") == "request":
            # Prepare a request task
            return {
                "type": pattern.config.get("task_type", "request_response"),
                "input": message.get("content"),
                "metadata": message.get("metadata", {})
            }
        else:
            # Prepare a response
            task_id = message.get("metadata", {}).get("task_id")
            return {
                "id": task_id,
                "output": message.get("content"),
                "error": message.get("error") if message.get("status") == "error" else None,
                "metadata": message.get("metadata", {})
            }
```

### MCP Protocol Adaptation

MCP protocol adapts the Request-Response pattern using function calls:

```yaml
request_response:
  protocol_adaptations:
    mcp:
      use_function_calls: true
      function_name: "handle_request"
      async_response: false
```

**Adapter Implementation:**

```python
class MCPRequestResponseAdapter(ProtocolAdapter):
    """Adapts the Request-Response pattern to MCP protocol."""

    async def process_incoming(self, message, pattern):
        """Process an incoming MCP message."""
        if message.get("type") == "function_call":
            # This is a request
            return {
                "id": message.get("id"),
                "type": "request",
                "content": message.get("arguments"),
                "metadata": {
                    "function_name": message.get("name"),
                    "pattern": "request_response"
                }
            }
        else:
            # This is a response
            return {
                "id": message.get("id"),
                "request_id": message.get("request_id"),
                "type": "response",
                "content": message.get("result"),
                "status": "success" if not message.get("error") else "error",
                "error": message.get("error"),
                "metadata": message.get("metadata", {})
            }

    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing MCP message."""
        if message.get("type") == "request":
            # Prepare a function call
            return {
                "type": "function_call",
                "name": pattern.config.get("function_name", "handle_request"),
                "arguments": message.get("content"),
                "id": message.get("id"),
                "metadata": message.get("metadata", {})
            }
        else:
            # Prepare a response
            return {
                "type": "function_result",
                "id": message.get("id"),
                "request_id": message.get("request_id"),
                "result": message.get("content"),
                "error": message.get("error") if message.get("status") == "error" else None,
                "metadata": message.get("metadata", {})
            }
```

## Integration with Topologies

The Request-Response pattern is commonly used in these topology relationships:

1. **Centralized**: Orchestrator-to-worker for command and control
2. **Peer-to-Peer**: Direct queries between peers
3. **Hierarchical**: Cross-level direct communication
4. **Mesh**: Point-to-point queries in the mesh

**Example Configuration:**

```yaml
topology:
  pattern: "centralized"
  roles:
    types:
      - name: "orchestrator"
      - name: "worker"
  relationships:
    types:
      - name: "orchestrator_to_worker"
        communication_patterns:
          primary: "request_response"
```

## Use Cases

### 1. Service Invocation

An agent requests a service from another agent:

```python
# Orchestrator requesting flight search
response = await request_response_pattern.send_request(
    content={
        "action": "search_flights",
        "parameters": {
            "from": "SFO",
            "to": "JFK",
            "date": "2025-06-15"
        }
    },
    target_agent_id="flight_search_agent"
)

# Process the response
if response.get("status") == "success":
    flights = response.get("content", {}).get("flights", [])
    # Handle flights data
else:
    error = response.get("error", {})
    # Handle error
```

### 2. Data Query

An agent requests data from another agent:

```python
# Request user profile data
response = await request_response_pattern.send_request(
    content={
        "query": "get_user_profile",
        "user_id": "user-123"
    },
    target_agent_id="user_profile_agent"
)

# Process the user profile
if response.get("status") == "success":
    user_profile = response.get("content", {})
    # Use user profile
else:
    # Handle error
```

### 3. Command and Control

An orchestrator issues commands to worker agents:

```yaml
# Orchestrator configuration
agents:
  task_orchestrator:
    class: "agents.orchestrator.TaskOrchestrator"
    patterns:
      request_response:
        options:
          timeout: 60000  # Longer timeout for complex tasks
    topology:
      role: "orchestrator"
      relationships:
        - agent_id: "worker_1"
          relationship_type: "orchestrator_to_worker"
          communication_pattern: "request_response"
```

## Security Considerations

The Request-Response pattern includes these security features:

1. **Authentication**: Verify the identity of requesters and responders
2. **Authorization**: Ensure requesters have permission for the requested action
3. **Input Validation**: Validate request content before processing
4. **Rate Limiting**: Prevent abuse through excessive requests
5. **Timeout Management**: Prevent resource exhaustion from hanging requests

**Security Configuration:**

```yaml
request_response:
  options:
    security:
      require_authentication: true
      authorization_profile: "standard_access"
      input_validation: true
      rate_limit:
        max_requests: 100
        period_seconds: 60
```

## Observability

The Request-Response pattern supports observability:

1. **Request/Response Metrics**: Count, latency, success rate
2. **Distributed Tracing**: Trace requests across agents
3. **Logging**: Configurable logging of requests and responses
4. **Error Tracking**: Track and categorize errors

**Metrics Example:**

```
request_response_count{agent="travel_coordinator",target="flight_search"} 150
request_response_latency_ms{agent="travel_coordinator",target="flight_search",status="success"} 245
request_response_error_rate{agent="travel_coordinator",target="flight_search"} 0.05
```

## Protocol Independence

The Request-Response pattern works consistently across protocols:

- **A2A**: Using tasks with input/output
- **MCP**: Using function calls and results
- **HTTP**: Using standard request/response methods
- **MQTT**: Using topic-based request/response
- **gRPC**: Using service method calls

This protocol independence enables agents to communicate using the same pattern regardless of the underlying protocol implementation.
