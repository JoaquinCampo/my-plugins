# fable-delegation-to-codex

Makes a Fable (Claude Code) session route all delegable work to the Codex CLI via `codex exec` instead of spawning Claude subagents. Fable keeps orchestration, design decisions, and final judgment; Codex does exploration, bulk reads, tests, mechanical edits, first-pass reviews, and repo-wide sweeps on its own quota. Main-context tokens are spent only on reading compact result files.

## Requirements

The skill assumes the following environment. Without these it will produce commands that prompt for approval, pick missing models, or fail outright.

### 1. Codex CLI installed and authenticated

```bash
brew install codex        # or: npm i -g @openai/codex
codex login
```

Verified against `codex-cli 0.142.4`. The skill relies on `codex exec` flags `-m`, `-C`, `-o`, `-s`, `--skip-git-repo-check`, `--output-schema`, and `codex exec resume`.

### 2. `~/.codex/config.toml` keys

The skill states that Codex runs fully autonomous with no extra flags. That is only true with:

```toml
approval_policy = "never"
sandbox_mode = "danger-full-access"
multi_agent = true
```

`multi_agent = true` is what lets a single delegation fan out internal Codex subagents. If you prefer a safer default, keep `sandbox_mode = "workspace-write"`; the skill's read-only rule (`-s read-only` for no-write tasks) still applies either way.

### 3. Models

The tier table uses `gpt-5.3-codex-spark` (fast default) and `gpt-5.5`. Check what your Codex plan exposes with a quick `codex exec -m gpt-5.3-codex-spark "say ok"`. If Spark is unavailable, route Spark-shaped tasks to `gpt-5.4-mini` (see the companion skill below).

### 4. Codex-side fan-out instruction (recommended)

For the "fan out internal subagents" scale directive to land reliably, add this to `~/.codex/AGENTS.md`:

```markdown
- Whenever a task decomposes into independent delegable units (multi-file sweeps, parallel
  exploration, batched mechanical edits), use the orchestrating-subagents skill: spawn internal
  subagents in parallel and route their models per the codex-model-routing skill. Keep the final
  message a compact synthesis; subagent transcripts stay out of it. This applies especially when
  running non-interactively (`codex exec`) as a worker for an orchestrating agent.
```

This requires the `orchestrating-subagents` skill to be available on the Codex side (in this marketplace it ships with the `tools` plugin, which also works as a Codex plugin).

### 5. Companion skill (optional)

`tools:codex-model-routing` (in this marketplace's `tools` plugin) provides the finer routing table (`gpt-5.4`, `gpt-5.4-mini`, maker/checker/fixer loops). The skill cross-references it; without it, the three-tier table in the skill still works.

## How it behaves

- Delegations launch as background Bash commands, so the harness notifies Fable on completion; several independent delegations run in parallel.
- Results land in a per-task `-o` file; Fable reads only that file, never the transcript log.
- No-write tasks always run with `-s read-only` as a hard guarantee.
- Write tasks get an isolated worktree, or stay read-only while Fable holds the working tree; two agents never edit the same tree concurrently.
- Claude subagents and forks are not used for delegable work. The single exception is a fable-tier Claude agent for genuinely hard isolated judgment, used sparingly.

## Install

From this marketplace: `/plugin install fable-delegation-to-codex@my-plugins`. If you previously kept a standalone copy of the skill in `~/.claude/skills/fable-delegation-to-codex/`, remove it after installing the plugin to avoid a duplicate skill listing.
