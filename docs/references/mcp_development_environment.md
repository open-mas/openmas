# MCP Development Environment Reference

**Document Purpose**: Centralized reference for all MCP-related specifications, versions, and ecosystem details used in OpenMAS 0.3.0
**Last Updated**: 2024-12-28
**Maintained By**: OpenMAS Development Team

## 📋 Core MCP Specifications

### MCP Protocol Specification
- **Version**: 2025-06-18
- **Official Specification**: https://modelcontextprotocol.io/specification/2025-06-18
- **Documentation**: https://modelcontextprotocol.io/docs/
- **Architecture Overview**: https://modelcontextprotocol.io/docs/concepts/architecture

### Python SDK
- **Version**: 1.12.0
- **Release Date**: July 17, 2024
- **GitHub Release**: https://github.com/modelcontextprotocol/python-sdk/releases/tag/v1.12.0
- **Repository**: https://github.com/modelcontextprotocol/python-sdk
- **PyPI Package**: `mcp>=1.12.0`

#### Key v1.12.0 Features Relevant to OpenMAS:
- **Session Initialization**: Enhanced session management (critical for our fixes)
- **OAuth Registration**: Improved authentication handling
- **Memory Cleanup**: Better stateless request cleanup
- **HTTP Routing**: Updated streamable HTTP routing
- **Authentication**: RFC9728 WWW-Authenticate header support

## 🔧 OpenMAS Integration Details

### Installation Requirements
```bash
# Core MCP SDK with CLI tools
poetry add "mcp[cli]>=1.12.0"

# Additional dependencies for SSE transport
poetry add aiohttp httpx

# OpenMAS integration
poetry add "starlette>=0.46.1" "uvicorn>=0.34.0"
```

### Supported Transports
1. **stdio** - Process-based communication (primary)
2. **SSE** - Server-Sent Events over HTTP (secondary)

### OpenMAS-Specific Patterns
- **Session Initialization**: Explicit `session.initialize()` calls required
- **SIMF Integration**: MCP-to-SIMF message translation via protocol adapters
- **Agent Framework**: MCPAgent extends base Agent with MCP tool capabilities
- **Capability Registration**: `mcp_tool_{name}` naming convention

## 🏗️ Architecture Integration

### Protocol Adapter Pattern
```
Agent (SIMF) ↔ MCPProtocolAdapter ↔ MCP SDK ↔ External MCP Server/Client
```

### Key Components
- **MCPAgent**: `src/openmas/agent/mcp_agent.py`
- **MCPProtocolAdapter**: `src/openmas/protocols/mcp/adapter.py`
- **MCPToSIMFTranslator**: `src/openmas/agent/mcp_to_simf_translator.py`
- **Configuration**: `src/openmas/protocols/mcp/config.py`

## 📚 OpenMAS Documentation References

### Internal Guides
- **Quick Rules**: `.cursor/rules/openmas_mcp.md`
- **Best Practices**: `docs/guides/mcp_best_practices.md`
- **0.2.0 Legacy Guide**: `0.2.0/docs/guides/mcp_developer_guide.md`

### Configuration Files
- **MCP Validation Examples**: `examples/mcp_validation/`
- **Integration Tests**: `tests/integration/agent/test_mcp_agent.py`
- **Protocol Tests**: `tests/integration/mcp/`

## 🚨 Critical Known Issues & Fixes

### Session Initialization (RESOLVED)
- **Issue**: "Invalid request parameters" and "Received request before initialization"
- **Root Cause**: Missing explicit `session.initialize()` call
- **Solution**: Always call `await asyncio.wait_for(session.initialize(), timeout=10.0)`
- **GitHub Reference**: [Issue #423](https://github.com/modelcontextprotocol/python-sdk/issues/423)

### Result Extraction (RESOLVED)
- **Issue**: MCP 1.12.0 returns complex `CallToolResult` objects
- **Solution**: Extract `structuredContent` or fallback to `content[0].text`

## 🔗 External Resources

### Official MCP Ecosystem
- **Main Website**: https://modelcontextprotocol.io/
- **GitHub Organization**: https://github.com/modelcontextprotocol
- **Python SDK Issues**: https://github.com/modelcontextprotocol/python-sdk/issues
- **Specification Repo**: https://github.com/modelcontextprotocol/specification

### Development Tools
- **MCP Inspector**: `python -m mcp.tools.inspector`
- **Debugging**: Enable with `log_level="DEBUG"` in FastMCP
- **Testing**: Official test patterns in SDK repository

### Community Resources
- **Discord**: MCP Discord community (check official site for invite)
- **Examples**: https://github.com/modelcontextprotocol/examples
- **TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk

## 🔄 Version Compatibility Matrix

| OpenMAS Version | MCP Spec | Python SDK | Python Version | Key Features |
|----------------|----------|------------|----------------|--------------|
| 0.3.0 | 2025-06-18 | 1.12.0 | 3.10+ | SIMF integration, explicit session init |
| 0.2.0 | 2025-06-18 | 1.6-1.8 | 3.10+ | Direct integration, legacy patterns |

## 📝 Development Standards

### Code Quality
- **Type Hints**: Full type annotation required for MCP integration code
- **Error Handling**: Structured exception handling with `AgentError`
- **Logging**: DEBUG level logging for MCP operations
- **Testing**: Real MCP server integration tests (no mock-only tests)

### Performance Guidelines
- **Timeouts**: 10s session init, 30s tool calls, 15s server startup
- **Connection Pooling**: Not implemented (consider for high-traffic scenarios)
- **Resource Cleanup**: Proper async context manager usage

---

## 🚀 Future Considerations

### Potential Upgrades
- **MCP Spec Updates**: Monitor for new specification versions
- **SDK Updates**: Track Python SDK releases for bug fixes and features
- **Transport Additions**: WebSocket transport when available
- **Performance**: Connection pooling and caching strategies

### Ecosystem Evolution
- Watch for breaking changes in major SDK updates
- Monitor community best practices and patterns
- Consider TypeScript SDK compatibility for multi-language environments

---

**Document Maintenance**: Update this file when upgrading MCP SDK versions or when new OpenMAS MCP patterns are established.
