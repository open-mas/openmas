"""Logging configuration for OpenMAS."""

import logging
import sys
from typing import cast

import structlog
from structlog.stdlib import BoundLogger
from structlog.types import Processor

# Flag to ensure logging is configured only once by default, or on first get_logger call
_OPENMAS_LOGGING_CONFIGURED = False


def configure_logging(
    log_level: str | int = logging.WARNING,
    json_format: bool = False,
    timestamp_key: str = "timestamp",
    additional_processors: list[Processor] | None = None,
) -> None:
    """Configure logging for the application.

    Args:
        log_level: The log level to use (default: WARNING)
        json_format: Whether to output logs in JSON format (default: False)
        timestamp_key: The key to use for the timestamp in the log output (default: timestamp)
        additional_processors: Additional processors to add to the structlog processing pipeline
    """
    global _OPENMAS_LOGGING_CONFIGURED
    level = log_level.upper() if isinstance(log_level, str) else log_level

    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", key=timestamp_key),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if additional_processors:
        processors.extend(additional_processors)

    if json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True, exception_formatter=structlog.dev.plain_traceback))

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    # Ensure handlers are cleared if re-configuring to avoid duplicate messages
    # or use a more robust way to update existing handlers if needed.
    # For basicConfig, it's often simpler to let it run if not configured,
    # or manually manage handlers if re-configuration is complex.
    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():  # Configure basicConfig only if no handlers exist
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=cast(int | str, level),
        )
    else:  # If handlers exist, just set the level on the root logger and its handlers
        root_logger.setLevel(cast(int | str, level))
        for handler in root_logger.handlers:
            handler.setLevel(cast(int | str, level))

    _OPENMAS_LOGGING_CONFIGURED = True


def set_global_log_level(level: str | int) -> None:
    """Set the global logging level for the root logger and structlog handlers.

    Args:
        level: The log level to set (e.g., logging.INFO, "DEBUG").
    """
    log_level_int = level if isinstance(level, int) else logging.getLevelName(level.upper())

    # Update standard library logging level
    logging.getLogger().setLevel(log_level_int)

    # Ensure all existing handlers also respect this new level
    for handler in logging.root.handlers:
        handler.setLevel(log_level_int)


def get_logger(name: str) -> BoundLogger:
    """Get a logger instance.

    Ensures that logging is configured with defaults if not already configured.

    Args:
        name: The name of the logger

    Returns:
        A configured logger
    """
    # Check if logging is already configured
    if not _OPENMAS_LOGGING_CONFIGURED:
        # If configure_logging hasn't been called explicitly yet (e.g. by cli.main),
        # call it now with default WARNING level to ensure some configuration exists
        # before any logger is used.
        configure_logging()  # Defaults to WARNING

    return cast(BoundLogger, structlog.get_logger(name))
