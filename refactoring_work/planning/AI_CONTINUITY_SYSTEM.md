AI Continuity System - OpenMAS
Complete AI assistant guidelines for seamless continuity across sessions

**Version**: 2.0 (Enhanced)
**Last Updated**: 2024-12-28
**Purpose**: Zero context loss AI handovers with improved organization and anti-hallucination focus

## 🚨 **CRITICAL: Session Start Protocol**

**EVERY AI session MUST start by reading these 4 files in order:**

1. **This file** (`.cursor/rules/openmas_ai_continuity.md`) - Core rules & standards
2. **Current Phase** (`refactoring_work/planning/current_phase.md`) - Active objectives
3. **Task Tracker** (`refactoring_work/planning/task_tracker.md`) - Status & next actions
4. **Task Creation Protocol** (`refactoring_work/planning/TASK_CREATION_PROTOCOL.md`) - **MANDATORY** for creating new tasks

## 🎯 **Project Context & Architecture**

### **OpenMAS 0.3.0 Core Principles**
- **Reasoning Agnosticism**: Clean separation between communication ("body") and reasoning ("brain")
- **Multi-Protocol Support**: A2A, MCP, HTTP, MQTT, gRPC with SIMF translation layer
- **Configuration-Driven**: Single unified schema for all components
- **Complete Rewrite**: No backward compatibility with 0.2.0 (available for reference only)

### **Standard Internal Message Format (SIMF)**
- **All protocols** must translate to/from SIMF - NO direct protocol bridging
- **Semantic preservation** during translations is mandatory
- **Reference**: `refactoring_work/design/01_architecture/internal_message_format_standard.md`

### **Interface Design Standards**
- **Pydantic models** for all data structures with complete type safety
- **Async by default** for all I/O operations
- **Abstract Base Classes** with explicit type hints and detailed docstrings
- **Protocol agnostic** - no protocol-specific logic in shared interfaces

## 📁 **V2 Enhanced Planning Directory Structure**

### **New Organization** (V2 Enhancement):
```
refactoring_work/planning/
├── 00_ACTIVE_TASKS/
│   ├── T001_CRITICAL_current_priority.md
│   └── T002_HIGH_next_priority.md
├── 01_READY_TO_START/
│   └── T003_MEDIUM_ready_task.md
├── 02_BLOCKED/
│   └── T004_HIGH_blocked_task.md
├── core_documents/
│   ├── current_phase.md
│   ├── task_tracker.md
│   └── ai_handover_summary.md (V2 addition)
└── templates/
    └── TASK_template.md
```

### **Task Status Workflow** (V2 Enhancement):
```
NOT_STARTED → READY_TO_START → ACTIVE → COMPLETE → ARCHIVED
     ↓             ↓             ↓         ↓         ↓
  planning/    planning/01_  planning/00_  archive/  archive/
  02_BLOCKED/  READY/        ACTIVE/       phase_N/  phase_N/
```

## 📋 **File Lifecycle Management**

### **Planning Documents Lifecycle**

| Document | Purpose | Lifecycle | Location |
|----------|---------|-----------|----------|
| `current_phase.md` | Active phase objectives | **LIVING** - Updated throughout phase | `refactoring_work/planning/core_documents/` |
| `task_tracker.md` | All task status tracking | **LIVING** - Updated in real-time | `refactoring_work/planning/core_documents/` |
| `ai_handover_summary.md` | **V2**: Session handover doc | **LIVING** - Updated each session | `refactoring_work/planning/core_documents/` |
| `PHASE_N_MASTER_PLAN.md` | Phase-specific master plan | **IMMUTABLE** - Archive when phase complete | `refactoring_work/01_implementation_plan/` → `refactoring_work/archive/phase_N/` |

### **V2 Enhanced Task Files Lifecycle**

| Status | Location | Naming Convention | Actions Required |
|--------|----------|-------------------|------------------|
| **NOT_STARTED** | `planning/02_BLOCKED/` | `T{num}_{priority}_{name}.md` | Create file, add to tracker |
| **READY_TO_START** | `planning/01_READY_TO_START/` | `T{num}_{priority}_{name}.md` | Dependencies complete |
| **ACTIVE** | `planning/00_ACTIVE_TASKS/` | `T{num}_{priority}_{name}.md` | Update Progress Notes in real-time |
| **COMPLETE** | `archive/phase_N/` | `T{num}_{priority}_{name}.md` | Move file, update tracker, update current_phase.md |

### **V2 File Naming Convention**:
```
T{number}_{priority}_{short_name}.md

Examples:
- T001_CRITICAL_mcp_agent.md
- T002_HIGH_multi_agent_demo.md
- T003_MEDIUM_housekeeping.md
```

## 🛡️ **V2 TASK CREATION INTEGRATION**

### **Critical Anti-Hallucination Enhancement**

The V2 system now includes **mandatory task creation safeguards** to prevent the AI hallucination disasters that plagued OpenMAS 0.2.0 (over 1000 passing tests that tested nothing).

**TASK CREATION PROTOCOL INTEGRATION:**
- **File**: `refactoring_work/planning/TASK_CREATION_PROTOCOL.md`
- **Purpose**: Enforce strict design alignment when creating new tasks
- **Mandatory**: ALL AIs creating tasks MUST follow this protocol
- **Integration**: Seamlessly extends V2 session management

### **Task Creation vs. Task Execution**

| Activity | Protocol | Purpose |
|----------|----------|----------|
| **Creating New Tasks** | TASK_CREATION_PROTOCOL.md | Design alignment, anti-hallucination safeguards |
| **Executing Existing Tasks** | AI_CONTINUITY_SYSTEM.md | Session continuity, progress tracking |

### **Mandatory Task Creation Process**

**BEFORE** creating any new task, AI MUST:
1. **Read design documents** relevant to the task scope
2. **Verify architecture alignment** with OpenMAS constraints
3. **Follow mandatory task format** with explicit design references
4. **Complete anti-hallucination checklist** to prevent assumption-based requirements

**This integration ensures every new task is perfectly aligned with OpenMAS design.**

## 🔄 **AI Session Management Protocol**

### **Session Start Checklist (MANDATORY)**
- [ ] Read this AI continuity system file
- [ ] Read `refactoring_work/planning/core_documents/current_phase.md`
- [ ] Read `refactoring_work/planning/core_documents/task_tracker.md`
- [ ] Read `refactoring_work/planning/TASK_CREATION_PROTOCOL.md` (if creating new tasks)
- [ ] Identify highest priority task or next action
- [ ] Update task status to "ACTIVE" if starting new work
- [ ] **BEFORE creating ANY new task**: Follow TASK_CREATION_PROTOCOL.md mandatory process

### **During Work (REAL-TIME UPDATES)**
- **Update Progress Notes** in active TASK file after each sub-task completion
- **Document design decisions** with clear rationale in "Decision Notes" sections
- **Reference completed work** in `refactoring_work/design/completed/` for consistency
- **Cross-reference updates** when changes impact other components
- **Maintain SIMF compatibility** for all protocol-related work

### **V2 Enhanced Session End Checklist (MANDATORY)**
- [ ] Update task status in `refactoring_work/planning/core_documents/task_tracker.md`
- [ ] **V2**: Update `ai_handover_summary.md` with session results
- [ ] Document exact resume point for next AI in TASK Progress Notes
- [ ] Move completed TASK files to appropriate archive directory (`archive/phase_N/`)
- [ ] Update `current_phase.md` if phase objectives change
- [ ] Verify all cross-references are updated
- [ ] Follow V2 auto-archival rules (no files remain in planning root)

### **V2 Mandatory Handover Document Template**
**File**: `refactoring_work/planning/core_documents/ai_handover_summary.md`

```markdown
# AI Handover Summary

**Last Updated**: [Date]
**Session**: [AI Agent Name/ID]
**Context Remaining**: [Estimated tokens/percentage]

## 🎯 **IMMEDIATE NEXT PRIORITY**
**Task**: [Task name and number]
**File**: [Path to task file]
**Estimated Time**: [Hours]
**Blockers**: [None/List blockers]

## ✅ **COMPLETED THIS SESSION**
- [List completions]

## 🚧 **IN PROGRESS**
- [List work started but not finished]

## ⚠️ **CRITICAL ISSUES DISCOVERED**
- [List any critical issues for next AI to address]

## 📁 **KEY FILES MODIFIED**
- [List important file changes]

## 🔄 **RECOMMENDED NEXT ACTIONS**
1. [First action]
2. [Second action]
3. [Third action]
```

## 💻 **Code Standards & Anti-Hallucination Testing**

### **Python Requirements**
- **Python 3.10+** minimum version (avoid 3.13+ for MCP compatibility)
- **Type hints required** for all functions, parameters, and returns
- **Black formatting** with 88-character line limit
- **Pydantic validation** for all data models and configurations

### **V2 Anti-Hallucination Testing Standards**
**Critical Lesson**: 0.2.0 had 1000+ passing tests with 80% coverage but NONE worked with real libraries

**Real-First Testing Requirements**:
- **90% minimum** coverage for MCP adapter code with REAL tests (no mocking)
- **80% minimum** for core agent framework with REAL integration
- **100%** for critical protocol translation paths
- **0% tolerance** for hallucinated coverage (mocked tests don't count)

**Anti-Hallucination Test Patterns**:
```python
@pytest.mark.real
@pytest.mark.mcp
@pytest.mark.anti_hallucination
async def test_real_mcp_integration():
    """MUST use real MCP 1.12.0 server - no mocking allowed"""
    pass

@pytest.fixture
def anti_hallucination_validator():
    """Validates no critical paths are mocked"""
    def validate_no_mocking(module_names):
        import sys
        mocked = [m for m in sys.modules if 'mock' in str(type(sys.modules[m]))]
        for module in module_names:
            assert module not in mocked, f"CRITICAL: {module} is mocked!"
    return validate_no_mocking
```

### **Testing Standards**
- **Unit tests required** for all new functions/classes with at least 70% coverage
- **Integration tests required** for all protocol adapters using REAL libraries
- **Real library verification** - NEVER mock external APIs without testing real ones first
- **Test organization**: Mirror source structure in `/tests` directory
- **Test markers**: Use appropriate markers (unit, integration, mcp, grpc, mqtt, async, real, anti_hallucination)

## 🚫 **Critical Prohibitions**

### **Never Do These Things**
- **Never hallucinate** library APIs, functions, or file paths - verify everything exists
- **Never assume missing context** - ask questions or read referenced documentation
- **Never delete existing implementations** without explicit user instruction
- **Never break SIMF compatibility** when working on protocol components
- **Never mix reasoning logic** with communication components
- **Never create files longer than 500 lines** - refactor into modules instead
- **V2**: **Never mock critical external libraries** without real validation first

### **Always Do These Things**
- **Always reference existing patterns** from completed TASK files for consistency
- **Always update cross-references** when modifying interfaces
- **Always include rationale** for design decisions in documentation
- **Always test against real libraries** before implementing adapters
- **Always maintain protocol independence** in shared components
- **V2**: **Always validate with real MCP 1.12.0 servers** before claiming integration works

## 📁 **Essential Reference Documents**

### **Architecture References**
- **SIMF Spec**: `refactoring_work/design/01_architecture/internal_message_format_standard.md`
- **Multi-Protocol Design**: `refactoring_work/design/01_architecture/multi_protocol_design.md`
- **Configuration Schema**: `refactoring_work/design/03_configuration/unified_configuration_schema.md`

### **Completed APIs (Reference Patterns)**
- **Message Handling**: `refactoring_work/design/completed/TASK_define_agent_framework_message_handling_api.md`
- **State Management**: `refactoring_work/design/completed/TASK_detail_agent_framework_state_management_api.md`
- **Knowledge Base**: `refactoring_work/design/completed/TASK_specify_iknowledgebase_interface_and_data_structures.md`
- **IProtocolAdapter**: `refactoring_work/archive/phase_1/TASK_define_iprotocol_adapter_interface.md`

### **Active Work References**
- **Current Phase**: `refactoring_work/planning/core_documents/current_phase.md`
- **Task Tracker**: `refactoring_work/planning/core_documents/task_tracker.md`
- **V2**: **Handover Summary**: `refactoring_work/planning/core_documents/ai_handover_summary.md`
- **0.2.0 Reference**: `0.2.0/` directory (for reference only, not compatibility)

## 🎪 **V2 Enhanced Project Structure**

```
openmas/
├── .cursor/rules/                 # AI continuity rules (THIS FILE)
├── refactoring_work/
│   ├── planning/                  # V2: Organized by status
│   │   ├── 00_ACTIVE_TASKS/       # Currently being worked on
│   │   ├── 01_READY_TO_START/     # Dependencies complete
│   │   ├── 02_BLOCKED/            # Waiting for dependencies
│   │   ├── core_documents/        # V2: Core tracking files
│   │   │   ├── current_phase.md   # LIVING: Current phase objectives
│   │   │   ├── task_tracker.md    # LIVING: Real-time task status
│   │   │   └── ai_handover_summary.md # V2: Session handovers
│   │   └── templates/             # V2: Task templates
│   ├── design/                    # LIVING: Work-in-progress design specs
│   │   ├── completed/             # IMMUTABLE: Ready-for-implementation APIs
│   │   └── [categories]/          # LIVING: Active design work
│   ├── archive/                   # IMMUTABLE: Completed phases & tasks
│   │   ├── phase_1/               # IMMUTABLE: Phase 1 completed tasks
│   │   └── phase_N/               # IMMUTABLE: Future completed phases
│   └── 01_implementation_plan/    # IMMUTABLE: Master plans & initial thinking
├── src/openmas/                   # Implementation code
├── tests/                         # Test suites mirroring src structure
└── 0.2.0/                        # REFERENCE ONLY: Previous implementation
```

## 🎯 **Success Metrics**

**AI Continuity Success = Any AI can resume work within 5 minutes by:**
1. Reading the 3 mandatory files (this file + current_phase.md + task_tracker.md)
2. Understanding exactly what's been completed and what's next
3. Following established patterns from completed work
4. Making progress without asking basic "what is this project" questions

**V2 Anti-Hallucination Success = Bulletproof quality by:**
1. All integration tests pass against REAL external libraries
2. No critical code paths use mocked external dependencies
3. Coverage metrics reflect REAL test execution only
4. Demos run reliably without hanging or timeout issues

---

**The goal of this system is to eliminate the "conversation too long" problem AND the "hallucinated implementation" problem by ensuring perfect handoff between AI sessions through systematic documentation, clear protocols, and real-first testing.**
