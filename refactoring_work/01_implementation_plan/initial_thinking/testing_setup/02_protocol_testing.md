# Protocol-Specific Testing for OpenMAS 0.3.0

## Task Overview
Create comprehensive protocol-specific test suites for all supported protocols in OpenMAS 0.3.0 (A2A, MCP, HTTP, MQTT, gRPC), ensuring proper functionality, standardization, and interoperability while maintaining the reasoning-agnostic architecture.

## Tasks

1. Protocol Test Setup
   - Create protocol-specific test configurations
   - Set up protocol test fixtures
   - Configure mock servers for each protocol

2. Protocol-Specific Unit Tests
   - Create unit tests for protocol-specific components
   - Test protocol serialization/deserialization
   - Test protocol-specific configuration validation

3. Protocol Integration Tests
   - Test agent-to-agent communication via each protocol
   - Test cross-protocol communication through multi-protocol agents
   - Test protocol-specific error handling

4. Agent Card & Capability Testing
   - Test A2A agent card generation and validation
   - Test agent capability discovery via A2A
   - Test capability alignment across protocols

## Protocol Test Structure

```
tests/
├── unit/
│   └── communicators/
│       └── protocols/
│           ├── test_a2a.py       # A2A protocol unit tests
│           ├── test_mcp.py       # MCP protocol unit tests
│           ├── test_http.py      # HTTP protocol unit tests
│           ├── test_mqtt.py      # MQTT protocol unit tests
│           └── test_grpc.py      # gRPC protocol unit tests
└── integration/
    ├── test_a2a_protocol.py      # A2A protocol integration tests
    ├── test_mcp_protocol.py      # MCP protocol integration tests
    ├── test_http_protocol.py     # HTTP protocol integration tests
    ├── test_mqtt_protocol.py     # MQTT protocol integration tests
    ├── test_grpc_protocol.py     # gRPC protocol integration tests
    └── test_multi_protocol.py    # Multi-protocol support tests
```

## A2A Protocol Testing

### Agent Card Tests

```python
import pytest
from openmas.communicators.protocols.a2a import A2ACommunicator, AgentCard

class TestA2AAgentCard:
    def test_agent_card_generation(self):
        """Test that agent cards are correctly generated."""
        # Arrange
        communicator = A2ACommunicator(config={
            "base_url": "http://localhost:8000",
            "agent_id": "test-agent",
            "capabilities": {
                "text": {"enabled": True, "models": ["test-model"]}
            }
        })

        # Act
        card = communicator.generate_agent_card()

        # Assert
        assert card.name == "test-agent"
        assert "text" in card.api.capabilities
        assert card.api.capabilities["text"].enabled == True
        assert "test-model" in card.api.capabilities["text"].models

    def test_agent_card_validation(self):
        """Test that agent cards are correctly validated."""
        # Arrange
        card_data = {
            "schema_version": "1.0",
            "name": "test-agent",
            "description": "Test agent",
            "api": {
                "type": "agent",
                "url": "http://localhost:8000",
                "capabilities": {
                    "text": {
                        "enabled": True,
                        "models": ["test-model"]
                    }
                }
            }
        }

        # Act
        card = AgentCard.parse_obj(card_data)

        # Assert
        assert card.name == "test-agent"
        assert card.api.capabilities["text"].enabled == True

    def test_invalid_agent_card(self):
        """Test that invalid agent cards are rejected."""
        # Arrange
        invalid_card_data = {
            "schema_version": "1.0",
            "name": "test-agent",
            "api": {
                "type": "agent",
                "url": "http://localhost:8000",
                "capabilities": {
                    "text": {
                        "enabled": "not-a-boolean"  # Invalid: should be boolean
                    }
                }
            }
        }

        # Act/Assert
        with pytest.raises(ValueError):
            AgentCard.parse_obj(invalid_card_data)
```

### A2A Communication Tests

```python
import pytest
from openmas.communicators.protocols.a2a import A2ACommunicator
from openmas.agent import Agent

class TestA2ACommunication:
    def test_send_receive_message(self, mocker):
        """Test sending and receiving messages via A2A protocol."""
        # Mock HTTP client
        mock_client = mocker.patch("openmas.communicators.protocols.a2a.http.HTTPClient")
        mock_client.return_value.post.return_value = {
            "status": "success",
            "response": {"content": "Hello back"}
        }

        # Setup communicator
        communicator = A2ACommunicator(config={
            "base_url": "http://localhost:8000",
            "agent_id": "agent1"
        })

        # Act
        response = communicator.send_message(
            target_agent_id="agent2",
            message={"content": "Hello"}
        )

        # Assert
        assert response["status"] == "success"
        assert response["response"]["content"] == "Hello back"
        mock_client.return_value.post.assert_called_once()

    def test_discover_agents(self, mocker):
        """Test agent discovery via A2A protocol."""
        # Mock discovery response
        mock_response = [
            {
                "name": "agent2",
                "url": "http://localhost:8001",
                "capabilities": ["text"]
            },
            {
                "name": "agent3",
                "url": "http://localhost:8002",
                "capabilities": ["image", "text"]
            }
        ]

        # Mock HTTP client
        mock_client = mocker.patch("openmas.communicators.protocols.a2a.http.HTTPClient")
        mock_client.return_value.get.return_value = mock_response

        # Setup communicator
        communicator = A2ACommunicator(config={
            "base_url": "http://localhost:8000",
            "agent_id": "agent1"
        })

        # Act
        discovered = communicator.discover_agents()

        # Assert
        assert len(discovered) == 2
        assert discovered[0]["name"] == "agent2"
        assert "text" in discovered[0]["capabilities"]
        assert "image" in discovered[1]["capabilities"]
```

## MCP Protocol Testing

### MCP Server Mode Tests

```python
import pytest
from openmas.communicators.protocols.mcp import MCPCommunicator
from openmas.communicators.protocols.mcp.server import MCPServer

class TestMCPServerMode:
    def test_server_initialization(self):
        """Test that MCP server mode initializes correctly."""
        # Arrange
        config = {
            "server_mode": True,
            "server_name": "test-server",
            "http_port": 8080,
            "tools": [
                {
                    "name": "test_tool",
                    "description": "A test tool",
                    "parameters": {"type": "object", "properties": {}}
                }
            ]
        }

        # Act
        server = MCPServer(config=config)

        # Assert
        assert server.name == "test-server"
        assert server.port == 8080
        assert len(server.tools) == 1
        assert server.tools[0].name == "test_tool"

    def test_tool_registration(self):
        """Test that tools can be registered with the MCP server."""
        # Arrange
        server = MCPServer(config={
            "server_mode": True,
            "server_name": "test-server",
            "http_port": 8080
        })

        # Act
        server.register_tool(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object", "properties": {}},
            handler=lambda params: {"result": "success"}
        )

        # Assert
        assert len(server.tools) == 1
        assert server.tools[0].name == "test_tool"

        # Test tool execution
        result = server.execute_tool("test_tool", {})
        assert result["result"] == "success"
```

### MCP Client Mode Tests

```python
import pytest
from openmas.communicators.protocols.mcp import MCPCommunicator
from openmas.communicators.protocols.mcp.client import MCPClient

class TestMCPClientMode:
    def test_client_initialization(self):
        """Test that MCP client mode initializes correctly."""
        # Arrange
        config = {
            "client_mode": True,
            "servers": [
                {
                    "name": "test-server",
                    "url": "http://localhost:8080"
                }
            ]
        }

        # Act
        client = MCPClient(config=config)

        # Assert
        assert len(client.servers) == 1
        assert client.servers[0].name == "test-server"
        assert client.servers[0].url == "http://localhost:8080"

    def test_tool_discovery(self, mocker):
        """Test that tools can be discovered from MCP servers."""
        # Mock HTTP client
        mock_client = mocker.patch("openmas.communicators.protocols.mcp.client.HTTPClient")
        mock_client.return_value.get.return_value = {
            "tools": [
                {
                    "name": "test_tool",
                    "description": "A test tool",
                    "parameters": {"type": "object", "properties": {}}
                }
            ]
        }

        # Setup client
        client = MCPClient(config={
            "client_mode": True,
            "servers": [
                {
                    "name": "test-server",
                    "url": "http://localhost:8080"
                }
            ]
        })

        # Act
        tools = client.discover_tools("test-server")

        # Assert
        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"

    def test_tool_execution(self, mocker):
        """Test that tools can be executed on MCP servers."""
        # Mock HTTP client
        mock_client = mocker.patch("openmas.communicators.protocols.mcp.client.HTTPClient")
        mock_client.return_value.post.return_value = {
            "result": "success"
        }

        # Setup client
        client = MCPClient(config={
            "client_mode": True,
            "servers": [
                {
                    "name": "test-server",
                    "url": "http://localhost:8080"
                }
            ]
        })

        # Act
        result = client.execute_tool(
            server_name="test-server",
            tool_name="test_tool",
            parameters={}
        )

        # Assert
        assert result["result"] == "success"
        mock_client.return_value.post.assert_called_once()
```

## Multi-Protocol Communication Tests

```python
import pytest
from openmas.agent import MultiProtocolAgent
from openmas.communicators.protocols.a2a import A2AProtocolInterface
from openmas.communicators.protocols.mcp import MCPProtocolInterface

class TestMultiProtocolCommunication:
    def test_a2a_to_mcp_communication(self, mocker):
        """Test communication from A2A to MCP protocol in a multi-protocol agent."""
        # Setup mock protocol interfaces
        mock_a2a_interface = mocker.Mock(spec=A2AProtocolInterface)
        mock_mcp_interface = mocker.Mock(spec=MCPProtocolInterface)

        # Configure mocks
        mock_a2a_interface.send_message.return_value = {"status": "success"}
        mock_mcp_interface.execute_tool.return_value = {"result": "tool_executed"}

        # Create multi-protocol agent with mocked interfaces
        agent = MultiProtocolAgent(config={
            "id": "multi-protocol-agent",
            "protocols": [
                {"type": "a2a-http"},
                {"type": "mcp-sse"}
            ]
        })

        # Replace interfaces with mocks
        agent.protocol_interfaces = {
            "a2a-http": mock_a2a_interface,
            "mcp-sse": mock_mcp_interface
        }

        # Act: Send message using A2A, which internally maps to proper protocol
        result = agent.send_message(
            target_agent_id="agent2",
            message={"content": "Hello"},
            preferred_protocol="a2a-http"
        )

        # Assert
        assert result["status"] == "success"
        mock_a2a_interface.send_message.assert_called_once()

    def test_mcp_to_a2a_communication(self, mocker):
        """Test communication from MCP to A2A protocol in a multi-protocol agent."""
        # Setup mock protocol interfaces
        mock_a2a_interface = mocker.Mock(spec=A2AProtocolInterface)
        mock_mcp_interface = mocker.Mock(spec=MCPProtocolInterface)

        # Configure mocks
        mock_a2a_interface.send_message.return_value = {"status": "success", "response": {"content": "Response"}}
        mock_mcp_interface.execute_tool.return_value = {"result": "tool_executed"}

        # Create multi-protocol agent with mocked interfaces
        agent = MultiProtocolAgent(config={
            "id": "multi-protocol-agent",
            "protocols": [
                {"type": "a2a-http"},
                {"type": "mcp-sse"}
            ]
        })

        # Replace interfaces with mocks
        agent.protocol_interfaces = {
            "a2a-http": mock_a2a_interface,
            "mcp-sse": mock_mcp_interface
        }

        # Act: Execute tool using MCP
        result = agent.execute_tool(
            server_name="test-server",
            tool_name="test_tool",
            parameters={"input": "Hello"},
            preferred_protocol="mcp-sse"
        )

        # Assert
        assert result["result"] == "tool_executed"
        mock_mcp_interface.execute_tool.assert_called_once()
```

## Protocol Test Fixtures

Create protocol-specific test fixtures for reuse across tests:

```python
# fixtures/protocol_fixtures.py
import pytest
from openmas.communicators.protocols.a2a import A2ACommunicator
from openmas.communicators.protocols.mcp import MCPCommunicator

@pytest.fixture
def a2a_config():
    """Return a basic A2A protocol configuration."""
    return {
        "base_url": "http://localhost:8000",
        "agent_id": "test-agent",
        "agent_card": {
            "published": True,
            "well_known_path": "/.well-known/agent.json"
        },
        "capabilities": {
            "text": {"enabled": True, "models": ["test-model"]}
        }
    }

@pytest.fixture
def a2a_communicator(a2a_config):
    """Return an initialized A2A communicator."""
    communicator = A2ACommunicator(config=a2a_config)
    return communicator

@pytest.fixture
def mcp_server_config():
    """Return a basic MCP server configuration."""
    return {
        "server_mode": True,
        "server_name": "test-server",
        "http_port": 8080,
        "tools": [
            {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": {"type": "object", "properties": {}}
            }
        ]
    }

@pytest.fixture
def mcp_client_config():
    """Return a basic MCP client configuration."""
    return {
        "client_mode": True,
        "servers": [
            {
                "name": "test-server",
                "url": "http://localhost:8080"
            }
        ]
    }

@pytest.fixture
def mcp_server_communicator(mcp_server_config):
    """Return an initialized MCP server communicator."""
    communicator = MCPCommunicator(config=mcp_server_config)
    return communicator

@pytest.fixture
def mcp_client_communicator(mcp_client_config):
    """Return an initialized MCP client communicator."""
    communicator = MCPCommunicator(config=mcp_client_config)
    return communicator
```

## Protocol Mock Servers

Create mock servers for testing protocols:

```python
# fixtures/mock_servers.py
import pytest
import threading
import http.server
import socketserver
import json
import time
from pathlib import Path

class MockA2AHandler(http.server.BaseHTTPRequestHandler):
    """Mock A2A protocol server handler."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/.well-known/agent.json":
            # Return agent card
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            card = {
                "schema_version": "1.0",
                "name": "mock-agent",
                "description": "Mock agent for testing",
                "api": {
                    "type": "agent",
                    "url": f"http://localhost:{self.server.server_port}",
                    "capabilities": {
                        "text": {
                            "enabled": True,
                            "models": ["test-model"]
                        }
                    }
                }
            }

            self.wfile.write(json.dumps(card).encode())
        elif self.path == "/discover":
            # Return list of agents
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            agents = [
                {
                    "name": "agent1",
                    "url": "http://localhost:8001",
                    "capabilities": ["text"]
                },
                {
                    "name": "agent2",
                    "url": "http://localhost:8002",
                    "capabilities": ["image", "text"]
                }
            ]

            self.wfile.write(json.dumps(agents).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/generate":
            # Text generation
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            request = json.loads(post_data)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            response = {
                "content": f"Response to: {request.get('content', '')}"
            }

            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

@pytest.fixture(scope="module")
def mock_a2a_server():
    """Create a mock A2A protocol server."""
    # Find an available port
    with socketserver.TCPServer(("", 0), None) as s:
        port = s.server_address[1]

    # Create and start the server
    server = socketserver.TCPServer(("", port), MockA2AHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Allow time for server to start
    time.sleep(0.1)

    yield server

    # Shutdown server
    server.shutdown()
    server.server_close()
```

## Cross-Protocol Testing

Test that different protocols can be used by the same multi-protocol agent:

```python
def test_cross_protocol_communication(mock_a2a_server, mocker):
    """Test communication using multiple protocols in the same agent."""
    # Mock protocol interfaces
    mock_a2a_interface = mocker.Mock(spec=A2AProtocolInterface)
    mock_mcp_interface = mocker.Mock(spec=MCPProtocolInterface)

    # Configure mocks
    mock_a2a_interface.send_message.return_value = {"status": "success"}
    mock_mcp_interface.execute_tool.return_value = {"result": "tool_executed"}

    # Create multi-protocol agent
    agent = MultiProtocolAgent(config={
        "id": "multi-protocol-agent",
        "protocols": [
            {
                "type": "a2a-http",
                "options": {
                    "base_url": f"http://localhost:{mock_a2a_server.server_port}"
                }
            },
            {
                "type": "mcp-sse",
                "options": {
                    "client_mode": True
                }
            }
        ]
    })

    # Replace interfaces with mocks
    agent.protocol_interfaces = {
        "a2a-http": mock_a2a_interface,
        "mcp-sse": mock_mcp_interface
    }

    # Act - Test A2A protocol
    a2a_result = agent.send_message(
        target_agent_id="agent2",
        message={"content": "Hello"},
        preferred_protocol="a2a-http"
    )

    # Test MCP protocol with the same agent
    mcp_result = agent.execute_tool(
        server_name="test-server",
        tool_name="test_tool",
        parameters={"input": "Hello"},
        preferred_protocol="mcp-sse"
    )

    # Assert
    assert a2a_result["status"] == "success"
    assert mcp_result["result"] == "tool_executed"
    mock_a2a_interface.send_message.assert_called_once()
    mock_mcp_interface.execute_tool.assert_called_once()
```

## Testing Reasoning Agnosticism with Multiple Protocols

Test that different reasoning approaches can be used with each protocol:

```python
def test_protocol_reasoning_agnosticism(mocker):
    """Test that all protocols can be used with different reasoning approaches."""
    # Mock reasoning modules
    mock_rule_based = mocker.Mock(name="RuleBasedReasoning")
    mock_bdi = mocker.Mock(name="BDIReasoning")
    mock_llm = mocker.Mock(name="LLMReasoning")

    # Configure A2A with different reasoning modules
    a2a_config = {"base_url": "http://localhost:8000", "agent_id": "test-agent"}

    rule_a2a = A2ACommunicator(config=a2a_config)
    rule_a2a.reasoning = mock_rule_based

    bdi_a2a = A2ACommunicator(config=a2a_config)
    bdi_a2a.reasoning = mock_bdi

    llm_a2a = A2ACommunicator(config=a2a_config)
    llm_a2a.reasoning = mock_llm

    # Mock message sending for testing
    mocker.patch.object(rule_a2a, '_send_http_request', return_value={"status": "success"})
    mocker.patch.object(bdi_a2a, '_send_http_request', return_value={"status": "success"})
    mocker.patch.object(llm_a2a, '_send_http_request', return_value={"status": "success"})

    # Act - send messages with each reasoning module
    rule_result = rule_a2a.send_message("agent2", {"content": "Hello from rules"})
    bdi_result = bdi_a2a.send_message("agent2", {"content": "Hello from BDI"})
    llm_result = llm_a2a.send_message("agent2", {"content": "Hello from LLM"})

    # Assert - all reasoning approaches can use the protocol
    assert rule_result["status"] == "success"
    assert bdi_result["status"] == "success"
    assert llm_result["status"] == "success"

    # Configure MCP with different reasoning modules (repeat for other protocols)
```

## Success Criteria
- Complete protocol test suites implemented
- Agent card generation and validation tests
- Protocol-specific communication tests
- Protocol bridging tests
- Cross-protocol integration tests
- Tests verify protocol standardization across all supported protocols
- Tests verify that all protocols maintain reasoning agnosticism
- Mock servers for protocol testing
- Protocol test fixtures for reuse across tests
