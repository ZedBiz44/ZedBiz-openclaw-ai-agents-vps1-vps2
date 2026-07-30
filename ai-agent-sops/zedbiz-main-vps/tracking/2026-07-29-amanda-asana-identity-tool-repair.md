# Amanda Asana Identity Tool And Turn-Delivery Repair

Date: 2026-07-29 MDT | Agent: Cody | Status: Deployed and verified

## Purpose

- Give Amanda a PAT-backed current-user operation that satisfies the required identity preflight.
- Stop an incompatible legacy SSE probe from falsely blocking working Streamable HTTP routes.
- Prevent intermediate Discord acknowledgements from terminating Amanda's work turn.
- Add safe tool start/finish timing logs without logging arguments, authorization headers, or raw error objects.

## Confirmed Diagnosis

- Both real HTTP MCP routes worked: `asana_list_workspaces` returned workspace `11298561585567`, and `asana_list_teams` returned 33 teams.
- The standard service exposed 41 tools but no current-user operation.
- `openclaw mcp probe asana` returned HTTP/SSE 400 because it issued a legacy SSE-style GET against a session-based Streamable HTTP endpoint.
- The surviving Amanda session records did not show a dropped `asana_list_workspaces` response at 18:15 MDT.
- The 18:15 run was a heartbeat, not the portfolio task.
- Amanda's work attempts ended after intermediate `message` tool acknowledgements produced terminal dynamic tool results. No Asana call was issued in those interrupted attempts.

## Technical Correction

- Add read-only `asana_get_user`, defaulting to `user_gid: "me"`.
- Request `gid,name,email,workspaces.gid,workspaces.name` by default.
- Add `UsersApi` to the Asana client wrapper.
- Increase the standard tool inventory from 41 to 42.
- Log tool name, outcome, and duration only.
- Keep `/mcp` standards-compliant; do not return a fake 200 to satisfy the incompatible probe.

## Skill And Agent Rules

- Use a real PAT-backed `asana_get_user` call as the authoritative identity test.
- Use `/healthz` as the service-level test when shell access is available.
- Do not block solely on the legacy probe's HTTP/SSE 400.
- In Discord or Slack, use non-terminal commentary for progress and reserve the `message` tool for final delivery.

## Files

- `docker/asana-http-mcp/src/tools/user-tools.ts`
- `docker/asana-http-mcp/src/asana-client-wrapper.ts`
- `docker/asana-http-mcp/src/tool-handler.ts`
- `docker/asana-http-mcp/deploy/amanda/patch-amanda-identity-delivery.mjs`
- `skills/zedbiz-asana-agent-control/`
- `skills/zedbiz-advanced-asana-control/`

## Local Verification

- TypeScript typecheck passed.
- Application build passed.
- Streamable HTTP inventory returned 42 tools including `asana_get_user`.
- A default identity call used the `/users/me` API path and returned a controlled error with a dummy PAT.
- Error logging returned only `Unauthorized`; it did not dump the request, headers, or token.
- Both canonical and shared-source skill folders passed the Skill Creator validator.

## Live Verification

- Deployed image `zedbiz/asana-http-mcp:1.0.1-amanda-identity` to both Amanda Asana sidecars.
- Both sidecars became Docker-healthy.
- Standard `asana` inventory returned 42 tools including `asana_get_user`.
- Advanced `asana-team` inventory remained intentionally limited to 6 team and membership tools.
- The live PAT identity call returned:
  - email `amanda@zedworks.com`
  - user GID `1213974002925107`
  - workspace `ZedBiz - Local Marketing Service`
  - workspace GID `11298561585567`
- The standard workspace call returned the expected ZedBiz workspace.
- The advanced team call returned 33 teams.
- Amanda's full agent runtime completed one combined two-route verification and two additional current-user calls without fallback or tool failure.
- Amanda returned one final response per test and did not terminate on an intermediate acknowledgement.
- After the repeated agent turns, both MCP sidecars remained flat at 11 PIDs.
- Amanda contained only the persistent OpenClaw/Codex runtime processes; no `npm exec`, `mcp-server-asana`, or Chromium process appeared.
- Amanda's post-turn PID count was 68-69, below the 160 limit and stable across the repeated calls.
- Tool logs recorded tool name, outcome, and duration without arguments, headers, or credentials.

## Rollback

- Live backup root: `/opt/openclaw/agents/amanda/backups/20260729-1910MDT`
- Backed up the compose file, OpenClaw config, `AGENTS.md`, `TOOLS.md`, both Asana skills, and the full prior MCP source tree.
- Previous image remains present as `zedbiz/asana-http-mcp:1.0.0-amanda-pilot`.
- Previous image ID: `sha256:e255debb2280213c09fffa6367e555e858cf622bf1862ff28dcb95196f5c7a88`.
- Rollback assets were checked after deployment.
- Rollback procedure: restore the timestamped files, switch both sidecars to the previous image, bring the compose project up through Amanda's 1Password-aware launcher, and rerun the read-only MCP checks.

## Links

- Fleet issue: #94
- Amanda pilot: #97
- Notion diagnosis: https://app.notion.com/p/3aca3e33d581806c8ec8ccd84113e769
