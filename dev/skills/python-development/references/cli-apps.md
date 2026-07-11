# CLI applications

Command-line interfaces are user interfaces. Keep command functions thin,
validated, and easy to test.

## Command shape

- Parse arguments at the boundary.
- Convert arguments into typed values early.
- Delegate business logic to functions that do not depend on CLI framework
  objects.
- Return meaningful exit codes.
- Write machine-readable output to stdout when promised.
- Write diagnostics, progress, and errors to stderr.

## Framework choice

Use Typer for CLI applications. Typer keeps command signatures close to typed
Python functions and supports clear command tests.

Keep command functions thin. Delegate business logic to functions that do not
depend on Typer objects so tests can cover behavior directly.

## Testing

Test CLI behavior through the command entry point or framework test runner when
possible. Also test the underlying business logic directly without CLI parsing.

Check:

- argument validation
- exit code
- stdout and stderr separation
- config precedence
- error messages

## Sources

- Typer docs: <https://typer.tiangolo.com/>
- Typer testing docs: <https://typer.tiangolo.com/tutorial/testing/>
- pytest output capture: <https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html>
