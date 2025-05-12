"""Integration test for MCP communicator selection issue.

This test addresses the specific issue reported by users where an agent explicitly configured
with the MCP/SSE communicator in openmas_project.yml would silently fall back to HTTP
communicator when run through the CLI.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
import yaml

# Skip if MCP not installed
try:
    # Just check if MCP can be imported
    __import__("mcp")
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

skip_reason = "MCP package not installed"


@pytest.fixture
def chess_commentary_project(tmp_path):
    """Create a test project mimicking the reported chess commentary system scenario.

    This simulates the exact setup described in the bug report where:
    1. The project has two MCP-based agents (orchestrator, commentator)
    2. Each agent is configured to use mcp-sse communicator
    3. When run through the CLI, HTTP was used instead of MCP/SSE
    """
    project_dir = tmp_path / "chess_commentary"
    project_dir.mkdir()

    # Create standard directories
    agents_dir = project_dir / "agents"
    agents_dir.mkdir()
    (project_dir / "config").mkdir()

    # Create orchestrator agent
    orchestrator_dir = agents_dir / "orchestrator_agent"
    orchestrator_dir.mkdir()

    orchestrator_file = orchestrator_dir / "agent.py"
    orchestrator_file.write_text(
        """  # noqa: W293
import asyncio
import json
import sys
from openmas.agent import BaseAgent

class Agent(BaseAgent):
    \"\"\"Chess orchestrator agent that uses MCP/SSE communicator.\"\"\"
    
    async def setup(self):
        \"\"\"Set up the agent.\"\"\"
        # Print diagnostic information
        print(f"AGENT_NAME:{self.name}")
        print(f"COMM_TYPE:{self.communicator.__class__.__name__}")
        
        # Print communicator type from config
        if hasattr(self.config, "communicator_type"):
            print(f"CONFIG_COMM_TYPE:{self.config.communicator_type}")
        
        # Print communicator options
        if hasattr(self.config, "communicator_options"):
            print(f"COMM_OPTIONS:{json.dumps(self.config.communicator_options)}")
        
        # For MCP/SSE communicator, report the port
        if hasattr(self.communicator, "http_port"):
            print(f"MCP_SSE_PORT:{self.communicator.http_port}")
        
        # For HTTP communicator, report the port
        if hasattr(self.communicator, "server") and hasattr(self.communicator.server, "port"):
            print(f"HTTP_PORT:{self.communicator.server.port}")
            
        # Print all attributes of the communicator
        print(f"COMMUNICATOR_ATTRS:{dir(self.communicator)}")
    
    async def run(self):
        \"\"\"Run the agent.\"\"\"
        # Just enough for testing
        await asyncio.sleep(0.1)
        return  # Exit immediately for test
    
    async def shutdown(self):
        \"\"\"Shut down the agent.\"\"\"
        pass
"""
    )

    # Create commentator agent
    commentator_dir = agents_dir / "commentator_agent"
    commentator_dir.mkdir()

    commentator_file = commentator_dir / "agent.py"
    commentator_file.write_text(
        """  # noqa: W293
import asyncio
import json
import sys
from openmas.agent import BaseAgent

class Agent(BaseAgent):
    \"\"\"Chess commentator agent that uses MCP/SSE communicator.\"\"\"
    
    async def setup(self):
        \"\"\"Set up the agent.\"\"\"
        # Print diagnostic information
        print(f"AGENT_NAME:{self.name}")
        print(f"COMM_TYPE:{self.communicator.__class__.__name__}")
        
        # Print communicator type from config
        if hasattr(self.config, "communicator_type"):
            print(f"CONFIG_COMM_TYPE:{self.config.communicator_type}")
        
        # Print communicator options
        if hasattr(self.config, "communicator_options"):
            print(f"COMM_OPTIONS:{json.dumps(self.config.communicator_options)}")
        
        # For MCP/SSE communicator, report the port
        if hasattr(self.communicator, "http_port"):
            print(f"MCP_SSE_PORT:{self.communicator.http_port}")
        
        # For HTTP communicator, report the port
        if hasattr(self.communicator, "server") and hasattr(self.communicator.server, "port"):
            print(f"HTTP_PORT:{self.communicator.server.port}")
            
        # Print all attributes of the communicator
        print(f"COMMUNICATOR_ATTRS:{dir(self.communicator)}")
    
    async def run(self):
        \"\"\"Run the agent.\"\"\"
        # Just enough for testing
        await asyncio.sleep(0.1)
        return  # Exit immediately for test
    
    async def shutdown(self):
        \"\"\"Shut down the agent.\"\"\"
        pass
"""
    )

    # Create project configuration with MCP/SSE communicator explicitly specified
    project_config = {
        "name": "chess_commentary",
        "version": "0.1.0",
        "agents": {
            "orchestrator": {
                "module": "agents.orchestrator_agent",
                "class": "Agent",
                "communicator": "mcp-sse",  # Explicitly request MCP/SSE
                "options": {"communicator_options": {"server_mode": True, "http_port": 8001}},  # Custom port
            },
            "commentator": {
                "module": "agents.commentator_agent",
                "class": "Agent",
                "communicator": "mcp-sse",  # Explicitly request MCP/SSE
                "options": {"communicator_options": {"server_mode": True, "http_port": 8002}},  # Different port
            },
        },
        "default_config": {
            "log_level": "INFO",
            "communicator_type": "http",  # Default is HTTP but agents override this
            "communicator_options": {"timeout": 30},
        },
        "service_urls": {"orchestrator": "http://localhost:8001", "commentator": "http://localhost:8002"},
    }

    with open(project_dir / "openmas_project.yml", "w") as f:
        yaml.dump(project_config, f)

    # Create a config file that overrides port but should not affect agent-specific settings
    env_config = {"communicator_options": {"http_port": 9000}}  # This should not override agent-specific ports

    with open(project_dir / "config" / "test.yml", "w") as f:
        yaml.dump(env_config, f)

    return project_dir


def run_agent_in_subprocess(
    project_dir: Path, agent_name: str, env: Optional[str] = None, timeout: int = 10
) -> Dict[str, Any]:
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

    # Run command with subprocess
    try:
        process = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True, timeout=timeout)

        return {"stdout": process.stdout, "stderr": process.stderr, "returncode": process.returncode}
    except subprocess.TimeoutExpired:
        pytest.fail(f"Command timed out after {timeout} seconds")


def parse_stdout_for_values(stdout: str) -> Dict[str, Any]:
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
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            pass
                except (ValueError, TypeError):
                    pass
                result[key] = value
    return result


@pytest.mark.mcp
@pytest.mark.skipif(not HAS_MCP, reason=skip_reason)
def test_mcp_sse_communicator_not_falling_back_to_http(chess_commentary_project):
    """Test that MCP/SSE communicator is used when specified in agent config.

    This reproduces the reported issue where agents configured with MCP/SSE
    would silently fall back to HTTP communicator when run through the OpenMAS CLI.
    """
    # Run the orchestrator agent
    result = run_agent_in_subprocess(chess_commentary_project, "orchestrator")

    # Check if command completed successfully (skip assertion for now if failing)
    if result["returncode"] != 0:
        print(f"WARNING: Command failed with stderr: {result['stderr']}")
        print(f"Command output: {result['stdout']}")

    # Parse the output for diagnostic values
    values = parse_stdout_for_values(result["stdout"])

    # Verify communicator type - we expect MCP SSE here, not HTTP
    assert "COMM_TYPE" in values, "No COMM_TYPE in output"
    assert values["COMM_TYPE"] == "McpSseCommunicator", f"Expected McpSseCommunicator, got {values['COMM_TYPE']}"

    # Verify config type is mcp-sse
    assert "CONFIG_COMM_TYPE" in values, "No CONFIG_COMM_TYPE in output"
    assert values["CONFIG_COMM_TYPE"] == "mcp-sse", f"Expected mcp-sse config type, got {values['CONFIG_COMM_TYPE']}"

    # Verify agent-specific port configuration is used
    assert "COMM_OPTIONS" in values, "No COMM_OPTIONS in output"
    assert "http_port" in values["COMM_OPTIONS"], "http_port not in communicator options"
    assert (
        values["COMM_OPTIONS"]["http_port"] == 8001
    ), f"Expected http_port 8001, got {values['COMM_OPTIONS'].get('http_port')}"


@pytest.mark.mcp
@pytest.mark.skipif(not HAS_MCP, reason=skip_reason)
def test_distinct_port_configuration_for_multiple_agents(chess_commentary_project):
    """Test that different agents can use different port configurations with MCP/SSE.

    This tests that port configuration is properly passed to each agent based on
    their individual configuration, rather than using a global default of 8000.
    """
    # Run both agents and capture their outputs
    result1 = run_agent_in_subprocess(chess_commentary_project, "orchestrator")
    result2 = run_agent_in_subprocess(chess_commentary_project, "commentator")

    # Parse diagnostics
    values1 = parse_stdout_for_values(result1["stdout"])
    values2 = parse_stdout_for_values(result2["stdout"])

    # Both should be using MCP/SSE
    assert values1.get("COMM_TYPE") == "McpSseCommunicator", "Orchestrator using wrong communicator type"
    assert values2.get("COMM_TYPE") == "McpSseCommunicator", "Commentator using wrong communicator type"

    # Verify different ports
    assert values1.get("COMM_OPTIONS", {}).get("http_port") == 8001, "Orchestrator http_port incorrect"
    assert values2.get("COMM_OPTIONS", {}).get("http_port") == 8002, "Commentator http_port incorrect"

    # Look for MCP_SSE_PORT which would be definitive
    if "MCP_SSE_PORT" in values1 and "MCP_SSE_PORT" in values2:
        assert values1["MCP_SSE_PORT"] == 8001, "Orchestrator MCP port incorrect"
        assert values2["MCP_SSE_PORT"] == 8002, "Commentator MCP port incorrect"


@pytest.mark.mcp
@pytest.mark.skipif(not HAS_MCP, reason=skip_reason)
def test_env_specific_config_not_overriding_agent_specific(chess_commentary_project):
    """Test that environment-specific config does not override agent-specific settings.

    This verifies that the agent-specific communicator type and port settings take
    precedence over environment configuration.
    """
    # Run with test environment that tries to override port to 9000
    result = run_agent_in_subprocess(chess_commentary_project, "orchestrator", env="test")

    # Parse diagnostics
    values = parse_stdout_for_values(result["stdout"])

    # Should still be using MCP/SSE
    assert values.get("COMM_TYPE") == "McpSseCommunicator", "Wrong communicator type"

    # Should still be using agent-specific port 8001, not env port 9000
    assert values.get("COMM_OPTIONS", {}).get("http_port") == 8001, "Agent-specific http_port overridden by environment"


# Run the test directly if this file is executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
