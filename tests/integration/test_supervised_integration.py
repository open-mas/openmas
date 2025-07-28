"""
TestSupervisor Integration Tests

Demonstrates the TestSupervisor pattern for reliable async agent testing
and validates that async resource cleanup issues are resolved.
"""

import asyncio
import pytest
from typing import Dict

from openmas.agent.base_agent import Agent
from openmas.core.simf.models import create_text_message, MessageType
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.test_supervisor import (
    TestSupervisor,
    TestPhase,
    supervised_agent_test,
    supervised_multi_agent_test
)


class TestSupervisedIntegration:
    """Integration tests using TestSupervisor for proper async coordination."""
    
    @pytest.mark.asyncio
    async def test_single_agent_lifecycle_with_supervisor(self, basic_agent_factory):
        """Test single agent lifecycle with TestSupervisor management."""
        
        async def agent_test(supervisor: TestSupervisor, agent: Agent):
            # Verify agent is properly started
            assert agent.is_running
            
            # Test basic agent functionality
            capabilities = await agent.get_capabilities()
            assert isinstance(capabilities, (list, set))
            
            # Emit test event for coordination
            await supervisor._emit_event("agent_tested", {"agent_id": agent.agent_id})
            
            # Wait for event to ensure coordination works
            event = await supervisor.wait_for_event("agent_tested", timeout=5.0)
            assert event is not None
            assert event.data["agent_id"] == agent.agent_id
            
            return "test_completed"
        
        # Run supervised test
        result = await supervised_agent_test(
            test_name="single_agent_lifecycle",
            agent_factory=basic_agent_factory,
            test_func=agent_test,
            timeout=30.0
        )
        
        assert result == "test_completed"
    
    @pytest.mark.asyncio
    async def test_multi_agent_coordination_with_supervisor(self, multi_agent_factory):
        """Test multi-agent coordination with TestSupervisor management."""
        
        async def multi_agent_test(supervisor: TestSupervisor, agents: Dict[str, Agent]):
            # Verify all agents are properly started
            assert len(agents) == 2
            for agent_id, agent in agents.items():
                assert agent.is_running
                assert agent.agent_id is not None
            
            # Test agent communication coordination
            agent_0 = agents["agent_0"]
            agent_1 = agents["agent_1"]
            
            # Create a test message
            test_message = create_text_message(
                text="Hello from agent_0",
                source_agent_id=agent_0.agent_id,
                target_agent_id=agent_1.agent_id,
                session_id="test_session"
            )
            
            # Send message through agent_0's communicator
            await agent_0.communicator.send_message(test_message)
            
            # Emit coordination events
            await supervisor._emit_event("message_sent", {
                "from": agent_0.agent_id,
                "to": agent_1.agent_id,
                "message_type": test_message.message_type
            })
            
            # Wait for coordination event
            event = await supervisor.wait_for_event("message_sent", timeout=5.0)
            assert event is not None
            
            return "multi_agent_test_completed"
        
        # Create agent factories
        factories = multi_agent_factory(2)
        
        # Run supervised multi-agent test
        result = await supervised_multi_agent_test(
            test_name="multi_agent_coordination",
            agent_factories=factories,
            test_func=multi_agent_test,
            timeout=60.0
        )
        
        assert result == "multi_agent_test_completed"
    
    @pytest.mark.asyncio
    async def test_supervisor_resource_cleanup(self, test_supervisor, basic_agent_factory):
        """Test that TestSupervisor properly cleans up resources."""
        
        # Create multiple agents within supervisor context
        agents = []
        for i in range(3):
            agent = basic_agent_factory()
            managed_agent = await test_supervisor.register_agent(
                agent_id=f"cleanup_test_agent_{i}",
                agent=agent,
                auto_start=True,
                auto_cleanup=True
            )
            agents.append(managed_agent)
        
        # Verify all agents are running
        for agent in agents:
            assert agent.is_running
        
        # Register additional test resources
        test_resource = {"data": "test_cleanup_data"}
        test_supervisor.register_resource(
            resource_id="test_cleanup_resource",
            resource=test_resource,
            resource_type="test_data"
        )
        
        # Verify resources are registered
        assert len(test_supervisor.resources) >= 4  # 3 agents + 1 test resource
        assert len(test_supervisor.agents) == 3
        
        # Test phase transitions
        await test_supervisor._transition_to_phase(TestPhase.EXECUTION)
        assert test_supervisor.current_phase == TestPhase.EXECUTION
        
        # The cleanup will happen automatically when the test_supervisor
        # context manager exits (handled by conftest.py fixture)
        
        return "cleanup_test_completed"
    
    @pytest.mark.asyncio
    async def test_supervisor_timeout_management(self, test_supervisor, basic_agent_factory):
        """Test TestSupervisor timeout management capabilities."""
        
        agent = basic_agent_factory()
        
        async with test_supervisor.agent_lifecycle(agent) as managed_agent:
            # Test successful operation within timeout
            async def quick_operation():
                await asyncio.sleep(0.1)
                return "quick_result"
            
            result = await test_supervisor.execute_test_phase(
                quick_operation,
                timeout=5.0
            )
            assert result == "quick_result"
            
            # Test timeout handling
            async def slow_operation():
                await asyncio.sleep(10.0)  # This should timeout
                return "slow_result"
            
            with pytest.raises(asyncio.TimeoutError):
                await test_supervisor.execute_test_phase(
                    slow_operation,
                    timeout=1.0
                )
        
        return "timeout_test_completed"
    
    @pytest.mark.asyncio
    async def test_supervisor_event_coordination(self, test_supervisor, basic_agent_factory):
        """Test TestSupervisor event-based coordination."""
        
        agent = basic_agent_factory()
        
        async with test_supervisor.agent_lifecycle(agent) as managed_agent:
            # Test event emission and waiting
            event_data = {"test_key": "test_value", "agent_id": managed_agent.agent_id}
            
            # Emit event in background task
            async def emit_delayed_event():
                await asyncio.sleep(0.5)
                await test_supervisor._emit_event("test_coordination_event", event_data)
            
            # Start background task
            emit_task = asyncio.create_task(emit_delayed_event())
            
            # Wait for the event
            received_event = await test_supervisor.wait_for_event(
                "test_coordination_event",
                timeout=2.0
            )
            
            # Verify event was received correctly
            assert received_event is not None
            assert received_event.event_type == "test_coordination_event"
            assert received_event.data == event_data
            
            # Clean up background task
            await emit_task
        
        return "event_coordination_completed"
    
    @pytest.mark.asyncio
    async def test_supervisor_phase_management(self, test_supervisor):
        """Test TestSupervisor phase management and transitions."""
        
        # Verify initial phase
        assert test_supervisor.current_phase == TestPhase.SETUP
        
        # Test phase transition
        await test_supervisor._transition_to_phase(TestPhase.EXECUTION)
        assert test_supervisor.current_phase == TestPhase.EXECUTION
        
        # Test waiting for phase
        phase_reached = await test_supervisor.wait_for_phase(TestPhase.EXECUTION, timeout=1.0)
        assert phase_reached is True
        
        # Test waiting for future phase (should timeout)
        phase_reached = await test_supervisor.wait_for_phase(TestPhase.COMPLETED, timeout=0.5)
        assert phase_reached is False
        
        return "phase_management_completed"


class TestSupervisedResourceCleanup:
    """Tests specifically focused on async resource cleanup validation."""
    
    @pytest.mark.asyncio
    async def test_no_pending_tasks_after_supervised_test(self, basic_agent_factory):
        """Verify that supervised tests don't leave pending async tasks."""
        
        # Get initial task count
        initial_tasks = len([t for t in asyncio.all_tasks() if not t.done()])
        
        async def resource_intensive_test(supervisor: TestSupervisor, agent: Agent):
            # Create some async operations
            tasks = []
            for i in range(5):
                async def async_operation(n=i):
                    await asyncio.sleep(0.1)
                    return f"operation_{n}_completed"
                
                task = asyncio.create_task(async_operation())
                tasks.append(task)
            
            # Wait for all operations to complete
            results = await asyncio.gather(*tasks)
            assert len(results) == 5
            
            return "resource_intensive_completed"
        
        # Run supervised test
        result = await supervised_agent_test(
            test_name="resource_intensive_test",
            agent_factory=basic_agent_factory,
            test_func=resource_intensive_test,
            timeout=30.0
        )
        
        assert result == "resource_intensive_completed"
        
        # Verify no additional pending tasks remain
        await asyncio.sleep(0.1)  # Give time for cleanup
        final_tasks = len([t for t in asyncio.all_tasks() if not t.done()])
        
        # Should have same or fewer tasks than initial (cleanup may have reduced count)
        assert final_tasks <= initial_tasks + 1  # Allow for small variance
    
    @pytest.mark.asyncio
    async def test_agent_cleanup_on_exception(self, test_supervisor, basic_agent_factory):
        """Test that agents are properly cleaned up even when exceptions occur."""
        
        agent = basic_agent_factory()
        
        try:
            async with test_supervisor.agent_lifecycle(agent) as managed_agent:
                assert managed_agent.is_running
                
                # Simulate an exception during test
                raise ValueError("Simulated test exception")
                
        except ValueError as e:
            assert str(e) == "Simulated test exception"
        
        # Verify agent was properly stopped despite the exception
        assert not agent.is_running
        
        return "exception_cleanup_completed"


# Additional test to validate the fix for the original hanging issue
class TestAsyncResourceCleanupValidation:
    """Validates that the original async resource cleanup issues are resolved."""
    
    @pytest.mark.asyncio
    async def test_multiple_agents_no_hanging(self, multi_agent_factory):
        """Test that multiple agent creation/destruction doesn't cause hanging."""
        
        async def multi_agent_lifecycle_test(supervisor: TestSupervisor, agents: Dict[str, Agent]):
            # Perform operations with all agents
            for agent_id, agent in agents.items():
                assert agent.is_running
                
                # Test basic operations
                capabilities = await agent.get_capabilities()
                assert isinstance(capabilities, (list, set))
                
                # Emit progress event
                await supervisor._emit_event("agent_processed", {"agent_id": agent_id})
            
            # Wait for all agent processing events
            for i in range(len(agents)):
                event = await supervisor.wait_for_event("agent_processed", timeout=5.0)
                assert event is not None
            
            return f"processed_{len(agents)}_agents"
        
        # Create multiple agents
        factories = multi_agent_factory(5)
        
        # Run test - this should complete without hanging
        result = await supervised_multi_agent_test(
            test_name="multi_agent_lifecycle_no_hanging",
            agent_factories=factories,
            test_func=multi_agent_lifecycle_test,
            timeout=60.0
        )
        
        assert "processed_5_agents" == result
