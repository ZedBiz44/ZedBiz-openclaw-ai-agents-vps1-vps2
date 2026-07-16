# External Memory Routing Agent Instructions And Inga LanceDB Removal

Date: 2026-07-16 MDT  
Agent: Cody  
Status: Complete

## Scope

- Verified the four canonical ZedBiz knowledge skills locally and across the live VPS1/VPS2 OpenClaw fleet.
- Added concise external-memory boundary and promotion behavior to each live agent `AGENTS.md` file.
- Corrected provider-specific capture assumptions for Mem0 and LanceDB.
- Removed Inga's obsolete LanceDB instructions and uninstalled her inactive LanceDB plugin while preserving her historical LanceDB data directory.

## Canonical Skill Verification

The following canonical repositories were clean, matched `origin/main`, passed `quick_validate.py`, and contained the shared rule exactly once:

- `zedbiz-knowledge-routing` at `ca4f998`
- `zedbiz-wiki-research` at `443c9c8`
- `zedbiz-notion-knowledge-publishing` at `a196f6f`
- `small-bite-wiki-research` at `870ecbd`

Live deployment verification confirmed the rule section and canonical completion statement exactly once in every deployed skill for:

- VPS1: Terry, Edith, Inga, GohZed, Grogar, Marsha, Maggie, Amanda, Victor, Vivian, Wilma
- VPS2: Harry, Frank, Suzy

## Agent Instruction Updates

Backups were created as `AGENTS.md.bak-external-memory-routing-20260716`.

Every live VPS1/VPS2 agent now has one concise `External-Memory Boundary And Promotion` section stating:

- external providers are working memory and recall, not final authority;
- durable agent knowledge must be promoted to Memory Wiki;
- human-reviewable or actionable knowledge must also go to Z-Knowledge;
- at most one compact provider pointer should be created when it improves future recall or handoff;
- duplicate, speculative, low-value, secret-bearing, raw-log, and full-document entries must be skipped;
- conflicts are resolved according to the type of claim.

Provider-specific corrections:

- Mem0 agents no longer assume `autoCapture` guarantees turn-end capture in skills mode.
- LanceDB agents no longer assume every turn is automatically captured; qualifying pointers must be explicitly saved and verified.
- Hindsight agents are instructed to use provider-native direct listing or recall and not treat an empty knowledge/public-artifact view as proof of an empty bank.
- Inga's obsolete `LanceDB Long-Term Memory` instruction block was removed because her active provider is Hindsight.

One-agent-first tests passed on Victor, Terry, and Grogar before the remaining agents were updated. All VPS1 containers remained healthy and all VPS2 services remained active.

## Inga LanceDB Removal

Before removal:

- Active memory slot: `hindsight-openclaw`
- Inactive config entry: `plugins.entries.memory-lancedb`
- Installed package: `@openclaw/memory-lancedb`

Actions:

- Backed up `openclaw.json` as `openclaw.json.bak-remove-inactive-lancedb-20260716`.
- Ran the supported `openclaw plugins uninstall memory-lancedb --force` command inside Inga.
- Restarted only Inga through `/opt/openclaw/agents/inga/op-start-inga.sh restart`.
- Preserved `/opt/openclaw/shared/external-memory/lancedb/inga`; no historical memory data was deleted.

Verification:

- `plugins.slots.memory` remains `hindsight-openclaw`.
- `plugins.entries.memory-lancedb` is absent.
- The LanceDB package directory is absent.
- Inga is healthy.
- Gateway startup lists `hindsight-openclaw` and does not list `memory-lancedb`.
- `https://inga.zbiz.ca/health` returned `{"ok":true,"status":"live"}`.

## Remaining Boundary

This work corrected instructions and removed Inga's inactive plugin. It did not perform the provider repair rollout for Victor, Grogar, or Terry beyond instruction changes. Those runtime repairs remain governed by the confirmation boundary in the canonical Notion plan.
