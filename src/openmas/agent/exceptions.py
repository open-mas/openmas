"""
OpenMAS Agent Framework Exceptions

This module defines exception classes used throughout the OpenMAS agent framework
for proper error handling and debugging.

Based on specifications in:
- refactoring_work/planning/TASK_basic_agent_framework_implementation.md
"""

from typing import Any, Optional


class AgentError(Exception):
    """Base exception for all agent-related errors."""

    def __init__(self, message: str, agent_id: Optional[str] = None, details: Optional[dict[Any, Any]] = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            agent_id: ID of the agent where the error occurred (optional)
            details: Additional error details (optional)
        """
        super().__init__(message)
        self.agent_id = agent_id
        self.details = details or {}

    def __str__(self):
        """String representation of the error."""
        base_message = super().__str__()
        if self.agent_id:
            base_message = f"Agent {self.agent_id}: {base_message}"
        return base_message


class AgentConfigurationError(AgentError):
    """Raised when agent configuration is invalid or cannot be loaded."""

    pass


class AgentCreationError(AgentError):
    """Raised when agent creation fails."""

    pass


class AgentLifecycleError(AgentError):
    """Raised when agent lifecycle operations (start/stop) fail."""

    pass


class AgentMessageError(AgentError):
    """Raised when message handling fails."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        message_id: Optional[str] = None,
        details: Optional[dict[Any, Any]] = None,
    ):
        """
        Initialize the exception.

        Args:
            message: Error message
            agent_id: ID of the agent where the error occurred (optional)
            message_id: ID of the message that caused the error (optional)
            details: Additional error details (optional)
        """
        super().__init__(message, agent_id, details)
        self.message_id = message_id

    def __str__(self):
        """String representation of the error."""
        base_message = super().__str__()
        if self.message_id:
            base_message = f"{base_message} (Message ID: {self.message_id})"
        return base_message


class AgentCapabilityError(AgentError):
    """Raised when capability operations fail."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        capability_name: Optional[str] = None,
        details: Optional[dict[Any, Any]] = None,
    ):
        """
        Initialize the exception.

        Args:
            message: Error message
            agent_id: ID of the agent where the error occurred (optional)
            capability_name: Name of the capability that caused the error (optional)
            details: Additional error details (optional)
        """
        super().__init__(message, agent_id, details)
        self.capability_name = capability_name

    def __str__(self):
        """String representation of the error."""
        base_message = super().__str__()
        if self.capability_name:
            base_message = f"{base_message} (Capability: {self.capability_name})"
        return base_message


class AgentSessionError(AgentError):
    """Raised when session operations fail."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        details: Optional[dict[Any, Any]] = None,
    ):
        """
        Initialize the exception.

        Args:
            message: Error message
            agent_id: ID of the agent where the error occurred (optional)
            session_id: ID of the session that caused the error (optional)
            details: Additional error details (optional)
        """
        super().__init__(message, agent_id, details)
        self.session_id = session_id

    def __str__(self):
        """String representation of the error."""
        base_message = super().__str__()
        if self.session_id:
            base_message = f"{base_message} (Session ID: {self.session_id})"
        return base_message


class AgentStateError(AgentError):
    """Raised when state management operations fail."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        state_key: Optional[str] = None,
        details: Optional[dict[Any, Any]] = None,
    ):
        """
        Initialize the exception.

        Args:
            message: Error message
            agent_id: ID of the agent where the error occurred (optional)
            state_key: State key that caused the error (optional)
            details: Additional error details (optional)
        """
        super().__init__(message, agent_id, details)
        self.state_key = state_key

    def __str__(self):
        """String representation of the error."""
        base_message = super().__str__()
        if self.state_key:
            base_message = f"{base_message} (State Key: {self.state_key})"
        return base_message


class AgentProtocolError(AgentError):
    """Raised when protocol adapter operations fail."""

    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        protocol_name: Optional[str] = None,
        details: Optional[dict[Any, Any]] = None,
    ):
        """
        Initialize the exception.

        Args:
            message: Error message
            agent_id: ID of the agent where the error occurred (optional)
            protocol_name: Name of the protocol that caused the error (optional)
            details: Additional error details (optional)
        """
        super().__init__(message, agent_id, details)
        self.protocol_name = protocol_name

    def __str__(self):
        """String representation of the error."""
        base_message = super().__str__()
        if self.protocol_name:
            base_message = f"{base_message} (Protocol: {self.protocol_name})"
        return base_message
