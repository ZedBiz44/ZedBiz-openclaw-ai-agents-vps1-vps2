# Amanda Persistent Asana MCP Pilot

Date: 2026-07-29 MDT | Agent: Cody | Status: In progress

## Purpose

- Stop Amanda's standard and advanced Asana MCP processes from being spawned inside every Codex task.
- Preserve Amanda's own PAT-authenticated Asana identity and advanced team-management toolset.
- Prove the persistent HTTP design on one agent before any fleet rollout.

## Scope

- Agent: Amanda
- VPS: VPS1 at `187.77.210.223`
- Standard route: `asana`
- Advanced route: `asana-team`
- GitHub issue: #94
- Notion diagnosis: Cody VPS1 Agent Diagnosis Solution

## Old Assumption

- A configured stdio MCP would be cleaned up after each Codex task.

## Confirmed Problem

- Codex keeps per-task MCP managers loaded and leaves their stdio child processes alive.
- Amanda can accumulate both the standard Asana subprocess stack and the advanced team subprocess stack.
- Raising the PID ceiling only delays the failure.

## Tested Correction

- Run one persistent Streamable HTTP service for standard Asana.
- Run one persistent Streamable HTTP service for Amanda's six advanced team tools.
- Keep both services internal to the existing Docker network with bearer authentication and no published ports.
- Point Amanda's two existing MCP names to the persistent URLs.
- Bound sessions by count and idle time so they cannot accumulate forever.

## Security And Identity

- Both services use Amanda's existing `ASANA_ACCESS_TOKEN`; no Jack-authenticated connector is used.
- The pilot reuses that PAT as the internal bearer token to avoid adding a second secret during initial deployment.
- The services have no public host ports.
- Read-only verification must confirm `amanda@zedworks.com`, user GID `1213974002925107`, and workspace GID `11298561585567`.

## Required Verification

- TypeScript checks and application build pass.
- Container image builds on VPS1.
- Standard endpoint exposes the expected tool inventory.
- Advanced endpoint exposes exactly six team tools.
- Amanda authenticates as Amanda on the standard route.
- Amanda can list teams through the advanced route.
- Repeated new Discord tasks do not spawn new local Asana MCP process trees.
- Amanda's PID use remains stable.
- Amanda and both sidecars survive a controlled restart.
- Stopping one sidecar does not stop Amanda or the other sidecar.
- Backups and exact rollback files exist before cutover.

## Rollback

- Restore the timestamped `docker-compose.yml` and `config/openclaw.json` backups.
- Run Amanda's normal 1Password-aware restart launcher.
- Confirm the original stdio MCP definitions and Amanda health.

## Files

- `docker/asana-http-mcp/`
- `docker/asana-http-mcp/deploy/amanda/docker-compose.yml`
- `docker/asana-http-mcp/deploy/amanda/switch-openclaw-mcp.mjs`
