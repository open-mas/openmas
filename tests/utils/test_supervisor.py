"""
TestSupervisor: Advanced async test coordination for OpenMAS agent testing.

This module provides sophisticated async lifecycle management, event-based coordination,
timeout management, and resource cleanup for reliable agent testing.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Set, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum

from openmas.agent.base_agent import Agent
from openmas.core.simf.models import SIMFMessage


class TestPhase(Enum):
    """Test execution phases for coordination."""
    SETUP = "setup"
    EXECUTION = "execution"
    CLEANUP = "cleanup"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TestResource:
    """Represents a test resource that needs lifecycle management."""
    resource_id: str
    resource_type: str
    resource: Any
    cleanup_callback: Optional[Callable] = None
    created_at: float = field(default_factory=time.time)
    is_cleaned: bool = False


@dataclass
class TestEvent:
    """Event for test coordination."""
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class TestSupervisor:
    """
    Advanced async test coordinator for OpenMAS agent testing.
    
    Provides:
    - Event-based test orchestration
    - Timeout management with configurable limits
    - Resource isolation and automatic cleanup
    - Agent lifecycle management
    - Async test fixtures with proper cleanup
    """
    
    def __init__(
        self,
        test_name: str,
        default_timeout: float = 30.0,
        cleanup_timeout: float = 10.0,
        enable_logging: bool = True
    ):
        self.test_name = test_name
        self.default_timeout = default_timeout
        self.cleanup_timeout = cleanup_timeout
        self.enable_logging = enable_logging
        
        # State management
        self.current_phase = TestPhase.SETUP
        self.start_time = time.time()
        self.resources: Dict[str, TestResource] = {}
        self.agents: Dict[str, Agent] = {}
        self.events: List[TestEvent] = []
        self.event_waiters: Dict[str, List[asyncio.Event]] = {}
        
        # Async coordination
        self.phase_events: Dict[TestPhase, asyncio.Event] = {
            phase: asyncio.Event() for phase in TestPhase
        }
        self.cleanup_tasks: Set[asyncio.Task] = set()
        
        # Logging
        self.logger = logging.getLogger(f"TestSupervisor.{test_name}")
        if enable_logging:
            self.logger.setLevel(logging.DEBUG)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._transition_to_phase(TestPhase.SETUP)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with guaranteed cleanup."""
        if exc_type:
            await self._transition_to_phase(TestPhase.FAILED)
            self.logger.error(f"Test failed with {exc_type.__name__}: {exc_val}")
        
        await self._transition_to_phase(TestPhase.CLEANUP)
        await self._cleanup_all_resources()
        await self._transition_to_phase(TestPhase.COMPLETED)
        
        # Wait for any remaining cleanup tasks
        if self.cleanup_tasks:
            await asyncio.gather(*self.cleanup_tasks, return_exceptions=True)
    
    async def _transition_to_phase(self, new_phase: TestPhase) -> None:
        """Transition to a new test phase with event coordination."""
        old_phase = self.current_phase
        self.current_phase = new_phase
        
        self.logger.debug(f"Phase transition: {old_phase.value} -> {new_phase.value}")
        
        # Signal phase transition
        self.phase_events[new_phase].set()
        
        # Emit phase event
        await self._emit_event("phase_transition", {
            "old_phase": old_phase.value,
            "new_phase": new_phase.value,
            "elapsed_time": time.time() - self.start_time
        })
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Emit an event for test coordination."""
        event = TestEvent(event_type=event_type, data=data or {})
        self.events.append(event)
        
        self.logger.debug(f"Event emitted: {event_type} - {data}")
        
        # Notify event waiters
        if event_type in self.event_waiters:
            for waiter in self.event_waiters[event_type]:
                waiter.set()
    
    async def wait_for_event(
        self,
        event_type: str,
        timeout: Optional[float] = None,
        predicate: Optional[Callable[[TestEvent], bool]] = None
    ) -> Optional[TestEvent]:
        """Wait for a specific event with optional predicate."""
        timeout = timeout or self.default_timeout
        
        # Check if event already exists
        for event in reversed(self.events):
            if event.event_type == event_type:
                if predicate is None or predicate(event):
                    return event
        
        # Set up waiter
        waiter = asyncio.Event()
        if event_type not in self.event_waiters:
            self.event_waiters[event_type] = []
        self.event_waiters[event_type].append(waiter)
        
        try:
            await asyncio.wait_for(waiter.wait(), timeout=timeout)
            
            # Find the matching event
            for event in reversed(self.events):
                if event.event_type == event_type:
                    if predicate is None or predicate(event):
                        return event
            
            return None
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout waiting for event: {event_type}")
            return None
        finally:
            # Clean up waiter
            if event_type in self.event_waiters:
                try:
                    self.event_waiters[event_type].remove(waiter)
                except ValueError:
                    pass
    
    async def wait_for_phase(self, phase: TestPhase, timeout: Optional[float] = None) -> bool:
        """Wait for a specific test phase."""
        timeout = timeout or self.default_timeout
        
        if self.current_phase == phase:
            return True
        
        try:
            await asyncio.wait_for(self.phase_events[phase].wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout waiting for phase: {phase.value}")
            return False
    
    def register_resource(
        self,
        resource_id: str,
        resource: Any,
        resource_type: str = "generic",
        cleanup_callback: Optional[Callable] = None
    ) -> None:
        """Register a resource for lifecycle management."""
        test_resource = TestResource(
            resource_id=resource_id,
            resource_type=resource_type,
            resource=resource,
            cleanup_callback=cleanup_callback
        )
        
        self.resources[resource_id] = test_resource
        self.logger.debug(f"Registered resource: {resource_id} ({resource_type})")
    
    async def register_agent(
        self,
        agent_id: str,
        agent: Agent,
        auto_start: bool = True,
        auto_cleanup: bool = True
    ) -> Agent:
        """Register an agent with automatic lifecycle management."""
        self.agents[agent_id] = agent
        
        # Register as resource for cleanup
        if auto_cleanup:
            self.register_resource(
                resource_id=f"agent_{agent_id}",
                resource=agent,
                resource_type="agent",
                cleanup_callback=self._cleanup_agent
            )
        
        # Auto-start if requested
        if auto_start:
            await agent.start()
            await self._emit_event("agent_started", {"agent_id": agent_id})
        
        self.logger.debug(f"Registered agent: {agent_id}")
        return agent
    
    async def _cleanup_agent(self, agent: Agent) -> None:
        """Clean up an agent resource."""
        try:
            if agent.is_running:
                await agent.stop()
                self.logger.debug(f"Stopped agent: {agent.agent_id}")
        except Exception as e:
            self.logger.error(f"Error stopping agent {agent.agent_id}: {e}")
    
    async def _cleanup_resource(self, resource: TestResource) -> None:
        """Clean up a single resource."""
        if resource.is_cleaned:
            return
        
        try:
            if resource.cleanup_callback:
                if asyncio.iscoroutinefunction(resource.cleanup_callback):
                    await resource.cleanup_callback(resource.resource)
                else:
                    resource.cleanup_callback(resource.resource)
            
            resource.is_cleaned = True
            self.logger.debug(f"Cleaned up resource: {resource.resource_id}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up resource {resource.resource_id}: {e}")
    
    async def _cleanup_all_resources(self) -> None:
        """Clean up all registered resources."""
        cleanup_tasks = []
        
        # Clean up agents first (they may have dependencies)
        agent_resources = [r for r in self.resources.values() if r.resource_type == "agent"]
        for resource in agent_resources:
            cleanup_tasks.append(self._cleanup_resource(resource))
        
        # Clean up other resources
        other_resources = [r for r in self.resources.values() if r.resource_type != "agent"]
        for resource in other_resources:
            cleanup_tasks.append(self._cleanup_resource(resource))
        
        if cleanup_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*cleanup_tasks, return_exceptions=True),
                    timeout=self.cleanup_timeout
                )
            except asyncio.TimeoutError:
                self.logger.warning("Cleanup timeout - some resources may not be properly cleaned")
    
    async def execute_test_phase(
        self,
        phase_func: Callable,
        timeout: Optional[float] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute a test phase with timeout and error handling."""
        timeout = timeout or self.default_timeout
        
        await self._transition_to_phase(TestPhase.EXECUTION)
        
        try:
            if asyncio.iscoroutinefunction(phase_func):
                result = await asyncio.wait_for(
                    phase_func(*args, **kwargs),
                    timeout=timeout
                )
            else:
                result = phase_func(*args, **kwargs)
            
            await self._emit_event("phase_completed", {"result": str(result)})
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"Test phase timed out after {timeout}s")
            raise
        except Exception as e:
            self.logger.error(f"Test phase failed: {e}")
            raise
    
    @asynccontextmanager
    async def agent_lifecycle(
        self,
        agent: Agent,
        agent_id: Optional[str] = None,
        auto_start: bool = True
    ) -> AsyncGenerator[Agent, None]:
        """Context manager for agent lifecycle with guaranteed cleanup."""
        agent_id = agent_id or agent.agent_id
        
        try:
            registered_agent = await self.register_agent(
                agent_id=agent_id,
                agent=agent,
                auto_start=auto_start,
                auto_cleanup=True
            )
            yield registered_agent
        finally:
            # Explicit cleanup (in addition to automatic cleanup)
            try:
                if agent.is_running:
                    await agent.stop()
            except Exception as e:
                self.logger.error(f"Error in explicit agent cleanup: {e}")
    
    @asynccontextmanager
    async def message_capture(
        self,
        agent: Agent,
        capture_timeout: float = 5.0
    ) -> AsyncGenerator[List[SIMFMessage], None]:
        """Context manager for capturing messages with timeout."""
        captured_messages = []
        original_handler = None
        
        # Store original message handler if it exists
        if hasattr(agent, '_message_handler'):
            original_handler = agent._message_handler
        
        # Create capturing handler
        async def capturing_handler(message: SIMFMessage):
            captured_messages.append(message)
            if original_handler:
                await original_handler(message)
        
        # Install capturing handler
        agent._message_handler = capturing_handler
        
        try:
            yield captured_messages
        finally:
            # Restore original handler
            if original_handler:
                agent._message_handler = original_handler
            elif hasattr(agent, '_message_handler'):
                delattr(agent, '_message_handler')
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get a summary of the test execution."""
        return {
            "test_name": self.test_name,
            "current_phase": self.current_phase.value,
            "elapsed_time": time.time() - self.start_time,
            "resources_count": len(self.resources),
            "agents_count": len(self.agents),
            "events_count": len(self.events),
            "cleanup_tasks_count": len(self.cleanup_tasks)
        }


# Convenience functions for common test patterns

async def supervised_agent_test(
    test_name: str,
    agent_factory: Callable[[], Agent],
    test_func: Callable[[TestSupervisor, Agent], Any],
    timeout: float = 30.0
) -> Any:
    """Run a supervised test with a single agent."""
    async with TestSupervisor(test_name, default_timeout=timeout) as supervisor:
        agent = agent_factory()
        
        async with supervisor.agent_lifecycle(agent) as managed_agent:
            return await supervisor.execute_test_phase(test_func, timeout, supervisor, managed_agent)


async def supervised_multi_agent_test(
    test_name: str,
    agent_factories: Dict[str, Callable[[], Agent]],
    test_func: Callable[[TestSupervisor, Dict[str, Agent]], Any],
    timeout: float = 60.0
) -> Any:
    """Run a supervised test with multiple agents."""
    async with TestSupervisor(test_name, default_timeout=timeout) as supervisor:
        agents = {}
        
        # Create and register all agents
        for agent_id, factory in agent_factories.items():
            agent = factory()
            agents[agent_id] = await supervisor.register_agent(agent_id, agent)
        
        try:
            return await supervisor.execute_test_phase(test_func, timeout, supervisor, agents)
        finally:
            # Explicit cleanup for all agents
            for agent in agents.values():
                try:
                    if agent.is_running:
                        await agent.stop()
                except Exception as e:
                    logging.error(f"Error stopping agent in multi-agent test: {e}")
