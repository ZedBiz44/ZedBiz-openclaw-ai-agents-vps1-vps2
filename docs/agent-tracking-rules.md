# Agent Tracking Rules

## Purpose

These rules make GitHub the operating ledger for all ZedBiz AI agent work.

Every agent should leave behind enough evidence that Jack can later ask:

- When was this skill added?
- Who added it?
- Why did we add it?
- What broke?
- What fixed it?
- Which VPS or agent was affected?
- Where is the tested SOP?

## Mandatory Tracking Rule

If an action changes how an agent, VPS, SOP, skill, feature, route, cron job, Docker setup, or folder structure works, it must be tracked in GitHub.

## What Must Be Tracked

- New skill added
- Existing skill changed
- New feature added
- Prompt, identity, memory, or tool file changed
- Docker, Caddy, routing, or domain change
- VPS folder structure change
- cron or automation change
- bug found
- bug fixed
- SOP rewritten
- manual workaround discovered
- security-sensitive change, recorded without secrets

## Minimum Tracking Entry

Each tracked item needs:

- Date in Mountain Time
- Agent or person responsible
- System affected
- VPS affected
- Change type
- Reason for change
- Files or commands touched
- Test result
- Rollback note
- Related Notion page or GitHub Issue

## Where To Track

- Use GitHub Issues for open work, bugs, questions, or anything not fully tested.
- Use Markdown logs for confirmed actions and historical record.
- Use SOP files for the current tested procedure.
- Use Notion only for dashboard summaries and review links.

## VPS And Hermes Lanes

- Main Docker VPS work goes in `ai-agent-sops/zedbiz-main-vps/`.
- Secondary VPS work, including Harry and Edith, goes in `ai-agent-sops/zedbiz-secondary-vps/`.
- Third VPS work goes in `ai-agent-sops/zedbiz-third-vps/`.
- Hermes platform 1 work goes in `ai-agent-sops/hermes1/`.
- Hermes platform 2 work goes in `ai-agent-sops/hermes2/`.

## Commit Message Standard

Use practical commit messages:

- `Add skill log: Terry email triage setup`
- `Fix SOP: Docker chown workaround for agent files`
- `Track feature: Harry folder-based skill install`
- `Update routing SOP: Caddy subdomain verification`

Avoid vague commit messages:

- `update`
- `misc`
- `fix`
- `stuff`

## Agent Signature

Every agent entry should name itself clearly:

- Cody
- Manus
- OpenClaw Terry
- OpenClaw Harry
- OpenClaw Edith
- Hermes1 agent name
- Hermes2 agent name
- Human name

## Secret Handling

Never commit:

- API keys
- GitHub tokens
- SSH private keys
- passwords
- session cookies
- full `.env` files

Use references instead:

- secret name
- credential location
- permission needed
- date verified
