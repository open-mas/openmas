# CLI Component Interoperability

## Overview

This document describes how the OpenMAS CLI tools interoperate with other components of the OpenMAS framework. Understanding these interactions is essential for effective use of the CLI tools in various workflows, particularly within development, testing, and deployment scenarios.

## CLI Component Architecture

The OpenMAS CLI tools follow a layered architecture that enables interoperability with other OpenMAS components:

```
┌─────────────────────────────────────────────────┐
│                  CLI Commands                   │
│                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────┐ │
│  │ Agent   │  │ Config  │  │Protocol │  │Other│ │
│  │Commands │  │Commands │  │Commands │  │Cmds │ │
│  └─────────┘  └─────────┘  └─────────┘  └─────┘ │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│               Command Framework                 │
│                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────┐ │
│  │ Parser  │  │Validator│  │Executor │  │Utils│ │
│  └─────────┘  └─────────┘  └─────────┘  └─────┘ │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│            Component Interfaces                 │
│                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────┐ │
│  │ Agent   │  │ Config  │  │Protocol │  │Other│ │
│  │Interface│  │Interface│  │Interface│  │Intfs│ │
│  └─────────┘  └─────────┘  └─────────┘  └─────┘ │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│             OpenMAS Core Components             │
└─────────────────────────────────────────────────┘
```

## Component Interoperability Matrix

The following matrix shows how CLI tools interact with other OpenMAS components:

| CLI Tool Category | Agent Components | Protocol Components | Configuration Components | Testing Components | Deployment Components | Security Components |
|------------------|-----------------|---------------------|------------------------|-------------------|----------------------|---------------------|
| Agent CLI         | ✓✓✓             | ✓✓                  | ✓✓                     | ✓                  | ✓                     | ✓                   |
| Protocol CLI      | ✓               | ✓✓✓                 | ✓                      | ✓                  | ✓                     | ✓                   |
| Configuration CLI | ✓✓              | ✓                   | ✓✓✓                    | ✓                  | ✓✓                    | ✓✓                  |
| Scaffold CLI      | ✓✓              | ✓✓                  | ✓✓                     | ✓                  | ✓                     | ✓                   |
| Testing CLI       | ✓✓              | ✓✓                  | ✓                      | ✓✓✓                | ✓                     | ✓                   |
| Deployment CLI    | ✓               | ✓                   | ✓✓                     | ✓                  | ✓✓✓                   | ✓✓                  |
| Security CLI      | ✓               | ✓                   | ✓                      | ✓                  | ✓                     | ✓✓✓                 |

Legend: ✓✓✓ (Strong interaction), ✓✓ (Moderate interaction), ✓ (Light interaction)

## Key Interoperability Workflows

### 1. Agent Development Workflow

The CLI tools interact with multiple components during agent development:

```
┌─────────────┐
│ Scaffold CLI│
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ Agent CLI   │────►│Configuration │
└──────┬──────┘     │ Components   │
       │            └─────────────┘
       ▼
┌─────────────┐     ┌─────────────┐
│ Testing CLI │────►│ Testing     │
└──────┬──────┘     │ Components   │
       │            └─────────────┘
       ▼
┌─────────────┐     ┌─────────────┐
│Deployment CLI────►│ Deployment  │
└─────────────┘     │ Components   │
                    └─────────────┘
```

**Key Interactions:**
1. **Scaffold CLI** creates initial agent structure
2. **Agent CLI** interacts with agent components to configure and manage agents
3. **Configuration CLI** interacts with configuration components to validate and manage agent configuration
4. **Testing CLI** interacts with testing components to test agent functionality
5. **Deployment CLI** interacts with deployment components to deploy agents

### 2. Protocol Development Workflow

The CLI tools interact with multiple components during protocol development:

```
┌─────────────┐
│ Scaffold CLI│
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ Protocol CLI│────►│Protocol     │
└──────┬──────┘     │ Components   │
       │            └─────────────┘
       ▼
┌─────────────┐     ┌─────────────┐
│ Testing CLI │────►│ Testing     │
└──────┬──────┘     │ Components   │
       │            └─────────────┘
       ▼
┌─────────────┐     ┌─────────────┐
│Deployment CLI────►│ Deployment  │
└─────────────┘     │ Components   │
                    └─────────────┘
```

**Key Interactions:**
1. **Scaffold CLI** creates initial protocol adapter structure
2. **Protocol CLI** interacts with protocol components to configure and test protocol adapters
3. **Testing CLI** interacts with testing components to test protocol functionality
4. **Deployment CLI** interacts with deployment components to deploy protocol adapters

### 3. Multi-Agent System Deployment

The CLI tools interact with multiple components during multi-agent system deployment:

```
┌─────────────┐     ┌─────────────┐
│Configuration│────►│Configuration │
│    CLI      │     │ Components   │
└──────┬──────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ Agent CLI   │────►│ Agent       │
└──────┬──────┘     │ Components   │
       │            └─────────────┘
       ▼
┌─────────────┐     ┌─────────────┐
│Security CLI │────►│ Security    │
└──────┬──────┘     │ Components   │
       │            └─────────────┘
       ▼
┌─────────────┐     ┌─────────────┐
│Deployment CLI────►│ Deployment  │
└─────────────┘     │ Components   │
                    └─────────────┘
```

**Key Interactions:**
1. **Configuration CLI** interacts with configuration components to prepare deployment configuration
2. **Agent CLI** interacts with agent components to configure agents for deployment
3. **Security CLI** interacts with security components to configure security for deployment
4. **Deployment CLI** interacts with deployment components to deploy the multi-agent system

## Component Interface Details

### Agent Component Interface

The Agent CLI tools interact with agent components through these interfaces:

```python
# Agent CLI to Agent Component Interface
class AgentInterface:
    async def create_agent(self, config):
        """Create a new agent."""
        pass

    async def start_agent(self, agent_id):
        """Start an agent."""
        pass

    async def stop_agent(self, agent_id):
        """Stop an agent."""
        pass

    async def get_agent_status(self, agent_id):
        """Get agent status."""
        pass

    async def list_agents(self):
        """List all agents."""
        pass
```

**Key Commands:**
- `openmas agent create` - Creates a new agent
- `openmas agent start` - Starts an agent
- `openmas agent stop` - Stops an agent
- `openmas agent status` - Shows agent status
- `openmas agent list` - Lists all agents

### Protocol Component Interface

The Protocol CLI tools interact with protocol components through these interfaces:

```python
# Protocol CLI to Protocol Component Interface
class ProtocolInterface:
    async def register_protocol(self, protocol_config):
        """Register a protocol adapter."""
        pass

    async def test_protocol(self, protocol_id, test_message):
        """Test a protocol adapter."""
        pass

    async def list_protocols(self):
        """List all protocol adapters."""
        pass

    async def get_protocol_status(self, protocol_id):
        """Get protocol adapter status."""
        pass
```

**Key Commands:**
- `openmas protocol register` - Registers a protocol adapter
- `openmas protocol test` - Tests a protocol adapter
- `openmas protocol list` - Lists all protocol adapters
- `openmas protocol status` - Shows protocol adapter status

### Configuration Component Interface

The Configuration CLI tools interact with configuration components through these interfaces:

```python
# Configuration CLI to Configuration Component Interface
class ConfigInterface:
    async def validate_config(self, config_path):
        """Validate a configuration file."""
        pass

    async def generate_config(self, template, output_path):
        """Generate a configuration file from a template."""
        pass

    async def merge_configs(self, config_paths, output_path):
        """Merge multiple configuration files."""
        pass

    async def get_config_schema(self, component_type):
        """Get configuration schema for a component type."""
        pass
```

**Key Commands:**
- `openmas config validate` - Validates a configuration file
- `openmas config generate` - Generates a configuration file from a template
- `openmas config merge` - Merges multiple configuration files
- `openmas config schema` - Shows configuration schema for a component

### Deployment Component Interface

The Deployment CLI tools interact with deployment components through these interfaces:

```python
# Deployment CLI to Deployment Component Interface
class DeploymentInterface:
    async def deploy(self, deployment_config):
        """Deploy a system according to deployment configuration."""
        pass

    async def undeploy(self, deployment_id):
        """Undeploy a previously deployed system."""
        pass

    async def get_deployment_status(self, deployment_id):
        """Get deployment status."""
        pass

    async def list_deployments(self):
        """List all deployments."""
        pass

    async def scale_deployment(self, deployment_id, component_type, replicas):
        """Scale a deployment component."""
        pass
```

**Key Commands:**
- `openmas deploy` - Deploys a system
- `openmas undeploy` - Undeploys a system
- `openmas deploy status` - Shows deployment status
- `openmas deploy list` - Lists all deployments
- `openmas deploy scale` - Scales a deployment component

## CLI Tool Extension Points

The OpenMAS CLI tools provide extension points for integration with custom components:

### Command Extensions

Custom commands can be added to extend CLI functionality:

```python
from openmas.cli.command import Command

class CustomCommand(Command):
    name = "custom"
    description = "Custom command"

    def configure_parser(self, parser):
        parser.add_argument("--option", help="Custom option")

    async def execute(self, args):
        # Custom command implementation
        pass

# Register the command
from openmas.cli.registry import CommandRegistry
CommandRegistry.register(CustomCommand)
```

### Component Interface Extensions

Custom component interfaces can be implemented to extend interoperability:

```python
from openmas.cli.interface import ComponentInterface

class CustomInterface(ComponentInterface):
    component_type = "custom"

    async def custom_operation(self, *args, **kwargs):
        # Custom operation implementation
        pass

# Register the interface
from openmas.cli.registry import InterfaceRegistry
InterfaceRegistry.register(CustomInterface)
```

## Best Practices for CLI Interoperability

1. **Follow the Command Pattern**: Implement CLI commands as discrete, self-contained operations
2. **Use Consistent Interfaces**: Maintain consistent interfaces across component boundaries
3. **Validate Inputs Early**: Validate CLI inputs before passing them to components
4. **Provide Meaningful Feedback**: Return clear, actionable feedback from component operations
5. **Support Automation**: Ensure CLI tools can be used in scripts and automation workflows
6. **Maintain Backward Compatibility**: Preserve backward compatibility when evolving interfaces
7. **Document Interfaces**: Clearly document component interfaces and their behavior
8. **Include Examples**: Provide examples of common interoperability scenarios
9. **Error Handling**: Implement proper error handling across component boundaries
10. **Testing**: Test component interoperability thoroughly

## Related Documentation

- [CLI Overview](../README.md)
- [CLI Commands](../commands/README.md)
- [Agent Components](../../04_agents/README.md)
- [Protocol Components](../../02_protocols/README.md)
- [Configuration Components](../../03_configuration/README.md)
- [Deployment Components](../../15_deployment/README.md)
