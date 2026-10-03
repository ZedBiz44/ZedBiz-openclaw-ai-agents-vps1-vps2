# TOOLS.md - Victor's Local Notes

## Environment Details
- **URL:** https://victor.zbiz.ca
- **Port:** 3002
- **Discord Channel ID:** 1492961829973004490
- **Email:** victor@agents.zbiz.ca

## Agent Management & Infrastructure
- **Mounted Directory:** `/opt/openclaw/agents` → `/home/node/.openclaw/agents-shared` (rw).
- **Docker Socket:** Accessible at `http://docker-socket-proxy:2375`.
- **UID Note:** `jackadmin` is UID 1001.

## Local Command Reference
- **Fix Permissions Workaround:** `docker run --rm -v /opt/openclaw/shared:/target alpine chown -R 1000:1000 /target/folder`
- **Skill Management (CLI):** `node /app/openclaw.mjs skills <search|list|install|info|update|check>`. (Installed to `/home/node/.openclaw/workspace/skills/`).
- **Email (Himalaya CLI):** `himalaya envelope list`, `himalaya message read <ID>`, `himalaya message reply <ID>`, `himalaya message write`. (Credentials pre-configured).

## External Services
- **Allzed WordPress MCP:** https://allzed.com/wp-json/mcp/v1/http — Token stored in 1Password.

## Victor Runtime And Integrations
- **Workspace:** `/opt/openclaw/agents/victor/workspace/`
- **VPS:** VPS1 at `187.77.210.223`
- **Primary channels:** Discord and email (IMAP/SMTP)
- **Primary MCP systems:** Asana and Notion
- **Technical source of truth:** GitHub/local Markdown for code, configs, Dockerfiles, repair notes, and implementation history SOPs, prompts and their reviews are maintained in Notion only.

## Notion Operating Details
- New-page frontmatter: `Date: YYYY-MM-DD | Agent: Victor | Status: Draft` using Mountain Time. Use `Review` or `Final` only when appropriate.
- Page names: capitalize words and separate them with dashes when the applicable Notion workflow requires it.
- Daily journal: `VPS1-Daily-Journals` > `Victor-Daily-Journal`
- Daily journal URL: `https://app.notion.com/p/395a3e33d58181a9b5a4db593624706c`
- Daily row format: `YYYY-MM-DD | Victor-daily-report`; record the date, agent `Victor`, and concise operational bullets.

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

## Asana Identity And Toolset

- Primary route: the persistent PAT-backed Streamable HTTP MCP server named `asana`. Never use Jack's Codex/ChatGPT Asana connector for agent-owned work.
- Toolset: `standard`.
- Required identity: `Victor Zagent`, `victor@agents.zbiz.ca`, user GID `1214049698028551`.
- Required workspace: `ZedBiz - Local Marketing Service`, GID `11298561585567`.
- Begin Asana work with `asana_get_user` using `user_gid: "me"`; stop if identity or workspace does not match.
- Resolve names across projects, teams, and portfolios instead of guessing the object type.
- Treat a successful real PAT tool call and the sidecar `/healthz` endpoint as authoritative. A legacy `openclaw mcp probe asana` HTTP/SSE 400 does not by itself prove the Streamable HTTP route is broken.

- This agent has the 76-tool Asana Standard toolset for normal team, project, task, subtask, section, project-status, project-brief, tag, attachment, date, dependency, blocker, and read-only portfolio work.
- Team administration, portfolio mutations, workspace custom-field administration, goals administration, webhooks, and unrestricted API operations require an approved Advanced agent.

## Verified native GitHub authentication
GitHub CLI and HTTPS Git are authenticated with the provisioned scoped read-only credential. Use gh api or normal HTTPS Git without interactive login. The private repository is ZedBiz44/zedbiz-jack-key-info; the required style guide is briefing/style-manifesto.md. Never print credentials. Native gh config is protected in github-runtime-auth/gh-config.
