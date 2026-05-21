# Notion GitHub Dashboard Setup

## Goal

Create a live Notion view that shows GitHub activity from `ZedBiz44/zedbiz-ai-agents` without forcing Jack to work inside GitHub every day.

## Recommended Dashboard

Use Notion as the visual dashboard and GitHub as the source of truth.

## Synced Database Setup

This part must be done inside Notion because Notion's "Paste as database" action is a workspace UI feature.

For a normal repo preview, use this repo link:

```text
https://github.com/ZedBiz44/zedbiz-ai-agents
```

Steps:

- Open the Notion page where the dashboard should live.
- Paste the GitHub repository link if you only want a normal repo preview.
- To create a synced GitHub database, paste a GitHub `Issues` or `Pull Requests` link instead of the repo homepage.
- Choose `Paste as database` when Notion offers it.
- Name it `GitHub - ZedBiz AI Agent Tracking`.
- Place it near the top of the Technical Documentation page or the Agent Creation SOP dashboard.

Recommended synced database links to try:

```text
https://github.com/ZedBiz44/zedbiz-ai-agents/issues
```

```text
https://github.com/ZedBiz44/zedbiz-ai-agents/pulls
```

If Notion still only shows `Preview`, `Mention`, and `URL`, then the Notion workspace GitHub connection is not fully enabled for synced databases.

## Recommended Notion Views

- `Recent Changes` - newest updates first.
- `Open Bugs` - GitHub Issues that are not closed.
- `Skills Added` - entries tagged as skills.
- `VPS Work` - entries tagged by main VPS, secondary VPS, or third VPS.
- `Needs Jack Decision` - issues tagged `needs-jack`.

## What GitHub Should Feed Into Notion

- Issues
- Pull requests
- commits
- changed files
- labels
- dates
- authors

## Important Limitation

The synced database shows GitHub activity, but the detailed operating record should still live in GitHub Markdown files and Issues.

Notion is the dashboard. GitHub is the audit trail.
