# Mock Services for OpenMAS Testing

## Overview

This document describes the mock services used for testing OpenMAS components. These mock services enable isolated testing of OpenMAS components by simulating external systems and services while preserving OpenMAS's reasoning-agnostic architecture and multi-protocol support.

## Core Mock Services

### Mock Agent Service

The Mock Agent Service simulates an OpenMAS agent for testing agent-to-agent interactions:

```python
from openmas.testing.mock import MockAgentService

# Create a mock agent service
mock_agent = MockAgentService(
    agent_id="test-agent",
    name="Test Agent",
    capabilities=["test-capability", "data-processing"],
    protocols=["a2a", "http", "mqtt"]
)

# Start the mock agent service
await mock_agent.start()

# The mock agent is now available for testing
# - A2A protocol: http://localhost:8080
# - HTTP protocol: http://localhost:8081
# - MQTT topics: agents/test-agent/#

# Stop the mock agent when done
await mock_agent.stop()
```

### Mock Protocol Services

#### Mock A2A Service

The Mock A2A Service simulates an A2A protocol endpoint:

```python
from openmas.testing.mock import MockA2AService

# Create a mock A2A service
mock_a2a = MockA2AService(
    agent_card={
        "id": "test-agent",
        "name": "Test Agent",
        "capabilities": [
            {
                "id": "test-capability",
                "name": "Test Capability",
                "description": "A test capability",
                "parameters": [
                    {
                        "name": "param1",
                        "type": "string",
                        "required": True
                    }
                ]
            }
        ]
    }
)

# Configure response for the test capability
mock_a2a.add_capability_response(
    capability_id="test-capability",
    response={"result": "test-result"}
)

# Start the mock A2A service
await mock_a2a.start()

# The mock A2A service is now available at http://localhost:8080
# Stop the mock A2A service when done
await mock_a2a.stop()
```

#### Mock MCP Service

The Mock MCP Service simulates an MCP protocol endpoint:

```python
from openmas.testing.mock import MockMCPService

# Create a mock MCP service
mock_mcp = MockMCPService(
    functions=[
        {
            "name": "test_function",
            "description": "A test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Test parameter"
                    }
                }
            }
        }
    ]
)

# Configure function response
mock_mcp.add_function_response(
    function_name="test_function",
    response={"result": "test-result"}
)

# Start the mock MCP service
await mock_mcp.start()

# The mock MCP service is now available at http://localhost:8100
# Stop the mock MCP service when done
await mock_mcp.stop()
```

#### Mock HTTP Service

The Mock HTTP Service simulates an HTTP API endpoint:

```python
from openmas.testing.mock import MockHTTPService

# Create a mock HTTP service
mock_http = MockHTTPService()

# Configure endpoint responses
mock_http.add_endpoint(
    method="GET",
    path="/api/test",
    response={"status": "success", "data": "test-data"},
    status_code=200
)

mock_http.add_endpoint(
    method="POST",
    path="/api/submit",
    response={"status": "created", "id": "123"},
    status_code=201
)

# Start the mock HTTP service
await mock_http.start()

# The mock HTTP service is now available at http://localhost:8080
# Stop the mock HTTP service when done
await mock_http.stop()
```

#### Mock MQTT Service

The Mock MQTT Service simulates an MQTT broker:

```python
from openmas.testing.mock import MockMQTTBroker

# Create a mock MQTT broker
mock_mqtt = MockMQTTBroker()

# Start the mock MQTT broker
await mock_mqtt.start()

# The mock MQTT broker is now available at localhost:1883
# Configure message responses
mock_mqtt.add_message_response(
    topic="agents/test-agent/request",
    response_topic="agents/test-agent/response",
    response_payload={"status": "success", "data": "test-data"}
)

# Stop the mock MQTT broker when done
await mock_mqtt.stop()
```

#### Mock gRPC Service

The Mock gRPC Service simulates a gRPC service:

```python
from openmas.testing.mock import MockGRPCService

# Create a mock gRPC service
mock_grpc = MockGRPCService(
    proto_file="test_service.proto",
    service_name="TestService"
)

# Configure method responses
mock_grpc.add_method_response(
    method_name="TestMethod",
    response={"status": "success", "data": "test-data"}
)

# Start the mock gRPC service
await mock_grpc.start()

# The mock gRPC service is now available at localhost:50051
# Stop the mock gRPC service when done
await mock_grpc.stop()
```

### Mock Reasoning Services

#### Mock Rule Engine

The Mock Rule Engine simulates a rule-based reasoning engine:

```python
from openmas.testing.mock import MockRuleEngine

# Create a mock rule engine
mock_rule_engine = MockRuleEngine()

# Configure rule responses
mock_rule_engine.add_rule_response(
    rule_name="test-rule",
    input={"x": 10, "y": 20},
    output={"result": 30}
)

# Use the mock rule engine in tests
result = mock_rule_engine.process({"x": 10, "y": 20})
assert result["result"] == 30
```

#### Mock BDI Engine

The Mock BDI Engine simulates a BDI reasoning engine:

```python
from openmas.testing.mock import MockBDIEngine

# Create a mock BDI engine
mock_bdi = MockBDIEngine()

# Configure beliefs, desires, and intentions
mock_bdi.add_belief("location", "home")
mock_bdi.add_desire("reach_work")
mock_bdi.add_intention_response(
    desire="reach_work",
    context={"location": "home"},
    actions=["travel_to_work"],
    result={"location": "work"}
)

# Use the mock BDI engine in tests
result = mock_bdi.reason({"current_desires": ["reach_work"]})
assert result["actions"] == ["travel_to_work"]
assert result["new_state"]["location"] == "work"
```

#### Mock LLM Engine

The Mock LLM Engine simulates an LLM-based reasoning engine:

```python
from openmas.testing.mock import MockLLMEngine

# Create a mock LLM engine
mock_llm = MockLLMEngine()

# Configure prompt responses
mock_llm.add_prompt_response(
    prompt="What is the capital of France?",
    response="The capital of France is Paris."
)

mock_llm.add_prompt_response(
    prompt_pattern=r"What is the capital of (.*)\?",
    response_template="The capital of {0} is {capital}.",
    context_map={
        "Germany": {"capital": "Berlin"},
        "Italy": {"capital": "Rome"},
        "Spain": {"capital": "Madrid"}
    }
)

# Use the mock LLM engine in tests
result = await mock_llm.complete("What is the capital of France?")
assert result == "The capital of France is Paris."

result = await mock_llm.complete("What is the capital of Germany?")
assert result == "The capital of Germany is Berlin."
```

#### Mock Knowledge Graph Engine

The Mock Knowledge Graph Engine simulates a knowledge graph reasoning engine:

```python
from openmas.testing.mock import MockKGEngine

# Create a mock knowledge graph engine
mock_kg = MockKGEngine()

# Configure graph data and query responses
mock_kg.add_nodes([
    {"id": "person1", "type": "Person", "properties": {"name": "Alice"}},
    {"id": "person2", "type": "Person", "properties": {"name": "Bob"}},
    {"id": "city1", "type": "City", "properties": {"name": "New York"}}
])

mock_kg.add_relationships([
    {"source": "person1", "target": "person2", "type": "KNOWS"},
    {"source": "person1", "target": "city1", "type": "LIVES_IN"}
])

mock_kg.add_query_response(
    query="MATCH (p:Person)-[:LIVES_IN]->(c:City) RETURN p.name, c.name",
    response=[{"p.name": "Alice", "c.name": "New York"}]
)

# Use the mock knowledge graph engine in tests
result = mock_kg.query("MATCH (p:Person)-[:LIVES_IN]->(c:City) RETURN p.name, c.name")
assert len(result) == 1
assert result[0]["p.name"] == "Alice"
assert result[0]["c.name"] == "New York"
```

## Integration Mock Services

### Mock Agent Supervisor

The Mock Agent Supervisor simulates a multi-agent system for integration testing:

```python
from openmas.testing.mock import MockAgentSupervisor

# Create a mock agent supervisor
supervisor = MockAgentSupervisor()

# Add mock agents
supervisor.add_agent(
    id="agent1",
    capabilities=["data-request"],
    protocols=["http"]
)

supervisor.add_agent(
    id="agent2",
    capabilities=["data-provider"],
    protocols=["http"]
)

# Configure interaction behaviors
supervisor.add_interaction(
    source_agent="agent1",
    target_agent="agent2",
    source_capability="data-request",
    target_capability="data-provider",
    request={"query": "test-query"},
    response={"data": "test-data"}
)

# Start the mock supervisor
await supervisor.start()

# Execute test interaction
result = await supervisor.execute_interaction(
    source_agent="agent1",
    target_agent="agent2",
    capability="data-request",
    parameters={"query": "test-query"}
)

assert result["data"] == "test-data"

# Stop the mock supervisor when done
await supervisor.stop()
```

### Mock External Services

#### Mock Database Service

```python
from openmas.testing.mock import MockDatabaseService

# Create a mock database service
mock_db = MockDatabaseService()

# Configure data
mock_db.add_collection("users", [
    {"id": "user1", "name": "Alice", "role": "admin"},
    {"id": "user2", "name": "Bob", "role": "user"}
])

# Configure query responses
mock_db.add_query_response(
    collection="users",
    query={"role": "admin"},
    result=[{"id": "user1", "name": "Alice", "role": "admin"}]
)

# Start the mock database service
await mock_db.start()

# The mock database service is now available
# Stop the mock database service when done
await mock_db.stop()
```

#### Mock Authentication Service

```python
from openmas.testing.mock import MockAuthService

# Create a mock authentication service
mock_auth = MockAuthService()

# Configure users and tokens
mock_auth.add_user(
    username="test-user",
    password="test-password",
    token="test-token-123",
    permissions=["read", "write"]
)

# Start the mock authentication service
await mock_auth.start()

# The mock authentication service is now available
# Stop the mock authentication service when done
await mock_auth.stop()
```

## Running Mock Services

### Command Line Interface

Mock services can be run from the command line:

```bash
# Start a mock agent service
openmas mock agent --id test-agent --protocol http --capability test-capability

# Start a mock A2A service
openmas mock a2a --port 8080 --capability test-capability

# Start a mock MCP service
openmas mock mcp --port 8100 --function test_function

# Start a mock HTTP service
openmas mock http --port 8080 --endpoint /api/test

# Start a mock MQTT broker
openmas mock mqtt --port 1883

# Start a mock gRPC service
openmas mock grpc --port 50051 --proto test_service.proto
```

### Docker-Based Mock Services

Mock services can also be run as Docker containers:

```bash
# Start a mock agent service
docker run -p 8080:8080 openmas/mock-agent:latest --id test-agent

# Start a mock A2A service
docker run -p 8080:8080 openmas/mock-a2a:latest

# Start a multi-service mock environment
docker-compose -f mock-services.yml up
```

Example `mock-services.yml`:

```yaml
version: '3'
services:
  mock-a2a:
    image: openmas/mock-a2a:latest
    ports:
      - "8080:8080"
    environment:
      CAPABILITIES: test-capability,data-processing
  
  mock-mcp:
    image: openmas/mock-mcp:latest
    ports:
      - "8100:8100"
    environment:
      FUNCTIONS: test_function,process_data
  
  mock-mqtt:
    image: openmas/mock-mqtt:latest
    ports:
      - "1883:1883"
  
  mock-agent-supervisor:
    image: openmas/mock-supervisor:latest
    ports:
      - "8000:8000"
    environment:
      AGENTS: agent1,agent2
      PROTOCOLS: a2a,http,mqtt
```

## Best Practices

1. **Isolation**: Each mock service should be isolated from others to prevent test interference
2. **Configurability**: Mock services should be highly configurable for different test scenarios
3. **Protocol Alignment**: Mock services should faithfully implement protocol specifications
4. **Body-Brain Separation**: Communication mocks ("body") should be separate from reasoning mocks ("brain")
5. **Dynamic Responses**: Support dynamic response generation based on request patterns
6. **Verification**: Mock services should record interactions for verification in tests

## Related Documentation

- [Test Frameworks](./test_frameworks.md)
- [Integration Testing](../integration_testing/README.md)
- [Protocol Testing](../integration_testing/protocol_testing.md)
- [Multi-Agent Testing](../integration_testing/multi_agent_testing.md)
- [Test Framework](../framework/README.md)
