# 2026-06-18 - VPS1 Codex Deferred Connector Inventory Gap

Date: 2026-06-18 MDT
Agent Name: Cody
Status: Completed

## Summary

Jack asked why Airtable did not come up during the earlier full skills/plugins audit after Maggie reported she had an Airtable connector.

The issue is an audit-category gap: the prior skills/plugins inventory checked OpenClaw `plugins.entries`, `skills.entries`, local skill directories, and explicit MCP servers. Airtable is not present in those normal OpenClaw locations. Airtable is present through the Codex deferred app connector/tool layer under each running agent's Codex home cache.

## Key Finding

All running VPS1 agents checked have deferred Codex connector tool families cached for:

- `airtable`
- `asana`
- `github`
- `notion`
- `slack`

Each checked running agent had:

- `dynamicToolsContainDeferred=true`
- cached Codex app tool families: `airtable,asana,github,notion,slack`
- Airtable tool definitions including `airtable_list_bases`, `airtable_search_bases`, `airtable_list_tables_for_base`, `airtable_list_records_for_table`, `airtable_search_records`, `airtable_create_records_for_table`, `airtable_update_records_for_table`, and related schema/comment/base/table tools.

## VPS1 Matrix

| Agent | Running | Auth Profile | Deferred Connector Families | Explicit OpenClaw MCP | Notable Local Skills |
|---|---:|---|---|---|---|
| Amanda | Yes | `openai:jzedbiz@gmail.com` | Airtable, Asana, GitHub, Notion, Slack | Asana | Discord, Gemini, GOG, MCPorter, Nano PDF, Notion, Tavily |
| Edith | Yes | `openai:jzedbiz@gmail.com` | Airtable, Asana, GitHub, Notion, Slack | None | None found in local skills dir |
| GohZed | Yes | `openai:jzedbiz@gmail.com` | Airtable, Asana, GitHub, Notion, Slack | Asana | None notable beyond standard local dirs |
| Grogar | Yes | `openai:jzedbiz@gmail.com` | Airtable, Asana, GitHub, Notion, Slack | Asana | None notable beyond standard local dirs |
| Inga | Yes | `openai:api-key-backup` | Airtable, Asana, GitHub, Notion, Slack | Asana | Discord, Gemini, GOG, MCPorter, Nano PDF, Notion, Tavily |
| Maggie | Yes | `openai:jzedbiz@gmail.com` | Airtable, Asana, GitHub, Notion, Slack | Asana | None notable beyond standard local dirs |
| Marsha | Yes | `openai:jzedbiz@gmail.com` | Airtable, Asana, GitHub, Notion, Slack | Asana | None notable beyond standard local dirs |
| Terry | Yes | `openai:jzedbiz@gmail.com` | Airtable, Asana, GitHub, Notion, Slack | Asana, Notion | MCPorter |
| Victor | Yes | `openai:jzedbiz@gmail.com` | Airtable, Asana, GitHub, Notion, Slack | Asana | Discord, Gemini, GitHub, GOG, MCPorter, Nano PDF, Notion, Tavily, Session Logs, WordPress MCP |
| Vivian | Yes | `openai:jzedbiz@gmail.com` | Airtable, Asana, GitHub, Notion, Slack | Asana | None notable beyond standard local dirs |
| Wilma | Yes | `openai:jzedbiz@gmail.com` | Airtable, Asana, GitHub, Notion, Slack | Asana, WordPress AllZed | Discord, Gemini, GOG, MCPorter, Nano PDF, Notion, Tavily, WordPress MCP |
| Zara | No | N/A | Not verified | N/A | N/A |

## Why This Was Missed

The earlier audit did not treat Codex app connector manifests and deferred tool caches as first-class inventory. Those live under paths like:

- `/home/node/.openclaw/agents/main/agent/codex-home/.tmp/plugins/plugins/airtable/`
- `/home/node/.openclaw/agents/main/agent/codex-home/cache/codex_apps_tools/`
- `/home/node/.openclaw/agents/main/sessions/*.codex-app-server.json`

These are not the same as:

- OpenClaw `plugins.entries`
- OpenClaw `skills.entries`
- Local `/home/node/.openclaw/skills`
- Explicit `mcp.servers`

## SOP Correction Needed

Future fleet skills/plugins audits must include a separate section named:

**Codex Deferred App Connectors**

That section should check:

- `dynamicToolsContainDeferred` in the latest `*.codex-app-server.json`
- available connector tool families from `cache/codex_apps_tools`
- app/plugin manifests under `codex-home/.tmp/plugins/plugins`
- whether connector auth is merely cached or proven by a harmless live read, such as Airtable `list_bases`

Do not mark a connector as operationally proven only because its tool definitions are cached. Mark it as:

- `Cached/Deferred` when definitions are present.
- `Callable` only after a harmless live read succeeds in that agent's actual session.

## Evidence Commands Used

- Read-only SSH to VPS1 as `jackadmin`.
- Read-only Docker inspection of running agent containers.
- No agent config, container, or connector settings were changed.

