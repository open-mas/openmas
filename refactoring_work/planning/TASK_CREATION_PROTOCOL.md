# OpenMAS Task Creation Protocol v2.0
## Mandatory Design Alignment & Anti-Hallucination Framework

---

## 🎯 **Protocol Objective**

**PREVENT AI HALLUCINATION IN TASK CREATION** by enforcing strict design alignment when AIs create new tasks for OpenMAS modules, components, or features.

**Context**: OpenMAS 0.2.0 suffered from over 1000 passing tests that tested nothing due to AI hallucinations creating misaligned tasks. This protocol ensures that **NEVER** happens again in 0.3.0.

---

## 🚫 **MANDATORY PROHIBITIONS**

Before creating ANY task, the AI **MUST NOT**:

1. **❌ NEVER create tasks without reading design documentation**
2. **❌ NEVER assume missing context or "fill in the gaps"**
3. **❌ NEVER ignore existing architectural patterns**
4. **❌ NEVER create tasks that bypass established interfaces**
5. **❌ NEVER hallucinate requirements not present in design docs**
6. **❌ NEVER create tasks without explicit design alignment statements**

**Violation of these prohibitions is grounds for immediate task rejection.**

---

## ✅ **MANDATORY TASK CREATION PROCESS**

### **Phase 1: Design Document Discovery & Review**

**BEFORE** writing a single word of a task, the AI **MUST**:

1. **Identify Relevant Design Documents**
   ```
   REQUIRED: List ALL design documents related to the task scope:
   - Primary: [specific design document path]
   - Secondary: [related interface documents]
   - Dependencies: [upstream/downstream components]
   ```

2. **Read and Understand Architecture Context**
   ```
   REQUIRED: Demonstrate understanding by stating:
   - How this component fits into OpenMAS architecture
   - Which existing interfaces it must implement/use
   - What architectural constraints apply (SIMF, reasoning agnosticism, etc.)
   ```

3. **Verify No Existing Implementation**
   ```
   REQUIRED: Confirm that:
   - Component doesn't already exist in design docs
   - Interface isn't already defined elsewhere
   - Task doesn't duplicate existing work
   ```

### **Phase 2: Architecture Alignment Verification**

**MANDATORY CHECKLIST** - AI must explicitly confirm:

- [ ] **SIMF Compatibility**: Task respects Standard Internal Message Format
- [ ] **Reasoning Agnosticism**: Clean separation between "body" and "brain"
- [ ] **Protocol Independence**: No protocol-specific logic in core components
- [ ] **Interface Consistency**: Follows established Pydantic model patterns
- [ ] **Async-First Design**: All interfaces support async operations
- [ ] **Configuration Schema**: Aligns with unified configuration schema
- [ ] **Extension Points**: Respects decentralized factory-based extension system

### **Phase 2.5: Quality & Linting Enforcement (MANDATORY)**

**CRITICAL**: Every task MUST include explicit quality enforcement to prevent the 400+ linting issues that occurred when AIs ignored code quality standards.

**MANDATORY QUALITY CHECKLIST** - AI must explicitly confirm:

- [ ] **Code Formatting & Linting**: All code will be formatted and linted with `ruff` (line-length=120, ignore=E203,W503)
- [ ] **Import Sorting**: All imports will be sorted with `ruff` (profile=black)
- [ ] **Type Checking**: All code will pass `mypy` static type analysis
- [ ] **Pre-commit Hooks**: All changes will pass pre-commit hook validation
- [ ] **Tox Integration**: Implementation will be tested using appropriate tox environments

**QUALITY ENFORCEMENT COMMANDS** - AI must run these before task completion:

```bash
# MANDATORY: Run these commands before marking task complete
# Check linting
poetry run ruff check src/openmas tests

# Format code and sort imports
poetry run ruff format src/openmas tests

# Type checking
poetry run mypy src/openmas

# Run pre-commit hooks
pre-commit run --all-files

# Run appropriate tox environments
tox -e lint,type,unit
```

**QUALITY GATE REQUIREMENTS**:

1. **Zero Linting Violations**: No ruff or mypy errors allowed
2. **Pre-commit Success**: All pre-commit hooks must pass
3. **Tox Environment Success**: Relevant tox environments must pass
4. **Documentation Standards**: All new code must include proper docstrings (Google style)
5. **Test Coverage**: New code must include appropriate unit tests

**ANTI-HALLUCINATION QUALITY MEASURES**:

- [ ] **Real Tool Execution**: Actually run quality tools, don't assume compliance
- [ ] **Error Resolution**: Fix all quality violations, don't ignore or suppress
- [ ] **Configuration Compliance**: Follow existing ruff configuration in pyproject.toml, .pre-commit-config.yaml, tox.ini settings
- [ ] **Incremental Quality**: Don't introduce new quality debt

### **Phase 3: Task Specification with Design References**

**REQUIRED TASK FORMAT:**

```markdown
# TASK: [Clear, Actionable Title]

## Design Alignment Statement
**Primary Design Document**: [exact path to main design doc]
**Related Interfaces**: [list of existing interfaces this task must implement/use]
**Architectural Constraints**: [specific OpenMAS constraints that apply]

## Objective
[Single sentence objective that references design documentation]

## Design Context & Justification
**Why This Task**: [reference to specific gap in design documentation]
**Architecture Fit**: [how this component integrates with existing architecture]
**Interface Dependencies**: [existing interfaces this component must use]

## Key Deliverables
[Each deliverable must reference specific design patterns or interfaces]
- Deliverable 1: [with reference to design doc section]
- Deliverable 2: [with reference to existing interface pattern]
- Deliverable 3: [with reference to architectural constraint]

## Design Compliance Requirements
**Interface Patterns**: [specific existing patterns to follow]
**Data Models**: [reference to existing Pydantic models to extend/use]
**Error Handling**: [reference to established error handling patterns]
**Testing Requirements**: [reference to established testing patterns]

## Cross-Reference Updates Required
[List of design documents that must be updated when this task is complete]
- Document 1: [specific section that needs updating]
- Document 2: [specific interface that needs extending]

## Verification Criteria
- [ ] Implementation follows referenced design patterns exactly
- [ ] All interfaces use established Pydantic model conventions
- [ ] Component integrates properly with referenced dependencies
- [ ] No architectural constraints are violated
- [ ] Cross-references are updated correctly

## Quality Enforcement Verification (MANDATORY)
- [ ] Code formatted with `black --line-length=120`
- [ ] Imports sorted with `isort --profile=black --line-length=120`
- [ ] All `flake8` checks pass (max-line-length=88)
- [ ] All `mypy` type checks pass
- [ ] All `pre-commit` hooks pass
- [ ] Relevant `tox` environments pass (lint, type, unit)
- [ ] Zero linting violations introduced
- [ ] Proper Google-style docstrings added
- [ ] Unit tests added for new functionality

## Anti-Hallucination Safeguards
**Design Documents Read**: [list with confirmation of understanding]
**Assumptions Made**: [NONE - all requirements come from design docs]
**Missing Context**: [if any, explicitly state and request clarification]
**Quality Tools Executed**: [list actual commands run and their results]
**Linting Status**: [confirm zero violations or list specific fixes made]

**Task Status**: [NOT_STARTED | IN_PROGRESS | COMPLETE]
```

---

## 🔍 **TASK REVIEW & VALIDATION PROCESS**

### **Self-Validation Checklist**

Before submitting any task, the AI **MUST** verify:

1. **Design Alignment**
   - [ ] Task references specific design documents
   - [ ] All requirements trace back to documented architecture
   - [ ] No assumptions or hallucinated requirements

2. **Interface Consistency**
   - [ ] Uses established interface patterns
   - [ ] Follows existing Pydantic model conventions
   - [ ] Respects architectural constraints

3. **Integration Requirements**
   - [ ] Identifies all dependent components
   - [ ] Specifies required cross-reference updates
   - [ ] Defines clear integration points

### **Mandatory Review Questions**

The AI **MUST** answer these questions before task creation:

1. **"What specific design document gap does this task address?"**
2. **"Which existing interfaces will this component implement or use?"**
3. **"How does this task maintain OpenMAS's reasoning agnosticism?"**
4. **"What architectural constraints apply to this component?"**
5. **"Which design documents need updates when this task is complete?"**

---

## 🛡️ **INTEGRATION WITH V2 PLANNING SYSTEM**

### **V2 System Enhancement**

This protocol **EXTENDS** the existing V2 AI Continuity System by adding task creation safeguards:

1. **Session Start Protocol** (existing V2)
   - Read `AI_CONTINUITY_SYSTEM.md`
   - Read `current_phase.md`
   - Read `task_tracker.md`

2. **NEW: Task Creation Protocol** (this document)
   - **BEFORE** creating any task, follow this protocol
   - **MANDATORY** design alignment verification
   - **REQUIRED** anti-hallucination safeguards

3. **Task Execution** (existing V2)
   - Execute tasks using established V2 patterns
   - Update progress tracking
   - Maintain design alignment during implementation

### **V2 System Integration Points**

- **AI_CONTINUITY_SYSTEM.md** should reference this protocol for task creation
- **current_phase.md** should include design alignment requirements
- **task_tracker.md** should track design compliance status

---

## 📋 **PROTOCOL ENFORCEMENT**

### **Violation Detection**

Tasks that violate this protocol exhibit these warning signs:
- Generic requirements not tied to specific design documents
- Assumptions about missing functionality
- Interface definitions that don't follow established patterns
- Requirements that bypass architectural constraints
- Missing references to existing design documentation
- **Quality violations**: Code that doesn't pass linting, formatting, or type checking
- **Tool ignorance**: Not running or ignoring results of quality enforcement commands
- **Linting debt**: Introducing new flake8, black, isort, or mypy violations

### **Remediation Process**

When protocol violations are detected:
1. **STOP** task creation immediately
2. **IDENTIFY** the specific violation(s)
3. **FOR QUALITY VIOLATIONS**: Run quality enforcement commands and fix all issues
4. **FOR DESIGN VIOLATIONS**: Return to Phase 1 and re-read relevant design documentation
5. **RESTART** task creation process with proper design alignment and quality compliance

---

## 🎪 **SUCCESS CRITERIA**

This protocol is successful when:

- [ ] **Zero hallucinated requirements** in task specifications
- [ ] **100% design document traceability** for all task requirements
- [ ] **Perfect architectural alignment** with OpenMAS constraints
- [ ] **Consistent interface patterns** across all new components
- [ ] **Proper integration** with existing design documentation
- [ ] **Clear cross-reference updates** specified for all tasks

---

## 🚀 **PROTOCOL ACTIVATION**

**EFFECTIVE IMMEDIATELY**: All AIs creating tasks for OpenMAS 0.3.0 **MUST** follow this protocol.

**No exceptions. No shortcuts. No assumptions.**

**The goal**: Ensure every task created is perfectly aligned with OpenMAS design, preventing the hallucination disasters that plagued 0.2.0.

---

**Remember**: Simple is better. Design alignment is mandatory. Hallucination is prohibited.

**This protocol exists to ensure OpenMAS 0.3.0 succeeds where 0.2.0 failed.**
