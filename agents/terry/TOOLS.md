# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

Terry your Discord Text Channel ID = 1502000570377044069

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Email - Himalaya CLI
- Check inbox: `himalaya envelope list`
- Read a message: `himalaya message read <ID>`
- Reply to a message: `himalaya message reply <ID>`
- Send a new message: `himalaya message write`
- Inbox is always available — no login needed, credentials are pre-configured.
- If inbox is empty or nothing needs action, end the session silently — do NOT post to Discord.

## Health Check
- When Jack asks to run the health check skill, treat that request as approval to run read-only health/audit commands.
- Still ask before state-changing actions such as `openclaw doctor --fix`, config changes, chmod, firewall changes, SSH changes, or service restarts.

## Terry Runtime

- Workspace: `/opt/openclaw/agents/terry/workspace/`
- VPS: `VPS1 (187.77.210.223)`
- Port: `3010`
- URL: `https://terry.zbiz.ca`
- Primary channels: Discord and email (IMAP/SMTP)
- Primary MCP servers: Asana and Notion

## Asana Tools

Primary Asana route: the persistent PAT-backed Streamable HTTP MCP server named `asana`, with `ASANA_ACCESS_TOKEN` supplied by the approved runtime secret store.

Expected authenticated user:

- Name: `Terry Zagent`
- Email: `terry@agents.zbiz.ca`
- User GID: `1214469570857381`
- Workspace GID: `11298561585567`

Required tool coverage before task execution: current-user lookup, assigned-task search, task read, task comment, task update/complete, and GID resolution.

Do not use Jack-authenticated Codex/ChatGPT Asana tools for agent-owned task execution. If that connector appears, ignore it and find the OpenClaw PAT MCP route named `asana`. Do not use Notion as an Asana auth fallback.

## Daily Memory Rule

Daily memory location: `/home/node/.openclaw/workspace/memory`.

Save a short daily memory note when work creates durable business or operating value. Do not wait for Jack to ask if the work clearly matters later.

Save after:
- Completing a task, fix, diagnosis, rollout, campaign, offer, funnel, document, or Notion/GitHub update.
- Making or receiving a decision that affects future work.
- Learning a durable fact about Jack, ZedBiz, an agent, a server, a workflow, a client, or a marketing system.
- Hitting a blocker that the next agent or next session must know about.
- Ending a long work session with meaningful progress.

Do not save:
- Casual chatter, tiny tests, jokes, duplicate status updates, or throwaway canary phrases.
- Sensitive secrets, tokens, passwords, or private credentials.
- Half-formed guesses unless clearly marked as uncertain.

Memory note format:
- Date and source channel.
- What changed or was learned.
- Why it matters operationally or commercially.
- Evidence or verification, if available.
- Next action or owner, if any.

Keep each note concise. Aim for 5 to 10 bullets, not a transcript.

## Notion Daily Journal

- In Codex sessions, use Codex Apps Notion; discover deferred tools when needed.
- Outside Codex, use the bundled `notion` skill with `env -u NOTION_API_TOKEN NOTION_KEYRING=0 NOTION_HOME=/home/node/.openclaw/notion-cli ntn`. The saved login is for ZedBiz Notion. Follow the Notion routing and approval rules in `AGENTS.md`.
- Maintain Terry's journal in the `VPS1-Daily-Journals` inline database under Terry Daily Journal.
- At the first session after 5:00 AM Mountain Time, create that day's row with agent `Terry` and the exact name `Terry-daily-report`.
- Add brief bullet summaries of activities, assignments, tasks, and sessions throughout the day.
- Follow the sample entry's formatting, then remove sample rows after Terry's real entry exists.


## Asana Identity And Read Navigation

- Begin Asana work with `asana_get_user` using `user_gid: "me"`; verify Terry's PAT identity and workspace before trusting results.
- Treat a successful real PAT tool call and the service `/healthz` endpoint as authoritative. A legacy `openclaw mcp probe asana` HTTP/SSE 400 does not prove this Streamable HTTP route is broken.
- Never infer that a name is a portfolio merely because project search returned no result.
- Resolve ambiguous names across projects, teams, and accessible portfolios.
- For a team, use `asana_search_teams`, then `asana_get_projects_for_team` with the resolved team GID.
- For read-only portfolio work, use `asana_list_accessible_portfolios`, `asana_get_portfolio`, and `asana_get_portfolio_items`.
- An empty portfolio list means Terry currently has no visible portfolio ownership or membership. It does not prove the workspace has no portfolios.
- Do not change team membership, portfolio sharing, portfolio roles, or portfolio structure without the advanced Asana policy and Jack's confirmation.

## Asana Identity And Toolset

- Primary route: the persistent PAT-backed Streamable HTTP MCP server named `asana`. Never use Jack's Codex/ChatGPT Asana connector for agent-owned work.
- Toolset: `standard`.
- Required identity: `Terry-Zagent`, `terry@agents.zbiz.ca`, user GID `1214469570857381`.
- Required workspace: `ZedBiz - Local Marketing Service`, GID `11298561585567`.
- Begin Asana work with `asana_get_user` using `user_gid: "me"`; stop if identity or workspace does not match.
- Resolve names across projects, teams, and portfolios instead of guessing the object type.
- Treat a successful real PAT tool call and the sidecar `/healthz` endpoint as authoritative. A legacy `openclaw mcp probe asana` HTTP/SSE 400 does not by itself prove the Streamable HTTP route is broken.

- This agent has the 76-tool Asana Standard toolset for normal team, project, task, subtask, section, project-status, project-brief, tag, attachment, date, dependency, blocker, and read-only portfolio work.
- Team administration, portfolio mutations, workspace custom-field administration, goals administration, webhooks, and unrestricted API operations require an approved Advanced agent.
