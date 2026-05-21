# ZedBiz AI Agent Operations

This repository is the GitHub source of truth for AI agent setup guides, SOP changes, troubleshooting notes, and tested command snippets.

Notion remains the business dashboard. GitHub holds the version-controlled working documents so Cody, Manus, and OpenClaw agents can update guides, explain why a change was made, and link fixes to issues.

## Operating Model

- GitHub stores the actual SOP files, templates, bugs, change history, and tested snippets.
- Notion stores the owner-friendly dashboard, priorities, summaries, and approval notes.
- Agents update GitHub first when a guide changes.
- Agents update Notion second with a plain-language summary and link back to the GitHub file or issue.
- Every meaningful SOP change needs a short reason, test status, and rollback note.

## Main Folders

- `agent-sops/` - The live agent creation and operations guides.
- `docs/` - The working system: index, runbook, decision log, and change log.
- `docs/templates/` - Reusable templates for SOPs, bug reports, and agent handoffs.
- `.github/ISSUE_TEMPLATE/` - GitHub issue forms for guide bugs and improvement requests.

## Daily Agent Rule

When an agent changes a guide, it should record:

- What changed
- Why it changed
- What failed before
- What was tested after
- Which Notion page or operational request triggered the change

