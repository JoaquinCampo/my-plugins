---
name: docs-lookup
description: Catch-all for any ElevenLabs question not covered by a more specific skill. Use for API endpoint reference lookups, forced alignment, models and pricing pages, changelog, or any new ElevenLabs product. Finds the right documentation page and fetches it as clean markdown.
---

# ElevenLabs Docs Lookup

The complete docs index lives at https://elevenlabs.io/docs/llms.txt
(roughly 760 lines, 112KB). Never read it whole into context; filter it in
the shell and only the matching lines come back:

    curl -sf https://elevenlabs.io/docs/llms.txt | grep -iE '<topic-regex>'

Then fetch only the specific pages needed (index URLs already end in `.md`
and return clean markdown):

    curl -sf <page-url>

## Tips

- API endpoint reference pages live under
  `https://elevenlabs.io/docs/api-reference/` (about 310 pages). Grep for the
  resource name, e.g. `grep -iE 'speech-to-text|transcript'`.
- Any docs section has its own small index; append `/llms.txt` to the section
  URL, e.g. `https://elevenlabs.io/docs/eleven-agents/llms.txt`.
- Any docs page has a markdown version; append `.md` to its URL.
- Never fetch `https://elevenlabs.io/docs/llms-full.txt` (the entire docs in
  one file; far too large).
- If curl fails, fall back to WebFetch on the same URL.
