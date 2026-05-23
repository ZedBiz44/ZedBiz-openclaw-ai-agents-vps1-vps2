# Fleet Repair — All 9 Agents — 2026-05-22

**Session:** Manus — OpenClaw VPS Fleet Repair
**Date:** 2026-05-22 (MDT)
**Agents repaired:** amanda, victor, wilma, inga, marsha, gohzed, grogar, maggie, vivian

## Issues Found (All 9 Agents)

| Issue | Detail |
|---|---|
| Image version | All on `2026.5.7` → updated to `2026.5.20` |
| Container status | All `Exited 137` (OOM killed) |
| Bad model in config | `google/gemini-3.1-pro-preview-customtools` in `agents.defaults.models` — invalid, caused startup crash |
| npm ownership | `/opt/openclaw/agents/<agent>/npm/` owned by root → chown 1000:1000 |
| Healthcheck port | All using port 3000 — each agent has unique port (3000-3009) → fixed per-agent |
| Workspace ownership | `/opt/openclaw/agents/<agent>/workspace/` owned by root → chown 1000:1000 |
| Discord plugin | Not in `plugins.allow` → added for all 9 |
| No systemd service | No auto-restart on reboot → created + enabled `openclaw-<agent>.service` for all 9 |
| Restart policy | `unless-stopped` in compose → changed to `"no"` (systemd owns restarts) |
| victor/marsha cron | `"frequency": "nightly"` → fixed to `"0 2 * * *"` |

## Agent Port Map

| Agent | Port | Gateway URL |
|---|---|---|
| amanda | 3000 | https://amanda.zbiz.ca |
| victor | 3002 | https://victor.zbiz.ca |
| wilma | 3003 | https://wilma.zbiz.ca |
| inga | 3004 | https://inga.zbiz.ca |
| marsha | 3005 | https://marsha.zbiz.ca |
| gohzed | 3006 | https://gohzed.zbiz.ca |
| grogar | 3007 | https://grogar.zbiz.ca |
| maggie | 3008 | https://maggie.zbiz.ca |
| vivian | 3009 | https://vivian.zbiz.ca |

## Final Status

All 10 agents (including Terry) confirmed **healthy** on `ghcr.io/openclaw/openclaw:2026.5.20`.

```
terry     Up ~2h (healthy)
amanda    Up 5m (healthy)
victor    Up 5m (healthy)
wilma     Up 5m (healthy)
inga      Up 5m (healthy)
marsha    Up 5m (healthy)
gohzed    Up 5m (healthy)
grogar    Up 5m (healthy)
maggie    Up 5m (healthy)
vivian    Up 5m (healthy)
```

## Additional Changes

- Notion MCP server configured for all agents (`@notionhq/notion-mcp-server` via npx)
- `NOTION_API_KEY` resolved from 1Password (`op://openclaw-agents-shared/notion-api-key/credential`)
- Agent Registry created in Notion (Technical Documentation > 🤖 OpenClaw Agent Registry)
- All 10 agents have full profile rows in the registry with live data

## Related

- Terry repair log: `2026-05-22-terry-agent-fixes.md`
- Notion Agent Registry: https://www.notion.so/d8de512f4af94bc99ba87f9a82245543
