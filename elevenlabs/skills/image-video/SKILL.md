---
name: image-video
description: Use when generating or editing images and videos with ElevenLabs, including avatars (talking-head videos with synchronized lip movement). Covers image and video generation from text prompts and visual references.
---

# ElevenLabs Image and Video

All image, video, and avatar pages in the current docs index (some matched
lines are about video dubbing or translation; ignore those here, the dubbing
skill covers them):

!`curl -sf --max-time 15 https://elevenlabs.io/docs/llms.txt | grep -iE 'image|video|avatar' || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/llms.txt and search for image-video"`

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- If a fetch fails, fall back to WebFetch on the same URL.
