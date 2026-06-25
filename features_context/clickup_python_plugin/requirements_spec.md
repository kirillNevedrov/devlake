# Requirements Specification — ClickUp Plugin

## 1.1 Problem statement

DevLake users who manage their work in ClickUp cannot currently bring that data
into DevLake. In particular, teams that track production incidents as ClickUp
tasks have no way to feed those incidents into DevLake's DORA metrics, where they
would be correlated with GitLab deployments to compute reliability metrics such
as Change Failure Rate and Mean Time To Recovery.

This feature delivers a **ClickUp data-source plugin** (implemented in Python /
pydevlake) that collects ClickUp tasks and transforms them into DevLake **Issue**
and **Incident** domain entities. Users connect to ClickUp with a personal API token, select which parts of
their ClickUp workspace to sync, configure how tasks are classified, and run a
sync. Incidents produced by the plugin are consumed by DevLake's DORA framework
alongside GitLab deployments. The plugin is registered in the DevLake config-UI
so it can be set up entirely through the web interface.

## 1.2 Glossary

| Term | Definition |
| --- | --- |
| **ClickUp** | A SaaS work-management tool. Hierarchy: Workspace (a.k.a. Team) → Space → Folder → List → Task. |
| **Task** | The unit of work in ClickUp; the source record the plugin collects. |
| **Space** | A ClickUp grouping of Folders/Lists. |
| **Folder** | A ClickUp grouping of Lists within a Space. The unit a user selects to sync in this plugin. |
| **List** | A ClickUp collection of Tasks; the level the ClickUp `GET tasks` API queries. |
| **Tag** | A free-form label attached to a ClickUp task; used here to classify task type. |
| **Connection** | Stored credentials/configuration for one ClickUp workspace. |
| **Data scope** | A selectable source of data within a connection; here, a ClickUp Folder. |
| **Scope config** | Reusable transformation/classification rules applied to one or more data scopes. |
| **Issue** | DevLake domain entity representing a unit of tracked work. |
| **Incident** | DevLake domain entity representing a production problem; consumed by DORA. |
| **Board** | DevLake domain entity that groups issues/incidents; one per selected Folder. |
| **DORA** | DevOps Research and Assessment metrics (deployment frequency, lead time, change failure rate, MTTR). |
| **Incremental collection** | Re-syncing only data created or updated since the last successful sync rather than re-fetching everything. |

## 1.3 Requirements

### REQ-1 — Connect to ClickUp with a personal API token

**Type:** User story

**Statement:**
As a DevLake user, I want to connect DevLake to my ClickUp workspace using a
personal API token, so that DevLake can read my ClickUp tasks.

**Acceptance criteria:**
1. I can create a named ClickUp connection from the config-UI.
2. I can enter a ClickUp personal API token, which is stored securely with the
   connection.
3. I can optionally configure a proxy and an API rate limit for the connection.
4. I can test the connection; the system reports success only if it can reach
   ClickUp and read the authorized workspace with the provided token, and reports a
   clear error otherwise.
5. I can edit and delete a connection.

### REQ-2 — Select ClickUp Folders to sync

**Type:** User story

**Statement:**
As a DevLake user, I want to browse my ClickUp workspace and choose which Folders
to sync, so that I only import the data relevant to my project.

**Acceptance criteria:**
1. After connecting, I can browse the workspace's Spaces and Folders and select one
   or more Folders as data scopes.
2. Each selected Folder is treated as one DevLake data scope and maps to one DevLake
   Board.
3. When a Folder is synced, the plugin collects tasks from all Lists contained in
   that Folder.
4. I can add and remove Folders from a connection at any time.

### REQ-3 — Collect ClickUp tasks as DevLake Issues

**Type:** User story

**Statement:**
As a DevLake user, I want every ClickUp task in a selected Folder to be imported as
a DevLake Issue, so that I can analyze my team's work in DevLake.

**Acceptance criteria:**
1. For each task in a synced Folder, the system creates a corresponding DevLake Issue.
2. The following task attributes are mapped to the Issue: title, description, URL,
   issue key/identifier, creation date, last-updated date, resolution/closed date,
   creator, assignee, priority, and parent task (for subtasks).
3. The ClickUp status is mapped to a normalized DevLake status of `TODO`,
   `IN_PROGRESS`, or `DONE`, while the original ClickUp status name is preserved.
4. When a task is resolved/closed, the Issue's lead time is available (calculated
   from creation to resolution when not otherwise provided).
5. Each Issue is associated with the Board representing its Folder.

### REQ-4 — Classify task type, including incidents

**Type:** Use case

**Name:** Classify a ClickUp task into an issue type

**Primary actor:** DevLake user (via configuration); the system at sync time.

**Preconditions:**
- A connection exists and at least one Folder is selected.
- The user has defined a scope config for the relevant scope(s).

**Trigger:** A sync runs and processes a collected ClickUp task.

**Normal flow:**
1. The user configures, in the scope config, three regular-expression patterns —
   one each for the **INCIDENT**, **BUG**, and **REQUIREMENT** types — matched
   against a task's ClickUp tags.
2. During conversion, the system evaluates a task's tags against the patterns.
3. The system assigns the task type using fixed precedence: **INCIDENT > BUG >
   REQUIREMENT**. The first matching pattern (in that order) wins.
4. If no pattern matches, the system assigns the default type **REQUIREMENT**.
5. The assigned type is stored on the DevLake Issue.

**Alternative flows:**
- *4a. Patterns left empty:* If the user does not configure patterns, all tasks
  default to REQUIREMENT (no incidents are produced).

**Postconditions:**
- Every imported Issue has a type of INCIDENT, BUG, or REQUIREMENT.

**Functional requirements:**
1. Classification rules are part of the scope config so the same rules can be reused
   across scopes and edited without re-collecting raw data.
2. Pattern matching against tags is case-insensitive.

### REQ-5 — Produce DevLake Incidents for DORA

**Type:** User story

**Statement:**
As a DevLake user measuring DORA metrics, I want ClickUp tasks classified as
incidents to also become DevLake Incident entities, so that they feed DORA
reliability metrics together with my GitLab deployments.

**Acceptance criteria:**
1. Every Issue whose type is INCIDENT additionally produces a DevLake Incident
   entity.
2. The Incident carries the fields DORA needs, including status, creation date,
   resolution date, and lead time, plus title, description, URL, priority, creator,
   and assignee(s).
3. The Incident is associated with the Board representing its Folder.
4. Incidents produced by the plugin are usable by DevLake's DORA framework and can
   be correlated with deployments generated by the GitLab plugin (e.g. for Change
   Failure Rate and Mean Time To Recovery), with no ClickUp-specific changes
   required in DORA.

### REQ-6 — Incremental, reliable collection

**Type:** Use case

**Name:** Incrementally collect new and updated ClickUp tasks

**Primary actor:** The system (sync job).

**Preconditions:** A connection and at least one selected Folder exist.

**Trigger:** A scheduled or manual sync runs.

**Normal flow:**
1. The system requests tasks from ClickUp sorted by their "updated at" date.
2. On the first sync for a scope, the system collects all available tasks.
3. On subsequent syncs, the system collects only tasks updated after the most recent
   "updated at" date seen in the previous sync. Because a newly created task also has
   a recent "updated at" date, this single pass captures both newly created and
   subsequently edited tasks.
4. To avoid missing tasks changed near the previous cut-off, the system applies a
   one-day overlapping window (re-requests tasks from one day before the last seen
   "updated at" date).
5. Re-collected tasks that already exist are updated in place (upsert by task id)
   rather than duplicated, so edits to existing tasks are reflected in their Issue
   and Incident records.

**Alternative flows:**
- *2a. Full re-sync requested:* The user can trigger a full collection that ignores
  the stored incremental state and rebuilds the scope (see also Exceptions).

**Exceptions:**
- *Deleted tasks:* The ClickUp `GET tasks` API does not report deleted (or trashed)
  tasks, so incremental collection cannot observe a deletion. As a result, an Issue
  or Incident whose source task was deleted in ClickUp remains in DevLake until the
  user triggers a full re-sync that wipes and rebuilds the scope. This is a known,
  documented limitation (see Limitations).

**Postconditions:**
- The DevLake store reflects all ClickUp tasks created or updated up to the latest
  sync, with no duplicates and no gaps at the overlap boundary.

**Functional requirements:**
1. Incremental state (the last seen "updated at" date) is tracked per data scope.
2. Pagination across the ClickUp tasks API is handled transparently.

### REQ-7 — Configure data entities and transformation rules

**Type:** User story

**Statement:**
As a DevLake user, I want to configure, per scope, which data entities are produced
and the classification rules, so that I control what the plugin imports.

**Acceptance criteria:**
1. I can create a scope config that selects the relevant data entities (at minimum
   `TICKET`, and `CROSS`/incident-related entities as needed for DORA).
2. The scope config includes the INCIDENT/BUG/REQUIREMENT tag patterns from REQ-4.
3. I can apply a scope config to one or more selected Folders and change it later.

### REQ-8 — Configure and run the plugin from the config-UI

**Type:** User story

**Statement:**
As a DevLake user, I want to set up and operate the ClickUp plugin entirely from
the DevLake config-UI, so that I do not need to edit configuration files or call
APIs directly.

**Acceptance criteria:**
1. ClickUp appears as a selectable plugin in the config-UI, with a name and icon.
2. I can complete the full setup from the UI: create the connection (REQ-1), select
   Folders (REQ-2), define a scope config (REQ-7), and add the scopes to a project /
   blueprint.
3. The UI exposes the connection fields (name, personal API token, proxy, rate
   limit) and the scope-config fields (entities, incident/bug/requirement patterns).
4. I can run a sync (collection) and see its outcome through the standard DevLake UI.

## 1.4 Analysis models

**ClickUp → DevLake mapping**

| ClickUp concept | DevLake concept |
| --- | --- |
| Workspace / Team | Connection (token-authorized scope) |
| Space | (traversed; no direct entity) |
| Folder | Data scope → Board |
| List | (traversed; source of tasks) |
| Task | Issue (always); Incident (when type = INCIDENT) |
| Task tags | Type classification input (REQ-4) |
| Task status (`status.type`) | Normalized status TODO / IN_PROGRESS / DONE |
| Task assignee(s) | Issue assignee / Incident assignee |
| Task creator | Issue/Incident creator |

**Data flow**

```
ClickUp API (GET tasks, per List, sorted by updated_at, paginated, incremental + 1-day overlap)
        │  collect
        ▼
   Raw task records
        │  extract
        ▼
   ClickUp task (tool model)
        │  convert  ── classify type by tag regex (INCIDENT > BUG > REQUIREMENT, default REQUIREMENT)
        ├────────────► Issue (always)  ──► Board (per Folder)
        └────────────► Incident (when type = INCIDENT)
                              │
                              ▼
                         DORA framework  ◄── GitLab deployments
```

## Limitations

1. **Deleted tasks are not pruned incrementally.** Because the ClickUp `GET tasks`
   API cannot report deletions, Issues/Incidents for tasks deleted in ClickUp
   persist in DevLake until a full re-sync rebuilds the affected scope. For
   incidents this can temporarily distort DORA metrics (e.g. an inflated change
   failure rate or MTTR) until the next full re-sync. Real-time deletion handling
   via ClickUp `taskDeleted` webhooks is a possible future enhancement and is out of
   scope here.

## Open assumptions

The following are reasonable defaults applied where the initial requirements were
silent; confirm or adjust during technical design:

1. **Status mapping** uses ClickUp's native status type: `open` → `TODO`,
   custom/in-progress types → `IN_PROGRESS`, `closed`/`done` → `DONE`.
2. **Resolution date** is taken from the ClickUp task's closed/done date; lead time
   is computed from created date to resolution date when the task is resolved.
3. The plugin **collects only tasks** (and their inherent attributes); it does not
   collect comments, time tracking entries, or sprints in this scope.
4. **Issue key** is derived from the ClickUp task id (and/or custom task id when
   available).
