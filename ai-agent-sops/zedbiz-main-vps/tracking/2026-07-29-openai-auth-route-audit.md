# 2026-07-29 - OpenAI Authentication Route Audit

## Summary

- **Date:** 2026-07-29 Mountain Time
- **Agent:** Cody
- **Systems:** VPS1 and VPS2 OpenClaw agents
- **Change Type:** Read-only authentication audit and factual correction
- **Status:** Corrected and verified

## Correction Notice

The first version of this record incorrectly concluded that the fleet was using direct OpenAI API credentials as its primary route. That conclusion was based on the presence of `OPENAI_API_KEY` in generated Codex runtime files and container environments. Those facts prove that an API credential exists, but they do not prove which OpenClaw authentication profile handled a request.

The authoritative evidence is the active OpenClaw SQLite authentication store, profile order, `lastGood` state, execution trajectories, and live request fallback result. Those checks confirm that OpenAI Codex OAuth is primary.

## Scope

- VPS1: Terry, Amanda, Inga, Marsha, Wilma, GoHzed, Grogar, Maggie, Victor, Vivian, and Edith
- VPS2: Harry, Suzy, and Frank

## Corrected Verified Result

All fourteen agents are configured to use OpenAI Codex OAuth through the named profile `openai:jzedbiz@gmail.com`.

- The active primary model is `openai/gpt-5.6-sol`.
- The ten primary VPS1 agents explicitly order `openai:jzedbiz@gmail.com` before `openai:api-key-backup`.
- Edith's active store uses the OAuth profile and does not currently contain the API-key backup profile.
- All eleven VPS1 agents report `openai:jzedbiz@gmail.com` as the `lastGood` OpenAI profile.
- Current completed VPS1 execution trajectories identify `openai:jzedbiz@gmail.com` as the selected authentication profile.
- Harry, Suzy, and Frank on VPS2 report the OAuth profile as effective with status `ok`, the Codex runtime route as `usable`, and no unusable profiles.
- The API key remains a backup lane where configured. Its presence does not mean it is the active route.

## Vivian Refresh Verification

Vivian had not used the OpenAI route since 2026-07-16. Her stored access token had expired on 2026-07-24, but her refresh token remained available.

A fresh live request was run on 2026-07-29:

- Authentication profile: `openai:jzedbiz@gmail.com`
- Provider/model: `openai/gpt-5.6-sol`
- Result: success
- Authentication mode: `auth-profile`
- Fallback used: `false`
- OAuth refresh: successful
- New access-token expiry: 2026-08-08
- API backup used: no

## Why The Original Check Was Wrong

The generated file `agents/main/agent/codex-home/auth.json` and the `OPENAI_API_KEY` environment variable were treated as proof of the selected credential. They are not the authoritative selector.

OpenClaw selects the credential from:

`agents/main/agent/openclaw-agent.sqlite`

The live selection evidence is:

- Provider authentication order
- OAuth profile type and refresh-token presence
- `lastGood` profile
- Execution trajectory `authProfileId`
- Live request `fallbackUsed` result

## Current Authentication Design

- Primary: OpenAI Codex OAuth using `openai:jzedbiz@gmail.com`
- Backup where configured: direct OpenAI API key
- Later model fallbacks: configured OpenRouter models

No switch from OAuth primary to API primary was found.

## Changes Made

- No agent authentication configuration was changed.
- No credential was copied, replaced, or exposed.
- No service or container was restarted.
- A temporary hung Terry audit process started during verification was terminated without stopping Terry's gateway; Terry remained healthy.
- This GitHub record and its linked Notion journal were corrected in place.

## Related Evidence

- GitHub issue #60: July 2026 OAuth invalidation, independent device-code reauthorization, and fleet recovery
- GitHub issue #63: post-update verification of OAuth-first profile order and live OAuth probes
