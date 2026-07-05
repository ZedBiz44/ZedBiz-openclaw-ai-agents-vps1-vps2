# 2026-06-17 - Terry Codex Provider Diagnosis

Date | Author | Status: 2026-06-17 | Cody | Completed

## Question

- Manus reported that Terry's model is set to `codex/gpt-5.5` but the auth section only has the `openai` provider, not `openai-codex`.
- User asked whether this is really an issue and what it means.

## Records Checked

- Local tracking: `2026-06-12-notion-access-diagnosis-amanda-inga-gohzed-maggie-marsha.md`
- Local tracking: `2026-06-12-openai-billing-route-diagnosis.md`
- Local tracking: `2026-06-17-codex-oauth-refresh-method-check.md`
- Live Terry config.
- Terry pre-upgrade backup: `/opt/openclaw/agents/terry/backups/pre-upgrade-20260531-0554/openclaw.json`
- Live read-only `openclaw doctor` output.

## Live Current State

- Terry container is running and healthy.
- Current primary model: `codex/gpt-5.5`.
- Current fallback model: `codex/gpt-5.4-mini`, plus OpenRouter fallbacks.
- Current GPT model registry includes both:
  - `codex/gpt-5.4`, `codex/gpt-5.4-mini`, `codex/gpt-5.5`
  - `openai/gpt-5.4`, `openai/gpt-5.4-mini`, `openai/gpt-5.5`
- Current auth section has:
  - `openai:jzedbiz@gmail.com` with provider `openai`, mode `oauth`
  - `openai:api-key-backup` with provider `openai`, mode `api_key`
- Codex plugin is enabled.

## Backup Comparison

- The May 31 pre-upgrade backup used the old model route:
  - `openai-codex/gpt-5.5`
- The backup also used the old auth profile:
  - `openai-codex:jzedbiz@gmail.com`
  - provider `openai-codex`
- This supports the timeline that `openai-codex` was old-style config.

## Doctor Evidence

- Read-only `openclaw doctor` reported pending changes:
  - Move `agents.defaults.model` legacy runtime primary refs to canonical provider refs.
  - Move `agents.defaults.models` legacy runtime keys to canonical provider refs.
  - Select Codex runtime.
  - Run `openclaw doctor --fix` to apply.
- Doctor also reported Terry's `openai:jzedbiz@gmail.com` OAuth profile is expired.

## Verdict

- `openai-codex` being absent from Terry's current auth section is not the issue.
- In the newer config shape, `openai` is the canonical provider and the Codex plugin/harness uses the OpenAI provider underneath.
- The real issue is that Terry still has active legacy `codex/gpt-*` model refs, while the canonical repaired pattern is `openai/gpt-*` with Codex runtime selected.
- This is a cleanup/migration issue, not a provider-missing outage.

## Recommended Next Step

- Re-authorize Terry's expired `openai:jzedbiz@gmail.com` OAuth profile individually.
- Then apply the OpenClaw doctor migration path to Terry only, with a backup and restart.
- Verify Terry's final state is:
  - primary `openai/gpt-5.5`
  - fallback `openai/gpt-5.4-mini`
  - auth order `openai:jzedbiz@gmail.com`, then `openai:api-key-backup`
  - Codex plugin enabled
  - container healthy
  - real workflow test passes

## Notion

- Created Tech Updates entry: `2026-06-17 | Cody | Terry Codex Provider Diagnosis`.
