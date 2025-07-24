"""Agent class loading and discovery for OpenMAS CLI."""

import importlib.util
import inspect
import os
import sys
import types
from pathlib import Path

from openmas.agent.base import BaseAgent
from openmas.exceptions import ConfigurationError


class AgentLoader:
    """Handles agent module loading and agent class discovery."""

    def __init__(self) -> None:
        """Initialize a new AgentLoader.

        This loader assumes that sys.path has already been set up correctly by ProjectEnvironment.
        """
        pass

    def load_agent_class(self, agent_module_path: str, expected_class_name: str | None = None) -> type[BaseAgent]:
        """Load and return the agent class from the specified module.

        Args:
            agent_module_path: The module path string (e.g., "agents.my_agent")
            expected_class_name: Optional name of the class to look for

        Returns:
            The found BaseAgent subclass

        Raises:
            ConfigurationError: If no suitable class is found
            ImportError: If the module cannot be imported
        """
        # Convert path-based format to module format if needed
        if "/" in agent_module_path or "\\" in agent_module_path:
            # This is a path-based module path
            # Normalize to use forward slashes
            agent_module_path = agent_module_path.replace("\\", "/")

            # Convert path to dot notation for module imports
            agent_module_path = agent_module_path.replace("/", ".")

            # Strip .py if present
            if agent_module_path.endswith(".py"):
                agent_module_path = agent_module_path[:-3]

        # Try to locate the agent module
        agent_module_name = f"{agent_module_path}.agent"

        try:
            # Import the agent module
            agent_module = importlib.import_module(agent_module_name)
        except ModuleNotFoundError as e:
            # If it's the agent module that can't be found, try direct file-based import
            if agent_module_name in str(e):
                # Construct possible file path for direct import
                if "/" in agent_module_path or "\\" in agent_module_path:
                    agent_path = agent_module_path.replace("\\", "/")
                    agent_file = Path(agent_path) / "agent.py"
                else:
                    agent_path = agent_module_path.replace(".", "/")
                    agent_file = Path(f"{agent_path}/agent.py")

                if not os.path.exists(agent_file):
                    raise ConfigurationError(f"Agent file not found: {agent_file}")

                try:
                    # Create a unique module name to avoid conflicts
                    unique_module_name = f"{agent_module_path.replace('.', '_')}_agent_module"

                    spec = importlib.util.spec_from_file_location(unique_module_name, agent_file)
                    if spec is None or spec.loader is None:
                        raise ConfigurationError(f"Error loading agent file: Invalid spec from {agent_file}")

                    module = importlib.util.module_from_spec(spec)
                    sys.modules[unique_module_name] = module
                    spec.loader.exec_module(module)
                    agent_module = module
                except Exception as e2:
                    # Propagate the original error along with the new one
                    raise ImportError(
                        f"Error importing agent from file {agent_file}: {e2}. Original error: {str(e)}"
                    ) from e2
            else:
                # It's some other dependency that can't be found
                raise ImportError(f"Missing dependency when importing '{agent_module_name}': {e}") from e

        # Find the appropriate agent class in the module
        agent_class = self._find_agent_class(agent_module, expected_class_name)
        return agent_class

    def _find_agent_class(
        self, agent_module: types.ModuleType, expected_class_name: str | None = None
    ) -> type[BaseAgent]:
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
            for name, obj in inspect.getmembers(agent_module):
                if inspect.isclass(obj):
                    found_classes.append(name)
                    if name == expected_class_name:
                        if issubclass(obj, BaseAgent) and obj is not BaseAgent:
                            agent_class = obj
                            break
                        else:
                            # Found the name, but it's not a valid BaseAgent subclass
                            raise ConfigurationError(
                                f"Specified class '{expected_class_name}' is not a valid BaseAgent subclass."
                            )
            if agent_class is None:
                raise ConfigurationError(
                    f"Specified agent class '{expected_class_name}' not found in module {agent_module.__name__}. "
                    f"Found classes: {found_classes}"
                )
        else:
            # First look specifically for a class named "Agent" (common case in our examples)
            for name, obj in inspect.getmembers(agent_module):
                if inspect.isclass(obj):
                    found_classes.append(name)
                    if name == "Agent" and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                        agent_class = obj
                        break

            # If we didn't find a class explicitly named "Agent", find the first BaseAgent subclass
            if agent_class is None:
                for name, obj in inspect.getmembers(agent_module):
                    if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                        agent_class = obj
                        break  # Use the first one found

            if agent_class is None:
                raise ConfigurationError(f"No BaseAgent subclass found in agent module. Found classes: {found_classes}")

        return agent_class
