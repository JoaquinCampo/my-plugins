---
name: admin
description: Use for ElevenLabs account and workspace administration. Covers billing, pay as you go, credits, data residency, usage analytics, workspaces, members, seats, billing groups, service accounts, API keys, SSO and SAML and SCIM, resource sharing, and user groups.
---

# ElevenLabs Administration

Current docs index for account, billing, and workspace administration:

!`curl -sf --max-time 15 https://elevenlabs.io/docs/overview/administration/llms.txt || echo "FETCH FAILED. Use WebFetch on https://elevenlabs.io/docs/overview/administration/llms.txt"`

## How to use this index

- Pick only the pages relevant to the task; URLs above already end in `.md`
  and return clean markdown. Fetch with `curl -sf <page-url>`.
- Fetch one page at a time; do not bulk-fetch the whole list.
- For admin API endpoints (usage, history, workspace management), grep the full
  index: `curl -sf https://elevenlabs.io/docs/llms.txt | grep -iE 'usage|workspace|history'`
- If a fetch fails, fall back to WebFetch on the same URL.
