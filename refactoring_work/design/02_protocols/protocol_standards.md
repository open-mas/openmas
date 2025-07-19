# OpenMAS Protocol Documentation Standards

## Overview

This document defines the documentation standards for protocols in OpenMAS. It specifies how each protocol should be documented to ensure consistency and completeness across all supported protocols.

## Protocol Documentation Template

Each protocol in OpenMAS should be documented following this standard structure:

### Basic Protocol Information

```markdown
## Protocol Definition
- **Name**: [Protocol Name]
- **Version**: [Protocol Version]
- **Specification URL**: [Link to official specification]
- **Purpose**: [Brief description of protocol's purpose]
- **Transport**: [Transport mechanism: HTTP, WebSockets, stdio, SSE, etc.]
- **Protocol Compatibility**: [Which protocols this protocol can interoperate with and how]
- **Reasoning Agnosticism**: [How this protocol maintains separation between communication and reasoning]
```

### Message Format

```markdown
## Message Format

### Message Structure
Messages follow this structure:

```json
{
  // Example message format
}
```

### Message Types
- **Type 1**: Description of first message type
- **Type 2**: Description of second message type
```

### Features and Capabilities

```markdown
## Features

### Core Features
- **Feature 1**: Description of first feature
- **Feature 2**: Description of second feature

### Optional Features
- **Optional Feature 1**: Description with support details
- **Optional Feature 2**: Description with support details
```

### Authentication and Security

```markdown
## Security

### Authentication Methods
- **Method 1**: Description of first authentication method
- **Method 2**: Description of second authentication method

### Security Considerations
- Security consideration 1
- Security consideration 2
```

### Implementation

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

### Configuration

```markdown
## Configuration

For the complete configuration schema, refer to the [unified configuration schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md).

### Example Configuration
```yaml
# Example configuration
```
```

## Protocol-Specific Directories

Each protocol should have its own directory containing:

1. `README.md` - Overview and navigation
2. `[protocol_name]_protocol.md` - Protocol specification
3. `[protocol_name]_implementation.md` - Implementation details

## Reference Documentation

All protocol documentation should include references to:

1. The unified configuration schema
2. Related communication patterns
3. Related architecture documents

## References

- [Documentation Structure](/refactoring_work/00b_overview/documentation_structure.md)
- [Unified Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Communication Patterns](/refactoring_work/00b_overview/07_communication_patterns/README.md)
