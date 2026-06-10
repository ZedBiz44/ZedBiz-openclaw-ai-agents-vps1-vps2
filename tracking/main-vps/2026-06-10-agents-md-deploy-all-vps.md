# AGENTS.md Deploy -- All VPS Agents
**Date:** 2026-06-10
**Author:** Manus
**Type:** File Deployment
**Status:** Complete

## Summary

Deployed updated AGENTS.md files (rebuilt from new Standard-AGENTS-MD-Template) from Notion to all 13 agent workspaces across VPS1 and VPS2.

Jack had manually edited all 13 AGENTS.md pages in Notion with the new template structure (improved Startup Rules, Memory Rules, Heartbeat section, and unique-vs-template split). This task deployed those Notion versions to the live agent workspaces.

## What Was Done

- Fetched each agent's AGENTS.md from Notion via MCP
- Backed up the old file as `AGENTS.md.bak.2026-06-10` in each workspace
- Deployed the new file to each workspace
- Verified byte counts on all 13 agents

## VPS1 Agents (jackadmin@187.77.210.223)

Workspace path: `/opt/openclaw/agents/{name}/workspace/AGENTS.md`
Method: docker alpine workaround (runs as root inside container)

| Agent | Bytes Deployed |
|-------|---------------|
| Victor | 11,390 |
| Amanda | 11,581 |
| Wilma | 11,191 |
| Inga | 11,178 |
| Gohzed | 11,202 |
| Marsha | 17,947 |
| Grogar | 11,280 |
| Maggie | 11,115 |
| Vivian | 11,265 |
| Terry | 11,110 |

## VPS2 Agents (root@2.24.104.80)

Workspace path: `/root/.openclaw-{name}/workspace/AGENTS.md`
Method: direct cp as root (no docker needed)

| Agent | Bytes Deployed |
|-------|---------------|
| Harry | 11,035 |
| Suzy | 10,894 |
| Edith | 11,403 |

## Notes

- All old AGENTS.md files backed up with `.bak.2026-06-10` suffix -- recoverable
- Marsha's file is significantly larger (17,947 bytes) -- she has a custom extended template per her Chief of Staff role
- No agents were restarted -- AGENTS.md is loaded at session start, so changes take effect on next agent session
- VPS2 agents (Harry, Suzy, Edith) are bare-metal installs, not Docker containers

## Related

- Notion: Agent-MD-Files database
- Template: Standard-AGENTS-MD-Template (372a3e33d581814fb813cd0ff647579d)
- Previous log: 2026-06-03-agents-md-template-rebuild-all-agents.md
