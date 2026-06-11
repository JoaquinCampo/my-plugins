# elevenlabs

Full ElevenLabs coverage for building with the API, in one Claude Code plugin.

## What's inside

**Vendored official skills** (from [elevenlabs/skills](https://github.com/elevenlabs/skills), MIT):
`text-to-speech`, `speech-to-text`, `agents`, `music`, `sound-effects`,
`voice-changer`, `voice-isolator`, `speech-engine`, `setup-api-key`.

**Gap skills** (authored here; each injects a live docs index at invocation
via `!`-command preprocessing, then fetches specific pages on demand):
`voices`, `dubbing`, `text-to-dialogue`, `studio`, `admin`,
`sdks-integrations`, `image-video`, `reception-ai`, and `docs-lookup`
(catch-all for endpoints, forced alignment, and anything new).

## Updating the vendored skills

```bash
# from the repo root
./elevenlabs/scripts/sync-official-skills.sh
git diff elevenlabs/skills/   # review what changed upstream
```

The script copies by allowlist and never touches the gap skills. If upstream
renames a folder, the script fails loudly without changing anything; update
the `VENDORED` list in the script.

## Maintenance notes

- Gap skills depend on `https://elevenlabs.io/docs/.../llms.txt` URLs. If one
  starts printing `FETCH FAILED` on invocation, the section moved; find the
  new path in https://elevenlabs.io/docs/llms.txt and update the skill's
  injection line.
- Want Claude to *perform* audio actions (generate speech, transcribe, clone)
  instead of writing code? Use the official MCP server:
  https://github.com/elevenlabs/elevenlabs-mcp

## Credits

Vendored skills are (c) ElevenLabs, MIT licensed:
https://github.com/elevenlabs/skills
