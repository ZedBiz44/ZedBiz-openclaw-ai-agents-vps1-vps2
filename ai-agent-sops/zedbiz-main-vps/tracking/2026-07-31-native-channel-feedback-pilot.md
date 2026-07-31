# 2026-07-31 - Feature Change - Native Channel Feedback Pilot

## Summary

- **Date:** 2026-07-31 Mountain Time
- **Added By:** Cody
- **System:** main-vps, OpenClaw v2026.7.1
- **Feature Status:** platform verification passed; user-visible test pending

## Feature Purpose

- Gives Jack immediate confirmation that an agent received an assignment.
- Shows a live progress message during longer work instead of leaving the channel silent.
- Uses native OpenClaw configuration so the behaviour survives upgrades.

## Implementation Notes

- **Agents:** Inga, Edith, Terry
- **Files changed:** each agent's live `/home/node/.openclaw/openclaw.json`
- **Reusable script:** `ai-agent-sops/shared-scripts/configure-channel-feedback.mjs`
- **GitHub Issue:** #104
- **Settings:**
  - `messages.ackReactionScope = "all"`
  - `messages.removeAckAfterReply = true`
  - Discord and Telegram `ackReaction = "👀"`
  - Slack `ackReaction = "eyes"`
  - Progress streaming enabled with the label `Working`, tool progress enabled, and status command text enabled
- **Configured channels changed:**
  - Inga: Discord and Telegram
  - Edith: Discord
  - Terry: Discord and Slack
- **Restart method:** each agent's `/opt/openclaw/agents/<agent>/op-start-<agent>.sh restart` wrapper

## Verification

- Configuration validation passed for all three agents.
- Inga container and Asana sidecar healthy; Discord and Telegram provider probes passed.
- Edith container and Asana sidecar healthy; Discord provider probe passed.
- Terry container and Asana sidecar healthy; Discord and Slack provider probes passed.
- OpenClaw logs confirmed each configured provider started after restart.
- The existing inactive `memory-core` warning remains unrelated to this change.
- **Remaining test:** Jack must send each agent a real assignment lasting more than five seconds and confirm the immediate reaction and visible progress update.

## Rollback Note

- Restore the applicable dated backup, validate the configuration, then restart the agent with its wrapper.
- Inga: `/home/node/.openclaw/openclaw.json.bak-channel-feedback-2026-07-31T161830337Z`
- Edith: `/home/node/.openclaw/openclaw.json.bak-channel-feedback-2026-07-31T162018703Z`
- Terry: `/home/node/.openclaw/openclaw.json.bak-channel-feedback-2026-07-31T162059400Z`

## Links

- **GitHub Issue:** https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/104
- **Notion page:** https://app.notion.com/p/3aea3e33d58181b0820ce7902f7db713
- **Related commit:** to be added after publication
