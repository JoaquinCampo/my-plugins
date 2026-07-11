# Configuration and settings

Configuration is a boundary. Treat it like input from users, files, the
environment, deployment systems, or command lines.

## Precedence

Discover the project's precedence before changing settings behavior. When the
project does not define one, use a simple documented order such as:

1. explicit function or CLI arguments
2. environment variables
3. config files
4. application defaults

Do not silently let two sources fight. If precedence is ambiguous or conflicting
sources define the same value, fail fast with a clear error unless the precedence
rule is explicit.

## Validation

Validate configuration at the boundary and expose typed values internally. Use
`pydantic-settings` for application settings and environment-backed
configuration objects.

Keep settings models simple. Use explicit fields, `Field`, and small validators
for shape checks. Avoid hiding business logic inside settings models; put that
logic in ordinary functions or services.

## Secrets

- Do not print or log raw secrets.
- Keep secret values out of repr strings and exception messages.
- Prefer references to secret names or sources over secret contents.
- Treat config dumps as potentially sensitive.

## Errors

Configuration errors should name the setting, source, and expected shape when
safe. They should not require reading a traceback to understand what to fix.

## Sources

- Pydantic settings docs: <https://docs.pydantic.dev/latest/concepts/pydantic_settings/>
- Python os.environ docs: <https://docs.python.org/3/library/os.html#os.environ>
- Pydantic fields docs: <https://docs.pydantic.dev/latest/concepts/fields/>
