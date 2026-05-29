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
