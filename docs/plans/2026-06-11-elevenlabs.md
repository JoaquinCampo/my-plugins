# elevenlabs Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Claude Code plugin covering the full ElevenLabs surface: 9 vendored official skills plus 9 gap skills that inject live docs indexes at invocation.

**Architecture:** Local plugin `./elevenlabs` in the my-plugins marketplace. A sync script vendors the official `elevenlabs/skills` repo verbatim by folder allowlist. Gap skills are thin SKILL.md files whose `` !`curl ...` `` lines inject a small, current docs index (section `llms.txt` or a grep filter over the full index) when the skill fires; Claude then fetches specific `.md` pages on demand.

**Tech Stack:** Claude Code plugin format (plugin.json, SKILL.md), bash (sync script), curl, rsync, git.

**Spec:** `docs/specs/2026-06-11-elevenlabs-plugin-design.md`

**Conventions for all commits in this plan:** no Co-Authored-By lines, no em-dashes (--) in any file content.

---

### Task 1: Plugin scaffold and marketplace entry

**Files:**
- Create: `elevenlabs/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json` (add entry to the `plugins` array)

- [x] **Step 1: Create plugin.json**

Create `elevenlabs/.claude-plugin/plugin.json`:

```json
{
  "name": "elevenlabs",
  "version": "0.1.0",
  "description": "ElevenLabs development skills: official vendored skills plus live-docs gap skills covering the full product surface.",
  "author": { "name": "Joaquin Campo", "email": "jcampo@pento.ai" },
  "license": "MIT",
  "keywords": ["elevenlabs", "tts", "speech-to-text", "voice", "audio", "agents", "music"],
  "skills": "./skills/"
}
```

- [x] **Step 2: Add marketplace entry**

In `.claude-plugin/marketplace.json`, append this object to the `plugins` array (after the last existing local plugin entry, keep valid JSON commas):

```json
{
  "name": "elevenlabs",
  "source": "./elevenlabs",
  "description": "Full ElevenLabs coverage for building with the API: the 9 official ElevenLabs agent skills (vendored, re-syncable) plus gap skills that pull live docs indexes for voices, dubbing, dialogue, studio, admin, SDKs, image-video, Reception AI, and a docs-lookup catch-all.",
  "version": "0.1.0",
  "keywords": ["elevenlabs", "tts", "speech-to-text", "voice", "audio", "agents", "music"]
}
```

- [x] **Step 3: Verify both files parse**

Run: `jq -e .name elevenlabs/.claude-plugin/plugin.json && jq -e '.plugins[] | select(.name == "elevenlabs") | .source' .claude-plugin/marketplace.json`
Expected: prints `"elevenlabs"` then `"./elevenlabs"`. Non-zero exit means broken JSON; fix before proceeding.

- [x] **Step 4: Commit**

```bash
git add elevenlabs/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat(elevenlabs): plugin scaffold and marketplace entry"
```

---

### Task 2: Sync script and vendored official skills

**Files:**
- Create: `elevenlabs/scripts/sync-official-skills.sh`
- Create (by running the script): `elevenlabs/skills/<9 vendored folders>`

Upstream facts (verified 2026-06-11): `https://github.com/elevenlabs/skills` has the 9 skill folders at repo root (`agents`, `music`, `setup-api-key`, `sound-effects`, `speech-engine`, `speech-to-text`, `text-to-speech`, `voice-changer`, `voice-isolator`), each containing `SKILL.md` (standard frontmatter, MIT) and usually `references/`. Non-skill items at root (`.agents/`, `evals/`, `README.md`, etc.) must NOT be copied; that is why the script copies by allowlist.

- [x] **Step 1: Write the sync script**

Create `elevenlabs/scripts/sync-official-skills.sh`:

```bash
#!/usr/bin/env bash
# Syncs the official ElevenLabs skills (github.com/elevenlabs/skills, MIT)
# into this plugin's skills/ directory. Copies ONLY the allowlisted folders;
# gap skills authored in this repo are never touched.
set -euo pipefail

REPO_URL="https://github.com/elevenlabs/skills"
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$PLUGIN_DIR/skills"
VENDORED=(agents music setup-api-key sound-effects speech-engine speech-to-text text-to-speech voice-changer voice-isolator)

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Cloning $REPO_URL ..."
git clone --depth 1 --quiet "$REPO_URL" "$TMP_DIR/upstream"

missing=()
for skill in "${VENDORED[@]}"; do
  [[ -d "$TMP_DIR/upstream/$skill" && -f "$TMP_DIR/upstream/$skill/SKILL.md" ]] || missing+=("$skill")
done
if (( ${#missing[@]} > 0 )); then
  echo "ERROR: upstream is missing expected skill folders (or their SKILL.md): ${missing[*]}" >&2
  echo "Upstream may have restructured. Nothing was changed locally." >&2
  echo "Update the VENDORED allowlist in this script to match upstream." >&2
  exit 1
fi

mkdir -p "$SKILLS_DIR"
for skill in "${VENDORED[@]}"; do
  rsync -a --delete "$TMP_DIR/upstream/$skill/" "$SKILLS_DIR/$skill/"
done

echo "Synced ${#VENDORED[@]} skills from $REPO_URL"
echo "Local changes (empty means already up to date):"
git -C "$PLUGIN_DIR" status --short -- skills/
```

- [x] **Step 2: Make it executable and lint it**

Run: `chmod +x elevenlabs/scripts/sync-official-skills.sh && bash -n elevenlabs/scripts/sync-official-skills.sh && echo SYNTAX-OK`
Expected: `SYNTAX-OK`

- [x] **Step 3: Run the sync**

Run: `./elevenlabs/scripts/sync-official-skills.sh`
Expected: `Synced 9 skills from https://github.com/elevenlabs/skills` followed by `??`/`A` lines for the 9 new folders under `elevenlabs/skills/`.

- [x] **Step 4: Verify the vendored skills are intact**

Run:

```bash
for d in agents music setup-api-key sound-effects speech-engine speech-to-text text-to-speech voice-changer voice-isolator; do
  f="elevenlabs/skills/$d/SKILL.md"
  head -1 "$f" | grep -q '^---$' && grep -q '^name:' "$f" && echo "OK $d" || echo "BROKEN $d"
done
```

Expected: 9 lines, all `OK`. Any `BROKEN` line means the upstream format changed; stop and inspect that folder.

- [x] **Step 5: Verify idempotency**

Run the script a second time, then compare:

```bash
git status --short -- elevenlabs/skills/ > /tmp/sync1.txt
./elevenlabs/scripts/sync-official-skills.sh > /dev/null
git status --short -- elevenlabs/skills/ > /tmp/sync2.txt
diff /tmp/sync1.txt /tmp/sync2.txt && echo IDEMPOTENT
```

Expected: `IDEMPOTENT` (re-running changes nothing).

- [x] **Step 6: Commit script and vendored skills**

```bash
git add elevenlabs/scripts/sync-official-skills.sh elevenlabs/skills/
git commit -m "feat(elevenlabs): sync script and vendored official skills"
```

---

### Task 3: Gap skills with section-index injection (voices, studio, admin, sdks-integrations, reception-ai)

**Files:**
- Create: `elevenlabs/skills/voices/SKILL.md`
- Create: `elevenlabs/skills/studio/SKILL.md`
- Create: `elevenlabs/skills/admin/SKILL.md`
- Create: `elevenlabs/skills/sdks-integrations/SKILL.md`
- Create: `elevenlabs/skills/reception-ai/SKILL.md`

These five inject a dedicated section `llms.txt` (all verified live on 2026-06-11, sizes 1.4-10KB). The `` !`...` `` line runs at skill invocation, before Claude sees the content, and its output is injected inline. YAML note: keep frontmatter `description` free of `: ` sequences (plain scalars break on colon-space).

- [x] **Step 1: Create voices skill**

Create `elevenlabs/skills/voices/SKILL.md`:

```markdown
---
name: voices
description: Use when working with ElevenLabs voices beyond plain TTS. Covers voice cloning (instant and professional), voice design from text prompts, voice remixing, the Voice Library, and creating, customizing, sharing, or managing voices via the ElevenLabs API.
---

# ElevenLabs Voices

Current docs index for voice cloning, voice design, and the Voice Library:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/eleven-creative/voices/llms.txt || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/eleven-creative/voices/llms.txt"`

Also relevant; fetch directly if the task needs them:

- https://elevenlabs.io/docs/overview/capabilities/voices.md (voices capability overview)
- https://elevenlabs.io/docs/overview/capabilities/voice-remixing.md (voice remixing)

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- For voice API endpoints (create, edit, share, list), grep the full index:
  `curl -sf https://elevenlabs.io/docs/llms.txt | grep -i 'voice'`
- If a fetch fails, fall back to WebFetch on the same URL.
```

- [x] **Step 2: Create studio skill**

Create `elevenlabs/skills/studio/SKILL.md`:

```markdown
---
name: studio
description: Use when working with the ElevenCreative platform. Covers Studio video and audio production, audiobooks, Flows (visual AI pipelines), templates, transcripts, subtitles, voiceover studio, Audio Native web embeds, and Productions (human-edited services).
---

# ElevenLabs Creative Studio (ElevenCreative)

Current docs index for the ElevenCreative platform:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/eleven-creative/llms.txt || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/eleven-creative/llms.txt"`

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- For Studio API endpoints, grep the full index:
  `curl -sf https://elevenlabs.io/docs/llms.txt | grep -i 'studio'`
- If a fetch fails, fall back to WebFetch on the same URL.
```

- [x] **Step 3: Create admin skill**

Create `elevenlabs/skills/admin/SKILL.md`:

```markdown
---
name: admin
description: Use for ElevenLabs account and workspace administration. Covers billing, pay as you go, credits, data residency, usage analytics, workspaces, members, seats, billing groups, service accounts, API keys, SSO and SAML and SCIM, resource sharing, and user groups.
---

# ElevenLabs Administration

Current docs index for account, billing, and workspace administration:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/overview/administration/llms.txt || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/overview/administration/llms.txt"`

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- For admin API endpoints (usage, history, workspace management), grep the full
  index: `curl -sf https://elevenlabs.io/docs/llms.txt | grep -iE 'usage|workspace|history'`
- If a fetch fails, fall back to WebFetch on the same URL.
```

- [x] **Step 4: Create sdks-integrations skill**

Create `elevenlabs/skills/sdks-integrations/SKILL.md`:

```markdown
---
name: sdks-integrations
description: Use when integrating the ElevenLabs API through an SDK or quickstart. Covers the JavaScript, Python, React, React Native, Kotlin, and Swift SDKs, cookbook quickstarts for every capability, authentication, and choosing the right model.
---

# ElevenLabs SDKs and API Quickstarts (ElevenAPI)

Current docs index for SDK quickstarts and cookbooks:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/eleven-api/llms.txt || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/eleven-api/llms.txt"`

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- For raw endpoint reference, grep the full index for the resource name:
  `curl -sf https://elevenlabs.io/docs/llms.txt | grep -i '<resource>'`
- Platform integrations for voice agents (Twilio, Slack, HubSpot) live in the
  agents skill; web embeds (Audio Native) live in the studio skill.
- If a fetch fails, fall back to WebFetch on the same URL.
```

- [x] **Step 5: Create reception-ai skill**

Create `elevenlabs/skills/reception-ai/SKILL.md`:

```markdown
---
name: reception-ai
description: Use when working with ElevenLabs Reception AI, the AI phone receptionist product. Covers setup, configuration, phone numbers, call handling, and the Reception AI APIs.
---

# ElevenLabs Reception AI

Current docs index for Reception AI:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/reception-ai/llms.txt || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/reception-ai/llms.txt"`

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- If a fetch fails, fall back to WebFetch on the same URL.
```

- [x] **Step 6: Verify every injection command works and is right-sized**

Run:

```bash
for d in voices studio admin sdks-integrations reception-ai; do
  cmd=$(grep -o '!`[^`]*`' "elevenlabs/skills/$d/SKILL.md" | head -1 | sed 's/^!`//; s/`$//')
  bytes=$(bash -c "$cmd" | wc -c | tr -d ' ')
  echo "$d: $bytes bytes"
done
```

Expected: five lines, each between 1000 and 15000 bytes, none containing `FETCH FAILED`. A 0 or a failure line means the URL or the command quoting is wrong; fix before committing.

- [x] **Step 7: Commit**

```bash
git add elevenlabs/skills/voices elevenlabs/skills/studio elevenlabs/skills/admin elevenlabs/skills/sdks-integrations elevenlabs/skills/reception-ai
git commit -m "feat(elevenlabs): section-index gap skills"
```

---

### Task 4: Gap skills with grep-filter injection (dubbing, text-to-dialogue, image-video) and docs-lookup catch-all

**Files:**
- Create: `elevenlabs/skills/dubbing/SKILL.md`
- Create: `elevenlabs/skills/text-to-dialogue/SKILL.md`
- Create: `elevenlabs/skills/image-video/SKILL.md`
- Create: `elevenlabs/skills/docs-lookup/SKILL.md`

These areas have no dedicated docs section; their pages span capabilities, ElevenCreative, Productions, and the API reference. The injection greps the full `llms.txt` (112KB stays in the shell; only matching lines reach context). `docs-lookup` injects nothing; it teaches the same filter technique for any topic.

- [x] **Step 1: Create dubbing skill**

Create `elevenlabs/skills/dubbing/SKILL.md`:

```markdown
---
name: dubbing
description: Use when building dubbing or audio and video translation features with ElevenLabs. Covers automated dubbing, Dubbing Studio fine-grained control, human-edited dubbing via Productions, and the dubbing API endpoints.
---

# ElevenLabs Dubbing

All dubbing-related pages in the current docs index:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/llms.txt | grep -i 'dub' || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/llms.txt and search for dubbing"`

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- If a fetch fails, fall back to WebFetch on the same URL.
```

- [x] **Step 2: Create text-to-dialogue skill**

Create `elevenlabs/skills/text-to-dialogue/SKILL.md`:

```markdown
---
name: text-to-dialogue
description: Use when generating multi-speaker dialogue with ElevenLabs Text to Dialogue. Covers immersive conversations between multiple voices, the dialogue API, and dialogue quickstarts.
---

# ElevenLabs Text to Dialogue

All dialogue-related pages in the current docs index:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/llms.txt | grep -i 'dialogue' || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/llms.txt and search for dialogue"`

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- If a fetch fails, fall back to WebFetch on the same URL.
```

- [x] **Step 3: Create image-video skill**

Create `elevenlabs/skills/image-video/SKILL.md`:

```markdown
---
name: image-video
description: Use when generating or editing images and videos with ElevenLabs, including avatars (talking-head videos with synchronized lip movement). Covers image and video generation from text prompts and visual references.
---

# ElevenLabs Image and Video

All image, video, and avatar pages in the current docs index (some matched
lines are about video dubbing or translation; ignore those here, the dubbing
skill covers them):

!`curl -sf --max-time 15 https://elevenlabs.io/docs/llms.txt | grep -iE 'image|video|avatar' || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/llms.txt and search for image-video"`

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- If a fetch fails, fall back to WebFetch on the same URL.
```

- [x] **Step 4: Create docs-lookup skill**

Create `elevenlabs/skills/docs-lookup/SKILL.md`:

```markdown
---
name: docs-lookup
description: Catch-all for any ElevenLabs question not covered by a more specific skill. Use for API endpoint reference lookups, forced alignment, models and pricing pages, changelog, or any new ElevenLabs product. Finds the right documentation page and fetches it as clean markdown.
---

# ElevenLabs Docs Lookup

The complete docs index lives at https://elevenlabs.io/docs/llms.txt
(roughly 760 lines, 112KB). Never read it whole into context; filter it in
the shell and only the matching lines come back:

    curl -sf https://elevenlabs.io/docs/llms.txt | grep -iE '<topic-regex>'

Then fetch only the specific pages needed (index URLs already end in `.md`
and return clean markdown):

    curl -sf <page-url>

## Tips

- API endpoint reference pages live under
  `https://elevenlabs.io/docs/api-reference/` (about 310 pages). Grep for the
  resource name, e.g. `grep -iE 'speech-to-text|transcript'`.
- Any docs section has its own small index; append `/llms.txt` to the section
  URL, e.g. `https://elevenlabs.io/docs/eleven-agents/llms.txt`.
- Any docs page has a markdown version; append `.md` to its URL.
- Never fetch `https://elevenlabs.io/docs/llms-full.txt` (the entire docs in
  one file; far too large).
- If curl fails, fall back to WebFetch on the same URL.
```

- [x] **Step 5: Verify the grep injections return sane output**

Run:

```bash
for d in dubbing text-to-dialogue image-video; do
  cmd=$(grep -o '!`[^`]*`' "elevenlabs/skills/$d/SKILL.md" | head -1 | sed 's/^!`//; s/`$//')
  out=$(bash -c "$cmd")
  echo "$d: $(echo "$out" | wc -l | tr -d ' ') lines, $(echo "$out" | wc -c | tr -d ' ') bytes"
done
```

Expected: each between 3 and 80 lines, under 15000 bytes, no `FETCH FAILED`. Also confirm `docs-lookup/SKILL.md` contains no `` !` `` injection at all: `grep -c '!\`' elevenlabs/skills/docs-lookup/SKILL.md` prints `0`.

- [x] **Step 6: Verify all 9 gap skills have parseable frontmatter and folder-matching names**

Run:

```bash
for d in voices studio admin sdks-integrations reception-ai dubbing text-to-dialogue image-video docs-lookup; do
  n=$(awk '/^name:/{print $2; exit}' "elevenlabs/skills/$d/SKILL.md")
  [[ "$n" == "$d" ]] && echo "OK $d" || echo "MISMATCH $d (frontmatter says: $n)"
done
```

Expected: 9 `OK` lines.

- [x] **Step 7: Commit**

```bash
git add elevenlabs/skills/dubbing elevenlabs/skills/text-to-dialogue elevenlabs/skills/image-video elevenlabs/skills/docs-lookup
git commit -m "feat(elevenlabs): grep-filter gap skills and docs-lookup catch-all"
```

---

### Task 5: README

**Files:**
- Create: `elevenlabs/README.md`

- [x] **Step 1: Write the README**

Create `elevenlabs/README.md`:

```markdown
# elevenlabs

Full ElevenLabs coverage for building with the API, in one Claude Code plugin.

## What's inside

**Vendored official skills** (from [elevenlabs/skills](https://github.com/elevenlabs/skills), MIT):
`text-to-speech`, `speech-to-text`, `agents`, `music`, `sound-effects`,
`voice-changer`, `voice-isolator`, `speech-engine`, `setup-api-key`.

**Gap skills** (authored here; each injects a live docs index at invocation
via `!`-command preprocessing, then fetches specific pages on demand):
`voices`, `dubbing`, `text-to-dialogue`, `studio`, `admin`,
`sdks-integrations`, `image-video`, `reception-ai`, and `docs-lookup`
(catch-all for endpoints, forced alignment, and anything new).

## Updating the vendored skills

```bash
# from the repo root
./elevenlabs/scripts/sync-official-skills.sh
git diff elevenlabs/skills/   # review what changed upstream
```

The script copies by allowlist and never touches the gap skills. If upstream
renames a folder, the script fails loudly without changing anything; update
the `VENDORED` list in the script.

## Maintenance notes

- Gap skills depend on `https://elevenlabs.io/docs/.../llms.txt` URLs. If one
  starts printing `FETCH FAILED` on invocation, the section moved; find the
  new path in https://elevenlabs.io/docs/llms.txt and update the skill's
  injection line.
- Want Claude to *perform* audio actions (generate speech, transcribe, clone)
  instead of writing code? Use the official MCP server:
  https://github.com/elevenlabs/elevenlabs-mcp

## Credits

Vendored skills are (c) ElevenLabs, MIT licensed:
https://github.com/elevenlabs/skills
```

- [x] **Step 2: Commit**

```bash
git add elevenlabs/README.md
git commit -m "docs(elevenlabs): plugin README"
```

---

### Task 6: End-to-end verification

**Files:** none created; verification only.

- [x] **Step 1: Re-run the sync script to confirm it is a no-op on a clean tree**

Run: `./elevenlabs/scripts/sync-official-skills.sh && git status --short`
Expected: `Synced 9 skills ...` and empty `git status --short` output (tree stays clean).

- [x] **Step 2: Refresh the installed marketplace and install the plugin**

Run: `claude plugin marketplace update my-plugins && claude plugin install elevenlabs@my-plugins`
Expected: both commands succeed; install reports the `elevenlabs` plugin added. If `marketplace update` complains the marketplace is a local path that has uncommitted state, commit first (all prior tasks end in commits, so the tree should be clean).

- [x] **Step 3: Smoke-test a gap skill end to end**

Run: `claude -p "Invoke the elevenlabs:docs-lookup skill, then give me the exact URL of the ElevenLabs API streaming reference page. Answer with the URL only."`
Expected: output contains `https://elevenlabs.io/docs/api-reference/streaming`. This proves the skill loads under the plugin namespace and the filter-then-fetch flow works.

- [x] **Step 4: Smoke-test an injection skill**

Run: `claude -p "Invoke the elevenlabs:admin skill and list the first three page titles from its injected docs index. Titles only."`
Expected: three titles matching the administration section (e.g. Account, Billing, Pay As You Go). If the model reports a FETCH FAILED line, the injection broke; debug the curl command from Task 3 Step 6.

- [x] **Step 5: Smoke-test a vendored skill loads**

Run: `claude -p "Invoke the elevenlabs:text-to-speech skill and tell me which env var it requires. Answer with the env var name only."`
Expected: `ELEVENLABS_API_KEY`.

- [x] **Step 6: Mark the plan complete**

Update this file's checkboxes, then:

```bash
git add docs/plans/2026-06-11-elevenlabs.md
git commit -m "docs: mark elevenlabs plan complete"
```
