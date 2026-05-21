# Agent Runbook For SOP Updates

## Purpose

This runbook tells Cody, Manus, and OpenClaw agents how to record guide updates without requiring Jack to work inside GitHub.

## When To Create A GitHub Issue

Create an issue when:

- A command fails.
- A guide step is unclear.
- A required permission or credential is missing.
- A guide works for one agent but not another.
- A step needs a human decision before changing the live SOP.

## When To Edit The SOP Directly

Edit the SOP directly when:

- The correction has been tested.
- The change is low risk.
- The old wording was clearly wrong.
- The update only clarifies the next action.

## Commit Message Format

Use this format:

`Fix <guide-name>: <specific operational reason>`

Examples:

- `Fix caddy-routing: correct domain flag that caused 404`
- `Update agent-base-build: add docker chown workaround`
- `Clarify skill-setup: separate tested steps from assumptions`

## Required Change Note

Each meaningful SOP change should include a short note in `docs/guide-change-log.md` with:

- Date
- Agent
- Guide
- Problem
- Fix
- Test result
- Related issue or Notion page

