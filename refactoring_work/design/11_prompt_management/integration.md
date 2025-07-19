# Prompt Management Integration

## Overview

This document describes how the Prompt Management system integrates with other components of OpenMAS. Understanding these integration points is essential for implementing prompt-aware components that leverage the full capabilities of the framework.

## Integration with Other Components

### Agent Framework Integration

The Prompt Management system integrates with the agent framework (`/04_agents/`) through:

- **Prompt-Based Capabilities**: Agent capabilities that utilize prompt templates
- **Conversation Management**: Management of prompt context in conversations
- **Agent Specialization**: Agent-specific prompt templates
- **LLM Integration**: Standardized interfaces to language models

```
Agent ──> Prompt Request ──> Prompt Management System ──> LLM
```

### Protocol Layer Integration

The Prompt Management system interacts with the protocol layer (`/02_protocols/`) through:

- **Protocol-Specific Formats**: Adaptation of prompts for specific protocols
- **Message Translation**: Translation between prompt formats and protocol messages
- **Context Preservation**: Maintaining context across protocol boundaries
- **System Message Standardization**: Consistent handling of system messages

```
Protocol Layer ──> Message Format ──> Prompt Management System
```

### Configuration System Integration

The Prompt Management system is configured through the configuration system (`/03_configuration/`) via:

- **Template Definitions**: Declaration of prompt templates
- **Context Settings**: Configuration of context management
- **Model Parameters**: Configuration of model-specific parameters
- **Versioning Settings**: Management of template versions

```
Configuration ──> Template Definitions ──> Prompt Management System
```

### Knowledge Representation Integration

The Prompt Management system supports the knowledge representation system (`/09_knowledge_representation/`) through:

- **Knowledge Injection**: Inclusion of knowledge in prompts
- **Reasoning Prompts**: Templates for different reasoning approaches
- **Context Augmentation**: Augmentation of prompts with relevant knowledge
- **Prompt-Based Reasoning**: Implementation of prompt-based reasoning strategies

```
Knowledge Representation ──> Knowledge Context ──> Prompt Management System
```

### Asset Management Integration

The Prompt Management system utilizes the asset management system (`/10_asset_management/`) for:

- **Template Storage**: Management of prompt templates as assets
- **Version Management**: Versioning of prompt templates
- **Model Alignment**: Alignment of prompt versions with model versions
- **Template Distribution**: Distribution of templates across environments

```
Prompt Management ──> Template Asset Request ──> Asset Management System
```

### Observability Integration

The Prompt Management system emits observability data to the observability system (`/12_observability/`) through:

- **Template Usage Logging**: Logging of template usage
- **Token Metrics**: Metrics on token usage and context efficiency
- **Performance Monitoring**: Monitoring of prompt rendering and processing times
- **Context Analytics**: Analysis of context utilization

```
Prompt Management ──> Logs/Metrics ──> Observability System
```

## Cross-Cutting Integration Concerns

Several integration aspects cut across multiple components:

1. **Template Referencing**: Standardized way to reference templates across components
2. **Context Sharing**: Coordination of context usage between components
3. **Model Compatibility**: Ensuring compatible prompt formats across integrated components
4. **Version Alignment**: Ensuring compatible versions across integrated components
5. **Error Handling**: Consistent handling of prompt-related errors

## Implementation Considerations

When implementing prompt integration:

1. Use the standard template interfaces for generating prompts
2. Follow context management patterns for efficient context usage
3. Consider token limitations in prompt design
4. Specify explicit version requirements for prompt templates
5. Leverage observability for monitoring prompt performance

## Common Integration Patterns

### Prompt-Based Capability

```python
class QuestionAnsweringAgent(Agent):
    async def setup(self):
        # Register capability using prompt template
        self.register_capability(
            "answer_question",
            prompt_template="qa_template",
            prompt_version="^1.0.0"
        )
        
    async def answer_question(self, question):
        # Use prompt template with capability
        response = await self.prompt_manager.render_and_complete(
            "qa_template",
            variables={"question": question}
        )
        return response
```

### Protocol Adaptation

```python
class MCPProtocolAdapter:
    async def format_for_protocol(self, prompt_template, variables):
        # Adapt prompt for MCP protocol
        template = await self.prompt_manager.get_template(prompt_template)
        
        # Convert to MCP message format
        mcp_message = {
            "role": "system",
            "content": await template.render(variables)
        }
        
        return mcp_message
```

### Context Management

```python
class ConversationManager:
    async def prepare_context(self, conversation_id, current_input):
        # Prepare context for prompt
        history = await self.conversation_store.get_history(conversation_id)
        
        # Create context with prioritization
        context = await self.prompt_manager.create_context(
            system=self.system_prompt,
            history=history,
            current_input=current_input,
            max_tokens=4000
        )
        
        return context
```

## References

- [Agent Framework](/refactoring_work/00b_overview/04_agents/README.md)
- [Protocol Layer](/refactoring_work/00b_overview/02_protocols/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Knowledge Representation](/refactoring_work/00b_overview/09_knowledge_representation/README.md)
- [Asset Management](/refactoring_work/00b_overview/10_asset_management/README.md)
- [Observability System](/refactoring_work/00b_overview/12_observability/README.md)
