# Agent Topology Implementation Examples

## Overview

This document provides concrete implementation examples of how agents in OpenMAS implement various topology patterns. These examples demonstrate the agent-specific aspects of topology implementation while maintaining OpenMAS's core principles of reasoning agnosticism and protocol independence.

## Centralized Topology Implementation

### Orchestrator Agent Implementation

```python
from openmas.agent import Agent
from openmas.topology import TopologyManager, OrchestratorRole

class TravelCoordinator(Agent):
    async def setup(self):
        # Set up topology manager with orchestrator role
        self.topology_manager = TopologyManager(self)
        await self.topology_manager.assume_role(OrchestratorRole())
        
        # Register worker relationships
        await self.topology_manager.register_worker("flight_search_agent")
        await self.topology_manager.register_worker("hotel_search_agent")
        await self.topology_manager.register_worker("activity_search_agent")
        
        # Set up task delegation capability
        self.add_capability("task_delegation", self.delegate_task)
        self.add_capability("result_aggregation", self.aggregate_results)
    
    async def delegate_task(self, task_data):
        # Determine which worker should handle this task
        worker = self.topology_manager.select_worker(task_data)
        
        # Delegate task to selected worker
        result = await self.topology_manager.send_request(
            worker, 
            "task_execution", 
            task_data
        )
        return result
    
    async def aggregate_results(self, results):
        # Process and combine results from multiple workers
        aggregated_result = {
            "status": "completed",
            "data": {}
        }
        
        for worker_id, result in results.items():
            aggregated_result["data"][worker_id] = result
        
        return aggregated_result
```

### Worker Agent Implementation

```python
from openmas.agent import Agent
from openmas.topology import TopologyManager, WorkerRole

class FlightSearchAgent(Agent):
    async def setup(self):
        # Set up topology manager with worker role
        self.topology_manager = TopologyManager(self)
        await self.topology_manager.assume_role(WorkerRole())
        
        # Register with orchestrator
        await self.topology_manager.register_with_orchestrator("travel_coordinator")
        
        # Set up task execution capability
        self.add_capability("task_execution", self.execute_task)
        self.add_capability("status_reporting", self.report_status)
    
    async def execute_task(self, task_data):
        # Implement specialized flight search logic
        flight_options = await self._search_flights(
            task_data["origin"],
            task_data["destination"],
            task_data["date"]
        )
        
        return {
            "status": "completed",
            "flights": flight_options
        }
    
    async def report_status(self):
        # Report current status to orchestrator
        status = {
            "available": True,
            "load": self.current_load,
            "capabilities": self.get_capabilities()
        }
        
        await self.topology_manager.send_event(
            "travel_coordinator",
            "status_update",
            status
        )
        
    async def _search_flights(self, origin, destination, date):
        # Implementation-specific flight search logic
        # This could use any reasoning approach (rule-based, LLM, etc.)
        pass
```

## Hierarchical Topology Implementation

### Root Orchestrator Implementation

```python
from openmas.agent import Agent
from openmas.topology import TopologyManager, RootRole

class EnterpriseCoordinator(Agent):
    async def setup(self):
        # Set up topology manager with root role
        self.topology_manager = TopologyManager(self)
        await self.topology_manager.assume_role(RootRole())
        
        # Register domain coordinators
        await self.topology_manager.register_subordinate("sales_coordinator")
        await self.topology_manager.register_subordinate("support_coordinator")
        await self.topology_manager.register_subordinate("logistics_coordinator")
        
        # Set up strategic planning capability
        self.add_capability("strategic_planning", self.create_strategic_plan)
        self.add_capability("domain_coordination", self.coordinate_domains)
    
    async def create_strategic_plan(self, requirements):
        # Create and distribute strategic plan to domain coordinators
        plan = self._generate_plan(requirements)
        
        # Distribute plan components to appropriate domains
        for domain, domain_plan in plan.items():
            coordinator = self.topology_manager.get_subordinate(f"{domain}_coordinator")
            await self.topology_manager.send_directive(
                coordinator,
                "implement_plan",
                domain_plan
            )
        
        return {"status": "plan_distributed", "plan_id": plan["id"]}
    
    async def coordinate_domains(self, coordination_task):
        # Coordinate activities across multiple domains
        # Implementation would vary based on reasoning approach
        pass
```

## Peer-to-Peer Topology Implementation

### Peer Agent Implementation

```python
from openmas.agent import Agent
from openmas.topology import TopologyManager, PeerRole

class DataProcessingPeer(Agent):
    async def setup(self):
        # Set up topology manager with peer role
        self.topology_manager = TopologyManager(self)
        await self.topology_manager.assume_role(PeerRole())
        
        # Discover other peers
        discovered_peers = await self.topology_manager.discover_peers()
        
        # Register capabilities that other peers can use
        self.add_capability("data_transformation", self.transform_data)
        self.add_capability("data_validation", self.validate_data)
        
        # Establish connections with relevant peers
        for peer in discovered_peers:
            if self._is_relevant_peer(peer):
                await self.topology_manager.establish_peer_connection(peer)
    
    async def transform_data(self, data):
        # Implement data transformation logic
        transformed_data = self._apply_transformation(data)
        
        # If needed, collaborate with other peers
        if self._needs_additional_processing(transformed_data):
            # Find peer with required capability
            processing_peer = await self.topology_manager.find_peer_with_capability(
                "advanced_processing"
            )
            
            if processing_peer:
                result = await self.topology_manager.send_request(
                    processing_peer,
                    "advanced_processing",
                    transformed_data
                )
                return result
        
        return transformed_data
    
    async def _apply_transformation(self, data):
        # Implementation-specific transformation logic
        # This demonstrates reasoning agnosticism - could use any approach
        pass
```

## Protocol Adapters

The following examples show how topology implementations adapt to different protocols:

### A2A Protocol Adapter

```python
# Example of topology implementation with A2A protocol
from openmas.agent import Agent
from openmas.topology import TopologyManager
from openmas.protocols.a2a import A2AAdapter

class A2AOrchestratorAgent(Agent):
    async def setup(self):
        # Set up topology with A2A protocol adapter
        self.protocol_adapter = A2AAdapter(self)
        self.topology_manager = TopologyManager(
            self, 
            protocol_adapter=self.protocol_adapter
        )
        
        # A2A-specific topology setup
        await self.topology_manager.assume_role("orchestrator")
        
        # A2A uses agent cards for discovery
        await self.protocol_adapter.publish_agent_card({
            "role": "orchestrator",
            "capabilities": ["task_delegation", "result_aggregation"]
        })
        
        # Register workers through A2A directory
        workers = await self.protocol_adapter.discover_agents_by_role("worker")
        for worker in workers:
            await self.topology_manager.register_worker(worker.agent_id)
```

### MCP Protocol Adapter

```python
# Example of topology implementation with MCP protocol
from openmas.agent import Agent
from openmas.topology import TopologyManager
from openmas.protocols.mcp import MCPAdapter

class MCPWorkerAgent(Agent):
    async def setup(self):
        # Set up topology with MCP protocol adapter
        self.protocol_adapter = MCPAdapter(self)
        self.topology_manager = TopologyManager(
            self, 
            protocol_adapter=self.protocol_adapter
        )
        
        # MCP-specific topology setup
        await self.topology_manager.assume_role("worker")
        
        # MCP uses tools for capabilities
        await self.protocol_adapter.register_tool(
            "task_execution",
            self.execute_task,
            {
                "type": "object",
                "properties": {
                    "task_type": {"type": "string"},
                    "parameters": {"type": "object"}
                }
            }
        )
        
        # Register with orchestrator
        orchestrator = await self.protocol_adapter.discover_resource_by_role("orchestrator")
        await self.topology_manager.register_with_orchestrator(orchestrator.resource_id)
```

## Reasoning Agnosticism in Implementation

These implementation examples demonstrate OpenMAS's reasoning agnosticism through:

1. **Interface-Based Implementation**: All examples use standard interfaces regardless of reasoning approach
2. **Capability Registration**: Capabilities are registered without specifying reasoning implementation
3. **Protocol Adapters**: Communication adapts to protocols without changing core topology logic
4. **Role-Based Organization**: Agents organize by roles independent of reasoning mechanisms

Any of these example implementations could use different reasoning approaches:
- Rule-based reasoning
- BDI architecture
- LLM-based reasoning
- Hybrid approaches

The topology implementation remains consistent regardless of the underlying reasoning.

## References

- [Topology System Architecture](/08_topology/architecture.md)
- [Agent Framework](/04_agents/README.md)
- [Protocol Adapters](/02_protocols/README.md)
- [Communication Patterns](/07_communication_patterns/README.md)
