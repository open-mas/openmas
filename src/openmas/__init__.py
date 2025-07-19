"""
OpenMAS: A reasoning-agnostic multi-agent framework.

OpenMAS provides a flexible, protocol-independent framework for building
intelligent agents that can communicate across multiple protocols while
maintaining clean separation between communication infrastructure (the "body")
and reasoning approaches (the "brain").

Key Features:
- Reasoning agnosticism: Support for multiple reasoning approaches
- Multi-protocol support: A2A, MCP, HTTP, MQTT, gRPC protocols
- Configuration-driven design: Unified configuration schema
- Enterprise-ready: Built-in security, observability, and deployment support
"""

__version__ = "0.3.0-dev"
__author__ = "OpenMAS Contributors"

# Core exports will be added as components are implemented
__all__ = [
    "__version__",
    "__author__",
] 