# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Wilma Runtime

- Workspace: `/opt/openclaw/agents/wilma/workspace/`
- Container workspace: `/home/node/.openclaw/workspace/`
- VPS: `VPS1` (`187.77.210.223`)
- Port: `3003`
- Public URL: https://wilma.zbiz.ca
- Primary channels: Discord and email
- Discord text channel ID: `1503820816645881956`
- Config: `/opt/openclaw/agents/wilma/config/openclaw.json`
- Container: `wilma`

## Source Systems

- WordPress AllZed MCP: live WordPress state and site operations.
- Notion: verified canonical website, SOP, operations, strategy, content, brand, agent-registry, and Z-Knowledge records.
- Asana: assigned task oversight and handoffs.
- GitHub/local Markdown: code, configuration, and implementation history. SOPs, prompts and their reviews are maintained in Notion only.
- Memory Wiki: reviewed durable agent knowledge.

## Email - Himalaya CLI
- Check inbox: `himalaya envelope list`
- Read a message: `himalaya message read <ID>`
- Reply to a message: `himalaya message reply <ID>`
- Send a new message: `himalaya message write`
- Inbox is always available — no login needed, credentials are pre-configured.
- If inbox is empty or nothing needs action, end the session silently — do NOT post to Discord.

## WordPress MCP - allzed.com
- MCP URL: https://allzed.com/wp-json/mcp/v1/http
- Bearer Token: op://agent-wilma/aiengine-bearer-token/credential
- Env var alias: AIENGINE_BEARER_TOKEN
- Always start with tools/list to see available tools, then mcp_ping to confirm connection
- Start with WordPress core only — do NOT use Plugins, Themes, Database, or Dynamic REST without Jack approval
- Use for: creating/editing posts, SEO analysis, media management, taxonomy, content workflows

## WordPress MCP - deals7.com
- MCP URL: https://deals7.com/wp-json/mcp/v1/http
- Bearer Token: provided by Jack on 2026-07-01; store in a secret manager before durable use
- Always start with tools/list to see available tools
- No mcp_ping tool exposed as of 2026-07-01
- Available tool set verified: posts, pages, media, users, comments, taxonomies
- Do not make client-facing, structural, destructive, plugin, theme, or database changes without Jack approval

## Asana Tools

Primary Asana route: the persistent PAT-backed Streamable HTTP MCP server named `asana`.

Expected authenticated user:

- Name: `Wilma Zagent`
- Email: `wilma@agents.zbiz.ca`
- User GID: `1214049698033540`
- Workspace GID: `11298561585567`

Required tool coverage before task execution: current-user lookup, assigned-task search, task read, task comment, task update/complete, and GID resolution.

Do not use Jack-authenticated Codex/ChatGPT Asana tools for agent-owned task execution. If that connector appears, ignore it and find the OpenClaw PAT MCP route named `asana`. Do not use Notion as an Asana auth fallback.

The full identity preflight, task-selection, comment, completion, and failure procedure is in `skills/z-asana-agent-control/SKILL.md`.

## Notion Journal

- Parent: `VPS1-Daily-Journals` > `Wilma-Daily-Journal`
- URL: https://app.notion.com/p/VPS1-Daily-Journals-395a3e33d58180308a94f4f219c9004a
- Routine: follow the daily-journal rule in `AGENTS.md` and current approved automations.

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
- Required identity: `Wilma Zagent`, `wilma@agents.zbiz.ca`, user GID `1214049698033540`.
- Required workspace: `ZedBiz - Local Marketing Service`, GID `11298561585567`.
- Begin Asana work with `asana_get_user` using `user_gid: "me"`; stop if identity or workspace does not match.
- Resolve names across projects, teams, and portfolios instead of guessing the object type.
- Treat a successful real PAT tool call and the sidecar `/healthz` endpoint as authoritative. A legacy `openclaw mcp probe asana` HTTP/SSE 400 does not by itself prove the Streamable HTTP route is broken.

- This agent has the 76-tool Asana Standard toolset for normal team, project, task, subtask, section, project-status, project-brief, tag, attachment, date, dependency, blocker, and read-only portfolio work.
- Team administration, portfolio mutations, workspace custom-field administration, goals administration, webhooks, and unrestricted API operations require an approved Advanced agent.

## GitHub private repository access
The runtime already holds a scoped read-only credential in GITHUB_API_TOKEN. The gh launcher maps it to GH_TOKEN in memory; GitHub HTTPS uses the same launcher as its credential helper. No interactive login is needed. Never print the token or put it in URLs.
Use `gh api repos/ZedBiz44/zedbiz-jack-key-info/contents/briefing/style-manifesto.md` to read the required style manifesto (API content is base64), or clone the HTTPS repository normally. If bypassing PATH with /usr/local/bin/gh, map GITHUB_API_TOKEN to GH_TOKEN for that process. An unauthenticated gh login result without this mapping does not establish missing repository access.

## Verified native GitHub authentication
GitHub CLI and HTTPS Git are authenticated with the provisioned scoped read-only credential. Use gh api or normal HTTPS Git without interactive login. The private repository is ZedBiz44/zedbiz-jack-key-info; the required style guide is briefing/style-manifesto.md. Never print credentials. Native gh config is protected in github-runtime-auth/gh-config.
