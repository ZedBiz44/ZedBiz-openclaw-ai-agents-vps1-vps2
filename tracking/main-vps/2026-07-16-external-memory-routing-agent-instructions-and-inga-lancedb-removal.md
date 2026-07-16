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

## Quick Recall Activity Index Expansion

Jack clarified that the active external memory provider must be the agent's first recall surface and a compact activity index for all meaningful work, not only durable artifacts.

Changes completed:

- Updated all four canonical skills to require recall before every meaningful assignment, research request, client interaction, system update, decision, handoff, or continuation of earlier work.
- Required one compact activity memory to be created or updated during the same interaction when meaningful work is assigned, important information or operating instructions are supplied, or work status changes.
- Required the activity memory to include subject, event, status, source or agent, timestamp, authoritative location when available, and next action or handoff.
- Explicitly made `no memories were changed` an incorrect completion response when meaningful information or instructions should have been remembered.
- Required write verification and plain reporting when provider capture fails.
- Preserved the boundary that external memory is the first recall surface, while live state, GitHub, Memory Wiki, and Z-Knowledge remain authoritative for their respective claim types.
- Replaced the earlier `External-Memory Boundary And Promotion` block with `Quick Recall Activity Index` in every live VPS1/VPS2 agent `AGENTS.md`.
- Deployed the four updated skills to Terry, Edith, Inga, GohZed, Grogar, Marsha, Maggie, Amanda, Victor, Vivian, Wilma, Harry, Frank, and Suzy.

Canonical GitHub skill commits:

- `zedbiz-knowledge-routing`: `cda8330`
- `zedbiz-wiki-research`: `66abf2b`
- `zedbiz-notion-knowledge-publishing`: `ab99186`
- `small-bite-wiki-research`: `343e654`

Verification:

- All four skill repositories passed `quick_validate.py` before deployment.
- Every deployed OpenClaw skill file matched the canonical SHA-256 hash.
- Every OpenClaw agent `AGENTS.md` contained the `Quick Recall Activity Index` heading exactly once.
- VPS1 containers remained healthy and VPS2 services remained active.
- Backups were retained as `AGENTS.md.bak-quick-recall-20260716`.

## Explicit Provider Write Enforcement And Live Verification

Agent acknowledgements from Inga, Suzy, Harry, and Vivian exposed a second failure mode: agents could report that no provider-native write was available without first attempting the registered provider tool.

Changes completed:

- Updated all four canonical skills and every live agent `AGENTS.md` to require an explicit provider store or ingest attempt before declaring the capability unavailable.
- Required the agent to name the exact failed tool and error or policy block when capture cannot run.
- Clarified that automatic turn retention is not proof of explicit capture.
- Clarified that Hindsight is asynchronous: an immediate empty recall does not prove failure; completion must be verified by operation status or direct bank listing.

Canonical skill commits:

- `zedbiz-knowledge-routing`: `877c7ff`
- `zedbiz-wiki-research`: `d0e6dee`
- `zedbiz-notion-knowledge-publishing`: `dcf0568`
- `small-bite-wiki-research`: `41cf76c`

Fleet verification:

- The four deployed skill hashes match the canonical files on all 11 VPS1 agents and all 3 VPS2 agents.
- The explicit-write-attempt rule appears exactly once in every live VPS1/VPS2 `AGENTS.md`.
- The shared VPS1 deployment bundle was updated at `/opt/openclaw/shared/knowledge/z-knowledge/30_TEMPLATES/zedbiz-skills-master/`.

Provider verification:

- Hindsight: direct bank listing confirmed Quick Recall activity memories in `internet-marketing`, `ghl`, and `zedbiz-shared`. Suzy's and Inga's knowledge tools were registered; the apparent recall failure was asynchronous indexing, not missing write access.
- Mem0: repaired Harry's shared Qdrant access, explicitly stored memory ID `2d65848a-1a78-4369-b754-653f9a8c13ce`, and recalled it from Harry, Terry, and Edith.
- LanceDB: Amanda and Victor recalled the rule already stored in their agent databases; Wilma stored the missing rule and recalled it at 84% relevance; Vivian had already completed explicit store and recall.

## Harry Mem0 Repair

Root causes:

- The installed Mem0 Qdrant adapter defaulted to port `6333` even for HTTPS URLs.
- The Qdrant client removed the configured `/qdrant-api` path and called the root `/collections` endpoint.
- Harry's embedding credential reference was unresolved in the service environment.

Repairs:

- Patched Harry's installed Mem0 adapter to select port `443` for HTTPS and `6333` for HTTP.
- Added a Caddy `/collections*` route restricted to the VPS2 source IP and proxied it to Qdrant; other callers receive `401`.
- Supplied the already-authorized resolved embedding credential to Harry's protected environment without logging it.
- Retained backups as `.env.bak-mem0-openai-key-20260716`, `openclaw.json.bak-qdrant-https-port-20260716`, package `.bak-qdrant-https-port-20260716` files, and `/config/Caddyfile.bak-harry-mem0-qdrant-root-20260716`.

Verification:

- VPS2 can reach the authorized Qdrant collections route.
- Harry successfully stored and recalled the compact fleet rule.
- Terry and Edith recalled the same memory from the shared Mem0 lane.
- Harry, Frank, and Suzy services remained active.

## Inga Orphan Package Cleanup

A final audit found that Inga's active slot and configuration were correct but the hashed npm project directory for LanceDB still remained. Removed only `/home/node/.openclaw/npm/projects/openclaw-memory-lancedb-6a4d78c41e`, restarted Inga, and verified:

- Inga is running and healthy.
- Active slot remains `hindsight-openclaw`.
- No LanceDB package directory remains.
- Historical LanceDB data outside the package directory remains preserved.

## Test Load Incident And Recovery

A five-agent parallel provider test left remote `openclaw agent` and hook subprocesses running after the client-side timeout, exhausting VPS1 memory and driving load sharply upward. The test subprocesses were terminated and only Grogar, Maggie, Amanda, Victor, and Wilma were restarted. VPS1 recovered, all 11 agent containers returned healthy, and subsequent LanceDB tests were run one agent at a time with `--local`.
