"""Tests for src/openmas/communication/base.py."""

import logging

import pytest

from openmas.communication.base import (
    _COMMUNICATOR_REGISTRY,
    BaseCommunicator,
    get_available_communicator_types,
    get_communicator_class,
    register_communicator,
)


# Mock Communicator Classes
class MockCommA(BaseCommunicator):
    async def send_request(self, *args, **kwargs):
        pass

    async def send_notification(self, *args, **kwargs):
        pass

    async def register_handler(self, *args, **kwargs):
        pass

    async def start(self, *args, **kwargs):
        pass

    async def stop(self, *args, **kwargs):
        pass


class MockCommB(BaseCommunicator):
    async def send_request(self, *args, **kwargs):
        pass

    async def send_notification(self, *args, **kwargs):
        pass

    async def register_handler(self, *args, **kwargs):
        pass

    async def start(self, *args, **kwargs):
        pass

    async def stop(self, *args, **kwargs):
        pass


@pytest.fixture(autouse=True)
def clean_registry():
    """Ensures the registry is clean before and after each test."""
    original_registry = _COMMUNICATOR_REGISTRY.copy()
    _COMMUNICATOR_REGISTRY.clear()
    yield
    _COMMUNICATOR_REGISTRY.clear()
    _COMMUNICATOR_REGISTRY.update(original_registry)


def test_register_communicator_success():
    """Test successful registration."""
    register_communicator("type_a", MockCommA)
    assert "type_a" in _COMMUNICATOR_REGISTRY
    assert _COMMUNICATOR_REGISTRY["type_a"] is MockCommA


def test_register_communicator_overwrite_logs_warning(caplog):
    """Test that overwriting an existing registration logs a warning."""
    register_communicator("type_a", MockCommA)  # Initial registration
    with caplog.at_level(logging.WARNING):
        register_communicator("type_a", MockCommB)  # Overwrite

    assert "type_a" in _COMMUNICATOR_REGISTRY
    assert _COMMUNICATOR_REGISTRY["type_a"] is MockCommB  # Should be overwritten
    assert len(caplog.records) == 1
    assert "Communicator type already registered, overwriting" in caplog.text
    assert "old_class=MockCommA" in caplog.text
    assert "new_class=MockCommB" in caplog.text


def test_get_communicator_class_success():
    """Test successfully retrieving a registered class."""
    register_communicator("type_a", MockCommA)
    comm_class = get_communicator_class("type_a")
    assert comm_class is MockCommA


def test_get_communicator_class_not_found_raises_value_error():
    """Test that getting a non-existent type raises ValueError."""
    register_communicator("type_a", MockCommA)  # Register something else
    with pytest.raises(ValueError) as excinfo:
        get_communicator_class("type_b")

    assert "Communicator type 'type_b' not registered" in str(excinfo.value)
    assert "Available types: type_a" in str(excinfo.value)


def test_get_communicator_class_not_found_empty_registry():
    """Test ValueError message when the registry is empty."""
    with pytest.raises(ValueError) as excinfo:
        get_communicator_class("type_c")
    assert "Communicator type 'type_c' not registered" in str(excinfo.value)
    assert "Available types: none" in str(excinfo.value)


def test_get_available_communicator_types():
    """Test getting the dictionary of available types."""
    register_communicator("type_a", MockCommA)
    register_communicator("type_b", MockCommB)
    available = get_available_communicator_types()
    assert available == {"type_a": MockCommA, "type_b": MockCommB}
    # Ensure it's a copy
    available["new"] = None  # type: ignore
    assert "new" not in _COMMUNICATOR_REGISTRY


# --- Tests for BaseCommunicator ABC ---


# Create a simple implementation for testing
class ConcreteCommunicator(BaseCommunicator):
    """Concrete implementation of the BaseCommunicator for testing."""

    async def send_request(self, target_service, method, params=None, response_model=None, timeout=None):
        """Send a request to a target service."""
        return {"result": "test"}

    async def send_notification(self, target_service, method, params=None):
        """Send a notification to a target service."""
        pass

    async def register_handler(self, method, handler):
        """Register a handler for a method."""
        pass

    async def start(self):
        """Start the communicator."""
        pass

    async def stop(self):
        """Stop the communicator."""
        pass


def test_base_communicator_init():
    """Test base communicator initialization."""
    # Create a basic communicator
    agent_name = "test_agent"
    service_urls = {"service1": "http://service1:8080"}
    communicator = ConcreteCommunicator(agent_name, service_urls)

    # Check initialization
    assert communicator.agent_name == agent_name
    assert communicator.service_urls == service_urls
    assert communicator._server_mode is False
    assert communicator._server_instructions is None
    assert communicator._service_args == {}
    assert communicator.http_port is None


def test_base_communicator_init_with_optional_args():
    """Test base communicator initialization with optional arguments."""
    # Create a communicator with all optional args
    agent_name = "test_agent"
    service_urls = {"service1": "http://service1:8080"}
    server_mode = True
    server_instructions = "Test instructions"
    service_args = {"service1": ["--arg1", "--arg2"]}
    http_port = 8080

    communicator = ConcreteCommunicator(
        agent_name,
        service_urls,
        server_mode=server_mode,
        server_instructions=server_instructions,
        service_args=service_args,
        http_port=http_port,
    )

    # Check initialization
    assert communicator.agent_name == agent_name
    assert communicator.service_urls == service_urls
    assert communicator._server_mode is server_mode
    assert communicator._server_instructions == server_instructions
    assert communicator._service_args == service_args
    assert communicator.http_port == http_port
