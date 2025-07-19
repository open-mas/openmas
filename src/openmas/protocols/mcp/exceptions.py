"""
MCP Protocol Exceptions

Defines MCP-specific exceptions for error handling in the protocol adapter.
"""


class MCPError(Exception):
    """Base exception for MCP protocol errors."""
    pass


class MCPConnectionError(MCPError):
    """Exception raised for MCP connection-related errors."""
    pass


class MCPMessageError(MCPError):
    """Exception raised for MCP message processing errors."""
    pass


class MCPTranslationError(MCPError):
    """Exception raised for SIMF-MCP message translation errors."""
    pass


class MCPTimeoutError(MCPError):
    """Exception raised for MCP operation timeouts."""
    pass


class MCPServerError(MCPError):
    """Exception raised for MCP server-side errors."""
    pass


class MCPClientError(MCPError):
    """Exception raised for MCP client-side errors."""
    pass 