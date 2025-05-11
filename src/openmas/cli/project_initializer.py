"""Project initialization utilities for OpenMAS CLI."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import yaml

from openmas.exceptions import ConfigurationError


class ProjectInitializer:
    """Handles the creation of a new OpenMAS project structure."""

    def __init__(
        self, project_path: Path, project_display_name: str, template: Optional[str] = None, poetry: bool = False
    ) -> None:
        """Initialize a new project initializer.

        Args:
            project_path: The path where the project will be created
            project_display_name: The display name for the project
            template: Optional template name to use for project initialization
            poetry: Whether to use Poetry for dependency management
        """
        self.project_path = project_path
        self.project_display_name = project_display_name
        self.template = template
        self.poetry = poetry

    def _prepare_file_actions(self) -> Dict[Path, Union[str, Callable[[], str]]]:
        """Determine all directories to be created and files to be written.

        Returns:
            A dictionary mapping file paths to their content (string or callable returning string)
        """
        actions: Dict[Path, Union[str, Callable[[], str]]] = {}

        # Define subdirectories and their init files
        subdirs = ["agents", "shared", "extensions", "config", "tests", "packages"]
        for subdir in subdirs:
            # __init__.py files in Python package directories (exclude config and packages)
            if subdir not in ["config", "packages"]:
                init_file = self.project_path / subdir / "__init__.py"
                actions[init_file] = f'"""OpenMAS {subdir} package."""\n'

        # Create README.md
        actions[self.project_path / "README.md"] = f"# {self.project_display_name}\n\nA OpenMAS project.\n"

        # Create dependency files based on the chosen option
        if self.poetry:
            # Create pyproject.toml for Poetry
            actions[
                self.project_path / "pyproject.toml"
            ] = f"""[tool.poetry]
name = "{self.project_display_name.lower().replace(' ', '-')}"
version = "0.1.0"
description = "An OpenMAS project"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
# This is an application, not a library
package-mode = false

[tool.poetry.dependencies]
python = "^3.10"
openmas = ">=0.2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^23.0.0"
mypy = "^1.0.0"
flake8 = "^6.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
        else:
            # Create requirements.txt
            actions[self.project_path / "requirements.txt"] = "openmas>=0.2.0\n"

        # Create .gitignore
        gitignore_content = "__pycache__/\n*.py[cod]\n*$py.class\n.env\n.venv\nenv/\nvenv/\nENV/\nenv.bak/\nvenv.bak/\n"
        gitignore_content += ".pytest_cache/\n.coverage\nhtmlcov/\n.tox/\n.mypy_cache/\n"
        gitignore_content += "# OpenMAS specific\npackages/\n"
        actions[self.project_path / ".gitignore"] = gitignore_content

        # Create openmas_project.yml content
        project_config: Dict[str, Any] = {
            "name": self.project_display_name,
            "version": "0.1.0",
            "agents": {},
            "shared_paths": ["shared"],
            "extension_paths": ["extensions"],
            "default_config": {"log_level": "INFO", "communicator_type": "http"},
            "dependencies": [],
        }

        # Always create a sample agent unless a specific template is used
        if not self.template:
            # Create sample agent files
            sample_agent_dir = self.project_path / "agents" / "sample_agent"

            # Create __init__.py file in the agent directory
            actions[sample_agent_dir / "__init__.py"] = '"""Sample agent package."""\n'

            # Create agent.py file with a simple agent implementation
            actions[
                sample_agent_dir / "agent.py"
            ] = '''"""Sample agent implementation."""

from openmas.agent import BaseAgent

class Agent(BaseAgent):
    """A simple OpenMAS agent."""

    async def setup(self) -> None:
        """Set up the agent."""
        self.logger.info("Setting up sample agent")

    async def run(self) -> None:
        """Run the agent."""
        self.logger.info("Sample agent is running")
        # Implement your agent logic here
        await self.wait_for_shutdown()

    async def shutdown(self) -> None:
        """Shut down the agent."""
        self.logger.info("Shutting down sample agent")
'''

            # Add the sample agent to the project config
            project_config["agents"]["sample_agent"] = "agents/sample_agent"

        # Process template-specific content
        if self.template:
            if self.template.lower() == "mcp-server":
                # Add MCP server agent files
                agent_dir = self.project_path / "agents" / "mcp_server"

                # Create __init__.py file in the agent directory
                actions[agent_dir / "__init__.py"] = '"""MCP Server agent package."""\n'

                # Create agent.py file
                actions[
                    agent_dir / "agent.py"
                ] = """'''MCP Server Agent.'''

import asyncio
from openmas.agent import BaseAgent

class McpServerAgent(BaseAgent):
    '''MCP Server agent implementation.'''

    async def setup(self) -> None:
        '''Set up the MCP server.'''
        # Setup your MCP server here
        pass

    async def run(self) -> None:
        '''Run the MCP server.'''
        # Run your MCP server here
        while True:
            await asyncio.sleep(1)

    async def shutdown(self) -> None:
        '''Shut down the MCP server.'''
        # Shutdown your MCP server here
        pass
"""

                # Create openmas.deploy.yaml file
                actions[
                    agent_dir / "openmas.deploy.yaml"
                ] = """version: "1.0"

component:
  name: "mcp-server"
  type: "service"
  description: "MCP server for model access"

docker:
  build:
    context: "."
    dockerfile: "Dockerfile"

environment:
  - name: "AGENT_NAME"
    value: "${component.name}"
  - name: "LOG_LEVEL"
    value: "INFO"
  - name: "COMMUNICATOR_TYPE"
    value: "http"
  - name: "MCP_API_KEY"
    secret: true
    description: "API key for MCP service"

ports:
  - port: 8000
    protocol: "http"
    description: "HTTP API for MCP access"

volumes:
  - name: "data"
    path: "/app/data"
    description: "Data storage"

dependencies: []
"""

                # Add the agent to the project config
                project_config["agents"]["mcp_server"] = "agents/mcp_server"
            # Add more templates here as needed

        # Add project config file with format determined by yaml.dump in the initialize_project method
        def project_config_content() -> str:
            return yaml.dump(project_config, default_flow_style=False, sort_keys=False)

        actions[self.project_path / "openmas_project.yml"] = project_config_content

        return actions

    def initialize_project(self) -> None:
        """Initialize the project directory structure and files.

        This method performs the actual file system operations to create the project structure.
        It first creates the main project directory and subdirectories, then writes all files
        determined by _prepare_file_actions.

        Raises:
            PermissionError: If there are permission issues creating directories or files
            OSError: If there are other OS-related errors during creation
            ConfigurationError: If there's an issue with the project configuration
        """
        try:
            # Ensure main project directory exists if not using current directory
            if self.project_path != Path("."):
                self.project_path.mkdir(parents=True, exist_ok=False)

            # Create subdirectories
            subdirs: List[str] = ["agents", "shared", "extensions", "config", "tests", "packages"]
            for subdir in subdirs:
                subdir_path = self.project_path / subdir
                subdir_path.mkdir(exist_ok=self.project_path == Path("."))

            # Get all file actions
            file_actions = self._prepare_file_actions()

            # Execute all file actions
            for file_path, content in file_actions.items():
                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Skip if file already exists (specifically for .gitignore)
                if file_path.exists():
                    continue

                # Write content to file
                with open(file_path, "w") as f:
                    if callable(content):
                        f.write(content())
                    else:
                        f.write(content)
        except (PermissionError, OSError):
            # Re-raise these specific errors to be handled by the CLI
            raise
        except Exception as error:
            # Convert unexpected errors to a more informative ConfigurationError
            raise ConfigurationError(f"Failed to initialize project: {str(error)}") from error
