# Asset Management Integration

## Overview

This document describes how the Asset Management System integrates with other components of OpenMAS. Understanding these integration points is essential for implementing asset-aware components that leverage the full capabilities of the framework.

## Integration with Other Components

### Agent Framework Integration

The Asset Management System integrates with the agent framework (`/04_agents/`) through:

- **Asset-Based Capabilities**: Agent capabilities that depend on specific assets
- **Dynamic Model Loading**: On-demand loading of models and other assets
- **Resource Management**: Efficient allocation and deallocation of asset resources
- **Capability Discovery**: Discovery of capabilities based on available assets

```
Agent ──> Asset Request ──> Asset Management System
```

### Protocol Layer Integration

The Asset Management System interacts with the protocol layer (`/02_protocols/`) through:

- **Asset Transfer**: Protocol-specific mechanisms for transferring assets
- **Asset Discovery**: Protocol-specific discovery of available assets
- **Remote Asset Access**: Access to assets on remote systems
- **Asset Streaming**: Streaming of large assets across protocols

```
Protocol Layer ──> Asset Transfer ──> Asset Management System
```

### Configuration System Integration

The Asset Management System is configured through the configuration system (`/03_configuration/`) via:

- **Asset Definitions**: Declaration of assets in configuration
- **Source Configuration**: Configuration of asset sources
- **Caching Policies**: Configuration of caching behavior
- **Version Constraints**: Specification of version requirements

```
Configuration ──> Asset Definitions ──> Asset Management System
```

### Knowledge Representation Integration

The Asset Management System supports the knowledge representation system (`/09_knowledge_representation/`) through:

- **Knowledge Assets**: Management of knowledge bases and ontologies
- **Embedding Models**: Provision of embedding models for knowledge representation
- **Reasoning Models**: Management of models used for reasoning
- **Dataset Management**: Storage and access to datasets for knowledge generation

```
Knowledge Representation ──> Knowledge Asset Request ──> Asset Management System
```

### Prompt Management Integration

The Asset Management System interacts with the prompt management system (`/11_prompt_management/`) through:

- **Prompt Template Storage**: Management of prompt templates as assets
- **Model-Specific Templates**: Association of templates with specific models
- **Version Alignment**: Ensuring compatibility between prompt and model versions
- **Template Discovery**: Discovery of available templates

```
Prompt Management ──> Template Request ──> Asset Management System
```

### Observability Integration

The Asset Management System emits observability data to the observability system (`/12_observability/`) through:

- **Asset Operations Logging**: Logging of asset lifecycle events
- **Usage Metrics**: Metrics on asset usage patterns
- **Performance Monitoring**: Monitoring of asset loading and processing times
- **Storage Metrics**: Tracking of asset storage utilization

```
Asset Management ──> Logs/Metrics ──> Observability System
```

## Cross-Cutting Integration Concerns

Several integration aspects cut across multiple components:

1. **Asset Referencing**: Standardized way to reference assets across components
2. **Resource Coordination**: Coordination of resource usage between components
3. **Dependency Management**: Management of asset dependencies across components
4. **Version Compatibility**: Ensuring compatible versions across integrated components
5. **Security Context**: Propagation of security context for asset operations

## Implementation Considerations

When implementing asset integration:

1. Use the standard asset interfaces for requesting and accessing assets
2. Follow resource management patterns for proper cleanup
3. Consider performance implications of asset operations
4. Specify explicit version requirements for predictable behavior
5. Leverage observability for monitoring asset operations

## Common Integration Patterns

### Asset-Based Capability Registration

```python
class LLMAgent(Agent):
    async def setup(self):
        # Declare asset requirements
        self.require_asset("llm_model", version="^1.0.0")
        
        # Register capability based on available asset
        if self.has_asset("llm_model"):
            self.register_capability("text_generation")
```

### Dynamic Asset Loading

```python
class EmbeddingService:
    async def get_embedding(self, text):
        # Dynamic asset loading
        embedding_model = await self.asset_manager.load_asset(
            "embedding_model", 
            version="^2.0.0"
        )
        
        # Use the asset
        result = embedding_model.embed(text)
        return result
```

### Asset Version Coordination

```python
class PromptTemplate:
    async def format_for_model(self, model, inputs):
        # Get compatible template version for model
        model_info = await self.asset_manager.get_asset_info(model.asset_id)
        compatible_template = await self.asset_manager.load_asset(
            "prompt_template",
            name=self.template_name,
            version=model_info.compatible_template_version
        )
        
        # Format using compatible template
        return compatible_template.format(inputs)
```

## References

- [Agent Framework](/refactoring_work/00b_overview/04_agents/README.md)
- [Protocol Layer](/refactoring_work/00b_overview/02_protocols/README.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Knowledge Representation](/refactoring_work/00b_overview/09_knowledge_representation/README.md)
- [Prompt Management](/refactoring_work/00b_overview/11_prompt_management/README.md)
- [Observability System](/refactoring_work/00b_overview/12_observability/README.md)
