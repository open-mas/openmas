# OpenMAS AI Planning & Continuity System

This directory contains the planning, tracking, and continuity system for the OpenMAS project. It is designed to ensure seamless handovers between AI agents, maintain context, and provide a clear, real-time view of project status.

## V2 Directory Structure

The system uses a status-based directory structure to make the state of any task immediately apparent:

- **`00_ACTIVE_TASKS/`**: Contains tasks that are currently being worked on by an AI agent.
- **`01_READY_TO_START/`**: Contains tasks that are fully specified, unblocked, and ready for an agent to begin work.
- **`02_BLOCKED/`**: Contains tasks that are waiting on other dependencies to be completed.
- **`core_documents/`**: Contains the central tracking and handover files for the entire project.
- **`archive/`**: Contains all completed tasks, organized by phase.

## Core Documents

The `core_documents/` directory is the heart of the continuity system:

- **`task_tracker.md`**: The single source of truth for the status of all tasks, past and present. **All file paths in this tracker are relative to the `planning/` directory.**
- **`current_phase.md`**: A living document that outlines the high-level goals, progress, and key decisions of the current development phase.
- **`ai_handover_summary.md`**: The mandatory handover document. Before signing off, an agent MUST update this file with a summary of work completed, issues discovered, and the recommended next task.

## AI Agent Workflow

To ensure seamless continuity, all AI agents must follow this protocol:

1.  **Start of Session:**
    1.  Read this `README.md` file.
    2.  Read `core_documents/AI_CONTINUITY_SYSTEM.md` for the detailed rules.
    3.  Read `core_documents/current_phase.md` for strategic context.
    4.  Read `core_documents/ai_handover_summary.md` for the most recent session's output.
    5.  Select the highest-priority task from the `01_READY_TO_START/` directory.

2.  **During Session:**
    - Move the selected task file from `01_READY_TO_START/` to `00_ACTIVE_TASKS/`.
    - Update the `task_tracker.md` to reflect the "IN PROGRESS" status.
    - Perform the work as described in the task file.

3.  **End of Session:**
    - If the task is complete, move the task file to the appropriate `archive/` sub-directory.
    - If the task is not complete, ensure it remains in `00_ACTIVE_TASKS/`.
    - Update the `task_tracker.md` with the final status.
    - **Critically**, update `core_documents/ai_handover_summary.md` with all required information for the next agent.
