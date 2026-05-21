# ZedBiz AI Agent Documentation Instructions

## Working Style

- Keep answers and documents practical for a business owner, marketer, and operator.
- Use plain language first, then technical detail only where it helps execution.
- Favor rapid execution: build the simplest working version, test it, then improve.
- Treat GitHub as the source of truth for code, configs, Dockerfiles, prompts, command snippets, and SOP versions.
- Treat Notion as the operational layer for dashboard views, summaries, planning, and approvals.
- Use Mountain Time for dated work notes.

## GitHub Documentation Rules

- Store live SOPs as Markdown in `agent-sops/`.
- Store reusable templates in `docs/templates/`.
- Use GitHub Issues for SOP bugs, failed steps, missing commands, unclear wording, and broken assumptions.
- Use short commit messages that explain the business reason for the fix.
- Do not bury important changes in vague messages like `updates` or `fixed docs`.

## Agent Change Standard

Every guide update should include:

- The guide name
- The broken or unclear step
- The old assumption
- The tested correction
- The agent or person who verified it
- The date verified
- Any related Notion page, GitHub issue, or VPS agent

## Notion Sync Standard

- Notion should summarize the status, owner, priority, and next action.
- GitHub should hold the detailed step-by-step content and change history.
- Notion pages should link to GitHub files and GitHub Issues instead of duplicating long SOP text.

