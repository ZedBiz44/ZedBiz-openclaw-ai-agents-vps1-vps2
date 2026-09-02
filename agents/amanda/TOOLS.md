# Amanda Local Tool Notes

Date: 2026-09-02 | Agent: Cody | Status: Current

## Runtime

- Workspace: `/opt/openclaw/agents/amanda/workspace/`
- Container workspace: `/home/node/.openclaw/workspace/`
- VPS: `VPS1` at `187.77.210.223`
- Container: `amanda`
- Port: `3001`
- Public URL: `https://amanda.zbiz.ca`
- Primary channels: Discord and Telegram; IMAP/SMTP email is configured.
- Discord text channel ID: `1492585662614999300`

## Asana Route

- Primary route: persistent PAT-backed Streamable HTTP MCP server `asana`.
- Expected identity: `Amanda zbiz`, `amanda@zedworks.com`, user GID `1213974002925107`.
- Expected workspace: `ZedBiz - Local Marketing Service`, GID `11298561585567`.
- Toolset: Advanced. The current route provides Standard and Advanced operations through the single `asana` server.
- There is no separate `asana-team` route in the verified 2026-09-02 configuration.
- Start Asana work with `asana_get_user` using `user_gid: "me"`; stop if identity or workspace does not match.
- Resolve names across projects, teams, and portfolios instead of guessing the object type.
- Treat a successful real PAT tool call and the sidecar health endpoint as authoritative. A legacy HTTP/SSE probe failure alone does not prove this Streamable HTTP route is unavailable.
- Never display or store the PAT.

## Approved Asana Capability

- The Advanced toolset covers routine task and project operations plus team, portfolio, custom-field, goal, template, webhook, workload, and organization-level operations.
- Use `z-asana-agent-control` for ordinary assigned work.
- Use the approved advanced Asana-control workflow for team administration, portfolio mutations, workspace custom-field administration, goals, webhooks, broad structural changes, or an operation requiring unrestricted API access.
- Prefer named tools. Do not use unrestricted API access to bypass approval rules.

## Notion And Knowledge

- Use `z-notion-knowledge-publish` through Codex Apps Notion OAuth for authorized governed publishing.
- Use `z-knowledge-routing` and `z-wiki-research` when their triggers apply.
- Do not use a generic Notion skill, `ntn`, curl, raw tokens, or plaintext credentials as a fallback.
- Journal location and routine are governed by `HEARTBEAT.md`.

## Email

- List inbox: `himalaya envelope list`
- Read: `himalaya message read <ID>`
- Reply: `himalaya message reply <ID>`
- Compose: `himalaya message write`
- If a scheduled inbox check finds nothing actionable, remain silent.

## Memory

- Provider slot: `memory-lancedb`.
- Daily memory location: `/home/node/.openclaw/workspace/memory`.
- Keep durable notes concise and sanitized. Store outcomes, decisions, evidence, blockers, and next actions—not transcripts or secrets.
