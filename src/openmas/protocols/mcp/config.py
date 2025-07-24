"""
MCP Protocol Configuration Models

Defines MCP-specific configuration classes that extend the base ProtocolConfig
with MCP transport options and settings.
"""

from enum import Enum

from pydantic import BaseModel, Field


class MCPTransportType(str, Enum):
    """MCP transport mechanisms."""

    STDIO = "stdio"
    # Note: SSE transport was deprecated in MCP SDK 1.8+ and is not supported
    # in OpenMAS 0.3.0


class MCPStdioConfig(BaseModel):
    """Configuration for MCP stdio transport."""

    command: str = Field(..., description="Command to execute MCP server")
    args: list[str] = Field(default_factory=list, description="Arguments for the command")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    cwd: str | None = Field(default=None, description="Working directory")


# Note: MCPSSEConfig removed - SSE transport deprecated in MCP SDK 1.8+ and not
# supported in OpenMAS 0.3.0


class MCPConfig(BaseModel):
    """MCP-specific protocol configuration."""

    protocol_type: str = Field(default="mcp", description="Protocol type identifier")
    enabled: bool = Field(default=True, description="Whether MCP is enabled")
    transport: MCPTransportType = Field(..., description="MCP transport type")

    # Transport-specific configurations
    stdio_config: MCPStdioConfig | None = Field(default=None, description="Stdio transport configuration")
    # Note: sse_config removed - SSE transport deprecated in MCP SDK 1.8+

    # MCP-specific options
    server_mode: bool = Field(default=False, description="Whether to run in server mode")
    server_name: str = Field(default="OpenMAS Agent", description="MCP server name")
    server_version: str = Field(default="1.0.0", description="MCP server version")

    # General options
    timeout_seconds: float = Field(default=30.0, description="Operation timeout in seconds")
    enable_structured_output: bool = Field(default=True, description="Enable structured output support")
    enable_oauth: bool = Field(default=False, description="Enable OAuth support")
    enable_elicitation: bool = Field(default=False, description="Enable elicitation support")

    def validate_transport_config(self) -> None:
        """Validate that the appropriate transport config is provided."""
        if self.transport == MCPTransportType.STDIO and not self.stdio_config:
            raise ValueError("stdio_config is required when transport is 'stdio'")
        # Note: SSE transport validation removed - deprecated in MCP SDK 1.8+
