"""Tests for the generate-compose command of the deployment CLI."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from openmas.cli.deploy import _generate_compose_from_project_impl
from openmas.deployment.metadata import (
    ComponentSpec as Component,
    DependencySpec as Dependency,
    DeploymentMetadata,
    DockerSpec as DockerComposeConfig,
    EnvironmentVar,
)


class TestGenerateComposeFromProject:
    @patch("openmas.deployment.orchestration.ComposeOrchestrator.save_compose_to_file")
    @patch("openmas.deployment.orchestration.ComposeOrchestrator.generate_compose_dict_from_project")
    @patch("openmas.deployment.metadata.DeploymentMetadata.from_file")
    @patch("yaml.safe_load")  # Mock the yaml.safe_load function
    @patch("builtins.open", mock_open())  # Mock file open
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.parent", new_callable=MagicMock)
    def test_generate_compose_from_project(
        self,
        mock_parent,
        mock_exists,
        mock_yaml_load,
        mock_from_file,
        mock_generate_compose,
        mock_save_compose,
    ):
        print("Starting test_generate_compose_from_project", file=sys.stderr)
        # Mock project root and agent paths
        project_root = Path("/path/to/project")
        mock_parent.return_value = project_root

        # Make sure Path.exists returns True for all paths
        mock_exists.return_value = True

        # Mock yaml.safe_load to return a project config directly instead of parsing
        mock_yaml_load.return_value = {
            "agents": {
                "agent1": "path/to/agent1",
                "agent2": "path/to/agent2",
                "agent3": "path/to/agent3",
            }
        }

        print("Setting up metadata mocks", file=sys.stderr)
        # Mock DeploymentMetadata for agent1 with a dependency on agent3
        agent1_metadata = DeploymentMetadata(
            version="1.0",
            component=Component(name="agent1", type="agent"),
            dependencies=[
                Dependency(
                    name="different-name",
                )
            ],
            docker=DockerComposeConfig(),
            environment=[EnvironmentVar(name="API_KEY", value="test-api-key", secret=True)],
        )

        # Mock DeploymentMetadata for agent2
        agent2_metadata = DeploymentMetadata(
            version="1.0",
            component=Component(name="agent2", type="agent"),
            docker=DockerComposeConfig(),
        )

        # Mock DeploymentMetadata for agent3
        agent3_metadata = DeploymentMetadata(
            version="1.0",
            component=Component(name="different-name", type="agent"),
            docker=DockerComposeConfig(),
        )

        # Set up the mock to return different metadata for each call
        mock_from_file.side_effect = [agent1_metadata, agent2_metadata, agent3_metadata]

        # Set up mocks for the refactored class
        mock_components = [agent1_metadata, agent2_metadata, agent3_metadata]
        mock_renamed = {"different-name": "agent3"}
        mock_warnings: list[str] = []
        mock_compose_dict = {"version": "3", "services": {}}

        # Configure the mock for the generate_compose_dict_from_project method
        mock_generate_compose.return_value = (mock_components, mock_renamed, mock_warnings, mock_compose_dict)

        # Configure the mock for save_compose_to_file
        mock_save_compose.return_value = Path("docker-compose.yml")

        # Mock _configure_service_urls function to add service URLs
        def configure_services(components):
            # Add SERVICE_URL to agent1
            service_url = EnvironmentVar(
                name="SERVICE_URL_DIFFERENT_NAME",
                value="http://different-name:8080",
                secret=False,
            )
            components[0].environment.append(service_url)
            return components

        with patch("openmas.cli.deploy._configure_service_urls", side_effect=configure_services):
            print("Calling _generate_compose_from_project_impl", file=sys.stderr)
            # Call the function
            result = _generate_compose_from_project_impl(
                project_file="openmas_project.yml",
                output="docker-compose.yml",
                strict=False,
                use_project_names=False,
            )

        print("Function returned, making assertions", file=sys.stderr)
        # Assertions
        assert result == 0
        mock_generate_compose.assert_called_once()
        mock_save_compose.assert_called_once()

        print("Test completed successfully", file=sys.stderr)

    @patch("openmas.deployment.orchestration.ComposeOrchestrator.save_compose_to_file")
    @patch("openmas.deployment.orchestration.ComposeOrchestrator.generate_compose_dict_from_project")
    @patch("openmas.deployment.metadata.DeploymentMetadata.from_file")
    @patch("yaml.safe_load")  # Mock the yaml.safe_load function
    @patch("builtins.open", mock_open())  # Mock file open
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.parent", new_callable=MagicMock)
    def test_generate_compose_strict_mode(
        self,
        mock_parent,
        mock_exists,
        mock_yaml_load,
        mock_from_file,
        mock_generate_compose,
        mock_save_compose,
    ):
        print("Starting test_generate_compose_strict_mode", file=sys.stderr)
        # Mock project root
        project_root = Path("/path/to/project")
        mock_parent.return_value = project_root

        # Mock yaml.safe_load to return a project config directly instead of parsing
        mock_yaml_load.return_value = {
            "agents": {
                "agent1": "path/to/agent1",
                "agent2": "path/to/agent2",
                "missing": "path/to/missing",
            }
        }

        # Mock existence of files - make project file exist, but have specific logic for other paths
        def exists_side_effect(path):
            path_str = str(path)
            if path_str.endswith("openmas_project.yml"):
                return True
            return "missing" not in path_str

        mock_exists.side_effect = exists_side_effect

        # Mock DeploymentMetadata for agent1 and agent2
        agent1_metadata = DeploymentMetadata(
            version="1.0",
            component=Component(name="agent1", type="agent"),
            docker=DockerComposeConfig(),
        )
        agent2_metadata = DeploymentMetadata(
            version="1.0",
            component=Component(name="agent2", type="agent"),
            docker=DockerComposeConfig(),
        )

        # Set up the mock to return different metadata for each call
        mock_from_file.side_effect = [agent1_metadata, agent2_metadata]

        # Patch the _configure_service_urls function to do nothing
        with patch("openmas.cli.deploy._configure_service_urls"):
            print("Calling _generate_compose_from_project_impl", file=sys.stderr)
            # Test with strict mode (should fail)
            result = _generate_compose_from_project_impl(
                project_file="openmas_project.yml",
                output="docker-compose.yml",
                strict=True,
                use_project_names=False,
            )

        print("Function returned, making assertions", file=sys.stderr)
        # Assertions for strict mode
        assert result == 1
        mock_generate_compose.assert_not_called()
        mock_save_compose.assert_not_called()
        print("Test completed successfully", file=sys.stderr)

    @patch("openmas.deployment.orchestration.ComposeOrchestrator.save_compose_to_file")
    @patch("openmas.deployment.orchestration.ComposeOrchestrator.generate_compose_dict_from_project")
    @patch("openmas.deployment.metadata.DeploymentMetadata.from_file")
    @patch("yaml.safe_load")  # Mock the yaml.safe_load function
    @patch("builtins.open", mock_open())  # Mock file open
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.parent", new_callable=MagicMock)
    def test_generate_compose_with_use_project_names(
        self,
        mock_parent,
        mock_exists,
        mock_yaml_load,
        mock_from_file,
        mock_generate_compose,
        mock_save_compose,
    ):
        print("Starting test_generate_compose_with_use_project_names", file=sys.stderr)
        # Mock project root
        project_root = Path("/path/to/project")
        mock_parent.return_value = project_root

        # Make sure Path.exists returns True for all paths
        mock_exists.return_value = True

        # Mock yaml.safe_load to return a project config directly instead of parsing
        mock_yaml_load.return_value = {
            "agents": {
                "agent1": "path/to/agent1",
                "agent2": "path/to/agent2",
            }
        }

        # Mock DeploymentMetadata with different names in metadata
        metadata1 = DeploymentMetadata(
            version="1.0",
            component=Component(name="different-name-1", type="agent"),
            docker=DockerComposeConfig(),
        )
        metadata2 = DeploymentMetadata(
            version="1.0",
            component=Component(name="different-name-2", type="agent"),
            docker=DockerComposeConfig(),
            dependencies=[Dependency(name="different-name-1")],
        )

        # Set up the mock to return different metadata for each call
        mock_from_file.side_effect = [metadata1, metadata2]

        # Set up the mock for generate_compose_dict_from_project
        mock_components = [metadata1, metadata2]
        mock_renamed = {"different-name-1": "agent1", "different-name-2": "agent2"}
        mock_warnings = [
            "Renaming component from 'different-name-1' to 'agent1' to match project config",
            "Renaming component from 'different-name-2' to 'agent2' to match project config",
        ]
        mock_compose_dict = {"version": "3", "services": {}}

        # Configure the mock for generate_compose_dict_from_project
        mock_generate_compose.return_value = (mock_components, mock_renamed, mock_warnings, mock_compose_dict)

        # Configure the mock for save_compose_to_file
        mock_save_compose.return_value = Path("docker-compose.yml")

        # Mock _configure_service_urls function to add service URLs
        def configure_services(components):
            # Add SERVICE_URL to agent2 (which was renamed from different-name-2)
            service_url = EnvironmentVar(
                name="SERVICE_URL_AGENT1",
                value="http://agent1:8080",
                secret=False,
            )
            components[1].environment.append(service_url)
            return components

        with patch("openmas.cli.deploy._configure_service_urls", side_effect=configure_services):
            print("Calling _generate_compose_from_project_impl", file=sys.stderr)
            # Call the function with use_project_names
            result = _generate_compose_from_project_impl(
                project_file="openmas_project.yml",
                output="docker-compose.yml",
                strict=False,
                use_project_names=True,
            )

        print("Function returned, making assertions", file=sys.stderr)
        # Assertions
        assert result == 0
        mock_generate_compose.assert_called_once()
        mock_save_compose.assert_called_once()

        print("Test completed successfully", file=sys.stderr)
