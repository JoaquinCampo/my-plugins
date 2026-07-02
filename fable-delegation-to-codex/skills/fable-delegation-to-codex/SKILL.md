---
name: fable-delegation-to-codex
description: Use at the start of every Fable session, and whenever a unit of work could go to a subagent - exploration, bulk file reading and summarizing, running tests or builds, mechanical multi-file edits, first-pass code reviews, research sweeps, or any token-heavy step whose deliverable is a compact result. Routes that work to the Codex CLI (codex exec) instead of Claude subagents, spending Codex quota instead of Anthropic tokens.
---

# Fable Delegation to Codex

## Overview

Fable orchestrates, decides, and judges; Codex executes. All delegable work goes to `codex exec`: it runs on a separate Codex quota, so main-context tokens are spent only on reading compact results. Codex has every tool it needs; do not spawn Claude subagents or forks for delegable work. The single exception is a fable-tier Claude agent for genuinely hard isolated judgment, used sparingly (it consumes the expensive quota). The main thread keeps orchestration, design decisions, and final judgment on Codex's output.

## Model tiers

| Model | Use for |
|---|---|
| `gpt-5.3-codex-spark` | Default. Exploration, bulk reads and summaries, mechanical edits, running tests/builds and reporting |
| `gpt-5.5` (effort medium, config default) | Substantive implementation, first-pass reviews |
| `gpt-5.5` + `-c model_reasoning_effort=high` | Genuinely hard delegated tasks only |

For finer routing (`gpt-5.4`, `gpt-5.4-mini`, maker/checker/fixer loops), use tools:codex-model-routing.

## Invocation

`~/.codex/config.toml` already sets `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, and `multi_agent = true`. So `codex exec` runs fully autonomous with no extra flags, and one delegation can fan out its own internal subagents (use this for large sweeps: one prompt, Codex parallelizes on its own quota).

```bash
codex exec -m gpt-5.3-codex-spark -C /path/to/repo \
  -o "$SCRATCHPAD/codex-<task>.md" --skip-git-repo-check - > "$SCRATCHPAD/codex-<task>.log" 2>&1 <<'EOF'
<prompt>
EOF
```

- Prompt via stdin heredoc (`-`), never inline quoting.
- Long tasks: `run_in_background: true`. Independent tasks: launch several at once.
- Read ONLY the `-o` file; the `.log` transcript is for debugging failures, never load it whole.
- If the task makes no writes (exploration, reading, review, research), the command includes `-s read-only`. Omit it only when Codex must edit files or run state-changing commands.
- Structured result: `--output-schema <schema.json>`. First-pass review: `codex exec review`.
- Follow-up on the same task: `codex exec resume --last "<follow-up>"` instead of re-prompting from scratch.

## Dispatch prompt

Codex cannot ask questions. Every prompt contains, in order:

1. Role and goal in one sentence.
2. Exact absolute paths; what to read first. Locate by content, line numbers are approximate.
3. Behavior scope: state explicitly whether it should edit files, run commands, or stay read-only. Within that scope it uses its own judgment.
4. Scale directive, always one of the two: "Work solo" for a single bounded unit, or, for anything spanning many files or independent units (repo-wide sweeps, batched edits, parallel exploration), "Fan out internal subagents via your orchestrating-subagents skill and return only the synthesis".
5. Deliverable: exact shape of the final message (it is data for Fable, not user-facing prose). No em-dashes.

Write tasks: give Codex an isolated worktree, or keep it read-only while Fable holds the working tree. Two agents editing the same tree concurrently corrupts both.

## Common mistakes

| Mistake | Fix |
|---|---|
| Spawning a Claude subagent or fork for delegable work | Always Codex; the sole exception is a fable-tier agent for genuinely hard judgment, sparingly |
| Reading the transcript/log into context | Read the `-o` file only |
| Vague scope ("look into X") | State deliverable shape and behavior scope explicitly |
| Trusting Codex edits blind | Fable reviews the diff (`git diff`) before building on it |
| Serial delegations | Independent units launch in parallel, in the background |
