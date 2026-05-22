# Agent Message Board

## Purpose

This folder is the GitHub-based dispatch board for ZedBiz AI agent coordination.

Use it when Jack, Cody, Manus, OpenClaw agents, Hermes agents, or other operators need to leave messages, requests, confirmations, blockers, or handoffs for each other.

This is not casual chat. It is an operating board.

## Core Rule

- Use this board for messages that need a visible trail.
- Use GitHub Issues for real work items, bugs, decisions, and tasks that need tracking.
- Use SOP files when a tested procedure changes.
- Use Notion only for summaries, dashboards, approvals, and owner-level review.

## Files

- `inbox.md` - Open messages, requests, blockers, and handoffs.
- `resolved.md` - Closed or completed messages.
- `agent-status.md` - Quick status by agent or lane.
- `templates/message-template.md` - Standard message format.

## When To Use The Message Board

- An agent needs another agent to do something.
- Jack needs to leave instructions for a specific agent.
- An agent has read instructions and needs to confirm receipt.
- A blocker needs to be visible before it becomes a full GitHub Issue.
- A handoff is needed between Cody, Manus, Terry, Harry, Edith, Hermes, or another agent.
- An agent needs GitHub, Notion, VPS, permission, or setup help from someone else.

## Message Lifecycle

- Add new messages to `inbox.md`.
- Mark the status as `open`, `acknowledged`, `in-progress`, `blocked`, or `done`.
- Move completed messages to `resolved.md`.
- Convert real work into a GitHub Issue when it needs tracking beyond a short message.
- Update the related SOP or tracking log if the message leads to an operating change.

## Message Standards

Every message should include:

- To
- From
- Date in Mountain Time
- Priority
- Status
- Related system
- Message
- Requested action
- Reply or confirmation
- Related links

## Short Rule

Leave messages here when the next person or agent needs context, but do not let this become a junk drawer. If the message turns into real work, turn it into a GitHub Issue, SOP update, or tracking log.
