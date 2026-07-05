# 2026-06-12 - VPS1 Edith Model Dropdown Cleanup

Date | Author | Status: 2026-06-12 | Cody | Completed

## Summary

- Cleaned Edith's LLM model dropdown and persistent OpenClaw config.
- Removed stale GPT-5 entries from Edith's model registry.
- Removed the direct `openai/gpt-5.5` LLM fallback from Edith's config.
- Restarted Edith using her normal `op-start-edith.sh restart` path.
- Verified Edith came back healthy and `/healthz` returned live status.

## Before

- Primary: `openai-codex/gpt-5.5`
- Fallbacks included:
  - `openai/gpt-5.5`
  - `openrouter/nvidia/nemotron-3-super-120b-a12b:free`
  - `openrouter/tencent/hy3-preview`
- GPT-5 dropdown/model registry included:
  - `openai-codex/gpt-5.5`
  - `openai-codex/gpt-5.4`
  - `openai-codex/gpt-5.4-mini`
  - `openai-codex/gpt-5.3-codex`
  - `openai-codex/gpt-5.3-codex-spark`
  - `openai-codex/gpt-5.2`
  - `openai/gpt-5.5`

## After

- Primary: `codex/gpt-5.5`
- Fallbacks:
  - `codex/gpt-5.4-mini`
  - `openrouter/nvidia/nemotron-3-super-120b-a12b:free`
  - `openrouter/tencent/hy3-preview`
- Remaining Codex GPT-5 model registry entries:
  - `codex/gpt-5.5`
  - `codex/gpt-5.4`
  - `codex/gpt-5.4-mini`

## Backup

- Host backup: `/opt/openclaw/agents/edith/openclaw.json.bak-edith-model-cleanup-2026-06-12T225410050Z`
- In-container pre-restart backup: `/home/node/.openclaw/openclaw.json.bak-edith-model-cleanup-2026-06-12T225311068Z`

## Verification

- `edith` container is running healthy.
- `http://127.0.0.1:3011/healthz` returned `{"ok":true,"status":"live"}`.
- Host config and running container config both show the cleaned model list after restart.
