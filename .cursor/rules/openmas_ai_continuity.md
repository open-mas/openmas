# OpenMAS AI Continuity Rules 🧠

**Last Updated**: 2024-12-28  
**Purpose**: Complete AI assistant guidelines for seamless continuity across sessions

## 🚨 **CRITICAL: Session Start Protocol**

**EVERY AI session MUST start by reading these 3 files in order:**

1. **This file** (`.cursor/rules/openmas_ai_continuity.md`) - Core rules & standards
2. **Current Phase** (`refactoring_work/planning/current_phase.md`) - Active objectives  
3. **Task Tracker** (`refactoring_work/planning/task_tracker.md`) - Status & next actions

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

## 📋 **File Lifecycle Management**

### **Planning Documents Lifecycle**

| Document | Purpose | Lifecycle | Location |
|----------|---------|-----------|----------|
| `current_phase.md` | Active phase objectives | **LIVING** - Updated throughout phase | `refactoring_work/planning/` |
| `task_tracker.md` | All task status tracking | **LIVING** - Updated in real-time | `refactoring_work/planning/` |
| `PHASE_N_MASTER_PLAN.md` | Phase-specific master plan | **IMMUTABLE** - Archive when phase complete | `refactoring_work/01_implementation_plan/` → `refactoring_work/archive/phase_N/` |

### **Task Files Lifecycle**

| Status | Location | Actions Required |
|--------|----------|------------------|
| **NOT_STARTED** | `refactoring_work/planning/TASK_*.md` | Create file, add to tracker |
| **IN_PROGRESS** | `refactoring_work/planning/TASK_*.md` | Update Progress Notes in real-time |
| **COMPLETE** | `refactoring_work/archive/phase_N/TASK_*.md` | Move file, update tracker, update current_phase.md |

### **Design Documentation Lifecycle**

| Type | Purpose | Location | Lifecycle |
|------|---------|----------|-----------|
| **Completed Specs** | Ready-for-implementation APIs | `refactoring_work/design/completed/` | **IMMUTABLE** - Reference only |
| **Active Design** | Work-in-progress specs | `refactoring_work/design/[category]/` | **LIVING** - Updated during work |
| **Archived Specs** | Historical/deprecated | `refactoring_work/archive/phase_N/design/` | **IMMUTABLE** - Historical reference |

## 🔄 **AI Session Management Protocol**

### **Session Start Checklist (MANDATORY)**
- [ ] Read this AI continuity rules file 
- [ ] Read `refactoring_work/planning/current_phase.md`
- [ ] Read `refactoring_work/planning/task_tracker.md`  
- [ ] Identify highest priority task or next action
- [ ] Update task status to "IN_PROGRESS" if starting new work

### **During Work (REAL-TIME UPDATES)**
- **Update Progress Notes** in active TASK file after each sub-task completion
- **Document design decisions** with clear rationale in "Decision Notes" sections
- **Reference completed work** in `refactoring_work/design/completed/` for consistency
- **Cross-reference updates** when changes impact other components
- **Maintain SIMF compatibility** for all protocol-related work

### **Session End Checklist (MANDATORY)**
- [ ] Update task status in `refactoring_work/planning/task_tracker.md`
- [ ] Document exact resume point for next AI in TASK Progress Notes
- [ ] Move completed TASK files to appropriate archive directory
- [ ] Update `refactoring_work/planning/current_phase.md` if phase objectives change
- [ ] Verify all cross-references are updated

### **Task Completion Protocol**
1. **Verify all criteria met** in TASK file verification section
2. **Update task status** to "COMPLETE" in tracker
3. **Move TASK file** from `planning/` to `archive/phase_N/`
4. **Update current_phase.md** with completion status
5. **Document next priority** for following AI session

## 💻 **Code Standards & Testing**

### **Python Requirements**
- **Python 3.10+** minimum version
- **Type hints required** for all functions, parameters, and returns
- **Black formatting** with 88-character line limit
- **Pydantic validation** for all data models and configurations

### **Testing Standards**
- **Unit tests required** for all new functions/classes with at least 70% coverage
- **Integration tests required** for all protocol adapters
- **Real library verification** - NEVER mock external APIs without testing real ones first
- **Test organization**: Mirror source structure in `/tests` directory
- **Test markers**: Use appropriate markers (unit, integration, mcp, grpc, mqtt, async)

### **Documentation Standards**
- **Google-style docstrings** for all public APIs with complete parameter documentation
- **Usage examples** required for complex interfaces
- **Cross-reference maintenance** when adding/modifying components
- **No documentation duplication** - reference unified configuration schema

## 🚫 **Critical Prohibitions**

### **Never Do These Things**
- **Never hallucinate** library APIs, functions, or file paths - verify everything exists
- **Never assume missing context** - ask questions or read referenced documentation  
- **Never delete existing implementations** without explicit user instruction
- **Never break SIMF compatibility** when working on protocol components
- **Never mix reasoning logic** with communication components
- **Never create files longer than 500 lines** - refactor into modules instead

### **Always Do These Things**
- **Always reference existing patterns** from completed TASK files for consistency
- **Always update cross-references** when modifying interfaces
- **Always include rationale** for design decisions in documentation
- **Always test against real libraries** before implementing adapters
- **Always maintain protocol independence** in shared components

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
- **Current Phase**: `refactoring_work/planning/current_phase.md` 
- **Task Tracker**: `refactoring_work/planning/task_tracker.md`
- **0.2.0 Reference**: `0.2.0/` directory (for reference only, not compatibility)

## 🎪 **Project Structure Overview**

```
openmas/
├── .cursor/rules/                 # AI continuity rules (THIS FILE)
├── refactoring_work/
│   ├── planning/                  # LIVING: Active planning & task tracking
│   │   ├── current_phase.md       # LIVING: Current phase objectives  
│   │   ├── task_tracker.md        # LIVING: Real-time task status
│   │   └── TASK_*.md              # ACTIVE: Work-in-progress tasks
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

---

**The goal of this system is to eliminate the "conversation too long" problem by ensuring perfect handoff between AI sessions through systematic documentation and clear protocols.** 