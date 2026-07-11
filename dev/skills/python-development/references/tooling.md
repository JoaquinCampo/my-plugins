# Tooling

Tooling should make the easy checks automatic so human review can focus on
contracts, correctness, and design. Use the house tools uniformly unless the user
explicitly asks for a migration assessment rather than a change.

## Formatting and linting

Discover configured Ruff settings before running checks. Ruff is the formatter,
import sorter, and linter for this skill. Treat other formatter or linter config
as migration evidence to report, not as an equal default.

Guidance:

- Use `uv run ruff format` for formatting.
- Use `uv run ruff check` for linting.
- Use the project's Ruff rule set when present.
- Do not argue with Ruff-owned style in human review.
- Treat unsafe auto-fixes as code changes that need review.
- Treat preview rules or formatter behavior as opt-in and potentially unstable.
- Prefer adding or adjusting tooling only when repeated human comments show a
  rule should be automated.

## Type checking

Use MyPy as the type checker. Discover project MyPy configuration before running
it. Treat other checker config as migration evidence to report, not as an equal
default.

Good type-checking practice:

- Keep annotations useful at boundaries and public APIs.
- Avoid broad `Any` leaks unless there is a boundary or gradual-typing reason.
- Add ignores narrowly, with a reason when project style expects it.
- Prefer simplifying code over fighting the checker with casts.

## Pre-commit and CI

If a repo uses wrappers or CI jobs, inspect them for parity with `uv run ruff
check`, `uv run ruff format`, `uv run mypy`, and `uv run pytest`. Use the house
commands locally when possible and state any gap between local and CI coverage.

## Sources

- Ruff docs: <https://docs.astral.sh/ruff/>
- Ruff fixes: <https://docs.astral.sh/ruff/linter/#fixes>
- Ruff preview: <https://docs.astral.sh/ruff/preview/>
- mypy docs: <https://mypy.readthedocs.io/>
- pytest docs: <https://docs.pytest.org/>
