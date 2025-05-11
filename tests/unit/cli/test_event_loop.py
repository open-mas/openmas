"""Tests for the EventLoopManager class."""

import asyncio
import signal
from unittest.mock import MagicMock, patch

import pytest

from openmas.cli.event_loop import EventLoopManager


@pytest.fixture
def cleanup_event_loop():
    """Ensure event loop is cleaned up after tests."""
    yield
    # Create a new event loop for subsequent tests
    try:
        asyncio.get_event_loop().close()
    except Exception:
        pass
    asyncio.set_event_loop(asyncio.new_event_loop())


class TestEventLoopManager:
    """Tests for the EventLoopManager class."""

    def test_create_loop(self, cleanup_event_loop):
        """Test creating an event loop."""
        manager = EventLoopManager()

        # Create a loop
        loop = manager.create_loop()

        # Verify the loop was created and set as current
        assert loop is not None
        assert loop is manager.loop
        assert loop is asyncio.get_event_loop()

    def test_add_signal_handler(self, cleanup_event_loop):
        """Test adding a signal handler."""
        manager = EventLoopManager()

        # Create a loop first
        manager.create_loop()

        # Add a signal handler
        mock_callback = MagicMock()
        manager.add_signal_handler(signal.SIGINT, mock_callback)

        # Verify the handler was added
        assert signal.SIGINT in manager.signal_handlers
        assert mock_callback in manager.signal_handlers[signal.SIGINT]

    def test_add_signal_handler_without_loop(self):
        """Test adding a signal handler without creating a loop first."""
        manager = EventLoopManager()

        # Verify that adding a signal handler without a loop raises an error
        with pytest.raises(RuntimeError, match="Event loop not created yet"):
            manager.add_signal_handler(signal.SIGINT, MagicMock())

    def test_add_shutdown_callback(self):
        """Test adding a shutdown callback."""
        manager = EventLoopManager()

        # Add a shutdown callback
        mock_callback = MagicMock()
        manager.add_shutdown_callback(mock_callback)

        # Verify the callback was added
        assert mock_callback in manager.shutdown_callbacks

    @patch("asyncio.all_tasks")
    def test_cleanup(self, mock_all_tasks, cleanup_event_loop):
        """Test cleanup of event loop."""
        manager = EventLoopManager()

        # Create a loop and add handlers
        loop = manager.create_loop()

        # Add a shutdown callback
        mock_callback = MagicMock()
        manager.add_shutdown_callback(mock_callback)

        # Mock a task to ensure cancellation happens
        mock_task = MagicMock()
        mock_all_tasks.return_value = [mock_task]

        # Patch the loop's run_until_complete to avoid actually running code
        with patch.object(loop, "run_until_complete"), patch.object(loop, "close"):
            # Call cleanup
            manager.cleanup()

            # Verify the callback was called
            mock_callback.assert_called_once()

            # Verify the task was cancelled
            mock_task.cancel.assert_called_once()

            # Verify state was reset
            assert manager.loop is None
            assert len(manager.signal_handlers) == 0
            assert len(manager.shutdown_callbacks) == 0

    @pytest.mark.asyncio
    def test_run_coro_with_signals(self, cleanup_event_loop):
        """Test running a coroutine with signal handling."""
        # Setup
        manager = EventLoopManager()

        # Create a simple coroutine to test
        async def test_coro(value):
            return value * 2

        # Create a mock signal handler
        mock_signal_handler = MagicMock()

        # Call run_coro_with_signals
        with (
            patch.object(manager, "create_loop") as mock_create_loop,
            patch.object(manager, "cleanup") as mock_cleanup,
            patch.object(manager, "add_signal_handler") as mock_add_signal_handler,
        ):
            # Setup the mock loop
            mock_loop = MagicMock()
            mock_create_loop.return_value = mock_loop
            manager.loop = mock_loop

            # Mock the loop's run_until_complete to return a known value
            mock_loop.run_until_complete.return_value = 42

            # Run the coroutine
            result = manager.run_coro_with_signals(
                test_coro, 21, signal_nums={signal.SIGINT, signal.SIGTERM}, signal_handler=mock_signal_handler
            )

            # Verify the signal handlers were added
            assert mock_add_signal_handler.call_count == 2

            # Verify the loop's run_until_complete was called
            mock_loop.run_until_complete.assert_called_once()

            # Verify cleanup was called
            mock_cleanup.assert_called_once()

            # Verify the result
            assert result == 42

    @patch("asyncio.all_tasks")
    def test_cleanup_with_exception(self, mock_all_tasks, cleanup_event_loop):
        """Test cleanup handles exceptions gracefully."""
        manager = EventLoopManager()

        # Create a loop
        loop = manager.create_loop()

        # Add a callback that raises an exception
        mock_callback = MagicMock(side_effect=Exception("Test exception"))
        manager.add_shutdown_callback(mock_callback)

        # Mock a task
        mock_task = MagicMock()
        mock_all_tasks.return_value = [mock_task]

        # Patch the loop's run_until_complete to avoid actually running code
        with patch.object(loop, "run_until_complete"), patch.object(loop, "close"):
            # Call cleanup - should not raise an exception
            manager.cleanup()

            # Verify the callback was called despite raising an exception
            mock_callback.assert_called_once()

            # Verify state was still reset
            assert manager.loop is None
