# Extension Types

## Overview

OpenMAS supports several extension types that enable customization and extension of the framework's core functionality. Each extension type serves a specific purpose within the framework's architecture while maintaining OpenMAS's distinctive reasoning agnosticism.

This document serves as a master index for all supported extension types, providing links to detailed documentation for each type.

## Core Extension Types

### 1. [Agent Extensions](./agent_extensions.md)

Agent extensions enhance agent capabilities and behaviors beyond the core functionality:

- Custom agent behaviors
- Additional agent capabilities
- Protocol-specific agent features
- Agent lifecycle management

[Learn more about Agent Extensions](./agent_extensions.md)

### 2. [Communicator Extensions](./communicator_extensions.md)

Communicator extensions add support for new communication protocols and transports:

- New protocol implementations
- Transport layer enhancements
- Connection management
- Message formatting

[Learn more about Communicator Extensions](./communicator_extensions.md)

### 3. [Asset Extensions](./assets.md)

Asset extensions handle the management, transformation, and protocol-specific adaptation of various assets and resources:

- Protocol-independent asset access
- Custom asset type support
- Storage provider integration
- Asset transformation
- Protocol-specific adaptations

[Learn more about Asset Extensions](./assets.md)

### 4. [Prompt Extensions](./prompts.md)

Prompt extensions provide mechanisms for managing and customizing prompts across all protocols:

- Template management
- Context optimization
- Protocol-specific adaptation
- Reasoning independence
- Schema validation

[Learn more about Prompt Extensions](./prompts.md)

### 5. [LLM Extensions](./llm_extensions.md)

LLM extensions integrate with language models and AI providers:

- LLM provider integration
- Model management
- Inference optimization
- Response handling

[Learn more about LLM Extensions](./llm_extensions.md)

### 6. [Reasoning Extensions](./reasoning_extensions.md)

Reasoning extensions implement custom reasoning approaches:

- Custom reasoning engines
- Reasoning strategy implementation
- Decision-making logic
- Knowledge integration

[Learn more about Reasoning Extensions](./reasoning_extensions.md)

### 7. [Protocol Adapter Extensions](./protocol_adapters.md)

Protocol adapter extensions enable seamless communication between different protocols:

- Protocol translation
- Schema mapping
- Capability representation
- Message format conversion
- Protocol chain and discovery

[Learn more about Protocol Adapter Extensions](./protocol_adapters.md)

### 8. [Tool Extensions](./tool_extensions.md)

Tool extensions add new tool capabilities to agents:

- Custom tool implementation
- Tool execution management
- Tool result handling
- Multi-protocol tool support

[Learn more about Tool Extensions](./tool_extensions.md)

## Extension System Architecture

All extension types share a common architecture and implementation pattern:

1. **Base Classes** - Each extension type extends a specific base class with a defined interface
2. **Registration** - Extensions register with the extension registry at runtime
3. **Configuration** - Extensions are configured through the unified configuration schema
4. **Discovery** - Extensions are automatically discovered through a layered process

## Extension Development Guide

For comprehensive guidance on developing extensions, including:
- Setting up the development environment
- Implementing extension interfaces
- Testing extensions
- Publishing extensions

Please refer to the [Extension Development Guide](../development/guide.md) and the [Custom Extension Tutorial](../development/tutorial_custom_extension.md).
