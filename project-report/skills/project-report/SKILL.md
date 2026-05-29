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

For each distinct recording from Step A, run the type-appropriate show, then separately fetch its comments (in CLI v0.7.2 typed `show` commands do NOT accept `--all-comments`; comments must be fetched via the dedicated `comments list` endpoint). No cap, no sampling.

**Show the recording:**

| Recording type | Show command |
|---|---|
| todo | `basecamp todos show <id> --in <project_id> --md` |
| card | `basecamp cards show <id> --in <project_id> --md` |
| message | `basecamp messages show <id> --in <project_id> --md` |
| document | `basecamp show document <id> --in <project_id> --md` |
| upload | `basecamp files show <id> --in <project_id> --md` |
| schedule entry | `basecamp show schedule-entry <id> --in <project_id> --md` |
| check-in question | `basecamp checkins question <id> --in <project_id> --md` |
| comment | Already attached via the comments fetch below; do not refetch. |
| chat line | Covered by Step C below. |

If a recording type appears that is not in the table, fall back to `basecamp show <type> <id> --in <project_id> --md`. Generic `basecamp show` supports these types: `todo, todolist, message, comment, card, card-table, document, schedule-entry, checkin, forward, upload, vault, chat, line`. It does NOT support `question`: for that use `basecamp checkins question <id>` as shown above. If any single show call fails, log it and skip that recording; do NOT abort the report.

**Then fetch comments for every commentable recording above** (todo, card, message, document):

```bash
basecamp comments list <id> --in <project_id> --all --json
```

`--all` paginates through the full comment history. For check-in questions, fetch answers instead:

```bash
basecamp checkins answers <id> --in <project_id> --all --md
```

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

## Output template (strict)

Print this to the terminal verbatim, filling in the placeholders. No deviations from the structure. The whole report is a single markdown block.

```
# <Project name>, week of <YYYY-MM-DD> to <YYYY-MM-DD>

## TL;DR
<2-3 sentences. Must explicitly answer: is this project on track? Lead with the headline of what mattered this week.>

## Blockers & decisions needed
- <Theme, not ticket. What is stuck or waiting on a human call.>
- <Each bullet: short statement + a sentence of why.>
- <If nothing is blocked: a single bullet that says so.>

## Gaps Basecamp can't see
- <Honest callouts: "this looks decided in Slack", "no client confirmation visible", "X is assigned but no activity logged in 7d".>
- <If nothing to flag: "No obvious gaps this week.">
```

## Writing rules

These are non-negotiable. Apply them while drafting the report.

- **No Basecamp IDs in prose.** Themes only. A specific URL link is allowed when a single recording is the load-bearing reference, sparingly.
- **No per-todo enumeration.** If 8 todos all touch the same theme, that is one bullet.
- **TL;DR answers "is it on track" explicitly.** It is not just a summary.
- **Gaps section is required.** Write the "no obvious gaps" line rather than omitting the section.
- **No filler.** If a section has nothing real to say, say so in one line. Do not pad.
- **No em-dashes.** Use commas, periods, semicolons, or parentheses.
- **Language.** Default to English. If the user invoked the skill in Spanish (their triggering message contains Spanish), write the report in Spanish.
- **No meta-commentary.** Do not narrate what you are about to do or summarize what you just did. The output IS the report.

## Error handling

| Condition | Behavior |
|---|---|
| Argument missing | Ask the user for a Basecamp project URL or ID. Stop. |
| URL parse fails | Surface the CLI's error verbatim. Suggest checking the URL. Stop. |
| `command -v basecamp` fails | Print the exact "CLI not installed" message from the Preflight section. Stop. |
| `basecamp auth status` fails | Print the exact "not authenticated" message from the Preflight section. Stop. |
| Project not found (CLI exit 2) | "You don't appear to have access to this Basecamp project. Check the URL and your account with `basecamp accounts list`." Stop. |
| Forbidden (CLI exit 4) | Same message as Project not found. Stop. |
| Rate limit (CLI exit 5) | The CLI handles backoff automatically. If a call still fails, surface the message and stop. Do not retry blindly. |
| Single `show` call fails mid-walk | Log internally and skip that recording. Continue. Mention in the Gaps section if at least one was skipped: "Could not read N item(s) from Basecamp." |
| Empty week (no events in window) | Still produce a report. TL;DR: "No activity recorded in Basecamp this week." Gaps section calls out that work may have happened off-Basecamp. |

Do not invent error messages beyond these. If the situation is none of the above, surface the CLI's raw error and stop.
