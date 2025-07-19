# Developer Workflows with OpenMAS CLI

This document outlines common development workflows when building applications with the OpenMAS framework and how to leverage the CLI tools to enhance productivity.

## Core Development Principles

OpenMAS development follows key architectural principles that are supported by the CLI:

1. **Reasoning Agnosticism**: Clear separation between communication (body) and reasoning (brain)
2. **Multi-Protocol Support**: Ability to work with different communication protocols (A2A, MCP, HTTP, MQTT, gRPC)
3. **Configuration-Driven**: Development driven by a single, unified configuration schema
4. **Component Boundaries**: Clear boundaries between components, with well-defined interfaces

## Common Development Workflows

### 1. Initializing a New Project

```bash
# Create a new OpenMAS project
openmas init my-project

# Create with specific protocol and reasoning approach
openmas init my-project --protocol a2a --reasoning llm
```

This creates:
- Project directory structure
- Initial configuration files
- Example agent templates
- Development environment setup

### 2. Agent Development Workflow

```bash
# Create a new agent
openmas agent create my-agent --template basic-agent

# Configure the agent capabilities
openmas config set agents.my-agent.capabilities.core "[text-generation, function-calling]"

# Map capabilities to specific protocol implementations
openmas config set agents.my-agent.capabilities.protocol_mapping.a2a.text-generation "openai-completion"
openmas config set agents.my-agent.capabilities.protocol_mapping.mcp.text-generation "mcp-completion"
```

### 3. Protocol Testing Workflow

```bash
# Run the agent using the A2A protocol
openmas run agent my-agent --protocol a2a

# Switch to MCP protocol for testing
openmas run agent my-agent --protocol mcp

# Test agent against a specific protocol adapter
openmas test agent my-agent --protocol a2a
```

### 4. Multi-Agent Development

```bash
# Start a local development cluster
openmas deploy start local-cluster

# Add agents to the cluster
openmas deploy add my-agent --to local-cluster
openmas deploy add other-agent --to local-cluster

# Test communication between agents
openmas deploy test local-cluster
```

### 5. Reasoning Engine Development

```bash
# Create a new reasoning engine implementation
openmas create reasoning-engine rule-based-engine

# Register with the framework
openmas register reasoning-engine rule-based-engine

# Test against different protocol interfaces
openmas test reasoning-engine rule-based-engine --protocol a2a
```

### 6. Development-to-Deployment Workflow

```bash
# Validate configuration
openmas validate config

# Prepare deployment package
openmas deploy package my-deployment

# Deploy to local environment
openmas deploy deploy my-deployment --env local

# Deploy to staging environment
openmas deploy deploy my-deployment --env staging
```

## Protocol-Specific Development

Each protocol requires specific development considerations:

### A2A Protocol Development

```bash
# Create A2A-compliant agent
openmas agent create my-a2a-agent --protocol a2a

# Configure A2A-specific capabilities
openmas config set agents.my-a2a-agent.capabilities.protocol_mapping.a2a.function-calling "a2a-function-calling"

# Generate A2A agent card
openmas protocol a2a generate-card agents.my-a2a-agent
```

### MCP Protocol Development

```bash
# Create MCP-compliant agent
openmas agent create my-mcp-agent --protocol mcp

# Configure MCP-specific capabilities
openmas config set agents.my-mcp-agent.capabilities.protocol_mapping.mcp.function-calling "mcp-function-calling"

# Test MCP server integration
openmas protocol mcp test-server agents.my-mcp-agent
```

## Reasoning-Specific Development

The CLI supports different reasoning approaches while maintaining protocol agnosticism:

### LLM-Based Development

```bash
# Create LLM-based agent
openmas agent create my-llm-agent --reasoning llm

# Configure LLM settings
openmas config set agents.my-llm-agent.reasoning.llm.model "gpt-4"
```

### Rule-Based Development

```bash
# Create rule-based agent
openmas agent create my-rule-agent --reasoning rule-based

# Register rule files
openmas config set agents.my-rule-agent.reasoning.rule-based.rules_dir "./rules"
```

### BDI Development

```bash
# Create BDI agent
openmas agent create my-bdi-agent --reasoning bdi

# Configure BDI components
openmas config set agents.my-bdi-agent.reasoning.bdi.beliefs_dir "./beliefs"
openmas config set agents.my-bdi-agent.reasoning.bdi.plans_dir "./plans"
```

## Developer Environment Setup

```bash
# Set up development environment
openmas setup dev-environment

# Install development dependencies
openmas deps install dev

# Configure local environment variables
openmas config env set OPENAI_API_KEY="your-key-here"
```

## Continuous Integration Workflow

```bash
# Run all tests
openmas test all

# Run linting and code quality checks
openmas lint

# Generate documentation
openmas docs generate
```

## Cross-Protocol Development

One of OpenMAS's strengths is the ability to write once and run on multiple protocols:

```bash
# Create a protocol-agnostic agent
openmas agent create multi-protocol-agent

# Set up capabilities that map to multiple protocols
openmas config set agents.multi-protocol-agent.capabilities.core "[text-generation, function-calling]"
openmas config set agents.multi-protocol-agent.capabilities.protocol_mapping.a2a.text-generation "a2a-completion"
openmas config set agents.multi-protocol-agent.capabilities.protocol_mapping.mcp.text-generation "mcp-completion"
openmas config set agents.multi-protocol-agent.capabilities.protocol_mapping.http.text-generation "http-completion"

# Test across all protocols
openmas test agent multi-protocol-agent --all-protocols
```

## Best Practices

1. **Use Configuration Templates**: Leverage `openmas init` templates for common patterns
2. **Maintain Protocol Agnosticism**: Separate communication logic from reasoning logic
3. **Test Across Protocols**: Test agents against all protocols they support
4. **Use the Validation Command**: Regularly validate configurations against the schema
5. **Leverage Environment Variables**: Use environment variables for sensitive configuration
6. **Container-Based Development**: Use `openmas deploy start local-cluster` for container-based testing

## See Also

- [Command Reference](../commands/README.md)
- [Configuration Options](../configuration/cli_config.md)
- [Deployment Workflows](../../15_deployment/README.md)
