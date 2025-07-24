# Observability Manager Interface

## 1. Overview

To ensure consistent and robust observability across the OpenMAS framework, a standardized set of interfaces is required for emitting telemetry data (logs, metrics, and traces). This document defines the `IObservabilityManager`, which acts as a central access point for all observability functions, and the specific interfaces for each telemetry type.

This approach decouples core components from any specific observability backend (e.g., OpenTelemetry, Prometheus, standard logging) and provides a consistent API for developers.

## 2. Core Interfaces

### 2.1. `ILogger` Interface

This interface defines a standard for structured logging.

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class ILogger(ABC):
    """An interface for structured logging."""

    @abstractmethod
    def debug(self, message: str, **kwargs: Any) -> None:
        """Logs a message with severity 'DEBUG'."""
        pass

    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        """Logs a message with severity 'INFO'."""
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs: Any) -> None:
        """Logs a message with severity 'WARNING'."""
        pass

    @abstractmethod
    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """Logs a message with severity 'ERROR'."""
        pass

    @abstractmethod
    def critical(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """Logs a message with severity 'CRITICAL'."""
        pass
```

### 2.2. `IMetrics` Interface

This interface provides methods for recording key performance indicators.

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class IMetrics(ABC):
    """An interface for recording metrics."""

    @abstractmethod
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] | None = None) -> None:
        """Increments a counter metric."""
        pass

    @abstractmethod
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] | None = None) -> None:
        """Sets a gauge metric to a specific value."""
        pass

    @abstractmethod
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] | None = None) -> None:
        """Records a value in a histogram."""
        pass
```

### 2.3. `ITracer` Interface

This interface provides a simplified way to create and manage spans for distributed tracing.

```python
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Iterator, Dict, Any

class ITracer(ABC):
    """An interface for creating trace spans."""

    @abstractmethod
    @contextmanager
    def start_span(self, name: str, attributes: Dict[str, Any] | None = None) -> Iterator[None]:
        """Starts a new trace span, to be used as a context manager."""
        yield
```

## 3. `IObservabilityManager` Facade

This is the main interface that components will interact with to get access to the telemetry emitters.

```python
from abc import ABC, abstractmethod

class IObservabilityManager(ABC):
    """A central facade for accessing observability tools."""

    @abstractmethod
    def get_logger(self, name: str) -> ILogger:
        """Gets a logger instance for a specific component.

        Args:
            name: The name of the logger, typically the component's module path.

        Returns:
            An object that implements the ILogger interface.
        """
        pass

    @abstractmethod
    def get_metrics(self, name: str) -> IMetrics:
        """Gets a metrics instance for a specific component.

        Args:
            name: The name of the metrics scope, typically the component's module path.

        Returns:
            An object that implements the IMetrics interface.
        """
        pass

    @abstractmethod
    def get_tracer(self, name: str) -> ITracer:
        """Gets a tracer instance for a specific component.

        Args:
            name: The name of the tracer, typically the component's module path.

        Returns:
            An object that implements the ITracer interface.
        """
        pass
```
