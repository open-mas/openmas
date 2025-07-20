# Extension Configuration

## Overview

This document provides guidance for configuring OpenMAS extensions. It focuses on usage patterns and best practices, while the complete schema definition is maintained in the [Unified Configuration Schema](/03_configuration/schema/extensions.md).

## Configuration Approach

OpenMAS uses a consistent configuration approach that supports:

1. **Reasoning Agnosticism** - Configuration works with all reasoning approaches
2. **Protocol Independence** - Configuration supports all protocols
3. **Single Source of Truth** - All schema definitions are centralized
4. **Environment Adaptability** - Configuration adapts to different environments

## Using the Unified Schema

For detailed schema information, always refer to the [Extension Configuration Schema](/03_configuration/schema/extensions.md), which includes:

- Complete property definitions for all extension types
- Detailed schema for each extension's options object
- Enum values for constrained fields
- Required vs. optional properties

## Configuration Examples

Below are minimal examples showing how to use extension configuration in practice. For complete schema details, see the unified schema documentation.

### Basic Extension Configuration

```yaml
extensions:
  extension_name:
    type: "extension_type"
    name: "extension_name"
    enabled: true
    options:
      # Extension-specific options
      option1: value1
      option2: value2
```

### Common Configuration Patterns

#### Environment Variable Substitution

OpenMAS supports environment variable substitution in configuration:

```yaml
extensions:
  my_extension:
    type: "my_extension_type"
    name: "my_extension"
    options:
      api_key: "${MY_API_KEY}"
      base_url: "${SERVICE_URL}"
```

#### Configuration Profiles

Different environments can use dedicated profiles:

```yaml
profiles:
  development:
    extensions:
      my_extension:
        options:
          debug: true
          endpoint: "http://localhost:8080"

  production:
    extensions:
      my_extension:
        options:
          debug: false
          endpoint: "https://api.production.example.com"
```

## Working with Extension Configuration

### Loading Configuration

```python
from openmas.config import load_configuration

# Load configuration from file
config = load_configuration("config.yaml")

# Access extension configuration
extension_config = config.extensions.get("my_extension")
```

### Programmatic Configuration

```python
from openmas.extensions import get_extension_registry

# Get extension registry
registry = get_extension_registry()

# Configure an extension dynamically
registry.configure_extension(
    extension_type="my_extension_type",
    extension_name="my_extension",
    config={
        "enabled": True,
        "options": {
            "option1": "value1",
            "option2": "value2"
        }
    }
)
```

## Extension Configuration Best Practices

1. **Use Environment Variables** - Store sensitive information in environment variables
2. **Validate Configuration** - Validate configuration against the schema
3. **Default Values** - Provide sensible defaults for optional properties
4. **Configuration Profiles** - Use profiles for different environments
5. **Consistent Naming** - Use consistent naming for extension types and names
6. **Documentation** - Document extension configuration in inline comments
7. **Minimal Configuration** - Keep configuration minimal and focused
8. **Reuse Common Patterns** - Follow established patterns for similar extensions
9. **Single Responsibility** - Each extension should have a single, clear purpose
10. **Configuration Versioning** - Version your configuration schema for compatibility
