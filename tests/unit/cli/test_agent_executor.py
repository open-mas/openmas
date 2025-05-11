"""Tests for the AgentExecutor class."""

import asyncio
import signal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openmas.agent.base import BaseAgent
from openmas.cli.agent_executor import AgentExecutor
from openmas.cli.event_loop import EventLoopManager
from openmas.exceptions import LifecycleError


class TestAgentExecutor:
    """Tests for the AgentExecutor class."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = MagicMock(spec=BaseAgent)
        agent.name = "test_agent"
        agent._is_running = True
        agent.start = AsyncMock()
        agent.run = AsyncMock()
        agent.stop = AsyncMock()
        agent.shutdown = AsyncMock()
        return agent

    @pytest.fixture
    def mock_project_config(self):
        """Create a mock project config for testing."""
        config = MagicMock()
        config.agents = {"test_agent": MagicMock(), "other_agent": MagicMock()}
        return config

    @pytest.fixture
    def mock_event_loop_manager(self):
        """Create a mock event loop manager for testing."""
        event_loop_manager = MagicMock(spec=EventLoopManager)

        # Mock run_coro_with_signals method
        event_loop_manager.run_coro_with_signals = MagicMock()

        return event_loop_manager

    def test_init(self, mock_agent, mock_project_config, mock_event_loop_manager):
        """Test initialization of AgentExecutor."""
        # Create executor with a custom event loop manager
        executor = AgentExecutor(mock_agent, mock_project_config, event_loop_manager=mock_event_loop_manager)

        # Assert attributes are set correctly
        assert executor.agent is mock_agent
        assert executor.project_config is mock_project_config
        assert executor.event_loop_manager is mock_event_loop_manager
        assert not executor.stop_in_progress
        assert isinstance(executor.shutdown_event, asyncio.Event)

    def test_init_default_event_loop_manager(self, mock_agent, mock_project_config):
        """Test initialization with default event loop manager."""
        # Create executor without specifying event loop manager
        with patch("openmas.cli.agent_executor.EventLoopManager") as mock_event_loop_manager_class:
            # Create a mock instance for the EventLoopManager class
            mock_event_loop_manager_instance = MagicMock()
            mock_event_loop_manager_class.return_value = mock_event_loop_manager_instance

            # Initialize the executor
            executor = AgentExecutor(mock_agent, mock_project_config)

            # Assert EventLoopManager was instantiated
            mock_event_loop_manager_class.assert_called_once()

            # Assert the instance was set
            assert executor.event_loop_manager is mock_event_loop_manager_instance

    def test_signal_handler_with_signal_name(self, mock_agent, mock_project_config):
        """Test signal handler with a signal name."""
        executor = AgentExecutor(mock_agent, mock_project_config)

        # Test with a signal name
        with patch("click.echo") as mock_echo:
            executor._signal_handler("SIGTERM")
            # Assert message was echoed
            mock_echo.assert_called_with("\nReceived signal SIGTERM, initiating graceful shutdown...")
            # Assert shutdown was triggered
            assert executor.stop_in_progress
            assert executor.shutdown_event.is_set()

    def test_signal_handler_without_signal_name(self, mock_agent, mock_project_config):
        """Test signal handler without a signal name."""
        executor = AgentExecutor(mock_agent, mock_project_config)

        # Test without a signal name
        with patch("click.echo") as mock_echo:
            executor._signal_handler()
            # Assert message was echoed
            mock_echo.assert_called_with("\nReceived signal, initiating graceful shutdown...")
            # Assert shutdown was triggered
            assert executor.stop_in_progress
            assert executor.shutdown_event.is_set()

    def test_signal_handler_with_stop_in_progress(self, mock_agent, mock_project_config):
        """Test signal handler when stop is already in progress."""
        executor = AgentExecutor(mock_agent, mock_project_config)

        # Set stop_in_progress to True
        executor.stop_in_progress = True

        # Test with stop already in progress (should exit)
        with patch("click.echo") as mock_echo, patch("sys.exit") as mock_exit:
            executor._signal_handler("SIGINT")
            # Assert forced exit message was displayed (using any_call instead of assert_called_with)
            mock_echo.assert_any_call("\nForced exit. Shutdown already in progress.")
            # Assert exit was called
            mock_exit.assert_called_with(1)

    def test_display_multiagent_guidance(self, mock_agent, mock_project_config):
        """Test display of multiagent guidance."""
        executor = AgentExecutor(mock_agent, mock_project_config)

        # Test with multiple agents
        with patch("click.echo") as mock_echo:
            executor._display_multiagent_guidance()

            # Assert guidance was displayed
            assert mock_echo.call_count >= 4  # Multiple messages should be displayed

    def test_display_multiagent_guidance_single_agent(self, mock_agent, mock_project_config):
        """Test that guidance is not displayed for a single agent project."""
        # Configure project config with just one agent
        mock_project_config.agents = {"test_agent": MagicMock()}

        executor = AgentExecutor(mock_agent, mock_project_config)

        # Test with a single agent
        with patch("click.echo") as mock_echo:
            executor._display_multiagent_guidance()

            # Assert no guidance was displayed
            mock_echo.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_agent_lifecycle_success(self, mock_agent, mock_project_config):
        """Test successful agent lifecycle execution."""
        # Configure mock agent
        mock_agent.run.side_effect = lambda: asyncio.Future()  # Never completes

        executor = AgentExecutor(mock_agent, mock_project_config)

        # Set up patches
        with (
            patch.object(executor, "_display_multiagent_guidance") as mock_display,
            patch("click.echo"),  # We don't need to track this mock
            patch("asyncio.wait") as mock_wait,
            patch("asyncio.create_task") as mock_create_task,
        ):
            # Configure asyncio.wait to simulate a shutdown signal
            mock_done = MagicMock()
            mock_pending = MagicMock()
            mock_wait.return_value = (mock_done, mock_pending)

            # Configure done tasks and pending tasks
            mock_shutdown_task = MagicMock()
            mock_agent_task = MagicMock()

            mock_pending.append(mock_agent_task)
            mock_done.append(mock_shutdown_task)

            # Create mock tasks for task creation
            task1 = MagicMock()
            task1.get_name.return_value = "agent_run_test_agent"
            task2 = MagicMock()
            task2.get_name.return_value = "shutdown_wait_test_agent"

            # Configure create_task to return different mocks for different calls
            mock_create_task.side_effect = [task1, task2]

            # Call the method
            await executor._run_agent_lifecycle()

            # Assert agent was started
            mock_agent.start.assert_called_once()

            # Assert guidance was displayed
            mock_display.assert_called_once()

            # Assert we waited for tasks to complete
            mock_wait.assert_called_once()

            # Assert pending tasks were cancelled
            for task in mock_pending:
                task.cancel.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_agent_lifecycle_start_failure(self, mock_agent, mock_project_config):
        """Test agent lifecycle when start fails."""
        # Configure mock agent to fail on start
        mock_agent.start.side_effect = LifecycleError("Failed to start")

        executor = AgentExecutor(mock_agent, mock_project_config)

        # Set up patches
        with patch("click.echo") as mock_echo:
            # Call the method
            await executor._run_agent_lifecycle()

            # Assert error was echoed
            mock_echo.assert_called_with("❌ Error starting agent: Failed to start")

            # Assert no other methods were called
            mock_agent.run.assert_not_called()
            mock_agent.stop.assert_not_called()

    def test_run(self, mock_agent, mock_project_config, mock_event_loop_manager):
        """Test the run method."""
        executor = AgentExecutor(mock_agent, mock_project_config, event_loop_manager=mock_event_loop_manager)

        # Call run
        executor.run()

        # Assert event loop manager's run_coro_with_signals was called
        mock_event_loop_manager.run_coro_with_signals.assert_called_once()

        # Extract the call arguments
        call_args = mock_event_loop_manager.run_coro_with_signals.call_args

        # Verify the coroutine is execute
        assert call_args[0][0] == executor.execute

        # Verify signal handling is set up
        kwargs = call_args[1]
        assert signal.SIGINT in kwargs["signal_nums"]
        assert signal.SIGTERM in kwargs["signal_nums"]
        assert kwargs["signal_handler"] == executor._signal_handler

    def test_run_keyboard_interrupt(self, mock_agent, mock_project_config, mock_event_loop_manager):
        """Test run method handling of KeyboardInterrupt."""
        # Configure event loop manager to raise KeyboardInterrupt
        mock_event_loop_manager.run_coro_with_signals.side_effect = KeyboardInterrupt()

        executor = AgentExecutor(mock_agent, mock_project_config, event_loop_manager=mock_event_loop_manager)

        # Set up patches
        with patch("click.echo") as mock_echo:
            # Call run
            executor.run()

            # Assert forced exit message was displayed
            mock_echo.assert_called_with("\nForced exit.")

    def test_run_other_exception(self, mock_agent, mock_project_config, mock_event_loop_manager):
        """Test run method handling of other exceptions."""
        # Configure event loop manager to raise an exception
        mock_event_loop_manager.run_coro_with_signals.side_effect = ValueError("Test error")

        executor = AgentExecutor(mock_agent, mock_project_config, event_loop_manager=mock_event_loop_manager)

        # Set up patches
        with patch("click.echo") as mock_echo:
            # Call run, expect exception to be re-raised
            with pytest.raises(ValueError):
                executor.run()

            # Assert error message was displayed
            mock_echo.assert_called_with("❌ Error: Test error")
