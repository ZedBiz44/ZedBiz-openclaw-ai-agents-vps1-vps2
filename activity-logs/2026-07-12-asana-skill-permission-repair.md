# 2026-07-12 | Cody | Asana Skill Permission Repair

Date: 2026-07-12
Agent: Cody
Status: Complete

## Issue

Terry reported that the regular Asana skill folder was unreadable by the runtime user because `workspace/skills/zedbiz-asana-agent-control` was owned by `root:root` with restrictive permissions.

## Finding

The issue was not Terry-only. The previous route-fix rollout had replaced the regular skill folders for Amanda, Terry, Wilma, and Inga with empty `root:root` directories. Amanda and Inga still appeared to work because the critical routing instructions were also present in `AGENTS.md` and `TOOLS.md`, but the skill folder itself was not correct.

## Fix

Restored the actual skill files and corrected ownership/permissions:

- Restored `zedbiz-asana-agent-control` for Amanda, Terry, Wilma, and Inga.
- Restored/verified `zedbiz-advanced-asana-control` for Amanda.
- Set ownership to `node:node` (`1000:1000`).
- Set directories to readable/executable and files to readable by the runtime user.

## Verification

Inside each target container, verified:

- `workspace/skills/zedbiz-asana-agent-control/SKILL.md` exists.
- `workspace/skills/zedbiz-asana-agent-control/agents/openai.yaml` exists.
- Files are owned by `node:node`.
- Runtime user can read `SKILL.md`.
- Regular skill includes the updated `Blocked on tool exposure` route-fix language.

Amanda advanced skill was also verified readable:

- `workspace/skills/zedbiz-advanced-asana-control/SKILL.md`
- `workspace/skills/zedbiz-advanced-asana-control/agents/openai.yaml`
