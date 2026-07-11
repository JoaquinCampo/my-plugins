---
name: kanban-process
description: Use when the user asks to use a kanban process, track development work on a GitHub board, work from the agent board, proactively track tasks and deferred findings, runs `/kanban-process`, or when the project is already configured to use this workflow.
---

# Kanban Process

Use GitHub Issues as durable task cards and a dedicated GitHub Project as the kanban board. Keep the board accurate throughout development without waiting for the user to request every update.

## Activation and authorization

Treat an explicit request to set up or use the kanban process as authorization for the current repository to:

- create one dedicated GitHub Project when none is configured;
- create and update relevant GitHub Issues;
- add those issues to the Project;
- move cards between workflow statuses; and
- close completed issues after human approval.

Do not infer authorization for pushes, pull requests, destructive operations, unrelated issues, or other shared-state changes.

When repository instructions already require this workflow or the repository contains `.github/kanban-process.yml`, activate it automatically. Otherwise, ask before the first shared-state mutation.

## Board model

An Issue contains the task's durable context. The Project supplies the board and its single-select `Status` field.

Use these statuses:

1. `Backlog` — valid work captured for later.
2. `Ready` — sufficiently defined and unblocked.
3. `In progress` — actively being worked on.
4. `Needs human review` — agent work is complete and a human owns the next action.
5. `Blocked` — work cannot continue because of a concrete dependency.
6. `Done` — accepted work; close the associated Issue.

Use labels for type, area, or priority, not workflow status.

## First use: initialize the board

1. Confirm the current directory belongs to a GitHub repository and `gh auth status` succeeds.
2. Search for `.github/kanban-process.yml`. If present, validate and reuse its Project.
3. If configuration is absent, inspect the repository owner and search that owner's Projects for a dedicated board for this repository. Reuse an unambiguous match rather than creating a duplicate.
4. If no board exists and setup is authorized, create a GitHub Project named `<repository> — Agent Board` under the repository owner.
5. Link the Project to the repository so it appears in the repository's **Projects** view. A user- or organization-owned Project is not automatically linked when created.
6. Make the Project's primary/default view a board grouped by `Status`. Do not leave the default table as the main workflow view. GitHub's API may not expose Project view layout management; when it does not, create the Project from a configured board template or ask the user to perform this one-time UI step rather than claiming setup is complete.
7. Configure the Project's `Status` field with the six statuses above. Preserve compatible existing options and avoid destructive field replacement.
8. Save the stable Project identity in `.github/kanban-process.yml`:

```yaml
owner: OWNER
project_number: 12
project_url: https://github.com/orgs/OWNER/projects/12
status_field: Status
```

9. Verify that an Issue can be added and moved. Do not create a dummy Issue solely for verification.

GitHub Projects may belong to a user or organization and may require additional scopes such as `project`. If permissions are missing, explain the exact failing command or scope and pause setup. Do not silently fall back to a different board.

## Start of work

1. Read the configured Project and current Issues before creating anything.
2. Find the Issue representing the requested work. Search titles and bodies to avoid duplicates.
3. If no Issue exists and the work is durable, create one with the requested outcome and acceptance criteria, then add it to the Project.
4. Move the selected card to `In progress` when implementation begins.
5. Keep one primary active card unless parallel work is genuinely underway.

Small conversational requests do not always need an Issue. Create cards for work worth preserving across sessions or handing to another person or agent.

## Work proactively

Maintain the board as part of the development loop:

- Update a card when its scope, acceptance criteria, or ownership materially changes.
- Move a card immediately when its real state changes; do not batch status maintenance until the end.
- Before stopping or switching tasks, leave the active card in an accurate status with enough context to resume.
- Check the Project before asking what to work on next. Prefer a `Ready` card whose prerequisites are satisfied.
- Never claim a card is complete solely because code was written. Verify its acceptance criteria first.

## Capture deferred findings

When work reveals something outside the current scope, capture it rather than expanding the active task or losing the finding.

Create a `Backlog` Issue only when the finding is:

- concrete and supported by observed code, behavior, or test output;
- actionable with a plausible desired outcome;
- outside the current task's acceptance criteria;
- likely to matter after the current session; and
- not already represented by an existing Issue.

Before creating it, search open Issues and Project items for duplicates. If one exists, add only genuinely useful missing context.

A deferred Issue should contain:

```markdown
## Context

Discovered while working on #<issue>. Describe the observed problem and why it matters.

## Evidence

Reference relevant files, behavior, logs, or tests. Separate observations from assumptions.

## Desired outcome

Describe the result, not an unnecessarily detailed implementation.

## Acceptance criteria

- A concrete, verifiable completion condition.
```

Do not create cards for passing thoughts, speculative redesigns, temporary debugging steps, work already fixed by the current change, or trivial cleanup that belongs in the active task.

## Blocked work

Move a card to `Blocked` only when work cannot continue. Add a concise comment or body update stating:

- what is blocked;
- the concrete reason;
- the dependency or decision required; and
- the action that will unblock it.

Link the blocking Issue when one exists. `Blocked` means implementation cannot proceed; it is not a substitute for human review.

## Human review handoff

Move work to `Needs human review` when agent work is complete but a human must validate, approve, choose, grant access, or authorize a consequential action. Leave a handoff containing:

```markdown
## Ready for human review

### Completed

- What changed.

### Verification

- Commands or checks run and their results.

### Human action needed

- The exact decision, validation, or approval required.
```

Do not use this status merely because coding stopped. If repository policy requires human approval for all completed work, always use it before `Done`.

After human feedback:

- approved: move to `Done` and close the Issue;
- changes requested: move to `In progress` and record the requested outcome;
- new dependency: move to `Blocked` with the reason.

## Completion and reporting

At the end of a work session:

1. Reconcile the active Issue with the actual implementation and verification state.
2. Capture only qualifying deferred findings.
3. Move every touched card to its truthful status.
4. Report the active, newly created, blocked, and human-review Issues with links.
5. Keep the summary brief; the Issues hold the durable details.

Never delete a Project, field, status, Issue, or user-authored content as part of normal board maintenance.
