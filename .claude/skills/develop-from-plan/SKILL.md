---
name: develop-from-plan
description: Develop the feature from development plan. Use it to develop feature from development plan and technical design specification.
allowed-tools: Read, Write, Bash
---

## Input

- Requirements specification: @features_context/$ARGUMENTS[0]/requirements_spec.md
- Technical design specification: @features_context/$ARGUMENTS[0]/tech_design_spec.md
- Development plan: @features_context/$ARGUMENTS[0]/dev_plan.md
- Stage numbers (optional): $ARGUMENTS[1]

## Instructions

1. Read the development plan file.
2. Read the technical design specification file.
3. Read the requirements specification file for additional context.
4. Determine which stages to implement (see "Stage selection" below).
5. Implement each stage sequentially, running tasks within a stage in parallel using subagents.
6. After each stage, run tests in a separate subagent and fix any failures before proceeding to the next stage.

### Stage selection

- If `$ARGUMENTS[1]` is provided, implement only those stages. Otherwise, implement all stages.
- Supported formats:
  - Comma-separated values: `1,3` means stages 1 and 3.
  - Dash-separated ranges: `2-4` means stages 2, 3, and 4.
  - Combined: `1,3-5` means stages 1, 3, 4, and 5.

### Execution strategy

- Use subagents to develop tasks so the main agent context is kept clean.
- Run parallel subagents to implement all tasks within a single stage.
- Stages must be executed sequentially — each stage may depend on the previous one.

### For each task

1. Implement the task according to the development plan and technical design specification.
2. Update task development progress in @features_context/$ARGUMENTS[0]/tasks/{task id}.md.
3. After completion, update the task status to "completed" in @features_context/$ARGUMENTS[0]/dev_plan.md.

### Testing

- Run tests in a separate subagent after each stage is completed, so all tests for the stage run at once.
- If any tests fail, run an extra fix stage before proceeding to the next stage.