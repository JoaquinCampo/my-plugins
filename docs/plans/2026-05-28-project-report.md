# project-report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Claude Code skill (`/project-report <url-or-id>`) that produces a high-level weekly Basecamp project status report (TL;DR, blockers, gaps), and install it via the `JoaquinCampo/my-plugins` marketplace.

**Architecture:** Prompt-only skill. One `SKILL.md` is the entire deliverable; it instructs the model to run a fixed activity-first sequence of `basecamp` CLI calls and synthesize a lean 3-section report. No scripts, no helpers. Installed as a local plugin folder inside `my-plugins`, registered in `marketplace.json`.

**Tech Stack:** Markdown, JSON (plugin manifests), `basecamp` CLI (37signals, v0.7.2), Claude Code skill loader.

**Repo:** `/Users/joaquincamponario/Documents/Personal/my-plugins` (branch `main`).

**Spec:** `docs/specs/2026-05-28-project-report-design.md` (committed at `4806d7e`). Refer to it for the canonical decisions. This plan turns it into ordered work.

**Verification model:** TDD does not map cleanly to a prose-only skill. Each task has a syntactic verification (JSON parses, file exists, frontmatter valid) plus a content checklist (spec requirements covered). The semantic verification ("does the report actually read well?") happens in Task 9 by running the skill against the Qdrant project.

**Important conventions to follow:**
- Spec is the source of truth. If anything below conflicts with the spec, the spec wins; fix the plan.
- No em-dashes anywhere in any artifact (user's standing style rule).
- No `Co-Authored-By:` trailers on commits (user's standing rule).
- Commits are small and per-task.

---

## File Structure

Files this plan creates or modifies in the `my-plugins` repo:

| File | Action | Responsibility |
|---|---|---|
| `project-report/.claude-plugin/plugin.json` | Create | Plugin manifest (name, version, author, skills path). |
| `project-report/skills/project-report/SKILL.md` | Create | The entire skill: frontmatter, preflight, playbook, output template, error handling. |
| `.claude-plugin/marketplace.json` | Modify | Add a `project-report` entry to the `plugins` array. |
| `docs/plans/2026-05-28-project-report.md` | Already created | This plan. |

No source code files. No test files. Verification is by inspection and by invoking the skill end to end.

---

## Task 1: Scaffold the plugin directory and `plugin.json`

**Files:**
- Create: `project-report/.claude-plugin/plugin.json`
- Create: `project-report/skills/project-report/` (empty directory placeholder; will host `SKILL.md` in Task 3)

- [ ] **Step 1: Create the directory tree**

Run:
```bash
cd /Users/joaquincamponario/Documents/Personal/my-plugins
mkdir -p project-report/.claude-plugin
mkdir -p project-report/skills/project-report
```

Verify:
```bash
ls project-report/.claude-plugin project-report/skills/project-report
```
Expected: both directories exist; both currently empty.

- [ ] **Step 2: Write `plugin.json`**

Create `project-report/.claude-plugin/plugin.json` with exactly this content:

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

- [ ] **Step 3: Verify the JSON parses**

Run:
```bash
cat project-report/.claude-plugin/plugin.json | python3 -m json.tool > /dev/null && echo OK
```
Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add project-report/.claude-plugin/plugin.json
git commit -m "feat(project-report): scaffold plugin manifest"
```

---

## Task 2: Register the plugin in `marketplace.json`

**Files:**
- Modify: `.claude-plugin/marketplace.json` (add one entry to the `plugins` array).

- [ ] **Step 1: Read the current `marketplace.json`**

Run:
```bash
cat .claude-plugin/marketplace.json
```
Confirm: the file has a top-level `plugins` array containing entries like `browser-use`, `humanizer`, `pr-review`, `apple-dev`, etc. Local-source entries use the shape `"source": "./<dir>"`. URL-source entries use `"source": { "source": "url", "url": "..." }`. The new entry is a local source.

- [ ] **Step 2: Add the `project-report` entry**

Insert this object as a new element of the `plugins` array. Place it after the existing `apple-dev` entry (keeps locally-sourced plugins together, mirroring current ordering):

```json
{
  "name": "project-report",
  "source": "./project-report",
  "description": "Generate a high-level weekly status report for a Basecamp project. Activity-first via the basecamp CLI; outputs a lean 3-section markdown report (TL;DR, blockers, gaps).",
  "version": "0.1.0",
  "keywords": ["basecamp", "report", "status", "weekly", "project-management"]
}
```

Make sure to add a comma after the previous entry's closing brace.

- [ ] **Step 3: Verify the JSON parses and the entry is present**

Run:
```bash
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null && echo OK
python3 -c "import json; m=json.load(open('.claude-plugin/marketplace.json')); names=[p['name'] for p in m['plugins']]; assert 'project-report' in names, names; print('found:', names)"
```
Expected: `OK` then a printed list containing `project-report`.

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat(marketplace): register project-report plugin"
```

---

## Task 3: Write the SKILL.md frontmatter and headline

**Files:**
- Create: `project-report/skills/project-report/SKILL.md`

This task writes the frontmatter only. Subsequent tasks append sections. Splitting per section keeps commits and reviews bite-sized.

- [ ] **Step 1: Write the frontmatter**

Create `project-report/skills/project-report/SKILL.md` with this content (do not add anything else yet):

```markdown
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

# /project-report — High-level Basecamp weekly report

Generate a lean 3-section weekly status report for a Basecamp project, written for a reader who is NOT in the project's daily work. Last 7 days only. Read-only: this skill never posts to Basecamp.
```

- [ ] **Step 2: Validate the YAML frontmatter**

Run:
```bash
python3 - <<'PY'
import sys, yaml
text = open('project-report/skills/project-report/SKILL.md').read()
assert text.startswith('---\n'), 'missing opening ---'
end = text.find('\n---\n', 4)
assert end != -1, 'missing closing ---'
meta = yaml.safe_load(text[4:end])
assert meta['name'] == 'project-report', meta
assert meta.get('invocable') is True, meta
assert '/project-report' in meta['triggers'], meta
print('frontmatter OK')
PY
```
Expected: `frontmatter OK`.

- [ ] **Step 3: Commit**

```bash
git add project-report/skills/project-report/SKILL.md
git commit -m "feat(project-report): SKILL.md frontmatter and intro"
```

---

## Task 4: Append the "When to use" and "Preflight checks" sections

**Files:**
- Modify: `project-report/skills/project-report/SKILL.md` (append).

- [ ] **Step 1: Append both sections**

Append the following to `SKILL.md`:

```markdown

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
```

- [ ] **Step 2: Verify content**

Run:
```bash
grep -c 'https://github.com/basecamp/basecamp-cli' project-report/skills/project-report/SKILL.md
grep -c 'basecamp auth login' project-report/skills/project-report/SKILL.md
grep -c 'command -v basecamp' project-report/skills/project-report/SKILL.md
```
Expected: `2`, `1`, `1` (the install link appears in both preflight failure messages).

- [ ] **Step 3: Commit**

```bash
git add project-report/skills/project-report/SKILL.md
git commit -m "feat(project-report): preflight checks for basecamp CLI"
```

---

## Task 5: Append the "Resolve the project" section

**Files:**
- Modify: `project-report/skills/project-report/SKILL.md` (append).

- [ ] **Step 1: Append the section**

Append to `SKILL.md`:

```markdown

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

Hold onto the project name. The report title is `# <Project name> — week of <start_date> to <end_date>`, where `<end_date>` is today (UTC date) and `<start_date>` is 6 days before (so the window is exactly 7 calendar days inclusive).
```

- [ ] **Step 2: Verify content**

Run:
```bash
grep -c 'basecamp url parse' project-report/skills/project-report/SKILL.md
grep -c 'basecamp projects show' project-report/skills/project-report/SKILL.md
```
Expected: at least `1` each.

- [ ] **Step 3: Commit**

```bash
git add project-report/skills/project-report/SKILL.md
git commit -m "feat(project-report): project resolution from URL or ID"
```

---

## Task 6: Append the "Data-gathering playbook" section

**Files:**
- Modify: `project-report/skills/project-report/SKILL.md` (append).

This is the largest single section. One task, one commit; the section is internally coherent.

- [ ] **Step 1: Append the playbook**

Append to `SKILL.md`:

````markdown

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
````

- [ ] **Step 2: Verify all six basecamp command families are referenced**

Run:
```bash
for cmd in 'basecamp timeline' 'basecamp todos show' 'basecamp cards show' 'basecamp messages show' 'basecamp chat list' 'basecamp chat messages' 'basecamp todos list' 'basecamp cards columns' 'basecamp cards list'; do
  grep -q -- "$cmd" project-report/skills/project-report/SKILL.md && echo "OK: $cmd" || echo "MISSING: $cmd"
done
```
Expected: every line starts with `OK:`. If any says `MISSING:`, re-check the playbook against the spec section 4.

- [ ] **Step 3: Commit**

```bash
git add project-report/skills/project-report/SKILL.md
git commit -m "feat(project-report): activity-first data-gathering playbook"
```

---

## Task 7: Append the "Output template" and "Writing rules" sections

**Files:**
- Modify: `project-report/skills/project-report/SKILL.md` (append).

- [ ] **Step 1: Append both sections**

Append to `SKILL.md`:

````markdown

## Output template (strict)

Print this to the terminal verbatim, filling in the placeholders. No deviations from the structure. The whole report is a single fenced or unfenced markdown block.

```
# <Project name> — week of <YYYY-MM-DD> to <YYYY-MM-DD>

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
````

- [ ] **Step 2: Verify content**

Run:
```bash
grep -q '## TL;DR' project-report/skills/project-report/SKILL.md && echo "OK: TL;DR header"
grep -q "Gaps Basecamp can't see" project-report/skills/project-report/SKILL.md && echo "OK: Gaps header"
grep -q 'No Basecamp IDs in prose' project-report/skills/project-report/SKILL.md && echo "OK: IDs rule"
grep -q 'No em-dashes' project-report/skills/project-report/SKILL.md && echo "OK: em-dash rule"
```
Expected: four `OK:` lines.

- [ ] **Step 3: Commit**

```bash
git add project-report/skills/project-report/SKILL.md
git commit -m "feat(project-report): output template and writing rules"
```

---

## Task 8: Append the "Error handling" section

**Files:**
- Modify: `project-report/skills/project-report/SKILL.md` (append).

- [ ] **Step 1: Append the section**

Append to `SKILL.md`:

```markdown

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
```

- [ ] **Step 2: Verify content**

Run:
```bash
grep -c '^| ' project-report/skills/project-report/SKILL.md
```
Expected: the count includes 11+ table rows (some are in the playbook, some in error handling). At minimum 18 rows total across all tables.

```bash
grep -q 'basecamp accounts list' project-report/skills/project-report/SKILL.md && echo "OK: accounts-list hint"
grep -q 'Empty week' project-report/skills/project-report/SKILL.md && echo "OK: empty-week case"
```
Expected: two `OK:` lines.

- [ ] **Step 3: Commit**

```bash
git add project-report/skills/project-report/SKILL.md
git commit -m "feat(project-report): error handling table"
```

---

## Task 9: End-to-end manual test against the Qdrant project

This task does NOT change any files. It is the semantic verification: does the skill produce a sane report on a real project?

**Test target:** `https://3.basecamp.com/4988110/projects/44862682` (Qdrant project; chosen at design time by the user).

- [ ] **Step 1: Reload the marketplace so the new plugin is registered**

In Claude Code, run:
```
/plugin marketplace refresh my-plugins
```
or restart the session. After the refresh, the skill `project-report` should be listed when you next start a session in this directory.

Verify by running (in a new session if needed):
```
/help
```
and confirming `/project-report` appears, or that the model can see the skill via the Skill tool listing.

- [ ] **Step 2: Invoke the skill on the Qdrant project**

```
/project-report https://3.basecamp.com/4988110/projects/44862682
```

- [ ] **Step 3: Inspect the output against this rubric**

Check each item:
- [ ] Title line uses the actual project name and shows a 7-day window ending today.
- [ ] TL;DR is 2-3 sentences and explicitly states whether the project is on track.
- [ ] Blockers section has bullets that read as themes (not "todo #123 done"). If nothing is blocked, exactly one bullet that says so.
- [ ] Gaps section exists. Either has callouts or the literal line "No obvious gaps this week."
- [ ] No em-dashes anywhere in the report.
- [ ] No Basecamp IDs in the prose (URLs are OK, sparingly).
- [ ] No filler, no meta-commentary ("I'll now write...").
- [ ] If the project was quiet, TL;DR says so honestly rather than inventing activity.

- [ ] **Step 4: Note observations**

Write down (in a scratch file or chat note) any rubric items the report failed. These feed Task 10.

If every rubric item passes and Agustín-style sanity check looks right, skip Task 10 and proceed to Task 11.

---

## Task 10: Iterate on `SKILL.md` based on Task 9 observations

Only run this task if Task 9 found issues. If it didn't, mark this task complete with the note "no iteration needed" and move on.

**Files:**
- Modify: `project-report/skills/project-report/SKILL.md` (targeted edits).

- [ ] **Step 1: For each rubric failure, identify the SKILL.md section that drives it**

Use this mapping:

| Symptom | Section to edit |
|---|---|
| TL;DR is a summary, not an "on track" answer | Writing rules: tighten the "TL;DR answers 'is it on track' explicitly" bullet. |
| Bullets enumerate todos instead of themes | Writing rules: tighten the "No per-todo enumeration" bullet with an example. |
| Gaps section missing | Writing rules + Output template: explicitly state "Gaps section is required." |
| Em-dashes appear | Writing rules: re-state "No em-dashes" and add example replacements. |
| Filler/meta-commentary | Writing rules: tighten "No meta-commentary". |
| Quiet week reports invent activity | Error handling: tighten the Empty week row's wording. |
| Wrong data missing | Data-gathering playbook: add the missing command or filter. |

- [ ] **Step 2: Apply the smallest possible edit**

Prefer adding a one-line clarification or a short concrete example over rewriting a section.

- [ ] **Step 3: Re-run the test**

Repeat Task 9 Step 2 and Step 3.

- [ ] **Step 4: Commit each iteration**

One commit per round of iteration:
```bash
git add project-report/skills/project-report/SKILL.md
git commit -m "fix(project-report): <what was tightened>"
```

Stop iterating once the rubric passes or after 3 rounds (whichever comes first). If 3 rounds do not converge, flag it for design review rather than tweaking further.

---

## Task 11: Final commit summary and bump check

**Files:**
- No additional file changes. This task validates the repo state and surfaces any cleanup.

- [ ] **Step 1: Confirm the working tree is clean and the branch is ahead of origin**

Run:
```bash
git status
git log origin/main..HEAD --oneline
```
Expected: working tree clean. The log shows the commits from this plan (Tasks 1, 2, 3, 4, 5, 6, 7, 8, and any Task 10 iterations).

- [ ] **Step 2: Confirm the plugin is discoverable**

Run:
```bash
ls project-report/.claude-plugin/plugin.json project-report/skills/project-report/SKILL.md
python3 -m json.tool .claude-plugin/marketplace.json | grep -A2 '"project-report"'
```
Expected: both files exist; the marketplace entry is printed.

- [ ] **Step 3: Decide on push**

This plan does NOT push. Ask the user whether to push `origin/main` once the plan is fully executed. Pushing makes the plugin installable for anyone subscribed to `JoaquinCampo/my-plugins`.

- [ ] **Step 4: Mark plan complete**

Add a final line to this plan file:
```markdown

## Status: complete (YYYY-MM-DD)
```
(Replace YYYY-MM-DD with the date.) Then:
```bash
git add docs/plans/2026-05-28-project-report.md
git commit -m "docs: mark project-report plan complete"
```

---

## Out of scope (do NOT do as part of this plan)

These are explicitly deferred per the spec. If the urge arises during implementation, resist and capture as future work instead:

- Slack context integration.
- Forward-looking / roadmap framing.
- Posting reports back to Basecamp.
- Comparing to previous reports / running diffs.
- `--days` or other flags for custom windows.
- Multi-project digests.
- Onboarding doc for the skill itself (separate deliverable Agustín requested).
- Templates or per-project customization.
- A standalone GitHub repo for this plugin (it lives in `my-plugins` for v1).
