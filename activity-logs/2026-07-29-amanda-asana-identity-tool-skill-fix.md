# 2026-07-29 - Skill Updated - Amanda Asana Identity And Advanced Routing

## Summary

- **Date:** 2026-07-29 Mountain Time
- **Added By:** Cody
- **Agent Receiving Skill:** Amanda
- **VPS:** main-vps
- **Status:** tested

## Skill Purpose

- Require a real PAT-backed `asana_get_user` identity check before Amanda performs Asana work.
- Preserve automatic routing between Amanda's normal `asana` tools and advanced `asana-team` tools.
- Prevent the incompatible legacy HTTP/SSE probe from falsely blocking a healthy Streamable HTTP service.
- Prevent intermediate Discord or Slack acknowledgement messages from ending the active work turn.

## Setup Details

- Skill folders:
  - `skills/zedbiz-asana-agent-control`
  - `skills/zedbiz-advanced-asana-control`
- Files added or changed:
  - both skill `SKILL.md` files and `agents/openai.yaml`
  - Amanda's live `AGENTS.md` and `TOOLS.md`
  - standard Asana HTTP MCP current-user tool and client wrapper
  - Amanda sidecar image and compose tag
- Dependencies:
  - existing Asana PAT
  - existing Streamable HTTP MCP sidecars
  - existing 1Password-aware Amanda launcher

## Test Result

- Test performed:
  - validated both skill packages
  - verified 42 standard tools and 6 advanced tools
  - called `asana_get_user`, `asana_list_workspaces`, and `asana_list_teams`
  - ran three real Amanda agent turns
  - checked PID behavior and process inventory
- Result:
  - Amanda authenticated as `amanda@zedworks.com`, user GID `1213974002925107`
  - correct workspace `11298561585567`
  - 33 teams returned through the advanced route
  - all turns completed with no MCP failure or model fallback
  - sidecars stayed at 11 PIDs each and no per-turn Asana MCP subprocess was created
- Known limitations:
  - `openclaw mcp probe asana` may still report HTTP/SSE 400 because that legacy probe does not match the Streamable HTTP session protocol. Real PAT calls and `/healthz` are authoritative.

## SOP Impact

- Tracking record updated:
  - `ai-agent-sops/zedbiz-main-vps/tracking/2026-07-29-amanda-asana-identity-tool-repair.md`
- The Amanda pilot proves the gateway-level persistent MCP pattern for the normal and advanced Asana routes.

## Rollback Note

- Restore `/opt/openclaw/agents/amanda/backups/20260729-1910MDT`.
- Revert both sidecars to `zedbiz/asana-http-mcp:1.0.0-amanda-pilot`.
- Restart through `/opt/openclaw/agents/amanda/op-start-amanda.sh` and rerun read-only verification.

## Links

- GitHub Issue: #94
- Notion page: https://app.notion.com/p/3aca3e33d581806c8ec8ccd84113e769
- Related commit: pending
