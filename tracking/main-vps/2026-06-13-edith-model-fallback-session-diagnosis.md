# 2026-06-13 - VPS1 Edith Model Fallback Session Diagnosis

Date | Author | Status: 2026-06-13 | Cody | Completed

## Summary

- Investigated why Edith posted `Model Fallback cleared: codex/gpt-5.5 (was openai/gpt-5.5)` in Discord around 10:00 AM Mountain Time.
- Verified the live VPS1 Edith container is running and healthy.
- Confirmed Edith's main OpenClaw config stayed clean after the June 12 cleanup.
- Found the Discord message lines up with a session registry update, not a main config rollback.

## Live Evidence

- VPS1 host: `187.77.210.223`
- Container: `edith`
- Container state: running, healthy.
- Container start time: `2026-06-12T22:54:30Z`, matching the June 12 cleanup/restart window.
- Main config timestamp: `2026-06-12 16:53:11 -0600`.
- Session registry timestamp during investigation: `2026-06-13 10:00:56 -0600`, matching the Discord screenshot timing.

## Current Model State

- Primary: `codex/gpt-5.5`
- Fallbacks:
  - `codex/gpt-5.4-mini`
  - `openrouter/nvidia/nemotron-3-super-120b-a12b:free`
  - `openrouter/tencent/hy3-preview`
- Active GPT/Codex registry entries:
  - `codex/gpt-5.5`
  - `codex/gpt-5.4`
  - `codex/gpt-5.4-mini`

## Finding

- The old direct `openai/gpt-5.5` fallback is not present in Edith's active main config.
- One Discord channel session still carries stale fallback-origin metadata from the earlier `openai-codex/gpt-5.5` path.
- That session's active model route is already `codex/gpt-5.5`.
- Follow-up Discord screenshot comparison showed why Edith's model picker looks different from Inga's:
  - Edith remains on `codex/gpt-5.5` with only `codex/gpt-5.5`, `codex/gpt-5.4`, and `codex/gpt-5.4-mini` GPT entries.
  - Inga was migrated by `openclaw doctor --fix` to canonical `openai/gpt-5.5`, with `openai/gpt-5.4-mini` fallback and explicit OpenAI auth order.
  - Edith does not currently show the same explicit `auth.order.openai` block that Inga has.
  - The odd Discord picker bucket `A-I (20)` is consistent with Edith still using the older `codex/*` route/display shape, not with the old `openai/gpt-5.5` fallback being back.

## Conclusion

- The June 12 model cleanup held.
- The Discord `Model Fallback cleared` message was a session-level cleanup notice, not proof that Edith's core model configuration reverted.
- Edith is clean but not fully normalized to the same canonical model/auth shape as Inga.
- No server changes were made during this check.

## Notion

- Created Tech Updates entry: `2026-06-13 | Cody | VPS1 Edith Model Fallback Session Diagnosis`.
