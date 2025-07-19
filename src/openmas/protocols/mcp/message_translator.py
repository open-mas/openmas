"""
SIMF-MCP Message Translator

Provides bidirectional translation between SIMF (Standard Internal Message Format)
and MCP protocol messages, preserving semantic information during translation.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from openmas.core.simf import (
    SIMFMessage, 
    MessageType, 
    PayloadType,
    MessageFlowDirection,
    AssetType,
    InvocationStatus,
    create_text_message,
    create_structured_data_message,
    create_invocation_message,
    create_invocation_result_message,
    create_error_message,
)

from .exceptions import MCPTranslationError


class MCPMessageTranslator:
    """
    Handles bidirectional translation between SIMF and MCP messages.
    
    This translator preserves semantic information during translation and
    maps MCP message types to appropriate SIMF payload types.
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize the translator.
        
        Args:
            agent_id: The agent ID for this translator
        """
        self.agent_id = agent_id
    
    def to_internal_format(self, mcp_message: Dict[str, Any]) -> SIMFMessage:
        """
        Convert MCP message to SIMF format.
        
        Args:
            mcp_message: MCP protocol message
            
        Returns:
            SIMFMessage: SIMF representation of the message
            
        Raises:
            MCPTranslationError: If translation fails
        """
        try:
            # Extract MCP message components
            method = mcp_message.get("method", "")
            params = mcp_message.get("params", {})
            message_id = mcp_message.get("id", str(uuid4()))
            
            # Determine SIMF message type based on MCP method
            if method.startswith("tools/call"):
                return self._translate_tool_call(mcp_message, message_id, params)
            elif method.startswith("tools/list"):
                return self._translate_tool_list(mcp_message, message_id, params)
            elif method.startswith("resources/read"):
                return self._translate_resource_read(mcp_message, message_id, params)
            elif method.startswith("resources/list"):
                return self._translate_resource_list(mcp_message, message_id, params)
            elif method.startswith("prompts/get"):
                return self._translate_prompt_get(mcp_message, message_id, params)
            elif method.startswith("prompts/list"):
                return self._translate_prompt_list(mcp_message, message_id, params)
            elif "result" in mcp_message:
                return self._translate_result(mcp_message, message_id)
            elif "error" in mcp_message:
                return self._translate_error(mcp_message, message_id)
            else:
                # Generic message - treat as text content
                return self._translate_generic_message(mcp_message, message_id)
                
        except Exception as e:
            raise MCPTranslationError(f"Failed to translate MCP message to SIMF: {e}") from e
    
    def from_internal_format(self, simf_message: SIMFMessage) -> Dict[str, Any]:
        """
        Convert SIMF message to MCP format.
        
        Args:
            simf_message: SIMF message to convert
            
        Returns:
            Dict[str, Any]: MCP protocol message
            
        Raises:
            MCPTranslationError: If translation fails
        """
        try:
            payload = simf_message.payload
            
            # Route based on SIMF message type and payload type
            if simf_message.message_type == MessageType.TOOL_INVOCATION:
                return self._simf_to_tool_call(simf_message)
            elif simf_message.message_type == MessageType.TOOL_RESULT:
                return self._simf_to_tool_result(simf_message)
            elif simf_message.message_type == MessageType.CAPABILITY_INVOCATION:
                return self._simf_to_resource_or_prompt_request(simf_message)
            elif simf_message.message_type == MessageType.CAPABILITY_RESULT:
                return self._simf_to_resource_or_prompt_response(simf_message)
            elif simf_message.message_type == MessageType.ERROR_MESSAGE:
                return self._simf_to_error(simf_message)
            else:
                # Generic text message
                return self._simf_to_generic_message(simf_message)
                
        except Exception as e:
            raise MCPTranslationError(f"Failed to translate SIMF message to MCP: {e}") from e
    
    # MCP -> SIMF translation methods
    
    def _translate_tool_call(self, mcp_message: Dict[str, Any], message_id: str, params: Dict[str, Any]) -> SIMFMessage:
        """Translate MCP tool call to SIMF invocation message."""
        tool_name = params.get("name", "unknown_tool")
        arguments = params.get("arguments", {})
        
        simf_msg = create_invocation_message(
            invocation_name=tool_name,
            arguments=arguments,
            target_agent_id=self.agent_id,
            message_type=MessageType.TOOL_INVOCATION,
            metadata={
                "mcp_method": mcp_message.get("method"),
                "original_mcp_message": mcp_message
            }
        )
        simf_msg.message_id = message_id
        return simf_msg
    
    def _translate_tool_list(self, mcp_message: Dict[str, Any], message_id: str, params: Dict[str, Any]) -> SIMFMessage:
        """Translate MCP tool list request to SIMF invocation message."""
        return create_invocation_message(
            invocation_name="list_tools",
            arguments=params,
            target_agent_id=self.agent_id,
            message_id=message_id,
            message_type=MessageType.CAPABILITY_INVOCATION,
            metadata={
                "mcp_method": mcp_message.get("method"),
                "original_mcp_message": mcp_message
            }
        )
    
    def _translate_resource_read(self, mcp_message: Dict[str, Any], message_id: str, params: Dict[str, Any]) -> SIMFMessage:
        """Translate MCP resource read to SIMF resource request."""
        uri = params.get("uri", "")
        
        return create_invocation_message(
            invocation_name="read_resource",
            arguments={"uri": uri, **params},
            target_agent_id=self.agent_id,
            message_type=MessageType.CAPABILITY_INVOCATION,
            metadata={
                "mcp_method": mcp_message.get("method"),
                "resource_uri": uri,
                "original_mcp_message": mcp_message
            }
        )
    
    def _translate_resource_list(self, mcp_message: Dict[str, Any], message_id: str, params: Dict[str, Any]) -> SIMFMessage:
        """Translate MCP resource list to SIMF invocation message."""
        return create_invocation_message(
            invocation_name="list_resources",
            arguments=params,
            target_agent_id=self.agent_id,
            message_type=MessageType.CAPABILITY_INVOCATION,
            metadata={
                "mcp_method": mcp_message.get("method"),
                "original_mcp_message": mcp_message
            }
        )
    
    def _translate_prompt_get(self, mcp_message: Dict[str, Any], message_id: str, params: Dict[str, Any]) -> SIMFMessage:
        """Translate MCP prompt get to SIMF prompt request."""
        prompt_name = params.get("name", "unknown_prompt")
        
        return create_invocation_message(
            invocation_name="get_prompt",
            arguments={"name": prompt_name, **params},
            target_agent_id=self.agent_id,
            message_type=MessageType.CAPABILITY_INVOCATION,
            metadata={
                "mcp_method": mcp_message.get("method"),
                "prompt_name": prompt_name,
                "original_mcp_message": mcp_message
            }
        )
    
    def _translate_prompt_list(self, mcp_message: Dict[str, Any], message_id: str, params: Dict[str, Any]) -> SIMFMessage:
        """Translate MCP prompt list to SIMF invocation message."""
        return create_invocation_message(
            invocation_name="list_prompts",
            arguments=params,
            target_agent_id=self.agent_id,
            message_type=MessageType.CAPABILITY_INVOCATION,
            metadata={
                "mcp_method": mcp_message.get("method"),
                "original_mcp_message": mcp_message
            }
        )
    
    def _translate_result(self, mcp_message: Dict[str, Any], message_id: str) -> SIMFMessage:
        """Translate MCP result message to SIMF result."""
        result_data = mcp_message.get("result", {})
        
        return create_invocation_result_message(
            invocation_name="mcp_result",
            status=InvocationStatus.SUCCESS,
            result=result_data,
            target_agent_id=self.agent_id,
            message_id=message_id,
            metadata={
                "original_mcp_message": mcp_message
            }
        )
    
    def _translate_error(self, mcp_message: Dict[str, Any], message_id: str) -> SIMFMessage:
        """Translate MCP error message to SIMF error."""
        error_data = mcp_message.get("error", {})
        
        return create_error_message(
            error_code=str(error_data.get("code", "UNKNOWN")),
            error_message=error_data.get("message", "Unknown error"),
            target_agent_id=self.agent_id,
            message_id=message_id,
            error_details=error_data,
            metadata={
                "original_mcp_message": mcp_message
            }
        )
    
    def _translate_generic_message(self, mcp_message: Dict[str, Any], message_id: str) -> SIMFMessage:
        """Translate generic MCP message to SIMF text message."""
        # Convert entire MCP message to text for generic handling
        content = json.dumps(mcp_message, indent=2)
        
        return create_text_message(
            text=content,
            target_agent_id=self.agent_id,
            message_id=message_id,
            metadata={
                "message_type": "generic_mcp_message",
                "original_mcp_message": mcp_message
            }
        )
    
    # SIMF -> MCP translation methods
    
    def _simf_to_tool_call(self, simf_message: SIMFMessage) -> Dict[str, Any]:
        """Convert SIMF tool invocation to MCP tool call."""
        payload = simf_message.payload
        
        return {
            "jsonrpc": "2.0",
            "id": simf_message.message_id,
            "method": "tools/call",
            "params": {
                "name": payload.invocation_name,
                "arguments": payload.arguments or {}
            }
        }
    
    def _simf_to_tool_result(self, simf_message: SIMFMessage) -> Dict[str, Any]:
        """Convert SIMF tool result to MCP result."""
        payload = simf_message.payload
        
        if payload.status == InvocationStatus.SUCCESS:
            return {
                "jsonrpc": "2.0",
                "id": simf_message.message_id,
                "result": payload.result
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": simf_message.message_id,
                "error": {
                    "code": -1,
                    "message": payload.error.get("message", "Tool execution failed") if payload.error else "Unknown error",
                    "data": payload.error
                }
            }
    
    def _simf_to_resource_or_prompt_request(self, simf_message: SIMFMessage) -> Dict[str, Any]:
        """Convert SIMF capability invocation to MCP resource or prompt call."""
        payload = simf_message.payload
        arguments = payload.arguments or {}
        
        if payload.invocation_name == "read_resource":
            return {
                "jsonrpc": "2.0",
                "id": simf_message.message_id,
                "method": "resources/read",
                "params": {
                    "uri": arguments.get("uri", "")
                }
            }
        elif payload.invocation_name == "list_resources":
            return {
                "jsonrpc": "2.0",
                "id": simf_message.message_id,
                "method": "resources/list",
                "params": arguments
            }
        elif payload.invocation_name == "get_prompt":
            return {
                "jsonrpc": "2.0",
                "id": simf_message.message_id,
                "method": "prompts/get",
                "params": {
                    "name": arguments.get("name", ""),
                    "arguments": arguments.get("arguments", {})
                }
            }
        elif payload.invocation_name == "list_prompts":
            return {
                "jsonrpc": "2.0",
                "id": simf_message.message_id,
                "method": "prompts/list",
                "params": arguments
            }
        else:
            # Generic resource request
            return {
                "jsonrpc": "2.0",
                "id": simf_message.message_id,
                "method": "resources/read",
                "params": arguments
            }
    
    def _simf_to_resource_or_prompt_response(self, simf_message: SIMFMessage) -> Dict[str, Any]:
        """Convert SIMF capability result to MCP result."""
        payload = simf_message.payload
        
        return {
            "jsonrpc": "2.0",
            "id": simf_message.message_id,
            "result": payload.result if hasattr(payload, 'result') else payload.data
        }
    
    def _simf_to_error(self, simf_message: SIMFMessage) -> Dict[str, Any]:
        """Convert SIMF error to MCP error."""
        payload = simf_message.payload
        
        return {
            "jsonrpc": "2.0",
            "id": simf_message.message_id,
            "error": {
                "code": -1,
                "message": payload.error_message,
                "data": payload.error_details
            }
        }
    
    def _simf_to_generic_message(self, simf_message: SIMFMessage) -> Dict[str, Any]:
        """Convert generic SIMF message to MCP message."""
        payload = simf_message.payload
        
        # For text messages, create a notification
        if hasattr(payload, 'text'):
            return {
                "jsonrpc": "2.0",
                "method": "notifications/message",
                "params": {
                    "type": "text",
                    "content": payload.text
                }
            }
        else:
            # For structured data, include the data directly
            return {
                "jsonrpc": "2.0",
                "method": "notifications/message",
                "params": {
                    "type": "data",
                    "content": payload.data if hasattr(payload, 'data') else str(payload)
                }
            } 