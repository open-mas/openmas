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
7. **❌ NEVER prioritize "backward compatibility" over simplicity and maintainability**
8. **❌ NEVER assume existing users or production deployments exist**

**OpenMAS 0.3.0 Clean Slate Principle**: This is a **clean slate rewrite** with no existing users, no production deployments, and **NO backward compatibility requirements**. Prioritize **simplicity, maintainability, and additive growth** over unnecessary complexity.

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

**TYPING REQUIREMENTS** - AI must explicitly confirm:

- [ ] **Type Annotations**: All functions have proper return type annotations (`-> None`, `-> str`, etc.)
- [ ] **Union Type Handling**: Complex unions use `isinstance()` for type narrowing (never direct attribute access)
- [ ] **Generic Types**: Proper parameterization (`dict[str, Any]`, `list[str]`, not bare `dict` or `list`)
- [ ] **Protocol Integration**: External library types properly integrated with type hints
- [ ] **Async Typing**: Async methods have proper return type annotations (`-> Awaitable[T]`, `-> None`)
- [ ] **Optional Types**: Explicit `Optional[T]` or `T | None` instead of implicit nullable types
- [ ] **Payload Unions**: SIMF payload unions handled with proper type guards (see typing guidelines)
- [ ] **Error Prevention**: No `union-attr`, `no-untyped-def`, or `assignment` mypy errors

**ZERO REGRESSION POLICY** - AI must NEVER break existing functionality:

```bash
# MANDATORY: Run BEFORE making any changes to establish baseline
echo "=== ESTABLISHING BASELINE - TESTS MUST PASS BEFORE CHANGES ==="
python -m pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
    echo "❌ BASELINE FAILED: Tests are already broken. Fix before proceeding."
    exit 1
fi
echo "✅ BASELINE ESTABLISHED: All tests passing before changes"
```

**QUALITY ENFORCEMENT COMMANDS** - AI must run these before task completion:

```bash
# MANDATORY: Run these commands before marking task complete
# Check linting
poetry run ruff check src/openmas tests

# Format code and sort imports
poetry run ruff format src/openmas tests

# Type checking with comprehensive validation
poetry run mypy src/openmas --show-error-codes

# TYPING VALIDATION: Verify no critical typing errors
echo "Checking for union-attr errors..."
! poetry run mypy src/openmas | grep "union-attr"

echo "Checking for missing annotations..."
! poetry run mypy src/openmas | grep "no-untyped-def"

echo "Checking for assignment errors..."
! poetry run mypy src/openmas | grep "assignment"

echo "Checking for call-arg errors..."
! poetry run mypy src/openmas | grep "call-arg"

# Run pre-commit hooks
pre-commit run --all-files

# Run appropriate tox environments (includes type checking)
tox -e lint,type,unit

# MANDATORY: ZERO REGRESSION VALIDATION - Tests must still pass after changes
echo "=== ZERO REGRESSION VALIDATION - TESTS MUST PASS AFTER CHANGES ==="
python -m pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
    echo "❌ REGRESSION DETECTED: Tests broken by changes. REVERT IMMEDIATELY."
    echo "❌ TASK FAILED: Cannot complete task with broken tests."
    exit 1
fi
echo "✅ ZERO REGRESSION CONFIRMED: All tests still passing after changes"
```

**QUALITY GATE REQUIREMENTS**:

1. **ZERO REGRESSION POLICY**: All tests MUST pass before AND after changes (MANDATORY)
2. **Zero Linting Violations**: No ruff or mypy errors allowed
3. **Pre-commit Success**: All pre-commit hooks must pass
4. **Tox Environment Success**: Relevant tox environments must pass
5. **Documentation Standards**: All new code must include proper docstrings (Google style)
6. **Test Coverage**: New code must include appropriate unit tests
7. **Type Safety Compliance**: Zero critical typing errors (union-attr, no-untyped-def, assignment, call-arg)
8. **Type Annotation Coverage**: All public methods and functions have proper type annotations
9. **Union Type Safety**: All union types use proper type narrowing with isinstance() checks
10. **Generic Type Usage**: All collections use proper generic parameterization
11. **Protocol Integration**: External library types properly integrated with OpenMAS type system

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

### Typing Patterns (MANDATORY)
**Union Type Handling**: All union types must use `isinstance()` for type narrowing
```python
# ✅ CORRECT: Type narrowing with isinstance()
if isinstance(payload, InvocationContentPayload):
    capability_name = payload.invocation_name  # Safe access

# ❌ WRONG: Direct attribute access on union
capability_name = payload.invocation_name  # mypy error: union-attr
```

**Generic Types**: Use proper parameterization for all collections
```python
# ✅ CORRECT: Proper generic types
data: dict[str, Any] = {}
tools: list[Tool] = []
result: Optional[str] = None

# ❌ WRONG: Bare types
data: dict = {}  # mypy error: missing type parameters
tools: list = []  # mypy error: missing type parameters
```

**Function Annotations**: All functions must have complete type annotations
```python
# ✅ CORRECT: Complete annotations
async def execute_capability(self, message: SIMFMessage) -> SIMFMessage:
    ...

def validate_config(self, config: dict[str, Any]) -> bool:
    ...

# ❌ WRONG: Missing annotations
async def execute_capability(self, message):  # mypy error: no-untyped-def
    ...
```

**SIMF Payload Unions**: Reference `docs/development/typing_guidelines.md` for payload handling patterns

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
- [ ] Code formatted with `ruff format` (line-length=120, ignore=E203,W503)
- [ ] Imports sorted with `ruff check --fix` (profile=black)
- [ ] All `ruff check` violations resolved
- [ ] All `mypy` type checks pass with `--show-error-codes`
- [ ] All `pre-commit` hooks pass
- [ ] Relevant `tox` environments pass (lint, type, unit)
- [ ] Zero linting violations introduced
- [ ] Proper Google-style docstrings added
- [ ] Unit tests added for new functionality

### Typing Verification (MANDATORY)
- [ ] **Type Annotations**: All functions have proper return type annotations
- [ ] **Union Type Safety**: No `union-attr` mypy errors (all unions use isinstance() checks)
- [ ] **Missing Annotations**: No `no-untyped-def` mypy errors
- [ ] **Assignment Safety**: No `assignment` mypy errors (proper type compatibility)
- [ ] **Call Arguments**: No `call-arg` mypy errors (proper function signatures)
- [ ] **Generic Types**: All collections properly parameterized (`dict[str, Any]`, not `dict`)
- [ ] **Optional Types**: Explicit `Optional[T]` or `T | None` usage
- [ ] **Protocol Integration**: External library types properly integrated
- [ ] **SIMF Compatibility**: Payload unions handled with proper type guards

## Anti-Hallucination Safeguards
**Design Documents Read**: [list with confirmation of understanding]
**Assumptions Made**: [NONE - all requirements come from design docs]
**Missing Context**: [if any, explicitly state and request clarification]
**Quality Tools Executed**: [list actual commands run and their results]
**Linting Status**: [confirm zero violations or list specific fixes made]
**Typing Validation**: [confirm all typing requirements met - reference typing guidelines]
**MyPy Error Status**: [confirm zero critical typing errors: union-attr, no-untyped-def, assignment, call-arg]

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
