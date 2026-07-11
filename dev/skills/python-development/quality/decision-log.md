# Decision log

This log records durable design decisions for the `python-development` skill.

## New skill instead of mutating the baseline

Decision: create `python-development` as a new general skill and leave the
review-oriented baseline as source material.

Reason: the baseline contained project-specific framing and review-only shape.
A new skill avoids compatibility breakage and keeps the general artifact clean.

## Discover before applying the house stack

Decision: make project discovery the first operating rule, then apply the house
stack uniformly.

Reason: Python projects differ in supported versions, source layouts, command
wrappers, and CI jobs. Discovery prevents blind edits, but it should surface
mismatches instead of silently replacing the house stack.

## House defaults are uniform

Decision: use uv, Ruff, pytest, MyPy, Pydantic, pydantic-settings, Typer,
Loguru, FastAPI, and scientific Python guidance as the house baseline.

Reason: the skill is meant to encode a consistent Python house style. When an
existing project conflicts, the assistant should name the mismatch and ask
whether to migrate or make a minimal compatibility change.

## References are modular

Decision: keep `SKILL.md` operational and move details into topic references.

Reason: agents need a fast playbook first. Deep citations and examples should be
loaded only when relevant to avoid context bloat.

## Review schema has a canonical home

Decision: `references/review-schema.md` is canonical for review finding fields,
categories, severity, and clean-review output.

Reason: duplicated schemas drift. `SKILL.md` keeps a summary, and the quality
harness checks alignment.

## Quality harness runs through uv

Decision: `quality/validate_skill.py` uses only the Python standard library, but
maintenance commands run it with `uv run`.

Reason: the validator should stay dependency-light, while the command style
still follows the house standard.

## Runnable fixtures are tiny and optional

Decision: include small runnable fixtures for high-risk sample tasks, while
keeping most fixtures descriptive.

Reason: runnable fixtures improve reproducibility, but a full fake ecosystem
would add maintenance cost and distract from the skill itself.

## Technical freshness needs source audits

Decision: add `quality/source-audit.md` and require source checks for strong
technical edits.

Reason: Python and tooling move quickly. The validator can catch structure and
drift, but it cannot prove that external advice remains current.
