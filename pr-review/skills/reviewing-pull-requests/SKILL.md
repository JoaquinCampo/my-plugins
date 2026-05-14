---
name: reviewing-pull-requests
description: Use when about to review a pull request, leave comments on a diff, approve a merge, or self-review your own changes before sending them. Applies to any PR from a typo fix to a migration, and to both human reviewers and AI sub-agents.
---

# Reviewing Pull Requests

A doctrine for spending review attention where it pays. Routes depth from risk, not habit. Refuses to generate noise.

This skill is the philosophy. For the operational mechanics of fetching a GitHub PR and comparing it to this codebase's conventions, see the project's `pr-review` skill. Use both for a real review.

## When to use

- Reviewing someone else's PR.
- Self-reviewing your own diff before opening a PR.
- Producing automated review comments (sub-agent or CI bot).

Not for: writing the change, writing tests, deciding whether to open a PR.

**If you are an AI agent: this skill alone is insufficient.** Also load `pr-review-agent-tactics`. The two skills are designed to be loaded together: this one is the philosophy (what to look for, what to ignore, how to comment); the other is how to *operate* as an agent while applying it (context budget, tool escalation, sub-agent dispatch, when to recuse, agent-specific failure modes). Loading only one produces incomplete reviews: doctrine without tactics burns context on the wrong things; tactics without doctrine is mechanically efficient noise.

## Core doctrine

Three lines. Everything else in this skill elaborates them. If you forget the skill, keep these.

1. **Triage by blast radius; depth follows risk, not habit.**
2. **Form expectations before reading the diff.**
3. **Say nothing that won't change the code.**

## Triage first (60 seconds, every PR)

Classify the PR before reading code. Take no more than 60 seconds.

- **PR description and linked ticket:** read these first. They feed `predict-then-diff` and reveal whether the stated goal matches the diff. A PR with no description or a description that doesn't match the diff is its own finding.
- **Size:** lines, files, modules crossed.
- **Risk surface:** does it touch any of these? data model, schema migrations, auth, money or billing, public API contract, concurrency, new external dependency, infra, security boundaries, anything irreversible.
- **Reversibility:** can this be rolled back cleanly? Database migrations and external API changes often can't.
- **Blast radius:** how many call sites depend on what's changing?

Assign one of three tiers. The tier decides everything downstream.

## Route depth by risk tier

| Tier | Triggers | Required moves |
|------|----------|---------------|
| **Trivial** | <50 lines, no risk surface, fully reversible, single module | Skim for obvious defects. Approve or comment. Done. |
| **Standard** | Default. Anything not Trivial or High-risk. | `predict-then-diff` (mandatory). Apply relevant lenses. |
| **High-risk** | Any risk-surface trigger above, or >500 lines, or hard-to-reverse | `predict-then-diff`. Apply all lenses. Verify rollback path. Demand test plan if absent. Run it locally if behavior is unclear. |

If a PR mixes a Trivial change with a High-risk change, **stop and ask for a split.** Bundled PRs hide the high-risk part in the noise of the trivial one.

`predict-then-diff` is mandatory for Standard and High-risk tiers. Read the ticket or PR description first, form an expectation of what the diff should contain, then diff your expectation against reality. Surprises (things missing, things present that shouldn't be) are the highest-signal moments in review. Without this, you become a spell-checker for the author's framing.

## Premise check (before any implementation review)

Before applying lenses to the code, interrogate the premise. Cheap, often surfaces the highest-leverage findings.

- **Should this exist at all?** Is the stated goal real, or a symptom-fix that should be solved upstream?
- **Is this reinvention?** Does the codebase already do this? Grep for the new function name, the new pattern, the new abstraction. "We already have X" is a real finding.
- **Does a library already do this well?** If the PR rolls a custom retry loop and `tenacity` is a dep, or a custom parser when `pydantic` would do it, say so.
- **Is the goal correct?** Does the description match the diff? If they diverge, fix the description or the scope before reviewing the code.
- **Chesterton's Fence.** If the PR removes or rewrites something whose purpose isn't immediately obvious, find the commit that introduced it (`git log -S` or `git blame`) before approving the removal.

If the premise doesn't survive, stop. Address the premise; do not review the implementation of a wrong thing.

## Review lenses

Apply these to Standard and High-risk PRs in roughly this order. Skip lenses that don't apply.

1. **Data model and shape.** Is the structure right? Does it remove special cases or create them? For migrations: are upgrade and downgrade both correct? Does data survive the round trip?
2. **Module boundaries and contracts.** Is layering respected (no DB queries in routers, no business logic in repositories)? Does the public surface match how callers will actually use it? Could a type encode an invariant that's currently a comment?
3. **Scope.** Every changed line should trace to the stated goal. Drive-by refactors, renames, and "while I'm in here" cleanups in a feature PR get rejected or split.
4. **Failure modes.** What happens on network drop, malformed input, partial write, downstream timeout, missing permission? Are errors surfaced where a human can act on them, or swallowed?
5. **Tests.** Do they cover intent (a behavior the code now guarantees) or just lines? Would the test fail if the implementation were quietly replaced by `return True`? Are integration tests hitting real systems where it matters?

## Deliberately ignore

These are not review work. Spending attention on them is performing diligence, not practicing it.

- **Style, formatting, import order.** If a real style issue isn't caught by lint or formatter, the fix is to update the tooling, not to comment.
- **Naming nits**, unless the name is actively misleading (e.g., `delete_user` that actually disables them).
- **"I would have written it differently."** Without a concrete defect, this is preference, not review.
- **Speculative "what if we need X later."** YAGNI. File an issue if you genuinely believe the future requirement; do not block this PR.
- **Pre-existing problems** unrelated to the change. Mention separately; do not pile onto this PR.

## Named techniques

Reach for these when the situation calls for it.

- **Predict-then-diff.** Read ticket, expect, compare. Mandatory for Standard and High-risk tiers per the routing table.
- **Tests-first read.** In unfamiliar code, start in the test files. Tests encode intent better than prose comments.
- **Walk one call site.** Pick a new public function. Find a real caller in the codebase. Verify the API shape matches actual usage.
- **Migration both-ways.** For schema or data migrations: run upgrade, run downgrade, verify data is intact. Do not trust autogenerated migrations.
- **Run it locally.** If you cannot infer behavior from reading, stop reading and exercise the code. Reading-only review of behavioral code is guessing.
- **Type the invariant.** If a comment says "must not be empty" or "callers must X first," propose encoding it in the type system instead.

## Comment ROI and severity labels

Before posting any comment, ask: *will this change the code, or am I performing review?* If the second, delete it.

Tag every comment with one severity:

- **must-fix:** blocks merge. Must include the concrete failure mode, the code path, and the minimal fix if obvious.
- **should-fix:** mergeable as-is, but the risk is real. State the risk.
- **nit:** optional, label explicitly. Default is don't post. Nits in aggregate train the author to ignore real feedback.
- **question:** post only if the answer would change your review. "Curiosity" questions are noise.

**Quality bar for `must-fix`:**
1. The concrete failure mode (what breaks).
2. The code path or user-visible behavior where it breaks.
3. The minimal fix, if obvious.

Missing any of these and it's not yet a `must-fix`. It's a `question` until you've done the work.

## Required review output (tier-scaled)

Universal "evidence checked" forms become hallucinated boilerplate on small PRs. Scale the output to the tier.

- **Trivial:** `Tier: trivial. No findings.` (or list any trivial defects found).
- **Standard:** Tier label + which lenses applied + findings only, severity-labeled. No narrative restating what the PR does.
- **High-risk:** Tier label + per-lens evidence + explicit rollback or test verification + findings. State what you verified, not just what you looked at.

**Standard and High-risk reviews must end with a "what I did not verify" line.** Examples: "Did not run the migration locally", "Did not exercise the streaming path under load", "Did not check call sites in the lambda handlers." Surfacing scope is more honest than burying it. Reviewers who don't declare gaps are pretending coverage they don't have.

In all tiers: **do not summarize what the PR does.** The author wrote that already, and the diff is right there. Comments exist to change code or record verification. Praise, summary, and acknowledgment are noise.

## Responsible non-review (a valid verdict)

"I cannot review this responsibly" is a legitimate output. Use it when:

- The PR touches a domain you cannot ground-truth (cryptography, billing math, infra you cannot exercise, security-critical paths without a runtime).
- You don't have the context to judge the change (you don't know the system well enough, the area is new, the design decisions assume knowledge you lack).
- The diff's correctness depends on runtime, integration, or operational evidence you cannot collect.

State what you inspected, what you could not verify, and who or what should verify it. Recusing is not a failure; producing a confident-sounding review you cannot back is.

## Stop rules

Stop reviewing and act when:

- **Scope and stated goal diverge.** Ask for a split, or for the description to match the diff.
- **The data model is wrong.** Stop reviewing surface implementation. The fix is upstream.
- **Behavior can't be inferred from the code.** Run it, or demand a test plan. Do not approve guessing.
- **All your comments are preference-level.** Approve, post no comments, move on. Holding a PR hostage for preferences is the worst failure mode in review.
- **You don't understand what the PR is doing.** Do not approve. Ask the author for context, in private if the gap is large.

## Anti-patterns

Named so they can be called out without ambiguity.

- **Line-by-line reading** instead of shape-first triage. Trains you to be a syntax checker.
- **Diff-bound thinking.** Reading only the hunk shown in the diff, never the surrounding file. Open the file at least once for any non-trivial hunk; the context outside the diff usually changes the verdict.
- **Style and naming debates.** Move to tooling or drop.
- **Vague comments:** "feels off", "could be cleaner", "consider refactoring." Either name the defect or don't post.
- **Mid-PR refactor demands.** "While you're here, can you also..." No. File a follow-up.
- **LGTM without reading.** A review that wasn't done is worse than no review; it confers false legitimacy.
- **Walking a checklist on a trivial PR** to feel thorough. Performance, not review.
- **Praise, summary, and acknowledgment comments** ("Nice approach", "Great test coverage", restating the diff). Default failure mode of AI reviewers and humans under social pressure. Comments exist to change code or record verification.
- **Hostage-taking for preference.** Blocking on personal style is an admission that you can't tell preference from defect.
- **Hallucinated evidence in the output.** Writing "tests verified, rollback checked" without doing it. Worse than skipping the verification, because it lies on the record.

## Red flags (self-check during review)

If any of these match while you're reviewing, stop and recalibrate:

- You're on line 200 of a diff and you haven't decided the tier yet.
- You're typing a comment that summarizes what the code does.
- Your only comments are nits.
- You're about to ask the author to refactor something unrelated to the PR.
- You're about to write "LGTM" on a 500-line diff you read in 90 seconds.
- You're writing evidence ("verified migration", "checked call sites") that you did not actually verify.

## What NOT to include in any expansion of this skill

If a future maintainer is tempted to add these, push back.

- A mandatory N-phase workflow applied to every PR. Triage is mandatory; everything else routes from it.
- Style rules. Lint's job.
- A growing "things to check" template. Inventories rot. Lenses + doctrine + stop rules are the bound.
- Universal evidence forms regardless of tier. Cargo cult on trivial PRs.
- Tone or kindness rules beyond "comments must be specific." Communication norms belong elsewhere.
