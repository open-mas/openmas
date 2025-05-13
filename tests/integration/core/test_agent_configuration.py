"""Tests for loading and applying agent-specific configurations."""

import json
import subprocess
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def multi_agent_project(tmp_path):
    """Create a multi-agent project for testing."""
    project_root = tmp_path / "multi_agent_project"
    project_root.mkdir()

    # Create basic project structure
    (project_root / "agents").mkdir()
    (project_root / "agents" / "diagnostic_agent").mkdir()
    (project_root / "config").mkdir()
    (project_root / "shared").mkdir()

    # Create a simple diagnostic agent
    agent_py = project_root / "agents" / "diagnostic_agent" / "agent.py"
    agent_py.write_text(
        '''
import asyncio
import time
import json
import os
from openmas.agent.base import BaseAgent

class Agent(BaseAgent):
    """A diagnostic agent that prints its configuration."""

    async def setup(self):
        """Set up and report configuration."""
        # Print communicator information for test assertions
        try:
            print(f"COMM_TYPE:{self.communicator.__class__.__name__}")

            if hasattr(self.config, "communicator_type"):
                print(f"CONFIG_COMM_TYPE:{self.config.communicator_type}")

            if hasattr(self.config, "communicator_options"):
                # Convert to JSON for consistent formatting
                print(f"COMM_OPTIONS:{json.dumps(self.config.communicator_options)}")

            # Print specific values for testing
            if hasattr(self.communicator, "http_port"):
                print(f"HTTP_PORT:{self.communicator.http_port}")

            # Report environment variables
            for key, value in os.environ.items():
                if key.startswith("OPENMAS_") or key.startswith("COMMUNICATOR_"):
                    print(f"ENV:{key}={value}")
        except Exception as e:
            print(f"ERROR_IN_SETUP:{str(e)}")

    async def run(self):
        """Run the agent, printing configuration information."""
        # Signal test completion
        print("AGENT_COMPLETED")
        await asyncio.sleep(0.1)
        print("AGENT_COMPLETED")

    async def shutdown(self):
        """Shutdown the agent."""
        print("AGENT_SHUTDOWN")
'''
    )

    # Create an __init__.py file
    init_py = project_root / "agents" / "diagnostic_agent" / "__init__.py"
    init_py.write_text("")

    # Create a project configuration file
    project_config = {
        "name": "test-multi-agent",
        "version": "0.1.0",
        "default_config": {
            "log_level": "INFO",
        },
        "communicator_defaults": {
            "type": "http",
            "options": {
                "http_port": 8000,
                "http_host": "0.0.0.0",
            },
        },
        "agents": {
            "diagnostic_agent": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
            },
            "http_default": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                "communicator": "http",
            },
            "http_custom_port": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                "communicator": "http",
                "communicator_options": {
                    "http_port": 8765,
                },
            },
            "http_agent_with_options": {
                "module": "agents.diagnostic_agent",
                "class": "Agent",
                "communicator": "http",
                "communicator_options": {
                    "http_port": 9876,
                },
            },
        },
    }

    # Write the project configuration file
    config_path = project_root / "openmas_project.yml"
    with open(config_path, "w") as f:
        yaml.dump(project_config, f)

    return project_root


def run_agent_in_subprocess(
    project_dir: Path, agent_name: str, env: str | None = None, timeout: int = 5
) -> dict[str, str | int]:
    """Run an agent in a subprocess and capture output.

    Args:
        project_dir: Project directory path
        agent_name: Name of the agent to run
        env: Optional environment name
        timeout: Maximum time to wait for the agent

    Returns:
        Dictionary with captured stdout and stderr
    """
    env_args = []
    if env:
        env_args = ["--env", env]

    cmd = ["python", "-m", "openmas.cli", "run", agent_name, *env_args]

    # Set working directory to project dir
    process = subprocess.Popen(
        cmd,
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()

    return {"stdout": stdout, "stderr": stderr, "returncode": process.returncode}


def parse_stdout_for_values(stdout: str) -> dict:
    """Parse the stdout for configuration values printed by the agent.

    Args:
        stdout: Standard output to parse

    Returns:
        Dictionary with configuration values
    """
    result = {}

    # Look for lines with format KEY:VALUE
    for line in stdout.splitlines():
        if ":" in line:
            # Split only on the first colon
            parts = line.split(":", 1)
            if len(parts) == 2:
                key, value = parts

                # Try to parse JSON values
                if key == "COMM_OPTIONS":
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                # Convert other values to appropriate types
                else:
                    try:
                        if value.lower() == "true":
                            value = True
                        elif value.lower() == "false":
                            value = False
                        elif value.isdigit():
                            value = int(value)
                        else:
                            try:
                                value = float(value)
                            except ValueError:
                                pass
                    except (ValueError, AttributeError):
                        pass

                result[key] = value

    return result


def test_agent_configuration_is_properly_loaded(multi_agent_project):
    """Test that agent configuration is properly loaded and applied."""
    # Update the project configuration with direct agent configuration
    project_path = multi_agent_project / "openmas_project.yml"
    with open(project_path, "r") as f:
        config = yaml.safe_load(f)

    # Add configuration directly to the agent entry
    config["agents"]["diagnostic_agent"].update(
        {
            "communicator": "http",
            "communicator_options": {"http_port": 9876, "http_host": "127.0.0.1"},  # Custom port to test with
        }
    )

    # Save updated configuration
    with open(project_path, "w") as f:
        yaml.dump(config, f)

    # Run the agent
    result = run_agent_in_subprocess(multi_agent_project, "diagnostic_agent")

    # Check for success
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Verify the port configuration
    stdout_str = str(result["stdout"])
    assert (
        "HTTP port configured: 9876" in stdout_str or "HTTP port: 9876" in stdout_str
    ), "Custom port 9876 not found in output"


def test_communicator_defaults_precedence(multi_agent_project):
    """Test that direct agent config takes precedence over default communicator settings."""
    # Update the project configuration with conflicting settings
    project_path = multi_agent_project / "openmas_project.yml"
    with open(project_path, "r") as f:
        config = yaml.safe_load(f)

    # Add communicator_defaults section
    config["communicator_defaults"] = {"type": "http", "options": {"port": 8000}}

    # Add direct agent configuration with different settings
    config["agents"]["diagnostic_agent"].update(
        {"communicator": "http", "communicator_options": {"http_port": 9999}}  # This should win over the default 8000
    )

    # Save updated configuration
    with open(project_path, "w") as f:
        yaml.dump(config, f)

    # Run the agent
    result = run_agent_in_subprocess(multi_agent_project, "diagnostic_agent")

    # Check for success
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Parse the stdout for values
    values = parse_stdout_for_values(result["stdout"])

    # Verify the communicator type is correct
    assert "COMM_TYPE" in values, "No communicator type in output"
    assert values["COMM_TYPE"] == "HttpCommunicator", f"Wrong communicator type: {values['COMM_TYPE']}"

    # Verify port was taken from agent config
    assert "HTTP_PORT" in values, "No HTTP_PORT in output"
    assert values["HTTP_PORT"] == 9999, f"Expected port 9999, got {values.get('HTTP_PORT')}"


def test_env_var_overrides_agent_config(multi_agent_project):
    """Test that environment variables override agent configuration settings."""
    # Update the project configuration with direct agent configuration
    project_path = multi_agent_project / "openmas_project.yml"
    with open(project_path, "r") as f:
        config = yaml.safe_load(f)

    # Add configuration directly to the agent entry
    config["agents"]["diagnostic_agent"].update({"communicator": "http", "communicator_options": {"http_port": 7777}})

    # Save updated configuration
    with open(project_path, "w") as f:
        yaml.dump(config, f)

    # We need to create a script that will set the environment variable and run the agent
    script_dir = multi_agent_project / "scripts"
    script_dir.mkdir(exist_ok=True)

    # Create a script that sets the environment variable - use the correct format with OPENMAS_ prefix
    script_file = script_dir / "run_with_env.py"
    script_content = """
import os
import sys
import subprocess

# Set the environment variable with the proper format
os.environ["OPENMAS_COMMUNICATOR_OPTIONS_HTTP_PORT"] = "8888"

# Run the agent
cmd = [sys.executable, "-m", "openmas.cli", "run", "diagnostic_agent"]
process = subprocess.run(cmd, cwd=os.getcwd())
sys.exit(process.returncode)
"""
    script_file.write_text(script_content)

    # Run the script
    cmd = ["python", str(script_file)]
    process = subprocess.Popen(cmd, cwd=multi_agent_project, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        stdout, stderr = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()

    result = {"stdout": stdout, "stderr": stderr, "returncode": process.returncode}

    # Print full output for debugging
    print("\nSTDOUT:")
    print(result["stdout"])
    print("\nSTDERR:")
    print(result["stderr"])

    # Check for success
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Verify that the environment variable is recognized and printed
    stdout_str_env = str(result["stdout"])
    assert (
        "ENV:OPENMAS_COMMUNICATOR_OPTIONS_HTTP_PORT=8888" in stdout_str_env
    ), "Environment variable not found in output"

    # Parse the output to extract key-value pairs
    values = parse_stdout_for_values(result["stdout"])

    # Verify that the HTTP_PORT value shows our environment variable took effect
    assert "HTTP_PORT" in values, "No HTTP_PORT in output"
    assert (
        values["HTTP_PORT"] == 8888
    ), f"Environment variable port not applied (got {values['HTTP_PORT']}, expected 8888)"


def test_mcp_port_configuration(multi_agent_project):
    """Test that http_port in communicator_options is properly applied for MCP-SSE communicator."""
    project_path = multi_agent_project / "openmas_project.yml"

    # Read existing config
    with open(project_path, "r") as f:
        config = yaml.safe_load(f)

    # Create extensions directory
    ext_dir = multi_agent_project / "extensions"
    ext_dir.mkdir(exist_ok=True)

    # Add extension path
    config["extension_paths"] = ["extensions"]

    # Add MCP agent with direct configuration
    config["agents"]["mcp_agent"] = {
        "module": "agents.diagnostic_agent",
        "class": "Agent",
        "communicator": "mcp-sse",
        "communicator_options": {"server_mode": True, "http_port": 9876, "http_host": "127.0.0.1"},
    }

    # Save updated configuration
    with open(project_path, "w") as f:
        yaml.dump(config, f)

    # Run the agent
    result = run_agent_in_subprocess(multi_agent_project, "mcp_agent")

    # Print output for debugging
    print("\nSTDOUT:")
    print(result["stdout"])
    print("\nSTDERR:")
    print(result["stderr"])

    # Check for success
    assert result["returncode"] == 0, f"Command failed: {result['stderr']}"

    # Parse the output
    values = parse_stdout_for_values(result["stdout"])

    # Check for communicator type in output
    assert "COMM_TYPE" in values, "No communicator type in output"
    assert "McpSseCommunicator" in values["COMM_TYPE"], f"Expected McpSseCommunicator, got {values.get('COMM_TYPE')}"

    # Check communicator options
    assert "COMM_OPTIONS" in values, "No communicator options in output"
    assert (
        values["COMM_OPTIONS"].get("http_port") == 9876
    ), f"Expected port 9876, got {values['COMM_OPTIONS'].get('http_port')}"

    # Check HTTP_PORT
    assert "HTTP_PORT" in values, "No HTTP_PORT in output"
    assert values["HTTP_PORT"] == 9876, f"Wrong port: expected 9876, got {values.get('HTTP_PORT')}"

    # Check MCP server port in log message
    assert "MCP server will use: 127.0.0.1:9876" in str(result["stdout"]), "MCP server port message not found in output"
