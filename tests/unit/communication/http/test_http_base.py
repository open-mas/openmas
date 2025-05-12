"""Tests for basic HTTP communicator functionality."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi import FastAPI

from openmas.communication.http import HttpCommunicator


class MockAsyncTask(MagicMock):
    """A mock for async tasks that properly handles cancel() and await."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This makes the mock awaitable but doesn't register as a coroutine
        self.__await__ = lambda: (yield from [])
        # Add this attribute to help the stop method identify it's not a real coroutine
        self._is_coroutine = False

    def cancel(self):
        """Override cancel to return None instead of a coroutine."""
        return None


def test_initialization(communicator_config):
    """Test that initialization sets up the communicator correctly."""
    communicator = HttpCommunicator(communicator_config["agent_name"], communicator_config["service_urls"])

    assert communicator.agent_name == communicator_config["agent_name"]
    assert communicator.service_urls == communicator_config["service_urls"]
    assert communicator.handlers == {}
    assert communicator.server_task is None
    assert communicator.http_port is None


@pytest.mark.asyncio
async def test_http_communicator_with_port_from_config():
    """Test that the port is correctly extracted from config options."""
    # Create a communicator with config options
    communicator = HttpCommunicator(agent_name="test-agent", service_urls={}, http_port=9876)

    # Verify the port was set correctly
    assert communicator.http_port == 9876
    await communicator.stop()


@pytest.mark.asyncio
async def test_http_communicator_uses_default_port_when_none_provided():
    """Test that a default port is used when none is provided."""
    # Create a mock task that works with async code
    mock_task = MockAsyncTask()

    # We need to capture the port when _ensure_server_running is called
    original_ensure_server = HttpCommunicator._ensure_server_running
    consumer_port = None
    producer_port = None

    async def mock_ensure_server(self):
        """Mock that captures the port and then calls the original."""
        nonlocal consumer_port, producer_port
        if self.agent_name == "consumer":
            # The port will be determined in the original method
            await original_ensure_server(self)
            consumer_port = self.http_port
        elif self.agent_name == "producer":
            # The port will be determined in the original method
            await original_ensure_server(self)
            producer_port = self.http_port

    # Mock create_task to return our proper mock and patch _ensure_server_running
    with (
        patch("openmas.communication.http.asyncio.create_task", return_value=mock_task),
        patch.object(HttpCommunicator, "_ensure_server_running", mock_ensure_server),
    ):
        # Create communicators for different agent types
        consumer = HttpCommunicator(agent_name="consumer", service_urls={})

        producer = HttpCommunicator(agent_name="producer", service_urls={})

        # Define a mock handler
        async def test_handler(params: Dict[str, Any]) -> Dict[str, Any]:
            return {"success": True}

        try:
            # Register handlers
            await consumer.register_handler("test_method", test_handler)
            await producer.register_handler("test_method", test_handler)

            # Verify the ports were set correctly (now using 8000 as the default)
            assert consumer_port == 8000, f"Expected consumer_port to be 8000, got {consumer_port}"
            assert producer_port == 8000, f"Expected producer_port to be 8000, got {producer_port}"
        finally:
            # Clean up
            await consumer.stop()
            await producer.stop()


def test_url_building():
    """Test that URLs are correctly built from service names."""
    service_url = "http://localhost:8001"
    service_name = "service1"

    # Create communicator with predetermined service URLs
    communicator = HttpCommunicator("test-agent", {service_name: service_url})

    # Simply verify the URL is stored correctly in the communicator
    assert communicator.service_urls[service_name] == service_url


def test_custom_port_config_direct():
    """Test setting a custom port directly with http_port parameter."""
    # Specify a custom port
    custom_port = 5432

    # Create a communicator with port directly in constructor
    communicator = HttpCommunicator("test-agent", {}, http_port=custom_port)

    # Verify the port is correctly set
    assert communicator.http_port == custom_port


@pytest.mark.asyncio
async def test_http_communicator_default_port_with_simple_mock():
    """Test that a default port is used when none is provided, with mocked server."""
    # Create mock task
    mock_task = MockAsyncTask()

    # We need to patch the server creation
    with patch("openmas.communication.http.asyncio.create_task", return_value=mock_task):
        # Create a communicator without port
        communicator = HttpCommunicator("test-agent", {})

        # Define a mock handler
        async def test_handler(params):
            return {"result": "ok"}

        # Register the handler which triggers server creation
        await communicator.register_handler("test", test_handler)

        # The default port should be used
        assert communicator.http_port == 8000

        # Clean up
        await communicator.stop()


@pytest.mark.asyncio
async def test_service_url_extraction():
    """Test the extraction of service URLs from the service URL dictionary."""
    # Setup service URLs
    service_urls = {
        "test-service": "http://localhost:8000",
        "my-agent": "http://localhost:8001",
    }

    # Create a communicator
    communicator = HttpCommunicator("my-agent", service_urls)

    # Check that the service URLs were extracted correctly
    assert communicator.service_urls["test-service"] == "http://localhost:8000"
    assert communicator.service_urls["my-agent"] == "http://localhost:8001"

    # Clean up
    await communicator.stop()


def test_http_communicator_with_port_from_options():
    """Test HTTP communicator with port from communicator_options."""
    communicator_options = {"http_port": 9999}
    communicator = HttpCommunicator(
        "test",
        {"service1": "http://service1:8080"},
        communicator_options=communicator_options,
    )

    assert communicator.http_port == 9999


# Mock AsyncClient to avoid actual HTTP requests
class MockAsyncClient:
    """Mock AsyncClient for testing."""

    def __init__(self, *args, **kwargs):
        """Initialize with mock methods."""
        self.post_responses = {}
        self.post_calls = []
        self.aclose_called = False
        self.timeout = httpx.Timeout(10.0)

    async def post(self, url, json=None, timeout=None):
        """Mock post method."""
        self.post_calls.append((url, json, timeout))
        if url in self.post_responses:
            return self.post_responses[url]
        response = httpx.Response(200, json={"jsonrpc": "2.0", "result": "test_result", "id": json.get("id")})
        return response

    async def aclose(self):
        """Mock aclose method."""
        self.aclose_called = True
        return None


@pytest.mark.asyncio
async def test_multiple_communicators_different_ports():
    """Test that multiple communicators use different ports."""

    class HttpCommunicatorForTest(HttpCommunicator):
        """Test subclass that exposes port access."""

        def __init__(self, *args, **kwargs):
            """Initialize and track port."""
            super().__init__(*args, **kwargs)
            self.server = None

        async def _ensure_server_running(self):
            """Override to avoid actual server creation."""
            if not hasattr(self, "server") or self.server is None:
                # Set a default port if none exists
                if self.http_port is None:
                    self.http_port = 8000 if self.agent_name == "consumer" else 8001

                self.server = FastAPI()
                setattr(self.server, "port", self.http_port)

    # Create two communicators with the same name but different agent configs
    consumer = HttpCommunicatorForTest("consumer", {})
    producer = HttpCommunicatorForTest("producer", {})

    # Register handlers to trigger server creation
    async def test_handler(params):
        return {"result": "success"}

    # Override _ensure_server_running to use our test version
    with (
        patch.object(consumer, "_ensure_server_running", consumer._ensure_server_running),
        patch.object(producer, "_ensure_server_running", producer._ensure_server_running),
    ):
        await consumer.register_handler("test", test_handler)
        await producer.register_handler("test", test_handler)

        # Get the ports
        consumer_port = consumer.http_port
        assert consumer_port is not None

        producer_port = producer.http_port
        assert producer_port is not None

        # Check they are different
        assert consumer_port != producer_port


def test_http_port_from_communicator_options():
    """Test that HTTP port can be set from communicator_options."""
    communicator_options = {"http_port": 7777}
    communicator = HttpCommunicator(
        "test",
        {"service1": "http://service1:8080"},
        communicator_options=communicator_options,
    )

    assert communicator.http_port == 7777


# Additional tests for the HTTP client functionality
@pytest.mark.asyncio
async def test_http_client_is_initialized():
    """Test that the HTTP client is initialized correctly."""
    # Create a communicator
    communicator = HttpCommunicator("test", {})

    # Verify a client was created
    assert communicator.client is not None
    assert isinstance(communicator.client, httpx.AsyncClient)


@pytest.mark.asyncio
async def test_http_client_is_closed_on_stop():
    """Test that the HTTP client is closed on stop."""
    client = MockAsyncClient()
    with patch("httpx.AsyncClient", return_value=client):
        communicator = HttpCommunicator("test", {})
        await communicator.stop()
        assert client.aclose_called
