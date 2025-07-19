# Creating Custom CLI Commands

This document provides a guide for creating custom commands for the OpenMAS CLI, allowing developers to extend the functionality while maintaining compatibility with OpenMAS's architectural principles.

## Overview

The OpenMAS CLI uses a plugin-based architecture that allows for the creation of custom commands. These commands can support new protocols, reasoning approaches, or specific workflow needs while maintaining compatibility with the unified configuration schema.

## Command Development Framework

Custom commands leverage the OpenMAS command framework, which provides:

1. **Argument Parsing**: Consistent argument handling aligned with other commands
2. **Configuration Integration**: Automatic loading and validation of configuration
3. **Protocol Abstraction**: Protocol-agnostic command execution
4. **Reasoning Approach Integration**: Support for various reasoning architectures
5. **Error Handling**: Standardized error reporting and handling

## Creating a Basic Custom Command

### 1. Create Command Class

Create a new Python file in your extension package:

```python
# my_extension/commands/my_command.py
from openmas.cli.command import BaseCommand

class MyCustomCommand(BaseCommand):
    """My custom command that does something useful."""
    
    name = "my-command"
    description = "Performs a custom operation"
    
    def configure_parser(self, parser):
        """Configure the argument parser."""
        parser.add_argument("--option", help="An option for my command")
        parser.add_argument("target", help="The target to operate on")
        
    def execute(self, args, config):
        """Execute the command with the given arguments and configuration."""
        # Access arguments
        target = args.target
        option = args.option
        
        # Access configuration
        protocol = config.get("cli.default_protocol", "a2a")
        
        # Command implementation
        self.console.print(f"Executing custom command on {target} with {protocol} protocol")
        
        # Perform operations...
        
        return 0  # Return success code
```

### 2. Register the Command

Create a plugin registration file:

```python
# my_extension/plugin.py
from openmas.cli.plugin import CLIPlugin
from my_extension.commands.my_command import MyCustomCommand

class MyExtensionPlugin(CLIPlugin):
    """Plugin that registers my custom commands."""
    
    def get_commands(self):
        """Return the commands provided by this plugin."""
        return [MyCustomCommand()]
```

### 3. Create a Setup Script

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="my-openmas-extension",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "openmas.cli.plugins": [
            "my_extension=my_extension.plugin:MyExtensionPlugin",
        ],
    },
    install_requires=[
        "openmas-cli>=0.3.0",
    ],
)
```

### 4. Install Your Extension

```bash
pip install -e .
```

## Protocol-Specific Commands

To create commands for specific protocols while maintaining reasoning agnosticism:

```python
from openmas.cli.command import ProtocolCommand

class MyA2ACommand(ProtocolCommand):
    """A command specific to the A2A protocol."""
    
    name = "a2a-specific"
    description = "Performs A2A-specific operations"
    protocol = "a2a"  # Specifies this command only works with A2A
    
    def configure_parser(self, parser):
        parser.add_argument("agent", help="The agent to operate on")
        
    def execute(self, args, config):
        # Access the A2A protocol handler
        a2a_handler = self.get_protocol_handler()
        
        # Use protocol-specific features
        a2a_handler.generate_agent_card(args.agent)
        
        return 0
```

## Reasoning-Specific Commands

For commands that work with specific reasoning approaches:

```python
from openmas.cli.command import ReasoningCommand

class BDICommand(ReasoningCommand):
    """A command for BDI reasoning operations."""
    
    name = "bdi-update"
    description = "Updates beliefs, desires, or intentions"
    reasoning_approach = "bdi"  # Specifies this command is for BDI reasoning
    
    def configure_parser(self, parser):
        parser.add_argument("--belief", help="Belief to update")
        parser.add_argument("agent", help="The agent to operate on")
        
    def execute(self, args, config):
        # Access the BDI reasoning engine
        bdi_engine = self.get_reasoning_engine()
        
        # Perform reasoning-specific operations
        if args.belief:
            bdi_engine.update_belief(args.agent, args.belief)
        
        return 0
```

## Protocol and Reasoning Agnostic Commands

To create commands that work across protocols and reasoning approaches:

```python
from openmas.cli.command import BaseCommand

class AgnosticCommand(BaseCommand):
    """A command that works with any protocol and reasoning approach."""
    
    name = "agnostic-command"
    description = "Works across protocols and reasoning approaches"
    
    def configure_parser(self, parser):
        parser.add_argument("--protocol", help="Override the protocol to use")
        parser.add_argument("--reasoning", help="Override the reasoning approach")
        parser.add_argument("agent", help="The agent to operate on")
        
    def execute(self, args, config):
        # Get the protocol handler based on args or config
        protocol_name = args.protocol or config.get("cli.default_protocol")
        protocol_handler = self.get_protocol_handler(protocol_name)
        
        # Get the reasoning engine based on args or config
        reasoning_name = args.reasoning or config.get("cli.default_reasoning")
        reasoning_engine = self.get_reasoning_engine(reasoning_name)
        
        # Perform protocol and reasoning agnostic operations
        # This maintains separation between communication and reasoning
        
        return 0
```

## Advanced Features

### Command Groups

Create command groups for organizing related commands:

```python
from openmas.cli.command import CommandGroup
from my_extension.commands.cmd1 import Command1
from my_extension.commands.cmd2 import Command2

class MyCommandGroup(CommandGroup):
    """A group of related commands."""
    
    name = "my-group"
    description = "Commands for my extension"
    
    def get_commands(self):
        return [Command1(), Command2()]
```

### Pre/Post Command Hooks

Create hooks that run before or after commands:

```python
from openmas.cli.hook import CommandHook

class MyPreCommandHook(CommandHook):
    """Hook that runs before command execution."""
    
    def pre_execute(self, command, args, config):
        print(f"About to execute: {command.name}")
        
class MyPostCommandHook(CommandHook):
    """Hook that runs after command execution."""
    
    def post_execute(self, command, args, config, result):
        print(f"Executed {command.name} with result: {result}")
```

Register hooks in your plugin:

```python
def get_hooks(self):
    return [MyPreCommandHook(), MyPostCommandHook()]
```

## Testing Custom Commands

Use the OpenMAS CLI testing framework:

```python
# test_my_command.py
from openmas.cli.testing import CommandTestCase

class TestMyCommand(CommandTestCase):
    """Tests for my custom command."""
    
    def test_basic_execution(self):
        """Test basic command execution."""
        result = self.run_command("my-command", ["--option", "value", "target"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Executing custom command", result.output)
```

## Configuration Schema Compliance

Custom commands must align with the unified configuration schema. Validate your configuration access patterns:

```python
from openmas.cli.config import validate_config_access

class MyCompliantCommand(BaseCommand):
    """A command that complies with the unified schema."""
    
    def execute(self, args, config):
        # This validates that the configuration path exists in the schema
        validate_config_access(config, "agents.my_agent.capabilities")
        
        # Proceed with command execution...
        return 0
```

## Best Practices

1. **Maintain Reasoning Agnosticism**: Separate communication logic from reasoning logic
2. **Respect Protocol Boundaries**: Don't assume a specific protocol unless necessary
3. **Follow Command Naming Conventions**: Use hyphenated names like `my-command`
4. **Provide Helpful Documentation**: Include detailed help text for commands and arguments
5. **Validate Against Schema**: Ensure command options align with the unified configuration schema
6. **Implement Proper Error Handling**: Provide clear error messages and appropriate exit codes
7. **Write Tests**: Create comprehensive tests for your commands

## See Also

- [Command Reference](../commands/README.md)
- [Configuration Options](../configuration/cli_config.md)
- [Component Interoperability](../interoperability/component_integration.md)
