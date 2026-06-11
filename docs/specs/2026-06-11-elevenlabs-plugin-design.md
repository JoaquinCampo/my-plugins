# elevenlabs: design spec

Date: 2026-06-11
Status: design approved, ready for plan

## Purpose

A Claude Code plugin covering the full ElevenLabs capability surface for developers building with the ElevenLabs API. It leverages what ElevenLabs already maintains (their official agent skills and LLM-friendly docs) instead of duplicating it, and fills the gaps with thin skills that pull fresh documentation at invocation time.

## What ElevenLabs already provides

| Asset | What it is | How we use it |
|---|---|---|
| [elevenlabs/skills](https://github.com/elevenlabs/skills) (MIT) | 9 official agent skills following the agentskills.io spec (SKILL.md format), actively maintained with evals: text-to-speech, speech-to-text, agents, music, sound-effects, voice-changer, voice-isolator, speech-engine, setup-api-key | Vendor verbatim via a sync script. Not usable directly as a marketplace source because the repo has no `.claude-plugin/plugin.json`; it installs via `npx skills add` into per-project `.claude/skills`. |
| [elevenlabs.io/docs/llms.txt](https://elevenlabs.io/docs/llms.txt) | Full docs index. Per-section `llms.txt` indexes and `.md` versions of every page. | Gap skills inject section indexes at invocation and fetch specific `.md` pages on demand. |
| [elevenlabs/elevenlabs-mcp](https://github.com/elevenlabs/elevenlabs-mcp) | Official local MCP server that performs actions (generate speech, clone, transcribe). | Out of scope. Primary use case is building with the API, not driving ElevenLabs from sessions. Documented in README as a pointer. |

## Decisions (locked)

| Decision | Choice | Why |
|---|---|---|
| Use case | Building with the API | Dev guidance skills; no MCP server bundled. |
| Official skills | Vendor + sync script | Marketplace install works; ElevenLabs maintains content; re-sync pulls updates. Vendored files are never edited so syncs stay clean. |
| Gap coverage | One skill per missing docs area, each using `!` dynamic injection | User-chosen pattern. `` !`curl -s <section>/llms.txt` `` runs at skill invocation, before Claude sees the content, injecting the current section index. Verified supported in SKILL.md (commands and skills are unified; multi-line via ` ```! ` fences). |
| Context sizing | Inject indexes only, never full pages | Injected output counts toward the skill's prompt; auto-compaction keeps ~5k tokens per skill. Section indexes are small lists of titles + URLs; Claude fetches only the specific `.md` pages the task needs. |
| Location | Local plugin `./elevenlabs` in `my-plugins` marketplace | Same shape as the other local plugins. |

## File layout

```
my-plugins/
├── .claude-plugin/marketplace.json     # add elevenlabs entry
├── elevenlabs/
│   ├── .claude-plugin/plugin.json
│   ├── README.md                       # coverage map, sync instructions, MCP pointer
│   ├── scripts/
│   │   └── sync-official-skills.sh
│   └── skills/
│       ├── text-to-speech/             # ── vendored from elevenlabs/skills ──
│       ├── speech-to-text/
│       ├── agents/
│       ├── music/
│       ├── sound-effects/
│       ├── voice-changer/
│       ├── voice-isolator/
│       ├── speech-engine/
│       ├── setup-api-key/
│       ├── voices/                     # ── gap skills (ours) ──
│       ├── dubbing/
│       ├── text-to-dialogue/
│       ├── studio/
│       ├── admin/
│       ├── sdks-integrations/
│       ├── image-video/
│       ├── reception-ai/
│       └── docs-lookup/
└── docs/specs/2026-06-11-elevenlabs-plugin-design.md   # this file
```

## Sync script

`scripts/sync-official-skills.sh`:

1. Shallow-clone `https://github.com/elevenlabs/skills` to a temp dir.
2. Copy each official skill folder into `elevenlabs/skills/`, replacing the previous copy (`rsync --delete` per folder).
3. Never touch the gap-skill folders (explicit allowlist of vendored folder names).
4. Print a diff summary so the commit message can say what changed upstream.

Run manually when an update is wanted; not wired to any hook.

## Gap skills

Nine skills, one per docs area the official skills do not cover, plus a catch-all. (The list grew from six during implementation research: the docs index revealed `image-video`, `reception-ai`, and the 310-page API reference as uncovered areas; `docs-lookup` future-proofs against new products.) Injection sources were verified live on 2026-06-11; all section indexes are 1-10KB.

| Skill | Docs area | Injection source |
|---|---|---|
| `voices` | Voice cloning, voice design, remixing, voice library | `eleven-creative/voices/llms.txt` (1.4KB) + capability overview page URLs in body |
| `dubbing` | Audio/video translation | grep `-i dub` over full `llms.txt` (no dedicated section; pages span capabilities, creative, productions, api-reference) |
| `text-to-dialogue` | Multi-speaker dialogue | grep `-i dialogue` over full `llms.txt` |
| `studio` | Creative studio, audiobooks, flows, transcripts, subtitles, audio native | `eleven-creative/llms.txt` (6.4KB) |
| `admin` | Workspaces, SSO, billing, data residency, usage analytics | `overview/administration/llms.txt` (3.3KB) |
| `sdks-integrations` | SDK quickstarts and cookbooks (JS, Python, React, React Native, Kotlin, Swift), platform integrations | `eleven-api/llms.txt` (10KB) |
| `image-video` | Image and video generation, avatars | grep `-iE 'image|video|avatar'` over full `llms.txt` |
| `reception-ai` | Reception AI product | `reception-ai/llms.txt` (4.4KB) |
| `docs-lookup` | Catch-all: API endpoint reference (310 pages), forced alignment, and anything new ElevenLabs ships | No injection; instructs grep-filtering the full `llms.txt` (112KB, never fetched whole into context) for any topic, then fetching specific `.md` pages |

Each SKILL.md follows this shape:

```markdown
---
name: dubbing
description: Use when building dubbing or audio/video translation features
  with the ElevenLabs API (project-based dubbing, language targets, watermarks).
---

# ElevenLabs Dubbing

Current documentation index for this area:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/<section>/llms.txt || echo "FETCH FAILED: use WebFetch on https://elevenlabs.io/docs/<section>/llms.txt"`

## How to use this index

- Pick only the pages relevant to the task; fetch each as markdown by
  appending `.md` to its URL: `curl -sf <page-url>.md`.
- Fetch one page at a time; do not bulk-fetch the whole section.
- If a fetch fails, fall back to WebFetch on the same URL.
```

Skill `name` matches its folder (the plugin namespace yields `elevenlabs:dubbing` etc.); the `description` carries the auto-trigger specificity, always mentioning "ElevenLabs" plus the concrete tasks the area covers.

Injection sources were verified live on 2026-06-11 (see the table above). Areas without a dedicated docs section (dubbing, dialogue, image-video) inject a grep filter over the full `llms.txt` instead, which yields exactly the matching page list without pulling the 112KB index into context.

## marketplace.json entry

```json
{
  "name": "elevenlabs",
  "source": "./elevenlabs",
  "description": "Full ElevenLabs coverage for building with the API: the 9 official ElevenLabs agent skills (vendored, re-syncable) plus gap skills that pull live docs indexes for voices, dubbing, dialogue, studio, admin, and SDKs.",
  "version": "0.1.0",
  "keywords": ["elevenlabs", "tts", "speech-to-text", "voice", "audio", "agents", "music"]
}
```

## plugin.json

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

Vendored content is MIT licensed upstream; the README credits `elevenlabs/skills` and links the upstream repo.

## Error handling

| Failure | Behavior |
|---|---|
| `curl` fails at injection time (offline, URL moved) | Injection emits a `FETCH FAILED` line naming the URL; skill body instructs falling back to WebFetch. The skill still loads. |
| Upstream repo restructures (skill folders renamed) | Sync script copies by allowlist; a missing folder produces a loud error listing what was not found, nothing is deleted. |
| Section `llms.txt` URL stops existing | Same FETCH FAILED path; README documents how to update the URL. |

## Testing

1. Run the sync script; confirm the 9 official skills land intact (frontmatter parses, references included).
2. Install the plugin locally from the marketplace.
3. Invoke each gap skill; confirm the injected index is present, current, and small (eyeball token size).
4. From a gap skill, fetch one specific `.md` page and confirm clean markdown.
5. Invoke one vendored skill end-to-end to confirm it functions under the plugin namespace.
6. Re-run the sync script on the clean tree; confirm it is a no-op (idempotent).

## Out of scope

- Bundling the ElevenLabs MCP server (`.mcp.json`); README points to it for users who want in-session audio generation.
- Authored long-form content for gap areas; the live docs are the content.
- Automated scheduled syncing of vendored skills.
