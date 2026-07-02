---
name: fable-delegation-to-codex
description: Use at the start of every Fable session. Fable is the brain: decompose, dispatch, judge, and talk to the user. Codex CLI does the work: exploration, bulk reads, tests, builds, implementation, reviews, and other token-heavy units.
---

# Fable Delegation to Codex

## Overview

Fable's cost is its context: every token loaded into the main thread is re-read on every turn. So the main thread holds only pure signal (plans, dispatch prompts, diffs, compact results, decisions) and Codex executes everything else on its own quota via `codex exec`. Never spawn Claude subagents or forks for delegable work; the single exception is a fable-tier Claude agent for genuinely hard isolated judgment, used sparingly.

**Dividing rule: if a step's raw output is bigger than its conclusion, delegate it.** Exploration, bulk reads, log analysis, running tests and builds, research sweeps, substantive implementation, and first-pass reviews all go to Codex. Fable keeps decomposition, dispatch-prompt writing, diff review, adjudication between conflicting findings, architecture and product decisions, user interaction, and edits smaller than the prompt it would take to delegate them.

## Brain vs worker

| Fable keeps | Codex gets |
|---|---|
| Task decomposition and batch design | Repository scouting and source-file summaries |
| Dispatch prompts and worker scope | Bulk reads, logs, research, tests, and builds |
| Architecture, product, and user-facing decisions | Implementation units with clear ownership |
| Adjudication between conflicting results | Mechanical multi-file edits and first-pass reviews |
| Diff review before the next batch | Verification loops that return compact pass/fail evidence |

## Operating loop

Every Fable turn is dispatch or judge, never execute.

1. **Decompose first.** On a new task, write the unit work-list before reading any file. If Fable does not know enough to split the task, that scouting is itself delegable: a Spark exploration returns the map.
2. **Dispatch in batches.** Launch every currently-independent unit in ONE tool message, with each `codex exec` call marked `run_in_background: true` by the host tool, not by a shell flag. Parallel writers share the tree but split by file ownership: each prompt names the exact files/directories the unit owns and forbids touching anything else; only units with overlapping scopes run in sequence. Fable stays out of owned files until the unit lands.
3. **Never poll.** After dispatching, do not block on TaskOutput for a running delegation: either advance a different unit or end the turn. The harness task notification wakes Fable when a result lands. A launch note to the user ("dispatched N units, ~X min") replaces status-checking.
4. **Judge, then next batch.** On results: read the `-o` file, spot-check the diff (`git diff` on the unit's owned files), then integrate or dispatch the follow-up batch. A compact summary can hide errors; never build on an undiffed edit.

## Model tiers

| Model | Use for |
|---|---|
| `gpt-5.3-codex-spark` | Default for exploration, bulk reads, mechanical edits, tests/builds, verification loops, first-pass reviews, and tightly scoped implementation |
| `gpt-5.4-mini` | Reliability bump for moderate edits, exact review fixes, second-pass reviews, and compact but tricky summaries |
| `gpt-5.5` (effort medium, config default) | Escalation on evidence: a Spark diff failed Fable's review, or the unit is genuinely tricky up front (subtle concurrency, cross-cutting design, gnarly debugging, architecture-sensitive implementation) |
| `gpt-5.5` + `-c model_reasoning_effort=high` | The hardest delegated units only |

For finer routing (`gpt-5.4`, `gpt-5.4-mini`, maker/checker/fixer loops), use tools:codex-model-routing.

**Spark is the workhorse.** Default to Spark for scouting, reduction, verification, and bounded work where Fable can cheaply review the diff or result. Use `gpt-5.4-mini` when the worker needs a reliability bump without hard judgment, and escalate to `gpt-5.5` when the unit needs deep reasoning or owns architecture-sensitive implementation. Spark's speed changes the shape of delegation: fire many small units at once instead of folding them into one big prompt, use it for scouting before decomposition, and run cheap verify loops that return pass/fail evidence.

## Invocation

`~/.codex/config.toml` already sets `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, and `multi_agent = true`. So `codex exec` runs fully autonomous with no extra flags, and one delegation can fan out its own internal subagents (use this for large sweeps: one prompt, Codex parallelizes on its own quota).

```bash
codex exec -m gpt-5.3-codex-spark -C /path/to/repo \
  -o "$SCRATCHPAD/codex-<task>.md" --skip-git-repo-check - > "$SCRATCHPAD/codex-<task>.log" 2>&1 <<'EOF'
<prompt>
EOF
```

- Prompt via stdin heredoc (`-`), never inline quoting.
- `run_in_background: true` is host-tool metadata around the shell command, not part of the `codex exec` command itself.
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

Write tasks: the prompt names the exact files/directories the unit owns and forbids edits outside them (this is what lets writers run in parallel on the same tree); Fable stays out of those files until the unit lands.

## Common mistakes

| Mistake | Fix |
|---|---|
| Executing a unit yourself because the context is already loaded | Loaded context is sunk cost; dispatch anyway unless the edit is smaller than the prompt it needs |
| Serial delegations | All independent units launch in one message, in the background |
| Polling TaskOutput on a running delegation | End the turn or advance another unit; the task notification wakes you |
| Serializing write-tasks to avoid tree conflicts | Give each writer disjoint file ownership in its prompt; they run in parallel on the same tree |
| Doing a small mechanical step inline to dodge delegation latency | Spark returns in seconds; fire it |
| Spawning a Claude subagent or fork for delegable work | Always Codex; the sole exception is a fable-tier agent for genuinely hard judgment, sparingly |
| Reading the transcript/log into context | Read the `-o` file only |
| Reading source files Codex could summarize | Fable reads diffs, `-o` files, and files it must itself edit; bulk reading is a delegation |
| Vague scope ("look into X") | State deliverable shape and behavior scope explicitly |
| Trusting Codex edits blind | Fable reviews the diff (`git diff`) before building on it |
