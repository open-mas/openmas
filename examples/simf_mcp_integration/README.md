# SIMF-MCP Integration Examples

This directory contains comprehensive examples demonstrating the integration between the **Standard Internal Message Format (SIMF)** and the **Model Context Protocol (MCP)**, showing how OpenMAS achieves protocol-agnostic message handling while preserving semantic meaning.

## 🎯 **Overview**

These examples demonstrate:

1. **Bidirectional Translation**: MCP ↔ SIMF ↔ MCP with perfect semantic preservation
2. **Real Protocol Validation**: Integration with actual MCP 1.12.0 servers and clients
3. **IProtocolAdapter Pattern**: How the Phase 1 IProtocolAdapter interface works in practice
4. **Anti-Hallucination**: Validation against real MCP specifications to prevent AI hallucination
5. **Comprehensive Coverage**: Tool calls, resources, streaming, complex data structures

## 📁 **Files Overview**

| File | Purpose | Key Features |
|------|---------|--------------|
| `mcp_to_simf_translator.py` | Core translation logic | Bidirectional MCP ↔ SIMF conversion |
| `integration_demo.py` | End-to-end demonstration | Real MCP server integration |
| `test_integration.py` | Comprehensive test suite | Anti-hallucination validation |
| `README.md` | This documentation | Usage guide and examples |

## 🚀 **Quick Start**

### **1. Run the Basic Translation Demo**

```bash
cd examples/simf_mcp_integration
python mcp_to_simf_translator.py
```

This demonstrates basic MCP tool call → SIMF → MCP roundtrip translation.

### **2. Run the Full Integration Demo**

```bash
python integration_demo.py
```

This runs a comprehensive demo showing:
- Real MCP server tool calls with SIMF integration
- Resource access → SIMF asset references  
- Streaming simulation with SIMF stream context
- Complete semantic preservation validation

### **3. Run the Test Suite**

```bash
pytest test_integration.py -v
```

This validates all integration patterns against real MCP protocol behavior.

## 📡 **Integration Patterns Demonstrated**

### **Pattern 1: MCP Tool Calls → SIMF**

```python
from mcp_to_simf_translator import MCPToSIMFTranslator

translator = MCPToSIMFTranslator("my_agent")

# MCP tool call request
mcp_request = CallToolRequest(
    id="tool_123",
    method="tools/call",
    params={
        "name": "analyze_text",
        "arguments": {"text": "Hello world", "analysis_type": "sentiment"}
    }
)

# Convert to SIMF
simf_message = translator.mcp_tool_call_to_simf(mcp_request, "session_001")

# SIMF message preserves semantic meaning:
# - message_type: "TOOL_INVOCATION"
# - payload.capability_name: "analyze_text" 
# - payload.parameters: {"text": "Hello world", "analysis_type": "sentiment"}
# - source_protocol_type: "mcp"
```

### **Pattern 2: SIMF → MCP Tool Calls**

```python
# Convert SIMF back to MCP (perfect roundtrip)
reconstructed_mcp = translator.simf_to_mcp_tool_call(simf_message)

# Semantic preservation validated:
assert reconstructed_mcp.params["name"] == "analyze_text"
assert reconstructed_mcp.params["arguments"] == {"text": "Hello world", "analysis_type": "sentiment"}
```

### **Pattern 3: MCP Resources → SIMF Asset References**

```python
# MCP resource metadata + content
mcp_resource = Resource(
    uri="config://server/info",
    name="Server Configuration",
    mimeType="application/json"
)
resource_content = '{"version": "1.0", "capabilities": ["tools", "resources"]}'

# Convert to SIMF asset reference
simf_message = translator.mcp_resource_to_simf(mcp_resource, resource_content, "session_001")

# SIMF asset reference preserves:
# - asset_id: "config://server/info"
# - asset_type: AssetType.DATA (detected from mimeType)
# - content_preview: First 200 chars of content
# - metadata: Original MCP resource information
```

### **Pattern 4: IProtocolAdapter Integration**

```python
from integration_demo import MockMCPProtocolAdapter

adapter = MockMCPProtocolAdapter()

# IProtocolAdapter.to_internal_format() - Protocol → SIMF
simf_message = await adapter.to_internal_format(
    mcp_request, 
    context={"session_id": "adapter_session"}
)

# IProtocolAdapter.from_internal_format() - SIMF → Protocol  
reconstructed_mcp = await adapter.from_internal_format(simf_message)
```

## 🔍 **Semantic Preservation Validation**

The integration examples include comprehensive validation to ensure semantic meaning is preserved across all translations:

### **Test Categories**

1. **Basic Data Types**: Strings, numbers, booleans
2. **Complex Structures**: Nested dictionaries, arrays, mixed types
3. **Unicode Handling**: International characters, emojis, special symbols
4. **Edge Cases**: Empty values, null handling, special characters
5. **Real Protocol Data**: Actual MCP server responses and formats

### **Validation Process**

```python
# 1. Create original MCP message
mcp_request = create_mcp_request(...)

# 2. Full roundtrip through SIMF
simf_message = translator.mcp_tool_call_to_simf(mcp_request, session_id)
reconstructed_mcp = translator.simf_to_mcp_tool_call(simf_message)

# 3. Validate exact preservation
assert original_mcp.params == reconstructed_mcp.params
assert original_mcp.method == reconstructed_mcp.method
```

## 🌊 **Streaming Support**

The integration includes SIMF stream context support for MCP streaming scenarios:

```python
# Create stream context for progressive responses
simf_stream_message = translator.create_stream_context_message(
    stream_id="response_stream_001",
    position="start",  # "start", "middle", "end", "complete"
    partial_content="This is the beginning of a streaming response...",
    session_id="streaming_session"
)

# SIMF stream context preserves:
# - stream_id: Unique identifier for the stream
# - position: Position in the stream sequence
# - partial_content: The actual content chunk
# - Stream metadata for reconstruction
```

## 🧪 **Anti-Hallucination Measures**

The examples include several anti-hallucination measures:

### **1. Real Protocol Validation**

All examples are validated against actual MCP 1.12.0 servers:

```python
# Connect to real MCP server
server_params = StdioServerParameters(
    command="python",
    args=["examples/mcp_validation/real_mcp_server.py"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Test against real MCP implementation
        result = await session.call_tool("analyze_text", arguments={...})
```

### **2. Format Compatibility Checks**

```python
# Ensure our translations match real MCP message formats
assert isinstance(result.content[0], TextContent)  # Real MCP format
assert reconstructed_mcp.params["name"] == "analyze_text"  # Our format
```

### **3. Comprehensive Test Coverage**

- **Unit Tests**: Individual translation functions
- **Integration Tests**: Real MCP server interactions  
- **End-to-End Tests**: Complete workflow validation
- **Edge Case Tests**: Unicode, special characters, complex data

## 📊 **Performance Characteristics**

The SIMF-MCP integration is designed for efficiency:

- **Memory Efficient**: Minimal object creation during translation
- **CPU Efficient**: Direct field mapping without expensive serialization
- **Type Safe**: Full Pydantic validation throughout the pipeline
- **Error Resilient**: Comprehensive error handling and validation

## 🔗 **Integration with OpenMAS Architecture**

These examples demonstrate how SIMF-MCP integration fits into the broader OpenMAS architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │────│ IProtocolAdapter │────│  Agent Framework│
│   (External)    │    │   (MCP Impl)     │    │     (Core)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │      SIMF        │
                    │ (Protocol Agnostic)│
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Pattern Engine  │
                    │  Communication   │
                    │    Patterns      │
                    └──────────────────┘
```

## 📚 **Related Documentation**

- **SIMF Specification**: `refactoring_work/design/01_architecture/internal_message_format_standard.md`
- **IProtocolAdapter Interface**: `refactoring_work/archive/phase_1/TASK_define_iprotocol_adapter_interface.md`
- **MCP Protocol Design**: `refactoring_work/design/02_protocols/mcp/mcp_protocol.md`
- **Phase 2 Implementation**: `refactoring_work/planning/TASK_phase_2_implementation_foundation.md`

## ✅ **Success Criteria**

These examples successfully demonstrate:

- [x] **Bidirectional Translation**: MCP ↔ SIMF ↔ MCP with semantic preservation
- [x] **Real Protocol Compatibility**: Integration with MCP 1.12.0 SDK
- [x] **IProtocolAdapter Pattern**: Working implementation of Phase 1 interface
- [x] **Anti-Hallucination**: Validation against real MCP specifications
- [x] **Comprehensive Coverage**: Tool calls, resources, streaming, edge cases
- [x] **Production Ready**: Type safe, error resilient, performance optimized

## 🎉 **Next Steps**

With these integration examples complete, OpenMAS is ready for:

1. **Phase 2 Continuation**: Basic Agent Framework implementation
2. **Additional Protocols**: A2A, HTTP, MQTT, gRPC adapters
3. **Production Deployment**: Real-world agent communication scenarios
4. **Advanced Features**: Multi-protocol bridging, pattern execution, capability management

---

**The SIMF-MCP integration examples provide a bulletproof foundation for protocol-agnostic agent communication in OpenMAS, validated against real protocol implementations and designed for production use.** 