"""Tests for the AgentLoader class."""

import importlib
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from openmas.agent.base import BaseAgent
from openmas.cli.agent_loader import AgentLoader
from openmas.exceptions import ConfigurationError


class TestAgentLoader:
    """Tests for the AgentLoader class."""

    def test_load_agent_class_with_expected_class(self):
        """Test loading an agent class when the expected class name is provided."""
        # Create a mock agent module
        mock_module = types.ModuleType("test_agent_module")

        # Create a mock BaseAgent class
        class MockBaseAgent:
            pass

        # Create a mock Agent class that inherits from MockBaseAgent
        class MockAgentClass(MockBaseAgent):
            pass

        # Add the classes to the module
        mock_module.BaseAgent = MockBaseAgent
        mock_module.ExpectedAgent = MockAgentClass

        # Patch necessary functions
        with (
            patch("importlib.import_module", return_value=mock_module),
            patch.object(AgentLoader, "_find_agent_class", return_value=MockAgentClass),
        ):
            # Create and call the AgentLoader
            loader = AgentLoader()
            result = loader.load_agent_class("agents.test_agent", "ExpectedAgent")

            # Assert the correct class is returned
            assert result == MockAgentClass

            # Assert _find_agent_class was called with the right arguments
            AgentLoader._find_agent_class.assert_called_once_with(mock_module, "ExpectedAgent")

    def test_load_agent_class_path_conversion(self):
        """Test that paths are correctly converted to module format."""
        # Create a mock for import_module
        mock_module = types.ModuleType("test_agent_module")

        with (
            patch("importlib.import_module", return_value=mock_module) as mock_import,
            patch.object(AgentLoader, "_find_agent_class", return_value=MagicMock()),
        ):
            # Create and call the AgentLoader with a path-based format
            loader = AgentLoader()
            loader.load_agent_class("agents/test_agent", None)

            # Assert the module path was correctly converted to dot notation
            mock_import.assert_called_once_with("agents.test_agent.agent")

    def test_load_agent_class_direct_file_import(self):
        """Test loading an agent class using direct file import when module import fails."""
        # Create a mock agent module
        mock_module = types.ModuleType("test_agent_module")

        # Create mock classes
        class MockBaseAgent:
            pass

        class MockAgentClass(MockBaseAgent):
            pass

        # Add classes to the module
        mock_module.Agent = MockAgentClass
        mock_module.BaseAgent = MockBaseAgent

        # Instead of using a custom side_effect function that causes recursion,
        # we'll use a patching approach that's more specific
        original_import = importlib.import_module

        def safe_import_mock(name, *args, **kwargs):
            if name == "agents.test_agent.agent":
                raise ModuleNotFoundError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        # Setup mocks for direct file import
        mock_spec = MagicMock()
        mock_spec.loader = MagicMock()

        with (
            patch("importlib.import_module", side_effect=safe_import_mock),
            patch("os.path.exists", return_value=True),
            patch("importlib.util.spec_from_file_location", return_value=mock_spec),
            patch("importlib.util.module_from_spec", return_value=mock_module),
            patch.object(AgentLoader, "_find_agent_class", return_value=MockAgentClass),
        ):
            # Create and call the AgentLoader
            loader = AgentLoader()
            result = loader.load_agent_class("agents.test_agent", None)

            # Assert the correct class is returned
            assert result == MockAgentClass

    def test_load_agent_class_file_not_found(self):
        """Test that ConfigurationError is raised when the agent file is not found."""
        # Use the same safer mocking approach
        original_import = importlib.import_module

        def safe_import_mock(name, *args, **kwargs):
            if name == "agents.test_agent.agent":
                raise ModuleNotFoundError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        with (
            patch("importlib.import_module", side_effect=safe_import_mock),
            patch("os.path.exists", return_value=False),
        ):
            # Create and call the AgentLoader
            loader = AgentLoader()

            # Assert that ConfigurationError is raised
            with pytest.raises(ConfigurationError, match="Agent file not found"):
                loader.load_agent_class("agents.test_agent", None)

    def test_load_agent_class_missing_dependency(self):
        """Test that ImportError is raised when a dependency is missing."""
        # Mock for when importlib.import_module fails with a dependency issue
        mock_dependency_error = ModuleNotFoundError("No module named 'some_dependency'")

        with patch("importlib.import_module", side_effect=mock_dependency_error):
            # Create and call the AgentLoader
            loader = AgentLoader()

            # Assert that ImportError is raised and propagated
            with pytest.raises(ImportError, match="Missing dependency"):
                loader.load_agent_class("agents.test_agent", None)

    def test_find_agent_class_specific_name(self):
        """Test _find_agent_class when a specific class name is provided."""
        mock_module = types.ModuleType("test_module")

        # Create base and derived classes
        class MockBaseAgent:
            pass

        # Patch BaseAgent for issubclass check
        with patch("openmas.cli.agent_loader.BaseAgent", MockBaseAgent):

            class ExpectedAgent(MockBaseAgent):
                pass

            class OtherAgent(MockBaseAgent):
                pass

            # Add the classes to the module
            mock_module.ExpectedAgent = ExpectedAgent
            mock_module.OtherAgent = OtherAgent

            # Create and call the AgentLoader
            loader = AgentLoader()
            result = loader._find_agent_class(mock_module, "ExpectedAgent")

            # Assert the correct class is returned
            assert result == ExpectedAgent

    def test_find_agent_class_no_expected_name_use_agent(self):
        """Test _find_agent_class when no expected name is provided but 'Agent' class exists."""
        mock_module = types.ModuleType("test_module")

        # Create base and derived classes
        class MockBaseAgent:
            pass

        # Patch BaseAgent for issubclass check
        with patch("openmas.cli.agent_loader.BaseAgent", MockBaseAgent):

            class Agent(MockBaseAgent):
                pass

            class OtherAgent(MockBaseAgent):
                pass

            # Add the classes to the module
            mock_module.Agent = Agent
            mock_module.OtherAgent = OtherAgent

            # Create and call the AgentLoader
            loader = AgentLoader()
            result = loader._find_agent_class(mock_module, None)

            # Assert the 'Agent' class is returned
            assert result == Agent

    def test_find_agent_class_no_expected_name_first_subclass(self):
        """Test _find_agent_class when no expected name is provided and no 'Agent' class exists."""
        mock_module = types.ModuleType("test_module")

        # Create base and derived classes
        class MockBaseAgent:
            pass

        # Patch BaseAgent for issubclass check
        with patch("openmas.cli.agent_loader.BaseAgent", MockBaseAgent):

            class FirstAgent(MockBaseAgent):
                pass

            class SecondAgent(MockBaseAgent):
                pass

            # Add the classes to the module
            mock_module.FirstAgent = FirstAgent
            mock_module.SecondAgent = SecondAgent

            # Create and call the AgentLoader
            loader = AgentLoader()
            result = loader._find_agent_class(mock_module, None)

            # Assert the first subclass is returned
            assert result == FirstAgent

    def test_find_agent_class_expected_name_not_found(self):
        """Test _find_agent_class when the expected class name is not found."""
        mock_module = types.ModuleType("test_module")
        mock_module.__name__ = "test_module"

        # Create base and derived classes
        class MockBaseAgent:
            pass

        # Patch BaseAgent for issubclass check
        with patch("openmas.cli.agent_loader.BaseAgent", MockBaseAgent):

            class SomeAgent(MockBaseAgent):
                pass

            # Add the class to the module
            mock_module.SomeAgent = SomeAgent

            # Create and call the AgentLoader
            loader = AgentLoader()

            # Assert that ConfigurationError is raised
            with pytest.raises(ConfigurationError, match="not found in module"):
                loader._find_agent_class(mock_module, "NonExistentAgent")

    def test_find_agent_class_expected_name_not_agent_subclass(self):
        """Test _find_agent_class when the expected class is found but is not a BaseAgent subclass."""
        mock_module = types.ModuleType("test_module")

        # Create base and non-agent class
        class MockBaseAgent:
            pass

        class NonAgentClass:
            pass

        # Patch BaseAgent for issubclass check
        with patch("openmas.cli.agent_loader.BaseAgent", MockBaseAgent):
            # Add the class to the module
            mock_module.NonAgentClass = NonAgentClass

            # Create and call the AgentLoader
            loader = AgentLoader()

            # Assert that ConfigurationError is raised
            with pytest.raises(ConfigurationError, match="not a valid BaseAgent subclass"):
                loader._find_agent_class(mock_module, "NonAgentClass")

    def test_find_agent_class_no_agent_subclass_found(self):
        """Test _find_agent_class when no BaseAgent subclass is found."""
        mock_module = types.ModuleType("test_module")

        # Create base class but no subclasses
        class MockBaseAgent:
            pass

        class NonAgentClass:
            pass

        # Patch BaseAgent for issubclass check
        with patch("openmas.cli.agent_loader.BaseAgent", MockBaseAgent):
            # Add the non-agent class to the module
            mock_module.NonAgentClass = NonAgentClass
            mock_module.BaseAgent = MockBaseAgent  # Add BaseAgent itself

            # Create and call the AgentLoader
            loader = AgentLoader()

            # Assert that ConfigurationError is raised
            with pytest.raises(ConfigurationError, match="No BaseAgent subclass found"):
                loader._find_agent_class(mock_module, None)
