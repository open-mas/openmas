"""CLI run module for OpenMAS."""

import asyncio
import functools
import importlib.util
import inspect
import os
import signal
import sys
import traceback
import types
from pathlib import Path
from typing import Optional, Type

import click
import typer
import yaml

from openmas.agent.base import BaseAgent
from openmas.config import AgentConfigEntry, ConfigLoader, ProjectConfig, _find_project_root, logger
from openmas.exceptions import ConfigurationError, LifecycleError


def add_package_paths_to_sys_path(packages_dir: str | Path) -> None:
    """Add package paths to sys.path for dependency resolution.

    Scans the packages directory and adds appropriate paths to sys.path so
    that packages can be imported. For packages with a src directory, it adds
    the src directory. For packages without a src directory, it adds the
    package root directory.

    Args:
        packages_dir: Path to the packages directory
    """
    packages_dir = Path(packages_dir)
    if not os.path.isdir(packages_dir):
        return

    # Skip special directories like .git, __pycache__, etc.
    skip_dirs = {".git", "__pycache__", "__pypackages__", ".tox", ".pytest_cache"}

    # Get all directories in the packages directory
    for package_name in os.listdir(packages_dir):
        package_path = packages_dir / package_name

        # Skip non-directories and special directories
        if not os.path.isdir(package_path) or package_name in skip_dirs or package_name.startswith("."):
            continue

        # Check if this package has a src directory
        src_path = package_path / "src"
        if os.path.isdir(src_path):
            # Add the src directory if it exists
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
        else:
            # Otherwise add the package root
            if str(package_path) not in sys.path:
                sys.path.insert(0, str(package_path))

    logger.debug(f"Updated sys.path with package paths from {packages_dir}")


def _find_agent_class(agent_module: types.ModuleType, expected_class_name: Optional[str] = None) -> Type[BaseAgent]:
    """Find the appropriate BaseAgent subclass within the agent module.

    Args:
        agent_module: The loaded agent module.
        expected_class_name: Optional specific class name from config.

    Returns:
        The found BaseAgent subclass.

    Raises:
        ConfigurationError: If no suitable class is found or the expected class is invalid.
    """
    agent_class = None
    found_classes = []

    # Treat expected_class_name="Agent" the same as None (find first subclass)
    if expected_class_name and expected_class_name != "Agent":
        # If class name is specified in config (and not just "Agent"), look for that specific class
        logger.info(f"Looking for specified agent class: {expected_class_name}")
        for name, obj in inspect.getmembers(agent_module):
            if inspect.isclass(obj):
                found_classes.append(name)
                if name == expected_class_name:
                    if issubclass(obj, BaseAgent) and obj is not BaseAgent:
                        agent_class = obj
                        logger.info(f"Found specified agent class: {name}")
                        break
                    else:
                        # Found the name, but it's not a valid BaseAgent subclass
                        logger.error(
                            f"❌ Specified class '{expected_class_name}' found, "
                            f"but it does not inherit from BaseAgent or is BaseAgent itself."
                        )
                        raise ConfigurationError(
                            f"Specified class '{expected_class_name}' is not a valid BaseAgent subclass."
                        )
        if agent_class is None:
            logger.error(
                f"❌ Specified agent class '{expected_class_name}' not found in module {agent_module.__name__}."
            )
            logger.error(f"Found classes: {found_classes}")
            raise ConfigurationError(f"Specified agent class '{expected_class_name}' not found.")
    else:
        # First look specifically for a class named "Agent" (common case in our examples)
        logger.info("Looking for class named 'Agent' or first BaseAgent subclass in module...")
        for name, obj in inspect.getmembers(agent_module):
            if inspect.isclass(obj):
                found_classes.append(name)
                if name == "Agent" and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                    agent_class = obj
                    logger.info("Found agent class named 'Agent'")
                    break

        # If we didn't find a class explicitly named "Agent", find the first BaseAgent subclass
        if agent_class is None:
            for name, obj in inspect.getmembers(agent_module):
                if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                    agent_class = obj
                    logger.info(f"Found agent class: {name}")
                    break  # Use the first one found

        if agent_class is None:
            logger.error("❌ No BaseAgent subclass found in agent module")
            logger.error(
                "Make sure the agent file contains exactly one class that inherits from openmas.agent.BaseAgent"
            )
            logger.error(f"Found classes: {found_classes}")
            raise ConfigurationError("No BaseAgent subclass found in module.")

    return agent_class


def run_project(agent_name: str, project_dir: Optional[Path] = None, env: Optional[str] = None) -> None:
    """Run an agent from the OpenMAS project using the hardened config loader.

    Args:
        agent_name: Name of the agent to run
        project_dir: Optional explicit path to the project directory
        env: Optional environment name to use for configuration

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
    project_root = _find_project_root(project_dir)
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

    # Load and validate project configuration using ConfigLoader
    try:
        config_loader = ConfigLoader()
        config = config_loader.load_yaml_file(project_root / "openmas_project.yml")
        project_config = ProjectConfig(**config)
    except (ConfigurationError, FileNotFoundError, yaml.YAMLError) as e:
        click.echo(f"❌ Error loading project configuration: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        click.echo(f"❌ Unexpected error loading project configuration: {e}")
        raise typer.Exit(code=1)

    # Find the agent in the project configuration
    if agent_name not in project_config.agents:
        click.echo(f"❌ Agent '{agent_name}' not found in project configuration")
        all_agents = list(project_config.agents.keys())
        if all_agents:
            click.echo(f"Available agents: {', '.join(all_agents)}")
        raise typer.Exit(code=1)

    # Get agent config entry
    agent_config_entry = project_config.agents.get(agent_name)
    if not isinstance(agent_config_entry, AgentConfigEntry):
        click.echo(f"❌ Invalid agent configuration for '{agent_name}'")
        raise typer.Exit(code=1)

    # Load agent configuration
    try:
        # Load agent-specific configuration using the agent name as the prefix
        config_loader = ConfigLoader()

        # Load environment configuration
        env_config = {}
        if env:
            env_config_path = project_root / "config" / f"{env}.yml"
            if env_config_path.exists():
                logger.debug(f"Loading environment configuration from {env_config_path}")
                env_config = config_loader.load_yaml_file(env_config_path)
            else:
                logger.debug(f"Environment config file not found: {env_config_path}")

        # For now, just create a basic AgentConfig
        # Keeping this variable definition commented out to avoid linting errors until we use it
        # agent_config = AgentConfig(name=agent_name)
    except ConfigurationError as e:
        click.echo(f"❌ Error loading agent configuration: {e}")
        raise typer.Exit(code=1)

    # Get agent module path
    module_path = agent_config_entry.module

    # Handle path-based module paths
    # Convert path-based format (e.g., "agents/my_agent") to module format (e.g., "agents.my_agent")
    if "/" in module_path or "\\" in module_path:
        # This is a path-based module path
        # Normalize to use forward slashes
        module_path = module_path.replace("\\", "/")

        # Convert path to dot notation for module imports
        module_path = module_path.replace("/", ".")

        # Strip .py if present
        if module_path.endswith(".py"):
            module_path = module_path[:-3]

        logger.debug(f"Converted path-based module '{agent_config_entry.module}' to '{module_path}'")

    # Get shared and extension paths
    shared_paths = [project_root / path for path in project_config.shared_paths]
    extension_paths = [project_root / path for path in project_config.extension_paths]

    # Store original sys.path to restore later
    original_sys_path = sys.path.copy()

    # Set up PYTHONPATH for imports
    sys_path_additions = []

    # Add project root first to ensure absolute imports work
    sys_path_additions.append(str(project_root))

    # Determine agent directory from module path
    if "/" in agent_config_entry.module or "\\" in agent_config_entry.module:
        # For path-based entries, use the path directly
        agent_path = agent_config_entry.module.replace("\\", "/")
        agent_dir_path = project_root / agent_path
    else:
        # For module-based entries, convert dots to path separators
        module_parts = module_path.split(".")
        agent_dir_path = project_root
        for part in module_parts:
            agent_dir_path = agent_dir_path / part

    # Add the agent's parent directory
    sys_path_additions.append(str(agent_dir_path.parent))

    # Add the agent directory itself
    sys_path_additions.append(str(agent_dir_path))

    # Add shared and extension paths
    for path in shared_paths + extension_paths:
        if path.exists() and str(path) not in sys_path_additions:
            sys_path_additions.append(str(path))

    # Add packages to sys.path
    packages_dir = project_root / "packages"
    if packages_dir.exists():
        # Use our utility function to add packages
        add_package_paths_to_sys_path(packages_dir)

    # Update sys.path - add in reverse order so that higher priority paths appear first
    for path_str in reversed(sys_path_additions):
        if path_str not in sys.path:
            sys.path.insert(0, path_str)

    click.echo("Python import paths:")  # noqa: F541
    for i, path_str in enumerate(sys.path[:5]):
        click.echo(f"  {i + 1}. {path_str}")
    if len(sys.path) > 5:
        click.echo(f"  ... and {len(sys.path) - 5} more paths")

    # Try to locate the agent module
    agent_module_name = f"{module_path}.agent"

    try:
        # Import the agent module
        agent_module = importlib.import_module(agent_module_name)
    except ModuleNotFoundError as e:
        # Check if it's openmas itself that can't be found
        if "openmas" in str(e):
            click.echo(f"❌ Critical error: Could not import OpenMAS modules: {e}")
            click.echo("Make sure you have OpenMAS installed in your current Python environment:")
            click.echo("  pip install openmas")
            click.echo("  # or with your preferred package manager:")
            click.echo("  poetry add openmas")
            click.echo("  conda install openmas")
            sys.path = original_sys_path
            raise typer.Exit(code=1)
        elif agent_module_name in str(e):
            # Agent module not found - try alternative approach using file-based import
            logger.debug(f"Could not import {agent_module_name} as a module, trying direct file import")

            # If importing the module failed, try next approach
            # Try to load by path directly
            if "/" in agent_config_entry.module or "\\" in agent_config_entry.module:
                # This is a path-based format, so we need to construct the file path
                agent_path = agent_config_entry.module.replace("\\", "/")
                agent_file = project_root / agent_path / "agent.py"
                logger.debug(f"Attempting to load module directly from path: {agent_file}")
            else:
                # For module-based format
                agent_path = module_path.replace(".", "/")
                agent_file = project_root / f"{agent_path}/agent.py"
                logger.debug(f"Attempting to load module directly from path: {agent_file}")

            if not os.path.exists(agent_file):
                click.echo(f"❌ Agent file not found: {agent_file}")
                click.echo(f"Make sure your agent directory '{agent_path}' contains an agent.py file")
                sys.path = original_sys_path
                raise typer.Exit(code=1)

            try:
                # Create a unique module name to avoid conflicts
                agent_module_name = f"{agent_name}_agent_module"

                spec = importlib.util.spec_from_file_location(agent_module_name, agent_file)
                if spec is None or spec.loader is None:
                    click.echo(f"❌ Error loading agent file: Invalid spec from {agent_file}")
                    sys.path = original_sys_path
                    raise typer.Exit(code=1)

                module = importlib.util.module_from_spec(spec)
                sys.modules[agent_module_name] = module
                spec.loader.exec_module(module)
                logger.info(f"Successfully loaded agent module from {agent_file}")
                agent_module = module
            except Exception as e2:
                click.echo(f"❌ Error importing agent from file {agent_file}: {e2}")
                click.echo(f"Original import error: {str(e)}")
                traceback.print_exc()
                sys.path = original_sys_path
                raise typer.Exit(code=1)
        else:
            # Some other dependency
            click.echo(f"❌ Missing dependency when importing '{agent_module_name}': {e}")
            missing_module = str(e).split("'")[1] if "'" in str(e) else str(e)
            click.echo("Please install the required dependency:")
            click.echo(f"  pip install {missing_module}")
            click.echo("  # or with your preferred package manager:")
            click.echo(f"  poetry add {missing_module}")
            click.echo(f"  conda install {missing_module}")
            sys.path = original_sys_path
            raise typer.Exit(code=1)
    except ImportError as e:
        click.echo(f"❌ Error importing agent module '{agent_module_name}': {e}")
        click.echo("Check your agent implementation for errors.")
        traceback.print_exc()
        sys.path = original_sys_path
        raise typer.Exit(code=1)

    # Find the appropriate agent class in the module
    class_name = None
    if hasattr(agent_config_entry, "class_"):
        class_name = agent_config_entry.class_
    elif hasattr(agent_config_entry, "class_name"):
        class_name = agent_config_entry.class_name

    try:
        agent_class = _find_agent_class(agent_module, class_name)
    except ConfigurationError as e:
        click.echo(f"Error finding agent class: {e}")
        raise typer.Exit(code=1)

    # Set up asset manager
    asset_manager = None
    if hasattr(project_config, "assets") and project_config.assets:
        try:
            from openmas.assets.manager import AssetManager

            asset_manager = AssetManager(project_config)
        except ImportError as e:
            click.echo(f"⚠️ Warning: Could not initialize asset manager: {e}")
            click.echo("Asset functionality will not be available.")

    # Initialize the agent with error handling
    try:
        # Create agent config with the required name field
        agent_config = {
            "name": agent_name,
            **project_config.default_config,  # Include default config from project
            **env_config,  # Override with environment-specific config
        }

        # Initialize agent with configuration and asset manager
        click.echo(f"Starting agent '{agent_name}' ({agent_class.__name__})")
        agent = agent_class(name=agent_name, config=agent_config, asset_manager=asset_manager)
    except (ImportError, AttributeError, TypeError, ConfigurationError) as e:
        click.echo(f"❌ Error initializing agent '{agent_name}': {e}")
        click.echo("This may be due to configuration issues or missing dependencies.")
        raise typer.Exit(code=1)
    except Exception as e:
        click.echo(f"❌ Unexpected error initializing agent: {e}")
        traceback.print_exc()
        raise typer.Exit(code=1)

    # Set up signal handlers for graceful shutdown
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    shutdown_event = asyncio.Event()
    stop_in_progress = False

    def signal_handler(signame: Optional[str] = None) -> None:
        nonlocal stop_in_progress
        if stop_in_progress:
            # If we get a second signal during shutdown, exit immediately
            click.echo("\nForced exit. Shutdown already in progress.")
            sys.exit(1)

        if signame:
            click.echo(f"\nReceived signal {signame}, initiating graceful shutdown...")
        else:
            click.echo("\nReceived signal, initiating graceful shutdown...")
        stop_in_progress = True
        shutdown_event.set()

    # Register signal handlers
    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(sig, functools.partial(signal_handler, sig.name))

    # Run the agent lifecycle with enhanced error handling
    async def run_agent() -> None:
        try:
            # Start the agent - this will call setup() and start the communicator
            try:
                await agent.start()
            except LifecycleError as e:
                click.echo(f"❌ Error starting agent: {e}")
                return
            except Exception as e:
                click.echo(f"❌ Unexpected error starting agent: {e}")
                traceback.print_exc()
                return

            # Display guidance message for multiple agents
            all_agent_names = list(project_config.agents.keys())
            if len(all_agent_names) > 1:
                other_agents = [a for a in all_agent_names if a != agent_name]
                click.echo("\n[OpenMAS CLI] Agent start success.")
                click.echo("[OpenMAS CLI] To run other agents in this project, open new terminal windows and use:")
                for other_agent in other_agents:
                    click.echo(f"[OpenMAS CLI]     openmas run {other_agent}")
                click.echo(f"[OpenMAS CLI] Project agents: {', '.join(all_agent_names)}")
                click.echo("")

            # Create tasks for the agent's run method and the shutdown signal wait
            agent_run_task = asyncio.create_task(agent.run(), name=f"agent_run_{agent_name}")
            shutdown_wait_task = asyncio.create_task(shutdown_event.wait(), name=f"shutdown_wait_{agent_name}")

            # Wait for either the agent to finish or a shutdown signal
            click.echo("Agent is running. Waiting for completion or Ctrl+C...")
            done, pending = await asyncio.wait(
                [agent_run_task, shutdown_wait_task], return_when=asyncio.FIRST_COMPLETED
            )

            if agent_run_task in done:
                click.echo("Agent run method completed.")
                # Check for exceptions in the agent's run task
                try:
                    agent_run_task.result()  # Raise exception if run() had one
                except asyncio.CancelledError:
                    click.echo("Agent run task was cancelled.")  # Should not happen unless stop() was called early
                except Exception as e:
                    click.echo(f"❌ Error during agent execution: {e}")
                    traceback.print_exc()
            else:
                # This means shutdown_wait_task finished (signal received)
                click.echo("Shutdown signal received.")

            # Ensure the other task is cancelled if it's still pending
            for task in pending:
                click.echo(f"Cancelling pending task: {task.get_name()}")
                task.cancel()
                try:
                    # Allow cancellation to propagate
                    await task
                except asyncio.CancelledError:
                    pass  # Expected

        except asyncio.CancelledError:
            click.echo("Agent execution cancelled")
        except Exception as e:
            click.echo(f"❌ Error in agent execution: {e}")
            traceback.print_exc()
        finally:
            # Always ensure agent is stopped cleanly, even if there was an error
            if agent._is_running:
                click.echo("Stopping agent...")
                try:
                    await agent.stop()
                    click.echo("Agent stopped successfully")
                except Exception as e:
                    click.echo(f"❌ Error stopping agent: {e}")
                    traceback.print_exc()

    # Run the agent
    try:
        # Run the coroutine directly in the loop instead of using asyncio.run
        loop.run_until_complete(run_agent())
    except KeyboardInterrupt:
        # Handle the case where the user rapidly presses Ctrl+C multiple times
        click.echo("\nForced exit.")
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        traceback.print_exc()
        raise typer.Exit(code=1)
    finally:
        # Clean up the loop properly
        try:
            # Cancel all tasks
            tasks = asyncio.all_tasks(loop)
            for task in tasks:
                task.cancel()

            # Allow tasks to terminate with CancelledError
            if tasks:
                loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

            # Shutdown asyncgens and close the loop
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        except Exception as e:
            click.echo(f"Error during loop cleanup: {e}")

        # Restore original sys.path
        sys.path = original_sys_path
