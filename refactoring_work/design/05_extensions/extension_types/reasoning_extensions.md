# Reasoning Extensions

## Overview

Reasoning Extensions provide a mechanism to implement custom reasoning approaches for OpenMAS agents. They enable the "brain" part of OpenMAS's body-brain separation, allowing developers to create diverse reasoning strategies while maintaining the framework's reasoning agnosticism.

## Base Class

Reasoning Extensions must inherit from the `ReasoningExtension` base class:

```python
from openmas.extensions import ReasoningExtension

class MyReasoningExtension(ReasoningExtension):
    """A custom reasoning extension."""
```

## Required Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `create_reasoner(agent_config)` | Create a reasoner instance for an agent | `agent_config`: Agent configuration dictionary | Reasoner instance |

## Optional Methods

| Method | Description | Parameters | Return Value |
|--------|-------------|------------|--------------|
| `validate_config()` | Validate the extension configuration | None | None, raises exception if invalid |
| `initialize()` | Initialize the extension | None | None |
| `get_reasoner_metadata()` | Get metadata about the reasoning approach | None | Dictionary of metadata |
| `get_supported_capabilities()` | Get capabilities supported by this reasoner | None | List of capability descriptors |

## Configuration Schema

Reasoning Extensions are configured in the unified configuration schema under the `extensions` section with `type: "reasoning"`:

```yaml
extensions:
  my_reasoning_extension:
    type: "reasoning"
    name: "my_reasoning_extension"
    enabled: true
    options:
      approach: "rule_based"  # or "llm", "bdi", "kr_symbolic", "hybrid"
      knowledge_base:
        type: "memory"
        max_items: 1000
      # Additional configuration specific to this extension
```

### Options Schema

The `options` block for Reasoning Extensions supports the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `approach` | string | Yes | The reasoning approach identifier |
| `knowledge_base` | object | No | Knowledge base configuration |
| `knowledge_base.type` | string | Yes (if knowledge_base present) | Knowledge base type |
| `llm_provider` | string | No | LLM provider to use (for LLM-based reasoning) |
| `decision_strategies` | object | No | Configuration for decision-making strategies |
| `debug_mode` | boolean | No | Enable detailed debugging output |

For the complete schema definition, refer to the [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md#reasoning-extension-options).

## Interaction Model

Reasoning Extensions interact with the OpenMAS framework through the following mechanisms:

1. **Registration**: The extension is registered with the extension registry
2. **Discovery**: The agent framework discovers available reasoning extensions
3. **Creation**: When an agent needs a reasoner, it calls the appropriate extension
4. **Message Processing**: The created reasoner processes messages received by the agent
5. **Response Generation**: The reasoner generates appropriate responses
6. **Knowledge Integration**: The reasoner interacts with the Knowledge Representation & Reasoning (KR&R) System

The Agent Framework maintains control over when reasoning is invoked, while the extension provides the specific reasoning implementation.

## Code Example

Here's a minimal example of a Reasoning Extension that implements a rule-based approach:

```python
from openmas.extensions import ReasoningExtension
from openmas.reasoning import BaseReasoner
import re
from typing import Dict, List, Any

class RuleBasedReasoner(BaseReasoner):
    """Rule-based reasoner implementation."""
    
    def __init__(self, config):
        super().__init__(config)
        self.rules = config.get("rules", [])
        self.variables = {}
        self.compile_rules()
    
    def compile_rules(self):
        """Compile rules for efficient matching."""
        self.compiled_rules = []
        for rule in self.rules:
            pattern = rule.get("pattern", "")
            action = rule.get("action", "")
            priority = rule.get("priority", 0)
            
            try:
                compiled_pattern = re.compile(pattern, re.IGNORECASE)
                self.compiled_rules.append({
                    "pattern": compiled_pattern,
                    "action": action,
                    "priority": priority
                })
            except re.error as e:
                self.logger.error(f"Failed to compile rule pattern '{pattern}': {e}")
        
        # Sort by priority (higher first)
        self.compiled_rules.sort(key=lambda r: r["priority"], reverse=True)
    
    async def process_message(self, message):
        """Process a message using the rule-based approach."""
        # Extract message content
        content = message.get_content_text()
        
        # Find matching rules
        matching_rules = []
        for rule in self.compiled_rules:
            match = rule["pattern"].search(content)
            if match:
                matching_rules.append((rule, match))
        
        if not matching_rules:
            # No rule matched, use default response
            return self.create_response(message, "I don't know how to respond to that.")
        
        # Use the highest priority matching rule
        rule, match = matching_rules[0]
        
        # Extract variables from match
        variables = match.groupdict()
        self.variables.update(variables)
        
        # Execute the action
        try:
            response_text = self.execute_action(rule["action"], variables)
            return self.create_response(message, response_text)
        except Exception as e:
            self.logger.error(f"Error executing rule action: {e}")
            return self.create_response(message, "I encountered an error processing your request.")
    
    def execute_action(self, action, variables):
        """Execute a rule action with variables."""
        # Simple template substitution
        result = action
        for var_name, var_value in variables.items():
            result = result.replace(f"{{{var_name}}}", var_value)
        
        # Replace global variables
        for var_name, var_value in self.variables.items():
            result = result.replace(f"${{{var_name}}}", str(var_value))
        
        return result
    
    def create_response(self, message, response_text):
        """Create a response to the message."""
        return {
            "text": response_text,
            "in_response_to": message.id
        }

class RuleBasedReasoningExtension(ReasoningExtension):
    """Extension that provides rule-based reasoning."""
    
    extension_type = "reasoning"
    extension_name = "rule_based"
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
    
    def validate_config(self):
        """Validate the extension configuration."""
        options = self.config.get("options", {})
        if options.get("approach") != "rule_based":
            raise ValueError("Rule-based reasoning extension requires 'approach: rule_based' in options")
    
    def get_reasoner_metadata(self):
        """Get metadata about the reasoning approach."""
        return {
            "name": "Rule-Based Reasoning",
            "description": "Simple pattern-matching and rule-based reasoning",
            "capabilities": ["text_processing", "pattern_matching", "template_responses"],
            "requires_llm": False,
            "requires_kb": False
        }
    
    def get_supported_capabilities(self):
        """Get capabilities supported by this reasoner."""
        return [
            {
                "id": "text_processing",
                "name": "Text Processing",
                "description": "Process text inputs using pattern matching"
            },
            {
                "id": "pattern_matching",
                "name": "Pattern Matching",
                "description": "Match text against regular expression patterns"
            },
            {
                "id": "template_responses",
                "name": "Template Responses",
                "description": "Generate responses based on templates with variable substitution"
            }
        ]
    
    def create_reasoner(self, agent_config):
        """Create a rule-based reasoner instance."""
        # Extract rule-based reasoning configuration
        reasoning_config = agent_config.get("reasoning", {})
        rule_config = reasoning_config.get("rule_based", {})
        
        # Add rules from the configuration
        rules = rule_config.get("rules", [])
        
        # Create reasoner instance with rules
        return RuleBasedReasoner({
            "rules": rules,
            "debug": reasoning_config.get("debug_mode", False)
        })
```

### Configuration Example

```yaml
extensions:
  rule_based:
    type: "reasoning"
    name: "rule_based"
    enabled: true
    options:
      approach: "rule_based"
      debug_mode: true

# Agent configuration that uses this reasoning extension
agents:
  greeter_agent:
    # ... other agent configuration ...
    reasoning:
      type: "rule_based"
      rule_based:
        rules:
          - pattern: "hello|hi|hey"
            action: "Hello! How can I help you today?"
            priority: 10
          - pattern: "my name is (?P<name>\\w+)"
            action: "Nice to meet you, {name}!"
            priority: 20
          - pattern: "what is the weather in (?P<location>\\w+)"
            action: "I don't have real-time weather data for {location}."
            priority: 15
```

## Integration with KR&R System

Reasoning Extensions can integrate with the Knowledge Representation & Reasoning (KR&R) System to access structured knowledge:

```python
# Example of reasoning extension accessing KR&R system
from openmas.krr import IKnowledgeBase

class KnowledgeEnabledReasoner(BaseReasoner):
    """Reasoner that uses the KR&R system."""
    
    def __init__(self, config, knowledge_base=None):
        super().__init__(config)
        self.knowledge_base = knowledge_base
    
    async def process_message(self, message):
        """Process a message using knowledge from the KR&R system."""
        content = message.get_content_text()
        
        # Use the knowledge base to find relevant knowledge
        if self.knowledge_base:
            facts = await self.knowledge_base.query({"text": content})
            if facts:
                # Use the facts to generate a response
                return self.create_knowledge_based_response(message, facts)
        
        # Fallback if no relevant knowledge
        return self.create_response(message, "I don't have information about that.")
```

## Best Practices

1. **Maintain Reasoning Agnosticism**: Design your extension to work with the body-brain separation
2. **Clear State Management**: Manage reasoner state carefully and document it
3. **Error Handling**: Implement robust error handling for reasoning failures
4. **Knowledge Integration**: When appropriate, integrate with the KR&R System
5. **Resource Management**: Be mindful of resource usage, especially for complex reasoning
6. **Protocol Independence**: Make your reasoner work with any protocol unless specifically designed for one

## Related Documentation

- [Extension System Design](../design/design_extension_system.md)
- [Reasoning System Design](../../08_reasoning/design_reasoning_system.md)
- [Extension Development Guide](../development/guide.md)
- [Knowledge Representation Integration](../../09_knowledge_representation/kr_reasoning_integration.md)
