---
name: project-report
description: |
  Generate a high-level weekly status report for a Basecamp project. Reader is a
  lead or outsider, not someone in the project's daily work. Outputs a lean
  3-section markdown report (TL;DR, Blockers & decisions needed, Gaps Basecamp
  can't see). Last 7 days only, retrospective. Requires the basecamp CLI
  installed and authenticated.
triggers:
  - /project-report
  - project-report
  - weekly basecamp report
  - basecamp project report
  - basecamp weekly status
  - high-level basecamp report
  - status report for basecamp
invocable: true
argument-hint: "<basecamp-project-url-or-id>"
---

# /project-report, High-level Basecamp weekly report

Generate a lean 3-section weekly status report for a Basecamp project, written for a reader who is NOT in the project's daily work. Last 7 days only. Read-only: this skill never posts to Basecamp.

## When to use

Invoke when the user says `/project-report`, asks for a Basecamp weekly status, or asks for a high-level project read from Basecamp. Argument is a Basecamp project URL or numeric project ID. If the user gave no argument, ask them for one; do NOT guess from cwd or `.basecamp/config.json`.

## Preflight checks

Run BOTH checks before any data calls. If either fails, stop immediately, print the exact message below, and do not run any other `basecamp` command.

**Check 1: CLI installed**

```bash
command -v basecamp >/dev/null 2>&1
```

If the exit code is non-zero, stop with this exact message:

> Basecamp CLI not installed. Install and configure it from https://github.com/basecamp/basecamp-cli, then re-run `/project-report`.

**Check 2: Authenticated**

```bash
basecamp auth status
```

If this fails (non-zero exit or output indicates unauthenticated), stop with this exact message:

> Basecamp CLI is installed but not authenticated. Run `basecamp auth login` (full setup at https://github.com/basecamp/basecamp-cli), then re-run `/project-report`.

Do NOT run `basecamp doctor` in v1. The two checks above are sufficient and keep latency low.

## Resolve the project

Given the invocation argument:

- **Basecamp URL** (e.g., `https://3.basecamp.com/<account>/projects/<id>`): run
  ```bash
  basecamp url parse "<url>" --json
  ```
  Extract `project_id` from the response. If the parse fails, surface the CLI error verbatim to the user and stop.

- **Bare numeric ID**: use it directly as `project_id`. No parse step needed.

- **Missing argument**: ask the user for a Basecamp project URL or ID. Do not guess.

Fetch the project header for the report title:

```bash
basecamp projects show <project_id> --md
```

Hold onto the project name. The report title is `# <Project name>, week of <start_date> to <end_date>`, where `<end_date>` is today (UTC date) and `<start_date>` is 6 days before (so the window is exactly 7 calendar days inclusive).

## Data-gathering playbook

Activity-first. The timeline is the index of what moved this week; deep-dives only happen on recordings that moved. No caps: pull every touched recording, every chat with activity, every comment in window. Fidelity over speed.

### Step A. Pull the timeline (the index)

```bash
basecamp timeline --in <project_id> --limit 500 --json
```

Filter the returned events client-side to the last 7 days (inclusive: `<start_date>` 00:00 UTC through `<end_date>` 23:59 UTC). From the filtered events:

- Collect distinct `(recording_type, recording_id)` pairs.
- Note actors per event (used later to spot ownership and "assigned but silent" cases).

### Step B. Deep-dive on every touched recording

For each distinct recording from Step A, run the type-appropriate show. No cap, no sampling. Use `--all-comments` on every commentable type to fetch the full comment history (default is capped at 100).

| Recording type | Command |
|---|---|
| todo | `basecamp todos show <id> --all-comments --json` |
| card | `basecamp cards show <id> --all-comments --json` |
| message | `basecamp messages show <id> --all-comments --json` |
| document | `basecamp show document <id> --all-comments --json` |
| upload | `basecamp files show <id> --in <project_id> --json` |
| schedule entry | `basecamp schedule show <id> --in <project_id> --json` |
| comment | Already attached to its parent recording above; do not refetch. |
| chat line | Covered by Step C below. |

If a recording type appears that is not in the table, fall back to `basecamp show <type> <id> --in <project_id> --json`. If any single `show` call fails, log it and skip that recording; do NOT abort the report.

### Step C. Walk every chat room with activity

List all chat rooms in the project (Dev Chat, side rooms, campfires):

```bash
basecamp chat list --in <project_id> --json
```

For each room returned, fetch its recent messages:

```bash
basecamp chat messages --in <project_id> --room <room_id> --limit 200 --md
```

(`--room` is needed only when the project has multiple rooms, but passing it always is safe and explicit.) Filter client-side to the last 7 days. If a room had zero activity in window, skip it entirely. Otherwise include every message in window. Do not summarize at gather time; the model summarizes during synthesis.

### Step D. Context the timeline does not catch

Pull these regardless of timeline activity, because "no activity" is itself a signal (stuck work).

Open todos:

```bash
basecamp todos list --in <project_id> --status incomplete --all --md
```

Look for: overdue items; items due in the next 7 days; items assigned to people who had no timeline activity this week.

Cards in flight (only if the project has card tables):

```bash
basecamp cards columns --in <project_id> --json
```

Then for each card table returned:

```bash
basecamp cards list --in <project_id> --card-table <table_id> --md
```

If the project has no card tables, skip this entirely.

### Step E. Synthesize

You now have: project header, weekly activity index, full content + comments for every touched recording, full chat transcripts in window, open and potentially stuck work. Write the 3-section report per the template in the next section.
