"""
Protocol-Specific Testing Utilities

Advanced protocol testing utilities for comprehensive OpenMAS protocol adapter testing.
Provides mock protocol servers, test harnesses, and protocol-specific testing patterns.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Callable, Optional, Union
from unittest.mock import AsyncMock, MagicMock
from contextlib import asynccontextmanager

from openmas.core.simf.models import SIMFMessage


class MockProtocolServer:
    """Mock protocol server for testing protocol adapters."""
    
    def __init__(self, protocol_type: str):
        self.protocol_type = protocol_type
        self.received_messages: List[Any] = []
        self.response_queue: asyncio.Queue = asyncio.Queue()
        self.message_handlers: Dict[str, Callable] = {}
        self.is_running = False
        self.connection_count = 0
        self.logger = logging.getLogger(f"MockProtocolServer.{protocol_type}")
    
    async def start(self) -> None:
        """Start the mock protocol server."""
        self.is_running = True
        self.logger.debug(f"Mock {self.protocol_type} server started")
    
    async def stop(self) -> None:
        """Stop the mock protocol server."""
        self.is_running = False
        self.logger.debug(f"Mock {self.protocol_type} server stopped")
    
    async def send_message(self, message: Any) -> None:
        """Simulate receiving a message from protocol adapter."""
        self.received_messages.append(message)
        self.logger.debug(f"Received message: {message}")
        
        # Process message through handlers if available
        message_type = self._extract_message_type(message)
        if message_type in self.message_handlers:
            handler = self.message_handlers[message_type]
            try:
                response = await handler(message) if asyncio.iscoroutinefunction(handler) else handler(message)
                if response:
                    await self.response_queue.put(response)
            except Exception as e:
                self.logger.error(f"Handler error for {message_type}: {e}")
    
    def _extract_message_type(self, message: Any) -> str:
        """Extract message type from protocol message."""
        if isinstance(message, dict):
            return message.get('type', message.get('method', 'unknown'))
        elif hasattr(message, 'message_type'):
            return str(message.message_type)
        else:
            return 'unknown'
    
    def add_message_handler(self, message_type: str, handler: Callable) -> None:
        """Add handler for specific message type."""
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Added handler for message type: {message_type}")
    
    async def get_next_response(self, timeout: float = 1.0) -> Any:
        """Get next response from queue."""
        try:
            return await asyncio.wait_for(self.response_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
    
    def get_received_messages(self) -> List[Any]:
        """Get copy of all received messages."""
        return self.received_messages.copy()
    
    def clear_messages(self) -> None:
        """Clear received messages."""
        self.received_messages.clear()


class ProtocolTestHarness:
    """Test harness for protocol adapter testing."""
    
    def __init__(self, adapter_class, server_class=None):
        self.adapter_class = adapter_class
        self.server_class = server_class or MockProtocolServer
        self.adapter = None
        self.server = None
        self.protocol_type = getattr(adapter_class, 'PROTOCOL_TYPE', 'unknown')
        self.logger = logging.getLogger(f"ProtocolTestHarness.{self.protocol_type}")
    
    async def setup(self) -> None:
        """Set up the test harness."""
        # Create mock server
        self.server = self.server_class(self.protocol_type)
        await self.server.start()
        
        # Create adapter instance
        self.adapter = self.adapter_class()
        
        # Connect adapter to mock server (implementation-specific)
        await self._connect_adapter_to_server()
        
        self.logger.debug(f"Test harness set up for {self.protocol_type}")
    
    async def teardown(self) -> None:
        """Tear down the test harness."""
        if self.server:
            await self.server.stop()
        
        if self.adapter and hasattr(self.adapter, 'stop'):
            await self.adapter.stop()
        
        self.logger.debug(f"Test harness torn down for {self.protocol_type}")
    
    async def _connect_adapter_to_server(self) -> None:
        """Connect adapter to mock server (override in subclasses)."""
        # Default implementation - may need protocol-specific overrides
        if hasattr(self.adapter, 'connect'):
            await self.adapter.connect(server=self.server)
    
    async def send_to_adapter(self, message: SIMFMessage) -> Any:
        """Send SIMF message to adapter."""
        if not self.adapter:
            raise RuntimeError("Test harness not set up")
        
        return await self.adapter.send_message(message)
    
    async def send_from_server(self, protocol_message: Any) -> None:
        """Send protocol-specific message from server."""
        if not self.server:
            raise RuntimeError("Test harness not set up")
        
        await self.server.send_message(protocol_message)
    
    def get_received_messages(self) -> List[Any]:
        """Get messages received by server."""
        if not self.server:
            return []
        return self.server.get_received_messages()
    
    def add_server_handler(self, message_type: str, handler: Callable) -> None:
        """Add message handler to mock server."""
        if self.server:
            self.server.add_message_handler(message_type, handler)
    
    @asynccontextmanager
    async def managed_harness(self):
        """Context manager for automatic setup/teardown."""
        try:
            await self.setup()
            yield self
        finally:
            await self.teardown()


class MCPTestHarness(ProtocolTestHarness):
    """Specialized test harness for MCP protocol testing."""
    
    def __init__(self, adapter_class):
        super().__init__(adapter_class)
        self.protocol_type = 'mcp'
    
    async def _connect_adapter_to_server(self) -> None:
        """MCP-specific connection setup."""
        # MCP adapters may need specific connection parameters
        if hasattr(self.adapter, 'initialize'):
            await self.adapter.initialize(mock_server=self.server)
    
    def create_mcp_tool_call(self, tool_name: str, **params) -> Dict[str, Any]:
        """Create MCP tool call message."""
        return {
            'method': 'tools/call',
            'params': {
                'name': tool_name,
                'arguments': params
            },
            'id': f"call_{int(time.time() * 1000)}"
        }
    
    def create_mcp_resource_request(self, resource_uri: str) -> Dict[str, Any]:
        """Create MCP resource request message."""
        return {
            'method': 'resources/read',
            'params': {
                'uri': resource_uri
            },
            'id': f"resource_{int(time.time() * 1000)}"
        }


class A2ATestHarness(ProtocolTestHarness):
    """Specialized test harness for Agent-to-Agent protocol testing."""
    
    def __init__(self, adapter_class):
        super().__init__(adapter_class)
        self.protocol_type = 'a2a'
    
    def create_a2a_message(self, from_agent: str, to_agent: str, content: str) -> Dict[str, Any]:
        """Create A2A protocol message."""
        return {
            'type': 'agent_message',
            'from': from_agent,
            'to': to_agent,
            'content': content,
            'timestamp': time.time()
        }


class HTTPTestHarness(ProtocolTestHarness):
    """Specialized test harness for HTTP protocol testing."""
    
    def __init__(self, adapter_class):
        super().__init__(adapter_class)
        self.protocol_type = 'http'
    
    def create_http_request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Create HTTP request message."""
        return {
            'method': method.upper(),
            'path': path,
            'headers': kwargs.get('headers', {}),
            'body': kwargs.get('body', ''),
            'query_params': kwargs.get('query_params', {})
        }


class MQTTTestHarness(ProtocolTestHarness):
    """Specialized test harness for MQTT protocol testing."""
    
    def __init__(self, adapter_class):
        super().__init__(adapter_class)
        self.protocol_type = 'mqtt'
    
    def create_mqtt_message(self, topic: str, payload: str, qos: int = 0) -> Dict[str, Any]:
        """Create MQTT message."""
        return {
            'topic': topic,
            'payload': payload,
            'qos': qos,
            'retain': False,
            'timestamp': time.time()
        }


# Utility functions for protocol testing

async def test_protocol_adapter_lifecycle(harness: ProtocolTestHarness) -> Dict[str, Any]:
    """Test protocol adapter lifecycle (start/stop)."""
    results = {
        'setup_success': False,
        'teardown_success': False,
        'errors': []
    }
    
    try:
        await harness.setup()
        results['setup_success'] = True
        
        await harness.teardown()
        results['teardown_success'] = True
        
    except Exception as e:
        results['errors'].append(str(e))
    
    return results


async def test_protocol_message_flow(
    harness: ProtocolTestHarness,
    simf_message: SIMFMessage,
    expected_protocol_message_type: str,
    timeout: float = 5.0
) -> Dict[str, Any]:
    """Test message flow from SIMF to protocol and back."""
    results = {
        'message_sent': False,
        'protocol_message_received': False,
        'message_type_correct': False,
        'response_received': False,
        'errors': []
    }
    
    try:
        async with harness.managed_harness():
            # Send SIMF message to adapter
            await harness.send_to_adapter(simf_message)
            results['message_sent'] = True
            
            # Check if protocol message was received by server
            await asyncio.sleep(0.1)  # Allow processing time
            received_messages = harness.get_received_messages()
            
            if received_messages:
                results['protocol_message_received'] = True
                
                # Check message type
                last_message = received_messages[-1]
                message_type = harness.server._extract_message_type(last_message)
                if message_type == expected_protocol_message_type:
                    results['message_type_correct'] = True
            
            # Test response flow if applicable
            if harness.server.response_queue.qsize() > 0:
                response = await harness.server.get_next_response(timeout)
                if response:
                    results['response_received'] = True
    
    except Exception as e:
        results['errors'].append(str(e))
    
    return results


# Factory functions for creating test harnesses

def create_protocol_harness(protocol_type: str, adapter_class) -> ProtocolTestHarness:
    """Factory function to create appropriate protocol test harness."""
    harness_map = {
        'mcp': MCPTestHarness,
        'a2a': A2ATestHarness,
        'http': HTTPTestHarness,
        'mqtt': MQTTTestHarness
    }
    
    harness_class = harness_map.get(protocol_type.lower(), ProtocolTestHarness)
    return harness_class(adapter_class)


def get_protocol_test_patterns(protocol_type: str) -> Dict[str, Callable]:
    """Get protocol-specific test patterns."""
    patterns = {
        'lifecycle': test_protocol_adapter_lifecycle,
        'message_flow': test_protocol_message_flow,
    }
    
    # Add protocol-specific patterns
    if protocol_type.lower() == 'mcp':
        patterns.update({
            'tool_call': lambda h, tool, **params: test_protocol_message_flow(
                h, create_mcp_tool_call_message(tool, **params), 'tools/call'
            ),
            'resource_request': lambda h, uri: test_protocol_message_flow(
                h, create_mcp_resource_message(uri), 'resources/read'
            )
        })
    
    return patterns


# Helper functions for creating protocol-specific SIMF messages

def create_mcp_tool_call_message(tool_name: str, **params) -> SIMFMessage:
    """Create SIMF message for MCP tool call."""
    from openmas.core.simf.models import create_invocation_message
    
    return create_invocation_message(
        invocation_type="tool_call",
        target=tool_name,
        parameters=params,
        sender_id="test_sender",
        recipient_id="test_recipient",
        conversation_id="test_conversation",
        protocol_metadata={"protocol": "mcp", "tool_name": tool_name}
    )


def create_mcp_resource_message(resource_uri: str) -> SIMFMessage:
    """Create SIMF message for MCP resource request."""
    from openmas.core.simf.models import create_invocation_message
    
    return create_invocation_message(
        invocation_type="resource_request",
        target=resource_uri,
        parameters={},
        sender_id="test_sender",
        recipient_id="test_recipient",
        conversation_id="test_conversation",
        protocol_metadata={"protocol": "mcp", "resource_uri": resource_uri}
    )
