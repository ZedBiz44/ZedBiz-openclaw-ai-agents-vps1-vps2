# 2026-07-08 - Hindsight AGENTS.md Memory Layer Rules

Date: 2026-07-08 Mountain Time
Agent: Cody
Status: Completed

## Scope

Added the approved `Hindsight, Memory Wiki, And Z-Knowledge` operating section to live OpenClaw Hindsight agents on VPS1 and VPS2.

## Agents Updated

VPS1:

- Inga: `/opt/openclaw/agents/inga/workspace/AGENTS.md`
- GohZed: `/opt/openclaw/agents/gohzed/workspace/AGENTS.md`
- Grogar: `/opt/openclaw/agents/grogar/workspace/AGENTS.md`
- Marsha: `/opt/openclaw/agents/marsha/workspace/AGENTS.md`
- Maggie: `/opt/openclaw/agents/maggie/workspace/AGENTS.md`

VPS2:

- Suzy: `/root/.openclaw-suzy/workspace/AGENTS.md`
- Frank: `/root/.openclaw-frank/workspace/AGENTS.md`

## Backups

VPS1:

- `/opt/openclaw/agents/inga/workspace/AGENTS.md.bak-hindsight-memory-rules-20260708-161712`
- `/opt/openclaw/agents/gohzed/workspace/AGENTS.md.bak-hindsight-memory-rules-20260708-161712`
- `/opt/openclaw/agents/grogar/workspace/AGENTS.md.bak-hindsight-memory-rules-20260708-161712`
- `/opt/openclaw/agents/marsha/workspace/AGENTS.md.bak-hindsight-memory-rules-20260708-161712`
- `/opt/openclaw/agents/maggie/workspace/AGENTS.md.bak-hindsight-memory-rules-20260708-161712`

VPS2:

- `/root/.openclaw-suzy/workspace/AGENTS.md.bak-hindsight-memory-rules-20260708-161738`
- `/root/.openclaw-frank/workspace/AGENTS.md.bak-hindsight-memory-rules-20260708-161738`

## Section Added

The section explains:

- Hindsight is live working memory and cross-session recall.
- `MEMORY.md` is curated long-term summary.
- Memory Wiki is reviewed durable knowledge.
- GitHub/local Markdown is technical source of truth.
- Notion / Z-Knowledge is the business-readable knowledge system.
- Hindsight memories can coexist with Memory Wiki, GitHub/local Markdown, Notion, and Z-Knowledge records.
- Do not store secrets, credentials, raw logs, or temporary chatter in Hindsight.
- Do not copy full Memory Wiki pages into Hindsight; store a pointer or short summary instead.
- If Jack says `Z-Knowledge`, route the item to the Notion Z-Knowledge system and recommend a Memory Wiki record when it is also durable agent knowledge.

## Verification

Verified all seven OpenClaw Hindsight agent `AGENTS.md` files contain:

- `## Hindsight, Memory Wiki, And Z-Knowledge`
- `Z-Knowledge Rule`
- `Do not store secrets`

No runtime config values were changed in this pass.
