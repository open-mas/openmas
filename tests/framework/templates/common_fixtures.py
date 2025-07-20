"""
Common Test Fixtures for OpenMAS Testing

This module provides real protocol message data and common fixtures
to prevent AI hallucination in tests. All fixtures use actual protocol
specifications and real message formats.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

import pytest

from openmas.core.simf import (
    AssetType,
    InvocationStatus,
    MessageFlowDirection,
    MessageType,
    SIMFMessage,
    create_asset_reference_message,
    create_invocation_message,
    create_invocation_result_message,
    create_text_message,
)

# ============================================================================
# Real MCP Protocol Messages (Based on 2025-06-18 Specification)
# ============================================================================


@pytest.fixture
def real_mcp_messages() -> Dict[str, Dict[str, Any]]:
    """
    Real MCP protocol messages based on the official 2025-06-18 specification.
    These prevent hallucination by using actual MCP JSON-RPC 2.0 formats.
    """
    return {
        "initialize_request": {
            "jsonrpc": "2.0",
            "id": "init-001",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True},
                    "prompts": {"listChanged": True},
                    "sampling": {},
                },
                "clientInfo": {"name": "OpenMAS-MCP-Client", "version": "0.3.0"},
            },
        },
        "initialize_response": {
            "jsonrpc": "2.0",
            "id": "init-001",
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True},
                    "prompts": {"listChanged": True},
                    "elicitation": {},
                    "sampling": {},
                },
                "serverInfo": {"name": "OpenMAS-Test-Server", "version": "1.0.0"},
                "instructions": "This is a test MCP server for OpenMAS protocol adapter validation.",
            },
        },
        "tools_list_request": {
            "jsonrpc": "2.0",
            "id": "tools-001",
            "method": "tools/list",
        },
        "tools_list_response": {
            "jsonrpc": "2.0",
            "id": "tools-001",
            "result": {
                "tools": [
                    {
                        "name": "search_database",
                        "description": "Search the customer database for records",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query",
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of results",
                                    "default": 10,
                                },
                            },
                            "required": ["query"],
                        },
                    },
                    {
                        "name": "calculate",
                        "description": "Perform mathematical calculations",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "expression": {
                                    "type": "string",
                                    "description": "Mathematical expression to evaluate",
                                }
                            },
                            "required": ["expression"],
                        },
                    },
                ]
            },
        },
        "tool_call_request": {
            "jsonrpc": "2.0",
            "id": "call-001",
            "method": "tools/call",
            "params": {
                "name": "search_database",
                "arguments": {"query": "customer feedback on product XYZ", "limit": 5},
            },
        },
        "tool_call_response": {
            "jsonrpc": "2.0",
            "id": "call-001",
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Found 3 customer feedback records for product XYZ",
                    }
                ],
                "isError": False,
            },
        },
        "resources_list_request": {
            "jsonrpc": "2.0",
            "id": "resources-001",
            "method": "resources/list",
        },
        "resources_list_response": {
            "jsonrpc": "2.0",
            "id": "resources-001",
            "result": {
                "resources": [
                    {
                        "uri": "file:///customer_data.csv",
                        "name": "Customer Data",
                        "description": "Customer database in CSV format",
                        "mimeType": "text/csv",
                    },
                    {
                        "uri": "database://prod/analytics",
                        "name": "Analytics Database",
                        "description": "Production analytics database",
                        "mimeType": "application/x-database",
                    },
                ]
            },
        },
        "error_response": {
            "jsonrpc": "2.0",
            "id": "call-001",
            "error": {
                "code": -32601,
                "message": "Method not found",
                "data": {"method": "tools/unknown"},
            },
        },
    }


@pytest.fixture
def real_a2a_messages() -> Dict[str, Dict[str, Any]]:
    """
    Real A2A protocol messages based on the specification.
    These use actual A2A multi-part message formats.
    """
    return {
        "capability_request": {
            "id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "sender": "agent-001",
            "recipient": "agent-002",
            "conversation_id": "conv-123",
            "parts": [
                {
                    "content_type": "application/json",
                    "content": {
                        "capability": "text_analysis",
                        "parameters": {
                            "text": "Please analyze the sentiment of this customer review",
                            "analysis_type": "sentiment",
                        },
                    },
                }
            ],
        },
        "capability_response": {
            "id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "sender": "agent-002",
            "recipient": "agent-001",
            "conversation_id": "conv-123",
            "parts": [
                {
                    "content_type": "application/json",
                    "content": {
                        "status": "success",
                        "result": {
                            "sentiment": "positive",
                            "confidence": 0.89,
                            "key_phrases": ["excellent product", "highly recommend"],
                        },
                    },
                }
            ],
        },
        "multipart_message": {
            "id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "sender": "agent-001",
            "recipient": "agent-002",
            "conversation_id": "conv-456",
            "parts": [
                {
                    "content_type": "text/plain",
                    "content": "Please analyze this image for product defects",
                },
                {
                    "content_type": "image/jpeg",
                    "file_id": "img_001.jpg",
                    "content": "base64_encoded_image_data",
                },
                {
                    "content_type": "application/json",
                    "content": {
                        "analysis_parameters": {
                            "defect_types": ["scratches", "dents", "discoloration"],
                            "confidence_threshold": 0.8,
                        }
                    },
                },
            ],
        },
    }


@pytest.fixture
def real_http_messages() -> Dict[str, Dict[str, Any]]:
    """
    Real HTTP protocol messages with proper headers and status codes.
    """
    return {
        "get_request": {
            "method": "GET",
            "url": "/api/v1/agents/agent-001/status",
            "headers": {
                "Accept": "application/json",
                "User-Agent": "OpenMAS/0.3.0",
                "Authorization": "Bearer jwt_token_here",
            },
            "params": {"include_details": "true"},
        },
        "get_response": {
            "status_code": 200,
            "headers": {
                "Content-Type": "application/json",
                "Content-Length": "156",
                "Server": "OpenMAS-HTTP-Server/1.0",
            },
            "body": {
                "agent_id": "agent-001",
                "status": "active",
                "uptime": 3600,
                "capabilities": ["text_processing", "data_analysis"],
            },
        },
        "post_request": {
            "method": "POST",
            "url": "/api/v1/agents/agent-001/invoke",
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer jwt_token_here",
            },
            "body": {
                "capability": "text_analysis",
                "parameters": {
                    "text": "Sample text for analysis",
                    "analysis_type": "sentiment",
                },
            },
        },
        "post_response": {
            "status_code": 200,
            "headers": {
                "Content-Type": "application/json",
                "Location": "/api/v1/tasks/task-456",
            },
            "body": {
                "task_id": "task-456",
                "status": "completed",
                "result": {"sentiment": "neutral", "confidence": 0.75},
            },
        },
        "error_response": {
            "status_code": 400,
            "headers": {"Content-Type": "application/json"},
            "body": {
                "error": {
                    "code": "INVALID_PARAMETERS",
                    "message": "Missing required parameter: capability",
                    "details": {"missing_fields": ["capability"]},
                }
            },
        },
    }


# ============================================================================
# SIMF Message Fixtures
# ============================================================================


@pytest.fixture
def simf_message_fixtures() -> Dict[str, SIMFMessage]:
    """
    Collection of valid SIMF messages for testing protocol adapters.
    """
    return {
        "text_message": create_text_message(
            text="Hello, this is a test message",
            target_agent_id="test-agent",
            session_id="session-123",
        ),
        "tool_invocation": create_invocation_message(
            invocation_name="search_database",
            arguments={"query": "customer feedback", "limit": 10},
            target_agent_id="test-agent",
            message_type=MessageType.TOOL_INVOCATION,
        ),
        "tool_result": create_invocation_result_message(
            invocation_name="search_database",
            status=InvocationStatus.SUCCESS,
            result={
                "records": [{"id": "fb-001", "content": "Great product!", "rating": 5}],
                "total_count": 1,
            },
            target_agent_id="client-agent",
        ),
        "asset_reference": create_asset_reference_message(
            asset_id="image-001.jpg",
            asset_type=AssetType.IMAGE,
            target_agent_id="test-agent",
            mime_type="image/jpeg",
            resource_metadata={
                "size": 1024768,
                "dimensions": {"width": 1920, "height": 1080},
            },
        ),
        "error_message": create_invocation_result_message(
            invocation_name="search_database",
            status=InvocationStatus.FAILURE,
            target_agent_id="client-agent",
            error={
                "code": "DATABASE_ERROR",
                "message": "Connection to database failed",
                "details": {"timeout": 30},
            },
        ),
    }


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def create_test_protocol_config():
    """Factory for creating test protocol configurations."""

    def _create_config(protocol_type: str, **options) -> Dict[str, Any]:
        return {
            "protocol_type": protocol_type,
            "enabled": True,
            "options": {"timeout": 30, "retry_attempts": 3, **options},
            "security": {"authentication_required": False, "tls_enabled": False},
        }

    return _create_config


@pytest.fixture
def create_test_agent_config():
    """Factory for creating test agent configurations."""

    def _create_config(agent_id: str, **options) -> Dict[str, Any]:
        return {
            "agent_id": agent_id,
            "name": f"Test Agent {agent_id}",
            "capabilities": ["text_processing", "data_analysis"],
            "protocols": ["mcp", "a2a", "http"],
            **options,
        }

    return _create_config


# ============================================================================
# Test Data Validation Utilities
# ============================================================================


def validate_real_mcp_message(message: Dict[str, Any]) -> bool:
    """
    Validate that a message conforms to real MCP JSON-RPC 2.0 format.
    This prevents tests from using hallucinated message formats.
    """
    required_fields = ["jsonrpc", "id"]

    # Check basic JSON-RPC structure
    if not all(field in message for field in required_fields):
        return False

    if message["jsonrpc"] != "2.0":
        return False

    # Must have either 'method' (request) or 'result'/'error' (response)
    is_request = "method" in message
    is_response = "result" in message or "error" in message

    return is_request or is_response


def validate_real_a2a_message(message: Dict[str, Any]) -> bool:
    """
    Validate that a message conforms to real A2A multi-part format.
    """
    required_fields = ["id", "timestamp", "sender", "recipient", "parts"]

    if not all(field in message for field in required_fields):
        return False

    # Validate parts structure
    if not isinstance(message["parts"], list) or len(message["parts"]) == 0:
        return False

    for part in message["parts"]:
        if not isinstance(part, dict) or "content_type" not in part:
            return False

    return True


def validate_real_http_message(message: Dict[str, Any]) -> bool:
    """
    Validate that a message conforms to real HTTP format.
    """
    if "method" in message:
        # HTTP request
        required_fields = ["method", "url"]
        return all(field in message for field in required_fields)
    elif "status_code" in message:
        # HTTP response
        return (
            isinstance(message["status_code"], int)
            and 100 <= message["status_code"] < 600
        )

    return False
