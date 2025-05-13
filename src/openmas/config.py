"""Configuration management for OpenMAS."""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Type, TypeVar, Union, cast, get_type_hints

import yaml
from dotenv import load_dotenv  # type: ignore
from pydantic import BaseModel, Field, ValidationError, field_validator

from openmas.assets.config import AssetConfig, AssetSettings
from openmas.exceptions import ConfigurationError
from openmas.logging import get_logger
from openmas.prompt.base import PromptConfig
from openmas.sampling.base import SamplingParameters

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class ConfigLoader:
    """Handles loading and parsing configuration files."""

    def load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse a YAML configuration file.

        Args:
            file_path: Path to the YAML configuration file

        Returns:
            Dictionary containing the parsed YAML or empty dict if file doesn't exist

        Raises:
            ConfigurationError: If the file exists but parsing fails
        """
        if not file_path.exists():
            logger.debug(f"Config file not found: {file_path}")
            return {}

        try:
            with open(file_path, "r") as f:
                result = yaml.safe_load(f)
                if result is None or not isinstance(result, dict):
                    logger.warning(f"Config file {file_path} does not contain a dictionary")
                    return {}
                return cast(Dict[str, Any], result)
        except yaml.YAMLError as e:
            message = f"Error parsing YAML file '{file_path}': {e}"
            logger.error(message)
            raise ConfigurationError(message)
        except Exception as e:
            message = f"Failed to load config file {file_path}: {e}"
            logger.error(message)
            raise ConfigurationError(message)


class SettingsConfig(BaseModel):
    """Global settings configuration for a project."""

    assets: Optional[AssetSettings] = None


class AgentConfig(BaseModel):
    """Configuration for an agent in the project configuration."""

    # Basic agent information
    module: Optional[str] = Field(None, description="Module path for the agent")
    class_: Optional[str] = Field(None, alias="class", description="Agent class name")
    name: str = Field(..., description="The name of the agent")

    # Communication configuration
    communicator: Optional[str] = Field(None, description="Communicator type to use for this agent")
    communicator_type: str = Field("http", description="Type of communicator to use (e.g., 'http', 'mcp_stdio')")
    communicator_options: Dict[str, Any] = Field(
        default_factory=dict, description="Options specific to the selected communicator"
    )

    # Logging and service configuration
    log_level: str = Field("INFO", description="Logging level")
    service_urls: Dict[str, str] = Field(default_factory=dict, description="Mapping of service names to URLs")

    # Extension and shared paths
    extension_paths: list[str] = Field(
        default_factory=list, description="List of paths to search for project-local extensions"
    )
    shared_paths: list[str] = Field(default_factory=list, description="List of paths to search for shared code")

    # Prompt configuration
    prompts: Optional[List[PromptConfig]] = Field(
        default=None, description="List of prompt configurations for the agent"
    )
    prompts_dir: Optional[Path] = Field(
        default=Path("prompts"),
        description="Directory where prompt template files are stored (relative to project root)",
    )

    # Sampling configuration
    sampling: Optional[SamplingParameters] = Field(default=None, description="Sampling configuration for the agent")

    # Asset requirements
    required_assets: List[str] = Field(default_factory=list, description="List of asset names required by the agent")

    # Deployment configuration
    deploy_config_path: Optional[str] = Field(None, description="Path to deployment configuration for the agent")

    model_config = {"populate_by_name": True}  # Allow using class_ without alias


class ProjectConfig(BaseModel):
    """Project configuration model."""

    name: str = Field(..., description="The name of the project")
    version: str = Field(..., description="The version of the project")
    agents: Mapping[str, Union[str, dict, AgentConfig]] = Field(
        ..., description="Mapping of agent names to configurations"
    )
    shared_paths: List[str] = Field(default_factory=list, description="List of paths to shared code")
    extension_paths: List[str] = Field(default_factory=list, description="List of paths to extensions")
    default_config: Dict[str, Any] = Field(default_factory=dict, description="Default configuration for all agents")
    agent_defaults: Dict[str, Any] = Field(default_factory=dict, description="Default values for agent configurations")
    communicator_defaults: Dict[str, Any] = Field(
        default_factory=dict, description="Default communicator configuration"
    )
    dependencies: List[Dict[str, Any]] = Field(default_factory=list, description="External dependencies")
    assets: List[AssetConfig] = Field(default_factory=list, description="List of assets used in the project")
    settings: Optional[SettingsConfig] = Field(default_factory=SettingsConfig, description="Global project settings")

    @field_validator("agents")
    def validate_agent_names(cls, agents: Mapping[str, Any]) -> Mapping[str, Any]:
        """Validate agent names to ensure they contain only alphanumeric characters, underscores, and hyphens."""
        agent_name_pattern = re.compile(r"^[a-zA-Z0-9_-]+$")

        for agent_name in agents.keys():
            if not agent_name_pattern.match(agent_name):
                raise ValueError(
                    f"Invalid agent name '{agent_name}'. Agent names must contain only alphanumeric characters, "
                    "underscores, and hyphens (matching pattern ^[a-zA-Z0-9_-]+$)."
                )

        return agents

    def model_post_init(self, __context: Any) -> None:
        """Process agents after initialization."""
        # Convert all agent entries to AgentConfig
        processed_agents: Dict[str, AgentConfig] = {}
        for name, config in self.agents.items():
            if isinstance(config, str):
                # Convert string path to module path (replace slashes with dots, strip .py extension)
                path = config.replace("/", ".")
                if path.endswith(".py"):
                    path = path[:-3]

                # Create an AgentConfig with the name from the key
                processed_agents[name] = AgentConfig.model_validate({"module": path, "class": "Agent", "name": name})
            elif isinstance(config, dict):
                # Add name field if not present
                if "name" not in config:
                    config_with_name = dict(config)
                    config_with_name["name"] = name
                    processed_agents[name] = AgentConfig.model_validate(config_with_name)
                else:
                    processed_agents[name] = AgentConfig.model_validate(config)
            elif isinstance(config, AgentConfig):
                # Update name field if exists
                if not config.name:
                    config_dict = config.model_dump()
                    config_dict["name"] = name
                    processed_agents[name] = AgentConfig.model_validate(config_dict)
                else:
                    processed_agents[name] = config
            else:
                raise ValueError(f"Invalid agent configuration for '{name}': {config}")

        # Cast to correct type to satisfy mypy
        self.agents = cast(Mapping[str, Union[str, dict, AgentConfig]], processed_agents)


def _find_project_root(project_dir: Optional[Path] = None) -> Optional[Path]:
    """Find the OpenMAS project root by looking for openmas_project.yml.

    Args:
        project_dir: Optional explicit path to the project directory. If provided,
                    will check if this directory contains a openmas_project.yml file.

    Returns:
        Path to the project root directory or None if not found
    """
    # If a project directory is explicitly provided, check if it contains the project file
    if project_dir is not None:
        project_dir = Path(project_dir).resolve()
        if (project_dir / "openmas_project.yml").exists():
            return project_dir
        else:
            logger.warning(f"No openmas_project.yml found in specified project directory: {project_dir}")
            return None

    # Otherwise, search for the project file in current and parent directories
    current_dir = Path.cwd()

    # Try current directory first
    if (current_dir / "openmas_project.yml").exists():
        return current_dir

    # Then check parent directories (limit to a reasonable depth to avoid infinite loops)
    for _ in range(10):  # Maximum depth of 10 directories
        current_dir = current_dir.parent
        if (current_dir / "openmas_project.yml").exists():
            return current_dir

    logger.warning("No openmas_project.yml found in current or parent directories")
    return None


def _load_yaml_config(file_path: Path) -> Dict[str, Any]:
    """Load and parse a YAML configuration file.

    Args:
        file_path: Path to the YAML configuration file

    Returns:
        Dictionary containing the parsed YAML or empty dict if file doesn't exist

    Raises:
        ConfigurationError: If the file exists but parsing fails
    """
    if not file_path.exists():
        logger.debug(f"Config file not found: {file_path}")
        return {}

    try:
        with open(file_path, "r") as f:
            result = yaml.safe_load(f)
            if result is None or not isinstance(result, dict):
                logger.warning(f"Config file {file_path} does not contain a dictionary")
                return {}
            return cast(Dict[str, Any], result)
    except yaml.YAMLError as e:
        message = f"Failed to parse YAML in config file {file_path}: {e}"
        logger.error(message)
        raise ConfigurationError(message)
    except Exception as e:
        message = f"Failed to load config file {file_path}: {e}"
        logger.error(message)
        raise ConfigurationError(message)


def _deep_merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries.

    The override dictionary values take precedence over base values.
    If both values are dictionaries, they are merged recursively.

    Args:
        base: Base dictionary
        override: Dictionary with override values

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def _load_project_config(project_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load the OpenMAS project config from YAML.

    Args:
        project_dir: Optional explicit path to the project directory.

    Returns:
        Dictionary containing the project configuration or empty dict if not found

    Raises:
        ConfigurationError: If the project config exists but parsing fails
    """
    config: Dict[str, Any] = {}

    # First check if the project config is provided in environment variable
    # (set by the CLI when running agents)
    project_config_env = os.environ.get("OPENMAS_PROJECT_CONFIG")
    if project_config_env:
        try:
            result = yaml.safe_load(project_config_env)
            if result is None or not isinstance(result, dict):
                logger.warning("Project config from environment is not a dictionary")
                return {}
            logger.debug("Loaded project config from OPENMAS_PROJECT_CONFIG environment variable")

            # Validate the config with the ProjectConfig model
            try:
                # Pre-process agents to proper format if they are strings
                if "agents" in result and isinstance(result["agents"], dict):
                    processed_agents = {}
                    for name, config in result["agents"].items():
                        if isinstance(config, str):
                            path = config.replace("/", ".")
                            if path.endswith(".py"):
                                path = path[:-3]
                            processed_agents[name] = {"module": path, "class": "Agent"}
                        else:
                            processed_agents[name] = config
                    result["agents"] = processed_agents

                project_config = ProjectConfig(**result)
                return dict(project_config.model_dump())
            except ValidationError as e:
                message = f"Invalid project configuration in OPENMAS_PROJECT_CONFIG: {e}"
                logger.error(message)
                raise ConfigurationError(message)
        except yaml.YAMLError as e:
            message = f"Failed to parse YAML in OPENMAS_PROJECT_CONFIG: {e}"
            logger.error(message)
            raise ConfigurationError(message)
        except Exception as e:
            logger.warning(f"Failed to parse project config from environment: {e}")
            return {}

    # Otherwise, try to load from file
    project_root = _find_project_root(project_dir)
    if project_root:
        try:
            config_path = project_root / "openmas_project.yml"
            config_dict = _load_yaml_config(config_path)
            if config_dict:
                logger.info(f"Loaded project config from {config_path}")

                # Validate the config with the ProjectConfig model
                try:
                    # Pre-process agents to proper format if they are strings
                    if "agents" in config_dict and isinstance(config_dict["agents"], dict):
                        processed_agents = {}
                        for name, config in config_dict["agents"].items():
                            if isinstance(config, str):
                                path = config.replace("/", ".")
                                if path.endswith(".py"):
                                    path = path[:-3]
                                processed_agents[name] = {"module": path, "class": "Agent"}
                            else:
                                processed_agents[name] = config
                        config_dict["agents"] = processed_agents

                    project_config = ProjectConfig(**config_dict)
                    config = dict(project_config.model_dump())
                except ValidationError as e:
                    message = f"Invalid project configuration in {config_path}: {e}"
                    logger.error(message)
                    raise ConfigurationError(message)
        except ConfigurationError as e:
            # Re-raise with clearer message
            raise ConfigurationError(f"Error in project config file (openmas_project.yml): {e}")
    else:
        logger.warning("No openmas_project.yml found in project directory")

    return config


def _load_env_file(project_dir: Optional[Path] = None) -> None:
    """Load environment variables from .env file at the project root.

    Args:
        project_dir: Optional explicit path to the project directory.

    Uses python-dotenv with override=True to ensure env vars take precedence if also set directly.
    """
    project_root = _find_project_root(project_dir)
    if not project_root:
        logger.debug("Project root not found, skipping .env file loading")
        return

    env_file = project_root / ".env"
    if env_file.exists():
        try:
            load_dotenv(env_file, override=True)
            logger.debug(f"Loaded environment variables from {env_file}")
        except Exception as e:
            logger.warning(f"Failed to load .env file: {e}")
            # Continue execution, don't raise an error for .env file failures
    else:
        logger.debug(f".env file not found: {env_file}")


def _load_environment_config_files(project_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from environment-specific YAML files.

    Args:
        project_dir: Optional explicit path to the project directory.

    Loads config/default.yml and config/<OPENMAS_ENV>.yml if they exist.
    The environment-specific config overrides default config.

    Returns:
        A dictionary containing merged configuration from files
    """
    config_data: Dict[str, Any] = {}
    project_root = _find_project_root(project_dir)

    if not project_root:
        logger.debug("Project root not found, skipping config file loading")
        return {}

    # Create the config directory path
    config_dir = project_root / "config"
    if not config_dir.exists():
        logger.debug(f"Config directory does not exist: {config_dir}")
        return {}

    # Load default config file
    default_config_path = config_dir / "default.yml"
    try:
        default_config = _load_yaml_config(default_config_path)
        if default_config:
            logger.debug(f"Loaded default configuration from {default_config_path}")
            config_data = default_config
    except ConfigurationError as e:
        # Re-raise with clearer message
        raise ConfigurationError(f"Error in default config file (config/default.yml): {e}")

    # Load environment-specific config if OPENMAS_ENV is set
    # If OPENMAS_ENV is not set, default to 'local'
    env_name = os.environ.get("OPENMAS_ENV", "local")
    env_config_path = config_dir / f"{env_name}.yml"

    try:
        env_config = _load_yaml_config(env_config_path)
        if env_config:
            logger.debug(f"Loaded environment configuration from {env_config_path}")
            config_data = _deep_merge_dicts(config_data, env_config)
    except ConfigurationError as e:
        # Re-raise with clearer message
        raise ConfigurationError(f"Error in environment config file (config/{env_name}.yml): {e}")

    return config_data


def _coerce_env_value(value: str, target_type: Any) -> Any:
    """Coerce environment variable values to appropriate types.

    Args:
        value: The string value from the environment
        target_type: The target type to convert to

    Returns:
        The coerced value
    """
    if target_type == bool:
        # Handle boolean values case-insensitively
        if value.lower() in ("true", "yes", "1", "y", "t"):
            return True
        elif value.lower() in ("false", "no", "0", "n", "f"):
            return False
        else:
            raise ValueError(f"Cannot convert '{value}' to boolean")

    if target_type == int:
        # Convert numeric strings to integer
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to integer")

    if target_type == float:
        # Convert numeric strings to float
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to float")

    # Default to string
    return value


def _get_env_var_with_type(name: str, target_type: Any, prefix: str = "") -> Optional[Any]:
    """Get environment variable with type conversion.

    Args:
        name: Environment variable name (without prefix)
        target_type: Target type for conversion
        prefix: Optional prefix for environment variables

    Returns:
        Converted value or None if variable doesn't exist
    """
    env_name = f"{prefix}_{name}" if prefix else name
    value = os.environ.get(env_name)

    if value is None:
        return None

    try:
        return _coerce_env_value(value, target_type)
    except (ValueError, TypeError) as e:
        message = f"Failed to convert environment variable {env_name} value '{value}' to {target_type.__name__}: {e}"
        logger.error(message)
        raise ConfigurationError(message)


def load_config(config_model: Type[T], prefix: str = "", project_dir: Optional[Path] = None) -> T:
    """Load configuration from files, environment variables and project configuration.

    Configuration is loaded in the following order (lowest to highest precedence):
    1. SDK Internal Defaults (in the Pydantic model)
    2. Project Defaults: default_config section in openmas_project.yml
    3. Default Environment YAML: config/default.yml
    4. Environment-specific YAML: config/<OPENMAS_ENV>.yml (defaults to local)
    5. .env File(s): Loaded from project directory
    6. Environment Variables: Directly set in the shell (Highest)

    Args:
        config_model: The Pydantic model to use for validation
        prefix: Optional prefix for environment variables
        project_dir: Optional explicit path to the project directory

    Returns:
        A validated configuration object

    Raises:
        ConfigurationError: If configuration loading or validation fails
    """
    try:
        # Build our configuration in correct precedence order (lowest to highest)
        config_data: Dict[str, Any] = {}
        env_prefix = f"{prefix}_" if prefix else ""

        # [LAYER 1] SDK Internal Defaults - These are in the Pydantic model
        # Nothing to do here, as Pydantic will use these if no value is provided

        # [LAYER 2] Project Defaults (default_config in openmas_project.yml)
        project_config = _load_project_config(project_dir)
        default_config = project_config.get("default_config", {})
        if default_config:
            logger.debug("Applying default configuration from project config")
            config_data.update(default_config)

        # Store project-level shared_paths and extension_paths for later
        project_shared_paths = project_config.get("shared_paths", [])
        project_extension_paths = project_config.get("extension_paths", [])

        # [LAYER 3 & 4] Config files (default.yml and <env>.yml)
        yaml_config = _load_environment_config_files(project_dir)
        if yaml_config:
            logger.debug("Applying configuration from YAML files")
            config_data = _deep_merge_dicts(config_data, yaml_config)

        # [LAYER 5] .env file from project directory
        # This affects the environment variables, loaded next
        _load_env_file(project_dir)

        # [LAYER 6] Environment Variables (highest precedence)

        # First check for a JSON config string (highest precedence)
        json_config = os.environ.get(f"{env_prefix}CONFIG")
        if json_config:
            try:
                env_config_data = json.loads(json_config)
                logger.debug(f"Loaded configuration from JSON in {env_prefix}CONFIG")
                config_data = _deep_merge_dicts(config_data, env_config_data)
            except json.JSONDecodeError as e:
                raise ConfigurationError(f"Invalid JSON in {env_prefix}CONFIG: {e}")

        # Process specific environment variables

        # Agent name
        name = os.environ.get(f"{env_prefix}AGENT_NAME")
        if name:
            config_data["name"] = name

        # Log level
        log_level = os.environ.get(f"{env_prefix}LOG_LEVEL")
        if log_level:
            config_data["log_level"] = log_level

        # Communicator type
        communicator_type = os.environ.get(f"{env_prefix}COMMUNICATOR_TYPE")
        if communicator_type:
            config_data["communicator_type"] = communicator_type

        # Service URLs (JSON dictionary)
        service_urls_str = os.environ.get(f"{env_prefix}SERVICE_URLS")
        if service_urls_str:
            try:
                service_urls = json.loads(service_urls_str)
                if not isinstance(service_urls, dict):
                    raise ConfigurationError(f"{env_prefix}SERVICE_URLS must be a JSON dictionary")

                # Initialize service_urls if not present
                if "service_urls" not in config_data:
                    config_data["service_urls"] = {}

                # Merge service URLs
                config_data["service_urls"] = _deep_merge_dicts(config_data["service_urls"], service_urls)
            except json.JSONDecodeError as e:
                raise ConfigurationError(f"Invalid JSON in {env_prefix}SERVICE_URLS: {e}")

        # Load individual service URLs if defined
        for key, value in os.environ.items():
            if key.startswith(f"{env_prefix}SERVICE_URL_"):
                service_name = key[len(f"{env_prefix}SERVICE_URL_") :].lower()
                if "service_urls" not in config_data:
                    config_data["service_urls"] = {}
                config_data["service_urls"][service_name] = value

        # Apply extension_paths from project config first
        if project_extension_paths:
            if "extension_paths" not in config_data:
                config_data["extension_paths"] = []
            # Add project paths to existing extension_paths
            for path in project_extension_paths:
                if path not in config_data["extension_paths"]:
                    config_data["extension_paths"].append(path)
            logger.debug(f"Applied extension_paths from project: {project_extension_paths}")

        # Apply shared_paths from project config
        if project_shared_paths:
            if "shared_paths" not in config_data:
                config_data["shared_paths"] = []
            # Add project paths to existing shared_paths
            for path in project_shared_paths:
                if path not in config_data["shared_paths"]:
                    config_data["shared_paths"].append(path)
            logger.debug(f"Applied shared_paths from project: {project_shared_paths}")

        # Handle special case for extension_paths from env var (JSON list of strings)
        extension_paths_var = f"{env_prefix}EXTENSION_PATHS"
        if extension_paths_var in os.environ:
            try:
                extension_paths = json.loads(os.environ[extension_paths_var])
                if not isinstance(extension_paths, list):
                    raise ConfigurationError(f"{extension_paths_var} must be a JSON array")

                # Initialize extension_paths if not present
                if "extension_paths" not in config_data:
                    config_data["extension_paths"] = []

                # Add any paths from the environment that aren't already in the list
                for path in extension_paths:
                    if path not in config_data["extension_paths"]:
                        config_data["extension_paths"].append(path)

                logger.debug(f"Applied environment variable {extension_paths_var}: {extension_paths}")
            except json.JSONDecodeError as e:
                raise ConfigurationError(f"Invalid JSON in {extension_paths_var}: {e}")

        # Handle special case for shared_paths from env var (JSON list of strings)
        shared_paths_var = f"{env_prefix}SHARED_PATHS"
        if shared_paths_var in os.environ:
            try:
                shared_paths = json.loads(os.environ[shared_paths_var])
                if not isinstance(shared_paths, list):
                    raise ConfigurationError(f"{shared_paths_var} must be a JSON array")

                # Initialize shared_paths if not present
                if "shared_paths" not in config_data:
                    config_data["shared_paths"] = []

                # Add any paths from the environment that aren't already in the list
                for path in shared_paths:
                    if path not in config_data["shared_paths"]:
                        config_data["shared_paths"].append(path)

                logger.debug(f"Applied environment variable {shared_paths_var}: {shared_paths}")
            except json.JSONDecodeError as e:
                raise ConfigurationError(f"Invalid JSON in {shared_paths_var}: {e}")

        # Communicator options (JSON dictionary)
        communicator_options_str = os.environ.get(f"{env_prefix}COMMUNICATOR_OPTIONS")
        if communicator_options_str:
            try:
                communicator_options = json.loads(communicator_options_str)
                if not isinstance(communicator_options, dict):
                    raise ConfigurationError(f"{env_prefix}COMMUNICATOR_OPTIONS must be a JSON dictionary")

                # Initialize communicator_options if not present
                if "communicator_options" not in config_data:
                    config_data["communicator_options"] = {}

                # Merge communicator options
                config_data["communicator_options"] = _deep_merge_dicts(
                    config_data["communicator_options"], communicator_options
                )
                logger.debug(f"Applied environment variable {env_prefix}COMMUNICATOR_OPTIONS: {communicator_options}")
            except json.JSONDecodeError as e:
                raise ConfigurationError(f"Invalid JSON in {env_prefix}COMMUNICATOR_OPTIONS: {e}")

        # Individual communicator options
        for key, value in os.environ.items():
            if key.startswith(f"{env_prefix}COMMUNICATOR_OPTION_"):
                option_name = key[len(f"{env_prefix}COMMUNICATOR_OPTION_") :].lower()
                if "communicator_options" not in config_data:
                    config_data["communicator_options"] = {}

                # Try to interpret the value
                try:
                    # First try to parse as JSON
                    option_value = json.loads(value)
                except json.JSONDecodeError:
                    # If not valid JSON, try simple type conversions
                    if value.lower() == "true":
                        option_value = True
                    elif value.lower() == "false":
                        option_value = False
                    elif value.isdigit():
                        option_value = int(value)
                    elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                        option_value = float(value)
                    else:
                        # Keep as string
                        option_value = value

                config_data["communicator_options"][option_name] = option_value
                logger.debug(f"Applied environment variable {key}={value}")

        # Create and validate the model instance
        logger.debug(f"Creating configuration model with data: {config_data}")
        model_instance = config_model(**config_data)
        logger.debug(f"Configuration loaded successfully: {model_instance}")

        # Return the validated configuration
        return model_instance
    except ValidationError as e:
        message = f"Configuration validation failed: {e}"
        logger.error(message)
        raise ConfigurationError(message)
    except ConfigurationError:
        # Re-raise configuration errors as they're already properly formatted
        raise
    except Exception as e:
        message = f"Unexpected error loading configuration: {e}"
        logger.error(message, exc_info=True)
        raise ConfigurationError(message)


def _update_from_env(config_dict: Dict[str, Any], model_class: Type[T], env_prefix: str = "OPENMAS_") -> Dict[str, Any]:
    """Update the config dictionary with values from environment variables.

    This function recursively processes environment variables that match expected fields
    in the given model class, converting them to the appropriate types.

    Args:
        config_dict: Current configuration dictionary to update
        model_class: Pydantic model class to use for type information
        env_prefix: Prefix for environment variables (e.g., "OPENMAS_")

    Returns:
        Updated configuration dictionary
    """
    # Get the type hints for the model fields
    model_fields = get_type_hints(model_class)

    # Handle top-level fields
    for field_name, field_type in model_fields.items():
        # Skip fields with leading underscore
        if field_name.startswith("_"):
            continue

        # Convert to uppercase for environment variables
        env_name = f"{env_prefix}{field_name.upper()}"

        # Check if the environment variable exists
        value = os.environ.get(env_name)

        if value is not None:
            try:
                config_dict[field_name] = _coerce_env_value(value, field_type)
                logger.debug(f"Applied environment variable {env_name} = {value}")
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to apply environment variable {env_name}: {e}")

    # Handle special case for extension_paths - JSON list of strings
    extension_paths_var = f"{env_prefix}EXTENSION_PATHS"
    if extension_paths_var in os.environ:
        try:
            extension_paths = json.loads(os.environ[extension_paths_var])
            if not isinstance(extension_paths, list):
                raise ConfigurationError(f"{extension_paths_var} must be a JSON array")
            config_dict["extension_paths"] = extension_paths
            logger.debug(f"Applied environment variable {extension_paths_var}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {extension_paths_var}: {e}")

    # Handle special case for shared_paths - JSON list of strings
    shared_paths_var = f"{env_prefix}SHARED_PATHS"
    if shared_paths_var in os.environ:
        try:
            shared_paths = json.loads(os.environ[shared_paths_var])
            if not isinstance(shared_paths, list):
                raise ConfigurationError(f"{shared_paths_var} must be a JSON array")
            config_dict["shared_paths"] = shared_paths
            logger.debug(f"Applied environment variable {shared_paths_var}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {shared_paths_var}: {e}")

    # Handle special case for communicator_options - JSON dictionary
    communicator_options_var = f"{env_prefix}COMMUNICATOR_OPTIONS"
    if communicator_options_var in os.environ:
        try:
            communicator_options = json.loads(os.environ[communicator_options_var])
            if not isinstance(communicator_options, dict):
                raise ConfigurationError(f"{communicator_options_var} must be a JSON dictionary")

            # Initialize communicator_options if not present
            if "communicator_options" not in config_dict:
                config_dict["communicator_options"] = {}

            # Merge options rather than replace
            config_dict["communicator_options"] = _deep_merge_dicts(
                config_dict["communicator_options"], communicator_options
            )
            logger.debug(f"Applied environment variable {communicator_options_var}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {communicator_options_var}: {e}")

    # Handle individual communicator options (COMMUNICATOR_OPTION_*)
    for key, value in os.environ.items():
        if key.startswith(f"{env_prefix}COMMUNICATOR_OPTION_"):
            option_name = key[len(f"{env_prefix}COMMUNICATOR_OPTION_") :].lower()

            # Initialize communicator_options if not present
            if "communicator_options" not in config_dict:
                config_dict["communicator_options"] = {}

            # Try to interpret the value
            try:
                # First try to parse as JSON
                option_value = json.loads(value)
            except json.JSONDecodeError:
                # If not valid JSON, try simple type conversions
                if value.lower() == "true":
                    option_value = True
                elif value.lower() == "false":
                    option_value = False
                elif value.isdigit():
                    option_value = int(value)
                elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                    option_value = float(value)
                else:
                    # Keep as string
                    option_value = value

            config_dict["communicator_options"][option_name] = option_value
            logger.debug(f"Applied environment variable {key}")

    return config_dict
