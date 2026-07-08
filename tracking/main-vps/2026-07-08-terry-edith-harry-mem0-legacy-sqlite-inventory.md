# Terry, Edith, and Harry Mem0 Legacy SQLite Inventory

date: 2026-07-08 | agent: Cody | status: Logged

## Context

Jack asked whether Terry, Edith, and Harry still had useful content inside the older SQLite memory system that should be processed into Mem0.

## Live Findings

- VPS1 host checked: `srv1404026` at `jackadmin@187.77.210.223`.
- Terry is running and healthy as a Docker/OpenClaw container.
- Edith is running and healthy as a Docker/OpenClaw container.
- Harry is not currently present as a running Docker container named `harry`.
- Harry has a directory at `/opt/openclaw/agents/harry`, but the live inventory found only the empty shell of the directory/config path and no old SQLite memory database under it.
- Terry and Edith both currently use `openclaw-mem0` as the OpenClaw memory slot.
- Terry and Edith both point Mem0 at Qdrant collection `mem0_vps1_agents` using `userId: zedbiz-vps1`.
- Qdrant collection `mem0_vps1_agents` currently has `13` points.

## Legacy SQLite Counts

- Terry old memory database: `/opt/openclaw/agents/terry/memory/main.sqlite`
  - Size: `95,408,128` bytes
  - `chunks`: `1,427`
  - `files`: `181`
  - `embedding_cache`: `1,062`
- Edith old memory database: `/opt/openclaw/agents/edith/memory/main.sqlite`
  - Size: `51,757,056` bytes
  - `chunks`: `776`
  - `files`: `95`
  - `embedding_cache`: `589`
- Terry empty config copy: `/opt/openclaw/agents/terry/config/memory/main.sqlite`
  - Size: `69,632` bytes
  - `chunks`: `0`
  - `files`: `0`
  - Treat as non-actionable.

## Content Shape

- The old SQLite stores are primarily indexed Markdown memory content, daily/session summaries, and dreaming/reflection files.
- Terry top content buckets:
  - `memory/daily-or-session-md`: `739` chunks across `53` files.
  - other `memory/*` paths including dreaming/reflection material: `675` chunks across `127` files.
  - `MEMORY.md`: `13` chunks.
- Edith top content buckets:
  - `memory/daily-or-session-md`: `398` chunks across `24` files.
  - other `memory/*` paths including dreaming/reflection material: `372` chunks across `70` files.
  - `MEMORY.md`: `6` chunks.

## Recommendation

- Yes, Terry and Edith have meaningful old memory content that has not been bulk-migrated to Mem0.
- Do not bulk-import raw chunks directly into Mem0.
- Process the old memory into clean, durable summaries first, then store those summaries in Mem0.
- Harry does not appear to have an old SQLite store to migrate on VPS1; verify the intended Harry runtime location before spending time on him.

## Proposed Migration Method

- Export Terry and Edith SQLite chunks read-only into JSONL with source metadata.
- Group records by agent and source file path.
- Filter out noisy or risky content:
  - secrets, tokens, keys, raw credentials
  - raw transcript filler
  - stale one-off failures already replaced by later fixes
  - duplicate dream candidates
- Condense each daily/session file into business-useful memory cards:
  - stable user preferences
  - proven fixes
  - live paths and container names
  - recurring failure patterns
  - current source-of-truth pointers
  - open questions or unresolved risks
- Tag every imported card with:
  - `agent: terry` or `agent: edith`
  - `source: legacy-sqlite`
  - `source_path`
  - `date_range`
  - `migration_batch`
- Import in small batches to Mem0 and test recall before continuing.
- Start with Terry only, verify recall quality, then repeat for Edith.

## Suggested First Batch

- Terry:
  - `MEMORY.md`
  - latest daily/session files from `2026-07-01` through `2026-07-05`
  - selected high-value May/June files only when they contain still-current operating rules or fixes
- Edith:
  - `MEMORY.md`
  - latest daily/session files from `2026-07-02` through `2026-07-05`
  - Agent Registry / Memory Wiki related entries first

## Status

- Investigation complete.
- No migration was performed in this pass.
- Next action is to build/run a selective migration script for Terry first, then verify Mem0 recall quality before applying the same process to Edith.
