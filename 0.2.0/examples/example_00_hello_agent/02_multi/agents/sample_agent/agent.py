"""
Sample agent implementation for OpenMAS.

This template demonstrates Dependency Injection, graceful shutdown, and best practices for testable agents.

To add more agents, copy this file into a new directory under `agents/` and update `openmas_project.yml`.
"""
import asyncio
import signal
from openmas.agent import BaseAgent

class Agent(BaseAgent):
    """A robust, testable OpenMAS agent with graceful shutdown."""

    def __init__(self, shutdown_event: asyncio.Event = None, **kwargs):
        super().__init__(**kwargs)
        self.shutdown_event = shutdown_event or asyncio.Event()

    async def setup(self) -> None:
        """Set up the agent. Inject dependencies here for testability."""
        self.logger.info("Setting up sample agent")
        # Example: self.db = kwargs.get('db')

    async def run(self) -> None:
        """Run the agent main loop. Supports graceful shutdown and testability."""
        self.logger.info("Sample agent is running")
        try:
            while not self.shutdown_event.is_set():
                # Agent logic here
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.logger.info("Run loop cancelled")
        except Exception as e:
            self.logger.error(f"Agent encountered an error: {e}")
            raise

    async def shutdown(self) -> None:
        """Shut down the agent gracefully."""
        self.logger.info("Shutting down sample agent")
        self.shutdown_event.set()

# Graceful shutdown handler for standalone runs
def _handle_signals(agent):
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(agent.shutdown()))

# Example main for running the agent standalone (for testing)
if __name__ == "__main__":
    shutdown_event = asyncio.Event()
    agent = Agent(shutdown_event=shutdown_event)
    _handle_signals(agent)
    asyncio.run(agent.setup())
    try:
        asyncio.run(agent.run())
    finally:
        asyncio.run(agent.shutdown())
