# Terry, Edith, Harry Mem0 AGENTS Rules

date: 2026-07-08 | agent: Cody | status: Logged

## Summary

Added a shared Mem0 operating section to Terry, Edith, and Harry's live `AGENTS.md` files. The new section is titled `Mem0, Memory Wiki, And Z-Knowledge`.

## Files Updated

- Terry: `/opt/openclaw/agents/terry/workspace/AGENTS.md`
- Edith: `/opt/openclaw/agents/edith/workspace/AGENTS.md`
- Harry: `/root/.openclaw-harry/workspace/AGENTS.md`

## What The Section Clarifies

- Mem0 is a live operational memory provider for Terry, Edith, and Harry.
- Mem0 does not replace OpenClaw Markdown memory, SQLite, Memory Wiki, GitHub/local Markdown, Notion, or Z-Knowledge.
- SQLite/Markdown memory can continue to exist and grow after Mem0 is enabled.
- Terry, Edith, and Harry share the Mem0 lane using `openclaw-mem0`, `userId: zedbiz-vps1`, collection `mem0_vps1_agents`, and entity collection `mem0_vps1_agents_entities`.
- Terry and Edith use VPS1 Qdrant directly at `http://187.77.210.223:6333`.
- Harry uses the same memory lane through `https://marsha.zbiz.ca/qdrant-api`.
- Strong memory-save signals include phrases such as `remember this`, `save this`, `decision`, `lesson learned`, `fix confirmed`, and `handoff`.
- Secrets, credentials, raw logs, full documents, and temporary chatter must not be stored in Mem0.
- Stable or repeated Mem0 knowledge should be promoted to the correct durable source: Memory Wiki, `MEMORY.md`, GitHub/local Markdown, Notion, Z-Knowledge, or `AGENTS.md`.
- If Mem0 conflicts with a reviewed/live source, follow the reviewed/live source and report the mismatch.

## Verification

- Terry verified with heading placement:
  - `## Memory Rules`
  - `## Mem0, Memory Wiki, And Z-Knowledge`
  - `## Decision Framework`
- Edith verified with heading placement:
  - `## Memory Rules`
  - `## Completion Rules`
  - `## Mem0, Memory Wiki, And Z-Knowledge`
  - `## Decision Framework`
- Harry verified with heading placement:
  - `## Memory Rules`
  - `## Mem0, Memory Wiki, And Z-Knowledge`
  - `## Decision Framework`

## Operational Note

No service restart was required. The updated instructions apply when each agent loads its `AGENTS.md` context in a new session or refreshed run.
