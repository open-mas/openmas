# Architectural Remediation Task Creation Prompt

## Context

The lead architect has completed a comprehensive design review of OpenMAS 0.3.0 and identified **critical architectural pattern violations** that must be addressed immediately. These violations prevent OpenMAS from achieving its core design goals of reasoning agnosticism and progressive extensibility.

**Review Document**: `/refactoring_work/planning/DESIGN_REVIEW_OPENMAS_0_3_0.md`

## Task Creation Objective

Create specific, actionable implementation tasks to address the **3 CRITICAL architectural pattern violations** identified in the design review. These tasks must follow the Task Creation Protocol in `/refactoring_work/planning/TASK_CREATION_PROTOCOL.md` and enable OpenMAS to achieve its architectural design goals.

## Critical Architectural Violations to Address

Based on the comprehensive design review, create implementation tasks for these **IMMEDIATE PRIORITY** violations:

### 1. **Body-Brain Separation (Reasoning Agnosticism)** - CRITICAL VIOLATION
**Current Problem**: Agent class directly manages both communication AND reasoning logic, making reasoning agnosticism impossible.

**Required Implementation**: 
- Create separate `Communicator` and `ReasoningEngine` components
- Refactor Agent class to use dependency injection: `Agent(communicator, reasoning_engine)`
- Implement clean interfaces between body (communication) and brain (reasoning)

### 2. **Facade Pattern** - CRITICAL VIOLATION  
**Current Problem**: No facade exists - clients interact directly with complex Agent class internals.

**Required Implementation**:
- Create `AgentFacade` class as primary client interface
- Implement factory pattern: `CommunicatorFactory`, `ReasoningFactory`
- Add lifecycle management: `LifecycleManager`
- Provide simplified interface for complex subsystem initialization

### 3. **Strategy Pattern (Reasoning)** - CRITICAL VIOLATION
**Current Problem**: No reasoning strategy abstraction, reasoning logic embedded in Agent.

**Required Implementation**:
- Create `ReasoningStrategy` abstract base class
- Implement concrete reasoning strategies (Rule-based, LLM-based, etc.)
- Enable runtime reasoning strategy swapping
- Separate reasoning logic from Agent class

## Task Creation Requirements

### Follow Task Creation Protocol
- Use the three mandatory inputs (Design Documentation, User Business Needs, Current Codebase)
- Reference specific design documents in `/refactoring_work/design/01_architecture/`
- Align with existing codebase structure and quality standards
- Include anti-hallucination safeguards

### Quality Requirements
- **Zero Regression Policy**: All 302 existing tests must continue passing
- **Type Safety**: Full MyPy compliance with strict typing
- **Testing**: Comprehensive unit and integration tests for new components
- **Documentation**: Clear interfaces and usage examples

### Implementation Constraints
- **Preserve SIMF**: Maintain existing SIMF message format and functionality
- **Preserve MCP Integration**: Keep existing MCP protocol adapter working
- **Incremental Changes**: Enable gradual migration without breaking existing functionality
- **Configuration Driven**: Follow OpenMAS configuration-driven architecture principles

## Specific Task Creation Instructions

Create **3 separate tasks**, one for each critical violation:

### Task 1: Body-Brain Separation Implementation
**Title**: "Implement Body-Brain Separation Pattern for Reasoning Agnosticism"

**Scope**:
- Create `Communicator` interface and implementation
- Create `ReasoningEngine` interface and base implementation  
- Refactor `Agent` class to use dependency injection
- Implement clean separation between communication and reasoning logic
- Maintain backward compatibility during transition

**Success Criteria**:
- Agent class accepts `communicator` and `reasoning_engine` parameters
- Communication logic isolated in Communicator component
- Reasoning logic isolated in ReasoningEngine component
- All existing tests pass
- New components have comprehensive test coverage

### Task 2: Facade Pattern Implementation
**Title**: "Implement AgentFacade Pattern for Simplified Client Interface"

**Scope**:
- Create `AgentFacade` class as primary client interface
- Implement factory classes: `CommunicatorFactory`, `ReasoningFactory`
- Create `LifecycleManager` for agent lifecycle management
- Provide simplified initialization and operation methods
- Create migration guide for existing Agent usage

**Success Criteria**:
- `AgentFacade` provides simple interface to complex agent subsystems
- Factory pattern enables configuration-driven component creation
- Lifecycle management handles initialization/shutdown complexity
- Existing Agent class becomes internal implementation detail
- Clear migration path for existing code

### Task 3: Strategy Pattern for Reasoning Implementation  
**Title**: "Implement Strategy Pattern for Pluggable Reasoning Engines"

**Scope**:
- Create `ReasoningStrategy` abstract base class
- Implement concrete strategies: `RuleBasedReasoning`, `LLMReasoning`
- Enable runtime strategy swapping
- Create reasoning strategy factory and registry
- Separate all reasoning logic from Agent class

**Success Criteria**:
- `ReasoningStrategy` interface with `async def reason(context)` method
- Multiple concrete reasoning implementations
- Runtime strategy swapping capability
- Agent class delegates all reasoning to strategy objects
- Reasoning strategies are testable in isolation

## Task Dependencies and Sequencing

**Recommended Implementation Order**:
1. **Task 1** (Body-Brain Separation) - Foundation for other patterns
2. **Task 3** (Strategy Pattern) - Depends on ReasoningEngine interface from Task 1
3. **Task 2** (Facade Pattern) - Orchestrates components from Tasks 1 & 3

**Parallel Development**: Tasks 1 and 3 can be developed in parallel if needed.

## Validation Requirements

Each task must include:
- **Design Alignment Verification**: Code examples showing compliance with architectural patterns
- **Integration Testing**: Verify components work together correctly
- **Performance Testing**: Ensure no performance regression
- **Documentation**: Clear usage examples and migration guides

## Business Value Delivery

After these 3 critical tasks are complete:
- OpenMAS will achieve true reasoning agnosticism
- Progressive extensibility will be possible
- PowerBI-specific agents can be easily created
- Foundation for enterprise adoption will be established

## Anti-Hallucination Safeguards

Each task must:
- Reference specific design documents and line numbers
- Include concrete code examples from design specifications
- Verify against existing codebase structure
- Include comprehensive testing to prevent regressions
- Follow established OpenMAS coding standards and patterns

## Success Metrics

**Task Completion Criteria**:
- [ ] All 3 critical architectural patterns properly implemented
- [ ] Zero test regressions (all 302 tests passing)
- [ ] MyPy strict compliance maintained
- [ ] Design review validation passes
- [ ] Clear migration path for existing code

**Architectural Goals Achieved**:
- [ ] Reasoning agnosticism functionally possible
- [ ] Progressive extensibility enabled
- [ ] Clean client interfaces available
- [ ] Foundation for business value delivery established

This prompt ensures the planning agent creates specific, actionable tasks that directly address the critical architectural violations while maintaining OpenMAS's quality standards and design principles.
