---
name: pr-review-agent-tactics
description: Use when an AI agent is itself performing a pull request review (not coaching a human, not fetching the PR). Covers agent-specific tactics: context budget, tool escalation triggers, Explore subagent dispatch (single sidecar and parallel fan-out), when to emit "I cannot review this responsibly", auto-memory integration, and agent failure modes (confabulation, tool-call theater, delegated certainty laundering, evidence laundering, patch sycophancy, premature fan-out). Complements reviewing-pull-requests (universal doctrine) and pr-review (operational PR fetch + per-layer comparison).
---

# PR Review: Agent Tactics

Agent-specific tactics that supplement the doctrine in `reviewing-pull-requests`. Treats context as a scarce resource, treats sub-agents as evidence sources not authorities, names the failure modes that only an LLM-shaped reviewer falls into.

## 1. Scope and load order

Load this skill when:
- You are an AI agent actually performing the review (forming a verdict, writing the comments).
- Not for: coaching a human reviewer, or fetching/checking out the PR (that's `pr-review`).

**This skill REQUIRES `reviewing-pull-requests` to also be loaded.** That parent doctrine contains the philosophy of review: triage by blast radius, predict-then-diff, review lenses (data model, boundaries, scope, failure modes, tests), the things to deliberately ignore, comment severity labels, tier-scaled output, premise check, responsible non-review, stop rules, anti-patterns. None of that is restated here. This skill only adds the *operational layer* for agents on top of that doctrine.

If you find yourself reading this skill without the parent doctrine loaded, stop and load the parent first. The two are designed as one review system, split for legibility: philosophy in one file, agent operations in the other.

## 2. Responsible non-review (first-class verdict)

`I cannot review this responsibly` is a legitimate output. Use it when:

- The PR touches a domain you cannot ground-truth (cryptography, billing math, infra you can't exercise, security-critical paths without a runtime to test against).
- Your context is exhausted before reaching the load-bearing files.
- The diff's correctness depends on runtime, integration, or operational evidence you cannot collect.

Output template:

```
Cannot review responsibly.
- What I inspected: <files / paths>
- What I could not verify: <specifics>
- Who or what should verify: <person / tool / test plan>
```

**Anti-pattern:** emitting LGTM or nits to produce *some* output when you should be recusing. This is the #1 agent review failure.

## 3. Premise check (callback to parent doctrine)

Before reading the diff, run the premise check from `reviewing-pull-requests`: is the goal correct, is this reinventing standard behavior, does a library or existing codebase pattern already solve it. Agents skip this faster than humans because the prompt orients them toward the diff in hand. Do not start lens-by-lens review until the premise survives.

## 4. Risk tier and review shape

Inherit the tier from the parent doctrine (Trivial / Standard / High-risk). Agent-specific addition: **pick the minimum tool shape needed for the tier.**

- **Trivial:** direct reading only. No grep, no subagent, no web fetch. If you reach for a subagent on a Trivial PR, you've misclassified.
- **Standard:** direct reading + targeted grep + occasional `Explore` subagent for broad questions.
- **High-risk:** direct reading + multiple targeted greps + sidecar verification or review fan-out + (if the area is genuinely new) one web fetch for the canonical library or RFC.

If the tier and the tool shape don't match, you're either over-spending (subagents on a typo PR) or under-spending (3 greps on a migration).

## 5. Context budget

Top-level concern, orthogonal to risk tier. Tier sets *effort*; budget tracks the *resource*.

Rules:
- Estimate budget before opening files. Reserve roughly 30% for the final synthesis and write-up.
- Prefer subagent dispatch over reading 5+ large files into main context. Subagents return summaries; reads return raw content.
- If you are about to `Read` a >500-line file purely to confirm one symbol or pattern, use grep or an `Explore` subagent instead.
- If context is insufficient for the load-bearing evidence, **abort to section 2** (responsible non-review). Do not skim and pretend you reviewed.

Concrete cue: if you find yourself re-reading the same file in the same review, you've already lost budget discipline.

## 6. Tool escalation triggers

Trigger-shaped, not threshold-table. Named triggers:

- **Broad and shallow** ("is X convention followed everywhere?"): dispatch an `Explore` subagent with `model: "haiku"`, single bounded query.
- **Deep and narrow** ("does this migration break N specific call sites?"): grep call sites yourself, then `Read` the 2-3 hottest. Don't fan out for a question you can answer in 2 reads.
- **Unknown module shape** ("I don't know what this module does"): `Explore` subagent first to map it, then targeted `Read` on what matters.

Single quantitative rule: **after 2 failed searches for the same hypothesis, the hypothesis is wrong.** Stop guessing names. Re-read the diff or escalate to a subagent.

**Sidecar verification:** a single delegated question (e.g., "verify this migration is reversible by reading the downgrade") is allowed under this section. One subagent, one bounded question, evidence returned. This is not fan-out (see section 7); it's a single tool call to a more capable searcher.

## 7. Review fan-out

A named pattern for dispatching **2+ independent review questions in parallel**, in a single message. Use when the PR is Standard or High-risk AND the review naturally splits into independent axes.

**One sub-agent per applicable doctrine lens.** The review lenses in `reviewing-pull-requests` ARE the specialist archetypes. For each lens that applies to this PR, dispatch one sub-agent whose entire job is to apply that lens and nothing else. Codebase-agnostic; the dispatching agent adapts the prompt to whatever stack and patterns are actually in play.

Specialist archetypes mapped to doctrine lenses:

| Specialist | Doctrine lens | Dispatch when |
|---|---|---|
| Data model specialist | Data model and shape | The PR changes persistent state, schemas, types that flow across boundaries, or migrations |
| Boundary specialist | Module boundaries and contracts | The PR changes a public API, exported signature, event schema, or layering |
| Failure mode specialist | Failure modes | The PR adds new code paths, error handling, retry/timeout/fallback logic, or concurrency |
| Tests specialist | Tests | The PR has non-trivial logic, or adds/changes tests, or claims coverage that needs verification |

Dispatch only the specialists whose lens applies to the actual change. A pure refactor doesn't need a data model specialist; a docs-only PR doesn't need any specialists.

**Prompt skeleton (the dispatching agent fills the slots):**

```
You are reviewing a pull request through the <LENS> lens only.

PR diff or path: <ref>
Codebase context: <stack, relevant patterns, framework idioms>
Lens questions (from reviewing-pull-requests doctrine):
  <one or two lens-specific questions, lifted from the doctrine>

Output:
- Severity-labeled findings with file:line references
- "What I did not verify" line

Constraints: no narrative, no summary of the PR, no praise. If you cannot apply
the lens responsibly, emit "Cannot review responsibly" with what you inspected
and what blocked you.
```

Rules:
- Questions must be **independent** (no shared state between subagent results).
- Questions must be **bounded** (each sub-agent gets one lens and a length cap).
- **The main agent owns the verdict.** Subagent output is evidence, not authority.
- The main agent's synthesis is where cross-lens *interactions* are found ("data model widened the type, boundary specialist found a caller that depends on the narrow type, therefore the caller breaks"). Specialists do not talk to each other; the main agent is the synthesis point.
- Do not fan out on a 20-line PR.

Anti-pattern: "specialist A returned 'looks fine,' therefore the lens is fine." See section 10 (`delegated certainty laundering`).

## 8. Memory integration

This project has an auto-memory system. Use it.

**Read before reviewing.** Scan auto-memory for related conventions, prior reviews of the touched modules, recurring bug patterns. If a memory changes your verdict, cite it in the comment.

**Write after reviewing — surprise findings only.** If the review surfaced:
- An unknown convention you didn't know was load-bearing,
- A recurring bug pattern across multiple files,
- A constraint that's not encoded in code,

then write a memory entry. Use the project's memory format (slug, type, description, body with `[[link]]` cross-refs).

**Do not write memory for:** "this PR did X." PR-specific summaries belong in the PR thread, not in durable memory.

Anti-pattern: re-deriving the same convention every review because you skipped the memory read.

## 9. Output discipline

### Where the output goes (destination)

**Default: report to the user in conversation. The user posts.**

The agent produces the review as a brief in the chat. The user reads it, edits or copies, and decides what (if anything) lands on GitHub. The user is the gate. This is the default for every review regardless of tier.

**Never autonomously, even if the verdict is unambiguous:**
- `gh pr review --approve` — approval changes merge state. Human call, always.
- `gh pr merge` — merging.
- `gh pr close` / `gh pr reopen` — lifecycle changes.

**Only with explicit per-PR authorization from the user:**
- Posting line comments via `gh api repos/.../pulls/<n>/comments` or `gh pr review --comment`.
- `gh pr review --request-changes` (blocks merge; still requires the explicit ask).

Authorization granted for one PR does NOT carry to the next. If unsure whether you have authorization, you don't. Report to the user and ask.

### Final review message structure (in this order)

1. **Verdict.** Approve / request changes / cannot review responsibly. One line.
2. **Findings.** Severity-labeled, `file:line` references, concrete failure mode. (Parent doctrine governs the format and severity labels.)
3. **Evidence.** What you verified, with the tool/path: "ran `gh pr diff`", "read `migrations/versions/<file>.py` lines 23-47", "subagent A confirmed downgrade is symmetric." Cite, don't summarize.
4. **Unverified scope.** Explicit list of what you did NOT verify and why (out of scope, no runtime, no permission, ran out of budget). Critical — this is where agents pretend they did more than they did.
5. **Memory citations.** If a memory shaped your verdict, name it.

Do not include: a recap of what the PR does, praise, acknowledgment, or your tour of which files you opened.

## 10. Agent failure modes (additive to parent's anti-patterns)

Named so they can be called out without ambiguity.

- **Confabulation under budget pressure.** As context fills, agents invent file contents. Hard rule: if you did not `Read` it, you have not seen it. State that.
- **Tool-call theater.** 15 greps to look thorough when one would do. Quality of question, not count of calls.
- **Delegated certainty laundering.** A subagent returned a hedged answer ("probably fine, did not check X"). You report it in your verdict as "verified." That is laundering their uncertainty into your confidence. State the subagent's exact qualifications.
- **Evidence laundering from snippets.** Citing a 3-line grep match as if you read the surrounding file. If the match is load-bearing, open the file.
- **Patch sycophancy.** "Nice cleanup", "good catch", "elegant approach." Strip every instance. Comments exist to change code or record verification.
- **Premature fan-out.** Dispatching subagents on a PR small enough to read in one pass. Wastes user tokens, dilutes signal.
- **Single-pass certainty.** Emitting a verdict without re-reading the synthesis once. The re-read catches half-finished sentences and unsupported "verified" claims.

(`diff-bound thinking`, `LGTM without reading`, `hallucinated evidence` are named in the parent doctrine. Do not restate them here.)
