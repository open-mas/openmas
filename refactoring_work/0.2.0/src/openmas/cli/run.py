"""CLI run module for OpenMAS."""

import importlib
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any

import click
import typer
import yaml
from pydantic import ValidationError  # Added to handle validation errors

from openmas.agent.base import BaseAgent
from openmas.assets.manager import AssetManager
from openmas.cli.agent_executor import AgentExecutor
from openmas.cli.agent_loader import AgentLoader
from openmas.cli.event_loop import EventLoopManager
from openmas.cli.project_env import ProjectEnvironment
from openmas.config import AgentConfig, ConfigLoader, ProjectConfig, _deep_merge_dicts, _find_project_root, logger
from openmas.exceptions import ConfigurationError


def find_project_root(project_dir: Path | None = None) -> Path | None:
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


def validate_agent_in_config(project_config: ProjectConfig, agent_name: str) -> AgentConfig:
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
    if not isinstance(agent_config_entry, AgentConfig):
        raise ConfigurationError(f"Invalid agent configuration for '{agent_name}'")

    return agent_config_entry


def load_environment_config(project_root: Path, env: str | None = None) -> dict[str, Any]:
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
        config = config_loader.load_yaml_file(env_config_path)
        logger.info(f"Loaded environment config: {config}")
        click.echo(f"Using environment configuration from {env_config_path}")
        if "communicator_options" in config and "http_port" in config["communicator_options"]:
            click.echo(f"Environment config sets HTTP port: {config['communicator_options']['http_port']}")
        return config

    logger.debug(f"Environment config file not found: {env_config_path}")
    return {}


def load_agent_class(agent_loader: AgentLoader, agent_config_entry: AgentConfig) -> type[BaseAgent]:
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
        module_path = agent_config_entry.module
        if module_path is None:
            raise ConfigurationError("Agent configuration missing 'module' attribute")

        return agent_loader.load_agent_class(
            module_path,
            agent_config_entry.class_ if hasattr(agent_config_entry, "class_") else None,
        )
    except (ImportError, ConfigurationError) as e:
        # Check for the specific error about class not found to match test expectations
        if "not found in module" in str(e) and "class" in str(e).lower():
            class_name = getattr(agent_config_entry, "class_", None)
            raise ConfigurationError(f"Error finding agent class: Specified agent class '{class_name}' not found.")
        # Otherwise just pass through the original error
        raise ConfigurationError(f"Error loading agent: {e}")


def create_asset_manager(project_config: ProjectConfig) -> AssetManager | None:
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


def verify_communicator_dependencies(communicator_type: str) -> None:
    """Verify that required dependencies for a specific communicator type are installed.

    Args:
        communicator_type: The communicator type to verify

    Raises:
        ConfigurationError: If required dependencies are not installed
    """
    # Define dependency requirements for each communicator type
    dependency_map = {
        "mcp-sse": [("mcp", "python-sdk", "pip install 'openmas[mcp]'")],
        "mcp-stdio": [("mcp", "python-sdk", "pip install 'openmas[mcp]'")],
        "grpc": [("grpcio", "grpcio", "pip install 'openmas[grpc]'")],
        "mqtt": [("paho.mqtt", "paho-mqtt", "pip install 'openmas[mqtt]'")],
    }

    # Skip verification for HTTP communicator (always available) or unknown types
    if communicator_type == "http" or communicator_type not in dependency_map:
        return

    # Check all required dependencies for the specified communicator type
    missing_deps = []
    for module_name, package_name, install_cmd in dependency_map.get(communicator_type, []):
        try:
            importlib.import_module(module_name)
            logger.debug(f"Dependency {module_name} ({package_name}) is installed")
        except ImportError:
            missing_deps.append((module_name, package_name, install_cmd))

    # If any dependencies are missing, raise an error with installation instructions
    if missing_deps:
        missing_info = ", ".join([f"{pkg}" for _, pkg, _ in missing_deps])
        install_cmds = "\n".join([f"  {cmd}" for _, _, cmd in missing_deps])
        error_msg = (
            f"Missing dependencies for communicator '{communicator_type}': {missing_info}\n"
            f"Install the required dependencies with:\n{install_cmds}"
        )
        logger.error(error_msg)
        click.echo(click.style(error_msg, fg="red"))
        raise ConfigurationError(error_msg)


def initialize_agent(
    agent_class: type[BaseAgent],
    agent_name: str,
    project_config: ProjectConfig,
    env_config: dict[str, Any],
    agent_config_entry: AgentConfig,
    asset_manager: AssetManager | None,
    project_root: Path,
) -> BaseAgent:
    """Initialize an agent instance with proper configuration.

    Args:
        agent_class: The agent class to instantiate
        agent_name: Name of the agent
        project_config: The project configuration
        env_config: Environment-specific configuration
        agent_config_entry: The agent's specific configuration
        asset_manager: Optional asset manager
        project_root: Path to the project root

    Returns:
        Initialized agent instance

    Raises:
        ConfigurationError: If the agent could not be initialized
    """
    logger.info(f"INITIALIZE_AGENT CALLED FOR: {agent_name}")
    logger.info(f"INITIALIZE_AGENT - SEEN ENVIRONMENT: {os.environ}")
    logger.info(f"INITIALIZE_AGENT - AGENT_CONFIG_ENTRY (from project.yml): {agent_config_entry.model_dump()}")
    try:
        # Create the agent configuration by merging defaults and specifics in the right order
        # Order of precedence (highest to lowest):
        # 1. Environment variables (handled by agent constructor)
        # 2. Agent-specific configuration
        # 3. Communicator defaults from project config
        # 4. Environment-specific configuration
        # 5. Project default_config

        # 1. Start with default config from project
        merged_config: dict[str, Any] = {}
        if "default_config" in project_config.model_dump():
            merged_config.update(project_config.default_config)
            logger.debug(f"Applied default config from project for agent {agent_name}")

        # 2. Add environment-specific config
        merged_config = _deep_merge_dicts(merged_config, env_config)
        logger.debug(f"Applied environment-specific config for agent {agent_name}")

        # 3. Add communicator defaults if this agent uses that communicator type

        # Handle special case for testing where communicator may be set but communicator_type is still default
        # Important: we set this directly in merged_config because we need it to take effect before using it
        if agent_config_entry.communicator:
            merged_config["communicator_type"] = agent_config_entry.communicator
            agent_communicator_type = agent_config_entry.communicator
        else:
            agent_communicator_type = agent_config_entry.communicator_type

        # Look for communicator defaults in project config
        if project_config.communicator_defaults:
            # For backward compatibility, check the old structure with 'type' and 'options'
            if "type" in project_config.communicator_defaults:
                # Use the type from communicator_defaults if none was specified in agent config
                if not agent_config_entry.communicator:
                    merged_config["communicator_type"] = project_config.communicator_defaults["type"]
                    agent_communicator_type = project_config.communicator_defaults["type"]

                # Apply options if present
                if "options" in project_config.communicator_defaults:
                    options = project_config.communicator_defaults["options"]
                    if "communicator_options" not in merged_config:
                        merged_config["communicator_options"] = {}
                    merged_config["communicator_options"] = _deep_merge_dicts(
                        merged_config.get("communicator_options", {}), options
                    )
            # Try to match directly if not using 'type' and 'options' structure
            elif agent_communicator_type in project_config.communicator_defaults:
                comm_defaults = project_config.communicator_defaults[agent_communicator_type]
                logger.debug(
                    f"Applying {agent_communicator_type} communicator defaults for agent {agent_name}",
                    defaults=comm_defaults,
                )
                # Ensure we have a communicator_options dict
                if "communicator_options" not in merged_config:
                    merged_config["communicator_options"] = {}
                # Apply communicator defaults to communicator_options
                merged_config["communicator_options"] = _deep_merge_dicts(
                    merged_config.get("communicator_options", {}), comm_defaults
                )

        # 4. Add agent-specific configuration (highest priority except for env vars)
        # First get the config as a dictionary
        agent_config_dict = agent_config_entry.model_dump(exclude_unset=True)
        merged_config = _deep_merge_dicts(merged_config, agent_config_dict)
        logger.debug(f"Applied agent-specific config for agent {agent_name}")

        # Handle OPENMAS_PROMPTS environment variable
        prompts_env_var_str = os.environ.get("OPENMAS_PROMPTS")
        if prompts_env_var_str:
            try:
                prompts_data = json.loads(prompts_env_var_str)
                if isinstance(prompts_data, list):
                    merged_config["prompts"] = prompts_data
                    logger.info("Loaded prompts configuration from OPENMAS_PROMPTS environment variable.")
                else:
                    logger.warning("OPENMAS_PROMPTS environment variable is not a valid JSON list. Ignoring.")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from OPENMAS_PROMPTS environment variable: {e}. Ignoring.")

        # Ensure communicator_type is set to communicator if provided
        if agent_config_entry.communicator:
            merged_config["communicator_type"] = agent_config_entry.communicator
            logger.debug(f"Set communicator_type to {agent_config_entry.communicator} from communicator field")

        # 5. Apply environment variables (highest priority)
        # Check for environment variables that should override the configuration
        # Format: OPENMAS_COMMUNICATOR_OPTIONS_HTTP_PORT=8888
        prefix = "OPENMAS_"
        for key, value in os.environ.items():
            if key.startswith(f"{prefix}COMMUNICATOR_OPTIONS_"):
                option_name = key[len(f"{prefix}COMMUNICATOR_OPTIONS_") :].lower()

                # Ensure communicator_options exists
                if "communicator_options" not in merged_config:
                    merged_config["communicator_options"] = {}

                # Convert value to appropriate type
                typed_value: Any
                if option_name == "http_port" and value.isdigit():
                    # Special case for port which needs to be an integer
                    merged_config["communicator_options"][option_name] = int(value)
                    logger.info(f"Environment variable overrides http_port: {value}")
                    print(f"Using environment variable {key}={value}")
                else:
                    # For other values, try to convert to appropriate type
                    if value.lower() == "true":
                        typed_value = True
                    elif value.lower() == "false":
                        typed_value = False
                    elif value.isdigit():
                        typed_value = int(value)
                    elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                        typed_value = float(value)
                    else:
                        typed_value = value

                    merged_config["communicator_options"][option_name] = typed_value
                    logger.info(f"Environment variable overrides {option_name}: {typed_value}")
                    print(f"Using environment variable {key}={value}")

        # Let's log the final configuration for debugging
        logger.debug(f"Final agent configuration for {agent_name}: {merged_config}")

        # ADD DEBUGGING HERE
        logger.info(
            "BEFORE AgentConfig instantiation: merged_config['prompts'] is %s, type is %s",
            merged_config.get("prompts"),
            type(merged_config.get("prompts")),
        )

        # Explicitly create AgentConfig instance from the merged dictionary
        # This ensures Pydantic handles parsing of nested models like prompts.
        try:
            final_agent_config = AgentConfig(**merged_config)
        except ValidationError as e:
            error_msg = f"Validation error when creating final AgentConfig for {agent_name}: {e}"
            logger.error(error_msg, exc_info=True)
            raise ConfigurationError(error_msg)

        # Initialize the agent with the validated AgentConfig object
        return agent_class(
            name=agent_name,
            config=final_agent_config,  # Pass the AgentConfig instance
            project_root=project_root,
            asset_manager=asset_manager,
        )
    except Exception as e:
        error_msg = f"Failed to initialize agent {agent_name}: {e}"
        logger.error(error_msg, exc_info=True)
        raise ConfigurationError(error_msg)


def run_project(
    agent_name: str,
    project_dir: Path | None = None,
    env: str | None = None,
    event_loop_manager: EventLoopManager | None = None,
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

        # Log the agent's configuration entry for debugging
        communicator_type = agent_config_entry.communicator or "default"
        click.echo(f"Agent configuration entry for '{agent_name}':")
        click.echo(f"  Module: {agent_config_entry.module}")
        click.echo(f"  Class: {agent_config_entry.class_}")
        click.echo(f"  Communicator: {communicator_type}")

        # Log communicator options if any
        if agent_config_entry.communicator_options:
            click.echo("  Communicator options:")
            for key, value in agent_config_entry.communicator_options.items():
                click.echo(f"    {key}: {value}")

            # Specifically log port for better visibility
            if "http_port" in agent_config_entry.communicator_options:
                click.echo(f"  HTTP port configured: {agent_config_entry.communicator_options['http_port']}")

        # Verify that the required dependencies for the communicator are installed
        if agent_config_entry.communicator:
            click.echo(f"Verifying dependencies for communicator: {agent_config_entry.communicator}")
            verify_communicator_dependencies(agent_config_entry.communicator)

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
        agent = initialize_agent(
            agent_class,
            agent_name,
            project_config,
            env_config,
            agent_config_entry,
            asset_manager,
            project_root,  # Pass the project_root directly
        )

        # Show final communicator configuration
        communicator_type = agent.config.communicator_type
        click.echo(f"Starting agent '{agent_name}' with communicator: {communicator_type}")

        # Log the final configuration for better debugging
        if communicator_type.startswith("mcp-"):
            port = agent.config.communicator_options.get("http_port", 8000)
            host = agent.config.communicator_options.get("http_host", "0.0.0.0")
            logger.debug(f"Final MCP configuration: host={host}, port={port}")
            click.echo(f"MCP server will use: {host}:{port}")

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
