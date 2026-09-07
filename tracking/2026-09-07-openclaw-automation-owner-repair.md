# 2026-09-07 - OpenClaw automation owner repair

Date: 2026-09-07 | Agent: Cody | Status: Complete

## Problem

The scheduled ZedBiz jobs stopped running after the IMAP email-to-action rollout added the internal `mail_reader` agent entry. Each Gateway then had both `main` and `mail_reader`, while the existing scheduled jobs had no explicit `agentId`. OpenClaw 2026.8.2 could no longer choose a safe owner and logged:

`Agent-less cron job has no resolvable owner`

The global automation switch was not the root cause. The scheduler was enabled, but the affected jobs had ambiguous ownership.

## Tested correction

Inga was repaired and tested first.

- Backed up the live OpenClaw configuration.
- Set `agents.defaults.systemAgent.agentId` to `main`.
- Pinned every managed `zedbiz:*` job to `agentId: main`.
- Kept the internal `mail_reader` entry unchanged for IMAP intake.
- Explicitly set `cron.enabled` to `true`.
- Restarted through the existing protected Docker wrapper or native systemd service.
- Validated the configuration, scheduler state, job ownership, run history, Notion output, and Discord delivery where applicable.

The same correction was then applied to all remaining OpenClaw agents.

## Agents repaired

- VPS1 Docker Gateways: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.
- VPS2 native Gateways: Harry, Suzy, and Frank.
- VPS4 native Gateway: Rocky.

All 15 Gateways now report an enabled scheduler and zero unresolved ZedBiz jobs.

## Prompt safety correction

Daily-journal prompts now tell agents to use the active memory provider's recall tool and `sessions_search`, not the unsupported generic `memory_search` tool. Amanda retains her explicitly approved experimental search behavior.

Frank's journal prompt also prohibits Bash or shell commands. His first corrected-owner run created the Notion page but marked the automation failed after an unnecessary Bash check. The tightened prompt reran successfully.

## Recovery verification

- Exactly one 2026-09-07 daily-journal page was found in each agent's own Notion database.
- All 15 daily-journal runs reached a confirmed successful completion state after recovery.
- Amanda's 7:00 a.m. Asana summary succeeded and delivered to Discord channel `1492585662614999300`.
- Marsha's 7:30 a.m. current-work summary succeeded and delivered to Discord channel `1492966441169981632`.
- Suzy's recovered 8:00 a.m. weather and Internet Marketing report succeeded and delivered to Discord user `864290378395025478`.
- Inga's noon report remains scheduled for noon Mountain Time and was not forced early.

## Backups and rollback

A timestamped `automation-owner-*` backup of each live `openclaw.json` was stored under that agent's existing backup area before modification.

Rollback is to restore the matching backup and restart that agent through its protected wrapper or native service. The internal `mail_reader` agent was not removed.

## Notes

- A Gateway is the OpenClaw service handling one installation's channels, tools, agents, and schedules. On VPS1 it runs inside each Docker container. On VPS2 and VPS4 it runs as a native systemd service.
- `mail_reader` is a narrow internal OpenClaw agent entry used by IMAP intake. It is not a separate Discord personality or a second visible team agent.
- VPS4 maintenance-shell validation warned that Asana and Percify environment variables were unavailable outside the service. The running service keeps its normal secret-injection path; no secret value was displayed or changed.

## Related records

- Issue #249: completion-timeout and scheduled-work investigation.
- Issue #252: IMAP email-to-action rollout that introduced the second agent entry.
