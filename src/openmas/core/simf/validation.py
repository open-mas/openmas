"""
SIMF Validation Utilities

This module provides validation utilities for SIMF messages, ensuring
message integrity, compliance with the specification, and catching
common errors before they cause issues in protocol adapters or
reasoning engines.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from .models import MessageType, PayloadType, SIMFMessage


class ValidationErrorType(str, Enum):
    """Types of validation errors."""

    SCHEMA_ERROR = "schema_error"
    SEMANTIC_ERROR = "semantic_error"
    SECURITY_ERROR = "security_error"
    PROTOCOL_ERROR = "protocol_error"


@dataclass
class ValidationIssue:
    """Individual validation issue."""

    error_type: ValidationErrorType
    field_path: str
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationResult:
    """Result of SIMF validation."""

    is_valid: bool
    issues: list[ValidationIssue]
    message: SIMFMessage | None = None

    @property
    def errors(self) -> list[ValidationIssue]:
        """Get only error-level issues."""
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Get only warning-level issues."""
        return [issue for issue in self.issues if issue.severity == "warning"]


class ValidationError(Exception):
    """Exception raised when SIMF validation fails."""

    def __init__(self, result: ValidationResult):
        self.result = result
        error_messages = [issue.message for issue in result.errors]
        super().__init__(f"SIMF validation failed: {'; '.join(error_messages)}")


class SIMFValidator:
    """
    Comprehensive SIMF message validator.

    Provides validation beyond basic Pydantic schema validation,
    including semantic checks, security validation, and protocol
    compliance verification.
    """

    def __init__(self, strict: bool = True, security_checks: bool = True):
        """
        Initialize validator.

        Args:
            strict: Whether to treat warnings as errors
            security_checks: Whether to perform security validation
        """
        self.strict = strict
        self.security_checks = security_checks

    def validate(self, message_data: dict[str, Any] | SIMFMessage) -> ValidationResult:
        """
        Validate a SIMF message.

        Args:
            message_data: Raw message data or SIMFMessage instance

        Returns:
            ValidationResult with validation status and issues
        """
        issues = []
        message = None

        # First, try basic Pydantic validation
        try:
            if isinstance(message_data, dict):
                message = SIMFMessage(**message_data)
            elif isinstance(message_data, SIMFMessage):
                message = message_data
            else:
                issues.append(
                    ValidationIssue(
                        error_type=ValidationErrorType.SCHEMA_ERROR,
                        field_path="root",
                        message=f"Invalid message type: {type(message_data)}",
                        severity="error",
                    )
                )
                return ValidationResult(is_valid=False, issues=issues)

        except PydanticValidationError as e:
            for error in e.errors():
                field_path = ".".join(str(loc) for loc in error["loc"])
                issues.append(
                    ValidationIssue(
                        error_type=ValidationErrorType.SCHEMA_ERROR,
                        field_path=field_path,
                        message=error["msg"],
                        severity="error",
                    )
                )
            return ValidationResult(is_valid=False, issues=issues)

        # Perform semantic validation
        issues.extend(self._validate_semantics(message))

        # Perform security validation if enabled
        if self.security_checks:
            issues.extend(self._validate_security(message))

        # Check protocol compliance
        issues.extend(self._validate_protocol_compliance(message))

        # Determine if validation passed
        has_errors = any(issue.severity == "error" for issue in issues)
        has_warnings = any(issue.severity == "warning" for issue in issues)

        is_valid = not has_errors and (not self.strict or not has_warnings)

        return ValidationResult(is_valid=is_valid, issues=issues, message=message)

    def validate_and_raise(self, message_data: dict[str, Any] | SIMFMessage) -> SIMFMessage:
        """
        Validate a SIMF message and raise ValidationError if invalid.

        Args:
            message_data: Raw message data or SIMFMessage instance

        Returns:
            Validated SIMFMessage instance

        Raises:
            ValidationError: If validation fails
        """
        result = self.validate(message_data)
        if not result.is_valid:
            raise ValidationError(result)
        return result.message

    def _validate_semantics(self, message: SIMFMessage) -> list[ValidationIssue]:
        """Validate semantic consistency of the message."""
        issues = []

        # Check message type consistency with payload
        payload_type = message.payload.payload_type
        message_type = message.message_type

        # Define expected payload types for message types
        expected_payload_mapping = {
            MessageType.TOOL_INVOCATION: [PayloadType.INVOCATION_CONTENT],
            MessageType.CAPABILITY_INVOCATION: [PayloadType.INVOCATION_CONTENT],
            MessageType.TOOL_RESULT: [PayloadType.INVOCATION_RESULT_CONTENT],
            MessageType.CAPABILITY_RESULT: [PayloadType.INVOCATION_RESULT_CONTENT],
            MessageType.ERROR_MESSAGE: [PayloadType.INVOCATION_RESULT_CONTENT],
            MessageType.EVENT_NOTIFICATION: [PayloadType.EVENT_CONTENT],
            MessageType.MULTI_PART_MESSAGE: [PayloadType.MULTI_PART_CONTENT],
            MessageType.PLAIN_TEXT_MESSAGE: [PayloadType.TEXT_CONTENT],
        }

        if message_type in expected_payload_mapping:
            expected_types = expected_payload_mapping[message_type]
            if payload_type not in expected_types:
                issues.append(
                    ValidationIssue(
                        error_type=ValidationErrorType.SEMANTIC_ERROR,
                        field_path="payload.payload_type",
                        message=(
                            f"Message type {message_type} should have payload type in "
                            f"{expected_types}, got {payload_type}"
                        ),
                        severity="warning",
                    )
                )

        # Check invocation result consistency
        if payload_type == PayloadType.INVOCATION_RESULT_CONTENT:
            payload = message.payload
            if payload.status == "success" and payload.result is None:
                issues.append(
                    ValidationIssue(
                        error_type=ValidationErrorType.SEMANTIC_ERROR,
                        field_path="payload.result",
                        message="Successful invocation should have result data",
                        severity="warning",
                    )
                )
            elif payload.status == "failure" and payload.error is None:
                issues.append(
                    ValidationIssue(
                        error_type=ValidationErrorType.SEMANTIC_ERROR,
                        field_path="payload.error",
                        message="Failed invocation should have error information",
                        severity="error",
                    )
                )

        # Check multi-part content
        if payload_type == PayloadType.MULTI_PART_CONTENT:
            payload = message.payload
            if not payload.parts:
                issues.append(
                    ValidationIssue(
                        error_type=ValidationErrorType.SEMANTIC_ERROR,
                        field_path="payload.parts",
                        message="Multi-part content must have at least one part",
                        severity="error",
                    )
                )

        # Check stream context
        if payload_type == PayloadType.STREAM_CONTEXT_CONTENT:
            payload = message.payload
            if payload.sequence_number < 0:
                issues.append(
                    ValidationIssue(
                        error_type=ValidationErrorType.SEMANTIC_ERROR,
                        field_path="payload.sequence_number",
                        message="Stream sequence number must be non-negative",
                        severity="error",
                    )
                )

            if payload.is_heartbeat and payload.content is not None:
                issues.append(
                    ValidationIssue(
                        error_type=ValidationErrorType.SEMANTIC_ERROR,
                        field_path="payload.content",
                        message="Heartbeat messages should not have content",
                        severity="warning",
                    )
                )

        return issues

    def _validate_security(self, message: SIMFMessage) -> list[ValidationIssue]:
        """Validate security aspects of the message."""
        issues = []

        # Check for potential injection attacks in text content
        if message.payload.payload_type == PayloadType.TEXT_CONTENT:
            text = message.payload.text

            # Basic injection detection patterns
            suspicious_patterns = [
                "javascript:",
                "data:text/html",
                "<script",
                "eval(",
                "exec(",
                "${",  # Template injection
                "{{",  # Template injection
            ]

            for pattern in suspicious_patterns:
                if pattern.lower() in text.lower():
                    issues.append(
                        ValidationIssue(
                            error_type=ValidationErrorType.SECURITY_ERROR,
                            field_path="payload.text",
                            message=(f"Potentially dangerous pattern detected: {pattern}"),
                            severity="warning",
                        )
                    )

        # Check asset references for path traversal
        if message.payload.payload_type == PayloadType.ASSET_REFERENCE_CONTENT:
            asset_id = message.payload.asset_id

            if "../" in asset_id or "../" in asset_id:
                issues.append(
                    ValidationIssue(
                        error_type=ValidationErrorType.SECURITY_ERROR,
                        field_path="payload.asset_id",
                        message="Asset ID contains path traversal patterns",
                        severity="error",
                    )
                )

        # Check for extremely large payloads (potential DoS)
        message_str = message.json()
        if len(message_str) > 10 * 1024 * 1024:  # 10MB
            issues.append(
                ValidationIssue(
                    error_type=ValidationErrorType.SECURITY_ERROR,
                    field_path="root",
                    message=(f"Message size ({len(message_str)} bytes) exceeds " f"recommended limit"),
                    severity="warning",
                )
            )

        return issues

    def _validate_protocol_compliance(self, message: SIMFMessage) -> list[ValidationIssue]:
        """Validate compliance with SIMF protocol requirements."""
        issues = []

        # Check required fields are meaningful
        if not message.target_agent_id.strip():
            issues.append(
                ValidationIssue(
                    error_type=ValidationErrorType.PROTOCOL_ERROR,
                    field_path="target_agent_id",
                    message="Target agent ID cannot be empty or whitespace",
                    severity="error",
                )
            )

        if not message.message_id.strip():
            issues.append(
                ValidationIssue(
                    error_type=ValidationErrorType.PROTOCOL_ERROR,
                    field_path="message_id",
                    message="Message ID cannot be empty or whitespace",
                    severity="error",
                )
            )

        # Validate timestamp is not too far in the future
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        if message.timestamp > now + timedelta(minutes=5):
            issues.append(
                ValidationIssue(
                    error_type=ValidationErrorType.PROTOCOL_ERROR,
                    field_path="timestamp",
                    message="Message timestamp is too far in the future",
                    severity="warning",
                )
            )

        # Check for reasonable message ID format (basic UUID-like check)
        import re

        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        if not uuid_pattern.match(message.message_id):
            issues.append(
                ValidationIssue(
                    error_type=ValidationErrorType.SCHEMA_ERROR,
                    field_path="message_id",
                    message="Invalid message_id format (must be UUID4)",
                    severity="error",
                )
            )

        # Check payload type consistency
        from .models import BasePayload

        if not isinstance(message.payload, BasePayload):
            issues.append(
                ValidationIssue(
                    error_type=ValidationErrorType.SCHEMA_ERROR,
                    field_path="payload",
                    message="Payload must be a subclass of BasePayload",
                    severity="error",
                )
            )

        # Check message type consistency
        if not isinstance(message.message_type, MessageType):
            issues.append(
                ValidationIssue(
                    error_type=ValidationErrorType.SCHEMA_ERROR,
                    field_path="message_type",
                    message=("message_type must be a MessageType enum value"),
                    severity="error",
                )
            )

        return issues


# Convenience functions for common validation patterns
def validate_simf_message(message_data: dict[str, Any] | SIMFMessage, strict: bool = True) -> ValidationResult:
    """Quick validation of a SIMF message."""
    validator = SIMFValidator(strict=strict)
    return validator.validate(message_data)


def ensure_valid_simf_message(message_data: dict[str, Any] | SIMFMessage, strict: bool = True) -> SIMFMessage:
    """Validate and return a SIMF message, raising ValidationError if invalid."""
    validator = SIMFValidator(strict=strict)
    return validator.validate_and_raise(message_data)
