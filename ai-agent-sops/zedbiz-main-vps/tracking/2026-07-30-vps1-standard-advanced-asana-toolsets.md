# VPS1 Standard And Advanced Asana Toolsets

Date: 2026-07-30 MDT | Agent: Cody | Status: Deployed and verified

## Why

VPS1 agents needed two clear Asana capability levels without returning to the
per-turn stdio MCP process pattern:

- Standard for nine day-to-day agents.
- Advanced for Amanda and Marsha.

The former six-tool Amanda team service was not a full administration toolset
and forced one agent to choose between two Asana routes. The replacement
Advanced service is one superset route.

## What

### Standard

- Image: `zedbiz/asana-http-mcp:2.0.0-standard`
- Tool count: 76
- Receivers: Terry, Victor, Wilma, Inga, Gohzed, Grogar, Maggie, Vivian, Edith
- Scope: current-user identity, workspaces, teams and team projects, projects,
  tasks, subtasks, sections, stories, project statuses/updates, project briefs,
  tags, attachments, dates, dependencies/blockers, task relationships,
  task-level custom fields, safe bulk task work, read-only goals, and read-only
  portfolios.

### Advanced

- Image: `zedbiz/asana-http-mcp:2.0.0-advanced`
- Tool count: 126
- Receivers: Amanda and Marsha
- Scope: every Standard tool plus team administration, portfolio mutations,
  workspace custom-field administration, goals, templates, webhooks,
  allocations, time entries, incoming-rule triggers, and a fixed-host
  `asana_api_request` tool for public Asana API endpoints not represented by a
  named tool.
- The effective authority remains bounded by the public Asana API, the agent's
  PAT identity and Asana permissions, and the Advanced skill's confirmation
  rules.
- Asana does not expose general native dashboard layout control or general
  native Rule creation/editing through its public API.

## Where

- Source: `docker/asana-http-mcp/`
- Deployment package: `docker/asana-http-mcp/deploy/fleet/`
- Standard skill: `skills/zedbiz-asana-agent-control/`
- Advanced skill: `skills/zedbiz-advanced-asana-control/`
- Live source: `/opt/openclaw/agents/<agent>/asana-http-mcp/`
- Live route: `http://<agent>-asana-mcp:8080/mcp`
- Live config: `/opt/openclaw/agents/<agent>/config/openclaw.json`
- Live skills: `/opt/openclaw/agents/<agent>/skills/`

## Access And Safety

- Each sidecar receives only its own agent's `ASANA_ACCESS_TOKEN`.
- No host port is published.
- The MCP endpoint requires bearer authentication.
- The route can call only the fixed Asana API host.
- Every deployment backs up Compose, OpenClaw config, TOOLS guidance, and the
  replaced skill folders.
- Advanced replaces Amanda's old `asana-team` service; it does not create a
  third capability lane.

## Verification

- Local TypeScript typecheck: passed.
- Local production build: passed.
- Catalog integrity: Standard 76 unique tools; Advanced 126 unique tools.
- Terry Standard pilot:
  - correct PAT identity `terry@agents.zbiz.ca`;
  - correct GID `1214469570857381`;
  - correct workspace `11298561585567`;
  - exact team resolved with 27 projects;
  - five visible portfolios;
  - exact 76-tool catalog;
  - full OpenClaw runtime turn returned the same identity and tool count;
  - Discord and Slack probes passed;
  - 16 main-container PIDs and 13 sidecar PIDs immediately after deployment.

## Rollback

- Restore the timestamped Compose, OpenClaw config, TOOLS, and skill backups.
- Recreate the agent through
  `/opt/openclaw/agents/<agent>/op-start-<agent>.sh restart`.
- The prior image remains locally available during the rollout.

## Completion Record

- All nine Standard agents received the 76-tool image and Standard skill.
- Amanda and Marsha received the 126-tool Advanced image, Standard skill, and
  Advanced skill.
- Amanda's former six-tool `asana-team` config and container were removed.
- Every deployment returned the expected personal PAT identity, workspace,
  tool count, permitted team/project result, and portfolio result.
- Advanced raw `GET /users/me` matched the named identity call for Amanda and
  Marsha.
- Terry completed a full OpenClaw runtime turn and returned his correct email,
  GID, workspace, and exact 76-tool count.
- Amanda used the new Advanced route in live work: identity, task, portfolio,
  team-project, and repeated universal-search calls all completed successfully.
- All eleven main containers and sidecars were healthy in the final audit.
- Every Discord bot passed its live probe.
- Every sidecar was at 13 PIDs; no main container contained an stdio Asana
  child.
- Final main-container PID samples:
  - Amanda 72 while actively working
  - Marsha 17
  - Terry 45 after the full runtime test
  - Victor 17
  - Wilma 17
  - Inga 41
  - Gohzed 16
  - Grogar 16
  - Maggie 16
  - Vivian 16
  - Edith 16
- Wilma's WordPress MCP and Maggie's narrower team boundary were preserved.
- Notion Phase 3.2, 3.2a, 3.2b, and 3.2c were rewritten to the current SOP
  standard and marked Done on 2026-07-30.

## Operational Links

- GitHub issue:
  https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/94
- Technical Documentation journal:
  https://app.notion.com/p/3ada3e33d581815296f1cb5132b62614
- VPS1 Agent Creation SOP:
  https://app.notion.com/p/f24a3e33d5818256accd0185fe925af2
