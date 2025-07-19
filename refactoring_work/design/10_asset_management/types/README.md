# Asset Types in OpenMAS

## Overview

This directory contains documentation about the different asset types supported by the OpenMAS Asset Management System. Assets are resources used by agents and other components, managed with consistent versioning, storage, and access patterns.

## Core Asset Types

OpenMAS supports several fundamental asset types, each with specific characteristics and usage patterns:

### 1. Model Assets

Machine learning models used by agents:

- **Model Files**: Serialized machine learning models
- **Model Weights**: Parameter files for neural networks
- **Tokenizers**: Text tokenization components
- **Configuration Files**: Model-specific configuration

Model assets follow these conventions:
```yaml
assets:
  llm_model:
    name: "gemma-2b"
    version: "1.0.0"
    asset_type: "model"
    model_type: "llm"
    source:
      type: "hf"
      repo_id: "google/gemma-2b"
```

### 2. Embedding Assets

Embeddings and embedding models:

- **Embedding Models**: Models that generate vector embeddings
- **Pre-computed Embeddings**: Stored vector representations
- **Quantized Embeddings**: Compressed embedding representations
- **Index Files**: Structures for efficient embedding retrieval

Embedding assets follow these conventions:
```yaml
assets:
  text_embeddings:
    name: "all-mpnet-base-v2"
    version: "2.0.0"
    asset_type: "embeddings"
    dimensions: 768
    source:
      type: "hf"
      repo_id: "sentence-transformers/all-mpnet-base-v2"
```

### 3. Data Assets

Structured and unstructured data resources:

- **Datasets**: Collections of examples or records
- **Knowledge Bases**: Structured knowledge sources
- **Reference Data**: Standardized reference information
- **Corpora**: Text collections for training or analysis

Data assets follow these conventions:
```yaml
assets:
  training_data:
    name: "qa-dataset"
    version: "2023.1"
    asset_type: "dataset"
    format: "jsonl"
    source:
      type: "http"
      url: "https://example.com/datasets/qa-dataset-2023.1.jsonl"
```

### 4. Prompt Assets

Prompt templates and related resources:

- **Prompt Templates**: Parameterized prompt structures
- **System Messages**: Reusable system instructions
- **Prompt Examples**: Few-shot learning examples
- **Prompt Collections**: Sets of related prompts

Prompt assets follow these conventions:
```yaml
assets:
  prompt_template:
    name: "qa-template"
    version: "1.2.0"
    asset_type: "prompt"
    compatible_models: ["gpt-4", "claude-2"]
    source:
      type: "local"
      path: "/prompts/qa-template.json"
```

### 5. Configuration Assets

Reusable configuration components:

- **Configuration Templates**: Parameterized configuration patterns
- **Default Configurations**: Standard configuration baselines
- **Environment Definitions**: Environment-specific settings
- **Configuration Profiles**: Sets of configuration options

Configuration assets follow these conventions:
```yaml
assets:
  config_template:
    name: "production-agent"
    version: "2.0.0"
    asset_type: "configuration"
    applies_to: ["agent"]
    source:
      type: "local"
      path: "/config/templates/production-agent.yaml"
```

## Asset Type Implementation

Each asset type implements these standard interfaces:

### Common Interface

All assets implement this core interface:
```python
class Asset(ABC):
    @property
    def asset_id(self) -> str:
        """Unique identifier for the asset."""
        pass
        
    @property
    def metadata(self) -> dict:
        """Asset metadata."""
        pass
        
    async def load(self) -> Any:
        """Load the asset into memory."""
        pass
        
    async def unload(self) -> None:
        """Unload the asset from memory."""
        pass
```

### Type-Specific Extensions

Each asset type extends the base interface with specialized capabilities:
```python
class ModelAsset(Asset):
    async def get_model(self) -> "Model":
        """Get the loaded model."""
        pass
        
    @property
    def model_type(self) -> str:
        """Type of the model."""
        pass
```

## Asset Metadata

All assets include standard metadata fields:

- **name**: User-friendly name of the asset
- **version**: Semantic version of the asset
- **asset_type**: Type category of the asset
- **description**: Human-readable description
- **created_at**: Creation timestamp
- **author**: Creator or publisher
- **license**: License information
- **tags**: Categorization tags
- **dependencies**: Other assets this asset depends on
- **compatibility**: Version compatibility information

## Asset Configuration Schema

Assets are configured through the unified configuration schema:

```yaml
# In configuration file
assets:
  [asset_id]:
    name: string
    version: string
    asset_type: string
    description: string (optional)
    source:
      type: string (http | hf | local | git)
      # Source-specific configuration
    metadata:
      # Additional metadata fields
    options:
      # Asset-type specific options
```

## References

- [Asset Management Architecture](/refactoring_work/00b_overview/10_asset_management/architecture.md)
- [Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Versioning System](/refactoring_work/00b_overview/10_asset_management/versioning/README.md)
