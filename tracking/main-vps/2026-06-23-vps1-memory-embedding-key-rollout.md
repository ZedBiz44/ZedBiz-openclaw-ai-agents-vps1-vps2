# 2026-06-23 - VPS1 Memory Embedding Key Rollout

Date: 2026-06-23 MDT
Agent Name: Cody
Status: Completed

## Summary

- Diagnosed fleet-wide `memory_search` failures on VPS1 agents.
- Root cause was not missing OpenAI Platform credit. The stale/runtime OpenAI embedding route was separate from the working Codex OAuth route.
- User added a fresh OpenAI Platform key to 1Password shared vault item `openai-embedding-key`.
- Verified the 1Password key directly against OpenAI embeddings from the VPS and from inside Wilma's container.
- Proved the correct working pattern on Wilma first, then rolled it across active VPS1 agents.

## Fix Applied

- Updated each active agent's startup environment to use the new 1Password-sourced OpenAI key for `OPENAI_API_KEY`.
- Set memory search to a dedicated embedding route:
  - Provider: `openai-compatible`
  - Model: `text-embedding-3-small`
  - Base URL: `https://api.openai.com/v1`
  - API key source: container `OPENAI_API_KEY`
- Recreated each active container so the new environment was loaded.
- Rebuilt each memory index because the provider identity changed from `openai` to `openai-compatible`.

## Agents Updated

- Amanda
- Edith
- GohZed
- Grogar
- Inga
- Maggie
- Marsha
- Terry
- Victor
- Vivian
- Wilma

## Verification

All active VPS1 agents were verified after rollout:

- Container status: running
- Health: healthy
- Memory provider: `openai-compatible`
- Memory model: `text-embedding-3-small`
- Embedding probe: true
- Memory index: valid
- Dirty state: false

Wilma was also tested with a real memory search for `ZedBiz`, which returned memory results successfully.

## Notes

- Chat/Codex OAuth auth order was preserved. The fix is scoped to memory embeddings.
- The stale `openai:api-key-backup` auth profile may still exist, but memory search no longer depends on that route.
- Backups were created for each touched `.env` and `.env.resolved` file with suffix `bak-cody-embedding-key-<timestamp>`.
