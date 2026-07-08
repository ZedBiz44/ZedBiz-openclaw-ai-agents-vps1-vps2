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
