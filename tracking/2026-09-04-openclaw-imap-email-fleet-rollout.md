# OpenClaw IMAP Email-to-Action Fleet Rollout

Date: 2026-09-04 Mountain Time | Agent: Cody | Status: Partially complete

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

## VPS2 And VPS4 Finding

Harry, Suzy, Frank, and Rocky have OpenClaw 2026.8.2 and the bundled IMAP plugin. Their running OpenClaw services do not currently receive `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `EMAIL_SERVER`, or `EMAIL_IMAP_PORT` from 1Password.

Their mailbox credentials remain stored in their separate 1Password vaults. No password was copied into GitHub, Notion, chat, or an unprotected file. Their live OpenClaw configurations were not changed because the mailbox would fail to log in without the missing startup connection.

## Rollback

Each VPS1 agent has a timestamped pre-rollout copy of `openclaw.json` and `AGENTS.md` inside that agent's workspace backup folder. Restore both files and restart the agent through its protected `op-start-<agent>.sh` script.

## Verification Result

- VPS1: 11 of 11 OpenClaw agents connected.
- VPS2: 0 of 3 connected; 1Password-to-service startup connection required.
- VPS4: 0 of 1 connected; 1Password-to-service startup connection required.
- Fleet total: 11 of 15 connected.
- Ruby was not included because Ruby runs Hermes, not OpenClaw.

## Links

- GitHub issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/252
- Notion SOP: https://app.notion.com/p/3d1a3e33d5818097a20de424cdedac8c
- OpenClaw IMAP reference: https://docs.openclaw.ai/automation/imap
