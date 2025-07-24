"""Base agent implementation for OpenMAS."""

import abc
import asyncio
from contextlib import suppress
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from openmas.assets.manager import AssetManager
from openmas.communication import BaseCommunicator, discover_local_communicators
from openmas.config import AgentConfig, load_config
from openmas.exceptions import ConfigurationError, DependencyError, LifecycleError
from openmas.logging import configure_logging, get_logger

logger = get_logger(__name__)


class BaseAgent(abc.ABC):
    """Base agent class for all OpenMAS agents.

    This class provides the basic structure for agents, including configuration loading,
    communication setup, and lifecycle management.
    """

    def __init__(
        self,
        name: str | None = None,
        config: dict[str, Any] | AgentConfig | None = None,
        config_model: type[AgentConfig] = AgentConfig,
        communicator_class: type[BaseCommunicator] | None = None,
        env_prefix: str = "",
        project_root: Path | None = None,
        asset_manager: AssetManager | None = None,
    ):
        """Initialize the agent.

        Args:
            name: The name of the agent (overrides config)
            config: The agent configuration (if not provided, will be loaded from environment)
            config_model: The configuration model class to use
            communicator_class: The communicator class to use (overrides config.communicator_type)
            env_prefix: Optional prefix for environment variables
            project_root: The project root directory for resolving prompt/template files
            asset_manager: Optional asset manager for retrieving external resources
        """
        # Load configuration
        # If config is a dict, convert it to an AgentConfig instance
        # If config is None, load from environment variables
        if config is None:
            self.config = load_config(config_model, env_prefix)
        elif isinstance(config, dict):
            # Add name to the config dictionary if provided
            if name and "name" not in config:
                config["name"] = name
            try:
                self.config = config_model(**config)
            except ValidationError as e:
                error_msg = f"Configuration validation failed: {e}"
                logger.error(error_msg)
                raise ConfigurationError(error_msg)
        else:
            # config is already an AgentConfig instance
            # Ensure it's the right type though
            if not isinstance(config, config_model):
                try:
                    # If it's a different AgentConfig subclass, try to convert
                    self.config = config_model(**config.model_dump())
                except ValidationError as e:
                    error_msg = f"Configuration validation failed: {e}"
                    logger.error(error_msg)
                    raise ConfigurationError(error_msg)
            else:
                self.config = config

        # Override name if provided
        if name:
            self.config.name = name

        # Configure logging
        configure_logging(log_level=self.config.log_level)
        self.logger = get_logger(self.__class__.__name__)

        # Discover and create communicator
        # If communicator_class is provided, use it directly
        # Otherwise, look it up based on config.communicator_type
        if communicator_class is None:
            communicator_class = self._get_communicator_class(self.config.communicator_type)

        # Create the communicator, passing communicator_options as kwargs
        # Extract communicator options and pass them properly to constructor
        communicator_kwargs = {}

        # Pass all communicator_options as direct kwargs to ensure they're correctly passed
        # to the appropriate parameter in the communicator's constructor
        if hasattr(self.config, "communicator_options") and self.config.communicator_options:
            communicator_kwargs.update(self.config.communicator_options)
            self.logger.debug("Passing communicator options to communicator", options=communicator_kwargs)

        # Create the communicator with extracted options
        self.communicator = communicator_class(
            self.config.name,
            self.config.service_urls,
            **communicator_kwargs,
        )

        # Internal state
        self._is_running = False
        self._task: asyncio.Task | None = None
        self._background_tasks: set[asyncio.Task] = set()

        # Store project root for prompt/template resolution
        self.project_root = project_root or Path.cwd()

        # Store asset manager for accessing external resources
        self.asset_manager = asset_manager
        if self.asset_manager:
            self.logger.debug("Asset manager provided", manager=self.asset_manager)

        self.logger.info("Initialized agent", agent_name=self.config.name, agent_type=self.__class__.__name__)

    def _get_communicator_class(self, communicator_type: str) -> type[BaseCommunicator]:
        """Get the communicator class for the specified type.

        This method uses the lazy-loading mechanism to find communicator classes without
        importing unnecessary dependencies.

        Args:
            communicator_type: The type identifier for the communicator

        Returns:
            The communicator class

        Raises:
            ConfigurationError: If the communicator type cannot be found
            DependencyError: If the communicator requires an optional dependency that is not installed
        """
        try:
            # First try to get using our lazy loading mechanism
            from openmas.communication import get_communicator_by_type

            return get_communicator_by_type(communicator_type)
        except DependencyError as e:
            self.logger.error(f"Missing dependency for communicator type '{communicator_type}': {str(e)}")
            raise
        except ValueError:
            # If not found, check local extension paths
            if self.config.extension_paths:
                discover_local_communicators(self.config.extension_paths)
                try:
                    # Try again after discovering local communicators
                    from openmas.communication import get_communicator_by_type

                    return get_communicator_by_type(communicator_type)
                except DependencyError as e:
                    self.logger.error(f"Missing dependency for communicator type '{communicator_type}': {str(e)}")
                    raise
                except ValueError:
                    pass

            # If we get here, the communicator type is not found
            from openmas.communication.base import _COMMUNICATOR_REGISTRY

            available_types = ", ".join(sorted(list(_COMMUNICATOR_REGISTRY.keys())))
            available = available_types or "none"
            message = (
                f"Communicator type '{communicator_type}' not found. "
                f"Available types: {available}. "
                f"Check your configuration or provide a valid communicator_class."
            )
            self.logger.error(message)
            raise ConfigurationError(message)

    @property
    def name(self) -> str:
        """Get the agent name."""
        return self.config.name

    def set_communicator(self, communicator: BaseCommunicator) -> None:
        """Set the communicator for this agent.

        This method allows changing the communicator after agent initialization.

        Args:
            communicator: The communicator to use
        """
        self.communicator = communicator
        self.logger.info("Set communicator", agent_name=self.name, communicator_type=communicator.__class__.__name__)

    def create_background_task(self, coro: Any) -> asyncio.Task:
        """Create a background task that will be properly cancelled during shutdown.

        Args:
            coro: Coroutine to run as a background task

        Returns:
            The created task
        """
        task = asyncio.create_task(coro)
        self._background_tasks.add(task)
        # Remove the task from the set when it's done
        task.add_done_callback(self._background_tasks.discard)
        return task

    async def start(self) -> None:
        """Start the agent.

        This method initializes the agent, sets up the communicator, and starts the main loop.
        """
        if self._is_running:
            raise LifecycleError("Agent is already running")

        self.logger.info("Starting agent", agent_name=self.name)

        try:
            # Start the communicator
            await self.communicator.start()
        except Exception as e:
            self.logger.error("Failed to start communicator", error=str(e), exc_info=True)
            raise LifecycleError(f"Failed to start communicator: {e}") from e

        try:
            # Call setup hook - wrap in try/except to catch any exceptions
            self.logger.debug("Setting up agent")
            await self.setup()
            self.logger.debug("Agent setup complete")
        except Exception as e:
            self.logger.error("Error in agent setup", error=str(e), exc_info=True)
            # Try to stop the communicator if setup fails
            try:
                await self.communicator.stop()
            except Exception as stop_error:
                self.logger.error("Failed to stop communicator after setup error", error=str(stop_error))
            raise LifecycleError(f"Error in agent setup: {e}") from e

        # Start the main loop
        self._is_running = True
        self._task = asyncio.create_task(self._run_lifecycle())

        self.logger.info("Agent started", agent_name=self.name)

    async def stop(self) -> None:
        """Stop the agent.

        This method stops the main loop, calls the shutdown hook, and stops the communicator.
        """
        if not self._is_running:
            self.logger.debug("Agent not running, stop is a no-op")
            return

        self.logger.info("Stopping agent", agent_name=self.name)
        self._is_running = False

        # Cancel the main loop task
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
            self._task = None

        # Cancel all background tasks
        for task in list(self._background_tasks):
            if not task.done():
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

        # Call shutdown hook - wrap in try/except to catch any exceptions
        # and ensure communicator is stopped even if shutdown fails
        try:
            self.logger.debug("Shutting down agent")
            await self.shutdown()
            self.logger.debug("Agent shutdown complete")
        except Exception as e:
            self.logger.error("Error in agent shutdown", error=str(e), exc_info=True)
        finally:
            # Stop the communicator (last, in case shutdown needs it)
            try:
                await self.communicator.stop()
            except Exception as e:
                self.logger.error("Failed to stop communicator", error=str(e), exc_info=True)

        self.logger.info("Agent stopped", agent_name=self.name)

    async def _run_lifecycle(self) -> None:
        """Run the agent's lifecycle.

        This method is the main loop for the agent.
        """
        try:
            self.logger.debug("Running agent")
            await self.run()
            self.logger.debug("Agent run method completed")
        except asyncio.CancelledError:
            self.logger.debug("Agent lifecycle task was cancelled")
            raise
        except Exception as e:
            self.logger.error("Error in agent run method", error=str(e), exc_info=True)
            # We don't re-raise the exception here to avoid killing the agent process
            # This gives us a chance to clean up properly via stop()
        finally:
            # This handles the case when run() completes naturally
            if self._is_running:
                # We're still running, meaning run() completed on its own
                # Call stop to perform a clean shutdown
                self.logger.debug("Agent run method completed, stopping agent")
                await self.stop()

    @abc.abstractmethod
    async def setup(self) -> None:
        """Set up the agent.

        This method is called when the agent is started, before run().
        Override this method to perform any initialization tasks.
        """
        pass

    @abc.abstractmethod
    async def run(self) -> None:
        """Run the agent.

        This method is called after setup() and represents the main operation of the agent.
        Override this method to implement the agent's main behavior.
        """
        pass

    @abc.abstractmethod
    async def shutdown(self) -> None:
        """Shut down the agent.

        This method is called when the agent is stopped, after run() completes.
        Override this method to perform any cleanup tasks.
        """
        pass
