---
name: orchestrating-subagents
description: Use preemptively at the start of any session whose work decomposes into delegable units and whose main-thread context is worth protecting. A report, a large feature, a migration are examples, not the full set; the trigger is the shape (many token-heavy steps, compact results), not the task type. Also use whenever the user asks to delegate work to subagents. Invoke before context fills, not after.
---

# Orchestrating Subagents

## Overview
The main thread is the context manager: it holds the conversation, the judgment, and the
running state. In this mode, delegate by default. Offload reading, exploration, authoring,
and review to subagents; orchestrate, do not do the token-heavy work yourself. Apply this
preemptively: the point is that the main thread's context never fills, not that it recovers
once it has.

## How to offload
1. Shell reduction first for large data (grep/jq/awk to compact output): lossless, no
   spin-up, you control the filter.
2. Subagent when the reduction itself needs judgment, or the work is authoring or review.
3. Main thread only for decisions, user interaction, and synthesis of compact results.

## Maximize parallelism
The preference is always to maximize parallelism; deviate only by deliberate judgment, not
by habit. If a unit is genuinely hard enough that running it linearly gives better results
(tight coupling, each step reshapes the next), linear is fine, as a choice you can state.
- Plan as a dependency graph, not in document or list order: identify which units are
  independent, dispatch ready units together (parallel tool calls in one message), and
  hold back only what is genuinely blocked.
- Prefer pipelining over phase barriers: a unit's checker can launch as soon as its maker
  returns; waiting for a whole phase to finish is rarely necessary.
- A shared target file pushes toward serialization. Usually better: parallelize generation,
  serialize integration (workers return content or patches, one integrator applies them in
  order).
- Watch for serial dispatch by default: if you are sending one subagent, waiting, then
  sending the next, ask what actually depends on what.

## The maker/checker loop
For each substantive unit of work:
1. Maker (sonnet) authors it from a self-contained prompt.
2. Checker (a separate agent, never the maker) reviews it; escalate the checker's model to
   the difficulty of the check, opus only for genuinely hard audits.
3. Fixer (haiku or sonnet) applies the review's fixes by exact content match.
4. Verify the fixes landed (cheap agent or shell check).

## Every delegation prompt carries
- A role ("you are an expert in..."), exact file paths, and what to read first.
- The user's constraints pushed down (no em-dashes (--), style and format rules).
- "Locate by content; line numbers are approximate."
- The expected return shape (a list, a diff summary, a verdict).
- Permission to delegate further: tell the subagent it may spawn its own subagents when its
  task decomposes the same way, applying this same discipline (explicit model tier,
  self-contained prompts, maker/checker on substantive output).
- On substantive work: consult the `advisor` before committing to an approach and before
  declaring done.

## Rules
- Model explicit on every spawn (haiku mechanical, sonnet substantive, opus hard-only).
- For Codex model names and reasoning effort, use `codex-model-routing` alongside this skill.
- Fan out independent work in parallel.
- Delegation is recursive: subagents judge when their own task warrants further delegation.
- Keep running state outside your context (todo list or scratch file) so done work is never
  re-derived.

## Common mistakes
- Reading a big file in the main thread "just to check": reduce it with jq/grep or delegate.
- Letting the maker grade its own output.
- Vague worker prompts: workers cannot ask back, they guess.
- Waiting until context is strained to start delegating; by then the heavy reads already
  happened.
