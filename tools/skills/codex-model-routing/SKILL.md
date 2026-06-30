---
name: codex-model-routing
description: Use when spawning Codex subagents or Codex threads and choosing among gpt-5.5, gpt-5.4, gpt-5.4-mini, and Spark. Use this with orchestrating-subagents whenever delegation involves Codex model overrides, reasoning effort, Explore agents, checker/fixer loops, or fan-out work.
---

# Codex Model Routing

## Principle
Always choose the cheapest model that can reliably do the delegated job, and make the choice explicit in the spawn payload or prompt. The main thread keeps judgment and synthesis; subagents return compact evidence, patches, or verdicts.

Use the exact model ids exposed by the current Codex runtime. In recent Codex sessions, Spark has appeared as `gpt-5.3-codex-spark`.

## Routing table

| Model | Use for | Avoid for | Effort |
| --- | --- | --- | --- |
| `gpt-5.3-codex-spark` | Explore agents, grep-heavy reconnaissance, inventory, log reading, first-pass triage, many cheap parallel workers, bounded mechanical edits | Architecture calls, final verdicts, tricky implementation, ambiguous debugging | `medium` by default, `low` for purely mechanical scans |
| `gpt-5.4-mini` | Reliability bump over Spark, small implementation tasks, fixing exact review findings, second-pass review, summarizing worker outputs, moderate code edits | Hard design calls, broad refactors, security-critical final review | `medium` by default, `high` for compact but tricky review |
| `gpt-5.4` | Substantive coding, integration, design decisions, complex diff review, normal maker/checker work when mini is too thin | Very high-stakes architecture synthesis where 5.5 is warranted | `medium` by default, `high` for hard analysis |
| `gpt-5.5` | Main-thread synthesis, architecture, ambiguous debugging, high-risk design, final review, hard judgment | Cheap fan-out, mechanical exploration, routine fixes | `medium` or `high`; use sparingly for subagents |

If Spark is unavailable, route Spark-shaped tasks to `gpt-5.4-mini`.

## Spawn policy
Every Codex delegation plan should state:

- `model`
- `reasoning_effort`
- role
- exact paths
- what to inspect first
- user constraints
- expected return shape

Do not omit the model unless the platform forbids model overrides. If the platform forbids overrides, say that in the plan and keep the task bounded.

## Explore defaults
For Codex Explore-style work, prefer Spark first:

- repo or file reconnaissance
- finding examples of a pattern
- reading logs or terminal output
- collecting candidate files and line references
- broad shallow review before a focused checker

Escalate to `gpt-5.4-mini` when Spark has to reason across several files or produce a small patch. Escalate to `gpt-5.4` when the worker owns a meaningful implementation or design choice.

For Claude-style Explore agents, keep using Haiku unless the user specifies otherwise. This skill only defines the Codex model mapping.

## Prompt shape
Use self-contained prompts. Include enough context that the subagent does not need the main thread.

```json
{
  "model": "gpt-5.3-codex-spark",
  "reasoning_effort": "medium",
  "role": "Explore agent",
  "task": "Find every place this project defines subagent model routing. Return paths, approximate lines, and a compact summary.",
  "paths": [
    "/absolute/path/to/repo"
  ],
  "constraints": [
    "Locate by content; line numbers are approximate.",
    "Return evidence only; do not edit files."
  ]
}
```

For maker/checker/fixer loops:

- Maker: `gpt-5.4` for substantive work, `gpt-5.4-mini` for bounded edits.
- Checker: match or exceed the maker for difficult review; use `gpt-5.5` only for hard final judgment.
- Fixer: `gpt-5.4-mini` for exact findings, `gpt-5.4` when fixes require design judgment.
- Verifier: Spark or shell checks when verification is mechanical.

## Completion check
Before dispatching, verify that every worker has:

- explicit model and reasoning effort
- a bounded task
- exact inputs
- a return format that is smaller than the context it consumes
- no need to ask clarifying questions
