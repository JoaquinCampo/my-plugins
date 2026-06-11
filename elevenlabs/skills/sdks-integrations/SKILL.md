---
name: sdks-integrations
description: Use when integrating the ElevenLabs API through an SDK or quickstart. Covers the JavaScript, Python, React, React Native, Kotlin, and Swift SDKs, cookbook quickstarts for every capability, authentication, and choosing the right model.
---

# ElevenLabs SDKs and API Quickstarts (ElevenAPI)

Current docs index for SDK quickstarts and cookbooks:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/eleven-api/llms.txt || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/eleven-api/llms.txt"`

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- For raw endpoint reference, grep the full index for the resource name:
  `curl -sf https://elevenlabs.io/docs/llms.txt | grep -i '<resource>'`
- Platform integrations for voice agents (Twilio, Slack, HubSpot) live in the
  agents skill; web embeds (Audio Native) live in the studio skill.
- If a fetch fails, fall back to WebFetch on the same URL.
