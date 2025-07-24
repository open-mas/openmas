"""Event loop management for OpenMAS CLI.

This module provides an event loop manager for OpenMAS CLI commands
that need to run asyncio code, making it testable and easier to mock.
"""

import asyncio
import contextlib
import functools
import signal
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


class EventLoopManager:
    """Manages asyncio event loops for CLI commands.

    This class encapsulates the complexity of setting up event loops,
    signal handlers, and proper cleanup, making the code more testable.
    """

    def __init__(self) -> None:
        """Initialize a new EventLoopManager."""
        self.loop: asyncio.AbstractEventLoop | None = None
        self.signal_handlers: dict[int, list[Callable[[], None]]] = {}
        self.shutdown_callbacks: list[Callable[[], None]] = []

    def create_loop(self) -> asyncio.AbstractEventLoop:
        """Create a new event loop and set it as the current one.

        Returns:
            The newly created event loop
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        return self.loop

    def add_signal_handler(self, signum: int, callback: Callable[[], None]) -> None:
        """Add a signal handler to the event loop.

        Args:
            signum: The signal number
            callback: The callback to call when the signal is received
        """
        if self.loop is None:
            raise RuntimeError("Event loop not created yet")

        # Store the callback for cleanup
        if signum not in self.signal_handlers:
            self.signal_handlers[signum] = []
        self.signal_handlers[signum].append(callback)

        # Add the handler to the loop
        self.loop.add_signal_handler(signum, callback)

    def add_shutdown_callback(self, callback: Callable[[], None]) -> None:
        """Add a callback to be called during cleanup.

        Args:
            callback: The callback to call during cleanup
        """
        self.shutdown_callbacks.append(callback)

    def run_coro_with_signals(
        self,
        coro: Callable[..., Awaitable[T]],
        *args: Any,
        signal_nums: set[int] | None = None,
        signal_handler: Callable[[str | None], None] | None = None,
        **kwargs: Any,
    ) -> T:
        """Run a coroutine with signal handling.

        Args:
            coro: The coroutine function to run
            *args: Arguments to pass to the coroutine
            signal_nums: Optional set of signal numbers to handle
            signal_handler: Optional signal handler to use
            **kwargs: Keyword arguments to pass to the coroutine

        Returns:
            The result of the coroutine
        """
        if self.loop is None:
            self.create_loop()

        assert self.loop is not None, "Loop should be created by now"

        # Set up signal handlers if provided
        if signal_nums and signal_handler:
            for sig in signal_nums:
                self.add_signal_handler(sig, functools.partial(signal_handler, signal.Signals(sig).name))

        try:
            # Run the coroutine
            coroutine_object = coro(*args, **kwargs)
            # We know the coroutine will resolve to type T
            return self.loop.run_until_complete(coroutine_object)
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Clean up resources used by the event loop manager."""
        if self.loop is None:
            return

        try:
            # Call shutdown callbacks
            for callback in self.shutdown_callbacks:
                with contextlib.suppress(Exception):
                    callback()

            # Cancel all tasks
            tasks = asyncio.all_tasks(self.loop)
            for task in tasks:
                task.cancel()

            # Allow tasks to terminate with CancelledError
            if tasks:
                self.loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

            # Shutdown asyncgens and close the loop
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
        except Exception:
            # Swallow exceptions during cleanup
            pass
        finally:
            # Reset our state
            self.loop = None
            self.signal_handlers.clear()
            self.shutdown_callbacks.clear()

            # Create a new event loop for subsequent operations
            asyncio.set_event_loop(asyncio.new_event_loop())
