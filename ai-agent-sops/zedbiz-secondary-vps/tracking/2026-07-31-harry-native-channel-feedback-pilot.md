# 2026-07-31 - Feature Change - Harry Native Channel Feedback Pilot

## Summary

- **Date:** 2026-07-31 Mountain Time
- **Added By:** Cody
- **System:** secondary-vps, Harry, OpenClaw v2026.7.1
- **Feature Status:** platform verification passed; user-visible test pending

## Feature Purpose

- Gives Jack immediate confirmation that Harry received an assignment.
- Shows a live progress message during longer Discord work.
- Uses native OpenClaw configuration so the behaviour survives upgrades.

## Implementation Notes

- **Agent:** Harry
- **File changed:** `/root/.openclaw-harry/openclaw.json`
- **Reusable script:** `ai-agent-sops/shared-scripts/configure-channel-feedback.mjs`
- **GitHub Issue:** #104
- **Settings:**
  - `messages.ackReactionScope = "all"`
  - `messages.removeAckAfterReply = true`
  - Discord `ackReaction = "👀"`
  - Progress streaming enabled with the label `Working`, tool progress enabled, and status command text enabled
- **Restart method:** `systemctl restart openclaw-harry.service`

## Verification

- Configuration validation passed.
- `openclaw-harry.service` returned active and running after restart.
- Harry's Discord provider was running, its bot probe passed, and its configured Discord channel audit passed.
- OpenClaw logs confirmed the native configuration reload and Discord provider restart.
- The existing inactive `memory-core` warning remains unrelated to this change.
- **Remaining test:** Jack must send Harry a real assignment lasting more than five seconds and confirm the immediate reaction and visible progress update.

## Rollback Note

- Restore `/root/.openclaw-harry/openclaw.json.bak-channel-feedback-2026-07-31T162202295Z`, validate the configuration, then restart `openclaw-harry.service`.

## Links

- **GitHub Issue:** https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/104
- **Notion page:** https://app.notion.com/p/3aea3e33d58181b0820ce7902f7db713
- **Pull request:** https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/105
- **Related commit:** `fca9ae7`
