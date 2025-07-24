# Reasoning Agnosticism in Capabilities

## 1. Overview

Reasoning agnosticism is a foundational principle of OpenMAS, allowing an agent's decision-making logic (the "brain") to be developed and swapped independently of its communication and interaction infrastructure (the "body"). The capability system is a key enabler of this principle.

It allows a single, abstract capability (e.g., `analyze_data`) to be implemented in multiple ways, with each implementation tailored to a specific reasoning paradigm (e.g., using a Large Language Model, a rule engine, or a BDI planner).

## 2. Associating Handlers with Reasoning Approaches

The `ICapabilityManager`'s registration methods include a `reasoning_approach` parameter. This allows you to associate a specific handler function with a named reasoning approach.

When registering a handler, you can specify which reasoning paradigm it implements. If omitted, it defaults to a `"default"` approach.

## 3. Configuration and Implementation

An agent's active reasoning approach is typically set in its configuration file.

**YAML Configuration:**

```yaml
agents:
  - id: "analysis_agent"
    # ... other agent config
    reasoning:
      approach: "llm" # This agent will use the 'llm' reasoning approach
    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "analyze_data"
            name: "Analyze Data"
            description: "Analyzes a dataset and returns insights."
            # ... parameters and returns schema
```

**Python Implementation with Multiple Handlers:**

In the agent's code, you register a different handler for the *same* `core_capability_id` for each reasoning approach you want to support.

```python
from openmas.agent import Agent
from openmas.capabilities import capability_handler

class MultiReasoningAgent(Agent):

    @capability_handler(core_capability_id="analyze_data", reasoning_approach="llm")
    async def analyze_data_llm(self, data: list) -> dict:
        """LLM-based implementation for data analysis."""
        # Logic to format the data and query an LLM
        print("Analyzing data using the LLM approach...")
        insights = await self.llm_service.generate_insights(data)
        return {"source": "llm", "insights": insights}

    @capability_handler(core_capability_id="analyze_data", reasoning_approach="rule_based")
    async def analyze_data_rules(self, data: list) -> dict:
        """Rule-based implementation for data analysis."""
        # Logic to process data through a rule engine
        print("Analyzing data using the rule-based approach...")
        violations = self.rule_engine.find_violations(data)
        return {"source": "rule_based", "violations": violations}

    @capability_handler(core_capability_id="analyze_data", reasoning_approach="bdi")
    async def analyze_data_bdi(self, data: list) -> dict:
        """BDI-based implementation for data analysis."""
        # Logic to update beliefs and trigger a plan
        print("Analyzing data using the BDI approach...")
        self.beliefs.update({"dataset_to_analyze": data})
        plan_result = await self.execute_plan("analyze_data_plan")
        return {"source": "bdi", "result": plan_result}
```

## 4. Runtime Invocation

When `invoke_capability` is called, the `ICapabilityManager` inspects the agent's configured `reasoning.approach` and dispatches the call to the corresponding handler.

If an external agent invokes the `analyze_data` capability on our `analysis_agent` (which is configured to use the `llm` approach), the framework will automatically execute the `analyze_data_llm` method.

This powerful mechanism allows for true plug-and-play reasoning engines. You can change an agent's entire decision-making process by changing a single line in its configuration, without altering the capability's interface or the code that calls it.
