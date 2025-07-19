# OpenMAS Asset Management

## Overview

This directory contains documentation about the Asset Management system in OpenMAS, which handles model files, embeddings, and asset versioning. The asset management system provides a unified approach to manage, version, and access various assets required by OpenMAS agents.

## Key Capabilities

The Asset Management system provides these core capabilities:

1. **Asset Types Management**
   - Model files (LLM models, embeddings, etc.)
   - Prompt templates
   - Knowledge bases
   - Media assets
   - Configuration assets

2. **Asset Versioning**
   - Semantic versioning for assets
   - Asset lineage tracking
   - Version compatibility management
   - Rollback capabilities

3. **Asset Storage**
   - Local storage support
   - Remote storage integration
   - Hybrid storage strategies
   - Asset caching

4. **Asset Access Control**
   - Role-based asset access
   - Asset usage tracking
   - Usage quotas and limitations

## Documentation Structure

| Document | Description |
|----------|-------------|
| [Asset Architecture](./architecture.md) | High-level architecture of the asset management system |
| [Asset Types](./types/README.md) | Documentation on different asset types |
| [Versioning System](./versioning/README.md) | Details on asset versioning approach |
| [Storage Providers](./storage/README.md) | Information on storage providers and configurations |
| [Integration Guide](./integration.md) | How to integrate assets with agents and other components |

## Integration with Other Components

The Asset Management system integrates with other OpenMAS components:

- **Agent Framework** - Provides assets to agents in `/04_agents/`
- **Prompt Management** - Manages prompt assets in coordination with `/11_prompt_management/`
- **Configuration** - Configured through the unified schema in `/03_configuration/`
