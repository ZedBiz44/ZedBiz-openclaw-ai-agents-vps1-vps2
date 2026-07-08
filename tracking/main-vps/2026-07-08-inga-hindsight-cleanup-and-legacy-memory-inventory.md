# 2026-07-08 - Inga Hindsight Cleanup and Legacy Memory Inventory

Date: 2026-07-08 Mountain Time
Agent: Cody
Status: Completed

## Scope

Live cleanup for Inga's Hindsight `internet-marketing` bank after finding stale provider-state memories that incorrectly implied LanceDB was active or that `OPENAI_API_KEY` was missing.

## Live Runtime Findings

- Inga container: running and healthy on VPS1.
- Inga active memory slot: `plugins.slots.memory = hindsight-openclaw`.
- Inga Hindsight bank: `internet-marketing`.
- Suzy service: active/running on VPS2.
- Suzy active memory slot: `plugins.slots.memory = hindsight-openclaw`.
- Hindsight server health: healthy, database connected.
- Running Inga container has `OPENAI_API_KEY` present.
- LanceDB is installed/configured for Inga, but is not the active provider unless the memory slot is changed to `memory-lancedb`.

## Hindsight Cleanup Performed

- Soft-invalidated incorrect raw memories that claimed:
  - LanceDB was the active provider for Inga.
  - `OPENAI_API_KEY` was missing in the active Inga runtime.
- Updated one LanceDB setup fact to clarify that the plugin/store exists but is not active while `plugins.slots.memory = hindsight-openclaw`.
- Retained a canonical correction in Hindsight:
  - Jack is the human owner/operator.
  - Inga and Suzy are AI agents.
  - Active provider truth comes from live `plugins.slots.memory`.
  - Inga is active on Hindsight, not LanceDB.
  - LanceDB is installed/configured but inactive.
  - Running Inga gateway has `OPENAI_API_KEY` present.
- Updated Hindsight bank config overrides with provider/source-of-truth guardrails.
- Cleared and rebuilt observations for the `internet-marketing` bank.
- Refreshed mental models:
  - `active-projects`
  - `working-procedures`
  - `user-preferences`

## Agent Config Guardrails Added

Updated source Hindsight config for:

- Inga: `/opt/openclaw/agents/inga/config/openclaw.json`
- Suzy: `/root/.openclaw-suzy/openclaw.json`

Backups created:

- Inga: `/opt/openclaw/agents/inga/config/openclaw.json.bak-cody-hindsight-guardrails-20260708`
- Suzy: `/root/.openclaw-suzy/openclaw.json.bak-cody-hindsight-guardrails-20260708`

Guardrails added:

- Jack is the human owner/operator.
- Inga and Suzy are AI agents.
- Active provider truth comes from live OpenClaw `plugins.slots.memory`.
- Installed/configured plugin entries do not mean active provider.
- For Inga as verified on 2026-07-08, active slot is `hindsight-openclaw`.
- LanceDB is installed/configured but not active.
- Live container environment checks override stale CLI shell warnings.

## Verification

- Inga hot reload applied successfully after config change.
- Suzy hot reload applied successfully after config change.
- Hindsight `internet-marketing` observation rebuild completed:
  - Cleared 17 old observations.
  - Rebuilt 14 observations.
  - Failed operations: 0.
  - Failed consolidation: 0.
- Final recall checks returned no results for:
  - `OPENAI_API_KEY`
  - `Inga is running LanceDB as the active`
  - `LanceDB active memory provider`
- Refreshed mental models no longer carried the stale provider-state claims.

## Legacy Memory Inventory

Correction from later live check on 2026-07-08:

- The original note below missed active SQLite files because the first inspection looked at too narrow a path.
- The live source of truth check across the Hindsight-connected agents found legacy OpenClaw memory databases at each agent's `memory/main.sqlite`.
- The Markdown `MEMORY.md` and daily memory files should remain in place. They are still part of the OpenClaw/Hindsight operating lane and should not be cleaned up as part of SQLite migration.

No SQLite database files were found in the inspected Inga agent or shared external-memory paths.

Found legacy/non-Hindsight material:

- Daily Markdown memory files: 43 files under `/opt/openclaw/agents/inga/workspace/memory`.
- Dreaming reports: 108 Markdown files under `/opt/openclaw/agents/inga/workspace/memory/dreaming`.
- Session corpus files: 38 files under `/opt/openclaw/agents/inga/workspace/memory/.dreams/session-corpus`.
- Core memory file: `/opt/openclaw/agents/inga/workspace/MEMORY.md`, about 9.5 KB.
- LanceDB store: `/opt/openclaw/shared/external-memory/lancedb/inga`, about 104 KB, with LanceDB `memories.lance` data files.

## Recommended Migration Path

Do not blindly import all legacy memory into Hindsight.

Recommended process:

- Start with `/opt/openclaw/agents/inga/workspace/MEMORY.md` because it is already promoted/curated.
- Then process daily Markdown memory files by date, newest and highest-value first.
- Use dreaming `deep` and `rem` reports as synthesis candidates, not raw truth.
- Treat session corpus files as fallback evidence only; they are noisier and more likely to duplicate facts already promoted elsewhere.
- Export LanceDB rows separately and compare against Hindsight before importing, because LanceDB may already contain some of the stale provider-state claims.
- Use Hindsight `dry-run-extract` on candidate chunks before retaining.
- Retain accepted chunks with tags:
  - `agent:inga`
  - `shared_bank:internet-marketing`
  - `source_system:legacy-memory-md` or `source_system:lancedb-import`
  - `legacy_import:2026-07-08`
  - `project:internet-marketing`
  - `sensitivity:internal`
- Use stable `document_id` values so repeat imports replace/update the same source rather than duplicating.
- After each batch, run consolidation and refresh the mental models.

## Next Recommended Batch

Pilot one small migration batch first:

- Import `/opt/openclaw/agents/inga/workspace/MEMORY.md`.
- Import the latest 5 daily memory files.
- Dry-run extract first, review the extracted facts, then retain.
- Verify recall before processing the rest.

## 2026-07-08 Live SQLite Inventory Addendum

Scope:

- Hindsight-connected OpenClaw agents:
  - Inga and Suzy: `internet-marketing` bank.
  - GohZed and Grogar: `ghl` bank.
  - Marsha, Maggie, and Frank: `zedbiz-shared` bank.
- Ruby Hermes Hindsight state on VPS3.
- Harry was not included in this Hindsight migration inventory because Harry is active on Mem0, not Hindsight.

Primary migration targets:

| Agent | VPS | Hindsight bank | Primary SQLite memory DB | Size | Knowledge rows |
|---|---:|---|---|---:|---:|
| Inga | VPS1 | `internet-marketing` | `/opt/openclaw/agents/inga/memory/main.sqlite` | 82,255,872 bytes | 1,215 chunks, 148 files |
| Suzy | VPS2 | `internet-marketing` | `/root/.openclaw-suzy/memory/main.sqlite` | 60,485,632 bytes | 993 chunks, 136 files |
| GohZed | VPS1 | `ghl` | `/opt/openclaw/agents/gohzed/memory/main.sqlite` | 57,823,232 bytes | 947 chunks, 123 files |
| Grogar | VPS1 | `ghl` | `/opt/openclaw/agents/grogar/memory/main.sqlite` | 62,205,952 bytes | 924 chunks, 119 files |
| Marsha | VPS1 | `zedbiz-shared` | `/opt/openclaw/agents/marsha/memory/main.sqlite` | 93,769,728 bytes | 1,324 chunks, 176 files |
| Maggie | VPS1 | `zedbiz-shared` | `/opt/openclaw/agents/maggie/memory/main.sqlite` | 58,281,984 bytes | 952 chunks, 122 files |
| Frank | VPS2 | `zedbiz-shared` | `/root/.openclaw-frank/memory/main.sqlite` | 65,986,560 bytes | 894 chunks, 121 files |
| Ruby | VPS3 | `zedbiz-shared` | `/opt/hermes-ruby/memory_store.db` | 65,536 bytes | 1 fact, 1 entity |

OpenClaw `memory/main.sqlite` schema:

- `chunks` carries `id`, `path`, `source`, `start_line`, `end_line`, `hash`, `model`, `text`, `embedding`, and `updated_at`.
- `files` carries `path`, `source`, `hash`, `mtime`, and `size`.
- This is suitable for a controlled migration because source path, source type, line range, and chunk hash can be preserved.

Secondary SQLite files found:

| Agent | Runtime/session DB | Count | Log DB | Count | Codex memory job DB |
|---|---|---:|---|---:|---|
| Inga | `agents/main/agent/codex-home/state_5.sqlite` | 170 threads | `agents/main/agent/codex-home/logs_2.sqlite` | 41,228 logs | 0 jobs, 0 stage1 outputs |
| Suzy | `agents/main/agent/codex-home/state_5.sqlite` | 125 threads | `agents/main/agent/codex-home/logs_2.sqlite` | 32,325 logs | 0 jobs, 0 stage1 outputs |
| GohZed | `agents/main/agent/codex-home/state_5.sqlite` | 140 threads | `agents/main/agent/codex-home/logs_2.sqlite` | 30,284 logs | 0 jobs, 0 stage1 outputs |
| Grogar | `agents/main/agent/codex-home/state_5.sqlite` | 135 threads | `agents/main/agent/codex-home/logs_2.sqlite` | 28,569 logs | 0 jobs, 0 stage1 outputs |
| Marsha | `agents/main/agent/codex-home/state_5.sqlite` | 202 threads | `agents/main/agent/codex-home/logs_2.sqlite` | 56,325 logs | 0 jobs, 0 stage1 outputs |
| Maggie | `agents/main/agent/codex-home/state_5.sqlite` | 149 threads | `agents/main/agent/codex-home/logs_2.sqlite` | 33,000 logs | 0 jobs, 0 stage1 outputs |
| Frank | `agents/main/agent/codex-home/state_5.sqlite` | 126 threads | `agents/main/agent/codex-home/logs_2.sqlite` | 34,720 logs | 0 jobs, 0 stage1 outputs |
| Ruby | `/opt/hermes-ruby/state.db` | 110 sessions, 4,397 messages | none targeted | n/a | n/a |

Files that should not be bulk-migrated:

- `config/state/openclaw.sqlite` and `state/openclaw.sqlite`: OpenClaw runtime state, not clean memory knowledge.
- `codex-home/state_5.sqlite`: thread/session state. Use only if a specific thread needs to be summarized.
- `codex-home/logs_2.sqlite`: logs. Too noisy for raw import.
- `codex-home/memories_1.sqlite`: present but empty for inspected OpenClaw agents.
- `tasks/runs.sqlite`, `kanban.db`, and response store databases: operational state, not memory facts.
- VPS2 nested `.openclaw/memory/main.sqlite` for Suzy and Frank exists but is empty.

Recommended migration approach:

- Leave Markdown memory files and `MEMORY.md` in place.
- Export rows from each agent's `memory/main.sqlite` `chunks` table.
- Preserve source metadata:
  - source path
  - source type
  - start and end line
  - original chunk hash
  - agent name
  - bank name
  - import batch date
- Build stable Hindsight document IDs such as `legacy-sqlite:{agent}:memory-main:{chunk_hash}`.
- Deduplicate against current Hindsight recall before retaining.
- Run a small dry-run batch first, then retain only useful facts or summaries.
- Consolidate and refresh mental models after each agent/bank batch.

Recommended pilot order:

- Ruby first if the goal is a very low-risk proof of process, because its Hindsight memory store contains only one fact.
- Frank or Grogar first if the goal is to pilot the OpenClaw `memory/main.sqlite` migration on a smaller chunk set.
- Inga/Suzy after the migration script is proven, because the `internet-marketing` bank was just cleaned and should not be polluted by a rough first import.
