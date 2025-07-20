"""
Unit tests for OpenMAS Agent Exceptions

Comprehensive tests for agent exception hierarchy, ensuring proper error handling
and debugging capabilities throughout the agent framework.
"""

import pytest

from openmas.agent.exceptions import (
    AgentCapabilityError,
    AgentConfigurationError,
    AgentCreationError,
    AgentError,
    AgentLifecycleError,
    AgentMessageError,
    AgentProtocolError,
    AgentSessionError,
    AgentStateError,
)


class TestAgentError:
    """Test the base AgentError class."""

    def test_basic_initialization(self):
        """Test basic exception creation."""
        error = AgentError("Test error message")

        assert str(error) == "Test error message"
        assert error.agent_id is None
        assert error.details == {}

    def test_initialization_with_agent_id(self):
        """Test exception creation with agent ID."""
        error = AgentError("Test error", agent_id="test-agent-001")

        assert str(error) == "Agent test-agent-001: Test error"
        assert error.agent_id == "test-agent-001"
        assert error.details == {}

    def test_initialization_with_details(self):
        """Test exception creation with details."""
        details = {"error_code": 500, "context": "test"}
        error = AgentError("Test error", details=details)

        assert str(error) == "Test error"
        assert error.agent_id is None
        assert error.details == details

    def test_initialization_with_all_parameters(self):
        """Test exception creation with all parameters."""
        details = {"error_code": 404, "timestamp": "2024-01-01"}
        error = AgentError("Test error", agent_id="test-agent", details=details)

        assert str(error) == "Agent test-agent: Test error"
        assert error.agent_id == "test-agent"
        assert error.details == details

    def test_inheritance_from_exception(self):
        """Test that AgentError inherits from Exception."""
        error = AgentError("Test error")

        assert isinstance(error, Exception)
        assert isinstance(error, AgentError)


class TestAgentConfigurationError:
    """Test AgentConfigurationError class."""

    def test_inheritance(self):
        """Test inheritance from AgentError."""
        error = AgentConfigurationError("Config error")

        assert isinstance(error, AgentError)
        assert isinstance(error, AgentConfigurationError)

    def test_basic_functionality(self):
        """Test basic functionality inherited from AgentError."""
        error = AgentConfigurationError("Invalid config", agent_id="agent-1")

        assert str(error) == "Agent agent-1: Invalid config"
        assert error.agent_id == "agent-1"

    def test_with_details(self):
        """Test with configuration details."""
        details = {"missing_field": "protocol", "file": "config.yaml"}
        error = AgentConfigurationError("Missing required field", details=details)

        assert error.details == details


class TestAgentCreationError:
    """Test AgentCreationError class."""

    def test_inheritance(self):
        """Test inheritance from AgentError."""
        error = AgentCreationError("Creation failed")

        assert isinstance(error, AgentError)
        assert isinstance(error, AgentCreationError)

    def test_basic_functionality(self):
        """Test basic functionality."""
        error = AgentCreationError("Failed to create agent", agent_id="new-agent")

        assert str(error) == "Agent new-agent: Failed to create agent"


class TestAgentLifecycleError:
    """Test AgentLifecycleError class."""

    def test_inheritance(self):
        """Test inheritance from AgentError."""
        error = AgentLifecycleError("Lifecycle error")

        assert isinstance(error, AgentError)
        assert isinstance(error, AgentLifecycleError)

    def test_lifecycle_scenarios(self):
        """Test common lifecycle error scenarios."""
        start_error = AgentLifecycleError("Failed to start", agent_id="agent-1")
        stop_error = AgentLifecycleError("Failed to stop", agent_id="agent-2")

        assert "Failed to start" in str(start_error)
        assert "Failed to stop" in str(stop_error)


class TestAgentMessageError:
    """Test AgentMessageError class."""

    def test_inheritance(self):
        """Test inheritance from AgentError."""
        error = AgentMessageError("Message error")

        assert isinstance(error, AgentError)
        assert isinstance(error, AgentMessageError)

    def test_initialization_basic(self):
        """Test basic initialization."""
        error = AgentMessageError("Message processing failed")

        assert str(error) == "Message processing failed"
        assert error.message_id is None

    def test_initialization_with_message_id(self):
        """Test initialization with message ID."""
        error = AgentMessageError(
            "Invalid message format", agent_id="agent-1", message_id="msg-123"
        )

        expected = "Agent agent-1: Invalid message format (Message ID: msg-123)"
        assert str(error) == expected
        assert error.message_id == "msg-123"

    def test_initialization_with_all_parameters(self):
        """Test initialization with all parameters."""
        details = {"validation_error": "missing_field", "field": "target_agent_id"}
        error = AgentMessageError(
            "Message validation failed",
            agent_id="validator-agent",
            message_id="msg-456",
            details=details,
        )

        assert error.agent_id == "validator-agent"
        assert error.message_id == "msg-456"
        assert error.details == details


class TestAgentCapabilityError:
    """Test AgentCapabilityError class."""

    def test_inheritance(self):
        """Test inheritance from AgentError."""
        error = AgentCapabilityError("Capability error")

        assert isinstance(error, AgentError)
        assert isinstance(error, AgentCapabilityError)

    def test_initialization_basic(self):
        """Test basic initialization."""
        error = AgentCapabilityError("Capability not found")

        assert str(error) == "Capability not found"
        assert error.capability_name is None

    def test_initialization_with_capability_name(self):
        """Test initialization with capability name."""
        error = AgentCapabilityError(
            "Capability execution failed",
            agent_id="worker-agent",
            capability_name="file_processor",
        )

        expected = "Agent worker-agent: Capability execution failed (Capability: file_processor)"
        assert str(error) == expected
        assert error.capability_name == "file_processor"

    def test_capability_scenarios(self):
        """Test common capability error scenarios."""
        not_found = AgentCapabilityError(
            "Capability not registered", capability_name="unknown"
        )
        execution_failed = AgentCapabilityError(
            "Execution timeout", capability_name="slow_task"
        )

        assert "unknown" in str(not_found)
        assert "slow_task" in str(execution_failed)


class TestAgentSessionError:
    """Test AgentSessionError class."""

    def test_inheritance(self):
        """Test inheritance from AgentError."""
        error = AgentSessionError("Session error")

        assert isinstance(error, AgentError)
        assert isinstance(error, AgentSessionError)

    def test_initialization_basic(self):
        """Test basic initialization."""
        error = AgentSessionError("Session expired")

        assert str(error) == "Session expired"
        assert error.session_id is None

    def test_initialization_with_session_id(self):
        """Test initialization with session ID."""
        error = AgentSessionError(
            "Session not found", agent_id="session-agent", session_id="sess-789"
        )

        expected = "Agent session-agent: Session not found (Session ID: sess-789)"
        assert str(error) == expected
        assert error.session_id == "sess-789"

    def test_session_scenarios(self):
        """Test common session error scenarios."""
        expired = AgentSessionError("Session expired", session_id="sess-old")
        invalid = AgentSessionError("Invalid session", session_id="sess-bad")

        assert "sess-old" in str(expired)
        assert "sess-bad" in str(invalid)


class TestAgentStateError:
    """Test AgentStateError class."""

    def test_inheritance(self):
        """Test inheritance from AgentError."""
        error = AgentStateError("State error")

        assert isinstance(error, AgentError)
        assert isinstance(error, AgentStateError)

    def test_initialization_basic(self):
        """Test basic initialization."""
        error = AgentStateError("State corruption detected")

        assert str(error) == "State corruption detected"
        assert error.state_key is None

    def test_initialization_with_state_key(self):
        """Test initialization with state key."""
        error = AgentStateError(
            "Invalid state value",
            agent_id="stateful-agent",
            state_key="user_preferences",
        )

        expected = (
            "Agent stateful-agent: Invalid state value (State Key: user_preferences)"
        )
        assert str(error) == expected
        assert error.state_key == "user_preferences"

    def test_state_scenarios(self):
        """Test common state error scenarios."""
        not_found = AgentStateError("State key not found", state_key="missing_key")
        invalid = AgentStateError("Invalid state format", state_key="config")

        assert "missing_key" in str(not_found)
        assert "config" in str(invalid)


class TestAgentProtocolError:
    """Test AgentProtocolError class."""

    def test_inheritance(self):
        """Test inheritance from AgentError."""
        error = AgentProtocolError("Protocol error")

        assert isinstance(error, AgentError)
        assert isinstance(error, AgentProtocolError)

    def test_initialization_basic(self):
        """Test basic initialization."""
        error = AgentProtocolError("Protocol connection failed")

        assert str(error) == "Protocol connection failed"
        assert error.protocol_name is None

    def test_initialization_with_protocol_name(self):
        """Test initialization with protocol name."""
        error = AgentProtocolError(
            "Protocol adapter not found",
            agent_id="multi-protocol-agent",
            protocol_name="mcp",
        )

        expected = (
            "Agent multi-protocol-agent: Protocol adapter not found (Protocol: mcp)"
        )
        assert str(error) == expected
        assert error.protocol_name == "mcp"

    def test_protocol_scenarios(self):
        """Test common protocol error scenarios."""
        connection_failed = AgentProtocolError(
            "Connection timeout", protocol_name="a2a"
        )
        invalid_message = AgentProtocolError(
            "Invalid message format", protocol_name="http"
        )

        assert "a2a" in str(connection_failed)
        assert "http" in str(invalid_message)


class TestExceptionHierarchy:
    """Test the overall exception hierarchy."""

    def test_all_exceptions_inherit_from_agent_error(self):
        """Test that all custom exceptions inherit from AgentError."""
        exception_classes = [
            AgentConfigurationError,
            AgentCreationError,
            AgentLifecycleError,
            AgentMessageError,
            AgentCapabilityError,
            AgentSessionError,
            AgentStateError,
            AgentProtocolError,
        ]

        for exception_class in exception_classes:
            instance = exception_class("Test error")
            assert isinstance(instance, AgentError)
            assert isinstance(instance, Exception)

    def test_exception_specificity(self):
        """Test that specific exceptions can be caught specifically."""
        # Test that we can catch specific exception types
        with pytest.raises(AgentConfigurationError):
            raise AgentConfigurationError("Config error")

        with pytest.raises(AgentMessageError):
            raise AgentMessageError("Message error")

        with pytest.raises(AgentCapabilityError):
            raise AgentCapabilityError("Capability error")

    def test_generic_exception_handling(self):
        """Test that all exceptions can be caught as AgentError."""
        exceptions_to_test = [
            AgentConfigurationError("Config error"),
            AgentCreationError("Creation error"),
            AgentLifecycleError("Lifecycle error"),
            AgentMessageError("Message error"),
            AgentCapabilityError("Capability error"),
            AgentSessionError("Session error"),
            AgentStateError("State error"),
            AgentProtocolError("Protocol error"),
        ]

        for exception in exceptions_to_test:
            with pytest.raises(AgentError):
                raise exception


class TestErrorMessageFormatting:
    """Test error message formatting consistency."""

    def test_consistent_agent_id_formatting(self):
        """Test that agent ID is formatted consistently across all exceptions."""
        agent_id = "test-agent-123"
        base_message = "Test error message"

        exceptions = [
            AgentError(base_message, agent_id=agent_id),
            AgentConfigurationError(base_message, agent_id=agent_id),
            AgentCreationError(base_message, agent_id=agent_id),
            AgentLifecycleError(base_message, agent_id=agent_id),
            AgentMessageError(base_message, agent_id=agent_id),
            AgentCapabilityError(base_message, agent_id=agent_id),
            AgentSessionError(base_message, agent_id=agent_id),
            AgentStateError(base_message, agent_id=agent_id),
            AgentProtocolError(base_message, agent_id=agent_id),
        ]

        for exception in exceptions:
            assert str(exception).startswith(f"Agent {agent_id}: {base_message}")

    def test_optional_context_formatting(self):
        """Test that optional context information is formatted correctly."""
        # Test message ID formatting
        msg_error = AgentMessageError("Error", message_id="msg-123")
        assert str(msg_error).endswith("(Message ID: msg-123)")

        # Test capability name formatting
        cap_error = AgentCapabilityError("Error", capability_name="tool")
        assert str(cap_error).endswith("(Capability: tool)")

        # Test session ID formatting
        sess_error = AgentSessionError("Error", session_id="sess-456")
        assert str(sess_error).endswith("(Session ID: sess-456)")

        # Test state key formatting
        state_error = AgentStateError("Error", state_key="config")
        assert str(state_error).endswith("(State Key: config)")

        # Test protocol name formatting
        proto_error = AgentProtocolError("Error", protocol_name="mcp")
        assert str(proto_error).endswith("(Protocol: mcp)")

    def test_combined_context_formatting(self):
        """Test formatting when multiple context elements are present."""
        error = AgentMessageError(
            "Message validation failed", agent_id="validator", message_id="msg-789"
        )

        error_str = str(error)
        assert "Agent validator:" in error_str
        assert "Message validation failed" in error_str
        assert "(Message ID: msg-789)" in error_str
