# ZedBiz AI Agent Documentation Instructions

## Working Style

- Keep answers and documents practical for a business owner, marketer, and operator.
- Use plain language first, then technical detail only where it helps execution.
- Favor rapid execution: build the simplest working version, test it, then improve.
- Treat GitHub as the source of truth for code, configs, Dockerfiles, prompts, command snippets, and SOP versions.
- Treat Notion as the operational layer for dashboard views, summaries, planning, and approvals.
- Use Mountain Time for dated work notes.

## GitHub Documentation Rules

- Store live SOPs as Markdown in `ai-agent-sops/`.
- Store reusable templates in `docs/templates/`.
- Use GitHub Issues for SOP bugs, failed steps, missing commands, unclear wording, and broken assumptions.
- Use short commit messages that explain the business reason for the fix.
- Do not bury important changes in vague messages like `updates` or `fixed docs`.

## GitHub Issue Filing Rules

Before creating, updating, or closing any GitHub issue, follow `docs/github-issue-filing-sop.md`.

Minimum behavior:

- Search existing issues before creating a new one.
- Use the correct repo lane or file in General Tech with `needs-routing` when unsure.
- Add required `agent:`, `system:`, `type:`, and `status:` labels where available.
- Keep ongoing work in one parent issue or workstream instead of making duplicate session issues.
- Comment material attempts, failures, fixes, verification, and PR/main-branch status.
- Do not close until the final comment says what was verified and whether SOPs, tracking files, registry, or Notion summaries were updated.

## Mandatory Tracking Rule

If an action changes how an agent, VPS, SOP, skill, feature, route, cron job, Docker setup, or folder structure works, it must be tracked in GitHub.

Track the work using one or more of these:

- GitHub Issue for open work, bug reports, untested ideas, and decisions needed.
- Markdown log in the relevant `tracking/` folder for confirmed historical record.
- SOP update when the tested procedure changes.
- Notion summary after GitHub has the operating detail.

## Agent Change Standard

Every guide update should include:

- The guide name
- The broken or unclear step
- The old assumption
- The tested correction
- The agent or person who verified it
- The date verified
- Any related Notion page, GitHub issue, or VPS agent

## Skill And Feature Tracking Standard

Every new skill or feature must record:

- Skill or feature name
- Added by
- Agent receiving it
- VPS or system affected
- Purpose
- Files changed
- Commands used
- Test result
- Rollback note

Use `docs/templates/skill-addition-template.md` or `docs/templates/feature-change-template.md`.

## VPS Tracking Standard

- Main Docker VPS work belongs under `ai-agent-sops/zedbiz-main-vps/`.
- Secondary VPS work for Harry and Edith belongs under `ai-agent-sops/zedbiz-secondary-vps/`.
- Third VPS work belongs under `ai-agent-sops/zedbiz-third-vps/`.
- Hermes platform 1 work belongs under `ai-agent-sops/hermes1/`.
- Hermes platform 2 work belongs under `ai-agent-sops/hermes2/`.
- Shared scripts belong under `ai-agent-sops/shared-scripts/`.

Use `docs/templates/vps-change-template.md` for server-level changes.

## Notion Sync Standard

- Notion should summarize the status, owner, priority, and next action.
- GitHub should hold the detailed step-by-step content and change history.
- Notion pages should link to GitHub files and GitHub Issues instead of duplicating long SOP text.

## Secret Handling

Never commit API keys, GitHub tokens, SSH private keys, passwords, session cookies, or full `.env` files.

Commit only safe references:

- secret name
- credential location
- permission needed
- date verified
