"""HTTP communicator implementation for OpenMAS."""

import asyncio
import uuid
from collections.abc import Callable
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError as PydanticValidationError

from openmas.communication.base import BaseCommunicator
from openmas.exceptions import (
    CommunicationError,
    MethodNotFoundError,
    RequestTimeoutError,
    ServiceNotFoundError,
    ValidationError as OpenMasValidationError,
)
from openmas.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class HttpCommunicator(BaseCommunicator):
    """HTTP-based communicator implementation.

    This communicator uses HTTP for communication between services.
    """

    def __init__(
        self,
        agent_name: str,
        service_urls: dict[str, str],
        http_port: int | None = None,
        **kwargs: Any,
    ):
        """Initialize the HTTP communicator.

        Args:
            agent_name: The name of the agent using this communicator
            service_urls: Mapping of service names to URLs
            http_port: Optional port to use for the server (default is determined by configuration)
            **kwargs: Additional keyword arguments including communicator_options
        """
        super().__init__(agent_name, service_urls)
        self.client: httpx.AsyncClient | None = httpx.AsyncClient(timeout=30.0)
        self.handlers: dict[str, Callable] = {}
        self.server_task: asyncio.Task | None = None
        self.http_port = http_port

        # Check communicator options for the port if not explicitly provided
        if self.http_port is None and kwargs.get("communicator_options"):
            self.http_port = kwargs.get("communicator_options", {}).get("http_port")

        # Log the communicator initialization with detailed configuration information
        logger.debug(
            "Initialized HTTP communicator",
            agent_name=agent_name,
            communicator_options=kwargs.get("communicator_options", {}),
            http_port=self.http_port,
            service_urls=service_urls,
        )

    async def send_request(
        self,
        target_service: str,
        method: str,
        params: dict[str, Any] | None = None,
        response_model: type[T] | None = None,
        timeout: float | None = None,
    ) -> Any:
        """Send a request to a target service.

        Args:
            target_service: The name of the service to send the request to
            method: The method to call on the service
            params: The parameters to pass to the method
            response_model: Optional Pydantic model to validate and parse the response
            timeout: Optional timeout in seconds

        Returns:
            The response from the service

        Raises:
            ServiceNotFoundError: If the target service is not found
            CommunicationError: If there is a problem with the communication
            ValidationError: If the response validation fails
        """
        if target_service not in self.service_urls:
            raise ServiceNotFoundError(f"Service '{target_service}' not found", target=target_service)

        url = self.service_urls[target_service]
        request_id = str(uuid.uuid4())
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}

        logger.debug("Sending request", target=target_service, method=method, request_id=request_id)

        try:
            # Make sure client exists
            if self.client is None:
                self.client = httpx.AsyncClient(timeout=30.0)

            response = await self.client.post(url, json=payload, timeout=timeout or self.client.timeout.read)
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                error = result["error"]
                error_code = error.get("code", 0)
                error_message = error.get("message", "Unknown error")

                if error_code == -32601:  # Method not found
                    raise MethodNotFoundError(
                        f"Method '{method}' not found on service '{target_service}'",
                        target=target_service,
                        details={"method": method, "error": error},
                    )

                raise CommunicationError(
                    f"Error from service '{target_service}': {error_message}",
                    target=target_service,
                    details={"method": method, "error": error},
                )

            if "result" not in result:
                raise CommunicationError(
                    f"Invalid response from service '{target_service}': missing 'result'",
                    target=target_service,
                    details={"method": method, "response": result},
                )

            response_data = result["result"]

            # Validate the response if a model was provided
            if response_model is not None:
                try:
                    return response_model.model_validate(response_data)
                except PydanticValidationError as e:
                    raise OpenMasValidationError(f"Response validation failed: {e}")

            return response_data

        except httpx.TimeoutException:
            raise RequestTimeoutError(
                f"Request to '{target_service}' timed out", target=target_service, details={"method": method}
            )
        except httpx.HTTPStatusError as e:
            raise CommunicationError(
                f"HTTP error from '{target_service}': {e.response.status_code} {e.response.reason_phrase}",
                target=target_service,
                details={"method": method, "status_code": e.response.status_code},
            )
        except httpx.HTTPError as e:
            raise CommunicationError(
                f"HTTP error from '{target_service}': {str(e)}", target=target_service, details={"method": method}
            )

    async def send_notification(
        self, target_service: str, method: str, params: dict[str, Any] | None = None
    ) -> None:
        """Send a notification to a target service.

        Args:
            target_service: The name of the service to send the notification to
            method: The method name to call
            params: The parameters to pass to the method

        Raises:
            ServiceNotFoundError: If the target service is not found
            CommunicationError: If there is an error sending the notification
        """
        # Get the service URL
        try:
            url = self.service_urls[target_service]
        except KeyError:
            raise ServiceNotFoundError(f"Service '{target_service}' not found")

        # Create a notification payload (no ID)
        payload = {"jsonrpc": "2.0", "method": method, "params": params or {}}

        logger.debug("Sending notification", target=target_service, method=method)

        try:
            # Make sure client exists
            if self.client is None:
                self.client = httpx.AsyncClient(timeout=30.0)

            response = await self.client.post(url, json=payload)
            # Check if raise_for_status is awaitable
            if hasattr(response.raise_for_status, "__await__"):
                await response.raise_for_status()  # type: ignore[misc]
            else:
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise CommunicationError(
                f"HTTP error from '{target_service}': {str(e)}", target=target_service, details={"method": method}
            )

    async def register_handler(self, method: str, handler: Callable) -> None:
        """Register a handler for a method.

        Args:
            method: The method name to handle
            handler: The handler function
        """
        self.handlers[method] = handler
        logger.debug("Registered handler", method=method)

        # If we have handlers and no server is running, start the server
        if self.handlers and self.server_task is None:
            await self._ensure_server_running()

    async def _ensure_server_running(self) -> None:
        """Ensure the server is running if needed.

        This method starts a FastAPI server if the communicator has registered handlers
        and no server is currently running.
        """
        if self.server_task is None and self.handlers:
            logger.debug("Starting HTTP server")
            try:
                import uvicorn
                from fastapi import FastAPI, Request, Response
                from fastapi.responses import JSONResponse

                # Get port from agent config
                agent_name = self.agent_name
                port = self.http_port

                # Default port if not specified
                if port is None:
                    # Try to extract port from the current hostname if this agent is in service_urls
                    if agent_name in self.service_urls:
                        url = self.service_urls[agent_name]
                        try:
                            import re

                            port_match = re.search(r":(\d+)(?:/|$)", url)
                            if port_match:
                                port = int(port_match.group(1))
                        except Exception:
                            logger.warning("Failed to extract port from URL", url=url)

                    # Use fallback port if extraction failed
                    if port is None:
                        port = 8000
                        logger.info(f"Using default port {port}")

                self.http_port = port
                logger.info(f"Starting HTTP server on port {port}")

                # Use the newer FastAPI lifespan API instead of deprecated on_event
                from collections.abc import AsyncIterator
                from contextlib import asynccontextmanager

                @asynccontextmanager
                async def lifespan(app: FastAPI) -> AsyncIterator[None]:
                    """Handle application lifespan events."""
                    # Startup event
                    logger.debug("HTTP server starting up")
                    yield
                    # Shutdown event
                    logger.debug("HTTP server shutting down")

                # Create FastAPI app
                app = FastAPI(title=f"{agent_name}-api", lifespan=lifespan)

                @app.post("/")  # type: ignore[misc]
                async def handle_jsonrpc(request: Request) -> Response:
                    """Handle JSON-RPC requests."""
                    try:
                        data = await request.json()

                        # Validate request format
                        if "method" not in data:
                            return JSONResponse(
                                content={
                                    "jsonrpc": "2.0",
                                    "error": {"code": -32600, "message": "Invalid request: missing method"},
                                    "id": data.get("id", None),
                                },
                                status_code=400,
                            )

                        method = data["method"]
                        params = data.get("params", {})
                        request_id = data.get("id")

                        # Check if method exists
                        if method not in self.handlers:
                            return JSONResponse(
                                content={
                                    "jsonrpc": "2.0",
                                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                                    "id": request_id,
                                },
                                status_code=404,
                            )

                        # Call the handler
                        handler = self.handlers[method]
                        try:
                            result = await handler(params)
                        except Exception as e:
                            # Convert handler exceptions to JSON-RPC error response
                            logger.exception(f"Handler error: {e}")
                            return JSONResponse(
                                content={
                                    "jsonrpc": "2.0",
                                    "error": {"code": -32000, "message": f"Handler error: {str(e)}"},
                                    "id": request_id,
                                },
                                status_code=500,
                            )

                        # If it's a notification (no ID), return no content
                        if request_id is None:
                            return Response(status_code=204)

                        # Return the result
                        return JSONResponse(content={"jsonrpc": "2.0", "result": result, "id": request_id})
                    except Exception as e:
                        logger.exception(f"Error handling request: {e}")
                        # Return a JSON-RPC error response
                        return JSONResponse(
                            content={
                                "jsonrpc": "2.0",
                                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                                "id": data.get("id", None) if "data" in locals() else None,
                            },
                            status_code=500,
                        )

                # Set the lifespan handler for the app
                app.router.lifespan_context = lifespan  # type: ignore[assignment]

                # Create a server config with proper lifespan setting
                config = uvicorn.Config(
                    app=app,
                    host="0.0.0.0",  # Listen on all interfaces
                    port=port,
                    log_level="info",
                    lifespan="on",  # Ensure proper lifespan management
                )

                # Start the server
                server = uvicorn.Server(config)

                # Define an async task to run the server
                async def run_server_task() -> None:
                    """Run the uvicorn server in a controlled way."""
                    try:
                        await server.serve()
                    except asyncio.CancelledError:
                        logger.debug("Server cancelled, shutting down gracefully")
                    except Exception as e:
                        logger.error(f"HTTP server error: {e}")

                # Run the server in a background task
                self.server_task = asyncio.create_task(run_server_task())
                logger.info(f"Started HTTP server on port {port}")
            except ImportError as e:
                logger.error(f"Cannot start HTTP server: missing dependencies: {e}")
                raise CommunicationError(
                    f"Cannot start HTTP server: {e}. "
                    f"Make sure you have fastapi and uvicorn installed: pip install fastapi uvicorn"
                )
            except Exception as e:
                logger.exception(f"Error starting HTTP server: {e}")
                raise CommunicationError(f"Failed to start HTTP server: {e}")

    async def start(self) -> None:
        """Start the communicator.

        This sets up the HTTP client and starts a server if handlers are registered.
        """
        logger.info("Started HTTP communicator")

        # If we have handlers, make sure the server is running
        if self.handlers:
            await self._ensure_server_running()

    async def stop(self) -> None:
        """Stop the communicator.

        This closes the HTTP client and stops any running server.
        """
        logger.info("Stopping HTTP communicator")

        # Close the client if it exists
        if self.client:
            await self.client.aclose()
            self.client = None

        # Cancel the server task if it exists
        if self.server_task is not None:
            # Check if the task is already done to avoid CancelledError
            if not self.server_task.done():
                # Cancel the task
                self.server_task.cancel()

                # Special handling for AsyncMock in tests
                if hasattr(self.server_task.cancel, "__await__"):
                    try:
                        await self.server_task.cancel()  # type: ignore[misc]
                    except Exception as e:
                        logger.warning(f"Error while awaiting server task cancellation: {e}")

                # Give the task a chance to clean up (but don't wait too long)
                try:
                    await asyncio.wait_for(asyncio.shield(self.server_task), timeout=0.5)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass  # This is expected
                except Exception as e:
                    logger.warning(f"Error while waiting for server task: {e}")

            # Clean up the reference
            self.server_task = None

        logger.info("Stopped HTTP communicator")
