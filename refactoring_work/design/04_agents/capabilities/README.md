# Agent Capabilities in OpenMAS

## 1. Overview

The OpenMAS capability system provides a standardized and flexible way for agents to define, advertise, discover, and invoke their abilities. It is built on a two-part design that separates the *what* from the *how*:

1.  **Declarative Definition**: Capabilities are defined as structured data in YAML configuration files. This specifies the capability's interface (name, description, parameters, return values).
2.  **Programmatic Implementation**: The actual logic that executes the capability is implemented in Python code as a handler method within an agent.

This separation is central to OpenMAS's design and enables key features like protocol adaptation and reasoning agnosticism.

## 2. Core Concepts & Documentation Structure

This documentation is organized into the following sections, which should be read in order to gain a complete understanding of the system.

*   **[ICapabilityManager Interface](./capability_manager_interface.md)**
    *   Defines the formal interface (`ICapabilityManager`) for registering, discovering, and invoking capabilities.

*   **[Declarative Capability Definition](./declarative_definition.md)**
    *   Explains how to define a capability's schema, including its ID, parameters, and return structures, in the agent's YAML configuration.

*   **[Programmatic Capability Implementation](./programmatic_implementation.md)**
    *   Details how to write the Python code for a capability's logic and how to register it as a handler using the `ICapabilityManager` or the `@capability_handler` decorator.

*   **[Protocol Adaptation](./protocol_adaptation.md)**
    *   Describes how the framework automatically exposes core capabilities over different communication protocols (e.g., A2A, MCP) using the `protocol_mapping` configuration.

*   **[Reasoning Agnosticism in Capabilities](./reasoning_agnosticism.md)**
    *   Illustrates how the same capability can have multiple implementations tailored to different reasoning approaches (e.g., LLM-based, rule-based), a key feature of OpenMAS.
        # Rule-based implementation
        weather_data = await self.weather_service.fetch(location)
        return {
            "temperature": weather_data["temp"],
            "conditions": weather_data["conditions"]
        }
```

## Implementation Flow and Framework Responsibilities

The integration between declarative capability definitions and programmatic implementations follows this sequence:

1. **Agent Configuration Loading**: The framework loads the agent's configuration, including the `multi_protocol_capabilities` section
2. **Agent Initialization**: The agent's `setup` method is called, where capability handlers are registered
3. **Validation**: The framework verifies that each declared capability has a corresponding handler
4. **Protocol Adapter Setup**: Protocol adapters use the `protocol_mapping` to expose capabilities appropriately
5. **Handler Selection**: When a capability is invoked, the framework selects the appropriate handler based on the agent's reasoning approach
6. **Parameter Validation**: Parameters are validated against the schema defined in the configuration
7. **Handler Execution**: The selected handler method is executed with the validated parameters
8. **Return Validation**: The return value is validated against the schema defined in the configuration

## Capability Security

Capabilities include security features that leverage the two-part model:

1. **Authentication** - The protocol layer ensures the caller is authenticated before reaching the capability handler
2. **Authorization** - The framework checks if the caller has permission to use the capability based on the agent's security configuration
3. **Rate Limiting** - The framework can enforce rate limits on capability invocations
4. **Input Validation** - Parameters are validated against the schema defined in the declarative configuration
5. **Output Validation** - Return values are validated against the schema defined in the declarative configuration

## Capability Integration with Other Components

The two-part capability system integrates with several OpenMAS components:

1. **Protocol Layer** - The declarative definitions and protocol mappings enable capabilities to be exposed through different protocols
2. **Topology System** - Capabilities can be used for role assignments in agent topologies
3. **Session Management** - Capability invocations can be tracked within sessions
4. **Observability System** - Both the declarative aspects (configuration, exposure) and programmatic aspects (handler execution) can be monitored

## Best Practices

When defining and implementing agent capabilities:

1. **Maintain Consistency** - Ensure the declarative definition (YAML) and programmatic implementation (Python) are aligned
2. **Use Clear IDs** - Core capability IDs should be meaningful and consistent
3. **Document All Aspects** - Provide clear descriptions in both the YAML configuration and Python code
4. **Leverage Reasoning-Specific Handlers** - Register different handlers for different reasoning approaches when appropriate
5. **Define Complete Schemas** - Comprehensive parameter and return schemas enable better validation and documentation
6. **Use Protocol Mappings Strategically** - Map capability names appropriately for each protocol's conventions
7. **Handle Errors Gracefully** - Implement robust error handling in capability handlers
8. **Test Across Protocols** - Verify that capabilities work correctly across all supported protocols
