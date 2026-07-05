# 2026-06-12 - VPS1 Deprecated GPT-5.3 Model Dropdown Cleanup

Date | Author | Status: 2026-06-12 | Cody | Completed

## Summary

- Cleaned deprecated `gpt-5.3-codex` model dropdown entries across the VPS1 OpenClaw fleet.
- Kept each agent's current primary/default route unchanged.
- Removed stale model registry key `openai/gpt-5.3-codex` where present.
- Restarted affected agents so Discord model pickers refresh.

## Agents Patched

- Amanda
- Gohzed
- Grogar
- Inga
- Maggie
- Terry
- Victor
- Vivian
- Wilma

## Already Clean

- Marsha
- Edith

## Backups

- Each patched agent received a backup beside its persistent config:
  - `/opt/openclaw/agents/<agent>/config/openclaw.json.bak-deprecated-gpt53-cleanup-2026-06-12T...Z`

## Verification

- Running model registries for all checked agents now show no `gpt-5.3-codex` stale key.
- Remaining visible GPT-5 entries are `gpt-5.4`, `gpt-5.4-mini`, and `gpt-5.5` under the active route families.
- Edith remains restricted to clean `codex/gpt-5.4`, `codex/gpt-5.4-mini`, and `codex/gpt-5.5` entries from the earlier cleanup.
- All restarted agents came back healthy.
- Victor took one full Docker health interval to flip from `health: starting` to `healthy`; its service endpoint was live during that wait.
