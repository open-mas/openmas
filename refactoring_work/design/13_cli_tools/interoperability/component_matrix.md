# CLI Component Integration Matrix

## Overview

This document provides a detailed matrix showing how each OpenMAS CLI tool integrates with other components of the OpenMAS framework. This matrix is useful for understanding cross-component dependencies and interactions when developing and extending the CLI tools.

## CLI Tool Categories

The OpenMAS CLI tools are organized into these main categories:

1. **Agent CLI**: Tools for creating, managing, and monitoring agents
2. **Protocol CLI**: Tools for managing protocol adapters and communication
3. **Configuration CLI**: Tools for validating, generating, and managing configuration
4. **Testing CLI**: Tools for testing agents, protocols, and systems
5. **Deployment CLI**: Tools for deploying agents and systems
6. **Scaffolding CLI**: Tools for generating project structures and code
7. **Security CLI**: Tools for managing security configurations and controls

## Component Categories

The OpenMAS components that interact with CLI tools include:

1. **Agent Components**: Core agent runtime and lifecycle components
2. **Protocol Components**: Protocol adapters and communication components
3. **Configuration Components**: Configuration management and validation
4. **Testing Components**: Test harnesses, fixtures, and utilities
5. **Deployment Components**: Deployment managers and orchestration
6. **Security Components**: Authentication, authorization, and encryption
7. **Observability Components**: Logging, monitoring, and diagnostics
8. **Extension Components**: Plugin system and extensions

## Detailed Integration Matrix

The following matrix provides a detailed view of how each CLI tool category integrates with OpenMAS components:

| CLI Tool Category | Agent Components | Protocol Components | Configuration Components | Testing Components | Deployment Components | Security Components | Observability Components | Extension Components |
|------------------|-----------------|---------------------|------------------------|-------------------|----------------------|--------------------|-----------------------|---------------------|
| **Agent CLI**     | **Direct Control**: Agent lifecycle management, Agent initialization, Agent monitoring | **Indirect**: Protocol selection, Protocol configuration | **Moderate**: Agent configuration validation, Configuration application | **Moderate**: Agent test fixtures, Agent test utilities | **Light**: Agent deployment configuration | **Moderate**: Agent authentication, Agent authorization | **Direct**: Agent logging, Agent metrics, Agent tracing | **Moderate**: Agent extension loading |
| **Protocol CLI**  | **Light**: Agent protocol assignment | **Direct Control**: Protocol registration, Protocol validation, Protocol testing | **Moderate**: Protocol configuration validation | **Moderate**: Protocol test utilities, Protocol test harnesses | **Light**: Protocol deployment configuration | **Moderate**: Protocol security configuration | **Moderate**: Protocol logging, Protocol metrics | **Direct**: Protocol extension loading |
| **Configuration CLI** | **Moderate**: Agent configuration generation | **Light**: Protocol configuration generation | **Direct Control**: Configuration validation, Schema verification, Configuration generation | **Light**: Test configuration generation | **Direct**: Deployment configuration generation | **Direct**: Security configuration validation | **Moderate**: Observability configuration | **Moderate**: Extension configuration |
| **Testing CLI**   | **Direct**: Agent test setup, Mock agent creation | **Direct**: Protocol test setup, Protocol mocking | **Light**: Test configuration validation | **Direct Control**: Test harness management, Test fixtures, Test reporting | **Light**: Test deployment setup | **Moderate**: Test security setup | **Direct**: Test logging, Test metrics | **Light**: Test extension loading |
| **Deployment CLI** | **Moderate**: Agent deployment management | **Light**: Protocol deployment configuration | **Direct**: Deployment configuration management | **Light**: Deployment testing | **Direct Control**: Deployment orchestration, Environment management, Scaling | **Direct**: Deployment security configuration | **Direct**: Deployment monitoring, Deployment logging | **Moderate**: Deployment extensions |
| **Scaffolding CLI** | **Direct**: Agent template generation | **Direct**: Protocol adapter generation | **Direct**: Configuration template generation | **Moderate**: Test template generation | **Moderate**: Deployment template generation | **Moderate**: Security template generation | **Moderate**: Observability template generation | **Direct**: Extension template generation |
| **Security CLI**  | **Moderate**: Agent security configuration | **Moderate**: Protocol security configuration | **Moderate**: Security configuration validation | **Light**: Security test setup | **Moderate**: Secure deployment configuration | **Direct Control**: Authentication setup, Authorization management, Key management | **Moderate**: Security logging, Security alerts | **Light**: Security extension loading |

Legend:
- **Direct Control**: CLI tools directly control and manage these components
- **Direct**: CLI tools directly interact with these components
- **Moderate**: CLI tools have moderate integration with these components
- **Light**: CLI tools have light or indirect integration with these components

## Command-Level Integration

The following table shows specific CLI commands and their component integrations:

| CLI Command | Primary Component Integration | Secondary Component Integration | Description |
|------------|------------------------------|--------------------------------|-------------|
| `openmas agent create` | Agent Components | Configuration Components | Creates a new agent from configuration |
| `openmas agent start` | Agent Components | Deployment Components | Starts an agent |
| `openmas agent stop` | Agent Components | Deployment Components | Stops an agent |
| `openmas protocol register` | Protocol Components | Configuration Components | Registers a protocol adapter |
| `openmas protocol test` | Protocol Components | Testing Components | Tests a protocol adapter |
| `openmas config validate` | Configuration Components | - | Validates configuration against schema |
| `openmas config generate` | Configuration Components | - | Generates configuration from template |
| `openmas deploy` | Deployment Components | Configuration Components | Deploys agents/systems |
| `openmas test suite` | Testing Components | Agent Components | Runs test suites |
| `openmas scaffold` | Multiple Components | - | Generates project structure |
| `openmas security keys` | Security Components | Configuration Components | Manages security keys |

## Integration Code Examples

### Agent CLI Integration with Agent Components

```python
# Example of Agent CLI integration with Agent Components
from openmas.cli.commands import AgentCommand
from openmas.agent.lifecycle import AgentLifecycleManager

class StartAgentCommand(AgentCommand):
    name = "start"
    description = "Start an agent"

    def configure_parser(self, parser):
        parser.add_argument("--id", required=True, help="Agent ID")

    async def execute(self, args):
        # Integration with Agent Components
        lifecycle_manager = AgentLifecycleManager()

        # Start the agent
        await lifecycle_manager.start_agent(args.id)

        # Return success message
        return f"Agent {args.id} started successfully"
```

### Protocol CLI Integration with Protocol Components

```python
# Example of Protocol CLI integration with Protocol Components
from openmas.cli.commands import ProtocolCommand
from openmas.protocol.registry import ProtocolRegistry

class RegisterProtocolCommand(ProtocolCommand):
    name = "register"
    description = "Register a protocol adapter"

    def configure_parser(self, parser):
        parser.add_argument("--from", required=True, help="Protocol configuration file")

    async def execute(self, args):
        # Load configuration
        config = self.load_config(args.from)

        # Integration with Protocol Components
        protocol_registry = ProtocolRegistry()

        # Register protocol
        protocol_id = await protocol_registry.register_protocol(config)

        # Return success message
        return f"Protocol registered with ID: {protocol_id}"
```

### Deployment CLI Integration with Deployment Components

```python
# Example of Deployment CLI integration with Deployment Components
from openmas.cli.commands import DeploymentCommand
from openmas.deployment.orchestrator import DeploymentOrchestrator

class DeployCommand(DeploymentCommand):
    name = "apply"
    description = "Deploy a system"

    def configure_parser(self, parser):
        parser.add_argument("--from", required=True, help="Deployment configuration file")

    async def execute(self, args):
        # Load configuration
        config = self.load_config(args.from)

        # Integration with Deployment Components
        orchestrator = DeploymentOrchestrator()

        # Deploy the system
        deployment_id = await orchestrator.deploy(config)

        # Return success message
        return f"Deployment successful. ID: {deployment_id}"
```

## Cross-Component Data Flow

The following diagram shows how data flows between CLI tools and components:

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CLI Tools Layer                           │
└───────────────┬───────────────┬──────────────────┬─────────────────┘
                │               │                  │
                ▼               ▼                  ▼
┌───────────────────┐  ┌────────────────┐  ┌─────────────────┐
│ Command Arguments │  │ Configuration  │  │ Command Output  │
│ & Options         │  │ Files          │  │ & Exit Codes    │
└─────────┬─────────┘  └───────┬────────┘  └────────┬────────┘
          │                    │                     │
          ▼                    ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Component Interface Layer                   │
└───────────────┬───────────────┬──────────────────┬─────────────────┘
                │               │                  │
                ▼               ▼                  ▼
┌───────────────────┐  ┌────────────────┐  ┌─────────────────┐
│ API Requests      │  │ Component      │  │ Event           │
│ & Method Calls    │  │ Configuration  │  │ Subscriptions   │
└─────────┬─────────┘  └───────┬────────┘  └────────┬────────┘
          │                    │                     │
          ▼                    ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Core Components Layer                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Extending CLI Component Integration

For developers who want to extend CLI component integration:

1. **New CLI Command with Existing Component**:
   ```python
   from openmas.cli.commands import BaseCommand
   from openmas.some_component import SomeComponent

   class MyCommand(BaseCommand):
       name = "mycommand"
       description = "My custom command"

       def configure_parser(self, parser):
           parser.add_argument("--option", help="Custom option")

       async def execute(self, args):
           # Integrate with existing component
           component = SomeComponent()
           result = await component.some_operation(args.option)
           return result

   # Register command
   from openmas.cli.registry import CommandRegistry
   CommandRegistry.register(MyCommand)
   ```

2. **CLI Integration with New Component**:
   ```python
   # Define component interface
   from openmas.cli.interface import ComponentInterface

   class MyComponentInterface(ComponentInterface):
       component_type = "mycomponent"

       async def custom_operation(self, *args, **kwargs):
           # Implement operation
           pass

   # Register interface
   from openmas.cli.registry import InterfaceRegistry
   InterfaceRegistry.register(MyComponentInterface)

   # Create CLI command that uses the interface
   from openmas.cli.commands import BaseCommand

   class MyComponentCommand(BaseCommand):
       name = "mycomponent"
       description = "My component command"

       def configure_parser(self, parser):
           parser.add_argument("--action", help="Component action")

       async def execute(self, args):
           # Get component interface
           interface = self.get_interface("mycomponent")

           # Execute operation
           result = await interface.custom_operation(args.action)
           return result

   # Register command
   from openmas.cli.registry import CommandRegistry
   CommandRegistry.register(MyComponentCommand)
   ```

## Related Documentation

- [CLI Component Interoperability](./component_interoperability.md)
- [CLI Workflow Diagrams](./workflow_diagrams.md)
- [CLI Commands](../commands/README.md)
- [Agent Components](../../04_agents/README.md)
- [Protocol Components](../../02_protocols/README.md)
- [Configuration Components](../../03_configuration/README.md)
- [Testing Framework](../../16_testing/framework/README.md)
- [Deployment Documentation](../../15_deployment/README.md)
- [Security Architecture](../../17_security/architecture/README.md)
