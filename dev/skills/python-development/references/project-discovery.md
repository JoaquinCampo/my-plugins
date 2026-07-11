# Project discovery

A general Python skill must discover repository facts before applying the house
stack. Do not assume Python version, line length, source layout, command wrappers,
or existing migration state before checking local files.

## Discovery order

1. Read local agent or contributor instructions.
2. Inspect `pyproject.toml` first when present.
3. Check secondary config: `setup.cfg`, `setup.py`, `pytest.ini`, `ruff.toml`,
   `.ruff.toml`, `mypy.ini`, CI workflows, Dockerfiles, and Makefiles. Treat
   config for other toolchains as migration evidence, not as an equal default.
4. Check human command surfaces: `README*`, `CONTRIBUTING*`, `Justfile`,
   `Taskfile.yml`, `Poe` or `poethepoet` tasks, `Makefile`, `package.json`
   scripts for mixed repos, `scripts/`, and CI job commands.
5. Identify `uv.lock` and any legacy lock files. Missing `uv.lock` or competing
   lock files are migration signals to report.
6. Inspect nearby code and tests for established patterns.
7. Prefer existing commands over invented commands.

## What to detect

- Supported Python versions, from `requires-python`, CI, Docker, or docs.
- Whether the project is already using `uv`, and what migration gaps remain.
- Source roots, such as `src/`, flat package layout, app directories, or
  notebooks.
- Test runner and markers.
- Formatter, linter, import sorter, and selected rule families.
- MyPy configuration and strictness.
- Runtime framework, such as FastAPI, Django, Flask, Typer, or batch scripts.
- Public API surface, CLI entry points, package data, and plugin hooks.

## Tool defaults when absent

When starting a new Python project or filling an unspecified gap, apply these
house defaults:

- `pyproject.toml` for project metadata and tool config.
- `uv` for environment, dependency, lock, build, and run workflows.
- Ruff formatter and Ruff linter for formatting, import sorting, and linting.
- pytest for tests.
- MyPy for type checking.

## Command selection

Prefer the house commands. Check task runners and scripts to understand wrappers
and CI parity, but do not invent alternate toolchains. Common commands include:

- `uv run pytest` for tests.
- `uv run ruff check` for linting.
- `uv run ruff format` for formatting.
- `uv run mypy` for types.
- `uv build` for builds.

State the command you ran and the result. If you cannot run the full project
check, run focused checks and explain the limitation.

## Sources

- Python Packaging User Guide, pyproject metadata:
  <https://packaging.python.org/en/latest/guides/writing-pyproject-toml/>
- uv project docs: <https://docs.astral.sh/uv/concepts/projects/>
- Ruff configuration docs: <https://docs.astral.sh/ruff/configuration/>
- pytest configuration docs: <https://docs.pytest.org/en/stable/reference/customize.html>
- MyPy configuration docs: <https://mypy.readthedocs.io/en/stable/config_file.html>
