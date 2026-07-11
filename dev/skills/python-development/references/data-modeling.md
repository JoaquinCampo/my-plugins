# Data modeling

Choose clear data shapes that make invalid states difficult and valid states
easy to read. Pydantic is the default named model for boundary data,
serialization, settings, and validated application records.

## Plain collections

Use plain `dict`, `list`, `tuple`, and `set` for local, obvious, short-lived
shapes. Promote them to a named Pydantic model when keys, positions, validation,
or serialization become important.

## dataclass

Use `@dataclass` only for internal records with named fields and little or no
runtime validation. Prefer Pydantic when data crosses a boundary, needs parsing,
or appears in serialized output.

Good defaults:

- `frozen=True` when instances should be hashable or immutable.
- `slots=True` for many instances or when accidental attributes would be bugs.
- `kw_only=True` when there are several fields or defaults make construction
  ambiguous.

Avoid putting complex business logic into dataclasses. Keep methods small and
close to the data's invariants.

## TypedDict

Use `TypedDict` for JSON-like dictionaries only when runtime validation is not
needed and static key checking is enough. Prefer Pydantic for request payloads,
response payloads, config fragments, and other boundary data.

Use `NotRequired` for optional keys rather than making every value optional.

## Pydantic

Use Pydantic v2 when runtime validation, parsing, serialization, or settings
integration matters. Keep models flat and validators simple. Prefer explicit
fields, `Field`, and simple validators over clever metaprogramming.

Avoid fancy logic on Pydantic models unless it protects a real invariant. Put
business logic in ordinary functions or services that are easy to test.

Use `pydantic-settings` for environment-backed settings and configuration
objects rather than hand-rolled environment parsing.

## Enum and StrEnum

Use `Enum` or `StrEnum` for named finite modes. Use `IntEnum` only when real
integer interop is required. For serialized values, spell strings explicitly,
especially with `StrEnum`.

## NamedTuple

Use `NamedTuple` only when tuple behavior is part of the intended API. For new
opaque result records, prefer a simple Pydantic model when validation or
serialization matters, otherwise use an internal dataclass.

## Sources

- dataclasses docs: <https://docs.python.org/3/library/dataclasses.html>
- typing TypedDict docs: <https://docs.python.org/3/library/typing.html#typing.TypedDict>
- enum docs: <https://docs.python.org/3/library/enum.html>
- Pydantic models docs: <https://docs.pydantic.dev/latest/concepts/models/>
- Pydantic settings docs: <https://docs.pydantic.dev/latest/concepts/pydantic_settings/>
