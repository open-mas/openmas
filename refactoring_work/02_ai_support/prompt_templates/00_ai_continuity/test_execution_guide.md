# AI Continuity Test Execution Guide

**Purpose**: Step-by-step instructions for testing the OpenMAS AI continuity system
**When to Use**: After establishing continuity protocols, periodically, or when improving the system

## 🚀 **Quick Test (5 minutes)**

### Step 1: Prepare Current Session
1. Complete your current work
2. Update task tracker with current status
3. Document exact resume point in any active TASK files

### Step 2: Get Test Prompt
Copy this exact prompt:

```
I am testing the OpenMAS AI continuity system. I must demonstrate rapid project understanding and work resumption.

MANDATORY PROTOCOL:
1. Read .cursor/rules/openmas_ai_continuity.md
2. Read refactoring_work/planning/current_phase.md
3. Read refactoring_work/planning/task_tracker.md

VALIDATION REQUIRED:
After reading those 3 files, I must immediately:
- Summarize current project status and next priority
- Demonstrate understanding of OpenMAS architecture (SIMF, reasoning agnosticism)
- Show file lifecycle comprehension (LIVING vs IMMUTABLE docs)
- Either start work OR state exactly what's needed to proceed

SUCCESS = Full context + work readiness in < 5 minutes, zero basic questions

Begin test now.
```

### Step 3: Execute Test
1. **Start fresh AI conversation** (new chat/session)
2. **Paste the prompt** exactly as written
3. **Start timer** when you send the prompt
4. **Watch for**:
   - Time to demonstrate understanding (target: < 5 minutes)
   - Basic questions like "What is OpenMAS?" (target: zero)
   - Correct identification of next priority task
   - Readiness to continue work

### Step 4: Evaluate Results

**✅ PASS** if AI:
- Identifies OpenMAS as reasoning-agnostic multi-agent framework
- Knows Phase 1 status (1/3 complete, Communication Pattern Engine next)
- Understands SIMF, protocol independence, Pydantic models
- Shows file lifecycle knowledge (planning/ → archive/)
- Ready to work without asking basic questions

**❌ FAIL** if AI:
- Asks "What is OpenMAS?" or similar basic questions
- Cannot identify current phase/progress
- Confused about file locations or architecture
- Takes > 5 minutes for basic understanding

## 📊 **Test Results Template**

Document your test results:

```
## AI Continuity Test Results - [Date]

**Test Duration**: [X minutes]
**AI Model**: [e.g., Claude Sonnet 4]
**Test Prompt**: Quick continuity test

### Context Acquisition
- [ ] Project identification (OpenMAS reasoning-agnostic framework)
- [ ] Phase status (Phase 1, 1/3 complete)
- [ ] Next priority (Communication Pattern Engine API)
- [ ] Architecture principles (SIMF, reasoning agnosticism, Pydantic)

### Process Understanding
- [ ] File lifecycle (LIVING vs IMMUTABLE)
- [ ] Task movement (planning/ → archive/)
- [ ] Tracking requirements (real-time updates)

### Work Readiness
- [ ] No basic context questions
- [ ] Ready to continue work immediately
- [ ] References completed work for patterns

### Overall Result: [PASS/FAIL]
**Notes**: [Any observations or improvement areas]
```

## 🔧 **If Test Fails**

### Common Failure Points & Fixes:

**Problem**: AI asks "What is OpenMAS?"
**Fix**: Enhance project description in `.cursor/rules/openmas_ai_continuity.md`

**Problem**: Cannot identify current phase
**Fix**: Improve clarity in `refactoring_work/planning/current_phase.md`

**Problem**: Confused about next priority
**Fix**: Make task priorities clearer in `refactoring_work/planning/task_tracker.md`

**Problem**: Doesn't understand file lifecycle
**Fix**: Add better examples to AI continuity rules

### Improvement Process:
1. Identify specific failure point
2. Enhance the problematic documentation
3. Re-test with fresh AI session
4. Iterate until test passes consistently

## 🎯 **Success Metrics**

Track these over time:
- **Time to Context**: Average time for AI to demonstrate understanding
- **Question Count**: Number of basic context questions (trend toward zero)
- **Test Pass Rate**: Percentage of tests that pass on first attempt
- **Work Continuity**: Can fresh AI immediately continue productive work?

**Target**: 100% pass rate with < 3 minute context acquisition and zero basic questions.

---

**Remember**: The goal is seamless handoff. If any fresh AI session struggles with basic context, the continuity system needs improvement.
