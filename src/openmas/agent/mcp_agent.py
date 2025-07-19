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
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import (
    CallToolRequest,
    CallToolRequestParams,
    CallToolResult,
    ListToolsRequest,
    Tool,
)

from openmas.agent.base_agent import Agent, AgentConfig
from openmas.agent.exceptions import AgentError, AgentConfigurationError
from openmas.core.simf import (
    SIMFMessage,
    MessageType,
    MessageFlowDirection,
    PayloadType,
    InvocationContentPayload,
    InvocationResultContentPayload,
    InvocationStatus,
    create_invocation_message,
    create_invocation_result_message,
)

# Import MCP-SIMF translator
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'examples', 'simf_mcp_integration'))
from mcp_to_simf_translator import MCPToSIMFTranslator


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
        **kwargs
    ):
        """
        Initialize MCP Agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
            mcp_server_command: Command to start MCP server (e.g., ["python", "server.py"])
            session_id: Optional session identifier
            capabilities: Additional agent capabilities
            **kwargs: Additional configuration passed to base Agent
        """
        # Create agent configuration
        config = AgentConfig(
            agent_id=agent_id,
            name=name,
            capabilities=capabilities or []
        )
        
        # Initialize base agent
        super().__init__(
            config=config,
            **kwargs
        )
        
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
        Stop the MCP agent, including MCP server disconnection.
        """
        # Disconnect from MCP session
        if self.mcp_session:
            try:
                await self.mcp_session.close()
                self.logger.info("MCP session closed")
            except Exception as e:
                self.logger.warning(f"Error closing MCP session: {e}")
            finally:
                self.mcp_session = None
        
        # Close stdio context if it exists
        if hasattr(self, 'stdio_context') and self.stdio_context:
            try:
                await self.stdio_context.__aexit__(None, None, None)
            except Exception as e:
                self.logger.warning(f"Error closing stdio context: {e}")
            finally:
                self.stdio_context = None
        
        # Stop base agent
        await super().stop()
        
        self.logger.info("MCPAgent stopped")
    
    async def _connect_mcp_server(self) -> None:
        """
        Connect to the MCP server using stdio transport.
        """
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=self.mcp_server_command[0],
                args=self.mcp_server_command[1:] if len(self.mcp_server_command) > 1 else [],
                env=None
            )
            
            # Connect to server using context manager pattern
            self.stdio_context = stdio_client(server_params)
            read, write = await self.stdio_context.__aenter__()
            
            # Create and initialize session
            self.mcp_session = ClientSession(read, write)
            await self.mcp_session.initialize()
            
            self.logger.info("Connected to MCP server successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server: {e}")
            raise AgentConfigurationError(f"MCP server connection failed: {e}")
    
    async def _discover_mcp_tools(self) -> None:
        """
        Discover available tools from the MCP server and register them as capabilities.
        """
        if not self.mcp_session:
            raise AgentError("MCP session not established")
        
        try:
            # List available tools
            tools_response = await self.mcp_session.list_tools()
            
            # Store tools and register as capabilities
            for tool in tools_response.tools:
                self.available_tools[tool.name] = tool
                
                # Register capability (base Agent uses string-based capabilities)
                await self.register_capability(tool.name)
            
            self.logger.info(f"Discovered {len(self.available_tools)} MCP tools")
            for tool_name in self.available_tools.keys():
                self.logger.debug(f"  - {tool_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to discover MCP tools: {e}")
            raise AgentError(f"MCP tool discovery failed: {e}")
    
    async def _execute_mcp_tool(
        self, 
        capability_name: str, 
        parameters: Dict[str, Any],
        source_message: Optional[SIMFMessage] = None
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool and return the result.
        
        Args:
            capability_name: Name of the MCP tool to execute
            parameters: Tool parameters
            source_message: Optional source SIMF message for context
            
        Returns:
            Tool execution result
        """
        if not self.mcp_session:
            raise AgentError("MCP session not established")
        
        if capability_name not in self.available_tools:
            raise AgentError(f"Unknown MCP tool: {capability_name}")
        
        try:
            self.logger.info(f"Executing MCP tool: {capability_name}")
            self.logger.debug(f"Tool parameters: {parameters}")
            
            # Create MCP tool call request
            mcp_request = CallToolRequest(
                id=str(uuid4()),
                method="tools/call",
                params=CallToolRequestParams(
                    name=capability_name,
                    arguments=parameters
                )
            )
            
            # Execute tool via MCP session
            mcp_result = await self.mcp_session.call_tool(
                name=capability_name,
                arguments=parameters
            )
            
            self.logger.info(f"MCP tool executed successfully: {capability_name}")
            self.logger.debug(f"Tool result: {mcp_result}")
            
            # Return content based on result type
            if hasattr(mcp_result, 'content') and mcp_result.content:
                # Handle multiple content items
                if isinstance(mcp_result.content, list):
                    if len(mcp_result.content) == 1:
                        content_item = mcp_result.content[0]
                        if hasattr(content_item, 'text'):
                            return {"result": content_item.text}
                        else:
                            return {"result": str(content_item)}
                    else:
                        # Multiple content items
                        results = []
                        for item in mcp_result.content:
                            if hasattr(item, 'text'):
                                results.append(item.text)
                            else:
                                results.append(str(item))
                        return {"result": results}
                else:
                    # Single content item
                    if hasattr(mcp_result.content, 'text'):
                        return {"result": mcp_result.content.text}
                    else:
                        return {"result": str(mcp_result.content)}
            else:
                # No content, return the raw result
                return {"result": str(mcp_result)}
                
        except Exception as e:
            self.logger.error(f"MCP tool execution failed: {capability_name} - {e}")
            raise AgentError(f"MCP tool execution failed: {e}")
    
    async def execute_capability_via_simf(
        self, 
        simf_message: SIMFMessage
    ) -> SIMFMessage:
        """
        Execute a capability via SIMF message, with MCP tool execution support.
        
        This overrides the base implementation to add MCP-specific handling
        while maintaining SIMF-first design.
        
        Args:
            simf_message: SIMF invocation message
            
        Returns:
            SIMF result message
        """
        # Handle MCP tool invocations specially
        if (simf_message.message_type == MessageType.TOOL_INVOCATION and
            hasattr(simf_message.payload, 'capability_name')):
            
            capability_name = simf_message.payload.capability_name
            
            # Check if this is an MCP tool
            if capability_name in self.available_tools:
                try:
                    # Execute MCP tool
                    result = await self._execute_mcp_tool(
                        capability_name=capability_name,
                        parameters=simf_message.payload.parameters or {},
                        source_message=simf_message
                    )
                    
                    # Create successful SIMF result message
                    return create_invocation_result_message(
                        target_agent_id=simf_message.source_agent_id or "unknown",
                        invocation_id=simf_message.payload.invocation_id,
                        result=result,
                        status=InvocationStatus.SUCCESS,
                        session_id=simf_message.session_id
                    )
                    
                except Exception as e:
                    # Create error SIMF result message
                    return create_invocation_result_message(
                        target_agent_id=simf_message.source_agent_id or "unknown",
                        invocation_id=simf_message.payload.invocation_id,
                        result={"error": str(e)},
                        status=InvocationStatus.FAILED,
                        session_id=simf_message.session_id
                    )
        
        # For non-MCP capabilities, use base implementation
        return await super().execute_capability_via_simf(simf_message)
    
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
            **{k: v for k, v in config.items() if k not in [
                "agent_id", "name", "mcp_server_command", "session_id", "capabilities"
            ]}
        )
        
    except Exception as e:
        raise AgentConfigurationError(f"Failed to create MCPAgent from config: {e}") 