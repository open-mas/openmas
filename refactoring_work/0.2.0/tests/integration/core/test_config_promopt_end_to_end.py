"""End-to-end integration tests for configuration loading.

These tests verify that configuration values flow correctly from sources
through to actual components in a realistic end-to-end scenario.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Test script template that includes all necessary imports
TEST_SCRIPT_CONTENT = """
import asyncio
import json
import os
import sys
from pathlib import Path
import logging

from openmas.config import AgentConfig, load_config, PromptConfig
from openmas.prompt import PromptManager, get_prompt_manager
from openmas.prompt.base import Prompt

# Check for MCP availability for the test script itself
HAS_MCP = False
try:
    from openmas.prompt.providers.mcp import McpPromptManager
    from mcp import load_project_config as mcp_load_project_config
    HAS_MCP = True
except ImportError:
    pass

async def main():
    # Basic logging setup for the test script
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s')

    # Load agent configuration
    agent_config = load_config(AgentConfig, prefix="OPENMAS", agent_name="test_agent")

    print(f"CONFIGURATION: agent_name={agent_config.name}, prompts_dir={agent_config.prompts_dir}")

    # Check if prompts are available in config - ensure we're properly accessing them
    # Debug information to help diagnose issues
    print(f"DEBUG: agent_config type: {type(agent_config)}")
    print(f"DEBUG: agent_config.prompts type: {type(agent_config.prompts)}")
    print(f"DEBUG: agent_config content: {agent_config.model_dump(exclude_none=True)}")

    if agent_config.prompts and len(agent_config.prompts) > 0:
        print(f"FOUND {len(agent_config.prompts)} PROMPTS IN CONFIG")
        for i, prompt in enumerate(agent_config.prompts):
            print(f"PROMPT {i+1}: {prompt.name}")
    else:
        print("NO PROMPTS FOUND IN CONFIG")

    # Determine if MCP is requested by environment variable for the test script
    use_mcp = os.environ.get("USE_MCP") == "true" and HAS_MCP

    # Get prompt manager instance
    if use_mcp:
        prompt_manager = get_prompt_manager(provider="mcp", prompts_base_path=agent_config.prompts_dir)
        print("USING MCP PROMPT MANAGER")
    else:
        prompt_manager = get_prompt_manager(provider="default", prompts_base_path=agent_config.prompts_dir)
        print("USING DEFAULT PROMPT MANAGER")

    # Set base path and load prompts
    prompt_manager.prompts_base_path = Path.cwd() / agent_config.prompts_dir
    if agent_config.prompts and len(agent_config.prompts) > 0:
        print("LOADING PROMPTS FROM CONFIG...")
        try:
            # This line is problematic for McpPromptManager if it doesn't have this method
            # For now, assume DefaultPromptManager path or that McpPromptManager will delegate/implement
            loaded_prompt_objects = prompt_manager.load_prompts_from_config(agent_config.prompts)
            print(f"LOADED {len(loaded_prompt_objects)} PROMPTS")

            # Render a prompt
            # Ensure the prompt exists before trying to render
            if loaded_prompt_objects and any(p.metadata.name == "greeting" for p in loaded_prompt_objects):
                print(f"RENDERING PROMPT: greeting")
                # render_prompt now accepts name
                rendered_prompt_data = await prompt_manager.render_prompt("greeting", context={"name": "User", "service": "OpenMAS"})
                if rendered_prompt_data:
                    print(f"RENDERED greeting: {rendered_prompt_data.get('content')}")
                else:
                    print(f"RENDERED greeting: None (render_prompt returned None)")
            else:
                print(f"PROMPT 'greeting' not loaded, cannot render.")

            if loaded_prompt_objects and any(p.metadata.name == "farewell" for p in loaded_prompt_objects):
                print(f"RENDERING PROMPT: farewell")
                rendered_prompt_data_farewell = await prompt_manager.render_prompt("farewell", context={"name": "User", "service": "OpenMAS"})
                if rendered_prompt_data_farewell:
                    print(f"RENDERED farewell: {rendered_prompt_data_farewell.get('content')}")
                else:
                    print(f"RENDERED farewell: None (render_prompt returned None)")
            else:
                print(f"PROMPT 'farewell' not loaded, cannot render.")

        except FileNotFoundError as e:
            print(f"ERROR LOADING PROMPTS - FILE NOT FOUND: {e}")
        except Exception as e:
            print(f"ERROR DURING PROMPT OPERATIONS: {e}")
    else:
        print("NO PROMPTS IN CONFIG TO LOAD OR RENDER.")

if __name__ == "__main__":
    asyncio.run(main())
"""


@pytest.fixture
def config_test_project():
    """Create a test project with complete configuration for end-to-end testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_dir = Path(tmp_dir) / "config_test_project"
        project_dir.mkdir()

        # Create directory structure
        prompts_dir = project_dir / "prompts"
        prompts_dir.mkdir()

        # Create prompt template files
        (prompts_dir / "greeting.txt").write_text("Hello, {{name}}! Welcome to {{service}}.")
        (prompts_dir / "farewell.txt").write_text("Goodbye, {{name}}! Thank you for using {{service}}.")

        # Create project configuration
        project_config = {
            "name": "config_test_project",
            "version": "0.1.0",
            "agents": {
                "test_agent": {
                    "name": "test_agent",
                    "communicator_type": "http",
                    "prompts_dir": "prompts",
                    "prompts": [
                        {"name": "greeting", "template_file": "greeting.txt", "input_variables": ["name", "service"]},
                        {"name": "farewell", "template_file": "farewell.txt", "input_variables": ["name", "service"]},
                    ],
                }
            },
        }

        with open(project_dir / "openmas_project.yml", "w") as f:
            yaml.dump(project_config, f)

        # Create test script
        test_script = project_dir / "end_to_end_test.py"
        test_script.write_text(TEST_SCRIPT_CONTENT)

        yield project_dir


@pytest.mark.parametrize(
    "config_source",
    [
        "project_yaml",  # Test loading from project YAML
        "env_vars",  # Test loading from environment variables
    ],
)
@pytest.mark.integration
def test_end_to_end_config_loading(config_test_project, config_source):
    """Test end-to-end configuration loading from different sources."""
    project_dir = config_test_project

    # Set up environment based on the test case
    env = os.environ.copy()
    env["OPENMAS_AGENT_NAME"] = "test_agent"

    if config_source == "env_vars":
        # Override configuration with environment variables
        env["PROMPTS_DIR"] = "prompts"  # Same dir, but explicitly set
        env["OPENMAS_PROMPTS"] = json.dumps(
            [
                {"name": "greeting", "template_file": "greeting.txt", "input_variables": ["name", "service"]},
                {"name": "farewell", "template_file": "farewell.txt", "input_variables": ["name", "service"]},
            ]
        )

    # Run the end-to-end test script
    proc = subprocess.run(
        [sys.executable, "end_to_end_test.py"], cwd=project_dir, env=env, capture_output=True, text=True
    )

    # Check for successful execution
    print("STDOUT:", proc.stdout)
    print("STDERR:", proc.stderr)
    assert proc.returncode == 0, f"Script failed with stderr: {proc.stderr}"

    # Verify configuration was loaded
    assert "CONFIGURATION: agent_name=test_agent, prompts_dir=prompts" in proc.stdout
    assert "FOUND 2 PROMPTS IN CONFIG" in proc.stdout

    # Verify prompt manager was created
    assert "USING DEFAULT PROMPT MANAGER" in proc.stdout

    # Verify prompts were loaded
    assert "LOADED 2 PROMPTS" in proc.stdout

    # Verify prompts were rendered
    assert "RENDERING PROMPT: greeting" in proc.stdout
    assert "RENDERING PROMPT: farewell" in proc.stdout
    assert "RENDERED greeting: " in proc.stdout
    assert "Hello, User! Welcome to OpenMAS" in proc.stdout
    assert "RENDERED farewell: " in proc.stdout
    assert "Goodbye, User! Thank you for using OpenMAS" in proc.stdout


@pytest.mark.integration
def test_end_to_end_provider_selection(config_test_project):
    """Test that the correct provider is selected based on configuration."""
    project_dir = config_test_project

    # Set up environment
    env = os.environ.copy()
    env["OPENMAS_AGENT_NAME"] = "test_agent"

    # Test with default provider
    env["USE_MCP"] = "false"

    proc = subprocess.run(
        [sys.executable, "end_to_end_test.py"], cwd=project_dir, env=env, capture_output=True, text=True
    )

    assert proc.returncode == 0, f"Script failed with stderr: {proc.stderr}"
    assert "USING DEFAULT PROMPT MANAGER" in proc.stdout

    # Test with MCP provider (if available)
    env["USE_MCP"] = "true"

    proc = subprocess.run(
        [sys.executable, "end_to_end_test.py"], cwd=project_dir, env=env, capture_output=True, text=True
    )

    assert proc.returncode == 0, f"Script failed with stderr: {proc.stderr}"
    # The script only uses MCP if HAS_MCP is true, so either result is valid
    assert "USING MCP PROMPT MANAGER" in proc.stdout or "USING DEFAULT PROMPT MANAGER" in proc.stdout


@pytest.mark.integration
def test_end_to_end_config_nonexistent_prompt(config_test_project):
    """Test error handling for non-existent prompt files."""
    project_dir = config_test_project

    # Set up environment with invalid prompt configuration
    env = os.environ.copy()
    env["OPENMAS_AGENT_NAME"] = "test_agent"
    env["OPENMAS_PROMPTS"] = json.dumps(
        [{"name": "nonexistent", "template_file": "nonexistent.txt", "input_variables": ["var1"]}]
    )

    # Run the test script with invalid configuration
    proc = subprocess.run(
        [sys.executable, "end_to_end_test.py"], cwd=project_dir, env=env, capture_output=True, text=True
    )

    # Print the actual outputs for debugging
    print(f"STDOUT: {proc.stdout}")
    print(f"STDERR: {proc.stderr}")

    # The script should run but report errors with prompt loading
    assert "FOUND 1 PROMPTS IN CONFIG" in proc.stdout
    assert "PROMPT 1: nonexistent" in proc.stdout

    # Updated assertion to match the actual error message format
    # The error could be in several formats, so check for key parts
    assert any(
        [
            "ERROR LOADING PROMPTS - FILE NOT FOUND" in proc.stdout,
            "prompts/nonexistent.txt" in proc.stdout,
            "No such file or directory" in proc.stdout,
            "FileNotFoundError" in proc.stdout,
        ]
    )


def test_end_to_end_config_validation():
    """Test end-to-end configuration validation."""
    # Implementation needed
    pass


def test_end_to_end_config_saving():
    """Test end-to-end configuration saving."""
    # Implementation needed
    pass


def test_end_to_end_config_merging():
    """Test end-to-end configuration merging."""
    # Implementation needed
    pass


def test_end_to_end_config_inheritance():
    """Test end-to-end configuration inheritance."""
    # Implementation needed
    pass
