# Prompt Extensions

## Overview

Prompt extensions provide mechanisms for managing and customizing prompts across all protocols in OpenMAS. These extensions maintain the framework's core architectural principles of reasoning agnosticism and protocol independence while providing flexible prompt management capabilities.

## Extension Type Definition

- **Name**: Prompt Extensions
- **Purpose**: Manage and customize prompt templates and context handling
- **Component**: Prompt Management
- **Type**: Extension
- **Community Usage**: Enable developers to add custom prompt templates and handling strategies
- **Protocol Compatibility**: All protocols (A2A, MCP, HTTP, MQTT, gRPC)

## Key Capabilities

Prompt extensions provide these core capabilities:

1. **Template Management** - Manage reusable prompt templates
2. **Context Optimization** - Optimize context windows across reasoning approaches
3. **Protocol-Specific Adaptation** - Adapt prompts to protocol-specific requirements
4. **Reasoning Independence** - Handle prompts independently of reasoning approach
5. **Versioning Control** - Track and manage prompt versions
6. **Schema Validation** - Validate prompts against schemas

## Prompt Extension Types

### 1. Template Engines

Template engines provide prompt templating capabilities:

```python
from openmas.extensions import PromptTemplateExtension

class JinjaTemplateExtension(PromptTemplateExtension):
    """Jinja2-based template engine for prompts."""

    extension_type = "prompt_template"
    extension_name = "jinja_template"

    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)

    async def initialize(self):
        """Initialize the template engine."""
        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape

            # Set up Jinja environment
            self.env = Environment(
                loader=FileSystemLoader(self.config.get("template_directory", "./templates")),
                autoescape=select_autoescape(['html', 'xml'])
            )

            self.initialized = True
        except ImportError:
            raise RuntimeError("Jinja2 is required for JinjaTemplateExtension")

    async def render_template(self, template_name, variables):
        """Render a template with variables."""
        if not self.initialized:
            raise RuntimeError("Template engine not initialized")

        # Get the template
        template = self.env.get_template(template_name)

        # Render with variables
        return template.render(**variables)

    def get_template_schema(self, template_name):
        """Get the schema for a template."""
        # Get schema path based on template name
        schema_path = os.path.join(
            self.config.get("template_directory", "./templates"),
            template_name.replace(".j2", ".schema.json")
        )

        # Load schema if it exists
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                return json.load(f)

        return None
```

### 2. Context Managers

Context managers optimize prompt context windows:

```python
from openmas.extensions import PromptContextExtension

class DynamicContextManagerExtension(PromptContextExtension):
    """Dynamic context window manager for prompts."""

    extension_type = "prompt_context"
    extension_name = "dynamic_context_manager"

    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        self.max_tokens = config.get("max_tokens", 4096)
        self.token_estimator = None

    async def initialize(self):
        """Initialize the context manager."""
        # Set up token estimator
        self.token_estimator = self._create_token_estimator()
        self.initialized = True

    async def optimize_context(self, messages, constraints=None):
        """Optimize a context window based on constraints."""
        constraints = constraints or {}
        max_tokens = constraints.get("max_tokens", self.max_tokens)

        # Calculate current token usage
        total_tokens = sum(self._estimate_tokens(msg) for msg in messages)

        # If within limits, return unchanged
        if total_tokens <= max_tokens:
            return messages

        # Otherwise, optimize context
        return await self._optimize_context(messages, max_tokens)

    def _create_token_estimator(self):
        """Create a token estimator."""
        # Simple estimation method (4 chars ≈ 1 token)
        def estimate_tokens(text):
            if isinstance(text, str):
                return len(text) // 4 + 1
            return 0

        return estimate_tokens

    def _estimate_tokens(self, message):
        """Estimate tokens in a message."""
        if isinstance(message, str):
            return self.token_estimator(message)

        if isinstance(message, dict):
            # Sum token count from all string fields
            return sum(
                self.token_estimator(value)
                for value in message.values()
                if isinstance(value, str)
            )

        return 0

    async def _optimize_context(self, messages, max_tokens):
        """Optimize context to fit within token limit."""
        # Categorize messages by type/importance
        system_messages = []
        user_messages = []
        assistant_messages = []

        for msg in messages:
            if isinstance(msg, dict) and "role" in msg:
                if msg["role"] == "system":
                    system_messages.append(msg)
                elif msg["role"] == "user":
                    user_messages.append(msg)
                elif msg["role"] == "assistant":
                    assistant_messages.append(msg)

        # Strategy: Keep all system messages, prioritize recent message pairs
        optimized = list(system_messages)  # Start with system messages

        # Add most recent messages first
        remaining_tokens = max_tokens - sum(self._estimate_tokens(msg) for msg in optimized)

        # Create pairs of user/assistant messages, most recent first
        pairs = []
        for i in range(min(len(user_messages), len(assistant_messages))):
            user_idx = len(user_messages) - 1 - i
            asst_idx = len(assistant_messages) - 1 - i
            pairs.append((user_messages[user_idx], assistant_messages[asst_idx]))

        # Add pairs as long as they fit
        for user_msg, asst_msg in pairs:
            pair_tokens = self._estimate_tokens(user_msg) + self._estimate_tokens(asst_msg)
            if pair_tokens <= remaining_tokens:
                optimized.append(user_msg)
                optimized.append(asst_msg)
                remaining_tokens -= pair_tokens
            else:
                break

        return optimized
```

### 3. Prompt Adapters

Prompt adapters convert prompts between protocols:

```python
from openmas.extensions import PromptAdapterExtension

class MCPPromptAdapterExtension(PromptAdapterExtension):
    """Adapter for MCP protocol prompts."""

    extension_type = "prompt_adapter"
    extension_name = "mcp_prompt_adapter"

    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)

    async def adapt_to_protocol(self, prompt, protocol, options=None):
        """Adapt a prompt to a specific protocol format."""
        options = options or {}

        if protocol == "mcp":
            return await self._adapt_to_mcp(prompt, options)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    async def adapt_from_protocol(self, protocol_prompt, protocol, options=None):
        """Adapt from a protocol format to a standard prompt."""
        options = options or {}

        if protocol == "mcp":
            return await self._adapt_from_mcp(protocol_prompt, options)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    async def _adapt_to_mcp(self, prompt, options):
        """Adapt a standard prompt to MCP format."""
        # Handle different prompt formats
        if isinstance(prompt, str):
            # Simple string prompt
            return {
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            }

        elif isinstance(prompt, list):
            # List of messages
            mcp_messages = []

            for message in prompt:
                if isinstance(message, str):
                    # Default to user role for string messages
                    mcp_messages.append({
                        "role": "user",
                        "content": message
                    })
                elif isinstance(message, dict) and "role" in message and "content" in message:
                    # Already in proper format
                    mcp_messages.append({
                        "role": message["role"],
                        "content": message["content"]
                    })

            return {
                "messages": mcp_messages
            }

        elif isinstance(prompt, dict):
            # Dictionary format
            if "messages" in prompt:
                # Already in MCP format
                return prompt
            elif "system" in prompt or "user" in prompt or "assistant" in prompt:
                # Role-based dictionary
                mcp_messages = []

                if "system" in prompt:
                    mcp_messages.append({
                        "role": "system",
                        "content": prompt["system"]
                    })

                if "user" in prompt:
                    user_content = prompt["user"]
                    if isinstance(user_content, list):
                        for content in user_content:
                            mcp_messages.append({
                                "role": "user",
                                "content": content
                            })
                    else:
                        mcp_messages.append({
                            "role": "user",
                            "content": user_content
                        })

                if "assistant" in prompt:
                    assistant_content = prompt["assistant"]
                    if isinstance(assistant_content, list):
                        for content in assistant_content:
                            mcp_messages.append({
                                "role": "assistant",
                                "content": content
                            })
                    else:
                        mcp_messages.append({
                            "role": "assistant",
                            "content": assistant_content
                        })

                return {
                    "messages": mcp_messages
                }

        # Default case
        return {
            "messages": [{
                "role": "user",
                "content": str(prompt)
            }]
        }

    async def _adapt_from_mcp(self, mcp_prompt, options):
        """Adapt from MCP format to standard prompt."""
        if not isinstance(mcp_prompt, dict) or "messages" not in mcp_prompt:
            raise ValueError("Invalid MCP prompt format")

        # Extract messages
        messages = []
        for msg in mcp_prompt["messages"]:
            if "role" in msg and "content" in msg:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        return messages
```

## Extension Configuration

Prompt extensions are configured through the unified configuration schema. For complete schema information, refer to the [Extension Configuration Schema](/03_configuration/schema/extensions.md#prompt-extensions):

```yaml
extensions:
  jinja_template:
    type: "prompt_template"
    name: "jinja_template"
    enabled: true
    options:
      template_directory: "/path/to/templates"
      default_template: "default.j2"

  dynamic_context_manager:
    type: "prompt_context"
    name: "dynamic_context_manager"
    enabled: true
    options:
      max_tokens: 4096
      prioritize_recent: true
      preserve_system: true
```

## Prompt Types

Prompt extensions can handle these standard types:

1. **System Prompts** - Define system behavior and context
2. **User Prompts** - Represent user inputs with variables
3. **Assistant Prompts** - Template assistant responses
4. **Function Prompts** - Define function calls and parameters
5. **Few-Shot Prompts** - Example-based templates for reasoning
6. **Chain Prompts** - Connected sequences of prompts
7. **Conditional Prompts** - Context-dependent prompt selection

## Protocol Mapping

Prompt extensions provide consistent mappings between OpenMAS prompts and protocol-specific formats:

### MCP Protocol Mapping

```yaml
prompt_mapping:
  mcp:
    system_prompt:
      message_type: "system"
    user_prompt:
      message_type: "user"
    assistant_prompt:
      message_type: "assistant"
    function_prompt:
      message_type: "function"
```

### A2A Protocol Mapping

```yaml
prompt_mapping:
  a2a:
    system_prompt:
      capability: "set_system_prompt"
    user_prompt:
      capability: "set_user_prompt"
    assistant_prompt:
      capability: "set_assistant_prompt"
    function_prompt:
      capability: "call_function"
```

## Implementation Example

Using prompt extensions in code:

```python
# Get template engine extension
template_engine = extension_registry.get_extension(
    "prompt_template",
    "jinja_template"
)

# Render a template
prompt = await template_engine.render_template(
    "conversation.j2",
    {
        "user_name": "Alice",
        "topic": "weather forecast",
        "location": "San Francisco"
    }
)

# Optimize context
context_manager = extension_registry.get_extension(
    "prompt_context",
    "dynamic_context_manager"
)

optimized_messages = await context_manager.optimize_context(
    [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Tell me about the weather"},
        {"role": "assistant", "content": "It's sunny today"},
        {"role": "user", "content": prompt}
    ],
    constraints={"max_tokens": 2048}
)

# Adapt to protocol format
adapter = extension_registry.get_extension(
    "prompt_adapter",
    "mcp_prompt_adapter"
)

mcp_prompt = await adapter.adapt_to_protocol(
    optimized_messages,
    "mcp"
)
```

## Template Example

A typical Jinja2 template for prompts:

```jinja
{# System prompt template #}
You are a helpful assistant that provides {{ expertise }} information.
{% if personality %}
Your personality is {{ personality }}.
{% endif %}

{# User query template #}
User query: {{ query }}
{% if context %}
Additional context:
{{ context }}
{% endif %}

{# Instructions template #}
{% if format_instructions %}
Please format your response as {{ format_instructions }}.
{% endif %}
```

## Reasoning Agnosticism

Prompt extensions maintain OpenMAS's reasoning agnosticism by:

1. **Content Agnosticism** - Templates focus on structure, not reasoning logic
2. **Protocol Independence** - Prompts work consistently across all protocols
3. **Abstract Interfaces** - Extensions expose abstract interfaces regardless of reasoning approach
4. **Adapters and Converters** - Adapters bridge between prompts and reasoning-specific requirements

This enables agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) to work with the same prompt templates consistently.
