"""CLI run module for OpenMAS."""

import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, Type

import click
import typer
import yaml

from openmas.agent.base import BaseAgent
from openmas.assets.manager import AssetManager
from openmas.cli.agent_executor import AgentExecutor
from openmas.cli.agent_loader import AgentLoader
from openmas.cli.event_loop import EventLoopManager
from openmas.cli.project_env import ProjectEnvironment
from openmas.config import AgentConfigEntry, ConfigLoader, ProjectConfig, _find_project_root, logger
from openmas.exceptions import ConfigurationError


def find_project_root(project_dir: Optional[Path] = None) -> Optional[Path]:
    """Find the project root directory.

    Args:
        project_dir: Optional explicit path to the project directory

    Returns:
        Path to the project root or None if not found
    """
    return _find_project_root(project_dir)


def load_project_config(project_root: Path) -> ProjectConfig:
    """Load the project configuration from the project root.

    Args:
        project_root: Path to the project root

    Returns:
        Loaded project configuration

    Raises:
        ConfigurationError: If the configuration is invalid
    """
    try:
        config_loader = ConfigLoader()
        config = config_loader.load_yaml_file(project_root / "openmas_project.yml")
        return ProjectConfig(**config)
    except (ConfigurationError, FileNotFoundError, yaml.YAMLError) as e:
        raise ConfigurationError(f"Error loading project configuration: {e}")
    except Exception as e:
        raise ConfigurationError(f"Unexpected error loading project configuration: {e}")


def validate_agent_in_config(project_config: ProjectConfig, agent_name: str) -> AgentConfigEntry:
    """Validate that the agent exists in the project configuration.

    Args:
        project_config: The project configuration
        agent_name: Name of the agent to validate

    Returns:
        The agent configuration entry

    Raises:
        ConfigurationError: If the agent is not found or has invalid configuration
    """
    if agent_name not in project_config.agents:
        all_agents = list(project_config.agents.keys())
        available_agents_msg = f"Available agents: {', '.join(all_agents)}" if all_agents else ""
        raise ConfigurationError(f"Agent '{agent_name}' not found in project configuration. {available_agents_msg}")

    agent_config_entry = project_config.agents.get(agent_name)
    if not isinstance(agent_config_entry, AgentConfigEntry):
        raise ConfigurationError(f"Invalid agent configuration for '{agent_name}'")

    return agent_config_entry


def load_environment_config(project_root: Path, env: Optional[str] = None) -> Dict[str, Any]:
    """Load environment-specific configuration.

    Args:
        project_root: Path to the project root
        env: Optional environment name

    Returns:
        Environment configuration dictionary
    """
    if not env:
        return {}

    config_loader = ConfigLoader()
    env_config_path = project_root / "config" / f"{env}.yml"
    if env_config_path.exists():
        logger.debug(f"Loading environment configuration from {env_config_path}")
        return config_loader.load_yaml_file(env_config_path)

    logger.debug(f"Environment config file not found: {env_config_path}")
    return {}


def load_agent_class(agent_loader: AgentLoader, agent_config_entry: AgentConfigEntry) -> Type[BaseAgent]:
    """Load the agent class using the agent loader.

    Args:
        agent_loader: Instance of AgentLoader
        agent_config_entry: Configuration entry for the agent

    Returns:
        The agent class

    Raises:
        ConfigurationError: If the agent class could not be loaded
    """
    try:
        return agent_loader.load_agent_class(
            agent_config_entry.module, agent_config_entry.class_ if hasattr(agent_config_entry, "class_") else None
        )
    except (ImportError, ConfigurationError) as e:
        # Check for the specific error about class not found to match test expectations
        if "not found in module" in str(e) and "class" in str(e).lower():
            class_name = getattr(agent_config_entry, "class_", None)
            raise ConfigurationError(f"Error finding agent class: Specified agent class '{class_name}' not found.")
        # Otherwise just pass through the original error
        raise ConfigurationError(f"Error loading agent: {e}")


def create_asset_manager(project_config: ProjectConfig) -> Optional[AssetManager]:
    """Create an asset manager if assets are configured.

    Args:
        project_config: The project configuration

    Returns:
        An asset manager or None if not configured or not available
    """
    if hasattr(project_config, "assets") and project_config.assets:
        try:
            return AssetManager(project_config)
        except ImportError as e:
            click.echo(f"⚠️ Warning: Could not initialize asset manager: {e}")
            click.echo("Asset functionality will not be available.")

    return None


def initialize_agent(
    agent_class: Type[BaseAgent],
    agent_name: str,
    project_config: ProjectConfig,
    env_config: Dict[str, Any],
    asset_manager: Optional[AssetManager] = None,
) -> BaseAgent:
    """Initialize an agent instance with proper configuration.

    Args:
        agent_class: The agent class to instantiate
        agent_name: Name of the agent
        project_config: The project configuration
        env_config: Environment-specific configuration
        asset_manager: Optional asset manager

    Returns:
        Initialized agent instance

    Raises:
        ConfigurationError: If the agent could not be initialized
    """
    try:
        # Create agent config with the required name field
        agent_config = {
            "name": agent_name,
            **(project_config.default_config or {}),  # Include default config from project
            **env_config,  # Override with environment-specific config
        }

        # Initialize agent with configuration and asset manager
        click.echo(f"Starting agent '{agent_name}' ({agent_class.__name__})")
        return agent_class(name=agent_name, config=agent_config, asset_manager=asset_manager)
    except (ImportError, AttributeError, TypeError, ConfigurationError) as e:
        raise ConfigurationError(
            f"Error initializing agent '{agent_name}': {e}\n"
            "This may be due to configuration issues or missing dependencies."
        )
    except Exception as e:
        raise ConfigurationError(f"Unexpected error initializing agent: {e}")


def run_project(
    agent_name: str,
    project_dir: Optional[Path] = None,
    env: Optional[str] = None,
    event_loop_manager: Optional[EventLoopManager] = None,
) -> None:
    """Run an agent from the OpenMAS project.

    This is the main entry point for running agents. It:
    1. Sets up the environment
    2. Loads the project configuration
    3. Finds and initializes the agent
    4. Runs the agent with proper lifecycle management

    Args:
        agent_name: Name of the agent to run
        project_dir: Optional explicit path to the project directory
        env: Optional environment name to use for configuration
        event_loop_manager: Optional event loop manager for testing

    Raises:
        typer.Exit: When an error occurs that should terminate execution
    """
    # Set the environment if provided
    if env:
        os.environ["OPENMAS_ENV"] = env
        click.echo(f"Using environment: {env}")

    # Verify that agent_name is not empty
    if not agent_name:
        click.echo("❌ Agent name cannot be empty")
        raise typer.Exit(code=1)

    # Find project root
    project_root = find_project_root(project_dir)
    if not project_root:
        if project_dir:
            click.echo(
                f"❌ Project configuration file 'openmas_project.yml' not found in specified directory: {project_dir}"
            )
        else:
            click.echo("❌ Project configuration file 'openmas_project.yml' not found in current or parent directories")
            click.echo("Hint: Make sure you're running the command from within an OpenMAS project or use --project-dir")
        raise typer.Exit(code=1)

    click.echo(f"Using project root: {project_root}")

    # Setup project environment
    project_env = None

    try:
        # Load and validate project configuration
        project_config = load_project_config(project_root)

        # Validate agent exists in config
        agent_config_entry = validate_agent_in_config(project_config, agent_name)

        # Set up and manage the project environment
        project_env = ProjectEnvironment(project_root, project_config)
        project_env.setup_environment(agent_name)

        # Display Python import paths for debugging
        click.echo("Python import paths:")
        for i, path_str in enumerate(sys.path[:5]):
            click.echo(f"  {i + 1}. {path_str}")
        if len(sys.path) > 5:
            click.echo(f"  ... and {len(sys.path) - 5} more paths")

        # Load the agent class
        agent_loader = AgentLoader()
        agent_class = load_agent_class(agent_loader, agent_config_entry)

        # Load environment configuration
        env_config = load_environment_config(project_root, env)

        # Set up asset manager
        asset_manager = create_asset_manager(project_config)

        # Initialize the agent
        agent = initialize_agent(agent_class, agent_name, project_config, env_config, asset_manager)

        # Run the agent using the AgentExecutor
        agent_executor = AgentExecutor(agent, project_config, event_loop_manager=event_loop_manager)
        agent_executor.run()

    except ConfigurationError as e:
        click.echo(f"❌ {str(e)}")
        raise typer.Exit(code=1)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        traceback.print_exc()
        raise typer.Exit(code=1)
    finally:
        # Restore environment if it was set up
        if project_env:
            project_env.restore_environment()
