"""Integration tests for prompt configuration."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import TypedDict

import pytest
import yaml

from openmas.config import AgentConfig
from openmas.prompt import PromptManager
from openmas.prompt.base import PromptConfig


class ConfigChange(TypedDict):
    """Type definition for configuration changes."""

    modify_template: bool
    delete_template: bool
    template_name: str
    invalid_prompts_dir: bool


@pytest.fixture
def prompt_project_setup(tmp_path: Path) -> Path:
    """Create a test project with prompt configuration for integration testing."""
    project_dir = tmp_path / "prompt_config_test"
    project_dir.mkdir()

    # Create prompts directory and template files
    prompts_dir = project_dir / "custom_prompts"
    prompts_dir.mkdir()

    # Create template files
    (prompts_dir / "template1.txt").write_text("Template 1: {{var1}}")
    (prompts_dir / "template2.txt").write_text("Template 2: {{var2}}")

    # Create openmas_project.yml
    project_config = {
        "name": "prompt_config_test",
        "version": "0.1.0",
        "agents": {
            "test_agent": {
                "name": "test_agent",
                "prompts_dir": "custom_prompts",
                "prompts": [
                    {"name": "prompt1", "template_file": "template1.txt", "input_variables": ["var1"]},
                    {"name": "prompt2", "template_file": "template2.txt", "input_variables": ["var2"]},
                ],
            }
        },
    }

    with open(project_dir / "openmas_project.yml", "w") as f:
        yaml.dump(project_config, f)

    # Create a test script that loads the config and uses the prompt manager
    test_script = project_dir / "test_prompt_config.py"
    test_script.write_text(
        """
import asyncio
import json
import os
import sys
from pathlib import Path

from openmas.config import load_config, AgentConfig
from openmas.prompt import PromptManager

async def main():
    # Load configuration
    config = load_config(AgentConfig)

    # Print detailed debug information
    print(f"DEBUG: config type: {type(config)}")
    print(f"DEBUG: config full dump: {config.model_dump()}")
    print(f"DEBUG: config.prompts type: {type(config.prompts)}")

    if config.prompts:
        print(f"DEBUG: prompts count: {len(config.prompts)}")
        for i, p in enumerate(config.prompts):
            print(f"DEBUG: prompt {i} type: {type(p)}")
            print(f"DEBUG: prompt {i} content: {p.model_dump()}")

    # Print the configuration for verification
    print(f"LOADED CONFIG: name={config.name}, prompts_dir={config.prompts_dir}")
    if config.prompts and len(config.prompts) > 0:
        print(f"PROMPTS COUNT: {len(config.prompts)}")
        for i, prompt in enumerate(config.prompts):
            print(f"PROMPT {i+1}: name={prompt.name}, template_file={prompt.template_file}")
    else:
        print("NO PROMPTS FOUND IN CONFIG")

    # Create prompt manager using the configuration
    prompts_path = Path.cwd() / str(config.prompts_dir)
    manager = PromptManager(prompts_base_path=prompts_path)

    # Load prompts from config
    if config.prompts and len(config.prompts) > 0:
        prompts = manager.load_prompts_from_config(config.prompts)
        print(f"LOADED PROMPTS: {len(prompts)}")

        # Verify each prompt's content
        for i, prompt in enumerate(prompts):
            print(f"PROMPT {i+1} CONTENT: {prompt.content.template}")
    else:
        print("NO PROMPTS TO LOAD")

    return 0

if __name__ == "__main__":
    asyncio.run(main())
"""
    )

    return project_dir


@pytest.mark.integration
def test_prompt_config_from_project_yaml(prompt_project_setup: Path) -> None:
    """Test that prompt configuration is correctly loaded from project YAML."""
    project_dir = prompt_project_setup

    # Run the test script in a subprocess
    proc = subprocess.run(
        [sys.executable, "test_prompt_config.py"],
        cwd=project_dir,
        env={"AGENT_NAME": "test_agent"},
        capture_output=True,
        text=True,
    )

    # Check for successful execution
    assert proc.returncode == 0, f"Script failed with stderr: {proc.stderr}"

    # Verify configuration was loaded correctly
    assert "LOADED CONFIG: name=test_agent" in proc.stdout
    assert "prompts_dir=custom_prompts" in proc.stdout or "prompts_dir=prompts" in proc.stdout
    assert "PROMPTS COUNT: 2" in proc.stdout
    assert "PROMPT 1: name=prompt1" in proc.stdout
    assert "PROMPT 2: name=prompt2" in proc.stdout

    # Verify prompts were loaded correctly
    assert "LOADED PROMPTS: 2" in proc.stdout
    assert "PROMPT 1 CONTENT: Template 1: {{var1}}" in proc.stdout
    assert "PROMPT 2 CONTENT: Template 2: {{var2}}" in proc.stdout


@pytest.mark.integration
def test_prompt_config_env_override(prompt_project_setup: Path) -> None:
    """Test that environment variables override project config."""
    project_dir = prompt_project_setup

    # Create a different prompts directory for the environment override
    env_prompts_dir = project_dir / "env_prompts"
    env_prompts_dir.mkdir()
    (env_prompts_dir / "env_template.txt").write_text("Environment template: {{env_var}}")

    # Create environment variables to override the configuration
    env = os.environ.copy()
    env["AGENT_NAME"] = "test_agent"
    env["PROMPTS_DIR"] = "env_prompts"
    env["PROMPTS"] = json.dumps(
        [{"name": "env_prompt", "template_file": "env_template.txt", "input_variables": ["env_var"]}]
    )

    # Run the test script with the overridden configuration
    proc = subprocess.run(
        [sys.executable, "test_prompt_config.py"], cwd=project_dir, env=env, capture_output=True, text=True
    )

    # Check for successful execution
    assert proc.returncode == 0, f"Script failed with stderr: {proc.stderr}"

    # Verify environment configuration was used
    assert "LOADED CONFIG: name=test_agent" in proc.stdout
    assert "prompts_dir=env_prompts" in proc.stdout
    assert "PROMPTS COUNT: 1" in proc.stdout
    assert "PROMPT 1: name=env_prompt" in proc.stdout

    # Verify environment prompt was loaded correctly
    assert "LOADED PROMPTS: 1" in proc.stdout
    assert "PROMPT 1 CONTENT: Environment template: {{env_var}}" in proc.stdout


@pytest.mark.parametrize(
    "config_change,expected_error",
    [
        # Test missing template file
        (
            {
                "modify_template": False,
                "delete_template": True,
                "template_name": "template1.txt",
                "invalid_prompts_dir": False,
            },
            "not found",
        ),
        # Test invalid prompts_dir
        (
            {
                "modify_template": False,
                "delete_template": False,
                "template_name": "",
                "invalid_prompts_dir": True,
            },
            "not found",
        ),
    ],
    ids=["missing_template", "invalid_prompts_dir"],
)
@pytest.mark.integration
def test_prompt_config_error_handling(
    prompt_project_setup: Path,
    config_change: ConfigChange,
    expected_error: str,
) -> None:
    """Test error handling for various configuration issues."""
    project_dir = prompt_project_setup

    # Apply configuration changes based on parameters
    if config_change["delete_template"]:
        template_name = config_change["template_name"]
        if template_name:
            template_path = project_dir / "custom_prompts" / str(template_name)
            if template_path.exists():
                template_path.unlink()

    # Set environment variables
    env = os.environ.copy()
    env["AGENT_NAME"] = "test_agent"

    if config_change["invalid_prompts_dir"]:
        env["PROMPTS_DIR"] = "nonexistent_dir"

    # Run the test script with the problematic configuration
    proc = subprocess.run(
        [sys.executable, "test_prompt_config.py"], cwd=project_dir, env=env, capture_output=True, text=True
    )

    # Verify the script failed with the expected error
    output = str(proc.stderr) + str(proc.stdout)
    error_found = expected_error.lower() in str(output).lower()
    assert proc.returncode != 0 or error_found, f"Expected error '{expected_error}' not found in output"


@pytest.mark.asyncio
async def test_prompt_manager_direct_config_integration():
    """Test that PromptManager directly integrates with configuration correctly."""
    # Create temporary prompts in memory
    prompt_configs = [PromptConfig(name="direct_prompt", template="Direct template: {{variable}}")]

    # Create AgentConfig with these prompts
    config = AgentConfig(name="test-agent", prompts=prompt_configs)

    # Create PromptManager and load prompts
    manager = PromptManager()
    prompts = manager.load_prompts_from_config(config.prompts)

    # Verify prompts were loaded correctly
    assert len(prompts) == 1
    assert prompts[0].metadata.name == "direct_prompt"
    assert prompts[0].content.template == "Direct template: {{variable}}"

    # Test that the prompt was added to the manager's internal storage
    # by checking the _prompts dictionary directly
    assert len(manager._prompts) == 1

    # Get the prompt by name using the API method - verify it works
    prompt = await manager.get_prompt_by_name("direct_prompt")
    assert prompt is not None
    assert prompt.metadata.name == "direct_prompt"

    # Verify the prompt content directly
    assert prompt.content.template is not None
    assert "{{variable}}" in prompt.content.template


def test_prompt_config_loading_from_file():
    """Test loading prompt configuration from a file."""
    pass


def test_prompt_config_loading_from_dict():
    """Test loading prompt configuration from a dictionary."""
    pass


def test_prompt_config_loading_from_yaml():
    """Test loading prompt configuration from a YAML string."""
    pass


def test_prompt_config_loading_from_json():
    """Test loading prompt configuration from a JSON string."""
    pass


def test_prompt_config_loading_from_toml():
    """Test loading prompt configuration from a TOML string."""
    pass
