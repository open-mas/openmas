# Agent Lifecycle Management

## Overview

This document describes the agent lifecycle management in OpenMAS, covering how agents are created, initialized, run, and terminated while maintaining OpenMAS's core principle of reasoning agnosticism.

## Agent Lifecycle Phases

The OpenMAS agent lifecycle consists of these core phases:

1. **Creation** - Agent instantiation from configuration
2. **Initialization** - Setup of capabilities, protocols, and resources
3. **Running** - Active operation and message handling
4. **Termination** - Graceful shutdown and resource cleanup

## Lifecycle Management

### Agent Creation

Agents are created from configuration:

```python
from openmas.agent import Agent, create_agent_from_config

# Create an agent from configuration
config = {
    "class": "agents.assistant.AssistantAgent",
    "type": "llm",
    "protocols": [
        {"type": "a2a-http", "enabled": True}
    ],
    "reasoning": {
        "approach": "llm",
        "llm": {
            "provider": "openai",
            "model": "gpt-4"
        }
    }
}

agent = create_agent_from_config("assistant_agent", config)

# Or extend the base Agent class
class CustomAgent(Agent):
    def __init__(self, agent_id, config):
        super().__init__(agent_id, config)
        self.custom_state = {}
```

### Initialization

Agents initialize their components during setup:

```python
class WeatherAgent(Agent):
    async def setup(self):
        # Register capabilities
        self.register_capability("get_weather")
        self.register_capability("subscribe_alerts")

        # Initialize external services
        self.weather_service = await WeatherService.create(
            api_key=self.config.get_credential("weather_api_key")
        )

        # Load resources
        self.weather_model = await self.asset_manager.load_model("weather_prediction")

        # Set up protocol handlers
        self.register_protocol_handlers()

        # Initialize reasoning components
        await self.init_reasoning()
```

### Running

Agents process messages and handle requests during their active phase:

```python
# Start the agent
await agent.start()

# Process a specific message
result = await agent.process_message(message)

# Process a specific capability request
result = await agent.invoke_capability("get_weather", {"location": "London"})

# Run the agent for a specific duration
await agent.run_until(timeout=60)  # Run for 60 seconds

# Run the agent indefinitely
await agent.run_forever()
```

### Termination

Agents properly clean up resources during shutdown:

```python
# Graceful shutdown
await agent.shutdown()

# With resource cleanup
await agent.shutdown(cleanup_resources=True)

# Custom cleanup logic
class DataProcessingAgent(Agent):
    async def cleanup(self):
        await super().cleanup()

        # Close database connections
        await self.db_client.close()

        # Save state
        await self.save_state()

        # Release resources
        await self.resource_manager.release_all()
```

## Protocol-Specific Lifecycle

Each protocol has its own lifecycle specifics:

### A2A Protocol Lifecycle

```python
class A2AAgent(Agent):
    async def setup(self):
        # Register with A2A protocol
        self.a2a = await self.get_protocol("a2a-http")

        # Register agent card
        await self.a2a.register_agent_card({
            "name": self.agent_id,
            "description": "A2A-enabled agent"
        })

        # Register discovery endpoint
        await self.a2a.enable_discovery(well_known_path="/.well-known/agent.json")

    async def cleanup(self):
        # Deregister from discovery
        await self.a2a.disable_discovery()
        await super().cleanup()
```

### MCP Protocol Lifecycle

```python
class MCPAgent(Agent):
    async def setup(self):
        # Register with MCP protocol
        self.mcp = await self.get_protocol("mcp-sse")

        # Register tools
        await self.mcp.register_tools(self.capabilities.to_tools())

        # Start MCP server if in server mode
        if self.config.get("protocols.mcp.options.server_mode", False):
            await self.mcp.start_server()

    async def cleanup(self):
        # Stop MCP server if running
        if self.mcp.server_running:
            await self.mcp.stop_server()
        await super().cleanup()
```

## Reasoning-Specific Lifecycle

Different reasoning types have specific lifecycle aspects:

### LLM-Based Agent Lifecycle

```python
class LLMAgent(Agent):
    async def setup(self):
        # Initialize the LLM
        provider = self.config.get("reasoning.llm.provider")
        model = self.config.get("reasoning.llm.model")
        self.llm = await self.llm_manager.create_llm(provider, model)

        # Set up prompt templates
        self.prompt_template = await self.prompt_manager.load_template(
            "main_prompt"
        )

        # Initialize memory
        self.memory = await self.create_memory(
            type=self.config.get("reasoning.llm.memory_type", "buffer")
        )

    async def cleanup(self):
        # Save conversation memory if needed
        if self.config.get("reasoning.llm.save_memory", False):
            await self.memory.save()
        await super().cleanup()
```

### Rule-Based Agent Lifecycle

```python
class RuleBasedAgent(Agent):
    async def setup(self):
        # Load rule engine
        engine_type = self.config.get("reasoning.rule_based.engine", "standard")
        self.rule_engine = self.create_rule_engine(engine_type)

        # Load rules
        rules_file = self.config.get("reasoning.rule_based.rules_file")
        await self.rule_engine.load_rules(rules_file)

        # Initialize fact base
        self.fact_base = self.rule_engine.create_fact_base()

    async def cleanup(self):
        # Save fact base state if needed
        if self.config.get("reasoning.rule_based.save_facts", False):
            await self.fact_base.save()
        await super().cleanup()
```

### BDI Agent Lifecycle

```python
class BDIAgent(Agent):
    async def setup(self):
        # Initialize belief base
        belief_base_type = self.config.get("reasoning.bdi.belief_base.type")
        self.belief_base = self.create_belief_base(belief_base_type)

        # Initialize desire set
        self.desire_set = self.create_desire_set()
        for desire in self.config.get("reasoning.bdi.desires", []):
            self.desire_set.add_desire(desire["name"], priority=desire.get("priority", 1))

        # Initialize plan library
        self.plan_library = self.create_plan_library()
        for plan in self.config.get("reasoning.bdi.plans", []):
            self.plan_library.add_plan(plan["name"], triggers=plan.get("triggers", []))

        # Initialize intention structure
        self.intention_structure = self.create_intention_structure()

    async def cleanup(self):
        # Save belief base if needed
        if self.config.get("reasoning.bdi.save_beliefs", False):
            await self.belief_base.save()
        await super().cleanup()
```

## Lifecycle Events

OpenMAS provides a rich event system for lifecycle management:

```python
class MonitoredAgent(Agent):
    async def setup(self):
        # Register lifecycle event handlers
        self.on_event("agent:starting", self.handle_starting)
        self.on_event("agent:started", self.handle_started)
        self.on_event("agent:stopping", self.handle_stopping)
        self.on_event("agent:stopped", self.handle_stopped)
        self.on_event("agent:error", self.handle_error)

        # Register capability-related events
        self.on_event("capability:invoked", self.handle_capability_invoked)
        self.on_event("capability:completed", self.handle_capability_completed)
        self.on_event("capability:failed", self.handle_capability_failed)

    async def handle_starting(self, event):
        self.logger.info(f"Agent {self.agent_id} is starting")

    async def handle_error(self, event):
        self.logger.error(f"Agent {self.agent_id} encountered an error: {event.error}")
        # Notify monitoring system
        await self.monitoring.report_error(event.error)
```

## Agent Lifecycle Configuration

For agent lifecycle configuration, OpenMAS uses the unified configuration schema. For the complete schema definition, see [Agent Configuration Schema](/03_configuration/schema/agents.md).

Key configuration sections related to lifecycle:

```yaml
agents:
  example_agent:
    # Lifecycle configuration
    lifecycle:
      auto_start: true
      restart_on_failure: true
      max_restarts: 3
      shutdown_timeout: 30
      startup_order: 1

    # Health check configuration
    health_check:
      enabled: true
      interval: 60
      timeout: 5
      healthy_threshold: 3
      unhealthy_threshold: 2
```

## Reasoning Agnosticism in Lifecycle Management

OpenMAS maintains reasoning agnosticism in lifecycle management through:

1. **Standard Lifecycle Interface** - Common lifecycle methods across all reasoning approaches
2. **Reasoning-Specific Initialization** - Custom setup for each reasoning approach
3. **Protocol-Independent Initialization** - Lifecycle management separate from protocol specifics
4. **Event-Based Coordination** - Consistent events regardless of reasoning approach

This enables developers to use different reasoning approaches while maintaining a consistent lifecycle model.
