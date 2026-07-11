# Dependency management

Dependencies are API, supply-chain, reproducibility, and maintenance decisions.
Do not add or upgrade them casually.

## Before changing dependencies

Check:

- whether the standard library already solves the problem well enough
- whether an existing dependency in the project already solves it
- `uv` configuration, `uv.lock`, and any legacy lockfile mismatch
- supported Python versions
- runtime versus development dependency group
- optional extra versus required dependency
- license and security posture when relevant

Avoid custom infrastructure when a maintained standard-library feature or
already-approved dependency provides the needed behavior. Avoid adding a new
dependency for a small helper that is simple, stable, and local.

## Lockfiles

Use `uv` for lockfile changes. If a dependency change is in scope, update
`uv.lock` with `uv lock` or the relevant `uv add` or `uv remove` command. If the
lockfile is not updated, state why.

## Dependency groups and extras

- Runtime requirements belong in standard project dependencies.
- Optional user-facing feature sets usually belong in optional dependencies or
  extras.
- Local development tools should use dependency groups managed by uv when the
  project supports them.

## Upgrade workflow

For upgrades, identify direct versus transitive changes, read relevant release
notes for risky packages, run focused tests around the dependency's integration,
and run broader validation before declaring success.

## Sources

- Python Packaging User Guide: <https://packaging.python.org/>
- Dependency groups specification: <https://packaging.python.org/en/latest/specifications/dependency-groups/>
- uv dependency docs: <https://docs.astral.sh/uv/concepts/projects/dependencies/>
