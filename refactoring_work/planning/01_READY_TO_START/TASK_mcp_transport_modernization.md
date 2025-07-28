# TASK: MCP Transport Modernization

**Task ID**: TASK_mcp_transport_modernization
**Priority**: HIGH
**Status**: NOT_STARTED
**Assigned**: Next AI Agent
**Created**: 2024-12-28
**Dependencies**: Foundation Test Coverage Complete (80%+ achieved)

## 🎯 **Objective**

Modernize MCP transport support to align with MCP SDK 1.12.0 capabilities and remove deprecated transport options to ensure production-ready multi-protocol deployments.

## 📊 **Current Transport Status**

### **✅ IMPLEMENTED & WORKING**
- **stdio Transport**: Complete implementation with real MCP 1.12.0 integration
- **Testing**: Comprehensive test coverage (86-89%)
- **Status**: Production-ready for local development

### **🚫 DEPRECATED & REMOVED**
- **SSE Transport**: Deprecated in MCP SDK 1.8+, fully removed from OpenMAS 0.3.0
- **References**: All SSE imports, configurations, and documentation cleaned up
- **Status**: Complete removal verified

### **🌐 MISSING & REQUIRED**
- **Streamable HTTP Transport**: Modern web-based MCP support needed
- **SDK Support**: Available in MCP SDK 1.12.0 via `mcp.client.streamable_http`
- **Use Case**: Web deployments, cloud environments, HTTP-based agent communication
- **Priority**: HIGH for production deployments

## 🛠️ **Implementation Requirements**

### **1. Add Streamable HTTP Transport Support**

**Location**: `src/openmas/protocols/mcp/`

**Files to Create/Modify**:
- `src/openmas/protocols/mcp/http_transport.py` (new)
- `src/openmas/protocols/mcp/config.py` (extend)
- `src/openmas/protocols/mcp/adapter.py` (extend)

**Key Changes**:
```python
# In config.py - Add HTTP transport config
class MCPHTTPConfig(BaseModel):
    """HTTP transport configuration for MCP."""
    url: str = Field(..., description="HTTP endpoint URL")
    headers: Dict[str, str] = Field(default_factory=dict)
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries")

# In adapter.py - Add HTTP connection method
async def _connect_http_client(self, config: MCPHTTPConfig) -> None:
    """Connect to MCP server via streamable HTTP."""
    from mcp.client.streamable_http import streamable_http_client
    # Implementation details...
```

### **2. Update Configuration Schema**

**File**: `src/openmas/protocols/mcp/config.py`

**Changes Required**:
- Add `MCPHTTPConfig` class
- Update `MCPTransport` enum to include `HTTP = "http"`
- Extend `MCPConfig` to support HTTP transport
- Add validation for HTTP-specific settings

### **3. Extend Protocol Adapter**

**File**: `src/openmas/protocols/mcp/adapter.py`

**Changes Required**:
- Add `_connect_http_client()` method
- Update `connect()` method to handle HTTP transport
- Add HTTP-specific error handling
- Ensure proper cleanup for HTTP connections

### **4. Add Comprehensive Tests**

**Location**: `tests/unit/protocols/`

**Test Files**:
- `test_mcp_http_transport.py` (new)
- Update existing `test_mcp_adapter.py` for HTTP support

**Test Coverage**:
- HTTP connection lifecycle
- Error handling and retries
- Configuration validation
- Message transmission over HTTP
- Concurrent HTTP requests

## 📋 **Verification Criteria**

### **✅ Success Criteria**
- [ ] HTTP transport connects successfully to real MCP servers
- [ ] All existing stdio tests continue to pass
- [ ] HTTP transport achieves 70%+ test coverage
- [ ] Configuration validation works for both stdio and HTTP
- [ ] Error handling is robust for network failures
- [ ] Documentation updated with HTTP transport examples

### **🔍 Verification Steps**
1. **Unit Tests**: All new HTTP transport tests pass
2. **Integration Tests**: HTTP transport works with real MCP servers
3. **Configuration Tests**: Both stdio and HTTP configs validate correctly
4. **Error Tests**: Network failures handled gracefully
5. **Performance Tests**: HTTP transport performs adequately

## 🚨 **Critical Notes**

### **DO NOT Re-add SSE Support**
- SSE transport is deprecated in MCP SDK 1.8+
- Do not implement or reference SSE in any new code
- Focus only on modern stdio and HTTP transports

### **Maintain Backward Compatibility**
- Existing stdio transport must continue working unchanged
- Default transport remains stdio for local development
- HTTP transport is additive, not replacement

### **Follow Existing Patterns**
- Use same error handling patterns as stdio transport
- Follow existing configuration validation approach
- Maintain consistent logging and debugging support

## 📚 **Reference Documentation**

### **MCP SDK 1.12.0 HTTP Transport**
- **Import**: `from mcp.client.streamable_http import streamable_http_client`
- **Usage**: Similar to stdio client but with HTTP endpoint
- **Documentation**: MCP SDK official docs

### **Existing Implementation Patterns**
- **Reference**: `src/openmas/protocols/mcp/adapter.py` stdio implementation
- **Configuration**: `src/openmas/protocols/mcp/config.py` stdio config
- **Tests**: `tests/unit/protocols/test_mcp_adapter.py` stdio tests

## 🎯 **Next Steps for AI Agent**

1. **Read existing MCP implementation** in `src/openmas/protocols/mcp/`
2. **Study MCP SDK 1.12.0** streamable_http documentation
3. **Implement HTTP transport** following stdio patterns
4. **Add comprehensive tests** with real HTTP MCP servers
5. **Update documentation** with HTTP transport examples
6. **Verify all transports** work in integration tests

**Estimated Effort**: 4-6 hours for experienced AI agent
**Complexity**: Medium (extending existing patterns)
**Risk**: Low (additive change, no breaking changes)
