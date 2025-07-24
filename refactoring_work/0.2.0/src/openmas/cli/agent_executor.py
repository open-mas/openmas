"""Agent execution and lifecycle management for OpenMAS CLI."""

import asyncio
import signal
import sys

import click

from openmas.agent.base import BaseAgent
from openmas.cli.event_loop import EventLoopManager
from openmas.config import ProjectConfig
from openmas.exceptions import LifecycleError


class AgentExecutor:
    """Manages the asynchronous lifecycle of an agent.

    This class handles:
    - Setting up and cleaning up the asyncio event loop
    - Signal handling for graceful shutdown
    - Agent start, run, and stop lifecycle
    - Multiagent guidance messages
    """

    def __init__(
        self, agent: BaseAgent, project_config: ProjectConfig, event_loop_manager: EventLoopManager | None = None
    ):
        """Initialize a new AgentExecutor.

        Args:
            agent: An instantiated agent
            project_config: The project configuration for guidance messages
            event_loop_manager: Optional custom event loop manager
        """
        self.agent = agent
        self.project_config = project_config
        self.shutdown_event = asyncio.Event()
        self.stop_in_progress = False
        self.event_loop_manager = event_loop_manager or EventLoopManager()

    def _signal_handler(self, signame: str | None = None) -> None:
        """Handle signals for graceful shutdown.

        Args:
            signame: Optional name of the signal received
        """
        if self.stop_in_progress:
            # If we get a second signal during shutdown, exit immediately
            click.echo("\nForced exit. Shutdown already in progress.")
            sys.exit(1)

        if signame:
            click.echo(f"\nReceived signal {signame}, initiating graceful shutdown...")
        else:
            click.echo("\nReceived signal, initiating graceful shutdown...")

        self.stop_in_progress = True
        self.shutdown_event.set()

    def _display_multiagent_guidance(self) -> None:
        """Display guidance message when running in a multi-agent configuration."""
        all_agent_names = list(self.project_config.agents.keys())
        if len(all_agent_names) > 1:
            agent_name = self.agent.name
            other_agents = [a for a in all_agent_names if a != agent_name]
            click.echo("\n[OpenMAS CLI] Agent start success.")
            click.echo("[OpenMAS CLI] To run other agents in this project, open new terminal windows and use:")
            for other_agent in other_agents:
                click.echo(f"[OpenMAS CLI]     openmas run {other_agent}")
            click.echo(f"[OpenMAS CLI] Project agents: {', '.join(all_agent_names)}")
            click.echo("")

    async def _run_agent_lifecycle(self) -> None:
        """Run the agent's lifecycle (start, run, stop) with error handling."""
        start_successful = False
        try:
            # Start the agent - this will call setup() and start the communicator
            try:
                await self.agent.start()
                start_successful = True  # Track that start was successful
            except LifecycleError as e:
                click.echo(f"❌ Error starting agent: {e}")
                return
            except Exception as e:
                click.echo(f"❌ Unexpected error starting agent: {e}")
                return

            # Display guidance message for multiple agents
            self._display_multiagent_guidance()

            # Create tasks for the agent's run method and the shutdown signal wait
            agent_run_task = asyncio.create_task(self.agent.run(), name=f"agent_run_{self.agent.name}")
            shutdown_wait_task = asyncio.create_task(
                self.shutdown_event.wait(), name=f"shutdown_wait_{self.agent.name}"
            )

            # Wait for either the agent to finish or a shutdown signal
            click.echo("Agent is running. Waiting for completion or Ctrl+C...")
            done, pending = await asyncio.wait(
                [agent_run_task, shutdown_wait_task], return_when=asyncio.FIRST_COMPLETED
            )

            if agent_run_task in done:
                click.echo("Agent run method completed.")
                # Check for exceptions in the agent's run task
                try:
                    agent_run_task.result()  # Raise exception if run() had one
                except asyncio.CancelledError:
                    click.echo("Agent run task was cancelled.")
                except Exception as e:
                    click.echo(f"❌ Error during agent execution: {e}")
            else:
                # This means shutdown_wait_task finished (signal received)
                click.echo("Shutdown signal received.")

            # Ensure the other task is cancelled if it's still pending
            for task in pending:
                click.echo(f"Cancelling pending task: {task.get_name()}")
                task.cancel()
                try:
                    # Allow cancellation to propagate
                    await task
                except asyncio.CancelledError:
                    pass  # Expected

        except asyncio.CancelledError:
            click.echo("Agent execution cancelled")
        except Exception as e:
            click.echo(f"❌ Error in agent execution: {e}")
        finally:
            # Only stop the agent if it was successfully started
            if start_successful and hasattr(self.agent, "_is_running") and self.agent._is_running:
                click.echo("Stopping agent...")
                try:
                    await self.agent.stop()
                    click.echo("Agent stopped successfully")
                except Exception as e:
                    click.echo(f"❌ Error stopping agent: {e}")

    async def execute(self) -> None:
        """Execute the agent with proper lifecycle management.

        This method handles the complete execution lifecycle including:
        - Signal handling setup
        - Running the agent lifecycle
        - Cleanup of tasks and resources
        """
        # Run the agent lifecycle
        try:
            # Run the agent lifecycle
            await self._run_agent_lifecycle()
        except Exception as e:
            click.echo(f"❌ Error: {e}")
            raise

    def run(self) -> None:
        """Run the agent in a new event loop.

        This is the main entry point and handles setting up the loop,
        registering signal handlers, and cleanup.
        """
        # Define the signal handler set
        signal_nums: set[int] = {signal.SIGINT, signal.SIGTERM}

        try:
            # Use the event loop manager to run the coroutine with signal handling
            self.event_loop_manager.run_coro_with_signals(
                self.execute, signal_nums=signal_nums, signal_handler=self._signal_handler
            )
        except KeyboardInterrupt:
            # Handle the case where the user rapidly presses Ctrl+C multiple times
            click.echo("\nForced exit.")
        except Exception as e:
            click.echo(f"❌ Error: {e}")
            raise
