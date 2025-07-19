# Protocol Documentation Standard

This document outlines the standard format for documenting protocols in OpenMAS. It provides guidance on how to structure protocol documentation consistently across all supported protocols.

## Protocol Definition Section

Each protocol should start with a clear definition:

```markdown
## Protocol Definition
- **Name**: [Protocol Name]
- **Version**: [Protocol Version]
- **Specification URL**: [Link to official specification]
- **Purpose**: [Brief description of protocol's purpose]
- **Transport**: [Transport mechanism: stdio, sse, streamable, etc.]
- **Protocol Compatibility**: [Which protocols this protocol can interoperate with and how]
- **Reasoning Agnosticism**: [How this protocol maintains separation between communication and reasoning]
```

## Message Format Section

Document the message structure and examples:

```markdown
## Message Format

### Message Structure
Messages in [Protocol] follow this structure:

```json
{
  // Example message format
}
```

### Message Types
- **Type 1**: Description and example
- **Type 2**: Description and example
```

## Features Section

Detail the protocol's features:

```markdown
## Features

### Core Features
- **Feature 1**: Description with example
- **Feature 2**: Description with example

### Optional Features
- **Optional Feature 1**: Description with support details
- **Optional Feature 2**: Description with support details
```

## Configuration Section

> **Important**: For configuration details, always reference the unified schema. Do not duplicate schema content.

```markdown
## Configuration

For the complete configuration schema, refer to the [Unified Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md) and [Protocol Schema Details](/refactoring_work/00b_overview/03_configuration/schema/protocols.md).

### Example Configuration
```yaml
# Basic example only - refer to schema for full details
communicator:
  protocol: "protocol_name"
  # Other basic settings
```
```

## Implementation Section

Provide implementation guidance:

```markdown
## Implementation

### Basic Usage
```python
# Example code showing basic usage
```

### Advanced Usage
```python
# Example code showing advanced usage
```
```

## Communication Patterns Section

Explain supported communication patterns:

```markdown
## Communication Patterns

This protocol supports these patterns:

- **Pattern 1**: Description and limitations
- **Pattern 2**: Description and limitations

For detailed pattern documentation, see [Communication Patterns](/refactoring_work/00b_overview/07_communication_patterns/README.md).
```

## Protocol-Specific Directories

Each protocol should have its own directory containing:

1. `README.md` - Overview and navigation
2. `[protocol_name]_protocol.md` - Protocol specification details
3. `[protocol_name]_implementation.md` - Implementation details and examples

## Schema References

All protocol documentation must include this standard reference block in the configuration section:

```markdown
This document provides protocol-specific documentation for [PROTOCOL NAME].
For the complete and definitive schema, please refer to the [unified configuration schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md) document.
```

## References

- [Documentation Structure](/refactoring_work/00b_overview/documentation_structure.md)
- [Unified Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Protocol Schema Details](/refactoring_work/00b_overview/03_configuration/schema/protocols.md)
- [Communication Patterns](/refactoring_work/00b_overview/07_communication_patterns/README.md)
