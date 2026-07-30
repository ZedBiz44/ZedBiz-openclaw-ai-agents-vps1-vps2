# VPS1 Fleet Asana HTTP Rollout

Date: 2026-07-29 | Agent: Cody | Status: Active

This package moves each VPS1 OpenClaw agent's standard Asana MCP from a
per-thread stdio child process to one persistent, bounded HTTP sidecar.

## Standard

- Image: `zedbiz/asana-http-mcp:1.1.0-standard-read-navigation`
- Standard tool count: 47
- Internal route: `http://<agent>-asana-mcp:8080/mcp`
- Authentication: the agent's own `ASANA_ACCESS_TOKEN`
- Sidecar limits: 384 MB, 64 PIDs, 64 sessions, 15-minute session TTL
- No host port is published.
- Main agent PID limit remains 160.

## Deployment Rules

- Back up the compose file, `openclaw.json`, `TOOLS.md`, and live skill before
  changing an agent.
- Confirm the agent has no active user turn.
- Run `patch-compose.py` and `switch-openclaw-mcp.mjs`.
- Copy the standard Asana control skill and identity-safe navigation guidance.
- Recreate through `/opt/openclaw/agents/<agent>/op-start-<agent>.sh up` so
  1Password injection is preserved.
- Verify 47 tools, `asana_get_user`, workspace `11298561585567`, exact team
  resolution, portfolio reads, channel health, and PID behavior.
- Preserve role-based team membership. The verification team defaults to
  `Z1AM-ZedBiz-Main`, but an agent with intentionally narrower team membership
  must be tested against one of that agent's existing teams instead of being
  silently added to unrelated teams.
- Run `verify-standard-sidecar.mjs` inside the sidecar for the repeatable
  identity, team, project-count, portfolio-count, and tool-count proof.
- Run `provision-portfolio-viewer.mjs` inside Amanda's main container so
  portfolio membership changes use Amanda's approved management PAT.
- Grant only Viewer portfolio membership when no membership exists. Never
  downgrade an existing broader role.

## Special Routes

- Amanda keeps her separate six-tool `asana-team` advanced service. Only her
  standard `asana` service is upgraded by this package.
- Wilma's `wordpress-allzed` HTTP MCP is unrelated and must remain unchanged.
- All other non-Asana MCP servers must remain byte-for-byte equivalent in the
  OpenClaw MCP configuration.

## Rollback

- Restore the timestamped compose, OpenClaw config, guidance, and skill backups.
- Recreate the agent with its managed `op-start-<agent>.sh` script.
- Remove the agent's Asana sidecar only after the restored config no longer
  references it.
