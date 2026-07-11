# Library notes

This file records the house Python stack. Apply these defaults uniformly for new
work. If a repository conflicts with them, report the mismatch and ask whether to
migrate or make a minimal compatibility change.

## uv

Use `uv` for project workflows:

- `uv run` to run commands in the project environment.
- `uv sync` to synchronize the environment from the lockfile.
- `uv lock` to update the lockfile.
- `uv add` and `uv remove` for dependencies when dependency changes are in
  scope.
- `uv build` for build validation when packaging is in scope.

## Ruff

Use Ruff for formatting, import sorting, and linting:

- `uv run ruff format` to format.
- `uv run ruff check` to lint.

Use the repository's Ruff configuration when present. Treat fixes according to
Ruff's safety model. Safe fixes are intended to preserve behavior; unsafe fixes
may change behavior and should be reviewed like code changes.

## MyPy

Use MyPy for type checking:

- `uv run mypy` for the configured type-check target.

Prefer useful boundary annotations, avoid broad `Any` leaks, and simplify code
before fighting the checker with casts.

## pytest

Use pytest for tests:

- `uv run pytest` for the full configured test suite.
- `uv run pytest path/to/test.py::test_name` for focused checks.

Prefer behavior tests over tests that only assert an internal method was called.

## Pydantic v2

Use Pydantic for runtime validation, parsing, serialization, and boundary data.
Prefer simple models, plain fields, `Field`, and clear validators. Avoid fancy
logic on Pydantic models unless it protects a real invariant.

## pydantic-settings

Use `pydantic-settings` for environment-backed settings and configuration
objects. Keep settings models simple and keep business logic outside them.

## Typer

Use Typer for CLIs. Keep command functions thin and delegate business logic to
testable helpers.

## Loguru

Use Loguru for logging. Prefer structured messages with contextual values. Do not
log secrets. Avoid noisy logs in tight loops. For exception logs, use
`logger.opt(exception=True).error(...)`, never `logger.error(..., exc_info=True)`.

## FastAPI

Use Pydantic models at request and response boundaries. Keep route handlers thin
and move business logic into testable functions or services.

## Sources

- uv docs: <https://docs.astral.sh/uv/>
- Ruff docs: <https://docs.astral.sh/ruff/>
- Ruff fixes: <https://docs.astral.sh/ruff/linter/#fixes>
- MyPy docs: <https://mypy.readthedocs.io/>
- pytest docs: <https://docs.pytest.org/>
- Pydantic docs: <https://docs.pydantic.dev/latest/>
- Pydantic settings docs: <https://docs.pydantic.dev/latest/concepts/pydantic_settings/>
- Typer docs: <https://typer.tiangolo.com/>
- Loguru docs: <https://loguru.readthedocs.io/>
- FastAPI docs: <https://fastapi.tiangolo.com/>
