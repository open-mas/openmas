"""Integration tests for communicator configuration."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

import pytest
import yaml

# Constants for communicator types
COMMUNICATOR_HTTP = "http"
COMMUNICATOR_MOCK = "mock"
COMMUNICATOR_MQTT = "mqtt"
COMMUNICATOR_GRPC = "grpc"
COMMUNICATOR_MCP_SSE = "mcp-sse"


@pytest.fixture
def multi_agent_project(tmp_path):
    """Create a project with multiple agents using different communicator types and ports."""
    project_dir = tmp_path / "multi_comm_project"
    project_dir.mkdir()

    # Create standard directories
    (project_dir / "agents").mkdir()
    (project_dir / "shared").mkdir()
    (project_dir / "extensions").mkdir()
    (project_dir / "config").mkdir()

    # Create a diagnostic agent that reports its communicator config
    diagnostic_agent_dir = project_dir / "agents" / "diagnostic_agent"
    diagnostic_agent_dir.mkdir()
    agent_file = diagnostic_agent_dir / "agent.py"
    agent_content = """  # noqa: W291, W293
import asyncio
import os
import json
import sys
from openmas.agent import BaseAgent


class Agent(BaseAgent):
    '''Diagnostic agent.'''

    async def setup(self):
        '''Set up the agent.'''
        # Report communicator information
        comm_type = self.communicator.__class__.__name__
        print(f"COMM_TYPE:{comm_type}")
        
        # Report detailed configuration
        if hasattr(self.config, "communicator_type"):
            print(f"CONFIG_COMM_TYPE:{self.config.communicator_type}")
        
        if hasattr(self.config, "communicator_options"):
            # Convert to JSON for easy parsing in tests
            comm_options = self.config.communicator_options
            print(f"COMM_OPTIONS:{json.dumps(comm_options)}")
        
        # For HTTP communicator, extract port if available
        if hasattr(self.communicator, "http_port"):
            print(f"HTTP_PORT:{self.communicator.http_port}")

    async def run(self):
        '''Run the agent briefly for testing.'''
        await asyncio.sleep(0.1)
        print("AGENT_COMPLETED")
        return  # Exit immediately for testing

    async def shutdown(self):
        '''Shut down the agent.'''
        print("AGENT_SHUTDOWN")
"""
    agent_file.write_text(agent_content)

    # Create HTTP specific agent
    http_agent_dir = project_dir / "agents" / "http_agent"
    http_agent_dir.mkdir()
    http_agent_file = http_agent_dir / "agent.py"
    http_agent_content = """
import asyncio
from openmas.agent import BaseAgent

class Agent(BaseAgent):
    \"\"\"Agent configured to use HTTP communicator with custom port.\"\"\"

    async def setup(self):
        \"\"\"Set up the agent.\"\"\"
        print(f"HTTP Agent using communicator: {self.communicator.__class__.__name__}")
        if hasattr(self.communicator, "http_port"):
            print(f"HTTP_PORT:{self.communicator.http_port}")
        elif hasattr(self.communicator, "port"):
            print(f"HTTP_PORT:{self.communicator.port}")
        elif hasattr(self.communicator, "server") and hasattr(self.communicator.server, "port"):
            print(f"HTTP_PORT:{self.communicator.server.port}")

    async def run(self):
        \"\"\"Run the agent.\"\"\"
        await asyncio.sleep(0.1)
        return

    async def shutdown(self):
        \"\"\"Shut down the agent.\"\"\"
        pass
"""
    http_agent_file.write_text(http_agent_content)

    # Create project configuration file with multiple agents having different communicator configs
    project_config = {
        "name": "multi_comm_project",
        "version": "0.1.0",
        "agents": {
            "http_default": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                "communicator": "http",  # Default HTTP communicator
            },
            "http_custom_port": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                "communicator": "http",
                "options": {"communicator_options": {"http_port": 8765}},  # Custom port
            },
            "http_agent_with_options": {
                "module": "agents.http_agent",
                "class": "Agent",
                "communicator": "http",
                "options": {"communicator_options": {"http_port": 9876}},
            },
            "diagnostic_agent": {"module": "agents.diagnostic_agent", "class": "Agent"},
        },
        "shared_paths": ["shared"],
        "extension_paths": ["extensions"],
        "default_config": {
            "log_level": "INFO",
            "communicator_type": "http",  # Default communicator type
            "communicator_options": {"timeout": 30},
        },
        "communicator_defaults": {
            # Default options for all communicators of any type
            "http_port": 9000
        },
    }

    with open(project_dir / "openmas_project.yml", "w") as f:
        yaml.dump(project_config, f)

    # Create environment-specific configuration with port override
    env_config = {
        "communicator_options": {"http_port": 8888}  # This should override the default but not agent-specific settings
    }

    with open(project_dir / "config" / "test.yml", "w") as f:
        yaml.dump(env_config, f)

    return project_dir


def run_agent_in_subprocess(project_dir: Path, agent_name: str, env: str = None, timeout: int = 5) -> Dict:
    """Run an agent in a subprocess and capture its output.

    Args:
        project_dir: Path to the project directory
        agent_name: Name of the agent to run
        env: Optional environment name
        timeout: Timeout in seconds

    Returns:
        Dictionary with stdout, stderr, and return code
    """
    # Skip if CI environment to avoid subprocess issues
    if os.environ.get("CI") == "true":
        pytest.skip("Skipping in CI environment")

    # Prepare command
    cmd = [sys.executable, "-m", "openmas.cli", "run", agent_name]

    if env:
        cmd.extend(["--env", env])

    # Set up environment variables to help with extensions
    env_vars = os.environ.copy()

    # Add extensions directory to PYTHONPATH to help with discovery
    extensions_dir = project_dir / "extensions"
    python_path = env_vars.get("PYTHONPATH", "")
    if python_path:
        env_vars["PYTHONPATH"] = f"{str(extensions_dir)}:{python_path}"
    else:
        env_vars["PYTHONPATH"] = str(extensions_dir)

    print(f"Setting PYTHONPATH to: {env_vars['PYTHONPATH']}")

    # Run command with subprocess
    try:
        process = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True, env=env_vars, timeout=timeout)

        return {"stdout": process.stdout, "stderr": process.stderr, "returncode": process.returncode}
    except subprocess.TimeoutExpired:
        pytest.fail(f"Command timed out after {timeout} seconds")


def parse_stdout_for_values(stdout: str) -> Dict:
    """Parse stdout for specific diagnostic values output by the agent.

    Looks for lines like KEY:VALUE and returns a dictionary of these values.

    Args:
        stdout: The standard output from the agent

    Returns:
        Dictionary of extracted key-value pairs
    """
    result = {}
    for line in stdout.splitlines():
        if ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2 and parts[0].isupper():
                key = parts[0]
                value = parts[1]
                try:
                    # Try to parse as number if possible
                    if value.isdigit():
                        value = int(value)
                    # Try to parse as JSON if it looks like a dict or list
                    elif (value.startswith("{") and value.endswith("}")) or (
                        value.startswith("[") and value.endswith("]")
                    ):
                        try:
                            import json

                            value = json.loads(value)
                        except json.JSONDecodeError:
                            pass
                except (ValueError, TypeError):
                    pass
                result[key] = value
    return result


@pytest.mark.integration
def test_agent_specific_port_configuration(multi_agent_project):
    """Test that agent-specific port configuration is properly applied when running an agent."""
    # Run the agent with custom port
    result = run_agent_in_subprocess(multi_agent_project, "http_custom_port")

    # Check the command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Parse the output for diagnostic values
    values = parse_stdout_for_values(result["stdout"])

    # Verify the communicator type is HTTP
    assert "COMM_TYPE" in values, "No COMM_TYPE in output"
    assert values["COMM_TYPE"] == "HttpCommunicator", f"Unexpected communicator type: {values['COMM_TYPE']}"

    # Verify the communicator port is set correctly from the agent-specific config
    assert "HTTP_PORT" in values, "No HTTP_PORT in output"
    assert values["HTTP_PORT"] == 8765, f"Port was not set correctly, got {values['HTTP_PORT']} instead of 8765"

    # Verify communicator options were passed
    assert "COMM_OPTIONS" in values, "No COMM_OPTIONS in output"
    assert "http_port" in values["COMM_OPTIONS"], "http_port not in communicator options"
    assert (
        values["COMM_OPTIONS"]["http_port"] == 8765
    ), f"Port in options is {values['COMM_OPTIONS']['http_port']} not 8765"


@pytest.mark.integration
def test_env_specific_port_configuration(multi_agent_project):
    """Test that environment-specific port configuration is properly applied when an agent has no specific port."""
    # Run the default agent with the test environment
    result = run_agent_in_subprocess(multi_agent_project, "http_default", env="test")

    # Check the command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Parse the output for diagnostic values
    values = parse_stdout_for_values(result["stdout"])

    # Verify the communicator type is HTTP
    assert "COMM_TYPE" in values, "No COMM_TYPE in output"
    assert values["COMM_TYPE"] == "HttpCommunicator", f"Unexpected communicator type: {values['COMM_TYPE']}"

    # Verify the communicator port is set correctly from the environment config
    assert "HTTP_PORT" in values, "No HTTP_PORT in output"
    assert values["HTTP_PORT"] == 8888, f"Port was not set correctly, got {values['HTTP_PORT']} instead of 8888"


@pytest.mark.integration
def test_multiple_agents_different_ports(multi_agent_project):
    """Test running two agents sequentially to verify they use different ports configured in their configs."""
    # First, run agent with 8765 port
    result1 = run_agent_in_subprocess(multi_agent_project, "http_custom_port")
    assert result1["returncode"] == 0, f"First agent failed: {result1['stderr']}"
    values1 = parse_stdout_for_values(result1["stdout"])

    # Then run agent with 9876 port
    result2 = run_agent_in_subprocess(multi_agent_project, "http_agent_with_options")
    assert result2["returncode"] == 0, f"Second agent failed: {result2['stderr']}"
    values2 = parse_stdout_for_values(result2["stdout"])

    # Verify different ports were used
    assert "HTTP_PORT" in values1, "No port information in first agent output"
    assert "HTTP_PORT" in values2, "No port information in second agent output"

    port1 = values1["HTTP_PORT"]
    port2 = values2["HTTP_PORT"]

    assert port1 != port2, f"Both agents used the same port: {port1}"
    assert port1 == 8765, f"First agent should use port 8765, got {port1}"
    assert port2 == 9876, f"Second agent should use port 9876, got {port2}"


@pytest.mark.integration
def test_communicator_options_precedence(multi_agent_project):
    """Test the precedence rules for communicator options from different sources."""
    # Create files with different configs to test precedence

    # Modify environment config to include timeout
    env_config = {
        "communicator_options": {
            "http_port": 7777,  # Should override default but not agent-specific
            "timeout": 60,  # Should be passed to the communicator
        }
    }

    with open(multi_agent_project / "config" / "precedence.yml", "w") as f:
        yaml.dump(env_config, f)

    # Run the agent with precedence environment
    result = run_agent_in_subprocess(multi_agent_project, "http_custom_port", env="precedence")

    # Check the command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Parse the output for diagnostic values
    values = parse_stdout_for_values(result["stdout"])

    # Verify communicator options
    assert "COMM_OPTIONS" in values, "No COMM_OPTIONS in output"
    assert (
        values["COMM_OPTIONS"]["http_port"] == 8765
    ), f"Agent-specific port not respected, got {values['COMM_OPTIONS']['http_port']}"
    assert "timeout" in values["COMM_OPTIONS"], "timeout not passed from environment config"
    assert (
        values["COMM_OPTIONS"]["timeout"] == 60
    ), f"Environment timeout not respected, got {values['COMM_OPTIONS']['timeout']}"


@pytest.mark.integration
@pytest.mark.xfail(reason="Mock communicator registration issues in subprocess - to be fixed separately")
def test_agent_specific_communicator_type(multi_agent_project):
    """Test that the agent-specific communicator type is properly applied with all CLI paths."""
    # For this test, we need to add an agent with a different communicator type
    # But since we want to avoid actual MCP dependency, we'll modify the project config
    # to specify a mock communicator for testing

    # Add custom mock communicator to make testing easier
    mock_comm_dir = multi_agent_project / "extensions" / "mock"
    mock_comm_dir.mkdir(parents=True)
    mock_comm_file = mock_comm_dir / "communicator.py"

    # Write mock communicator implementation
    mock_content = """  # noqa: W291, W293
from typing import Any, Dict, Optional
from openmas.communication.base import BaseCommunicator, register_communicator


class MockCommunicator(BaseCommunicator):
    '''Mock communicator for testing.'''
    
    def __init__(
        self,
        agent_name,
        service_urls,
        timeout=30,
        http_port=None,
        server_mode=False,
        communicator_options=None,
        **kwargs
    ):
        '''Initialize with all potential parameters to prevent errors.'''
        super().__init__(agent_name, service_urls)
        # Store all parameters for testing
        self.timeout = timeout
        self.http_port = http_port
        self.server_mode = server_mode
        self.communicator_options = communicator_options or {}
        self.kwargs = kwargs
        
    async def send_request(self, *args, **kwargs):
        return {"result": "mock_response"}
        
    async def send_notification(self, *args, **kwargs):
        pass
        
    async def register_handler(self, *args, **kwargs):
        pass
        
    async def start(self):
        pass
        
    async def stop(self):
        pass


# Register the mock communicator
register_communicator("mock", MockCommunicator)
"""
    mock_comm_file.write_text(mock_content)

    # Now modify the project configuration to add an agent with the mock communicator
    with open(multi_agent_project / "openmas_project.yml", "r") as f:
        config = yaml.safe_load(f)

    # Add mock agent
    config["agents"]["mock_agent"] = {
        "module": "agents.diagnostic_agent",
        "class": "Agent",
        "communicator": "mock",
        "options": {"communicator_options": {"test_option": "test_value"}},
    }

    with open(multi_agent_project / "openmas_project.yml", "w") as f:
        yaml.dump(config, f)

    # Run the mock agent
    result = run_agent_in_subprocess(multi_agent_project, "mock_agent")

    # Print stdout and stderr for debugging
    print("\nSTDOUT:")
    print(result["stdout"])
    print("\nSTDERR:")
    print(result["stderr"])

    # Check the command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Verify the mock communicator was used
    assert "MOCK_COMM_INITIALIZED" in result["stdout"], "Mock communicator not initialized"
    assert "COMM_TYPE" in parse_stdout_for_values(result["stdout"]), "No COMM_TYPE in output"
    assert parse_stdout_for_values(result["stdout"])["COMM_TYPE"] == "MockCommunicator", "Wrong communicator type used"


@pytest.fixture
def mcp_styled_project(tmp_path):
    """Create a project with agents configured to use MCP but will use mocks for testing."""
    project_dir = tmp_path / "mcp_project"
    project_dir.mkdir()

    # Create standard directories
    (project_dir / "agents").mkdir()
    (project_dir / "config").mkdir()

    # Add a diagnostic agent
    agent_dir = project_dir / "agents" / "diagnostic_agent"
    agent_dir.mkdir()
    agent_file = agent_dir / "agent.py"
    agent_file.write_text(
        """  # noqa: W291, W293
import asyncio
import json
from openmas.agent import BaseAgent

class Agent(BaseAgent):
    \"\"\"Diagnostic agent.\"\"\"

    async def setup(self):
        \"\"\"Set up the agent.\"\"\"
        # Report communicator information
        comm_type = self.communicator.__class__.__name__
        print(f"COMM_TYPE:{comm_type}")
        
        # Report communicator options if available
        if hasattr(self.config, "communicator_options"):
            print(f"COMM_OPTIONS:{json.dumps(self.config.communicator_options)}")
            
        # Report communicator type from config
        if hasattr(self.config, "communicator_type"):
            print(f"CONFIG_COMM_TYPE:{self.config.communicator_type}")

    async def run(self):
        \"\"\"Run the agent.\"\"\"
        await asyncio.sleep(0.1)
        return

    async def shutdown(self):
        \"\"\"Shut down the agent.\"\"\"
        pass
"""
    )

    # Create project configuration with MCP agents
    project_config = {
        "name": "mcp_test_project",
        "version": "0.1.0",
        "agents": {
            "mcp_sse_agent": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                "communicator": "mock",  # For testing, we'll use mock instead of mcp-sse
                "options": {"communicator_options": {"server_mode": True, "http_port": 9191}},
            },
            "http_fallback_agent": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                # No communicator specified, should use default http
            },
        },
        "default_config": {
            "log_level": "INFO",
            "communicator_type": "http",
        },
    }

    with open(project_dir / "openmas_project.yml", "w") as f:
        yaml.dump(project_config, f)

    # Mock communicator extension
    mock_comm_dir = project_dir / "extensions" / "mock"
    mock_comm_dir.mkdir(parents=True)
    mock_comm_file = mock_comm_dir / "communicator.py"

    # Write mock communicator implementation
    mock_content = """  # noqa: W291, W293
from typing import Any, Callable, Dict, Optional
from openmas.communication.base import BaseCommunicator

class MockCommunicator(BaseCommunicator):
    \"\"\"Mock communicator for testing.\"\"\"
    
    def __init__(
        self, 
        agent_name, 
        service_urls, 
        timeout=30, 
        http_port=None,
        port=None,  # Keep for backward compatibility
        server_mode=False, 
        communicator_options=None, 
        **kwargs
    ):
        \"\"\"Initialize with all potential parameters to prevent errors.\"\"\"
        super().__init__(agent_name, service_urls)
        # Store all parameters for testing
        self.timeout = timeout
        self.http_port = http_port or port  # Use port as fallback for backward compatibility
        self.server_mode = server_mode
        self.communicator_options = communicator_options or {}
        self.kwargs = kwargs
        print(f"MOCK_COMM_INITIALIZED with kwargs: {kwargs}")
        if server_mode:
            print(f"MOCK_SERVER_MODE:{server_mode}")
        if self.http_port:
            print(f"MOCK_HTTP_PORT:{self.http_port}")
    
    async def send_request(self, *args, **kwargs):
        return {}
        
    async def send_notification(self, *args, **kwargs):
        pass
        
    async def register_handler(self, *args, **kwargs):
        pass
        
    async def start(self):
        pass
        
    async def stop(self):
        pass
"""
    mock_comm_file.write_text(mock_content)

    # Add communicator registration
    init_file = mock_comm_dir / "__init__.py"
    init_content = """
from openmas.communication.base import register_communicator
from extensions.mock.communicator import MockCommunicator

# Register the communicator so it can be found by name
register_communicator("mock", MockCommunicator)
"""
    init_file.write_text(init_content)

    return project_dir


@pytest.mark.integration
@pytest.mark.xfail(reason="Mock communicator registration issues in subprocess - to be fixed separately")
def test_communicator_type_selection(mcp_styled_project):
    """Test that the correct communicator type is selected based on agent configuration."""
    # Update project YAML to add extension paths
    with open(mcp_styled_project / "openmas_project.yml", "r") as f:
        config = yaml.safe_load(f)

    config["extension_paths"] = ["extensions"]

    with open(mcp_styled_project / "openmas_project.yml", "w") as f:
        yaml.dump(config, f)

    # Run the agent with mock communicator
    result = run_agent_in_subprocess(mcp_styled_project, "mcp_sse_agent")

    # Check the command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Verify the mock communicator was used with correct options
    values = parse_stdout_for_values(result["stdout"])
    assert "COMM_TYPE" in values, "No COMM_TYPE in output"
    assert values["COMM_TYPE"] == "MockCommunicator", f"Expected MockCommunicator, got {values['COMM_TYPE']}"
    assert "MOCK_COMM_INITIALIZED" in result["stdout"], "Mock communicator not initialized"
    assert "server_mode" in result["stdout"], "server_mode option not passed"
    assert "port" in result["stdout"], "port option not passed"

    # Run the agent that should fall back to HTTP
    result = run_agent_in_subprocess(mcp_styled_project, "http_fallback_agent")

    # Check the command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Verify HTTP communicator was used
    values = parse_stdout_for_values(result["stdout"])
    assert "COMM_TYPE" in values, "No COMM_TYPE in output"
    assert values["COMM_TYPE"] == "HttpCommunicator", f"Expected HttpCommunicator, got {values['COMM_TYPE']}"


@pytest.mark.integration
def test_issue3_mcp_sse_communicator_and_port_config(multi_agent_project):
    """Test specifically addressing GitHub issue #3 where MCP/SSE communicator and port config are ignored.

    The issue reports that when configuring agents to use MCP/SSE in openmas_project.yml,
    the OpenMAS CLI ignores this configuration and defaults to HTTP communicator.
    Additionally, port configuration is ignored, with the system always using port 8000.
    """
    # Create a simplified MCP mock for testing
    mock_dir = multi_agent_project / "extensions" / "mock_mcp"
    mock_dir.mkdir(parents=True)

    # Create a very simple mock communicator that just reports its configuration
    mock_file = mock_dir / "communicator.py"
    mock_content = """  # noqa: W291, W293
import json
from openmas.communication.base import BaseCommunicator

class McpSseCommunicator(BaseCommunicator):
    '''Simplified Mock MCP/SSE Communicator for testing.'''
    
    def __init__(
        self,
        agent_name,
        service_urls,
        **kwargs
    ):
        '''Initialize with minimal dependencies.'''
        super().__init__(agent_name, service_urls)
        self.kwargs = kwargs
        
        # Extract important config values
        self.server_mode = kwargs.get('server_mode', False)
        self.http_port = kwargs.get('http_port', 8000)
        
        # Print key information for test assertions
        print(f"MOCK_MCP_SSE_INITIALIZED:{json.dumps({'port': self.http_port, 'server_mode': self.server_mode})}")
        
    async def start(self):
        print(f"MOCK_MCP_SSE_START:{self.http_port}")
        
    async def stop(self):
        print("MOCK_MCP_SSE_STOP")
        
    async def send_request(self, *args, **kwargs):
        return {}
        
    async def send_notification(self, *args, **kwargs):
        pass
        
    async def register_handler(self, *args, **kwargs):
        pass
"""
    mock_file.write_text(mock_content)

    # Register the mock communicator
    init_file = mock_dir / "__init__.py"
    init_content = """
from openmas.communication import register_communicator
from extensions.mock_mcp.communicator import McpSseCommunicator

# Register mock MCP/SSE communicator
register_communicator("mcp-sse", McpSseCommunicator)
"""
    init_file.write_text(init_content)

    # Load and update project configuration
    project_path = multi_agent_project / "openmas_project.yml"
    with open(project_path, "r") as f:
        config = yaml.safe_load(f)

    # Add extension path
    config["extension_paths"] = ["extensions"]

    # Add agent using MCP/SSE communicator
    mcp_sse_config = {
        "module": "agents.diagnostic_agent",
        "class": "Agent",
        "communicator": "mcp-sse",
        "options": {"communicator_options": {"server_mode": True, "http_port": 8765}},
    }

    # Add agent to project configuration
    config["agents"]["mcp_sse_agent"] = mcp_sse_config

    # Save updated configuration
    with open(project_path, "w") as f:
        yaml.dump(config, f)

    # Run the agent
    result = run_agent_in_subprocess(multi_agent_project, "mcp_sse_agent")

    # Print stdout and stderr for debugging
    print("\nSTDOUT:")
    print(result["stdout"])
    print("\nSTDERR:")
    print(result["stderr"])

    # Check for success
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Verify MCP/SSE communicator was used with correct settings
    values = parse_stdout_for_values(result["stdout"])

    # Check for the communicator type
    assert "COMM_TYPE" in values, "No communicator type in output"
    assert values["COMM_TYPE"] == "McpSseCommunicator", f"Expected McpSseCommunicator but got {values['COMM_TYPE']}"

    # Check for the communicator options
    assert "COMM_OPTIONS" in values, "No communicator options in output"
    options = values["COMM_OPTIONS"]
    assert options.get("http_port") == 8765, f"Expected port 8765, got {options.get('http_port')}"
    assert options.get("server_mode") is True, "Expected server_mode to be True"

    # Check the actual server port in the log message
    assert "Creating FastMCP server on 0.0.0.0:8765" in result["stdout"], "Server not created on expected port"

    # This verifies that Issue #3 is fixed - the agent successfully uses the MCP/SSE communicator
    # with the port configuration specified in the project.yml file


# Run only when tox marker is present or specifically requested
if __name__ == "__main__":
    # This allows running individual tests manually
    pytest.main(["-xvs", __file__])
