---
name: studio
description: Use when working with the ElevenCreative platform. Covers Studio video and audio production, audiobooks, Flows (visual AI pipelines), templates, transcripts, subtitles, voiceover studio, Audio Native web embeds, and Productions (human-edited services).
---

# ElevenLabs Creative Studio (ElevenCreative)

Current docs index for the ElevenCreative platform:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/eleven-creative/llms.txt || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/eleven-creative/llms.txt"`

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- For Studio API endpoints, grep the full index:
  `curl -sf https://elevenlabs.io/docs/llms.txt | grep -i 'studio'`
- If a fetch fails, fall back to WebFetch on the same URL.
