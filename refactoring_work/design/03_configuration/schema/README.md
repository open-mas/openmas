# Component-Specific Configuration Schema Documentation

This directory contains component-specific documentation for the OpenMAS configuration schema. These documents provide detailed information about configuring individual components while referencing the definitive unified configuration schema.

## Structure and Purpose

The component-specific schema documentation follows these principles:

1. **Single Source of Truth** - The [unified configuration schema](../unified_configuration_schema.md) in the parent directory is the authoritative reference for all configuration
2. **Component-Specific Details** - Each file in this directory provides component-specific documentation and examples
3. **No Duplication** - These documents should not duplicate schema definitions from the unified schema
4. **Cross-References** - Components refer to the unified schema rather than duplicating definitions
5. **Extended Documentation** - These files provide more detailed explanations and examples than the unified schema

## Contents

| File | Description |
|------|-------------|
| `agents.md` | Agent configuration schema documentation |
| `protocols.md` | Protocol configuration schema documentation |
| `protocols_reference.md` | Detailed reference and examples for protocol configuration |
| `integrations.md` | External integrations configuration schema |
| `extensions.md` | Extension system configuration schema |
| `communication_patterns.md` | Communication patterns configuration schema |
| `security.md` | Security configuration schema |

## Usage Guide

When documenting configuration for a specific component:

1. **DO NOT duplicate schema content** from the unified configuration schema
2. **DO reference** the [unified configuration schema](../unified_configuration_schema.md) as the definitive source of truth
3. **DO provide** component-specific examples and additional explanations
4. **DO update** both the unified schema and the component schema when making changes
5. **DO link to** related schema documentation

Example reference:
```markdown
For the complete schema definition, see [Integration Configuration Schema](/03_configuration/schema/integrations.md).
```
