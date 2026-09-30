# Amanda native Asana subtask headings

Date: 2026-09-29 America/Edmonton | Author: Cody | Status: Verified live on Amanda

## Problem and repair

Amanda reported that native subtask headings were unavailable. Her deployed MCP schemas did not expose Asana's `is_rendered_as_separator` boolean. Asana rejects `resource_subtype: section`; native subtask headings are `default_task` objects with the separator boolean set.

Added the boolean and usage guidance to `asana_create_subtask`, `asana_create_task`, and `asana_update_task`. Existing handler and client wrapper forward the field unchanged. No new endpoint or identity route was added.

Related record: https://github.com/ZedBiz44/ZedBiz-general-tech-issues-updates/issues/58
Related audit: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/398

## Live deployment

- Source: `/opt/openclaw/agents/amanda/asana-http-mcp/src/tools/task-tools.ts`.
- Image: `zedbiz/asana-http-mcp:2.0.0-amanda-native-headings-20260929`.
- Image ID: `sha256:68084d139d6f287097f209e83d821768171fd19adfa90e6a2e8846ece793e0eb`.
- Updated only the Amanda MCP image reference in `/opt/openclaw/agents/amanda/docker-compose.yml`.
- Built with `docker build`; deployed with `docker compose up -d --no-deps --no-build amanda-asana-mcp`.
- Amanda's main agent was not restarted. Other agents were not deployed.
- Retained all three September 27 `sessionId ? 404 : 400` recovery corrections.
- Repo deployment template predates the current host composition; it was not copied over the host or broadly synchronized. This record identifies the exact live image and narrow configuration change.

## Verification

- Docker build passed TypeScript checking and bundle compilation.
- Catalog test passed: 76 standard tools, 126 advanced tools, 50 additions.
- Container health returned healthy.
- Fresh MCP session inside Amanda's agent verified `amanda@zedworks.com`, user `1213974002925107`, workspace `11298561585567`.
- Live tool discovery exposes the boolean in all three schemas.
- Through Amanda's approved MCP, created `Prepare` under Paul's existing task `1218761421820816`. Heading ID: `1219007013809954`.
- Independent read-back returned `is_rendered_as_separator: true`, `resource_subtype: default_task`, null assignee, null due date, and the correct parent.
- Authenticated Chrome rendered it as `Section Name`, without a completion checkbox. Adjacent action was `Task Name` with its completion checkbox. Subtask count remained 0 / 9, excluding the heading.
- This test repairs connector capability. Amanda's broader assignment breakdown and ordering remain her pending work. No existing task descriptions, owners, dates or completion states were changed.

## Attempts and rollback

- Local Python lacked Paramiko; used existing native SSH with the approved VPS1 key.
- First remote backup attempt failed because the source directory was not writable. No source edit occurred in that attempt. Saved backup in jackadmin's home, then patched the writable source file.
- Initial image build began before the successful source patch; rebuilt after the patch and deployed only that second image.
- In-app browser was signed out; used the available signed-in Chrome for visual verification.
- Source backup: `/home/jackadmin/amanda-task-tools.before-native-headings-20260929.ts`.
- Compose backup: `/home/jackadmin/amanda-compose.before-native-headings-20260929.yml`.
- Rollback: restore the source backup and original image reference `zedbiz/asana-http-mcp:2.0.0-amanda-session-recovery-20260927`, then recreate only Amanda's MCP service.
- Existing npm audit advisories were reported during the build; no dependency upgrade or audit repair was included.

## Source status

Branch: `fix/amanda-native-headings-20260929`. PR contains the shared schema repair and this live evidence. Main is unchanged until merge. No SOP, prompt, or registry rewrite was needed; the exposed tool field explains the correct usage.
