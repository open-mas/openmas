"""
OpenMAS MCP Agent Implementation

This module provides the MCPAgent class that specializes the base Agent
for MCP (Model Context Protocol) communication. It uses the MCP-SIMF translator
to maintain SIMF-first internal messaging while connecting to real MCP servers.

Based on specifications in:
- refactoring_work/planning/TASK_basic_agent_framework_implementation.md (Phase B)
- examples/simf_mcp_integration/mcp_to_simf_translator.py (MCP integration patterns)
- examples/mcp_validation/real_mcp_server.py (real MCP validation)
"""

import asyncio
import os
import sys
from typing import Any, Dict, List, Optional

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import Tool

from openmas.agent.base_agent import Agent, AgentConfig
from openmas.agent.exceptions import AgentConfigurationError, AgentError
from openmas.core.simf import (
    InvocationStatus,
    SIMFMessage,
    create_invocation_result_message,
)

# Add path for MCP translator import
sys.path.append(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "examples", "simf_mcp_integration"
    )
)

try:
    from mcp_to_simf_translator import MCPToSIMFTranslator
except ImportError:
    # Fallback for when translator is not available
    MCPToSIMFTranslator = None


class MCPAgent(Agent):
    """
    MCP-specialized agent that connects to MCP servers while maintaining
    SIMF-first internal communication.

    This agent:
    - Inherits all base Agent functionality (SIMF integration, lifecycle, etc.)
    - Adds MCP server connection and tool execution capabilities
    - Uses MCPToSIMFTranslator for seamless MCP ↔ SIMF translation
    - Maintains protocol independence in internal operations
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        mcp_server_command: List[str],
        session_id: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        Initialize MCP Agent.

        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
            mcp_server_command: Command to start MCP server
            (e.g., ["python", "server.py"])
            session_id: Optional session identifier
            capabilities: Additional agent capabilities
            **kwargs: Additional configuration passed to base Agent
        """
        # Create agent configuration
        config = AgentConfig(
            agent_id=agent_id, name=name, capabilities=capabilities or []
        )

        # Initialize base agent
        super().__init__(config=config, **kwargs)

        # MCP-specific configuration
        self.mcp_server_command = mcp_server_command
        self.mcp_session: Optional[ClientSession] = None
        self.mcp_translator = MCPToSIMFTranslator(agent_id)
        self.available_tools: Dict[str, Tool] = {}

        # Session management
        if session_id:
            self.current_session_id = session_id

        self.logger.info(f"MCPAgent initialized: {name} ({agent_id})")
        self.logger.debug(f"MCP server command: {' '.join(mcp_server_command)}")

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def is_running(self) -> bool:
        """Check if the agent is currently running."""
        return self._running

    @property
    def session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self.current_session_id

    # ========================================================================
    # Lifecycle Management
    # ========================================================================

    async def start(self) -> None:
        """
        Start the MCP agent, including MCP server connection.
        """
        # Start base agent
        await super().start()

        # Connect to MCP server
        await self._connect_mcp_server()

        # Discover available tools and register as capabilities
        await self._discover_mcp_tools()

        self.logger.info(f"MCPAgent started with {len(self.available_tools)} MCP tools")

    async def stop(self) -> None:
        """
        Stop the agent and clean up MCP session.
        """
        await super().stop()

        # Reset connection state
        self.mcp_session = None

        # Clean up server parameters
        if hasattr(self, "_server_params"):
            delattr(self, "_server_params")
            self.logger.info("MCP server connection parameters cleared")

    async def _connect_mcp_server(self) -> None:
        """
        Establish connection to the MCP server and initialize the session.
        """
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=self.mcp_server_command[0],
                args=(
                    self.mcp_server_command[1:]
                    if len(self.mcp_server_command) > 1
                    else []
                ),
                env=None,
            )

            # Test connection with proper initialization sequence
            try:
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        # CRITICAL: Explicitly initialize session to prevent race
                        # condition
                        await asyncio.wait_for(session.initialize(), timeout=10.0)

                        # If we get here, the session is properly initialized
                        self.logger.info("MCP connection test successful")

                        # Store connection info for later use
                        self._server_params = server_params
                        # Set flag to indicate successful connection (for tests)
                        self.mcp_session = "connected"  # Simple indicator for tests

            except Exception as e:
                self.logger.error(f"MCP connection test failed: {e}")
                raise AgentConfigurationError(f"MCP server connection test failed: {e}")

            self.logger.info("Connected to MCP server successfully")

        except AgentConfigurationError:
            # Re-raise configuration errors as-is
            raise
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server: {e}")
            raise AgentConfigurationError(f"MCP server connection failed: {e}")

    async def _discover_mcp_tools(self) -> None:
        """
        Discover available MCP tools and register them as agent capabilities.
        """
        try:
            if not hasattr(self, "_server_params"):
                raise AgentError("MCP server not connected")

            # Use temporary session for tool discovery (proper MCP pattern)
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # CRITICAL: Explicitly initialize session before making requests
                    await asyncio.wait_for(session.initialize(), timeout=10.0)

                    # Now it's safe to make MCP requests
                    tools_response = await session.list_tools()

                    self.logger.info(
                        f"Discovered {len(tools_response.tools)} MCP tools"
                    )

                    # Register each tool as a capability
                    for tool in tools_response.tools:
                        capability_name = (
                            tool.name
                        )  # Use actual tool name, not prefixed

                        # Tool registered successfully - no need to store
                        # capability dict

                        # Register the capability (base Agent only expects the name)
                        await self.register_capability(capability_name)

                        # Store the capability details with the capability name
                        self.available_tools[capability_name] = tool

                        self.logger.debug(
                            f"Registered MCP tool '{tool.name}' as capability "
                            f"'{capability_name}'"
                        )

        except Exception as e:
            self.logger.error(f"Failed to discover MCP tools: {e}")
            raise AgentError(f"MCP tool discovery failed: {e}")

    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute an MCP tool with the given parameters.

        Args:
            tool_name: Name of the MCP tool to execute
            parameters: Parameters to pass to the tool

        Returns:
            Result from the tool execution
        """
        if not hasattr(self, "_server_params"):
            raise AgentError("MCP server not connected")

        try:
            # Use temporary session for tool execution (proper MCP pattern)
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # CRITICAL: Explicitly initialize session before making requests
                    await asyncio.wait_for(session.initialize(), timeout=10.0)

                    # Now it's safe to execute the tool
                    result = await session.call_tool(tool_name, parameters)

                    # Extract the actual result from the MCP response
                    if (
                        hasattr(result, "structuredContent")
                        and result.structuredContent
                    ):
                        # Return the structured content which is the actual result
                        extracted_result = result.structuredContent
                    elif hasattr(result, "content") and result.content:
                        # Fallback to text content if structured content not available
                        extracted_result = (
                            result.content[0].text if result.content else str(result)
                        )
                    else:
                        # Fallback to string representation
                        extracted_result = str(result)

                    self.logger.debug(
                        f"Executed MCP tool '{tool_name}' with result: "
                        f"{extracted_result}"
                    )
                    return extracted_result

        except Exception as e:
            self.logger.error(f"Failed to execute MCP tool '{tool_name}': {e}")
            raise AgentError(f"MCP tool execution failed: {e}")

    async def execute_capability(self, simf_message: SIMFMessage) -> SIMFMessage:
        """
        Execute a capability based on the incoming SIMF message.

        Args:
            simf_message: SIMF message containing capability execution request

        Returns:
            SIMF response message with execution results
        """
        try:
            capability_name = simf_message.payload.invocation_name
            if not capability_name:
                raise AgentError("No capability specified in message")

            self.logger.info(f"Executing capability: {capability_name}")

            # For MCPAgent, try to execute as MCP tool first
            # (MCPAgent primarily handles MCP tool capabilities)
            try:
                # Execute as MCP tool
                result = await self.execute_mcp_tool(
                    tool_name=capability_name,
                    parameters=simf_message.payload.arguments or {},
                )

                # Create successful response
                response = create_invocation_result_message(
                    invocation_name=capability_name,
                    status=InvocationStatus.SUCCESS,
                    target_agent_id=simf_message.source_agent_id or "unknown",
                    result=result,
                    source_agent_id=self.agent_id,
                    session_id=self.session_id,
                )

                self.logger.info(f"Capability executed successfully: {capability_name}")
                return response

            except Exception as e:
                # Create error response for MCP tool failures
                error_response = create_invocation_result_message(
                    invocation_name=capability_name,
                    status=InvocationStatus.FAILURE,
                    target_agent_id=simf_message.source_agent_id or "unknown",
                    result={"error": str(e)},
                    source_agent_id=self.agent_id,
                    session_id=self.session_id,
                )

                self.logger.error(
                    f"MCP capability execution failed: {capability_name} - {e}"
                )
                return error_response

        except Exception as e:
            # Create error response for unexpected errors
            error_response = create_invocation_result_message(
                invocation_name=(
                    capability_name if "capability_name" in locals() else "unknown"
                ),
                status=InvocationStatus.FAILURE,
                target_agent_id=simf_message.source_agent_id or "unknown",
                result={"error": str(e)},
                source_agent_id=self.agent_id,
                session_id=self.session_id,
            )

            self.logger.error(f"Unexpected error during capability execution: {e}")
            return error_response

    def get_mcp_tools(self) -> Dict[str, Tool]:
        """
        Get all available MCP tools.

        Returns:
            Dictionary mapping tool names to Tool objects
        """
        return self.available_tools.copy()

    def is_mcp_tool(self, capability_name: str) -> bool:
        """
        Check if a capability is an MCP tool.

        Args:
            capability_name: Name of the capability to check

        Returns:
            True if the capability is an MCP tool
        """
        return capability_name in self.available_tools


# ============================================================================
# Factory Support
# ============================================================================


def create_mcp_agent_from_config(config: Dict[str, Any]) -> MCPAgent:
    """
    Create MCPAgent from configuration dictionary.

    Args:
        config: Configuration dictionary with MCP-specific settings

    Returns:
        Configured MCPAgent instance

    Raises:
        AgentConfigurationError: If configuration is invalid
    """
    try:
        # Extract required configuration
        agent_id = config.get("agent_id")
        name = config.get("name")
        mcp_server_command = config.get("mcp_server_command")

        if not agent_id:
            raise AgentConfigurationError("agent_id is required")
        if not name:
            raise AgentConfigurationError("name is required")
        if not mcp_server_command:
            raise AgentConfigurationError("mcp_server_command is required")

        # Extract optional configuration
        session_id = config.get("session_id")
        capabilities_config = config.get("capabilities", [])

        # Convert capability configs to strings if needed
        capabilities = []
        for cap_config in capabilities_config:
            if isinstance(cap_config, dict):
                capabilities.append(cap_config["name"])
            else:
                capabilities.append(cap_config)

        # Create agent
        return MCPAgent(
            agent_id=agent_id,
            name=name,
            mcp_server_command=mcp_server_command,
            session_id=session_id,
            capabilities=capabilities,
            **{
                k: v
                for k, v in config.items()
                if k
                not in [
                    "agent_id",
                    "name",
                    "mcp_server_command",
                    "session_id",
                    "capabilities",
                ]
            },
        )

    except Exception as e:
        raise AgentConfigurationError(f"Failed to create MCPAgent from config: {e}")
