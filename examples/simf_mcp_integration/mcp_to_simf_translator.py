"""
MCP to SIMF Translator

This module demonstrates how to translate between MCP protocol messages
and the Standard Internal Message Format (SIMF), preserving semantic
meaning while enabling protocol-agnostic message handling.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ImageContent,
    JSONRPCMessage,
    ListResourcesRequest,
    ListResourcesResult,
    ReadResourceRequest,
    ReadResourceResult,
    Resource,
    TextContent,
    Tool,
)

# Import SIMF models (fallback to mock for demo)
try:
    from openmas.core.simf import (
        AssetReferenceContentPayload,
        AssetType,
        InvocationContentPayload,
        InvocationResultContentPayload,
        InvocationStatus,
        MessageFlowDirection,
        MessageType,
        PayloadType,
        SIMFMessage,
        StructuredDataContentPayload,
        TextContentPayload,
        create_asset_reference_message,
        create_text_message,
        create_tool_invocation_message,
        create_tool_result_message,
    )

    SIMF_AVAILABLE = True
except ImportError:
    # Mock implementations for demo when SIMF is not available
    print("Info: Using mock SIMF implementations for demonstration")
    SIMF_AVAILABLE = False

    class MockSIMFMessage:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            # Set defaults that match real SIMF structure
            self.message_type = kwargs.get("message_type", "TOOL_INVOCATION")
            self.payload = kwargs.get("payload", MockPayload())
            self.session_id = kwargs.get("session_id")
            self.source_protocol_type = kwargs.get("source_protocol_type")
            self.metadata = kwargs.get("metadata", {})

        def model_dump(self):
            return self.__dict__

    class MockPayload:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.payload_type = kwargs.get("payload_type", "invocation_content")
            self.capability_name = kwargs.get("capability_name", "unknown")
            self.parameters = kwargs.get("parameters", {})

    # Mock SIMF classes
    SIMFMessage = MockSIMFMessage

    # Mock enums as strings
    class MessageType:
        TOOL_INVOCATION = "TOOL_INVOCATION"
        TOOL_RESULT = "TOOL_RESULT"
        PLAIN_TEXT_MESSAGE = "PLAIN_TEXT_MESSAGE"
        AGENT_RESPONSE = "AGENT_RESPONSE"

    class PayloadType:
        INVOCATION_CONTENT = "invocation_content"
        INVOCATION_RESULT_CONTENT = "invocation_result_content"
        ASSET_REFERENCE_CONTENT = "asset_reference_content"
        STREAM_CONTEXT_CONTENT = "stream_context_content"

    class MessageFlowDirection:
        INBOUND = "inbound"
        OUTBOUND = "outbound"
        INTERNAL = "internal"

    class AssetType:
        DOCUMENT = "document"
        IMAGE = "image"
        AUDIO = "audio"
        VIDEO = "video"
        DATA = "data"

    class InvocationStatus:
        SUCCESS = "success"
        FAILURE = "failure"
        PENDING = "pending"

    # Mock payload classes
    InvocationContentPayload = lambda **kwargs: MockPayload(
        payload_type="invocation_content", **kwargs
    )
    InvocationResultContentPayload = lambda **kwargs: MockPayload(
        payload_type="invocation_result_content", **kwargs
    )
    AssetReferenceContentPayload = lambda **kwargs: MockPayload(
        payload_type="asset_reference_content", **kwargs
    )
    TextContentPayload = lambda **kwargs: MockPayload(
        payload_type="text_content", **kwargs
    )


class MCPToSIMFTranslator:
    """
    Handles bidirectional translation between MCP protocol messages and SIMF.

    This translator demonstrates how to preserve semantic meaning while
    converting between protocol-specific formats and the internal SIMF format.
    """

    def __init__(self, agent_id: str = "mcp_agent"):
        """
        Initialize the translator.

        Args:
            agent_id: Identifier for the agent handling MCP messages
        """
        self.agent_id = agent_id

    # ========================================================================
    # MCP Tool Calls → SIMF Translation
    # ========================================================================

    def mcp_tool_call_to_simf(
        self, mcp_request: CallToolRequest, session_id: Optional[str] = None
    ) -> SIMFMessage:
        """
        Convert MCP tool call request to SIMF invocation message.

        Args:
            mcp_request: MCP tool call request
            session_id: Optional session identifier

        Returns:
            SIMF message with invocation content
        """
        # Extract tool information from MCP request
        tool_name = mcp_request.params.name
        tool_arguments = mcp_request.params.arguments or {}

        # Create SIMF invocation payload
        invocation_payload = InvocationContentPayload(
            capability_name=tool_name,
            parameters=tool_arguments,
            invocation_id=str(mcp_request.id) if mcp_request.id else str(uuid4()),
            expected_output_format="structured",  # MCP tools return structured data
        )

        # Create SIMF message
        simf_message = SIMFMessage(
            target_agent_id=self.agent_id,
            message_flow_direction=MessageFlowDirection.INBOUND,
            message_type=MessageType.TOOL_INVOCATION,
            payload=invocation_payload,
            session_id=session_id,
            source_protocol_type="mcp",
            metadata={
                "mcp_request_id": str(mcp_request.id) if mcp_request.id else None,
                "mcp_method": "tools/call",
                "original_mcp_params": tool_arguments,
            },
        )

        return simf_message

    def simf_to_mcp_tool_call(self, simf_message: SIMFMessage) -> CallToolRequest:
        """
        Convert SIMF invocation message back to MCP tool call request.

        Args:
            simf_message: SIMF message with invocation content

        Returns:
            MCP tool call request
        """
        # Check payload type (compatible with both real and mock SIMF)
        if (
            SIMF_AVAILABLE
            and not isinstance(simf_message.payload, InvocationContentPayload)
        ) or (
            not SIMF_AVAILABLE
            and getattr(simf_message.payload, "payload_type", None)
            != "invocation_content"
        ):
            raise ValueError("SIMF message must have invocation content payload")

        payload = simf_message.payload

        # Extract original MCP request ID if available
        request_id = None
        if simf_message.metadata and "mcp_request_id" in simf_message.metadata:
            request_id = simf_message.metadata["mcp_request_id"]

        # Create MCP tool call request with proper structure
        from mcp.types import CallToolRequestParams

        mcp_request = CallToolRequest(
            id=request_id,
            method="tools/call",
            params=CallToolRequestParams(
                name=payload.capability_name, arguments=payload.parameters
            ),
        )

        return mcp_request

    # ========================================================================
    # MCP Tool Results → SIMF Translation
    # ========================================================================

    def mcp_tool_result_to_simf(
        self,
        mcp_result: CallToolResult,
        original_request_id: str,
        session_id: Optional[str] = None,
    ) -> SIMFMessage:
        """
        Convert MCP tool call result to SIMF invocation result message.

        Args:
            mcp_result: MCP tool call result
            original_request_id: ID from the original invocation
            session_id: Optional session identifier

        Returns:
            SIMF message with invocation result content
        """
        # Process MCP result content
        result_data = {}
        text_content = []

        for content_item in mcp_result.content:
            if isinstance(content_item, TextContent):
                text_content.append(content_item.text)
            elif hasattr(content_item, "data"):  # Structured content
                result_data.update(content_item.data)

        # Determine success/failure status
        is_error = hasattr(mcp_result, "isError") and mcp_result.isError
        status = InvocationStatus.FAILURE if is_error else InvocationStatus.SUCCESS

        # Create SIMF invocation result payload
        result_payload = InvocationResultContentPayload(
            invocation_id=original_request_id,
            status=status,
            result_data=(
                result_data if result_data else {"text": " ".join(text_content)}
            ),
            error_message=(
                mcp_result.content[0].text if is_error and mcp_result.content else None
            ),
        )

        # Create SIMF message
        simf_message = SIMFMessage(
            target_agent_id=self.agent_id,
            message_flow_direction=MessageFlowDirection.OUTBOUND,
            message_type=MessageType.TOOL_RESULT,
            payload=result_payload,
            session_id=session_id,
            source_protocol_type="mcp",
            metadata={
                "mcp_content_types": [type(c).__name__ for c in mcp_result.content],
                "mcp_result_success": not is_error,
            },
        )

        return simf_message

    def simf_to_mcp_tool_result(self, simf_message: SIMFMessage) -> CallToolResult:
        """
        Convert SIMF invocation result message back to MCP tool call result.

        Args:
            simf_message: SIMF message with invocation result content

        Returns:
            MCP tool call result
        """
        # Check payload type (compatible with both real and mock SIMF)
        if (
            SIMF_AVAILABLE
            and not isinstance(simf_message.payload, InvocationResultContentPayload)
        ) or (
            not SIMF_AVAILABLE
            and getattr(simf_message.payload, "payload_type", None)
            != "invocation_result_content"
        ):
            raise ValueError("SIMF message must have invocation result content payload")

        payload = simf_message.payload

        # Create content based on result data
        content = []

        if payload.status == InvocationStatus.FAILURE and payload.error_message:
            # Error result
            content.append(TextContent(type="text", text=payload.error_message))
        else:
            # Success result - convert result_data to appropriate content
            if isinstance(payload.result_data, dict):
                # Try to create structured content, fall back to text
                if "text" in payload.result_data:
                    content.append(
                        TextContent(type="text", text=payload.result_data["text"])
                    )
                else:
                    # Convert dict to JSON text
                    content.append(
                        TextContent(
                            type="text", text=json.dumps(payload.result_data, indent=2)
                        )
                    )
            else:
                # Convert any other type to string
                content.append(TextContent(type="text", text=str(payload.result_data)))

        # Create MCP result
        mcp_result = CallToolResult(
            content=content, isError=(payload.status == InvocationStatus.FAILURE)
        )

        return mcp_result

    # ========================================================================
    # MCP Resources → SIMF Asset References
    # ========================================================================

    def mcp_resource_to_simf(
        self,
        mcp_resource: Resource,
        resource_content: str,
        session_id: Optional[str] = None,
    ) -> SIMFMessage:
        """
        Convert MCP resource to SIMF asset reference message.

        Args:
            mcp_resource: MCP resource metadata
            resource_content: The actual content of the resource
            session_id: Optional session identifier

        Returns:
            SIMF message with asset reference content
        """
        # Determine asset type from MCP resource
        asset_type = AssetType.DOCUMENT  # Default
        if mcp_resource.mimeType:
            if mcp_resource.mimeType.startswith("image/"):
                asset_type = AssetType.IMAGE
            elif mcp_resource.mimeType.startswith("audio/"):
                asset_type = AssetType.AUDIO
            elif mcp_resource.mimeType.startswith("video/"):
                asset_type = AssetType.VIDEO
            elif "json" in mcp_resource.mimeType:
                asset_type = AssetType.DATA

        # Create SIMF asset reference payload
        asset_payload = AssetReferenceContentPayload(
            asset_id=mcp_resource.uri,
            asset_type=asset_type,
            asset_url=mcp_resource.uri,
            content_preview=(
                resource_content[:200] + "..."
                if len(resource_content) > 200
                else resource_content
            ),
            mime_type=mcp_resource.mimeType,
            metadata={
                "mcp_resource_name": mcp_resource.name,
                "mcp_resource_description": mcp_resource.description,
                "mcp_content_length": len(resource_content),
            },
        )

        # Create SIMF message
        simf_message = SIMFMessage(
            target_agent_id=self.agent_id,
            message_flow_direction=MessageFlowDirection.INBOUND,
            message_type=MessageType.PLAIN_TEXT_MESSAGE,  # Resource access is informational
            payload=asset_payload,
            session_id=session_id,
            source_protocol_type="mcp",
            metadata={
                "mcp_resource_uri": mcp_resource.uri,
                "mcp_resource_name": mcp_resource.name,
            },
        )

        return simf_message

    # ========================================================================
    # Streaming Support
    # ========================================================================

    def create_stream_context_message(
        self,
        stream_id: str,
        position: str,
        partial_content: str,
        session_id: Optional[str] = None,
    ) -> SIMFMessage:
        """
        Create SIMF stream context message for MCP streaming scenarios.

        Args:
            stream_id: Unique identifier for the stream
            position: Position in stream (start, middle, end, complete)
            partial_content: The partial content for this stream message
            session_id: Optional session identifier

        Returns:
            SIMF message with stream context content
        """
        from openmas.core.simf import StreamContextContentPayload, StreamPosition

        # Create stream context payload
        stream_payload = StreamContextContentPayload(
            stream_id=stream_id,
            position=StreamPosition(position),
            partial_content=TextContentPayload(
                text=partial_content, language="en", encoding="utf-8"
            ),
        )

        # Create SIMF message
        simf_message = SIMFMessage(
            target_agent_id=self.agent_id,
            message_flow_direction=MessageFlowDirection.OUTBOUND,
            message_type=MessageType.AGENT_RESPONSE,
            payload=stream_payload,
            session_id=session_id,
            source_protocol_type="mcp",
            metadata={"stream_id": stream_id, "stream_position": position},
        )

        return simf_message


# ============================================================================
# Utility Functions
# ============================================================================


def demonstrate_mcp_simf_roundtrip():
    """
    Demonstrate a complete roundtrip: MCP → SIMF → MCP with semantic preservation.
    """
    translator = MCPToSIMFTranslator("demo_agent")

    # 1. Create sample MCP tool call with proper structure
    from mcp.types import CallToolRequestParams

    mcp_request = CallToolRequest(
        id="test_123",
        method="tools/call",
        params=CallToolRequestParams(
            name="analyze_text",
            arguments={
                "text": "This is a great example!",
                "analysis_type": "sentiment",
            },
        ),
    )

    print("=== Original MCP Tool Call ===")
    print(f"Tool: {mcp_request.params.name}")
    print(f"Arguments: {mcp_request.params.arguments}")
    print()

    # 2. Convert to SIMF
    simf_message = translator.mcp_tool_call_to_simf(mcp_request, "demo_session")
    print("=== SIMF Message ===")
    print(f"Message Type: {simf_message.message_type}")
    print(f"Payload Type: {simf_message.payload.payload_type}")
    print(f"Capability: {simf_message.payload.capability_name}")
    print(f"Parameters: {simf_message.payload.parameters}")
    print()

    # 3. Convert back to MCP
    reconstructed_mcp = translator.simf_to_mcp_tool_call(simf_message)
    print("=== Reconstructed MCP Tool Call ===")
    print(f"Tool: {reconstructed_mcp.params.name}")
    print(f"Arguments: {reconstructed_mcp.params.arguments}")
    print()

    # 4. Verify semantic preservation
    original_tool = mcp_request.params.name
    original_args = mcp_request.params.arguments
    reconstructed_tool = reconstructed_mcp.params.name
    reconstructed_args = reconstructed_mcp.params.arguments

    print("=== Semantic Preservation Check ===")
    print(f"Tool name preserved: {original_tool == reconstructed_tool}")
    print(f"Arguments preserved: {original_args == reconstructed_args}")

    return original_tool == reconstructed_tool and original_args == reconstructed_args


if __name__ == "__main__":
    demonstrate_mcp_simf_roundtrip()
