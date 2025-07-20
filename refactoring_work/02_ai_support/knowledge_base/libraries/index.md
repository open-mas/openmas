# OpenMAS Library Dependencies

This document provides information about the key libraries used in OpenMAS and how they should be incorporated in the refactoring process.

## Core Dependencies

### Pydantic

**Purpose**: Data validation and settings management
**Version**: 2.6+
**Documentation**: [Pydantic Documentation](https://docs.pydantic.dev/latest/)

Key usage patterns:

```python
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any

class AgentConfig(BaseModel):
    """Configuration for an OpenMAS agent."""

    name: str = Field(..., description="Unique name for the agent")
    module: str = Field(..., description="Python module containing agent code")
    class_name: str = Field("Agent", description="Class name of the agent")
    communicator: CommunicatorConfig
    parameters: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}

    @validator("name")
    def name_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError("Agent name cannot be empty")
        return v
```

### asyncio

**Purpose**: Asynchronous I/O, event loop, and coroutines
**Version**: Python 3.10+ built-in
**Documentation**: [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

Key usage patterns:

```python
import asyncio

async def setup_agent(agent):
    """Set up an agent asynchronously."""
    await agent.setup()

async def main():
    """Main entry point."""
    agents = [create_agent("agent1"), create_agent("agent2")]
    await asyncio.gather(*(setup_agent(agent) for agent in agents))

if __name__ == "__main__":
    asyncio.run(main())
```

### PyYAML

**Purpose**: YAML parsing and generation
**Version**: 6.0+
**Documentation**: [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)

Key usage patterns:

```python
import yaml
from pathlib import Path

def load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def save_config(config: dict, config_path: str) -> None:
    """Save configuration to a YAML file."""
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
```

### Click

**Purpose**: Command line interface creation
**Version**: 8.1+
**Documentation**: [Click Documentation](https://click.palletsprojects.com/)

Key usage patterns:

```python
import click

@click.group()
def cli():
    """OpenMAS command line interface."""
    pass

@cli.command()
@click.option("--config", "-c", help="Path to configuration file")
@click.option("--agent", "-a", help="Agent to run")
def run(config, agent):
    """Run an OpenMAS agent."""
    # Implementation

if __name__ == "__main__":
    cli()
```

### structlog

**Purpose**: Structured logging
**Version**: 23.2+
**Documentation**: [structlog Documentation](https://www.structlog.org/en/stable/)

Key usage patterns:

```python
import structlog

logger = structlog.get_logger()

def process_request(request_id, data):
    """Process a request with structured logging."""
    logger.info("Processing request", request_id=request_id)

    try:
        result = process_data(data)
        logger.info("Request processed successfully", request_id=request_id)
        return result
    except Exception as e:
        logger.exception("Error processing request", request_id=request_id, error=str(e))
        raise
```

## Communication Libraries

### aiohttp

**Purpose**: Asynchronous HTTP client/server
**Version**: 3.9+
**Documentation**: [aiohttp Documentation](https://docs.aiohttp.org/en/stable/)

Key usage patterns:

```python
import aiohttp
from aiohttp import web

# Client
async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Server
async def handle_request(request):
    data = await request.json()
    return web.json_response({"status": "success", "data": data})

app = web.Application()
app.router.add_post("/api/data", handle_request)
```

### MCP (Model Context Protocol)

**Purpose**: Standardized protocol for LLM interactions
**Version**: 1.6+
**Documentation**: [MCP Documentation](https://modelcontextprotocol.io/docs/concepts/architecture)

Key usage patterns:

```python
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.types import TextContent, CallToolResult
from mcp.server.fastmcp import FastMCP, Context

# Server
app = FastMCP()

async def handle_tool_call(ctx: Context, name: str, parameters: dict) -> CallToolResult:
    result = f"Processed {name} with {parameters}"
    return CallToolResult(content=result)

app.tool("process_data", handle_tool_call)

# Client
async with ClientSession() as session:
    async with session.connect("http://localhost:8000/mcp", transport=sse_client) as connection:
        prompt = {"role": "user", "content": "Hello, can you process this data?"}

        async for event in connection.completion([prompt]):
            if event.type == "content":
                print(event.content.text, end="", flush=True)
```

### paho-mqtt

**Purpose**: MQTT client implementation
**Version**: 2.0+
**Documentation**: [paho-mqtt Documentation](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)

Key usage patterns:

```python
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("openmas/agents/#")

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    print(f"Received message on {msg.topic}: {payload}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()
```

## Testing Libraries

### pytest

**Purpose**: Testing framework
**Version**: 7.4+
**Documentation**: [pytest Documentation](https://docs.pytest.org/)

Key usage patterns:

```python
import pytest

@pytest.fixture
def mock_config():
    return {
        "project_name": "test_project",
        "agents": {
            "agent1": {
                "module": "test.agent",
                "class_name": "TestAgent"
            }
        }
    }

def test_config_loader(mock_config):
    loader = ConfigLoader()
    config = loader.load(mock_config)
    assert config.project_name == "test_project"
    assert "agent1" in config.agents
```

### pytest-asyncio

**Purpose**: Async support for pytest
**Version**: 0.23+
**Documentation**: [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)

Key usage patterns:

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected_value

@pytest.fixture
async def async_resource():
    resource = await create_resource()
    yield resource
    await cleanup_resource(resource)
```

### pytest-mock

**Purpose**: Mock support for pytest
**Version**: 3.12+
**Documentation**: [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)

Key usage patterns:

```python
def test_with_mock(mocker):
    # Create a mock
    mock_function = mocker.patch("module.function")
    mock_function.return_value = "mocked_result"

    # Use the mock
    result = use_function()

    # Assert the mock was called correctly
    mock_function.assert_called_once_with(expected_args)
    assert result == "mocked_result"
```

## Implementation Guidelines

1. **Dependency Injection**: All libraries should be injected into components to allow for easy mocking in tests.

2. **Isolation**: Components should be designed to work with interfaces rather than concrete library implementations.

3. **Async Everything**: All I/O operations should be async to allow for scalable performance.

4. **Type Hints**: All code should use proper type hints to leverage static type checking.

5. **Error Handling**: Proper error handling should be implemented for all library calls.

6. **Version Pinning**: Dependencies should be pinned to specific versions in pyproject.toml.

7. **Documentation**: Library usage should be documented clearly with examples.

## Library Import Patterns

### Absolute Imports

Use absolute imports for all OpenMAS modules:

```python
from openmas.configuration import ConfigLoader
from openmas.agent import BaseAgent
from openmas.communicator import BaseCommunicator
```

### Type Hints

Include proper type hints for all libraries:

```python
from typing import Dict, List, Optional, Any, Protocol, Type
from pydantic import BaseModel
from asyncio import Future, Event
```

### Optional Dependencies

Handle optional dependencies gracefully:

```python
try:
    import grpc
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False

class GRPCCommunicator(BaseCommunicator):
    def __init__(self, config: Dict[str, Any]):
        if not GRPC_AVAILABLE:
            raise ImportError("gRPC is not available. Install it with 'pip install grpcio'")
        super().__init__(config)
