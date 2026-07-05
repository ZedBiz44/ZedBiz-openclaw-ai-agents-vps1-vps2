# 2026-06-17 - Terry Codex Model Normalization Fix

Date | Author | Status: 2026-06-17 | Cody | Completed

## Summary

- Fixed Terry after OAuth renewal by applying the OpenClaw doctor migration path on Terry only.
- Goal was to move Terry from legacy `codex/gpt-*` active model refs to canonical `openai/gpt-*` provider refs while keeping the Codex plugin enabled.

## Backup

- Created pre-fix backup inside Terry's runtime state:
  - `/home/node/.openclaw/openclaw.json.bak-codex-model-normalize-20260618T041108Z`
- OpenClaw doctor also created its own standard backup:
  - `/home/node/.openclaw/openclaw.json.bak`

## Fix Applied

- Ran inside Terry:
  - `openclaw doctor --fix`
- Doctor changes included:
  - Moved `agents.defaults.model` legacy runtime primary refs to canonical provider refs.
  - Moved `agents.defaults.models` legacy runtime keys to canonical provider keys.
  - Cleared stale Google session routing state for one session.
  - Disabled several unavailable/missing-requirement skills.
- Restarted Terry through the normal script:
  - `/opt/openclaw/agents/terry/op-start-terry.sh restart`

## Verification

- Terry returned healthy after restart.
- Health endpoint returned:
  - `{"ok":true,"status":"live"}`
- Final primary model:
  - `openai/gpt-5.5`
- Final fallbacks:
  - `openai/gpt-5.4-mini`
  - `openrouter/google/gemini-3.1-flash-lite`
  - `openrouter/deepseek/deepseek-v4-flash:free`
- Auth order:
  - `openai:jzedbiz@gmail.com`
  - `openai:api-key-backup`
- OAuth expiry:
  - `2026-06-28T04:02:41.916Z`
- Plugins:
  - Codex plugin enabled.
  - OpenAI plugin enabled.
- Gateway startup log confirmed:
  - `agent model: openai/gpt-5.5`

## Remaining Separate Items

- Doctor still reports unrelated security/posture warnings:
  - plaintext `gateway.auth.token`
  - gateway binding to non-loopback/LAN
  - open Discord DM and guild policies
- These were not part of this model normalization fix.

## Notion

- Created Tech Updates entry: `2026-06-17 | Cody | Terry Codex Model Normalization Fix`.
