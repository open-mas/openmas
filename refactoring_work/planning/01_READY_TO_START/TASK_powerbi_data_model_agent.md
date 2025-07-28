# TASK: PowerBI Data Model Agent

## Task Metadata
- **Task ID**: TASK_powerbi_data_model_agent
- **Created**: 2025-01-25
- **Updated**: 2025-01-28 (Hub Architecture Alignment)
- **Priority**: High (Business-Critical Daily Use)
- **Estimated Effort**: Medium (3-5 days)
- **Dependencies**: **BLOCKED BY TASK_hub_extension_system_foundation**
- **Hub Integration**: This agent will be the **first community package** for hub.openmas.ai

---

## Three-Input Task Foundation

### Input 1: Design Document Alignment

**Primary Design Documents**:
- **Agent Framework**: `/refactoring_work/design/04_agents/agent_framework_overview.md`
- **Agent Capabilities**: `/refactoring_work/design/04_agents/agent_capabilities.md`
- **Configuration Schema**: `/refactoring_work/design/03_configuration/unified_configuration_schema.md`
- **Reasoning Agnostic Design**: `/refactoring_work/design/01_architecture/reasoning_agnostic_design.md`

### Input 2: User Business Requirements

**PowerBI Workflow Pain Point**: Manual M-query extraction from PBIP data models for ETL context sharing
**Daily Use Cases**: ETL context sharing, data model analysis, documentation generation, change impact analysis
**Target Integration**: PowerBI/SQL Server/analytics workflows with OpenMAS multi-agent system

### Input 3: Current Codebase Implementation Status

**Existing Agent Framework** (`src/openmas/agent/`):
- ✅ `Agent` base class with SIMF integration (`base_agent.py`)
- ✅ `AgentConfig`, `IAgentStateManager`, `IMessageHandler`, `IProtocolAdapter` interfaces
- ✅ Agent factory with configuration-driven creation (`factory.py`)
- ✅ MCP agent implementation (`mcp_agent.py`)
- ✅ Comprehensive exception handling (`exceptions.py`)

**Existing SIMF Implementation** (`src/openmas/core/simf/`):
- ✅ Complete SIMF models with all message types (`models.py`)
- ✅ Serialization/deserialization support (`serialization.py`)
- ✅ Message validation framework (`validation.py`)
- ✅ Factory functions: `create_text_message`, `create_invocation_result_message`, etc.

**Existing Protocol Support** (`src/openmas/protocols/`):
- ✅ MCP protocol adapter with full SIMF translation (`mcp/`)
- ✅ `MCPProtocolAdapter`, `MCPConfig`, `MCPTransportType` implementations
- ⚠️ A2A, HTTP, MQTT, gRPC protocols: Design documented but not yet implemented

**Configuration System** (`src/openmas/config/`):
- ✅ Basic configuration structure exists
- ⚠️ PowerBI-specific configuration patterns: Not yet implemented

**Quality Infrastructure**:
- ✅ Ruff configuration: line-length=120, ignore=E203, select=["E", "F", "I", "UP", "N", "B", "SIM"]
- ✅ MyPy configuration with strict typing requirements
- ✅ Pre-commit hooks and tox environments configured
- ✅ 302 passing tests (220 unit + 12 integration + 70 SIMF tests)

### Strategic Context

**Hub Architecture Alignment**: This task implements the PowerBI agent as the **first community package** for the hub.openmas.ai ecosystem, serving as a reference implementation for the extension system.

**Business Workflow**: Addresses critical PowerBI data model analysis by extracting and analyzing M-queries from PBIP format files. The agent will be packaged as a **hub-installable extension** that can be discovered, installed, and managed through the OpenMAS CLI.

**Architecture**: Follows the hub extension patterns with standardized packaging, protocol-agnostic design, and community publishing workflows. This agent demonstrates the full hub ecosystem from development to publication.

### Interface Dependencies (Existing Implementation)
- **Agent Base Class**: Extend existing `openmas.agent.base_agent.Agent` class
- **SIMF Models**: Use existing `openmas.core.simf.models` (SIMFMessage, MessageType, etc.)
- **SIMF Factory Functions**: Leverage existing `create_text_message`, `create_invocation_result_message`
- **Protocol Integration**: Use existing `MCPProtocolAdapter` for communication
- **Configuration**: Integrate with existing `AgentConfig` patterns
- **Exception Handling**: Use existing `openmas.agent.exceptions` hierarchy

---

## Business Context & Requirements

### User Workflow Pain Point
**Current Manual Process**: When working with PowerBI data models, the user must manually copy-paste M-queries from the data model to share ETL context with other agents or developers. This is time-consuming and error-prone.

**Target Automated Workflow**: Agent automatically extracts, parses, and contextualizes M-queries from PBIP format files, providing rich metadata about data sources, transformations, and relationships for use in analytics workflows.

### Daily Use Cases
1. **ETL Context Sharing**: Extract M-queries with metadata for SQL Server integration discussions
2. **Data Model Analysis**: Analyze data source dependencies and transformation logic
3. **Documentation Generation**: Auto-generate data lineage documentation from M-queries
4. **Change Impact Analysis**: Identify affected queries when data sources change

---

## Key Deliverables

### 1. PowerBI Data Model Agent Implementation
**Reference**: Existing `Agent` class in `src/openmas/agent/base_agent.py`
- Create `PowerBIDataModelAgent` class extending existing `Agent` base class
- Leverage existing SIMF integration and message handling infrastructure
- PBIP file format parsing capabilities (new functionality)
- M-query extraction and metadata analysis (new functionality)
- Use existing async patterns and error handling from base agent

### 2. M-Query Analysis Capabilities
**Reference**: Existing capability patterns in `src/openmas/agent/base_agent.py`
- `extract_mqueries`: Parse PBIP semantic model files and extract M-queries
- `analyze_data_sources`: Identify data source connections and dependencies  
- `generate_lineage`: Create data lineage documentation from query relationships
- `validate_syntax`: Basic M-query syntax validation and error reporting
- **Integration**: Use existing SIMF message types for capability invocation/results

### 3. Configuration Integration
**Reference**: Existing `AgentConfig` in `src/openmas/agent/base_agent.py`
- Extend existing `AgentConfig` with PowerBI-specific settings
- PBIP file path configuration and monitoring
- Output format preferences (JSON, markdown, etc.)
- **Leverage Existing**: Use current MCP protocol adapter (`src/openmas/protocols/mcp/`)

### 4. Business Workflow Integration
**Reference**: Existing demo in `examples/basic_two_agent_demo/demo.py`
- **Build Upon**: Existing multi-agent communication patterns (Document Processor + Sentiment Analyzer)
- **Extend**: Add PowerBI agent to existing multi-agent workflow
- **Leverage**: Existing SIMF message routing and capability discovery
- Context-aware responses for PowerBI/SQL Server workflows

---

## Design Compliance Requirements

### Interface Patterns
**Existing Patterns to Follow**:
- Agent base class patterns from current `src/openmas/agent/` implementation
- Capability registration via `ICapabilityManager` interface
- Pydantic model schemas for all data structures
- Async method signatures throughout

### Architectural Constraints
**Reasoning Agnosticism**: 
- Clear separation between M-query parsing logic ("brain") and communication handling ("body")
- Rule-based parsing approach - no LLM dependencies
- Pluggable reasoning approach for future enhancement

**Protocol Independence**:
- Core M-query analysis logic independent of transport protocol
- SIMF message format for all inter-agent communication
- Capability advertisement works across MCP, A2A, and other protocols

### SIMF Integration
- All agent communications use Standard Internal Message Format
- Capability invocations follow established SIMF patterns
- Error handling and status reporting via SIMF message types

---

## Technical Implementation Plan

### Phase 1: Agent Foundation (Day 1-2)
1. Create `PowerBIDataModelAgent` class extending existing `Agent` from `src/openmas/agent/base_agent.py`
2. Implement basic PBIP file parsing (focus on `.SemanticModel/` directory structure)
3. **Leverage Existing**: Use existing capability registration patterns from base agent
4. **Extend Existing**: Add PowerBI settings to existing `AgentConfig` structure

### Phase 2: M-Query Extraction (Day 2-3)
1. Implement M-query extraction from PBIP semantic model files
2. Parse table definitions and relationship metadata
3. Extract data source connection information
4. Basic syntax validation and error handling

### Phase 3: Analysis Capabilities (Day 3-4)
1. Data lineage analysis from M-query relationships
2. Data source dependency mapping
3. Transformation logic documentation generation
4. Integration with existing multi-agent communication patterns

### Phase 4: Business Integration (Day 4-5)
1. PowerBI-specific workflow optimizations
2. SQL Server integration context generation
3. Documentation output formatting (markdown, JSON)
4. **Integration Testing**: Test with existing multi-agent demo framework
5. End-to-end testing with real PBIP files

---

## Quality Assurance Requirements

### Code Quality Standards
- **Code Formatting & Linting**: All code will be formatted and linted with `ruff` (line-length=120, ignore=E203)
- **Import Sorting**: All imports will be sorted with `ruff` (known-first-party=["openmas"], combine-as-imports=true)
- **Type Checking**: 100% `mypy` compliance with proper type annotations
- **Linting**: Zero `ruff` violations (select=["E", "F", "I", "UP", "N", "B", "SIM"])
- **Documentation**: Google-style docstrings for all public methods

### Testing Requirements
- **Unit Tests**: Comprehensive test coverage for M-query parsing logic
- **Integration Tests**: End-to-end testing with sample PBIP files
- **Anti-Hallucination Tests**: Validation that agent only reports actual PBIP file contents
- **Protocol Tests**: Verify capability advertisement across MCP/A2A protocols

### Quality Enforcement Commands
```bash
# MANDATORY: Run these commands before task completion
poetry run ruff check src/openmas tests
poetry run ruff format src/openmas tests
poetry run mypy src/openmas
pre-commit run --all-files
tox -e lint,type,unit
```

---

## Success Criteria

### Functional Requirements
- [ ] Agent successfully extracts M-queries from PBIP semantic model files
- [ ] Data source dependencies correctly identified and mapped
- [ ] Generated documentation accurately reflects PowerBI data model structure
- [ ] Integration with existing OpenMAS multi-agent communication works seamlessly

### Quality Requirements
- [ ] All `ruff` checks pass (formatting, linting, import sorting)
- [ ] All `mypy` type checks pass
- [ ] All `pre-commit` hooks pass
- [ ] Relevant `tox` environments pass (lint, type, unit)
- [ ] Zero linting violations introduced
- [ ] Proper Google-style docstrings added
- [ ] Unit tests added for new functionality

### Business Value Validation
- [ ] Eliminates manual M-query copy-paste workflow
- [ ] Provides rich context for ETL development discussions
- [ ] Integrates seamlessly with existing PowerBI/SQL Server workflows
- [ ] Demonstrates OpenMAS value for daily analytics work

---

## Anti-Hallucination Safeguards

### Design Documents Read
- ✅ `/refactoring_work/design/04_agents/agent_framework_overview.md` - Confirmed understanding of agent base classes, capability system, and lifecycle management
- ✅ `/refactoring_work/design/04_agents/agent_capabilities.md` - Confirmed understanding of capability registration and Pydantic schema patterns
- ✅ `/refactoring_work/design/03_configuration/unified_configuration_schema.md` - Confirmed understanding of agent configuration patterns
- ✅ `/refactoring_work/design/01_architecture/reasoning_agnostic_design.md` - Confirmed understanding of body/brain separation

### Assumptions Made
**NONE** - All requirements derived from:
1. User's explicitly stated PowerBI workflow pain points
2. Existing OpenMAS agent framework design patterns
3. Microsoft's documented PBIP file format structure
4. Current OpenMAS multi-agent communication patterns

### Real-World Validation
- Implementation will be tested with actual PBIP files from user's PowerBI projects
- M-query extraction validated against known PowerBI semantic model structure
- Integration tested with existing OpenMAS demo agents
- Business workflow validated through daily use scenarios

---

## Cross-Reference Updates Required

Upon task completion, update these design documents:
1. **Agent Framework Overview**: Add PowerBI Data Model Agent to specialized agent types
2. **Agent Capabilities**: Document M-query analysis capability patterns for reuse
3. **Configuration Schema**: Add PowerBI-specific configuration examples
4. **Use Cases Documentation**: Add PowerBI analytics workflow as concrete use case

---

## Mandatory Review Questions - ANSWERED

1. **"What specific design document gap does this task address?"**
   - **Answer**: Addresses the gap between generic agent framework and specialized business workflow agents. No PowerBI-specific agent exists in current design, yet this represents a critical daily use case for the user.

2. **"Which existing interfaces will this component implement or use?"**
   - **Answer**: Will implement `ICapabilityManager` for capability registration, use base agent classes from agent framework, follow SIMF message patterns, and integrate with unified configuration schema.

3. **"How does this task maintain OpenMAS's reasoning agnosticism?"**
   - **Answer**: Uses rule-based M-query parsing (no LLM dependency) with clear separation between parsing logic ("brain") and communication handling ("body"). Parsing approach is pluggable for future enhancement.

4. **"What architectural constraints apply to this component?"**
   - **Answer**: Must use SIMF for all communications, maintain protocol independence, follow async-first design patterns, integrate with unified configuration schema, and respect capability system patterns.

5. **"Which design documents need updates when this task is complete?"**
   - **Answer**: Agent framework overview (add to specialized agents), agent capabilities (document patterns), configuration schema (add examples), and use cases documentation (add PowerBI workflow).

---

---

## Hub Integration Requirements

### Package Structure
```
openmas-powerbi-agent/
├── openmas_package.yaml    # Hub package manifest
├── src/powerbi_agent/      # Agent implementation
│   ├── __init__.py
│   ├── agent.py           # Main agent class
│   ├── capabilities/      # M-query analysis capabilities
│   └── config/           # Agent configuration
├── tests/                 # Package tests
├── README.md             # Hub documentation
└── examples/             # Usage examples
```

### Hub Commands
```bash
# After hub system implementation:
openmas hub validate ./openmas-powerbi-agent
openmas hub publish ./openmas-powerbi-agent
openmas hub install powerbi-agent
```

### Extension Integration
- **Extension Type**: `agent`
- **Protocols Supported**: `[mcp, a2a, http]`
- **Capabilities**: `[extract_mqueries, analyze_data_sources, generate_lineage]`
- **Dependencies**: `openmas>=0.3.0, pandas>=1.5.0`

---

**STRATEGIC IMPORTANCE**: This task serves as the foundational example for the hub ecosystem, demonstrating end-to-end package development, validation, and community publishing workflows.

**PROTOCOL COMPLIANCE**: This task fully adheres to the OpenMAS Task Creation Protocol v2.0, with complete design alignment, zero assumptions, and comprehensive anti-hallucination safeguards.
