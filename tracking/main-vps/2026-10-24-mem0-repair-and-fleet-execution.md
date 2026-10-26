# Mem0 repair and remaining VPS1 10.6 execution

Date:2026-10-24 | Owner:Cody | Status:Executing, production acceptance pending

Jack authorized Get-er-Done: repair Terry, use the proven process for other Mem0 agents, finish remaining VPS1 agents on2026.10.6 and scoped cleanup. Marsha's Slack plugin remains enabled for a planned connection. This amends issue480 and the existing release record/PR482; it does not authorize outbound test messages, unrelated credential changes, memory deletion or bypassing loader trust checks.

## Current scope and decisions

Terry/Edith are VPS1 Mem0 agents; Harry/VPS2 also uses Mem0. Live Harry already uses gpt-6-luna; preserve it. Terry uses gpt-5.6-luna; preserve it. Edith's retired extraction model needs the already tested supported replacement during her upgrade. Both live Harry and Terry customized plugin code SHA256 match0e7205db54c8790c1aff7b09786ec0b7578db08181b5394a7137df4e530297c2. Verify Edith independently. Retain Qdrant client1.18.0, embedding configuration, actual collections/users, history policy, explicit retention, unique search/get tools, Codex-first Notion, skills, schedules and all required channels.

## Reproducible Mem0 artifact

Versioned customized plugin1.2.1 vendor tar declares mem0ai3.3.1. Root package declares that tar, Qdrant1.18.0 and better-sqlite3 12.11.1, with .npmrc/lock for clean npm ci. No ordinary startup npm installation. Plugin executable bytes and contracts preserve existing customizations. Revision2 pins zod4.6.6 after revision1 audit found GHSA-mrhx-c7xc-m3w5; npm clean reinstall and real SDK inference/search/fresh-instance recall pass, audit zero. Source:docker/mem0-repair-20261024. Protected staging:/opt/openclaw/backups/mem0-repair-20261024-r2. Build/runtime proof does not yet constitute live acceptance.

## Pilot and rollout gates

Test current copied Terry state through the exact production entrypoint, command and post-start.sh. Isolate Qdrant in temporary storage; skip external channel delivery and schedules only in the fixture. Repeat comparable full starts; test automatic capture on a no-tool turn, independent fresh-session recall, explicit memory_add/mem0_search/mem0_get, authenticated Codex Notion and Asana/Drive reads. Keep result receipts private when they contain business context. No production cutover if a required test fails.

Before each live change, verify idle requests and scheduled work, current health, headroom, fresh offline state archive/restored SQLite checks, current exact images and recovery manifests. Preserve old project/config/scripts outside live state; switch only reviewed project and startup guards while offline. SDK data format is expected unchanged: prefer code/package rollback on current state; state restoration is separate and must preserve later work. Model changes only Edith's already retired helper model, verified on isolated storage first. No automatic rollback to an unusable retired model.

Terry pilot must pass before Edith/Harry replication. Complete remaining VPS1 core/tools/Asana cohorts serially, preserving special Amanda/Grogar/Marsha guards and existing Wiki locks. Use managed op-start lifecycle and verified cold recovery for every selected image. Retain compatible Hindsight backend until shared-service acceptance is complete; do not silently migrate it as a gateway-only step.

## Cleanup and completion

Remove only exact verified disposable test/build leftovers after acceptance and mount/process/recovery checks. Retain business media, active memory, current image archives, manifests and required rollback. October18 state backups remain until remaining updates and replacement recovery pass. Off-server recovery remains a separate explicitly defined requirement, not satisfied by a local archive.

Completion needs live per-agent core/Node/image, health/readiness, public routes, memory/model/tools/channels, unchanged schedules/custom assets, managed recovery and final resource measurements. Host updates already completed; shared loader overhead/RAM goal must remain visible unless independently fixed. Source and results updated in this record/issue480 plus the same dated Notion journal.
