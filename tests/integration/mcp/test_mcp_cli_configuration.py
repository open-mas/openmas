"""Integration tests for CLI-based MCP configuration.

These tests verify that MCP configuration through the CLI and openmas_project.yml
works correctly, focusing on the specific issues reported by users:

1. Proper selection of MCP/SSE communicator instead of falling back to HTTP
2. Correct port configuration for MCP/SSE communicators
3. Proper handling of communicator_options
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
import yaml

# Skip the test if MCP is not installed
try:
    # Just check if MCP can be imported
    __import__("mcp")
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

skip_reason = "MCP package not installed"


@pytest.fixture
def mcp_project(tmp_path):
    """Create a project with MCP-based agents for testing CLI configuration."""
    project_dir = tmp_path / "mcp_project"
    project_dir.mkdir()

    # Create standard directories
    (project_dir / "agents").mkdir()
    (project_dir / "shared").mkdir()
    (project_dir / "config").mkdir()

    # Create a diagnostic agent that reports its communicator configuration
    agent_dir = project_dir / "agents" / "diagnostic_agent"
    agent_dir.mkdir()
    agent_file = agent_dir / "agent.py"
    agent_file.write_text(
        """  # noqa: W293
import asyncio
import json
import os
import sys
from openmas.agent import BaseAgent


class Agent(BaseAgent):
    \"\"\"A diagnostic agent that reports detailed information about its configuration.\"\"\"

    async def setup(self):
        \"\"\"Set up the agent.\"\"\"
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

        # For MCP/SSE communicator, extract port if available
        if hasattr(self.communicator, "http_port"):
            print(f"MCP_SSE_PORT:{self.communicator.http_port}")

        # For HTTP communicator, extract port if available
        if hasattr(self.communicator, "server") and hasattr(self.communicator.server, "port"):
            print(f"HTTP_PORT:{self.communicator.server.port}")

    async def run(self):
        \"\"\"Run the agent briefly for testing.\"\"\"
        await asyncio.sleep(0.1)
        print("AGENT_COMPLETED")
        return  # Exit immediately for testing

    async def shutdown(self):
        \"\"\"Shut down the agent.\"\"\"
        print("AGENT_SHUTDOWN")
"""
    )

    # Create project configuration file with MCP agents
    project_config = {
        "name": "mcp_test_project",
        "version": "0.1.0",
        "agents": {
            # Agent explicitly configured for MCP/SSE
            "mcp_sse_agent": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                "communicator": "mcp-sse",  # Explicitly set MCP/SSE communicator
                "options": {
                    "communicator_options": {
                        "server_mode": True,
                        "http_port": 8765,  # Use the canonical http_port parameter
                    }
                },
            },
            # Agent with default communicator (should be HTTP)
            "default_http_agent": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                # No communicator specified - should use default
            },
            # Agent using deprecated port parameter (for testing deprecation warning)
            "deprecated_port_agent": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                "communicator": "mcp-sse",
                "options": {
                    "communicator_options": {
                        "server_mode": True,
                        "port": 8766,  # Use legacy port parameter to test conversion
                    }
                },
            },
        },
        "shared_paths": ["shared"],
        "default_config": {
            "log_level": "INFO",
            "communicator_type": "http",  # Default communicator type
            "communicator_options": {"timeout": 30},
        },
    }

    with open(project_dir / "openmas_project.yml", "w") as f:
        yaml.dump(project_config, f)

    # Create environment-specific config with different port
    env_config = {
        "communicator_options": {
            "http_port": 9999,  # This should be overridden by agent-specific settings
            "timeout": 60,  # This should be merged with agent-specific settings
        }
    }

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
        return {}


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
                            import json

                            value = json.loads(value)
                        except json.JSONDecodeError:
                            pass
                except (ValueError, TypeError):
                    pass
                result[key] = value
    return result


@pytest.mark.mcp
@pytest.mark.skipif(not HAS_MCP, reason=skip_reason)
def test_mcp_sse_communicator_selection(mcp_project):
    """Test that the MCP/SSE communicator is properly selected when specified in agent config.

    This test verifies that the MCP/SSE communicator is correctly selected when specified
    in the agent configuration, rather than falling back to the default HTTP communicator.

    This specifically tests the issue reported by users where the system was ignoring the
    communicator_type: mcp-sse directive in openmas_project.yml and using HTTP instead.
    """
    # Run the agent with MCP/SSE communicator configuration
    result = run_agent_in_subprocess(mcp_project, "mcp_sse_agent")

    # Check if command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Parse the output for diagnostic values
    values = parse_stdout_for_values(result["stdout"])

    # Verify that the MCP/SSE communicator was used
    assert "COMM_TYPE" in values, "No COMM_TYPE in output"
    assert values["COMM_TYPE"] == "McpSseCommunicator", f"Expected McpSseCommunicator, got {values['COMM_TYPE']}"

    # Verify that the configuration shows MCP/SSE as the communicator type
    assert "CONFIG_COMM_TYPE" in values, "No CONFIG_COMM_TYPE in output"
    assert values["CONFIG_COMM_TYPE"] == "mcp-sse", f"Expected mcp-sse config type, got {values['CONFIG_COMM_TYPE']}"


@pytest.mark.mcp
@pytest.mark.skipif(not HAS_MCP, reason=skip_reason)
def test_mcp_sse_port_configuration(mcp_project):
    """Test that port configuration for MCP/SSE communicator is correctly applied.

    This test verifies that the http_port specified in the agent's communicator_options
    is correctly applied to the MCP/SSE communicator.

    This specifically tests the issue reported by users where port configuration was being
    ignored in favor of default port 8000.
    """
    # Run the agent with MCP/SSE communicator configuration
    result = run_agent_in_subprocess(mcp_project, "mcp_sse_agent")

    # Check if command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Parse the output for diagnostic values
    values = parse_stdout_for_values(result["stdout"])

    # Verify that the port from agent-specific config was applied
    assert "COMM_OPTIONS" in values, "No COMM_OPTIONS in output"
    assert "http_port" in values["COMM_OPTIONS"], "http_port not in communicator options"
    assert (
        values["COMM_OPTIONS"]["http_port"] == 8765
    ), f"Expected http_port 8765, got {values['COMM_OPTIONS']['http_port']}"

    # If MCP_SSE_PORT is in output, verify it matches the configured port
    if "MCP_SSE_PORT" in values:
        assert values["MCP_SSE_PORT"] == 8765, f"Expected MCP_SSE_PORT 8765, got {values['MCP_SSE_PORT']}"


@pytest.mark.mcp
@pytest.mark.skipif(not HAS_MCP, reason=skip_reason)
def test_default_communicator_fallback(mcp_project):
    """Test that default communicator is correctly used when none is specified.

    This test verifies that the default HTTP communicator is used when no specific
    communicator is specified in the agent configuration.
    """
    # Run the agent with default communicator configuration
    result = run_agent_in_subprocess(mcp_project, "default_http_agent")

    # Check if command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Parse the output for diagnostic values
    values = parse_stdout_for_values(result["stdout"])

    # Verify that the HTTP communicator was used (default)
    assert "COMM_TYPE" in values, "No COMM_TYPE in output"
    assert values["COMM_TYPE"] == "HttpCommunicator", f"Expected HttpCommunicator, got {values['COMM_TYPE']}"

    # Verify that the configuration shows HTTP as the communicator type
    assert "CONFIG_COMM_TYPE" in values, "No CONFIG_COMM_TYPE in output"
    assert values["CONFIG_COMM_TYPE"] == "http", f"Expected http config type, got {values['CONFIG_COMM_TYPE']}"


@pytest.mark.mcp
@pytest.mark.skipif(not HAS_MCP, reason=skip_reason)
def test_env_specific_communicator_options(mcp_project):
    """Test that environment-specific communicator options are correctly applied.

    This test verifies that communicator options specified in the environment-specific
    configuration file are correctly applied when not overridden by agent-specific options.
    """
    # Run the default agent with test environment
    result = run_agent_in_subprocess(mcp_project, "default_http_agent", env="test")

    # Check if command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Parse the output for diagnostic values
    values = parse_stdout_for_values(result["stdout"])

    # Verify that the port from environment config was applied
    assert "COMM_OPTIONS" in values, "No COMM_OPTIONS in output"
    assert "http_port" in values["COMM_OPTIONS"], "http_port not in communicator options"
    assert values["COMM_OPTIONS"]["http_port"] == 9999, f"Wrong port value: {values['COMM_OPTIONS']}"

    # If HTTP_PORT is in output, verify it matches the configured port
    if "HTTP_PORT" in values:
        assert values["HTTP_PORT"] == 9999, f"Expected HTTP_PORT 9999, got {values['HTTP_PORT']}"


@pytest.mark.mcp
@pytest.mark.skipif(not HAS_MCP, reason=skip_reason)
def test_agent_specific_options_precedence(mcp_project):
    """Test that agent-specific communicator options take precedence over environment config.

    This test verifies that communicator options specified in the agent configuration
    take precedence over those specified in the environment-specific configuration.
    """
    # Run the MCP/SSE agent with test environment
    result = run_agent_in_subprocess(mcp_project, "mcp_sse_agent", env="test")

    # Print debug output
    print(f"STDOUT CONTENT: {result['stdout']}")
    print(f"STDERR CONTENT: {result['stderr']}")

    # Check if command completed successfully
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Parse the output for diagnostic values
    values = parse_stdout_for_values(result["stdout"])

    # Verify that the port from agent-specific config was used, not environment config
    assert "COMM_OPTIONS" in values, "No COMM_OPTIONS in output"
    assert "http_port" in values["COMM_OPTIONS"], "http_port not in communicator options"
    assert values["COMM_OPTIONS"]["http_port"] == 8765, f"Wrong port value: {values['COMM_OPTIONS']}"

    # If MCP_SSE_PORT is in output, verify it matches agent-specific port
    if "MCP_SSE_PORT" in values:
        assert values["MCP_SSE_PORT"] == 8765, f"Expected MCP_SSE_PORT 8765, got {values['MCP_SSE_PORT']}"  # noqa: W293


@pytest.mark.mcp  # noqa: W293
@pytest.mark.skipif(not HAS_MCP, reason=skip_reason)
def test_port_http_port_compatibility(tmp_path):  # noqa: W293
    """Test http_port parameter standardization for MCP/SSE communicator.

    This test verifies that the 'http_port' parameter is correctly recognized and utilized
    by the MCP/SSE communicator and that legacy 'port' parameters are properly rejected.
    """
    # Create project directory
    project_dir = tmp_path / "port_compatibility_project"
    project_dir.mkdir()

    # Create standard directories
    (project_dir / "agents").mkdir()
    (project_dir / "shared").mkdir()
    (project_dir / "config").mkdir()

    # Create diagnostic agent
    agent_dir = project_dir / "agents" / "diagnostic_agent"
    agent_dir.mkdir()
    agent_file = agent_dir / "agent.py"
    agent_file.write_text(
        """
import asyncio
import json
import os
import sys
from openmas.agent import BaseAgent


class Agent(BaseAgent):
    \"\"\"A diagnostic agent that reports detailed information about its configuration.\"\"\"

    async def setup(self):
        \"\"\"Set up the agent.\"\"\"
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

        # For MCP/SSE communicator, extract port if available
        if hasattr(self.communicator, "http_port"):
            print(f"MCP_SSE_PORT:{self.communicator.http_port}")

        # For HTTP communicator, extract port if available
        if hasattr(self.communicator, "server") and hasattr(self.communicator.server, "port"):
            print(f"HTTP_PORT:{self.communicator.server.port}")

    async def run(self):
        \"\"\"Run the agent briefly for testing.\"\"\"
        await asyncio.sleep(0.1)
        print("AGENT_COMPLETED")
        return  # Exit immediately for testing

    async def shutdown(self):
        \"\"\"Shut down the agent.\"\"\"
        print("AGENT_SHUTDOWN")
"""
    )

    # Create project with two agents: one using standard http_port and one using legacy port
    project_config = {
        "name": "port_compatibility_test",
        "version": "0.1.0",
        "agents": {
            # Agent using standard http_port parameter
            "standard_agent": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                "communicator": "mcp-sse",
                "options": {
                    "communicator_options": {"server_mode": True, "http_port": 8765}  # Using standard parameter
                },
            },
            # Agent using legacy port parameter
            "legacy_agent": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                "communicator": "mcp-sse",
                "options": {
                    "communicator_options": {
                        "server_mode": True,
                        "port": 8766,  # Using legacy parameter that should be rejected
                    }
                },
            },
        },
        "shared_paths": ["shared"],
        "default_config": {
            "log_level": "INFO",
            "communicator_type": "http",
        },
    }

    with open(project_dir / "openmas_project.yml", "w") as f:
        yaml.dump(project_config, f)

    # Test agent with standard http_port parameter
    result_standard = run_agent_in_subprocess(project_dir, "standard_agent")
    assert result_standard["returncode"] == 0, f"Command failed: {result_standard['stderr']}"
    values_standard = parse_stdout_for_values(result_standard["stdout"])

    # Verify that http_port was correctly used
    assert "COMM_OPTIONS" in values_standard, "No COMM_OPTIONS in output"
    assert "http_port" in values_standard["COMM_OPTIONS"], "http_port not in communicator options"
    assert (
        values_standard["COMM_OPTIONS"]["http_port"] == 8765
    ), f"Expected http_port 8765, got {values_standard['COMM_OPTIONS']['http_port']}"

    # Verify that MCP_SSE_PORT matches the configured http_port
    if "MCP_SSE_PORT" in values_standard:
        assert (
            values_standard["MCP_SSE_PORT"] == 8765
        ), f"Expected MCP_SSE_PORT 8765, got {values_standard['MCP_SSE_PORT']}"

    # Test agent with legacy port parameter - should now fail with an error
    result_legacy = run_agent_in_subprocess(project_dir, "legacy_agent")
    assert result_legacy["returncode"] != 0, "Command should have failed but succeeded"

    # Print debug information
    print(f"STDOUT CONTENT: {result_legacy['stdout']}")
    print(f"STDERR CONTENT: {result_legacy['stderr']}")

    # Verify that error message about unsupported parameter was logged (either in stdout or stderr)
    error_found = (
        ("port" in result_legacy["stderr"].lower() and "not supported" in result_legacy["stderr"].lower())
        or ("port" in result_legacy["stdout"].lower() and "not supported" in result_legacy["stdout"].lower())
        or ("port" in result_legacy["stderr"].lower() and "deprecated" in result_legacy["stderr"].lower())
        or ("port" in result_legacy["stdout"].lower() and "deprecated" in result_legacy["stdout"].lower())
        or ("port" in result_legacy["stderr"].lower() and "error" in result_legacy["stderr"].lower())
        or ("port" in result_legacy["stdout"].lower() and "error" in result_legacy["stdout"].lower())
    )

    assert error_found, "Expected error about unsupported 'port' parameter not found in output"


@pytest.mark.mcp
@pytest.mark.skipif(not HAS_MCP, reason=skip_reason)
def test_legacy_port_conversion(mcp_project):
    """Test that legacy 'port' parameter is properly rejected with an error.

    This test verifies that when the deprecated 'port' parameter is used,
    it is properly rejected with an error message.
    """
    # Run the agent with legacy port parameter
    result = run_agent_in_subprocess(mcp_project, "deprecated_port_agent")

    # Check that the command failed as expected due to the unsupported parameter
    assert result["returncode"] != 0, "Command should have failed but succeeded"

    # Print debug information
    print(f"STDOUT CONTENT: {result['stdout']}")
    print(f"STDERR CONTENT: {result['stderr']}")

    # Verify that error message was logged (either in stdout or stderr)
    error_found = (
        ("port" in result["stderr"].lower() and "not supported" in result["stderr"].lower())
        or ("port" in result["stdout"].lower() and "not supported" in result["stdout"].lower())
        or ("port" in result["stderr"].lower() and "deprecated" in result["stderr"].lower())
        or ("port" in result["stdout"].lower() and "deprecated" in result["stdout"].lower())
        or ("port" in result["stderr"].lower() and "error" in result["stderr"].lower())
        or ("port" in result["stdout"].lower() and "error" in result["stdout"].lower())
    )

    assert error_found, "Expected error about unsupported port parameter not found in output"


# Run the test directly if this file is executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
