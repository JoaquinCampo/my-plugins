# Style and naming

Style should make code easier to read and maintain. Prefer tool-enforced style
where possible, and spend human attention on names and structure that tools
cannot judge.

## House style

Optimize for clarity, safety, and usefulness.

- Prefer beautiful, explicit, simple, flat, sparse, readable code.
- Choose one obvious path and explain the rationale in one to three bullets when
  it helps the reader.
- Apply rules uniformly. Do not invent ad hoc exceptions.
- Surface uncertainty and failure modes with clear, actionable messages.
- Ask a crisp clarifying question when ambiguity would change the safe answer.
- If a method is hard to explain briefly, propose a simpler plan.

## Names

- Use names that reveal intent.
- Avoid shadowing builtins such as `id`, `type`, `list`, `dict`, and `file`.
- Avoid single-letter names except for tiny local scopes where the convention is
  obvious.
- Name booleans as predicates when possible, such as `is_ready` or `has_cache`.
- Name functions after what they do, not how they are implemented.

## Human review scope

Do not bikeshed formatting, import order, or quote style when tools own those
choices. Do comment when a name is actively misleading or a structure hides the
reader's path through the code.

## Sources

- PEP 8: <https://peps.python.org/pep-0008/>
- Google Python style guide: <https://google.github.io/styleguide/pyguide.html>
