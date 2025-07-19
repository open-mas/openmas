# OpenMAS 0.3.0

A reasoning-agnostic multi-agent framework that supports multiple communication protocols.

## 🎯 Key Features

- **Reasoning Agnosticism**: Clean separation between communication infrastructure ("body") and reasoning approaches ("brain")
- **Multi-Protocol Support**: Native support for A2A, MCP, HTTP, MQTT, and gRPC protocols
- **Flexible Agent Architecture**: Support for various agent types and topologies
- **Configuration-Driven Design**: Unified configuration schema for all components
- **Enterprise Ready**: Built-in security, observability, and deployment support

## 🏗️ Architecture Principles

1. **Protocol Independence**: Agents communicate across different protocols without changing core logic
2. **Reasoning Flexibility**: Support for rule-based, BDI, LLM-based, and hybrid reasoning approaches
3. **Modularity**: Well-defined interfaces between components with minimal dependencies
4. **Configuration-First**: All behavior driven by structured configuration

## 🚀 Quick Start

### Installation

```bash
pip install openmas
```

### Basic Agent Configuration

```yaml
# config.yaml
agents:
  my_agent:
    reasoning:
      type: "llm"
      model: "gpt-4"
    protocols:
      - type: "mcp-sse"
        enabled: true
      - type: "a2a-http"
        enabled: true
        options:
          port: 8080
```

### Running an Agent

```python
from openmas import Agent

# Load configuration and start agent
agent = Agent.from_config("config.yaml")
await agent.start()
```

## 📋 Development Status

This is OpenMAS 0.3.0 - a complete rewrite focused on:
- Clean architecture with reasoning agnosticism
- Comprehensive multi-protocol support
- Enterprise-grade observability and security

> **Note**: This version has no backward compatibility with 0.2.0 as it represents a fundamental architectural redesign.

## 📚 Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Configuration Reference](docs/configuration/schema.md)
- [Protocol Support](docs/protocols/overview.md)
- [Agent Framework](docs/agents/overview.md)

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/openmas/openmas.git
cd openmas

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=openmas

# Run specific test types
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Type checking
mypy src

# Linting
flake8 src tests
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Support

- [Documentation](https://openmas.github.io/openmas)
- [Issues](https://github.com/openmas/openmas/issues)
- [Discussions](https://github.com/openmas/openmas/discussions) 