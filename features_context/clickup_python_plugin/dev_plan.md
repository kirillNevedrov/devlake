# Development Plan — ClickUp Python Plugin

> Specs: [requirements_spec.md](./requirements_spec.md) · [tech_design_spec.md](./tech_design_spec.md)
>
> This plan slices the feature into tasks sized for a single AI agent (≤200k-token
> context). Each task is independently shippable: it compiles/imports and does not break
> the existing system. Task detail files live in [`tasks/`](./tasks/) and do **not**
> duplicate the specs — they link back to them.

## Conventions

- **Tests live inside each task.** Every task that produces code also adds its unit /
  integration tests (pytest for backend) as part of its Definition of Done. There are no
  test-only tasks.
- **Mirror `azuredevops`.** The backend plugin copies the structure, file layout, and
  licensing header of `backend/python/plugins/azuredevops`.
- **Domain tables are owned by Go core.** No task creates `issues` / `incidents` /
  `boards` / `*_assignees` tables; migrations create **tool tables only** (see T5).

## Status legend

`TODO` · `IN_PROGRESS` · `DONE`

## Stages

A stage contains tasks with no dependencies on each other; every task depends only on
earlier stages.

### Stage 1 — Foundations (fully parallel)

| ID | Name | Status | Details | Depends on |
| --- | --- | --- | --- | --- |
| T1 | Shared `ticket` domain layer module in pydevlake | DONE | [T1.md](./tasks/T1.md) | — |
| T2 | ClickUp plugin scaffold + tool/config models | DONE | [T2.md](./tasks/T2.md) | — |
| T3 | Config-UI plugin registration | DONE | [T3.md](./tasks/T3.md) | — |

### Stage 2 — API client & schema (parallel)

| ID | Name | Status | Details | Depends on |
| --- | --- | --- | --- | --- |
| T4 | ClickUp API client, paginator & error/rate-limit hooks | DONE | [T4.md](./tasks/T4.md) | T2 |
| T5 | Tool-table migration | DONE | [T5.md](./tasks/T5.md) | T2 |

### Stage 3 — Collection & conversion

| ID | Name | Status | Details | Depends on |
| --- | --- | --- | --- | --- |
| T6 | `ClickupTasks` stream (collect / extract / convert) | DONE | [T6.md](./tasks/T6.md) | T1, T2, T4 |

### Stage 4 — Plugin assembly

| ID | Name | Status | Details | Depends on |
| --- | --- | --- | --- | --- |
| T7 | `ClickUpPlugin` wiring: connection test, remote scopes, board scopes | TODO | [T7.md](./tasks/T7.md) | T1, T2, T4, T6 |

## Out of scope (documented, not implemented as tasks)

- **E2E config-UI (Playwright) flow** from tech design §1.6. Requires a live ClickUp
  workspace and a running DevLake stack; tracked as a manual / deferred verification step
  rather than an implementation task.
- **Deleted-task pruning** — a known limitation (requirements §Limitations); no task.
- **Webhook-based real-time deletion** — explicit future enhancement, out of scope.

## Dependency graph

```
T1 ─┐
T2 ─┼─► T4 ─┐
    └─► T5  ├─► T6 ─► T7
T3 (independent — config-UI)
T1 ──────────► T6, T7
```
