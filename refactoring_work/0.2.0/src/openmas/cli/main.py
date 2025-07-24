"""Main CLI module for OpenMAS."""

import json
import logging
import os
import platform
import sys
import traceback
from importlib import metadata
from pathlib import Path
from typing import Any

import click
import typer
import yaml
from dotenv import load_dotenv  # type: ignore

from openmas import __version__
from openmas.cli.assets import assets_app
from openmas.cli.project_initializer import ProjectInitializer
from openmas.cli.prompts import prompts
from openmas.cli.validate import validate_config
from openmas.exceptions import ConfigurationError
from openmas.logging import configure_logging, get_logger, set_global_log_level

# Import the CLI commands from their respective modules
# The deploy command will be added separately since it's using typer
# from openmas.cli.deploy import deploy_cmd

logger = get_logger(__name__)


# Enhanced version display for the built-in version option
def version_callback(ctx: click.Context | None, param: click.Parameter, value: bool) -> None:
    # For testing purposes or direct calls, handle None ctx
    resilient_parsing = False if ctx is None else getattr(ctx, "resilient_parsing", False)

    if not value or resilient_parsing:
        return

    # Logging is now handled by default quietness and main() function logic
    # No need to suppress logging here anymore.

    try:
        # Standard version info
        click.echo(f"OpenMAS, version {__version__}")

        click.echo("\nKey Features & Integrations:")
        click.echo("  - HTTP Communicator: Enabled")

        # Check for MCP availability
        try:
            # Try importing mcp using importlib
            import importlib.util

            mcp_spec = importlib.util.find_spec("mcp")
            has_mcp = mcp_spec is not None

            if has_mcp:
                mcp_version = metadata.version("mcp")
                click.echo("  - MCP (Model Context Protocol):")
                click.echo(f"      - SDK Version: {mcp_version}")
                click.echo("      - Available Communicators: mcp-sse, mcp-stdio")
            else:
                raise ImportError("Module not found")
        except ImportError:
            # MCP not available
            click.echo("  - MCP (Model Context Protocol): Not installed")
        except Exception:
            # MCP is available but version couldn't be determined
            click.echo("  - MCP (Model Context Protocol):")
            click.echo("      - SDK Version: unknown")
            click.echo("      - Available Communicators: mcp-sse, mcp-stdio")

        # Check for gRPC availability
        try:
            # Try importing grpc
            grpc_spec = importlib.util.find_spec("grpc")
            has_grpc = grpc_spec is not None

            if has_grpc:
                grpc_version = metadata.version("grpcio")
                click.echo("  - gRPC:")
                click.echo(f"      - SDK Version: {grpc_version}")
                click.echo("      - Available Communicators: grpc")
            else:
                raise ImportError("Module not found")
        except ImportError:
            # gRPC not available
            click.echo("  - gRPC: Not installed")
        except Exception:
            # gRPC is available but version couldn't be determined
            click.echo("  - gRPC:")
            click.echo("      - SDK Version: unknown")
            click.echo("      - Available Communicators: grpc")

        # Check for MQTT availability
        try:
            import importlib.metadata

            # Try importing paho.mqtt in a way that doesn't trigger unused import warnings
            mqtt_spec = importlib.util.find_spec("paho.mqtt")
            has_mqtt = mqtt_spec is not None

            if has_mqtt:
                mqtt_version = importlib.metadata.version("paho-mqtt")
                click.echo("  - MQTT:")
                click.echo(f"      - SDK Version: {mqtt_version}")
                click.echo("      - Available Communicators: mqtt")
            else:
                raise ImportError("Module not found")
        except ImportError:
            # MQTT not available
            click.echo("  - MQTT: Not installed")
        except Exception:
            # MQTT is available but version couldn't be determined
            click.echo("  - MQTT:")
            click.echo("      - SDK Version: unknown")
            click.echo("      - Available Communicators: mqtt")
    finally:
        # Restore previous logging level - No longer needed
        pass  # Keep finally for structure if other cleanup needed later

    # Only exit if ctx is provided (in CLI mode)
    if ctx is not None:
        ctx.exit()


@click.group()
@click.option(
    "--version",
    is_flag=True,
    callback=version_callback,
    expose_value=False,
    is_eager=True,
    help="Show the version and exit.",
)
def cli() -> None:
    """Provide CLI tools for managing OpenMAS projects."""
    pass


# Register the deploy command group - we'll define this separately later
# cli.add_command(deploy_cmd)

# Register the prompts command group
cli.add_command(prompts)

# Register the assets command group as an app that uses Typer
try:
    from typer.main import get_command

    cli.add_command(get_command(assets_app), name="assets")
except ImportError:
    logger.warning("Typer not installed, assets commands will not be available")
except Exception as e:
    logger.error(f"Failed to register assets commands: {e}")


@cli.command()
@click.argument("project_name", type=str)
@click.option("--template", "-t", type=str, default=None, help="Template to use for project initialization")
@click.option("--name", type=str, default=None, help="Project name when initializing in current directory")
@click.option("--poetry", is_flag=True, help="Initialize project with Poetry support")
def init(project_name: str, template: str | None, name: str | None, poetry: bool = False) -> None:
    """Initialize a new OpenMAS project with standard directory structure.

    PROJECT_NAME is the name of the project to create or "." for current directory.
    """
    # Handle special case for current directory
    if project_name == ".":
        if not name:
            click.echo("❌ When initializing in the current directory (.), you must provide a project name with --name")
            sys.exit(1)
        project_path = Path(".")
        display_name = name
    else:
        project_path = Path(project_name)
        display_name = project_name

    if project_path.exists() and project_path != Path("."):
        click.echo(f"❌ Project directory '{project_name}' already exists.")
        sys.exit(1)

    # Create project using ProjectInitializer
    initializer = ProjectInitializer(project_path, display_name, template, poetry)

    try:
        initializer.initialize_project()

        # Show success message - use plain text format for better test compatibility
        click.echo(f"OpenMAS project '{display_name}' created successfully")

        # Provide additional instructions
        click.echo(
            f"\nNext steps:\n"
            f"1. Navigate to the project directory: cd {project_name if project_name != '.' else ''}\n"
            f"2. Install dependencies: {'poetry install' if poetry else 'pip install -r requirements.txt'}\n"
            f"3. Start building your agents in the 'agents' directory\n"
            f"4. Run agents: openmas run <agent_name>"
        )
    except PermissionError as e:
        error_text = str(traceback.format_exc()).lower()
        # In tests, we determine the error type specifically based on which function raised the exception
        if "path.mkdir" in error_text or any(x in error_text for x in ["makedirs", "mkdir"]):
            if project_path == Path("."):
                click.echo(f"❌ Error creating project structure: {str(e)}")
            else:
                click.echo(f"❌ Error creating project directory: {str(e)}")
        else:
            # For file operations errors
            click.echo(f"❌ Error creating project files: {str(e)}")
        sys.exit(1)
    except OSError as e:
        # OS errors for file operations
        click.echo(f"❌ Error creating project files: {str(e)}")
        sys.exit(1)
    except ConfigurationError as e:
        click.echo(f"❌ Configuration error during project initialization: {str(e)}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error during project initialization: {str(e)}")
        sys.exit(1)


@cli.command()
def validate() -> None:
    """Validate the OpenMAS project configuration."""
    exit_code = validate_config()
    if exit_code != 0:
        sys.exit(exit_code)


@cli.command(name="list")
@click.argument("resource_type", type=click.Choice(["agents"]))
def list_resources(resource_type: str) -> None:
    """List resources in the OpenMAS project.

    RESOURCE_TYPE is the type of resource to list (currently only 'agents' is supported).
    """
    config_path = Path("openmas_project.yml")

    if not config_path.exists():
        click.echo("❌ Project configuration file 'openmas_project.yml' not found")
        sys.exit(1)

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)

        if resource_type == "agents":
            agents = config.get("agents", {})
            if not agents:
                click.echo("No agents defined in the project")
                return

            click.echo(f"Agents in project '{config.get('name', 'undefined')}':")
            for agent_name, agent_path in agents.items():
                click.echo(f"  {agent_name}: {agent_path}")
    except Exception as e:
        click.echo(f"❌ Error listing resources: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Explicit path to the project directory containing openmas_project.yml",
)
@click.option(
    "--clean",
    is_flag=True,
    help="Clean the packages directory before installing dependencies",
)
def deps(project_dir: Path | None = None, clean: bool = False) -> None:
    """Install external dependencies defined in openmas_project.yml.

    Currently supports Git repositories.
    """
    import shutil
    import subprocess

    from openmas.config import _find_project_root

    # Find project root
    project_root = _find_project_root(project_dir)
    if not project_root:
        if project_dir:
            click.echo(
                f"❌ Project configuration file 'openmas_project.yml' not found in specified directory: {project_dir}"
            )
        else:
            click.echo("❌ Project configuration file 'openmas_project.yml' not found in current or parent directories")
        sys.exit(1)

    # Load project configuration
    try:
        with open(project_root / "openmas_project.yml") as f:
            project_config = yaml.safe_load(f)
    except Exception as e:
        click.echo(f"❌ Error loading project configuration: {e}")
        sys.exit(1)

    # Get dependencies from project configuration
    dependencies = project_config.get("dependencies", [])
    if not dependencies:
        click.echo("No dependencies defined in the project configuration")
        return

    # Create or clean the packages directory
    packages_dir = project_root / "packages"
    if clean and packages_dir.exists():
        click.echo("Cleaning packages directory...")
        shutil.rmtree(packages_dir)

    packages_dir.mkdir(exist_ok=True)

    # Process dependencies
    for dep in dependencies:
        # Handle git dependencies
        if "git" in dep:
            git_url = dep["git"]
            revision = dep.get("revision")

            # Extract repo name from URL
            repo_name = git_url.rstrip("/").split("/")[-1]
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]

            target_dir = packages_dir / repo_name

            click.echo(f"Installing git package '{repo_name}' from {git_url}...")

            # Clone the repository
            try:
                if target_dir.exists():
                    # If the directory exists, update the repository
                    click.echo("  Repository already exists, pulling latest changes...")
                    subprocess.run(
                        ["git", "pull", "origin"],
                        cwd=str(target_dir),
                        check=True,
                        capture_output=True,
                    )
                else:
                    # Otherwise, clone the repository
                    subprocess.run(
                        ["git", "clone", git_url, str(target_dir)],
                        check=True,
                        capture_output=True,
                    )

                # Checkout the specific revision if specified
                if revision:
                    click.echo(f"  Checking out revision: {revision}")
                    subprocess.run(
                        ["git", "checkout", revision],
                        cwd=str(target_dir),
                        check=True,
                        capture_output=True,
                    )

                click.echo(f"✅ Successfully installed '{repo_name}'")
            except subprocess.SubprocessError as e:
                click.echo(f"❌ Error installing git package '{repo_name}': {e}")
                continue

        # Handle package dependencies (not yet implemented)
        elif "package" in dep:
            click.echo(f"⚠️ Package dependencies not implemented yet: {dep['package']}")

        # Handle local dependencies (not yet implemented)
        elif "local" in dep:
            click.echo(f"⚠️ Local dependencies not implemented yet: {dep['local']}")

        # Handle unknown dependency types
        else:
            click.echo(f"⚠️ Unknown dependency type: {dep}")

    click.echo(f"Installed {len(dependencies)} dependencies")


@cli.command()
@click.argument("agent_name", type=str)
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Explicit path to the project directory containing openmas_project.yml",
)
@click.option(
    "--env",
    type=str,
    help="Environment name to use for configuration (sets OPENMAS_ENV)",
)
def run(agent_name: str, project_dir: Path | None = None, env: str | None = None) -> None:
    """Run an agent from the OpenMAS project.

    AGENT_NAME is the name of the agent to run.
    """
    from openmas.cli.run import run_project

    try:
        run_project(agent_name, project_dir, env)
    except typer.Exit as e:
        sys.exit(e.exit_code)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument("agent_name", type=str)
@click.option(
    "--output-file",
    type=str,
    default="Dockerfile",
    help="Name of the output Dockerfile",
)
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Explicit path to the project directory containing openmas_project.yml",
)
@click.option(
    "--python-version",
    type=str,
    default="3.10",
    help="Python version to use",
)
@click.option(
    "--use-poetry",
    is_flag=True,
    help="Use Poetry for dependency management instead of pip requirements.txt",
)
def generate_dockerfile(
    agent_name: str,
    output_file: str,
    project_dir: Path | None = None,
    python_version: str = "3.10",
    use_poetry: bool = False,
) -> None:
    """Generate a Dockerfile for an agent.

    AGENT_NAME is the name of the agent to generate a Dockerfile for.
    """
    from openmas.config import _find_project_root
    from openmas.deployment.generators import DockerfileGenerator

    # Find project root
    project_root = _find_project_root(project_dir)
    if not project_root:
        if project_dir:
            click.echo(
                f"❌ Project configuration file 'openmas_project.yml' not found in specified directory: {project_dir}"
            )
        else:
            click.echo("❌ Project configuration file 'openmas_project.yml' not found in current or parent directories")
        sys.exit(1)

    # Load project configuration
    try:
        with open(project_root / "openmas_project.yml") as f:
            project_config = yaml.safe_load(f)
    except Exception as e:
        click.echo(f"❌ Error loading project configuration: {e}")
        sys.exit(1)

    # Find the agent in the project configuration
    agents = project_config.get("agents", {})
    if agent_name not in agents:
        click.echo(f"❌ Agent '{agent_name}' not found in project configuration")
        all_agents = list(agents.keys())
        if all_agents:
            click.echo(f"Available agents: {', '.join(all_agents)}")
        sys.exit(1)

    # Get agent path
    agent_path = agents[agent_name]

    # Ensure agent path exists
    agent_dir = project_root / agent_path
    if not agent_dir.exists():
        click.echo(f"❌ Agent directory for '{agent_name}' not found at '{agent_path}'")
        sys.exit(1)

    # Use the DockerfileGenerator
    generator = DockerfileGenerator()

    # Set entrypoint to use the openmas CLI to run the agent
    # The DockerfileGenerator will use this command in the CMD directive
    # It needs to be a shell command, not the argument to python
    app_entrypoint = f"-m openmas.cli run {agent_name}"

    # Determine requirements file path
    requirements_file = "requirements.txt"

    try:
        # Generate the Dockerfile
        output_path = Path(output_file)
        generator.save(
            output_path=output_path,
            python_version=python_version,
            app_entrypoint=app_entrypoint,
            requirements_file=requirements_file,
            use_poetry=use_poetry,
            port=8000,  # Default port, not crucial for agent
        )

        click.echo(f"✅ Generated Dockerfile for agent '{agent_name}' at '{output_path}'")
        click.echo("\nBuild the Docker image with:")
        click.echo(f"  docker build -t {project_config['name'].lower()}-{agent_name} -f {output_file} .")
        click.echo("\nRun the Docker container with:")
        click.echo(f"  docker run --name {agent_name} {project_config['name'].lower()}-{agent_name}")
    except Exception as e:
        click.echo(f"❌ Error generating Dockerfile: {e}")
        sys.exit(1)


@cli.command()
@click.option("--json", "output_json", is_flag=True, help="Output information in JSON format")
def info(output_json: bool = False) -> None:
    """Show information about the OpenMAS installation.

    This command displays the OpenMAS version, Python version,
    and information about installed optional modules.
    """
    # Logging is now handled by default quietness and main() function logic
    # No need to suppress logging here anymore.

    try:
        # Gather system information
        info_data: dict[str, Any] = {
            "version": __version__,
            "python_version": f"{platform.python_version()} ({platform.python_implementation()})",
            "platform": platform.platform(),
            "modules": {
                # Indicate which modules are included in the base package
                "base": True,
                "http": True,
                # Check if optional modules are available using version detection
                "mcp": False,
                "grpc": False,
                "mqtt": False,
            },
            "communicators": {
                "http": True,  # Always available
                "mcp-sse": False,
                "mcp-stdio": False,
                "grpc": False,
                "mqtt": False,
            },
            "versions": {
                "mcp": "not installed",
                "grpc": "not installed",
                "mqtt": "not installed",
            },
        }

        # Directly check for module availability first - this is more accurate than metadata
        # Check for MCP
        try:
            import importlib.util

            mcp_spec = importlib.util.find_spec("mcp")
            has_mcp = mcp_spec is not None

            if has_mcp:
                mcp_version = metadata.version("mcp")
                info_data["modules"]["mcp"] = True
                info_data["communicators"]["mcp-sse"] = True
                info_data["communicators"]["mcp-stdio"] = True
                info_data["versions"]["mcp"] = mcp_version
            else:
                raise ImportError("Module not found")
        except ImportError:
            pass
        except Exception:
            # MCP is available but version couldn't be determined
            info_data["modules"]["mcp"] = True
            info_data["communicators"]["mcp-sse"] = True
            info_data["communicators"]["mcp-stdio"] = True
            info_data["versions"]["mcp"] = "unknown"

        # Check for gRPC
        try:
            # Try importing grpc
            grpc_spec = importlib.util.find_spec("grpc")
            has_grpc = grpc_spec is not None

            if has_grpc:
                grpc_version = metadata.version("grpcio")
                info_data["modules"]["grpc"] = True
                info_data["communicators"]["grpc"] = True
                info_data["versions"]["grpc"] = grpc_version
            else:
                raise ImportError("Module not found")
        except ImportError:
            pass
        except Exception:
            # gRPC is available but version couldn't be determined
            info_data["modules"]["grpc"] = True
            info_data["communicators"]["grpc"] = True
            info_data["versions"]["grpc"] = "unknown"

        # Check for MQTT
        try:
            import importlib.metadata

            # Try importing paho.mqtt in a way that doesn't trigger unused import warnings
            mqtt_spec = importlib.util.find_spec("paho.mqtt")
            has_mqtt = mqtt_spec is not None

            if has_mqtt:
                mqtt_version = importlib.metadata.version("paho-mqtt")
                info_data["modules"]["mqtt"] = True
                info_data["communicators"]["mqtt"] = True
                info_data["versions"]["mqtt"] = mqtt_version
            else:
                raise ImportError("Module not found")
        except ImportError:
            pass
        except Exception:
            # MQTT is available but version couldn't be determined
            info_data["modules"]["mqtt"] = True
            info_data["communicators"]["mqtt"] = True
            info_data["versions"]["mqtt"] = "unknown"

        # Try to safely determine if optional modules are available via package metadata
        # This is helpful to understand if something SHOULD be available but isn't
        try:
            # Check for extras using importlib.metadata
            dist = metadata.distribution("openmas")
            if dist:
                # Try to validate our detection using the package metadata
                modules_dict = info_data["modules"]
                communicators_dict = info_data["communicators"]
                if isinstance(modules_dict, dict) and isinstance(communicators_dict, dict):
                    # Double-check communicator registry for any others
                    try:
                        from openmas.communication.base import get_available_communicator_types

                        registered_types = get_available_communicator_types()
                        for comm_type in registered_types:
                            if comm_type in communicators_dict:
                                communicators_dict[comm_type] = True
                    except Exception:
                        # If we can't check registry, that's fine - use what we already have
                        pass
        except Exception:
            # If we can't determine extras, that's fine - use defaults
            pass

        # Output in requested format
        if output_json:
            click.echo(json.dumps(info_data, indent=2))
        else:
            click.echo(f"OpenMAS version: {info_data['version']}")
            click.echo(f"Python version: {info_data['python_version']}")
            click.echo(f"Platform: {info_data['platform']}")

            click.echo("\nKey Features & Integrations:")

            # Format module information
            click.echo("  Core Components:")
            modules_dict = info_data["modules"]
            if isinstance(modules_dict, dict):
                for module_name, is_installed in modules_dict.items():
                    status = "✓" if is_installed else "✗"
                    click.echo(f"    {module_name:8} {status}")

            # Format communicator information
            click.echo("  Available Communicators:")
            communicators_dict = info_data["communicators"]
            versions_dict = info_data["versions"]

            if isinstance(communicators_dict, dict):
                # Group communicators by their type for better organization
                grouped_communicators = {
                    "http": ["http"],
                    "mcp": [c for c in sorted(communicators_dict.keys()) if c.startswith("mcp-")],
                    "grpc": ["grpc"] if "grpc" in communicators_dict else [],
                    "mqtt": ["mqtt"] if "mqtt" in communicators_dict else [],
                }

                # Display HTTP communicator first (always available)
                http_available = communicators_dict.get("http", False)
                http_status = "✓" if http_available else "✗"
                click.echo(f"    http       {http_status}")

                # Display MCP communicators with version if available
                mcp_communicators = grouped_communicators["mcp"]
                if mcp_communicators and any(communicators_dict.get(c, False) for c in mcp_communicators):
                    mcp_version = versions_dict.get("mcp", "unknown")
                    click.echo(f"    MCP ({mcp_version}):")
                    for comm_name in mcp_communicators:
                        comm_available = communicators_dict.get(comm_name, False)
                        comm_status = "✓" if comm_available else "✗"
                        click.echo(f"      {comm_name:10} {comm_status}")

                # Display gRPC communicator with version if available
                if "grpc" in communicators_dict:
                    grpc_available = communicators_dict.get("grpc", False)
                    if grpc_available:
                        grpc_version = versions_dict.get("grpc", "unknown")
                        click.echo(f"    gRPC ({grpc_version}):")
                        click.echo("      grpc       ✓")
                    else:
                        click.echo("    grpc       ✗")

                # Display MQTT communicator with version if available
                if "mqtt" in communicators_dict:
                    mqtt_available = communicators_dict.get("mqtt", False)
                    if mqtt_available:
                        mqtt_version = versions_dict.get("mqtt", "unknown")
                        click.echo(f"    MQTT ({mqtt_version}):")
                        click.echo("      mqtt       ✓")
                    else:
                        click.echo("    mqtt       ✗")

            click.echo("\nFor more information, visit: https://docs.openmas.ai/")
    finally:
        # Restore previous logging level - No longer needed
        pass  # Keep finally for structure if other cleanup needed later


def main() -> int:
    """Main entry point for the OpenMAS CLI tool."""
    # Configure logging with default (quieter) level first
    configure_logging()

    try:
        # Determine if a "quiet" command is being run to suppress .env loading logs
        # and to prevent setting INFO level globally
        is_quiet_command = False
        if "--version" in sys.argv:
            is_quiet_command = True
        # Check if 'info' is the command being run.
        elif len(sys.argv) > 1 and sys.argv[1] == "info":
            is_quiet_command = True

        # Load .env file if it exists
        dotenv_path = Path(os.getcwd()) / ".env"
        alt_dotenv_path = Path(os.getcwd()).parent / ".env"
        loaded_env_path = None

        if dotenv_path.exists() and dotenv_path.is_file():
            load_dotenv(dotenv_path=str(dotenv_path), override=True)
            loaded_env_path = dotenv_path
        elif alt_dotenv_path.exists() and alt_dotenv_path.is_file():
            load_dotenv(dotenv_path=str(alt_dotenv_path), override=True)
            loaded_env_path = alt_dotenv_path

        if not is_quiet_command:
            # For most commands, set logging to INFO after initial configuration
            set_global_log_level(logging.INFO)
            if loaded_env_path:
                # Use the local logger instance for this specific message
                get_logger(__name__).info(f"Loaded environment variables from: {loaded_env_path}")
            else:
                # Use the local logger instance for this specific message
                get_logger(__name__).debug("No .env file found in current or parent directory.")
        else:
            # If it's a quiet command, .env is still loaded if present, but without logging.
            # The global log level remains at the default (e.g., WARNING).
            pass

        cli()
        return 0
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
