# Amanda Persistent Asana MCP Pilot

Date: 2026-07-29 MDT | Agent: Cody | Status: Amanda pilot verified

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

- TypeScript checks and application build passed.
- Container image built on VPS1.
- Standard endpoint exposed 41 tools.
- Advanced endpoint exposed exactly six team tools.
- Amanda authenticated as `amanda@zedworks.com`, GID `1213974002925107`.
- Amanda confirmed workspace GID `11298561585567`.
- Amanda listed 33 teams through the advanced route.
- A real Amanda task called both routes with zero failures and no Asana writes.
- A naturally worded team request automatically selected normal `asana` for workspace preflight and `asana-team` for the team operation.
- Ten additional sessions per endpoint left service PIDs flat at 11 each.
- Eight live workload samples left Amanda flat at 50 PIDs, both services flat at 11 PIDs, and local Asana MCP child count at zero.
- Amanda and both sidecars survived the normal controlled restart; fresh post-restart baseline was 15/7/7 PIDs.
- Stopping the advanced sidecar did not stop Amanda or the standard sidecar; standard Asana remained callable.
- The post-restart two-route proof was delivered successfully to Amanda's Discord channel.
- Exact rollback files were parsed, Compose-validated, and checksum-recorded.

## Automatic Routing

- Day-to-day task work loads `zedbiz-asana-agent-control` and uses `asana`.
- Team creation, team updates, and team membership work automatically load `zedbiz-advanced-asana-control` and use `asana-team`.
- Advanced project work also loads `zedbiz-advanced-asana-control`, but uses `asana` when the needed operation belongs to its project, section, status, dependency, or task tools.
- The skill controls safety and confirmation; the server name controls which tool implementation performs the operation.

## Live Deployment

- Image: `zedbiz/asana-http-mcp:1.0.0-amanda-pilot`
- Standard service: `amanda-asana-mcp`
- Advanced service: `amanda-asana-team-mcp`
- Internal endpoints: port 8080 on the external `openclaw` Docker network
- Public host ports: none
- Session cap: 64 per service
- Idle expiry: 15 minutes
- Service PID limit: 64 each
- Main Amanda PID limit remains 160; raising it was not required for the pilot.
- Pull request: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/97

## Rollback

- Restore the timestamped `docker-compose.yml` and `config/openclaw.json` backups.
- Run Amanda's normal 1Password-aware restart launcher.
- Confirm the original stdio MCP definitions and Amanda health.

Validated backups:

- `/opt/openclaw/agents/amanda/docker-compose.yml.pre-http-mcp-20260729-174958`
- `/opt/openclaw/agents/amanda/config/openclaw.json.pre-http-mcp-20260729-174958`
- Compose SHA-256: `673adfd1c29bf603eb296e72a062fa8b9f3e5bcdd31f0fbc182baf27dc0ef4ca`
- Config SHA-256: `28f9b4507aa2d89e8d6539dca470a90ba802d2ad06bdbca6fb215ad2da9f4a80`

## Dependency Note

- Non-breaking updates removed the critical inherited advisory and updated the MCP SDK to 1.30.0.
- Five high audit findings remain in the old Asana SDK's bundled Babel CLI dependency tree. That CLI is not invoked by the runtime service. Replacing or removing the upstream Asana SDK is separate hardening work, not part of the MCP lifecycle fix.

## Fleet Decision

- Amanda is proven.
- Do not roll out fleet-wide until Jack approves the next one-agent pilot.
- The reusable standard HTTP service can be used for the other Asana agents.
- Non-Asana MCPs need their own compatible HTTP service or gateway route; this Amanda image does not automatically convert WordPress or unrelated MCPs.

## Post-Pilot Interruption Incident

- At 17:54 MDT, Amanda acknowledged Jack's live Discord assignment and began the identity preflight and project audit.
- Cody incorrectly treated Amanda's lower PID count as evidence that she was idle.
- At 18:03 MDT, Cody ran the planned restart-persistence test.
- The restart removed Amanda's container and terminated Jack's in-progress Discord/Codex task.
- At 18:06 MDT, after Jack sent `??`, Amanda reported the interruption and started a new run using the updated connection.
- Amanda recovered healthy and continued the assignment. The interruption was caused by Cody's maintenance restart, not by the new MCP services or renewed PID exhaustion.

Corrective operating rule:

- Never infer agent idleness from PID count, CPU use, or the absence of local MCP child processes.
- Before maintenance that can terminate a container, verify the live task/session state and the user-facing channel, and obtain a clear maintenance window when a user has recently assigned work.
- Do not run optional resilience tests while an agent is handling user work; wait until the assignment is visibly complete.

## Files

- `docker/asana-http-mcp/`
- `docker/asana-http-mcp/deploy/amanda/docker-compose.yml`
- `docker/asana-http-mcp/deploy/amanda/switch-openclaw-mcp.mjs`
