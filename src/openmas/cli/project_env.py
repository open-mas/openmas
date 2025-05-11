"""Project environment management for OpenMAS CLI."""

import os
import sys
from pathlib import Path
from typing import List

from openmas.cli.utils import add_package_paths_to_sys_path
from openmas.config import AgentConfigEntry, ProjectConfig


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
        self.original_sys_path: List[str] = []
        self.added_paths: List[str] = []

    def setup_environment(self, agent_name: str) -> None:
        """Set up the environment for running the specified agent.

        This method:
        - Adds necessary paths to sys.path for importing the agent and its dependencies
        - Sets environment variables like OPENMAS_PROJECT_ROOT and AGENT_NAME

        Args:
            agent_name: The name of the agent to run
        """
        # Store original sys.path to restore later
        self.original_sys_path = sys.path.copy()

        # Prepare additional paths for sys.path
        sys_path_additions = []

        # Add project root first to ensure absolute imports work
        sys_path_additions.append(str(self.project_root))

        # Get shared and extension paths
        shared_paths = [self.project_root / path for path in self.project_config.shared_paths]
        extension_paths = [self.project_root / path for path in self.project_config.extension_paths]

        # Get agent config entry to determine the module path
        agent_config_entry = self.project_config.agents.get(agent_name)
        if agent_config_entry:
            # Only proceed if agent_config_entry is an AgentConfigEntry with a module attribute
            if isinstance(agent_config_entry, AgentConfigEntry) and hasattr(agent_config_entry, "module"):
                module_path = agent_config_entry.module
                # Determine agent directory from module path
                if "/" in module_path or "\\" in module_path:
                    # For path-based entries, use the path directly
                    agent_path = module_path.replace("\\", "/")
                    agent_dir_path = self.project_root / agent_path
                else:
                    # For module-based entries, convert dots to path separators
                    module_parts = module_path.split(".")
                    agent_dir_path = self.project_root
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
        packages_dir = self.project_root / "packages"
        if packages_dir.exists():
            # Use the utility function to add packages
            add_package_paths_to_sys_path(packages_dir)

        # Update sys.path - add in reverse order so that higher priority paths appear first
        for path_str in reversed(sys_path_additions):
            if path_str not in sys.path:
                sys.path.insert(0, path_str)
                self.added_paths.append(path_str)

        # Set environment variables
        os.environ["OPENMAS_PROJECT_ROOT"] = str(self.project_root)
        os.environ["AGENT_NAME"] = agent_name

        # Set default OPENMAS_ENV if not already set
        if "OPENMAS_ENV" not in os.environ:
            os.environ["OPENMAS_ENV"] = "development"

    def restore_environment(self) -> None:
        """Restore the original sys.path.

        This should be called when the agent execution is complete.
        """
        # Restore original sys.path by clearing and extending
        # This is a more reliable approach than replacing the list
        sys.path.clear()
        sys.path.extend(self.original_sys_path)
