---
name: voices
description: Use when working with ElevenLabs voices beyond plain TTS. Covers voice cloning (instant and professional), voice design from text prompts, voice remixing, the Voice Library, and creating, customizing, sharing, or managing voices via the ElevenLabs API.
---

# ElevenLabs Voices

Current docs index for voice cloning, voice design, and the Voice Library:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/eleven-creative/voices/llms.txt || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/eleven-creative/voices/llms.txt"`

Also relevant; fetch directly if the task needs them:

- https://elevenlabs.io/docs/overview/capabilities/voices.md (voices capability overview)
- https://elevenlabs.io/docs/overview/capabilities/voice-remixing.md (voice remixing)

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- For voice API endpoints (create, edit, share, list), grep the full index:
  `curl -sf https://elevenlabs.io/docs/llms.txt | grep -i 'voice'`
- If a fetch fails, fall back to WebFetch on the same URL.
