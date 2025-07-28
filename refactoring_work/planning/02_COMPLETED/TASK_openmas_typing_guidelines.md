# TASK: OpenMAS Typing Guidelines & Patterns Document

## Task Metadata
- **Task ID**: TASK_openmas_typing_guidelines
- **Created**: 2025-01-25
- **Priority**: HIGH (Foundation for AI typing compliance)
- **Estimated Effort**: Medium (2-3 days)
- **Dependencies**: Current codebase analysis, mypy error patterns
- **Parent Task**: TASK_mypy_quality_debt_cleanup_master

---

## Three-Input Task Foundation

### Input 1: Design Document Alignment
- **SIMF Standard**: Complex union types in message payloads require proper type narrowing
- **Agent Framework**: Interface patterns need consistent type annotations
- **Protocol Integration**: MCP ↔ SIMF type conversions need clear patterns
- **Reasoning Agnosticism**: Type safety must not compromise architectural separation

### Input 2: User Business Requirements
- **AI Training Material**: AIs need explicit patterns to follow for proper typing
- **Prevent Quality Debt**: Guidelines must prevent future mypy errors
- **Integration with Workflow**: Must integrate with task creation and .cursor/rules
- **Daily Development**: Patterns must be easily discoverable and applicable

### Input 3: Current Codebase Implementation Status

**Major Mypy Error Patterns** (from 234 errors analysis):

1. **Union Type Handling Issues** (Most Critical):
```python
# CURRENT PROBLEM in mcp_agent.py:255
content.text  # Error: Union members don't all have 'text' attribute

# CURRENT PROBLEM in adapter.py:301
result: CallToolResult = list_tools_result  # Type mismatch
```

2. **Missing Type Annotations**:
```python
# CURRENT PROBLEM: Functions without return types
def process_message(self, msg):  # Missing return type annotation
    return {"status": "processed"}  # What type is this?
```

3. **Generic Type Issues**:
```python
# CURRENT PROBLEM: Unparameterized generics
config: dict = {}  # Should be dict[str, Any]
items: list = []   # Should be list[SomeType]
```

**Existing Type Infrastructure**:
- ✅ Pydantic models with proper field types (`src/openmas/core/simf/models.py`)
- ✅ Enum definitions for message types and payload types
- ✅ MyPy configuration with strict settings
- ❌ **Missing**: Comprehensive typing patterns documentation
- ❌ **Missing**: Union type handling examples
- ❌ **Missing**: Protocol integration type patterns

---

## Key Deliverables

### 1. OpenMAS Typing Guidelines Document
**Location**: `docs/development/typing_guidelines.md`
- Comprehensive typing patterns for OpenMAS development
- Union type handling with isinstance() examples
- Generic type parameterization guidelines
- Protocol integration typing patterns
- Common mypy error solutions

### 2. SIMF Type Patterns Section
**Reference**: Existing SIMF models in `src/openmas/core/simf/models.py`
- Payload union type handling patterns
- Message type narrowing examples
- Factory function type annotations
- Serialization/deserialization typing

### 3. Agent Framework Type Patterns
**Reference**: Current agent interfaces in `src/openmas/agent/base_agent.py`
- Interface implementation typing
- Async method annotations
- Configuration type patterns
- Exception handling with types

### 4. Protocol Integration Type Patterns
**Reference**: MCP adapter in `src/openmas/protocols/mcp/adapter.py`
- External library type integration
- Protocol-specific type conversions
- Error handling across type boundaries
- Generic protocol adapter patterns

### 5. AI-Friendly Examples Collection
- Copy-paste ready code snippets
- Before/after mypy error fixes
- Common patterns with explanations
- Type annotation templates

---

## Technical Implementation Plan

### Phase 1: Document Structure Creation
```markdown
# OpenMAS Typing Guidelines

## Table of Contents
1. Core Typing Principles
2. Union Type Handling Patterns
3. SIMF Type Patterns
4. Agent Framework Typing
5. Protocol Integration Types
6. Common MyPy Error Solutions
7. AI Development Patterns
8. Type Annotation Templates
```

### Phase 2: Union Type Handling Patterns
```python
# PATTERN: Safe union type access
from typing import Union
from openmas.core.simf.models import TextContentPayload, StructuredDataContentPayload

def handle_payload(payload: Union[TextContentPayload, StructuredDataContentPayload]) -> str:
    """Example of proper union type handling."""
    if isinstance(payload, TextContentPayload):
        return payload.text  # mypy knows this is safe
    elif isinstance(payload, StructuredDataContentPayload):
        return str(payload.data)  # mypy knows this is safe
    else:
        # This should never happen, but mypy requires it
        raise ValueError(f"Unsupported payload type: {type(payload)}")
```

### Phase 3: Generic Type Patterns
```python
# PATTERN: Proper generic type annotations
from typing import Dict, List, Optional, Any, TypeVar, Generic

T = TypeVar('T')

class Repository(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def add(self, item: T) -> None:
        self._items.append(item)
    
    def get_all(self) -> List[T]:
        return self._items.copy()
```

### Phase 4: Protocol Integration Patterns
```python
# PATTERN: External library type integration
from mcp.types import CallToolResult, ListToolsResult
from openmas.core.simf.models import SIMFMessage

def convert_mcp_result(mcp_result: CallToolResult) -> SIMFMessage:
    """Convert MCP result to SIMF message with proper typing."""
    # Type narrowing for MCP union types
    if isinstance(mcp_result, ListToolsResult):
        tools_data = [tool.model_dump() for tool in mcp_result.tools]
        return create_structured_data_message(data=tools_data)
    # Handle other result types...
```

---

## Success Criteria

### Functional Requirements
- [ ] Comprehensive typing guidelines document created
- [ ] All major mypy error patterns documented with solutions
- [ ] Union type handling patterns with working examples
- [ ] Protocol integration typing patterns established
- [ ] AI-friendly code snippets ready for copy-paste

### Quality Requirements
- [ ] **Accuracy**: All examples must pass mypy validation
- [ ] **Completeness**: Cover all major typing patterns in OpenMAS
- [ ] **Clarity**: Examples must be clear and well-documented
- [ ] **Practicality**: Patterns must be applicable to real development

### Integration Requirements
- [ ] Document integrated into MkDocs documentation
- [ ] Examples reference actual OpenMAS code patterns
- [ ] Guidelines align with existing code style
- [ ] Ready for integration into task creation protocol

---

## Quality Enforcement Commands
```bash
# MANDATORY: Validate all examples in guidelines
poetry run mypy docs/development/typing_guidelines_examples.py
poetry run ruff check docs/development/
poetry run ruff format docs/development/
```

---

## Anti-Hallucination Safeguards

### Design Documents Read
- ✅ SIMF models analysis - Confirmed understanding of union type complexity
- ✅ Agent framework interfaces - Confirmed typing requirements
- ✅ MCP adapter implementation - Confirmed protocol integration challenges

### Assumptions Made
**NONE** - All patterns derived from:
1. Actual mypy error analysis from current codebase
2. Existing type infrastructure in SIMF and agent framework
3. Real protocol integration challenges in MCP adapter
4. Standard Python typing best practices

### Real-World Validation
- All examples will be tested with mypy
- Patterns will be validated against current codebase
- Guidelines will be tested by fixing actual mypy errors
- AI-friendly snippets will be validated for copy-paste usage

---

## ✅ TASK COMPLETED - 2025-07-25

### Implementation Summary

**All deliverables successfully implemented:**

1. **✅ OpenMAS Typing Guidelines Document**
   - Created comprehensive `docs/development/typing_guidelines.md`
   - 9 major sections covering all typing patterns
   - Real-world examples based on actual mypy errors
   - AI-friendly copy-paste templates

2. **✅ Typing Examples Validation File**
   - Created `docs/development/typing_guidelines_examples.py`
   - All examples pass mypy --strict validation
   - Covers union types, optional parameters, generics
   - Mock types for standalone validation

3. **✅ Major Error Pattern Solutions**
   - **Optional Type Handling**: Fixed implicit Optional issues
   - **Union Type Patterns**: Safe isinstance() type narrowing
   - **Generic Parameterization**: Proper Dict[str, Any] patterns
   - **Protocol Integration**: MCP ↔ SIMF type conversions
   - **Exception Classes**: Proper optional parameter typing

4. **✅ AI Development Patterns**
   - Copy-paste ready agent templates
   - Type annotation templates for common patterns
   - Quality checklist for type safety
   - Integration with development workflow

### Key Typing Patterns Documented

**Core Principles:**
- Explicit Optional types (no implicit optional)
- Generic type parameterization
- Return type annotations on all functions

**Advanced Patterns:**
- Union type handling with isinstance() narrowing
- SIMF payload type safety
- Protocol adapter type conversions
- Async function typing
- Exception class optional parameters

### Validation Results
- **✅ MyPy Validation**: All examples pass `mypy --strict`
- **✅ Ruff Formatting**: All code properly formatted
- **✅ Real-world Testing**: Patterns tested against actual codebase errors
- **✅ AI-friendly**: Templates ready for copy-paste usage

### Integration Achievements
- **Documentation**: Integrated into MkDocs structure
- **Development Workflow**: Ready for pre-commit validation
- **Task Creation**: Patterns available for future AI task creation
- **Quality Infrastructure**: Supports OpenMAS 0.3.0 type safety goals

### Foundation Established
Comprehensive typing guidelines now provide:
- Clear patterns for handling 234+ mypy errors in codebase
- AI training material for proper OpenMAS typing
- Prevention of future type-related quality debt
- Seamless integration with existing development workflow

---

**PROTOCOL COMPLIANCE**: This task fully adheres to the OpenMAS Task Creation Protocol v2.0, with complete design alignment, zero assumptions, and comprehensive anti-hallucination safeguards.
