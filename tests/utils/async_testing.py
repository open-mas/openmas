"""
Advanced Async Testing Utilities

Sophisticated async testing utilities for OpenMAS comprehensive testing framework.
Provides network mocking, condition waiting, resource management, and async coordination patterns.
"""

import asyncio
import time
import logging
from typing import Any, Callable, Awaitable, Optional, Dict, List, Union
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from tests.utils.test_supervisor import TestSupervisor


@dataclass
class AsyncCondition:
    """Represents an async condition to wait for."""
    name: str
    predicate: Callable[[], Union[bool, Awaitable[bool]]]
    timeout: float = 10.0
    check_interval: float = 0.1
    description: str = ""


class AsyncConditionWaiter:
    """Advanced async condition waiting with timeout and logging."""
    
    def __init__(self, logger_name: str = "AsyncConditionWaiter"):
        self.logger = logging.getLogger(logger_name)
        self.active_conditions: Dict[str, AsyncCondition] = {}
    
    async def wait_for_condition(
        self,
        condition: AsyncCondition,
        supervisor: Optional[TestSupervisor] = None
    ) -> bool:
        """Wait for an async condition to be met."""
        self.active_conditions[condition.name] = condition
        start_time = time.time()
        
        self.logger.debug(f"Waiting for condition: {condition.name} - {condition.description}")
        
        if supervisor:
            await supervisor._emit_event("condition_wait_started", {
                "condition_name": condition.name,
                "timeout": condition.timeout
            })
        
        try:
            while time.time() - start_time < condition.timeout:
                try:
                    # Evaluate predicate (sync or async)
                    if asyncio.iscoroutinefunction(condition.predicate):
                        result = await condition.predicate()
                    else:
                        result = condition.predicate()
                    
                    if result:
                        elapsed = time.time() - start_time
                        self.logger.debug(f"Condition met: {condition.name} (after {elapsed:.2f}s)")
                        
                        if supervisor:
                            await supervisor._emit_event("condition_wait_completed", {
                                "condition_name": condition.name,
                                "elapsed_time": elapsed
                            })
                        
                        return True
                    
                    await asyncio.sleep(condition.check_interval)
                    
                except Exception as e:
                    self.logger.error(f"Error checking condition {condition.name}: {e}")
                    if supervisor:
                        await supervisor._emit_event("condition_wait_error", {
                            "condition_name": condition.name,
                            "error": str(e)
                        })
                    raise
            
            # Timeout reached
            elapsed = time.time() - start_time
            self.logger.warning(f"Condition timeout: {condition.name} (after {elapsed:.2f}s)")
            
            if supervisor:
                await supervisor._emit_event("condition_wait_timeout", {
                    "condition_name": condition.name,
                    "elapsed_time": elapsed
                })
            
            return False
            
        finally:
            self.active_conditions.pop(condition.name, None)
    
    async def wait_for_multiple_conditions(
        self,
        conditions: List[AsyncCondition],
        require_all: bool = True,
        supervisor: Optional[TestSupervisor] = None
    ) -> Dict[str, bool]:
        """Wait for multiple conditions (all or any)."""
        results = {}
        
        if require_all:
            # Wait for all conditions sequentially
            for condition in conditions:
                results[condition.name] = await self.wait_for_condition(condition, supervisor)
                if not results[condition.name]:
                    break  # Stop on first failure
        else:
            # Wait for any condition (race)
            tasks = [
                asyncio.create_task(self.wait_for_condition(condition, supervisor))
                for condition in conditions
            ]
            
            try:
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=max(c.timeout for c in conditions)
                )
                
                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                
                # Collect results
                for i, task in enumerate(tasks):
                    condition_name = conditions[i].name
                    if task in done:
                        results[condition_name] = await task
                    else:
                        results[condition_name] = False
                        
            except asyncio.TimeoutError:
                for condition in conditions:
                    results[condition.name] = False
        
        return results


class NetworkMockManager:
    """Advanced network mocking for protocol testing."""
    
    def __init__(self):
        self.active_mocks: Dict[str, Any] = {}
        self.request_log: List[Dict[str, Any]] = []
        self.response_handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("NetworkMockManager")
    
    @asynccontextmanager
    async def mock_http_server(
        self,
        host: str = "localhost",
        port: int = 8080,
        responses: Optional[Dict[str, Any]] = None
    ):
        """Mock HTTP server for testing HTTP protocol adapters."""
        server_id = f"http_{host}_{port}"
        
        # Create mock server
        mock_server = AsyncMock()
        mock_server.host = host
        mock_server.port = port
        mock_server.responses = responses or {}
        
        # Set up request handling
        async def handle_request(method: str, path: str, **kwargs):
            request_data = {
                "method": method,
                "path": path,
                "timestamp": time.time(),
                **kwargs
            }
            self.request_log.append(request_data)
            
            # Find matching response
            response_key = f"{method.upper()} {path}"
            if response_key in mock_server.responses:
                return mock_server.responses[response_key]
            elif path in mock_server.responses:
                return mock_server.responses[path]
            else:
                return {"status": 404, "body": "Not Found"}
        
        mock_server.handle_request = handle_request
        self.active_mocks[server_id] = mock_server
        
        try:
            self.logger.debug(f"Started mock HTTP server: {host}:{port}")
            yield mock_server
        finally:
            self.active_mocks.pop(server_id, None)
            self.logger.debug(f"Stopped mock HTTP server: {host}:{port}")
    
    @asynccontextmanager
    async def mock_websocket_server(
        self,
        host: str = "localhost",
        port: int = 8081
    ):
        """Mock WebSocket server for testing WebSocket-based protocols."""
        server_id = f"ws_{host}_{port}"
        
        mock_server = AsyncMock()
        mock_server.host = host
        mock_server.port = port
        mock_server.connected_clients = []
        mock_server.message_queue = asyncio.Queue()
        
        async def send_message(client_id: str, message: Any):
            await mock_server.message_queue.put({
                "client_id": client_id,
                "message": message,
                "timestamp": time.time()
            })
        
        mock_server.send_message = send_message
        self.active_mocks[server_id] = mock_server
        
        try:
            self.logger.debug(f"Started mock WebSocket server: {host}:{port}")
            yield mock_server
        finally:
            self.active_mocks.pop(server_id, None)
            self.logger.debug(f"Stopped mock WebSocket server: {host}:{port}")
    
    def get_request_log(self, server_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get request log for analysis."""
        if server_id:
            return [req for req in self.request_log if req.get("server_id") == server_id]
        return self.request_log.copy()
    
    def clear_request_log(self):
        """Clear request log."""
        self.request_log.clear()


class AsyncResourceManager:
    """Advanced async resource management for testing."""
    
    def __init__(self, supervisor: Optional[TestSupervisor] = None):
        self.supervisor = supervisor
        self.managed_resources: Dict[str, Any] = {}
        self.cleanup_callbacks: Dict[str, Callable] = {}
        self.logger = logging.getLogger("AsyncResourceManager")
    
    async def manage_resource(
        self,
        resource_id: str,
        resource_factory: Callable[[], Awaitable[Any]],
        cleanup_callback: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> Any:
        """Create and manage an async resource."""
        if resource_id in self.managed_resources:
            self.logger.warning(f"Resource {resource_id} already managed")
            return self.managed_resources[resource_id]
        
        try:
            # Create resource
            resource = await resource_factory()
            self.managed_resources[resource_id] = resource
            
            if cleanup_callback:
                self.cleanup_callbacks[resource_id] = cleanup_callback
            
            # Register with supervisor if available
            if self.supervisor:
                self.supervisor.register_resource(
                    resource_id=resource_id,
                    resource=resource,
                    resource_type="async_managed",
                    cleanup_callback=lambda r: self._cleanup_resource(resource_id)
                )
            
            self.logger.debug(f"Created managed resource: {resource_id}")
            return resource
            
        except Exception as e:
            self.logger.error(f"Failed to create resource {resource_id}: {e}")
            raise
    
    async def _cleanup_resource(self, resource_id: str) -> None:
        """Clean up a managed resource."""
        if resource_id not in self.managed_resources:
            return
        
        resource = self.managed_resources[resource_id]
        cleanup_callback = self.cleanup_callbacks.get(resource_id)
        
        try:
            if cleanup_callback:
                await cleanup_callback(resource)
            elif hasattr(resource, 'close'):
                if asyncio.iscoroutinefunction(resource.close):
                    await resource.close()
                else:
                    resource.close()
            elif hasattr(resource, 'stop'):
                if asyncio.iscoroutinefunction(resource.stop):
                    await resource.stop()
                else:
                    resource.stop()
            
            self.logger.debug(f"Cleaned up resource: {resource_id}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up resource {resource_id}: {e}")
        finally:
            self.managed_resources.pop(resource_id, None)
            self.cleanup_callbacks.pop(resource_id, None)
    
    async def cleanup_all(self) -> None:
        """Clean up all managed resources."""
        cleanup_tasks = []
        for resource_id in list(self.managed_resources.keys()):
            cleanup_tasks.append(self._cleanup_resource(resource_id))
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
    
    @asynccontextmanager
    async def managed_context(self):
        """Context manager for automatic resource cleanup."""
        try:
            yield self
        finally:
            await self.cleanup_all()


class AsyncTestCoordinator:
    """Advanced async test coordination patterns."""
    
    def __init__(self, supervisor: TestSupervisor):
        self.supervisor = supervisor
        self.condition_waiter = AsyncConditionWaiter("AsyncTestCoordinator")
        self.network_mock = NetworkMockManager()
        self.resource_manager = AsyncResourceManager(supervisor)
        self.logger = logging.getLogger("AsyncTestCoordinator")
    
    async def coordinate_multi_agent_test(
        self,
        agents: Dict[str, Any],
        test_scenario: Callable[[Dict[str, Any]], Awaitable[Any]],
        timeout: float = 60.0
    ) -> Any:
        """Coordinate complex multi-agent test scenarios."""
        await self.supervisor._emit_event("multi_agent_coordination_started", {
            "agent_count": len(agents),
            "timeout": timeout
        })
        
        try:
            # Ensure all agents are ready
            ready_condition = AsyncCondition(
                name="all_agents_ready",
                predicate=lambda: all(
                    hasattr(agent, 'is_running') and agent.is_running 
                    for agent in agents.values()
                ),
                timeout=30.0,
                description="All agents are running and ready"
            )
            
            agents_ready = await self.condition_waiter.wait_for_condition(
                ready_condition, self.supervisor
            )
            
            if not agents_ready:
                raise RuntimeError("Not all agents became ready within timeout")
            
            # Execute test scenario
            result = await self.supervisor.execute_test_phase(
                test_scenario,
                timeout=timeout,
                agents=agents
            )
            
            await self.supervisor._emit_event("multi_agent_coordination_completed", {
                "result": str(result)
            })
            
            return result
            
        except Exception as e:
            await self.supervisor._emit_event("multi_agent_coordination_failed", {
                "error": str(e)
            })
            raise
    
    async def test_protocol_integration(
        self,
        protocol_adapters: Dict[str, Any],
        integration_scenario: Callable[[Dict[str, Any]], Awaitable[Any]],
        timeout: float = 30.0
    ) -> Any:
        """Test protocol integration scenarios."""
        await self.supervisor._emit_event("protocol_integration_started", {
            "protocol_count": len(protocol_adapters),
            "protocols": list(protocol_adapters.keys())
        })
        
        try:
            # Test each protocol adapter individually first
            for protocol_name, adapter in protocol_adapters.items():
                adapter_ready = AsyncCondition(
                    name=f"{protocol_name}_ready",
                    predicate=lambda a=adapter: hasattr(a, 'is_connected') and a.is_connected,
                    timeout=10.0,
                    description=f"{protocol_name} adapter is connected and ready"
                )
                
                ready = await self.condition_waiter.wait_for_condition(
                    adapter_ready, self.supervisor
                )
                
                if not ready:
                    raise RuntimeError(f"Protocol adapter {protocol_name} not ready")
            
            # Execute integration scenario
            result = await self.supervisor.execute_test_phase(
                integration_scenario,
                timeout=timeout,
                protocol_adapters=protocol_adapters
            )
            
            await self.supervisor._emit_event("protocol_integration_completed", {
                "result": str(result)
            })
            
            return result
            
        except Exception as e:
            await self.supervisor._emit_event("protocol_integration_failed", {
                "error": str(e)
            })
            raise


# Utility functions for common async testing patterns

async def wait_for_agent_state(
    agent: Any,
    expected_state: str,
    timeout: float = 10.0,
    supervisor: Optional[TestSupervisor] = None
) -> bool:
    """Wait for agent to reach expected state."""
    condition = AsyncCondition(
        name=f"agent_{agent.agent_id}_state_{expected_state}",
        predicate=lambda: getattr(agent, 'state', None) == expected_state,
        timeout=timeout,
        description=f"Agent {agent.agent_id} reaches state {expected_state}"
    )
    
    waiter = AsyncConditionWaiter()
    return await waiter.wait_for_condition(condition, supervisor)


async def wait_for_message_exchange(
    sender: Any,
    receiver: Any,
    message_count: int = 1,
    timeout: float = 10.0,
    supervisor: Optional[TestSupervisor] = None
) -> bool:
    """Wait for message exchange between agents."""
    condition = AsyncCondition(
        name=f"message_exchange_{sender.agent_id}_to_{receiver.agent_id}",
        predicate=lambda: (
            hasattr(receiver, 'received_messages') and 
            len(receiver.received_messages) >= message_count
        ),
        timeout=timeout,
        description=f"Message exchange: {sender.agent_id} -> {receiver.agent_id} ({message_count} messages)"
    )
    
    waiter = AsyncConditionWaiter()
    return await waiter.wait_for_condition(condition, supervisor)


async def wait_for_protocol_connection(
    adapter: Any,
    timeout: float = 10.0,
    supervisor: Optional[TestSupervisor] = None
) -> bool:
    """Wait for protocol adapter to establish connection."""
    condition = AsyncCondition(
        name=f"protocol_connection_{type(adapter).__name__}",
        predicate=lambda: hasattr(adapter, 'is_connected') and adapter.is_connected,
        timeout=timeout,
        description=f"Protocol adapter {type(adapter).__name__} establishes connection"
    )
    
    waiter = AsyncConditionWaiter()
    return await waiter.wait_for_condition(condition, supervisor)


@asynccontextmanager
async def async_test_environment(
    supervisor: TestSupervisor,
    setup_resources: Optional[Callable[[], Awaitable[Dict[str, Any]]]] = None
):
    """Comprehensive async test environment context manager."""
    coordinator = AsyncTestCoordinator(supervisor)
    
    try:
        # Set up resources if provided
        resources = {}
        if setup_resources:
            resources = await setup_resources()
            
            # Register resources with supervisor
            for resource_id, resource in resources.items():
                supervisor.register_resource(
                    resource_id=resource_id,
                    resource=resource,
                    resource_type="test_environment"
                )
        
        yield {
            'coordinator': coordinator,
            'resources': resources,
            'condition_waiter': coordinator.condition_waiter,
            'network_mock': coordinator.network_mock,
            'resource_manager': coordinator.resource_manager
        }
        
    finally:
        # Cleanup handled by supervisor and resource manager
        await coordinator.resource_manager.cleanup_all()
