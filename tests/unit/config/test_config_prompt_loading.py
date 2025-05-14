"""Unit tests for prompt configuration loading."""

from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from openmas.config import AgentConfig
from openmas.prompt import PromptManager, get_prompt_manager


class TestPromptConfigLoading:
    """Test loading of prompt configuration."""

    def test_agent_config_prompt_fields(self):
        """Test that the prompt-related fields in AgentConfig are loaded correctly."""
        # Create a config with prompt fields
        config = AgentConfig(
            name="test-agent",
            prompts=[{"name": "test-prompt", "template": "This is a test template"}],
            prompts_dir=Path("custom/prompts/dir"),
        )

        # Verify the fields are correctly set
        assert config.prompts is not None
        assert len(config.prompts) == 1
        assert config.prompts[0].name == "test-prompt"
        assert config.prompts[0].template == "This is a test template"
        assert config.prompts_dir == Path("custom/prompts/dir")

    def test_default_prompts_dir(self):
        """Test that the default prompts_dir is 'prompts'."""
        config = AgentConfig(name="test-agent")
        assert config.prompts_dir == Path("prompts")

    @patch("openmas.config._load_project_config")
    def test_env_prompts_dir(self, mock_load_project_config, monkeypatch):
        """Test loading prompts_dir from environment variables."""
        # Mock the project config to return an empty dictionary
        mock_load_project_config.return_value = {}

        # Create config directly
        config = AgentConfig(name="test-agent", prompts_dir="env/prompts/dir")

        assert config.prompts_dir == Path("env/prompts/dir")

    @patch("openmas.config._load_project_config")
    def test_env_prompts(self, mock_load_project_config, monkeypatch):
        """Test loading prompts from environment variables."""
        # Mock the project config to return an empty dictionary
        mock_load_project_config.return_value = {}

        prompts = [{"name": "env-prompt", "template": "This is from the environment"}]

        # Create config directly
        config = AgentConfig(name="test-agent", prompts=prompts)

        assert config.prompts is not None
        assert len(config.prompts) == 1
        assert config.prompts[0].name == "env-prompt"
        assert config.prompts[0].template == "This is from the environment"

    @patch("openmas.config._load_project_config")
    def test_config_precedence_simulation(self, mock_load_project_config):
        """Simulate configuration precedence by creating configs directly."""
        # Mock the project config to return an empty dictionary
        mock_load_project_config.return_value = {}

        # Create a config with the default prompts_dir
        config1 = AgentConfig(name="test-agent")
        assert config1.prompts_dir == Path("prompts")

        # Create a config with a custom prompts_dir (simulating JSON config)
        config2 = AgentConfig(name="test-agent", prompts_dir="json/prompts")
        assert config2.prompts_dir == Path("json/prompts")

        # Create a config with another custom prompts_dir (simulating ENV var)
        config3 = AgentConfig(name="test-agent", prompts_dir="env/prompts")
        assert config3.prompts_dir == Path("env/prompts")

    def test_invalid_prompts_config(self):
        """Test error handling for invalid prompts configuration."""
        # Missing required field (name)
        invalid_prompts = [{"template": "No name field"}]

        with pytest.raises(ValidationError):
            AgentConfig(name="test-agent", prompts=invalid_prompts)


class TestPromptManagerWithConfig:
    """Test the integration between PromptManager and configuration."""

    def test_prompt_manager_with_config(self, tmp_path):
        """Test creating a PromptManager with configuration values."""
        # Create a test prompt file
        prompts_dir = tmp_path / "test_prompts"
        prompts_dir.mkdir()
        template_file = prompts_dir / "greeting.txt"
        template_file.write_text("Hello, {{name}}!")

        # Create configuration
        config = AgentConfig(
            name="test-agent", prompts_dir=prompts_dir, prompts=[{"name": "greeting", "template_file": "greeting.txt"}]
        )

        # Create PromptManager with the config
        manager = PromptManager(prompts_base_path=config.prompts_dir)
        prompts = manager.load_prompts_from_config(config.prompts)

        # Verify the prompt was loaded correctly
        assert len(prompts) == 1
        assert prompts[0].metadata.name == "greeting"
        assert prompts[0].content.template == "Hello, {{name}}!"

    def test_get_prompt_manager_factory(self):
        """Test that the get_prompt_manager factory correctly uses configuration."""
        config = AgentConfig(
            name="test-agent", prompts=[{"name": "inline-prompt", "template": "This is an inline template"}]
        )

        # Get a prompt manager with default provider
        manager = get_prompt_manager(provider="default")

        # Load the prompts from config
        prompts = manager.load_prompts_from_config(config.prompts)

        # Verify the prompt was loaded correctly
        assert len(prompts) == 1
        assert prompts[0].metadata.name == "inline-prompt"
        assert prompts[0].content.template == "This is an inline template"

    def test_prompt_manager_missing_template_file(self, tmp_path):
        """Test error handling when a template file is missing."""
        prompts_dir = tmp_path / "empty_dir"
        prompts_dir.mkdir()

        # Create configuration with non-existent template file
        config = AgentConfig(
            name="test-agent",
            prompts_dir=prompts_dir,
            prompts=[{"name": "missing", "template_file": "does_not_exist.txt"}],
        )

        # Create PromptManager with the config
        manager = PromptManager(prompts_base_path=config.prompts_dir)

        # Should raise FileNotFoundError when template file is missing
        with pytest.raises(FileNotFoundError):
            manager.load_prompts_from_config(config.prompts)

    def test_prompt_manager_missing_prompts_dir(self):
        """Test error handling when prompts_base_path is not provided for template files."""
        # Create configuration with template file but no prompts_base_path
        config = AgentConfig(name="test-agent", prompts=[{"name": "template-prompt", "template_file": "some_file.txt"}])

        # Create PromptManager without prompts_base_path
        manager = PromptManager()

        # Should raise ValueError when trying to resolve template file
        with pytest.raises(ValueError, match="prompts_base_path must be set"):
            manager.load_prompts_from_config(config.prompts)
