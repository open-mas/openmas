"""
MCP Protocol Adapter

Implements the IProtocolAdapter interface for the Model Context Protocol (MCP),
providing support for stdio transport with full SIMF integration.
"""

import asyncio
import contextlib
import json
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any
from openmas.agent.base_agent import IProtocolAdapter

from openmas.core.simf import SIMFMessage

from .config import MCPConfig, MCPTransportType
from .exceptions import MCPConnectionError, MCPMessageError
from .message_translator import MCPMessageTranslator

# Import MCP SDK components
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.server.fastmcp import FastMCP

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

logger = logging.getLogger(__name__)


class MCPProtocolAdapter(IProtocolAdapter):
    """
    MCP Protocol Adapter implementing IProtocolAdapter interface.

    Provides bidirectional communication between OpenMAS agents using the
    Model Context Protocol over stdio transport.
    """

    def __init__(self, agent_id: str):
        """
        Initialize the MCP protocol adapter.

        Args:
            agent_id: Unique identifier for the agent using this adapter
        """
        if not MCP_AVAILABLE:
            raise ImportError("MCP SDK not available. Install with: pip install mcp")

        self.agent_id = agent_id
        self.config: MCPConfig | None = None
        self.translator = MCPMessageTranslator(agent_id)

        # Connection state
        self.connected = False
        self.connection_error: str | None = None
        self.connected_at: datetime | None = None
        self.last_activity: datetime | None = None
        self.message_count = 0
        self.error_count = 0

        # Transport-specific components
        self.client_session: ClientSession | None = None
        self.server: FastMCP | None = None
        self.message_callback: Callable[[SIMFMessage], Awaitable[None]] | None = None

        # Background tasks
        self._connection_task: asyncio.Task | None = None

    async def connect(self, config: dict[str, Any]) -> None:
        """
        Initialize and establish the MCP connection.

        Args:
            config: MCP-specific configuration

        Raises:
            MCPConnectionError: If connection cannot be established
            ValueError: If configuration is invalid
        """
        try:
            # Convert dict config to MCPConfig object
            mcp_config = MCPConfig(**config) if isinstance(config, dict) else config
            # Validate configuration
            mcp_config.validate_transport_config()
            self.config = mcp_config

            logger.info(f"Connecting MCP adapter for agent {self.agent_id} " f"with transport {mcp_config.transport}")

            if mcp_config.server_mode:
                await self._connect_server()
            else:
                await self._connect_client()

            self.connected = True
            self.connected_at = datetime.utcnow()
            self.connection_error = None

            logger.info(f"MCP adapter connected successfully for agent {self.agent_id}")

        except Exception as e:
            self.connection_error = str(e)
            self.error_count += 1
            logger.error(f"Failed to connect MCP adapter: {e}")
            raise MCPConnectionError(f"Failed to connect MCP adapter: {e}") from e

    async def disconnect(self) -> None:
        """Clean up MCP connection and resources."""
        try:
            logger.info(f"Disconnecting MCP adapter for agent {self.agent_id}")

            # Cancel background tasks
            if self._connection_task and not self._connection_task.done():
                self._connection_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._connection_task

            # Close client session
            if self.client_session:
                # Client session doesn't have explicit close method
                self.client_session = None

            # Stop server
            if self.server:
                # FastMCP doesn't have explicit stop method in basic usage
                self.server = None

            self.connected = False
            self.connected_at = None

            logger.info(f"MCP adapter disconnected for agent {self.agent_id}")

        except Exception as e:
            logger.error(f"Error during MCP disconnect: {e}")
            self.error_count += 1

    async def send_message(self, simf_message: SIMFMessage) -> None:
        """
        Send SIMF message via MCP protocol.

        Args:
            simf_message: SIMF message to send

        Raises:
            MCPConnectionError: If not connected
            MCPMessageError: If message cannot be sent
        """
        if not self.connected:
            raise MCPConnectionError("MCP adapter not connected")

        try:
            # Translate SIMF to MCP
            mcp_message = self.translator.from_internal_format(simf_message)

            # Send via appropriate transport
            if self.config and self.config.server_mode:
                await self._send_server_message(mcp_message)
            else:
                await self._send_client_message(mcp_message)

            self.message_count += 1
            self.last_activity = datetime.utcnow()

            logger.debug(f"Sent MCP message: {mcp_message.get('method', 'unknown')}")

        except Exception as e:
            self.error_count += 1
            logger.error(f"Failed to send MCP message: {e}")
            raise MCPMessageError(f"Failed to send MCP message: {e}") from e

    async def register_message_callback(self, callback: Callable[[SIMFMessage], Awaitable[None]]) -> None:
        """
        Register callback for incoming messages.

        Args:
            callback: Async function to call when messages are received
        """
        self.message_callback = callback
        logger.debug(f"Registered message callback for agent {self.agent_id}")

    def to_internal_format(self, mcp_message: dict[str, Any]) -> SIMFMessage:
        """
        Convert MCP message to SIMF format.

        Args:
            mcp_message: MCP protocol message

        Returns:
            SIMFMessage: SIMF representation
        """
        return self.translator.to_internal_format(mcp_message)

    def from_internal_format(self, simf_message: SIMFMessage) -> dict[str, Any]:
        """
        Convert SIMF message to MCP format.

        Args:
            simf_message: SIMF message

        Returns:
            Dict[str, Any]: MCP protocol message
        """
        return self.translator.from_internal_format(simf_message)

    # Transport-specific connection methods

    async def _connect_server(self) -> None:
        """Connect as MCP server."""
        if not self.config:
            raise MCPConnectionError("No configuration provided")

        # Create FastMCP server
        self.server = FastMCP(name=self.config.server_name, version=self.config.server_version)

        # Register default tools/resources/prompts
        await self._register_default_mcp_capabilities()

        logger.info(f"MCP server initialized: {self.config.server_name}")

    async def _connect_client(self) -> None:
        """Connect as MCP client."""
        if not self.config:
            raise MCPConnectionError("No configuration provided")

        if self.config.transport == MCPTransportType.STDIO:
            await self._connect_stdio_client()
        # Note: SSE transport removed - deprecated in MCP SDK 1.8+
        else:
            raise MCPConnectionError(f"Unsupported transport: {self.config.transport}")

    async def _connect_stdio_client(self) -> None:
        """Connect stdio client."""
        if not self.config or not self.config.stdio_config:
            raise MCPConnectionError("No stdio configuration provided")

        stdio_config = self.config.stdio_config

        # Create server parameters
        server_params = StdioServerParameters(
            command=stdio_config.command, args=stdio_config.args, env=stdio_config.env
        )

        try:
            # Start background task for client connection
            self._connection_task = asyncio.create_task(self._run_stdio_client(server_params))

            # Wait a moment for connection to establish
            await asyncio.sleep(0.1)

        except Exception as e:
            raise MCPConnectionError(f"Failed to connect stdio client: {e}") from e

    # Note: _connect_sse_client method removed - SSE transport deprecated in MCP
    # SDK 1.8+

    async def _run_stdio_client(self, server_params: StdioServerParameters) -> None:
        """Run stdio client in background task."""
        try:
            async with stdio_client(server_params) as (read, write), ClientSession(read, write) as session:
                self.client_session = session

                # Initialize session
                await session.initialize()
                logger.info("MCP stdio client session initialized")

                # Keep connection alive and handle messages
                while self.connected:
                    await asyncio.sleep(1.0)

        except Exception as e:
            logger.error(f"MCP stdio client error: {e}")
            self.connection_error = str(e)
            self.connected = False

    # Message sending methods

    async def _send_server_message(self, mcp_message: dict[str, Any]) -> None:
        """Send message from server side."""
        # Server-side message sending would depend on how we expose the server
        # For now, log the message
        logger.info(f"MCP server would send: {mcp_message}")

    async def _send_client_message(self, mcp_message: dict[str, Any]) -> None:
        """Send message from client side."""
        if not self.client_session:
            raise MCPConnectionError("No active client session")

        try:
            method = mcp_message.get("method", "")
            params = mcp_message.get("params", {})

            # Route based on method
            if method == "tools/call":
                call_result = await self.client_session.call_tool(
                    name=params.get("name", ""), arguments=params.get("arguments", {})
                )
                await self._handle_mcp_result(call_result, mcp_message.get("id"))

            elif method == "tools/list":
                list_tools_result = await self.client_session.list_tools()
                await self._handle_mcp_result(list_tools_result.tools, mcp_message.get("id"))

            elif method == "resources/read":
                from pydantic import AnyUrl

                read_resource_result = await self.client_session.read_resource(AnyUrl(params.get("uri", "")))
                await self._handle_mcp_result(read_resource_result, mcp_message.get("id"))

            elif method == "resources/list":
                list_resources_result = await self.client_session.list_resources()
                await self._handle_mcp_result(list_resources_result.resources, mcp_message.get("id"))

            elif method == "prompts/get":
                get_prompt_result = await self.client_session.get_prompt(
                    name=params.get("name", ""), arguments=params.get("arguments", {})
                )
                await self._handle_mcp_result(get_prompt_result, mcp_message.get("id"))

            elif method == "prompts/list":
                list_prompts_result = await self.client_session.list_prompts()
                await self._handle_mcp_result(list_prompts_result.prompts, mcp_message.get("id"))

            else:
                logger.warning(f"Unsupported MCP method: {method}")

        except Exception as e:
            raise MCPMessageError(f"Failed to send client message: {e}") from e

    async def _handle_mcp_result(self, result: Any, request_id: str | None) -> None:
        """Handle MCP result and convert to SIMF for callback."""
        if not self.message_callback:
            return

        try:
            # Create MCP result message
            mcp_result = {"jsonrpc": "2.0", "id": request_id, "result": result}

            # Convert to SIMF and call callback
            simf_message = self.translator.to_internal_format(mcp_result)
            if self.message_callback is not None:
                await self.message_callback(simf_message)

        except Exception as e:
            logger.error(f"Error handling MCP result: {e}")

    # Default MCP capabilities

    async def _register_default_mcp_capabilities(self) -> None:
        """Register default MCP tools/resources/prompts for the server."""
        if not self.server:
            return

        # Register a basic echo tool
        @self.server.tool()
        def echo(message: str) -> str:
            """Echo the input message."""
            return f"Echo: {message}"

        # Register an agent info resource
        @self.server.resource("agent://info")
        def agent_info() -> str:
            """Get agent information."""
            return json.dumps(
                {
                    "agent_id": self.agent_id,
                    "protocol": "mcp",
                    "status": "connected",
                    "connected_at": (self.connected_at.isoformat() if self.connected_at else None),
                }
            )

        logger.info("Registered default MCP capabilities")
