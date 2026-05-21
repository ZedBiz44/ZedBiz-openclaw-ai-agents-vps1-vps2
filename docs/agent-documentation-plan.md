# AI Agent Documentation Plan

## Recommended System

Use a hybrid system:

- GitHub is the source of truth for the actual guides.
- Notion is the dashboard for business visibility, approvals, priorities, and summaries.
- GitHub Issues track guide bugs and failed steps.
- GitHub commits document exactly what changed and why.
- GitHub branches are used only for risky guide rewrites or untested new agent procedures.

## Why GitHub Fits This Work

Your agent SOPs behave like operational software:

- They include CLI commands.
- They include snippets and config examples.
- They break when the environment changes.
- They need tested fixes.
- They need clear rollback history.

GitHub gives you the audit trail that Notion does not handle cleanly at the step level.

## What Stays In Notion

- Dashboard of guides and agent build status.
- Plain-English summaries for you.
- Priorities, blockers, and approvals.
- Links to GitHub SOP files and GitHub Issues.
- Daily journal entries and implementation notes.

## What Moves To GitHub

- The full text of each SOP.
- Command snippets and config examples.
- Known failure notes.
- Tested fixes.
- Change logs.
- Issue history.
- Agent handoff instructions.

## Agent Workflow

- Agent finds a guide bug or unclear step.
- Agent opens or updates a GitHub Issue.
- Agent edits the Markdown SOP.
- Agent commits with a clear reason.
- Agent links the commit to the issue.
- Agent updates Notion with a short business summary and link.

## Minimum Viable Setup

- Create one private GitHub repository.
- Add this folder structure.
- Move the most active SOPs first, not everything at once.
- Start with the Agent Creation SOP and the highest-friction subguides.
- Use one GitHub Issue per failed step or unclear guide section.

