# Terry Asana Team And Portfolio Read Navigation

Date: 2026-07-29 MDT | Agent: Cody | Status: Deployed and verified

## Purpose

- Correct Terry's false inference that `Z1AM-ZedBiz-Main` was a portfolio after project search returned no match.
- Let standard ZedBiz agents resolve teams and list their projects without advanced team-management authority.
- Give agents read-only portfolio discovery, detail, and item access while keeping all portfolio mutations restricted.

## Confirmed Diagnosis

- `Z1AM-ZedBiz-Main` is team GID `1216007690588299`.
- Terry's PAT could read the team and its 27 active projects directly.
- Terry's old standard MCP lacked team navigation, current-user identity, and portfolio read tools.
- Terry had zero portfolio memberships before this repair.
- Five current portfolios owned by Jack were identified: Directories, GHL Growth Garage, Test Portfolio, Website Development, and ZedBiz Testing Websites.

## Implementation

- Expanded the persistent standard Asana MCP from 42 to 47 tools.
- Added `asana_search_teams`.
- Added `asana_get_projects_for_team`.
- Added `asana_list_accessible_portfolios`.
- Added `asana_get_portfolio`.
- Added `asana_get_portfolio_items`.
- Preserved `asana_get_user` as the required PAT identity preflight.
- Added pagination limits and deduplication for team projects and portfolio memberships.
- Return each portfolio membership's `access_level`.
- Updated the day-to-day skill to resolve ambiguous names across project, team, and portfolio object types before making claims.
- Kept team membership changes and every portfolio mutation behind the advanced skill and confirmation.
- Corrected Terry's Discord/Slack delivery rule so an intermediate acknowledgement does not terminate the work turn.

## Portfolio Permissions

Terry was added as a `viewer` to all five current Jack-owned portfolios:

- Directories: membership `1217007402711748`
- GHL Growth Garage: membership `1217007151525582`
- Test Portfolio: membership `1217007290257720`
- Website Development: membership `1217007290404445`
- ZedBiz Testing Websites: membership `1217007412015486`

Viewer grants were created through Amanda's approved PAT authority after the user confirmed the repair. Terry did not receive editor or admin access.

## Verification

- TypeScript typecheck passed.
- Application build passed locally and on VPS1.
- Skill Creator validation passed for both repository and shared Codex skill copies.
- Candidate MCP inventory returned exactly 47 tools.
- Real PAT candidate tests returned Terry's correct identity and workspace.
- `asana_search_teams` resolved the exact team GID.
- `asana_get_projects_for_team` returned all 27 active projects.
- Live portfolio discovery returned all five portfolios with `access_level: viewer`.
- Live `asana_get_portfolio` opened Test Portfolio.
- Live `asana_get_portfolio_items` returned its three projects.
- Terry's own full OpenClaw agent turn answered the exact team question, identified the object as a team, listed 27 projects, and made no Asana changes.
- Terry's own portfolio turn listed all five portfolios and the three Test Portfolio items with no Asana changes.
- Both containers remained healthy.
- Post-test process counts were stable at 14 PIDs for Terry and 11 PIDs for `terry-asana-mcp`.
- No local Asana stdio child or Chromium process remained in Terry.

## Live Deployment

- Image: `zedbiz/asana-http-mcp:1.1.0-terry-read-navigation`
- Service: `terry-asana-mcp`
- Internal endpoint: `http://terry-asana-mcp:8080/mcp`
- Public host ports: none
- Terry PID limit: 160
- Sidecar PID limit: 64

## Rollback

- Backup root: `/opt/openclaw/agents/terry/backups/20260729-2021-terry-read-navigation`
- Restore the prior Compose file, MCP source, `openclaw.json`, `AGENTS.md`, `TOOLS.md`, and normal Asana skill from that directory.
- Bring the stack up through Terry's 1Password-aware launcher.
- Remove the five recorded memberships through Asana only if Jack also wants to reverse the Viewer permissions.
- The previous image remains available as `zedbiz/asana-http-mcp:1.0.0-terry-pilot`.

## Deployment Notes

- The first live image build correctly failed before restart because Terry's older source folder did not yet contain `user-tools.ts`; the missing canonical file was added and the next build passed.
- The first archive extraction inherited read-only directory flags from the Windows source. No production file was deleted. Individual verified source files were staged instead.
- Terry's `AGENTS.md` was root-owned from earlier work, so the approved root-container method applied the patch and restored ownership to UID/GID 1000.
- The inherited Asana SDK dependency tree still reports five high audit findings. That separate dependency-hardening work is unchanged by this read-navigation repair.

## Links

- Fleet issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/94
- Notion diagnosis: https://app.notion.com/p/3aca3e33d581806c8ec8ccd84113e769
