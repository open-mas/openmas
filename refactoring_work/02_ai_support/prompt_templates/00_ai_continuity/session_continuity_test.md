# AI Session Continuity Test Template

**Purpose**: Test the OpenMAS AI continuity system by simulating a fresh AI session handoff  
**Type**: Continuity Validation  
**Prerequisites**: Existing AI session with documented work in progress  
**Expected Duration**: 5-10 minutes for successful continuity  

## Test Objectives

This template validates that our AI continuity system works by:
1. **Rapid Context Acquisition**: New AI understands project state within 5 minutes
2. **Task Identification**: Correctly identifies current phase and next priority task
3. **Work Resumption**: Can continue work without asking basic context questions
4. **Protocol Adherence**: Follows established session start protocols

## Test Setup Instructions

### For the Current AI Session (Before Testing)
1. **Complete Session End Protocol** from `.cursor/rules/openmas_ai_continuity.md`
2. **Update all tracking documents**:
   - `refactoring_work/planning/task_tracker.md` - Current status
   - `refactoring_work/planning/current_phase.md` - Phase progress
   - Any active `TASK_*.md` files with progress notes
3. **Document exact resume point** in task progress notes
4. **Note specific testing criteria** you want the fresh AI to validate

### For the Testing Session (Fresh AI)
Use this exact prompt template below ⬇️

---

## 🧠 **Fresh AI Session Continuity Test Prompt**

```
I am a fresh AI session testing the OpenMAS AI continuity system. I need to demonstrate that I can rapidly understand the project state and resume work without context loss.

MANDATORY PROTOCOL - I must follow the exact session start checklist:

1. Read .cursor/rules/openmas_ai_continuity.md (complete AI guidelines)
2. Read refactoring_work/planning/current_phase.md (current objectives) 
3. Read refactoring_work/planning/task_tracker.md (task status & next actions)

After reading these 3 files, I must demonstrate continuity by:

IMMEDIATE OBJECTIVES:
- Identify current phase and progress status
- Identify next priority task or action  
- Understand project architecture constraints (SIMF, reasoning agnosticism, etc.)
- Show understanding of file lifecycle management
- Proceed with actual work OR identify specific blockers

SUCCESS CRITERIA:
- Complete context acquisition in < 5 minutes
- Zero questions about "what is this project" or basic architecture
- Correctly identify what was last worked on and what's next
- Follow established patterns from completed work
- Update progress tracking in real-time

TESTING VALIDATION:
After establishing context, please:
1. Summarize current phase status and progress
2. Identify the next priority task with specific reasoning
3. Explain the project's core architectural principles
4. Demonstrate understanding of file lifecycle (where documents move when complete)
5. Either begin actual work OR clearly state what information is needed to proceed

If I cannot achieve full context within 5 minutes or need to ask basic "what is this project" questions, the continuity system has failed and needs improvement.

Begin test now.
```

---

## Expected Success Indicators

### **Rapid Context Acquisition (< 5 minutes)**
- [ ] Identifies OpenMAS as reasoning-agnostic multi-agent framework
- [ ] Understands current phase objectives and progress
- [ ] Knows that 1/3 Phase 1 tasks are complete (IProtocolAdapter ✅)
- [ ] Identifies Communication Pattern Engine API as next priority

### **Architecture Understanding**
- [ ] Mentions Standard Internal Message Format (SIMF) requirement
- [ ] Understands reasoning agnosticism (body vs brain separation)
- [ ] Knows multi-protocol support (A2A, MCP, HTTP, MQTT, gRPC)
- [ ] References Pydantic models and async-first design principles

### **File Lifecycle Comprehension**
- [ ] Understands LIVING vs IMMUTABLE document types
- [ ] Knows task files move from `planning/` → `archive/phase_N/` when complete
- [ ] Can identify where to find completed APIs for reference patterns
- [ ] Knows the 3-file mandatory read sequence for AI sessions

### **Work Readiness**
- [ ] Can identify next concrete action without asking basic questions
- [ ] References existing completed work for consistency patterns
- [ ] Understands TASK file format and progress tracking requirements
- [ ] Ready to update task tracker and progress notes in real-time

## Failure Indicators (System Needs Improvement)

### **Context Confusion**
- ❌ Asks "What is OpenMAS?" or other basic project questions
- ❌ Cannot identify current phase or progress status
- ❌ Confused about file locations or document purposes
- ❌ Takes > 5 minutes to establish basic context

### **Architecture Misunderstanding**
- ❌ Doesn't understand SIMF requirement for protocols
- ❌ Mixes reasoning logic with communication components
- ❌ Ignores established interface patterns from completed work
- ❌ Doesn't follow Pydantic-first or async-first principles

### **Process Violations**
- ❌ Skips the 3-file mandatory read sequence
- ❌ Doesn't understand task file lifecycle
- ❌ Creates new processes instead of following established ones
- ❌ Doesn't update tracking documents during work

## Test Results Documentation

### Record These Metrics:
- **Time to Context**: How long until AI demonstrated full project understanding
- **Questions Asked**: Number of basic context questions (target: 0)
- **Accuracy**: Correctness of phase/task/priority identification
- **Work Readiness**: Could AI begin productive work immediately?

### Improvement Areas:
If test fails, identify which files need enhancement:
- **AI Rules**: `.cursor/rules/openmas_ai_continuity.md`
- **Phase Documentation**: `refactoring_work/planning/current_phase.md`
- **Task Tracking**: `refactoring_work/planning/task_tracker.md`
- **Cross-References**: Links between documents

## Post-Test Actions

### If Test Succeeds:
- [ ] Document test success with metrics
- [ ] Proceed with actual work using the fresh AI session
- [ ] Note any minor improvements for next iteration

### If Test Fails:
- [ ] Document specific failure points
- [ ] Identify which files need improvement
- [ ] Enhance the problematic documentation
- [ ] Re-test with another fresh AI session

---

**Goal**: Achieve seamless AI handoff where any fresh session can be productive within 5 minutes using only the 3-file protocol. 