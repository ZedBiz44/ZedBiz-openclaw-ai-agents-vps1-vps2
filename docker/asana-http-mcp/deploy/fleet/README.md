# VPS1 Fleet Asana Toolset Rollout

Date: 2026-07-30 | Agent: Cody | Status: Active

This package deploys one persistent, bounded Asana HTTP sidecar per VPS1 agent.

## Toolsets

- Standard image: `zedbiz/asana-http-mcp:2.0.0-standard`
- Standard tool count: 76
- Advanced image: `zedbiz/asana-http-mcp:2.0.0-advanced`
- Advanced tool count: 126
- Standard receivers: Terry, Victor, Wilma, Inga, Gohzed, Grogar, Maggie,
  Vivian, Edith
- Advanced receivers: Amanda and Marsha
- Advanced is a complete superset of Standard and uses the same single `asana`
  route.
- Internal route: `http://<agent>-asana-mcp:8080/mcp`
- Authentication: the agent's own `ASANA_ACCESS_TOKEN`
- Sidecar limits: 384 MB, 64 PIDs, 64 sessions, 15-minute session TTL
- No host port is published.
- Main agent PID limit remains 160.

## Deployment Rules

- Back up the compose file, `openclaw.json`, `TOOLS.md`, and live skill before
  changing an agent.
- Confirm the agent has no active user turn.
- Run `patch-compose-v2.py` and `switch-openclaw-mcp.mjs`.
- Copy the Standard skill to all agents and the Advanced skill to Amanda and
  Marsha.
- Replace old identity guidance using `patch-agent-asana-guidance-v2.mjs`.
- Recreate through `/opt/openclaw/agents/<agent>/op-start-<agent>.sh up` so
  1Password injection is preserved.
- Verify the exact catalog count, `asana_get_user`, workspace
  `11298561585567`, exact team resolution, portfolio reads, channel health, and
  PID behavior.
- Preserve role-based team membership. The verification team defaults to
  `Z1AM-ZedBiz-Main`, but an agent with intentionally narrower team membership
  must be tested against one of that agent's existing teams instead of being
  silently added to unrelated teams.
- Run `verify-toolset.mjs` inside the sidecar for the repeatable identity,
  team, project-count, portfolio-count, catalog, and Advanced API-route proof.

## Special Routes

- Amanda and Marsha receive the single Advanced route.
- Amanda's former six-tool `asana-team` service is removed after the Advanced
  route passes verification.
- Wilma's `wordpress-allzed` HTTP MCP is unrelated and must remain unchanged.
- All other non-Asana MCP servers must remain byte-for-byte equivalent in the
  OpenClaw MCP configuration.

## Rollback

- Restore the timestamped compose, OpenClaw config, guidance, and skill backups.
- Recreate the agent with its managed `op-start-<agent>.sh` script.
- Remove the agent's Asana sidecar only after the restored config no longer
  references it.
