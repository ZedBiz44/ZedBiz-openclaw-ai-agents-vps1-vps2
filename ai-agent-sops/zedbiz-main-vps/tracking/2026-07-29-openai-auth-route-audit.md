# 2026-07-29 - OpenAI Authentication Route Audit

## Summary

- **Date:** 2026-07-29 Mountain Time
- **Agent:** Cody
- **Systems:** VPS1 and VPS2 OpenClaw agents
- **Change Type:** Read-only authentication audit
- **Status:** Complete

## Scope

- VPS1: Terry, Amanda, Inga, Marsha, Wilma, GoHzed, Grogar, Maggie, Victor, Vivian, and Edith
- VPS2: Harry, Suzy, and Frank

## Verified Result

All fourteen agents are currently routed to OpenAI through direct API credentials.

- The active primary model is `openai/gpt-5.6-sol`.
- The first OpenAI fallbacks are `openai/gpt-5.6-terra` and `openai/gpt-5.6-luna`.
- Every inspected Codex runtime `auth.json` contains an `OPENAI_API_KEY`.
- No inspected Codex runtime `auth.json` contains active OAuth access or refresh tokens.
- Each running agent environment exposes `OPENAI_API_KEY`.
- VPS1 agents are healthy.
- VPS2 gateways and the Harry/Suzy Codex app-server processes are running.

## Important Configuration Note

Several VPS1 OpenClaw configurations still contain an OAuth-labelled profile such as `openai:jzedbiz@gmail.com`. These labels are historical configuration metadata and do not represent the credential stored in the current Codex runtime authentication file.

The live Codex runtime is using an OpenAI API key. This audit did not expose, copy, or record any credential value.

## Changes Made

- No agent configuration was changed.
- No service or container was restarted.
- No credential was modified.

## Verification Method

- Checked live process and container health.
- Read the active model route from each live `openclaw.json`.
- Checked credential field types in each live Codex runtime `auth.json`.
- Checked only whether relevant environment variables exist.
- Did not print or store secret values.
