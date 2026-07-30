# VPS1 Fleet Persistent Asana HTTP MCP Rollout

Date: 2026-07-29 MDT | Agent: Cody | Status: Deployed and verified

## Purpose

- Stop Codex app-server threads from spawning and retaining one stdio Asana MCP
  process per turn.
- Give every VPS1 agent one persistent, bounded, PAT-authenticated standard
  Asana service.
- Preserve each agent's own Asana identity and existing team-access boundaries.
- Add safe team/project navigation and Viewer-only portfolio reads.

## Confirmed Starting State

- Amanda and Terry already used persistent HTTP Asana sidecars.
- Victor, Marsha, Inga, Maggie, Grogar, Gohzed, Wilma, and Vivian still used
  `/usr/local/bin/npx -y @roychri/mcp-server-asana`.
- Edith had a valid Edith PAT and workspace identity but no Asana MCP route.
- Several main containers still held live stdio Asana child processes.
- Main-agent PID use before conversion included Victor 65, Inga 62, Maggie 61,
  Grogar 52, Gohzed 52, and Wilma 62 out of a 160-PID limit.
- Wilma also had an unrelated `wordpress-allzed` HTTP MCP.
- Amanda had a separate six-tool `asana-team` management MCP in addition to
  her standard Asana MCP.

## Standard Deployed

- Image: `zedbiz/asana-http-mcp:1.1.0-standard-read-navigation`
- Standard tool count: 47
- Internal route: `http://<agent>-asana-mcp:8080/mcp`
- Authentication: the receiving agent's own `ASANA_ACCESS_TOKEN`
- Sidecar limits: 384 MB, 64 PIDs, 64 sessions, 15-minute session TTL
- Public ports: none
- Main-agent PID limit: unchanged at 160
- Managed restart path:
  `/opt/openclaw/agents/<agent>/op-start-<agent>.sh restart`

The standard route includes current-user identity, workspace lookup, exact team
search, team-project listing, portfolio discovery, portfolio details, portfolio
items, and the pre-existing project/task tools.

## Agent Identities Verified

| Agent | PAT identity | User GID | Standard route |
| --- | --- | --- | --- |
| Amanda | amanda@zedworks.com | 1213974002925107 | 47 tools |
| Terry | terry@agents.zbiz.ca | 1214469570857381 | 47 tools |
| Victor | victor@agents.zbiz.ca | 1214049698028551 | 47 tools |
| Marsha | marsha@agents.zbiz.ca | 1214051396458813 | 47 tools |
| Inga | inga@agents.zbiz.ca | 1214056417378023 | 47 tools |
| Maggie | maggie@agents.zbiz.ca | 1214056417379216 | 47 tools |
| Grogar | grogar@agents.zbiz.ca | 1214049698045940 | 47 tools |
| Gohzed | gohzed@agents.zbiz.ca | 1214045726549148 | 47 tools |
| Wilma | wilma@agents.zbiz.ca | 1214049698033540 | 47 tools |
| Vivian | vivian@agents.zbiz.ca | 1214470244795396 | 47 tools |
| Edith | edith@agents.zbiz.ca | 1215564984542462 | 47 tools |

Every identity verified workspace `11298561585567`,
`ZedBiz - Local Marketing Service`.

## Portfolio Access

Every agent now has explicit Viewer membership on the five current
Jack-owned portfolios:

- Directories
- GHL Growth Garage
- Test Portfolio
- Website Development
- ZedBiz Testing Websites

Membership creation was run through Amanda's approved management PAT. The
deployment script preserves an existing membership and its access level instead
of downgrading broader access.

## Team Access Boundary

- Amanda, Terry, Victor, Marsha, Inga, Grogar, Gohzed, Wilma, Vivian, and Edith
  resolved `Z1AM-ZedBiz-Main`, GID `1216007690588299`, and its 27 active
  projects.
- Maggie is intentionally scoped to two existing Asana teams. She is not a
  member of `Z1AM-ZedBiz-Main`.
- Maggie's verification therefore used her existing
  `ZVTR-Tools-Resources` team, GID `1200483214328568`, and returned eight
  active projects.
- No team memberships were silently expanded during this MCP lifecycle repair.

## Special Routes Preserved

- Amanda's `asana-team` endpoint remained
  `http://amanda-asana-team-mcp:8080/mcp`.
- Amanda's advanced sidecar still exposes exactly six tools:
  `asana_list_teams`, `asana_update_team`, `asana_create_team`,
  `asana_add_team_member`, `asana_remove_team_member`, and
  `asana_get_team_members`.
- A real advanced `asana_list_teams` call returned 33 teams and included
  `Z1AM-ZedBiz-Main`.
- Wilma's `wordpress-allzed` endpoint remained
  `https://allzed.com/wp-json/mcp/v1/http`.

## Verification

- All 11 main containers were Docker-healthy.
- All 11 standard Asana sidecars were Docker-healthy.
- All 11 sidecars returned exactly 47 standard tools.
- Every real `asana_get_user` call matched the expected agent PAT identity.
- Every agent resolved and read a team already allowed by its current Asana
  membership.
- Every agent returned five accessible portfolios with `viewer` access.
- Every Discord bot was configured, running, and passed its live API probe.
- No main agent contained `npm exec @roychri/mcp-server-asana`,
  `mcp-server-asana`, or another local stdio Asana child after rollout.
- Victor's full OpenClaw turn used the new tools and returned his correct
  identity, the Z1AM team GID, 27 projects, and five portfolios with zero tool
  failures.
- Edith's full OpenClaw turn proved that her newly added route returned her
  correct identity, the Z1AM team GID, 27 projects, and five portfolios with
  zero tool failures.

Post-rollout main/sidecar PID samples were:

| Agent | Main PIDs | Standard sidecar PIDs |
| --- | ---: | ---: |
| Amanda | 17 | 13 |
| Terry | 16 | 13 |
| Victor | 21 | 13 |
| Marsha | 17 | 13 |
| Inga | 40 | 13 |
| Maggie | 16 | 13 |
| Grogar | 16 | 13 |
| Gohzed | 16 | 13 |
| Wilma | 17 | 13 |
| Vivian | 16 | 13 |
| Edith | 16 | 13 |

Inga's and Victor's higher main counts were not Asana children. A later
monitoring sample showed Maggie at 38 main PIDs after her Codex app-server
started. Inga's and Maggie's process trees contained only the gateway and the
expected Codex app-server pair; neither had an Asana child. Every sidecar
remained at 13 PIDs, and the explicit process audit found zero stdio Asana
processes across all 11 main containers.

## Files And Runtime Surfaces Changed

- Repository deployment package:
  `docker/asana-http-mcp/deploy/fleet/`
- Live Compose:
  `/opt/openclaw/agents/<agent>/docker-compose.yml`
- Live standard MCP source:
  `/opt/openclaw/agents/<agent>/asana-http-mcp/`
- Live MCP route:
  `/opt/openclaw/agents/<agent>/config/openclaw.json`
- Live agent guidance:
  `/opt/openclaw/agents/<agent>/workspace/TOOLS.md`
- Live standard Asana skill:
  `/opt/openclaw/agents/<agent>/skills/zedbiz-asana-agent-control/`

Amanda's guidance and advanced skill were not replaced during her standard
sidecar upgrade.

## Backups And Rollback

Timestamped backups were created beside each live file before modification:

- Victor: `20260729-2145-mdt-fleet-asana`
- Marsha, Inga, Maggie, Grogar, Gohzed, Wilma, Vivian, Edith:
  `20260729-2200-mdt-fleet-asana`
- Amanda standard sidecar Compose:
  `20260729-2230-mdt-standard-asana-upgrade`
- Terry standard image Compose:
  `20260729-2245-mdt-standard-image`

Rollback:

- Restore the timestamped Compose, OpenClaw config, `TOOLS.md`, and standard
  skill backup for the affected agent.
- Recreate through the agent's managed `op-start-<agent>.sh restart` launcher.
- Remove Viewer memberships only if Jack explicitly wants the permission
  rollout reversed.
- Do not remove Amanda's advanced `asana-team` service or Wilma's WordPress MCP.

## Operational Outcome

The fleet no longer hands the standard Asana stdio command to Codex. Codex
connects to one already-running HTTP sidecar per agent, so repeated turns do not
create another Asana process in the main agent container. This directly removes
the diagnosed unbounded Asana PID-growth path while keeping credentials and
team visibility separated by agent.

## Links

- Fleet issue:
  https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/94
- Notion diagnosis:
  https://app.notion.com/p/3aca3e33d581806c8ec8ccd84113e769
- Technical Documentation journal:
  https://app.notion.com/p/3aca3e33d581812d84d4c1d1c469aa37
