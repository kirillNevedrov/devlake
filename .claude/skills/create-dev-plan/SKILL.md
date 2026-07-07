---
name: create-dev-plan
description: Create development plan. Use it to prepare development plan consisting of list of tasks from technical design specification.
allowed-tools: Read, Write, Bash
---

## Input

- Requirements specification: @features_context/$ARGUMENTS[0]/requirements_spec.md
- Technical design specification: @features_context/$ARGUMENTS[0]/tech_design_spec.md

## Instructions

1. Read the technical design specification file.
2. Read the requirements specification file for additional context.
3. Ask the user all necessary questions to clarify planning details before writing the plan.
4. Write the development plan as a list of tasks organized into stages.
5. Write a details file for each task.

### Task requirements

- Each task must represent a completed part of the feature that does not break the existing system.
- Each task must be small enough to be implemented by a single AI agent using an LLM with 200k tokens context window.
- Each task has an id, name, status, and a link to its details file at @features_context/$ARGUMENTS[0]/tasks/{task id}.md.
- Task details file shall not duplicate information from Requirements specification and Technical design specification files. Instead it shall have links to Requirements specification and Technical design specification if necessary.

### Stage organization

- Organize tasks into stages in the development plan.
- Each stage contains all the tasks that can be implemented in parallel and have no dependencies on tasks from the next stage.
- Tasks within the same stage must not depend on each other.

## Output

- Write the development plan to @features_context/$ARGUMENTS[0]/dev_plan.md
- Write task details to @features_context/$ARGUMENTS[0]/tasks/{task id}.md for each task.
