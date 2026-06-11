# SOP Update -- Fallback Chain Changed to gpt-5.4-mini
**Date:** 2026-06-11 (MST)
**Recorded by:** Manus
**Status:** COMPLETED

## Change
Updated Notion SOP pages Phase 1.4 (llm-model-picker) and Phase 1.4a (OpenAI-Oath-Provider)
in Agent-Creation-VPS1-SOP to reflect the new fallback chain decision.

## New Fallback Chain (as of 2026-06-11)
```json
{
  "primary": "codex/gpt-5.5",
  "fallbacks": [
    "codex/gpt-5.4-mini",
    "openrouter/google/gemini-3.1-flash-lite",
    "openrouter/deepseek/deepseek-v4-flash:free"
  ]
}
```

## Previous Chain (set 2026-06-10)
```json
{
  "primary": "codex/gpt-5.5",
  "fallbacks": [
    "codex/gpt-5.4",
    "openrouter/google/gemini-3.1-flash-lite",
    "openrouter/deepseek/deepseek-v4-flash:free"
  ]
}
```

## Rationale
- gpt-5.4 costs $2.50/1M input tokens -- 3x more than gpt-5.4-mini ($0.75/1M)
- For day-to-day agent work (file ops, tool calls, memory reads, email drafts, structured responses),
  gpt-5.4-mini handles 90% of tasks without quality loss
- Cost protection: if agents ever run unattended on fallback (OAuth expiry, runaway task incident),
  the exposure is dramatically lower with mini as Fallback 1
- gpt-5.3-codex is officially deprecated by OpenAI -- confirmed removed from all configs

## API Pricing Reference (Standard Rate)
| Model | Input / 1M | Cached / 1M | Output / 1M |
|---|---|---|---|
| codex/gpt-5.5 | $5.00 | $0.50 | $30.00 |
| codex/gpt-5.4 | $2.50 | $0.25 | $15.00 |
| codex/gpt-5.4-mini | $0.75 | $0.075 | $4.50 |
| gpt-5.3-codex | DEPRECATED | -- | -- |

## Notion Pages Updated
- Phase 1.4 llm-model-picker: https://app.notion.com/p/112a3e33d58183e3982701e7462ce417
- Phase 1.4a OpenAI-Oath-Provider: https://app.notion.com/p/36da3e33d58180849714e16abdc8f1fc

## Notes
- Cody (VPS2) to apply the mini fallback change to live agent configs
- The `codex/` prefix correction (vs `openai-codex/` or `openai/`) was already applied fleet-wide 2026-06-10
- Both SOP pages also updated to v4 with correct `codex/` prefix throughout
