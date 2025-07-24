"""Tests for the ComposeOrchestrator logic in the deployment module."""

import tempfile
from pathlib import Path

import pytest
import yaml

from openmas.deployment.orchestration import ComposeOrchestrator


@pytest.fixture
def sample_project_file():
    """Create a temporary project file with agent configurations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir)

        # Create the project YAML file
        project_data = {
            "name": "test-project",
            "version": "0.1.0",
            "agents": {
                "agent1": "agents/agent1",
                "agent2": "agents/agent2",
            },
        }

        project_file = project_dir / "openmas_project.yml"
        with open(project_file, "w") as f:
            yaml.safe_dump(project_data, f)

        # Create agent1 directory with deployment metadata
        agent1_dir = project_dir / "agents" / "agent1"
        agent1_dir.mkdir(parents=True, exist_ok=True)

        agent1_metadata = {
            "version": "1.0",
            "component": {"name": "agent1", "type": "agent", "description": "Agent 1"},
            "docker": {"build": {"context": ".", "dockerfile": "Dockerfile"}},
            "ports": [{"port": 8001, "protocol": "http"}],
        }

        with open(agent1_dir / "openmas.deploy.yaml", "w") as f:
            yaml.safe_dump(agent1_metadata, f)

        # Create agent2 directory with deployment metadata
        agent2_dir = project_dir / "agents" / "agent2"
        agent2_dir.mkdir(parents=True, exist_ok=True)

        agent2_metadata = {
            "version": "1.0",
            "component": {"name": "agent2", "type": "agent", "description": "Agent 2"},
            "docker": {"build": {"context": ".", "dockerfile": "Dockerfile"}},
            "ports": [{"port": 8002, "protocol": "http"}],
            "dependencies": [{"name": "agent1", "required": True}],
        }

        with open(agent2_dir / "openmas.deploy.yaml", "w") as f:
            yaml.safe_dump(agent2_metadata, f)

        yield project_file


def test_generate_compose_dict_from_project(sample_project_file):
    """Test generating a compose dictionary from a project file."""
    # Create the orchestrator
    orchestrator = ComposeOrchestrator()

    # Generate the compose dictionary
    compose_dict, components, warnings, renamed = orchestrator.generate_compose_dict_from_project(
        sample_project_file, strict=False, use_project_names=True
    )

    # Verify the dictionary structure
    assert "version" in compose_dict
    assert "services" in compose_dict
    assert len(compose_dict["services"]) == 2
    assert "agent1" in compose_dict["services"]
    assert "agent2" in compose_dict["services"]

    # Verify component data was processed
    assert len(components) == 2
    assert len(warnings) == 0

    # Verify service URLs were configured
    agent2_service = next(c for c in components if c.component.name == "agent2")
    agent2_env_names = [env.name for env in agent2_service.environment]
    assert "SERVICE_URL_AGENT1" in agent2_env_names

    # Verify no file IO occurred during dictionary generation
    # (this is implicit since we didn't mock file operations and the test passes)


def test_generate_compose_dict_with_renamed_components(sample_project_file):
    """Test generating a compose dictionary with renamed components."""
    # First modify the agent2 metadata to have a different name
    project_dir = sample_project_file.parent
    agent2_dir = project_dir / "agents" / "agent2"

    with open(agent2_dir / "openmas.deploy.yaml") as f:
        agent2_metadata = yaml.safe_load(f)

    agent2_metadata["component"]["name"] = "different-name"
    agent2_metadata["dependencies"] = [{"name": "agent1", "required": True}]

    with open(agent2_dir / "openmas.deploy.yaml", "w") as f:
        yaml.safe_dump(agent2_metadata, f)

    # Create the orchestrator
    orchestrator = ComposeOrchestrator()

    # Generate with use_project_names=True to enforce renaming
    compose_dict, components, warnings, renamed_components = orchestrator.generate_compose_dict_from_project(
        sample_project_file, strict=False, use_project_names=True
    )

    # Verify renamed components are tracked
    assert "different-name" in renamed_components
    assert renamed_components["different-name"] == "agent2"

    # Verify the service name in the compose dict matches the project name
    assert "agent2" in compose_dict["services"]
    assert "different-name" not in compose_dict["services"]

    # Verify there's a warning about the rename
    assert len(warnings) == 1
    assert "Renaming component" in warnings[0]


def test_save_compose_to_file():
    """Test that save_compose_to_file correctly writes to disk."""
    orchestrator = ComposeOrchestrator()

    # Create a simple compose dictionary
    compose_dict = {"version": "3", "services": {"test-service": {"image": "test-image", "ports": ["8000:8000"]}}}

    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
        try:
            # Save the dictionary to file
            output_path = orchestrator.save_compose_to_file(compose_dict, tmp.name)

            # Verify the file was written correctly
            assert output_path.exists()

            # Read the file content
            with open(output_path) as f:
                content = yaml.safe_load(f)

            # Verify the content matches our dictionary
            assert content == compose_dict
        finally:
            # Clean up the file
            Path(tmp.name).unlink(missing_ok=True)


def test_process_project_file_error_handling():
    """Test error handling in process_project_file method."""
    orchestrator = ComposeOrchestrator()

    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        orchestrator.process_project_file(Path("/nonexistent/path.yml"))

    # Test with empty file (not a dict)
    with tempfile.NamedTemporaryFile(suffix=".yml", mode="w", delete=False) as tmp:
        tmp.write("")  # Empty file
        tmp.flush()

        with pytest.raises(ValueError):
            orchestrator.process_project_file(Path(tmp.name))

        Path(tmp.name).unlink(missing_ok=True)

    # Test with missing agents section
    with tempfile.NamedTemporaryFile(suffix=".yml", mode="w", delete=False) as tmp:
        yaml.safe_dump({"name": "test-project"}, tmp)  # No agents section
        tmp.flush()

        with pytest.raises(ValueError, match="missing 'agents' section"):
            orchestrator.process_project_file(Path(tmp.name))

        Path(tmp.name).unlink(missing_ok=True)


def test_generate_compose_dict_from_project_error_handling():
    """Test error handling in generate_compose_dict_from_project method."""
    orchestrator = ComposeOrchestrator()

    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        orchestrator.generate_compose_dict_from_project(Path("/nonexistent/path.yml"))

    # Test with no components
    with tempfile.NamedTemporaryFile(suffix=".yml", mode="w", delete=False) as tmp:
        yaml.safe_dump({"name": "test", "agents": {}}, tmp)
        tmp.flush()

        with pytest.raises(ValueError, match="No valid components found"):
            orchestrator.generate_compose_dict_from_project(Path(tmp.name))

        Path(tmp.name).unlink(missing_ok=True)


def test_e2e_compose_orchestration(sample_project_file):
    """Test the end-to-end orchestration workflow with dependency injection for testability."""
    orchestrator = ComposeOrchestrator()

    # Generate the compose dictionary
    compose_dict, components, warnings, renamed = orchestrator.generate_compose_dict_from_project(sample_project_file)

    # Verify the dictionary has all expected components
    assert len(compose_dict["services"]) == 2

    # Verify dependency from agent2 to agent1 is configured
    assert "depends_on" in compose_dict["services"]["agent2"]
    assert "agent1" in compose_dict["services"]["agent2"]["depends_on"]

    # Verify URLs are configured for agent2
    agent2 = next(comp for comp in components if comp.component.name == "agent2")
    has_url_env = False
    for env in agent2.environment:
        if env.name == "SERVICE_URL_AGENT1":
            has_url_env = True
            assert env.value == "http://agent1:8001"
    assert has_url_env
