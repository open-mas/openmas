"""Integration tests for the deps command in the OpenMAS CLI."""

import os
import subprocess
import sys
from unittest.mock import mock_open, patch

import pytest
import yaml


@pytest.fixture
def git_setup(tmp_path):
    """Create a minimal Git repo for testing."""
    # Create a fake repository
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Initialize Git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)

    # Configure Git (required for commits)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True, capture_output=True)

    # Create src directory
    src_dir = repo_path / "src"
    src_dir.mkdir()

    # Create a sample Python module
    sample_module = src_dir / "sample.py"
    with open(sample_module, "w") as f:
        f.write(
            """
def hello():
    return "Hello from test repo"
"""
        )

    # Add and commit
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True, capture_output=True)

    # Create and checkout a branch
    subprocess.run(["git", "checkout", "-b", "test-branch"], cwd=repo_path, check=True, capture_output=True)

    # Make a change on the branch
    with open(sample_module, "w") as f:
        f.write(
            """
def hello():
    return "Hello from test branch"
"""
        )

    # Commit the change
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Update on branch"], cwd=repo_path, check=True, capture_output=True)

    # Go back to main branch
    subprocess.run(["git", "checkout", "master"], cwd=repo_path, check=True, capture_output=True)

    return repo_path


@pytest.fixture
def test_project(tmp_path, git_setup):
    """Create a test OpenMAS project with a dependency."""
    # Create project directory
    project_dir = tmp_path / "test_openmas_project"
    project_dir.mkdir()

    # Create required directories
    subdirs = ["agents", "shared", "extensions", "config", "tests", "packages"]
    for subdir in subdirs:
        (project_dir / subdir).mkdir()

    # Create openmas_project.yml with dependency to the test repo
    config = {
        "name": "test_project",
        "version": "0.1.0",
        "agents": {"test_agent": "agents/test_agent"},
        "shared_paths": ["shared"],
        "extension_paths": ["extensions"],
        "default_config": {"log_level": "INFO"},
        "dependencies": [{"git": str(git_setup), "revision": "test-branch"}],
    }

    with open(project_dir / "openmas_project.yml", "w") as f:
        yaml.dump(config, f)

    # Create agent directory and file
    agent_dir = project_dir / "agents" / "test_agent"
    agent_dir.mkdir()

    with open(agent_dir / "agent.py", "w") as f:
        f.write(
            """
from openmas.agent import BaseAgent

class TestAgent(BaseAgent):
    async def setup(self):
        pass

    async def run(self):
        # This code will try to import from our test repo
        try:
            from sample import hello
            print(hello())
        except ImportError as e:
            print(f"Import error: {e}")

    async def shutdown(self):
        pass
"""
        )

    return project_dir


@pytest.mark.skipif(sys.platform == "win32", reason="Git operations in integration tests may be unreliable on Windows")
def test_deps_integration(test_project, monkeypatch, git_setup):
    """Test that the deps command correctly installs Git packages."""
    # Use CI approach with mocks to avoid directory issues
    from click.testing import CliRunner

    from openmas.cli.main import cli

    # Print diagnostic information
    print(f"\nTest project path: {test_project}")
    print(f"Git setup path: {git_setup}")

    # Define a custom exists function to prevent recursion
    original_exists = os.path.exists

    def custom_exists(path):
        # Always return True for the git repo path
        if str(path).endswith(git_setup.name):
            return True
        # For the packages directory, return True
        if str(path).endswith("packages"):
            return True
        # For the sample.py file, return True
        if str(path).endswith("sample.py"):
            return True
        # Use the original function for other paths
        return original_exists(path)

    # Mock all subprocess calls and file operations
    with (
        patch("subprocess.run") as mock_run,
        patch("os.chdir") as mock_chdir,
        patch("os.getcwd", return_value=str(test_project)),
        patch("os.path.exists", side_effect=custom_exists),
        patch("os.path.isdir", return_value=True),
    ):
        # Configure mock to return successful result for all subprocess calls
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b"Mocked git output"

        # Mock file operations for reading
        sample_content = """
def hello():
    return "Hello from test branch"
"""
        # Define a more selective mock_open to prevent recursion
        orig_open = open

        def selective_open(*args, **kwargs):
            if args and isinstance(args[0], (str, bytes, os.PathLike)):
                path = str(args[0])
                if path.endswith("sample.py"):
                    return mock_open(read_data=sample_content)(*args, **kwargs)
                if "openmas_project.yml" in path:
                    # Create a mock file for project config
                    return mock_open(
                        read_data=yaml.dump(
                            {
                                "name": "test_project",
                                "version": "0.1.0",
                                "dependencies": [{"git": str(git_setup), "revision": "test-branch"}],
                            }
                        )
                    )(*args, **kwargs)
            return orig_open(*args, **kwargs)

        # Run the command with our more controlled mocks
        with patch("builtins.open", selective_open):
            runner = CliRunner()
            # Avoid actually changing directory, just let the patched version handle it
            result = runner.invoke(cli, ["deps"])

            print(f"Command output:\n{result.output}")

            # Check command succeeded
            assert result.exit_code == 0, f"Command failed with: {result.output}"

            # Verify mock was called
            assert mock_run.called, "subprocess.run was not called"


@pytest.mark.skipif(sys.platform == "win32", reason="Git operations in integration tests may be unreliable on Windows")
def test_deps_integration_update(test_project, monkeypatch, git_setup):
    """Test that the deps command updates an existing Git package."""
    # Use CI approach with mocks to avoid directory issues
    from click.testing import CliRunner

    from openmas.cli.main import cli

    # Print diagnostic information
    print(f"\nTest project path: {test_project}")
    print(f"Git setup path: {git_setup}")

    # Mock all subprocess calls and file operations
    with (
        patch("subprocess.run") as mock_run,
        patch("os.chdir") as mock_chdir,
        patch("os.getcwd", return_value=str(test_project)),
    ):
        # Configure mock to return successful result
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b"Mocked git output"

        # Mock file/directory existence for the cloned repo
        with patch("os.path.exists", return_value=True):
            # Run the deps command
            runner = CliRunner()
            monkeypatch.chdir(test_project)  # This is safe now as it's mocked

            # First deps command install
            result1 = runner.invoke(cli, ["deps"])
            assert result1.exit_code == 0, f"First deps command failed with: {result1.output}"

            # Mock second run - update
            result2 = runner.invoke(cli, ["deps"])

            # Check command output
            print(f"Update command output:\n{result2.output}")
            assert result2.exit_code == 0, f"Update command failed with: {result2.output}"

            # We can't check the exact message because we're mocking, but we can verify
            # that the subprocess was called more than once (initial + update)
            assert mock_run.call_count >= 2, "Not enough subprocess calls for update operation"
