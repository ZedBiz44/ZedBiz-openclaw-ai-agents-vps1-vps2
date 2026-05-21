# zedbiz-ai-agents

How to set up your custom AI agent team for your marketing business.

This repository is the GitHub source of truth for ZedBiz AI agent SOPs, setup guides, command snippets, decisions, tested fixes, and operating notes.

Notion remains the business dashboard. GitHub holds the version-controlled working documents so Cody, Manus, and OpenClaw agents can update guides, explain why a change was made, and link fixes to issues.

## Recommended Folder Structure

```text
ai-agent-sops/
├── .github/                     # Workflows, issue templates if needed
├── core/                        # Everything that applies to ALL agents
│   ├── templates/
│   ├── cli-cheatsheet.md
│   ├── memory-strategies.md
│   ├── prompt-engineering.md
│   └── best-practices.md
├── zedbiz-main-vps/             # Your primary 10 agents
│   ├── deployment/
│   ├── sops/
│   └── agent-specific/
├── zedbiz-vps2/                 # Testing / experimental
│   ├── experiments/
│   └── test-results/
├── zedbiz-vps3/                 # Domain-specific agent
│   ├── tools/
│   ├── plumbing-workflows.md
│   └── client-handling.md
├── hermes1/                     # Hermes cluster
│   ├── routing-logic.md
│   ├── orchestration/
│   └── swarm-management.md
├── hermes2/                     # Hermes cluster
│   ├── routing-logic.md
│   ├── orchestration/
│   └── swarm-management.md
├── shared-scripts/              # Any actual bash/python scripts used across servers
└── archives/                    # Old versions you want to keep
```

## Operating Model

- GitHub stores the actual SOP files, templates, bugs, change history, and tested snippets.
- Notion stores the owner-friendly dashboard, priorities, summaries, and approval notes.
- Agents update GitHub first when a guide changes.
- Agents update Notion second with a plain-language summary and link back to the GitHub file or issue.
- Every meaningful SOP change needs a short reason, test status, and rollback note.

## Key Rules For Agents

- Core folder is read-heavy and edited rarely.
- Each server or group mostly stays in its own folder but is allowed to read `core/` and other folders.
- Use clear naming and date/version stamps in filenames when making big changes.
- Use GitHub Issues for broken SOP steps, unclear commands, missing context, or retest requests.
- Use practical commit messages that explain the operational reason for the change.

## Practical Deployment Tips

- Sparse checkout or simple path-based pulls: a server can use `git sparse-checkout set <folder-name>` or just work inside its assigned folder.
- All servers pull from the same repo but only write to their designated folders.
- Use GitHub branches only for real isolation, such as a risky experiment or untested rewrite.
- Most day-to-day work should use folders plus clear agent notes, not heavy process.

## Documentation System

- `AGENTS.md` - Standing instructions for agents working in this repository.
- `docs/agent-documentation-plan.md` - The GitHub + Notion operating plan.
- `docs/agent-runbook.md` - How agents should log guide bugs and SOP fixes.
- `docs/guide-change-log.md` - Plain-English summary of meaningful guide changes.
- `docs/decision-log.md` - Durable operating decisions.
- `docs/templates/` - Reusable SOP, bug report, and handoff templates.

