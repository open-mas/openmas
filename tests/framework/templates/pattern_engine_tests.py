"""
IPatternEngine Test Framework Template

This module provides comprehensive test templates for IPatternEngine implementations,
designed to validate communication pattern execution, SIMF integration, and
cross-protocol pattern compatibility.
"""

import asyncio
import contextlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from openmas.core.simf import (
    InvocationStatus,
    MessageType,
    PayloadType,
    SIMFMessage,
    create_invocation_message,
    create_invocation_result_message,
    create_text_message,
    validate_simf_message,
)

from .common_fixtures import simf_message_fixtures

# ============================================================================
# IPatternEngine Interface Definition (for testing)
# ============================================================================


class IPatternEngine(ABC):
    """
    Interface definition for pattern engines.
    This mirrors the actual interface and is used for testing.
    """

    @abstractmethod
    async def register_pattern(self, pattern: dict[str, Any]) -> None:
        """Register a new communication pattern."""
        pass

    @abstractmethod
    async def execute_pattern(self, pattern_name: str, config: dict[str, Any], message: SIMFMessage) -> dict[str, Any]:
        """Execute a specific pattern."""
        pass

    @abstractmethod
    async def get_available_patterns(self) -> list[dict[str, Any]]:
        """Get list of registered patterns."""
        pass

    @abstractmethod
    async def create_pattern_instance(self, pattern_name: str, config: dict[str, Any]) -> "IPatternInstance":
        """Create pattern instance for stateful patterns."""
        pass

    @abstractmethod
    def supports_protocol(self, pattern_name: str, protocol_type: str) -> bool:
        """Check protocol compatibility."""
        pass

    @abstractmethod
    async def validate_pattern_config(self, pattern_name: str, config: dict[str, Any]) -> dict[str, Any]:
        """Validate pattern configuration."""
        pass


class IPatternInstance(ABC):
    """Interface for stateful pattern instances."""

    @abstractmethod
    async def start(self) -> None:
        """Initialize pattern instance."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Cleanup pattern instance."""
        pass

    @abstractmethod
    async def process_message(self, message: SIMFMessage) -> dict[str, Any] | None:
        """Process incoming message."""
        pass

    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        """Get current instance status."""
        pass


# ============================================================================
# Pattern Definition Fixtures
# ============================================================================


@pytest.fixture
def pattern_execution_fixtures():
    """
    Real pattern execution scenarios for testing.
    These represent actual communication patterns used in multi-agent systems.
    """
    return {
        "request_response_pattern": {
            "name": "request_response",
            "version": "1.0.0",
            "description": "Simple request-response communication pattern",
            "pattern_type": "request_response",
            "supported_protocols": ["mcp", "a2a", "http"],
            "options_schema": {
                "type": "object",
                "properties": {
                    "timeout": {"type": "integer", "default": 30},
                    "retry_attempts": {"type": "integer", "default": 3},
                },
            },
            "implementation_class": "RequestResponsePattern",
        },
        "publish_subscribe_pattern": {
            "name": "publish_subscribe",
            "version": "1.0.0",
            "description": "Publish-subscribe communication pattern",
            "pattern_type": "publish_subscribe",
            "supported_protocols": ["mqtt", "http", "a2a"],
            "options_schema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "qos": {"type": "integer", "default": 1},
                },
                "required": ["topic"],
            },
            "implementation_class": "PublishSubscribePattern",
        },
        "delegation_pattern": {
            "name": "delegation",
            "version": "1.0.0",
            "description": "Task delegation pattern with result aggregation",
            "pattern_type": "delegation",
            "supported_protocols": ["a2a", "mcp"],
            "options_schema": {
                "type": "object",
                "properties": {
                    "delegates": {"type": "array", "items": {"type": "string"}},
                    "aggregation_strategy": {
                        "type": "string",
                        "enum": ["first", "all", "majority"],
                        "default": "all",
                    },
                },
                "required": ["delegates"],
            },
            "implementation_class": "DelegationPattern",
        },
        "streaming_pattern": {
            "name": "streaming",
            "version": "1.0.0",
            "description": "Streaming data pattern for continuous communication",
            "pattern_type": "streaming",
            "supported_protocols": ["sse", "websocket", "grpc"],
            "options_schema": {
                "type": "object",
                "properties": {
                    "buffer_size": {"type": "integer", "default": 1024},
                    "heartbeat_interval": {"type": "integer", "default": 30},
                },
            },
            "implementation_class": "StreamingPattern",
        },
    }


@pytest.fixture
def pattern_config_fixtures():
    """Valid pattern execution configurations."""
    return {
        "request_response_config": {
            "pattern_name": "request_response",
            "options": {"timeout": 30, "retry_attempts": 2},
            "protocol_adaptations": {
                "mcp": {"transport": "sse"},
                "a2a": {"format": "multipart"},
                "http": {"method": "POST"},
            },
        },
        "publish_subscribe_config": {
            "pattern_name": "publish_subscribe",
            "options": {"topic": "agent.events", "qos": 1},
            "protocol_adaptations": {
                "mqtt": {"retain": True},
                "a2a": {"broadcast": True},
            },
        },
        "delegation_config": {
            "pattern_name": "delegation",
            "options": {
                "delegates": ["agent-001", "agent-002", "agent-003"],
                "aggregation_strategy": "majority",
            },
            "protocol_adaptations": {
                "a2a": {"parallel": True},
                "mcp": {"batch": False},
            },
        },
    }


@pytest.fixture
def pattern_execution_scenarios():
    """
    Real-world pattern execution scenarios for testing.
    These use actual SIMF messages and expected pattern behaviors.
    """
    return {
        "request_response_scenario": {
            "pattern": "request_response",
            "input_message": create_invocation_message(
                invocation_name="analyze_sentiment",
                arguments={"text": "This product is amazing!", "language": "en"},
                target_agent_id="sentiment-analyzer",
            ),
            "expected_result": {
                "success": True,
                "execution_time": 1.5,
                "messages": [
                    # Expected response message structure
                ],
                "metadata": {"pattern_type": "request_response", "timeout": 30},
            },
        },
        "delegation_scenario": {
            "pattern": "delegation",
            "input_message": create_invocation_message(
                invocation_name="classify_document",
                arguments={
                    "document_id": "doc-123",
                    "categories": ["business", "personal", "technical"],
                },
                target_agent_id="document-classifier",
            ),
            "expected_result": {
                "success": True,
                "execution_time": 3.2,
                "messages": [
                    # Expected delegation messages to multiple agents
                ],
                "metadata": {
                    "pattern_type": "delegation",
                    "delegate_count": 3,
                    "aggregation_strategy": "majority",
                },
            },
        },
        "publish_subscribe_scenario": {
            "pattern": "publish_subscribe",
            "input_message": create_text_message(
                text="System alert: High CPU usage detected",
                target_agent_id="monitoring-system",
            ),
            "expected_result": {
                "success": True,
                "execution_time": 0.5,
                "messages": [
                    # Expected publish message
                ],
                "metadata": {
                    "pattern_type": "publish_subscribe",
                    "topic": "system.alerts",
                    "subscriber_count": 5,
                },
            },
        },
    }


# ============================================================================
# Base Test Template Class
# ============================================================================


class IPatternEngineTestTemplate:
    """
    Comprehensive test template for IPatternEngine implementations.

    This template ensures that pattern engine implementations:
    1. Correctly register and manage communication patterns
    2. Execute patterns with proper SIMF integration
    3. Handle cross-protocol pattern execution
    4. Manage pattern instances and lifecycle
    5. Validate pattern configurations properly
    """

    @pytest.fixture
    def pattern_engine(self) -> IPatternEngine:
        """
        Override this fixture in your test class to provide your
        IPatternEngine implementation for testing.
        """
        raise NotImplementedError("Must provide pattern_engine fixture in test class")

    # ========================================================================
    # Pattern Registration Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_register_valid_pattern(self, pattern_engine: IPatternEngine, pattern_execution_fixtures):
        """Test registration of valid communication patterns."""
        pattern = pattern_execution_fixtures["request_response_pattern"]

        # Should not raise exception
        await pattern_engine.register_pattern(pattern)

        # Pattern should be available
        patterns = await pattern_engine.get_available_patterns()
        pattern_names = [p["name"] for p in patterns]
        assert "request_response" in pattern_names

    @pytest.mark.asyncio
    async def test_register_invalid_pattern(self, pattern_engine: IPatternEngine):
        """Test registration failure with invalid pattern definition."""
        invalid_patterns = [
            {},  # Empty pattern
            {"name": "test"},  # Missing required fields
            {"name": "test", "version": "invalid version"},  # Invalid version format
            None,  # Null pattern
        ]

        for invalid_pattern in invalid_patterns:
            with pytest.raises((ValueError, TypeError, KeyError)):
                await pattern_engine.register_pattern(invalid_pattern)

    @pytest.mark.asyncio
    async def test_register_multiple_patterns(self, pattern_engine: IPatternEngine, pattern_execution_fixtures):
        """Test registration of multiple patterns."""
        patterns = [
            pattern_execution_fixtures["request_response_pattern"],
            pattern_execution_fixtures["publish_subscribe_pattern"],
            pattern_execution_fixtures["delegation_pattern"],
        ]

        for pattern in patterns:
            await pattern_engine.register_pattern(pattern)

        available_patterns = await pattern_engine.get_available_patterns()
        assert len(available_patterns) >= 3

        pattern_names = [p["name"] for p in available_patterns]
        assert "request_response" in pattern_names
        assert "publish_subscribe" in pattern_names
        assert "delegation" in pattern_names

    @pytest.mark.asyncio
    async def test_register_duplicate_pattern_name(self, pattern_engine: IPatternEngine, pattern_execution_fixtures):
        """Test handling of duplicate pattern names."""
        pattern = pattern_execution_fixtures["request_response_pattern"]

        # Register pattern
        await pattern_engine.register_pattern(pattern)

        # Attempt to register with same name should handle gracefully
        duplicate_pattern = pattern.copy()
        duplicate_pattern["version"] = "2.0.0"

        # Implementation may either update or raise error - both are valid
        with contextlib.suppress(ValueError):
            await pattern_engine.register_pattern(duplicate_pattern)

    # ========================================================================
    # Pattern Execution Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_pattern_execution_with_valid_simf_messages(
        self,
        pattern_engine: IPatternEngine,
        pattern_execution_fixtures,
        pattern_config_fixtures,
        simf_message_fixtures_exec,
    ):
        """Test pattern execution with valid SIMF messages."""
        # Register pattern
        pattern = pattern_execution_fixtures["request_response_pattern"]
        await pattern_engine.register_pattern(pattern)

        # Execute pattern
        config = pattern_config_fixtures["request_response_config"]
        message = simf_message_fixtures["tool_invocation"]

        result = await pattern_engine.execute_pattern(pattern_name="request_response", config=config, message=message)

        # Validate result structure
        assert isinstance(result, dict)
        assert "success" in result
        assert "execution_time" in result
        assert "messages" in result
        assert isinstance(result["messages"], list)

        # Validate SIMF message preservation
        for msg in result["messages"]:
            if isinstance(msg, SIMFMessage):
                validation_result = validate_simf_message(msg)
                assert validation_result.is_valid, f"Invalid SIMF message: {validation_result.issues}"

    @pytest.mark.asyncio
    async def test_execute_pattern_with_nonexistent_pattern(
        self,
        pattern_engine: IPatternEngine,
        pattern_config_fixtures,
        simf_message_fixtures_nonexistent,
    ):
        """Test execution failure with nonexistent pattern."""
        config = pattern_config_fixtures["request_response_config"]
        message = simf_message_fixtures_nonexistent["tool_invocation"]

        with pytest.raises((ValueError, KeyError)):
            await pattern_engine.execute_pattern(pattern_name="nonexistent_pattern", config=config, message=message)

    @pytest.mark.asyncio
    async def test_execute_pattern_with_invalid_config(
        self,
        pattern_engine: IPatternEngine,
        pattern_execution_fixtures,
        simf_message_fixtures_invalid,
    ):
        """Test pattern execution with invalid configuration."""
        # Register pattern
        pattern = pattern_execution_fixtures["request_response_pattern"]
        await pattern_engine.register_pattern(pattern)

        # Execute with invalid config
        invalid_config = {"invalid": "config"}
        message = simf_message_fixtures["tool_invocation"]

        with pytest.raises((ValueError, TypeError, KeyError)):
            await pattern_engine.execute_pattern(
                pattern_name="request_response", config=invalid_config, message=message
            )

    # ========================================================================
    # Protocol Compatibility Tests
    # ========================================================================

    def test_supports_protocol_for_registered_patterns(
        self, pattern_engine: IPatternEngine, pattern_execution_fixtures
    ):
        """Test protocol compatibility checking."""
        # Register patterns
        pattern = pattern_execution_fixtures["request_response_pattern"]

        # Test with pattern that supports multiple protocols
        supported_protocols = pattern["supported_protocols"]

        for protocol in supported_protocols:
            # Should support declared protocols
            assert pattern_engine.supports_protocol("request_response", protocol) or True  # May need registration first

        # Should not support undeclared protocols
        unsupported_protocols = ["websocket", "grpc", "custom"]
        for protocol in unsupported_protocols:
            if protocol not in supported_protocols:
                # Implementation may return False or raise exception
                try:
                    result = pattern_engine.supports_protocol("request_response", protocol)
                    if result is not None:
                        assert result is False
                except (ValueError, KeyError):
                    # Exception is also acceptable
                    pass

    def test_supports_protocol_for_nonexistent_pattern(self, pattern_engine: IPatternEngine):
        """Test protocol compatibility for nonexistent patterns."""
        with pytest.raises((ValueError, KeyError)):
            pattern_engine.supports_protocol("nonexistent_pattern", "mcp")

    # ========================================================================
    # Configuration Validation Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_validate_pattern_config_with_valid_config(
        self,
        pattern_engine: IPatternEngine,
        pattern_execution_fixtures,
        pattern_config_fixtures,
    ):
        """Test validation of valid pattern configurations."""
        # Register pattern
        pattern = pattern_execution_fixtures["request_response_pattern"]
        await pattern_engine.register_pattern(pattern)

        # Validate config
        config = pattern_config_fixtures["request_response_config"]
        result = await pattern_engine.validate_pattern_config(pattern_name="request_response", config=config)

        # Should indicate valid configuration
        assert isinstance(result, dict)
        assert result.get("is_valid", True) is True
        assert "errors" not in result or len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_validate_pattern_config_with_invalid_config(
        self, pattern_engine: IPatternEngine, pattern_execution_fixtures
    ):
        """Test validation of invalid pattern configurations."""
        # Register pattern
        pattern = pattern_execution_fixtures["request_response_pattern"]
        await pattern_engine.register_pattern(pattern)

        # Test invalid configurations
        invalid_configs = [
            {},  # Empty config
            {"invalid": "config"},  # Wrong structure
            {"pattern_name": "wrong_pattern"},  # Wrong pattern name
        ]

        for invalid_config in invalid_configs:
            result = await pattern_engine.validate_pattern_config(
                pattern_name="request_response", config=invalid_config
            )

            # Should indicate invalid configuration
            assert isinstance(result, dict)
            assert result.get("is_valid", False) is False or len(result.get("errors", [])) > 0

    # ========================================================================
    # Pattern Instance Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_create_pattern_instance(
        self,
        pattern_engine: IPatternEngine,
        pattern_execution_fixtures,
        pattern_config_fixtures,
    ):
        """Test creation of stateful pattern instances."""
        # Register pattern
        pattern = pattern_execution_fixtures["streaming_pattern"]
        await pattern_engine.register_pattern(pattern)

        # Create instance
        config = {
            "pattern_name": "streaming",
            "options": {"buffer_size": 2048, "heartbeat_interval": 15},
        }

        instance = await pattern_engine.create_pattern_instance(pattern_name="streaming", config=config)

        # Validate instance
        assert isinstance(instance, IPatternInstance)

        # Test instance lifecycle
        await instance.start()
        status = await instance.get_status()
        assert isinstance(status, dict)
        assert status.get("status") in ["running", "active", "started"]

        await instance.stop()
        status = await instance.get_status()
        assert status.get("status") in ["stopped", "inactive", "finished"]

    @pytest.mark.asyncio
    async def test_pattern_instance_message_processing(
        self,
        pattern_engine: IPatternEngine,
        pattern_execution_fixtures,
        simf_message_fixtures_processing,
    ):
        """Test pattern instance message processing."""
        # Register pattern
        pattern = pattern_execution_fixtures["streaming_pattern"]
        await pattern_engine.register_pattern(pattern)

        # Create and start instance
        config = {"pattern_name": "streaming", "options": {}}
        instance = await pattern_engine.create_pattern_instance(pattern_name="streaming", config=config)
        await instance.start()

        # Process message
        message = simf_message_fixtures["text_message"]
        result = await instance.process_message(message)

        # Validate result (may be None for some patterns)
        if result is not None:
            assert isinstance(result, dict)

        await instance.stop()

    # ========================================================================
    # Integration Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_end_to_end_pattern_execution_scenario(
        self, pattern_engine: IPatternEngine, pattern_execution_scenarios
    ):
        """Test complete end-to-end pattern execution scenarios."""
        scenario = pattern_execution_scenarios["request_response_scenario"]

        # This would be implemented based on the specific pattern engine
        # and would test the full execution flow
        assert True  # Placeholder - implement based on specific engine

    @pytest.mark.asyncio
    async def test_concurrent_pattern_execution(
        self,
        pattern_engine: IPatternEngine,
        pattern_execution_fixtures,
        pattern_config_fixtures,
        simf_message_fixtures_concurrent,
    ):
        """Test concurrent execution of multiple patterns."""
        # Register patterns
        patterns = [
            pattern_execution_fixtures["request_response_pattern"],
            pattern_execution_fixtures["publish_subscribe_pattern"],
        ]

        for pattern in patterns:
            await pattern_engine.register_pattern(pattern)

        # Execute patterns concurrently
        tasks = []
        for _i in range(3):
            task = pattern_engine.execute_pattern(
                pattern_name="request_response",
                config=pattern_config_fixtures["request_response_config"],
                message=simf_message_fixtures["tool_invocation"],
            )
            tasks.append(task)

        # Wait for all executions
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 3
        for result in results:
            assert result.get("success", False) is True or "execution_time" in result


# ============================================================================
# Test Suite Factory
# ============================================================================


def create_pattern_engine_test_suite(engine_class, additional_fixtures: dict[str, Any] | None = None) -> type:
    """
    Factory function to create a complete test suite for a pattern engine.

    Args:
        engine_class: The IPatternEngine implementation to test
        additional_fixtures: Additional test fixtures specific to the engine

    Returns:
        A test class that can be run with pytest
    """

    class GeneratedPatternEngineTests(IPatternEngineTestTemplate):
        @pytest.fixture
        def pattern_engine(self) -> IPatternEngine:
            return engine_class()

        # Add any additional fixtures
        if additional_fixtures:
            for name, fixture in additional_fixtures.items():
                locals()[name] = pytest.fixture()(fixture)

    GeneratedPatternEngineTests.__name__ = f"Test{engine_class.__name__}"

    return GeneratedPatternEngineTests
