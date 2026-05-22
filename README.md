# zedbiz-ai-agents

How to set up your custom AI agent team for your marketing business.

This repository is the GitHub source of truth for ZedBiz AI agent SOPs, setup guides, command snippets, decisions, tested fixes, and operating notes.

Notion remains the business dashboard. GitHub holds the version-controlled working documents so Cody, Manus, OpenClaw agents, and Hermes agents can update guides, explain why a change was made, and link fixes to issues.

## Recommended Folder Structure

```text
ai-agent-sops/
|-- core/                        # Everything that applies to ALL agents
|   |-- templates/
|   |-- cli-cheatsheet.md
|   |-- memory-strategies.md
|   |-- prompt-engineering.md
|   `-- best-practices.md
|-- zedbiz-main-vps/             # Main Docker VPS and current OpenClaw testing
|   |-- deployment/
|   |-- sops/
|   |-- agent-specific/
|   `-- tracking/
|-- zedbiz-secondary-vps/        # Secondary VPS, Harry, and Edith
|   |-- deployment/
|   |-- sops/
|   |-- agent-specific/
|   `-- tracking/
|-- zedbiz-third-vps/            # Third VPS and domain-specific agent work
|   |-- deployment/
|   |-- sops/
|   |-- agent-specific/
|   `-- tracking/
|-- hermes1/                     # Hermes agent/platform 1
|   |-- routing-logic.md
|   |-- orchestration/
|   `-- tracking/
|-- hermes2/                     # Hermes agent/platform 2
|   |-- routing-logic.md
|   |-- orchestration/
|   `-- tracking/
|-- shared-scripts/              # Bash, Python, and reusable command helpers
`-- archives/                    # Old versions kept for history
```

## Operating Model

- GitHub stores the actual SOP files, templates, bugs, change history, and tested snippets.
- Notion stores the owner-friendly dashboard, priorities, summaries, and approval notes.
- Agents update GitHub first when a guide changes.
- Agents update Notion second with a plain-language summary and link back to the GitHub file or issue.
- Every meaningful change needs a short reason, test status, and rollback note.

## What We Track

- Main Docker VPS testing and changes
- Secondary VPS setup for Harry and Edith
- Third VPS setup and domain-specific agent work
- OpenClaw agent changes
- Hermes1 and Hermes2 agent changes
- skill additions and updates
- feature additions and updates
- Docker, Caddy, routing, cron, permissions, and folder structure changes
- SOP fixes and guide rewrites
- bugs, incidents, and failed commands

## Key Rules For Agents

- Core folder is read-heavy and edited rarely.
- Each server or group mostly stays in its own folder but is allowed to read `core/` and other folders.
- Use clear naming and date/version stamps in filenames when making big changes.
- Use GitHub Issues for broken SOP steps, unclear commands, missing context, or retest requests.
- Use practical commit messages that explain the operational reason for the change.
- Never commit secrets, tokens, SSH keys, passwords, or full `.env` files.

## Practical Deployment Tips

- Sparse checkout or simple path-based pulls: a server can use `git sparse-checkout set <folder-name>` or just work inside its assigned folder.
- All servers pull from the same repo but only write to their designated folders.
- Use GitHub branches only for real isolation, such as a risky experiment or untested rewrite.
- Most day-to-day work should use folders plus clear agent notes, not heavy process.

## Documentation System

- `AGENTS.md` - Standing instructions for agents working in this repository.
- `docs/agent-tracking-rules.md` - Mandatory tracking rules for Cody, Manus, OpenClaw, and Hermes agents.
- `docs/tracking-taxonomy.md` - The label/category system for agents, servers, and change types.
- `docs/notion-github-dashboard-setup.md` - How to create the Notion synced GitHub database.
- `docs/agent-documentation-plan.md` - The GitHub + Notion operating plan.
- `docs/agent-runbook.md` - How agents should log guide bugs and SOP fixes.
- `docs/guide-change-log.md` - Plain-English summary of meaningful guide changes.
- `docs/decision-log.md` - Durable operating decisions.
- `docs/templates/` - Reusable SOP, bug report, skill, feature, VPS, incident, and handoff templates.
- `agent-message-board/` - GitHub-based dispatch board for agent-to-agent messages, handoffs, confirmations, and blockers.
