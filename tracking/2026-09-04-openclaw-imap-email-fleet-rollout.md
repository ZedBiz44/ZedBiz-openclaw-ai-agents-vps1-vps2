# OpenClaw IMAP Email-to-Action Fleet Rollout

Date: 2026-09-04 Mountain Time | Agent: Cody | Status: Complete

## Purpose

Connect each OpenClaw agent's `agents.zbiz.ca` mailbox to OpenClaw so approved email can start real work.

## Approved Senders

- `no-reply@asana.com`
- `succeed@zedbiz.com`
- `jzedbiz@gmail.com`

Sender authentication remains set to `verified`.

## Work Rule

- A new Asana assignment email tells the agent to open Asana and work the matching existing task assigned to that agent.
- The agent must not create another Asana task from the email.
- Asana comments, reminders, due-date changes, completion notices, and the agent's own updates do not start work.
- Email from Jack's two approved addresses is a direct assignment, subject to the agent's normal approval and safety rules.
- The email worker uses the same workspace and normal tools as the named agent.

## VPS1 Rollout

The following agents are configured and connected in IMAP push mode:

- Amanda
- Marsha
- Victor
- Wilma
- Grogar
- GohZed
- Inga
- Maggie
- Terry
- Vivian
- Edith

Amanda and Marsha passed real email-to-action tests from Jack. Jack independently confirmed both agents completed the emailed instructions.

The other nine agents passed configuration validation, protected restart, normal Gateway startup, IMAP login, push-mode watcher startup, sender-list verification, and work-rule verification.

## VPS2 And VPS4 Rollout

Harry, Suzy, Frank, and Rocky already had working 1Password startup paths and access to their own email items plus the shared email-server items. The first audit checked the service's first process and incorrectly concluded that new vault access was needed. A second check followed the complete startup chain and proved the existing access was sufficient.

- Added the four email item references to Harry, Suzy, and Frank's existing `op run` startup files.
- Added the four email reads to Rocky's existing 1Password startup wrapper.
- Connected each mailbox to the bundled IMAP plugin.
- Confirmed the email values are injected into the final running OpenClaw processes without printing or storing the values in documentation.
- Confirmed all four services are active, OpenClaw is ready, and each mailbox watcher is running in IMAP push mode.

Harry's old `meta.lastTouchedAt` entry was removed because OpenClaw 2026.8.2 rejects that obsolete field during validation. Rocky's configuration was validated as the `openclaw` runtime user so his approved memory-plugin path was checked under the correct account.

## Rollback

Each VPS1 agent has a timestamped pre-rollout copy of `openclaw.json` and `AGENTS.md` inside that agent's workspace backup folder. Harry, Suzy, Frank, and Rocky also have timestamped copies of their configuration, work rules, and startup files. Restore the saved files and restart through the agent's normal protected service.

## Verification Result

- VPS1: 11 of 11 OpenClaw agents connected.
- VPS2: 3 of 3 OpenClaw agents connected.
- VPS4: 1 of 1 OpenClaw agent connected.
- Fleet total: 15 of 15 OpenClaw agents connected.
- Ruby was not included because Ruby runs Hermes, not OpenClaw.

## Links

- GitHub issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/252
- Notion SOP: https://app.notion.com/p/3d1a3e33d5818097a20de424cdedac8c
- OpenClaw IMAP reference: https://docs.openclaw.ai/automation/imap
