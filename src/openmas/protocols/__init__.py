"""
OpenMAS Protocol Adapters

This module provides protocol adapter implementations for various communication
protocols, enabling OpenMAS agents to communicate across different transports
while maintaining consistency through SIMF translation.
"""

from .mcp import MCPProtocolAdapter, MCPConfig, MCPTransportType

__all__ = [
    "MCPProtocolAdapter",
    "MCPConfig", 
    "MCPTransportType",
]
