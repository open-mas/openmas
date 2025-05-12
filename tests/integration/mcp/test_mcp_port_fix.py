"""Integration test for MCP/SSE port configuration fix."""

import json
import subprocess
import sys

import pytest
import yaml

# Skip tests if MCP is not available
try:
    import mcp  # noqa

    HAS_MCP = True
    skip_reason = "MCP package is installed"
except ImportError:
    HAS_MCP = False
    skip_reason = "MCP package not installed"


@pytest.fixture
def mcp_port_fix_project(tmp_path):
    """Create a test project for verifying the port configuration fix."""
    # Create project directory
    project_dir = tmp_path / "mcp_port_test_project"
    project_dir.mkdir()

    # Create standard directories
    (project_dir / "agents").mkdir()
    (project_dir / "config").mkdir()

    # Create a test agent
    agent_dir = project_dir / "agents" / "test_agent"
    agent_dir.mkdir()
    (agent_dir / "__init__.py").write_text('from .agent import Agent\n\n__all__ = ["Agent"]\n')

    agent_file = agent_dir / "agent.py"
    agent_file.write_text(
        """
import asyncio
import json
from openmas.agent import BaseAgent


class Agent(BaseAgent):
    \"\"\"Test agent for MCP port configuration.\"\"\"

    async def setup(self):
        \"\"\"Set up the agent and print configuration.\"\"\"
        # Print communicator type
        comm_type = self.communicator.__class__.__name__
        print(f"COMM_TYPE:{comm_type}")

        # Print communicator configuration
        if hasattr(self.config, "communicator_type"):
            print(f"CONFIG_COMM_TYPE:{self.config.communicator_type}")

        if hasattr(self.config, "communicator_options"):
            # Print as JSON for easy parsing
            print(f"COMM_OPTIONS:{json.dumps(self.config.communicator_options)}")

        # Print the actual port used by the MCP/SSE communicator
        if hasattr(self.communicator, "http_port"):
            print(f"MCP_SSE_PORT:{self.communicator.http_port}")

        # Report server initialization details if available
        if hasattr(self.communicator, "fastmcp_server") and self.communicator.fastmcp_server is not None:
            if hasattr(self.communicator.fastmcp_server, "port"):
                print(f"FASTMCP_PORT:{self.communicator.fastmcp_server.port}")

    async def run(self):
        \"\"\"Run the agent briefly for testing.\"\"\"
        print("AGENT_STARTED")
        await asyncio.sleep(0.5)  # Short sleep for test
        print("AGENT_COMPLETED")
        return

    async def shutdown(self):
        \"\"\"Shut down the agent.\"\"\"
        print("AGENT_SHUTDOWN")
"""
    )

    # Create project configuration with MCP/SSE communicator and custom port
    project_config = {
        "name": "mcp_port_fix_test",
        "version": "0.1.0",
        "agents": {
            "test_agent": {
                "module": "agents.test_agent",
                "class": "Agent",
                "communicator": "mcp-sse",
                "options": {
                    "communicator_options": {
                        "server_mode": True,
                        "http_port": 9999,  # Custom port
                    }
                },
            }
        },
    }

    with open(project_dir / "openmas_project.yml", "w") as f:
        yaml.dump(project_config, f)

    return project_dir


def run_agent_in_subprocess(project_dir, agent_name, timeout=10):
    """Run an agent in a subprocess and capture its output."""
    cmd = [sys.executable, "-m", "openmas.cli", "run", agent_name, "--project-dir", str(project_dir)]

    # Run command with subprocess
    try:
        process = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True, timeout=timeout)
        return {"stdout": process.stdout, "stderr": process.stderr, "returncode": process.returncode}
    except subprocess.TimeoutExpired:
        pytest.fail(f"Command timed out after {timeout} seconds")
        return {}  # Added return statement to fix mypy error


def parse_stdout_for_values(stdout):
    """Parse stdout for key-value pairs."""
    result = {}
    for line in stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            # Try to parse JSON for structured values
            if key in ("COMM_OPTIONS",):
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
                    result[key] = value
            # Parse integers
            elif key in ("MCP_SSE_PORT", "HTTP_PORT", "FASTMCP_PORT"):
                try:
                    result[key] = int(value)
                except ValueError:
                    result[key] = value
            else:
                result[key] = value
    return result


@pytest.mark.mcp
@pytest.mark.skipif(not HAS_MCP, reason=skip_reason)
def test_mcp_sse_port_fix(mcp_port_fix_project):
    """Test that the MCP/SSE port configuration fix works correctly.

    This test verifies that the port specified in communicator_options is correctly
    passed to the FastMCP server instance.
    """
    # Run the agent with MCP/SSE communicator configuration
    result = run_agent_in_subprocess(mcp_port_fix_project, "test_agent")

    # Print debug output
    print(f"STDOUT: {result['stdout']}")
    print(f"STDERR: {result['stderr']}")

    # Check if command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Parse the output for diagnostic values
    values = parse_stdout_for_values(result["stdout"])

    # Verify that the MCP/SSE communicator was used
    assert "COMM_TYPE" in values, "No COMM_TYPE in output"
    assert values["COMM_TYPE"] == "McpSseCommunicator", f"Wrong communicator type: {values['COMM_TYPE']}"

    # Verify the configuration has the correct http_port
    assert "COMM_OPTIONS" in values, "No COMM_OPTIONS in output"
    assert "http_port" in values["COMM_OPTIONS"], "No http_port in communicator options"
    assert (
        values["COMM_OPTIONS"]["http_port"] == 9999
    ), f"Wrong http_port in options: {values['COMM_OPTIONS']['http_port']}"

    # Verify the actual port passed to the MCP/SSE communicator
    assert "MCP_SSE_PORT" in values, "No MCP_SSE_PORT in output"
    assert values["MCP_SSE_PORT"] == 9999, f"Wrong MCP_SSE_PORT: {values['MCP_SSE_PORT']}"
