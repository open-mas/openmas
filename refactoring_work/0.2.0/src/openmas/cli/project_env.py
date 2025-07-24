"""Project environment management for OpenMAS CLI."""

import os
import sys
from pathlib import Path

from openmas.cli.utils import add_package_paths_to_sys_path
from openmas.config import AgentConfig, ProjectConfig
from openmas.logging import get_logger

logger = get_logger(__name__)


class ProjectEnvironment:
    """Manages the Python environment for an OpenMAS project.

    This class handles the setup and cleanup of environment variables and sys.path
    additions required for running an OpenMAS agent.
    """

    def __init__(self, project_root: Path, project_config: ProjectConfig):
        """Initialize a new ProjectEnvironment.

        Args:
            project_root: The root directory of the project
            project_config: The project configuration
        """
        self.project_root = project_root
        self.project_config = project_config
        self.original_python_path = sys.path.copy()
        self.original_env = os.environ.copy()

    def setup_environment(self, agent_name: str | None = None) -> None:
        """Set up the environment for running the specified agent.

        This method:
        - Adds necessary paths to sys.path for importing the agent and its dependencies
        - Sets environment variables like OPENMAS_PROJECT_ROOT and AGENT_NAME

        Args:
            agent_name: The name of the agent to run
        """
        logger.info(f"Setting up environment for project: {self.project_config.name}")

        # 1. Add the project root to sys.path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
            logger.debug(f"Added project root to sys.path: {self.project_root}")

        # 2. Add shared paths to sys.path
        for shared_path in self.project_config.shared_paths:
            path = self.project_root / shared_path
            if path.exists() and str(path) not in sys.path:
                sys.path.insert(0, str(path))
                logger.debug(f"Added shared path to sys.path: {path}")

        # 3. Add extension paths to sys.path
        for extension_path in self.project_config.extension_paths:
            path = self.project_root / extension_path
            if path.exists() and str(path) not in sys.path:
                sys.path.insert(0, str(path))
                logger.debug(f"Added extension path to sys.path: {path}")

        # 4. Process any Python packages in the packages directory
        packages_path = self.project_root / "packages"
        if packages_path.exists():
            add_package_paths_to_sys_path(packages_path)
            logger.debug(f"Added package paths from: {packages_path}")

        # 5. If an agent is specified, add its package directory to sys.path
        if agent_name and agent_name in self.project_config.agents:
            agent_config_entry = self.project_config.agents[agent_name]

            # Only proceed if agent_config_entry is an AgentConfig with a module attribute
            if isinstance(agent_config_entry, AgentConfig) and hasattr(agent_config_entry, "module"):
                module_path = agent_config_entry.module

                # Ensure module_path is a non-empty string
                if not module_path:
                    logger.warning("Agent config has no module path specified; skipping sys.path additions")
                    return

                # If module_path is in path format (with slashes), convert to directory path
                if "/" in module_path:
                    # If it ends with .py, we want the parent directory
                    if module_path.endswith(".py"):
                        module_path = str(Path(module_path).parent)

                    # Add the module path to sys.path
                    parts = module_path.split("/")
                    current_path = self.project_root

                    # Add parent paths incrementally to support nested packages
                    for i, part in enumerate(parts):
                        # Add each parent directory
                        if i > 0:  # Skip adding the project root
                            parent_path = self.project_root / "/".join(parts[:i])
                            if str(parent_path) not in sys.path:
                                sys.path.insert(0, str(parent_path))
                                logger.debug(f"Added parent path to sys.path: {parent_path}")

                        # Add the full path at the end
                        current_path = current_path / part

                    if str(current_path) not in sys.path:
                        sys.path.insert(0, str(current_path))
                        logger.debug(f"Added agent module path to sys.path: {current_path}")
                else:
                    # For dotted module paths, add each package directory to sys.path
                    parts = module_path.split(".")

                    # Add each parent directory to sys.path
                    for i in range(len(parts)):
                        parent_path = self.project_root / "/".join(parts[: i + 1])
                        parent_dir = str(self.project_root / "/".join(parts[:i]))

                        # Add parent directories like "agents" for dotted paths like "agents.test_agent"
                        if i > 0 and parent_dir not in sys.path:
                            sys.path.insert(0, parent_dir)
                            logger.debug(f"Added parent directory to sys.path: {parent_dir}")

                    # Add the full module path
                    full_path = self.project_root / "/".join(parts)
                    if str(full_path) not in sys.path:
                        sys.path.insert(0, str(full_path))
                        logger.debug(f"Added agent directory to sys.path: {full_path}")

                    # Continue with the package-based approach for dotted notation
                    current_path = self.project_root
                    for i in range(len(parts)):
                        if i == len(parts) - 1 and current_path.is_dir():
                            # Last part might be a module (.py file) not a package,
                            # so don't go into it
                            candidate_py = current_path / f"{parts[i]}.py"
                            if candidate_py.exists():
                                # Seems to be a .py file module, just ensure the parent dir is in sys.path
                                if str(current_path) not in sys.path:
                                    sys.path.insert(0, str(current_path))
                                    logger.debug(f"Added module parent to sys.path: {current_path}")
                                break

                        # Add the next part to the path
                        current_path = current_path / parts[i]
                        if current_path.is_dir():
                            if (current_path / "__init__.py").exists():
                                # It's a package, add to sys.path
                                if str(current_path.parent) not in sys.path:
                                    sys.path.insert(0, str(current_path.parent))
                                    logger.debug(f"Added package parent to sys.path: {current_path.parent}")
                            else:
                                # Not a package, but might be a directory containing modules
                                if str(current_path) not in sys.path:
                                    sys.path.insert(0, str(current_path))
                                    logger.debug(f"Added directory to sys.path: {current_path}")
                        else:
                            # Not a directory, stop here
                            break

        # Log the final sys.path state
        logger.debug("Python path after setup:")
        for i, path_str in enumerate(sys.path[:5]):
            logger.debug(f"{i + 1}: {path_str}")
        if len(sys.path) > 5:
            logger.debug(f"... and {len(sys.path) - 5} more paths")

        # Set environment variables
        os.environ["OPENMAS_PROJECT_ROOT"] = str(self.project_root)
        if agent_name:
            os.environ["AGENT_NAME"] = agent_name

        # Set default OPENMAS_ENV if not already set
        if "OPENMAS_ENV" not in os.environ:
            os.environ["OPENMAS_ENV"] = "development"

    def restore_environment(self) -> None:
        """Restore the original Python environment.

        This should be called when the project is no longer needed
        to clean up the Python environment.
        """
        logger.debug("Restoring original Python environment")
        # First clear sys.path, then restore it with exactly the original list
        sys.path.clear()
        # Make a separate copy to ensure we're not using the same object reference
        original_path_copy = self.original_python_path.copy()
        sys.path.extend(original_path_copy)

        # Only restore environment variables we might have modified
        # to avoid wiping out env vars set by other code
        for key, value in self.original_env.items():
            if key.startswith("OPENMAS_") or key.startswith("PYTHONPATH"):
                os.environ[key] = value
