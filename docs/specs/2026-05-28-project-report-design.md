# project-report: design spec

Date: 2026-05-28
Status: design approved, ready for plan

## Purpose

A Claude Code skill that generates a high-level weekly status report for a Basecamp project. Reader is a lead or outsider (not in the project's daily work) who wants a fast, honest read on whether the project is on track, what's stuck, and what Basecamp does not capture.

The trigger for this spec is feedback on a previous Parsan.ai report (produced by ad-hoc tooling): "esta bastante bien, para mi se podria hacer desde un punto de vista mas high level, asi no es necesario estar tan metido en el proyecto para entender". Build a v1 lean enough to ship, then iterate.

## Decisions (locked)

| Decision | Choice | Why |
|---|---|---|
| Audience | Lead / outsider | Matches Agustín feedback. Not for someone already deep in the project. |
| Time horizon | Last 7 days, retrospective only | Simplest v1. Roadmap framing deferred. |
| Output venue | Markdown printed in terminal | Skill prints, user copy-pastes wherever (Basecamp, Slack, doc). No posting permissions or draft/publish logic. |
| Shape | 3 sections | TL;DR, Blockers & decisions needed, Gaps Basecamp can't see. |
| Invocation | `/project-report <url-or-id>` | Dedicated slash command. Easy to remember. Clean separation from `/basecamp`. |
| Location | Personal marketplace `JoaquinCampo/my-plugins` | Local plugin folder, registered in marketplace.json. Same shape as `browser-use`, `humanizer`. |
| Approach | Prompt-only skill (SKILL.md as playbook) | Fastest to iterate on prompt while we tune "high-level". Add helper scripts only if the prompt feels brittle. |
| Data collection | Activity-first via timeline, no caps | Pull all touched recordings, all chats with activity, all comments in window. Fidelity over speed. |

## File layout

```
my-plugins/
├── .claude-plugin/
│   └── marketplace.json        # add project-report entry
├── project-report/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   └── skills/
│       └── project-report/
│           └── SKILL.md
└── docs/specs/2026-05-28-project-report-design.md   # this file
```

No version subfolder; flat layout matches the existing local plugins in `my-plugins`. Version lives in `plugin.json`.

### marketplace.json entry

Add to the `plugins` array:

```json
{
  "name": "project-report",
  "source": "./project-report",
  "description": "Generate a high-level weekly status report for a Basecamp project. Activity-first via the basecamp CLI; outputs a lean 3-section markdown report (TL;DR, blockers, gaps).",
  "version": "0.1.0",
  "keywords": ["basecamp", "report", "status", "weekly", "project-management"]
}
```

### plugin.json

```json
{
  "name": "project-report",
  "version": "0.1.0",
  "description": "High-level weekly Basecamp project status report.",
  "author": { "name": "Joaquin Campo" },
  "license": "MIT",
  "keywords": ["basecamp", "report", "status", "weekly"],
  "skills": "./skills/"
}
```

## SKILL.md structure

Four parts.

### 1. Frontmatter

```yaml
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
```

### 2. Preflight checks

Before any data calls, the model runs:

1. `command -v basecamp >/dev/null 2>&1`. If exit code is non-zero, stop with this exact message and do nothing else:

   > Basecamp CLI not installed. Install and configure it from https://github.com/basecamp/basecamp-cli, then re-run `/project-report`.

2. `basecamp auth status`. If not authenticated, stop with:

   > Basecamp CLI is installed but not authenticated. Run `basecamp auth login` (full setup at https://github.com/basecamp/basecamp-cli), then re-run `/project-report`.

`basecamp doctor --json` is intentionally skipped for v1 to keep latency low.

### 3. Argument handling

- Argument is a Basecamp project URL → run `basecamp url parse "<url>" --json` to extract `project_id`.
- Argument is a bare numeric ID → use it directly as `project_id`.
- Argument missing → ask the user for a URL or ID. Do NOT guess from cwd or `.basecamp/config.json`.
- URL parse fails → surface the CLI's error verbatim and stop.

### 4. Data-gathering playbook

Activity-first. The timeline is the index; deep-dives only happen on recordings that moved.

**Step A. Project header**
```
basecamp projects show <project_id> --md
```
Use the name and (if present) description for the report header.

**Step B. Pull the timeline (the index)**
```
basecamp timeline --in <project_id> --limit 500 --json
```
Filter events client-side to the last 7 days. From this:
- Collect distinct `(recording_type, recording_id)` pairs touched in window.
- Note creators/actors per event (used later to spot ownership).

**Step C. Deep-dive on every touched recording**

For each distinct recording from B, run the type-appropriate show, then fetch comments separately. (In CLI v0.7.2 typed show commands do NOT accept `--all-comments`; comments must be fetched via the dedicated `comments list` endpoint.) No cap, no sampling.

| Type | Show command |
|---|---|
| todo | `basecamp todos show <id> --in <project_id> --md` |
| card | `basecamp cards show <id> --in <project_id> --md` |
| message | `basecamp messages show <id> --in <project_id> --md` |
| document | `basecamp show document <id> --in <project_id> --md` |
| upload | `basecamp files show <id> --in <project_id> --md` |
| schedule entry | `basecamp show schedule-entry <id> --in <project_id> --md` |
| check-in question | `basecamp checkins question <id> --in <project_id> --md` |
| comment | attached via comments fetch below; do not refetch |
| chat line | covered by step D below |

Then for every commentable recording, fetch comments:
```bash
basecamp comments list <id> --in <project_id> --all --json
```

For check-in questions, fetch answers instead:
```bash
basecamp checkins answers <id> --in <project_id> --all --md
```

If a recording type appears that isn't listed, fall back to `basecamp show <type> <id> --in <project_id> --md`. The generic show supports: `todo, todolist, message, comment, card, card-table, document, schedule-entry, checkin, forward, upload, vault, chat, line`. It does NOT support `question`; route those through `basecamp checkins question` as above. If any single show call fails, log and skip that recording, do not abort.

**Step D. Walk every chat room with activity**
```
basecamp chat list --in <project_id> --json
```
This returns all chat rooms (Dev Chat, side rooms, campfires). For each room returned, fetch its recent messages:
```
basecamp chat messages --in <project_id> --room <room_id> --limit 200 --md
```
(`--room` is needed only when the project has multiple rooms; safe to always pass it.) Filter to last 7 days client-side. If a room had zero activity in window, skip it. Otherwise include every message in window.

**Step E. Context the timeline does not catch**

These are signals where "no activity" is itself the signal (stuck work).

- Open todos:
  ```
  basecamp todos list --in <project_id> --status incomplete --all --md
  ```
  Look for: overdue, due in next 7 days, assignments to people who had no timeline activity this week.

- Cards in flight: if the project has card tables, list columns and active cards.
  ```
  basecamp cards columns --in <project_id> --json
  basecamp cards list --in <project_id> --card-table <id> --md
  ```
  Skip if the project has no card tables.

**Step F. Synthesize**

The model now has: project metadata, weekly activity index, full content + comments for everything touched, full chat transcripts in window, open and stuck work. Write the 3-section report per the template below.

### 5. Output template (strict)

```
# <Project name> — week of <YYYY-MM-DD> to <YYYY-MM-DD>

## TL;DR
<2-3 sentences. Must explicitly answer: is this project on track? Lead with the
headline of what mattered this week.>

## Blockers & decisions needed
- <Theme, not ticket. What is stuck or waiting on a human call.>
- <Each bullet: short statement + a sentence of why.>
- <If nothing is blocked: a single bullet that says so.>

## Gaps Basecamp can't see
- <Honest callouts: "this looks decided in Slack", "no client confirmation
  visible", "X is assigned but no activity logged in 7d".>
- <If nothing to flag: "No obvious gaps this week.">
```

### 6. Writing rules (baked into the prompt)

- **No Basecamp IDs in prose.** Themes only. A specific URL link is allowed when a single recording is the load-bearing reference, sparingly.
- **No per-todo enumeration.** If 8 todos all touch the same theme, that is one bullet.
- **TL;DR answers "is it on track" explicitly.** It is not just a summary.
- **Gaps section is required.** Write the "no obvious gaps" line rather than omitting the section.
- **No filler.** If a section has nothing real to say, say so in one line. Do not pad.
- **No em-dashes.** Use commas, periods, semicolons, or parentheses.
- **Language.** Default to English. If the user invoked the skill in Spanish (their message that triggered it contains Spanish), write the report in Spanish.

## Error handling

| Condition | Behavior |
|---|---|
| No argument | Ask the user for a Basecamp project URL or ID. |
| URL parse fails | Surface the CLI error verbatim. Suggest checking the URL. Stop. |
| CLI missing | Preflight check 1. Point to https://github.com/basecamp/basecamp-cli. |
| Not authenticated | Preflight check 2. Tell user to run `basecamp auth login`. |
| Project not found (exit 2) | "You don't appear to have access to this Basecamp project. Check the URL and your account with `basecamp accounts list`." |
| Forbidden (exit 4) | Same as above. |
| Rate limit (exit 5) | The CLI handles backoff. If it still fails, surface message and stop. No blind retries. |
| Empty week | Still produce a report. TL;DR says "No activity recorded in Basecamp this week." Gaps section calls out that work may have happened elsewhere. |
| Single recording show fails | Log and skip. Do not abort the whole report. |

## Out of scope for v1

These are deferred deliberately and named here so future-me does not re-litigate:

- Slack context (separate v2 feature, requires Slack MCP).
- Forward-looking / roadmap / objectives framing.
- Posting the report back to Basecamp.
- Comparing to previous report ("changes since last report").
- Custom time windows or `--days` flag.
- Multi-project digests.
- Standalone onboarding doc for the skill (separate deliverable Agustín requested).
- Templates / customization per project.

## Test target

Qdrant project at https://3.basecamp.com/4988110/projects/44862682. First real-world run will be against this project; Agustín will sanity-check the output against his ground truth.

## Open questions for implementation

None blocking. The plan can proceed from this spec.
