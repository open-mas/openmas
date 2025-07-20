# OpenMAS Refactoring Knowledge Base

This directory contains reference information to support the OpenMAS refactoring process. These resources provide detailed information about frameworks, libraries, patterns, and best practices that should be incorporated into the refactored components.

## Knowledge Base Structure

```
knowledge_base/
├── mcp/                # Model Context Protocol documentation
│   └── index.md        # MCP overview and reference
├── testing/            # Testing patterns and strategies
│   └── index.md        # Testing overview and best practices
├── design_patterns/    # Design patterns used in OpenMAS
│   └── index.md        # Pattern descriptions and examples
└── libraries/          # Core library documentation
    └── index.md        # Library usage and best practices
```

## Core Knowledge Areas

### MCP (Model Context Protocol)

The [MCP directory](mcp/index.md) provides comprehensive information about the Model Context Protocol implementation in OpenMAS, including:

- Core MCP concepts (Resources, Prompts, Tools, Sampling, Roots, Transports)
- MCP implementation patterns
- Integration with OpenMAS components
- Examples of server and client usage

### Testing

The [Testing directory](testing/index.md) documents the testing approach for OpenMAS, covering:

- Unit testing strategies
- Mock vs. real integration testing
- Test fixture patterns
- Async testing techniques
- Dependency injection for testability

### Design Patterns

The [Design Patterns directory](design_patterns/index.md) catalogs the core patterns used throughout OpenMAS:

- Dependency Injection
- Factory Pattern
- Builder Pattern
- Strategy Pattern
- Repository Pattern
- Component-Based Architecture
- Event-Driven Architecture
- Plugin Architecture

### Libraries

The [Libraries directory](libraries/index.md) provides guidance on using the key dependencies in OpenMAS:

- Core dependencies (Pydantic, asyncio, PyYAML, Click, structlog)
- Communication libraries (aiohttp, MCP, paho-mqtt)
- Testing libraries (pytest, pytest-asyncio, pytest-mock)
- Implementation guidelines
- Import patterns

## How to Use This Knowledge Base

AI assistants working on OpenMAS refactoring should:

1. **Review Relevant Sections** - Before implementing a component, review the relevant knowledge base sections to understand patterns and practices.

2. **Follow Established Patterns** - Ensure implementations follow the patterns documented in the design patterns section.

3. **Use Recommended Libraries** - Leverage the libraries documented in the libraries section, following the established patterns.

4. **Apply Testing Strategies** - Use the testing strategies documented in the testing section to create comprehensive tests.

5. **Reference in Prompts** - Reference specific knowledge base documents in prompts to ensure AI assistants have access to relevant information.

## Knowledge Integration

When implementing components, ensure integration of knowledge across these areas:

1. **MCP + Design Patterns** - Implement MCP functionality using the documented design patterns
2. **Libraries + Testing** - Use testing libraries with appropriate patterns for effective tests
3. **Design Patterns + Testing** - Apply patterns that enhance testability

This knowledge base serves as a reference point to ensure consistency across the refactoring work. It should be consulted regularly and updated as new patterns or best practices emerge during the refactoring process.
