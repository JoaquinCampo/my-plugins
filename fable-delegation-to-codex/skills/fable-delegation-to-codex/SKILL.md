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

1. **Decompose first.** On a new task, write the unit work-list before reading any file. If Fable does not know enough to split the task, that scouting is itself delegable: a Luna exploration returns the map.
2. **Dispatch selectively.** Launch the critical-path unit first. In the same tool message, launch at most 2 to 3 genuinely independent units whose combined value justifies the usage, with each `codex exec` call marked `run_in_background: true` by the host tool, not by a shell flag. Parallel writers must have disjoint file ownership; overlapping scopes run in sequence. Fable stays out of owned files until each unit lands.
3. **Never idle or poll.** After dispatching, do not block on TaskOutput for a running delegation. Advance another unit, prepare validation, inspect an unrelated diff, synthesize completed evidence, or end the turn. The harness notification wakes Fable when a result lands. Wait only when no independent work remains and the result is required to proceed.
4. **Judge, then next batch.** On results: read the `-o` file, spot-check the diff (`git diff` on the unit's owned files), then integrate or dispatch the follow-up batch. A compact summary can hide errors; never build on an undiffed edit.

## Model tiers (GPT-5.6)

Use the GPT-5.6 Sol / Terra / Luna family. Exact ids:

| Model and effort | Use for |
|---|---|
| `gpt-5.6-luna` at low | Bounded mechanical search, inventory, and verification support |
| `gpt-5.6-luna` at high | Small, bounded implementation and routine work |
| `gpt-5.6-luna` at xhigh | Quality-sensitive normal coding and independent review |
| `gpt-5.6-terra` at high | Larger multi-file implementation and substantial cross-file reasoning |
| `gpt-5.6-sol` at medium | Ambiguous substantive work that needs stronger reasoning |
| `gpt-5.6-sol` at high | Architecture, hard debugging, difficult review, and final judgment |
| `gpt-5.6-sol` at xhigh | Advisor only, never an ordinary worker |

For finer routing and maker/checker/fixer loops, use tools:codex-model-routing.

Start with the cheapest reliable route and escalate only when uncertainty, failed validation, conflicting evidence, or meaningful risk justifies it. Avoid max effort, Terra xhigh, and broad Sol fan-out. Prefer one strong worker over several weaker workers repeating the same task. GPT 5.6 is required; if the ids are unavailable, upgrade Codex rather than silently falling back to an older model family.

Requires Codex CLI that recognizes the 5.6 ids, verified here with 0.144.0. Confirm with `codex --version` and a quick `codex exec -m gpt-5.6-luna "say ok"`.

## Invocation

`~/.codex/config.toml` already sets `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, and `multi_agent = true`. So `codex exec` runs fully autonomous with no extra approval flags. Keep ordinary delegated units single-agent; internal fan-out is an explicit exception for a large, genuinely decomposable unit whose value justifies the extra quota.

```bash
codex exec -m gpt-5.6-luna -c model_reasoning_effort=high -C /path/to/repo \
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
- Set effort explicitly on every delegation with `-c model_reasoning_effort=low|medium|high|xhigh`. Avoid max effort and Terra xhigh; reserve Sol xhigh for the advisor.

## Dispatch prompt

Codex cannot ask questions. Every prompt contains, in order:

1. Role and goal in one sentence.
2. Exact absolute paths; what to read first. Locate by content, line numbers are approximate.
3. Behavior scope: state explicitly whether it should edit files, run commands, or stay read-only. Within that scope it uses its own judgment.
4. Scale directive: use "Work solo" by default. Use "Fan out at most 2 to 3 independent internal subagents and return only the synthesis" only for a large decomposable unit whose parallel value justifies the quota.
5. Deliverable: exact shape of the final message (it is data for Fable, not user-facing prose). No em-dashes.

Write tasks: the prompt names the exact files/directories the unit owns and forbids edits outside them (this is what lets writers run in parallel on the same tree); Fable stays out of those files until the unit lands.

## Common mistakes

| Mistake | Fix |
|---|---|
| Executing a unit yourself because the context is already loaded | Loaded context is sunk cost; dispatch anyway unless the edit is smaller than the prompt it needs |
| Serial delegations | Launch the critical path first, then at most 2 to 3 worthwhile independent units in the background |
| Polling TaskOutput on a running delegation | End the turn or advance another unit; the task notification wakes you |
| Serializing write-tasks to avoid tree conflicts | Give each writer disjoint file ownership in its prompt; they run in parallel on the same tree |
| Doing a small mechanical step inline to dodge delegation latency | Use Luna when delegation is cheaper than loading the raw output into Fable |
| Spawning a Claude subagent or fork for delegable work | Always Codex; the sole exception is a fable-tier agent for genuinely hard judgment, sparingly |
| Reading the transcript/log into context | Read the `-o` file only |
| Reading source files Codex could summarize | Fable reads diffs, `-o` files, and files it must itself edit; bulk reading is a delegation |
| Vague scope ("look into X") | State deliverable shape and behavior scope explicitly |
| Trusting Codex edits blind | Fable reviews the diff (`git diff`) before building on it |
| Defaulting to Sol for every unit | Luna is the default; escalate to Terra then Sol on evidence |
| Using max effort, Terra xhigh, or broad Sol fan-out by default | Escalate through the approved tiers only when evidence or risk justifies the usage |
